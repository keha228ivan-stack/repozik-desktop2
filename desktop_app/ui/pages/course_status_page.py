from typing import Literal

from PySide6.QtWidgets import QLabel, QListWidget, QPushButton, QVBoxLayout, QWidget

from desktop_app.core.state import AppState

CourseMode = Literal["completed", "in_progress"]


class CourseStatusPage(QWidget):
    def __init__(self, state: AppState, mode: CourseMode) -> None:
        super().__init__()
        self.state = state
        self.mode = mode

        title_text = "Завершенные курсы" if mode == "completed" else "Курсы в процессе"
        self._empty_text = (
            "Завершенных курсов пока нет."
            if mode == "completed"
            else "Курсов в процессе пока нет."
        )

        title = QLabel(title_text)
        title.setObjectName("pageTitle")

        self.list = QListWidget()
        self.list.setObjectName("contentList")

        self.status = QLabel("")
        self.status.setObjectName("statusText")

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.refresh)

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(self.status)
        layout.addWidget(self.list, 1)
        layout.addWidget(refresh_btn)
        self.setLayout(layout)

        self.state.courses_changed.connect(self._set_courses)
        self.state.courses_error.connect(self._set_error)

    def refresh(self) -> None:
        self.status.setText("Загрузка курсов...")
        self.state.load_courses()

    def _set_courses(self, courses: list) -> None:
        filtered = [course for course in courses if self._matches(course)]

        self.list.clear()
        for item in filtered:
            title = item.get("title", "Без названия")
            progress = item.get("progress")
            if isinstance(progress, (int, float)):
                self.list.addItem(f"{title} — {int(progress)}%")
            else:
                self.list.addItem(title)

        if not filtered:
            self.status.setText(self._empty_text)
        else:
            self.status.setText("")

    def _set_error(self, text: str) -> None:
        if text:
            self.status.setText(text)

    def _matches(self, course: dict) -> bool:
        status_value = str(course.get("status", "")).strip().lower()
        progress = course.get("progress")
        completed = course.get("completed")

        is_completed = (
            status_value in {"completed", "done", "finished", "completed_course", "завершен", "завершено"}
            or completed is True
            or (isinstance(progress, (int, float)) and progress >= 100)
        )

        if self.mode == "completed":
            return is_completed

        has_progress = isinstance(progress, (int, float)) and 0 < progress < 100
        in_progress_status = status_value in {
            "in_progress",
            "in-progress",
            "active",
            "ongoing",
            "в процессе",
            "начат",
        }
        return (not is_completed) and (in_progress_status or has_progress)
