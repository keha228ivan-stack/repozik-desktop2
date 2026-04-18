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
from desktop_app.ui.pages.course_status_page import CourseStatusPage
from desktop_app.ui.pages.courses_page import CoursesPage
from desktop_app.ui.pages.notifications_page import NotificationsPage
from desktop_app.ui.pages.profile_page import ProfilePage
from desktop_app.ui.theme import main_window_stylesheet


class MainWindow(QMainWindow):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.setWindowTitle("Система управления персоналом")
        self.resize(1180, 760)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._build_topbar())

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        body.addWidget(self._build_sidebar())

        content_wrap = QFrame()
        content_wrap.setObjectName("contentCard")
        content_layout = QVBoxLayout(content_wrap)
        content_layout.setContentsMargins(18, 18, 18, 18)

        self.stack = QStackedWidget()
        self.courses = CoursesPage(state)
        self.courses_in_progress = CourseStatusPage(state, mode="in_progress")
        self.courses_completed = CourseStatusPage(state, mode="completed")
        self.notifications = NotificationsPage(state)
        self.profile = ProfilePage(state)

        self.stack.addWidget(self.courses)
        self.stack.addWidget(self.courses_in_progress)
        self.stack.addWidget(self.courses_completed)
        self.stack.addWidget(self.notifications)
        self.stack.addWidget(self.profile)

        content_layout.addWidget(self.stack)
        body.addWidget(content_wrap, 1)

        root_layout.addLayout(body, 1)
        self.setCentralWidget(root)

        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.setCurrentRow(0)
        self._apply_styles()

    def _build_topbar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("topbar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(12)

        left = QVBoxLayout()
        left.setSpacing(2)

        title = QLabel("Система управления персоналом")
        title.setObjectName("appTitle")
        subtitle = QLabel("Учёт персонала и обучения")
        subtitle.setObjectName("appSubtitle")

        left.addWidget(title)
        left.addWidget(subtitle)

        layout.addLayout(left)
        layout.addStretch(1)

        logout_btn = QPushButton("Выйти")
        logout_btn.setObjectName("logoutBtn")
        logout_btn.clicked.connect(self.state.logout)
        layout.addWidget(logout_btn)

        return bar

    def _build_sidebar(self) -> QWidget:
        side = QFrame()
        side.setObjectName("sidebar")
        layout = QVBoxLayout(side)
        layout.setContentsMargins(12, 14, 12, 14)

        self.nav = QListWidget()
        self.nav.setObjectName("navList")
        for text in [
            "Библиотека курсов",
            "Курсы в процессе",
            "Завершенные курсы",
            "Уведомления",
            "Личный кабинет",
        ]:
            self.nav.addItem(QListWidgetItem(text))

        layout.addWidget(self.nav)
        return side

    def refresh_all_pages(self) -> None:
        self.courses.refresh()
        self.courses_in_progress.refresh()
        self.courses_completed.refresh()
        self.notifications.refresh()
        self.profile.refresh()

    def _apply_styles(self) -> None:
        self.setStyleSheet(main_window_stylesheet())
