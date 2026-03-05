"""Monitoring state and history."""

from django.db import models
from apps.ptero.models import GameServer

class ServerStatus(models.Model):
    """Latest known status for a server.

    This is the *latest snapshot* only. If you later want history charts,
    we can add a separate table for time-series samples.
    """
    server = models.OneToOneField(GameServer, on_delete=models.CASCADE, related_name="status")

    # State derived from Pterodactyl "resources" endpoint:
    # running/starting -> online, stopped/offline -> offline, else unknown
    state = models.CharField(max_length=16, default="unknown")  # online/offline/unknown

    # Optional game-level metrics (future: per-game query plugins).
    players_online = models.IntegerField(null=True, blank=True)
    players_max = models.IntegerField(null=True, blank=True)

    # Optional network metric (future).
    ping_ms = models.IntegerField(null=True, blank=True)

    # Resource metrics from Pterodactyl resources endpoint
    cpu_percent = models.FloatField(null=True, blank=True, help_text="CPU usage percent (resources.cpu_absolute).")
    memory_mb = models.IntegerField(null=True, blank=True, help_text="RAM usage MB (resources.memory_bytes / 1024 / 1024).")

    # When this record was last updated by the poller.
    last_checked_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.server.name}: {self.state}"

class PollRun(models.Model):
    """Record of poll runs (useful for debugging and showing 'last updated')."""
    ran_at = models.DateTimeField(auto_now_add=True)
    ok = models.BooleanField(default=True)
    message = models.TextField(blank=True, default="")

    def __str__(self):
        return f"PollRun {self.ran_at} ok={self.ok}"
