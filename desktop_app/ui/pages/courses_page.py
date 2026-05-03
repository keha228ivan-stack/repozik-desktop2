from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, QPushButton, QProgressBar, QScrollArea, QTextBrowser, QVBoxLayout, QWidget

from desktop_app.core.state import AppState


STATUS_COLORS = {"NOT_STARTED": "#6b7280", "IN_PROGRESS": "#2563eb", "COMPLETED": "#16a34a", "OVERDUE": "#dc2626", "LOW_SCORE": "#f59e0b"}
STATUS_LABELS = {"NOT_STARTED": "Не начат", "IN_PROGRESS": "В процессе", "COMPLETED": "Завершён", "OVERDUE": "Просрочен", "LOW_SCORE": "Низкий балл"}


class CoursesPage(QWidget):
    def __init__(self, state: AppState, title_text: str = "Библиотека курсов", locked_status: str | None = None) -> None:
        super().__init__()
        self.state = state
        self.locked_status = locked_status
        self.search = QLineEdit()
        self.search.setPlaceholderText("Поиск курсов")
        self.filter = QComboBox()
        self.filter.addItems(["ALL", "NOT_STARTED", "IN_PROGRESS", "COMPLETED", "OVERDUE"])
        if locked_status:
            self.filter.setCurrentText(locked_status)
            self.filter.setEnabled(False)
        btn = QPushButton("Поиск")
        btn.setObjectName("primaryButton")
        btn.clicked.connect(self.refresh)
        top = QHBoxLayout()
        top.addWidget(self.search)
        top.addWidget(self.filter)
        top.addWidget(btn)
        self.status = QLabel("")
        self.container = QVBoxLayout()
        wrap = QWidget(); wrap.setLayout(self.container)
        sc = QScrollArea(); sc.setWidgetResizable(True); sc.setWidget(wrap); sc.setFrameShape(QFrame.Shape.NoFrame)
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(16)
        header = QLabel(title_text)
        header.setStyleSheet("font-size: 44px; font-weight: 800; color: #0f172a;")
        root.addWidget(header)
        root.addLayout(top); root.addWidget(self.status); root.addWidget(sc)
        self.setStyleSheet("""
            QFrame#surfaceCard { background: white; border: 1px solid #E2E8F0; border-radius: 16px; padding: 14px; }
            QFrame#surfaceCard:hover { border: 1px solid #c7d2fe; }
            QLabel#courseTitle { font-size: 30px; font-weight: 800; color: #0f172a; }
            QLabel#courseMeta { color: #6B7280; }
            QLabel#courseBadge { font-weight: 700; padding: 5px 12px; border-radius: 10px; background: #F3F4F6; }
            QProgressBar { border: 0; background: #E5E7EB; border-radius: 4px; height: 8px; }
            QProgressBar::chunk { background: #2563EB; border-radius: 4px; }
        """)
        self.state.courses_changed.connect(self._set_courses)
        self.state.courses_error.connect(self.status.setText)

    def refresh(self) -> None:
        self.status.setText("Загрузка курсов...")
        self.state.load_courses()

    def _set_courses(self, courses: list) -> None:
        query = self.search.text().strip().lower()
        if query:
            courses = [c for c in courses if query in c.get("title", "").lower()]

        status = self.locked_status or self.filter.currentText()
        if status and status != "ALL":
            courses = [c for c in courses if c.get("status") == status]

        while self.container.count():
            child = self.container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        if not courses:
            self.status.setText("Вам пока не назначены курсы")
            return
        self.status.setText("")
        for c in courses:
            self.container.addWidget(self._card(c))
        self.container.addStretch(1)

    def _card(self, c: dict) -> QWidget:
        frame = QFrame()
        frame.setObjectName("surfaceCard")
        l = QVBoxLayout(frame)
        color = STATUS_COLORS.get(c.get("status"), "#6b7280")
        title = QLabel(c.get('title')); title.setObjectName("courseTitle")
        desc = QLabel(c.get("description", "")); desc.setObjectName("courseMeta")
        status = c.get("status")
        badge_text = "Доступен" if self.locked_status == "NOT_STARTED" else STATUS_LABELS.get(status, status)
        lessons_count = len(c.get("lessons", [])) or int(c.get("lessonsCount", 0))
        if self.locked_status is None:
            meta_text = f"Уроков: {lessons_count}"
        else:
            meta_text = f"Уроков: {lessons_count} • Дедлайн: {c.get('deadline', '—')}"
        meta = QLabel(meta_text)
        meta.setObjectName("courseMeta")

        l.addWidget(title)
        l.addWidget(meta)

        if self.locked_status is None:
            open_btn = QPushButton("Открыть курс")
            open_btn.setObjectName("secondaryButton")
            open_btn.clicked.connect(lambda _=False, course=c: self._open_course_dialog(course))
            l.addWidget(open_btn, alignment=Qt.AlignmentFlag.AlignLeft)
            return frame

        badge = QLabel(badge_text); badge.setObjectName("courseBadge")
        badge_bg = "#F3F4F6"
        if status == "IN_PROGRESS":
            badge_bg = "#DBEAFE"
        elif status == "COMPLETED":
            badge_bg = "#DCFCE7"
        elif status == "OVERDUE":
            badge_bg = "#FEE2E2"
        elif self.locked_status == "NOT_STARTED":
            badge_bg = "#E0E7FF"
            color = "#1D4ED8"
        badge.setStyleSheet(f"color:{color}; background:{badge_bg};")
        progress = QProgressBar(); progress.setRange(0,100); progress.setValue(int(c.get("progress",0))); progress.setTextVisible(False)
        percent = QLabel(f"{int(c.get('progress',0))}%")
        percent.setObjectName("courseMeta")
        l.addWidget(desc); l.addWidget(badge); l.addWidget(percent); l.addWidget(progress)
        action = QPushButton("Начать" if c.get("status") == "NOT_STARTED" else "Продолжить" if c.get("status") in {"IN_PROGRESS", "OVERDUE", "LOW_SCORE"} else "Посмотреть результат")
        action.setObjectName("primaryButton" if c.get("status") != "COMPLETED" else "secondaryButton")
        if c.get("status") == "NOT_STARTED":
            action.clicked.connect(lambda _=False, cid=c.get("id"): self.state.start_course(str(cid)))
        action.clicked.connect(lambda _=False, course=c: self._open_course_dialog(course))
        l.addWidget(action, alignment=Qt.AlignmentFlag.AlignLeft)
        return frame

    def _open_lesson_dialog(self, lesson: dict) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle(lesson.get("title", "Урок"))
        dlg.resize(760, 520)
        layout = QVBoxLayout(dlg)

        title = QLabel(f"<b>{lesson.get('title', 'Урок')}</b>")
        content = QTextBrowser()
        content.setOpenExternalLinks(True)
        content.setHtml(
            f"<h3>{lesson.get('title', 'Урок')}</h3>"
            f"<p>{lesson.get('content', 'Материалы урока пока заполняются.')}</p>"
            "<p><i>Иллюстрация/медиа для урока может быть добавлена сюда.</i></p>"
        )
        layout.addWidget(title)
        layout.addWidget(content)
        dlg.exec()

    def _open_course_dialog(self, course: dict) -> None:
        details = self.state.get_course_details(str(course.get("id"))) or course
        dlg = QDialog(self)
        dlg.setWindowTitle(details.get("title", "Курс"))
        dlg.resize(640, 520)
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel(f"<b>{details.get('title', '')}</b>"))
        layout.addWidget(QLabel(details.get("description", "")))
        layout.addWidget(QLabel(f"Статус: {STATUS_LABELS.get(details.get('status'), details.get('status'))} • Прогресс: {details.get('progress', 0)}% • Дедлайн: {details.get('deadline', '—')}"))
        lessons_list = QListWidget()
        lessons = details.get("lessons", [])
        for ls in lessons:
            lesson_title = ls.get('title')
            if self.locked_status is None:
                lessons_list.addItem(f"{lesson_title}")
            else:
                lessons_list.addItem(f"{lesson_title} — {ls.get('status')}")
        layout.addWidget(QLabel("Уроки"))
        layout.addWidget(lessons_list)
        open_lesson_btn = QPushButton("Открыть урок")
        open_lesson_btn.setObjectName("secondaryButton")
        def _open_selected_lesson() -> None:
            row = lessons_list.currentRow()
            if 0 <= row < len(lessons):
                self._open_lesson_dialog(lessons[row])
        open_lesson_btn.clicked.connect(_open_selected_lesson)
        lessons_list.itemDoubleClicked.connect(lambda _item: _open_selected_lesson())
        layout.addWidget(open_lesson_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        questions = details.get("testQuestions", [])
        if questions:
            layout.addWidget(QLabel("Примеры вопросов теста"))
            questions_list = QListWidget()
            for q in questions:
                questions_list.addItem(str(q.get("q", "Вопрос")))
            layout.addWidget(questions_list)
        if self.locked_status is None:
            start_btn = QPushButton("Начать обучение")
            start_btn.setObjectName("primaryButton")
            start_btn.setEnabled(details.get("status") != "COMPLETED")
            def _start() -> None:
                self.state.start_course(str(details.get("id")))
                dlg.accept()
                self.refresh()
            start_btn.clicked.connect(_start)
            layout.addWidget(start_btn)
        else:
            if details.get("status") != "COMPLETED":
                complete_btn = QPushButton("Отметить выбранный урок завершённым")
                complete_btn.setObjectName("primaryButton")
                def _complete() -> None:
                    row = lessons_list.currentRow()
                    if row >= 0 and row < len(lessons):
                        self.state.complete_lesson(str(details.get("id")), str(lessons[row].get("id")))
                        dlg.accept()
                        self.refresh()
                complete_btn.clicked.connect(_complete)
                layout.addWidget(complete_btn)
            if details.get("readyForTest") or details.get("status") in {"COMPLETED", "LOW_SCORE"}:
                test_btn = QPushButton("Пройти итоговый тест")
                test_btn.setObjectName("secondaryButton")
                def _submit_test() -> None:
                    result = self.state.submit_test(str(details.get("id")), answers=[])
                    layout.addWidget(QLabel(f"Результат: {result.get('percent', 0)}%"))
                    self.refresh()
                test_btn.clicked.connect(_submit_test)
                layout.addWidget(test_btn)
        dlg.exec()
