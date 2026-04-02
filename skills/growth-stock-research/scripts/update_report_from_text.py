#!/usr/bin/env python3
"""Incrementally update an existing report JSON from fresh text."""

from __future__ import annotations

import argparse
import json
import re

from industry_scorecard import build_score_payload


NUMBER = r"(-?\d+(?:\.\d+)?)"

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update a growth stock report from text.")
    parser.add_argument("--report", required=True, help="Existing report JSON path")
    parser.add_argument("--input", required=True, help="Fresh text or markdown file")
    parser.add_argument("--analysis-date", required=True, help="Analysis date in YYYY-MM-DD format")
    parser.add_argument("--output", required=True, help="Output report JSON path")
    return parser.parse_args()


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def read_text(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def normalize_text(text: str) -> str:
    lowered = text.lower()
    lowered = lowered.replace("\u2212", "-")
    lowered = lowered.replace("per cent", "%")
    lowered = lowered.replace("percent", "%")
    lowered = lowered.replace("percentage points", "pts")
    return lowered


def compact_snippet(text: str, start: int, end: int, radius: int = 80) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    return " ".join(text[left:right].split())


def first_percent(patterns: list[str], text: str) -> tuple[float | None, str | None]:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return float(match.group(1)), compact_snippet(text, match.start(1), match.end(1))
    return None, None


def first_money(patterns: list[str], text: str) -> tuple[float | None, str | None]:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            value = float(match.group(1))
            unit = (match.group(2) or "").lower()
            multiplier = 1.0
            if unit.startswith("b"):
                multiplier = 1_000_000_000.0
            elif unit.startswith("m"):
                multiplier = 1_000_000.0
            end = match.end(2) if match.lastindex and match.lastindex >= 2 else match.end(1)
            return value * multiplier, compact_snippet(text, match.start(1), end)
    return None, None


def extract_revenue_growth(text: str) -> tuple[float | None, str | None]:
    patterns = [
        rf"revenue (?:grew|growth(?: of)?|increased|up) (?:by )?{NUMBER}\s*%",
        rf"{NUMBER}\s*%\s*(?:year[- ]over[- ]year|yoy)\s*(?:revenue growth|revenue)",
        rf"revenue .*?{NUMBER}\s*%\s*(?:year[- ]over[- ]year|yoy)",
    ]
    return first_percent(patterns, text)


def extract_gross_margin(text: str) -> tuple[float | None, str | None]:
    return first_percent(
        [
            rf"gross margin (?:was|of|at)?\s*{NUMBER}\s*%",
            rf"{NUMBER}\s*%\s*gross margin",
        ],
        text,
    )


def extract_fcf_margin(text: str) -> tuple[float | None, str | None]:
    return first_percent(
        [
            rf"free cash flow margin (?:was|of|at)?\s*{NUMBER}\s*%",
            rf"fcf margin (?:was|of|at)?\s*{NUMBER}\s*%",
            rf"{NUMBER}\s*%\s*(?:free cash flow margin|fcf margin)",
        ],
        text,
    )


def extract_top_customer_share(text: str) -> tuple[float | None, str | None]:
    return first_percent(
        [
            rf"top customer represented {NUMBER}\s*% of revenue",
            rf"top customer .*? represented {NUMBER}\s*% of revenue",
            rf"customer concentration .*? {NUMBER}\s*%",
            rf"{NUMBER}\s*% of revenue .*? top customer",
        ],
        text,
    )


def extract_share_dilution(text: str) -> tuple[float | None, str | None]:
    return first_percent(
        [
            rf"share dilution (?:was|of|at)?\s*{NUMBER}\s*%",
            rf"diluted share count .*? up {NUMBER}\s*%",
            rf"shares outstanding .*? increased .*? {NUMBER}\s*%",
        ],
        text,
    )


def extract_rule_of_40(text: str) -> tuple[float | None, str | None]:
    return first_percent(
        [
            rf"rule of 40 (?:was|of|at)?\s*{NUMBER}",
            rf"{NUMBER}\s*(?:rule of 40)",
        ],
        text,
    )


def extract_revenue_amount(text: str) -> tuple[float | None, str | None]:
    return first_money(
        [rf"revenue (?:was|of|totaled|totalled|reached)\s*\$?\s*{NUMBER}\s*(billion|million|b|m)?"],
        text,
    )


def extract_capex_amount(text: str) -> tuple[float | None, str | None]:
    return first_money(
        [rf"(?:capex|capital expenditures?|capital expenditure) (?:was|were|of|totaled|totalled)?\s*\$?\s*{NUMBER}\s*(billion|million|b|m)?"],
        text,
    )


def extract_net_cash_amount(text: str) -> tuple[float | None, str | None]:
    return first_money(
        [
            rf"net cash (?:was|of|at|position of)?\s*\$?\s*{NUMBER}\s*(billion|million|b|m)?",
            rf"cash and equivalents .*? \$\s*{NUMBER}\s*(billion|million|b|m)?.*? debt .*? \$\s*0",
        ],
        text,
    )


def extract_metrics(text: str) -> dict:
    payload: dict[str, object] = {}
    sources: dict[str, str] = {}
    missing: list[str] = []

    for key, fn in [
        ("revenue_growth_yoy", extract_revenue_growth),
        ("gross_margin", extract_gross_margin),
        ("fcf_margin", extract_fcf_margin),
        ("top_customer_share", extract_top_customer_share),
        ("share_dilution_yoy", extract_share_dilution),
        ("rule_of_40", extract_rule_of_40),
    ]:
        value, source = fn(text)
        if value is not None:
            payload[key] = value
            sources[key] = source or ""
        else:
            missing.append(key)

    revenue_amount, source = extract_revenue_amount(text)
    if revenue_amount is not None:
        sources["revenue_amount"] = source or ""
    capex_amount, source = extract_capex_amount(text)
    if capex_amount is not None:
        sources["capex_amount"] = source or ""
    net_cash_amount, source = extract_net_cash_amount(text)
    if net_cash_amount is not None:
        sources["net_cash_amount"] = source or ""

    if revenue_amount and capex_amount:
        payload["capex_to_revenue"] = capex_amount / revenue_amount
    else:
        missing.append("capex_to_revenue")

    if revenue_amount and net_cash_amount:
        payload["net_cash_to_revenue"] = net_cash_amount / revenue_amount
    else:
        missing.append("net_cash_to_revenue")

    if "rule_of_40" not in payload:
        if "revenue_growth_yoy" in payload and "fcf_margin" in payload:
            payload["rule_of_40"] = float(payload["revenue_growth_yoy"]) + float(payload["fcf_margin"])
            sources["rule_of_40"] = "Derived as revenue_growth_yoy + fcf_margin"
            missing = [item for item in missing if item != "rule_of_40"]

    payload["missing"] = missing
    payload["sources"] = sources
    return payload


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


def merge_metrics(existing: dict, updated: dict) -> dict:
    merged = dict(existing)
    merged_sources = dict(existing.get("sources", {})) if isinstance(existing.get("sources"), dict) else {}
    new_sources = updated.get("sources", {})
    for key, value in updated.items():
        if key in {"missing", "sources"}:
            continue
        merged[key] = value
    if isinstance(new_sources, dict):
        merged_sources.update(new_sources)
    merged["sources"] = merged_sources

    required = [
        "revenue_growth_yoy",
        "gross_margin",
        "fcf_margin",
        "top_customer_share",
        "share_dilution_yoy",
        "capex_to_revenue",
        "net_cash_to_revenue",
        "rule_of_40",
    ]
    merged["missing"] = [key for key in required if key not in merged]
    return merged


def update_report(report: dict, fresh_text: str, analysis_date: str) -> dict:
    extracted = extract_metrics(fresh_text)
    metrics = report.get("metrics", {})
    if not isinstance(metrics, dict):
        metrics = {}
    metrics = merge_metrics(metrics, extracted)
    metrics["ticker"] = report.get("ticker", metrics.get("ticker", "UNKNOWN"))
    metrics["analysis_date"] = analysis_date

    score_payload = None
    if not metrics.get("missing"):
        score_payload = build_score_payload(metrics, ticker=str(report.get("ticker", "UNKNOWN")))

    updated = dict(report)
    updated["analysis_date"] = analysis_date
    updated["metrics"] = metrics
    if metrics.get("missing"):
        updated["metrics_missing"] = metrics["missing"]
    elif "metrics_missing" in updated:
        updated.pop("metrics_missing")
    if score_payload:
        updated["score"] = score_payload
        updated["score_summary"] = score_payload["score_summary"]
    if isinstance(updated.get("backtest"), dict):
        updated["backtest_summary"] = summarize_backtest(updated["backtest"])
    return updated


def main() -> None:
    args = parse_args()
    report = load_json(args.report)
    text = normalize_text(read_text(args.input))
    updated = update_report(report, text, args.analysis_date)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(updated, handle, indent=2)
    print(f"Wrote updated report to {args.output}")


if __name__ == "__main__":
    main()
