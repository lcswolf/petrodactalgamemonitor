from unittest.mock import patch

from cryptography.fernet import Fernet
from django.test import TestCase, override_settings

from apps.panels.models import PterodactylPanel
from apps.panels.services import PterodactylServer
from apps.panels.sync import sync_panel_servers
from apps.servers.models import GameServer


TEST_ENCRYPTION_KEY = Fernet.generate_key().decode()


@override_settings(ENCRYPTION_KEY=TEST_ENCRYPTION_KEY)
class PanelServerSyncTests(TestCase):
    def setUp(self):
        self.panel = PterodactylPanel.objects.create(
            name="Test panel",
            base_url="https://panel.example.com",
            application_api_key="test-application-key",
        )

    @patch("apps.panels.sync.PterodactylApplicationClient")
    def test_imports_new_servers(self, client_class):
        client_class.return_value.list_servers.return_value = [
            PterodactylServer(1, "abc123", "Survival", "", 1, False, False),
        ]

        result = sync_panel_servers(self.panel)

        server = GameServer.objects.get(panel=self.panel, external_id="abc123")
        self.assertEqual(server.name, "Survival")
        self.assertTrue(server.is_present_on_panel)
        self.assertEqual(result["created"], 1)
        self.assertEqual(result["total"], 1)
        self.panel.refresh_from_db()
        self.assertIsNotNone(self.panel.last_synced_at)

    @patch("apps.panels.sync.PterodactylApplicationClient")
    def test_updates_name_but_preserves_local_settings(self, client_class):
        existing = GameServer.objects.create(
            panel=self.panel,
            external_id="abc123",
            name="Old name",
            slug="survival-abc123",
            is_public=False,
            monitoring_enabled=False,
        )
        client_class.return_value.list_servers.return_value = [
            PterodactylServer(1, "abc123", "New name", "", 1, False, False),
        ]

        result = sync_panel_servers(self.panel)

        existing.refresh_from_db()
        self.assertEqual(existing.name, "New name")
        self.assertFalse(existing.is_public)
        self.assertFalse(existing.monitoring_enabled)
        self.assertTrue(existing.is_present_on_panel)
        self.assertEqual(result["updated"], 1)
        self.assertEqual(result["created"], 0)

    @patch("apps.panels.sync.PterodactylApplicationClient")
    def test_marks_missing_servers_without_deleting_them(self, client_class):
        existing = GameServer.objects.create(
            panel=self.panel,
            external_id="gone123",
            name="Removed server",
            slug="removed-server",
        )
        client_class.return_value.list_servers.return_value = []

        result = sync_panel_servers(self.panel)

        existing.refresh_from_db()
        self.assertFalse(existing.is_present_on_panel)
        self.assertTrue(GameServer.objects.filter(pk=existing.pk).exists())
        self.assertEqual(result["missing"], 1)

    @patch("apps.panels.sync.PterodactylApplicationClient")
    def test_failed_remote_listing_does_not_change_local_records(self, client_class):
        existing = GameServer.objects.create(
            panel=self.panel,
            external_id="abc123",
            name="Keep me",
            slug="keep-me",
        )
        client_class.return_value.list_servers.side_effect = RuntimeError("network down")

        with self.assertRaises(RuntimeError):
            sync_panel_servers(self.panel)

        existing.refresh_from_db()
        self.assertTrue(existing.is_present_on_panel)
        self.assertIsNone(existing.last_seen_on_panel)
