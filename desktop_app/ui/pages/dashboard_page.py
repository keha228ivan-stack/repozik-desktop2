from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

from desktop_app.core.state import AppState


class DashboardPage(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 12, 24, 24)

        container = QFrame()
        container.setObjectName("dashboardContainer")
        body = QVBoxLayout(container)
        body.setContentsMargins(36, 28, 32, 24)
        body.setSpacing(16)

        title = QLabel("Dashboard")
        title.setObjectName("dashTitle")
        subtitle = QLabel("Обзор ключевых метрик обучения")
        subtitle.setObjectName("dashSubtitle")
        body.addWidget(title)
        body.addWidget(subtitle)

        metrics = QGridLayout()
        metrics.setHorizontalSpacing(16)
        metrics.addWidget(self._metric_card("Всего курсов", "0"), 0, 0)
        metrics.addWidget(self._metric_card("Активные", "0"), 0, 1)
        metrics.addWidget(self._metric_card("Завершено", "0"), 0, 2)
        body.addLayout(metrics)

        courses = QFrame()
        courses.setObjectName("coursesCard")
        courses_layout = QVBoxLayout(courses)
        courses_layout.addWidget(QLabel("Мои курсы"))
        body.addWidget(courses)
        body.addStretch(1)

        root.addWidget(container)
        self._apply_styles()

    def _metric_card(self, title: str, value: str) -> QWidget:
        card = QFrame()
        card.setObjectName("metricCard")
        layout = QVBoxLayout(card)
        label = QLabel(title)
        label.setObjectName("metricLabel")
        number = QLabel(value)
        number.setObjectName("metricValue")
        layout.addWidget(label)
        layout.addWidget(number)
        layout.addStretch(1)
        return card

    def refresh(self) -> None:
        self.state.refresh_backend_status()

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QFrame#dashboardContainer { background: #e8ebf1; border-radius: 0; }
            QLabel#dashTitle { font-size: 62px; font-weight: 700; color: #252a30; }
            QLabel#dashSubtitle { font-size: 50px; color: #757b85; margin-bottom: 8px; }
            QFrame#metricCard { background: #f7f7f8; border-radius: 18px; min-height: 230px; }
            QLabel#metricLabel { font-size: 45px; color: #7b8087; padding: 8px 10px 0 10px; }
            QLabel#metricValue { font-size: 84px; font-weight: 700; color: #21252b; padding: 0 10px 10px 10px; }
            QFrame#coursesCard { background: #f7f7f8; border-radius: 18px; min-height: 95px; }
            QFrame#coursesCard QLabel { font-size: 55px; font-weight: 700; color: #2f343b; padding: 8px 10px; }
            """
        )
