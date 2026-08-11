import re
from typing import Any

from server.agent import tools


class AgentGraph:
    """Ski-trip agent graph with LLM reasoning and BigQuery tool fallback.

    Flow:
    1. Parse user message for intent.
    2. Execute BigQuery tool.
    3. Query Gemini LLM, or fall back to deterministic response marked when quota is reached.
    """

    def _parse_min_snow(self, message: str) -> int:
        """Extract a minimum snow depth in cm from the user message."""
        m = re.search(r"(mehr als|>=|>)\s*(\d{1,3})\s*cm", message, re.IGNORECASE)
        if m:
            return int(m.group(2))
        m2 = re.search(r"(\d{1,3})\s*cm", message, re.IGNORECASE)
        if m2:
            return int(m2.group(1))
        return 0

    def _format_answer(
        self,
        user_message: str,
        tool_result: dict[str, Any],
        is_quota_fallback: bool = True,
    ) -> str:
        """Build a plain-text answer from tool data (no LLM needed)."""
        total = tool_result.get("total", 0)
        resorts = tool_result.get("resorts", [])
        min_snow = tool_result.get("min_snow_depth", 0)

        header = ""
        if is_quota_fallback:
            header = "⚡ [Hinweis: Gemini-Tageslimit (Free Tier) erreicht – Automatische Antwort aus der BigQuery-Datenbank]\n\n"

        if total == 0:
            return (
                header
                + f"Ich habe keine Skigebiete mit mindestens {min_snow} cm Schnee "
                f"in der Datenbank gefunden. Versuche es mit einer niedrigeren Schneehöhe."
            )

        lines = [
            header + f"Ich habe {total} Skigebiet{'e' if total != 1 else ''} "
            f"mit mindestens {min_snow} cm Schnee am Berg gefunden:"
        ]
        for r in resorts[:10]:
            lines.append(f"• {r['name']}: {r['snowMountain']:.0f} cm")
        if total > 10:
            lines.append(f"… und {total - 10} weitere.")
        return "\n".join(lines)

    def run(self, message: str) -> dict[str, Any]:
        min_snow = self._parse_min_snow(message)
        tool_resp = tools.query_ski_resorts(min_snow_depth=min_snow, limit=10)

        answer: str
        is_quota_fallback = False
        try:
            from server.agent.llm import get_llm

            llm = get_llm()
            answer = llm.generate(message)
        except (RuntimeError, ImportError, OSError) as e:
            err_str = str(e).lower()
            is_quota_fallback = any(
                k in err_str for k in ["429", "quota", "resource_exhausted", "limit"]
            )
            print(
                f"LLM generation failed ({e}), falling back instantly (is_quota={is_quota_fallback})."
            )
            answer = self._format_answer(
                message, tool_resp, is_quota_fallback=is_quota_fallback
            )

        return {
            "answer": answer,
            "tool_calls": 1,
            "tool_result": tool_resp,
            "is_quota_fallback": is_quota_fallback,
        }

    def run_stream(self, message: str):
        """Yield text chunks for the given query using Gemini streaming or instant marked fallback."""
        min_snow = self._parse_min_snow(message)
        tool_resp = tools.query_ski_resorts(min_snow_depth=min_snow, limit=10)

        yielded_any = False
        is_quota_fallback = False
        try:
            from server.agent.llm import get_llm

            llm = get_llm()
            for chunk in llm.generate_stream(message):
                if chunk:
                    yielded_any = True
                    yield chunk
        except (RuntimeError, ImportError, OSError) as e:
            err_str = str(e).lower()
            is_quota_fallback = any(
                k in err_str for k in ["429", "quota", "resource_exhausted", "limit"]
            )
            print(
                f"LLM streaming failed ({e}), falling back instantly (is_quota={is_quota_fallback})."
            )

        if not yielded_any:
            yield self._format_answer(message, tool_resp, is_quota_fallback=True)
