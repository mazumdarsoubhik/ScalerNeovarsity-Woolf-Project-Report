import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.auth_token import AuthToken
from app.db.models.user import User
from app.db.models.user_credential import UserCredential
from app.db.models.user_goal import UserGoal

PBKDF2_ITERATIONS = 200_000


def normalize_email(email: str) -> str:
    return email.strip().lower()


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations_raw, salt_hex, digest_hex = stored_hash.split("$", maxsplit=3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_raw)
        salt = bytes.fromhex(salt_hex)
    except (TypeError, ValueError):
        return False

    computed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(computed.hex(), digest_hex)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_user_with_password(db: Session, email: str, password: str) -> User:
    normalized_email = normalize_email(email)
    existing = db.scalar(select(UserCredential).where(UserCredential.email == normalized_email))
    existing_user = db.scalar(select(User).where(User.email == normalized_email))
    if existing is not None or existing_user is not None:
        raise ValueError("Email already registered")

    user = User(email=normalized_email)
    db.add(user)
    db.flush()
    db.add(UserCredential(user_id=user.id, email=normalized_email, password_hash=hash_password(password)))
    db.add(UserGoal(user_id=user.id))
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    normalized_email = normalize_email(email)
    credential = db.scalar(select(UserCredential).where(UserCredential.email == normalized_email))
    if credential is None:
        return None
    if not verify_password(password, credential.password_hash):
        return None
    return db.scalar(select(User).where(User.id == credential.user_id))


def issue_access_token(db: Session, user_id: str) -> tuple[str, datetime]:
    raw_token = secrets.token_urlsafe(48)
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.auth_token_ttl_minutes)
    db.add(AuthToken(token_hash=hash_token(raw_token), user_id=user_id, expires_at=expires_at))
    db.commit()
    return raw_token, expires_at


def revoke_access_token(db: Session, token: str) -> None:
    token_row = db.scalar(select(AuthToken).where(AuthToken.token_hash == hash_token(token)))
    if token_row is None or token_row.revoked_at is not None:
        return
    token_row.revoked_at = datetime.now(UTC)
    db.commit()


def get_user_by_access_token(db: Session, token: str) -> User | None:
    now = datetime.now(UTC)
    token_row = db.scalar(select(AuthToken).where(AuthToken.token_hash == hash_token(token)))
    if token_row is None or token_row.revoked_at is not None:
        return None

    expires_at = token_row.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if expires_at <= now:
        return None
    return db.scalar(select(User).where(User.id == token_row.user_id))
