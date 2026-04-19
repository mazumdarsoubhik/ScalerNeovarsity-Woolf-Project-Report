from datetime import date, datetime, time

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.db.models.food import Food
from app.db.models.meal import Meal
from app.db.models.meal_item import MealItem
from app.schemas.meal import (
    MealCreateRequest,
    MealHistoryEntry,
    MealHistoryResponse,
    MealItemOut,
    MealOut,
    MealTotals,
    MealUpdateRequest,
)
from app.services.dashboard import recompute_daily_summary
from app.services.food_reference import ensure_seed_foods, get_food_alias_map
from app.services.parser import ParsedItem, parse_meal_text


def _items_totals(items: list[MealItem]) -> MealTotals:
    """Compute rounded macro totals for a list of meal items."""
    return MealTotals(
        calories=round(sum(i.calories for i in items), 2),
        protein=round(sum(i.protein for i in items), 2),
        carbs=round(sum(i.carbs for i in items), 2),
        fat=round(sum(i.fat for i in items), 2),
        fibre=round(sum(i.fibre for i in items), 2),
    )


def _to_meal_out(meal: Meal) -> MealOut:
    """Transform a persisted Meal ORM object into API response schema."""
    items_out = [MealItemOut.model_validate(item) for item in meal.items]
    return MealOut(
        id=meal.id,
        original_text=meal.original_text,
        meal_type=meal.meal_type,
        eaten_at=meal.eaten_at,
        parse_confidence=meal.parse_confidence,
        totals=_items_totals(meal.items),
        items=items_out,
    )


def _parsed_to_item(parsed: ParsedItem, meal_id: str) -> MealItem:
    """Convert ParsedItem data into a MealItem ORM row."""
    return MealItem(
        meal_id=meal_id,
        food_id=parsed.food_id,
        raw_label=parsed.raw_label,
        canonical_name=parsed.canonical_name,
        quantity=parsed.quantity,
        unit=parsed.unit,
        calories=parsed.calories,
        protein=parsed.protein,
        carbs=parsed.carbs,
        fat=parsed.fat,
        fibre=parsed.fibre,
        confidence=parsed.confidence,
        assumptions=parsed.assumptions,
    )


def create_meal(db: Session, user_id: str, payload: MealCreateRequest) -> MealOut:
    """Create meal and associated meal-item rows from free text input."""
    ensure_seed_foods(db)
    alias_map = get_food_alias_map(db)
    parsed = parse_meal_text(db, payload.text, alias_map)
    if not parsed.items:
        raise ValueError("Could not parse meal text")
    meal = Meal(
        user_id=user_id,
        original_text=payload.text.strip(),
        meal_type=payload.meal_type,
        eaten_at=payload.eaten_at or datetime.utcnow(),
        parse_confidence=parsed.confidence,
    )
    db.add(meal)
    db.flush()
    for item in parsed.items:
        db.add(_parsed_to_item(item, meal.id))
    db.commit()
    db.refresh(meal)
    meal = db.scalar(select(Meal).where(Meal.id == meal.id))
    recompute_daily_summary(db, user_id, meal.eaten_at.date())
    return _to_meal_out(meal)


def _food_to_parsed_item(food: Food, quantity: float, unit: str) -> ParsedItem:
    """Build a ParsedItem from a known catalog food for manual item updates."""
    factor = quantity / max(food.default_quantity, 1e-6)
    return ParsedItem(
        raw_label=f"{quantity} {unit} {food.canonical_name}",
        canonical_name=food.canonical_name,
        quantity=quantity,
        unit=unit,
        calories=round(food.calories_per_serving * factor, 2),
        protein=round(food.protein_per_serving * factor, 2),
        carbs=round(food.carbs_per_serving * factor, 2),
        fat=round(food.fat_per_serving * factor, 2),
        fibre=round(food.fibre_per_serving * factor, 2),
        confidence=0.9,
        assumptions={"source": "manual_update"},
        food_id=food.id,
    )


def update_meal(db: Session, user_id: str, meal_id: str, payload: MealUpdateRequest) -> MealOut | None:
    """Update meal metadata and optionally re-parse or replace meal items."""
    meal = db.scalar(select(Meal).where(and_(Meal.id == meal_id, Meal.user_id == user_id)))
    if meal is None:
        return None
    old_day = meal.eaten_at.date()

    if payload.meal_type is not None:
        meal.meal_type = payload.meal_type
    if payload.eaten_at is not None:
        meal.eaten_at = payload.eaten_at

    if payload.text is not None:
        ensure_seed_foods(db)
        alias_map = get_food_alias_map(db)
        parsed = parse_meal_text(db, payload.text, alias_map)
        if not parsed.items:
            raise ValueError("Could not parse meal text")
        meal.original_text = payload.text.strip()
        meal.parse_confidence = parsed.confidence
        for existing in list(meal.items):
            db.delete(existing)
        db.flush()
        for parsed_item in parsed.items:
            db.add(_parsed_to_item(parsed_item, meal.id))

    if payload.items is not None:
        ensure_seed_foods(db)
        alias_map = get_food_alias_map(db)
        for existing in list(meal.items):
            db.delete(existing)
        db.flush()
        new_items = []
        for manual in payload.items:
            food = alias_map.get(manual.canonical_name.lower())
            if food is None:
                continue
            parsed_item = _food_to_parsed_item(food, manual.quantity, manual.unit)
            db.add(_parsed_to_item(parsed_item, meal.id))
            new_items.append(parsed_item)
        if new_items:
            meal.original_text = ", ".join([i.raw_label for i in new_items])
            meal.parse_confidence = round(sum(x.confidence for x in new_items) / len(new_items), 3)
        else:
            raise ValueError("No valid food names found in manual items")

    db.commit()
    meal = db.scalar(select(Meal).where(Meal.id == meal.id))
    recompute_daily_summary(db, user_id, old_day)
    recompute_daily_summary(db, user_id, meal.eaten_at.date())
    return _to_meal_out(meal)


def delete_meal(db: Session, user_id: str, meal_id: str) -> bool:
    """Delete one meal and refresh the daily summary for that day."""
    meal = db.scalar(select(Meal).where(and_(Meal.id == meal_id, Meal.user_id == user_id)))
    if meal is None:
        return False
    day = meal.eaten_at.date()
    db.delete(meal)
    db.commit()
    recompute_daily_summary(db, user_id, day)
    return True


def get_meal_history(
    db: Session,
    user_id: str,
    start_day: date | None,
    end_day: date | None,
    limit: int,
    offset: int,
) -> MealHistoryResponse:
    """Return paginated meal history with optional date-range filtering."""
    query = select(Meal).where(Meal.user_id == user_id)
    if start_day is not None:
        query = query.where(Meal.eaten_at >= datetime.combine(start_day, time.min))
    if end_day is not None:
        query = query.where(Meal.eaten_at <= datetime.combine(end_day, time.max))

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    meals = db.scalars(query.order_by(Meal.eaten_at.desc()).offset(offset).limit(limit)).all()
    entries = [
        MealHistoryEntry(
            id=meal.id,
            meal_type=meal.meal_type,
            eaten_at=meal.eaten_at,
            original_text=meal.original_text,
            parse_confidence=meal.parse_confidence,
            totals=_items_totals(meal.items),
        )
        for meal in meals
    ]
    return MealHistoryResponse(items=entries, total=int(total))
