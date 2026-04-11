from datetime import date

from sqlalchemy.orm import Session

from app.db.models.chat_message import ChatMessage
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.dashboard import get_today_dashboard


def _build_response(message: str, dashboard) -> str:
    gaps = []
    if dashboard.protein.remaining > 0:
        gaps.append(f"protein gap is about {dashboard.protein.remaining:.0f} g")
    if dashboard.fibre.remaining > 0:
        gaps.append(f"fibre gap is about {dashboard.fibre.remaining:.0f} g")
    if dashboard.calories.remaining < 0:
        gaps.append(f"you are over calories by {abs(dashboard.calories.remaining):.0f} kcal")

    gap_line = ", ".join(gaps) if gaps else "today looks balanced so far"
    prompt_hint = message.strip().lower()

    if "dinner" in prompt_hint or "eat" in prompt_hint:
        suggestions = "Try paneer + salad, dal + curd, eggs + sauteed veggies, or grilled chicken + rice."
    else:
        suggestions = "Focus on one more balanced meal and keep portions simple."

    return (
        f"Based on today's log, {gap_line}. "
        f"{suggestions} Keep logging quick entries so we can refine suggestions."
    )


def create_chat_reply(db: Session, user_id: str, payload: ChatRequest) -> ChatResponse:
    context_day = payload.context_day or date.today()
    dashboard = get_today_dashboard(db, user_id, context_day)
    reply = _build_response(payload.message, dashboard)

    db.add(ChatMessage(user_id=user_id, role="user", content=payload.message, context_day=context_day))
    db.add(ChatMessage(user_id=user_id, role="assistant", content=reply, context_day=context_day))
    db.commit()

    return ChatResponse(response=reply, context_day=context_day)
