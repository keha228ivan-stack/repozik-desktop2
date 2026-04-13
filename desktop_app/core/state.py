from typing import Any, Dict, List

from PySide6.QtCore import QObject, Signal

from desktop_app.api.client import ApiClient, ApiError


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
