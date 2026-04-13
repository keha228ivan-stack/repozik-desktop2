from PySide6.QtWidgets import QListWidget, QPushButton, QVBoxLayout, QWidget

from desktop_app.core.state import AppState


class NotificationsPage(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.list = QListWidget()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        layout = QVBoxLayout()
        layout.addWidget(self.list)
        layout.addWidget(refresh_btn)
        self.setLayout(layout)
        self.state.notifications_changed.connect(self._set_items)

    def refresh(self) -> None:
        self.state.load_notifications()

    def _set_items(self, items: list) -> None:
        self.list.clear()
        for n in items:
            marker = "✓" if n.get("read") else "•"
            self.list.addItem(f"{marker} {n.get('title', '')}")
