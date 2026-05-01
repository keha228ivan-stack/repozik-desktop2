from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Dict, List

from desktop_app.api.client import ApiClient
from desktop_app.api.errors import ApiError
from desktop_app.services.local_auth_service import LocalAuthService


class _SimpleSignal:
    def __init__(self) -> None:
        self._subs: List[Callable] = []

    def connect(self, fn: Callable) -> None:
        self._subs.append(fn)

    def emit(self, *args: Any, **kwargs: Any) -> None:
        for fn in list(self._subs):
            fn(*args, **kwargs)


try:
    from PySide6.QtCore import QObject, Signal
except Exception:
    class QObject:
        pass

    def Signal(*_args: Any, **_kwargs: Any) -> _SimpleSignal:
        return _SimpleSignal()


class AppState(QObject):
    auth_changed = Signal(bool)
    backend_status_changed = Signal(bool, str)
    error = Signal(str)

    profile_changed = Signal(dict)
    profile_error = Signal(str)
    courses_changed = Signal(list)
    courses_error = Signal(str)
    dashboard_changed = Signal(dict)
    notifications_changed = Signal(list)
    notifications_error = Signal(str)
    forum_changed = Signal(list)
    forum_error = Signal(str)

    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self.api = api
        self.local_auth = LocalAuthService()
        self.user: Dict[str, Any] | None = None
        self.is_authenticated = False
        self.offline_mode = False
        self.courses: list[dict[str, Any]] = []
        self._local_courses: list[dict[str, Any]] = self._mock_courses()
        current_user = self.local_auth.get_current_user()
        if current_user:
            self.user = current_user
            self.is_authenticated = True

    def refresh_backend_status(self) -> bool:
        available = self.api.health_check()
        self.backend_status_changed.emit(available, "Backend доступен" if available else "Backend недоступен")
        self.offline_mode = not available
        return available

    def login(self, email: str, password: str) -> bool:
        try:
            payload = self.local_auth.login(email, password)
            token = payload.get("token")
            if token:
                self.api.set_token(token)
            self.user = payload.get("user")
            self.is_authenticated = True
            self.auth_changed.emit(True)
            return True
        except ApiError as exc:
            self.error.emit(str(exc))
            return False

    def register(self, full_name: str, email: str, password: str) -> bool:
        try:
            payload = self.local_auth.register(full_name=full_name, email=email, password=password)
            token = payload.get("token")
            if token:
                self.api.set_token(token)
            self.user = payload.get("user")
            self.is_authenticated = True
            self.auth_changed.emit(True)
            return True
        except ApiError as exc:
            self.error.emit(str(exc))
            return False

    def logout(self) -> None:
        self.local_auth.logout()
        self.api.set_token(None)
        self.user = None
        self.is_authenticated = False
        self.auth_changed.emit(False)

    def load_dashboard(self) -> None:
        try:
            data = self.api.get_employee_courses() if not self.offline_mode else {"courses": self._local_courses}
            courses = data.get("courses") or data.get("items") or []
            self.dashboard_changed.emit(self._build_dashboard_from_courses(courses))
        except ApiError:
            self.dashboard_changed.emit(self._build_dashboard_from_courses(self._local_courses))

    def load_courses(self, q: str = "", status: str = "ALL") -> None:
        try:
            data = self.api.get_employee_courses() if not self.offline_mode else {"courses": self._local_courses}
            courses = data.get("courses") or data.get("items") or []
            if q:
                courses = [c for c in courses if q.lower() in c.get("title", "").lower()]
            if status != "ALL":
                courses = [c for c in courses if c.get("status") == status]
            self.courses = courses
            self.courses_changed.emit(courses)
            self.courses_error.emit("")
        except ApiError as exc:
            self.courses_changed.emit([])
            self.courses_error.emit(str(exc))

    def load_profile(self) -> None:
        try:
            profile = self.api.get_profile() if not self.offline_mode else self._mock_profile()
            self.profile_changed.emit(profile)
            self.profile_error.emit("")
        except ApiError as exc:
            self.profile_changed.emit({})
            self.profile_error.emit(str(exc))

    def save_profile(self, payload: Dict[str, Any]) -> None:
        try:
            profile = self.api.update_profile(payload) if not self.offline_mode else payload
            self.profile_changed.emit(profile)
            self.profile_error.emit("Сохранено")
        except ApiError as exc:
            self.profile_error.emit(str(exc))

    def start_course(self, course_id: str) -> None:
        if self.offline_mode:
            course = self.get_course_details(course_id)
            if course and course.get("status") == "NOT_STARTED":
                course["status"] = "IN_PROGRESS"
                course["startedAt"] = datetime.utcnow().isoformat()
        else:
            self.api.start_course(course_id)

    def complete_lesson(self, course_id: str, lesson_id: str) -> None:
        if self.offline_mode:
            course = self.get_course_details(course_id)
            if not course:
                return
            lessons = course.get("lessons", [])
            for lesson in lessons:
                if str(lesson.get("id")) == str(lesson_id):
                    lesson["status"] = "COMPLETED"
            total = max(len(lessons), 1)
            completed = len([l for l in lessons if l.get("status") == "COMPLETED"])
            course["progress"] = int((completed / total) * 100)
            if completed > 0 and course.get("status") == "NOT_STARTED":
                course["status"] = "IN_PROGRESS"
            if completed == total:
                course["readyForTest"] = True
        else:
            self.api.complete_lesson(course_id, lesson_id)

    def submit_test(self, course_id: str, answers: list[dict[str, Any]]) -> dict[str, Any]:
        if self.offline_mode:
            course = self.get_course_details(course_id)
            score = 7
            max_score = 10
            percent = int((score / max_score) * 100)
            passed = percent >= 70
            result = {"score": score, "maxScore": max_score, "percent": percent, "passed": passed, "attempts": 1, "completedAt": datetime.utcnow().isoformat()}
            if course:
                course["testResult"] = f"{percent}%"
                course["status"] = "COMPLETED" if passed else "LOW_SCORE"
                course["completedAt"] = result["completedAt"]
                course["progress"] = 100
            return result
        return self.api.submit_test(course_id, answers)

    def get_course_details(self, course_id: str) -> dict[str, Any] | None:
        for c in self._local_courses:
            if str(c.get("id")) == str(course_id):
                return c
        return None


    def load_notifications(self) -> None:
        self.notifications_changed.emit([])
        self.notifications_error.emit("")

    def load_topics(self) -> None:
        self.forum_changed.emit([])
        self.forum_error.emit("")

    def create_topic(self, title: str, body: str) -> bool:
        return False

    def _build_dashboard_from_courses(self, courses: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(courses)
        in_progress = len([c for c in courses if c.get("status") in {"IN_PROGRESS", "OVERDUE", "LOW_SCORE"}])
        completed = len([c for c in courses if c.get("status") == "COMPLETED"])
        avg_progress = int(sum(int(c.get("progress", 0)) for c in courses) / total) if total else 0
        nearest_deadline = "—"
        deadlines = sorted([c.get("deadline") for c in courses if c.get("deadline") and c.get("status") != "COMPLETED"])
        if deadlines:
            nearest_deadline = deadlines[0]
        recent_courses = [c.get("title", "") for c in sorted(courses, key=lambda x: int(x.get("progress", 0)), reverse=True)[:3]]
        return {
            "totalCourses": total,
            "inProgressCourses": in_progress,
            "completedCourses": completed,
            "averageProgress": avg_progress,
            "averageScore": 0,
            "overdueCourses": len([c for c in courses if c.get("status") == "OVERDUE"]),
            "nearestDeadline": nearest_deadline,
            "recentCourses": [c for c in recent_courses if c],
        }

    def _dashboard_fallback(self) -> dict[str, Any]:
        return {
            "totalCourses": 4,
            "inProgressCourses": 2,
            "completedCourses": 1,
            "averageProgress": 48,
            "averageScore": 76,
            "overdueCourses": 1,
            "nearestDeadline": "2026-05-03",
            "recentCourses": ["Командная работа", "Охрана труда"],
        }

    def _mock_courses(self) -> list[dict[str, Any]]:
        return [
            {"id": "1", "title": "Охрана труда", "description": "Базовые правила", "status": "IN_PROGRESS", "progress": 35, "lessonsCount": 6, "estimatedMinutes": 120, "deadline": "2026-05-03", "lastLesson": "Модуль 2", "lessons": [{"id": "1-1", "title": "Введение", "status": "COMPLETED"}, {"id": "1-2", "title": "Инструктаж", "status": "AVAILABLE"}, {"id": "1-3", "title": "Практика", "status": "AVAILABLE"}]},
            {"id": "2", "title": "Командная работа", "description": "Коммуникации", "status": "NOT_STARTED", "progress": 0, "lessonsCount": 5, "estimatedMinutes": 95, "deadline": "2026-05-12", "lessons": [{"id": "2-1", "title": "Роли в команде", "status": "AVAILABLE"}, {"id": "2-2", "title": "Обратная связь", "status": "AVAILABLE"}]},
            {"id": "3", "title": "Антифрод", "description": "Проверка рисков", "status": "COMPLETED", "progress": 100, "lessonsCount": 7, "estimatedMinutes": 140, "deadline": "2026-04-20", "testResult": "86%", "lessons": [{"id": "3-1", "title": "Риски", "status": "COMPLETED"}]},
            {"id": "4", "title": "Этика и комплаенс", "description": "Нормы поведения", "status": "OVERDUE", "progress": 50, "lessonsCount": 8, "estimatedMinutes": 170, "deadline": "2026-04-10", "lastLesson": "Модуль 4", "lessons": [{"id": "4-1", "title": "Кодекс", "status": "COMPLETED"}, {"id": "4-2", "title": "Конфликты интересов", "status": "AVAILABLE"}]},
        ]

    def _mock_profile(self) -> dict[str, Any]:
        return {
            "fullName": "Иван Петров",
            "email": "i.petrov@company.local",
            "position": "HR Specialist",
            "department": "People Operations",
            "registeredAt": "2025-09-01",
            "role": "Сотрудник",
            "overallProgress": 62,
            "assignedCourses": 12,
            "completedCourses": 7,
            "averageScore": 81,
            "history": self._mock_courses(),
        }
