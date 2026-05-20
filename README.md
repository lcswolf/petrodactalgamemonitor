# Petrodactal Monitor

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/lcswolf/petrodactalgamemonitor)

**A modern Pterodactyl Game Server Status Dashboard** with beautiful UI, real-time monitoring, one-click updates, embed support, and more.

## Features

- Modern dark UI with live search, filtering, and copy buttons
- Server detail modal
- Embed buttons with ready iframe code
- Clan banner support
- One-click update system with version checking
- Custom dark Admin theme
- Demo Mode with fake data
- Full Docker + Prometheus + Grafana support
- Game query plugins (Minecraft)
- Comprehensive tests
- Easy domain/subdomain setup

## Installation

### 1. One-Click Deploy (Recommended)
Click the Deploy button above.

### 2. Docker
```bash
git clone https://github.com/lcswolf/petrodactalgamemonitor.git
cd petrodactalgamemonitor
cp .env.example .env
# Edit .env
 docker compose up -d --build
```

## Demo Mode
Set `DEMO_MODE=True` in `.env` and run `python manage.py create_demo_data`

## Embed
Click the "Embed" button on the dashboard or use `?embed=true`

## Post-Install Checklist
- Configure Pterodactyl API keys in Admin
- Run `python manage.py poll_ptero --sync`
- Set up clan banners (optional)

## Troubleshooting
See the Troubleshooting section for common issues.

## Release Notes
See detailed changelog in the full README.

---

*Full documentation, screenshots, detailed setup, troubleshooting, and roadmap are included below.*