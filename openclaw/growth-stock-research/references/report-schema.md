# Report Schema

Use this reference when storing a single-stock research packet as JSON.

## Goal

Keep the schema small enough to fill manually, but structured enough for scripts to compare and summarize.

## Recommended Fields

Required fields:

- `ticker`
- `analysis_date`
- `business_quality`
- `growth_durability`
- `key_risks`
- `valuation_context`

Optional but recommended:

- `better_business`
- `better_stock`
- `higher_upside`
- `lower_risk`
- `backtest_summary`
- `score_summary`
- `notes`

## Example

```json
{
  "ticker": "NBIS",
  "analysis_date": "2026-04-02",
  "business_quality": "AI infrastructure platform with strong partners and visible capacity demand.",
  "growth_durability": "High if customer ramps and capacity additions continue.",
  "key_risks": "Capex intensity, customer concentration, valuation.",
  "valuation_context": "Premium multiple with elevated execution expectations.",
  "score_summary": "Overall 76/100. Strong growth and balance sheet, weaker capital intensity score.",
  "backtest_summary": "Momentum-126 from 2025-04-01 to 2026-04-01 returned -8.34%.",
  "notes": "Revisit after next earnings and any new financing update."
}
```

## Writing Guidance

- Store concise summaries, not full essays.
- Keep dates explicit.
- Use strings for narrative fields.
- Treat the JSON as an intermediate artifact that other scripts can read.
