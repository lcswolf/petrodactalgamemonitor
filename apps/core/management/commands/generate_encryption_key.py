"""Generate a Fernet encryption key.

Usage:
    python manage.py generate_encryption_key

Copy the output into `.env` as:
    ENCRYPTION_KEY=<output>
"""

from django.core.management.base import BaseCommand
from cryptography.fernet import Fernet

class Command(BaseCommand):
    help = "Generate an ENCRYPTION_KEY (Fernet) for .env"

    def handle(self, *args, **options):
        key = Fernet.generate_key().decode("utf-8")
        self.stdout.write(key)
