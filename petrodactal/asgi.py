"""ASGI config for Petrodactal."""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'petrodactal.settings')
application = get_asgi_application()
