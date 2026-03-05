"""Encryption helpers for storing secrets in the database.

We use Fernet (symmetric encryption) from the `cryptography` package.

Why:
- You may need to store API keys in DB so they can be edited in Admin.
- Storing plaintext is risky if your DB backups leak.
- Fernet keeps it simple: key in `.env`, encrypted value in DB.

Important:
- Losing `ENCRYPTION_KEY` will make existing encrypted values unreadable.
"""

from __future__ import annotations
from dataclasses import dataclass
from cryptography.fernet import Fernet, InvalidToken

@dataclass(frozen=True)
class Crypto:
    fernet: Fernet

    @staticmethod
    def from_key(key: str) -> "Crypto":
        if not key:
            raise ValueError("ENCRYPTION_KEY is not set.")
        return Crypto(Fernet(key.encode("utf-8")))

    def encrypt(self, value: str) -> str:
        if value is None:
            return ""
        token = self.fernet.encrypt(value.encode("utf-8"))
        return token.decode("utf-8")

    def decrypt(self, token: str) -> str:
        if not token:
            return ""
        try:
            value = self.fernet.decrypt(token.encode("utf-8"))
            return value.decode("utf-8")
        except InvalidToken:
            # This typically means you changed ENCRYPTION_KEY.
            raise ValueError("Unable to decrypt value (wrong ENCRYPTION_KEY?).")
