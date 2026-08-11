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
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from server.agent.llm import get_model
from server.agent.tools import AGENT_TOOLS

SYSTEM_PROMPT = """
Du bist ein deutschsprachiger Ski-Trip-Datenagent. Antworte kompakt, konkret und
kennzeichne Datenquellen sowie Zeitstände. Nutze query_ski_resorts zuerst, wenn
es um Empfehlungen oder den Vergleich von Skigebieten geht. Reichere nur eine
kleine Shortlist mit get_weather_forecast und – für Schweizer Koordinaten –
get_avalanche_bulletin an. Der Shred Score wird von der bestehenden Datenpipeline
berechnet; erfinde oder verändere ihn nicht.

Wichtige Grenzen:
- Es gibt noch kein Routing- oder Fahrzeit-Tool. Behaupte deshalb keine
  Routenberechnung und sage transparent, wenn diese Daten fehlen.
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
    model_with_tools = get_model().bind_tools(AGENT_TOOLS)

    def call_model(state: MessagesState) -> dict[str, list[BaseMessage]]:
        response = model_with_tools.invoke(
            [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
        )
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("assistant", call_model)
    builder.add_node("tools", ToolNode(AGENT_TOOLS))
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
