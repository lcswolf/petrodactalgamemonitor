from django import forms
from django.contrib import admin

from .models import DiscordWebhook


class DiscordWebhookAdminForm(forms.ModelForm):
    webhook_url_encrypted = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}, render_value=False),
        help_text="Leave blank to keep the existing webhook URL. Enter a new URL to replace it.",
    )

    class Meta:
        model = DiscordWebhook
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stored_webhook_url = self.instance.webhook_url_encrypted if self.instance.pk else ""
        self.fields["webhook_url_encrypted"].required = not bool(self.instance.pk)
        self.initial["webhook_url_encrypted"] = ""

    def clean_webhook_url_encrypted(self):
        return self.cleaned_data["webhook_url_encrypted"] or self._stored_webhook_url


@admin.register(DiscordWebhook)
class DiscordWebhookAdmin(admin.ModelAdmin):
    form = DiscordWebhookAdminForm
    list_display = ("name", "community", "server", "is_enabled", "notify_offline", "notify_recovery")
    list_filter = ("is_enabled", "notify_offline", "notify_recovery")
