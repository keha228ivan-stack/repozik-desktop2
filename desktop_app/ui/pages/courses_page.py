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
        self.title = QLabel("Курсы")
        self.title.setObjectName("coursesTitle")
        self.search = QLineEdit()
        self.search.setPlaceholderText("Поиск курсов")
        self.search.setObjectName("coursesSearch")
        self.list = QListWidget()
        self.list.setObjectName("coursesList")
        self.status = QLabel("")
        self.status.setObjectName("coursesStatus")

        btn = QPushButton("Поиск")
        btn.setObjectName("searchButton")
        btn.clicked.connect(self.refresh)

        top = QHBoxLayout()
        top.addWidget(self.search)
        top.addWidget(btn)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 18, 24, 20)
        layout.setSpacing(12)
        layout.addWidget(self.title)
        layout.addLayout(top)
        layout.addWidget(self.status)
        layout.addWidget(self.list)
        self.setLayout(layout)
        self._apply_styles()

        self.state.courses_changed.connect(self._set_courses)
        self.state.courses_error.connect(self._set_error)

    def refresh(self) -> None:
        self.status.setText("Загрузка курсов...")
        self.state.load_courses(self.search.text().strip())

    def _set_courses(self, courses: list) -> None:
        self.list.clear()
        for item in courses:
            self.list.addItem(item.get("title", "Untitled"))

        if not courses:
            self.status.setText("Курсы не найдены.")
        else:
            self.status.setText("")

    def _set_error(self, text: str) -> None:
        if text:
            self.status.setText(text)

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QLabel#coursesTitle { font-size: 30px; font-weight: 700; color: #1f2937; }
            QLineEdit#coursesSearch {
                background: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 10px;
                padding: 10px 12px;
                font-size: 15px;
            }
            QPushButton#searchButton {
                background: #2563eb;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 10px 16px;
                font-weight: 600;
                min-width: 110px;
            }
            QPushButton#searchButton:hover { background: #1d4ed8; }
            QLabel#coursesStatus { color: #b45309; font-size: 14px; }
            QListWidget#coursesList {
                background: #f8fafc;
                border: 1px solid #e5e7eb;
                border-radius: 14px;
                font-size: 18px;
                color: #334155;
                padding: 6px;
            }
            QListWidget#coursesList::item { padding: 12px; border-radius: 10px; margin: 4px 0; }
            QListWidget#coursesList::item:hover { background: #eff6ff; }
            """
        )
