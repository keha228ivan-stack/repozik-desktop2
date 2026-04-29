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
        payload = kwargs.get("json")
        if isinstance(payload, dict):
            safe_payload = {
                k: ("***" if "password" in k.lower() else v)
                for k, v in payload.items()
            }
            logger.info("API request %s %s payload=%s", method, url, safe_payload)
        else:
            logger.info("API request %s %s", method, url)

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
        except ApiError:
            self._health_cache = False
            return False

    def is_backend_available(self) -> bool:
        if self._health_cache is None:
            return self.health_check()
        return self._health_cache

    def login(self, email: str, password: str) -> Dict[str, Any]:
        return self._request("POST", "/auth/login", json={"email": email, "password": password})

    def register(self, full_name: str, email: str, password: str) -> Dict[str, Any]:
        payload = {
            "fullName": full_name,
            "email": email,
            "password": password,
            "position": "Сотрудник",
            "departmentId": None,
        }
        try:
            return self._request("POST", "/auth/register", json=payload)
        except ApiError as exc:
            if exc.status_code == 409:
                raise ApiError("Пользователь с таким email уже существует", status_code=409) from exc
            if exc.status_code in (400, 422):
                raise ApiError("Заполните обязательные поля", status_code=400) from exc
            if exc.status_code == 500:
                raise ApiError("Ошибка регистрации. Попробуйте позже", status_code=500) from exc
            raise

    def me(self) -> Dict[str, Any]:
        return self._request("GET", "/auth/me")

    def get_dashboard(self) -> Dict[str, Any]:
        return self._request("GET", "/api/employee/dashboard")

    def get_employee_courses(self) -> Dict[str, Any]:
        return self._request("GET", "/api/employee/courses")

    def get_in_progress_courses(self) -> Dict[str, Any]:
        return self._request("GET", "/api/employee/courses/in-progress")

    def get_completed_courses(self) -> Dict[str, Any]:
        return self._request("GET", "/api/employee/courses/completed")

    def get_course_details(self, course_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/api/employee/courses/{course_id}")

    def start_course(self, course_id: str) -> Dict[str, Any]:
        return self._request("POST", f"/api/employee/courses/{course_id}/start")

    def complete_lesson(self, course_id: str, lesson_id: str) -> Dict[str, Any]:
        return self._request("POST", f"/api/employee/courses/{course_id}/lessons/{lesson_id}/complete")

    def submit_test(self, course_id: str, answers: list[dict[str, Any]]) -> Dict[str, Any]:
        return self._request("POST", f"/api/employee/courses/{course_id}/test/submit", json={"answers": answers})

    def get_profile(self) -> Dict[str, Any]:
        return self._request("GET", "/api/employee/profile")

    def update_profile(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("PATCH", "/profile", json=payload)

    def get_courses(self, q: str = "") -> Dict[str, Any]:
        params = {"q": q} if q else None
        return self._request("GET", "/courses", params=params)
