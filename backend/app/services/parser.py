import re
from dataclasses import dataclass

from app.db.models.food import Food


@dataclass
class ParsedItem:
    raw_label: str
    canonical_name: str
    quantity: float
    unit: str
    calories: float
    protein: float
    carbs: float
    fat: float
    fibre: float
    confidence: float
    assumptions: dict
    food_id: int | None


@dataclass
class ParsedMeal:
    items: list[ParsedItem]
    confidence: float


WORD_TO_NUM = {
    "a": 1.0,
    "an": 1.0,
    "one": 1.0,
    "two": 2.0,
    "three": 3.0,
    "four": 4.0,
}


def _normalize_qty(token: str | None) -> float | None:
    if token is None:
        return None
    token = token.strip().lower()
    if token in WORD_TO_NUM:
        return WORD_TO_NUM[token]
    try:
        return float(token)
    except ValueError:
        return None


def _split_chunks(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text.strip().lower())
    chunks = re.split(r",| and ", cleaned)
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def parse_meal_text(text: str, alias_map: dict[str, Food]) -> ParsedMeal:
    chunks = _split_chunks(text)
    items: list[ParsedItem] = []

    for chunk in chunks:
        match = re.match(r"(?:(\d+(?:\.\d+)?)|(one|two|three|four|a|an))?\s*(.*)", chunk)
        qty_raw = match.group(1) or match.group(2) if match else None
        body = match.group(3).strip() if match else chunk
        quantity = _normalize_qty(qty_raw)

        food = alias_map.get(body)
        assumptions: dict = {}
        confidence = 0.95

        if food is None:
            matched_food = None
            for alias, candidate in alias_map.items():
                if alias in body or body in alias:
                    matched_food = candidate
                    break
            food = matched_food

        if food is None:
            # Unknown food fallback keeps logging flow fast while preserving an editable record.
            canonical_name = body
            calories = 120.0
            protein = 4.0
            carbs = 14.0
            fat = 4.0
            fibre = 2.0
            unit = "serving"
            confidence = 0.45
            assumptions["food_match"] = "unknown_fallback"
            food_id = None
        else:
            canonical_name = food.canonical_name
            unit = food.default_unit
            food_id = food.id
            if quantity is None:
                quantity = food.default_quantity
                confidence = 0.7
                assumptions["quantity"] = "defaulted"
            calories = food.calories_per_serving * quantity
            protein = food.protein_per_serving * quantity
            carbs = food.carbs_per_serving * quantity
            fat = food.fat_per_serving * quantity
            fibre = food.fibre_per_serving * quantity

        if quantity is None:
            quantity = 1.0
            confidence = min(confidence, 0.6)
            assumptions["quantity"] = "defaulted_to_1"

        items.append(
            ParsedItem(
                raw_label=chunk,
                canonical_name=canonical_name,
                quantity=quantity,
                unit=unit,
                calories=round(calories, 2),
                protein=round(protein, 2),
                carbs=round(carbs, 2),
                fat=round(fat, 2),
                fibre=round(fibre, 2),
                confidence=confidence,
                assumptions=assumptions,
                food_id=food_id,
            )
        )

    overall = round(sum(item.confidence for item in items) / len(items), 3) if items else 0.0
    return ParsedMeal(items=items, confidence=overall)
