import re
from typing import Dict, Any
from server.agent import tools
from server.agent.llm import get_llm

class AgentGraph:
    """A minimal LangGraph-like orchestrator for Phase 1.

    Responsibilities:
    - Parse the user's message for simple structured intent (e.g., minimum snow depth)
    - Call the controlled tool (query_ski_resorts)
    - Use the LLM to format the final answer

    This keeps the orchestration explicit and small so additional tools can be
    added later.
    """

    def __init__(self):
        # LLM is created lazily to allow the application to start without the key.
        self._llm = None

    def _parse_min_snow(self, message: str) -> int:
        # Heuristic: look for a number followed by 'cm' and 'Schnee' or just 'mehr als X'
        m = re.search(r"(mehr als|>=|>)\s*(\d{1,3})\s*cm", message, re.IGNORECASE)
        if m:
            return int(m.group(2))
        m2 = re.search(r"(\d{1,3})\s*cm", message, re.IGNORECASE)
        if m2:
            return int(m2.group(1))
        # Default
        return 0

    def _make_prompt(self, user_message: str, tool_result: Dict[str, Any]) -> str:
        # Hand the tool result back to the LLM as structured text.
        total = tool_result.get("total", 0)
        resorts = tool_result.get("resorts", [])
        lines = [f"User asked: {user_message}", f"Found {total} resorts matching the criteria:"]
        for r in resorts[:10]:
            lines.append(f"- {r['name']} ({r['snowMountain']} cm on the mountain)")
        if total == 0:
            lines.append("No resorts matched the criteria.")
        return "\n".join(lines)

    def run(self, message: str) -> Dict[str, Any]:
        # 1) Parse structured params
        min_snow = self._parse_min_snow(message)

        # 2) Call tool
        tool_resp = tools.query_ski_resorts(min_snow_depth=min_snow, limit=10)

        # 3) Ask LLM to produce a user-facing answer
        # Instantiate LLM (may raise if API key missing)
        if self._llm is None:
            self._llm = get_llm()

        prompt = self._make_prompt(message, tool_resp)
        llm_answer = self._llm.generate(prompt)

        return {
            "answer": llm_answer,
            "tool_calls": 1,
            "tool_result": tool_resp,
        }
