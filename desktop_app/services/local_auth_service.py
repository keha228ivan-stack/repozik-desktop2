from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from desktop_app.api.errors import ApiError
from desktop_app.core.session_store import SessionStore
from desktop_app.services.local_storage import LocalStorage


class LocalAuthService:
    def __init__(self, storage: LocalStorage | None = None) -> None:
        self.storage = storage or LocalStorage()
        self.session = SessionStore()

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register(self, full_name: str, email: str, password: str, department: str, position: str | None = None) -> dict[str, Any]:
        full_name = full_name.strip()
        email = email.strip().lower()
        if not full_name or not email or not password:
            raise ApiError("Заполните обязательные поля", status_code=400)
        if self.storage.find_user_by_email(email):
            raise ApiError("Пользователь с таким email уже существует", status_code=409)

        allowed_departments = {"Отдел продаж", "Бухгалтерия", "IT-отдел", "Производство"}
        if department not in allowed_departments:
            raise ApiError("Выберите отдел из списка", status_code=400)

        now = datetime.now(timezone.utc).isoformat()
        user_id = str(uuid4())
        user = {
            "id": user_id,
            "fullName": full_name,
            "email": email,
            "passwordHash": self._hash_password(password),
            "role": "EMPLOYEE",
            "createdAt": now,
        }
        employee = {
            "id": str(uuid4()),
            "userId": user_id,
            "fullName": full_name,
            "email": email,
            "position": position or "Сотрудник",
            "department": department,
            "status": "В адаптации",
            "createdAt": now,
        }
        self.storage.create_user_and_employee(user, employee)
        token = f"local:{user_id}"
        self.session.set_token(token)
        return {"token": token, "user": {"id": user_id, "email": email, "fullName": full_name, "role": "EMPLOYEE", "employeeId": employee["id"]}}

    def login(self, email: str, password: str) -> dict[str, Any]:
        user = self.storage.find_user_by_email(email)
        if not user:
            raise ApiError("Неверный email или пароль", status_code=401)
        if user.get("passwordHash") != self._hash_password(password):
            raise ApiError("Неверный email или пароль", status_code=401)
        token = f"local:{user.get('id')}"
        self.session.set_token(token)
        return {"token": token, "user": {"id": user.get("id"), "email": user.get("email"), "fullName": user.get("fullName"), "role": user.get("role", "EMPLOYEE")}}

    def get_current_user(self) -> dict[str, Any] | None:
        token = self.session.get_token()
        if not token or not token.startswith("local:"):
            return None
        user_id = token.split(":", 1)[1]
        users = self.storage.load().get("users", [])
        for user in users:
            if user.get("id") == user_id:
                return {"id": user.get("id"), "email": user.get("email"), "fullName": user.get("fullName"), "role": user.get("role", "EMPLOYEE")}
        return None

    def logout(self) -> None:
        self.session.set_token(None)
