#!/usr/bin/env python3
"""Assess evidence quality for growth-stock metrics and valuation inputs."""

from __future__ import annotations

import argparse
import json


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


SOURCE_TYPE_SCORE = {
    "10-k": 1.0,
    "10-q": 1.0,
    "20-f": 1.0,
    "8-k": 0.95,
    "earnings_release": 0.9,
    "shareholder_letter": 0.85,
    "prepared_remarks": 0.8,
    "investor_presentation": 0.75,
    "news": 0.55,
    "secondary_summary": 0.45,
    "analyst_note": 0.4,
    "manual_estimate": 0.35,
    "unknown": 0.3,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assess evidence quality for a metrics or report JSON.")
    parser.add_argument("--input", required=True, help="Metrics JSON or report JSON path")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    return parser.parse_args()


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def normalize_source_type(value: object) -> str:
    text = str(value or "unknown").strip().lower().replace(" ", "_")
    return text if text in SOURCE_TYPE_SCORE else "unknown"


def source_strength(entry: dict) -> float:
    source_type = normalize_source_type(entry.get("source_type"))
    score = SOURCE_TYPE_SCORE[source_type]
    if entry.get("is_derived"):
        score -= 0.15
    if entry.get("is_machine_extracted", True):
        score -= 0.10
    if entry.get("manually_confirmed"):
        score += 0.10
    if entry.get("source_date"):
        score += 0.05
    if entry.get("period"):
        score += 0.05
    if entry.get("gaap_basis"):
        score += 0.05
    if entry.get("citation"):
        score += 0.05
    return max(0.0, min(1.0, score))


def confidence_label(score: float) -> str:
    if score >= 0.85:
        return "high"
    if score >= 0.65:
        return "medium"
    return "low"


def build_evidence_map(payload: dict) -> dict[str, dict]:
    metrics = payload.get("metrics") if isinstance(payload.get("metrics"), dict) else payload
    sources = metrics.get("sources", {}) if isinstance(metrics.get("sources"), dict) else {}
    evidence = metrics.get("evidence", {}) if isinstance(metrics.get("evidence"), dict) else {}
    output: dict[str, dict] = {}

    for field in METRIC_FIELDS:
        entry = evidence.get(field, {}) if isinstance(evidence.get(field), dict) else {}
        snippet = sources.get(field)
        if snippet and "citation" not in entry:
            entry = dict(entry)
            entry["citation"] = str(snippet)
        if field == "rule_of_40" and str(sources.get(field, "")).startswith("Derived as"):
            entry = dict(entry)
            entry.setdefault("is_derived", True)
            entry.setdefault("source_type", "manual_estimate")
        if field in metrics:
            output[field] = {
                "value": metrics.get(field),
                "source_type": normalize_source_type(entry.get("source_type")),
                "source_date": entry.get("source_date"),
                "period": entry.get("period"),
                "is_machine_extracted": bool(entry.get("is_machine_extracted", True)),
                "manually_confirmed": bool(entry.get("manually_confirmed", False)),
                "is_derived": bool(entry.get("is_derived", False)),
                "gaap_basis": entry.get("gaap_basis"),
                "citation": entry.get("citation"),
            }
    return output


def build_payload(payload: dict) -> dict:
    metrics = payload.get("metrics") if isinstance(payload.get("metrics"), dict) else payload
    ticker = str(payload.get("ticker", metrics.get("ticker", "UNKNOWN")))
    analysis_date = str(payload.get("analysis_date", metrics.get("analysis_date", "n/a")))
    evidence_map = build_evidence_map(payload)

    items = []
    for field, entry in evidence_map.items():
        score = source_strength(entry)
        items.append(
            {
                "field": field,
                "value": entry.get("value"),
                "source_type": entry.get("source_type"),
                "source_date": entry.get("source_date"),
                "period": entry.get("period"),
                "is_machine_extracted": entry.get("is_machine_extracted"),
                "manually_confirmed": entry.get("manually_confirmed"),
                "is_derived": entry.get("is_derived"),
                "gaap_basis": entry.get("gaap_basis"),
                "citation": entry.get("citation"),
                "confidence_score": round(score, 2),
                "confidence_label": confidence_label(score),
            }
        )

    overall = round(sum(item["confidence_score"] for item in items) / len(items), 2) if items else 0.0
    low_fields = [item["field"] for item in items if item["confidence_label"] == "low"]
    summary = f"Evidence quality {overall:.2f}/1.00 ({confidence_label(overall)})."
    if low_fields:
        summary += f" Lowest-confidence fields: {', '.join(low_fields)}."

    return {
        "ticker": ticker,
        "analysis_date": analysis_date,
        "evidence_version": "v1-source-confidence",
        "overall_confidence_score": overall,
        "overall_confidence_label": confidence_label(overall),
        "summary": summary,
        "items": items,
    }


def render_text(payload: dict) -> str:
    lines = [
        f"Ticker:               {payload['ticker']}",
        f"Evidence version:     {payload['evidence_version']}",
        f"Overall confidence:   {payload['overall_confidence_score']:.2f} ({payload['overall_confidence_label']})",
        f"Summary:              {payload['summary']}",
        "",
        "Field confidence:",
    ]
    for item in payload["items"]:
        lines.append(
            f"- {item['field']}: {item['confidence_label']} ({item['confidence_score']:.2f})"
            f" | source={item['source_type']}"
            f" | basis={item.get('gaap_basis') or 'n/a'}"
            f" | derived={item['is_derived']}"
            f" | machine_extracted={item['is_machine_extracted']}"
        )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    payload = build_payload(load_json(args.input))
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(render_text(payload))


if __name__ == "__main__":
    main()
