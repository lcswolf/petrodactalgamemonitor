from unittest.mock import patch

from django.test import SimpleTestCase

from apps.panels.services import (
    PterodactylApplicationClient,
    PterodactylAPIError,
)


class PterodactylApplicationClientTests(SimpleTestCase):
    def test_requires_api_key(self):
        with self.assertRaises(ValueError):
            PterodactylApplicationClient("https://panel.example.com", "")

    def test_rejects_plain_http_for_remote_panels(self):
        with self.assertRaises(ValueError):
            PterodactylApplicationClient("http://panel.example.com", "test-key")

    def test_allows_local_http_for_development(self):
        client = PterodactylApplicationClient("http://127.0.0.1:8080", "test-key")
        self.assertEqual(client.base_url, "http://127.0.0.1:8080")

    @patch.object(PterodactylApplicationClient, "_get_json")
    def test_lists_servers_across_pages(self, get_json):
        get_json.side_effect = [
            {
                "data": [{
                    "attributes": {
                        "id": 12,
                        "identifier": "abc123",
                        "name": "Example server",
                        "description": "",
                        "node": 2,
                        "is_suspended": False,
                        "is_installing": False,
                    }
                }],
                "meta": {"pagination": {"total_pages": 2}},
            },
            {
                "data": [{
                    "attributes": {
                        "id": 13,
                        "identifier": "def456",
                        "name": "Second server",
                    }
                }],
                "meta": {"pagination": {"total_pages": 2}},
            },
        ]

        client = PterodactylApplicationClient("https://panel.example.com", "test-key")
        servers = client.list_servers()

        self.assertEqual([server.id for server in servers], [12, 13])
        self.assertEqual([server.identifier for server in servers], ["abc123", "def456"])
        self.assertEqual(get_json.call_count, 2)
        self.assertEqual(get_json.call_args_list[0].args, ("servers", {"page": 1, "per_page": 100}))
        self.assertEqual(get_json.call_args_list[1].args, ("servers", {"page": 2, "per_page": 100}))

    @patch.object(PterodactylApplicationClient, "_get_json")
    def test_returns_empty_list_when_panel_has_no_servers(self, get_json):
        get_json.return_value = {
            "data": [],
            "meta": {"pagination": {"total_pages": 1}},
        }
        client = PterodactylApplicationClient("https://panel.example.com", "test-key")
        self.assertEqual(client.list_servers(), [])

