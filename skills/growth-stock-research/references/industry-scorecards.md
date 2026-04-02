# Industry Scorecards

Use this reference when scoring growth stocks with `scripts/score_growth_stock.py` or any report refresh flow.

## Why This Exists

One-size-fits-all growth scorecards are misleading.

- SaaS businesses should be judged on margin structure and dilution discipline.
- AI infrastructure names need more tolerance for capex but less tolerance for customer concentration.
- Optical networking names are more cyclical and should be judged against lower margin norms.
- Satellite and telecom infrastructure names live or die on balance-sheet runway and funding risk.

The v2 score engine therefore uses an explicit `industry_profile`.

## Supported Profiles

- `generic_growth`
  Use only as a fallback when you do not yet know the right business model.

- `saas`
  Best for subscription software, recurring-revenue platforms, and mature cloud applications.

- `ai_infra`
  Best for GPU cloud, neocloud, AI datacenter capacity, and infrastructure-heavy AI platforms.

- `optical_networking`
  Best for optical components, networking hardware, and semis-like infrastructure suppliers.

- `satellite_telecom`
  Best for satellite broadband, telecom infrastructure, and capital-intensive network buildouts.

## How To Set The Profile

Preferred: store the profile in the metrics JSON.

```json
{
  "ticker": "NBIS",
  "industry_profile": "ai_infra",
  "revenue_growth_yoy": 58,
  "gross_margin": 64,
  "fcf_margin": -6,
  "net_cash_to_revenue": 0.72,
  "share_dilution_yoy": 3.5,
  "top_customer_share": 28,
  "capex_to_revenue": 0.85,
  "rule_of_40": 52
}
```

You can also override from the command line:

```bash
python3 scripts/score_growth_stock.py --input data/nbis_metrics.json --profile ai_infra
```

## Profile Selection Heuristics

- Use `saas` when gross margin and recurring software economics are core to the business.
- Use `ai_infra` when capital deployment, power, compute utilization, and customer concentration matter more than short-term FCF.
- Use `optical_networking` when cycle position, hyperscaler demand, and hardware margin swings matter.
- Use `satellite_telecom` when liquidity runway and deployment milestones dominate the thesis.

## Interpretation Rules

- Treat the score as a consistency check, not a price target.
- Do not compare two names across sectors unless both use the correct industry profile.
- If a name only works under `generic_growth`, your profile selection is probably under-specified.
- Always read the `limitations` field in the score output before relying on the result.

## Important Limits

Even the industry-aware v2 engine still misses sector-critical variables such as:

- SaaS: NRR, CAC payback, churn, multi-product adoption
- AI infra: GPU utilization, contract duration, power pipeline, customer credit risk
- Optical networking: inventory digestion, design-win durability, pricing pressure
- Satellite / telecom: launch cadence, regulatory milestones, financing windows

Use the scorecard to structure thinking, then add these missing variables manually.
