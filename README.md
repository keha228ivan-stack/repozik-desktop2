# Repozik Desktop 2

Desktop-клиент системы управления персоналом на **PySide6**.

## Что реализовано
- Авторизация
- **Регистрация пользователя (только роль "Сотрудник")**
- Dashboard в стиле макета (верхняя панель, левое меню, карточки метрик, действия, топ курсов)
- Профиль, курсы, форум, уведомления
- API-клиент с хранением токена сессии

## Запуск

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-desktop.txt
$env:HR_API_BASE_URL = "http://localhost:3000/api"
python -m desktop_app.main
```

> Если в окружении не установлен PySide6, приложение стартует в безопасном режиме без traceback и выведет подсказку по установке зависимостей.
