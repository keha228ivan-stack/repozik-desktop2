from __future__ import annotations

from datetime import datetime, date
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

    def register(self, full_name: str, email: str, password: str, department: str) -> bool:
        try:
            payload = self.local_auth.register(full_name=full_name, email=email, password=password, department=department)
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
            courses = self._apply_overdue_status(courses)
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
            profile = self.api.get_profile() if not self.offline_mode else self._build_local_profile()
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
            if course and course.get("status") != "COMPLETED":
                course["status"] = "IN_PROGRESS"
                course["startedAt"] = datetime.utcnow().isoformat()
                course["progress"] = 0
                course["readyForTest"] = False
                course.pop("testResult", None)
                for lesson in course.get("lessons", []):
                    lesson["status"] = "AVAILABLE"
        else:
            self.api.start_course(course_id)
        self.load_dashboard()

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
        self.load_dashboard()

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
            self.load_dashboard()
            return result
        result = self.api.submit_test(course_id, answers)
        self.load_dashboard()
        return result

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


    def _apply_overdue_status(self, courses: list[dict[str, Any]]) -> list[dict[str, Any]]:
        today = date.today()
        for course in courses:
            deadline = course.get("deadline")
            status = course.get("status")
            if not deadline or status in {"COMPLETED"}:
                continue
            try:
                deadline_date = datetime.fromisoformat(str(deadline)).date()
            except ValueError:
                continue
            if deadline_date < today and status in {"NOT_STARTED", "IN_PROGRESS", "LOW_SCORE"}:
                course["status"] = "OVERDUE"
        return courses

    def _build_dashboard_from_courses(self, courses: list[dict[str, Any]]) -> dict[str, Any]:
        courses = self._apply_overdue_status(courses)
        total = len(courses)
        in_progress = len([c for c in courses if c.get("status") == "IN_PROGRESS"])
        completed = len([c for c in courses if c.get("status") == "COMPLETED"])
        in_progress_courses = [c for c in courses if c.get("status") == "IN_PROGRESS"]
        avg_progress = int(sum(int(c.get("progress", 0)) for c in in_progress_courses) / len(in_progress_courses)) if in_progress_courses else 0
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
            {"id": "1", "title": "Охрана труда", "description": "Базовые правила", "status": "NOT_STARTED", "progress": 0, "lessonsCount": 6, "estimatedMinutes": 120, "deadline": "2026-05-03", "testQuestions": [{"q": "Что делать при пожаре?", "options": ["Паниковать", "Сообщить и эвакуироваться", "Игнорировать"]}], "lessons": [{"id": "1-1", "title": "Введение", "status": "AVAILABLE", "content": "В этом уроке вы узнаете общие требования по охране труда и обязанности сотрудника."}, {"id": "1-2", "title": "Инструктаж", "status": "AVAILABLE", "content": "Порядок прохождения вводного и повторного инструктажа, фиксация в журнале."}, {"id": "1-3", "title": "Практика", "status": "AVAILABLE", "content": "Разбор типовых кейсов: СИЗ, эвакуация, действия при инциденте."}]},
            {"id": "2", "title": "Командная работа", "description": "Коммуникации", "status": "NOT_STARTED", "progress": 0, "lessonsCount": 5, "estimatedMinutes": 95, "deadline": "2026-05-12", "testQuestions": [{"q": "Как давать обратную связь?", "options": ["Через факты и действия", "Через эмоции", "Никак"]}], "lessons": [{"id": "2-1", "title": "Роли в команде", "status": "AVAILABLE", "content": "Описание ролей: лидер, исполнитель, аналитик, координатор."}, {"id": "2-2", "title": "Обратная связь", "status": "AVAILABLE", "content": "Модель SBI: ситуация, поведение, влияние. Практика конструктивного диалога."}]},
            {"id": "3", "title": "Антифрод", "description": "Проверка рисков", "status": "NOT_STARTED", "progress": 0, "lessonsCount": 7, "estimatedMinutes": 140, "deadline": "2026-04-20", "testQuestions": [{"q": "Признак подозрительной операции?", "options": ["Крупная нетипичная сумма", "Обычный платёж", "Регулярная зарплата"]}], "lessons": [{"id": "3-1", "title": "Риски", "status": "AVAILABLE", "content": "Основные виды мошенничества: социальная инженерия, подмена реквизитов, фишинг."}]},
            {"id": "4", "title": "Этика и комплаенс", "description": "Нормы поведения", "status": "NOT_STARTED", "progress": 0, "lessonsCount": 8, "estimatedMinutes": 170, "deadline": "2026-04-10", "testQuestions": [{"q": "Что делать при конфликте интересов?", "options": ["Скрыть", "Сообщить руководителю", "Игнорировать"]}], "lessons": [{"id": "4-1", "title": "Кодекс", "status": "AVAILABLE", "content": "Кодекс поведения: уважение, законность, прозрачность и ответственность."}, {"id": "4-2", "title": "Конфликты интересов", "status": "AVAILABLE", "content": "Как выявлять и декларировать конфликт интересов, примеры и действия."}]},
        ]


    def _build_local_profile(self) -> dict[str, Any]:
        user = self.user or {}
        courses = self._local_courses
        assigned = len(courses)
        completed = len([c for c in courses if c.get("status") == "COMPLETED"])
        avg_progress = int(sum(int(c.get("progress", 0)) for c in courses) / assigned) if assigned else 0
        return {
            "fullName": user.get("fullName", "Сотрудник"),
            "email": user.get("email", "—"),
            "position": user.get("position", "Сотрудник"),
            "department": user.get("department", "—"),
            "registeredAt": user.get("registeredAt", "—"),
            "role": user.get("role", "Сотрудник"),
            "overallProgress": avg_progress,
            "assignedCourses": assigned,
            "completedCourses": completed,
            "averageScore": 0,
        }

    def _mock_profile(self) -> dict[str, Any]:
        return {
            "fullName": "Иван Петров",
            "email": "i.petrov@company.local",
            "position": "HR Specialist",
            "department": "People Operations",
            "registeredAt": "2025-09-01",
            "role": "Сотрудник",
            "overallProgress": 0,
            "assignedCourses": 4,
            "completedCourses": 0,
            "averageScore": 0,
            "history": self._mock_courses(),
        }
