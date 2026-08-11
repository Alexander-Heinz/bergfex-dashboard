from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from server.agent import tools
from server.agent.router import _thread_id
from server.agent.tools import (
    _country_pattern,
    _daily_weather,
    _geometry_contains,
)


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
            return FakeQueryJob()

    fake_client = FakeClient()
    monkeypatch.setattr(tools, "_get_bigquery_client", lambda: fake_client)

    result = tools.query_ski_resorts.invoke(
        {"country": "Österreich%' OR TRUE --", "min_snow_depth": 50, "limit": 3}
    )

    assert "OR TRUE" not in fake_client.query_text
    assert result["resorts"][0]["snowMountainCm"] == 120.0
    assert result["resorts"][0]["shredScore"] == 87.5


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
