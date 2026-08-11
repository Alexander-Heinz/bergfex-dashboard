import logging
import os
import re
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

from server.agent.graph import AgentGraph
from server.agent.llm import AgentConfigurationError

logger = logging.getLogger(__name__)


def get_dev_or_remote_address(request: Request):
    """Bypass rate limiting on localhost or local development."""
    client_ip = request.client.host if request.client else ""
    # Skips rate limit for localhost IPs or when ENVIRONMENT is not production
    if (
        client_ip in ("127.0.0.1", "localhost", "::1")
        or os.getenv("ENVIRONMENT") != "production"
    ):
        return None
    return get_remote_address(request)


router = APIRouter()
limiter = Limiter(key_func=get_dev_or_remote_address)


class AgentRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4_000)
    thread_id: str | None = None


@router.post("", summary="Agent endpoint")
@router.post("/", summary="Agent endpoint", include_in_schema=False)
@limiter.limit("10/minute")
async def agent_endpoint(request: Request, req: AgentRequest) -> dict[str, Any]:
    """Run one agent turn and preserve context under the supplied thread ID."""
    thread_id = _thread_id(req.thread_id)
    try:
        graph = AgentGraph()
        result = await run_in_threadpool(graph.run, req.message, thread_id)
    except AgentConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Agent request failed")
        raise HTTPException(status_code=500, detail="Internal agent error") from exc

    return {
        "answer": result.get("answer", ""),
        "tool_calls": result.get("tool_calls", 0),
        "thread_id": thread_id,
    }


@router.post("/stream", summary="Streaming agent endpoint")
@limiter.limit("15/minute")
async def agent_stream_endpoint(request: Request, req: AgentRequest):
    """Stream one LangGraph turn as server-sent events."""
    import json

    thread_id = _thread_id(req.thread_id)

    def event_generator():
        try:
            graph = AgentGraph()
            for chunk in graph.run_stream(req.message, thread_id):
                yield f"data: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"
        except AgentConfigurationError as exc:
            yield f"data: {json.dumps({'text': f'Konfigurationsfehler: {exc}'}, ensure_ascii=False)}\n\n"
        except Exception:
            logger.exception("Streaming agent request failed")
            yield 'data: {"text":"Interner Agentenfehler."}\n\n'
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"X-Agent-Thread-ID": thread_id},
    )


def _thread_id(value: str | None) -> str:
    """Accept compact opaque IDs and generate one when the client has none."""
    if value is None:
        return str(uuid.uuid4())
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", value):
        raise HTTPException(status_code=422, detail="Invalid thread_id")
    return value
