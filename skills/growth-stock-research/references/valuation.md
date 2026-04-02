# Valuation Engine

Use this reference when turning a growth-stock narrative into a transparent valuation snapshot.

## Goal

Separate:

- business quality
- valuation support
- implied upside or downside

The valuation engine is intentionally simple and auditable. It is not a full DCF and it is not a black-box target price.

## What It Does

`scripts/valuation_engine.py` calculates:

- current `EV / Sales`
- current `EV / Gross Profit`
- current `FCF yield` when FCF data exists
- profile-aware bear / base / bull multiple bands
- implied enterprise value and equity return scenarios

It uses the same `industry_profile` logic as the v2 scorecard.

## Recommended Input

You can point it at either:

- a compact valuation JSON
- or a full `report.json` that contains `metrics` and `valuation_inputs`

Best practice is to include:

- `ticker`
- `analysis_date`
- `industry_profile`
- `market_cap`
- `enterprise_value`
- `revenue_next_12m` or `revenue`
- `gross_profit_next_12m` or `gross_profit`
- `fcf_next_12m` or `fcf`
- `net_cash`

If some fields are missing, the engine tries reasonable derivations:

- derive gross profit from `revenue * gross_margin`
- derive FCF from `revenue * fcf_margin`
- derive market cap from `enterprise_value + net_cash`
- derive enterprise value from `market_cap - net_cash`

## Example

```json
{
  "ticker": "NBIS",
  "analysis_date": "2026-04-02",
  "industry_profile": "ai_infra",
  "market_cap": 28000000000,
  "enterprise_value": 25500000000,
  "revenue_next_12m": 3500000000,
  "gross_margin": 64,
  "fcf_margin": -6,
  "net_cash": 2500000000,
  "metrics": {
    "revenue_growth_yoy": 58,
    "gross_margin": 64,
    "fcf_margin": -6
  }
}
```

Run:

```bash
python3 scripts/valuation_engine.py --input data/nbis_valuation.json --json
```

## Interpretation Rules

- Use the output to ask what growth and margins are already priced in.
- Do not treat the base case as a price target.
- Compare the scenario bands against peers, not just against the stock's own history.
- For capital-intensive businesses, cross-check EV/Sales and EV/Gross Profit against asset productivity.

## Limits

This version still does not include:

- full DCFs
- dilution-forward share count modeling
- sum-of-the-parts valuation
- macro regime conditioning
- peer regression models

That is acceptable for triage. It is not sufficient for a final institutional model.
