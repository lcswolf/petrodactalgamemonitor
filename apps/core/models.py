"""Core models used across the project."""

from __future__ import annotations
from django.db import models
from .fields import EncryptedTextField

class SiteConfig(models.Model):
    """Singleton-style configuration stored in DB.

    Why a singleton?
    - Most installations only need one set of API keys + URLs.
    - It makes the admin UI simple: one page, one config.

    Secrets (API keys) are stored using EncryptedTextField.
    """

    # Pterodactyl
    ptero_base_url = models.URLField(blank=True, default="", help_text="Example: https://panel.example.com")
    ptero_application_api_key = EncryptedTextField(blank=True, default="", help_text="Application API key (admin).")
    ptero_client_api_key = EncryptedTextField(blank=True, default="", help_text="Client API key.")

    # Notifications
    discord_webhook_url = EncryptedTextField(blank=True, default="", help_text="Optional Discord webhook for alerts.")

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return "Site Configuration"

    @classmethod
    def get_solo(cls) -> "SiteConfig":
        """Fetch the single config row, creating it if missing."""
        obj, _ = cls.objects.get_or_create(id=1)
        return obj
