"""Comparable opening-year demand, matched supplier scope and phased buyer cash."""

from math import isclose, isfinite

from cities.Baghdad.financing import CASES, cash_schedule
from engineering.outline.baghdad_system import _id

DIRECT_LOTS = {
    "trainsets": ["Fleet, including spare sets"],
    "line_power": ["Protected conductor and switchgear", "Grid supply sites"],
    "civil": ["Viaduct, piers and foundations"],
    "stations": ["Six station shells and accessible approaches"],
}


def quote_form(case):
    return {
        "opening_candidate_id": case["candidate_id"],
        "opening_evaluation_id": case["evaluation_id"],
        "unit": "million constant 2026 USD",
        "lots": {key: None for key in DIRECT_LOTS},
    }


def quote_adjustments(case, form, rates):
    """Accept complete replacement direct prices and separately scoped recurring changes."""
    blank = quote_form(case)
    form = blank if form is None else form
    if (
        form.keys() != blank.keys()
        or any(form[k] != blank[k] for k in blank if k != "lots")
        or not isinstance(form["lots"], dict)
        or form["lots"].keys() != DIRECT_LOTS.keys()
    ):
        raise ValueError("Supplier return must match the opening candidate, evaluation, units and lots")
    adjustments = {}
    factor = (1 + rates["design_fraction"] + rates["testing_fraction"]) * (
        1 + rates["project_allowance_fraction"]
    )
    for key, quote in form["lots"].items():
        if quote is None:
            continue
        required = {
            "review_reference",
            "direct_price_usd_m",
            "annual_maintenance_change_usd_m",
            "renewal_changes_usd_m",
        }
        if (
            not isinstance(quote, dict)
            or quote.keys() != required
            or not isinstance(quote["review_reference"], str)
            or not quote["review_reference"].strip()
        ):
            raise ValueError(f"Return complete installed scope, incremental upkeep and renewals for {key}")
        price, upkeep, renewals = (
            quote[k]
            for k in ("direct_price_usd_m", "annual_maintenance_change_usd_m", "renewal_changes_usd_m")
        )
        if (
            any(type(v) not in (int, float) or not isfinite(v) for v in (price, upkeep))
            or price <= 0
            or not isinstance(renewals, dict)
            or any(
                str(y) not in {str(i) for i in range(1, 31)} or type(x) not in (int, float) or not isfinite(x)
                for y, x in renewals.items()
            )
        ):
            raise ValueError(f"Invalid installed price, maintenance or renewal schedule for {key}")
        credit = sum(case["scopes_usd_m"][scope] for scope in DIRECT_LOTS[key])
        adjustments[key] = {
            **quote,
            "displaced_direct_usd_m": credit,
            "installed_change_usd_m": (price - credit) * factor,
        }
    return adjustments


def evaluate(case, cfg, reference_hourly, quote=None):
    b, group = case["bundle"], case["train"]
    changes = quote_adjustments(case, quote, cfg["capital_rates_usd_m"])
    cap_delta = sum(q["installed_change_usd_m"] for q in changes.values())
    capex = {
        name: row["capital_usd_m"] + cap_delta
        for name, row in case["iraq_site_estimate"]["scenarios"].items()
    }
    renewals = [dict(r) for r in case["renewals"]]
    for key, row in changes.items():
        renewals.extend(
            {"year": int(y), "component": key + " matched change", "usd_m": x}
            for y, x in row["renewal_changes_usd_m"].items()
        )
    if min(capex.values()) <= 0 or any(
        sum(r["usd_m"] for r in renewals if r["year"] == y) < 0 for y in range(1, 31)
    ):
        raise ValueError("Supplier adjustment exceeds the installed or renewal budget")
    days, places = cfg["vehicle"]["service_days_per_year"], cfg["vehicle"]["normal_places_per_train"]
    peak_capacity = places * 3600 / case["power"]["common_service"]["peak_headway_s"]
    rate = cfg["discount_rate_real"]
    scenarios = {}
    for name, capital in (("central", "base"), ("upside", "low"), ("downside", "high")):
        op = case["iraq_operations"]["cases"][name]
        annual = op["opex_usd_m"] + sum(q["annual_maintenance_change_usd_m"] for q in changes.values())
        if annual <= 0:
            raise ValueError("Matched upkeep consumes the annual operating budget")
        fares = op["net_farebox_usd_m"]
        # Time-of-day demand is held fixed across offers. Use the original hourly
        # service shares as a time-distribution proxy until OD observations arrive.
        peak_requests = op["all_journeys"] / days * max(reference_hourly) / sum(reference_hourly)
        pv = capex[capital] + sum(annual / (1 + rate) ** y for y in range(1, 31))
        pv += sum(r["usd_m"] / (1 + rate) ** r["year"] for r in renewals)
        scenarios[name] = dict(
            capital_usd_m=capex[capital],
            annual_opex_usd_m=annual,
            annual_fares_usd_m=fares,
            paid_journeys_day=op["paid_journeys"] / days,
            passenger_km_year=op["all_journeys"] * op["mean_trip_km"],
            annual_support_usd_m=annual - fares,
            operating_support_usd_per_paid_journey=(annual - fares) * 1e6 / op["paid_journeys"],
            peak_hour_all_boardings_assumed=peak_requests,
            peak_places_hour_direction=peak_capacity,
            capital_usd_per_peak_place_hour_direction=capex[capital] * 1e6 / peak_capacity,
            priced_whole_life_30y_usd_m=pv,
            fare_recovery=fares / annual,
        )
    central = scenarios["central"]
    # Relative years. Assume three years of construction and six months of
    # passenger service in the final year. Count exactly 30 operating years.
    draws = [0.20, 0.45, 0.35]
    profile = {
        "selected_construction_cashflow": {
            "annual_capital_draw": [
                {"year": i, "capital_usd_m": w * capex["base"]} for i, w in enumerate(draws, 1)
            ],
            "full_service_start_year_assumption": len(draws) + 1,
        },
        "selected_annual_opex_usd_m": {"total": central["annual_opex_usd_m"]},
        "selected_renewals_usd_m": renewals,
    }
    cash = cash_schedule(profile, *CASES["mixed_debt"])
    for row in cash["annual"]:
        y = row["year"]
        fraction = 0 if y < 3 else (0.5 if y in (3, 33) else 1.0)
        # Keep the booked service intact when open. Stable fares and fixed
        # staffing scale with the fraction of the year the whole line is open.
        row["service_fraction"] = fraction
        row["operations"] = fraction * central["annual_opex_usd_m"]
        row["net_fares"] = fraction * central["annual_fares_usd_m"]
        row["public_cash_after_fares"] = (
            row["capital"]
            - row["borrowing"]
            + row["interest"]
            + row["principal"]
            + row["operations"]
            + row["renewals"]
            - row["net_fares"]
        )
        row["buyer_cash"] = row["public_cash_after_fares"] + row["net_fares"]
    if not isclose(sum(r["service_fraction"] for r in cash["annual"]), 30):
        raise ValueError("Phased cash schedule lost a service year")
    return {
        "candidate_id": case["candidate_id"],
        "evaluation_id": _id([case["evaluation_id"], changes, scenarios, cash]),
        "priced_capital_usd_m": capex,
        "market_scenarios": scenarios,
        "procurement_changes": changes,
        "renewals": renewals,
        "phased_cash": cash,
        "avoided_congestion_benefit_usd": None,
        "whole_life_complete": False,
        "unpriced": [
            "Site-specific approvals and exceptional works",
            "Incremental recurring substation service, tie and protection scope outside quoted rates",
            "Taxes and financing fees outside the price envelopes",
            "Road mode share, time saved and congestion externalities",
        ],
    }
