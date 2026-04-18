import logging
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import requests

from desktop_app.api.config import load_api_config
from desktop_app.api.errors import ApiError, map_exception_to_user_message
from desktop_app.core.session_store import SessionStore

logger = logging.getLogger(__name__)


class ApiClient:
    def __init__(self) -> None:
        self.config = load_api_config()
        self.base_url = self.config.base_url
        self.timeout_seconds = self.config.timeout_seconds
        self.session = requests.Session()
        self._configure_proxy_behavior()
        self.store = SessionStore()
        self._health_cache: bool | None = None
        token = self.store.get_token()
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def _configure_proxy_behavior(self) -> None:
        parsed = urlparse(self.base_url)
        if parsed.hostname in {"localhost", "127.0.0.1", "::1"}:
            self.session.trust_env = False

    def set_token(self, token: Optional[str]) -> None:
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        else:
            self.session.headers.pop("Authorization", None)
        self.store.set_token(token)

    def _join_url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _request(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        url = self._join_url(path)
        kwargs.setdefault("timeout", self.timeout_seconds)

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
        except requests.Timeout as exc:
            logger.warning("Timeout while calling %s %s: %s", method, url, exc)
            raise ApiError(
                user_message="Истекло время ожидания ответа от сервера.",
                technical_message=str(exc),
            ) from exc
        except requests.ConnectionError as exc:
            logger.warning("Connection error while calling %s %s: %s", method, url, exc)
            raise ApiError(
                user_message="Не удалось подключиться к серверу. Проверьте, запущен ли backend.",
                technical_message=str(exc),
            ) from exc
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else None
            logger.warning("HTTP error while calling %s %s: %s", method, url, exc)
            detail = self._extract_error_message(exc.response)
            if status and status >= 500:
                user_message = "Сервер временно недоступен."
            elif status == 401:
                user_message = "Неверный email или пароль."
            elif status == 403:
                user_message = "Недостаточно прав для выполнения операции."
            elif status == 404:
                user_message = "Запрошенный API endpoint не найден."
            elif status == 409:
                user_message = detail or "Пользователь уже существует."
            elif status in (400, 422):
                user_message = detail or "Проверьте корректность введённых данных."
            else:
                user_message = detail or "Сервер вернул ошибку при обработке запроса."
            raise ApiError(
                user_message=user_message,
                technical_message=f"HTTP {status}: {detail or str(exc)}",
                status_code=status,
            ) from exc
        except requests.RequestException as exc:
            logger.exception("Request exception while calling %s %s", method, url)
            raise ApiError(
                user_message=map_exception_to_user_message(exc),
                technical_message=str(exc),
            ) from exc

        if response.status_code == 204 or not response.content:
            return {}

        try:
            data = response.json()
        except ValueError as exc:
            logger.warning("Invalid JSON in response from %s %s", method, url)
            raise ApiError(
                user_message="Сервер вернул некорректный ответ.",
                technical_message="Failed to parse JSON response",
                status_code=response.status_code,
            ) from exc

        if not isinstance(data, dict):
            logger.warning("Unexpected JSON shape from %s %s: %s", method, url, type(data).__name__)
            return {"items": data} if isinstance(data, list) else {}
        return data

    def _extract_error_message(self, response: requests.Response | None) -> str:
        if response is None:
            return ""
        try:
            payload = response.json()
        except ValueError:
            return response.text.strip()[:160]

        if isinstance(payload, dict):
            value = payload.get("message") or payload.get("error") or payload.get("detail")
            return str(value) if value else ""
        return ""

    def health_check(self) -> bool:
        try:
            self._request("GET", self.config.health_path, timeout=min(3.0, self.timeout_seconds))
            self._health_cache = True
            return True
        except ApiError as exc:
            logger.info("Health check failed: %s | technical=%s", exc.user_message, exc.technical_message)
            self._health_cache = False
            return False

    def is_backend_available(self) -> bool:
        if self._health_cache is None:
            return self.health_check()
        return self._health_cache

    def login(self, email: str, password: str) -> Dict[str, Any]:
        return self._request("POST", "/auth/login", json={"email": email, "password": password})

    def register(self, full_name: str, email: str, password: str) -> Dict[str, Any]:
        payload_variants = [
            {"fullName": full_name, "email": email, "password": password, "role": "employee"},
            {"full_name": full_name, "email": email, "password": password, "role": "employee"},
            {"name": full_name, "email": email, "password": password, "role": "employee"},
            {"fullName": full_name, "email": email, "password": password},
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
                    return self._request("POST", path, json=payload)
                except ApiError as exc:
                    last_error = exc
                    if exc.status_code in (400, 422):
                        continue
                    if exc.status_code in (404, 405):
                        break
                    if exc.status_code is not None and exc.status_code >= 500:
                        continue
                    if exc.status_code is None:
                        raise exc
                    raise exc

        raise last_error or ApiError("Не удалось зарегистрировать аккаунт.")

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
