#!/usr/bin/env python3
"""Transparent, profile-aware valuation engine for growth stocks."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass

from industry_scorecard import resolve_profile


@dataclass(frozen=True)
class ScenarioBand:
    bear: float
    base: float
    bull: float


PROFILE_MULTIPLES = {
    "generic_growth": {
        "ev_to_sales": ScenarioBand(2.5, 5.0, 8.0),
        "ev_to_gross_profit": ScenarioBand(4.0, 8.0, 14.0),
        "fcf_yield": ScenarioBand(0.10, 0.06, 0.03),
    },
    "saas": {
        "ev_to_sales": ScenarioBand(3.0, 6.5, 10.0),
        "ev_to_gross_profit": ScenarioBand(5.0, 10.0, 16.0),
        "fcf_yield": ScenarioBand(0.08, 0.05, 0.03),
    },
    "ai_infra": {
        "ev_to_sales": ScenarioBand(2.5, 5.5, 9.0),
        "ev_to_gross_profit": ScenarioBand(5.0, 10.0, 16.0),
        "fcf_yield": ScenarioBand(0.12, 0.07, 0.04),
    },
    "optical_networking": {
        "ev_to_sales": ScenarioBand(1.2, 2.5, 4.0),
        "ev_to_gross_profit": ScenarioBand(3.0, 5.5, 8.5),
        "fcf_yield": ScenarioBand(0.14, 0.09, 0.05),
    },
    "satellite_telecom": {
        "ev_to_sales": ScenarioBand(1.0, 2.5, 5.0),
        "ev_to_gross_profit": ScenarioBand(2.5, 5.0, 9.0),
        "fcf_yield": ScenarioBand(0.16, 0.10, 0.06),
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a profile-aware valuation snapshot.")
    parser.add_argument("--input", required=True, help="Input JSON with valuation and metric fields")
    parser.add_argument(
        "--profile",
        help="Optional industry profile override. Otherwise infer from `industry_profile` or related fields.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    return parser.parse_args()


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def coalesce_number(*values: object) -> float | None:
    for value in values:
        if value is None or value == "":
            continue
        return float(value)
    return None


def pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def x(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.2f}x"


def money(value: float | None) -> str:
    if value is None:
        return "n/a"
    abs_value = abs(value)
    if abs_value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if abs_value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    return f"${value:,.0f}"


def extract_inputs(payload: dict) -> dict[str, float | str | None]:
    metrics = payload.get("metrics", {}) if isinstance(payload.get("metrics"), dict) else {}
    valuation = payload.get("valuation_inputs", {}) if isinstance(payload.get("valuation_inputs"), dict) else {}

    ticker = str(payload.get("ticker", metrics.get("ticker", valuation.get("ticker", "UNKNOWN"))))
    analysis_date = str(payload.get("analysis_date", metrics.get("analysis_date", valuation.get("analysis_date", "n/a"))))

    revenue = coalesce_number(
        valuation.get("revenue_next_12m"),
        valuation.get("revenue"),
        payload.get("revenue_next_12m"),
        payload.get("revenue"),
        metrics.get("revenue"),
    )
    gross_margin = coalesce_number(valuation.get("gross_margin"), payload.get("gross_margin"), metrics.get("gross_margin"))
    gross_profit = coalesce_number(
        valuation.get("gross_profit_next_12m"),
        valuation.get("gross_profit"),
        payload.get("gross_profit_next_12m"),
        payload.get("gross_profit"),
    )
    if gross_profit is None and revenue is not None and gross_margin is not None:
        gross_profit = revenue * gross_margin / 100.0

    fcf = coalesce_number(
        valuation.get("fcf_next_12m"),
        valuation.get("fcf"),
        payload.get("fcf_next_12m"),
        payload.get("fcf"),
    )
    if fcf is None and revenue is not None:
        fcf_margin = coalesce_number(valuation.get("fcf_margin"), payload.get("fcf_margin"), metrics.get("fcf_margin"))
        if fcf_margin is not None:
            fcf = revenue * fcf_margin / 100.0

    net_cash = coalesce_number(
        valuation.get("net_cash"),
        payload.get("net_cash"),
    )
    if net_cash is None and revenue is not None:
        net_cash_to_revenue = coalesce_number(
            valuation.get("net_cash_to_revenue"),
            payload.get("net_cash_to_revenue"),
            metrics.get("net_cash_to_revenue"),
        )
        if net_cash_to_revenue is not None:
            net_cash = revenue * net_cash_to_revenue

    enterprise_value = coalesce_number(
        valuation.get("enterprise_value"),
        payload.get("enterprise_value"),
    )
    market_cap = coalesce_number(
        valuation.get("market_cap"),
        payload.get("market_cap"),
    )
    if enterprise_value is None and market_cap is not None and net_cash is not None:
        enterprise_value = market_cap - net_cash
    if market_cap is None and enterprise_value is not None and net_cash is not None:
        market_cap = enterprise_value + net_cash

    growth = coalesce_number(
        valuation.get("revenue_growth_yoy"),
        payload.get("revenue_growth_yoy"),
        metrics.get("revenue_growth_yoy"),
    )

    return {
        "ticker": ticker,
        "analysis_date": analysis_date,
        "revenue": revenue,
        "gross_profit": gross_profit,
        "fcf": fcf,
        "net_cash": net_cash,
        "enterprise_value": enterprise_value,
        "market_cap": market_cap,
        "revenue_growth_yoy": growth,
        "gross_margin": gross_margin,
    }


def scenario_multiple(current: float | None, anchor: ScenarioBand, growth: float | None, gross_margin: float | None) -> ScenarioBand:
    adjust = 0.0
    if growth is not None:
        if growth >= 60.0:
            adjust += 0.6
        elif growth >= 35.0:
            adjust += 0.3
        elif growth <= 10.0:
            adjust -= 0.4
    if gross_margin is not None:
        if gross_margin >= 65.0:
            adjust += 0.3
        elif gross_margin <= 25.0:
            adjust -= 0.3

    if current is not None:
        base = max(anchor.bear, min(anchor.bull + 2.0, (anchor.base + current) / 2.0 + adjust))
    else:
        base = anchor.base + adjust
    bear = max(0.1, min(base - 1.0, anchor.base + adjust - 1.0))
    bull = max(base + 0.5, anchor.bull + adjust)
    bear = min(bear, base)
    bull = max(bull, base)
    return ScenarioBand(round(bear, 2), round(base, 2), round(bull, 2))


def scenario_ev_from_multiple(metric_value: float | None, band: ScenarioBand) -> dict[str, float] | None:
    if metric_value is None:
        return None
    return {
        "bear": metric_value * band.bear,
        "base": metric_value * band.base,
        "bull": metric_value * band.bull,
    }


def scenario_equity_and_return(ev_scenarios: dict[str, float] | None, current_market_cap: float | None, net_cash: float | None) -> dict[str, dict[str, float]] | None:
    if ev_scenarios is None or current_market_cap is None or net_cash is None:
        return None
    output: dict[str, dict[str, float]] = {}
    for key, ev in ev_scenarios.items():
        implied_market_cap = ev + net_cash
        output[key] = {
            "implied_market_cap": implied_market_cap,
            "implied_return": (implied_market_cap / current_market_cap) - 1.0,
        }
    return output


def valuation_label(base_return: float | None) -> str:
    if base_return is None:
        return "insufficient-data"
    if base_return >= 0.30:
        return "compelling"
    if base_return >= 0.10:
        return "constructive"
    if base_return > -0.10:
        return "balanced"
    return "stretched"


def build_payload(source: dict, profile_override: str | None = None) -> dict:
    values = extract_inputs(source)
    profile = resolve_profile(source, profile_override)
    anchors = PROFILE_MULTIPLES[profile.slug]

    ev = values["enterprise_value"]
    revenue = values["revenue"]
    gross_profit = values["gross_profit"]
    fcf = values["fcf"]

    current_ev_to_sales = ev / revenue if ev is not None and revenue not in (None, 0.0) else None
    current_ev_to_gross_profit = ev / gross_profit if ev is not None and gross_profit not in (None, 0.0) else None
    current_fcf_yield = fcf / ev if ev not in (None, 0.0) and fcf is not None else None

    sales_band = scenario_multiple(current_ev_to_sales, anchors["ev_to_sales"], values["revenue_growth_yoy"], values["gross_margin"])
    gp_band = scenario_multiple(current_ev_to_gross_profit, anchors["ev_to_gross_profit"], values["revenue_growth_yoy"], values["gross_margin"])

    sales_ev = scenario_ev_from_multiple(revenue, sales_band)
    gp_ev = scenario_ev_from_multiple(gross_profit, gp_band)

    base_return_sales = None
    if sales_ev and values["market_cap"] is not None and values["net_cash"] is not None:
        base_return_sales = ((sales_ev["base"] + values["net_cash"]) / values["market_cap"]) - 1.0

    current_yield_note = None
    if current_fcf_yield is not None:
        target = anchors["fcf_yield"].base
        current_yield_note = "cheap vs FCF yield anchor" if current_fcf_yield >= target else "rich vs FCF yield anchor"

    summary_parts = [
        f"Current EV/Sales {x(current_ev_to_sales)}",
        f"base-case fair EV/Sales {x(sales_band.base)}",
    ]
    if base_return_sales is not None:
        summary_parts.append(f"base implied return {pct(base_return_sales)}")
    summary = "; ".join(summary_parts) + "."

    return {
        "ticker": values["ticker"],
        "analysis_date": values["analysis_date"],
        "profile": profile.slug,
        "profile_title": profile.title,
        "valuation_version": "v1-transparent-scenarios",
        "label": valuation_label(base_return_sales),
        "summary": summary,
        "inputs": values,
        "current": {
            "ev_to_sales": current_ev_to_sales,
            "ev_to_gross_profit": current_ev_to_gross_profit,
            "fcf_yield": current_fcf_yield,
        },
        "scenario_multiples": {
            "ev_to_sales": sales_band.__dict__,
            "ev_to_gross_profit": gp_band.__dict__,
            "fcf_yield_anchor": anchors["fcf_yield"].__dict__,
        },
        "scenario_values": {
            "from_ev_to_sales": {
                "enterprise_value": sales_ev,
                "equity": scenario_equity_and_return(sales_ev, values["market_cap"], values["net_cash"]),
            },
            "from_ev_to_gross_profit": {
                "enterprise_value": gp_ev,
                "equity": scenario_equity_and_return(gp_ev, values["market_cap"], values["net_cash"]),
            },
        },
        "notes": [
            "This is a transparent scenario framework, not a full DCF or target-price model.",
            "Always compare the multiple bands against peers and the current macro regime before sizing a position.",
            current_yield_note,
        ],
    }


def render_text(payload: dict) -> str:
    current = payload["current"]
    sales = payload["scenario_multiples"]["ev_to_sales"]
    gp = payload["scenario_multiples"]["ev_to_gross_profit"]
    lines = [
        f"Ticker:            {payload['ticker']}",
        f"Profile:           {payload['profile']} ({payload['profile_title']})",
        f"Label:             {payload['label']}",
        f"Version:           {payload['valuation_version']}",
        f"Current EV/Sales:  {x(current.get('ev_to_sales'))}",
        f"Current EV/GP:     {x(current.get('ev_to_gross_profit'))}",
        f"Current FCF Yield: {pct(current.get('fcf_yield'))}",
        "",
        "Scenario Multiples:",
        f"- EV/Sales bear/base/bull: {x(sales['bear'])} / {x(sales['base'])} / {x(sales['bull'])}",
        f"- EV/GP bear/base/bull: {x(gp['bear'])} / {x(gp['base'])} / {x(gp['bull'])}",
        "",
        f"Summary: {payload['summary']}",
    ]
    sales_equity = payload["scenario_values"]["from_ev_to_sales"]["equity"]
    if sales_equity:
        lines.extend([
            "",
            "EV/Sales Implied Equity Returns:",
            f"- Bear: {pct(sales_equity['bear']['implied_return'])}",
            f"- Base: {pct(sales_equity['base']['implied_return'])}",
            f"- Bull: {pct(sales_equity['bull']['implied_return'])}",
        ])
    notes = [note for note in payload.get("notes", []) if note]
    if notes:
        lines.extend(["", "Notes:"])
        for note in notes:
            lines.append(f"- {note}")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    source = load_json(args.input)
    payload = build_payload(source, args.profile)
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(render_text(payload))


if __name__ == "__main__":
    main()
