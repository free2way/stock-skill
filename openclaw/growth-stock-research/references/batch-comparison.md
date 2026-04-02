# Batch Comparison

Use this reference when comparing several growth-stock reports at once.

## Goal

Create a triage view, not a final investment decision.

The batch comparison script is designed to answer:

- Which names look strongest on the current scorecard?
- Which names have cleaner narratives?
- Which names have more obvious risk flags?

It should help narrow the list before deeper manual work.

## Ranking Logic

The script prefers transparent components:

- score ratio when a scorecard exists
- lighter penalties for missing metrics
- narrative summaries carried through unchanged

It does not infer valuation quality from prose and does not read live market prices.

## Output

The markdown output includes:

- a ranking table
- score summary
- metrics completeness
- backtest summary if present
- short narrative fields for quality, growth durability, and risks

## Interpretation Guidance

- Treat high rank as "investigate first", not "buy first".
- Compare the ranking with your own thesis. If they differ, ask why.
- Missing data should reduce confidence, not automatically eliminate a stock.
