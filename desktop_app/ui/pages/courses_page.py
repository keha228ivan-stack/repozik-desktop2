from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QProgressBar, QScrollArea, QVBoxLayout, QWidget

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
        self.setStyleSheet("""
            QFrame#surfaceCard { background: white; border: 1px solid #E5E7EB; border-radius: 12px; }
            QLabel#courseTitle { font-size: 16px; font-weight: 700; }
            QLabel#courseMeta { color: #6B7280; }
            QLabel#courseBadge { font-weight: 600; padding: 2px 8px; border-radius: 8px; background: #F3F4F6; }
            QProgressBar { border: 0; background: #E5E7EB; border-radius: 4px; height: 8px; }
            QProgressBar::chunk { background: #2563EB; border-radius: 4px; }
        """)
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
        frame.setObjectName("surfaceCard")
        l = QVBoxLayout(frame)
        color = STATUS_COLORS.get(c.get("status"), "#6b7280")
        title = QLabel(c.get('title')); title.setObjectName("courseTitle")
        desc = QLabel(c.get("description", "")); desc.setObjectName("courseMeta")
        badge = QLabel(c.get("status")); badge.setObjectName("courseBadge")
        badge.setStyleSheet(f"color:{color};")
        meta = QLabel(f"Уроков: {c.get('lessonsCount', 0)} • ~{c.get('estimatedMinutes', 0)} мин • Дедлайн: {c.get('deadline', '—')}")
        meta.setObjectName("courseMeta")
        progress = QProgressBar(); progress.setRange(0,100); progress.setValue(int(c.get("progress",0)))
        l.addWidget(title); l.addWidget(desc); l.addWidget(badge); l.addWidget(progress); l.addWidget(meta)
        action = QPushButton("Начать" if c.get("status") == "NOT_STARTED" else "Продолжить" if c.get("status") in {"IN_PROGRESS", "OVERDUE", "LOW_SCORE"} else "Посмотреть результат")
        if c.get("status") == "NOT_STARTED":
            action.clicked.connect(lambda _=False, cid=c.get("id"): self.state.start_course(str(cid)))
        l.addWidget(action, alignment=Qt.AlignmentFlag.AlignLeft)
        return frame
