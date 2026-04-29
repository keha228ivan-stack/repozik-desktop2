from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LocalStorage:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path.cwd() / "data" / "local_users.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _default_data(self) -> dict[str, list[dict[str, Any]]]:
        return {"users": [], "employees": []}

    def load(self) -> dict[str, list[dict[str, Any]]]:
        if not self.path.exists():
            data = self._default_data()
            self.save(data)
            return data
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                return self._default_data()
            payload.setdefault("users", [])
            payload.setdefault("employees", [])
            return payload
        except (json.JSONDecodeError, OSError):
            return self._default_data()

    def save(self, data: dict[str, list[dict[str, Any]]]) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def find_user_by_email(self, email: str) -> dict[str, Any] | None:
        data = self.load()
        email_normalized = email.strip().lower()
        for user in data["users"]:
            if str(user.get("email", "")).lower() == email_normalized:
                return user
        return None

    def create_user_and_employee(self, user: dict[str, Any], employee: dict[str, Any]) -> None:
        data = self.load()
        data["users"].append(user)
        data["employees"].append(employee)
        self.save(data)
