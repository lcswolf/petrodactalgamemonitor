from django import forms
from django.contrib import admin, messages

from .models import PterodactylPanel
from .services import PterodactylAPIError
from .sync import sync_panel_servers


class PterodactylPanelAdminForm(forms.ModelForm):
    application_api_key = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}, render_value=False),
        help_text="Leave blank to keep the existing key. Enter a new key to replace it.",
    )

    class Meta:
        model = PterodactylPanel
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stored_api_key = self.instance.application_api_key if self.instance.pk else ""
        self.fields["application_api_key"].required = not bool(self.instance.pk)
        self.initial["application_api_key"] = ""

    def clean_application_api_key(self):
        return self.cleaned_data["application_api_key"] or self._stored_api_key


@admin.register(PterodactylPanel)
class PterodactylPanelAdmin(admin.ModelAdmin):
    form = PterodactylPanelAdminForm
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
