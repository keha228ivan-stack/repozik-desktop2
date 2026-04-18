from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from desktop_app.core.state import AppState


class CoursesPage(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state

        self.search = QLineEdit()
        self.search.setPlaceholderText("Поиск курса по названию")

        self.list = QListWidget()
        self.list.setObjectName("contentList")

        self.status = QLabel("")
        self.status.setObjectName("statusText")

        title = QLabel("Библиотека курсов")
        title.setObjectName("pageTitle")

        btn = QPushButton("Поиск")
        btn.clicked.connect(self.refresh)

        top = QHBoxLayout()
        top.setSpacing(10)
        top.addWidget(self.search, 1)
        top.addWidget(btn)

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addLayout(top)
        layout.addWidget(self.status)
        layout.addWidget(self.list, 1)
        self.setLayout(layout)

        self.state.courses_changed.connect(self._set_courses)
        self.state.courses_error.connect(self._set_error)

    def refresh(self) -> None:
        self.status.setText("Загрузка курсов...")
        self.state.load_courses(self.search.text().strip())

    def _set_courses(self, courses: list) -> None:
        self.list.clear()
        for item in courses:
            self.list.addItem(item.get("title", "Без названия"))

        if not courses:
            self.status.setText("Курсы не найдены.")
        else:
            self.status.setText("")

    def _set_error(self, text: str) -> None:
        if text:
            self.status.setText(text)
