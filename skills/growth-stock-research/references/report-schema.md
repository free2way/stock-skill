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
- `valuation_summary`
- `evidence_summary`
- `event_study_summary`
- `relative_strength_summary`
- `notes`
- `score.profile`
- `score.score_version`
- `valuation.profile`
- `valuation.valuation_version`
- `evidence_quality.evidence_version`
- `event_study.event_study_version`
- `relative_strength.relative_strength_version`
- `metrics.industry_profile`

## Example

```json
{
  "ticker": "NBIS",
  "analysis_date": "2026-04-02",
  "business_quality": "AI infrastructure platform with strong partners and visible capacity demand.",
  "growth_durability": "High if customer ramps and capacity additions continue.",
  "key_risks": "Capex intensity, customer concentration, valuation.",
  "valuation_context": "Premium multiple with elevated execution expectations.",
  "score_summary": "Overall 76/100 (strong) using the AI Infrastructure / Neocloud scorecard.",
  "score": {
    "profile": "ai_infra",
    "score_version": "v2-industry-aware"
  },
  "valuation_summary": "Current EV/Sales 7.29x; base-case fair EV/Sales 5.90x; base implied return -16.4%.",
  "valuation": {
    "profile": "ai_infra",
    "valuation_version": "v1-transparent-scenarios"
  },
  "evidence_summary": "Evidence quality 0.71/1.00 (medium). Lowest-confidence fields: rule_of_40, capex_to_revenue.",
  "evidence_quality": {
    "evidence_version": "v1-source-confidence"
  },
  "event_study_summary": "Event study: bullish 20d mean 30.33%; bearish 20d mean 0.24%; 3 event(s).",
  "relative_strength_summary": "Relative strength: 20d rel 8.59%; 60d rel 15.27%; 120d rel -12.00%.",
  "metrics": {
    "industry_profile": "ai_infra"
  },
  "backtest_summary": "Momentum-126 from 2025-04-01 to 2026-04-01 returned -8.34%.",
  "notes": "Revisit after next earnings and any new financing update."
}
```

## Writing Guidance

- Store concise summaries, not full essays.
- Keep dates explicit.
- Use strings for narrative fields.
- Store `industry_profile` whenever you want the score to be decision-useful.
- Treat the JSON as an intermediate artifact that other scripts can read.
