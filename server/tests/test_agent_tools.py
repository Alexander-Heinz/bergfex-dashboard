from datetime import UTC, datetime
from types import SimpleNamespace

import httpx
import pytest
from fastapi import HTTPException

from server.agent import tools
from server.agent.router import _thread_id
from server.agent.tools import (
    _country_pattern,
    _daily_met_norway,
    _daily_weather,
    _geometry_contains,
    _resort_quality_notes,
    _shared_metric_groups,
)


def test_weather_rate_limit_uses_met_norway_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A throttled primary API should still return a reduced forecast."""
    request = httpx.Request("GET", tools.OPEN_METEO_DWD_URL)
    response = httpx.Response(429, request=request)
    error = httpx.HTTPStatusError(
        "rate limited",
        request=request,
        response=response,
    )

    def raise_rate_limit(*args, **kwargs):
        raise error

    monkeypatch.setattr(tools, "_get_weather_payload", raise_rate_limit)
    monkeypatch.setattr(
        tools,
        "_get_met_norway_payload",
        lambda *args, **kwargs: {
            "geometry": {"coordinates": [7.7, 46.4, 1_500]},
            "properties": {
                "meta": {"updated_at": "2026-01-15T00:00:00Z"},
                "timeseries": [
                    {
                        "time": "2026-01-15T00:00:00Z",
                        "data": {
                            "instant": {
                                "details": {
                                    "air_temperature": -3.0,
                                    "wind_speed": 5.0,
                                }
                            },
                            "next_1_hours": {
                                "summary": {"symbol_code": "snow"},
                                "details": {"precipitation_amount": 1.5},
                            },
                        },
                    }
                ],
            },
        },
    )

    result = tools.get_weather_forecast.invoke(
        {"latitude": 46.4, "longitude": 7.7, "forecast_days": 3}
    )

    assert result["available"] is True
    assert result["provider"] == "MET Norway Locationforecast"
    assert result["fallbackReason"] == 429
    assert result["daily"][0]["windSpeedMaxKmh"] == 18.0


def test_both_weather_failures_return_a_tool_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two unavailable providers must not terminate the LangGraph stream."""
    request = httpx.Request("GET", tools.OPEN_METEO_DWD_URL)
    primary_error = httpx.HTTPStatusError(
        "rate limited",
        request=request,
        response=httpx.Response(429, request=request),
    )
    fallback_request = httpx.Request("GET", tools.MET_NORWAY_URL)
    fallback_error = httpx.HTTPStatusError(
        "unavailable",
        request=fallback_request,
        response=httpx.Response(503, request=fallback_request),
    )

    def raise_primary(*args, **kwargs):
        raise primary_error

    def raise_fallback(*args, **kwargs):
        raise fallback_error

    monkeypatch.setattr(tools, "_get_weather_payload", raise_primary)
    monkeypatch.setattr(tools, "_get_met_norway_payload", raise_fallback)

    result = tools.get_weather_forecast.invoke(
        {"latitude": 46.4, "longitude": 7.7, "forecast_days": 3}
    )

    assert result["available"] is False
    assert result["error"] == "weather_sources_unavailable"
    assert result["primaryStatusCode"] == 429
    assert result["fallbackStatusCode"] == 503


def test_resort_tool_uses_parameters_and_maps_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = SimpleNamespace(
        resort_id="resort-1",
        resort_name="Testberg",
        region="Tirol",
        country="Österreich",
        status="open",
        snow_valley_raw="45 cm",
        snow_mountain_raw="120 cm",
        new_snow_raw="15 cm",
        avalanche_level=2,
        avalanche_warning="II - mäßig",
        lifts_open_count=8,
        lifts_total_count=10,
        slopes_open_km_raw="40 km",
        slopes_total_km="50 km",
        elevation_valley="1.000 m",
        elevation_mountain="2.500 m",
        shred_coefficient=87.5,
        lat=47.0,
        lon=11.0,
        scraped_at=datetime(2026, 1, 15, tzinfo=UTC),
    )

    class FakeQueryJob:
        def result(self):
            return [row]

    class FakeClient:
        query_text = ""

        def query(self, query: str, job_config):
            self.query_text = query
            assert any(
                parameter.name == "country_pattern"
                and parameter.value == "%österreich%' or true --%"
                for parameter in job_config.query_parameters
            )
            assert any(
                parameter.name == "min_new_snow" and parameter.value == 5
                for parameter in job_config.query_parameters
            )
            return FakeQueryJob()

    fake_client = FakeClient()
    monkeypatch.setattr(tools, "_get_bigquery_client", lambda: fake_client)

    result = tools.query_ski_resorts.invoke(
        {
            "country": "Österreich%' OR TRUE --",
            "min_snow_depth": 50,
            "min_new_snow": 5,
            "limit": 3,
        }
    )

    assert "OR TRUE" not in fake_client.query_text
    assert result["source"] == "Bergfex-Schneedaten"
    assert result["resorts"][0]["snowMountainCm"] == 120.0
    assert result["resorts"][0]["shredScore"] == 87.5
    assert result["resorts"][0]["dataTimestamp"] == "15.01.2026, 01:00 Uhr"


def test_driving_route_returns_user_friendly_summary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENROUTESERVICE_API_KEY", "test-key")
    monkeypatch.setattr(
        tools,
        "_geocode_place",
        lambda *args, **kwargs: {
            "label": "München, Bayern, Deutschland",
            "latitude": 48.137,
            "longitude": 11.575,
        },
    )
    monkeypatch.setattr(
        tools,
        "_get_route_payload",
        lambda *args, **kwargs: {
            "features": [
                {"properties": {"summary": {"distance": 210_500, "duration": 9_000}}}
            ]
        },
    )

    result = tools.get_driving_route.invoke(
        {
            "origin": "München",
            "destination_latitude": 47.1,
            "destination_longitude": 11.7,
        }
    )

    assert result["available"] is True
    assert result["distanceKm"] == 210.5
    assert result["durationMinutes"] == 150
    assert result["trafficIncluded"] is False


def test_driving_route_reports_missing_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENROUTESERVICE_API_KEY", raising=False)

    result = tools.get_driving_route.invoke(
        {
            "origin": "München",
            "destination_latitude": 47.1,
            "destination_longitude": 11.7,
        }
    )

    assert result["available"] is False
    assert result["error"] == "configuration_missing"
    assert "LLM-Zeitspanne" in result["fallbackGuidance"]


def test_polygon_matching_supports_holes() -> None:
    geometry = {
        "type": "Polygon",
        "coordinates": [
            [[7.0, 46.0], [9.0, 46.0], [9.0, 48.0], [7.0, 48.0], [7.0, 46.0]],
            [[7.5, 46.5], [8.0, 46.5], [8.0, 47.0], [7.5, 47.0], [7.5, 46.5]],
        ],
    }

    assert _geometry_contains(geometry, 8.5, 47.0)
    assert not _geometry_contains(geometry, 7.75, 46.75)
    assert not _geometry_contains(geometry, 10.0, 47.0)


def test_daily_weather_compacts_hourly_values() -> None:
    payload = {
        "daily": {
            "time": ["2026-01-15"],
            "temperature_2m_min": [-8.0],
            "temperature_2m_max": [-1.0],
            "precipitation_probability_max": [80],
            "precipitation_sum": [12.0],
            "snowfall_sum": [15.5],
            "wind_gusts_10m_max": [45.0],
            "sunshine_duration": [7_200],
        },
        "hourly": {
            "time": ["2026-01-15T00:00", "2026-01-15T01:00"],
            "visibility": [2_000.0, 1_200.0],
            "snow_depth": [0.8, 0.85],
            "freezing_level_height": [1_100.0, 1_300.0],
        },
    }

    result = _daily_weather(payload)

    assert result[0]["snowfallSumCm"] == 15.5
    assert result[0]["sunshineHours"] == 2.0
    assert result[0]["minimumVisibilityM"] == 1_200.0
    assert result[0]["maximumSnowDepthM"] == 0.85
    assert result[0]["freezingLevelMinM"] == 1_100.0


def test_daily_met_norway_does_not_invent_snow_fields() -> None:
    payload = {
        "properties": {
            "timeseries": [
                {
                    "time": "2026-01-15T00:00:00Z",
                    "data": {
                        "instant": {
                            "details": {
                                "air_temperature": -4.0,
                                "wind_speed": 2.0,
                                "wind_speed_of_gust": 7.0,
                            }
                        },
                        "next_1_hours": {
                            "summary": {"symbol_code": "snow"},
                            "details": {"precipitation_amount": 2.0},
                        },
                    },
                }
            ]
        }
    }

    result = _daily_met_norway(payload, forecast_days=1)

    assert result[0]["precipitationSumMm"] == 2.0
    assert result[0]["windGustMaxKmh"] == 25.2
    assert result[0]["snowfallSumCm"] is None
    assert result[0]["minimumVisibilityM"] is None


def test_resort_quality_notes_flag_shared_zero_snow_metrics() -> None:
    resorts = [
        {
            "name": name,
            "country": "Österreich",
            "region": "Zillertal",
            "snowMountainCm": 305.0,
            "newSnowCm": 0.0,
            "liftsOpen": 9,
            "liftsTotal": 63,
        }
        for name in ("Eggalm", "Rastkogel")
    ]

    notes = _resort_quality_notes(resorts, only_open=True)

    assert len(notes) == 3
    assert _shared_metric_groups(resorts) == [["Eggalm", "Rastkogel"]]


@pytest.mark.parametrize(
    ("value", "pattern"),
    [("AT", "%österreich%"), ("Deutschland", "%deutschland%"), ("CH", "%schweiz%")],
)
def test_country_aliases(value: str, pattern: str) -> None:
    assert _country_pattern(value) == pattern


def test_thread_id_validation() -> None:
    assert _thread_id("chat_123") == "chat_123"
    assert _thread_id(None)

    with pytest.raises(HTTPException):
        _thread_id("contains spaces")
