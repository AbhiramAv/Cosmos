#!/usr/bin/env bash
set -euo pipefail

DASH_ROOT="/opt/data/Cosmos/dashboard"
DASH_DIR="/opt/data/Cosmos/dashboard/dist"
PORT="8787"
LOG_DIR="/opt/data/logs/cosmos-dashboard"
URL_FILE="/opt/data/Cosmos/dashboard/public-url.txt"
CLOUDFLARED="/opt/data/bin/cloudflared"
mkdir -p "$LOG_DIR"

# Build React dashboard if the dist bundle does not exist yet.
if [ ! -f "$DASH_DIR/index.html" ]; then
  cd "$DASH_ROOT"
  npm install >>"$LOG_DIR/npm-install.log" 2>&1 || true
  npm run build >>"$LOG_DIR/build.log" 2>&1 || true
fi

# Refresh live metrics first so the dashboard never boots stale.
/opt/data/scripts/cosmos-dashboard-collector.py >>"$LOG_DIR/collector.log" 2>&1 || true

# Start local dashboard if localhost is not responding.
if ! curl -fsS "http://127.0.0.1:${PORT}/" >/dev/null 2>&1; then
  pkill -f "python3 -m http.server ${PORT}" >/dev/null 2>&1 || true
  cd "$DASH_DIR"
  nohup python3 -m http.server "$PORT" --bind 0.0.0.0 >>"$LOG_DIR/server.log" 2>&1 &
  sleep 2
fi

# Prefer Cloudflare quick tunnels over localtunnel because localtunnel shows an interstitial
# in real browsers and can block dashboard JSON fetches on iPad/Safari.
if [ -x "$CLOUDFLARED" ]; then
  CURRENT_URL=""
  if [ -f "$URL_FILE" ]; then
    CURRENT_URL="$(tr -d '\n' < "$URL_FILE")"
  fi
  if [ -n "$CURRENT_URL" ] && curl -fsS --max-time 12 "$CURRENT_URL/" | grep -q 'Cosmos Mission Control'; then
    exit 0
  fi

  pkill -f "cloudflared tunnel --url http://127.0.0.1:${PORT}" >/dev/null 2>&1 || true
  : > "$LOG_DIR/cloudflared.log"
  nohup "$CLOUDFLARED" tunnel --url "http://127.0.0.1:${PORT}" --no-autoupdate >>"$LOG_DIR/cloudflared.log" 2>&1 &
  for _ in $(seq 1 60); do
    URL="$(grep -Eo 'https://[-a-zA-Z0-9]+\.trycloudflare\.com' "$LOG_DIR/cloudflared.log" | tail -1 || true)"
    if [ -n "$URL" ]; then
      HOST="${URL#https://}"
      if getent hosts "$HOST" >/dev/null 2>&1 && curl -fsS --max-time 12 "$URL/" | grep -q 'Cosmos Mission Control'; then
        printf '%s\n' "$URL" > "$URL_FILE"
        break
      fi
    fi
    sleep 2
  done
  exit 0
fi

# Fallback only if cloudflared is unavailable.
if ! curl -fsS --max-time 12 -H 'localtunnel-skip-browser-warning: true' "https://ram-cosmos-dashboard.loca.lt/" | grep -q 'Cosmos Mission Control'; then
  pkill -f "localtunnel --port ${PORT} --subdomain ram-cosmos-dashboard" >/dev/null 2>&1 || true
  cd "$DASH_DIR"
  nohup npx --yes localtunnel --port "$PORT" --subdomain "ram-cosmos-dashboard" >>"$LOG_DIR/localtunnel.log" 2>&1 &
fi

# Stay silent on success so cron does not spam Telegram.
exit 0
