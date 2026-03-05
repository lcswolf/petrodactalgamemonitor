"""Notification utilities (Discord webhook, etc.)."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import requests

@dataclass
class DiscordNotifier:
    webhook_url: str

    def send(self, content: str) -> None:
        """Send a basic Discord webhook message."""
        if not self.webhook_url:
            return
        requests.post(self.webhook_url, json={"content": content}, timeout=10).raise_for_status()
