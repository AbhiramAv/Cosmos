# Cosmos Dashboard

Modern React/Vite Mission Control dashboard for Cosmos Agentic OS.

## Public free link

The current no-interstitial Cloudflare quick tunnel URL is stored locally at:

```text
dashboard/public-url.txt
```

Current live URL:

```text
https://ent-tool-especially-based.trycloudflare.com/
```

Cloudflare quick tunnels are free and avoid the localtunnel browser warning screen. They are not permanent URLs; if the tunnel restarts, the watchdog refreshes `public-url.txt`.

## Frontend stack

- React
- Vite
- Recharts
- Lucide icons
- Responsive CSS tuned for phone, iPad/tablet, laptop, and desktop breakpoints

Source files:

```text
dashboard/index.html
dashboard/src/main.jsx
dashboard/src/styles.css
dashboard/package.json
dashboard/vite.config.ts
```

Production build:

```text
dashboard/dist/
```

`dist/` is generated and intentionally gitignored. The watchdog will build it if missing.

## Live telemetry

The dashboard reads real local telemetry from:

- `/opt/data/state.db` — Hermes sessions, token counts, tool calls, API call counts, cost status
- `/opt/data/cron/jobs.json` — cron registry
- `/opt/data/logs/` — gateway/agent/error log health
- `/opt/data/Cosmos/.git` — Git status and latest commit
- local process table — dashboard/localtunnel process health
- `/opt/data/.env` key names only — provider credential presence without exposing values

Generated data files:

```text
dashboard/data/live.json
dashboard/dist/data/live.json
```

Collector script:

```text
/opt/data/scripts/cosmos-dashboard-collector.py
```

Cron job:

```text
Cosmos dashboard live metrics collector — every 1 minute
```

Browser refresh:

```text
every 20 seconds
```

## What is intentionally not guessed

Provider-specific subscription resets and remaining message quotas are not available from local Hermes session DB. The dashboard labels those as not connected instead of fabricating numbers. To make them real, Cosmos needs provider-specific quota integrations or authenticated browser/OAuth/API access for each provider.

## Run locally

```bash
cd /opt/data/Cosmos/dashboard
npm install
npm run build
cd dist
python3 -m http.server 8787 --bind 0.0.0.0
```

Then open:

```text
http://127.0.0.1:8787
```

## Current status

- React/Vite live dashboard
- Responsive layout for iPad and all major screen sizes
- Data source: `dashboard/data/live.json` / `dashboard/dist/data/live.json`
- Collector refresh: every 1 minute
- Browser refresh: every 20 seconds
- CEO/current-session panel with used / total / remaining context math
- OpenAI/Codex usage populated from local Hermes sessions now
- Full cron registry: name, purpose, schedule, script, last run, next run, status
- Agent roster: CEO, specialist sub-agent roles, assigned/unassigned work, active session IDs
- Kanban board wired to `/opt/data/kanban.db` with To do / Doing / Blocked / Done columns
- Capacity cards show used / remaining / total for context, weekly observed tokens, OpenAI observed usage, and disk
- No secrets in dashboard data
- No Supabase dependency yet
- Free public tunnel: localtunnel
- Watchdog script: `/opt/data/scripts/cosmos-dashboard-watchdog.sh`
