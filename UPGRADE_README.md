# Petrodactal Upgrade Pack v1

This pack implements:

- Hide server **IP/port/identifier** from:
  - public pages
  - JSON API
  - Django admin

- Show **CPU%** and **RAM (MB)** from Pterodactyl resources endpoint.

- Clan admin shows a **clickable share link** (set `PUBLIC_BASE_URL` for a full URL).

- Adds a **daily inventory sync** systemd timer (`--sync` at 03:00 daily).

## Install (on the VPS)

1. Upload this zip to the VPS (e.g. `/root/petrodactal-upgrade-pack-v1.zip`)

2. Unzip over the project root:

   ```bash
   cd /opt/petrodactalgamemonitor
   sudo unzip -o /root/petrodactal-upgrade-pack-v1.zip
   sudo chmod +x upgrade.sh
   ```

3. Run the upgrade script:

   ```bash
   sudo bash upgrade.sh
   ```

4. Optional: add this to your `.env` for full share URLs:

   ```
   PUBLIC_BASE_URL=https://monitor.cymru-hosting.co.uk
   ```

## Verify

- Homepage: https://monitor.cymru-hosting.co.uk/
- API: https://monitor.cymru-hosting.co.uk/api/v1/servers/
- Admin → Clans → should show a "Public link"
