from cryptography.fernet import Fernet
from django.test import TestCase, override_settings

from apps.panels.admin import PterodactylPanelAdminForm
from apps.panels.models import PterodactylPanel


TEST_ENCRYPTION_KEY = Fernet.generate_key().decode()


@override_settings(ENCRYPTION_KEY=TEST_ENCRYPTION_KEY)
class PanelSecretAdminFormTests(TestCase):
    def test_existing_api_key_is_not_rendered_and_blank_keeps_it(self):
        panel = PterodactylPanel.objects.create(
            name="Test panel",
            base_url="https://panel.example.com",
            application_api_key="secret-test-key",
        )
        form = PterodactylPanelAdminForm(instance=panel)
        self.assertEqual(form["application_api_key"].value(), "")

        data = {
            "name": panel.name,
            "base_url": panel.base_url,
            "application_api_key": "",
            "is_active": "on",
        }
        form = PterodactylPanelAdminForm(data=data, instance=panel)
        self.assertTrue(form.is_valid(), form.errors)
        updated = form.save()
        updated.refresh_from_db()
        self.assertEqual(updated.application_api_key, "secret-test-key")

    def test_new_panel_requires_an_api_key(self):
        form = PterodactylPanelAdminForm(data={
            "name": "New panel",
            "base_url": "https://panel.example.com",
            "application_api_key": "",
            "is_active": "on",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("application_api_key", form.errors)
