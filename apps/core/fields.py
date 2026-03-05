"""Custom model fields.

`EncryptedTextField` transparently encrypts values before storing them,
and decrypts them when reading from the database.
"""

from django.conf import settings
from django.db import models
from .crypto import Crypto

class EncryptedTextField(models.TextField):
    description = "TextField stored encrypted in DB using Fernet"

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value in (None, ""):
            return ""
        crypto = Crypto.from_key(settings.ENCRYPTION_KEY)
        return crypto.encrypt(value)

    def from_db_value(self, value, expression, connection):
        if value in (None, ""):
            return ""
        crypto = Crypto.from_key(settings.ENCRYPTION_KEY)
        return crypto.decrypt(value)

    def to_python(self, value):
        # When Django assigns raw DB values, it may call to_python().
        # If it looks like ciphertext but we can’t be sure, we attempt decrypt safely.
        if value in (None, ""):
            return ""
        try:
            crypto = Crypto.from_key(settings.ENCRYPTION_KEY)
            return crypto.decrypt(value)
        except Exception:
            # Probably already plaintext (e.g., during form cleaning)
            return value
