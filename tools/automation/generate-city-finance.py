#!/usr/bin/env python3
"""Generate a reconciled, machine-readable planning finance model for one city."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from decimal import Decimal
import hashlib
import json
import math
import os
import sys
import tempfile
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CAPEX_COSTS_PATH = REPO_ROOT / "lib/templates/capex-costs.toml"
CIVIL_COST_MODEL_PATH = REPO_ROOT / "lib/templates/civil-cost-model.toml"
COUNTRY_FINANCE_PATH = REPO_ROOT / "lib/templates/country-finance.toml"
CAPITAL_MODEL_PATH = REPO_ROOT / "design/city-generation/src/osr_scenario/capital.py"
NETWORK_FINANCE_MODEL_PATH = REPO_ROOT / "design/city-generation/src/osr_scenario/network_readme.py"
sys.path.insert(0, str(REPO_ROOT / "design/city-generation/src"))

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
from osr_scenario.iraq_finance import build_financing, city_funding_config  # noqa: E402

IRAQ_FUNDING_PATH = REPO_ROOT / "lib/templates/iraq-funding.toml"
IRAQ_MODEL_PATH = REPO_ROOT / "design/city-generation/src/osr_scenario/iraq_finance.py"


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
    model = {
        "schema_version": 4,
        "city": slug,
        "status": "planning-screen",
        "passed": True,
        "workforce": {
            "basis": "Existing driverless operating labour allowance; indicative FTE, not an accepted roster.",
            "groups_fte": workforce,
            "total_fte": sum(workforce.values()),
            "annual_labour_usd": labour,
            "annual_cost_per_fte_usd": float(fin["median_monthly_income_usd"]) * 12 * 1.4,
            "service_hours_per_day": energy.service_hours_per_day,
            "shift_hours": 8,
            "relief_multiplier": 1.35,
        },
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
            "civil_cost_model": str(CIVIL_COST_MODEL_PATH.relative_to(REPO_ROOT)),
            "civil_cost_model_sha256": sha256(CIVIL_COST_MODEL_PATH),
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
    if stats.country_iso == "IQ":
        config = city_funding_config(tomllib.loads(IRAQ_FUNDING_PATH.read_text()), str(model["city"]))
        contracts_path = design_path.parent / "engineering/finance/funding-input.csv"
        for key, path in (("iraq_funding", IRAQ_FUNDING_PATH), ("iraq_finance_model", IRAQ_MODEL_PATH)):
            model["sources"][key] = str(path.relative_to(REPO_ROOT))
            model["sources"][key + "_sha256"] = sha256(path)
        model["funding"]["status"] = "generic-reference-only-see-structured-financing"
        model["primary_funding_model"] = "structured_financing"
        model["cases_financial_basis"] = "Generic uniform-construction comparator only. Revenue/OPEX feed the primary structured model; its scheduled NPV, DSCR and public cash replace the generic financial ratios for Iraq appraisal."
        model["limitations"] = [s for s in model["limitations"] if "exclude inflation and foreign-exchange paths" not in s]
        model["limitations"].append("Generic cases exclude inflation and FX; structured_financing contains the primary Iraq schedule and explicit FX/delay stresses. Neither model establishes financial close.")
        model["foreign_turnkey_comparator"]["financing_basis"] += " Generic financing reference only; not the Iraq funding proposal."
        # Operations budgets are generated from CAPEX, then this model is
        # refreshed. Hash the deterministic CSV, not the twin that hashes us.
        if contracts_path.is_file():
            with contracts_path.open(newline="") as handle:
                contracts = list(csv.DictReader(handle))
            try:
                structured = build_financing(bucket_rows(capital), contracts, cases, annual_opex, config)
            except ValueError as error:
                if "contract budgets do not reconcile" not in str(error) and "stale procurement origin" not in str(error):
                    raise
                structured = {"status": "schedule-refresh-required", "schedule_status": str(error), "funding_committed": False}
            else:
                model["sources"]["funding_schedule"] = str(contracts_path.relative_to(REPO_ROOT))
                model["sources"]["funding_schedule_sha256"] = sha256(contracts_path)
                model["passed"] = all(structured["checks"].values())
        else:
            structured = {"status": "schedule-refresh-required", "schedule_status": "funding-input.csv missing", "funding_committed": False}
        model["structured_financing"] = structured
    return model


def write_funding_artifacts(directory: Path, model: dict) -> None:
    """Human-readable and spreadsheet outputs share the JSON calculation."""
    funding = model.get("structured_financing", {})
    if funding.get("schedule_status") != "linked-to-budget-work-packages":
        return
    for frequency in ("monthly", "annual"):
        rows = funding["base"][frequency]
        with (directory / f"funding-{frequency}-cashflow.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    metrics = funding["base"]["metrics"]
    share = funding["assumptions"]["model"].get("government_share_of_total")
    contribution_note = (
        f"Government capital is **{share:.0%} of total city CAPEX**, before Chinese credit is deducted. "
        "The residual after that contribution and proposed Chinese proceeds is split 75% IQD bonds / 25% IQD bank credit. "
        "Imported purchases use 50% government USD cash and 50% proposed Chinese credit, assuming full-basket eligibility is later qualified; the remaining government contribution is IQD. Financing fees, construction interest, reserves and operating/debt support are additional funding requirements, not included in the 25% capital contribution. "
        "See the [Baghdad-only programme](../../../IRAQ-FUNDING-PROGRAMME.md) for the uncovered cash requirements if no additional government cash is available."
        if share is not None else "This standalone city appraisal is outside the Baghdad-only funding programme."
    )
    lines = [f"# {model['city'].title()} — Iraq funding appraisal", "",
        "Generated from current city CAPEX and procurement milestones. All facilities and appropriations remain uncommitted.", "",
        contribution_note, "",
        f"Construction cash runs through month **{metrics['construction_cash_months']}**; full-network operations start in month **{metrics['operations_start_month']}** after retention. This conservative rollout follows the current resource-constrained CPM, not a five-year promise.", "",
        "## Capital sources and uses", "", "USD is the comparison unit below. **Chinese credit is USD debt; domestic bonds and bank credit are IQD debt. Baghdad imported purchases are funded 50% government USD cash and 50% proposed Chinese loan; the remaining government capital and local cash are IQD.** The full Baghdad import basket is assumed eligible pending supplier-origin and lender qualification. Other city appraisals retain their own assumptions. Fares and local operating payments are budgeted in IQD.", "", "| Capital source | Contract / cash currency | Native amount at model FX | USD equivalent |", "|---|---|---:|---:|"]
    for name, value in metrics["capital_sources_usd"].items():
        if name == "government" and metrics.get("government_capital_usd_cash", 0):
            lines.append(f"| government import cash | USD | {metrics['government_capital_usd_cash']:,.2f} | {metrics['government_capital_usd_cash']:,.2f} |")
            lines.append(f"| government local cash | IQD | {metrics['government_capital_iqd_cash']:,.2f} | {value-metrics['government_capital_usd_cash']:,.2f} |")
            continue
        currency = "USD" if name == "chinese_export_credit" else "IQD"
        native = value if currency == "USD" else value * funding["assumptions"]["model"]["iqd_per_usd"]
        lines.append(f"| {name.replace('_', ' ')} | {currency} | {native:,.2f} | {value:,.2f} |")
    lines.extend([f"| **Total city capital uses** | Mixed | — | **{metrics['total_capex_usd']:,.2f}** |", "",
        "Chinese buyer credit is proposed for eligible Chinese component invoices only. Government contributes its configured capital share, including the eligible-invoice downpayment; IQD bonds and bank credit finance the residual. The conditional ledger also calculates cash needed for fees, construction interest, reserves and operating/debt shortfalls. That additional support is uncommitted and is an unfunded requirement if Baghdad public cash is capped at its 25% capital contribution.", "",
        "## Proposed instruments", "", "| Instrument | Currency | Rate assumed | Grace from draw | Repayment |", "|---|---|---:|---:|---:|"])
    for name in TRANCHE_NAMES:
        t = funding["assumptions"][name]
        lines.append(f"| {name.replace('_', ' ')} | {t['currency']} | {t['annual_rate']:.1%} | {t['grace_months_from_draw']} months | {t['repayment_months']} months |")
    lines.extend(["", "## Chinese component allocation", "", "These allocations divide existing imported budgets; they are not additional costs, supplier quotes or confirmed origin.", "", "| Bucket | Component | Assumed eligible invoice USD |", "|---|---|---:|"])
    lines.extend(f"| {r['bucket']} | {r['component']} | {r['invoice_budget_usd']:,.2f} |" for r in funding["eligible_import_components"])
    lines.extend(["", "## Annual cash requirements", "", "Year 1 begins at assumed financial close; NTP follows 30 working days later. Amounts below are USD millions. DSCR excludes subsidy; public cash includes capital, fees, interest, reserves and support.", "", "| Year | CAPEX | Revenue | OPEX | Debt service | Public cash | DSCR before support |", "|---:|---:|---:|---:|---:|---:|---:|"])
    for r in funding["base"]["annual"]:
        dscr = r["dscr_before_public_support"]
        lines.append(f"| {r['year']} | {r['capex_usd']/1e6:.2f} | {r['revenue_usd']/1e6:.2f} | {r['opex_usd']/1e6:.2f} | {r['debt_service_usd']/1e6:.2f} | {r['government_total_cash_usd']/1e6:.2f} | {dscr:.2f} |" if dscr is not None else f"| {r['year']} | {r['capex_usd']/1e6:.2f} | {r['revenue_usd']/1e6:.2f} | {r['opex_usd']/1e6:.2f} | 0.00 | {r['government_total_cash_usd']/1e6:.2f} | — |")
    lines.extend(["", "## Sensitivities", "", "| Scenario | Peak annual public cash USD m | Minimum operating DSCR | Peak uncovered monthly capital USD m |", "|---|---:|---:|---:|"])
    for name, r in funding["sensitivity_cases"].items():
        dscr = r["minimum_operating_dscr_before_public_support"]
        lines.append(f"| {name.replace('_', ' ')} | {r['peak_annual_government_cash_usd']/1e6:.2f} | {dscr:.2f} | {r['peak_monthly_unfunded_cash_usd']/1e6:.2f} |" if dscr is not None else f"| {name} | {r['peak_annual_government_cash_usd']/1e6:.2f} | — | {r['peak_monthly_unfunded_cash_usd']/1e6:.2f} |")
    lines.extend(["", "## Assumptions and evidence", "", *[f"- {s}" for s in funding["limitations"]], "",
        "Long construction schedules can leave much of the debt already repaid by government before full-network opening. An operating DSCR above one therefore does not establish self-financing or remove the construction-period public cash burden. Uncovered capital gaps are conditional funding requirements, not actual cash receipts.", "",
        f"See [editable assumptions]({os.path.relpath(IRAQ_FUNDING_PATH, directory)}), [monthly cashflow](funding-monthly-cashflow.csv), [annual cashflow](funding-annual-cashflow.csv), and [machine-readable model](summary.json).", "",
        "The [IMF Article IV](https://www.imf.org/en/news/articles/2025/07/08/pr-25243-iraq-imf-executive-board-concludes-2025-article-iv-consultation) provides the historical FX anchor. [CBI](https://www.cbi.iq/page/26) describes its role as fiscal agent for MoF bonds. [China Exim](https://english.eximbank.gov.cn/Business/CreditB/SupportingFT/201810/t20181016_6965.html) describes export buyer credit; numeric project terms remain assumptions.", ""])
    (directory / "FUNDING-MODEL.md").write_text("\n".join(lines))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    annual = funding["base"]["annual"]
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), constrained_layout=True)
    years = [r["year"] for r in annual]
    bottoms = [0.0] * len(annual)
    for key, label in (("government_capital_received_usd", "Government capital"),
                       ("chinese_export_credit_draw_usd", "Chinese export credit"),
                       ("domestic_bonds_draw_usd", "IQD bonds"), ("bank_credit_draw_usd", "IQD bank credit")):
        values = [r[key]/1e6 for r in annual]
        axes[0].bar(years, values, bottom=bottoms, label=label)
        bottoms = [a+b for a, b in zip(bottoms, values)]
    axes[0].set_ylabel("Capital draws · USD million")
    axes[0].legend(loc="upper right", fontsize=8)
    for key, label in (("revenue_usd", "Revenue"), ("opex_usd", "OPEX"),
                       ("debt_service_usd", "Debt service"), ("government_total_cash_usd", "Total public cash")):
        axes[1].plot(years, [r[key]/1e6 for r in annual], label=label)
    axes[1].set_ylabel("Annual cash · USD million")
    axes[1].set_xlabel("Year from assumed financial close")
    axes[1].legend(loc="upper right", fontsize=8)
    axes[1].grid(alpha=.25)
    fig.suptitle(f"{model['city'].title()} · Iraq funding appraisal\nUncommitted terms; capacity-led low-demand case")
    fig.savefig(directory / "funding-cashflows.png", dpi=160)
    plt.close(fig)


TRANCHE_NAMES = ("chinese_export_credit", "domestic_bonds", "bank_credit")


def refresh_funding_input(design_path: Path, slug: str) -> None:
    """Persist a compact funding schedule so finance reproduces in a checkout.

    Detailed locally generated operations CSVs are large and gitignored. This
    projection keeps their actual budget/timing/origin values without asset IDs.
    """
    source = design_path.parent / "operations" / f"{slug}-budget-work-packages.csv"
    if not source.is_file():
        return  # existing controlled input supports a fresh checkout
    totals = defaultdict(Decimal)
    with source.open(newline="") as handle:
        for row in csv.DictReader(handle):
            key = tuple(row[k] for k in ("bucket", "planned_start_day", "planned_finish_day", "imported_share"))
            totals[key] += Decimal(row["budget_usd"])
    directory = design_path.parent / "engineering/finance"
    directory.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=directory, newline="", delete=False) as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("bucket", "planned_start_day", "planned_finish_day", "imported_share", "budget_usd"))
        for key, amount in sorted(totals.items()):
            writer.writerow((*key, str(amount)))
        temporary = Path(handle.name)
    temporary.replace(directory / "funding-input.csv")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--scenario", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    design_path = args.design.resolve()
    with design_path.open("rb") as handle:
        city = tomllib.load(handle)["city"]
        slug = str(city["slug"])
    scenario_path = (args.scenario or design_path.parent / f"{slug}.toml").resolve()
    output = args.output or design_path.parent / "engineering/finance/summary.json"
    if city["country"] == "IQ":
        refresh_funding_input(design_path, slug)
    model = build_model(design_path, scenario_path)
    atomic_json(output, model)
    write_funding_artifacts(output.parent, model)
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
