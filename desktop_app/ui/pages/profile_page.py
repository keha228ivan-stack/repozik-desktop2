from PySide6.QtWidgets import (
    QFrame,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from desktop_app.core.state import AppState


class ProfilePage(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state

        self.full_name = QLineEdit()
        self.phone = QLineEdit()
        self.status = QLabel("")
        self.status.setStyleSheet("color: #b45309;")

        self.profile_card = QFrame()
        self.profile_card.setObjectName("profileCard")
        card_layout = QVBoxLayout(self.profile_card)
        card_title = QLabel("Данные профиля")
        card_title.setObjectName("profileCardTitle")
        card_layout.addWidget(card_title)

        self.name_label = QLabel("Имя: —")
        self.email_label = QLabel("Email: —")
        self.role_label = QLabel("Роль: —")
        for label in (self.name_label, self.email_label, self.role_label):
            label.setObjectName("profileCardText")
            card_layout.addWidget(label)

        form = QFormLayout()
        form.addRow("Full name", self.full_name)
        form.addRow("Phone", self.phone)

        save = QPushButton("Save")
        save.clicked.connect(self._save)
        logout_btn = QPushButton("Выйти")
        logout_btn.clicked.connect(self.state.logout)

        actions = QHBoxLayout()
        actions.addWidget(save)
        actions.addWidget(logout_btn)
        actions.addStretch(1)

        layout = QVBoxLayout()
        layout.addWidget(self.profile_card)
        layout.addLayout(form)
        layout.addWidget(self.status)
        layout.addLayout(actions)
        layout.addStretch(1)
        self.setLayout(layout)
        self.setStyleSheet(
            """
            QFrame#profileCard { background: #e5e7eb; border-radius: 18px; padding: 12px; }
            QLabel#profileCardTitle { font-size: 30px; font-weight: 700; color: #1f2937; }
            QLabel#profileCardText { font-size: 22px; color: #1f2937; }
            """
        )

        self.state.profile_changed.connect(self._set_profile)
        self.state.profile_error.connect(self._set_error)

    def refresh(self) -> None:
        self.status.setText("Загрузка профиля...")
        self.state.load_profile()

    def _save(self) -> None:
        self.status.setText("Сохранение...")
        self.state.save_profile({"fullName": self.full_name.text().strip(), "phone": self.phone.text().strip()})

    def _set_profile(self, p: dict) -> None:
        user = self.state.user or {}
        full_name = p.get("fullName") or user.get("fullName", "")
        email = p.get("email") or user.get("email", "")
        role = p.get("role") or user.get("role", "Сотрудник")

        self.full_name.setText(full_name)
        self.phone.setText(p.get("phone", ""))
        self.name_label.setText(f"Имя: {full_name or '—'}")
        self.email_label.setText(f"Email: {email or '—'}")
        self.role_label.setText(f"Роль: {role or '—'}")
        if p:
            self.status.setText("")

    def _set_error(self, msg: str) -> None:
        self.status.setText(msg)
