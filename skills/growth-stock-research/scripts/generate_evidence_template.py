#!/usr/bin/env python3
"""Generate an analyst-friendly evidence annotation template from metrics or report JSON."""

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate an evidence annotation template.")
    parser.add_argument("--input", required=True, help="Metrics JSON or report JSON path")
    parser.add_argument("--output", required=True, help="Output annotation JSON path")
    return parser.parse_args()


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def build_template(payload: dict) -> dict:
    metrics = payload.get("metrics") if isinstance(payload.get("metrics"), dict) else payload
    sources = metrics.get("sources", {}) if isinstance(metrics.get("sources"), dict) else {}
    evidence = metrics.get("evidence", {}) if isinstance(metrics.get("evidence"), dict) else {}

    annotations: dict[str, dict[str, object]] = {}
    for field in METRIC_FIELDS:
        existing = evidence.get(field, {}) if isinstance(evidence.get(field), dict) else {}
        if field not in metrics:
            continue
        annotations[field] = {
            "value": metrics.get(field),
            "source_type": existing.get("source_type", "unknown"),
            "source_date": existing.get("source_date", ""),
            "period": existing.get("period", ""),
            "is_machine_extracted": bool(existing.get("is_machine_extracted", True)),
            "manually_confirmed": bool(existing.get("manually_confirmed", False)),
            "is_derived": bool(existing.get("is_derived", False)),
            "gaap_basis": existing.get("gaap_basis", ""),
            "citation": existing.get("citation", sources.get(field, "")),
            "notes": existing.get("notes", ""),
        }

    return {
        "ticker": metrics.get("ticker", payload.get("ticker", "UNKNOWN")),
        "analysis_date": metrics.get("analysis_date", payload.get("analysis_date", "n/a")),
        "instructions": [
            "Fill source_type with values like 10-Q, 10-K, earnings_release, shareholder_letter, investor_presentation, news, or manual_estimate.",
            "Set manually_confirmed=true after checking the cited source directly.",
            "Use period values like Q4 FY2025, FY2025, NTM, or 2026 guidance.",
            "Use gaap_basis values like GAAP, non-GAAP, guidance, derived, or company-specific KPI.",
            "Leave is_machine_extracted=true if the value still depends on automated parsing.",
        ],
        "annotations": annotations,
    }


def main() -> None:
    args = parse_args()
    payload = build_template(load_json(args.input))
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    print(f"Wrote evidence template to {args.output}")


if __name__ == "__main__":
    main()
