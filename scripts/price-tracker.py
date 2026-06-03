#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/opt/data/Cosmos")
CONFIG = ROOT / "workflows" / "price-tracker.yaml"
LOG_DIR = ROOT / "logs" / "price-tracker"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def _cast(raw: str) -> object:
    low = raw.lower()
    if low in {"true", "yes"}:
        return True
    if low in {"false", "no"}:
        return False
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1]
        if not inner.strip():
            return []
        parts = []
        for entry in inner.split(","):
            entry = entry.strip().strip("\"'")
            parts.append(_cast(entry))
        return parts
    if low in {"null", "none", "~"}:
        return None
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        pass
    return raw


def read_watchlist(path: Path) -> list[dict]:
    text = path.read_text(errors="ignore")
    items: list[dict] = []
    current: dict | None = None
    active = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not raw.startswith("  ") and line.startswith("watchlist:"):
            active = True
            current = None
            continue
        if active and line == "rules:":
            active = False
            continue
        if not active:
            continue
        if line.startswith("- "):
            current = {}
            kv = line[2:].strip()
            k, _, v = kv.partition(":")
            if k:
                current[k.strip()] = _cast(v.strip().strip('"'))
            items.append(current)
        elif current is not None and raw.startswith("    ") and ":" in line:
            k, _, v = line.partition(":")
            try:
                current[k.strip()] = float(v.strip())
            except ValueError:
                current[k.strip()] = _cast(v.strip().strip('"'))
    return items


def log(item, price, status, currency="USD", note=""):
    slug = re.sub(r"[^a-z0-9]+", "-", (item.get("name") or "unknown").lower()).strip("-") or "unknown"
    rec = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "name": item.get("name"),
        "url": item.get("url"),
        "price": price,
        "currency": currency,
        "status": status,
        "source": "direct",
    }
    if note:
        rec["note"] = note
    with (LOG_DIR / f"{slug}.jsonl").open("a") as f:
        f.write(json.dumps(rec, default=str) + "\n")


def log_browser(item, price, currency="USD", note=""):
    slug = re.sub(r"[^a-z0-9]+", "-", (item.get("name") or "unknown").lower()).strip("-") or "unknown"
    rec = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "name": item.get("name"),
        "url": item.get("url"),
        "price": price,
        "currency": currency,
        "status": "ok",
        "source": "browser_fallback",
    }
    if note:
        rec["note"] = note
    with (LOG_DIR / f"{slug}.jsonl").open("a") as f:
        f.write(json.dumps(rec, default=str) + "\n")


def fetch(url: str):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "CosmosPriceTracker/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "ignore")


def extract_price(text: str):
    matches = re.findall(r'[€$£¥₹]\s*([0-9,]+(?:\.[0-9]{1,4})?)', text)
    if not matches:
        return None
    for m in matches:
        p = float(m.replace(",", ""))
        if p > 0:
            return p, f"${p:.2f}"
    p = float(matches[0].replace(",", ""))
    return p, f"${p:.2f}"


if __name__ == "__main__":
    items = read_watchlist(CONFIG)
    if not items:
        print(json.dumps({"checked": 0, "alerts": [], "info": "watchlist empty"}, indent=2))
        sys.exit(0)

    alerts = []
    for item in items:
        url = item.get("url")
        if not url:
            continue

        used_browser = False
        price = None
        note = ""

        # Primary: direct HTTP text fetch. Not all sites allow it.
        try:
            text = fetch(url)
            found = extract_price(text)
            if found:
                price, note = found
                log(item, price, "ok", item.get("currency") or "USD", "direct")
            else:
                log(item, None, "price_not_found", item.get("currency") or "USD")
        except Exception as exc:
            log(item, None, f"fetch_error:{exc.__class__.__name__}", item.get("currency") or "USD", str(exc))

        # Fallback: when UA blocks us, refetch via curl binary which frequently succeeds where
        # stdlib urllib fails on bot-protected product pages.
        if price is None:
            try:
                import subprocess
                p = subprocess.run(
                    ["curl", "-sS", "-L", "--max-time", "30", "-A",
                     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                     url],
                    text=True,
                    capture_output=True,
                    timeout=35,
                )
                if p.returncode == 0:
                    found = extract_price(p.stdout)
                    if found:
                        price, note = found
                        used_browser = True
                        log(item, price, "ok", item.get("currency") or "USD", "curl_fallback")
            except Exception as exc:
                note = f"curl_failed:{exc.__class__.__name__}"

        alerts.append(
            {
                "name": item.get("name"),
                "url": url,
                "price": price,
                "currency": item.get("currency") or "USD",
                "note": note or "ok",
                "alert": False,
                "source": "browser_fallback" if used_browser else "direct",
            }
        )

    print(json.dumps({"checked": len(items), "alerts": alerts}, indent=2, default=str))
    sys.exit(0)
