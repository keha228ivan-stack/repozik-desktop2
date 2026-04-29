from PySide6.QtWidgets import QLabel, QListWidget, QPushButton, QVBoxLayout, QWidget

from desktop_app.core.state import AppState


class ProfilePage(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.info = QLabel("Профиль")
        self.status = QLabel("")
        self.history = QListWidget()
        save = QPushButton("Обновить")
        save.clicked.connect(self.refresh)
        layout = QVBoxLayout(self)
        layout.addWidget(self.info)
        layout.addWidget(self.status)
        layout.addWidget(self.history)
        layout.addWidget(save)
        self.state.profile_changed.connect(self._set_profile)
        self.state.profile_error.connect(self.status.setText)

    def refresh(self) -> None:
        self.status.setText("Загрузка профиля...")
        self.state.load_profile()

    def _set_profile(self, p: dict) -> None:
        self.info.setText(
            f"ФИО: {p.get('fullName', '—')}\nEmail: {p.get('email', '—')}\nДолжность: {p.get('position', '—')}\nОтдел: {p.get('department', '—')}\n"
            f"Дата регистрации: {p.get('registeredAt', '—')}\nРоль: {p.get('role', '—')}\nОбщий прогресс: {p.get('overallProgress', 0)}%\n"
            f"Назначено: {p.get('assignedCourses', 0)} | Завершено: {p.get('completedCourses', 0)} | Средний балл: {p.get('averageScore', 0)}%"
        )
        self.history.clear()
        for h in p.get("history", []):
            self.history.addItem(f"{h.get('title')} | {h.get('status')} | {h.get('progress', 0)}% | Тест: {h.get('testResult', '—')} | {h.get('deadline', '—')}")
        self.status.setText("")
