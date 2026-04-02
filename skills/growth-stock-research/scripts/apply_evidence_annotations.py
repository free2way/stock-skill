#!/usr/bin/env python3
"""Apply analyst evidence annotations onto a metrics or report JSON file."""

from __future__ import annotations

import argparse
import json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply evidence annotations to metrics or report JSON.")
    parser.add_argument("--input", required=True, help="Metrics JSON or report JSON path")
    parser.add_argument("--annotations", required=True, help="Evidence annotation JSON path")
    parser.add_argument("--output", required=True, help="Output JSON path")
    return parser.parse_args()


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def merge_metrics(metrics: dict, annotations: dict) -> dict:
    merged = dict(metrics)
    evidence = dict(metrics.get("evidence", {})) if isinstance(metrics.get("evidence"), dict) else {}
    annotation_map = annotations.get("annotations", {}) if isinstance(annotations.get("annotations"), dict) else {}

    for field, entry in annotation_map.items():
        if not isinstance(entry, dict):
            continue
        target = dict(evidence.get(field, {})) if isinstance(evidence.get(field), dict) else {}
        for key in [
            "source_type",
            "source_date",
            "period",
            "is_machine_extracted",
            "manually_confirmed",
            "is_derived",
            "gaap_basis",
            "citation",
            "notes",
        ]:
            if key in entry:
                target[key] = entry[key]
        evidence[field] = target
    merged["evidence"] = evidence
    return merged


def main() -> None:
    args = parse_args()
    payload = load_json(args.input)
    annotations = load_json(args.annotations)

    if isinstance(payload.get("metrics"), dict):
        updated = dict(payload)
        updated["metrics"] = merge_metrics(payload["metrics"], annotations)
    else:
        updated = merge_metrics(payload, annotations)

    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(updated, handle, indent=2)
    print(f"Wrote annotated JSON to {args.output}")


if __name__ == "__main__":
    main()
