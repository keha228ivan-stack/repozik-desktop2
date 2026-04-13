from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from desktop_app.core.state import AppState


class LoginView(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.setWindowTitle("Repozik Desktop — Login")
        self.resize(380, 200)

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("Password")

        button = QPushButton("Sign In")
        button.clicked.connect(self._submit)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Авторизация"))
        layout.addWidget(self.email)
        layout.addWidget(self.password)
        layout.addWidget(button)
        self.setLayout(layout)

        self.state.error.connect(self._show_error)

    def _submit(self) -> None:
        self.state.login(self.email.text().strip(), self.password.text())

    def _show_error(self, text: str) -> None:
        QMessageBox.critical(self, "Ошибка", text)
