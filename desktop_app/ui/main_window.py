from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from desktop_app.core.state import AppState
from desktop_app.ui.pages.courses_page import CoursesPage
from desktop_app.ui.pages.dashboard_page import DashboardPage
from desktop_app.ui.pages.forum_page import ForumPage
from desktop_app.ui.pages.notifications_page import NotificationsPage
from desktop_app.ui.pages.profile_page import ProfilePage


class MainWindow(QMainWindow):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.setWindowTitle("Система управления персоналом")
        self.resize(1024, 800)

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
        self.dashboard = DashboardPage(state)
        self.profile = ProfilePage(state)
        self.courses = CoursesPage(state)
        self.forum = ForumPage(state)
        self.notifications = NotificationsPage(state)

        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.profile)
        self.stack.addWidget(self.courses)
        self.stack.addWidget(self.forum)
        self.stack.addWidget(self.notifications)

        body.addWidget(self.stack, 1)
        root_layout.addLayout(body, 1)
        self.setCentralWidget(root)

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

        notifications_btn = QPushButton("🔔")
        notifications_btn.setObjectName("topIconButton")
        notifications_btn.setToolTip("Уведомления")
        notifications_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.notifications))

        profile_btn = QPushButton("👤")
        profile_btn.setObjectName("topIconButton")
        profile_btn.setToolTip("Личный кабинет")
        profile_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.profile))

        layout.addWidget(notifications_btn)
        layout.addWidget(profile_btn)
        return bar

    def _build_sidebar(self) -> QWidget:
        side = QFrame()
        side.setObjectName("sidebar")
        layout = QVBoxLayout(side)
        layout.setContentsMargins(14, 18, 14, 18)

        self.nav = QListWidget()
        self._nav_to_stack_index = [0, 2, 2, 2, 4, 1]
        for text in [
            "◻ Dashboard",
            "◻ Библиотека курсов",
            "◌ Курсы в процессе",
            "◉ Завершенные курсы",
            "◌ Уведомления",
            "◌ Личный кабинет",
        ]:
            self.nav.addItem(QListWidgetItem(text))

        self.nav.currentRowChanged.connect(self._on_nav_changed)
        layout.addWidget(self.nav)
        return side

    def _on_nav_changed(self, row: int) -> None:
        if row < 0 or row >= len(self._nav_to_stack_index):
            return
        self.stack.setCurrentIndex(self._nav_to_stack_index[row])

    def refresh_all_pages(self) -> None:
        self.dashboard.refresh()
        self.profile.refresh()
        self.courses.refresh()
        self.forum.refresh()
        self.notifications.refresh()

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow { background: #f3f4f6; }
            QFrame#topbar { background: #f3f4f6; border-bottom: none; }
            QLabel#appTitle { font-size: 56px; font-weight: 700; color: #1f2937; }
            QLabel#appSubtitle { font-size: 40px; color: #6b7280; }
            QFrame#sidebar { background: #f3f4f6; border-right: none; min-width: 290px; max-width: 290px; }
            QListWidget { border: none; background: transparent; font-size: 35px; color: #64748b; outline: none; }
            QListWidget::item { padding: 14px 16px; border-radius: 12px; margin: 4px 0; }
            QListWidget::item:selected { background: transparent; color: #2563eb; font-weight: 600; }
            QPushButton#topIconButton { background: transparent; border: none; color: #64748b; font-size: 30px; min-width: 64px; }
            """
        )
