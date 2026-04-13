from PySide6.QtWidgets import (
    QHBoxLayout,
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
        self.search.setPlaceholderText("Поиск курсов")
        self.list = QListWidget()

        btn = QPushButton("Search")
        btn.clicked.connect(self.refresh)

        top = QHBoxLayout()
        top.addWidget(self.search)
        top.addWidget(btn)

        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addWidget(self.list)
        self.setLayout(layout)

        self.state.courses_changed.connect(self._set_courses)

    def refresh(self) -> None:
        self.state.load_courses(self.search.text().strip())

    def _set_courses(self, courses: list) -> None:
        self.list.clear()
        for item in courses:
            self.list.addItem(item.get("title", "Untitled"))
