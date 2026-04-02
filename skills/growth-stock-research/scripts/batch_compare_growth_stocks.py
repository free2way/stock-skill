#!/usr/bin/env python3
"""Rank multiple growth-stock report JSON files and emit a markdown summary."""

from __future__ import annotations

import argparse
from growth_core import load_json, render_ranking


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch compare growth-stock reports.")
    parser.add_argument("--reports", nargs="+", required=True, help="Report JSON paths")
    parser.add_argument("--output", required=True, help="Output markdown path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    reports = [load_json(path) for path in args.reports]
    content = render_ranking(reports)
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(content)
    print(f"Wrote batch comparison to {args.output}")


if __name__ == "__main__":
    main()
