"""Gemini model configuration for the LangGraph agent."""

import os

from langchain_google_genai import ChatGoogleGenerativeAI

DEFAULT_MODEL = "gemini-3.5-flash-lite"


class AgentConfigurationError(ValueError):
    """Raised when the agent cannot be configured from environment variables."""


def get_model() -> ChatGoogleGenerativeAI:
    """Create the LangChain Gemini chat model used by the agent graph."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise AgentConfigurationError(
            "GEMINI_API_KEY ist nicht gesetzt. Hinterlege den Schlüssel als Secret "
            "Environment Variable bei Render."
        )

    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", DEFAULT_MODEL),
        google_api_key=api_key,
        temperature=0.2,
        max_retries=2,
    )
