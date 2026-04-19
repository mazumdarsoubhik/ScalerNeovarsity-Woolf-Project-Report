from __future__ import annotations

import json

from app.core.config import settings
from app.core.custom_logging import get_logger
from app.core.llm.base import LLMConnectorError
from app.core.llm.factory import get_llm_connector
from app.core.llm.types import LLMMessage, LLMRequest
from app.services.meal_parser.types import LLMExtractedItem, LLMExtraction
from app.services.meal_prompts.registry import get_system_prompt, get_user_prompt_template

logger = get_logger(__name__)


def _extract_json_blob(content: str) -> dict:
    """Extract a JSON object from raw model output."""
    stripped = content.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return json.loads(stripped)

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        return json.loads(stripped[start : end + 1])
    raise ValueError("No JSON object found in LLM output")


def _safe_float(value: object) -> float | None:
    """Convert arbitrary values into float when possible."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_str(value: object) -> str | None:
    """Convert arbitrary values into a cleaned string."""
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _parse_items(payload: dict) -> list[LLMExtractedItem]:
    """Normalize item dictionaries from LLM JSON payload."""
    raw_items = payload.get("items")
    if not isinstance(raw_items, list):
        return []

    items: list[LLMExtractedItem] = []
    for raw in raw_items:
        if not isinstance(raw, dict):
            continue
        name = _safe_str(raw.get("name"))
        raw_label = _safe_str(raw.get("raw_label")) or name
        if not name or not raw_label:
            continue

        aliases_raw = raw.get("aliases")
        aliases = [str(x).strip().lower() for x in aliases_raw if str(x).strip()] if isinstance(aliases_raw, list) else []
        confidence = _safe_float(raw.get("confidence")) or 0.5
        items.append(
            LLMExtractedItem(
                raw_label=raw_label.lower(),
                name=name.lower(),
                quantity=_safe_float(raw.get("quantity")),
                unit=_safe_str(raw.get("unit")),
                calories_per_serving=_safe_float(raw.get("calories_per_serving")),
                protein_per_serving=_safe_float(raw.get("protein_per_serving")),
                carbs_per_serving=_safe_float(raw.get("carbs_per_serving")),
                fat_per_serving=_safe_float(raw.get("fat_per_serving")),
                fibre_per_serving=_safe_float(raw.get("fibre_per_serving")),
                confidence=max(0.0, min(1.0, confidence)),
                aliases=aliases,
            )
        )
    return items


def extract_meal_with_llm(meal_text: str) -> LLMExtraction:
    """Call the configured LLM and return a structured meal extraction."""
    prompt_version = settings.meal_prompt_version
    messages = [
        LLMMessage(role="system", content=get_system_prompt(prompt_version)),
        LLMMessage(
            role="user",
            content=get_user_prompt_template(prompt_version).format(meal_text=meal_text.strip()),
        ),
    ]
    connector = get_llm_connector()
    request_payload = LLMRequest(
        messages=messages,
        model=settings.llm_model,
        temperature=0.1,
        max_tokens=settings.llm_max_tokens,
    )

    try:
        response = connector.generate(request_payload)
        payload = _extract_json_blob(response.content)
        items = _parse_items(payload)
        confidence = _safe_float(payload.get("confidence")) or 0.0
        return LLMExtraction(
            items=items,
            confidence=max(0.0, min(1.0, confidence)),
            model=response.model,
            prompt_version=prompt_version,
        )
    except (LLMConnectorError, ValueError, json.JSONDecodeError) as exc:
        logger.warning("Meal LLM extraction failed: %s", exc)
        return LLMExtraction(items=[], confidence=0.0, model=settings.llm_model, prompt_version=prompt_version)
