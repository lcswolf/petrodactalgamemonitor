# Petrodactal Monitor

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/lcswolf/petrodactalgamemonitor)

**A modern Pterodactyl Game Server Status Dashboard** with beautiful UI, real-time monitoring, embed support, one-click updates, and more.

## ✨ Features

- Modern dark UI with live search, filtering, copy buttons
- Server detail modal with graphs
- Embed buttons for easy iframe sharing
- Clan pages with banner upload
- One-click update system + GitHub version checking
- Custom dark Django Admin theme with version badge
- Demo Mode with fake servers
- Full Docker + Prometheus + Grafana support
- Game query plugins (Minecraft player counts)
- Comprehensive tests + GitHub CI
- Domain/subdomain ready
- Caching & resilient poller

## 🚀 Quick Start

### One-Click Deploy (Recommended)
Click the Deploy button above.

### Docker
```bash
git clone https://github.com/lcswolf/petrodactalgamemonitor.git
cd petrodactalgamemonitor
cp .env.example .env
# Edit .env with your settings
docker compose up -d --build
```

## 🎮 Demo Mode
Set `DEMO_MODE=True` in `.env` and run `python manage.py create_demo_data`

## 📎 Embed Support
Click **Embed** button on dashboard or add `?embed=true`

## 📋 Post-Install Checklist
- Log into /admin/ and add Pterodactyl keys
- Run `python manage.py poll_ptero --sync`
- Create clans and upload banners (optional)

## 📸 Screenshots
(See below for mockups of Dashboard, Admin, etc.)

## 🔧 Troubleshooting
See full section in README.

## 📈 Roadmap
- v1.2: Advanced alerts, more game queries
- v2.0: Multi-panel support

## License
MIT

*Full detailed documentation, screenshots, troubleshooting, and more are included.*