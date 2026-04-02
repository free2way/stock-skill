#!/usr/bin/env python3
"""Relative-strength analysis for a stock versus a benchmark."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import datetime


DEFAULT_WINDOWS = [20, 60, 120, 252]


@dataclass(frozen=True)
class PriceRow:
    date: datetime
    close: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Measure stock performance relative to a benchmark.")
    parser.add_argument("--prices", required=True, help="Stock price CSV with date and close columns")
    parser.add_argument("--benchmark", required=True, help="Benchmark price CSV with date and close columns")
    parser.add_argument(
        "--windows",
        nargs="+",
        type=int,
        default=DEFAULT_WINDOWS,
        help="Lookback windows in trading days, default: 20 60 120 252",
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
    rows.sort(key=lambda row: row.date)
    if len(rows) < 30:
        raise ValueError(f"Need at least 30 price rows, got {len(rows)}")
    return rows


def to_close_map(rows: list[PriceRow]) -> dict[str, float]:
    return {row.date.date().isoformat(): row.close for row in rows}


def aligned_series(stock: list[PriceRow], benchmark: list[PriceRow]) -> list[tuple[str, float, float]]:
    bench_map = to_close_map(benchmark)
    output = []
    for row in stock:
        key = row.date.date().isoformat()
        if key in bench_map:
            output.append((key, row.close, bench_map[key]))
    if len(output) < 30:
        raise ValueError("Need at least 30 aligned rows between stock and benchmark")
    return output


def return_over_window(series: list[tuple[str, float, float]], window: int) -> dict[str, float | str] | None:
    if len(series) <= window:
        return None
    start_date, start_stock, start_bench = series[-window - 1]
    end_date, end_stock, end_bench = series[-1]
    stock_return = (end_stock / start_stock) - 1.0
    benchmark_return = (end_bench / start_bench) - 1.0
    relative_return = stock_return - benchmark_return
    ratio = (1.0 + stock_return) / (1.0 + benchmark_return) if benchmark_return > -1.0 else None
    return {
        "start_date": start_date,
        "end_date": end_date,
        "stock_return": stock_return,
        "benchmark_return": benchmark_return,
        "relative_return": relative_return,
        "performance_ratio": ratio,
    }


def rolling_relative_strength(series: list[tuple[str, float, float]], window: int) -> list[dict[str, float | str]]:
    output = []
    for index in range(window, len(series)):
        start_date, start_stock, start_bench = series[index - window]
        end_date, end_stock, end_bench = series[index]
        stock_return = (end_stock / start_stock) - 1.0
        benchmark_return = (end_bench / start_bench) - 1.0
        output.append(
            {
                "start_date": start_date,
                "end_date": end_date,
                "stock_return": stock_return,
                "benchmark_return": benchmark_return,
                "relative_return": stock_return - benchmark_return,
            }
        )
    return output


def summarize_rolling(values: list[dict[str, float | str]]) -> dict[str, float]:
    if not values:
        return {"count": 0, "mean_relative_return": 0.0, "hit_rate": 0.0}
    rels = [float(item["relative_return"]) for item in values]
    return {
        "count": len(rels),
        "mean_relative_return": sum(rels) / len(rels),
        "hit_rate": sum(1 for value in rels if value > 0) / len(rels),
    }


def build_payload(stock: list[PriceRow], benchmark: list[PriceRow], windows: list[int]) -> dict:
    aligned = aligned_series(stock, benchmark)
    snapshots: dict[str, dict[str, float | str]] = {}
    rolling: dict[str, dict[str, float]] = {}
    for window in sorted(set(windows)):
        snapshot = return_over_window(aligned, window)
        if snapshot:
            snapshots[str(window)] = snapshot
            rolling[str(window)] = summarize_rolling(rolling_relative_strength(aligned, window))
    latest_date = aligned[-1][0]
    return {
        "relative_strength_version": "v1-lookback-relative",
        "latest_date": latest_date,
        "aligned_row_count": len(aligned),
        "snapshots": snapshots,
        "rolling_summary": rolling,
    }


def pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.2f}%"


def render_text(payload: dict) -> str:
    lines = [
        f"Relative strength version: {payload['relative_strength_version']}",
        f"Latest date:               {payload['latest_date']}",
        f"Aligned rows:              {payload['aligned_row_count']}",
        "",
        "Lookback snapshots:",
    ]
    for window, snapshot in payload.get("snapshots", {}).items():
        lines.append(
            f"- {window}d: stock {pct(float(snapshot['stock_return']))}, "
            f"benchmark {pct(float(snapshot['benchmark_return']))}, "
            f"relative {pct(float(snapshot['relative_return']))}"
        )
    if payload.get("rolling_summary"):
        lines.extend(["", "Rolling summary:"])
        for window, summary in payload["rolling_summary"].items():
            lines.append(
                f"- {window}d: mean relative {pct(float(summary['mean_relative_return']))}, "
                f"hit rate {pct(float(summary['hit_rate']))}, n={int(summary['count'])}"
            )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    payload = build_payload(load_prices(args.prices), load_prices(args.benchmark), args.windows)
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(render_text(payload))


if __name__ == "__main__":
    main()
