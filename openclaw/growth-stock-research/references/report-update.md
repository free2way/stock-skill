# Report Update

Use this reference when you already have a `report.json` and want to refresh it with new text.

## Goal

Avoid rebuilding the full report from scratch when only one quarter or one event has changed.

## What the updater does

- reads the existing report
- extracts a fresh first-pass metrics block from new text
- merges extracted values into the existing metrics
- refreshes the score and score summary
- updates the analysis date

## Merge policy

The updater is intentionally conservative:

- new extracted numeric fields overwrite old values when present
- existing fields stay in place when the new text does not mention them
- narrative fields are preserved unless you edit them separately

## Best use cases

- quarterly earnings refresh
- new investor letter
- short event summary after a financing or customer announcement

## Review checklist

- Confirm that the extracted quarter matches the intended period.
- Check any derived ratios such as `capex_to_revenue`.
- Re-read `sources` if a number looks suspicious.
- If the thesis changed materially, update notes separately after the refresh.
