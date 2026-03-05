from django.contrib import admin
from django.utils.html import format_html
import os

from .models import GameServer, Clan


@admin.register(GameServer)
class GameServerAdmin(admin.ModelAdmin):
    """Admin for servers.

    Security requirement:
    - Do NOT display IP/port/identifier anywhere in the admin UI.
      (These values are still stored in the DB for internal polling.)
    """
    list_display = ("name", "ptero_id", "node_name", "is_hidden")
    list_filter = ("is_hidden", "node_name")
    search_fields = ("name", "node_name")

    # Hide sensitive/internal fields from the admin form:
    exclude = ("identifier", "ip", "port")


@admin.register(Clan)
class ClanAdmin(admin.ModelAdmin):
    """Admin for clans.

    Adds a clickable public link so it's easy to share clan pages.
    Set PUBLIC_BASE_URL in your .env (recommended):
        PUBLIC_BASE_URL=https://monitor.cymru-hosting.co.uk
    """
    list_display = ("name", "slug", "is_public", "public_link")
    list_filter = ("is_public",)
    search_fields = ("name", "slug")
    filter_horizontal = ("servers",)
    readonly_fields = ("public_link",)

    def public_link(self, obj: Clan):
        base = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/")
        path = f"/clan/{obj.slug}/"
        url = f"{base}{path}" if base else path
        return format_html('<a href="{}" target="_blank" rel="noopener">Open clan page</a> <span class="quiet">({})</span>', url, url)

    public_link.short_description = "Public link"
