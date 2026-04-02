#!/usr/bin/env python3
"""Extract a first-pass growth-stock metrics JSON from plain text."""

from __future__ import annotations

import argparse
import json
import re


NUMBER = r"(-?\d+(?:\.\d+)?)"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract growth metrics from text.")
    parser.add_argument("--input", required=True, help="Text or markdown file to parse")
    parser.add_argument("--ticker", required=True, help="Ticker symbol")
    parser.add_argument("--analysis-date", required=True, help="Analysis date in YYYY-MM-DD format")
    parser.add_argument("--output", required=True, help="Output metrics JSON path")
    return parser.parse_args()


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
            return value * multiplier, compact_snippet(text, match.start(1), match.end(2) if match.lastindex and match.lastindex >= 2 else match.end(1))
    return None, None


def extract_revenue_growth(text: str) -> tuple[float | None, str | None]:
    patterns = [
        rf"revenue (?:grew|growth(?: of)?|increased|up) (?:by )?{NUMBER}\s*%",
        rf"{NUMBER}\s*%\s*(?:year[- ]over[- ]year|yoy)\s*(?:revenue growth|revenue)",
        rf"revenue .*?{NUMBER}\s*%\s*(?:year[- ]over[- ]year|yoy)",
    ]
    return first_percent(patterns, text)


def extract_gross_margin(text: str) -> tuple[float | None, str | None]:
    patterns = [
        rf"gross margin (?:was|of|at)?\s*{NUMBER}\s*%",
        rf"{NUMBER}\s*%\s*gross margin",
    ]
    return first_percent(patterns, text)


def extract_fcf_margin(text: str) -> tuple[float | None, str | None]:
    patterns = [
        rf"free cash flow margin (?:was|of|at)?\s*{NUMBER}\s*%",
        rf"fcf margin (?:was|of|at)?\s*{NUMBER}\s*%",
        rf"{NUMBER}\s*%\s*(?:free cash flow margin|fcf margin)",
    ]
    return first_percent(patterns, text)


def extract_top_customer_share(text: str) -> tuple[float | None, str | None]:
    patterns = [
        rf"top customer represented {NUMBER}\s*% of revenue",
        rf"top customer .*? represented {NUMBER}\s*% of revenue",
        rf"customer concentration .*? {NUMBER}\s*%",
        rf"{NUMBER}\s*% of revenue .*? top customer",
    ]
    return first_percent(patterns, text)


def extract_share_dilution(text: str) -> tuple[float | None, str | None]:
    patterns = [
        rf"share dilution (?:was|of|at)?\s*{NUMBER}\s*%",
        rf"diluted share count .*? up {NUMBER}\s*%",
        rf"shares outstanding .*? increased .*? {NUMBER}\s*%",
    ]
    return first_percent(patterns, text)


def extract_rule_of_40(text: str) -> tuple[float | None, str | None]:
    patterns = [
        rf"rule of 40 (?:was|of|at)?\s*{NUMBER}",
        rf"{NUMBER}\s*(?:rule of 40)",
    ]
    return first_percent(patterns, text)


def extract_revenue_amount(text: str) -> tuple[float | None, str | None]:
    patterns = [
        rf"revenue (?:was|of|totaled|totalled|reached)\s*\$?\s*{NUMBER}\s*(billion|million|b|m)?",
    ]
    return first_money(patterns, text)


def extract_capex_amount(text: str) -> tuple[float | None, str | None]:
    patterns = [
        rf"(?:capex|capital expenditures?|capital expenditure) (?:was|were|of|totaled|totalled)?\s*\$?\s*{NUMBER}\s*(billion|million|b|m)?",
    ]
    return first_money(patterns, text)


def extract_net_cash_amount(text: str) -> tuple[float | None, str | None]:
    patterns = [
        rf"net cash (?:was|of|at|position of)?\s*\$?\s*{NUMBER}\s*(billion|million|b|m)?",
        rf"cash and equivalents .*? \$\s*{NUMBER}\s*(billion|million|b|m)?.*? debt .*? \$\s*0",
    ]
    return first_money(patterns, text)


def build_payload(ticker: str, analysis_date: str, text: str) -> dict:
    payload: dict[str, object] = {
        "ticker": ticker,
        "analysis_date": analysis_date,
    }
    sources: dict[str, str] = {}
    evidence: dict[str, dict[str, object]] = {}
    missing: list[str] = []

    revenue_growth, source = extract_revenue_growth(text)
    if revenue_growth is not None:
        payload["revenue_growth_yoy"] = revenue_growth
        sources["revenue_growth_yoy"] = source or ""
        evidence["revenue_growth_yoy"] = {"source_type": "unknown", "is_machine_extracted": True, "citation": source or ""}
    else:
        missing.append("revenue_growth_yoy")

    gross_margin, source = extract_gross_margin(text)
    if gross_margin is not None:
        payload["gross_margin"] = gross_margin
        sources["gross_margin"] = source or ""
        evidence["gross_margin"] = {"source_type": "unknown", "is_machine_extracted": True, "citation": source or ""}
    else:
        missing.append("gross_margin")

    fcf_margin, source = extract_fcf_margin(text)
    if fcf_margin is not None:
        payload["fcf_margin"] = fcf_margin
        sources["fcf_margin"] = source or ""
        evidence["fcf_margin"] = {"source_type": "unknown", "is_machine_extracted": True, "citation": source or ""}
    else:
        missing.append("fcf_margin")

    top_customer_share, source = extract_top_customer_share(text)
    if top_customer_share is not None:
        payload["top_customer_share"] = top_customer_share
        sources["top_customer_share"] = source or ""
        evidence["top_customer_share"] = {"source_type": "unknown", "is_machine_extracted": True, "citation": source or ""}
    else:
        missing.append("top_customer_share")

    share_dilution, source = extract_share_dilution(text)
    if share_dilution is not None:
        payload["share_dilution_yoy"] = share_dilution
        sources["share_dilution_yoy"] = source or ""
        evidence["share_dilution_yoy"] = {"source_type": "unknown", "is_machine_extracted": True, "citation": source or ""}
    else:
        missing.append("share_dilution_yoy")

    rule_of_40, source = extract_rule_of_40(text)
    if rule_of_40 is not None:
        payload["rule_of_40"] = rule_of_40
        sources["rule_of_40"] = source or ""
        evidence["rule_of_40"] = {"source_type": "unknown", "is_machine_extracted": True, "citation": source or ""}

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
        evidence["capex_to_revenue"] = {"source_type": "unknown", "is_machine_extracted": True, "is_derived": True, "citation": f"{sources.get('capex_amount', '')} | {sources.get('revenue_amount', '')}"}
    else:
        missing.append("capex_to_revenue")

    if revenue_amount and net_cash_amount:
        payload["net_cash_to_revenue"] = net_cash_amount / revenue_amount
        evidence["net_cash_to_revenue"] = {"source_type": "unknown", "is_machine_extracted": True, "is_derived": True, "citation": f"{sources.get('net_cash_amount', '')} | {sources.get('revenue_amount', '')}"}
    else:
        missing.append("net_cash_to_revenue")

    if "rule_of_40" not in payload:
        if "revenue_growth_yoy" in payload and "fcf_margin" in payload:
            payload["rule_of_40"] = float(payload["revenue_growth_yoy"]) + float(payload["fcf_margin"])
            sources["rule_of_40"] = "Derived as revenue_growth_yoy + fcf_margin"
            evidence["rule_of_40"] = {"source_type": "manual_estimate", "is_machine_extracted": True, "is_derived": True, "citation": sources["rule_of_40"]}
        else:
            missing.append("rule_of_40")

    payload["missing"] = missing
    payload["sources"] = sources
    payload["evidence"] = evidence
    return payload


def main() -> None:
    args = parse_args()
    text = normalize_text(read_text(args.input))
    payload = build_payload(args.ticker, args.analysis_date, text)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    print(f"Wrote extracted metrics to {args.output}")
    if payload["missing"]:
        print("Missing:", ", ".join(payload["missing"]))


if __name__ == "__main__":
    main()
