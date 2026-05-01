from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from desktop_app.core.state import AppState


class ProfilePage(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(16)

        title = QLabel("Профиль")
        title.setObjectName("pageTitle")
        root.addWidget(title)

        self.header = QFrame()
        self.header.setObjectName("surfaceCard")
        header_layout = QVBoxLayout(self.header)
        self.name = QLabel("Сотрудник")
        self.name.setObjectName("name")
        self.role = QLabel("—")
        self.role.setObjectName("meta")
        header_layout.addWidget(self.name)
        header_layout.addWidget(self.role)

        self.info_card = QFrame()
        self.info_card.setObjectName("surfaceCard")
        info_layout = QGridLayout(self.info_card)
        self.contacts = QLabel("—")
        self.work = QLabel("—")
        self.metrics = QLabel("—")
        for lbl in [self.contacts, self.work, self.metrics]:
            lbl.setObjectName("profileText")
            lbl.setWordWrap(True)
        info_layout.addWidget(self.contacts, 0, 0)
        info_layout.addWidget(self.work, 0, 1)
        info_layout.addWidget(self.metrics, 1, 0, 1, 2)

        self.status = QLabel("")
        self.status.setObjectName("status")

        refresh_btn = QPushButton("Обновить")
        refresh_btn.setObjectName("primaryButton")
        refresh_btn.clicked.connect(self.refresh)

        root.addWidget(self.header)
        root.addWidget(self.info_card)
        root.addWidget(self.status)
        root.addWidget(refresh_btn)

        self.state.profile_changed.connect(self._set_profile)
        self.state.profile_error.connect(self.status.setText)

        self.setStyleSheet("""
            QLabel#pageTitle { font-size: 44px; font-weight: 800; color: #0f172a; }
            QFrame#surfaceCard { background: white; border: 1px solid #E5E7EB; border-radius: 16px; padding: 14px; }
            QLabel#name { font-size: 30px; font-weight: 800; color: #0f172a; }
            QLabel#meta { color: #64748B; font-size: 14px; }
            QLabel#profileText { color: #334155; font-size: 15px; }
            QLabel#status { color: #475569; }
        """)

    def refresh(self) -> None:
        self.status.setText("Загрузка профиля...")
        self.state.load_profile()

    def _set_profile(self, p: dict) -> None:
        self.name.setText(p.get("fullName", "Сотрудник"))
        self.role.setText(f"{p.get('role', '—')} • {p.get('department', '—')}")
        self.contacts.setText(
            f"Email: {p.get('email', '—')}\n"
            f"Дата регистрации: {p.get('registeredAt', '—')}"
        )
        self.work.setText(
            f"Должность: {p.get('position', '—')}\n"
            f"Отдел: {p.get('department', '—')}"
        )
        self.metrics.setText(
            f"Общий прогресс: {p.get('overallProgress', 0)}%\n"
            f"Средний балл: {p.get('averageScore', 0)}%\n"
            f"Назначено курсов: {p.get('assignedCourses', 0)}"
        )
        self.status.setText("")
