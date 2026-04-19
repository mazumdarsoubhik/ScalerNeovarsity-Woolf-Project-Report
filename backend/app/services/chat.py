from datetime import date

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.custom_logging import get_logger
from app.core.llm.base import LLMConnectorError
from app.core.llm.factory import get_llm_connector
from app.core.llm.types import LLMMessage, LLMRequest
from app.db.models.chat_message import ChatMessage
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.dashboard import get_today_dashboard

logger = get_logger(__name__)


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


def _build_llm_messages(message: str, dashboard) -> list[LLMMessage]:
    system_content = (
        "You are a practical nutrition assistant for NutriFlow. "
        "Give concise, safe meal suggestions. Avoid medical diagnoses. "
        "Use plain language and actionable next meal guidance."
    )
    context_content = (
        f"Today's nutrition summary: "
        f"Calories remaining: {dashboard.calories.remaining:.0f} kcal, "
        f"Protein remaining: {dashboard.protein.remaining:.0f} g, "
        f"Fibre remaining: {dashboard.fibre.remaining:.0f} g."
    )
    user_content = f"User message: {message}"

    return [
        LLMMessage(role="system", content=system_content),
        LLMMessage(role="user", content=f"{context_content}\n{user_content}"),
    ]


def _build_llm_response(message: str, dashboard) -> str:
    connector = get_llm_connector()
    request_payload = LLMRequest(
        messages=_build_llm_messages(message, dashboard),
        model=settings.llm_model,
        temperature=0.3,
        max_tokens=settings.llm_max_tokens,
    )
    result = connector.generate(request_payload)
    return result.content


def create_chat_reply(db: Session, user_id: str, payload: ChatRequest) -> ChatResponse:
    context_day = payload.context_day or date.today()
    dashboard = get_today_dashboard(db, user_id, context_day)
    reply = _build_response(payload.message, dashboard)

    if settings.llm_enabled:
        try:
            llm_reply = _build_llm_response(payload.message, dashboard)
            if llm_reply:
                reply = llm_reply
        except LLMConnectorError as exc:
            logger.warning("LLM connector failed, using fallback response: %s", exc)

    db.add(ChatMessage(user_id=user_id, role="user", content=payload.message, context_day=context_day))
    db.add(ChatMessage(user_id=user_id, role="assistant", content=reply, context_day=context_day))
    db.commit()

    return ChatResponse(response=reply, context_day=context_day)
