import os
from typing import Any, Dict, Optional

import requests

from desktop_app.core.session_store import SessionStore


class ApiError(Exception):
    pass


class ApiClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("HR_API_BASE_URL", "http://localhost:3000/api").rstrip("/")
        self.session = requests.Session()
        self.store = SessionStore()
        token = self.store.get_token()
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def set_token(self, token: Optional[str]) -> None:
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        else:
            self.session.headers.pop("Authorization", None)
        self.store.set_token(token)

    def _request(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = self.session.request(method, url, timeout=20, **kwargs)
        except requests.RequestException as exc:
            raise ApiError(f"Network error: {exc}") from exc

        if not response.ok:
            try:
                payload = response.json()
                message = payload.get("message") or payload.get("error") or response.text
            except Exception:
                message = response.text
            raise ApiError(f"API {response.status_code}: {message}")

        if response.status_code == 204 or not response.content:
            return {}

        try:
            return response.json()
        except Exception as exc:
            raise ApiError("Failed to parse JSON response") from exc

    def login(self, email: str, password: str) -> Dict[str, Any]:
        return self._request("POST", "/auth/login", json={"email": email, "password": password})

    def register(self, full_name: str, email: str, password: str, role: str = "Менеджер") -> Dict[str, Any]:
        return self._request(
            "POST",
            "/auth/register",
            json={"fullName": full_name, "email": email, "password": password, "role": role},
        )

    def me(self) -> Dict[str, Any]:
        return self._request("GET", "/auth/me")

    def get_profile(self) -> Dict[str, Any]:
        return self._request("GET", "/profile")

    def update_profile(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("PATCH", "/profile", json=payload)

    def get_courses(self, q: str = "") -> Dict[str, Any]:
        params = {"q": q} if q else None
        return self._request("GET", "/courses", params=params)

    def get_progress(self) -> Dict[str, Any]:
        return self._request("GET", "/progress")

    def get_notifications(self) -> Dict[str, Any]:
        return self._request("GET", "/notifications")

    def mark_notification_read(self, notif_id: str) -> Dict[str, Any]:
        return self._request("PATCH", f"/notifications/{notif_id}/read")

    def get_topics(self) -> Dict[str, Any]:
        return self._request("GET", "/forum/topics")

    def create_topic(self, title: str, body: str) -> Dict[str, Any]:
        return self._request("POST", "/forum/topics", json={"title": title, "body": body})
