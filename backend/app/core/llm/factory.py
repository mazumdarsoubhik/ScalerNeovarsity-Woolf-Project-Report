from app.core.config import settings
from app.core.llm.base import BaseLLMConnector
from app.core.llm.connectors.gemini_connector import build_gemini_connector
from app.core.llm.connectors.groq_connector import build_groq_connector
from app.core.llm.connectors.mistral_connector import build_mistral_connector
from app.core.llm.connectors.mock_connector import MockConnector


def get_llm_connector() -> BaseLLMConnector:
    provider = settings.llm_provider.strip().lower()

    if provider == "groq":
        return build_groq_connector()
    if provider == "gemini":
        return build_gemini_connector()
    if provider == "mistral":
        return build_mistral_connector()

    return MockConnector()
