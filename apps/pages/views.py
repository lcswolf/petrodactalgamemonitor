"""Public pages (server-rendered HTML)."""

from django.shortcuts import get_object_or_404, render
from django.db.models import Prefetch
from apps.ptero.models import GameServer, Clan
from apps.monitor.models import PollRun, ServerStatus

def _last_poll():
    return PollRun.objects.order_by("-ran_at").values_list("ran_at", flat=True).first()

def dashboard(request):
    # Preload status objects to avoid N+1 queries.
    servers = (
        GameServer.objects.filter(is_hidden=False)
        .select_related(None)
        .prefetch_related("status")
        .order_by("name")
    )

    # Flatten to a view-model dict so templates stay simple.
    view_servers = []
    for s in servers:
        st = getattr(s, "status", None)
        view_servers.append({
            "id": s.id,
            "name": s.name,
            "node_name": s.node_name,
            "ip": s.ip,
            "port": s.port,
            "status_state": getattr(st, "state", "unknown"),
            "players_online": getattr(st, "players_online", None),
            "players_max": getattr(st, "players_max", None),
            "ping_ms": getattr(st, "ping_ms", None),
        })

    return render(request, "pages/dashboard.html", {"servers": view_servers, "last_poll": _last_poll()})

def clan_page(request, slug: str):
    clan = get_object_or_404(Clan, slug=slug, is_public=True)
    servers = (
        clan.servers.filter(is_hidden=False)
        .prefetch_related("status")
        .order_by("name")
    )

    view_servers = []
    for s in servers:
        st = getattr(s, "status", None)
        view_servers.append({
            "id": s.id,
            "name": s.name,
            "node_name": s.node_name,
            "ip": s.ip,
            "port": s.port,
            "status_state": getattr(st, "state", "unknown"),
            "players_online": getattr(st, "players_online", None),
            "players_max": getattr(st, "players_max", None),
            "ping_ms": getattr(st, "ping_ms", None),
        })

    return render(request, "pages/clan.html", {"clan": clan, "servers": view_servers, "last_poll": _last_poll()})
