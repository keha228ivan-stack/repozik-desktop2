from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from desktop_app.core.state import AppState


class ProfilePage(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state

        page_title = QLabel("Личный кабинет")
        page_title.setObjectName("pageTitle")

        card = QFrame()
        card.setObjectName("profileCard")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)

        card_title = QLabel("Данные профиля")
        card_title.setObjectName("profileCardTitle")

        self.name_value = QLabel("Имя: —")
        self.email_value = QLabel("Email: —")
        self.role_value = QLabel("Роль: —")
        for lbl in (self.name_value, self.email_value, self.role_value):
            lbl.setObjectName("profileValue")

        self.status = QLabel("")
        self.status.setObjectName("statusText")

        logout_btn = QPushButton("Выйти")
        logout_btn.clicked.connect(self.state.logout)

        card_layout.addWidget(card_title)
        card_layout.addWidget(self.name_value)
        card_layout.addWidget(self.email_value)
        card_layout.addWidget(self.role_value)

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(12)
        layout.addWidget(page_title)
        layout.addWidget(card)
        layout.addWidget(self.status)
        layout.addStretch(1)
        layout.addWidget(logout_btn)
        self.setLayout(layout)

        self.state.profile_changed.connect(self._set_profile)
        self.state.profile_error.connect(self._set_error)

    def refresh(self) -> None:
        self.status.setText("Загрузка профиля...")
        self.state.load_profile()

    def _set_profile(self, p: dict) -> None:
        user = self.state.user or {}

        full_name = p.get("fullName") or user.get("fullName") or user.get("name") or "—"
        email = p.get("email") or user.get("email") or "—"
        role = p.get("role") or user.get("role") or "Сотрудник"

        self.name_value.setText(f"Имя: {full_name}")
        self.email_value.setText(f"Email: {email}")
        self.role_value.setText(f"Роль: {role}")
        self.status.setText("")

    def _set_error(self, msg: str) -> None:
        self.status.setText(msg)
