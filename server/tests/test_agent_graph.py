from langchain_core.messages import HumanMessage

from server.agent.graph import SYSTEM_PROMPT, _tools_for_messages


def test_system_prompt_hides_internal_data_warehouse_names() -> None:
    assert "BigQuery" not in SYSTEM_PROMPT
    assert "Bergfex-Schneedaten" in SYSTEM_PROMPT


def test_system_prompt_labels_route_estimates_as_llm_fallbacks() -> None:
    assert "Grobe LLM-Schätzung ohne Routing und Live-Verkehr" in SYSTEM_PROMPT
    assert "exakte Zeit" in SYSTEM_PROMPT


def test_resort_conditions_do_not_enable_weather() -> None:
    """Current piste and avalanche fields already come from resort data."""
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


def test_origin_request_enables_driving_route() -> None:
    selected = _tools_for_messages(
        [HumanMessage(content="Plane einen Familien-Skitrip ab München")]
    )

    assert [tool.name for tool in selected] == [
        "query_ski_resorts",
        "get_driving_route",
    ]
