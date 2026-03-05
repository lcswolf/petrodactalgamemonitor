# Petrodactal Game Monitor (Pterodactyl Status Panel)

A self-hosted, modular **status panel** for game servers hosted on a **Pterodactyl** panel.

Designed for:
- Ubuntu 24.04 VPS (no Docker required)
- A simple, upgrade-friendly architecture (Django apps)
- Admin UI for configuration (Django Admin)
- Public pages: global status + per-clan status pages
- Embeddable JSON endpoints for widgets

> **Note:** Pterodactyl API endpoints can vary slightly by panel version. The integration here supports both
> **Application API** and **Client API** flows, and is written to be easy to adjust in one place (`apps/ptero/api.py`).

---

## Features (v0.1 included in this repo)

### Admin (built-in Django Admin)
- Store Pterodactyl base URL and API keys **in the DB** (encrypted at rest)
- Auto-sync server list from Pterodactyl (via poller)
- Hide servers from public pages
- Create “Clans” and assign servers to each clan
- Configure Discord webhook alerts (optional)

### Public
- `/` dashboard: visible servers + last check time
- `/clan/<slug>/` clan status pages

### API (for embeds/widgets)
- `/api/v1/servers/` list
- `/api/v1/servers/<id>/status/`
- `/api/v1/clans/<slug>/status/`

---

## Quick start (Ubuntu 24.04)

### 1) System dependencies
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx
```

### 2) Clone + virtualenv
```bash
git clone https://github.com/lcswolf/petrodactalgamemonitor.git
cd petrodactalgamemonitor
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3) Configure environment
Copy the example env file:
```bash
cp .env.example .env
```

Generate an encryption key:
```bash
python manage.py generate_encryption_key
```

Put the printed key into `.env` as `ENCRYPTION_KEY=`.

### 4) DB + admin user
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 5) Run locally (test)
```bash
python manage.py runserver 0.0.0.0:8000
```
Open:
- `http://<your-vps-ip>:8000/` (public)
- `http://<your-vps-ip>:8000/admin/` (admin)

### 6) Production (systemd + nginx)
See:
- `deploy/systemd/` (Gunicorn + poller)
- `deploy/nginx/` (Nginx site)

---

## How polling works

A poller command fetches:
- Server inventory (names/identifiers) via Application API
- Live status/resources via Client API (or Application API if enabled on your panel)

It updates the `ServerStatus` table and triggers Discord alerts on state changes.

You can run it manually:
```bash
python manage.py poll_ptero --sync
```

---

## Development notes
- All “Pterodactyl API” code is centralized in: `apps/ptero/api.py`
- Polling logic lives in: `apps/monitor/management/commands/poll_ptero.py`
- Public pages: `apps/pages/`
- Embeddable JSON: `apps/api/`

---

## License
MIT
