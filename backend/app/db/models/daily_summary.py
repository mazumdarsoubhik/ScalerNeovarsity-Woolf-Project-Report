import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base


class DailySummary(Base):
    __tablename__ = "daily_summaries"
    __table_args__ = (UniqueConstraint("user_id", "day", name="uq_daily_summary_user_day"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    day: Mapped[date] = mapped_column(Date, nullable=False)
    calories_consumed: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    protein_consumed: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    carbs_consumed: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    fat_consumed: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    fibre_consumed: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    meal_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="summaries")
