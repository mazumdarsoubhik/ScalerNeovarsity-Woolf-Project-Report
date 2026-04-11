from datetime import date

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=2, max_length=800)
    context_day: date | None = None


class ChatResponse(BaseModel):
    response: str
    context_day: date
