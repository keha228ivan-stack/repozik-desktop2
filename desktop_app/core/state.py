import logging
from typing import Any, Callable, Dict, List

from desktop_app.api.client import ApiClient
from desktop_app.api.errors import ApiError

logger = logging.getLogger(__name__)


class _SimpleSignal:
    def __init__(self) -> None:
        self._subs: List[Callable] = []

    def connect(self, fn: Callable) -> None:
        self._subs.append(fn)

    def emit(self, *args: Any, **kwargs: Any) -> None:
        for fn in list(self._subs):
            fn(*args, **kwargs)


try:
    from PySide6.QtCore import QObject, Signal  # type: ignore
except Exception:
    class QObject:  # type: ignore
        pass

    def Signal(*_args: Any, **_kwargs: Any) -> _SimpleSignal:  # type: ignore
        return _SimpleSignal()


class AppState(QObject):
    auth_changed = Signal(bool)
    backend_status_changed = Signal(bool, str)
    error = Signal(str)

    profile_changed = Signal(dict)
    profile_error = Signal(str)

    courses_changed = Signal(list)
    courses_error = Signal(str)

    notifications_changed = Signal(list)
    notifications_error = Signal(str)

    forum_changed = Signal(list)
    forum_error = Signal(str)

    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self.api = api
        self.user: Dict[str, Any] | None = None
        self.is_authenticated = False
        self.offline_mode = False
        self._last_error_text: str | None = None

        self._demo_user = {
            "id": "demo-user-1",
            "fullName": "Demo Employee",
            "email": "demo@company.local",
            "role": "Сотрудник",
        }
        self._demo_password = "Demo12345!"
        self._bootstrap_session()

    def _emit_error(self, text: str) -> None:
        if text != self._last_error_text:
            self.error.emit(text)
            self._last_error_text = text

    def _set_backend_status(self, available: bool) -> None:
        message = "Backend доступен" if available else "Backend недоступен: работа в ограниченном режиме"
        self.backend_status_changed.emit(available, message)

    def refresh_backend_status(self) -> bool:
        available = self.api.health_check()
        self._set_backend_status(available)
        return available

    def _bootstrap_session(self) -> None:
        if not self.api.is_backend_available():
            self._enable_offline_mode()
            return

        self.offline_mode = False
        self._set_backend_status(True)
        try:
            me = self.api.me()
            self.user = me
            self.is_authenticated = True
        except ApiError:
            self.user = None
            self.is_authenticated = False
    
    def _enable_offline_mode(self) -> None:
        self.offline_mode = True
        self.user = dict(self._demo_user)
        self.is_authenticated = True
        self._set_backend_status(False)

    def login(self, email: str, password: str) -> bool:
        if self.offline_mode and email.lower() == self._demo_user["email"] and password == self._demo_password:
            self.user = dict(self._demo_user)
            self.is_authenticated = True
            self.auth_changed.emit(True)
            return True
        try:
            payload = self.api.login(email, password)
            token = payload.get("token")
            if token:
                self.api.set_token(token)
            self.user = payload.get("user") or self.api.me()
            self.is_authenticated = True
            self.auth_changed.emit(True)
            self._set_backend_status(True)
            return True
        except ApiError as exc:
            if self._try_offline_demo_login(email=email, password=password, error=exc):
                return True
            self._set_backend_status(False)
            self._emit_error(str(exc))
            return False

    def _try_offline_demo_login(self, email: str, password: str, error: ApiError) -> bool:
        if "Не удалось подключиться к серверу" not in str(error) and "Сервер временно недоступен" not in str(error):
            return False
        if email.lower() != self._demo_user["email"] or password != self._demo_password:
            return False
        self._enable_offline_mode()
        self.auth_changed.emit(True)
        return True

    def _try_offline_demo_login(self, email: str, password: str, error: ApiError) -> bool:
        if "Не удалось подключиться к серверу" not in str(error) and "Сервер временно недоступен" not in str(error):
            return False
        if email.lower() != self._demo_user["email"] or password != self._demo_password:
            return False
        self.user = dict(self._demo_user)
        self.is_authenticated = True
        self.auth_changed.emit(True)
        self._set_backend_status(False)
        return True

    def register(self, full_name: str, email: str, password: str) -> bool:
        if self.offline_mode:
            self._emit_error("Сервер недоступен. Регистрация временно отключена в офлайн-режиме.")
            return False
        try:
            payload = self.api.register(full_name=full_name, email=email, password=password)
            token = payload.get("token")
            if token:
                self.api.set_token(token)
            self.user = payload.get("user") or {"fullName": full_name, "email": email, "role": "Сотрудник"}
            self.is_authenticated = True
            self.auth_changed.emit(True)
            self._set_backend_status(True)
            return True
        except ApiError as exc:
            self._set_backend_status(False)
            self._emit_error(str(exc))
            return False

    def logout(self) -> None:
        self.api.set_token(None)
        self.user = None
        self.is_authenticated = False
        self.auth_changed.emit(False)

    def load_profile(self) -> None:
        if self.offline_mode:
            self.profile_changed.emit(
                {"fullName": self._demo_user["fullName"], "phone": "+7 (900) 000-00-00"}
            )
            self.profile_error.emit("")
            return
        try:
            profile = self.api.get_profile()
            self.profile_changed.emit(profile)
            self.profile_error.emit("")
            self._set_backend_status(True)
        except ApiError as exc:
            logger.info("Profile load failed: %s", exc)
            self.profile_changed.emit({})
            self.profile_error.emit("Не удалось загрузить профиль.")
            self._set_backend_status(False)

    def save_profile(self, payload: Dict[str, Any]) -> None:
        if self.offline_mode:
            self.profile_changed.emit(payload)
            self.profile_error.emit("Изменения сохранены локально (офлайн-режим).")
            return
        try:
            profile = self.api.update_profile(payload)
            self.profile_changed.emit(profile)
            self.profile_error.emit("")
            self._set_backend_status(True)
        except ApiError as exc:
            logger.info("Profile save failed: %s", exc)
            self.profile_error.emit("Не удалось сохранить профиль.")
            self._emit_error(str(exc))
            self._set_backend_status(False)

    def load_courses(self, q: str = "") -> None:
        if self.offline_mode:
            mock_courses = [
                {"title": "Введение в HR-процессы"},
                {"title": "Оценка эффективности сотрудников"},
                {"title": "Коммуникация в команде"},
            ]
            filtered = [c for c in mock_courses if q.lower() in c["title"].lower()] if q else mock_courses
            self.courses_changed.emit(filtered)
            self.courses_error.emit("")
            return
        try:
            data = self.api.get_courses(q)
            courses: List[dict] = data.get("items") or data.get("courses") or []
            self.courses_changed.emit(courses)
            self.courses_error.emit("")
            self._set_backend_status(True)
        except ApiError as exc:
            logger.info("Courses load failed: %s", exc)
            self.courses_changed.emit([])
            self.courses_error.emit("Не удалось загрузить курсы.")
            self._set_backend_status(False)

    def load_notifications(self) -> None:
        if self.offline_mode:
            self.notifications_changed.emit(
                [
                    {"title": "Добро пожаловать в демо-режим", "read": False},
                    {"title": "Backend недоступен: данные могут быть неполными", "read": True},
                ]
            )
            self.notifications_error.emit("")
            return
        try:
            data = self.api.get_notifications()
            items = data.get("items") or data.get("notifications") or []
            self.notifications_changed.emit(items)
            self.notifications_error.emit("")
            self._set_backend_status(True)
        except ApiError as exc:
            logger.info("Notifications load failed: %s", exc)
            self.notifications_changed.emit([])
            self.notifications_error.emit("Не удалось загрузить уведомления.")
            self._set_backend_status(False)

    def load_topics(self) -> None:
        if self.offline_mode:
            self.forum_changed.emit(
                [
                    {"title": "FAQ по демо-режиму"},
                    {"title": "Как подключить реальный backend"},
                ]
            )
            self.forum_error.emit("")
            return
        try:
            data = self.api.get_topics()
            items = data.get("items") or data.get("topics") or []
            self.forum_changed.emit(items)
            self.forum_error.emit("")
            self._set_backend_status(True)
        except ApiError as exc:
            logger.info("Forum load failed: %s", exc)
            self.forum_changed.emit([])
            self.forum_error.emit("Не удалось загрузить темы форума.")
            self._set_backend_status(False)

    def create_topic(self, title: str, body: str) -> bool:
        if self.offline_mode:
            self.forum_error.emit("В офлайн-режиме создание тем отключено.")
            return False
        try:
            self.api.create_topic(title, body)
            self._set_backend_status(True)
            return True
        except ApiError as exc:
            logger.info("Forum create failed: %s", exc)
            self.forum_error.emit("Не удалось создать тему.")
            self._emit_error(str(exc))
            self._set_backend_status(False)
            return False
