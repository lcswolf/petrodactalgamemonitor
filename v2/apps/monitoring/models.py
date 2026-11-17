from django.db import models
from apps.servers.models import GameServer


class MetricSample(models.Model):
    server = models.ForeignKey(GameServer, on_delete=models.CASCADE, related_name="metric_samples")
    sampled_at = models.DateTimeField(db_index=True)
    cpu_percent = models.FloatField(null=True, blank=True)
    memory_bytes = models.PositiveBigIntegerField(null=True, blank=True)
    disk_bytes = models.PositiveBigIntegerField(null=True, blank=True)
    players_online = models.PositiveIntegerField(null=True, blank=True)
    players_max = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-sampled_at"]
        indexes = [models.Index(fields=["server", "-sampled_at"], name="mon_metric_server_time_idx")]


class StatusEvent(models.Model):
    class Kind(models.TextChoices):
        OFFLINE = "offline", "Offline"
        ONLINE = "online", "Online"
        UNKNOWN = "unknown", "Unknown"

    server = models.ForeignKey(GameServer, on_delete=models.CASCADE, related_name="status_events")
    kind = models.CharField(max_length=12, choices=Kind.choices)
    occurred_at = models.DateTimeField(db_index=True)
    detail = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ["-occurred_at"]
        indexes = [models.Index(fields=["server", "-occurred_at"], name="mon_status_server_time_idx")]
