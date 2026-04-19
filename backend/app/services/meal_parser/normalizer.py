from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models.food import Food
from app.services.food_learning import CandidateNutrition, upsert_food_candidate
from app.services.meal_parser.types import LLMExtractedItem, ParsedItem


def _resolve_food(item: LLMExtractedItem, alias_map: dict[str, Food]) -> Food | None:
    """Resolve a canonical food from alias map using exact and loose matching."""
    for key in [item.name, *item.aliases]:
        candidate = alias_map.get(key.lower())
        if candidate is not None:
            return candidate

    for alias, food in alias_map.items():
        if alias in item.name or item.name in alias:
            return food
    return None


def _safe_quantity(quantity: float | None, fallback: float = 1.0) -> float:
    """Normalize quantity values into a sane positive range."""
    if quantity is None:
        return fallback
    return max(0.1, min(10.0, quantity))


def _safe_macro(value: float | None, fallback: float) -> float:
    """Normalize macro numbers with non-negative bounds."""
    if value is None:
        return fallback
    return max(0.0, value)


def normalize_extracted_item(
    db: Session,
    item: LLMExtractedItem,
    alias_map: dict[str, Food],
    *,
    source_model: str,
    prompt_version: str,
) -> ParsedItem:
    """Convert one LLM item into a ParsedItem with deterministic or candidate-backed macros."""
    food = _resolve_food(item, alias_map)
    quantity = _safe_quantity(item.quantity, fallback=1.0)
    unit = (item.unit or "serving").strip().lower()
    assumptions = {"parse_source": "llm_parser", "prompt_version": prompt_version}

    if food is not None:
        assumptions["food_match"] = "catalog"
        assumptions["matched_food"] = food.canonical_name
        assumptions["llm_confidence"] = item.confidence
        if item.quantity is None:
            quantity = _safe_quantity(food.default_quantity, fallback=1.0)
            assumptions["quantity"] = "defaulted_from_catalog"
        unit = food.default_unit
        factor = quantity / max(food.default_quantity, 1e-6)
        return ParsedItem(
            raw_label=item.raw_label,
            canonical_name=food.canonical_name,
            quantity=quantity,
            unit=unit,
            calories=round(food.calories_per_serving * factor, 2),
            protein=round(food.protein_per_serving * factor, 2),
            carbs=round(food.carbs_per_serving * factor, 2),
            fat=round(food.fat_per_serving * factor, 2),
            fibre=round(food.fibre_per_serving * factor, 2),
            confidence=max(0.0, min(1.0, item.confidence)),
            assumptions=assumptions,
            food_id=food.id,
        )

    nutrition = CandidateNutrition(
        calories_per_serving=_safe_macro(item.calories_per_serving, 120.0),
        protein_per_serving=_safe_macro(item.protein_per_serving, 4.0),
        carbs_per_serving=_safe_macro(item.carbs_per_serving, 14.0),
        fat_per_serving=_safe_macro(item.fat_per_serving, 4.0),
        fibre_per_serving=_safe_macro(item.fibre_per_serving, 2.0),
    )
    candidate = upsert_food_candidate(
        db,
        name_raw=item.raw_label,
        proposed_canonical_name=item.name,
        aliases=item.aliases,
        default_quantity=1.0,
        default_unit=unit,
        nutrition=nutrition,
        source_model=source_model,
        prompt_version=prompt_version,
        confidence=item.confidence,
    )
    assumptions["food_match"] = "candidate"
    assumptions["candidate_id"] = candidate.id
    assumptions["llm_confidence"] = item.confidence
    return ParsedItem(
        raw_label=item.raw_label,
        canonical_name=item.name,
        quantity=quantity,
        unit=unit,
        calories=round(nutrition.calories_per_serving * quantity, 2),
        protein=round(nutrition.protein_per_serving * quantity, 2),
        carbs=round(nutrition.carbs_per_serving * quantity, 2),
        fat=round(nutrition.fat_per_serving * quantity, 2),
        fibre=round(nutrition.fibre_per_serving * quantity, 2),
        confidence=max(0.0, min(1.0, item.confidence)),
        assumptions=assumptions,
        food_id=None,
    )
