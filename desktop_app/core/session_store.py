from pathlib import Path
from typing import Optional

import keyring


class SessionStore:
    SERVICE = "repozik-desktop"
    KEY = "auth-token"
    FALLBACK_FILE = Path.home() / ".repozik_token"

    def get_token(self) -> Optional[str]:
        try:
            token = keyring.get_password(self.SERVICE, self.KEY)
            if token:
                return token
        except Exception:
            pass
        if self.FALLBACK_FILE.exists():
            return self.FALLBACK_FILE.read_text(encoding="utf-8").strip() or None
        return None

    def set_token(self, token: Optional[str]) -> None:
        try:
            if token:
                keyring.set_password(self.SERVICE, self.KEY, token)
            else:
                keyring.delete_password(self.SERVICE, self.KEY)
        except Exception:
            pass

        if token:
            self.FALLBACK_FILE.write_text(token, encoding="utf-8")
        elif self.FALLBACK_FILE.exists():
            self.FALLBACK_FILE.unlink()
