from datetime import date, datetime, time, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.db.models.daily_summary import DailySummary
from app.db.models.meal import Meal
from app.db.models.meal_item import MealItem
from app.db.models.user_goal import UserGoal
from app.schemas.dashboard import DashboardTodayResponse, MacroPair


def _build_macro_pair(consumed: float, target: float) -> MacroPair:
    return MacroPair(consumed=round(consumed, 2), target=round(target, 2), remaining=round(target - consumed, 2))


def recompute_daily_summary(db: Session, user_id: str, day: date) -> DailySummary:
    start = datetime.combine(day, time.min)
    end = datetime.combine(day, time.max)
    rows = db.execute(
        select(
            func.count(func.distinct(Meal.id)),
            func.coalesce(func.sum(MealItem.calories), 0),
            func.coalesce(func.sum(MealItem.protein), 0),
            func.coalesce(func.sum(MealItem.carbs), 0),
            func.coalesce(func.sum(MealItem.fat), 0),
            func.coalesce(func.sum(MealItem.fibre), 0),
        )
        .join(MealItem, MealItem.meal_id == Meal.id)
        .where(and_(Meal.user_id == user_id, Meal.eaten_at >= start, Meal.eaten_at <= end))
    ).one()
    meal_count, calories, protein, carbs, fat, fibre = rows

    summary = db.scalar(select(DailySummary).where(and_(DailySummary.user_id == user_id, DailySummary.day == day)))
    if summary is None:
        summary = DailySummary(user_id=user_id, day=day)
        db.add(summary)

    summary.meal_count = int(meal_count or 0)
    summary.calories_consumed = float(calories or 0)
    summary.protein_consumed = float(protein or 0)
    summary.carbs_consumed = float(carbs or 0)
    summary.fat_consumed = float(fat or 0)
    summary.fibre_consumed = float(fibre or 0)
    db.commit()
    db.refresh(summary)
    return summary


def get_streak_days(db: Session, user_id: str, from_day: date) -> int:
    streak = 0
    cursor = from_day
    while True:
        summary = db.scalar(
            select(DailySummary).where(and_(DailySummary.user_id == user_id, DailySummary.day == cursor))
        )
        if summary is None or summary.meal_count <= 0:
            break
        streak += 1
        cursor = cursor - timedelta(days=1)
    return streak


def get_today_dashboard(db: Session, user_id: str, day: date) -> DashboardTodayResponse:
    summary = recompute_daily_summary(db, user_id, day)
    goal = db.scalar(select(UserGoal).where(UserGoal.user_id == user_id))
    if goal is None:
        goal = UserGoal(user_id=user_id)
        db.add(goal)
        db.commit()
        db.refresh(goal)

    return DashboardTodayResponse(
        day=day,
        calories=_build_macro_pair(summary.calories_consumed, goal.calories_target),
        protein=_build_macro_pair(summary.protein_consumed, goal.protein_target),
        carbs=_build_macro_pair(summary.carbs_consumed, goal.carbs_target),
        fat=_build_macro_pair(summary.fat_consumed, goal.fat_target),
        fibre=_build_macro_pair(summary.fibre_consumed, goal.fibre_target),
        meal_count=summary.meal_count,
        streak_days=get_streak_days(db, user_id, day),
    )
