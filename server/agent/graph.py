"""Explicit LangGraph workflow for the ski-trip assistant."""

from collections.abc import Iterator
from functools import lru_cache
from typing import Any

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import BaseTool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from server.agent.llm import get_model
from server.agent.tools import (
    AGENT_TOOLS,
    get_avalanche_bulletin,
    get_driving_route,
    get_weather_forecast,
    query_ski_resorts,
)

SYSTEM_PROMPT = """
Du bist ein deutschsprachiger Ski-Trip-Datenagent. Antworte kompakt, konkret und
kennzeichne Datenquellen sowie Zeitstände. Nutze query_ski_resorts zuerst, wenn
es um Empfehlungen oder den Vergleich von Skigebieten geht. Wetter- und
Lawinenbulletin-Tools werden nur bei einer ausdrücklichen Nutzerfrage danach
angeboten. Der Shred Score wird von der bestehenden Datenpipeline berechnet;
erfinde oder verändere ihn nicht. Beachte qualityNotes und sharedMetricGroups
aus dem Skigebiets-Tool zwingend. Es gibt ein standortgenaues Wetter-Tool und
ein Fahrtzeit-Tool. Behaupte nicht, diese seien generell nicht integriert,
sondern rufe sie bei einer passenden Nutzerfrage auf.

Wichtige Grenzen:
- Bei Fragen nach viel Neuschnee nutze min_new_snow mit mindestens 1 cm. Gibt
  es keine Treffer, sage das klar und ersetze die Bedingung nicht stillschweigend
  durch Gesamtschneehöhe.
- "Open" kann besonders außerhalb der Wintersaison Sommerbetrieb bedeuten.
  Behaupte aktuellen Skibetrieb nur mit positiven Pistenöffnungsdaten. Bezeichne
  Schneesicherheit nie als garantiert.
- Fehlende Lawinenmeldung ist keine geringe Warnstufe. Gruppiere Teilgebiete mit
  identischen Messwerten, statt sie als unabhängige Powder-Spots zu zählen.
- Die Daten enthalten keine belastbare Familienfreundlichkeitsbewertung. Nenne
  solche Treffer nur Kandidaten und keine verifizierten Familienempfehlungen.
- Fahrtzeiten von openrouteservice sind Näherungswerte ohne Live-Verkehr,
  Pausen oder Wetterlage. Wenn das Tool nicht konfiguriert ist oder keine Route
  liefert, darfst du für bekannte Start- und Zielorte ersatzweise eine grobe
  Spanne aus deinem Weltwissen nennen. Kennzeichne sie wörtlich als
  "Grobe LLM-Schätzung ohne Routing und Live-Verkehr". Nenne niemals eine
  exakte Zeit und empfehle die Prüfung mit einem Navigationsdienst. Sind Ort
  oder Strecke unklar, verzichte auf die Schätzung und frage nach.
- Vergleiche bei Fahrtzeitfragen höchstens drei zuvor ausgewählte Kandidaten.
  Behaupte ein Zeitlimit nur anhand berechneter Routen oder klar markierter
  LLM-Schätzungen; sortiere nicht stillschweigend nach Luftlinie.
- Nenne Quellen nutzerfreundlich: Bergfex-Schneedaten, den jeweiligen
  Wetteranbieter, SLF oder openrouteservice/OpenStreetMap. Erwähne niemals
  interne Datenbanken, Projekt-IDs, Dataset-/View-Namen oder andere
  Infrastrukturdetails.
- Lawinenbulletins sind regional und ersetzen niemals lokale Beurteilung,
  Sperrungen, Ausbildung oder Sicherheitsausrüstung.
- Wenn eine Quelle keine Daten liefert, sage das klar und erfinde nichts.
""".strip()


class AgentGraph:
    """Small façade around the compiled LangGraph workflow."""

    def __init__(self) -> None:
        self.graph = _compiled_graph()

    def run(self, message: str, thread_id: str) -> dict[str, Any]:
        """Run one conversational turn and return the final answer."""
        result = self.graph.invoke(
            {"messages": [HumanMessage(content=message)]},
            config=_thread_config(thread_id),
        )
        messages = result["messages"]
        return {
            "answer": _last_ai_text(messages),
            "tool_calls": _current_turn_tool_count(messages),
        }

    def run_stream(self, message: str, thread_id: str) -> Iterator[str]:
        """Stream text from assistant nodes while LangGraph runs its tool loop."""
        parts = self.graph.stream(
            {"messages": [HumanMessage(content=message)]},
            config=_thread_config(thread_id),
            stream_mode="messages",
            version="v2",
        )
        for part in parts:
            if part.get("type") != "messages":
                continue
            chunk, metadata = part["data"]
            if metadata.get("langgraph_node") != "assistant":
                continue
            text = _message_text(chunk)
            if text:
                yield text


@lru_cache(maxsize=1)
def _compiled_graph() -> CompiledStateGraph:
    """Create one stateful ReAct graph per backend process."""
    model = get_model()

    def call_model(state: MessagesState) -> dict[str, list[BaseMessage]]:
        model_with_relevant_tools = model.bind_tools(
            _tools_for_messages(state["messages"])
        )
        response = model_with_relevant_tools.invoke(
            [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
        )
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("assistant", call_model)
    builder.add_node(
        "tools",
        ToolNode(AGENT_TOOLS, handle_tool_errors=_tool_error_message),
    )
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        tools_condition,
        {"tools": "tools", END: END},
    )
    builder.add_edge("tools", "assistant")
    return builder.compile(checkpointer=InMemorySaver())


def _thread_config(thread_id: str) -> dict[str, dict[str, str]]:
    return {"configurable": {"thread_id": thread_id}}


def _tools_for_messages(messages: list[BaseMessage]) -> list[BaseTool]:
    """Expose external APIs only when the current user turn asks for them."""
    user_text = next(
        (
            _message_text(message).lower()
            for message in reversed(messages)
            if isinstance(message, HumanMessage)
        ),
        "",
    )
    selected: list[BaseTool] = [query_ski_resorts]
    weather_terms = (
        "wetter",
        "wetterprognose",
        "schneeprognose",
        "vorhersage",
        "temperatur",
        "wind",
        "sicht",
        "gefriergrenze",
        "morgen",
        "wochenende",
    )
    bulletin_terms = (
        "lawinenbulletin",
        "lawinenlage",
        "lawinenbericht",
        "lawinenprognose",
        "slf",
    )
    route_terms = (
        "fahrtzeit",
        "fahrzeit",
        "anfahrt",
        "entfernung",
        "route",
        "routing",
        "ab münchen",
        "von münchen",
        "aus münchen",
    )
    if any(term in user_text for term in weather_terms):
        selected.append(get_weather_forecast)
    if any(term in user_text for term in route_terms):
        selected.append(get_driving_route)
    if any(term in user_text for term in bulletin_terms):
        selected.append(get_avalanche_bulletin)
    return selected


def _tool_error_message(error: Exception) -> str:
    """Keep one unavailable data source from aborting the entire agent turn."""
    return (
        "Die Datenquelle ist vorübergehend nicht verfügbar. Fahre ohne dieses "
        f"Tool fort und erfinde keine Daten. Technischer Typ: {type(error).__name__}."
    )


def _last_ai_text(messages: list[BaseMessage]) -> str:
    for message in reversed(messages):
        if isinstance(message, AIMessage):
            text = _message_text(message)
            if text:
                return text
    return "Keine Antwort erhalten."


def _current_turn_tool_count(messages: list[BaseMessage]) -> int:
    last_human_index = max(
        (
            index
            for index, message in enumerate(messages)
            if isinstance(message, HumanMessage)
        ),
        default=-1,
    )
    return sum(
        isinstance(message, ToolMessage) for message in messages[last_human_index + 1 :]
    )


def _message_text(message: BaseMessage) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return ""
