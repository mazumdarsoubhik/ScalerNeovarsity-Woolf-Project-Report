from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


class ApiError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


@dataclass
class BackendClient:
    base_url: str
    access_token: str | None = None
    timeout_seconds: int = 15

    @property
    def api_prefix(self) -> str:
        return "/api/v1"

    @property
    def headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def _url(self, path: str) -> str:
        clean_base = self.base_url.rstrip("/")
        clean_path = path if path.startswith("/") else f"/{path}"
        return f"{clean_base}{self.api_prefix}{clean_path}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        expected_statuses: set[int] | None = None,
    ) -> Any:
        expected = expected_statuses or {200}
        try:
            response = requests.request(
                method=method,
                url=self._url(path),
                headers=self.headers,
                params=params,
                json=json_body,
                timeout=self.timeout_seconds,
            )
        except requests.exceptions.RequestException as exc:
            raise ApiError(f"Network error: {exc}") from exc

        if response.status_code not in expected:
            detail = None
            try:
                payload = response.json()
                detail = payload.get("detail") if isinstance(payload, dict) else None
            except ValueError:
                detail = None
            message = detail or response.text or f"Request failed with status {response.status_code}"
            raise ApiError(message, status_code=response.status_code)

        if response.status_code == 204:
            return None
        try:
            return response.json()
        except ValueError:
            return None

    def health(self) -> dict[str, Any]:
        return self._request("GET", "/health")

    def register(self, email: str, password: str) -> dict[str, Any]:
        return self._request(
            "POST",
            "/auth/register",
            json_body={"email": email, "password": password},
            expected_statuses={201},
        )

    def login(self, email: str, password: str) -> dict[str, Any]:
        return self._request(
            "POST",
            "/auth/login",
            json_body={"email": email, "password": password},
        )

    def logout(self) -> None:
        self._request("POST", "/auth/logout", expected_statuses={204})

    def me(self) -> dict[str, Any]:
        return self._request("GET", "/auth/me")

    def create_meal(self, text: str, meal_type: str | None, eaten_at_iso: str | None) -> dict[str, Any]:
        body: dict[str, Any] = {"text": text}
        if meal_type:
            body["meal_type"] = meal_type
        if eaten_at_iso:
            body["eaten_at"] = eaten_at_iso
        return self._request("POST", "/meals", json_body=body, expected_statuses={201})

    def update_meal(
        self,
        meal_id: str,
        text: str | None,
        meal_type: str | None,
        eaten_at_iso: str | None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if text is not None:
            body["text"] = text
        if meal_type is not None:
            body["meal_type"] = meal_type
        if eaten_at_iso is not None:
            body["eaten_at"] = eaten_at_iso
        return self._request("PATCH", f"/meals/{meal_id}", json_body=body)

    def delete_meal(self, meal_id: str) -> None:
        self._request("DELETE", f"/meals/{meal_id}", expected_statuses={204})

    def get_meal_history(
        self,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._request("GET", "/meals/history", params=params)

    def get_dashboard_today(self, *, day: str | None = None) -> dict[str, Any]:
        params = {"day": day} if day else None
        return self._request("GET", "/dashboard/today", params=params)

    def chat(self, message: str, context_day: str | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"message": message}
        if context_day:
            body["context_day"] = context_day
        return self._request("POST", "/chat", json_body=body)
