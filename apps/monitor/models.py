"""Monitoring state and history."""

from django.db import models
from apps.ptero.models import GameServer

class ServerStatus(models.Model):
    """Latest known status for a server."""
    server = models.OneToOneField(GameServer, on_delete=models.CASCADE, related_name="status")

    state = models.CharField(max_length=16, default="unknown")  # online/offline/unknown
    players_online = models.IntegerField(null=True, blank=True)
    players_max = models.IntegerField(null=True, blank=True)
    ping_ms = models.IntegerField(null=True, blank=True)

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
