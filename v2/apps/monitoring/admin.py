from django.contrib import admin
from .models import MetricSample, StatusEvent

@admin.register(MetricSample)
class MetricSampleAdmin(admin.ModelAdmin):
    list_display = ("server", "sampled_at", "cpu_percent", "memory_bytes", "players_online")
    list_filter = ("sampled_at",)
    date_hierarchy = "sampled_at"

@admin.register(StatusEvent)
class StatusEventAdmin(admin.ModelAdmin):
    list_display = ("server", "kind", "occurred_at", "detail")
    list_filter = ("kind", "occurred_at")
