import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base


class UserGoal(Base):
    __tablename__ = "user_goals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    calories_target: Mapped[float] = mapped_column(Float, default=2000, nullable=False)
    protein_target: Mapped[float] = mapped_column(Float, default=120, nullable=False)
    carbs_target: Mapped[float] = mapped_column(Float, default=250, nullable=False)
    fat_target: Mapped[float] = mapped_column(Float, default=60, nullable=False)
    fibre_target: Mapped[float] = mapped_column(Float, default=30, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="goals")
