# Cosmos Dashboard

Static MVP dashboard for Cosmos Agentic OS.

## Run locally

```bash
cd /opt/data/Cosmos/dashboard
python3 -m http.server 8787 --bind 0.0.0.0
```

Then open:

```text
http://127.0.0.1:8787
```

If running on a remote server, the dashboard needs a secure tunnel, reverse proxy, or hosted deployment before Ram can open it from a phone/browser.

## Current status

- Static HTML/CSS/JS
- Data source: `dashboard/data/cosmos.json`
- No secrets
- No Supabase dependency yet
- Ready to become a live dashboard later
