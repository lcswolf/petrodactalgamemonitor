from django.db import models
from apps.communities.models import Community
from apps.panels.models import PterodactylPanel


class GameServer(models.Model):
    panel = models.ForeignKey(PterodactylPanel, on_delete=models.PROTECT, related_name="servers")
    community = models.ForeignKey(Community, on_delete=models.SET_NULL, null=True, blank=True, related_name="servers")
    external_id = models.CharField(max_length=80)
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    game = models.CharField(max_length=80, blank=True)
    is_public = models.BooleanField(default=True)
    monitoring_enabled = models.BooleanField(default=True)
    is_present_on_panel = models.BooleanField(default=True)
    last_seen_on_panel = models.DateTimeField(null=True, blank=True)
    poll_interval_seconds = models.PositiveSmallIntegerField(default=300)
    last_status = models.CharField(max_length=16, default="unknown")
    last_status_at = models.DateTimeField(null=True, blank=True)
    last_metrics_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(fields=["panel", "external_id"], name="unique_panel_server_id")]
        indexes = [
            models.Index(fields=["monitoring_enabled", "last_metrics_at"], name="srv_mon_enabled_metrics_idx"),
            models.Index(fields=["panel", "is_present_on_panel"], name="srv_panel_present_idx"),
        ]

    def __str__(self):
        return self.name
