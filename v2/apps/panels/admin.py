from django.contrib import admin
from .models import PterodactylPanel

@admin.register(PterodactylPanel)
class PterodactylPanelAdmin(admin.ModelAdmin):
    list_display = ("name", "base_url", "is_active", "updated_at")
    search_fields = ("name", "base_url")
