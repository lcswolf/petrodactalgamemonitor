#!/usr/bin/env bash
# Petrodactal Game Monitor - installer for Ubuntu 24.04 (no Docker)
#
# What this does:
#  - Installs OS packages (python/nginx/etc.)
#  - Places the app into /opt/petrodactalgamemonitor (default)
#  - Creates a Python virtualenv and installs requirements
#  - Creates/updates .env (SECRET_KEY, ENCRYPTION_KEY, ALLOWED_HOSTS, etc.)
#  - Runs migrations + collectstatic + (optional) createsuperuser
#  - Installs systemd services (gunicorn + poller timer)
#  - Installs nginx site config and reloads nginx
#
# Usage:
#   sudo bash install.sh
#
# After install:
#   Visit: http://monitor.cymru-hosting.co.uk/admin/
#   Or set keys in .env and then run a sync:
#     sudo -u www-data /opt/petrodactalgamemonitor/.venv/bin/python /opt/petrodactalgamemonitor/manage.py poll_ptero --sync

set -euo pipefail

########################################
# Config you may change
########################################
DOMAIN_DEFAULT="monitor.cymru-hosting.co.uk"
APP_DIR_DEFAULT="/opt/petrodactalgamemonitor"
RUN_USER="www-data"
RUN_GROUP="www-data"

########################################
# Helpers
########################################
log()  { echo -e "\n[install] $*"; }
warn() { echo -e "\n[install][WARN] $*" >&2; }
die()  { echo -e "\n[install][ERROR] $*" >&2; exit 1; }

require_root() {
  if [[ "${EUID}" -ne 0 ]]; then
    die "Please run as root: sudo bash install.sh"
  fi
}

# Simple "replace or add" for KEY=VALUE lines in .env
set_env_kv() {
  local key="$1"
  local value="$2"
  local file="$3"

  # Escape backslashes, slashes and ampersands for sed replacement
  local esc_value
  esc_value="$(printf '%s' "$value" | sed -e 's/[\/&]/\\&/g')"

  if grep -qE "^${key}=" "$file"; then
    sed -i "s/^${key}=.*/${key}=${esc_value}/" "$file"
  else
    printf '\n%s=%s\n' "$key" "$value" >> "$file"
  fi
}

prompt_default() {
  local prompt="$1"
  local default="$2"
  local out_var="$3"

  local input=""
  read -r -p "${prompt} [${default}]: " input || true
  if [[ -z "${input}" ]]; then
    input="${default}"
  fi
  printf -v "${out_var}" "%s" "${input}"
}

prompt_secret() {
  local prompt="$1"
  local out_var="$2"
  local input=""
  read -r -s -p "${prompt}: " input || true
  echo ""
  printf -v "${out_var}" "%s" "${input}"
}

########################################
# Main
########################################
require_root

log "Starting Petrodactal installer…"

# If the user runs this from a cloned repo/zip folder, we will copy the code into /opt.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
DOMAIN="${DOMAIN_DEFAULT}"
APP_DIR="${APP_DIR_DEFAULT}"

prompt_default "Domain name for this panel" "${DOMAIN_DEFAULT}" DOMAIN
prompt_default "Install directory" "${APP_DIR_DEFAULT}" APP_DIR

log "Installing OS packages…"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y python3 python3-venv python3-pip nginx git curl rsync

# Ensure target directory exists
mkdir -p "${APP_DIR}"

# If APP_DIR does not already contain manage.py, copy the project into it.
if [[ ! -f "${APP_DIR}/manage.py" ]]; then
  log "Copying project into ${APP_DIR}…"
  # Copy everything from the current folder (where install.sh lives) into APP_DIR
  rsync -a \
    --exclude ".venv" \
    --exclude "db.sqlite3" \
    --exclude "staticfiles" \
    --exclude ".env" \
    "${SCRIPT_DIR}/" "${APP_DIR}/"
else
  log "Project already present at ${APP_DIR} (manage.py found). Skipping copy."
fi

cd "${APP_DIR}"

log "Creating Python virtualenv…"
if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi

log "Installing Python requirements…"
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

# --- Ensure .env.example exists (so fresh git clones always work) ---
if [ ! -f ".env.example" ]; then
  echo "[install] .env.example missing — creating a default template..."
  cat > .env.example <<'EOF'
DEBUG=0
ALLOWED_HOSTS=monitor.cymru-hosting.co.uk,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://monitor.cymru-hosting.co.uk
SECRET_KEY=
ENCRYPTION_KEY=
PTERO_BASE_URL=
PTERO_APPLICATION_API_KEY=
PTERO_CLIENT_API_KEY=
DISCORD_WEBHOOK_URL=
EOF
fi

# --- Create .env if it doesn't exist ---
if [ ! -f ".env" ]; then
  echo "[install] Creating/Updating .env…"
  cp .env.example .env
  chmod 600 .env
else
  echo "[install] .env already exists — leaving it unchanged."
fi

# SECRET_KEY (used by Django to sign cookies etc.)
if ! grep -qE '^SECRET_KEY=' .env || grep -q 'dev-only-change-me' .env; then
  DJ_SECRET="$(python - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
)"
  set_env_kv "SECRET_KEY" "${DJ_SECRET}" ".env"
fi

# ENCRYPTION_KEY (used to encrypt API keys in the DB)
if ! grep -qE '^ENCRYPTION_KEY=' .env || [[ -z "$(grep -E '^ENCRYPTION_KEY=' .env | cut -d= -f2-)" ]]; then
  ENC_KEY="$(python manage.py generate_encryption_key | tail -n 1)"
  set_env_kv "ENCRYPTION_KEY" "${ENC_KEY}" ".env"
fi

# Basic production defaults
set_env_kv "DEBUG" "0" ".env"
set_env_kv "ALLOWED_HOSTS" "${DOMAIN},localhost,127.0.0.1" ".env"

# Prompt for Pterodactyl details (optional - you can also set in /admin later).
log "Pterodactyl settings (you can leave blank and configure in /admin later)…"
prompt_default "Pterodactyl Panel URL (example: https://panel.example.com)" "" PTERO_URL
if [[ -n "${PTERO_URL}" ]]; then
  set_env_kv "PTERO_BASE_URL" "${PTERO_URL%/}" ".env"
fi

prompt_secret "Pterodactyl Application API key (input hidden)" PTERO_APP_KEY
if [[ -n "${PTERO_APP_KEY}" ]]; then
  set_env_kv "PTERO_APPLICATION_API_KEY" "${PTERO_APP_KEY}" ".env"
fi

prompt_secret "Pterodactyl Client API key (input hidden)" PTERO_CLIENT_KEY
if [[ -n "${PTERO_CLIENT_KEY}" ]]; then
  set_env_kv "PTERO_CLIENT_API_KEY" "${PTERO_CLIENT_KEY}" ".env"
fi

prompt_default "Discord webhook URL (optional)" "" DISCORD_URL
if [[ -n "${DISCORD_URL}" ]]; then
  set_env_kv "DISCORD_WEBHOOK_URL" "${DISCORD_URL}" ".env"
fi

# Permissions:
# - .env readable by root and www-data group (systemd runs as www-data)
chown root:${RUN_GROUP} .env
chmod 640 .env

log "Running database migrations + collectstatic…"
python manage.py migrate
python manage.py collectstatic --noinput

# Create sqlite DB file ownership (so www-data can write status updates)
if [[ -f "db.sqlite3" ]]; then
  chown ${RUN_USER}:${RUN_GROUP} db.sqlite3
fi
mkdir -p staticfiles
chown -R ${RUN_USER}:${RUN_GROUP} staticfiles

log "Create an admin user now (recommended)."
echo "You will be prompted for username/email/password."
echo "If you want to skip, press Ctrl+C, then run later:"
echo "  source ${APP_DIR}/.venv/bin/activate && python manage.py createsuperuser"
python manage.py createsuperuser || true

log "Installing systemd services…"
# Render systemd unit files with the chosen APP_DIR (if you changed it)
tmpdir="$(mktemp -d)"
sed "s|/opt/petrodactalgamemonitor|${APP_DIR}|g" deploy/systemd/gunicorn.service > "${tmpdir}/petrodactal-gunicorn.service"
sed "s|/opt/petrodactalgamemonitor|${APP_DIR}|g" deploy/systemd/poller.service  > "${tmpdir}/petrodactal-poller.service"
cp deploy/systemd/poller.timer "${tmpdir}/petrodactal-poller.timer"

install -m 0644 "${tmpdir}/petrodactal-gunicorn.service" /etc/systemd/system/petrodactal-gunicorn.service
install -m 0644 "${tmpdir}/petrodactal-poller.service"  /etc/systemd/system/petrodactal-poller.service
install -m 0644 "${tmpdir}/petrodactal-poller.timer"    /etc/systemd/system/petrodactal-poller.timer
rm -rf "${tmpdir}"

systemctl daemon-reload
systemctl enable --now petrodactal-gunicorn
systemctl enable --now petrodactal-poller.timer

log "Installing nginx site…"
# Render nginx config with DOMAIN + APP_DIR
ng_tmp="$(mktemp)"
sed -e "s/monitor\.cymru-hosting\.co\.uk/${DOMAIN}/g" \
    -e "s|/opt/petrodactalgamemonitor|${APP_DIR}|g" \
    deploy/nginx/site.conf > "${ng_tmp}"

install -m 0644 "${ng_tmp}" "/etc/nginx/sites-available/${DOMAIN}"
rm -f "${ng_tmp}"

ln -sf "/etc/nginx/sites-available/${DOMAIN}" "/etc/nginx/sites-enabled/${DOMAIN}"
# Optional: disable default site if present
if [[ -e /etc/nginx/sites-enabled/default ]]; then
  rm -f /etc/nginx/sites-enabled/default
fi

nginx -t
systemctl reload nginx

log "Optional TLS (HTTPS) with certbot?"
read -r -p "Install TLS certificate now with certbot? (y/N): " DO_TLS || true
DO_TLS="${DO_TLS:-N}"
if [[ "${DO_TLS}" =~ ^[Yy]$ ]]; then
  apt-get install -y certbot python3-certbot-nginx
  read -r -p "Email for Let's Encrypt notices: " LE_EMAIL
  if [[ -n "${LE_EMAIL}" ]]; then
    certbot --nginx -d "${DOMAIN}" -m "${LE_EMAIL}" --agree-tos --no-eff-email
    log "TLS installed. If you want Django to force HTTPS, set SECURE_SSL_REDIRECT=True in petrodactal/settings.py."
  else
    warn "No email provided; skipping certbot."
  fi
fi

log "Done!"
echo ""
echo "Panel should now be available at:"
echo "  http://${DOMAIN}/"
echo "Admin login:"
echo "  http://${DOMAIN}/admin/"
echo ""
echo "Tip: First sync (imports servers from Pterodactyl):"
echo "  sudo -u ${RUN_USER} ${APP_DIR}/.venv/bin/python ${APP_DIR}/manage.py poll_ptero --sync"
