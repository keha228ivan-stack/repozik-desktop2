from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from desktop_app.core.state import AppState


class ForumPage(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.topics = QListWidget()
        self.status = QLabel("")
        self.status.setStyleSheet("color: #b45309;")
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Тема")
        self.body_input = QTextEdit()
        self.body_input.setPlaceholderText("Сообщение")
        send = QPushButton("Создать тему")
        send.clicked.connect(self._create)

        row = QHBoxLayout()
        row.addWidget(self.title_input)
        row.addWidget(send)

        layout = QVBoxLayout()
        layout.addWidget(self.status)
        layout.addWidget(self.topics)
        layout.addLayout(row)
        layout.addWidget(self.body_input)
        self.setLayout(layout)

        self.state.forum_changed.connect(self._set_topics)
        self.state.forum_error.connect(self._set_error)

    def refresh(self) -> None:
        self.status.setText("Загрузка тем...")
        self.state.load_topics()

    def _create(self) -> None:
        title = self.title_input.text().strip()
        body = self.body_input.toPlainText().strip()
        if title and body and self.state.create_topic(title, body):
            self.title_input.clear()
            self.body_input.clear()
            self.refresh()

    def _set_topics(self, topics: list) -> None:
        self.topics.clear()
        for t in topics:
            self.topics.addItem(t.get("title", "(без названия)"))
        if not topics:
            self.status.setText("Тем пока нет.")
        else:
            self.status.setText("")

    def _set_error(self, text: str) -> None:
        if text:
            self.status.setText(text)
