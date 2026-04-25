from datetime import date, datetime, time, timedelta

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.custom_logging import get_logger
from app.core.llm.base import LLMConnectorError
from app.core.llm.factory import get_llm_connector
from app.core.llm.types import LLMMessage, LLMRequest
from app.db.models.chat_message import ChatMessage
from app.db.models.meal import Meal
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.dashboard import get_today_dashboard

logger = get_logger(__name__)
MAX_CHAT_HISTORY_MESSAGES = 8
MAX_MEAL_HISTORY_ENTRIES = 12
MEAL_CONTEXT_DAYS = 7


def _build_response(message: str, dashboard) -> str:
    """Build deterministic fallback response when LLM is disabled or fails."""
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


def _system_prompt() -> str:
    """Return system instruction for nutrition chat behavior."""
    return (
        "You are a practical nutrition assistant for NutriFlow. "
        "Give concise, safe meal suggestions. Avoid medical diagnoses. "
        "Use plain language and actionable next meal guidance. "
        "Prioritize the provided meal history and recent chat context."
    )


def _context_prompt(dashboard) -> str:
    """Render structured nutrition dashboard context for the model."""
    return (
        f"Today's nutrition summary: "
        f"Calories remaining: {dashboard.calories.remaining:.0f} kcal, "
        f"Protein remaining: {dashboard.protein.remaining:.0f} g, "
        f"Fibre remaining: {dashboard.fibre.remaining:.0f} g."
    )


def _recent_chat_messages_prompt(current_message: str) -> list[LLMMessage]:
    """Return current-user message as the final prompt turn."""
    return [LLMMessage(role="user", content=f"User message: {current_message}")]


def _fetch_recent_meals(db: Session, user_id: str, context_day: date) -> list[Meal]:
    """Fetch recent meals ending at context_day for chat grounding."""
    end_dt = datetime.combine(context_day, time.max)
    start_dt = datetime.combine(context_day - timedelta(days=MEAL_CONTEXT_DAYS - 1), time.min)
    return db.scalars(
        select(Meal)
        .where(and_(Meal.user_id == user_id, Meal.eaten_at >= start_dt, Meal.eaten_at <= end_dt))
        .order_by(Meal.eaten_at.desc())
        .limit(MAX_MEAL_HISTORY_ENTRIES)
    ).all()


def _format_recent_meals_context(meals: list[Meal]) -> str:
    """Format recent meals into compact lines for prompt context."""
    if not meals:
        return "Recent meals: none logged in the selected context window."

    lines: list[str] = []
    for meal in meals:
        totals = {
            "cal": round(sum(item.calories for item in meal.items), 1),
            "p": round(sum(item.protein for item in meal.items), 1),
            "c": round(sum(item.carbs for item in meal.items), 1),
            "f": round(sum(item.fat for item in meal.items), 1),
            "fi": round(sum(item.fibre for item in meal.items), 1),
        }
        meal_label = meal.meal_type or "meal"
        lines.append(
            f"- {meal.eaten_at.date().isoformat()} {meal_label}: {meal.original_text} "
            f"(kcal {totals['cal']}, p {totals['p']}, c {totals['c']}, f {totals['f']}, fi {totals['fi']})"
        )
    return "Recent meals:\n" + "\n".join(lines)


def _fetch_recent_chat_messages(db: Session, user_id: str) -> list[ChatMessage]:
    """Fetch recent chat history for continuity in LLM responses."""
    messages = db.scalars(
        select(ChatMessage)
        .where(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(MAX_CHAT_HISTORY_MESSAGES)
    ).all()
    return list(reversed(messages))


def _build_llm_messages_with_context(
    *,
    message: str,
    dashboard,
    meals_context: str,
    recent_chat_messages: list[ChatMessage],
) -> list[LLMMessage]:
    """Build final model messages including dashboard, meals, and prior chat turns."""
    system_content = (
        _system_prompt()
    )
    context_content = f"{_context_prompt(dashboard)}\n{meals_context}"

    messages: list[LLMMessage] = [LLMMessage(role="system", content=system_content)]
    messages.append(LLMMessage(role="user", content=context_content))

    for chat_msg in recent_chat_messages:
        role = "assistant" if chat_msg.role == "assistant" else "user"
        messages.append(LLMMessage(role=role, content=chat_msg.content))

    messages.extend(_recent_chat_messages_prompt(message))
    return messages


def _build_llm_response(
    *,
    db: Session,
    user_id: str,
    context_day: date,
    message: str,
    dashboard,
) -> str:
    """Generate LLM response using dashboard summary, meal history, and prior chat context."""
    connector = get_llm_connector()
    recent_meals = _fetch_recent_meals(db, user_id, context_day)
    meals_context = _format_recent_meals_context(recent_meals)
    recent_chat_messages = _fetch_recent_chat_messages(db, user_id)
    logger.info(
        "Building chat LLM context (meals=%s recent_messages=%s day=%s)",
        len(recent_meals),
        len(recent_chat_messages),
        context_day.isoformat(),
    )
    request_payload = LLMRequest(
        messages=_build_llm_messages_with_context(
            message=message,
            dashboard=dashboard,
            meals_context=meals_context,
            recent_chat_messages=recent_chat_messages,
        ),
        model=settings.llm_model,
        temperature=0.3,
        max_tokens=settings.llm_max_tokens,
    )
    result = connector.generate(request_payload)
    return result.content


def create_chat_reply(db: Session, user_id: str, payload: ChatRequest) -> ChatResponse:
    """Create one assistant reply, persisting user and assistant chat messages."""
    context_day = payload.context_day or date.today()
    dashboard = get_today_dashboard(db, user_id, context_day)
    reply = _build_response(payload.message, dashboard)

    if settings.llm_enabled:
        try:
            llm_reply = _build_llm_response(
                db=db,
                user_id=user_id,
                context_day=context_day,
                message=payload.message,
                dashboard=dashboard,
            )
            if llm_reply:
                reply = llm_reply
        except LLMConnectorError as exc:
            logger.warning("LLM connector failed, using fallback response: %s", exc)

    db.add(ChatMessage(user_id=user_id, role="user", content=payload.message, context_day=context_day))
    db.add(ChatMessage(user_id=user_id, role="assistant", content=reply, context_day=context_day))
    db.commit()

    return ChatResponse(response=reply, context_day=context_day)
