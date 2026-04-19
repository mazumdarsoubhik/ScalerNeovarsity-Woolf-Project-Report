import json
from urllib import error, request

from app.core.config import settings
from app.core.llm.base import BaseLLMConnector, LLMConnectorError
from app.core.llm.types import LLMMessage, LLMRequest, LLMResponse, LLMUsage


class MistralConnector(BaseLLMConnector):
    """Mistral chat completion connector."""

    def __init__(self, api_key: str, base_url: str, timeout_seconds: int) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _serialize_messages(self, messages: list[LLMMessage]) -> list[dict[str, str]]:
        return [{"role": message.role, "content": message.content} for message in messages]

    def generate(self, request_payload: LLMRequest) -> LLMResponse:
        if not self.api_key:
            raise LLMConnectorError("Missing MISTRAL_API_KEY for Mistral connector")

        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": request_payload.model,
            "messages": self._serialize_messages(request_payload.messages),
            "temperature": request_payload.temperature,
            "max_tokens": request_payload.max_tokens,
        }
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            url=url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="ignore")
            raise LLMConnectorError(f"Mistral HTTP error {exc.code}: {details[:300]}") from exc
        except error.URLError as exc:
            raise LLMConnectorError(f"Mistral connection error: {exc}") from exc
        except TimeoutError as exc:
            raise LLMConnectorError("Mistral request timed out") from exc

        try:
            data = json.loads(raw)
            content = data["choices"][0]["message"]["content"]
            usage_obj = data.get("usage", {})
            usage = LLMUsage(
                prompt_tokens=usage_obj.get("prompt_tokens"),
                completion_tokens=usage_obj.get("completion_tokens"),
                total_tokens=usage_obj.get("total_tokens"),
            )
            resolved_model = data.get("model", request_payload.model)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise LLMConnectorError("Unexpected Mistral response shape") from exc

        return LLMResponse(
            content=content.strip(),
            provider="mistral",
            model=resolved_model,
            usage=usage,
        )


def build_mistral_connector() -> MistralConnector:
    return MistralConnector(
        api_key=settings.mistral_api_key,
        base_url=settings.mistral_base_url,
        timeout_seconds=settings.llm_timeout_seconds,
    )

