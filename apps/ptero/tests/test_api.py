"""
Basic tests for the Pterodactyl API client (apps/ptero/api.py).
"""

from unittest.mock import patch, MagicMock

import pytest
import requests

from apps.ptero.api import PteroAPI, PteroServer, PteroStatus


# ====================== Fixtures ======================

@pytest.fixture
def mock_requests():
    with patch("apps.ptero.api.requests") as mock_req:
        yield mock_req


@pytest.fixture
def api():
    return PteroAPI(
        base_url="https://panel.example.com",
        application_key="app_key_123",
        client_key="client_key_456",
        timeout=10,
    )


# ====================== Tests ======================

def test_init_strips_values():
    api = PteroAPI(
        base_url="https://panel.example.com/",
        application_key="  app_key  ",
        client_key="  client_key  ",
    )
    assert api.base_url == "https://panel.example.com"
    assert api.application_key == "app_key"
    assert api.client_key == "client_key"


def test_list_servers_success(mock_requests, api):
    # Mock paginated response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {
                "attributes": {
                    "id": 101,
                    "identifier": "abc123def",
                    "name": "My Awesome Server",
                    "node": "node-1",
                    "relationships": {
                        "allocations": {
                            "data": [
                                {"attributes": {"ip": "1.2.3.4", "port": 25565, "is_default": True}}
                            ]
                        }
                    },
                }
            }
        ],
        "meta": {"pagination": {"total_pages": 1}},
    }
    mock_response.raise_for_status.return_value = None
    mock_requests.get.return_value = mock_response

    servers = api.list_servers()

    assert len(servers) == 1
    assert isinstance(servers[0], PteroServer)
    assert servers[0].ptero_id == 101
    assert servers[0].identifier == "abc123def"
    assert servers[0].name == "My Awesome Server"
    assert servers[0].ip == "1.2.3.4"
    assert servers[0].port == 25565


def test_list_servers_no_application_key(api):
    api.application_key = ""
    with pytest.raises(ValueError, match="PTERO_APPLICATION_API_KEY"):
        api.list_servers()


def test_get_resources_client_success(mock_requests, api):
    mock_response = MagicMock()
    mock_response.json.return_value = {"object": "stats", "attributes": {...}}
    mock_response.raise_for_status.return_value = None
    mock_requests.get.return_value = mock_response

    data = api.get_resources_client("abc123def")

    assert data == {"object": "stats", "attributes": {...}}
    mock_requests.get.assert_called_once()


def test_get_resources_client_no_key(api):
    api.client_key = ""
    with pytest.raises(ValueError, match="PTERO_CLIENT_API_KEY"):
        api.get_resources_client("abc123")


def test_parse_status_online():
    resources_json = {
        "attributes": {
            "current_state": "running",
            "resources": {
                "cpu_absolute": 45.7,
                "memory_bytes": 2147483648,  # 2GB
            },
        }
    }

    status = PteroAPI(base_url="").parse_status(resources_json)

    assert status.state == "online"
    assert status.cpu_percent == 45.7
    assert status.memory_mb == 2048
    assert status.raw == resources_json


def test_parse_status_offline():
    resources_json = {"attributes": {"current_state": "offline", "resources": {}}}

    status: PteroStatus = PteroAPI(base_url="").parse_status(resources_json)
    assert status.state == "offline"


def test_parse_status_unknown():
    resources_json = {"attributes": {"current_state": "crashed", "resources": {}}}
    status = PteroAPI(base_url="").parse_status(resources_json)
    assert status.state == "unknown"


def test_http_error_handling(mock_requests, api):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("401 Unauthorized")
    mock_requests.get.return_value = mock_response

    with pytest.raises(requests.HTTPError):
        api._get("/api/test", token="badkey")
