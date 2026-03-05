from django.contrib import admin
from .models import GameServer, Clan

@admin.register(GameServer)
class GameServerAdmin(admin.ModelAdmin):
    list_display = ("name", "ptero_id", "identifier", "node_name", "ip", "port", "is_hidden")
    list_filter = ("is_hidden", "node_name")
    search_fields = ("name", "identifier", "ip")

@admin.register(Clan)
class ClanAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_public")
    list_filter = ("is_public",)
    search_fields = ("name", "slug")
    filter_horizontal = ("servers",)
