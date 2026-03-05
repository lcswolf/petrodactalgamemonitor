from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='GameServer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ptero_id', models.PositiveIntegerField(unique=True)),
                ('identifier', models.CharField(max_length=32, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('node_name', models.CharField(blank=True, default='', max_length=255)),
                ('ip', models.CharField(blank=True, default='', max_length=64)),
                ('port', models.PositiveIntegerField(blank=True, null=True)),
                ('is_hidden', models.BooleanField(default=False, help_text='If true, hide from public pages and API.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Clan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('slug', models.SlugField(max_length=120, unique=True)),
                ('description', models.TextField(blank=True, default='')),
                ('is_public', models.BooleanField(default=True)),
            ],
        ),
        migrations.AddField(
            model_name='clan',
            name='servers',
            field=models.ManyToManyField(blank=True, related_name='clans', to='ptero.gameserver'),
        ),
    ]
