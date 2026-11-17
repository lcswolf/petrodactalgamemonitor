from cryptography.fernet import Fernet
from django.db import connection
from django.test import TestCase, override_settings

from apps.panels.admin import PterodactylPanelAdminForm
from apps.panels.models import PterodactylPanel


TEST_ENCRYPTION_KEY = Fernet.generate_key().decode()


@override_settings(ENCRYPTION_KEY=TEST_ENCRYPTION_KEY)
class EncryptedPanelCredentialTests(TestCase):
    def test_api_key_is_encrypted_in_database_and_decrypted_on_read(self):
        secret = "ptla_this-is-a-test-api-key"
        panel = PterodactylPanel.objects.create(
            name="Test panel",
            base_url="https://panel.example.com",
            application_api_key=secret,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT application_api_key FROM panels_pterodactylpanel WHERE id = %s",
                [panel.pk],
            )
            stored_value = cursor.fetchone()[0]

        self.assertNotEqual(stored_value, secret)
        panel.refresh_from_db()
        self.assertEqual(panel.application_api_key, secret)

    def test_admin_form_does_not_prefill_existing_api_key(self):
        panel = PterodactylPanel.objects.create(
            name="Test panel",
            base_url="https://panel.example.com",
            application_api_key="ptla_existing-secret",
        )

        form = PterodactylPanelAdminForm(instance=panel)

        self.assertEqual(form.initial["application_api_key"], "")
        self.assertFalse(form.fields["application_api_key"].required)
        self.assertTrue(form.fields["application_api_key"].widget.render_value is False)

    def test_blank_admin_key_field_preserves_existing_api_key(self):
        panel = PterodactylPanel.objects.create(
            name="Test panel",
            base_url="https://panel.example.com",
            application_api_key="ptla_existing-secret",
        )
        form = PterodactylPanelAdminForm(
            data={
                "name": "Renamed panel",
                "base_url": "https://panel.example.com",
                "application_api_key": "",
                "is_active": "on",
            },
            instance=panel,
        )

        self.assertTrue(form.is_valid(), form.errors)
        updated = form.save()
        self.assertEqual(updated.application_api_key, "ptla_existing-secret")
