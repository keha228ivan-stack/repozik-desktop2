from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QListWidget, QPushButton, QVBoxLayout, QWidget

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

        header = QFrame()
        header.setObjectName("surfaceCard")
        header_layout = QVBoxLayout(header)
        self.avatar = QLabel("👤")
        self.avatar.setObjectName("avatar")
        self.name = QLabel("Сотрудник")
        self.name.setObjectName("name")
        self.role = QLabel("—")
        self.role.setObjectName("meta")
        header_layout.addWidget(self.avatar, alignment=Qt.AlignmentFlag.AlignHCenter)
        header_layout.addWidget(self.name, alignment=Qt.AlignmentFlag.AlignHCenter)
        header_layout.addWidget(self.role, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.stats_card = QFrame()
        self.stats_card.setObjectName("surfaceCard")
        stats_layout = QGridLayout(self.stats_card)
        self.contacts = QLabel("—")
        self.work = QLabel("—")
        self.kpi = QLabel("—")
        for w in [self.contacts, self.work, self.kpi]:
            w.setObjectName("profileText")
        stats_layout.addWidget(self.contacts, 0, 0)
        stats_layout.addWidget(self.work, 0, 1)
        stats_layout.addWidget(self.kpi, 1, 0, 1, 2)

        self.status = QLabel("")
        self.status.setObjectName("status")

        history_card = QFrame()
        history_card.setObjectName("surfaceCard")
        history_layout = QVBoxLayout(history_card)
        history_title = QLabel("История курсов")
        history_title.setObjectName("sectionTitle")
        self.history = QListWidget()
        refresh_btn = QPushButton("Обновить")
        refresh_btn.setObjectName("primaryButton")
        refresh_btn.clicked.connect(self.refresh)
        history_layout.addWidget(history_title)
        history_layout.addWidget(self.history)
        history_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignRight)

        root.addWidget(header)
        root.addWidget(self.stats_card)
        root.addWidget(self.status)
        root.addWidget(history_card, 1)

        self.state.profile_changed.connect(self._set_profile)
        self.state.profile_error.connect(self.status.setText)
        self.setStyleSheet("""
            QLabel#pageTitle { font-size: 44px; font-weight: 800; color: #0f172a; }
            QFrame#surfaceCard { background: white; border: 1px solid #E5E7EB; border-radius: 16px; padding: 14px; }
            QLabel#avatar { font-size: 42px; }
            QLabel#name { font-size: 28px; font-weight: 700; color: #0f172a; }
            QLabel#meta { font-size: 14px; color: #64748B; }
            QLabel#profileText { font-size: 15px; color: #334155; }
            QLabel#sectionTitle { font-size: 22px; font-weight: 700; color: #0f172a; }
            QLabel#status { color: #475569; }
            QListWidget { background: #F8FAFC; border: 1px solid #E5E7EB; border-radius: 12px; }
            QListWidget::item { padding: 10px; border-bottom: 1px solid #EEF2F7; }
            QListWidget::item:selected { background: #E2E8F0; color: #0f172a; }
        """)

    def refresh(self) -> None:
        self.status.setText("Загрузка профиля...")
        self.state.load_profile()

    def _set_profile(self, p: dict) -> None:
        self.name.setText(p.get('fullName', 'Сотрудник'))
        self.role.setText(f"{p.get('role', '—')} • {p.get('department', '—')}")
        self.contacts.setText(f"Email: {p.get('email', '—')}\nДата регистрации: {p.get('registeredAt', '—')}")
        self.work.setText(f"Должность: {p.get('position', '—')}\nОтдел: {p.get('department', '—')}")
        self.kpi.setText(
            f"Общий прогресс: {p.get('overallProgress', 0)}%    "
            f"Назначено: {p.get('assignedCourses', 0)}    "
            f"Завершено: {p.get('completedCourses', 0)}    "
            f"Средний балл: {p.get('averageScore', 0)}%"
        )
        self.history.clear()
        for h in p.get("history", []):
            self.history.addItem(
                f"{h.get('title')}  •  {h.get('status')}  •  {h.get('progress', 0)}%  •  Тест: {h.get('testResult', '—')}  •  Дедлайн: {h.get('deadline', '—')}"
            )
        self.status.setText("")
