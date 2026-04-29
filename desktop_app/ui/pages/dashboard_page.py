from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

from desktop_app.core.state import AppState


class DashboardPage(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.cards: dict[str, QLabel] = {}
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 12, 24, 24)
        container = QFrame()
        body = QVBoxLayout(container)
        body.addWidget(QLabel("Dashboard"))
        self.empty = QLabel("")
        body.addWidget(self.empty)

        metrics = QGridLayout()
        for i, (key, title) in enumerate([
            ("totalCourses", "Всего курсов"),
            ("inProgressCourses", "В процессе"),
            ("completedCourses", "Завершено"),
            ("averageProgress", "Средний прогресс"),
            ("averageScore", "Средний балл"),
            ("overdueCourses", "Просрочено"),
        ]):
            card = QFrame()
            layout = QVBoxLayout(card)
            layout.addWidget(QLabel(title))
            val = QLabel("0")
            layout.addWidget(val)
            self.cards[key] = val
            metrics.addWidget(card, i // 3, i % 3)
        body.addLayout(metrics)
        self.extra = QLabel("")
        body.addWidget(self.extra)
        root.addWidget(container)
        self.state.dashboard_changed.connect(self._set_data)

    def refresh(self) -> None:
        self.state.refresh_backend_status()
        self.state.load_dashboard()

    def _set_data(self, data: dict) -> None:
        total = int(data.get("totalCourses", 0))
        if total == 0:
            self.empty.setText("Вам пока не назначены курсы")
        else:
            self.empty.setText("")
        for k, lbl in self.cards.items():
            v = data.get(k, 0)
            suffix = "%" if k in {"averageProgress", "averageScore"} else ""
            lbl.setText(f"{v}{suffix}")
        self.extra.setText(f"Ближайший дедлайн: {data.get('nearestDeadline', '—')} | Последние активные: {', '.join(data.get('recentCourses', []))}")
