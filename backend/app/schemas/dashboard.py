from datetime import date

from pydantic import BaseModel


class MacroPair(BaseModel):
    consumed: float
    target: float
    remaining: float


class DashboardTodayResponse(BaseModel):
    day: date
    calories: MacroPair
    protein: MacroPair
    carbs: MacroPair
    fat: MacroPair
    fibre: MacroPair
    meal_count: int
    streak_days: int
