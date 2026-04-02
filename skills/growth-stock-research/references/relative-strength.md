# Relative Strength

Use this reference when you want to know whether a stock actually outperformed a benchmark, not just whether it went up.

## Why This Matters

High-beta growth stocks can post strong absolute returns while still underperforming:

- `QQQ`
- `SPY`
- a sector ETF
- a peer basket

Relative strength helps answer:

- has the stock been gaining leadership?
- is recent upside just market beta?
- does the name outperform over 20/60/120/252-day windows?

## Script

Run:

```bash
python3 scripts/relative_strength.py --prices data/NBIS.csv --benchmark data/QQQ.csv
```

Default windows:

- `20`
- `60`
- `120`
- `252`

## Output

The script reports:

- current lookback return for the stock
- current lookback return for the benchmark
- current relative return
- rolling average relative return for each window
- rolling hit rate, meaning the fraction of windows in which the stock outperformed

## Interpretation

Use relative strength to separate:

- strong business, weak stock leadership
- strong stock, but mostly because the whole factor rallied
- real share gains versus beta-driven moves

## Good Benchmarks

- `QQQ` for high-duration growth
- `SPY` for broad market context
- sector ETF when one exists
- peer basket when you want the cleanest read on share gain

## Limits

- benchmark choice matters a lot
- high volatility can distort short lookbacks
- this does not explain why outperformance happened

Treat it as positioning evidence, not as a substitute for fundamental work.
