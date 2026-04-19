from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_token
from app.core.database import get_db
from app.db.models.user import User
from app.schemas.auth import AuthRequest, AuthResponse, MeResponse
from app.services.auth import authenticate_user, create_user_with_password, issue_access_token, revoke_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: AuthRequest, db: Session = Depends(get_db)) -> AuthResponse:
    try:
        user = create_user_with_password(db, payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    token, expires_at = issue_access_token(db, user.id)
    return AuthResponse(user_id=user.id, email=user.email or payload.email, access_token=token, expires_at=expires_at)


@router.post("/login", response_model=AuthResponse)
def login(payload: AuthRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = authenticate_user(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token, expires_at = issue_access_token(db, user.id)
    return AuthResponse(user_id=user.id, email=user.email or payload.email, access_token=token, expires_at=expires_at)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(token: str = Depends(get_token), db: Session = Depends(get_db)) -> None:
    revoke_access_token(db, token)


@router.get("/me", response_model=MeResponse)
def me(current_user: User = Depends(get_current_user)) -> MeResponse:
    return MeResponse(user_id=current_user.id, email=current_user.email)
