from django.core.management.base import BaseCommand

from apps.panels.models import PterodactylPanel
from apps.panels.services import PterodactylAPIError
from apps.panels.sync import sync_panel_servers


class Command(BaseCommand):
    help = "Synchronise server records from all active Pterodactyl panels."

    def handle(self, *args, **options):
        panels = PterodactylPanel.objects.filter(is_active=True).order_by("pk")
        for panel in panels.iterator():
            try:
                result = sync_panel_servers(panel)
            except (PterodactylAPIError, ValueError) as exc:
                self.stderr.write(self.style.ERROR(f"{panel.name}: sync failed — {exc}"))
                continue

            self.stdout.write(
                self.style.SUCCESS(
                    f"{panel.name}: {result['created']} added, "
                    f"{result['updated']} updated, {result['missing']} missing."
                )
            )
