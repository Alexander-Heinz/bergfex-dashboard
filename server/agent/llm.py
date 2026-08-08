import os
from typing import Any

GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
GEMINI_MODEL_ENV = "GEMINI_MODEL"

class GeminiLLM:
    """Minimal wrapper for a Gemini LLM client.

    This wrapper checks for the presence of the GEMINI_API_KEY environment
    variable. It does not attempt a real API call here — for Phase 1 we
    keep the integration surface small so tests can mock behavior.
    """
    def __init__(self):
        self.api_key = os.getenv(GEMINI_API_KEY_ENV)
        self.model = os.getenv(GEMINI_MODEL_ENV, "gemini-proto")
        if not self.api_key:
            # Fail early when someone attempts to use the LLM without a key.
            raise ValueError("GEMINI_API_KEY not set. Set the GEMINI_API_KEY environment variable to use the agent.")

    def generate(self, prompt: str) -> str:
        """Generate a response for the given prompt.

        In Phase 1 this method is intentionally simple. In later phases this
        will call the real Gemini API via LangChain.
        """
        # Placeholder behaviour: real implementation should call the Gemini API
        # via LangChain. Keeping this minimal allows tests to mock GeminiLLM.
        return f"(Gemini mock) Generated answer for prompt: {prompt}"


# Factory
def get_llm() -> GeminiLLM:
    return GeminiLLM()
