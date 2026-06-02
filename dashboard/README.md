# Cosmos Dashboard

Static MVP dashboard for Cosmos Agentic OS.

## Public free link

```text
https://ram-cosmos-dashboard.loca.lt/
```

This is hosted for free using localtunnel pointed at the local dashboard server. A Hermes cron watchdog keeps the local server/tunnel alive every 10 minutes.

## Run locally

```bash
cd /opt/data/Cosmos/dashboard
python3 -m http.server 8787 --bind 0.0.0.0
```

Then open:

```text
http://127.0.0.1:8787
```

## Current status

- Static HTML/CSS/JS
- Data source: `dashboard/data/cosmos.json`
- No secrets
- No Supabase dependency yet
- Free public tunnel: localtunnel
- Watchdog script: `/opt/data/scripts/cosmos-dashboard-watchdog.sh`
