from django.db import models

class PterodactylPanel(models.Model):
    name = models.CharField(max_length=100)
    base_url = models.URLField()
    application_api_key = models.TextField(help_text="Encrypted at application level before saving.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
