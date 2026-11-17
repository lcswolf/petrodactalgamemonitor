# Petrodactal Monitor v2

Petrodactal Monitor v2 is a lightweight rewrite of the original application. Development takes place on the `rewrite-development` branch; the original `main` branch is kept unchanged until the rewrite is reviewed.

## Product goals

- Public community pages and individual server status pages.
- Public CPU and RAM history, server uptime, and outage history.
- Optional player counts when the game server exposes them.
- Per-community or per-server Discord webhook alerts.
- Custom community branding.
- Read-only embeddable status and statistics widgets.
- A private administration area for managing panels, communities, servers, and visibility.
- Automatic synchronisation of server records from connected Pterodactyl panels.
- A controlled application update process with backups and recovery.

## Installation

An initial installer is provided for a **fresh Ubuntu 22.04 or 24.04 VPS**. It installs the operating-system packages, Python environment, PostgreSQL, Nginx, Gunicorn service, application secrets, and initial database tables.

### Before you start

You will need:

- A fresh Ubuntu VPS with a public IP address.
- A user with sudo access.
- At least 1 GB RAM (2 GB is preferable while installing packages).
- SSH access to the VPS.
- A domain name pointing to the VPS if you want HTTPS using Let's Encrypt. You can use the VPS IP address initially, but do not enter real administrator credentials or panel API keys until HTTPS is enabled.

**Important:** this installer configures Nginx as the website for this VPS and disables Ubuntu's stock Nginx default site. Do not run it on a server already hosting another website or using a custom Nginx configuration without reviewing the script first.

### 1. Connect to the VPS

Connect over SSH, then install Git:

```bash
sudo apt update
sudo apt install -y git
```

### 2. Download the development branch

The application is currently being developed on `rewrite-development`:

```bash
sudo git clone --branch rewrite-development https://github.com/lcswolf/petrodactalgamemonitor.git /opt/petrodactal-monitor
```

### 3. Run the installer

```bash
cd /opt/petrodactal-monitor
sudo bash v2/install-ubuntu.sh
```

The installer will:

1. Check that it is running on Ubuntu and from the correct project directory.
2. Install Python, build tools, PostgreSQL, Nginx, Certbot, and required system libraries.
3. Create a dedicated, unprivileged `petrodactal` service account.
4. Create a Python virtual environment and install the packages in `v2/requirements.txt`.
5. Ask for the public hostname or IP address.
6. Generate a Django secret key, a Fernet encryption key, and a PostgreSQL password.
7. Save the private configuration in `v2/.env` with restricted file permissions.
8. Create the PostgreSQL database and database account.
9. Generate the initial Django migrations and create the database tables.
10. Collect static files, then prompt you to create the first administrator account.
11. Configure and start Gunicorn under systemd and Nginx as the web server.

The installer preserves an existing `.env` file when run again. It also leaves an existing administrator account alone. It is designed for the initial development deployment, not as the future software updater.

### 4. Open the application

After a successful installation, visit:

- Admin area: `http://YOUR-HOSTNAME/admin/`
- Health check: `http://YOUR-HOSTNAME/health/`

The health check should return a small JSON response with status `ok`.

### 5. Enable HTTPS

If you entered a domain name, make sure its DNS record points to this VPS and that ports 80 and 443 are reachable. Then run:

```bash
sudo certbot --nginx -d monitor.example.com
```

Replace `monitor.example.com` with your actual domain. Follow Certbot's prompts and choose the HTTPS redirect option. Only enter administrator credentials or Pterodactyl API keys after HTTPS is working.

If you installed using an IP address and add a domain later, update `DJANGO_ALLOWED_HOSTS` in `v2/.env`, update the Nginx `server_name` in `/etc/nginx/sites-available/petrodactal-monitor`, then run:

```bash
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl restart petrodactal
```

### Useful service commands

Check whether the application is running:

```bash
sudo systemctl status petrodactal
```

View live application logs:

```bash
sudo journalctl -u petrodactal -f
```

Restart the application after a configuration change:

```bash
sudo systemctl restart petrodactal
```

Check Nginx:

```bash
sudo nginx -t
sudo systemctl status nginx
```

### Backups and secrets

The file `v2/.env` contains the Django secret, database password, and encryption key. Keep it private and make a secure backup. **If the Fernet `ENCRYPTION_KEY` is lost, encrypted Pterodactyl API keys and Discord webhook URLs cannot be recovered.** Do not put `.env` in GitHub, email it, or share it in support messages.

A basic PostgreSQL backup can be made with:

```bash
sudo -u postgres pg_dump petrodactal > petrodactal-backup.sql
```

Store the database backup and a protected copy of `v2/.env` somewhere separate from the VPS.

### Updating the development checkout

The built-in application updater is planned but is not implemented yet. For now, updates require a manual Git operation and should only be attempted after taking a database and `.env` backup.

The application directory is owned by the dedicated service account after installation. To fetch the latest development code:

```bash
sudo -u petrodactal git -C /opt/petrodactal-monitor pull
```

Do not run this as an unattended production update. Review changes first. Database migration and service restart steps will be documented as the project becomes ready for deployment.

## Hosting approach

The initial target is a small Ubuntu VPS (approximately 1 vCPU and 1 GB RAM). Keep the runtime deliberately small:

- Django application served by Gunicorn.
- PostgreSQL with conservative memory settings.
- Nginx for static files and reverse proxying.
- A lightweight scheduled monitoring worker; no Redis/Celery initially.
- Docker Compose is optional and will be evaluated against its memory overhead before adoption.

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
- Require HTTPS before entering real credentials.
- Validate and rate-limit public widget endpoints.
- Make public fields explicit rather than serialising database models wholesale.

## Current implementation status

Implemented on the development branch:

- Initial Django project and health endpoint.
- Database models for panels, communities, game servers, monitoring samples/events, and Discord webhook configuration.
- Fernet-backed encrypted model fields for panel API keys and Discord webhook URLs.
- Read-only Pterodactyl Application API client with pagination and safe error messages.
- Panel synchronisation that imports new servers, updates names, and marks missing servers without deleting history.
- Django admin action for manual panel sync.
- `sync_panels` management command for scheduled panel sync.
- Initial tests for the API client and panel synchronisation.
- Ubuntu installation script, PostgreSQL setup, and Gunicorn/Nginx service configuration.

Not yet implemented or verified:

- The application has not yet been installed or tested on the project owner's VPS.
- Automated tests have been written but have not yet been run in a complete deployment environment.
- Initial database migrations are currently generated by the installer; committed migration files are still needed before a production release.
- A systemd timer for automatic panel synchronisation.
- Live server status and CPU/RAM polling.
- Discord alert delivery.
- Public community and server pages.
- Embeddable widgets.
- The built-in software updater and rollback workflow.

The Pterodactyl Application API client is intentionally read-only. Live CPU/RAM resource utilisation uses Pterodactyl's Client API, not the Application API key; that credential flow will be designed separately.
