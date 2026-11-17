from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [("servers", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="MetricSample",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sampled_at", models.DateTimeField(db_index=True)),
                ("cpu_percent", models.FloatField(blank=True, null=True)),
                ("memory_bytes", models.PositiveBigIntegerField(blank=True, null=True)),
                ("disk_bytes", models.PositiveBigIntegerField(blank=True, null=True)),
                ("players_online", models.PositiveIntegerField(blank=True, null=True)),
                ("players_max", models.PositiveIntegerField(blank=True, null=True)),
                ("server", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="metric_samples", to="servers.gameserver")),
            ],
            options={
                "ordering": ["-sampled_at"],
                "indexes": [models.Index(fields=["server", "-sampled_at"], name="mon_metric_server_time_idx")],
            },
        ),
        migrations.CreateModel(
            name="StatusEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(choices=[("offline", "Offline"), ("online", "Online"), ("unknown", "Unknown")], max_length=12)),
                ("occurred_at", models.DateTimeField(db_index=True)),
                ("detail", models.CharField(blank=True, max_length=240)),
                ("server", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="status_events", to="servers.gameserver")),
            ],
            options={
                "ordering": ["-occurred_at"],
                "indexes": [models.Index(fields=["server", "-occurred_at"], name="mon_status_server_time_idx")],
            },
        ),
    ]
