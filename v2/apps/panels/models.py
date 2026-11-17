from django.db import models
from apps.core.fields import EncryptedTextField

class PterodactylPanel(models.Model):
    name = models.CharField(max_length=100)
    base_url = models.URLField()
    application_api_key = EncryptedTextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
