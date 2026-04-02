#!/usr/bin/env python3
"""Lightweight backtester for growth-stock workflows.

Supports:
- built-in long-only price rules
- externally supplied signal CSV files
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


TRADING_DAYS = 252


@dataclass
class PriceRow:
    date: datetime
    close: float


@dataclass
class Trade:
    entry_date: str
    entry_price: float
    exit_date: str
    exit_price: float
    return_pct: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backtest simple growth-stock rules.")
    parser.add_argument("--prices", required=True, help="CSV with date and close columns")
    parser.add_argument(
        "--strategy",
        choices=["sma-cross", "breakout-252", "momentum-126"],
        help="Built-in strategy to derive signals from prices",
    )
    parser.add_argument("--signals", help="CSV with date and signal columns")
    parser.add_argument("--benchmark", help="Optional benchmark price CSV")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()

    if bool(args.strategy) == bool(args.signals):
        parser.error("Provide exactly one of --strategy or --signals")
    return args


def read_price_csv(path: str) -> list[PriceRow]:
    rows: list[PriceRow] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            date_text = (raw.get("date") or "").strip()
            close_text = (raw.get("close") or "").strip()
            if not date_text or not close_text:
                continue
            rows.append(
                PriceRow(
                    date=datetime.fromisoformat(date_text),
                    close=float(close_text),
                )
            )
    rows.sort(key=lambda row: row.date)
    if len(rows) < 30:
        raise ValueError(f"Need at least 30 price rows, got {len(rows)}")
    return rows


def read_signal_csv(path: str) -> dict[datetime, int]:
    signals: dict[datetime, int] = {}
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            date_text = (raw.get("date") or "").strip()
            signal_text = (raw.get("signal") or "").strip()
            if not date_text or signal_text == "":
                continue
            signal = int(float(signal_text))
            if signal not in (0, 1):
                raise ValueError(f"Signal must be 0 or 1, got {signal!r}")
            signals[datetime.fromisoformat(date_text)] = signal
    if not signals:
        raise ValueError("No signals found")
    return signals


def simple_moving_average(values: list[float], window: int) -> list[float | None]:
    result: list[float | None] = [None] * len(values)
    if window <= 0:
        return result
    rolling_sum = 0.0
    for index, value in enumerate(values):
        rolling_sum += value
        if index >= window:
            rolling_sum -= values[index - window]
        if index >= window - 1:
            result[index] = rolling_sum / window
    return result


def build_signals_from_strategy(rows: list[PriceRow], strategy: str) -> list[int]:
    closes = [row.close for row in rows]
    signals = [0] * len(rows)

    if strategy == "sma-cross":
        sma_50 = simple_moving_average(closes, 50)
        sma_200 = simple_moving_average(closes, 200)
        for index in range(len(rows)):
            if sma_50[index] is not None and sma_200[index] is not None:
                signals[index] = int(sma_50[index] > sma_200[index])
        return signals

    if strategy == "breakout-252":
        for index in range(252, len(rows)):
            trailing_high = max(closes[index - 252 : index])
            signals[index] = int(closes[index] >= trailing_high)
        return signals

    if strategy == "momentum-126":
        for index in range(126, len(rows)):
            signals[index] = int(closes[index] > closes[index - 126])
        return signals

    raise ValueError(f"Unsupported strategy: {strategy}")


def build_signals_from_dates(rows: list[PriceRow], signal_map: dict[datetime, int]) -> list[int]:
    ordered_dates = sorted(signal_map)
    active_signal = 0
    pointer = 0
    signals: list[int] = []

    for row in rows:
        while pointer < len(ordered_dates) and ordered_dates[pointer] <= row.date:
            active_signal = signal_map[ordered_dates[pointer]]
            pointer += 1
        signals.append(active_signal)
    return signals


def calc_drawdown(equity_curve: Iterable[float]) -> float:
    peak = 0.0
    max_drawdown = 0.0
    for value in equity_curve:
        peak = max(peak, value)
        if peak > 0:
            max_drawdown = min(max_drawdown, (value / peak) - 1.0)
    return max_drawdown


def backtest(rows: list[PriceRow], signals: list[int]) -> tuple[dict[str, float | int | str], list[Trade]]:
    if len(rows) != len(signals):
        raise ValueError("Price rows and signals length mismatch")

    equity = 1.0
    exposure_days = 0
    daily_returns: list[float] = []
    equity_curve = [equity]
    trades: list[Trade] = []
    entry_price: float | None = None
    entry_date: str | None = None

    for index in range(1, len(rows)):
        prev_close = rows[index - 1].close
        current_close = rows[index].close
        prev_signal = signals[index - 1]
        current_signal = signals[index]
        asset_return = (current_close / prev_close) - 1.0
        strategy_return = asset_return if prev_signal == 1 else 0.0
        equity *= 1.0 + strategy_return
        equity_curve.append(equity)
        daily_returns.append(strategy_return)
        exposure_days += prev_signal

        if prev_signal == 0 and current_signal == 1:
            entry_price = current_close
            entry_date = rows[index].date.date().isoformat()
        elif prev_signal == 1 and current_signal == 0 and entry_price is not None and entry_date is not None:
            exit_price = current_close
            trades.append(
                Trade(
                    entry_date=entry_date,
                    entry_price=entry_price,
                    exit_date=rows[index].date.date().isoformat(),
                    exit_price=exit_price,
                    return_pct=(exit_price / entry_price) - 1.0,
                )
            )
            entry_price = None
            entry_date = None

    if signals[-1] == 1 and entry_price is not None and entry_date is not None:
        exit_price = rows[-1].close
        trades.append(
            Trade(
                entry_date=entry_date,
                entry_price=entry_price,
                exit_date=rows[-1].date.date().isoformat(),
                exit_price=exit_price,
                return_pct=(exit_price / entry_price) - 1.0,
            )
        )

    total_days = max(1, len(rows) - 1)
    total_return = equity - 1.0
    years = total_days / TRADING_DAYS
    cagr = (equity ** (1.0 / years) - 1.0) if years > 0 else 0.0
    mean_daily = sum(daily_returns) / len(daily_returns)
    variance = sum((value - mean_daily) ** 2 for value in daily_returns) / max(1, len(daily_returns) - 1)
    volatility = math.sqrt(variance) * math.sqrt(TRADING_DAYS)
    downside = [min(0.0, value) for value in daily_returns]
    downside_variance = sum(value * value for value in downside) / max(1, len(daily_returns) - 1)
    downside_vol = math.sqrt(downside_variance) * math.sqrt(TRADING_DAYS)
    sharpe = (mean_daily * TRADING_DAYS / volatility) if volatility else 0.0
    sortino = (mean_daily * TRADING_DAYS / downside_vol) if downside_vol else 0.0
    win_rate = (
        sum(1 for trade in trades if trade.return_pct > 0) / len(trades)
        if trades
        else 0.0
    )

    stats: dict[str, float | int | str] = {
        "start_date": rows[0].date.date().isoformat(),
        "end_date": rows[-1].date.date().isoformat(),
        "total_return": total_return,
        "cagr": cagr,
        "max_drawdown": calc_drawdown(equity_curve),
        "volatility": volatility,
        "sharpe": sharpe,
        "sortino": sortino,
        "exposure": exposure_days / total_days,
        "trade_count": len(trades),
        "win_rate": win_rate,
    }
    return stats, trades


def benchmark_stats(rows: list[PriceRow]) -> dict[str, float]:
    start = rows[0].close
    end = rows[-1].close
    total_days = max(1, len(rows) - 1)
    years = total_days / TRADING_DAYS
    total_return = (end / start) - 1.0
    cagr = ((end / start) ** (1.0 / years) - 1.0) if years > 0 else 0.0
    return {"benchmark_total_return": total_return, "benchmark_cagr": cagr}


def format_pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def print_report(
    stats: dict[str, float | int | str],
    trades: list[Trade],
    benchmark: dict[str, float] | None,
) -> None:
    print(f"Window:      {stats['start_date']} -> {stats['end_date']}")
    print(f"Return:      {format_pct(float(stats['total_return']))}")
    print(f"CAGR:        {format_pct(float(stats['cagr']))}")
    print(f"Max DD:      {format_pct(float(stats['max_drawdown']))}")
    print(f"Volatility:  {format_pct(float(stats['volatility']))}")
    print(f"Sharpe:      {float(stats['sharpe']):.2f}")
    print(f"Sortino:     {float(stats['sortino']):.2f}")
    print(f"Exposure:    {format_pct(float(stats['exposure']))}")
    print(f"Trades:      {int(stats['trade_count'])}")
    print(f"Win rate:    {format_pct(float(stats['win_rate']))}")
    if benchmark:
        print(f"Benchmark:   {format_pct(benchmark['benchmark_total_return'])} total, {format_pct(benchmark['benchmark_cagr'])} CAGR")
    if trades:
        print("")
        print("Recent trades:")
        for trade in trades[-5:]:
            print(
                f"- {trade.entry_date} @ {trade.entry_price:.2f} -> "
                f"{trade.exit_date} @ {trade.exit_price:.2f} "
                f"({format_pct(trade.return_pct)})"
            )


def main() -> None:
    args = parse_args()
    prices = read_price_csv(args.prices)
    if args.strategy:
        signals = build_signals_from_strategy(prices, args.strategy)
    else:
        signal_map = read_signal_csv(args.signals)
        signals = build_signals_from_dates(prices, signal_map)

    stats, trades = backtest(prices, signals)

    benchmark = None
    if args.benchmark:
        benchmark = benchmark_stats(read_price_csv(args.benchmark))
        stats.update(benchmark)

    if args.json:
        payload = {"stats": stats, "trades": [trade.__dict__ for trade in trades]}
        print(json.dumps(payload, indent=2))
        return

    print_report(stats, trades, benchmark)


if __name__ == "__main__":
    main()
