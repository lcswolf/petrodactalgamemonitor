from django.contrib import admin
from .models import ServerStatus, PollRun

@admin.register(ServerStatus)
class ServerStatusAdmin(admin.ModelAdmin):
    list_display = ("server", "state", "players_online", "players_max", "ping_ms", "last_checked_at")
    list_filter = ("state",)
    search_fields = ("server__name", "server__identifier")

@admin.register(PollRun)
class PollRunAdmin(admin.ModelAdmin):
    list_display = ("ran_at", "ok", "message")
    list_filter = ("ok",)
    ordering = ("-ran_at",)
