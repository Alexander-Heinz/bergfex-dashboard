"""LangChain tools for resort, weather, and avalanche data."""

import json
import os
import re
import time
from collections.abc import Sequence
from datetime import UTC, datetime
from functools import lru_cache
from typing import Any
from zoneinfo import ZoneInfo

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

APP_VERSION = "0.2.4"
APP_URL = "https://bergfex-dashboard.onrender.com"
APP_USER_AGENT = f"bergfex-dashboard/{APP_VERSION}"
OPEN_METEO_DWD_URL = "https://api.open-meteo.com/v1/dwd-icon"
OPEN_METEO_CUSTOMER_URL = "https://customer-api.open-meteo.com/v1/dwd-icon"
MET_NORWAY_URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
ORS_GEOCODE_URL = "https://api.openrouteservice.org/geocode/search"
ORS_DIRECTIONS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"
SLF_BULLETIN_URL = "https://aws.slf.ch/api/bulletin/caaml/v4/{language}/geojson"
MAX_LIMIT = 30
WEATHER_CACHE_SECONDS = 30 * 60
ROUTE_CACHE_SECONDS = 60 * 60
LOCAL_TIMEZONE = ZoneInfo("Europe/Berlin")
ROUTE_ESTIMATE_GUIDANCE = (
    "Bei bekannten Start- und Zielorten ist ersatzweise nur eine grobe, klar "
    "markierte LLM-Zeitspanne ohne Routing und Live-Verkehr zulässig."
)


@tool
def query_ski_resorts(
    min_snow_depth: int = 0,
    min_new_snow: int = 0,
    country: str | None = None,
    max_avalanche_level: int | None = None,
    only_open: bool = False,
    limit: int = 10,
) -> dict[str, Any]:
    """Search current Bergfex ski-resort data.

    Use this first for resort recommendations. It returns current resort metrics,
    coordinates, the existing deterministic Shred Score, source timestamps, and
    data-quality notes. Use min_new_snow for requests that explicitly require
    fresh snow. Country accepts names or ISO codes such as AT, DE, and CH. The
    function only runs a fixed parameterized query; it never executes
    model-generated SQL.
    """
    min_snow_depth = _bounded_int(min_snow_depth, minimum=0, maximum=1_000)
    min_new_snow = _bounded_int(min_new_snow, minimum=0, maximum=1_000)
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
        SAFE_CAST(
          REGEXP_EXTRACT(COALESCE(v.new_snow_raw, ''), r'(\\d+\\.?\\d*)')
          AS FLOAT64
        ) AS new_snow_cm,
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
      AND COALESCE(new_snow_cm, 0) >= @min_new_snow
      AND (@country_pattern IS NULL OR LOWER(COALESCE(country, '')) LIKE @country_pattern)
      AND (@only_open = FALSE OR LOWER(COALESCE(status, '')) LIKE '%open%')
      AND (@max_avalanche_level IS NULL OR avalanche_level BETWEEN 1 AND @max_avalanche_level)
    ORDER BY shred_coefficient DESC, snow_mountain_cm DESC
    LIMIT {limit}
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("min_snow_depth", "INT64", min_snow_depth),
            bigquery.ScalarQueryParameter("min_new_snow", "INT64", min_new_snow),
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
        "source": "Bergfex-Schneedaten",
        "total": len(resorts),
        "filters": {
            "minSnowDepthCm": min_snow_depth,
            "minNewSnowCm": min_new_snow,
            "country": country,
            "maxAvalancheLevel": avalanche_level,
            "onlyOpen": only_open,
        },
        "qualityNotes": _resort_quality_notes(resorts, only_open=bool(only_open)),
        "sharedMetricGroups": _shared_metric_groups(resorts),
        "resorts": resorts,
    }


@tool
def get_weather_forecast(
    latitude: float,
    longitude: float,
    elevation: float | None = None,
    forecast_days: int = 3,
) -> dict[str, Any]:
    """Get an alpine weather forecast with a public-provider fallback.

    Open-Meteo DWD ICON is preferred because it supplies snow-specific fields.
    If that service is unavailable or rate-limited, MET Norway supplies a
    reduced forecast with temperature, precipitation, wind, and symbols.
    """
    latitude, longitude = _validated_coordinates(latitude, longitude)
    forecast_days = _bounded_int(forecast_days, minimum=1, maximum=7)
    elevation = float(elevation) if elevation is not None else None
    try:
        payload = _get_weather_payload(
            round(latitude, 5),
            round(longitude, 5),
            elevation,
            forecast_days,
            int(time.monotonic() // WEATHER_CACHE_SECONDS),
        )
    except httpx.HTTPError as primary_error:
        return _met_norway_fallback(
            latitude,
            longitude,
            elevation,
            forecast_days,
            primary_error,
        )

    return {
        "provider": "Open-Meteo DWD ICON",
        "source": _open_meteo_url(),
        "available": True,
        "coordinates": {"latitude": latitude, "longitude": longitude},
        "elevationM": payload.get("elevation"),
        "timezone": payload.get("timezone"),
        "daily": _daily_weather(payload),
    }


@tool
def get_driving_route(
    origin: str,
    destination_latitude: float,
    destination_longitude: float,
) -> dict[str, Any]:
    """Calculate approximate driving distance and duration to one ski resort.

    Use this after selecting a resort when the user explicitly asks about
    travel time, distance, or a route from a named origin. Results use
    openrouteservice and OpenStreetMap and do not include live traffic.
    """
    api_key = os.getenv("OPENROUTESERVICE_API_KEY")
    if not api_key:
        return {
            "available": False,
            "error": "configuration_missing",
            "message": (
                "Fahrtzeiten sind noch nicht konfiguriert. Dafür muss "
                "OPENROUTESERVICE_API_KEY gesetzt werden."
            ),
            "fallbackGuidance": ROUTE_ESTIMATE_GUIDANCE,
        }

    origin = origin.strip()
    if len(origin) < 2:
        raise ValueError("Origin must contain at least two characters")
    destination_latitude, destination_longitude = _validated_coordinates(
        destination_latitude,
        destination_longitude,
    )

    try:
        place = _geocode_place(
            origin,
            int(time.monotonic() // ROUTE_CACHE_SECONDS),
        )
        if place is None:
            return {
                "available": False,
                "error": "origin_not_found",
                "message": f"Startort '{origin}' wurde nicht gefunden.",
                "fallbackGuidance": ROUTE_ESTIMATE_GUIDANCE,
            }
        route = _get_route_payload(
            round(place["latitude"], 5),
            round(place["longitude"], 5),
            round(destination_latitude, 5),
            round(destination_longitude, 5),
            int(time.monotonic() // ROUTE_CACHE_SECONDS),
        )
    except httpx.HTTPError as error:
        return {
            "available": False,
            "error": "route_source_unavailable",
            "statusCode": _http_error_code(error),
            "message": "Die Fahrtzeit konnte gerade nicht berechnet werden.",
            "fallbackGuidance": ROUTE_ESTIMATE_GUIDANCE,
        }

    summary = _route_summary(route)
    if summary is None:
        return {
            "available": False,
            "error": "route_not_found",
            "message": "Für diese Strecke wurde keine Autoroute gefunden.",
            "fallbackGuidance": ROUTE_ESTIMATE_GUIDANCE,
        }

    return {
        "provider": "openrouteservice auf Basis von OpenStreetMap",
        "source": "openrouteservice / OpenStreetMap",
        "available": True,
        "origin": place["label"],
        "destination": {
            "latitude": destination_latitude,
            "longitude": destination_longitude,
        },
        "distanceKm": round(summary["distance"] / 1_000, 1),
        "durationMinutes": round(summary["duration"] / 60),
        "trafficIncluded": False,
        "note": "Ungefähre Fahrzeit ohne Live-Verkehr, Pausen oder Wetterlage.",
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


AGENT_TOOLS = [
    query_ski_resorts,
    get_weather_forecast,
    get_driving_route,
    get_avalanche_bulletin,
]


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


def _get_json(
    url: str,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Fetch one public JSON data source with a bounded timeout."""
    request_headers = {"User-Agent": APP_USER_AGENT}
    request_headers.update(headers or {})
    with httpx.Client(timeout=15.0, follow_redirects=True) as client:
        response = client.get(
            url,
            params=params,
            headers=request_headers,
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


def _met_norway_fallback(
    latitude: float,
    longitude: float,
    elevation: float | None,
    forecast_days: int,
    primary_error: httpx.HTTPError,
) -> dict[str, Any]:
    """Return a reduced MET Norway forecast when Open-Meteo fails."""
    try:
        payload = _get_met_norway_payload(
            round(latitude, 4),
            round(longitude, 4),
            elevation,
            int(time.monotonic() // WEATHER_CACHE_SECONDS),
        )
    except httpx.HTTPError as fallback_error:
        return _weather_unavailable(primary_error, fallback_error)

    return {
        "provider": "MET Norway Locationforecast",
        "source": MET_NORWAY_URL,
        "available": True,
        "fallbackFrom": "Open-Meteo DWD ICON",
        "fallbackReason": _http_error_code(primary_error),
        "coordinates": {"latitude": latitude, "longitude": longitude},
        "elevationM": _met_norway_elevation(payload),
        "timezone": "UTC",
        "updatedAt": _friendly_timestamp(
            payload.get("properties", {}).get("meta", {}).get("updated_at")
        ),
        "limitations": [
            (
                "Fallback enthält keine verlässliche Schneefallmenge, Schneehöhe, "
                "Sichtweite oder Gefriergrenze."
            ),
        ],
        "daily": _daily_met_norway(payload, forecast_days),
    }


@lru_cache(maxsize=256)
def _get_met_norway_payload(
    latitude: float,
    longitude: float,
    elevation: float | None,
    cache_bucket: int,
) -> dict[str, Any]:
    """Cache MET Norway forecasts and use cache-friendly coordinates."""
    del cache_bucket  # The time bucket exists only to expire cached entries.
    params: dict[str, Any] = {"lat": latitude, "lon": longitude}
    if elevation is not None:
        params["altitude"] = round(elevation)
    return _get_json(
        MET_NORWAY_URL,
        params=params,
        headers={"User-Agent": _weather_user_agent()},
    )


def _weather_user_agent() -> str:
    """Identify the application as required by the MET Norway terms."""
    return os.getenv(
        "WEATHER_USER_AGENT",
        f"{APP_USER_AGENT} {APP_URL}",
    )


def _weather_unavailable(
    primary_error: httpx.HTTPError,
    fallback_error: httpx.HTTPError,
) -> dict[str, Any]:
    """Describe both provider failures without aborting the agent stream."""
    return {
        "provider": "Open-Meteo DWD ICON + MET Norway Locationforecast",
        "available": False,
        "error": "weather_sources_unavailable",
        "primaryStatusCode": _http_error_code(primary_error),
        "fallbackStatusCode": _http_error_code(fallback_error),
        "message": (
            "Beide Wetterquellen sind vorübergehend nicht verfügbar. Bitte "
            "ohne Wetterdaten fortfahren und später erneut versuchen."
        ),
    }


def _http_error_code(error: httpx.HTTPError) -> int | str:
    """Return a stable status value for tool output and tests."""
    if isinstance(error, httpx.HTTPStatusError):
        return error.response.status_code
    return type(error).__name__


def _met_norway_elevation(payload: dict[str, Any]) -> float | None:
    """Read elevation from the GeoJSON coordinate tuple when present."""
    coordinates = payload.get("geometry", {}).get("coordinates", [])
    return float(coordinates[2]) if len(coordinates) > 2 else None


def _daily_met_norway(
    payload: dict[str, Any], forecast_days: int
) -> list[dict[str, Any]]:
    """Compact hourly MET Norway data into honest daily summaries."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    timeseries = payload.get("properties", {}).get("timeseries", [])
    for item in timeseries:
        date = str(item.get("time", ""))[:10]
        if date:
            grouped.setdefault(date, []).append(item.get("data", {}))

    rows: list[dict[str, Any]] = []
    for date, items in list(grouped.items())[:forecast_days]:
        details = [item.get("instant", {}).get("details", {}) for item in items]
        symbols = {
            item.get("next_1_hours", {}).get("summary", {}).get("symbol_code")
            for item in items
        }
        rows.append(
            {
                "date": date,
                "temperatureMinC": _values_aggregate(details, "air_temperature", min),
                "temperatureMaxC": _values_aggregate(details, "air_temperature", max),
                "precipitationSumMm": round(
                    sum(
                        _nested_number(
                            item, "next_1_hours", "details", "precipitation_amount"
                        )
                        for item in items
                    ),
                    1,
                ),
                "windSpeedMaxKmh": _meters_per_second_to_kmh(
                    _values_aggregate(details, "wind_speed", max)
                ),
                "windGustMaxKmh": _meters_per_second_to_kmh(
                    _values_aggregate(details, "wind_speed_of_gust", max)
                ),
                "weatherSymbols": sorted(symbol for symbol in symbols if symbol),
                "snowfallSumCm": None,
                "minimumVisibilityM": None,
                "maximumSnowDepthM": None,
                "freezingLevelMinM": None,
                "freezingLevelMaxM": None,
            }
        )
    return rows


def _open_meteo_url() -> str:
    """Use reserved Open-Meteo capacity when an optional customer key exists."""
    return (
        OPEN_METEO_CUSTOMER_URL
        if os.getenv("OPEN_METEO_API_KEY")
        else OPEN_METEO_DWD_URL
    )


@lru_cache(maxsize=256)
def _geocode_place(place: str, cache_bucket: int) -> dict[str, Any] | None:
    """Resolve one user-provided origin with the configured routing provider."""
    del cache_bucket  # The time bucket exists only to expire cached entries.
    payload = _get_json(
        ORS_GEOCODE_URL,
        params={"text": place, "size": 1, "lang": "de"},
        headers=_ors_headers(),
    )
    features = payload.get("features", [])
    if not features:
        return None
    feature = features[0]
    coordinates = feature.get("geometry", {}).get("coordinates", [])
    if len(coordinates) < 2:
        return None
    return {
        "label": feature.get("properties", {}).get("label", place),
        "latitude": float(coordinates[1]),
        "longitude": float(coordinates[0]),
    }


@lru_cache(maxsize=512)
def _get_route_payload(
    origin_latitude: float,
    origin_longitude: float,
    destination_latitude: float,
    destination_longitude: float,
    cache_bucket: int,
) -> dict[str, Any]:
    """Fetch and briefly cache one car route."""
    del cache_bucket  # The time bucket exists only to expire cached entries.
    return _get_json(
        ORS_DIRECTIONS_URL,
        params={
            "start": f"{origin_longitude},{origin_latitude}",
            "end": f"{destination_longitude},{destination_latitude}",
        },
        headers=_ors_headers(),
    )


def _ors_headers() -> dict[str, str]:
    """Build authenticated headers without placing the API key in the URL."""
    api_key = os.getenv("OPENROUTESERVICE_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTESERVICE_API_KEY is not configured")
    return {
        "Authorization": api_key,
        "User-Agent": APP_USER_AGENT,
    }


def _route_summary(payload: dict[str, Any]) -> dict[str, float] | None:
    """Support the documented GeoJSON and JSON direction response shapes."""
    features = payload.get("features", [])
    if features:
        summary = features[0].get("properties", {}).get("summary")
    else:
        routes = payload.get("routes", [])
        summary = routes[0].get("summary") if routes else None
    if not summary or "distance" not in summary or "duration" not in summary:
        return None
    return {
        "distance": float(summary["distance"]),
        "duration": float(summary["duration"]),
    }


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
        "dataTimestamp": _friendly_timestamp(scraped_at),
    }


def _resort_quality_notes(resorts: list[dict[str, Any]], only_open: bool) -> list[str]:
    """Expose caveats the model must not silently reinterpret."""
    notes: list[str] = []
    if resorts and not any(resort["newSnowCm"] > 0 for resort in resorts):
        notes.append(
            "Kein Treffer meldet positiven Neuschnee. Nicht als Powder- oder "
            "Neuschnee-Empfehlung darstellen."
        )
    if only_open:
        notes.append(
            "Status 'open' kann außerhalb der Wintersaison Sommerbetrieb bedeuten. "
            "Skibetrieb nur bei zusätzlichen Pistendaten behaupten."
        )
    if _shared_metric_groups(resorts):
        notes.append(
            "Mehrere Treffer teilen identische Regions-, Schnee- und Liftdaten. "
            "Als mögliche Teilgebiete gruppieren statt als unabhängige Messungen."
        )
    return notes


def _shared_metric_groups(resorts: list[dict[str, Any]]) -> list[list[str]]:
    """Find likely sub-resorts backed by the same aggregate measurements."""
    groups: dict[tuple[Any, ...], list[str]] = {}
    for resort in resorts:
        key = (
            resort["country"],
            resort["region"],
            resort["snowMountainCm"],
            resort["newSnowCm"],
            resort["liftsOpen"],
            resort["liftsTotal"],
        )
        groups.setdefault(key, []).append(resort["name"])
    return [names for names in groups.values() if len(names) > 1]


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


def _values_aggregate(
    items: list[dict[str, Any]], key: str, operation: Any
) -> float | None:
    """Aggregate numeric values while ignoring absent forecast fields."""
    values = [float(item[key]) for item in items if item.get(key) is not None]
    return operation(values) if values else None


def _nested_number(item: dict[str, Any], *keys: str) -> float:
    """Read an optional nested numeric field as zero for summation."""
    value: Any = item
    for key in keys:
        if not isinstance(value, dict):
            return 0.0
        value = value.get(key)
    return float(value) if value is not None else 0.0


def _meters_per_second_to_kmh(value: float | None) -> float | None:
    """Convert MET Norway wind units to the dashboard's km/h convention."""
    return round(value * 3.6, 1) if value is not None else None


def _friendly_timestamp(value: Any) -> str | None:
    """Format source timestamps for German end users instead of infrastructure logs."""
    if value is None:
        return None
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return value
    else:
        return str(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(LOCAL_TIMEZONE).strftime("%d.%m.%Y, %H:%M Uhr")
