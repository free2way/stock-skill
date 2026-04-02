#!/usr/bin/env python3
"""Compare two versions of a growth-stock report and emit a markdown diff."""

from __future__ import annotations

import argparse
import json


NARRATIVE_FIELDS = [
    "business_quality",
    "growth_durability",
    "key_risks",
    "valuation_context",
    "notes",
    "score_summary",
    "backtest_summary",
]

METRIC_FIELDS = [
    "revenue_growth_yoy",
    "gross_margin",
    "fcf_margin",
    "top_customer_share",
    "share_dilution_yoy",
    "capex_to_revenue",
    "net_cash_to_revenue",
    "rule_of_40",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diff two growth-stock report JSON files.")
    parser.add_argument("--old", required=True, help="Old report JSON path")
    parser.add_argument("--new", required=True, help="New report JSON path")
    parser.add_argument("--output", required=True, help="Output markdown path")
    return parser.parse_args()


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def format_number(value: object) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return str(value)


def metric_diff(old_metrics: dict, new_metrics: dict) -> list[str]:
    lines: list[str] = []
    for field in METRIC_FIELDS:
        old_value = old_metrics.get(field)
        new_value = new_metrics.get(field)
        if old_value == new_value:
            continue
        if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
            delta = float(new_value) - float(old_value)
            delta_text = f"{delta:+.4f}".rstrip("0").rstrip(".")
            lines.append(
                f"- `{field}`: {format_number(old_value)} -> {format_number(new_value)} ({delta_text})"
            )
        else:
            lines.append(
                f"- `{field}`: {format_number(old_value)} -> {format_number(new_value)}"
            )
    return lines


def missing_diff(old_metrics: dict, new_metrics: dict) -> list[str]:
    old_missing = set(old_metrics.get("missing", [])) if isinstance(old_metrics.get("missing"), list) else set()
    new_missing = set(new_metrics.get("missing", [])) if isinstance(new_metrics.get("missing"), list) else set()
    lines: list[str] = []
    added = sorted(new_missing - old_missing)
    removed = sorted(old_missing - new_missing)
    if added:
        lines.append(f"- Newly missing: {', '.join(added)}")
    if removed:
        lines.append(f"- No longer missing: {', '.join(removed)}")
    return lines


def narrative_diff(old_report: dict, new_report: dict) -> list[str]:
    lines: list[str] = []
    for field in NARRATIVE_FIELDS:
        old_value = str(old_report.get(field, "")).strip()
        new_value = str(new_report.get(field, "")).strip()
        if old_value == new_value:
            continue
        lines.append(f"- `{field}` changed")
        lines.append(f"  old: {old_value or 'n/a'}")
        lines.append(f"  new: {new_value or 'n/a'}")
    return lines


def score_block(old_report: dict, new_report: dict) -> list[str]:
    old_score = old_report.get("score", {}) if isinstance(old_report.get("score"), dict) else {}
    new_score = new_report.get("score", {}) if isinstance(new_report.get("score"), dict) else {}
    old_total = old_score.get("total_score")
    new_total = new_score.get("total_score")
    old_max = old_score.get("max_score")
    new_max = new_score.get("max_score")
    lines: list[str] = []
    if old_total is not None or new_total is not None:
        lines.append(
            f"- Score: {format_number(old_total)}/{format_number(old_max)} -> {format_number(new_total)}/{format_number(new_max)}"
        )
    old_label = old_score.get("label")
    new_label = new_score.get("label")
    if old_label != new_label:
        lines.append(f"- Label: {format_number(old_label)} -> {format_number(new_label)}")
    return lines


def render_markdown(old_report: dict, new_report: dict) -> str:
    ticker = new_report.get("ticker") or old_report.get("ticker") or "UNKNOWN"
    old_date = old_report.get("analysis_date", "n/a")
    new_date = new_report.get("analysis_date", "n/a")
    old_metrics = old_report.get("metrics", {}) if isinstance(old_report.get("metrics"), dict) else {}
    new_metrics = new_report.get("metrics", {}) if isinstance(new_report.get("metrics"), dict) else {}

    lines = [
        f"# {ticker} Report Diff",
        "",
        f"- Old analysis date: {old_date}",
        f"- New analysis date: {new_date}",
        "",
        "## Score",
    ]
    score_lines = score_block(old_report, new_report)
    lines.extend(score_lines or ["- No score change detected"])

    lines.extend(["", "## Metric Changes"])
    metric_lines = metric_diff(old_metrics, new_metrics)
    lines.extend(metric_lines or ["- No metric changes detected"])

    lines.extend(["", "## Missing Fields"])
    missing_lines = missing_diff(old_metrics, new_metrics)
    lines.extend(missing_lines or ["- No missing-field changes detected"])

    lines.extend(["", "## Narrative Changes"])
    narrative_lines = narrative_diff(old_report, new_report)
    lines.extend(narrative_lines or ["- No narrative changes detected"])
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    old_report = load_json(args.old)
    new_report = load_json(args.new)
    content = render_markdown(old_report, new_report)
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(content)
    print(f"Wrote report diff to {args.output}")


if __name__ == "__main__":
    main()
