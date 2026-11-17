from django.db import models

class Community(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    logo_url = models.URLField(blank=True)
    banner_url = models.URLField(blank=True)
    accent_colour = models.CharField(max_length=7, default="#2563eb")
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
