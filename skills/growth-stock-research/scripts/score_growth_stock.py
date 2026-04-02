#!/usr/bin/env python3
"""Score a growth stock from a compact metrics JSON file."""

from __future__ import annotations

import argparse
import json

from industry_scorecard import build_score_payload, render_text, supported_profiles


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score a growth stock from metrics JSON.")
    parser.add_argument("--input", required=True, help="Path to metrics JSON")
    parser.add_argument(
        "--profile",
        choices=supported_profiles(),
        help="Optional industry profile override. Otherwise use the metrics JSON field `industry_profile` when present.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with open(args.input, encoding="utf-8") as handle:
        payload = json.load(handle)

    ticker = str(payload.get("ticker", "UNKNOWN"))
    score_payload = build_score_payload(payload, ticker=ticker, profile_override=args.profile)
    if score_payload is None:
        raise SystemExit("Missing required metrics for scoring")
    if args.json:
        print(json.dumps(score_payload, indent=2))
        return
    print(render_text(score_payload))


if __name__ == "__main__":
    main()
