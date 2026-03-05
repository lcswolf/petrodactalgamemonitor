"""JSON endpoints for widgets/embeds.

Security goal:
- NEVER leak server IP, port, or Pterodactyl identifier via the public API.
  (Identifiers can be used to query the Client API, so keep them private.)

Output goal:
- Provide enough info to build widgets: state, players, ping, CPU%, RAM.
"""

from django.http import JsonResponse, Http404
from django.views.decorators.http import require_GET

from apps.ptero.models import GameServer, Clan
from apps.monitor.models import PollRun

def _last_poll_iso():
    dt = PollRun.objects.order_by("-ran_at").values_list("ran_at", flat=True).first()
    return dt.isoformat() if dt else None

def _status_dict(server: GameServer):
    st = getattr(server, "status", None)
    return {
        "state": getattr(st, "state", "unknown"),
        "players_online": getattr(st, "players_online", None),
        "players_max": getattr(st, "players_max", None),
        "ping_ms": getattr(st, "ping_ms", None),
        "cpu_percent": getattr(st, "cpu_percent", None),
        "memory_mb": getattr(st, "memory_mb", None),
        "last_checked_at": getattr(st, "last_checked_at", None).isoformat() if st else None,
    }

@require_GET
def servers_list(request):
    qs = GameServer.objects.filter(is_hidden=False).prefetch_related("status").order_by("name")
    data = []
    for s in qs:
        data.append({
            "id": s.id,
            "name": s.name,
            "node": s.node_name,
            "status": _status_dict(s),
        })
    return JsonResponse({"last_poll": _last_poll_iso(), "servers": data})

@require_GET
def server_status(request, server_id: int):
    s = GameServer.objects.filter(id=server_id, is_hidden=False).prefetch_related("status").first()
    if not s:
        raise Http404("Server not found.")

    return JsonResponse({
        "last_poll": _last_poll_iso(),
        "server": {
            "id": s.id,
            "name": s.name,
            "node": s.node_name,
        },
        "status": _status_dict(s),
    })

@require_GET
def clan_status(request, slug: str):
    clan = Clan.objects.filter(slug=slug, is_public=True).first()
    if not clan:
        raise Http404("Clan not found.")

    servers = clan.servers.filter(is_hidden=False).prefetch_related("status").order_by("name")
    out = []
    for s in servers:
        out.append({
            "id": s.id,
            "name": s.name,
            "node": s.node_name,
            "status": _status_dict(s),
        })

    return JsonResponse({
        "last_poll": _last_poll_iso(),
        "clan": {"name": clan.name, "slug": clan.slug},
        "servers": out
    })
