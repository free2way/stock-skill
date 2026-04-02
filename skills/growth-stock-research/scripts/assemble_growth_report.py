#!/usr/bin/env python3
"""Assemble a normalized growth-stock report from intermediate artifacts."""

from __future__ import annotations

import argparse
import json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assemble a growth stock report JSON.")
    parser.add_argument("--ticker", required=True, help="Ticker symbol")
    parser.add_argument("--analysis-date", required=True, help="Analysis date in YYYY-MM-DD format")
    parser.add_argument("--metrics", help="Path to metrics JSON")
    parser.add_argument("--score", help="Path to score JSON")
    parser.add_argument("--backtest", help="Path to backtest JSON")
    parser.add_argument("--notes", help="Path to analyst notes JSON")
    parser.add_argument("--output", required=True, help="Output report JSON path")
    return parser.parse_args()


def load_json(path: str | None) -> dict:
    if not path:
        return {}
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def summarize_backtest(backtest: dict) -> str | None:
    stats = backtest.get("stats")
    if not isinstance(stats, dict):
        return None
    start = stats.get("start_date")
    end = stats.get("end_date")
    total_return = stats.get("total_return")
    max_drawdown = stats.get("max_drawdown")
    if start is None or end is None or total_return is None or max_drawdown is None:
        return None
    return (
        f"Backtest {start} to {end}: total return {float(total_return) * 100:.2f}%, "
        f"max drawdown {float(max_drawdown) * 100:.2f}%."
    )


def coalesce(*values: object, default: str = "TBD") -> object:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return default


def build_report(args: argparse.Namespace) -> dict:
    metrics = load_json(args.metrics)
    score = load_json(args.score)
    backtest = load_json(args.backtest)
    notes = load_json(args.notes)

    report = {
        "ticker": args.ticker,
        "analysis_date": args.analysis_date,
        "business_quality": coalesce(notes.get("business_quality")),
        "growth_durability": coalesce(notes.get("growth_durability")),
        "key_risks": coalesce(notes.get("key_risks")),
        "valuation_context": coalesce(notes.get("valuation_context")),
        "better_business": coalesce(notes.get("better_business")),
        "better_stock": coalesce(notes.get("better_stock")),
        "higher_upside": coalesce(notes.get("higher_upside")),
        "lower_risk": coalesce(notes.get("lower_risk")),
        "score_summary": score.get("score_summary"),
        "backtest_summary": summarize_backtest(backtest),
        "notes": notes.get("notes", ""),
    }

    if metrics:
        report["metrics"] = metrics
        if isinstance(metrics.get("missing"), list) and metrics["missing"]:
            report["metrics_missing"] = metrics["missing"]

    if score:
        report["score"] = score

    if backtest:
        report["backtest"] = backtest

    if notes:
        report["notes_input"] = notes

    return report


def main() -> None:
    args = parse_args()
    report = build_report(args)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
    print(f"Wrote assembled report to {args.output}")


if __name__ == "__main__":
    main()
