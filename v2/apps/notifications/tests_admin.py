from cryptography.fernet import Fernet
from django.test import TestCase, override_settings

from apps.communities.models import Community
from apps.notifications.admin import DiscordWebhookAdminForm
from apps.notifications.models import DiscordWebhook


TEST_ENCRYPTION_KEY = Fernet.generate_key().decode()


@override_settings(ENCRYPTION_KEY=TEST_ENCRYPTION_KEY)
class DiscordWebhookSecretAdminFormTests(TestCase):
    def test_existing_webhook_is_not_rendered_and_blank_keeps_it(self):
        community = Community.objects.create(name="Test community", slug="test-community")
        webhook = DiscordWebhook.objects.create(
            community=community,
            webhook_url_encrypted="https://discord.com/api/webhooks/test/secret",
        )
        form = DiscordWebhookAdminForm(instance=webhook)
        self.assertEqual(form["webhook_url_encrypted"].value(), "")

        data = {
            "community": community.pk,
            "name": webhook.name,
            "webhook_url_encrypted": "",
            "notify_offline": "on",
            "notify_recovery": "on",
            "is_enabled": "on",
        }
        form = DiscordWebhookAdminForm(data=data, instance=webhook)
        self.assertTrue(form.is_valid(), form.errors)
        updated = form.save()
        updated.refresh_from_db()
        self.assertEqual(
            updated.webhook_url_encrypted,
            "https://discord.com/api/webhooks/test/secret",
        )
