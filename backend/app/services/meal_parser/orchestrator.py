from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.custom_logging import get_logger
from app.db.models.food import Food
from app.services.meal_parser.fallback_parser import parse_meal_text_with_rules
from app.services.meal_parser.llm_extractor import extract_meal_with_llm
from app.services.meal_parser.normalizer import normalize_extracted_item
from app.services.meal_parser.types import ParsedMeal

logger = get_logger(__name__)


def _should_use_fallback(parsed: ParsedMeal, llm_confidence: float) -> bool:
    """Decide whether parser should fall back to deterministic rules."""
    if not parsed.items:
        return True
    if llm_confidence < settings.meal_llm_min_confidence:
        return True
    avg_item_conf = sum(item.confidence for item in parsed.items) / len(parsed.items)
    return avg_item_conf < settings.meal_llm_min_confidence


def parse_meal_text(db: Session, text: str, alias_map: dict[str, Food]) -> ParsedMeal:
    """Parse meal text using configured mode, preferring LLM with safe fallback."""
    mode = settings.meal_parser_mode.strip().lower()
    if mode == "rule_only":
        return parse_meal_text_with_rules(text, alias_map)

    llm_extraction = extract_meal_with_llm(text)
    llm_items = [
        normalize_extracted_item(
            db,
            item,
            alias_map,
            source_model=llm_extraction.model,
            prompt_version=llm_extraction.prompt_version,
        )
        for item in llm_extraction.items
    ]
    llm_parsed = ParsedMeal(
        items=llm_items,
        confidence=round(sum(item.confidence for item in llm_items) / len(llm_items), 3) if llm_items else 0.0,
    )

    if mode == "llm_only":
        return llm_parsed

    if _should_use_fallback(llm_parsed, llm_extraction.confidence):
        logger.info(
            "Meal parser fallback triggered (mode=%s llm_conf=%.2f items=%s)",
            mode,
            llm_extraction.confidence,
            len(llm_parsed.items),
        )
        return parse_meal_text_with_rules(text, alias_map)

    logger.info(
        "Meal parsed by LLM (mode=%s llm_conf=%.2f items=%s)",
        mode,
        llm_extraction.confidence,
        len(llm_parsed.items),
    )
    return llm_parsed
