import json
from urllib import error, request

from app.core.config import settings
from app.core.llm.base import BaseLLMConnector, LLMConnectorError
from app.core.llm.types import LLMRequest, LLMResponse


class GeminiConnector(BaseLLMConnector):
    """Gemini connector using Google Generative Language API."""

    def __init__(self, api_key: str, base_url: str, timeout_seconds: int) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def generate(self, request_payload: LLMRequest) -> LLMResponse:
        if not self.api_key:
            raise LLMConnectorError("Missing GEMINI_API_KEY for Gemini connector")

        model = request_payload.model
        url = f"{self.base_url}/models/{model}:generateContent"
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": "\n".join(
                                f"{message.role}: {message.content}" for message in request_payload.messages
                            )
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": request_payload.temperature,
                "maxOutputTokens": request_payload.max_tokens,
                # Prevent hidden "thinking" tokens from consuming output budget.
                "thinkingConfig": {"thinkingBudget": 0},
            },
        }
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            url=url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-goog-api-key": self.api_key,
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="ignore")
            raise LLMConnectorError(f"Gemini HTTP error {exc.code}: {details[:300]}") from exc
        except error.URLError as exc:
            raise LLMConnectorError(f"Gemini connection error: {exc}") from exc
        except TimeoutError as exc:
            raise LLMConnectorError("Gemini request timed out") from exc

        try:
            data = json.loads(raw)
            candidates = data.get("candidates", [])
            parts = candidates[0]["content"]["parts"]
            content = " ".join(part.get("text", "") for part in parts).strip()
            if not content:
                raise LLMConnectorError("Gemini returned empty content")
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise LLMConnectorError("Unexpected Gemini response shape") from exc

        return LLMResponse(
            content=content,
            provider="gemini",
            model=model,
        )


def build_gemini_connector() -> GeminiConnector:
    return GeminiConnector(
        api_key=settings.gemini_api_key,
        base_url=settings.gemini_base_url,
        timeout_seconds=settings.llm_timeout_seconds,
    )
