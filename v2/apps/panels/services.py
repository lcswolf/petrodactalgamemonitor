"""Small, dependency-free client for the Pterodactyl Application API.

This client deliberately handles panel administration endpoints only. Live
resource utilisation is served by Pterodactyl's Client API and needs a
server-specific client API credential; an Application API key is not a
substitute for that credential.
"""
from dataclasses import dataclass
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class PterodactylAPIError(Exception):
    """A safe-to-display API error; never includes the API key."""


@dataclass(frozen=True)
class PterodactylServer:
    id: int
    identifier: str
    name: str
    description: str
    node: str | None
    is_suspended: bool
    is_installing: bool


class PterodactylApplicationClient:
    """Read-only access to a panel's Application API."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key.strip()
        self.timeout = timeout

        if not self.api_key:
            raise ValueError("A Pterodactyl Application API key is required.")

        # Avoid sending credentials over plain HTTP, except for local testing.
        if not self.base_url.startswith("https://") and not self.base_url.startswith(
            ("http://localhost", "http://127.0.0.1")
        ):
            raise ValueError("Pterodactyl panel URLs must use HTTPS.")

    def _get_json(self, path: str, query: dict | None = None) -> dict:
        url = f"{self.base_url}/api/application/{path.lstrip('/')}"
        if query:
            url = f"{url}?{urlencode(query)}"

        request = Request(
            url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/vnd.pterodactyl.v1+json",
                "Content-Type": "application/json",
                "User-Agent": "Petrodactal-Monitor/2",
            },
            method="GET",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            # Do not include request headers or exception details that might
            # expose credentials in logs or admin-facing error messages.
            if exc.code == 401:
                message = "Pterodactyl rejected the API key (HTTP 401)."
            elif exc.code == 403:
                message = "The API key lacks permission for this operation (HTTP 403)."
            elif exc.code == 404:
                message = "The requested Pterodactyl API endpoint was not found (HTTP 404)."
            else:
                message = f"Pterodactyl returned HTTP {exc.code}."
            raise PterodactylAPIError(message) from None
        except URLError:
            raise PterodactylAPIError(
                "Could not connect to the Pterodactyl panel. Check its URL and network access."
            ) from None
        except (TimeoutError, json.JSONDecodeError, UnicodeDecodeError):
            raise PterodactylAPIError(
                "Pterodactyl did not return a valid response before the request timed out."
            ) from None

        if not isinstance(payload, dict):
            raise PterodactylAPIError("Pterodactyl returned an unexpected response.")
        return payload

    def list_servers(self) -> list[PterodactylServer]:
        """Return every server visible to this Application API key."""
        servers = []
        page = 1

        while True:
            payload = self._get_json("servers", {"page": page, "per_page": 100})
            for item in payload.get("data", []):
                attributes = item.get("attributes", {})
                servers.append(
                    PterodactylServer(
                        id=int(attributes["id"]),
                        identifier=str(attributes["identifier"]),
                        name=str(attributes.get("name") or "Unnamed server"),
                        description=str(attributes.get("description") or ""),
                        node=(
                            str(attributes["node"])
                            if attributes.get("node") is not None
                            else None
                        ),
                        is_suspended=bool(attributes.get("is_suspended", False)),
                        is_installing=bool(attributes.get("is_installing", False)),
                    )
                )

            pagination = payload.get("meta", {}).get("pagination", {})
            total_pages = int(pagination.get("total_pages", page))
            if page >= total_pages:
                break
            page += 1

        return servers
