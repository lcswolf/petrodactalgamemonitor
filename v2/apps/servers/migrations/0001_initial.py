from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("communities", "0001_initial"),
        ("panels", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="GameServer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("external_id", models.CharField(max_length=80)),
                ("name", models.CharField(max_length=120)),
                ("slug", models.SlugField(max_length=140, unique=True)),
                ("game", models.CharField(blank=True, max_length=80)),
                ("is_public", models.BooleanField(default=True)),
                ("monitoring_enabled", models.BooleanField(default=True)),
                ("is_present_on_panel", models.BooleanField(default=True)),
                ("last_seen_on_panel", models.DateTimeField(blank=True, null=True)),
                ("poll_interval_seconds", models.PositiveSmallIntegerField(default=300)),
                ("last_status", models.CharField(default="unknown", max_length=16)),
                ("last_status_at", models.DateTimeField(blank=True, null=True)),
                ("last_metrics_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("community", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="servers", to="communities.community")),
                ("panel", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="servers", to="panels.pterodactylpanel")),
            ],
            options={
                "ordering": ["name"],
                "constraints": [models.UniqueConstraint(fields=("panel", "external_id"), name="unique_panel_server_id")],
                "indexes": [
                    models.Index(fields=["monitoring_enabled", "last_metrics_at"], name="srv_mon_enabled_metrics_idx"),
                    models.Index(fields=["panel", "is_present_on_panel"], name="srv_panel_present_idx"),
                ],
            },
        ),
    ]
