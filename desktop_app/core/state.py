from typing import Any, Callable, Dict, List

from desktop_app.api.client import ApiClient, ApiError


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
    error = Signal(str)
    profile_changed = Signal(dict)
    courses_changed = Signal(list)
    notifications_changed = Signal(list)
    forum_changed = Signal(list)

    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self.api = api
        self.user: Dict[str, Any] | None = None
        self.is_authenticated = False
        self._demo_user = {
            "id": "demo-user-1",
            "fullName": "Demo Employee",
            "email": "demo@company.local",
            "role": "Сотрудник",
        }
        self._demo_password = "Demo12345!"
        self._bootstrap_session()

    def _bootstrap_session(self) -> None:
        try:
            me = self.api.me()
            self.user = me
            self.is_authenticated = True
        except ApiError:
            self.user = None
            self.is_authenticated = False

    def login(self, email: str, password: str) -> bool:
        try:
            payload = self.api.login(email, password)
            token = payload.get("token")
            if token:
                self.api.set_token(token)
            self.user = payload.get("user") or self.api.me()
            self.is_authenticated = True
            self.auth_changed.emit(True)
            return True
        except ApiError as exc:
            if self._try_offline_demo_login(email=email, password=password, error=exc):
                return True
            self.error.emit(str(exc))
            return False

    def _try_offline_demo_login(self, email: str, password: str, error: ApiError) -> bool:
        """
        Фолбэк для локальной проверки UI, когда backend недоступен.
        Срабатывает только для сетевых ошибок и заранее известной демо-учётки.
        """
        if "Network error:" not in str(error):
            return False
        if email.lower() != self._demo_user["email"] or password != self._demo_password:
            return False
        self.user = dict(self._demo_user)
        self.is_authenticated = True
        self.auth_changed.emit(True)
        return True

    def register(self, full_name: str, email: str, password: str) -> bool:
        try:
            payload = self.api.register(full_name=full_name, email=email, password=password)
            token = payload.get("token")
            if token:
                self.api.set_token(token)
            self.user = payload.get("user") or {"fullName": full_name, "email": email, "role": "Сотрудник"}
            self.is_authenticated = True
            self.auth_changed.emit(True)
            return True
        except ApiError as exc:
            self.error.emit(str(exc))
            return False

    def logout(self) -> None:
        self.api.set_token(None)
        self.user = None
        self.is_authenticated = False
        self.auth_changed.emit(False)

    def load_profile(self) -> None:
        try:
            profile = self.api.get_profile()
            self.profile_changed.emit(profile)
        except ApiError as exc:
            self.error.emit(str(exc))

    def save_profile(self, payload: Dict[str, Any]) -> None:
        try:
            profile = self.api.update_profile(payload)
            self.profile_changed.emit(profile)
        except ApiError as exc:
            self.error.emit(str(exc))

    def load_courses(self, q: str = "") -> None:
        try:
            data = self.api.get_courses(q)
            courses: List[dict] = data.get("items") or data.get("courses") or []
            self.courses_changed.emit(courses)
        except ApiError as exc:
            self.error.emit(str(exc))

    def load_notifications(self) -> None:
        try:
            data = self.api.get_notifications()
            items = data.get("items") or data.get("notifications") or []
            self.notifications_changed.emit(items)
        except ApiError as exc:
            self.error.emit(str(exc))

    def load_topics(self) -> None:
        try:
            data = self.api.get_topics()
            items = data.get("items") or data.get("topics") or []
            self.forum_changed.emit(items)
        except ApiError as exc:
            self.error.emit(str(exc))
