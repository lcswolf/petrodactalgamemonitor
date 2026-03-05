#!/usr/bin/env bash
# Petrodactal Game Monitor - updater (for future releases)
#
# What this does:
#  - (Optional) pulls the latest code from GitHub
#  - Backs up db.sqlite3 and .env
#  - Updates Python requirements
#  - Runs migrations + collectstatic
#  - Restarts services (gunicorn + poller)
#
# Usage:
#   sudo bash update.sh
#
# Notes:
#  - This script will NOT overwrite your .env
#  - If you made local code changes, git pull may fail (by design). In that case, commit/stash first.

set -euo pipefail

########################################
# Config
########################################
APP_DIR_DEFAULT="/opt/petrodactalgamemonitor"
RUN_USER="www-data"

log()  { echo -e "\n[update] $*"; }
warn() { echo -e "\n[update][WARN] $*" >&2; }
die()  { echo -e "\n[update][ERROR] $*" >&2; exit 1; }

if [[ "${EUID}" -ne 0 ]]; then
  die "Please run as root: sudo bash update.sh"
fi

# Determine app directory (prefer script location if it contains manage.py)
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
APP_DIR="${APP_DIR_DEFAULT}"
if [[ -f "${SCRIPT_DIR}/manage.py" ]]; then
  APP_DIR="${SCRIPT_DIR}"
elif [[ -f "${APP_DIR_DEFAULT}/manage.py" ]]; then
  APP_DIR="${APP_DIR_DEFAULT}"
else
  die "Could not find manage.py in ${SCRIPT_DIR} or ${APP_DIR_DEFAULT}. Run update.sh from the project folder."
fi

cd "${APP_DIR}"

log "Installing minimal OS packages…"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y git python3 python3-venv python3-pip

log "Backing up config and database…"
BACKUP_DIR="${APP_DIR}/backups"
mkdir -p "${BACKUP_DIR}"
TS="$(date -u +%Y%m%d-%H%M%S)"

if [[ -f ".env" ]]; then
  cp ".env" "${BACKUP_DIR}/.env.${TS}"
  chmod 600 "${BACKUP_DIR}/.env.${TS}" || true
fi

if [[ -f "db.sqlite3" ]]; then
  cp "db.sqlite3" "${BACKUP_DIR}/db.sqlite3.${TS}"
fi

log "Updating code from GitHub (if this is a git repo)…"
if [[ -d ".git" ]]; then
  # Warn if there are uncommitted changes
  if ! git diff --quiet || ! git diff --cached --quiet; then
    warn "You have local changes. git pull may fail. Consider: git status"
  fi

  git fetch --all --prune
  # Fast-forward only: prevents accidental merge commits in production
  git pull --ff-only
else
  warn "No .git folder found. Skipping git pull. (If you installed from a ZIP, update by replacing files manually.)"
fi

log "Ensuring virtualenv exists…"
if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi

log "Updating Python dependencies…"
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

log "Running migrations + collectstatic…"
python manage.py migrate
python manage.py collectstatic --noinput

log "Restarting services…"
# These service names match the ones installed by install.sh
systemctl restart petrodactal-gunicorn || warn "Could not restart petrodactal-gunicorn (is it installed?)"
systemctl start petrodactal-poller.service || true

# Reload nginx safely if present
if command -v nginx >/dev/null 2>&1; then
  nginx -t && systemctl reload nginx || warn "nginx reload failed"
fi

log "Done!"
echo ""
echo "If something goes wrong, your backups are here:"
echo "  ${BACKUP_DIR}"
