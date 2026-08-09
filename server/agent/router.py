import os
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any
from slowapi import Limiter
from slowapi.util import get_remote_address
from server.agent.graph import AgentGraph

def get_dev_or_remote_address(request: Request):
    """Bypass rate limiting on localhost or local development."""
    client_ip = request.client.host if request.client else ""
    # Skips rate limit for localhost IPs or when ENVIRONMENT is not production
    if client_ip in ("127.0.0.1", "localhost", "::1") or os.getenv("ENVIRONMENT") != "production":
        return None
    return get_remote_address(request)

router = APIRouter()
limiter = Limiter(key_func=get_dev_or_remote_address)

class AgentRequest(BaseModel):
    message: str

@router.post("", summary="Agent endpoint")
@router.post("/", summary="Agent endpoint", include_in_schema=False)
@limiter.limit("10/minute")
async def agent_endpoint(request: Request, req: AgentRequest) -> Dict[str, Any]:
    """Minimal API endpoint that forwards the user's message into the agent graph.

    Returns a small JSON structure with the answer and the number of tool calls.
    """
    graph = AgentGraph()
    try:
        result = graph.run(req.message)
    except ValueError as e:
        # LLM key not configured
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal agent error")

    return {
        "answer": result.get("answer", ""),
        "tool_calls": result.get("tool_calls", 0),
        "is_quota_fallback": result.get("is_quota_fallback", False),
    }


@router.post("/stream", summary="Streaming agent endpoint")
@limiter.limit("15/minute")
async def agent_stream_endpoint(request: Request, req: AgentRequest):
    """Streaming API endpoint that streams Gemini chunks incrementally via SSE."""
    from fastapi.responses import StreamingResponse
    import json

    async def event_generator():
        graph = AgentGraph()
        try:
            for chunk in graph.run_stream(req.message):
                yield f"data: {json.dumps({'text': chunk})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'text': f'Fehler: {e}'})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
