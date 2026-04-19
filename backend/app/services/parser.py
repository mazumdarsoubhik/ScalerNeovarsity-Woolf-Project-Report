from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models.food import Food
from app.services.meal_parser.orchestrator import parse_meal_text as parse_meal_text_orchestrated
from app.services.meal_parser.types import ParsedItem, ParsedMeal


def parse_meal_text(db: Session, text: str, alias_map: dict[str, Food]) -> ParsedMeal:
    """Parse meal text through the configured parser orchestration flow."""
    return parse_meal_text_orchestrated(db, text, alias_map)


__all__ = ["ParsedItem", "ParsedMeal", "parse_meal_text"]
