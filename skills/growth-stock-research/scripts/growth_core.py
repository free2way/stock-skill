#!/usr/bin/env python3
"""Shared helpers for the growth-stock-research skill."""

from __future__ import annotations

import csv
import html
import json


def load_json(path: str):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: str, payload) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def short_text(value: object, fallback: str = "n/a", limit: int = 90) -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    if not text:
        return fallback
    return text if len(text) <= limit else text[: limit - 3] + "..."


def missing_count(report: dict) -> int:
    missing = report.get("metrics_missing")
    if isinstance(missing, list):
        return len(missing)
    metrics = report.get("metrics")
    if isinstance(metrics, dict) and isinstance(metrics.get("missing"), list):
        return len(metrics["missing"])
    return 0


def score_ratio(report: dict) -> float:
    score = report.get("score")
    if not isinstance(score, dict):
        return 0.0
    total = score.get("total_score")
    maximum = score.get("max_score")
    if total is None or maximum in (None, 0):
        return 0.0
    return float(total) / float(maximum)


def ranking_score(report: dict) -> float:
    return max(0.0, score_ratio(report) - 0.02 * missing_count(report))


def assign_tags(report: dict) -> list[str]:
    tags: list[str] = []
    score = report.get("score")
    total = score.get("total_score") if isinstance(score, dict) else None
    maximum = score.get("max_score") if isinstance(score, dict) else None
    label = str(score.get("label", "n/a")) if isinstance(score, dict) else "n/a"
    ratio = None if total is None or maximum in (None, 0) else float(total) / float(maximum)
    missing = missing_count(report)
    backtest_summary = str(report.get("backtest_summary", "")).strip()

    if ratio is None:
        tags.append("needs-review")
    elif ratio >= 0.65:
        tags.extend(["strong-score", "high-quality"])
    elif ratio < 0.5:
        tags.extend(["weak-score", "high-risk"])
    else:
        tags.append("watch-only")

    if missing > 0:
        tags.extend(["missing-data", "needs-review"])
    if backtest_summary and backtest_summary.lower() != "no backtest attached.":
        tags.append("has-backtest")
    if label == "weak" and "high-risk" not in tags:
        tags.append("high-risk")
    if label == "strong" and "high-quality" not in tags:
        tags.append("high-quality")

    deduped: list[str] = []
    for tag in tags:
        if tag not in deduped:
            deduped.append(tag)
    return deduped


def build_tags(reports: list[dict]) -> dict:
    return {
        "items": [
            {
                "ticker": report.get("ticker", "UNKNOWN"),
                "analysis_date": report.get("analysis_date", "n/a"),
                "score": None if not isinstance(report.get("score"), dict) else f"{report['score'].get('total_score', 'n/a')}/{report['score'].get('max_score', 'n/a')}",
                "label": report.get("score", {}).get("label", "n/a") if isinstance(report.get("score"), dict) else "n/a",
                "missing_metrics": missing_count(report),
                "tags": assign_tags(report),
            }
            for report in reports
        ]
    }


def render_snapshot(reports: list[dict], tag_map: dict[str, list[str]]) -> str:
    ordered = sorted(reports, key=ranking_score, reverse=True)
    top_names = ordered[:3]
    flagged = [
        report for report in ordered
        if "needs-review" in tag_map.get(str(report.get("ticker", "")), []) or "high-risk" in tag_map.get(str(report.get("ticker", "")), [])
    ]
    lines = ["# Growth Watchlist Snapshot", "", "## Top Names"]
    if top_names:
        for report in top_names:
            lines.append(f"- {short_text(report.get('ticker'))}: {short_text(report.get('score_summary'), 'No score attached', 120)} | Rank score {ranking_score(report):.2f}")
    else:
        lines.append("- No reports provided")
    lines.extend(["", "## Needs Review"])
    if flagged:
        seen = set()
        for report in flagged:
            ticker = short_text(report.get("ticker"))
            if ticker in seen:
                continue
            seen.add(ticker)
            lines.append(f"- {ticker}: {', '.join(tag_map.get(ticker, [])) or 'n/a'}")
    else:
        lines.append("- No names currently flagged")
    lines.extend(["", "## Table", "", "| Ticker | Score | Rank | Tags | Risks |", "| --- | --- | --- | --- | --- |"])
    for report in ordered:
        ticker = short_text(report.get("ticker"))
        score = report.get("score") if isinstance(report.get("score"), dict) else {}
        score_text = f"{score.get('total_score', 'n/a')}/{score.get('max_score', 'n/a')}" if isinstance(score, dict) else "n/a"
        tags = ", ".join(tag_map.get(ticker, [])) or "n/a"
        lines.append(f"| {ticker} | {score_text} | {ranking_score(report):.2f} | {short_text(tags, 'n/a', 80)} | {short_text(report.get('key_risks'), 'n/a', 80)} |")
    lines.append("")
    lines.append("Use this snapshot for triage, then open the full report or dashboard for names that matter.")
    lines.append("")
    return "\n".join(lines)


def render_ranking(reports: list[dict]) -> str:
    ordered = sorted(reports, key=ranking_score, reverse=True)
    lines = ["# Growth Stock Ranking", "", "| Rank | Ticker | Score | Missing | Business quality | Growth durability |", "| --- | --- | --- | --- | --- | --- |"]
    for index, report in enumerate(ordered, start=1):
        score = report.get("score") or {}
        score_text = f"{score.get('total_score', 'n/a')}/{score.get('max_score', 'n/a')}" if isinstance(score, dict) else "n/a"
        lines.append("| " + " | ".join([str(index), short_text(report.get("ticker")), score_text, str(missing_count(report)), short_text(report.get("business_quality")), short_text(report.get("growth_durability"))]) + " |")
    lines.extend(["", "## Detail"])
    for report in ordered:
        lines.extend([
            f"### {short_text(report.get('ticker'))}",
            f"- Analysis date: {short_text(report.get('analysis_date'))}",
            f"- Score summary: {short_text(report.get('score_summary'), 'No score attached', 120)}",
            f"- Backtest summary: {short_text(report.get('backtest_summary'), 'No backtest attached', 120)}",
            f"- Key risks: {short_text(report.get('key_risks'), 'n/a', 120)}",
            f"- Valuation context: {short_text(report.get('valuation_context'), 'n/a', 120)}",
            f"- Ranking score: {ranking_score(report):.2f}",
            "",
        ])
    lines.append("Use this ranking as a triage view, then re-check live sources before making any decision.")
    lines.append("")
    return "\n".join(lines)


def build_dashboard_rows(reports: list[dict]) -> list[dict[str, str]]:
    ordered = sorted(reports, key=ranking_score, reverse=True)
    rows = []
    for index, report in enumerate(ordered, start=1):
        rows.append({
            "rank": str(index),
            "ticker": short_text(report.get("ticker")),
            "analysis_date": short_text(report.get("analysis_date")),
            "score_summary": short_text(report.get("score_summary"), "No score attached"),
            "ranking_score": f"{ranking_score(report):.2f}",
            "missing_metrics": str(missing_count(report)),
            "business_quality": short_text(report.get("business_quality")),
            "growth_durability": short_text(report.get("growth_durability")),
            "key_risks": short_text(report.get("key_risks")),
            "valuation_context": short_text(report.get("valuation_context")),
            "backtest_summary": short_text(report.get("backtest_summary"), "No backtest attached"),
        })
    return rows


def write_csv(path: str, rows: list[dict[str, str]]) -> None:
    fields = ["rank", "ticker", "analysis_date", "score_summary", "ranking_score", "missing_metrics", "business_quality", "growth_durability", "key_risks", "valuation_context", "backtest_summary"]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_html(path: str, rows: list[dict[str, str]]) -> None:
    header = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Growth Stock Watchlist</title>
  <style>
    :root { --bg:#f5f1e8; --card:#fffaf2; --ink:#1f2937; --muted:#6b7280; --line:#d6c7ae; --accent:#0f766e; --accent-soft:#d1fae5; }
    body { margin:0; font-family:Georgia, "Times New Roman", serif; color:var(--ink); background:radial-gradient(circle at top left, #fff7ed, var(--bg)); }
    main { max-width:1200px; margin:0 auto; padding:32px 20px 48px; }
    h1 { margin:0 0 8px; font-size:2rem; }
    p { color:var(--muted); max-width:760px; }
    table { width:100%; border-collapse:collapse; background:var(--card); border:1px solid var(--line); box-shadow:0 12px 30px rgba(31, 41, 55, 0.08); }
    th,td { padding:12px 10px; border-bottom:1px solid var(--line); vertical-align:top; text-align:left; font-size:0.95rem; }
    th { background:#f7efe2; position:sticky; top:0; }
    .rank { font-weight:bold; color:var(--accent); }
    .score { display:inline-block; padding:4px 8px; border-radius:999px; background:var(--accent-soft); color:var(--accent); font-weight:600; }
  </style>
</head>
<body>
  <main>
    <h1>Growth Stock Watchlist</h1>
    <p>Use this dashboard as a triage surface. Re-check live filings, prices, and catalysts before making any investment decision.</p>
    <table>
      <thead><tr><th>Rank</th><th>Ticker</th><th>Date</th><th>Score</th><th>Rank Score</th><th>Missing</th><th>Business</th><th>Growth</th><th>Risks</th><th>Valuation</th><th>Backtest</th></tr></thead>
      <tbody>
"""
    body = []
    for row in rows:
        body.append(
            "        <tr>"
            f"<td class=\"rank\">{html.escape(row['rank'])}</td>"
            f"<td>{html.escape(row['ticker'])}</td>"
            f"<td>{html.escape(row['analysis_date'])}</td>"
            f"<td><span class=\"score\">{html.escape(row['score_summary'])}</span></td>"
            f"<td>{html.escape(row['ranking_score'])}</td>"
            f"<td>{html.escape(row['missing_metrics'])}</td>"
            f"<td>{html.escape(row['business_quality'])}</td>"
            f"<td>{html.escape(row['growth_durability'])}</td>"
            f"<td>{html.escape(row['key_risks'])}</td>"
            f"<td>{html.escape(row['valuation_context'])}</td>"
            f"<td>{html.escape(row['backtest_summary'])}</td>"
            "</tr>"
        )
    footer = """
      </tbody>
    </table>
  </main>
</body>
</html>
"""
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(header + "\n".join(body) + footer)
