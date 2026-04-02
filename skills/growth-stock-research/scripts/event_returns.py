#!/usr/bin/env python3
"""Event-study style forward return analysis for growth stocks."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import datetime
from statistics import median


DEFAULT_WINDOWS = [1, 5, 20, 60, 120]


@dataclass(frozen=True)
class PriceRow:
    date: datetime
    close: float


@dataclass(frozen=True)
class EventRow:
    date: datetime
    stance: str
    reason: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a forward-return event study from dated events and price CSVs.")
    parser.add_argument("--prices", required=True, help="Price CSV with date and close columns")
    parser.add_argument("--events", required=True, help="Event CSV with date, stance, and reason")
    parser.add_argument("--benchmark", help="Optional benchmark price CSV")
    parser.add_argument(
        "--windows",
        nargs="+",
        type=int,
        default=DEFAULT_WINDOWS,
        help="Forward windows in trading days, default: 1 5 20 60 120",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    return parser.parse_args()


def load_prices(path: str) -> list[PriceRow]:
    rows: list[PriceRow] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            date_text = (raw.get("date") or "").strip()
            close_text = (raw.get("close") or "").strip()
            if not date_text or not close_text:
                continue
            rows.append(PriceRow(datetime.fromisoformat(date_text), float(close_text)))
    rows.sort(key=lambda item: item.date)
    if len(rows) < 30:
        raise ValueError(f"Need at least 30 price rows, got {len(rows)}")
    return rows


def load_events(path: str) -> list[EventRow]:
    rows: list[EventRow] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            date_text = (raw.get("date") or "").strip()
            if not date_text:
                continue
            rows.append(
                EventRow(
                    date=datetime.fromisoformat(date_text),
                    stance=(raw.get("stance") or "").strip().lower() or "unspecified",
                    reason=(raw.get("reason") or "").strip(),
                )
            )
    rows.sort(key=lambda item: item.date)
    if not rows:
        raise ValueError("No events found")
    return rows


def first_index_on_or_after(rows: list[PriceRow], event_date: datetime) -> int | None:
    for index, row in enumerate(rows):
        if row.date >= event_date:
            return index
    return None


def forward_return(rows: list[PriceRow], start_index: int, window: int) -> float | None:
    end_index = start_index + window
    if end_index >= len(rows):
        return None
    start_price = rows[start_index].close
    end_price = rows[end_index].close
    if start_price == 0:
        return None
    return (end_price / start_price) - 1.0


def summarize(values: list[float]) -> dict[str, float]:
    if not values:
        return {
            "count": 0,
            "mean": 0.0,
            "median": 0.0,
            "hit_rate": 0.0,
        }
    return {
        "count": len(values),
        "mean": sum(values) / len(values),
        "median": median(values),
        "hit_rate": sum(1 for value in values if value > 0) / len(values),
    }


def build_payload(
    prices: list[PriceRow],
    events: list[EventRow],
    benchmark: list[PriceRow] | None,
    windows: list[int],
) -> dict:
    event_results = []
    bucketed: dict[str, dict[int, list[float]]] = {}
    bucketed_relative: dict[str, dict[int, list[float]]] = {}

    for event in events:
        price_index = first_index_on_or_after(prices, event.date)
        if price_index is None:
            continue
        benchmark_index = first_index_on_or_after(benchmark, event.date) if benchmark else None
        by_window = {}

        for window in windows:
            abs_return = forward_return(prices, price_index, window)
            bench_return = forward_return(benchmark, benchmark_index, window) if benchmark and benchmark_index is not None else None
            rel_return = None if abs_return is None or bench_return is None else abs_return - bench_return
            by_window[str(window)] = {
                "absolute_return": abs_return,
                "benchmark_return": bench_return,
                "relative_return": rel_return,
            }
            if abs_return is not None:
                bucketed.setdefault(event.stance, {}).setdefault(window, []).append(abs_return)
            if rel_return is not None:
                bucketed_relative.setdefault(event.stance, {}).setdefault(window, []).append(rel_return)

        event_results.append(
            {
                "event_date": event.date.date().isoformat(),
                "effective_trade_date": prices[price_index].date.date().isoformat(),
                "stance": event.stance,
                "reason": event.reason,
                "windows": by_window,
            }
        )

    summaries = {}
    for stance, values_by_window in bucketed.items():
        summaries[stance] = {}
        for window, values in values_by_window.items():
            summary = summarize(values)
            rel_values = bucketed_relative.get(stance, {}).get(window, [])
            rel_summary = summarize(rel_values) if rel_values else None
            payload = {
                "absolute": summary,
            }
            if rel_summary:
                payload["relative"] = rel_summary
            summaries[stance][str(window)] = payload

    return {
        "event_study_version": "v1-forward-returns",
        "windows": windows,
        "event_count": len(event_results),
        "events": event_results,
        "summaries": summaries,
    }


def pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.2f}%"


def render_text(payload: dict) -> str:
    lines = [
        f"Event study version: {payload['event_study_version']}",
        f"Event count:         {payload['event_count']}",
        f"Windows:             {', '.join(str(item) for item in payload['windows'])}",
        "",
        "Summary by stance:",
    ]
    summaries = payload.get("summaries", {})
    if not summaries:
        lines.append("- No events had enough price history for the selected windows")
    for stance, window_map in summaries.items():
        lines.append(f"- {stance}:")
        for window, summary in window_map.items():
            abs_summary = summary["absolute"]
            text = (
                f"  {window}d abs mean {pct(abs_summary['mean'])}, "
                f"median {pct(abs_summary['median'])}, "
                f"hit rate {pct(abs_summary['hit_rate'])}, "
                f"n={abs_summary['count']}"
            )
            rel_summary = summary.get("relative")
            if rel_summary:
                text += (
                    f" | rel mean {pct(rel_summary['mean'])}, "
                    f"median {pct(rel_summary['median'])}"
                )
            lines.append(text)
    if payload["events"]:
        lines.extend(["", "Events:"])
        for event in payload["events"]:
            lines.append(
                f"- {event['event_date']} ({event['stance']}) -> trade date {event['effective_trade_date']}: "
                f"{event['reason'] or 'n/a'}"
            )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    prices = load_prices(args.prices)
    events = load_events(args.events)
    benchmark = load_prices(args.benchmark) if args.benchmark else None
    payload = build_payload(prices, events, benchmark, sorted(set(args.windows)))
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(render_text(payload))


if __name__ == "__main__":
    main()
