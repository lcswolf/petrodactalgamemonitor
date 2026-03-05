#!/usr/bin/env bash
set -euo pipefail

echo "[upgrade] Petrodactal upgrade pack v1"
echo "[upgrade] This script assumes the project is installed in /opt/petrodactalgamemonitor"

if [[ $EUID -ne 0 ]]; then
  echo "[upgrade] Please run as root: sudo bash upgrade.sh"
  exit 1
fi

cd /opt/petrodactalgamemonitor

if [[ ! -d ".venv" ]]; then
  echo "[upgrade] ERROR: .venv not found in /opt/petrodactalgamemonitor"
  exit 1
fi

# Install daily sync systemd units (optional but recommended)
if [[ -f "deploy/systemd/petrodactal-sync.service" && -f "deploy/systemd/petrodactal-sync.timer" ]]; then
  echo "[upgrade] Installing daily sync systemd timer..."
  cp -f deploy/systemd/petrodactal-sync.service /etc/systemd/system/petrodactal-sync.service
  cp -f deploy/systemd/petrodactal-sync.timer /etc/systemd/system/petrodactal-sync.timer
  systemctl daemon-reload
  systemctl enable --now petrodactal-sync.timer || true
fi

echo "[upgrade] Running migrations..."
sudo -u www-data /opt/petrodactalgamemonitor/.venv/bin/python /opt/petrodactalgamemonitor/manage.py migrate --noinput

echo "[upgrade] Restarting services..."
systemctl restart petrodactal-gunicorn || true
systemctl reload nginx || true

echo "[upgrade] Running one poll to populate CPU/RAM..."
sudo -u www-data /opt/petrodactalgamemonitor/.venv/bin/python /opt/petrodactalgamemonitor/manage.py poll_ptero || true

echo "[upgrade] Done."
echo "[upgrade] Optional: set PUBLIC_BASE_URL in /opt/petrodactalgamemonitor/.env to show full clan share links:"
echo "         PUBLIC_BASE_URL=https://monitor.cymru-hosting.co.uk"
