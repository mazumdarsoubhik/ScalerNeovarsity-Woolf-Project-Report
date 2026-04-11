import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base


class MealItem(Base):
    __tablename__ = "meal_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meal_id: Mapped[str] = mapped_column(String(36), ForeignKey("meals.id", ondelete="CASCADE"), nullable=False, index=True)
    food_id: Mapped[int | None] = mapped_column(ForeignKey("foods.id", ondelete="SET NULL"), nullable=True)
    raw_label: Mapped[str] = mapped_column(String(160), nullable=False)
    canonical_name: Mapped[str] = mapped_column(String(120), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    unit: Mapped[str] = mapped_column(String(40), default="serving", nullable=False)
    calories: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    protein: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    carbs: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    fat: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    fibre: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    assumptions: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    meal = relationship("Meal", back_populates="items")
    food = relationship("Food", back_populates="meal_items")
