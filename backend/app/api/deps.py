from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db.models.user import User
from app.services.auth import get_user_by_access_token

auth_scheme = HTTPBearer(auto_error=False)


def get_token(credentials: HTTPAuthorizationCredentials | None = Depends(auth_scheme)) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid bearer token",
        )
    return credentials.credentials.strip()


def get_current_user(
    token: str = Depends(get_token),
    db: Session = Depends(get_db),
) -> User:
    user = get_user_by_access_token(db, token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return user


def get_user_id(current_user: User = Depends(get_current_user)) -> str:
    return current_user.id
