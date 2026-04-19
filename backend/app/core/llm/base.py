from abc import ABC, abstractmethod

from app.core.llm.types import LLMRequest, LLMResponse


class LLMConnectorError(RuntimeError):
    """Raised when an LLM provider call fails."""


class BaseLLMConnector(ABC):
    """Abstract base class for all LLM provider connectors."""

    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a chat completion response from provider."""

