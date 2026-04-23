from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from desktop_app.core.state import AppState


class DashboardPage(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 12, 20, 20)

        container = QFrame()
        container.setObjectName("dashboardContainer")
        body = QVBoxLayout(container)
        body.setContentsMargins(28, 26, 28, 24)
        body.setSpacing(16)

        title = QLabel("Dashboard")
        title.setObjectName("dashTitle")
        subtitle = QLabel("Обзор ключевых метрик обучения")
        subtitle.setObjectName("dashSubtitle")
        body.addWidget(title)
        body.addWidget(subtitle)

        metrics = QGridLayout()
        metrics.setHorizontalSpacing(14)
        metrics.addWidget(self._metric_card("Всего курсов", "0"), 0, 0)
        metrics.addWidget(self._metric_card("Активные", "0"), 0, 1)
        metrics.addWidget(self._metric_card("Завершено", "0"), 0, 2)
        body.addLayout(metrics)

        courses = QFrame()
        courses.setObjectName("coursesCard")
        courses_layout = QVBoxLayout(courses)
        courses_layout.addWidget(QLabel("Мои курсы"))
        body.addWidget(courses)

        self.login_done_btn = QPushButton("Вход выполнен")
        self.login_done_btn.setObjectName("loginDoneButton")
        self.login_done_btn.setEnabled(False)
        body.addWidget(self.login_done_btn)
        body.addStretch(1)

        root.addWidget(container)
        self._apply_styles()

    def _metric_card(self, label: str, value: str) -> QWidget:
        card = QFrame()
        card.setObjectName("metricCard")
        layout = QVBoxLayout(card)
        text = QLabel(label)
        text.setObjectName("metricLabel")
        number = QLabel(value)
        number.setObjectName("metricValue")
        layout.addWidget(text)
        layout.addWidget(number)
        layout.addStretch(1)
        return card

    def refresh(self) -> None:
        self.state.refresh_backend_status()

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QFrame#dashboardContainer { background: #e9edf3; border-radius: 0; }
            QLabel#dashTitle { font-size: 30px; font-weight: 700; color: #1f2937; }
            QLabel#dashSubtitle { font-size: 18px; color: #6b7280; margin-bottom: 8px; }
            QFrame#metricCard { background: #f8fafc; border-radius: 16px; min-height: 140px; }
            QLabel#metricLabel { font-size: 20px; color: #737373; padding: 8px 10px 0 10px; }
            QLabel#metricValue { font-size: 52px; font-weight: 700; color: #202124; padding: 0 10px 10px 10px; }
            QFrame#coursesCard { background: #f8fafc; border-radius: 16px; min-height: 78px; }
            QFrame#coursesCard QLabel { font-size: 22px; font-weight: 700; color: #2f343b; padding: 8px 10px; }
            QPushButton#loginDoneButton {
                max-width: 230px;
                background: #2f3136;
                color: #ffffff;
                border-radius: 14px;
                border: none;
                font-size: 20px;
                padding: 12px 16px;
            }
            QPushButton#loginDoneButton:disabled { color: #ffffff; }
            """
        )
