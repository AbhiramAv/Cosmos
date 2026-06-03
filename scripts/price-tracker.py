#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path("/opt/data/Cosmos")
CONFIG = ROOT / "workflows" / "price-tracker.yaml"
LOG_DIR = ROOT / "logs" / "price-tracker"
LOG_DIR.mkdir(parents=True, exist_ok=True)


class SimpleYAML:
    def __init__(self):
        self.data: dict[str, object] = {}

    def load(self, path: Path):
        target = self.data
        for raw in path.read_text(errors="ignore").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or line == "---":
                continue
            indent = len(raw) - len(raw.lstrip())
            key, sep, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val == "" and sep == ":":
                target[key] = {}
                continue
            if val == "" and not line.endswith(":"):
                continue
            parsed = _cast(val)
            if key:
                target[key] = parsed


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
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "name": item.get("name"),
        "url": item.get("url"),
        "price": price,
        "currency": currency,
        "status": status,
    }
    if note:
        entry["note"] = note
    with (LOG_DIR / f"{slug}.jsonl").open("a") as f:
        f.write(json.dumps(entry, default=str) + "\n")


def fetch(url: str):
    req = Request(url, headers={"User-Agent": "CosmosPriceTracker/1.0"})
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "ignore")


def extract_price(text: str):
    m = re.search(r'[€$£¥₹]\s*([0-9,]+(?:\.[0-9]{1,4})?)', text)
    if not m:
        return None
    return float(m.group(1).replace(",", "")), m.group(0)


def main():
    items = read_watchlist(CONFIG)
    alerts: list[dict] = []
    for item in items:
        url = item.get("url")
        if not url:
            continue
        try:
            text = fetch(url)
        except Exception as exc:
            log(item, None, f"fetch_error:{exc.__class__.__name__}")
            continue
        found = extract_price(text)
        if not found:
            log(item, None, "price_not_found")
            continue
        price, _ = found
        min_p = item.get("min_price")
        max_p = item.get("max_price")
        note = "ok"
        alert = False
        if max_p is not None and price > float(max_p):
            alert, note = True, "above max"
        if min_p is not None and price < float(min_p):
            alert, note = True, "below min"
        log(item, price, "ok", item.get("currency") or "USD", note)
        alerts.append(
            {
                "name": item.get("name"),
                "url": url,
                "price": price,
                "currency": item.get("currency") or "USD",
                "note": note,
                "alert": alert,
            }
        )
    print(json.dumps({"checked": len(items), "alerts": alerts}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
