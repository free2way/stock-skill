# Backtesting

Use this reference when turning a stock idea into a testable rule.

## Principle

A backtest is only as good as the rule being tested. "This is a good company" is not a rule. "Buy when price breaks a 252-day high and revenue growth is accelerating" is closer to a rule, but only becomes testable when both data series exist in structured form.

## Supported Modes

The bundled script supports two modes:

1. Built-in price rules
   Use for fast baselines when you only have OHLCV data.

2. Signal CSV
   Use when you already transformed the thesis into dated enter/exit instructions.

Signal CSV is the preferred path for fundamental research because it keeps the investment logic explicit.

## Data Contracts

### Price CSV

Required columns:

- `date`
- `close`

Optional columns:

- `open`
- `high`
- `low`
- `volume`

Date format should be ISO-like, for example `2024-03-15`.

### Signal CSV

Required columns:

- `date`
- `signal`

Interpretation:

- `1` means target long exposure
- `0` means flat

The script applies the newest signal on the first available price row on or after that date.

## Built-in Strategies

- `sma-cross`
  Long when 50-day SMA is above 200-day SMA.

- `breakout-252`
  Long when close is at a new 252-day high.

- `momentum-126`
  Long when 126-day return is positive.

These are generic trend rules. They are not substitutes for company-specific research.

## Execution Assumptions

- End-of-day data
- Position changes happen on the close of the first tradable bar after the signal becomes active
- Long-only
- Single asset, full allocation when long
- Flat cash return assumed to be zero

## Interpretation Guidance

Always report:

- test window
- strategy or signal source
- total return
- CAGR
- max drawdown
- Sharpe ratio
- exposure
- trade count

If using a benchmark, compare outcomes but avoid overstating alpha from a simple model.
