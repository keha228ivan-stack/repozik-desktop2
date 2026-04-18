from PySide6.QtWidgets import (
    QFormLayout,
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

        title = QLabel("Личный кабинет")
        title.setObjectName("pageTitle")

        self.full_name = QLineEdit()
        self.phone = QLineEdit()

        self.status = QLabel("")
        self.status.setObjectName("statusText")

        form = QFormLayout()
        form.setSpacing(10)
        form.addRow("ФИО", self.full_name)
        form.addRow("Телефон", self.phone)

        save = QPushButton("Сохранить")
        save.clicked.connect(self._save)

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addLayout(form)
        layout.addWidget(self.status)
        layout.addWidget(save)
        layout.addStretch(1)
        self.setLayout(layout)

        self.state.profile_changed.connect(self._set_profile)
        self.state.profile_error.connect(self._set_error)

    def refresh(self) -> None:
        self.status.setText("Загрузка профиля...")
        self.state.load_profile()

    def _save(self) -> None:
        self.status.setText("Сохранение...")
        self.state.save_profile({"fullName": self.full_name.text().strip(), "phone": self.phone.text().strip()})

    def _set_profile(self, p: dict) -> None:
        self.full_name.setText(p.get("fullName", ""))
        self.phone.setText(p.get("phone", ""))
        if p:
            self.status.setText("")

    def _set_error(self, msg: str) -> None:
        self.status.setText(msg)
