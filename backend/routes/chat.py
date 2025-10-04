from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.agent import get_agent_response

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    """
    Simple POST endpoint that takes a user message and returns the agent's reply.
    """
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        output = await get_agent_response(payload.message)
        return ChatResponse(response=output)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")
