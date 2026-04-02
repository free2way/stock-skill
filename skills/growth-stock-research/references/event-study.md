# Event Study

Use this reference when a growth-stock thesis depends on specific dated catalysts rather than a generic price trend.

## Why This Matters

Simple trend backtests answer:

- did momentum work?

Event studies answer more relevant questions such as:

- what usually happens after earnings beats?
- how does the stock behave after guide raises or guide cuts?
- what is the 20-day and 60-day drift after financing news?
- does the stock outperform a benchmark after bullish thesis changes?

## Script

Use:

```bash
python3 scripts/event_returns.py --prices data/NBIS.csv --events data/nbis_events.csv --benchmark data/QQQ.csv
```

The script computes forward returns for default windows:

- `1`
- `5`
- `20`
- `60`
- `120`

You can override them with `--windows`.

## Event CSV Contract

Required columns:

- `date`
- `stance`
- `reason`

Example:

```csv
date,stance,reason
2025-05-08,bullish,Q1 revenue beat and stronger guide
2025-08-07,bearish,Gross margin miss and slower customer ramp
2025-11-06,bullish,Large customer contract expands visibility
```

## Interpretation

For each stance bucket, the script summarizes:

- mean forward return
- median forward return
- hit rate
- optional relative return vs benchmark

Use this to test whether your thesis events historically led to:

- positive drift
- benchmark outperformance
- asymmetric downside after bearish events

## Limits

- small samples can be noisy
- event labels still depend on analyst judgment
- this is not a causal model
- overlapping event windows can blur interpretation

Use event studies as evidence about path and reaction, not as proof of intrinsic value.
