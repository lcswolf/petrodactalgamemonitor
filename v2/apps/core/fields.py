import os
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models


def _fernet():
    key = getattr(settings, "ENCRYPTION_KEY", "") or os.environ.get("ENCRYPTION_KEY", "")
    if not key:
        raise ImproperlyConfigured("ENCRYPTION_KEY must be set before storing or reading encrypted secrets.")
    try:
        return Fernet(key.encode("ascii"))
    except (ValueError, UnicodeEncodeError) as exc:
        raise ImproperlyConfigured("ENCRYPTION_KEY must be a valid Fernet key.") from exc


class EncryptedTextField(models.TextField):
    """Encrypt text values at rest using a dedicated Fernet key."""
    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value in (None, ""):
            return value
        return _fernet().encrypt(value.encode("utf-8")).decode("ascii")

    def from_db_value(self, value, expression, connection):
        if value in (None, ""):
            return value
        try:
            return _fernet().decrypt(value.encode("ascii")).decode("utf-8")
        except InvalidToken as exc:
            raise ImproperlyConfigured("Could not decrypt a stored secret. Check ENCRYPTION_KEY.") from exc
