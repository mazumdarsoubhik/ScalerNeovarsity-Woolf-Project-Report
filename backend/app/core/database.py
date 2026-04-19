from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


is_sqlite = settings.database_url.startswith("sqlite")
engine = create_engine(
    settings.database_url,
    future=True,
    connect_args={"check_same_thread": False} if is_sqlite else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app.db.models.base import Base
    from app.db.models import auth_token, chat_message, daily_summary, food, meal, meal_item, user, user_credential, user_goal  # noqa: F401

    Base.metadata.create_all(bind=engine)
