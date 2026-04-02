#!/usr/bin/env python3
"""Export a short markdown snapshot for a growth-stock watchlist."""

from __future__ import annotations

import argparse
from growth_core import load_json, render_snapshot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a short growth watchlist snapshot.")
    parser.add_argument("--reports", nargs="+", required=True, help="Report JSON paths")
    parser.add_argument("--tags", help="Optional watchlist tags JSON path")
    parser.add_argument("--output", required=True, help="Output markdown path")
    return parser.parse_args()


def load_tags(path: str | None) -> dict[str, list[str]]:
    if not path:
        return {}
    payload = load_json(path)
    items = payload.get("items", []) if isinstance(payload, dict) else []
    tag_map: dict[str, list[str]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        ticker = str(item.get("ticker", "")).strip()
        tags = item.get("tags", [])
        if ticker:
            tag_map[ticker] = [str(tag) for tag in tags] if isinstance(tags, list) else []
    return tag_map


def main() -> None:
    args = parse_args()
    reports = [load_json(path) for path in args.reports]
    tag_map = load_tags(args.tags)
    content = render_snapshot(reports, tag_map)
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(content)
    print(f"Wrote growth snapshot to {args.output}")


if __name__ == "__main__":
    main()
