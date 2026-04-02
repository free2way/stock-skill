#!/usr/bin/env python3
"""Score a growth stock from a compact metrics JSON file."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass


@dataclass
class ScoreResult:
    name: str
    score: int
    max_score: int
    note: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score a growth stock from metrics JSON.")
    parser.add_argument("--input", required=True, help="Path to metrics JSON")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    return parser.parse_args()


def clamp_score(value: float, low: int = 0, high: int = 5) -> int:
    return max(low, min(high, round(value)))


def require_number(payload: dict, key: str) -> float:
    if key not in payload:
        raise ValueError(f"Missing required metric: {key}")
    return float(payload[key])


def score_revenue_growth(value: float) -> ScoreResult:
    score = clamp_score((value - 5.0) / 10.0)
    return ScoreResult("revenue_growth", score, 5, f"Revenue growth {value:.1f}%")


def score_gross_margin(value: float) -> ScoreResult:
    score = clamp_score((value - 30.0) / 8.0)
    return ScoreResult("gross_margin", score, 5, f"Gross margin {value:.1f}%")


def score_fcf_margin(value: float) -> ScoreResult:
    score = clamp_score((value + 10.0) / 6.0)
    return ScoreResult("fcf_margin", score, 5, f"FCF margin {value:.1f}%")


def score_net_cash(value: float) -> ScoreResult:
    score = clamp_score(value / 0.4)
    return ScoreResult("net_cash_to_revenue", score, 5, f"Net cash / revenue {value:.2f}x")


def score_dilution(value: float) -> ScoreResult:
    score = clamp_score((8.0 - value) / 1.6)
    return ScoreResult("share_dilution", score, 5, f"Share dilution {value:.1f}%")


def score_customer_concentration(value: float) -> ScoreResult:
    score = clamp_score((60.0 - value) / 12.0)
    return ScoreResult("top_customer_share", score, 5, f"Top customer share {value:.1f}%")


def score_capital_intensity(value: float) -> ScoreResult:
    score = clamp_score((1.2 - value) / 0.24)
    return ScoreResult("capex_to_revenue", score, 5, f"Capex / revenue {value:.2f}x")


def score_rule_of_40(value: float) -> ScoreResult:
    score = clamp_score((value - 10.0) / 10.0)
    return ScoreResult("rule_of_40", score, 5, f"Rule of 40 {value:.1f}")


def build_scorecard(payload: dict) -> list[ScoreResult]:
    revenue_growth = require_number(payload, "revenue_growth_yoy")
    gross_margin = require_number(payload, "gross_margin")
    fcf_margin = require_number(payload, "fcf_margin")
    net_cash = require_number(payload, "net_cash_to_revenue")
    dilution = require_number(payload, "share_dilution_yoy")
    concentration = require_number(payload, "top_customer_share")
    capex = require_number(payload, "capex_to_revenue")
    rule_of_40 = require_number(payload, "rule_of_40")

    return [
        score_revenue_growth(revenue_growth),
        score_gross_margin(gross_margin),
        score_fcf_margin(fcf_margin),
        score_net_cash(net_cash),
        score_dilution(dilution),
        score_customer_concentration(concentration),
        score_capital_intensity(capex),
        score_rule_of_40(rule_of_40),
    ]


def overall_label(total_score: int, max_score: int) -> str:
    ratio = total_score / max_score
    if ratio >= 0.8:
        return "excellent"
    if ratio >= 0.65:
        return "strong"
    if ratio >= 0.5:
        return "mixed"
    return "weak"


def render_text(ticker: str, scorecard: list[ScoreResult]) -> str:
    total_score = sum(item.score for item in scorecard)
    max_score = sum(item.max_score for item in scorecard)
    lines = [
        f"Ticker:       {ticker}",
        f"Total score:  {total_score}/{max_score}",
        f"Label:        {overall_label(total_score, max_score)}",
        "",
        "Breakdown:",
    ]
    for item in scorecard:
        lines.append(f"- {item.name}: {item.score}/{item.max_score} ({item.note})")
    return "\n".join(lines)


def render_json(ticker: str, scorecard: list[ScoreResult]) -> str:
    total_score = sum(item.score for item in scorecard)
    max_score = sum(item.max_score for item in scorecard)
    payload = {
        "ticker": ticker,
        "total_score": total_score,
        "max_score": max_score,
        "label": overall_label(total_score, max_score),
        "score_summary": f"Overall {total_score}/{max_score} ({overall_label(total_score, max_score)}).",
        "breakdown": [
            {
                "name": item.name,
                "score": item.score,
                "max_score": item.max_score,
                "note": item.note,
            }
            for item in scorecard
        ],
    }
    return json.dumps(payload, indent=2)


def main() -> None:
    args = parse_args()
    with open(args.input, encoding="utf-8") as handle:
        payload = json.load(handle)

    ticker = str(payload.get("ticker", "UNKNOWN"))
    scorecard = build_scorecard(payload)
    if args.json:
        print(render_json(ticker, scorecard))
        return
    print(render_text(ticker, scorecard))


if __name__ == "__main__":
    main()
