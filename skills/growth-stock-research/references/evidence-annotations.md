# Evidence Annotations

Use this workflow when you want to upgrade evidence quality from machine-extracted draft data to analyst-reviewed data.

## Goal

Make evidence review a standard step, not an ad hoc JSON edit.

## Scripts

Generate a template:

```bash
python3 scripts/generate_evidence_template.py --input data/nbis_metrics.json --output data/nbis_evidence_annotations.json
```

Apply the annotations:

```bash
python3 scripts/apply_evidence_annotations.py --input data/nbis_metrics.json --annotations data/nbis_evidence_annotations.json --output data/nbis_metrics_reviewed.json
```

Then re-score evidence quality:

```bash
python3 scripts/evidence_quality.py --input data/nbis_metrics_reviewed.json --json
```

## What The Analyst Should Fill

For each critical field, try to fill:

- `source_type`
- `source_date`
- `period`
- `manually_confirmed`
- `gaap_basis`
- `citation`

Good examples:

- `source_type: "10-Q"`
- `source_date: "2026-02-12"`
- `period: "Q4 FY2025"`
- `manually_confirmed: true`
- `gaap_basis: "GAAP"`

## Recommended Rule

Manually confirm at least these fields before relying on the report:

- `revenue_growth_yoy`
- `gross_margin`
- `fcf_margin`
- `share_dilution_yoy`
- `top_customer_share`

For capital-intensive names, also confirm:

- `capex_to_revenue`
- `net_cash_to_revenue`

## Why This Matters

Without annotations, the evidence layer should stay skeptical.

That is a feature, not a bug. The system should force higher confidence to be earned through source review.
