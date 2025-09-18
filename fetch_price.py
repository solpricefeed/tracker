#!/usr/bin/env python3
import os
import time
import json
import requests
from datetime import datetime, timezone

IFTTT_KEY   = os.environ.get("IFTTT_KEY")          # put your key in repo secrets
EVENT_NAME  = os.environ.get("IFTTT_EVENT", "sol_price_log")

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "solpricefeed-bot/1.0 (https://twitter.com/solpricefeed)"
}

def now_utc_hour_iso() -> str:
    """UTC timestamp rounded down to the hour in ISO format (no Z)."""
    ts = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    return ts.strftime("%Y-%m-%d %H:%M:%S")

def get_sol_price_usd() -> float:
    """Fetch current SOL price (USD) from CoinGecko."""
    params = {"ids": "solana", "vs_currencies": "usd"}
    r = requests.get(COINGECKO_URL, params=params, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json()
    return float(data["solana"]["usd"])

def post_to_ifttt(timestamp_iso: str, price: float, value3: str = ""):
    """Send a row to IFTTT Webhooks (Value1, Value2, Value3)."""
    url = f"https://maker.ifttt.com/trigger/{EVENT_NAME}/json/with/key/{IFTTT_KEY}"
    payload = {"value1": timestamp_iso, "value2": f"{price:.2f}", "value3": value3}
    resp = requests.post(url, json=payload, timeout=15)
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        # helpful logging for IFTTT/CG errors
        raise SystemExit(f"IFTTT POST failed: {e}\nResponse: {resp.text}") from e
    print("Logged row:", json.dumps(payload))

def main():
    if not IFTTT_KEY:
        raise SystemExit("Missing IFTTT_KEY env var")

    ts = now_utc_hour_iso()
    price = get_sol_price_usd()

    # We leave Value3 blank because your Sheet column C calculates hourly change.
    post_to_ifttt(ts, price, value3="")

if __name__ == "__main__":
    main()
