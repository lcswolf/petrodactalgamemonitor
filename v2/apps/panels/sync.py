"""Synchronise server records from a connected Pterodactyl panel."""
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from apps.servers.models import GameServer
from .services import PterodactylApplicationClient


def sync_panel_servers(panel, client_class=PterodactylApplicationClient):
    """Import/update panel servers without overwriting local monitor settings.

    Servers missing from a successful API listing are marked as no longer
    present. Their records and monitoring history are deliberately retained.
    """
    if not panel.is_active:
        raise ValueError("This Pterodactyl panel is disabled.")

    client = client_class(panel.base_url, panel.application_api_key)
    remote_servers = client.list_servers()
    checked_at = timezone.now()
    seen_identifiers = set()
    created_count = 0
    updated_count = 0

    # Only change local records after the complete remote listing succeeds.
    with transaction.atomic():
        for remote in remote_servers:
            identifier = remote.identifier
            seen_identifiers.add(identifier)
            server = GameServer.objects.filter(
                panel=panel, external_id=identifier
            ).first()

            if server:
                server.name = remote.name[:120]
                server.is_present_on_panel = True
                server.last_seen_on_panel = checked_at
                server.save(update_fields=[
                    "name", "is_present_on_panel", "last_seen_on_panel", "updated_at"
                ])
                updated_count += 1
                continue

            base_slug = slugify(f"{remote.name}-{identifier}")[:120] or "server"
            candidate = base_slug
            suffix = 2
            while GameServer.objects.filter(slug=candidate).exists():
                tail = f"-{panel.pk}-{suffix}"
                candidate = f"{base_slug[:140 - len(tail)]}{tail}"
                suffix += 1

            GameServer.objects.create(
                panel=panel,
                external_id=identifier,
                name=remote.name[:120],
                slug=candidate,
                is_present_on_panel=True,
                last_seen_on_panel=checked_at,
            )
            created_count += 1

        # A missing server is marked absent only after a successful full list.
        panel_servers = GameServer.objects.filter(panel=panel)
        if seen_identifiers:
            panel_servers.exclude(external_id__in=seen_identifiers).update(
                is_present_on_panel=False
            )
        else:
            panel_servers.update(is_present_on_panel=False)

        panel.last_synced_at = checked_at
        panel.save(update_fields=["last_synced_at", "updated_at"])

    return {
        "created": created_count,
        "updated": updated_count,
        "missing": GameServer.objects.filter(
            panel=panel, is_present_on_panel=False
        ).count(),
        "total": len(remote_servers),
        "synced_at": checked_at,
    }
