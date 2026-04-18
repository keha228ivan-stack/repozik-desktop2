from PySide6.QtWidgets import QLabel, QListWidget, QPushButton, QVBoxLayout, QWidget

from desktop_app.core.state import AppState


class NotificationsPage(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.list = QListWidget()
        self.status = QLabel("")
        self.status.setStyleSheet("color: #b45309;")

        refresh_btn = QPushButton("Повторить")
        refresh_btn.clicked.connect(self.refresh)

        layout = QVBoxLayout()
        layout.addWidget(self.status)
        layout.addWidget(self.list)
        layout.addWidget(refresh_btn)
        self.setLayout(layout)

        self.state.notifications_changed.connect(self._set_items)
        self.state.notifications_error.connect(self._set_error)

    def refresh(self) -> None:
        self.status.setText("Загрузка уведомлений...")
        self.state.load_notifications()

    def _set_items(self, items: list) -> None:
        self.list.clear()
        for n in items:
            marker = "✓" if n.get("read") else "•"
            self.list.addItem(f"{marker} {n.get('title', '')}")

        if not items:
            self.status.setText("Уведомлений пока нет.")
        else:
            self.status.setText("")

    def _set_error(self, text: str) -> None:
        if text:
            self.status.setText(text)
