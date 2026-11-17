from django.db import models
from apps.core.fields import EncryptedTextField
from apps.communities.models import Community
from apps.servers.models import GameServer

class DiscordWebhook(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="webhooks")
    server = models.ForeignKey(GameServer, on_delete=models.CASCADE, null=True, blank=True, related_name="webhooks")
    name = models.CharField(max_length=100, default="Discord alerts")
    webhook_url_encrypted = EncryptedTextField()
    notify_offline = models.BooleanField(default=True)
    notify_recovery = models.BooleanField(default=True)
    cpu_threshold_percent = models.PositiveSmallIntegerField(null=True, blank=True)
    memory_threshold_percent = models.PositiveSmallIntegerField(null=True, blank=True)
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
