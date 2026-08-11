from langchain_core.messages import HumanMessage

from server.agent.graph import _tools_for_messages


def test_resort_conditions_do_not_enable_weather() -> None:
    """Current piste and avalanche fields already come from BigQuery."""
    selected = _tools_for_messages(
        [HumanMessage(content="Beste Pistenbedingungen mit geringer Lawinenwarnstufe")]
    )

    assert [tool.name for tool in selected] == ["query_ski_resorts"]


def test_explicit_forecast_enables_weather() -> None:
    selected = _tools_for_messages(
        [HumanMessage(content="Wie wird das Wetter dort am Wochenende?")]
    )

    assert [tool.name for tool in selected] == [
        "query_ski_resorts",
        "get_weather_forecast",
    ]


def test_explicit_bulletin_enables_slf() -> None:
    selected = _tools_for_messages(
        [HumanMessage(content="Zeige mir das aktuelle SLF-Lawinenbulletin")]
    )

    assert [tool.name for tool in selected] == [
        "query_ski_resorts",
        "get_avalanche_bulletin",
    ]
