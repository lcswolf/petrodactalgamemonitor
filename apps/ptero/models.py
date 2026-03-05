"""Models related to game servers (synced from Pterodactyl)."""

from django.db import models

class GameServer(models.Model):
    """Represents a server on Pterodactyl (inventory data)."""
    # Pterodactyl has a numeric `id` (application API) and an `identifier` (used by client API).
    ptero_id = models.PositiveIntegerField(unique=True)
    identifier = models.CharField(max_length=32, unique=True)

    name = models.CharField(max_length=255)
    node_name = models.CharField(max_length=255, blank=True, default="")
    ip = models.CharField(max_length=64, blank=True, default="")
    port = models.PositiveIntegerField(null=True, blank=True)

    is_hidden = models.BooleanField(default=False, help_text="If true, hide from public pages and API.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

class Clan(models.Model):
    """A clan has its own status page that only shows assigned servers."""
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True, default="")
    is_public = models.BooleanField(default=True)

    servers = models.ManyToManyField(GameServer, blank=True, related_name="clans")

    def __str__(self) -> str:
        return self.name
