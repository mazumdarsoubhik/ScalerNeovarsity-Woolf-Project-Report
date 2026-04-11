from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_user_id
from app.core.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import create_chat_reply
from app.services.users import ensure_user_and_goal

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id),
) -> ChatResponse:
    ensure_user_and_goal(db, user_id)
    return create_chat_reply(db, user_id, payload)
