# Petrodactal Monitor v2

This directory is the clean rewrite. The original application remains in the repository for reference; development of v2 happens here on the `rewrite-development` branch.

## Product goals

- Public community pages and individual server status pages.
- Public CPU and RAM history, server uptime, and outage history.
- Optional player counts when the game server exposes them.
- Per-community Discord webhook alerts.
- Custom community branding.
- Read-only embeddable status and statistics widgets.
- A private administration area for managing panels, communities, servers, and visibility.

## Initial deployment constraints

The first deployment targets a small Ubuntu VPS (approximately 1 vCPU and 1 GB RAM). Keep the runtime deliberately small:

- Django application.
- PostgreSQL with conservative memory settings.
- One lightweight scheduled monitoring worker; no Redis/Celery initially.
- A reverse proxy providing HTTPS.
- Docker Compose is optional and will be evaluated against its memory overhead before adoption.

## Proposed layout

```text
v2/
  config/                 Django project settings and URL routing
  apps/
    panels/               Pterodactyl panel connections
    communities/          Public communities and branding
    servers/              Server records and public status
    monitoring/            Poll scheduling, samples, outages, uptime
    notifications/         Discord webhook delivery and throttling
    widgets/               Public, read-only embed endpoints
  templates/               Server-rendered pages
  static/                  CSS, JavaScript, and images
  tests/                   Cross-app and deployment tests
  manage.py
  requirements.txt
  .env.example
```

This is a proposed structure, not a claim that these components have already been implemented.

## Monitoring principles

- Treat server availability and resource-stat collection as separate signals.
- Start with a configurable five-minute collection interval.
- Stagger work across servers to avoid bursts.
- Pterodactyl resource utilisation can provide CPU and memory together; avoid duplicate API calls.
- Record sample timestamps and expose the age of the latest sample.
- Do not turn a failed statistics request into an offline event.
- Deduplicate alerts and notify on meaningful state transitions.

## Security principles

- Never expose Pterodactyl credentials, internal IDs that reveal infrastructure, or private configuration in public pages or widgets.
- Store secrets outside source control.
- Validate and rate-limit public widget endpoints.
- Make public fields explicit rather than serialising database models wholesale.

## Development approach

Build and test one small milestone at a time. Keep the old `main` branch unchanged, commit work on `rewrite-development`, and only merge after review and approval.

## Current implementation status

The initial domain-model layer is now present on the development branch:

- Pterodactyl panel records.
- Public community records and basic branding fields.
- Game server records linked to a panel and optional community.
- Timestamped metric samples and server status events.
- Per-community or per-server Discord webhook configuration.
- Django admin registrations for the initial models.
- Fernet-backed encrypted model fields for panel API keys and Discord webhook URLs.\n- A read-only Pterodactyl Application API client that can list all servers visible to a panel key, including pagination and safe error messages.

The project has not yet been installed or executed on the VPS. The Pterodactyl API client has been added but has not yet been tested against a live panel. Database migrations, automated tests, importing servers into the database, resource polling, alert delivery, public pages, and widgets remain to be implemented and verified.\n\nThe Application API client is intentionally read-only. Pterodactyl's live CPU/RAM resource endpoint uses the Client API, not the Application API key. We will design that credential handling separately rather than incorrectly reusing the panel key. Generate a unique Fernet key for `ENCRYPTION_KEY` and keep it backed up securely; losing it makes stored secrets unreadable.
