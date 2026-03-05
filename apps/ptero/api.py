"""Pterodactyl API client.

All HTTP calls to Pterodactyl are centralized here so upgrades are easy.

Auth:
- Application API key (admin): used to list servers across the panel.
- Client API key: used to query per-server resource usage/status.

By design, we keep HTTP and parsing logic here, and store the normalized results
into our database in the poller.

You can change endpoints in ONE place if your panel version differs.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import requests

@dataclass
class PteroServer:
    ptero_id: int
    identifier: str
    name: str
    node_name: str
    ip: str
    port: Optional[int]

@dataclass
class PteroStatus:
    state: str  # online/offline/unknown
    players_online: Optional[int] = None
    players_max: Optional[int] = None
    ping_ms: Optional[int] = None
    raw: Optional[dict] = None

class PteroAPI:
    def __init__(self, base_url: str, application_key: str = "", client_key: str = "", timeout: int = 15):
        self.base_url = base_url.rstrip("/")
        self.application_key = application_key.strip()
        self.client_key = client_key.strip()
        self.timeout = timeout

    # ---------- low-level helpers ----------
    def _get(self, path: str, *, token: str) -> dict:
        url = f"{self.base_url}{path}"
        r = requests.get(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"}, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    # ---------- application API ----------
    def list_servers(self) -> List[PteroServer]:
        """List servers from the Application API.

        Endpoint (typical):
            GET /api/application/servers?per_page=100

        We paginate defensively.
        """
        if not self.application_key:
            raise ValueError("PTERO_APPLICATION_API_KEY is not configured.")

        servers: List[PteroServer] = []
        page = 1
        while True:
            data = self._get(f"/api/application/servers?per_page=100&page={page}", token=self.application_key)
            items = data.get("data", []) or []
            for item in items:
                attr = item.get("attributes", {}) or {}
                alloc = None
                # Pterodactyl includes allocations in relationships (depends on include params).
                # We'll try best-effort and leave ip/port blank if missing.
                rel = attr.get("relationships", {}) or {}
                allocs = ((rel.get("allocations") or {}).get("data") or [])
                for a in allocs:
                    a_attr = a.get("attributes", {}) or {}
                    if a_attr.get("is_default"):
                        alloc = a_attr
                        break

                servers.append(PteroServer(
                    ptero_id=int(attr.get("id")),
                    identifier=str(attr.get("identifier") or ""),
                    name=str(attr.get("name") or f"server-{attr.get('id')}"),
                    node_name=str((attr.get("node") or "") or ""),
                    ip=str((alloc or {}).get("ip") or ""),
                    port=int((alloc or {}).get("port")) if (alloc or {}).get("port") else None,
                ))

            # pagination meta differs by version; handle common fields
            meta = data.get("meta", {}) or {}
            pagination = meta.get("pagination", {}) or {}
            total_pages = pagination.get("total_pages")
            if total_pages is None:
                # If meta is missing, stop when response is empty.
                if not items:
                    break
                page += 1
                continue

            if page >= int(total_pages):
                break
            page += 1

        return servers

    # ---------- client API ----------
    def get_resources_client(self, identifier: str) -> dict:
        """Fetch server resources using the Client API.

        Endpoint (typical):
            GET /api/client/servers/{identifier}/resources
        """
        if not self.client_key:
            raise ValueError("PTERO_CLIENT_API_KEY is not configured.")
        return self._get(f"/api/client/servers/{identifier}/resources", token=self.client_key)

    def parse_status(self, resources_json: dict) -> PteroStatus:
        """Normalize a Pterodactyl 'resources' response to a simple status.

        Pterodactyl returns something like:
            { "object": "stats", "attributes": { "current_state": "running", ... } }

        We map 'running' -> online, 'offline'/'stopped' -> offline.
        """
        attr = resources_json.get("attributes", {}) or {}
        current = (attr.get("current_state") or "").lower()

        if current in ("running", "starting"):
            state = "online"
        elif current in ("offline", "stopping", "stopped"):
            state = "offline"
        else:
            state = "unknown"

        # We don't have player counts for every game automatically.
        # Later versions can add per-game query integrations.
        return PteroStatus(state=state, raw=resources_json)
