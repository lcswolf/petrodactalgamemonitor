from django.contrib import admin
from .models import SiteConfig

@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    """Admin UI for the singleton configuration."""
    list_display = ("__str__", "updated_at")

    def has_add_permission(self, request):
        # Only allow ONE config row.
        return not SiteConfig.objects.exists()
