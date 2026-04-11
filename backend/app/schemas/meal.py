from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MealItemBase(BaseModel):
    canonical_name: str
    quantity: float = Field(..., gt=0)
    unit: str
    calories: float
    protein: float
    carbs: float
    fat: float
    fibre: float
    confidence: float = Field(..., ge=0, le=1)
    assumptions: dict = Field(default_factory=dict)


class MealItemOut(MealItemBase):
    id: str
    raw_label: str

    model_config = ConfigDict(from_attributes=True)


class MealCreateRequest(BaseModel):
    text: str = Field(..., min_length=2, max_length=500)
    meal_type: str | None = Field(default=None, max_length=40)
    eaten_at: datetime | None = None


class MealItemManualInput(BaseModel):
    canonical_name: str
    quantity: float = Field(..., gt=0)
    unit: str = "serving"


class MealUpdateRequest(BaseModel):
    text: str | None = Field(default=None, min_length=2, max_length=500)
    meal_type: str | None = Field(default=None, max_length=40)
    eaten_at: datetime | None = None
    items: list[MealItemManualInput] | None = None

    @field_validator("items")
    @classmethod
    def validate_items(cls, value: list[MealItemManualInput] | None) -> list[MealItemManualInput] | None:
        if value is not None and len(value) == 0:
            raise ValueError("items must contain at least one item when provided")
        return value


class MealTotals(BaseModel):
    calories: float
    protein: float
    carbs: float
    fat: float
    fibre: float


class MealOut(BaseModel):
    id: str
    original_text: str
    meal_type: str | None
    eaten_at: datetime
    parse_confidence: float
    totals: MealTotals
    items: list[MealItemOut]

    model_config = ConfigDict(from_attributes=True)


class MealHistoryEntry(BaseModel):
    id: str
    meal_type: str | None
    eaten_at: datetime
    original_text: str
    parse_confidence: float
    totals: MealTotals


class MealHistoryResponse(BaseModel):
    items: list[MealHistoryEntry]
    total: int
