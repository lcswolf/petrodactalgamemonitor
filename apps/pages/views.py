"""Public pages (server-rendered HTML).

Goals:
- Keep templates simple by building a small "view model" dict per server.
- NEVER expose server IP/port publicly.
- Show useful runtime stats: state, players, ping, CPU%, RAM (MB).
"""

from django.shortcuts import get_object_or_404, render

from apps.ptero.models import GameServer, Clan
from apps.monitor.models import PollRun

def _last_poll():
    """Timestamp of the last poll run (used for 'Last updated' display)."""
    return PollRun.objects.order_by("-ran_at").values_list("ran_at", flat=True).first()

def _server_vm(s):
    """Build a safe view-model for a server (NO IP/PORT)."""
    st = getattr(s, "status", None)

    return {
        "id": s.id,
        "name": s.name,
        "node_name": s.node_name,

        # status fields (from ServerStatus one-to-one)
        "status_state": getattr(st, "state", "unknown"),
        "players_online": getattr(st, "players_online", None),
        "players_max": getattr(st, "players_max", None),
        "ping_ms": getattr(st, "ping_ms", None),

        # resource usage (from Pterodactyl resources endpoint)
        "cpu_percent": getattr(st, "cpu_percent", None),
        "memory_mb": getattr(st, "memory_mb", None),

        "last_checked_at": getattr(st, "last_checked_at", None),
    }

def dashboard(request):
    """Public dashboard page (all visible servers)."""
    servers = (
        GameServer.objects
        .filter(is_hidden=False)
        .prefetch_related("status")
        .order_by("name")
    )

    view_servers = [_server_vm(s) for s in servers]
    return render(request, "pages/dashboard.html", {"servers": view_servers, "last_poll": _last_poll()})

def clan_page(request, slug: str):
    """Public clan page (only servers assigned to this clan)."""
    clan = get_object_or_404(Clan, slug=slug, is_public=True)

    servers = (
        clan.servers
        .filter(is_hidden=False)
        .prefetch_related("status")
        .order_by("name")
    )

    view_servers = [_server_vm(s) for s in servers]
    return render(request, "pages/clan.html", {"clan": clan, "servers": view_servers, "last_poll": _last_poll()})
