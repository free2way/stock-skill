# Evidence Quality

Use this reference when you need to judge whether a metric is merely present or actually trustworthy.

## Why It Matters

Growth-stock research breaks when low-quality data produces high-confidence conclusions.

The evidence-quality layer helps separate:

- filed facts
- management claims
- machine-extracted snippets
- derived metrics
- manually confirmed numbers

## Script

Use:

```bash
python3 scripts/evidence_quality.py --input data/nbis_metrics.json --json
```

The input may be:

- a `metrics.json`
- or a `report.json` that contains `metrics`

## Current Output

The script emits:

- `overall_confidence_score`
- `overall_confidence_label`
- one item per field with:
  - `source_type`
  - `source_date`
  - `period`
  - `is_machine_extracted`
  - `manually_confirmed`
  - `is_derived`
  - `citation`
  - field-level confidence

## Source-Type Guidance

Best to worst, roughly:

- `10-K`, `10-Q`, `20-F`
- `8-K`, earnings release
- shareholder letter, prepared remarks
- investor presentation
- news article or secondary summary
- analyst note
- manual estimate
- unknown

## Practical Workflow

1. Run the extractor or build the metrics JSON manually.
2. Add or patch `metrics.evidence` for the most important fields.
3. Run `scripts/evidence_quality.py`.
4. Carry the result into `assemble_growth_report.py`.
5. Downgrade confidence when the evidence summary is weak.

## Limits

This version still scores metadata quality, not semantic correctness.

That means:

- it can tell you a value came from a filing
- it cannot yet verify the value was parsed with the right accounting context

So use it as a confidence floor, not as a substitute for analyst review.
