#!/usr/bin/env python3
"""Fetch daily price history for a U.S. stock and write a local CSV.

The script first tries Stooq's daily CSV endpoint. If that source has no data
for the requested ticker, it falls back to Yahoo Finance's chart API.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import UTC, datetime, timedelta
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download price history to CSV.")
    parser.add_argument("--ticker", required=True, help="Ticker symbol, e.g. NBIS")
    parser.add_argument("--years", type=int, default=5, help="Approximate years of daily data")
    parser.add_argument("--output", required=True, help="Output CSV path")
    return parser.parse_args()


def parse_stooq_csv(text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(text.splitlines())
    rows: list[dict[str, str]] = []
    for raw in reader:
        if not raw:
            continue
        date_text = (raw.get("Date") or "").strip()
        close_text = (raw.get("Close") or "").strip()
        if not date_text or close_text in {"", "N/D"}:
            continue
        rows.append(
            {
                "date": date_text,
                "open": (raw.get("Open") or "").strip(),
                "high": (raw.get("High") or "").strip(),
                "low": (raw.get("Low") or "").strip(),
                "close": close_text,
                "volume": (raw.get("Volume") or "").strip(),
            }
        )
    rows.sort(key=lambda row: row["date"])
    return rows


def trim_to_years(rows: list[dict[str, str]], years: int) -> list[dict[str, str]]:
    if not rows:
        return rows
    end_date = datetime.fromisoformat(rows[-1]["date"]).replace(tzinfo=UTC)
    cutoff = end_date - timedelta(days=365 * years)
    return [row for row in rows if datetime.fromisoformat(row["date"]).replace(tzinfo=UTC) >= cutoff]


def fetch_csv_text(ticker: str) -> str:
    normalized = ticker.strip().lower()
    if not normalized:
        raise ValueError("Ticker must not be empty")
    url = f"https://stooq.com/q/d/l/?s={normalized}.us&i=d"
    with urlopen(url, timeout=20) as response:
        return response.read().decode("utf-8")


def parse_yahoo_chart(payload: str) -> list[dict[str, str]]:
    document = json.loads(payload)
    result = (((document.get("chart") or {}).get("result")) or [None])[0]
    if not result:
        return []

    timestamps = result.get("timestamp") or []
    indicators = ((result.get("indicators") or {}).get("quote") or [None])[0] or {}
    opens = indicators.get("open") or []
    highs = indicators.get("high") or []
    lows = indicators.get("low") or []
    closes = indicators.get("close") or []
    volumes = indicators.get("volume") or []

    rows: list[dict[str, str]] = []
    for index, timestamp in enumerate(timestamps):
        close_value = closes[index] if index < len(closes) else None
        if close_value is None:
            continue
        dt = datetime.fromtimestamp(timestamp, tz=UTC).date().isoformat()
        rows.append(
            {
                "date": dt,
                "open": "" if index >= len(opens) or opens[index] is None else f"{opens[index]}",
                "high": "" if index >= len(highs) or highs[index] is None else f"{highs[index]}",
                "low": "" if index >= len(lows) or lows[index] is None else f"{lows[index]}",
                "close": f"{close_value}",
                "volume": "" if index >= len(volumes) or volumes[index] is None else f"{volumes[index]}",
            }
        )
    rows.sort(key=lambda row: row["date"])
    return rows


def fetch_yahoo_rows(ticker: str) -> list[dict[str, str]]:
    end = int(datetime.now(tz=UTC).timestamp())
    start = int((datetime.now(tz=UTC) - timedelta(days=365 * 10)).timestamp())
    query = urlencode(
        {
            "period1": start,
            "period2": end,
            "interval": "1d",
            "includeAdjustedClose": "true",
            "events": "history",
        }
    )
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?{query}"
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=20) as response:
        payload = response.read().decode("utf-8")
    return parse_yahoo_chart(payload)


def write_rows(path: str, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError("No rows downloaded")
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    try:
        text = fetch_csv_text(args.ticker)
    except HTTPError as exc:
        raise SystemExit(f"HTTP error while downloading data: {exc.code}") from exc
    except URLError as exc:
        raise SystemExit(f"Network error while downloading data: {exc.reason}") from exc

    rows = parse_stooq_csv(text)
    if not rows:
        try:
            rows = fetch_yahoo_rows(args.ticker)
        except HTTPError as exc:
            raise SystemExit(f"HTTP error while downloading Yahoo data: {exc.code}") from exc
        except URLError as exc:
            raise SystemExit(f"Network error while downloading Yahoo data: {exc.reason}") from exc
    rows = trim_to_years(rows, args.years)
    write_rows(args.output, rows)
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
