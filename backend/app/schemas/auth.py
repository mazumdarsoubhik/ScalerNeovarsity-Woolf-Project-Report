from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class AuthRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized or "." not in normalized.split("@")[-1]:
            raise ValueError("Invalid email address")
        return normalized


class AuthResponse(BaseModel):
    user_id: str
    email: str
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime


class MeResponse(BaseModel):
    user_id: str
    email: str | None = None
