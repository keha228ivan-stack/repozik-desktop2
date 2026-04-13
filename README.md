# Repozik Desktop 2

Этот репозиторий доработан на основе структуры и функциональности репозитория-источника:
`https://github.com/keha228ivan-stack/repozik-desktop`.

Перенесены ключевые части desktop-приложения на PySide6:
- API-клиент (`desktop_app/api/client.py`)
- модели и state-management (`desktop_app/core/*`)
- экран логина и главное окно (`desktop_app/ui/login_view.py`, `desktop_app/ui/main_window.py`)
- страницы: Dashboard, Profile, Courses, Forum, Notifications (`desktop_app/ui/pages/*`)
- entrypoint (`desktop_app/main.py`, `desktop_app/app.py`)

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-desktop.txt
export HR_API_BASE_URL=http://localhost:3000/api
python -m desktop_app.main
```
