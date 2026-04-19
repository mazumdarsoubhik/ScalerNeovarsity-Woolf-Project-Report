import os
import secrets
import string
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _generate_boot_id(length: int = 6) -> str:
    """Generate an uppercase alphanumeric boot identifier."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "NutriFlow Backend")
    boot_id: str = field(default_factory=_generate_boot_id)
    api_v1_prefix: str = os.getenv("API_V1_PREFIX", "/api/v1")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./nutriflow.db")
    llm_enabled: bool = os.getenv("LLM_ENABLED", "true").lower() in {"1", "true", "yes", "on"}
    llm_provider: str = os.getenv("LLM_PROVIDER", "groq")
    llm_model: str = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
    llm_timeout_seconds: int = int(os.getenv("LLM_TIMEOUT_SECONDS", "20"))
    llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "512"))
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_base_url: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_base_url: str = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
    mistral_api_key: str = os.getenv("MISTRAL_API_KEY", "")
    mistral_base_url: str = os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1")
    auth_token_ttl_minutes: int = int(os.getenv("AUTH_TOKEN_TTL_MINUTES", "10080"))
    meal_parser_mode: str = os.getenv("MEAL_PARSER_MODE", "llm_first")
    meal_prompt_version: str = os.getenv("MEAL_PROMPT_VERSION", "v1")
    meal_llm_min_confidence: float = float(os.getenv("MEAL_LLM_MIN_CONFIDENCE", "0.65"))


settings = Settings()
