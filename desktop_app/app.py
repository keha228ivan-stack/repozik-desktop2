import sys
from PySide6.QtWidgets import QApplication

from desktop_app.api.client import ApiClient
from desktop_app.core.state import AppState
from desktop_app.ui.login_view import LoginView
from desktop_app.ui.main_window import MainWindow


def run() -> None:
    app = QApplication(sys.argv)
    api = ApiClient()
    state = AppState(api)

    login = LoginView(state)
    window = MainWindow(state)

    def on_auth_changed(is_auth: bool) -> None:
        if is_auth:
            login.hide()
            window.show()
            window.refresh_all_pages()
        else:
            window.hide()
            login.show()

    state.auth_changed.connect(on_auth_changed)
    on_auth_changed(state.is_authenticated)

    sys.exit(app.exec())
