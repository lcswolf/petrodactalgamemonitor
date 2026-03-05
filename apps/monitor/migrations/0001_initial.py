from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ptero', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PollRun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ran_at', models.DateTimeField(auto_now_add=True)),
                ('ok', models.BooleanField(default=True)),
                ('message', models.TextField(blank=True, default='')),
            ],
        ),
        migrations.CreateModel(
            name='ServerStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(default='unknown', max_length=16)),
                ('players_online', models.IntegerField(blank=True, null=True)),
                ('players_max', models.IntegerField(blank=True, null=True)),
                ('ping_ms', models.IntegerField(blank=True, null=True)),
                ('last_checked_at', models.DateTimeField(auto_now=True)),
                ('server', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='status', to='ptero.gameserver')),
            ],
        ),
    ]
