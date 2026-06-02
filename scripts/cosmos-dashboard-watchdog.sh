#!/usr/bin/env bash
set -euo pipefail

DASH_DIR="/opt/data/Cosmos/dashboard"
PORT="8787"
SUBDOMAIN="ram-cosmos-dashboard"
LOG_DIR="/opt/data/logs/cosmos-dashboard"
mkdir -p "$LOG_DIR"

# Refresh live metrics first so the dashboard never boots stale.
/opt/data/scripts/cosmos-dashboard-collector.py >>"$LOG_DIR/collector.log" 2>&1 || true

# Start local dashboard if localhost is not responding.
if ! curl -fsS "http://127.0.0.1:${PORT}/" >/dev/null 2>&1; then
  pkill -f "python3 -m http.server ${PORT}" >/dev/null 2>&1 || true
  cd "$DASH_DIR"
  nohup python3 -m http.server "$PORT" --bind 0.0.0.0 >>"$LOG_DIR/server.log" 2>&1 &
  sleep 2
fi

# Start/refresh localtunnel if public URL is not serving the live Cosmos dashboard.
if ! python3 - <<'PY' >/dev/null 2>&1
import urllib.request, sys
url='https://ram-cosmos-dashboard.loca.lt/'
try:
    data=urllib.request.urlopen(url, timeout=10).read(2000).decode('utf-8','ignore')
    sys.exit(0 if 'Cosmos Live Mission Control' in data else 1)
except Exception:
    sys.exit(1)
PY
then
  pkill -f "localtunnel --port ${PORT} --subdomain ${SUBDOMAIN}" >/dev/null 2>&1 || true
  cd "$DASH_DIR"
  nohup npx --yes localtunnel --port "$PORT" --subdomain "$SUBDOMAIN" >>"$LOG_DIR/localtunnel.log" 2>&1 &
fi

# Stay silent on success so cron does not spam Telegram.
exit 0
