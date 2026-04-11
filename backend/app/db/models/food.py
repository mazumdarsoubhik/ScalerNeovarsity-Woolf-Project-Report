from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base


class Food(Base):
    __tablename__ = "foods"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    canonical_name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    aliases_csv: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    default_quantity: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    default_unit: Mapped[str] = mapped_column(String(40), default="serving", nullable=False)
    calories_per_serving: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    protein_per_serving: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    carbs_per_serving: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    fat_per_serving: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    fibre_per_serving: Mapped[float] = mapped_column(Float, default=0, nullable=False)

    meal_items = relationship("MealItem", back_populates="food")
