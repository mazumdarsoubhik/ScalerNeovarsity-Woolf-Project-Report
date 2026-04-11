from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.models.user_goal import UserGoal


def ensure_user_and_goal(db: Session, user_id: str) -> None:
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        user = User(id=user_id)
        db.add(user)
        db.flush()

    goal = db.scalar(select(UserGoal).where(UserGoal.user_id == user_id))
    if goal is None:
        db.add(UserGoal(user_id=user_id))
    db.commit()
