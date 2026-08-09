import os
import inspect

GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
GEMINI_MODEL_ENV = "GEMINI_MODEL"

# Ordered model fallback list. Lite models have higher free-tier limits (1500 req/day)
# vs standard models (~20 req/day). Ordered by measured response time & quota availability:
# gemini-flash-lite-latest: 0.7s, large free quota
# gemini-3.5-flash-lite:    3.8s, large free quota
# gemini-flash-latest:      ~22s, separate quota
# gemini-3.5-flash:         ~20 req/day limit (exhausts quickly)
MODELS_TO_TRY = [
    os.getenv(GEMINI_MODEL_ENV, "gemini-flash-lite-latest"),
    "gemini-3.5-flash-lite",
    "gemini-flash-latest",
    "gemini-3.5-flash",
]

# HTTP status codes that indicate quota/rate-limit — fail immediately, no retries
_QUOTA_STATUS_CODES = {429}
_QUOTA_KEYWORDS = ("resource_exhausted", "quota", "429")


def _is_quota_error(exc: Exception) -> bool:
    """Return True if the exception is a rate-limit / quota error."""
    msg = str(exc).lower()
    return any(kw in msg for kw in _QUOTA_KEYWORDS)


class GeminiLLM:
    """Wrapper for Google Gemini LLM client.

    Checks for GEMINI_API_KEY in environment variables or fetches it
    dynamically from Google Cloud Secret Manager.
    """

    def __init__(self):
        self.api_key = os.getenv(GEMINI_API_KEY_ENV)

        if not self.api_key:
            try:
                from google.cloud import secretmanager
                from google.oauth2 import service_account
                import json

                project_id = os.getenv("GCP_PROJECT_ID", "bergfex-481612")
                credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")

                if credentials_json:
                    credentials_info = json.loads(credentials_json)
                    credentials = service_account.Credentials.from_service_account_info(
                        credentials_info
                    )
                    client = secretmanager.SecretManagerServiceClient(
                        credentials=credentials
                    )
                else:
                    client = secretmanager.SecretManagerServiceClient()

                name = f"projects/{project_id}/secrets/GEMINI_API_KEY/versions/latest"
                response = client.access_secret_version(request={"name": name})
                self.api_key = response.payload.data.decode("UTF-8").strip()

                os.environ[GEMINI_API_KEY_ENV] = self.api_key
                print("Successfully loaded GEMINI_API_KEY from GCP Secret Manager.")
            except Exception as e:
                print(f"Failed to fetch GEMINI_API_KEY from Secret Manager: {e}")

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not set. Please set the GEMINI_API_KEY environment variable "
                "or configure it in GCP Secret Manager to use the agent."
            )

    def _get_tools(self):
        from . import tools as tool_mod
        return [
            attr
            for attr_name in dir(tool_mod)
            if not attr_name.startswith("_")
            and inspect.isfunction(attr := getattr(tool_mod, attr_name))
            and attr.__module__ == tool_mod.__name__
        ]

    def _make_client(self):
        from google import genai
        # Disable tenacity retries so quota errors fail immediately
        return genai.Client(
            api_key=self.api_key,
            http_options={"timeout": 15_000},  # 15s hard timeout per request
        )

    def generate(self, prompt: str) -> str:
        """Generate a response using Gemini with immediate quota detection."""
        client = self._make_client()
        tool_fns = self._get_tools()
        config = {"tools": tool_fns} if tool_fns else None

        last_err = None
        for model in MODELS_TO_TRY:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config,
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                last_err = e
                if _is_quota_error(e):
                    print(f"Gemini quota/rate-limit on {model}, trying next model immediately…")
                    continue
                # Non-quota errors: also try fallback but log differently
                print(f"Gemini model {model} error ({e}), trying fallback…")
                continue

        raise RuntimeError(f"All Gemini models failed: {last_err}")

    def generate_stream(self, prompt: str):
        """Yield text chunks incrementally with immediate quota detection and model fallback."""
        client = self._make_client()
        tool_fns = self._get_tools()
        config = {"tools": tool_fns} if tool_fns else None

        last_err = None
        for model in MODELS_TO_TRY:
            try:
                response_stream = client.models.generate_content_stream(
                    model=model,
                    contents=prompt,
                    config=config,
                )
                has_chunks = False
                for chunk in response_stream:
                    if chunk and chunk.text:
                        has_chunks = True
                        yield chunk.text
                if has_chunks:
                    return
                # Stream returned but yielded nothing (e.g. only function calls)
                last_err = RuntimeError(f"Model {model} returned no text chunks")
            except Exception as e:
                last_err = e
                if _is_quota_error(e):
                    print(f"Gemini quota/rate-limit on {model}, trying next model immediately…")
                    continue
                print(f"Streaming model {model} error ({e}), trying fallback…")
                continue

        raise RuntimeError(f"All streaming models failed: {last_err}")


def get_llm() -> GeminiLLM:
    return GeminiLLM()
