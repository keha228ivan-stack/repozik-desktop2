from PySide6.QtCore import Qt
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
        self.status.setObjectName("profileStatus")

        self.profile_card = QFrame()
        self.profile_card.setObjectName("profileCard")
        profile_layout = QVBoxLayout(self.profile_card)
        profile_title = QLabel("Данные профиля")
        profile_title.setObjectName("profileCardTitle")
        self.name_label = QLabel("Имя: —")
        self.email_label = QLabel("Email: —")
        self.role_label = QLabel("Роль: —")
        for item in (self.name_label, self.email_label, self.role_label):
            item.setObjectName("profileCardText")
        profile_layout.addWidget(profile_title)
        profile_layout.addWidget(self.name_label)
        profile_layout.addWidget(self.email_label)
        profile_layout.addWidget(self.role_label)

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
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.addRow("Full name", self.full_name)
        form.addRow("Phone", self.phone)

        save = QPushButton("Save")
        save.setObjectName("primaryButton")
        save.clicked.connect(self._save)
        logout = QPushButton("Выйти")
        logout.setObjectName("logoutButton")
        logout.clicked.connect(self.state.logout)

        actions = QHBoxLayout()
        actions.addWidget(save)
        actions.addWidget(logout)
        actions.addStretch(1)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 18, 24, 20)
        layout.setSpacing(12)
        layout.addWidget(self.profile_card)
        layout.addLayout(form)
        layout.addWidget(self.status)
        layout.addLayout(actions)
        layout.addStretch(1)
        self.setLayout(layout)
        self._apply_styles()

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

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QFrame#profileCard { background: #e5e7eb; border-radius: 16px; padding: 10px; }
            QLabel#profileCardTitle { font-size: 26px; font-weight: 700; color: #1f2937; }
            QLabel#profileCardText { font-size: 18px; color: #1f2937; padding-bottom: 2px; }
            QLabel#profileStatus { color: #b45309; font-size: 14px; }
            QLineEdit { border: 1px solid #cbd5e1; border-radius: 10px; padding: 8px; background: #fff; }
            QPushButton#primaryButton {
                background: #2563eb; color: white; border: none; border-radius: 10px; padding: 9px 14px; font-weight: 600;
            }
            QPushButton#primaryButton:hover { background: #1d4ed8; }
            QPushButton#logoutButton {
                background: #ffffff; color: #1f2937; border: 1px solid #cbd5e1; border-radius: 10px; padding: 9px 14px; font-weight: 600;
            }
            """
        )
