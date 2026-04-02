# Report Assembly

Use this reference when turning separate research artifacts into one report JSON.

## Goal

Produce a single normalized artifact that downstream tools can compare, rank, or render.

## Inputs

The assembly script can combine:

- `metrics.json`
- `score.json`
- `backtest.json`
- `notes.json`

Only `ticker`, `analysis_date`, and `output` are required at the CLI level. The other files are optional but strongly recommended.

## Notes JSON

Use a small hand-written JSON file for narrative conclusions.

Recommended fields:

- `business_quality`
- `growth_durability`
- `key_risks`
- `valuation_context`
- `better_business`
- `better_stock`
- `higher_upside`
- `lower_risk`
- `notes`

## Assembly Principles

- Preserve machine-readable metrics and score details.
- Add concise narrative summaries.
- Derive `backtest_summary` from the backtest file when available.
- Carry forward missing fields as explicit placeholders rather than inventing certainty.

## Recommended Workflow

1. Extract metrics.
2. Score the company.
3. Run a baseline or signal-driven backtest when appropriate.
4. Write short analyst notes.
5. Assemble the report.
6. Compare reports across names.
