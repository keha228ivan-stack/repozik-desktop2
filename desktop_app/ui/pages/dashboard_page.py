from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

from desktop_app.core.state import AppState


class DashboardPage(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 16, 22, 20)

        container = QFrame()
        container.setObjectName("dashboardContainer")
        content = QVBoxLayout(container)
        content.setContentsMargins(36, 30, 36, 30)
        content.setSpacing(18)

        title = QLabel("Dashboard")
        title.setObjectName("dashTitle")
        subtitle = QLabel("Обзор ключевых метрик обучения")
        subtitle.setObjectName("dashSubtitle")
        content.addWidget(title)
        content.addWidget(subtitle)

        cards = QGridLayout()
        cards.setHorizontalSpacing(16)

        cards.addWidget(self._metric_card("Всего курсов", "0"), 0, 0)
        cards.addWidget(self._metric_card("Активные", "0"), 0, 1)
        cards.addWidget(self._metric_card("Завершено", "0"), 0, 2)
        content.addLayout(cards)

        courses = QFrame()
        courses.setObjectName("coursesCard")
        courses_layout = QVBoxLayout(courses)
        courses_layout.addWidget(QLabel("Мои курсы"))
        content.addWidget(courses)

        toast = QLabel("Вход выполнен")
        toast.setObjectName("toast")
        content.addWidget(toast)
        content.addStretch(1)

        root.addWidget(container)
        self._apply_styles()

    def _metric_card(self, title: str, value: str) -> QWidget:
        card = QFrame()
        card.setObjectName("metricCard")
        layout = QVBoxLayout(card)
        top = QLabel(title)
        top.setObjectName("metricTitle")
        number = QLabel(value)
        number.setObjectName("metricValue")
        layout.addWidget(top)
        layout.addWidget(number)
        layout.addStretch(1)
        return card

    def refresh(self) -> None:
        self.state.refresh_backend_status()

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QFrame#dashboardContainer { background: #e9edf3; border-radius: 0px; }
            QLabel#dashTitle { font-size: 48px; font-weight: 700; color: #1f2937; }
            QLabel#dashSubtitle { font-size: 40px; color: #6b7280; margin-bottom: 6px; }
            QFrame#metricCard { background: #f8fafc; border-radius: 18px; min-height: 200px; }
            QLabel#metricTitle { font-size: 38px; color: #737373; margin: 10px; }
            QLabel#metricValue { font-size: 64px; font-weight: 700; color: #202124; margin: 10px; }
            QFrame#coursesCard { background: #f8fafc; border-radius: 18px; min-height: 95px; }
            QFrame#coursesCard QLabel { font-size: 52px; font-weight: 600; color: #2f343b; margin: 8px; }
            QLabel#toast {
                background: #2f3136;
                color: #ffffff;
                border-radius: 14px;
                font-size: 50px;
                padding: 16px 28px;
                max-width: 330px;
            }
            """
        )
