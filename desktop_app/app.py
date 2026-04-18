import sys
import logging


def run() -> None:
    """Start desktop UI when PySide6 is available.

    In restricted environments (CI/sandbox without Qt packages), this function
    falls back to a non-crashing stub mode so the project still starts cleanly.
    """
    try:
        from PySide6.QtWidgets import QApplication
    except Exception:
        print(
            "PySide6 is not installed in this environment. "
            "Install requirements and run again to start the desktop UI."
        )
        return

    from desktop_app.api.client import ApiClient
    from desktop_app.core.state import AppState
    from desktop_app.ui.login_view import LoginView
    from desktop_app.ui.main_window import MainWindow

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

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
