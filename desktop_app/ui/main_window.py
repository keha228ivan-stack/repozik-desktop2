from PySide6.QtWidgets import QMainWindow, QTabWidget

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
        self.setWindowTitle("Repozik Desktop")
        self.resize(1000, 720)

        tabs = QTabWidget()
        self.dashboard = DashboardPage(state)
        self.profile = ProfilePage(state)
        self.courses = CoursesPage(state)
        self.forum = ForumPage(state)
        self.notifications = NotificationsPage(state)

        tabs.addTab(self.dashboard, "Dashboard")
        tabs.addTab(self.profile, "Profile")
        tabs.addTab(self.courses, "Courses Catalog")
        tabs.addTab(self.forum, "Forum")
        tabs.addTab(self.notifications, "Notifications")

        self.setCentralWidget(tabs)

    def refresh_all_pages(self) -> None:
        self.dashboard.refresh()
        self.profile.refresh()
        self.courses.refresh()
        self.forum.refresh()
        self.notifications.refresh()
