from django.contrib import admin
from .models import GameServer

@admin.register(GameServer)
class GameServerAdmin(admin.ModelAdmin):
    list_display = ("name", "panel", "community", "last_status", "monitoring_enabled", "is_public")
    list_filter = ("last_status", "monitoring_enabled", "is_public", "panel")
    search_fields = ("name", "external_id", "slug")
