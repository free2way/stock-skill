#!/usr/bin/env python3
"""Assign lightweight management tags to a set of growth-stock reports."""

from __future__ import annotations

import argparse
from growth_core import build_tags, load_json, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tag growth-stock watchlist reports.")
    parser.add_argument("--reports", nargs="+", required=True, help="Report JSON paths")
    parser.add_argument("--output", required=True, help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    reports = [load_json(path) for path in args.reports]
    payload = build_tags(reports)
    write_json(args.output, payload)
    print(f"Wrote watchlist tags to {args.output}")


if __name__ == "__main__":
    main()
