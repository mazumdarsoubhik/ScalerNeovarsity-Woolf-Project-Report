from app.core.llm.base import BaseLLMConnector
from app.core.llm.types import LLMRequest, LLMResponse


class MockConnector(BaseLLMConnector):
    """Deterministic connector for local fallback/testing."""

    def generate(self, request: LLMRequest) -> LLMResponse:
        prompt = request.messages[-1].content if request.messages else "No prompt provided."
        return LLMResponse(
            content=f"[mock-llm] {prompt[:200]}",
            provider="mock",
            model=request.model,
        )

