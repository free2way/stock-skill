#!/usr/bin/env python3
"""Industry-aware scorecards for growth stock research."""

from __future__ import annotations

from dataclasses import dataclass


REQUIRED_METRICS = [
    "revenue_growth_yoy",
    "gross_margin",
    "fcf_margin",
    "net_cash_to_revenue",
    "share_dilution_yoy",
    "top_customer_share",
    "capex_to_revenue",
    "rule_of_40",
]


@dataclass(frozen=True)
class MetricRule:
    key: str
    label: str
    weight: int
    thresholds: tuple[float, float, float, float, float]
    higher_is_better: bool = True
    formatter: str = "{value:.1f}"


@dataclass(frozen=True)
class IndustryProfile:
    slug: str
    title: str
    description: str
    metric_rules: tuple[MetricRule, ...]
    limitations: tuple[str, ...] = ()


def format_metric(rule: MetricRule, value: float) -> str:
    return rule.formatter.format(value=value)


def clamp_score(value: int, low: int = 0, high: int = 5) -> int:
    return max(low, min(high, value))


def score_from_thresholds(value: float, thresholds: tuple[float, float, float, float, float], higher_is_better: bool) -> int:
    if higher_is_better:
        passed = sum(1 for threshold in thresholds if value >= threshold)
    else:
        passed = sum(1 for threshold in thresholds if value <= threshold)
    return clamp_score(passed)


def weighted_score(base_score: int, weight: int) -> int:
    return round((base_score / 5.0) * weight)


PROFILE_ALIASES = {
    "generic": "generic_growth",
    "generic_growth": "generic_growth",
    "growth": "generic_growth",
    "saas": "saas",
    "software": "saas",
    "cloud_software": "saas",
    "ai_infra": "ai_infra",
    "ai_infrastructure": "ai_infra",
    "neocloud": "ai_infra",
    "gpu_cloud": "ai_infra",
    "optical": "optical_networking",
    "optical_networking": "optical_networking",
    "semicap_networking": "optical_networking",
    "satellite": "satellite_telecom",
    "satellite_telecom": "satellite_telecom",
    "space": "satellite_telecom",
    "telecom": "satellite_telecom",
}


PROFILES = {
    "generic_growth": IndustryProfile(
        slug="generic_growth",
        title="Generic Growth",
        description="Fallback profile for high-growth companies when no industry-specific scorecard is provided.",
        metric_rules=(
            MetricRule("revenue_growth_yoy", "Revenue growth", 14, (10.0, 20.0, 35.0, 50.0, 80.0), True, "{value:.1f}%"),
            MetricRule("gross_margin", "Gross margin", 12, (25.0, 40.0, 55.0, 65.0, 75.0), True, "{value:.1f}%"),
            MetricRule("fcf_margin", "FCF margin", 12, (-15.0, -5.0, 5.0, 15.0, 25.0), True, "{value:.1f}%"),
            MetricRule("net_cash_to_revenue", "Net cash / revenue", 12, (0.0, 0.10, 0.25, 0.50, 1.00), True, "{value:.2f}x"),
            MetricRule("share_dilution_yoy", "Share dilution", 12, (12.0, 8.0, 5.0, 2.0, 0.5), False, "{value:.1f}%"),
            MetricRule("top_customer_share", "Top customer share", 12, (50.0, 35.0, 25.0, 15.0, 8.0), False, "{value:.1f}%"),
            MetricRule("capex_to_revenue", "Capex / revenue", 12, (1.20, 0.90, 0.60, 0.35, 0.15), False, "{value:.2f}x"),
            MetricRule("rule_of_40", "Rule of 40", 14, (0.0, 15.0, 30.0, 45.0, 60.0), True, "{value:.1f}"),
        ),
        limitations=(
            "Fallback scorecard only. Use an industry-specific profile before comparing names across sectors.",
        ),
    ),
    "saas": IndustryProfile(
        slug="saas",
        title="SaaS / Subscription Software",
        description="Emphasizes durable gross margin, FCF conversion, low dilution, and Rule of 40 discipline.",
        metric_rules=(
            MetricRule("revenue_growth_yoy", "Revenue growth", 12, (12.0, 20.0, 28.0, 38.0, 50.0), True, "{value:.1f}%"),
            MetricRule("gross_margin", "Gross margin", 16, (55.0, 65.0, 72.0, 78.0, 82.0), True, "{value:.1f}%"),
            MetricRule("fcf_margin", "FCF margin", 16, (-5.0, 5.0, 12.0, 20.0, 28.0), True, "{value:.1f}%"),
            MetricRule("net_cash_to_revenue", "Net cash / revenue", 10, (-0.10, 0.0, 0.15, 0.35, 0.60), True, "{value:.2f}x"),
            MetricRule("share_dilution_yoy", "Share dilution", 14, (8.0, 5.0, 3.0, 1.5, 0.5), False, "{value:.1f}%"),
            MetricRule("top_customer_share", "Top customer share", 10, (35.0, 25.0, 18.0, 10.0, 5.0), False, "{value:.1f}%"),
            MetricRule("capex_to_revenue", "Capex / revenue", 6, (0.30, 0.18, 0.10, 0.06, 0.03), False, "{value:.2f}x"),
            MetricRule("rule_of_40", "Rule of 40", 16, (20.0, 30.0, 40.0, 50.0, 60.0), True, "{value:.1f}"),
        ),
        limitations=(
            "This scorecard does not capture NRR, CAC payback, or churn. Use those before sizing a position.",
        ),
    ),
    "ai_infra": IndustryProfile(
        slug="ai_infra",
        title="AI Infrastructure / Neocloud",
        description="Emphasizes growth, balance sheet flexibility, customer concentration, and capital intensity realism.",
        metric_rules=(
            MetricRule("revenue_growth_yoy", "Revenue growth", 18, (20.0, 40.0, 70.0, 100.0, 150.0), True, "{value:.1f}%"),
            MetricRule("gross_margin", "Gross margin", 10, (20.0, 28.0, 36.0, 45.0, 55.0), True, "{value:.1f}%"),
            MetricRule("fcf_margin", "FCF margin", 8, (-35.0, -20.0, -10.0, 0.0, 10.0), True, "{value:.1f}%"),
            MetricRule("net_cash_to_revenue", "Net cash / revenue", 16, (-0.20, 0.0, 0.20, 0.60, 1.00), True, "{value:.2f}x"),
            MetricRule("share_dilution_yoy", "Share dilution", 10, (15.0, 10.0, 6.0, 3.0, 1.0), False, "{value:.1f}%"),
            MetricRule("top_customer_share", "Top customer share", 14, (55.0, 40.0, 28.0, 18.0, 10.0), False, "{value:.1f}%"),
            MetricRule("capex_to_revenue", "Capex / revenue", 16, (2.20, 1.60, 1.10, 0.70, 0.40), False, "{value:.2f}x"),
            MetricRule("rule_of_40", "Rule of 40", 8, (-20.0, 0.0, 15.0, 30.0, 45.0), True, "{value:.1f}"),
        ),
        limitations=(
            "This scorecard does not capture GPU utilization, power availability, contract duration, or customer credit quality.",
        ),
    ),
    "optical_networking": IndustryProfile(
        slug="optical_networking",
        title="Optical Networking / Components",
        description="Balances cyclical growth, margin durability, customer mix, and balance-sheet resilience.",
        metric_rules=(
            MetricRule("revenue_growth_yoy", "Revenue growth", 18, (5.0, 15.0, 30.0, 50.0, 80.0), True, "{value:.1f}%"),
            MetricRule("gross_margin", "Gross margin", 14, (18.0, 25.0, 32.0, 38.0, 44.0), True, "{value:.1f}%"),
            MetricRule("fcf_margin", "FCF margin", 14, (-12.0, -2.0, 4.0, 10.0, 16.0), True, "{value:.1f}%"),
            MetricRule("net_cash_to_revenue", "Net cash / revenue", 12, (-0.20, -0.05, 0.05, 0.15, 0.30), True, "{value:.2f}x"),
            MetricRule("share_dilution_yoy", "Share dilution", 8, (10.0, 6.0, 4.0, 2.0, 0.5), False, "{value:.1f}%"),
            MetricRule("top_customer_share", "Top customer share", 16, (60.0, 45.0, 32.0, 22.0, 12.0), False, "{value:.1f}%"),
            MetricRule("capex_to_revenue", "Capex / revenue", 8, (0.40, 0.25, 0.15, 0.10, 0.05), False, "{value:.2f}x"),
            MetricRule("rule_of_40", "Rule of 40", 10, (10.0, 20.0, 30.0, 40.0, 50.0), True, "{value:.1f}"),
        ),
        limitations=(
            "This scorecard does not capture inventory risk, hyperscaler design-win durability, or cycle position.",
        ),
    ),
    "satellite_telecom": IndustryProfile(
        slug="satellite_telecom",
        title="Satellite / Telecom Infrastructure",
        description="Heavily rewards liquidity and runway because accounting metrics understate financing and execution risk.",
        metric_rules=(
            MetricRule("revenue_growth_yoy", "Revenue growth", 10, (5.0, 15.0, 30.0, 50.0, 80.0), True, "{value:.1f}%"),
            MetricRule("gross_margin", "Gross margin", 8, (15.0, 25.0, 35.0, 45.0, 55.0), True, "{value:.1f}%"),
            MetricRule("fcf_margin", "FCF margin", 6, (-80.0, -50.0, -25.0, -10.0, 0.0), True, "{value:.1f}%"),
            MetricRule("net_cash_to_revenue", "Net cash / revenue", 24, (0.50, 1.00, 2.00, 3.00, 5.00), True, "{value:.2f}x"),
            MetricRule("share_dilution_yoy", "Share dilution", 10, (18.0, 12.0, 8.0, 5.0, 2.0), False, "{value:.1f}%"),
            MetricRule("top_customer_share", "Top customer share", 8, (70.0, 55.0, 40.0, 25.0, 15.0), False, "{value:.1f}%"),
            MetricRule("capex_to_revenue", "Capex / revenue", 18, (8.00, 5.00, 3.00, 1.50, 0.80), False, "{value:.2f}x"),
            MetricRule("rule_of_40", "Rule of 40", 16, (-120.0, -60.0, -20.0, 10.0, 30.0), True, "{value:.1f}"),
        ),
        limitations=(
            "This scorecard does not capture launch cadence, spectrum/regulatory risk, or funding milestones.",
        ),
    ),
}


def supported_profiles() -> list[str]:
    return sorted(PROFILES)


def resolve_profile(payload: dict, override: str | None = None) -> IndustryProfile:
    raw_value = override or payload.get("industry_profile") or payload.get("profile") or payload.get("business_model")
    normalized = PROFILE_ALIASES.get(str(raw_value).strip().lower(), "generic_growth") if raw_value else "generic_growth"
    return PROFILES[normalized]


def missing_required_metrics(payload: dict) -> list[str]:
    return [key for key in REQUIRED_METRICS if key not in payload]


def overall_label(total_score: int, max_score: int) -> str:
    ratio = total_score / max_score if max_score else 0.0
    if ratio >= 0.8:
        return "excellent"
    if ratio >= 0.65:
        return "strong"
    if ratio >= 0.5:
        return "mixed"
    return "weak"


def build_breakdown(payload: dict, profile: IndustryProfile) -> list[dict[str, object]]:
    breakdown: list[dict[str, object]] = []
    for rule in profile.metric_rules:
        value = float(payload[rule.key])
        base_score = score_from_thresholds(value, rule.thresholds, rule.higher_is_better)
        score = weighted_score(base_score, rule.weight)
        direction = "higher is better" if rule.higher_is_better else "lower is better"
        note = f"{rule.label} {format_metric(rule, value)}; {direction} for {profile.title}."
        breakdown.append(
            {
                "name": rule.key,
                "display_name": rule.label,
                "score": score,
                "max_score": rule.weight,
                "base_score": base_score,
                "base_max_score": 5,
                "note": note,
            }
        )
    return breakdown


def build_score_payload(payload: dict, ticker: str | None = None, profile_override: str | None = None) -> dict | None:
    missing = missing_required_metrics(payload)
    if missing:
        return None
    profile = resolve_profile(payload, profile_override)
    breakdown = build_breakdown(payload, profile)
    total_score = sum(int(item["score"]) for item in breakdown)
    max_score = sum(int(item["max_score"]) for item in breakdown)
    label = overall_label(total_score, max_score)
    resolved_ticker = ticker or str(payload.get("ticker", "UNKNOWN"))
    limitations = list(profile.limitations)
    if profile.slug == "generic_growth":
        limitations.append("Add `industry_profile` to the metrics JSON for a more decision-useful score.")
    return {
        "ticker": resolved_ticker,
        "profile": profile.slug,
        "profile_title": profile.title,
        "profile_description": profile.description,
        "score_version": "v2-industry-aware",
        "total_score": total_score,
        "max_score": max_score,
        "label": label,
        "score_summary": f"Overall {total_score}/{max_score} ({label}) using the {profile.title} scorecard.",
        "limitations": limitations,
        "breakdown": breakdown,
    }


def render_text(payload: dict) -> str:
    lines = [
        f"Ticker:       {payload['ticker']}",
        f"Profile:      {payload['profile']} ({payload['profile_title']})",
        f"Total score:  {payload['total_score']}/{payload['max_score']}",
        f"Label:        {payload['label']}",
        f"Version:      {payload['score_version']}",
        "",
        "Breakdown:",
    ]
    for item in payload["breakdown"]:
        lines.append(
            f"- {item['display_name']}: {item['score']}/{item['max_score']} "
            f"(base {item['base_score']}/5, {item['note']})"
        )
    if payload.get("limitations"):
        lines.extend(["", "Limitations:"])
        for item in payload["limitations"]:
            lines.append(f"- {item}")
    return "\n".join(lines)
