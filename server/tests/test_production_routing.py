import importlib
import sys
from pathlib import Path

from google.cloud import bigquery


def test_agent_stream_post_route_is_registered(monkeypatch) -> None:
    """Ensure production imports expose the POST route instead of the SPA fallback."""
    monkeypatch.setattr(bigquery, "Client", lambda *args, **kwargs: object())
    sys.modules.pop("server.server", None)

    backend = importlib.import_module("server.server")
    openapi_paths = backend.app.openapi()["paths"]

    assert "post" in openapi_paths["/api/agent/stream"]


def test_docker_preserves_the_server_package_layout() -> None:
    """Guard the package layout required by imports such as server.agent."""
    repository_root = Path(__file__).resolve().parents[2]
    dockerfile = (repository_root / "Dockerfile").read_text(encoding="utf-8")

    assert "COPY server/ /app/server/" in dockerfile
    assert "uvicorn server.server:app" in dockerfile
