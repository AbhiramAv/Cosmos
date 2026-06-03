#!/usr/bin/env python3
"""BullBearian price + headline collector."""
from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path("/opt/data/Cosmos/finance")
LOG = ROOT / "logs" / "prices.jsonl"
ROOT.mkdir(parents=True, exist_ok=True)
LOG.parent.mkdir(parents=True, exist_ok=True)
CACHE: dict[str, tuple[dict, float]] = {}
CACHE_TTL = 240


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def now_ts() -> float:
    return datetime.now(timezone.utc).timestamp()


def save(rec: dict) -> None:
    with LOG.open("a") as f:
        f.write(json.dumps(rec, default=str) + "\n")


def get_cached(key: str) -> dict | None:
    hit = CACHE.get(key)
    if not hit:
        return None
    rec, ts = hit
    if now_ts() - ts > CACHE_TTL:
        return None
    return rec


def set_cached(key: str, rec: dict) -> None:
    CACHE[key] = (rec, now_ts())


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "ignore")


def map_symbol(sym: str) -> str:
    s = sym.strip().upper()
    crypto = ["BTC", "ETH", "DOGE", "SHIB", "XRP", "SOL", "ADA", "AVAX", "DOT", "LINK"]
    if s in crypto:
        return s + "-USD"
    return s


def quote_yahoo(sym: str) -> dict:
    url = f"https://finance.yahoo.com/quote/{map_symbol(sym)}"
    text = fetch(url)
    out = {"symbol": sym, "source": "yahoo", "currency": "USD", "ts": now_iso()}
    m = re.search(r"\"currentPrice\":\s*\{\"raw\":\s*([0-9.]+)", text)
    if not m:
        m = re.search(r"\"regularMarketPrice\":\s*\{\"raw\":\s*([0-9.]+)", text)
    out["price"] = float(m.group(1)) if m else None
    mn = re.search(r"\"fiftyTwoWeekLow\":\s*\{\"raw\":\s*([0-9.]+)", text)
    mx = re.search(r"\"fiftyTwoWeekHigh\":\s*\{\"raw\":\s*([0-9.]+)", text)
    out["low52"] = float(mn.group(1)) if mn else None
    out["high52"] = float(mx.group(1)) if mx else None
    return out


def quote_coingecko(sym: str) -> dict:
    slug = map_symbol(sym).replace("-USD", "").lower()
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={slug}&vs_currencies=usd"
    text = fetch(url)
    data = json.loads(text or "{}")
    price = ((data.get(slug) or {}).get("usd"))
    return {"symbol": sym, "price": price, "source": "coingecko", "currency": "USD", "ts": now_iso()}


def quote(sym: str) -> dict:
    cached = get_cached(sym)
    if cached:
        return cached
    last_err = None
    src = "yahoo"
    for fn in (quote_yahoo, quote_coingecko):
        try:
            rec = fn(sym)
            rec["source"] = src = fn.__name__.replace("quote_", "")
            set_cached(sym, rec)
            return rec
        except Exception as exc:
            last_err = exc
    fallback = {"symbol": sym, "price": None, "source": "none", "currency": "USD", "ts": now_iso(), "error": repr(last_err)}
    set_cached(sym, fallback)
    return fallback


def collect_news(sym: str, count: int = 3) -> list[dict]:
    url = f"https://finance.yahoo.com/quote/{map_symbol(sym)}/news"
    try:
        text = fetch(url)
        titles = re.findall(r"<h3[^>]*>(.*?)</h3>", text, re.S)
        out = []
        for t in titles[:count]:
            clean = re.sub(r"<.*?>", "", t).strip()
            if clean:
                out.append({"title": clean})
        return out
    except Exception:
        return []


def main() -> int:
    raw_eq = os.environ.get("BB_EQUITIES", "")
    raw_cr = os.environ.get("BB_CRYPTO", "")
    equities = [s for s in raw_eq.split(",") if s.strip()]
    equities += ["NVDA", "GOOGL", "PLTR", "RKLB", "ASTS", "LUNR", "RGTI", "QUBT"]
    crypto = [s for s in raw_cr.split(",") if s.strip()]
    crypto += ["BTC", "ETH", "DOGE", "SHIB", "XRP"]
    seen = sorted(set(equities + crypto))
    rec: dict = {"ts": now_iso(), "quotes": [], "alerts": [], "news": []}
    for i, sym in enumerate(seen, 1):
        q = quote(sym)
        rec["quotes"].append(q)
        if i % 4 == 0:
            time.sleep(1.0)
    for sym in seen[:3]:
        rec["news"].append({"symbol": sym, "headlines": collect_news(sym)})
    save(rec)
    print(json.dumps(rec, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
