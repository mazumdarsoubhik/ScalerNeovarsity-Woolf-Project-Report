from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.food import Food


SEED_FOODS = [
    {
        "canonical_name": "roti",
        "aliases_csv": "chapati,phulka",
        "default_quantity": 1,
        "default_unit": "piece",
        "calories_per_serving": 110,
        "protein_per_serving": 3.0,
        "carbs_per_serving": 18.0,
        "fat_per_serving": 2.5,
        "fibre_per_serving": 2.0,
    },
    {
        "canonical_name": "dal",
        "aliases_csv": "lentils,daal",
        "default_quantity": 1,
        "default_unit": "bowl",
        "calories_per_serving": 180,
        "protein_per_serving": 10.0,
        "carbs_per_serving": 26.0,
        "fat_per_serving": 3.0,
        "fibre_per_serving": 8.0,
    },
    {
        "canonical_name": "paneer sabzi",
        "aliases_csv": "paneer curry,paneer",
        "default_quantity": 1,
        "default_unit": "bowl",
        "calories_per_serving": 260,
        "protein_per_serving": 14.0,
        "carbs_per_serving": 8.0,
        "fat_per_serving": 18.0,
        "fibre_per_serving": 2.0,
    },
    {
        "canonical_name": "curd",
        "aliases_csv": "yogurt,dahi",
        "default_quantity": 1,
        "default_unit": "bowl",
        "calories_per_serving": 100,
        "protein_per_serving": 5.0,
        "carbs_per_serving": 7.0,
        "fat_per_serving": 4.0,
        "fibre_per_serving": 0.0,
    },
    {
        "canonical_name": "rice",
        "aliases_csv": "white rice,steamed rice",
        "default_quantity": 1,
        "default_unit": "bowl",
        "calories_per_serving": 200,
        "protein_per_serving": 4.0,
        "carbs_per_serving": 44.0,
        "fat_per_serving": 0.5,
        "fibre_per_serving": 0.6,
    },
    {
        "canonical_name": "chicken",
        "aliases_csv": "grilled chicken,chicken curry",
        "default_quantity": 1,
        "default_unit": "serving",
        "calories_per_serving": 240,
        "protein_per_serving": 27.0,
        "carbs_per_serving": 3.0,
        "fat_per_serving": 12.0,
        "fibre_per_serving": 0.0,
    },
    {
        "canonical_name": "egg",
        "aliases_csv": "eggs,boiled egg",
        "default_quantity": 1,
        "default_unit": "piece",
        "calories_per_serving": 78,
        "protein_per_serving": 6.3,
        "carbs_per_serving": 0.6,
        "fat_per_serving": 5.3,
        "fibre_per_serving": 0.0,
    },
    {
        "canonical_name": "milk",
        "aliases_csv": "toned milk",
        "default_quantity": 1,
        "default_unit": "glass",
        "calories_per_serving": 130,
        "protein_per_serving": 8.0,
        "carbs_per_serving": 12.0,
        "fat_per_serving": 5.0,
        "fibre_per_serving": 0.0,
    },
]


def ensure_seed_foods(db: Session) -> None:
    any_food = db.scalar(select(Food.id).limit(1))
    if any_food:
        return
    for seed in SEED_FOODS:
        db.add(Food(**seed))
    db.commit()


def get_food_alias_map(db: Session) -> dict[str, Food]:
    foods = db.scalars(select(Food)).all()
    alias_map: dict[str, Food] = {}
    for food in foods:
        alias_map[food.canonical_name.lower()] = food
        aliases = [x.strip().lower() for x in food.aliases_csv.split(",") if x.strip()]
        for alias in aliases:
            alias_map[alias] = food
    return alias_map
