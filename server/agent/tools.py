"""LangChain tools for resort, weather, and avalanche data."""

import json
import os
import re
import time
from collections.abc import Sequence
from functools import lru_cache
from typing import Any

import httpx
from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account
from langchain_core.tools import tool

load_dotenv()
load_dotenv("../.env")

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "bergfex-481612")
DATASET_ID = os.getenv("BQ_DATASET_ID", "bergfex_data")
VIEW_ID = os.getenv("BQ_VIEW_ID", "vw_latest_snow_with_shred_score")

OPEN_METEO_DWD_URL = "https://api.open-meteo.com/v1/dwd-icon"
OPEN_METEO_CUSTOMER_URL = "https://customer-api.open-meteo.com/v1/dwd-icon"
SLF_BULLETIN_URL = "https://aws.slf.ch/api/bulletin/caaml/v4/{language}/geojson"
MAX_LIMIT = 30
WEATHER_CACHE_SECONDS = 15 * 60


@tool
def query_ski_resorts(
    min_snow_depth: int = 0,
    country: str | None = None,
    max_avalanche_level: int | None = None,
    only_open: bool = False,
    limit: int = 10,
) -> dict[str, Any]:
    """Search the Bergfex BigQuery data for ski resorts.

    Use this first for resort recommendations. It returns current resort metrics,
    coordinates, the existing deterministic Shred Score, and source timestamps.
    Country accepts names or ISO codes such as AT, DE, and CH. The function only
    runs a fixed parameterized query; it never executes model-generated SQL.
    """
    min_snow_depth = _bounded_int(min_snow_depth, minimum=0, maximum=1_000)
    limit = _bounded_int(limit, minimum=1, maximum=MAX_LIMIT)
    country_pattern = _country_pattern(country)
    avalanche_level = _optional_avalanche_level(max_avalanche_level)

    query = f"""
    WITH resorts AS (
      SELECT
        v.resort_id,
        v.resort_name,
        v.region,
        v.country,
        v.status,
        v.snow_valley_raw,
        v.snow_mountain_raw,
        v.new_snow_raw,
        v.avalanche_warning,
        v.lifts_open_count,
        v.lifts_total_count,
        v.slopes_open_km_raw,
        v.slopes_total_km,
        v.elevation_valley,
        v.elevation_mountain,
        v.shred_coefficient,
        v.scraped_at,
        d.lat,
        d.lon,
        SAFE_CAST(
          REGEXP_EXTRACT(COALESCE(v.snow_mountain_raw, ''), r'(\\d+\\.?\\d*)')
          AS FLOAT64
        ) AS snow_mountain_cm,
        CASE
          WHEN REGEXP_CONTAINS(UPPER(COALESCE(v.avalanche_warning, '')), r'(^|[ -])V([ -]|$)') THEN 5
          WHEN REGEXP_CONTAINS(UPPER(COALESCE(v.avalanche_warning, '')), r'(^|[ -])IV([ -]|$)') THEN 4
          WHEN REGEXP_CONTAINS(UPPER(COALESCE(v.avalanche_warning, '')), r'(^|[ -])III([ -]|$)') THEN 3
          WHEN REGEXP_CONTAINS(UPPER(COALESCE(v.avalanche_warning, '')), r'(^|[ -])II([ -]|$)') THEN 2
          WHEN REGEXP_CONTAINS(UPPER(COALESCE(v.avalanche_warning, '')), r'(^|[ -])I([ -]|$)') THEN 1
          ELSE SAFE_CAST(REGEXP_EXTRACT(COALESCE(v.avalanche_warning, ''), r'([1-5])') AS INT64)
        END AS avalanche_level
      FROM `{PROJECT_ID}.{DATASET_ID}.{VIEW_ID}` v
      LEFT JOIN `{PROJECT_ID}.{DATASET_ID}.dim_resorts` d
        ON v.resort_id = d.resort_id
    )
    SELECT *
    FROM resorts
    WHERE COALESCE(snow_mountain_cm, 0) >= @min_snow_depth
      AND (@country_pattern IS NULL OR LOWER(COALESCE(country, '')) LIKE @country_pattern)
      AND (@only_open = FALSE OR LOWER(COALESCE(status, '')) LIKE '%open%')
      AND (@max_avalanche_level IS NULL OR avalanche_level BETWEEN 1 AND @max_avalanche_level)
    ORDER BY shred_coefficient DESC, snow_mountain_cm DESC
    LIMIT {limit}
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("min_snow_depth", "INT64", min_snow_depth),
            bigquery.ScalarQueryParameter("country_pattern", "STRING", country_pattern),
            bigquery.ScalarQueryParameter("only_open", "BOOL", bool(only_open)),
            bigquery.ScalarQueryParameter(
                "max_avalanche_level", "INT64", avalanche_level
            ),
        ]
    )
    rows = _get_bigquery_client().query(query, job_config=job_config).result()
    resorts = [_resort_from_row(row) for row in rows]

    return {
        "source": f"BigQuery {PROJECT_ID}.{DATASET_ID}.{VIEW_ID}",
        "total": len(resorts),
        "filters": {
            "minSnowDepthCm": min_snow_depth,
            "country": country,
            "maxAvalancheLevel": avalanche_level,
            "onlyOpen": only_open,
        },
        "resorts": resorts,
    }


@tool
def get_weather_forecast(
    latitude: float,
    longitude: float,
    elevation: float | None = None,
    forecast_days: int = 3,
) -> dict[str, Any]:
    """Get a DWD ICON weather forecast from Open-Meteo for a resort coordinate.

    Use this after selecting one or a few resorts. It supplies daily snowfall,
    precipitation probability, temperature, gusts, sunshine, visibility, snow
    depth, and freezing-level ranges. No API key is required.
    """
    latitude, longitude = _validated_coordinates(latitude, longitude)
    forecast_days = _bounded_int(forecast_days, minimum=1, maximum=7)
    elevation = float(elevation) if elevation is not None else None
    source_url = _open_meteo_url()
    try:
        payload = _get_weather_payload(
            round(latitude, 5),
            round(longitude, 5),
            elevation,
            forecast_days,
            int(time.monotonic() // WEATHER_CACHE_SECONDS),
        )
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        return {
            "provider": "Open-Meteo DWD ICON",
            "source": source_url,
            "available": False,
            "error": "rate_limited" if status_code == 429 else "upstream_error",
            "statusCode": status_code,
            "message": (
                "Die Wetterquelle ist gerade gedrosselt oder nicht verfügbar. "
                "Bitte ohne Wetterdaten fortfahren und später erneut versuchen."
            ),
        }

    return {
        "provider": "Open-Meteo DWD ICON",
        "source": source_url,
        "available": True,
        "coordinates": {"latitude": latitude, "longitude": longitude},
        "elevationM": payload.get("elevation"),
        "timezone": payload.get("timezone"),
        "daily": _daily_weather(payload),
    }


@tool
def get_avalanche_bulletin(
    latitude: float,
    longitude: float,
    language: str = "de",
) -> dict[str, Any]:
    """Get the official SLF avalanche bulletin matching a Swiss coordinate.

    The public SLF CAAML/GeoJSON feed covers Switzerland. Always present this as
    a regional bulletin, not as a guarantee of slope safety. For coordinates
    outside its coverage the tool returns an explicit no-match status.
    """
    latitude, longitude = _validated_coordinates(latitude, longitude)
    language = (
        language.lower() if language.lower() in {"de", "fr", "it", "en"} else "de"
    )
    source_url = SLF_BULLETIN_URL.format(language=language)
    payload = _get_json(source_url)
    feature = _matching_feature(payload.get("features", []), longitude, latitude)

    if feature is None:
        return {
            "provider": "WSL Institute for Snow and Avalanche Research SLF",
            "source": source_url,
            "matched": False,
            "message": (
                "No SLF bulletin polygon matched this coordinate. The point may be "
                "outside Switzerland or no regional bulletin may be active."
            ),
        }

    return {
        "provider": "WSL Institute for Snow and Avalanche Research SLF",
        "source": source_url,
        "matched": True,
        "coordinates": {"latitude": latitude, "longitude": longitude},
        "bulletin": _compact_bulletin(feature.get("properties", {})),
    }


AGENT_TOOLS = [query_ski_resorts, get_weather_forecast, get_avalanche_bulletin]


@lru_cache(maxsize=1)
def _get_bigquery_client() -> bigquery.Client:
    """Build the BigQuery client lazily so agent imports stay side-effect free."""
    credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not credentials_json:
        return bigquery.Client(project=PROJECT_ID)

    credentials_info = json.loads(credentials_json)
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info
    )
    return bigquery.Client(project=PROJECT_ID, credentials=credentials)


def _get_json(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Fetch one public JSON data source with a bounded timeout."""
    with httpx.Client(timeout=15.0, follow_redirects=True) as client:
        response = client.get(
            url,
            params=params,
            headers={"User-Agent": "bergfex-dashboard/0.2.1"},
        )
        response.raise_for_status()
        payload = response.json()
    if not isinstance(payload, dict):
        raise TypeError(f"Expected a JSON object from {url}")
    return payload


@lru_cache(maxsize=256)
def _get_weather_payload(
    latitude: float,
    longitude: float,
    elevation: float | None,
    forecast_days: int,
    cache_bucket: int,
) -> dict[str, Any]:
    """Cache equivalent forecasts briefly to reduce public API traffic."""
    del cache_bucket  # The time bucket exists only to expire cached entries.
    params: dict[str, Any] = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": "auto",
        "forecast_days": forecast_days,
        "daily": (
            "temperature_2m_max,temperature_2m_min,precipitation_probability_max,"
            "precipitation_sum,snowfall_sum,wind_gusts_10m_max,sunshine_duration"
        ),
        "hourly": "snow_depth,visibility,freezing_level_height",
    }
    if elevation is not None:
        params["elevation"] = elevation
    api_key = os.getenv("OPEN_METEO_API_KEY")
    if api_key:
        params["apikey"] = api_key
    return _get_json(_open_meteo_url(), params=params)


def _open_meteo_url() -> str:
    """Use reserved Open-Meteo capacity when an optional customer key exists."""
    return (
        OPEN_METEO_CUSTOMER_URL
        if os.getenv("OPEN_METEO_API_KEY")
        else OPEN_METEO_DWD_URL
    )


def _resort_from_row(row: Any) -> dict[str, Any]:
    scraped_at = getattr(row, "scraped_at", None)
    return {
        "id": str(row.resort_id),
        "name": row.resort_name or "Unknown",
        "region": getattr(row, "region", None),
        "country": getattr(row, "country", None),
        "status": getattr(row, "status", None),
        "snowValleyCm": float(_parse_number(getattr(row, "snow_valley_raw", None))),
        "snowMountainCm": float(_parse_number(getattr(row, "snow_mountain_raw", None))),
        "newSnowCm": float(_parse_number(getattr(row, "new_snow_raw", None))),
        "avalancheLevel": getattr(row, "avalanche_level", None),
        "avalancheWarningRaw": getattr(row, "avalanche_warning", None),
        "liftsOpen": getattr(row, "lifts_open_count", 0) or 0,
        "liftsTotal": getattr(row, "lifts_total_count", 0) or 0,
        "slopesOpenKm": float(_parse_number(getattr(row, "slopes_open_km_raw", None))),
        "slopesTotalKm": float(_parse_number(getattr(row, "slopes_total_km", None))),
        "elevationValleyM": _parse_number(getattr(row, "elevation_valley", None)),
        "elevationMountainM": _parse_number(getattr(row, "elevation_mountain", None)),
        "shredScore": getattr(row, "shred_coefficient", None),
        "latitude": getattr(row, "lat", None),
        "longitude": getattr(row, "lon", None),
        "dataTimestamp": scraped_at.isoformat() if scraped_at else None,
    }


def _daily_weather(payload: dict[str, Any]) -> list[dict[str, Any]]:
    daily = payload.get("daily", {})
    hourly = payload.get("hourly", {})
    dates = daily.get("time", [])
    rows: list[dict[str, Any]] = []

    for index, date in enumerate(dates):
        hourly_indexes = [
            i
            for i, timestamp in enumerate(hourly.get("time", []))
            if timestamp.startswith(date)
        ]
        rows.append(
            {
                "date": date,
                "temperatureMinC": _list_value(daily, "temperature_2m_min", index),
                "temperatureMaxC": _list_value(daily, "temperature_2m_max", index),
                "precipitationProbabilityMaxPercent": _list_value(
                    daily, "precipitation_probability_max", index
                ),
                "precipitationSumMm": _list_value(daily, "precipitation_sum", index),
                "snowfallSumCm": _list_value(daily, "snowfall_sum", index),
                "windGustMaxKmh": _list_value(daily, "wind_gusts_10m_max", index),
                "sunshineHours": _seconds_to_hours(
                    _list_value(daily, "sunshine_duration", index)
                ),
                "minimumVisibilityM": _aggregate_hourly(
                    hourly, "visibility", hourly_indexes, min
                ),
                "maximumSnowDepthM": _aggregate_hourly(
                    hourly, "snow_depth", hourly_indexes, max
                ),
                "freezingLevelMinM": _aggregate_hourly(
                    hourly, "freezing_level_height", hourly_indexes, min
                ),
                "freezingLevelMaxM": _aggregate_hourly(
                    hourly, "freezing_level_height", hourly_indexes, max
                ),
            }
        )
    return rows


def _matching_feature(
    features: Sequence[dict[str, Any]], longitude: float, latitude: float
) -> dict[str, Any] | None:
    for feature in features:
        if _geometry_contains(feature.get("geometry", {}), longitude, latitude):
            return feature
    return None


def _geometry_contains(geometry: dict[str, Any], lon: float, lat: float) -> bool:
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates", [])
    if geometry_type == "Polygon":
        return _polygon_contains(coordinates, lon, lat)
    if geometry_type == "MultiPolygon":
        return any(_polygon_contains(polygon, lon, lat) for polygon in coordinates)
    return False


def _polygon_contains(polygon: Sequence[Any], lon: float, lat: float) -> bool:
    if not polygon or not _ring_contains(polygon[0], lon, lat):
        return False
    return not any(_ring_contains(hole, lon, lat) for hole in polygon[1:])


def _ring_contains(ring: Sequence[Sequence[float]], lon: float, lat: float) -> bool:
    inside = False
    if len(ring) < 3:
        return False
    previous = ring[-1]
    for current in ring:
        current_lon, current_lat = current[:2]
        previous_lon, previous_lat = previous[:2]
        crosses = (current_lat > lat) != (previous_lat > lat)
        if crosses:
            intersection = (previous_lon - current_lon) * (lat - current_lat) / (
                previous_lat - current_lat
            ) + current_lon
            if lon < intersection:
                inside = not inside
        previous = current
    return inside


def _compact_bulletin(properties: dict[str, Any]) -> dict[str, Any]:
    wanted = {
        "bulletinid",
        "lang",
        "publicationtime",
        "validtime",
        "nextupdate",
        "regions",
        "dangerratings",
        "avalancheproblems",
        "highlights",
        "traveladvisory",
        "snowpackstructure",
        "tendency",
    }
    selected = {
        key: _compact_value(value)
        for key, value in properties.items()
        if key.lower().replace("_", "") in wanted
    }
    return selected or {key: _compact_value(value) for key, value in properties.items()}


def _compact_value(value: Any, depth: int = 0) -> Any:
    if depth >= 4:
        return "…"
    if isinstance(value, dict):
        return {
            str(key): _compact_value(item, depth + 1)
            for key, item in list(value.items())[:20]
        }
    if isinstance(value, list):
        return [_compact_value(item, depth + 1) for item in value[:12]]
    if isinstance(value, str) and len(value) > 1_500:
        return value[:1_500] + "…"
    return value


def _country_pattern(country: str | None) -> str | None:
    if not country:
        return None
    normalized = country.strip().lower()
    aliases = {
        "at": "österreich",
        "austria": "österreich",
        "österreich": "österreich",
        "de": "deutschland",
        "germany": "deutschland",
        "deutschland": "deutschland",
        "ch": "schweiz",
        "switzerland": "schweiz",
        "schweiz": "schweiz",
    }
    return f"%{aliases.get(normalized, normalized)}%"


def _validated_coordinates(latitude: float, longitude: float) -> tuple[float, float]:
    latitude = float(latitude)
    longitude = float(longitude)
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ValueError("Coordinates are outside the valid latitude/longitude range")
    return latitude, longitude


def _optional_avalanche_level(value: int | None) -> int | None:
    if value is None:
        return None
    return _bounded_int(value, minimum=1, maximum=5)


def _bounded_int(value: Any, minimum: int, maximum: int) -> int:
    parsed = int(value)
    return max(minimum, min(maximum, parsed))


def _parse_number(value: Any) -> int | float:
    if value is None or value == "":
        return 0
    if isinstance(value, (int, float)):
        return value
    match = re.search(r"(\d+\.?\d*)", str(value).strip().replace(",", "."))
    if not match:
        return 0
    number = float(match.group(1))
    return int(number) if number.is_integer() else number


def _list_value(data: dict[str, Any], key: str, index: int) -> Any:
    values = data.get(key, [])
    return values[index] if index < len(values) else None


def _aggregate_hourly(
    hourly: dict[str, Any], key: str, indexes: list[int], operation: Any
) -> Any:
    values = [
        hourly.get(key, [])[index]
        for index in indexes
        if index < len(hourly.get(key, [])) and hourly.get(key, [])[index] is not None
    ]
    return operation(values) if values else None


def _seconds_to_hours(value: Any) -> float | None:
    return round(float(value) / 3_600, 1) if value is not None else None
