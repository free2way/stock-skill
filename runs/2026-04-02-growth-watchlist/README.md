# 2026-04-02 Growth Watchlist Run

This run applies the skill workflow to:

- NBIS
- IREN
- CRWV
- ASTS
- AAOI

The run directory is organized as:

- `inputs/` plain-text source summaries for the scorecard workflow
- `notes/` narrative notes used in report assembly
- `prices/` downloaded daily price history
- `metrics/` extracted metrics JSON
- `scores/` scorecard JSON
- `backtests/` backtest JSON
- `reports/` assembled report JSON
- `outputs/` ranking, tags, snapshot, CSV, and HTML artifacts

Some metric inputs are normalized workflow values so the scorecard can run consistently across very different business models. Treat those as internal research scaffolding, not audited financial statements.
