from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from desktop_app.core.state import AppState
from desktop_app.ui.pages.courses_page import CoursesPage
from desktop_app.ui.pages.notifications_page import NotificationsPage
from desktop_app.ui.pages.profile_page import ProfilePage


class MainWindow(QMainWindow):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.setWindowTitle("Система управления персоналом")
        self.resize(1400, 860)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._build_topbar())

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        body.addWidget(self._build_sidebar())

        self.stack = QStackedWidget()
        self.courses = CoursesPage(state)
        self.notifications = NotificationsPage(state)
        self.profile = ProfilePage(state)

        self.stack.addWidget(self.courses)
        self.stack.addWidget(self.notifications)
        self.stack.addWidget(self.profile)

        body.addWidget(self.stack, 1)
        root_layout.addLayout(body, 1)
        self.setCentralWidget(root)

        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.setCurrentRow(0)
        self._apply_styles()

    def _build_topbar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("topbar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(28, 20, 28, 20)

        left = QVBoxLayout()
        title = QLabel("Система управления персоналом")
        title.setObjectName("appTitle")
        subtitle = QLabel("Учёт персонала, обучения и оценки эффективности")
        subtitle.setObjectName("appSubtitle")
        left.addWidget(title)
        left.addWidget(subtitle)

        layout.addLayout(left)
        layout.addStretch(1)
        return bar

    def _build_sidebar(self) -> QWidget:
        side = QFrame()
        side.setObjectName("sidebar")
        layout = QVBoxLayout(side)
        layout.setContentsMargins(14, 18, 14, 18)

        self.nav = QListWidget()
        for text in ["Библиотека курсов", "Уведомления", "Личный кабинет"]:
            item = QListWidgetItem(text)
            self.nav.addItem(item)

        layout.addWidget(self.nav)
        return side

    def refresh_all_pages(self) -> None:
        self.courses.refresh()
        self.notifications.refresh()
        self.profile.refresh()

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow { background: #f1f5f9; }
            QFrame#topbar { background: #ffffff; border-bottom: 1px solid #e2e8f0; }
            QLabel#appTitle { font-size: 40px; font-weight: 700; color: #0b1730; }
            QLabel#appSubtitle { font-size: 32px; color: #5b708f; }
            QFrame#sidebar { background: #eef2f6; border-right: 1px solid #dbe3ec; min-width: 300px; max-width: 300px; }
            QListWidget { border: none; background: transparent; font-size: 30px; color: #516888; }
            QListWidget::item { padding: 18px; border-radius: 16px; margin: 8px 0; }
            QListWidget::item:selected { background: #dde4ec; color: #0f172a; font-weight: 600; }
            """
        )
