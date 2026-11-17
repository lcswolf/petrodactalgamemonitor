from django.contrib import admin, messages

from .models import PterodactylPanel
from .services import PterodactylAPIError
from .sync import sync_panel_servers


@admin.register(PterodactylPanel)
class PterodactylPanelAdmin(admin.ModelAdmin):
    list_display = ("name", "base_url", "is_active", "last_synced_at", "updated_at")
    search_fields = ("name", "base_url")
    actions = ("sync_selected_panels",)

    @admin.action(description="Sync servers from selected Pterodactyl panels")
    def sync_selected_panels(self, request, queryset):
        for panel in queryset:
            try:
                result = sync_panel_servers(panel)
            except (PterodactylAPIError, ValueError) as exc:
                self.message_user(
                    request,
                    f"{panel.name}: sync failed — {exc}",
                    level=messages.ERROR,
                )
                continue

            self.message_user(
                request,
                (
                    f"{panel.name}: sync complete — "
                    f"{result['created']} added, {result['updated']} updated, "
                    f"{result['missing']} no longer present."
                ),
                level=messages.SUCCESS,
            )
