# NOTE: this project uses PySide6 (not PyQt), so Qt must be imported from PySide6.QtCore.
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QSizePolicy,
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
        root.setObjectName("appRoot")
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
        self.courses = CoursesPage(state, title_text="Библиотека курсов")
        self.courses_in_progress = CoursesPage(state, title_text="Курсы в процессе", locked_status="IN_PROGRESS")
        self.courses_completed = CoursesPage(state, title_text="Завершённые курсы", locked_status="COMPLETED")
        self.courses_overdue = CoursesPage(state, title_text="Просроченные курсы", locked_status="OVERDUE")
        self.forum = ForumPage(state)
        self.notifications = NotificationsPage(state)

        self.stack.addWidget(self.dashboard)      # 0
        self.stack.addWidget(self.profile)        # 1
        self.stack.addWidget(self.courses)        # 2
        self.stack.addWidget(self.courses_in_progress)  # 3
        self.stack.addWidget(self.courses_completed)  # 4
        self.stack.addWidget(self.courses_overdue)  # 5
        self.stack.addWidget(self.forum)          # 6
        self.stack.addWidget(self.notifications)  # 7
        body.addWidget(self.stack, 1)

        root_layout.addLayout(body, 1)
        self.setCentralWidget(root)

        self._nav_to_stack_index = [0, 2, 3, 4, 5, 1]
        self._set_active_nav(0)
        self._apply_styles()

    def _build_topbar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("topbar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 8, 16, 8)

        titles = QVBoxLayout()
        brand = QLabel("Система управления персоналом")
        brand.setObjectName("brand")
        subtitle = QLabel("Мой прогресс и активные курсы")
        subtitle.setObjectName("headerSubtitle")
        titles.addWidget(brand)
        titles.addWidget(subtitle)
        user_name = QLabel((self.state.user or {}).get("fullName", "Сотрудник"))
        user_name.setObjectName("userName")
        logout_btn = QPushButton("Выйти")
        logout_btn.setObjectName("secondaryButton")
        logout_btn.clicked.connect(self.state.logout)
        layout.addLayout(titles)
        layout.addStretch(1)
        layout.addWidget(user_name)
        layout.addWidget(logout_btn)
        return bar

    def _build_sidebar(self) -> QWidget:
        side = QFrame()
        side.setObjectName("sidebar")
        layout = QVBoxLayout(side)
        layout.setContentsMargins(20, 10, 14, 10)
        layout.setSpacing(8)

        layout.addSpacing(4)

        self.nav_buttons: list[QPushButton] = []
        for idx, text in enumerate([
            "📊 Dashboard",
            "📚 Библиотека курсов",
            "⏳ В процессе",
            "✅ Завершённые",
            "🚨 Просроченные",
            "👤 Профиль",
        ]):
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setObjectName("navButton")
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.clicked.connect(lambda _=False, r=idx: self._on_nav_changed(r))
            self.nav_buttons.append(btn)
            layout.addWidget(btn)
        layout.addStretch(1)
        return side

    def _on_nav_changed(self, row: int) -> None:
        if 0 <= row < len(self._nav_to_stack_index):
            self._set_active_nav(row)
            self.stack.setCurrentIndex(self._nav_to_stack_index[row])

    def _set_active_nav(self, active_row: int) -> None:
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == active_row)




    def refresh_all_pages(self) -> None:
        self.dashboard.refresh()
        self.profile.refresh()
        self.courses.refresh()
        self.courses_in_progress.refresh()
        self.courses_completed.refresh()
        self.courses_overdue.refresh()
        self.forum.refresh()
        self.notifications.refresh()

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow { background: #F3F6FA; }
            QFrame#topbar { background: #FFFFFF; border-bottom: 1px solid #E5E7EB; min-height: 56px; max-height: 56px; }
            QLabel#brand { font-size: 20px; font-weight: 800; color: #0f172a; }
            QLabel#headerSubtitle { font-size: 13px; color: #64748b; }
            QLabel#userName { font-size: 14px; color: #6B7280; padding-right: 8px; }
            QFrame#sidebar {
                background: #FFFFFF;
                border-right: 1px solid #e5e7eb;
                min-width: 260px;
                max-width: 260px;
            }
            QLabel#appTitle { font-size: 18px; font-weight: 700; color: #111827; }
            QLabel#appSubtitle { font-size: 14px; color: #70757e; margin-top: 2px; }
            QPushButton#navButton {
                background: transparent;
                border: none;
                text-align: left;
                color: #4B5563;
                font-size: 14px;
                min-height: 38px;
                padding: 8px 12px;
                border-radius: 10px;
            }
            QPushButton#navButton:checked {
                background: #2563EB;
                color: #FFFFFF;
                font-weight: 600;
            }
            QPushButton#navButton:focus { outline: none; }
            """
        )
