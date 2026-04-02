---
name: growth-stock-research
description: Analyze U.S. growth stocks with a repeatable first-principles framework, peer comparison, risk review, and lightweight backtesting. Use when Codex needs to evaluate companies such as SaaS, semis, AI infrastructure, consumer internet, or other high-growth equities; compare bull and bear cases; translate a narrative thesis into measurable drivers; download local historical price data; or run a simple price- or signal-based backtest from CSV data.
---

# Growth Stock Research

Use this skill to turn a stock question into a falsifiable research process.

## Core Workflow

1. Anchor the analysis date.
   Use exact dates, not relative phrases. If the user says "today", restate the actual calendar date and the latest completed U.S. trading session.

2. Frame the company from first principles.
   Reduce the business to:
   - demand driver
   - product or capacity bottleneck
   - pricing power
   - unit economics
   - reinvestment needs
   - reasons growth may persist or fade

3. Gather evidence in layers.
   Start with the latest company filings, earnings material, and investor updates. Then add market data, major customer or supplier news, and peer context. Prefer current primary sources whenever the question depends on the latest facts.

4. Score the thesis, not just the story.
   For each name, make explicit judgments on:
   - revenue growth durability
   - gross margin direction
   - operating leverage potential
   - dilution or financing risk
   - customer concentration
   - cyclicality
   - valuation support

   Use an industry-specific scorecard whenever possible. Do not compare SaaS, AI infrastructure, optical components, and satellite infrastructure under one generic threshold set.

5. Convert the thesis into triggers.
   Define what would confirm or break the thesis over the next 2-4 quarters. A good stock writeup should have specific leading indicators, not only a conclusion.

6. Backtest only what can be operationalized.
   Do not pretend to backtest vague narratives. Convert the idea into either:
   - a price rule with one of the built-in strategies, or
   - a dated signal series in CSV form
   - a dated event series for forward-return studies

## Analysis Structure

Use this compact structure unless the user asks for something else:

1. Thesis in one paragraph
2. What the market may be underpricing
3. What can go wrong
4. Key metrics to watch
5. Valuation or positioning context
6. Decision: more attractive / less attractive / watch only

When comparing multiple names, force symmetry. Evaluate the same dimensions for each company before giving a conclusion.

## Growth Stock Checklist

Always check these items when the data is available:

- Revenue growth: year-over-year and sequential deceleration or acceleration
- Gross margin: structural trend versus temporary mix effects
- Operating expenses: whether scaling is disciplined or growth is being bought
- SBC and dilution: use share count, not only EPS
- FCF quality: separate true cash generation from working-capital swings
- Balance sheet: cash runway, debt maturities, convertibles, funding needs
- Customer concentration: who the top buyers are and how replaceable they are
- Capacity constraints: chips, power, datacenter slots, ad load, merchant acquisition, etc.
- Competitive response: incumbents, price cuts, copycat products, regulation

## Backtesting Rules

Use backtests as a decision aid, not proof.

- Prefer signal-based backtests for thesis validation.
- Use built-in price rules only as a baseline sanity check.
- State the input data period, execution assumption, and limitations.
- Never claim a backtest validates a company-specific fundamental thesis unless the signals encode those fundamentals.

For a deterministic local backtest, use:

```bash
python3 scripts/fetch_price_history.py --ticker NBIS --years 3 --output data/NBIS.csv
python3 scripts/extract_growth_metrics.py --input data/nbis_q4_2025.txt --ticker NBIS --analysis-date 2026-04-02 --output data/nbis_metrics.json
python3 scripts/build_signals_template.py --events data/nbis_events.csv --output data/nbis_signals.csv
python3 scripts/event_returns.py --prices data/NBIS.csv --events data/nbis_events.csv --benchmark data/QQQ.csv
python3 scripts/relative_strength.py --prices data/NBIS.csv --benchmark data/QQQ.csv
python3 scripts/score_growth_stock.py --input data/nbis_metrics.json --profile ai_infra
python3 scripts/generate_evidence_template.py --input data/nbis_metrics.json --output data/nbis_evidence_annotations.json
python3 scripts/apply_evidence_annotations.py --input data/nbis_metrics.json --annotations data/nbis_evidence_annotations.json --output data/nbis_metrics_reviewed.json
python3 scripts/evidence_quality.py --input data/nbis_metrics.json --json
python3 scripts/valuation_engine.py --input data/nbis_valuation.json --json
python3 scripts/backtest_growth_stock.py --prices data/stock.csv --strategy breakout-252
python3 scripts/backtest_growth_stock.py --prices data/stock.csv --signals data/signals.csv --benchmark data/spy.csv --json
python3 scripts/assemble_growth_report.py --ticker NBIS --analysis-date 2026-04-02 --metrics data/nbis_metrics.json --score data/nbis_score.json --valuation data/nbis_valuation_snapshot.json --evidence data/nbis_evidence.json --event-study data/nbis_event_study.json --relative-strength data/nbis_relative_strength.json --backtest data/nbis_backtest.json --notes data/nbis_notes.json --output data/nbis_report.json
python3 scripts/compare_growth_stocks.py --left data/nbis_report.json --right data/iren_report.json --output comparison.md
python3 scripts/batch_compare_growth_stocks.py --reports data/nbis_report.json data/iren_report.json data/crwv_report.json --output ranking.md
python3 scripts/export_growth_dashboard.py --reports data/nbis_report.json data/iren_report.json data/crwv_report.json --csv watchlist.csv --html watchlist.html
python3 scripts/update_report_from_text.py --report data/nbis_report.json --input data/nbis_q1_2026.txt --analysis-date 2026-05-08 --output data/nbis_report.json
python3 scripts/batch_refresh_reports.py --manifest data/refresh_manifest.json --analysis-date 2026-05-08
python3 scripts/report_diff.py --old data/nbis_report_2026-04-02.json --new data/nbis_report_2026-05-08.json --output data/nbis_diff.md
python3 scripts/tag_watchlist.py --reports data/nbis_report.json data/iren_report.json data/crwv_report.json --output data/watchlist_tags.json
python3 scripts/export_growth_snapshot.py --reports data/nbis_report.json data/iren_report.json data/crwv_report.json --tags data/watchlist_tags.json --output data/watchlist_snapshot.md
python3 scripts/run_growth_pipeline.py --manifest data/refresh_manifest.json --analysis-date 2026-05-08 --reports data/nbis_report.json data/iren_report.json data/crwv_report.json --tags-out data/watchlist_tags.json --snapshot-out data/watchlist_snapshot.md --ranking-out data/watchlist_ranking.md --csv-out data/watchlist.csv --html-out data/watchlist.html
```

Read [references/framework.md](references/framework.md) when building the investment case.
Read [references/backtesting.md](references/backtesting.md) before using or extending the backtest script.
Read [references/event-study.md](references/event-study.md) when testing forward returns after earnings, financing, or customer events.
Read [references/relative-strength.md](references/relative-strength.md) when testing whether a stock actually outperformed its benchmark.
Read [references/output-template.md](references/output-template.md) when you need a full writeup format.
Read [references/signals-template.md](references/signals-template.md) when mapping thesis events into dated signals.
Read [references/report-schema.md](references/report-schema.md) when creating report JSON files for comparison or automation.
Read [references/metrics-extraction.md](references/metrics-extraction.md) when extracting a scorecard from earnings text.
Read [references/industry-scorecards.md](references/industry-scorecards.md) when selecting the correct business-model scorecard.
Read [references/valuation.md](references/valuation.md) when you need a transparent valuation snapshot.
Read [references/evidence-quality.md](references/evidence-quality.md) when checking how trustworthy the extracted metrics really are.
Read [references/evidence-annotations.md](references/evidence-annotations.md) when manually upgrading evidence quality after source review.
Read [references/report-assembly.md](references/report-assembly.md) when combining research artifacts into a final report JSON.
Read [references/batch-comparison.md](references/batch-comparison.md) when ranking or comparing many growth-stock reports at once.
Read [references/dashboard-export.md](references/dashboard-export.md) when exporting a watchlist CSV or HTML dashboard.
Read [references/report-update.md](references/report-update.md) when incrementally updating an existing report from new earnings text.
Read [references/batch-refresh.md](references/batch-refresh.md) when refreshing many existing reports during earnings season.
Read [references/report-diff.md](references/report-diff.md) when comparing two versions of the same stock report.
Read [references/watchlist-tags.md](references/watchlist-tags.md) when applying management tags across a watchlist.
Read [references/growth-snapshot.md](references/growth-snapshot.md) when generating a short watchlist summary for daily or weekly review.
Read [references/pipeline.md](references/pipeline.md) when running the whole watchlist maintenance flow in one command.
Read [references/sample-data.md](references/sample-data.md) when you want a minimal example dataset to practice with.

## Output Guidance

Be crisp and explicit.

- Separate facts from inference.
- Attach dates to claims.
- Distinguish business quality from stock attractiveness.
- If the analysis depends on fresh market or filing data, browse and cite sources.
- If the data is missing for a robust conclusion, say what is missing and how that affects confidence.

## Common Workflows

### 1. Fresh stock analysis

1. Restate the exact analysis date.
2. Gather the latest company filings, investor letter, and key news.
3. Build the thesis with the framework reference.
4. Output the conclusion using the report template.

### 2. Thesis plus baseline backtest

1. Download local price history with `scripts/fetch_price_history.py`.
2. Run a baseline trend rule with `scripts/backtest_growth_stock.py`.
3. Explain why the price-rule result is only a baseline.
4. If possible, propose a better signal CSV tied to fundamentals.

### 3. Signal-driven validation

1. Encode dated thesis changes into a `signals.csv` file.
2. Backtest those signals against the stock and optionally a benchmark.
3. Report what the rule captures and what it still misses.

### 4. Event-study validation

1. Encode dated thesis events into an `events.csv` file.
2. Run `scripts/event_returns.py` against the stock and optionally a benchmark.
3. Review forward returns by stance and horizon.
4. Ask whether bullish events actually led to positive drift and whether bearish events led to downside or underperformance.

### 5. Relative-strength review

1. Pick a benchmark that matches the question, such as `QQQ`, `SPY`, or a peer basket proxy.
2. Run `scripts/relative_strength.py`.
3. Check current and rolling relative returns over 20/60/120/252-day windows.
4. Use the result to separate leadership from simple beta participation.

### 6. Two-stock research packet

1. Research each company separately.
2. Save the key outputs as JSON report files.
3. Use `scripts/compare_growth_stocks.py` to create a first draft comparison.
4. Refine the narrative with fresh sources and judgment.

### 7. Scorecard-driven review

1. Extract a compact metrics JSON from filings or earnings materials.
2. Set `industry_profile` in the metrics JSON, or override it explicitly at the CLI.
3. Use `scripts/extract_growth_metrics.py` for a first pass if the source is plain text or markdown.
4. Re-check any auto-extracted metrics and add the missing profile by hand when needed.
5. Score it with `scripts/score_growth_stock.py`.
6. Use the score as a consistency check, not as a substitute for judgment.

### 8. Final report assembly

1. Create or gather `metrics.json`, `score.json`, `backtest.json`, and optional analyst notes.
2. Run `scripts/assemble_growth_report.py` to build a normalized report artifact.
3. Use that report for comparisons, batch work, or further narrative refinement.

### 9. Batch ranking

1. Assemble one report JSON per stock.
2. Run `scripts/batch_compare_growth_stocks.py` across the report set.
3. Review the ranking table as a triage tool, then inspect the top names manually.

### 10. Watchlist export

1. Assemble one report JSON per stock.
2. Run `scripts/export_growth_dashboard.py` to produce CSV and HTML outputs.
3. Refresh the dashboard whenever new earnings, backtests, or notes change the reports.

### 11. Incremental refresh

1. Start from an existing `report.json`.
2. Feed new earnings or event text into `scripts/update_report_from_text.py`.
3. Review the merged metrics and refreshed score before exporting the watchlist again.

### 12. Earnings-season batch refresh

1. Create a manifest listing each existing report and its new source text.
2. Run `scripts/batch_refresh_reports.py` once for the whole batch.
3. Re-export rankings and dashboard outputs from the refreshed reports.

### 13. Report diff

1. Keep the old report snapshot before refreshing.
2. Compare the old and new reports with `scripts/report_diff.py`.
3. Review metric deltas and score changes before updating your narrative view.

### 14. Watchlist tagging

1. Refresh or assemble the latest `report.json` files.
2. Run `scripts/tag_watchlist.py` across the report set.
3. Use the tags to sort your watchlist into investigate / monitor / avoid buckets.

### 15. Snapshot export

1. Refresh reports and tags.
2. Run `scripts/export_growth_snapshot.py`.
3. Read the snapshot first, then drill into the full dashboard only when needed.

### 16. One-command pipeline

1. Prepare a refresh manifest and the list of current report files.
2. Run `scripts/run_growth_pipeline.py`.
3. Review the snapshot first, then the ranking and dashboard outputs.
