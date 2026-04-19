from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.custom_logging import get_logger
from app.db.models.food_candidate import FoodCandidate

logger = get_logger(__name__)


@dataclass(frozen=True)
class CandidateNutrition:
    """Nutrition proposal for one default serving of an unknown food."""

    calories_per_serving: float
    protein_per_serving: float
    carbs_per_serving: float
    fat_per_serving: float
    fibre_per_serving: float


def _canonical_candidate_key(name: str, unit: str) -> str:
    """Build a stable dedupe key for unknown-food candidates."""
    return f"{name.strip().lower()}::{unit.strip().lower()}"


def _clamp(value: float, low: float, high: float) -> float:
    """Clamp numeric values into safe ingestion bounds."""
    return max(low, min(high, value))


def _sanitize_nutrition(nutrition: CandidateNutrition) -> CandidateNutrition:
    """Apply safe caps so bad model outputs do not poison the candidate catalog."""
    return CandidateNutrition(
        calories_per_serving=_clamp(nutrition.calories_per_serving, 0.0, 1200.0),
        protein_per_serving=_clamp(nutrition.protein_per_serving, 0.0, 120.0),
        carbs_per_serving=_clamp(nutrition.carbs_per_serving, 0.0, 200.0),
        fat_per_serving=_clamp(nutrition.fat_per_serving, 0.0, 120.0),
        fibre_per_serving=_clamp(nutrition.fibre_per_serving, 0.0, 80.0),
    )


def upsert_food_candidate(
    db: Session,
    *,
    name_raw: str,
    proposed_canonical_name: str,
    aliases: list[str],
    default_quantity: float,
    default_unit: str,
    nutrition: CandidateNutrition,
    source_model: str,
    prompt_version: str,
    confidence: float,
) -> FoodCandidate:
    """Create or refresh a food candidate from an LLM parse result."""
    candidate_key = _canonical_candidate_key(proposed_canonical_name, default_unit)
    nutrition = _sanitize_nutrition(nutrition)
    candidate = db.scalar(select(FoodCandidate).where(FoodCandidate.candidate_key == candidate_key))

    aliases_csv = ",".join(sorted({a.strip().lower() for a in aliases if a.strip()}))
    safe_qty = _clamp(default_quantity, 0.1, 10.0)
    safe_confidence = _clamp(confidence, 0.0, 1.0)

    if candidate is None:
        candidate = FoodCandidate(
            candidate_key=candidate_key,
            name_raw=name_raw.strip(),
            proposed_canonical_name=proposed_canonical_name.strip().lower(),
            aliases_csv=aliases_csv,
            default_quantity=safe_qty,
            default_unit=default_unit.strip().lower() or "serving",
            calories_per_serving=nutrition.calories_per_serving,
            protein_per_serving=nutrition.protein_per_serving,
            carbs_per_serving=nutrition.carbs_per_serving,
            fat_per_serving=nutrition.fat_per_serving,
            fibre_per_serving=nutrition.fibre_per_serving,
            source_model=source_model,
            prompt_version=prompt_version,
            confidence=safe_confidence,
            status="pending",
            times_seen=1,
        )
        db.add(candidate)
        logger.info("Created food candidate '%s' from LLM parse", candidate.proposed_canonical_name)
    else:
        candidate.times_seen += 1
        candidate.confidence = round((candidate.confidence + safe_confidence) / 2.0, 3)
        candidate.aliases_csv = aliases_csv or candidate.aliases_csv
        candidate.calories_per_serving = nutrition.calories_per_serving
        candidate.protein_per_serving = nutrition.protein_per_serving
        candidate.carbs_per_serving = nutrition.carbs_per_serving
        candidate.fat_per_serving = nutrition.fat_per_serving
        candidate.fibre_per_serving = nutrition.fibre_per_serving
        candidate.source_model = source_model
        candidate.prompt_version = prompt_version
        logger.info(
            "Updated food candidate '%s' (times_seen=%s)",
            candidate.proposed_canonical_name,
            candidate.times_seen,
        )

    db.flush()
    return candidate
