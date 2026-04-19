from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ParsedItem:
    """Normalized meal item used by storage and response layers."""

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
    assumptions: dict = field(default_factory=dict)
    food_id: int | None = None


@dataclass(frozen=True)
class ParsedMeal:
    """Parsed meal payload with item list and aggregate confidence."""

    items: list[ParsedItem]
    confidence: float


@dataclass(frozen=True)
class LLMExtractedItem:
    """Raw item extracted by the LLM before DB normalization."""

    raw_label: str
    name: str
    quantity: float | None
    unit: str | None
    calories_per_serving: float | None
    protein_per_serving: float | None
    carbs_per_serving: float | None
    fat_per_serving: float | None
    fibre_per_serving: float | None
    confidence: float
    aliases: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class LLMExtraction:
    """Structured extraction result from meal-parsing LLM prompt."""

    items: list[LLMExtractedItem]
    confidence: float
    model: str
    prompt_version: str
