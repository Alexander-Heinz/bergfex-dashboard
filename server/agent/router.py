from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from server.agent.graph import AgentGraph

router = APIRouter()

class AgentRequest(BaseModel):
    message: str

@router.post("/", summary="Agent endpoint")
async def agent_endpoint(req: AgentRequest) -> Dict[str, Any]:
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

    return {"answer": result.get("answer", ""), "tool_calls": result.get("tool_calls", 0)}
