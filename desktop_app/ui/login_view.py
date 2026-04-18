from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from desktop_app.core.state import AppState


class LoginView(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.setWindowTitle("Система управления персоналом")
        self.resize(520, 560)

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)

        title = QLabel("Система управления персоналом")
        title.setObjectName("title")
        subtitle = QLabel("Учёт персонала, обучения и оценки эффективности")
        subtitle.setObjectName("subtitle")

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)

        self.mode_label = QLabel("Вход в систему")
        self.mode_label.setObjectName("cardTitle")

        self.switch_btn = QPushButton("Нет аккаунта? Регистрация")
        self.switch_btn.setObjectName("switch")
        self.switch_btn.clicked.connect(self._toggle_mode)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_login_form())
        self.stack.addWidget(self._build_register_form())

        card_layout.addWidget(self.mode_label)
        card_layout.addWidget(self.stack)
        card_layout.addWidget(self.switch_btn, alignment=Qt.AlignmentFlag.AlignRight)

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addSpacing(20)
        root.addWidget(card)

        self.state.error.connect(self._show_error)
        self._apply_styles()

    def _build_login_form(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self.email = QLineEdit()
        self.email.setPlaceholderText("email@company.com")
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("Пароль")
        btn = QPushButton("Войти")
        btn.setObjectName("primary")
        btn.clicked.connect(self._submit_login)
        demo_btn = QPushButton("Войти в демо")
        demo_btn.clicked.connect(self._login_demo)
        demo_hint = QLabel("Если API недоступен: demo@company.local / Demo12345!")
        demo_hint.setObjectName("hint")
        form.addRow("Email", self.email)
        form.addRow("Пароль", self.password)
        form.addRow("", demo_hint)
        form.addRow("", btn)
        form.addRow("", demo_btn)
        return w

    def _build_register_form(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self.reg_name = QLineEdit()
        self.reg_name.setPlaceholderText("Иван Иванов")
        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText("email@company.com")
        self.reg_password = QLineEdit()
        self.reg_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_password.setPlaceholderText("Не менее 8 символов")

        info = QLabel("Регистрация доступна только для сотрудников")
        info.setObjectName("hint")

        btn = QPushButton("Создать аккаунт")
        btn.setObjectName("primary")
        btn.clicked.connect(self._submit_register)

        form.addRow("ФИО", self.reg_name)
        form.addRow("Email", self.reg_email)
        form.addRow("Пароль", self.reg_password)
        form.addRow("", info)
        form.addRow("", btn)
        return w

    def _toggle_mode(self) -> None:
        is_login = self.stack.currentIndex() == 0
        self.stack.setCurrentIndex(1 if is_login else 0)
        self.mode_label.setText("Регистрация" if is_login else "Вход в систему")
        self.switch_btn.setText("Уже есть аккаунт? Войти" if is_login else "Нет аккаунта? Регистрация")

    def _submit_login(self) -> None:
        self.state.login(self.email.text().strip(), self.password.text())

    def _submit_register(self) -> None:
        full_name = self.reg_name.text().strip()
        email = self.reg_email.text().strip()
        password = self.reg_password.text()
        if not full_name or not email or not password:
            self._show_error("Заполните все поля регистрации")
            return
        if len(password) < 8:
            self._show_error("Пароль должен содержать минимум 8 символов")
            return
        if "@" not in email:
            self._show_error("Введите корректный email")
            return
        self.state.register(full_name, email, password)

    def _login_demo(self) -> None:
        self.email.setText("demo@company.local")
        self.password.setText("Demo12345!")
        self._submit_login()

    def _show_error(self, text: str) -> None:
        if self.isVisible():
            QMessageBox.critical(self, "Ошибка", text)

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QWidget { background: #f6f8fb; font-size: 15px; }
            QLabel#title { font-size: 36px; font-weight: 700; color: #0b1730; }
            QLabel#subtitle { font-size: 20px; color: #536888; margin-bottom: 10px; }
            QFrame#card { background: #ffffff; border-radius: 18px; border: 1px solid #e2e8f0; }
            QLabel#cardTitle { font-size: 24px; font-weight: 600; color: #0f172a; margin-bottom: 6px; }
            QLabel#hint { color: #64748b; font-size: 13px; }
            QPushButton#primary { background: #2563eb; color: white; border: none; border-radius: 10px; padding: 10px 14px; font-weight: 600; }
            QPushButton#primary:hover { background: #1d4ed8; }
            QPushButton#switch { color: #2563eb; background: transparent; border: none; }
            QLineEdit { border: 1px solid #cbd5e1; border-radius: 10px; padding: 9px; background: #fff; }
            """
        )
