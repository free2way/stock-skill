#!/usr/bin/env python3
"""Export growth-stock reports to CSV and HTML watchlist artifacts."""

from __future__ import annotations

import argparse
from growth_core import build_dashboard_rows, load_json, write_csv, write_html


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a growth-stock watchlist dashboard.")
    parser.add_argument("--reports", nargs="+", required=True, help="Report JSON paths")
    parser.add_argument("--csv", required=True, help="Output CSV path")
    parser.add_argument("--html", required=True, help="Output HTML path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    reports = [load_json(path) for path in args.reports]
    rows = build_dashboard_rows(reports)
    write_csv(args.csv, rows)
    write_html(args.html, rows)
    print(f"Wrote CSV dashboard to {args.csv}")
    print(f"Wrote HTML dashboard to {args.html}")


if __name__ == "__main__":
    main()
