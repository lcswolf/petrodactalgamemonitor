from django.contrib import admin
from .models import DiscordWebhook

@admin.register(DiscordWebhook)
class DiscordWebhookAdmin(admin.ModelAdmin):
    list_display = ("name", "community", "server", "is_enabled", "notify_offline", "notify_recovery")
    list_filter = ("is_enabled", "notify_offline", "notify_recovery")
