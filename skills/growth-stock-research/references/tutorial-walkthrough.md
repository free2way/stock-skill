# Tutorial Walkthrough

Use this walkthrough when learning the skill end to end for the first time.

## What you are building

A repeatable growth-stock research loop:

1. collect current text inputs
2. extract or normalize metrics
3. review and confirm evidence
4. score the business and stock setup
5. fetch price history
6. run a baseline backtest
7. assemble report JSON files
8. rank, tag, and export the watchlist

## Fastest practice path

1. Copy `assets/sample-data/` into a writable scratch folder.
2. Run `scripts/run_growth_pipeline.py` on that copied folder.
3. Open the generated:
   - snapshot
   - ranking
   - CSV watchlist
   - HTML watchlist
4. Generate an evidence template and manually confirm a few key fields.
5. Read the sample reports and manifest to understand the input format.

## Real-world path

1. Create one folder per review cycle in your workspace.
2. Save a plain-text summary for each stock using the latest investor materials.
3. Write a short `notes.json` for each stock.
4. Generate and review evidence annotations for the key metrics.
5. Fetch prices and run a consistent backtest rule.
6. Assemble one `report.json` per stock.
7. Run batch ranking, tags, snapshot, and dashboard exports.

## Important judgment calls

- Not every company discloses every scorecard field directly.
- Infrastructure and pre-profit companies often require normalized workflow inputs.
- Treat normalized inputs as internal research scaffolding, not audited truth.
- Keep a note of where you inferred, approximated, or proxied a metric.
- Low evidence scores should lower conviction even when the thesis sounds good.

## Suggested cadence

- After each earnings release: refresh that company report
- Weekly: regenerate snapshot and dashboard
- Monthly: re-check notes, tags, and rankings

## Common mistakes

- Mixing stale price data with fresh fundamentals
- Letting missing metrics silently turn into false certainty
- Treating the ranking table as a final investment decision
- Forgetting to save a dated copy before updating a report
