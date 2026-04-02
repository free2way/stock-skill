#!/usr/bin/env python3
"""Convert dated thesis events into a backtest-ready signals CSV."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime


STANCE_TO_SIGNAL = {
    "bullish": 1,
    "bearish": 0,
    "neutral": 0,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a signal CSV from an events CSV.")
    parser.add_argument("--events", required=True, help="CSV with date, stance, reason")
    parser.add_argument("--output", required=True, help="Output signal CSV path")
    return parser.parse_args()


def normalize_date(value: str) -> str:
    return datetime.fromisoformat(value.strip()).date().isoformat()


def read_events(path: str) -> list[dict[str, str]]:
    events: list[dict[str, str]] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            date_text = (raw.get("date") or "").strip()
            stance_text = (raw.get("stance") or "").strip().lower()
            reason_text = (raw.get("reason") or "").strip()
            if not date_text or not stance_text:
                continue
            if stance_text not in STANCE_TO_SIGNAL:
                raise ValueError(f"Unsupported stance: {stance_text}")
            events.append(
                {
                    "date": normalize_date(date_text),
                    "stance": stance_text,
                    "reason": reason_text,
                }
            )
    events.sort(key=lambda row: row["date"])
    if not events:
        raise ValueError("No events found")
    return events


def write_signals(path: str, events: list[dict[str, str]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "signal", "source_reason"])
        writer.writeheader()
        for event in events:
            writer.writerow(
                {
                    "date": event["date"],
                    "signal": STANCE_TO_SIGNAL[event["stance"]],
                    "source_reason": event["reason"],
                }
            )


def main() -> None:
    args = parse_args()
    events = read_events(args.events)
    write_signals(args.output, events)
    print(f"Wrote {len(events)} signals to {args.output}")


if __name__ == "__main__":
    main()
