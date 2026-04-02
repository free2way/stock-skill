#!/usr/bin/env python3
"""Run the end-to-end growth watchlist maintenance pipeline."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from growth_core import build_dashboard_rows, build_tags, load_json, ranking_score, render_ranking, render_snapshot, short_text, write_csv, write_html, write_json


NUMBER = r"(-?\d+(?:\.\d+)?)"


@dataclass
class ScoreResult:
    name: str
    score: int
    max_score: int
    note: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the growth watchlist pipeline.")
    parser.add_argument("--manifest", required=True, help="Refresh manifest JSON path")
    parser.add_argument("--analysis-date", help="Fallback analysis date for manifest entries")
    parser.add_argument("--reports", nargs="+", required=True, help="Report JSON paths after refresh")
    parser.add_argument("--tags-out", required=True, help="Output tags JSON path")
    parser.add_argument("--snapshot-out", required=True, help="Output snapshot markdown path")
    parser.add_argument("--ranking-out", required=True, help="Output ranking markdown path")
    parser.add_argument("--csv-out", required=True, help="Output dashboard CSV path")
    parser.add_argument("--html-out", required=True, help="Output dashboard HTML path")
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
            end = match.end(2) if match.lastindex and match.lastindex >= 2 else match.end(1)
            return value * multiplier, compact_snippet(text, match.start(1), end)
    return None, None


def extract_metrics(text: str) -> dict:
    payload: dict[str, object] = {}
    sources: dict[str, str] = {}
    missing: list[str] = []
    patterns = {
        "revenue_growth_yoy": [
            rf"revenue (?:grew|growth(?: of)?|increased|up) (?:by )?{NUMBER}\s*%",
            rf"{NUMBER}\s*%\s*(?:year[- ]over[- ]year|yoy)\s*(?:revenue growth|revenue)",
            rf"revenue .*?{NUMBER}\s*%\s*(?:year[- ]over[- ]year|yoy)",
        ],
        "gross_margin": [
            rf"gross margin (?:was|of|at)?\s*{NUMBER}\s*%",
            rf"{NUMBER}\s*%\s*gross margin",
        ],
        "fcf_margin": [
            rf"free cash flow margin (?:was|of|at)?\s*{NUMBER}\s*%",
            rf"fcf margin (?:was|of|at)?\s*{NUMBER}\s*%",
            rf"{NUMBER}\s*%\s*(?:free cash flow margin|fcf margin)",
        ],
        "top_customer_share": [
            rf"top customer represented {NUMBER}\s*% of revenue",
            rf"top customer .*? represented {NUMBER}\s*% of revenue",
            rf"customer concentration .*? {NUMBER}\s*%",
            rf"{NUMBER}\s*% of revenue .*? top customer",
        ],
        "share_dilution_yoy": [
            rf"share dilution (?:was|of|at)?\s*{NUMBER}\s*%",
            rf"diluted share count .*? up {NUMBER}\s*%",
            rf"shares outstanding .*? increased .*? {NUMBER}\s*%",
        ],
        "rule_of_40": [
            rf"rule of 40 (?:was|of|at)?\s*{NUMBER}",
            rf"{NUMBER}\s*(?:rule of 40)",
        ],
    }
    for key, pattern_list in patterns.items():
        value, source = first_percent(pattern_list, text)
        if value is not None:
            payload[key] = value
            sources[key] = source or ""
        else:
            missing.append(key)
    revenue_amount, source = first_money([rf"revenue (?:was|of|totaled|totalled|reached)\s*\$?\s*{NUMBER}\s*(billion|million|b|m)?"], text)
    if revenue_amount is not None:
        sources["revenue_amount"] = source or ""
    capex_amount, source = first_money([rf"(?:capex|capital expenditures?|capital expenditure) (?:was|were|of|totaled|totalled)?\s*\$?\s*{NUMBER}\s*(billion|million|b|m)?"], text)
    if capex_amount is not None:
        sources["capex_amount"] = source or ""
    net_cash_amount, source = first_money([
        rf"net cash (?:was|of|at|position of)?\s*\$?\s*{NUMBER}\s*(billion|million|b|m)?",
        rf"cash and equivalents .*? \$\s*{NUMBER}\s*(billion|million|b|m)?.*? debt .*? \$\s*0",
    ], text)
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
    if "rule_of_40" not in payload and "revenue_growth_yoy" in payload and "fcf_margin" in payload:
        payload["rule_of_40"] = float(payload["revenue_growth_yoy"]) + float(payload["fcf_margin"])
        sources["rule_of_40"] = "Derived as revenue_growth_yoy + fcf_margin"
        missing = [item for item in missing if item != "rule_of_40"]
    payload["missing"] = missing
    payload["sources"] = sources
    return payload


def merge_metrics(existing: dict, updated: dict, analysis_date: str, ticker: str) -> dict:
    merged = dict(existing)
    merged_sources = dict(existing.get("sources", {})) if isinstance(existing.get("sources"), dict) else {}
    new_sources = updated.get("sources", {})
    for key, value in updated.items():
        if key in {"missing", "sources"}:
            continue
        merged[key] = value
    if isinstance(new_sources, dict):
        merged_sources.update(new_sources)
    merged["ticker"] = ticker
    merged["analysis_date"] = analysis_date
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


def clamp_score(value: float, low: int = 0, high: int = 5) -> int:
    return max(low, min(high, round(value)))


def build_score_json(ticker: str, metrics: dict) -> dict | None:
    if metrics.get("missing"):
        return None
    scorecard = [
        ScoreResult("revenue_growth", clamp_score((float(metrics["revenue_growth_yoy"]) - 5.0) / 10.0), 5, f"Revenue growth {float(metrics['revenue_growth_yoy']):.1f}%"),
        ScoreResult("gross_margin", clamp_score((float(metrics["gross_margin"]) - 30.0) / 8.0), 5, f"Gross margin {float(metrics['gross_margin']):.1f}%"),
        ScoreResult("fcf_margin", clamp_score((float(metrics["fcf_margin"]) + 10.0) / 6.0), 5, f"FCF margin {float(metrics['fcf_margin']):.1f}%"),
        ScoreResult("net_cash_to_revenue", clamp_score(float(metrics["net_cash_to_revenue"]) / 0.4), 5, f"Net cash / revenue {float(metrics['net_cash_to_revenue']):.2f}x"),
        ScoreResult("share_dilution", clamp_score((8.0 - float(metrics["share_dilution_yoy"])) / 1.6), 5, f"Share dilution {float(metrics['share_dilution_yoy']):.1f}%"),
        ScoreResult("top_customer_share", clamp_score((60.0 - float(metrics["top_customer_share"])) / 12.0), 5, f"Top customer share {float(metrics['top_customer_share']):.1f}%"),
        ScoreResult("capex_to_revenue", clamp_score((1.2 - float(metrics["capex_to_revenue"])) / 0.24), 5, f"Capex / revenue {float(metrics['capex_to_revenue']):.2f}x"),
        ScoreResult("rule_of_40", clamp_score((float(metrics["rule_of_40"]) - 10.0) / 10.0), 5, f"Rule of 40 {float(metrics['rule_of_40']):.1f}"),
    ]
    total = sum(item.score for item in scorecard)
    maximum = sum(item.max_score for item in scorecard)
    ratio = total / maximum
    label = "excellent" if ratio >= 0.8 else "strong" if ratio >= 0.65 else "mixed" if ratio >= 0.5 else "weak"
    return {
        "ticker": ticker,
        "total_score": total,
        "max_score": maximum,
        "label": label,
        "score_summary": f"Overall {total}/{maximum} ({label}).",
        "breakdown": [{"name": item.name, "score": item.score, "max_score": item.max_score, "note": item.note} for item in scorecard],
    }


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
    return f"Backtest {start} to {end}: total return {float(total_return) * 100:.2f}%, max drawdown {float(max_drawdown) * 100:.2f}%."


def refresh_one(entry: dict, fallback_date: str | None) -> None:
    report_path = entry["report"]
    input_path = entry["input"]
    output_path = entry.get("output", report_path)
    analysis_date = entry.get("analysis_date", fallback_date)
    if not analysis_date:
        raise ValueError(f"Missing analysis_date for {report_path}")
    report = load_json(report_path)
    text = normalize_text(read_text(input_path))
    extracted = extract_metrics(text)
    existing_metrics = report.get("metrics", {}) if isinstance(report.get("metrics"), dict) else {}
    ticker = str(report.get("ticker", existing_metrics.get("ticker", "UNKNOWN")))
    merged_metrics = merge_metrics(existing_metrics, extracted, analysis_date, ticker)
    score = build_score_json(ticker, merged_metrics)
    updated = dict(report)
    updated["analysis_date"] = analysis_date
    updated["metrics"] = merged_metrics
    if merged_metrics.get("missing"):
        updated["metrics_missing"] = merged_metrics["missing"]
    else:
        updated.pop("metrics_missing", None)
    if score:
        updated["score"] = score
        updated["score_summary"] = score["score_summary"]
    if isinstance(updated.get("backtest"), dict):
        updated["backtest_summary"] = summarize_backtest(updated["backtest"])
    write_json(output_path, updated)


def main() -> None:
    args = parse_args()
    manifest = load_json(args.manifest)
    if not isinstance(manifest, list):
        raise SystemExit("Manifest must be a JSON array")
    for entry in manifest:
        refresh_one(entry, args.analysis_date)

    reports = [load_json(path) for path in args.reports]
    tags_payload = build_tags(reports)
    write_json(args.tags_out, tags_payload)

    tag_map = {item["ticker"]: item["tags"] for item in tags_payload.get("items", [])}
    with open(args.snapshot_out, "w", encoding="utf-8") as handle:
        handle.write(render_snapshot(reports, tag_map))
    with open(args.ranking_out, "w", encoding="utf-8") as handle:
        handle.write(render_ranking(reports))

    rows = build_dashboard_rows(reports)
    write_csv(args.csv_out, rows)
    write_html(args.html_out, rows)

    print(f"Refreshed {len(manifest)} report(s)")
    print(f"Wrote tags to {args.tags_out}")
    print(f"Wrote snapshot to {args.snapshot_out}")
    print(f"Wrote ranking to {args.ranking_out}")
    print(f"Wrote dashboard CSV to {args.csv_out}")
    print(f"Wrote dashboard HTML to {args.html_out}")


if __name__ == "__main__":
    main()
