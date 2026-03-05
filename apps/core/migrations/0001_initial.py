from django.db import migrations, models
import apps.core.fields

class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='SiteConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ptero_base_url', models.URLField(blank=True, default='', help_text='Example: https://panel.example.com')),
                ('ptero_application_api_key', apps.core.fields.EncryptedTextField(blank=True, default='', help_text='Application API key (admin).')),
                ('ptero_client_api_key', apps.core.fields.EncryptedTextField(blank=True, default='', help_text='Client API key.')),
                ('discord_webhook_url', apps.core.fields.EncryptedTextField(blank=True, default='', help_text='Optional Discord webhook for alerts.')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
