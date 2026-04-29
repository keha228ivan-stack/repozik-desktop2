from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget

from desktop_app.core.state import AppState


STATUS_COLORS = {"NOT_STARTED": "#6b7280", "IN_PROGRESS": "#2563eb", "COMPLETED": "#16a34a", "OVERDUE": "#dc2626", "LOW_SCORE": "#f59e0b"}


class CoursesPage(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.search = QLineEdit()
        self.search.setPlaceholderText("Поиск курсов")
        self.filter = QComboBox()
        self.filter.addItems(["ALL", "NOT_STARTED", "IN_PROGRESS", "COMPLETED", "OVERDUE"])
        btn = QPushButton("Применить")
        btn.clicked.connect(self.refresh)
        top = QHBoxLayout()
        top.addWidget(self.search)
        top.addWidget(self.filter)
        top.addWidget(btn)
        self.status = QLabel("")
        self.container = QVBoxLayout()
        wrap = QWidget(); wrap.setLayout(self.container)
        sc = QScrollArea(); sc.setWidgetResizable(True); sc.setWidget(wrap)
        root = QVBoxLayout(self)
        root.addLayout(top); root.addWidget(self.status); root.addWidget(sc)
        self.state.courses_changed.connect(self._set_courses)
        self.state.courses_error.connect(self.status.setText)

    def refresh(self) -> None:
        self.status.setText("Загрузка курсов...")
        self.state.load_courses(self.search.text().strip(), self.filter.currentText())

    def _set_courses(self, courses: list) -> None:
        while self.container.count():
            child = self.container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        if not courses:
            self.status.setText("Вам пока не назначены курсы")
            return
        self.status.setText("")
        for c in courses:
            self.container.addWidget(self._card(c))
        self.container.addStretch(1)

    def _card(self, c: dict) -> QWidget:
        frame = QFrame()
        l = QVBoxLayout(frame)
        color = STATUS_COLORS.get(c.get("status"), "#6b7280")
        l.addWidget(QLabel(f"<b>{c.get('title')}</b>"))
        l.addWidget(QLabel(c.get("description", "")))
        l.addWidget(QLabel(f"Статус: <span style='color:{color}'>{c.get('status')}</span> | Прогресс: {c.get('progress', 0)}% | Уроков: {c.get('lessonsCount', 0)} | Время: ~{c.get('estimatedMinutes', 0)} мин | Дедлайн: {c.get('deadline', '—')}"))
        action = QPushButton("Начать" if c.get("status") == "NOT_STARTED" else "Продолжить" if c.get("status") in {"IN_PROGRESS", "OVERDUE", "LOW_SCORE"} else "Посмотреть результат")
        if c.get("status") == "NOT_STARTED":
            action.clicked.connect(lambda _=False, cid=c.get("id"): self.state.start_course(str(cid)))
        l.addWidget(action, alignment=Qt.AlignmentFlag.AlignLeft)
        return frame
