from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_user_id
from app.core.database import get_db
from app.schemas.dashboard import DashboardTodayResponse
from app.services.dashboard import get_today_dashboard
from app.services.users import ensure_user_and_goal

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/today", response_model=DashboardTodayResponse)
def today_dashboard(
    day: date | None = Query(default=None),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id),
) -> DashboardTodayResponse:
    ensure_user_and_goal(db, user_id)
    return get_today_dashboard(db, user_id, day or date.today())
