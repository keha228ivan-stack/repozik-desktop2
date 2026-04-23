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
        self.resize(1080, 800)

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

        self.nav.currentRowChanged.connect(self._on_nav_changed)
        self.nav.setCurrentRow(0)
        self._apply_styles()

    def _build_topbar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("topbar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(18, 12, 20, 12)

        brand = QLabel("◔ HRLMS")
        brand.setObjectName("brand")
        layout.addWidget(brand)
        layout.addStretch(1)

        self.notifications_btn = QPushButton("🔔")
        self.notifications_btn.setObjectName("topIconButton")
        self.notifications_btn.setToolTip("Уведомления")
        self.notifications_btn.clicked.connect(lambda: self.stack.setCurrentIndex(4))

        self.profile_btn = QPushButton("👤")
        self.profile_btn.setObjectName("topIconButton")
        self.profile_btn.setToolTip("Личный кабинет")
        self.profile_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        layout.addWidget(self.notifications_btn)
        layout.addWidget(self.profile_btn)
        return bar

    def _build_sidebar(self) -> QWidget:
        side = QFrame()
        side.setObjectName("sidebar")
        layout = QVBoxLayout(side)
        layout.setContentsMargins(22, 20, 18, 20)

        title = QLabel("Система управления\nперсоналом")
        title.setObjectName("appTitle")
        subtitle = QLabel("Мой прогресс и активные курсы")
        subtitle.setObjectName("appSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(18)

        self.nav = QListWidget()
        self._nav_to_stack_index = [0, 2, 2, 2, 4, 1]
        for text in [
            "◻  Dashboard",
            "◫  Библиотека курсов",
            "◌  Курсы в процессе",
            "◉  Завершенные курсы",
            "◌  Уведомления",
            "◌  Личный кабинет",
        ]:
            item = QListWidgetItem(text)
            self.nav.addItem(item)

        layout.addWidget(self.nav)
        layout.addStretch(1)
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
            QFrame#topbar { background: #f3f4f6; border: none; }
            QLabel#brand { font-size: 22px; color: #111827; font-weight: 600; }
            QLabel#appTitle { font-size: 58px; font-weight: 700; color: #1f2937; line-height: 1.1; }
            QLabel#appSubtitle { font-size: 40px; color: #6b7280; margin-bottom: 8px; }
            QFrame#sidebar { background: #f3f4f6; border-right: 1px solid #e5e7eb; min-width: 320px; max-width: 320px; }
            QListWidget { border: none; background: transparent; font-size: 35px; color: #64748b; outline: none; }
            QListWidget::item { padding: 13px 10px; border-radius: 10px; margin: 3px 0; }
            QListWidget::item:selected { background: #e8eefc; color: #2563eb; font-weight: 600; }
            QPushButton#topIconButton { background: transparent; border: none; color: #64748b; font-size: 28px; min-width: 48px; }
            """
        )
