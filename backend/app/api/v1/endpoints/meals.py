from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_user_id
from app.core.database import get_db
from app.schemas.meal import MealCreateRequest, MealHistoryResponse, MealOut, MealUpdateRequest
from app.services.meals import create_meal, delete_meal, get_meal_history, update_meal
from app.services.users import ensure_user_and_goal

router = APIRouter(prefix="/meals", tags=["meals"])


@router.post("", response_model=MealOut, status_code=status.HTTP_201_CREATED)
def create_meal_entry(
    payload: MealCreateRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id),
) -> MealOut:
    ensure_user_and_goal(db, user_id)
    try:
        return create_meal(db, user_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch("/{meal_id}", response_model=MealOut)
def update_meal_entry(
    meal_id: str,
    payload: MealUpdateRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id),
) -> MealOut:
    ensure_user_and_goal(db, user_id)
    try:
        meal = update_meal(db, user_id, meal_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if meal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found")
    return meal


@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal_entry(
    meal_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id),
) -> None:
    ensure_user_and_goal(db, user_id)
    deleted = delete_meal(db, user_id, meal_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found")


@router.get("/history", response_model=MealHistoryResponse)
def meal_history(
    start_day: date | None = Query(default=None, alias="start_date"),
    end_day: date | None = Query(default=None, alias="end_date"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id),
) -> MealHistoryResponse:
    ensure_user_and_goal(db, user_id)
    return get_meal_history(db, user_id, start_day, end_day, limit, offset)
