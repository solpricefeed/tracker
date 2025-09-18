#!/usr/bin/env python3
import json
import requests
from datetime import datetime, timezone

# Hardcoded IFTTT URL with your key and event
IFTTT_URL = "https://maker.ifttt.com/trigger/sol_price_log/with/key/cLcVxJK2s0I_FF-5UNwjNq"

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "solpricefeed-bot/1.0 (https://twitter.com/solpricefeed)"
}

def now_utc_hour_iso() -> str:
    """UTC timestamp rounded down to the hour in ISO format."""
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
    """Send a row to IFTTT Webhooks (Value1, Value2, Value3) via GET."""
    params = {
        "value1": timestamp_iso,
        "value2": f"{price:.2f}",
        "value3": value3
    }
    resp = requests.get(IFTTT_URL, params=params, timeout=15)
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        raise SystemExit(f"IFTTT GET failed: {e}\nResponse: {resp.text}") from e
    print("Logged row:", json.dumps(params))

def main():
    ts = now_utc_hour_iso()
    price = get_sol_price_usd()
    post_to_ifttt(ts, price, value3="")

if __name__ == "__main__":
    main()
