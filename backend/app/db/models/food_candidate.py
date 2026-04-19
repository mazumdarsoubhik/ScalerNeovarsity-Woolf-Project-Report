from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class FoodCandidate(Base):
    __tablename__ = "food_candidates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    candidate_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name_raw: Mapped[str] = mapped_column(String(160), nullable=False)
    proposed_canonical_name: Mapped[str] = mapped_column(String(120), nullable=False)
    aliases_csv: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    default_quantity: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    default_unit: Mapped[str] = mapped_column(String(40), default="serving", nullable=False)
    calories_per_serving: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    protein_per_serving: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    carbs_per_serving: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    fat_per_serving: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    fibre_per_serving: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    source_model: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(40), default="v1", nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    times_seen: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
