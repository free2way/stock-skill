---
name: growth-stock-research
description: Analyze U.S. growth stocks with a repeatable first-principles workflow, peer comparison, lightweight backtesting, batch ranking, watchlist tagging, and dashboard exports. Use when evaluating high-growth equities such as AI infrastructure, SaaS, semis, networking, communications, or adjacent growth names; when converting a narrative thesis into measurable drivers; or when maintaining a repeatable watchlist review process.
---

# Growth Stock Research

Use this skill to turn a stock question into a falsifiable research process.

## Core workflow

1. Anchor the analysis date.
   Restate the exact calendar date and the latest completed U.S. trading session.

2. Reduce the company to first principles.
   Focus on:
   - demand driver
   - supply or capacity bottleneck
   - pricing power
   - unit economics
   - reinvestment needs
   - reasons growth may persist or fade

3. Build evidence from current primary sources first.
   Prefer the latest earnings release, shareholder letter, filing, and investor update before adding secondary coverage.

4. Score the setup, not just the story.
   Make explicit judgments on:
   - revenue growth durability
   - margin quality
   - dilution or financing risk
   - customer concentration
   - cyclicality
   - valuation support

5. Backtest only what can be operationalized.
   Use either:
   - a built-in price rule for a baseline sanity check
   - a dated signal CSV for thesis-driven validation

6. Convert the work into durable artifacts.
   Prefer creating:
   - `metrics.json`
   - `score.json`
   - `backtest.json`
   - `report.json`

## Key resources

- Framework: `{baseDir}/references/framework.md`
- Backtesting guidance: `{baseDir}/references/backtesting.md`
- Output template: `{baseDir}/references/output-template.md`
- Signals template: `{baseDir}/references/signals-template.md`
- Report schema: `{baseDir}/references/report-schema.md`
- Metrics extraction: `{baseDir}/references/metrics-extraction.md`
- Report assembly: `{baseDir}/references/report-assembly.md`
- Batch comparison: `{baseDir}/references/batch-comparison.md`
- Batch refresh: `{baseDir}/references/batch-refresh.md`
- Watchlist tags: `{baseDir}/references/watchlist-tags.md`
- Snapshot export: `{baseDir}/references/growth-snapshot.md`
- Pipeline guide: `{baseDir}/references/pipeline.md`
- Tutorial walkthrough: `{baseDir}/references/tutorial-walkthrough.md`
- Sample data guide: `{baseDir}/references/sample-data.md`

## Main scripts

- Fetch historical prices:
  `{baseDir}/scripts/fetch_price_history.py`

- Extract a first-pass metrics JSON from plain text:
  `{baseDir}/scripts/extract_growth_metrics.py`

- Score a normalized metrics JSON:
  `{baseDir}/scripts/score_growth_stock.py`

- Build dated signals from event rows:
  `{baseDir}/scripts/build_signals_template.py`

- Run a baseline or signal-based backtest:
  `{baseDir}/scripts/backtest_growth_stock.py`

- Assemble a normalized report:
  `{baseDir}/scripts/assemble_growth_report.py`

- Refresh an existing report from fresh text:
  `{baseDir}/scripts/update_report_from_text.py`

- Compare two reports:
  `{baseDir}/scripts/compare_growth_stocks.py`

- Rank a watchlist batch:
  `{baseDir}/scripts/batch_compare_growth_stocks.py`

- Tag a watchlist:
  `{baseDir}/scripts/tag_watchlist.py`

- Export snapshot or dashboard outputs:
  `{baseDir}/scripts/export_growth_snapshot.py`
  `{baseDir}/scripts/export_growth_dashboard.py`

- Run the end-to-end maintenance pipeline:
  `{baseDir}/scripts/run_growth_pipeline.py`

## Practical usage

For a quick manual workflow:

1. Save current notes or earnings text for a company.
2. Extract metrics with `extract_growth_metrics.py`.
3. Score the resulting metrics JSON.
4. Fetch one year of prices and run a baseline backtest.
5. Assemble a report JSON.
6. Repeat for peers, then run ranking, tags, and snapshot exports.

For recurring watchlist maintenance:

1. Keep one `report.json` per stock.
2. Refresh reports after earnings with `update_report_from_text.py` or `batch_refresh_reports.py`.
3. Rebuild tags, ranking, snapshot, CSV, and HTML outputs.

## Important cautions

- Separate facts from inference.
- Attach dates to claims.
- Distinguish business quality from stock attractiveness.
- Treat normalized workflow inputs as research scaffolding, not audited truth.
- Treat ranking and tags as triage aids, not final investment decisions.
