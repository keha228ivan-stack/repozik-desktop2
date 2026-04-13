from PySide6.QtWidgets import (
    QFormLayout,
    QLineEdit,
    QMessageBox,
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

        form = QFormLayout()
        form.addRow("Full name", self.full_name)
        form.addRow("Phone", self.phone)

        save = QPushButton("Save")
        save.clicked.connect(self._save)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(save)
        self.setLayout(layout)

        self.state.profile_changed.connect(self._set_profile)
        self.state.error.connect(self._show_error)

    def refresh(self) -> None:
        self.state.load_profile()

    def _save(self) -> None:
        self.state.save_profile({"fullName": self.full_name.text().strip(), "phone": self.phone.text().strip()})

    def _set_profile(self, p: dict) -> None:
        self.full_name.setText(p.get("fullName", ""))
        self.phone.setText(p.get("phone", ""))

    def _show_error(self, msg: str) -> None:
        QMessageBox.warning(self, "Profile", msg)
