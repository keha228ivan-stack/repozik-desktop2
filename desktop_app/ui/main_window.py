# NOTE: this project uses PySide6 (not PyQt), so Qt must be imported from PySide6.QtCore.
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
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
        self.resize(1920, 1080)

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

        self.stack.addWidget(self.dashboard)      # 0
        self.stack.addWidget(self.profile)        # 1
        self.stack.addWidget(self.courses)        # 2
        self.stack.addWidget(self.forum)          # 3
        self.stack.addWidget(self.notifications)  # 4
        body.addWidget(self.stack, 1)

        root_layout.addLayout(body, 1)
        self.setCentralWidget(root)

        self._nav_to_stack_index = [0, 2, 2, 2, 4, 1]
        self.nav.currentRowChanged.connect(self._on_nav_changed)
        self.nav.setCurrentRow(0)
        self._apply_styles()

    def _build_topbar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("topbar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(4, 0, 26, 0)

        brand = QLabel("◔ HRLMS")
        brand.setObjectName("brand")
        layout.addWidget(brand)
        layout.addStretch(1)

        notifications_btn = QPushButton("🔔")
        notifications_btn.setObjectName("topIconButton")
        notifications_btn.setToolTip("Уведомления")
        notifications_btn.clicked.connect(lambda: self.stack.setCurrentIndex(4))

        profile_btn = QPushButton("👤")
        profile_btn.setObjectName("topIconButton")
        profile_btn.setToolTip("Личный кабинет")
        profile_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        layout.addWidget(notifications_btn)
        layout.addWidget(profile_btn)
        return bar

    def _build_sidebar(self) -> QWidget:
        # Local import for extra runtime safety in bundled/partial environments.
        from PySide6.QtWidgets import QListWidget, QListWidgetItem

        side = QFrame()
        side.setObjectName("sidebar")
        layout = QVBoxLayout(side)
        layout.setContentsMargins(30, 14, 22, 14)

        title = QLabel("Система управления персоналом")
        title.setObjectName("appTitle")
        subtitle = QLabel("Мой прогресс и активные курсы")
        subtitle.setObjectName("appSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(34)

        self.nav = QListWidget()
        self.nav.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.nav.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.nav.setSpacing(2)
        self.nav.setFixedHeight(230)
        for text in [
            "◈  Dashboard",
            "◧  Библиотека курсов",
            "◌  Курсы в процессе",
            "◎  Завершенные курсы",
            "◌  Уведомления",
            "◌  Личный кабинет",
        ]:
            self.nav.addItem(QListWidgetItem(text))
        layout.addWidget(self.nav)
        layout.addStretch(1)
        return side

    def _on_nav_changed(self, row: int) -> None:
        if 0 <= row < len(self._nav_to_stack_index):
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
            QMainWindow { background: #f2f2f3; }
            QFrame#topbar { background: #f2f2f3; border: none; min-height: 42px; max-height: 42px; }
            QLabel#brand { font-size: 30px; font-weight: 500; color: #111827; padding-left: 2px; }
            QPushButton#topIconButton {
                background: transparent;
                border: none;
                color: #64748b;
                font-size: 32px;
                min-width: 54px;
            }
            QFrame#sidebar {
                background: #f2f2f3;
                border-right: 1px solid #e5e7eb;
                min-width: 320px;
                max-width: 320px;
            }
            QLabel#appTitle { font-size: 22px; font-weight: 700; color: #24292f; }
            QLabel#appSubtitle { font-size: 14px; color: #70757e; margin-top: 2px; }
            QListWidget {
                border: none;
                background: transparent;
                color: #5f7392;
                font-size: 14px;
                outline: none;
            }
            QListWidget::item {
                padding: 8px 10px;
                border-radius: 10px;
                margin: 3px 0;
            }
            QListWidget::item:selected {
                background: transparent;
                color: #2b61df;
                font-weight: 500;
            }
            """
        )
