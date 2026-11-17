from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("communities", "0001_initial"),
        ("servers", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="DiscordWebhook",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(default="Discord alerts", max_length=100)),
                ("webhook_url_encrypted", models.TextField()),
                ("notify_offline", models.BooleanField(default=True)),
                ("notify_recovery", models.BooleanField(default=True)),
                ("cpu_threshold_percent", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("memory_threshold_percent", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("is_enabled", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("community", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="webhooks", to="communities.community")),
                ("server", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="webhooks", to="servers.gameserver")),
            ],
        ),
    ]
