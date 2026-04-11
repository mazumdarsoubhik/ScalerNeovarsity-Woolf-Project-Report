import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "NutriFlow Backend")
    api_v1_prefix: str = os.getenv("API_V1_PREFIX", "/api/v1")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./nutriflow.db")


settings = Settings()
