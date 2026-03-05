"""Poll Pterodactyl and update server status.

Usage:
  # Sync inventory (create/update GameServer rows) + update status
  python manage.py poll_ptero --sync

  # Only update status (faster once inventory exists)
  python manage.py poll_ptero

Tips:
- Run this via cron every 1 minute, or use the provided systemd timer.
- If your panel has many servers, reduce polling interval or shard by clan.
"""

from __future__ import annotations
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.core.models import SiteConfig
from apps.ptero.api import PteroAPI
from apps.ptero.models import GameServer
from apps.monitor.models import ServerStatus, PollRun
from apps.monitor.notifications import DiscordNotifier

class Command(BaseCommand):
    help = "Poll Pterodactyl for server list and live status"

    def add_arguments(self, parser):
        parser.add_argument("--sync", action="store_true", help="Sync server inventory from Application API before polling status.")
        parser.add_argument("--limit", type=int, default=0, help="Optional limit number of servers to poll (for testing).")

    def handle(self, *args, **opts):
# Load configuration from DB (admin-editable). Fall back to env if blank.
cfg = SiteConfig.get_solo()
base_url = (cfg.ptero_base_url or settings.PTERO_BASE_URL).rstrip("/")
application_key = cfg.ptero_application_api_key or settings.PTERO_APPLICATION_API_KEY
client_key = cfg.ptero_client_api_key or settings.PTERO_CLIENT_API_KEY
webhook_url = cfg.discord_webhook_url or settings.DISCORD_WEBHOOK_URL

api = PteroAPI(base_url=base_url, application_key=application_key, client_key=client_key)
notifier = DiscordNotifier(webhook_url)

        run_ok = True
        run_msg = "OK"

        try:
            if opts["sync"]:
                self._sync_inventory(api)

            qs = GameServer.objects.all().order_by("id")
            if opts["limit"]:
                qs = qs[: int(opts["limit"])]

            for server in qs:
                self._poll_one(api, notifier, server)

        except Exception as e:
            run_ok = False
            run_msg = f"{type(e).__name__}: {e}"
            raise
        finally:
            PollRun.objects.create(ok=run_ok, message=run_msg)

    @transaction.atomic
    def _sync_inventory(self, api: PteroAPI) -> None:
        self.stdout.write("Syncing server inventory from Pterodactyl (Application API)...")
        servers = api.list_servers()

        for s in servers:
            obj, created = GameServer.objects.update_or_create(
                ptero_id=s.ptero_id,
                defaults={
                    "identifier": s.identifier,
                    "name": s.name,
                    "node_name": s.node_name,
                    "ip": s.ip,
                    "port": s.port,
                },
            )
            # Ensure status row exists
            ServerStatus.objects.get_or_create(server=obj)

        self.stdout.write(f"Inventory sync complete: {len(servers)} servers seen.")

    def _poll_one(self, api: PteroAPI, notifier: DiscordNotifier, server: GameServer) -> None:
        # Read previous status so we can alert on changes.
        status_obj, _ = ServerStatus.objects.get_or_create(server=server)
        previous = status_obj.state

        try:
            res = api.get_resources_client(server.identifier)
            status = api.parse_status(res)

            status_obj.state = status.state
            status_obj.players_online = status.players_online
            status_obj.players_max = status.players_max
            status_obj.ping_ms = status.ping_ms
            status_obj.last_checked_at = timezone.now()
            status_obj.save(update_fields=["state", "players_online", "players_max", "ping_ms", "last_checked_at"])

            # Send Discord alert on state changes
            if previous != status.state and previous != "unknown":
                notifier.send(f"🔔 **{server.name}** changed: `{previous}` → `{status.state}`")
        except Exception as e:
            # Don't crash polling for one server.
            status_obj.state = "unknown"
            status_obj.last_checked_at = timezone.now()
            status_obj.save(update_fields=["state", "last_checked_at"])
            # Optional: alert on poll failures
            # notifier.send(f"⚠️ Poll failed for **{server.name}**: {type(e).__name__}: {e}")
