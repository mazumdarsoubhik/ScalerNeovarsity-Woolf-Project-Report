from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from app.core.config import settings
from app.core.llm.base import LLMConnectorError
from app.core.llm.connectors.gemini_connector import build_gemini_connector
from app.core.llm.connectors.groq_connector import build_groq_connector
from app.core.llm.connectors.mistral_connector import build_mistral_connector
from app.core.llm.types import LLMMessage, LLMRequest


@dataclass(frozen=True)
class ProviderCheck:
    name: str
    model: str
    connector_builder: Callable[[], object]
    api_key: str


def _masked_key(key: str) -> str:
    if not key:
        return "<missing>"
    if len(key) <= 8:
        return "*" * len(key)
    return f"{key[:4]}...{key[-4:]}"


def _run_one(check: ProviderCheck) -> tuple[bool, str]:
    if not check.api_key:
        return False, "missing API key"

    connector = check.connector_builder()
    request_payload = LLMRequest(
        messages=[
            LLMMessage(
                role="user",
                content="Health check. Reply with: OK",
            )
        ],
        model=check.model,
        temperature=0.0,
        max_tokens=100,
    )

    try:
        response = connector.generate(request_payload)
        content = (response.content or "").strip()
        print(f"  debug: full response content={content!r}")
        if not content:
            return False, "empty response content"
        return True, f"model={response.model} response={content[:80]!r}"
    except LLMConnectorError as exc:
        return False, str(exc)
    except Exception as exc:  # pragma: no cover - defensive fallback
        return False, f"unexpected error: {exc}"


def main() -> int:
    checks = [
        ProviderCheck(
            name="groq",
            model="llama-3.1-8b-instant",
            connector_builder=build_groq_connector,
            api_key=settings.groq_api_key,
        ),
        ProviderCheck(
            name="gemini",
            model="gemini-flash-latest",
            connector_builder=build_gemini_connector,
            api_key=settings.gemini_api_key,
        ),
        ProviderCheck(
            name="mistral",
            model="mistral-small-latest",
            connector_builder=build_mistral_connector,
            api_key=settings.mistral_api_key,
        ),
    ]

    print("LLM Health Check")
    print("----------------")

    failures = 0
    for check in checks:
        print(f"[{check.name}] key={_masked_key(check.api_key)} model={check.model}")
        ok, detail = _run_one(check)
        if ok:
            print(f"  PASS: {detail}")
        else:
            failures += 1
            print(f"  FAIL: {detail}")

    print("----------------")
    if failures == 0:
        print("All provider checks passed.")
        return 0

    print(f"{failures} provider check(s) failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

