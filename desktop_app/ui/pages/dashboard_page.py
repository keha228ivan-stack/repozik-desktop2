from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from desktop_app.core.state import AppState


class DashboardPage(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.label = QLabel("Welcome")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def refresh(self) -> None:
        name = (self.state.user or {}).get("fullName") or (self.state.user or {}).get("email") or "user"
        self.label.setText(f"Добро пожаловать, {name}!")
