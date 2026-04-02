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
    parser.add_argument("--valuation", help="Path to valuation JSON")
    parser.add_argument("--evidence", help="Path to evidence-quality JSON")
    parser.add_argument("--backtest", help="Path to backtest JSON")
    parser.add_argument("--event-study", help="Path to event-study JSON")
    parser.add_argument("--relative-strength", help="Path to relative-strength JSON")
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


def summarize_event_study(event_study: dict) -> str | None:
    summaries = event_study.get("summaries")
    if not isinstance(summaries, dict) or not summaries:
        return None
    parts: list[str] = []
    bullish = summaries.get("bullish")
    bearish = summaries.get("bearish")
    if isinstance(bullish, dict):
        for window in ("20", "60", "120"):
            block = bullish.get(window)
            if isinstance(block, dict) and isinstance(block.get("absolute"), dict):
                mean_value = block["absolute"].get("mean")
                if mean_value is not None:
                    parts.append(f"bullish {window}d mean {float(mean_value) * 100:.2f}%")
                    break
    if isinstance(bearish, dict):
        for window in ("20", "60", "120"):
            block = bearish.get(window)
            if isinstance(block, dict) and isinstance(block.get("absolute"), dict):
                mean_value = block["absolute"].get("mean")
                if mean_value is not None:
                    parts.append(f"bearish {window}d mean {float(mean_value) * 100:.2f}%")
                    break
    event_count = event_study.get("event_count")
    if event_count is not None:
        parts.append(f"{int(event_count)} event(s)")
    if not parts:
        return None
    return "Event study: " + "; ".join(parts) + "."


def summarize_relative_strength(relative_strength: dict) -> str | None:
    snapshots = relative_strength.get("snapshots")
    if not isinstance(snapshots, dict) or not snapshots:
        return None
    parts: list[str] = []
    for window in ("20", "60", "120", "252"):
        block = snapshots.get(window)
        if isinstance(block, dict):
            rel = block.get("relative_return")
            if rel is not None:
                parts.append(f"{window}d rel {float(rel) * 100:.2f}%")
    if not parts:
        return None
    return "Relative strength: " + "; ".join(parts[:3]) + "."


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
    valuation = load_json(args.valuation)
    evidence = load_json(args.evidence)
    backtest = load_json(args.backtest)
    event_study = load_json(args.event_study)
    relative_strength = load_json(args.relative_strength)
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
        "valuation_summary": valuation.get("summary"),
        "evidence_summary": evidence.get("summary"),
        "backtest_summary": summarize_backtest(backtest),
        "event_study_summary": summarize_event_study(event_study),
        "relative_strength_summary": summarize_relative_strength(relative_strength),
        "notes": notes.get("notes", ""),
    }

    if metrics:
        report["metrics"] = metrics
        if isinstance(metrics.get("missing"), list) and metrics["missing"]:
            report["metrics_missing"] = metrics["missing"]

    if score:
        report["score"] = score

    if valuation:
        report["valuation"] = valuation

    if evidence:
        report["evidence_quality"] = evidence

    if backtest:
        report["backtest"] = backtest

    if event_study:
        report["event_study"] = event_study

    if relative_strength:
        report["relative_strength"] = relative_strength

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
