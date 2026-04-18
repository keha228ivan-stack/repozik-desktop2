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

## Диагностика API (PowerShell)

Если на регистрации/логине появляется `Network error`, проверьте, что backend действительно запущен и доступен:

```powershell
$env:HR_API_BASE_URL = "http://localhost:3000/api"
Invoke-RestMethod -Method GET -Uri "$env:HR_API_BASE_URL/health"
```

Если у backend нет `/health`, можно проверить endpoint регистрации:

```powershell
$body = @{
  fullName = "Test User"
  email    = "test$(Get-Random)@example.com"
  password = "Password123!"
  role     = "employee"
} | ConvertTo-Json

Invoke-RestMethod -Method POST -Uri "$env:HR_API_BASE_URL/auth/register" -ContentType "application/json" -Body $body
```

Приложение автоматически отключает системные proxy-переменные для `localhost/127.0.0.1`, чтобы запросы к локальному API не уходили в сторонний прокси.

## Вход без backend (демо-режим)

Если backend на `http://localhost:3000` недоступен (например, `WinError 10061`), для проверки интерфейса можно войти демо-пользователем:

- Email: `demo@company.local`
- Пароль: `Demo12345!`

Демо-вход срабатывает только при сетевой ошибке API и только для этой пары логин/пароль.
