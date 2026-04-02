#!/usr/bin/env python3
"""Create a markdown comparison draft from two stock research JSON files."""

from __future__ import annotations

import argparse
import json


FIELDS = [
    ("ticker", "Ticker"),
    ("analysis_date", "Analysis date"),
    ("better_business", "Better business"),
    ("better_stock", "Better stock"),
    ("higher_upside", "Higher upside"),
    ("lower_risk", "Lower risk"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare two growth-stock JSON reports.")
    parser.add_argument("--left", required=True, help="Left-side JSON report")
    parser.add_argument("--right", required=True, help="Right-side JSON report")
    parser.add_argument("--output", required=True, help="Output markdown path")
    return parser.parse_args()


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def metric(report: dict, key: str, fallback: str = "n/a") -> str:
    value = report.get(key, fallback)
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def render_markdown(left: dict, right: dict) -> str:
    left_name = metric(left, "ticker")
    right_name = metric(right, "ticker")
    lines = [
        f"# {left_name} vs {right_name}",
        "",
        "| Dimension | Left | Right |",
        "| --- | --- | --- |",
    ]
    for key, label in FIELDS:
        lines.append(f"| {label} | {metric(left, key)} | {metric(right, key)} |")

    lines.extend(
        [
            "",
            "## Business Quality",
            f"- {left_name}: {metric(left, 'business_quality')}",
            f"- {right_name}: {metric(right, 'business_quality')}",
            "",
            "## Growth Durability",
            f"- {left_name}: {metric(left, 'growth_durability')}",
            f"- {right_name}: {metric(right, 'growth_durability')}",
            "",
            "## Key Risks",
            f"- {left_name}: {metric(left, 'key_risks')}",
            f"- {right_name}: {metric(right, 'key_risks')}",
            "",
            "## Valuation Context",
            f"- {left_name}: {metric(left, 'valuation_context')}",
            f"- {right_name}: {metric(right, 'valuation_context')}",
            "",
            "## Backtest Snapshot",
            f"- {left_name}: {metric(left, 'backtest_summary', 'No backtest attached')}",
            f"- {right_name}: {metric(right, 'backtest_summary', 'No backtest attached')}",
            "",
            "## Tentative Conclusion",
            f"- Better business: {metric(left, 'better_business')}",
            f"- Better stock: {metric(left, 'better_stock')}",
            f"- Higher upside: {metric(left, 'higher_upside')}",
            f"- Lower risk: {metric(left, 'lower_risk')}",
            "",
            "Replace the tentative conclusion after checking current sources and making a real judgment.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    left = load_json(args.left)
    right = load_json(args.right)
    content = render_markdown(left, right)
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(content)
    print(f"Wrote comparison draft to {args.output}")


if __name__ == "__main__":
    main()
