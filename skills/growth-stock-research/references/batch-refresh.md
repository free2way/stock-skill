# Batch Refresh

Use this reference when many existing `report.json` files need to be refreshed at once.

## Goal

Make earnings-season updates boring and repeatable.

## Manifest Format

Create a JSON array. Each item should contain:

- `report`
- `input`

Optional fields:

- `output`
- `analysis_date`

Example:

```json
[
  {
    "report": "data/nbis_report.json",
    "input": "data/nbis_q1_2026.txt",
    "output": "data/nbis_report.json"
  },
  {
    "report": "data/iren_report.json",
    "input": "data/iren_q3_2026.txt",
    "output": "data/iren_report.json"
  }
]
```

If an item omits `output`, the script overwrites the original `report` path.

## Global Analysis Date

Pass `--analysis-date` when all entries belong to the same review cycle. If an item has its own `analysis_date`, that entry-specific value wins.

## Workflow

1. Gather new quarterly text for each company.
2. Build the manifest.
3. Run the batch refresh script.
4. Review any warnings or missing metrics.
5. Re-export rankings and dashboards.
