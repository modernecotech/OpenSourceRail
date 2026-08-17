#!/usr/bin/env python3
"""Generate a reconciled, machine-readable planning finance model for one city."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import tempfile
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CAPEX_COSTS_PATH = REPO_ROOT / "lib/templates/capex-costs.toml"
COUNTRY_FINANCE_PATH = REPO_ROOT / "lib/templates/country-finance.toml"
CAPITAL_MODEL_PATH = REPO_ROOT / "design-py/src/osr_scenario/capital.py"
NETWORK_FINANCE_MODEL_PATH = REPO_ROOT / "design-py/src/osr_scenario/network_readme.py"
sys.path.insert(0, str(REPO_ROOT / "design-py/src"))

from osr_scenario.network_readme import (  # noqa: E402
    _CAPACITY_UTILIZATION_HIGH,
    _CAPACITY_UTILIZATION_LOW,
    _ENERGY_KWH_PER_CAR_KM,
    _NON_REVENUE_TRAIN_KM_FACTOR,
    _PRACTICAL_CAPACITY_LOAD_FACTOR,
    _USD_TO_EUR,
    _driverless_workforce_breakdown,
    _energy_plan,
    _load_country_finance,
    _scheduled_daily_train_journeys,
    _station_commercial_revenue_eur,
    compute_stats,
)
from osr_scenario.capital import (  # noqa: E402
    FOREIGN_TURNKEY_BASIS,
    FOREIGN_TURNKEY_EXTERNAL_SHARE,
    bucket_rows,
    city_capital_breakdown,
    foreign_turnkey_cases,
    funding_plan,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def npv(rate: float, cashflows: list[float]) -> float:
    return sum(value / ((1.0 + rate) ** year) for year, value in enumerate(cashflows))


def irr(cashflows: list[float]) -> float | None:
    low, high = -0.99, 10.0
    low_value, high_value = npv(low, cashflows), npv(high, cashflows)
    if low_value == 0:
        return low
    if low_value * high_value > 0:
        return None
    for _ in range(200):
        mid = (low + high) / 2.0
        value = npv(mid, cashflows)
        if abs(value) < 0.01:
            return mid
        if value * low_value > 0:
            low, low_value = mid, value
        else:
            high = mid
    return (low + high) / 2.0


def atomic_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False) as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(path)


def build_model(design_path: Path, scenario_path: Path) -> dict[str, object]:
    with design_path.open("rb") as handle:
        design = tomllib.load(handle)
    with scenario_path.open("rb") as handle:
        scenario = tomllib.load(handle)
    slug = str(design["city"]["slug"])
    population = int(design["city"]["population"])
    stats = compute_stats(design, scenario, population)
    energy = _energy_plan(design, scenario, stats)
    costs = design["costs"]
    fin = _load_country_finance(stats.country_iso)

    solar_capex = energy.solar_plant_capex_usd
    base_capital = city_capital_breakdown(costs)
    capital = city_capital_breakdown(costs, solar_capex)
    base_capex = base_capital.total_usd
    total_capex = capital.total_usd
    total_capex_eur = total_capex * _USD_TO_EUR
    capital_plan = funding_plan(capital, fin)
    turnkey_cases = foreign_turnkey_cases(capital, capital_plan)
    turnkey_default = turnkey_cases["default"]

    def turnkey_case_payload(comparison) -> dict[str, float]:
        return {
            "cost_multiplier": comparison.cost_multiplier,
            "foreign_company_total_capex_usd": comparison.foreign_total_usd,
            "foreign_company_external_capital_usd": comparison.foreign_external_usd,
            "osr_total_capex_saving_usd": comparison.total_capex_avoided_usd,
            "osr_total_capex_reduction": comparison.total_capex_reduction,
            "osr_external_capital_saving_usd": comparison.external_capital_avoided_usd,
            "osr_external_capital_reduction": comparison.external_capital_reduction,
            "annual_foreign_company_external_draw_usd": comparison.annual_foreign_external_draw_usd,
            "annual_osr_external_capital_saving_usd": comparison.annual_external_capital_avoided_usd,
            "external_interest_rate": comparison.external_rate,
            "construction_interest_years": comparison.construction_years,
            "repayment_years": comparison.repayment_years,
            "osr_lifetime_external_interest_usd": comparison.osr_lifetime_external_interest_usd,
            "foreign_company_lifetime_external_interest_usd": comparison.foreign_lifetime_external_interest_usd,
            "osr_external_interest_saving_usd": comparison.external_interest_avoided_usd,
            "osr_lifetime_external_financing_saving_usd": comparison.lifetime_external_financing_avoided_usd,
            "osr_lifetime_external_financing_reduction": comparison.lifetime_external_financing_reduction,
        }

    rs_maint = 0.04 * float(costs["rolling_stock_usd"])
    fixed_maint = 0.02 * (
        float(costs["civil_subtotal_usd"])
        + float(costs["stations_usd"])
        + float(costs["depots_usd"])
    )
    signalling_maint = 0.05 * float(costs["signalling_usd"])
    grid_energy = energy.residual_grid_import_kwh * float(
        fin.get("grid_energy_usd_per_kwh", 0.10)
    )
    solar_maint = energy.solar_plant_maintenance_usd

    journeys = _scheduled_daily_train_journeys(design, scenario)
    theoretical_capacity = journeys * stats.trainset_capacity_pax
    practical_capacity = theoretical_capacity * _PRACTICAL_CAPACITY_LOAD_FACTOR
    daily_high = int(practical_capacity * _CAPACITY_UTILIZATION_HIGH)
    total_trainsets = (
        stats.revenue_fleet
        + stats.service_rotation_fleet
        + stats.spare_fleet
        + stats.reserve_fleet
    )
    workforce = _driverless_workforce_breakdown(
        design=design,
        stats=stats,
        service_hours_per_day=energy.service_hours_per_day,
        total_trainsets=total_trainsets,
        annual_train_km=energy.annual_train_km,
        daily_paid_trips_high=daily_high,
    )
    labour = sum(workforce.values()) * float(fin["median_monthly_income_usd"]) * 12 * 1.4
    opex_components = {
        "rolling_stock_maintenance_including_battery_renewal_reserve": rs_maint,
        "civil_station_depot_maintenance": fixed_maint,
        "signalling_maintenance": signalling_maint,
        "residual_grid_energy": grid_energy,
        "solar_plant_maintenance": solar_maint,
        "labour": labour,
    }
    annual_opex = sum(opex_components.values())

    commercial = _station_commercial_revenue_eur(
        design, float(fin["median_monthly_income_usd"])
    )
    nonfare = float(commercial["total_eur"]) / _USD_TO_EUR
    trip_fare = (
        float(fin.get("revenue_case_monthly_pass_income_share", 0.08))
        * float(fin["median_monthly_income_usd"])
        / 30.0
    )
    repayment_years = capital_plan.repayment_years
    debt_principal = capital_plan.external_debt_usd + capital_plan.local_bond_usd
    debt_service = capital_plan.annual_debt_service_usd

    discount_rate = 0.08
    cases: dict[str, object] = {}
    for name, utilisation in (
        ("low_capacity_use", _CAPACITY_UTILIZATION_LOW),
        ("high_capacity_use", _CAPACITY_UTILIZATION_HIGH),
    ):
        annual_trips = practical_capacity * utilisation * 365
        revenue = annual_trips * trip_fare + nonfare
        operating_cash = revenue - annual_opex
        cashflows = [0.0]
        cashflows.extend(
            [-total_capex / capital_plan.construction_years]
            * capital_plan.construction_years
        )
        cashflows.extend([operating_cash] * repayment_years)
        project_irr = irr(cashflows)
        cases[name] = {
            "capacity_utilisation": utilisation,
            "annual_paid_trips": annual_trips,
            "annual_revenue_usd": revenue,
            "annual_operating_cash_usd": operating_cash,
            "project_npv_usd_at_8_percent": npv(discount_rate, cashflows),
            "project_irr": project_irr,
            "steady_state_dscr": operating_cash / debt_service if debt_service else None,
            "annual_public_support_usd": max(0.0, debt_service - operating_cash),
        }

    required_farebox = max(0.0, annual_opex - nonfare)
    neutral_trips = required_farebox / trip_fare if trip_fare else math.inf
    return {
        "schema_version": 4,
        "city": slug,
        "status": "planning-screen",
        "passed": True,
        "sources": {
            "design": str(design_path.relative_to(REPO_ROOT)),
            "design_sha256": sha256(design_path),
            "scenario": str(scenario_path.relative_to(REPO_ROOT)),
            "scenario_sha256": sha256(scenario_path),
            "generator": str(Path(__file__).relative_to(REPO_ROOT)),
            "generator_sha256": sha256(Path(__file__)),
            "capital_model": str(CAPITAL_MODEL_PATH.relative_to(REPO_ROOT)),
            "capital_model_sha256": sha256(CAPITAL_MODEL_PATH),
            "network_finance_model": str(
                NETWORK_FINANCE_MODEL_PATH.relative_to(REPO_ROOT)
            ),
            "network_finance_model_sha256": sha256(NETWORK_FINANCE_MODEL_PATH),
            "capex_costs": str(CAPEX_COSTS_PATH.relative_to(REPO_ROOT)),
            "capex_costs_sha256": sha256(CAPEX_COSTS_PATH),
            "country_finance": str(COUNTRY_FINANCE_PATH.relative_to(REPO_ROOT)),
            "country_finance_sha256": sha256(COUNTRY_FINANCE_PATH),
        },
        "capex_usd": {
            "authoritative_design_base": base_capex,
            "timetable_sized_dedicated_solar": solar_capex,
            "reconciled_project_total": total_capex,
            "risk_envelope_15_percent": total_capex * 1.15,
            "risk_envelope_25_percent": total_capex * 1.25,
            "imported_external_capital": capital.imported_usd,
            "local_capital": capital.local_usd,
            "imported_percentage_of_total": capital.imported_share,
            "local_percentage_of_total": capital.local_share,
            "procurement_origin_buckets": bucket_rows(capital),
            "national_trainset_factory_treatment": "excluded from city CAPEX; costed once in the country NATIONAL-BRIEF.md",
        },
        "capex_eur": {"reconciled_project_total": total_capex_eur},
        "foreign_turnkey_comparator": {
            "status": "illustrative-variable-benchmark-not-vendor-quote",
            "basis": FOREIGN_TURNKEY_BASIS,
            "financing_basis": "OSR and foreign-turnkey external debt use the same country rate, construction interest period, and repayment tenor; foreign-turnkey external capital is assumed debt-financed. Lifetime saving equals avoided external capital plus avoided external interest.",
            "external_capital_share": FOREIGN_TURNKEY_EXTERNAL_SHARE,
            "selected_case": "default",
            "default_comparison": turnkey_case_payload(turnkey_default),
            "sensitivity_cases": {
                name: turnkey_case_payload(comparison)
                for name, comparison in turnkey_cases.items()
            },
        },
        "annual_opex_usd": {"components": opex_components, "total": annual_opex},
        "operations_basis": {
            "scheduled_train_km_per_day": energy.scheduled_daily_train_km,
            "annual_train_km_including_non_revenue": energy.annual_train_km,
            "energy_kwh_per_car_km_hot_climate_planning": _ENERGY_KWH_PER_CAR_KM,
            "non_revenue_train_km_factor": _NON_REVENUE_TRAIN_KM_FACTOR,
        },
        "funding": {
            "debt_principal_usd": debt_principal,
            "annual_debt_service_usd": debt_service,
            "repayment_years": repayment_years,
            "construction_grace_years": capital_plan.construction_years,
            "external_capital_required_usd": capital.imported_usd,
            "annual_external_capital_draw_usd": capital_plan.annual_external_capital_draw_usd,
            "external_grant_usd": capital_plan.external_grant_usd,
            "external_debt_usd": capital_plan.external_debt_usd,
            "external_debt_rate": capital_plan.external_rate,
            "annual_external_debt_service_usd": capital_plan.annual_external_debt_service_usd,
            "local_capital_required_usd": capital.local_usd,
            "annual_local_capital_draw_usd": capital_plan.annual_local_capital_draw_usd,
            "local_bond_principal_usd": capital_plan.local_bond_usd,
            "annual_local_bond_issuance_usd": capital_plan.annual_local_bond_issuance_usd,
            "local_bond_rate": capital_plan.local_bond_rate,
            "annual_local_bond_service_usd": capital_plan.annual_local_bond_service_usd,
            "local_public_equity_usd": capital_plan.local_equity_usd,
            "annual_local_public_equity_draw_usd": capital_plan.annual_local_equity_draw_usd,
            "annual_grace_interest_usd": capital_plan.annual_grace_interest_usd,
            "annual_public_construction_commitment_usd": capital_plan.annual_public_construction_commitment_usd,
            "lender_commitment_status": "unconfirmed-placeholder",
        },
        "revenue_basis": {
            "single_trip_fare_usd": trip_fare,
            "nonfare_revenue_usd_per_year": nonfare,
            "practical_capacity_passenger_trips_per_day": practical_capacity,
            "operating_neutral_paid_trips_per_year": neutral_trips,
            "operating_neutral_capacity_utilisation": neutral_trips / (practical_capacity * 365),
            "demand_status": "capacity-led-not-calibrated-od-forecast",
        },
        "cases": cases,
        "renewal_policy": {
            "train_battery_cycle_years": 12,
            "treatment": "included in rolling-stock maintenance reserve; do not double-count as separate CAPEX",
            "field_asset_renewals": "included in fixed-asset maintenance allowance pending condition-based asset plan",
        },
        "limitations": [
            "No calibrated origin-destination or stated-preference ridership survey.",
            "No committed lender term sheet, vendor bids, land valuation, utility relocation survey, tax or duty assessment.",
            "Imported shares are planning assumptions pending country supplier-capability, customs, tax, and procurement-origin surveys.",
            "NPV, IRR and DSCR are deterministic planning screens and exclude inflation and foreign-exchange paths.",
            "The 15% and 25% risk envelopes are sensitivities, not a quantified probabilistic risk analysis.",
            "The foreign-turnkey comparison is a configurable like-for-like multiplier sensitivity, not a received bid or vendor quotation.",
            "Lifetime external-interest savings use identical country financing terms for both cases and assume the foreign-turnkey external requirement is debt-financed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--scenario", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    design_path = args.design.resolve()
    with design_path.open("rb") as handle:
        slug = str(tomllib.load(handle)["city"]["slug"])
    scenario_path = (args.scenario or design_path.parent / f"{slug}.toml").resolve()
    output = args.output or design_path.parent / "engineering/finance/summary.json"
    model = build_model(design_path, scenario_path)
    atomic_json(output, model)
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
