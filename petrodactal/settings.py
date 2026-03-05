"""Django settings for Petrodactal.

This project is intentionally split into modular Django apps:
- apps/core: settings, encrypted fields, app config helpers
- apps/ptero: Pterodactyl API integration + models
- apps/monitor: polling + status history
- apps/pages: public status pages (dashboard + clan pages)
- apps/api: JSON endpoints for embeds/widgets
"""

from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

def env(name: str, default: str = "") -> str:
    """Small helper to read environment variables safely."""
    return os.environ.get(name, default)

SECRET_KEY = env("SECRET_KEY", "dev-only-change-me")
DEBUG = env("DEBUG", "0") == "1"

ALLOWED_HOSTS = [h.strip() for h in env("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Local apps
    "apps.core",
    "apps.ptero",
    "apps.monitor",
    "apps.pages",
    "apps.api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # serve static assets w/ gunicorn
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "petrodactal.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "petrodactal.wsgi.application"

# Database: default to sqlite3 for simplest VPS setup.
# You can swap to Postgres later.
DATABASE_URL = env("DATABASE_URL", "").strip()
if DATABASE_URL:
    # Minimal parser for postgres URLs could be added later.
    # For now: keep sqlite unless you explicitly wire a DB.
    raise RuntimeError("DATABASE_URL parsing not implemented in v0.1; use SQLite or extend settings.py.")
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Security (production sensible defaults)
CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS if "." in h]
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False  # set True after you confirm nginx TLS is correct


# App-level defaults (DB config overrides these at runtime)
PTERO_BASE_URL = env("PTERO_BASE_URL", "").rstrip("/")
PTERO_APPLICATION_API_KEY = env("PTERO_APPLICATION_API_KEY", "").strip()
PTERO_CLIENT_API_KEY = env("PTERO_CLIENT_API_KEY", "").strip()
ENCRYPTION_KEY = env("ENCRYPTION_KEY", "").strip()
DISCORD_WEBHOOK_URL = env("DISCORD_WEBHOOK_URL", "").strip()
