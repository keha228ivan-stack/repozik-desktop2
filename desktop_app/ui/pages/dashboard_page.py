from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QProgressBar, QVBoxLayout, QWidget

from desktop_app.core.state import AppState


class DashboardPage(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.cards: dict[str, QLabel] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(16)

        title = QLabel("Панель обучения")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Актуальная сводка по вашим курсам")
        subtitle.setObjectName("subtitle")
        root.addWidget(title)
        root.addWidget(subtitle)

        self.empty = QLabel("")
        self.empty.setObjectName("hint")
        root.addWidget(self.empty)

        metrics = QGridLayout()
        metrics.setHorizontalSpacing(16)
        metrics.setVerticalSpacing(16)
        for i, (key, text, icon) in enumerate([
            ("totalCourses", "Всего курсов", "📚"),
            ("inProgressCourses", "В процессе", "⏳"),
            ("completedCourses", "Завершено", "✅"),
            ("averageProgress", "Прогресс (в процессе)", "📈"),
        ]):
            card = QFrame()
            card.setObjectName("metricCard")
            l = QVBoxLayout(card)
            l.addWidget(QLabel(icon))
            t = QLabel(text)
            t.setObjectName("metricTitle")
            v = QLabel("0")
            v.setObjectName("metricValue")
            l.addWidget(t)
            l.addWidget(v)
            self.cards[key] = v
            metrics.addWidget(card, 0, i)
        root.addLayout(metrics)

        summary = QFrame()
        summary.setObjectName("surfaceCard")
        summary_layout = QVBoxLayout(summary)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFormat("Прогресс: %p%")
        self.extra = QLabel("—")
        self.extra.setObjectName("hint")
        summary_layout.addWidget(self.progress)
        summary_layout.addWidget(self.extra)
        root.addWidget(summary)

        self.setStyleSheet("""
            QLabel#pageTitle { font-size: 52px; font-weight: 800; color: #0f172a; }
            QLabel#subtitle { font-size: 22px; color: #64748b; margin-bottom: 8px; }
            QLabel#hint { color: #475569; font-size: 15px; }
            QFrame#metricCard, QFrame#surfaceCard { background: white; border: 1px solid #E2E8F0; border-radius: 16px; padding: 16px; }
            QLabel#metricTitle { color: #64748b; font-size: 15px; }
            QLabel#metricValue { color: #0f172a; font-size: 42px; font-weight: 800; }
            QProgressBar { border: 0; background: #E5E7EB; border-radius: 6px; height: 10px; }
            QProgressBar::chunk { background: #2563EB; border-radius: 6px; }
        """)

        self.state.dashboard_changed.connect(self._set_data)

    def refresh(self) -> None:
        self.state.refresh_backend_status()
        self.state.load_dashboard()

    def _set_data(self, data: dict) -> None:
        total = int(data.get("totalCourses", 0))
        self.empty.setText("Вам пока не назначены курсы" if total == 0 else "")
        for k, lbl in self.cards.items():
            v = data.get(k, 0)
            suffix = "%" if k == "averageProgress" else ""
            lbl.setText(f"{v}{suffix}")
        self.progress.setValue(int(data.get("averageProgress", 0)))
        recent = ', '.join(data.get('recentCourses', [])) or '—'
        self.extra.setText(f"Ближайший дедлайн: {data.get('nearestDeadline', '—')}  •  Активные курсы: {recent}")
