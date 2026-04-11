import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base


class Meal(Base):
    __tablename__ = "meals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    meal_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    eaten_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    parse_confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="meals")
    items = relationship("MealItem", back_populates="meal", cascade="all, delete-orphan")
