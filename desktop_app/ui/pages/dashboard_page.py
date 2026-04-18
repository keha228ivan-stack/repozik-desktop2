from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from desktop_app.core.state import AppState


class DashboardPage(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 26, 32, 26)
        root.setSpacing(18)

        title = QLabel("Dashboard")
        title.setObjectName("dashTitle")
        subtitle = QLabel("Обзор ключевых метрик системы")
        subtitle.setObjectName("dashSubtitle")
        self.backend_status = QLabel("Проверка backend...")
        self.backend_status.setObjectName("backendStatus")
        root.addWidget(title)
        root.addWidget(subtitle)
        root.addWidget(self.backend_status)

        metrics = QGridLayout()
        metrics.setHorizontalSpacing(16)
        metrics.setVerticalSpacing(16)

        cards = [
            ("👥", "Всего сотрудников", "6", "+12%"),
            ("🟢", "Активных", "5", "+5%"),
            ("📈", "Средняя оценка", "89%", "+3%"),
            ("📘", "Пройдено курсов", "33", "+18%"),
        ]
        for idx, card in enumerate(cards):
            metrics.addWidget(self._metric_card(*card), 0, idx)

        root.addLayout(metrics)

        lower = QHBoxLayout()
        lower.setSpacing(16)
        lower.addWidget(self._activity_panel(), 1)
        lower.addWidget(self._top_courses_panel(), 1)
        root.addLayout(lower, 1)

        self.state.backend_status_changed.connect(self._set_backend_status)
        self._apply_styles()

    def _metric_card(self, icon: str, label: str, value: str, delta: str) -> QWidget:
        frame = QFrame()
        frame.setObjectName("metricCard")
        layout = QVBoxLayout(frame)

        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setObjectName("icon")
        delta_lbl = QLabel(delta)
        delta_lbl.setObjectName("delta")
        top.addWidget(icon_lbl)
        top.addStretch(1)
        top.addWidget(delta_lbl)

        text = QLabel(label)
        text.setObjectName("metricLabel")
        val = QLabel(value)
        val.setObjectName("metricValue")

        layout.addLayout(top)
        layout.addWidget(text)
        layout.addWidget(val)
        layout.addStretch(1)
        return frame

    def _activity_panel(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.addWidget(QLabel("Последние действия"))
        layout.addWidget(QLabel("Иванов Иван завершил курс — 5 минут назад"))
        layout.addWidget(QLabel("Петрова Мария начала курс — 23 минуты назад"))
        layout.addWidget(QLabel("Сидоров Алексей прошёл тест — 52 минуты назад"))
        layout.addStretch(1)
        return frame

    def _top_courses_panel(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.addWidget(QLabel("Топ курсов по популярности"))

        for title, progress, people in [
            ("React для начинающих", 85, "24 чел."),
            ("Управление проектами", 70, "18 чел."),
            ("UI/UX дизайн", 90, "15 чел."),
        ]:
            row = QHBoxLayout()
            row.addWidget(QLabel(title))
            row.addStretch(1)
            row.addWidget(QLabel(people))
            layout.addLayout(row)
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(progress)
            bar.setTextVisible(False)
            layout.addWidget(bar)

        layout.addStretch(1)
        return frame

    def refresh(self) -> None:
        self.state.refresh_backend_status()

    def _set_backend_status(self, available: bool, message: str) -> None:
        color = "#15803d" if available else "#b45309"
        self.backend_status.setStyleSheet(f"color: {color}; font-size: 20px;")
        self.backend_status.setText(message)

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QLabel#dashTitle { font-size: 44px; font-weight: 700; color: #0f172a; }
            QLabel#dashSubtitle { font-size: 30px; color: #5a718f; margin-bottom: 8px; }
            QFrame#metricCard { background: #fff; border: 1px solid #d9e2ec; border-radius: 18px; min-height: 210px; }
            QLabel#icon { font-size: 28px; }
            QLabel#delta { font-size: 28px; color: #10b981; }
            QLabel#metricLabel { font-size: 31px; color: #5b708f; }
            QLabel#metricValue { font-size: 48px; font-weight: 700; color: #0f172a; }
            QFrame#panel { background: #fff; border: 1px solid #d9e2ec; border-radius: 18px; padding: 8px; }
            QFrame#panel QLabel { font-size: 30px; color: #0f172a; margin: 6px 0; }
            QProgressBar { border: 0; background: #e2e8f0; border-radius: 4px; height: 10px; }
            QProgressBar::chunk { background: #f59e0b; border-radius: 4px; }
            """
        )
