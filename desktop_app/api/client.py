import os
from typing import Any, Dict, Optional

import requests

from desktop_app.core.session_store import SessionStore


class ApiError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


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
            raise ApiError(f"API {response.status_code}: {message}", status_code=response.status_code)

        if response.status_code == 204 or not response.content:
            return {}

        try:
            return response.json()
        except Exception as exc:
            raise ApiError("Failed to parse JSON response") from exc

    def _try_register_variant(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", path, json=payload)

    def login(self, email: str, password: str) -> Dict[str, Any]:
        return self._request("POST", "/auth/login", json={"email": email, "password": password})

    def register(self, full_name: str, email: str, password: str) -> Dict[str, Any]:
        # Приложение только для сотрудников: роль фиксированная.
        # Сначала используем каноничный payload, альтернативы — только для обратной совместимости.
        payload_variants = [
            {"fullName": full_name, "email": email, "password": password, "role": "employee"},
            {"full_name": full_name, "email": email, "password": password, "role": "employee"},
            {"name": full_name, "email": email, "password": password, "role": "employee"},
            {"fullName": full_name, "email": email, "password": password, "role": "Сотрудник"},
            {"fullName": full_name, "email": email, "password": password},
            {"full_name": full_name, "email": email, "password": password},
            {"name": full_name, "email": email, "password": password},
        ]
        register_paths = [
            "/auth/register",
            "/auth/signup",
            "/register",
            "/users/register",
            "/employees/register",
            "/auth/employee/register",
        ]

        last_error: ApiError | None = None
        for path in register_paths:
            for payload in payload_variants:
                try:
                    return self._try_register_variant(path, payload)
                except ApiError as exc:
                    last_error = exc
                    status_code = exc.status_code
                    # 400/422: endpoint найден, но формат payload может не совпадать — пробуем следующий вариант.
                    if status_code in (400, 422):
                        continue
                    # 404/405: этот путь не подходит — переходим к следующему endpoint.
                    if status_code in (404, 405):
                        break
                    # 5xx (включая 502): на части бэкендов ошибка зависит от конкретной схемы body,
                    # поэтому сначала пробуем следующий payload на этом же endpoint.
                    if status_code is not None and status_code >= 500:
                        continue
                    # Для остальных ошибок (401/403/409 и т.п.) сразу возвращаем исходную причину.
                    raise exc

        # Более явное сообщение, чтобы пользователь видел причину.
        raise ApiError(
            f"Не удалось зарегистрировать аккаунт. Последняя ошибка: {last_error}"
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
