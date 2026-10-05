#!/usr/bin/env python3
"""Build the Baghdad-only capital programme and expose the 25% public cash cap."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "design/city-generation/src"))
from osr_scenario.iraq_finance import build_financing, city_funding_config
from osr_scenario.network_readme import _station_commercial_revenue_eur, _USD_TO_EUR
from finance_evidence import stale_finance_sources
from baghdad_funding_analysis import build_analysis, write_outputs, early_repayment_report, repayment_outcome


def write_comparison_chart(summary: dict, directory: Path) -> None:
    """Keep funding currency and purchase FX exposure on separate axes."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    china = summary["usd_denominated_capital_usd"] / 1e9
    domestic = summary["total_capex_usd"] / 1e9 - china
    imported = summary["comparison"]["osr_imported_purchases_usd"] / 1e9
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), layout="constrained")
    names = ["OSR Baghdad\nincluding plant", "148 km proposal\nrequested USD scenario"]
    axes[0].bar(names, [china, 18], color="#b86e18", label="USD loan + government USD cash")
    axes[0].bar(names, [domestic, 0], bottom=[china, 18], color="#166d77", label="IQD funding, USD equivalent")
    axes[0].set_title("Capital funding currency")
    axes[0].set_ylabel("USD billion equivalent")
    axes[0].legend(loc="upper left", fontsize=8)
    axes[0].text(0, china+domestic+.4, f"{china+domestic:.3f} total; {china:.3f} USD", ha="center", fontsize=9)
    axes[0].text(1, 18.4, "18.000 assumed USD", ha="center", fontsize=9)
    axes[1].bar(names, [imported, 18], color=["#166d77", "#b86e18"])
    axes[1].set_title("Imported-purchase FX exposure")
    axes[1].set_ylabel("USD billion")
    axes[1].text(0, imported+.4, f"{imported:.3f} imports", ha="center", fontsize=9)
    axes[1].text(1, 18.4, "18.000 all-USD assumption", ha="center", fontsize=9)
    for ax in axes:
        ax.set_ylim(0, 22)
        ax.grid(axis="y", alpha=.2)
        ax.set_axisbelow(True)
    fig.suptitle("Baghdad: import funding is split between government USD cash and USD credit", fontsize=13)
    fig.supxlabel("Planning comparison; third-party final currency terms unverified; differing scope and price dates", fontsize=9)
    fig.savefig(directory / "baghdad-financing-comparison.png", dpi=160)
    plt.close(fig)


def write_phasing_chart(summary: dict, directory: Path) -> None:
    """Display timed liquidity needs separately from operating receipts."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    case = summary["phased_opening"]["cases"]["low_demand"]
    rows = case["annual"]
    years = [row["year"] for row in rows]
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), layout="constrained")
    for key, label in (("revenue_usd", "Phased revenue"), ("opex_usd", "Phased OPEX"), ("debt_service_usd", "Debt service, city + plant")):
        axes[0].plot(years, [row[key]/1e6 for row in rows], label=label)
    for data, label in ((summary["annual"], "All fares after final capital payment"), (rows, "Conditional phased opening")):
        axes[1].plot([row["year"] for row in data], [row["government_operations_and_debt_support_usd"]/1e6 for row in data], label=label)
    axes[0].set_ylabel("Operating cash / service, USD m")
    axes[1].set_ylabel("Extra liquidity required, USD m")
    axes[1].set_xlabel("Year from assumed financial close")
    for ax in axes:
        ax.legend(fontsize=8)
        ax.grid(alpha=.2)
    fig.suptitle("Baghdad + one plant: phased receipts and additional annual liquidity")
    fig.supxlabel("Conditional nominal planning flows; 25% capital grant excluded from extra liquidity; opening and funding uncommitted", fontsize=8)
    fig.savefig(directory / "baghdad-phased-cashflows.png", dpi=160)
    plt.close(fig)


def main() -> int:
    country = ROOT / "cities/catalogue/west-asia/Iraq"
    config_path = ROOT / "lib/templates/iraq-funding.toml"
    options_path = ROOT / "lib/templates/baghdad-finance-options.toml"
    options = tomllib.loads(options_path.read_text())
    config = city_funding_config(tomllib.loads(config_path.read_text()), "baghdad")
    capex = tomllib.loads((ROOT / "lib/templates/capex-costs.toml").read_text())
    cities = {}
    city_models = {}
    source_paths = [options_path, Path(__file__).with_name("baghdad_funding_analysis.py"), config_path, ROOT / "lib/templates/capex-costs.toml", Path(__file__),
                    ROOT / "design/city-generation/src/osr_scenario/iraq_finance.py"]
    modules = {}
    for name in ("Baghdad",):
        path = country / name / "engineering/finance/summary.json"
        finance = json.loads(path.read_text())
        if stale_finance_sources(finance, ROOT):
            raise ValueError(f"{name}: stale finance inputs require regeneration")
        funding = finance["structured_financing"]
        if funding.get("schedule_status") != "linked-to-budget-work-packages" or not all(funding["checks"].values()):
            raise ValueError(f"{name}: current reconciled funding schedule required")
        cities[name] = funding
        city_models[name] = finance
        design_path = country / name / "design.toml"
        design = tomllib.loads(design_path.read_text())
        modules[name] = sum(f["trainset_count"] for f in design["fleets"]) * design["costs"]["technology_basis"]["car_count"]
        if funding["assumptions"]["model"] != config["model"]:
            raise ValueError("Baghdad finance must be regenerated with the current 25% scenario")
        source_paths.extend([path, design_path, country / name / "engineering/finance/funding-input.csv"])
    anchor = max(modules, key=modules.get)
    factory_plan_path = country / "Baghdad/engineering/factory/summary.json"
    factory_plan = json.loads(factory_plan_path.read_text())
    for relative, digest in factory_plan['sources_sha256'].items():
        if hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()!=digest:
            raise ValueError('Stale factory sizing source: '+relative)
    if factory_plan['total_trainsets']*6 != modules[anchor] or factory_plan['city']!='baghdad':
        raise ValueError('Factory sizing must match the actual Baghdad fleet')
    factory_usd = max(modules[anchor] * capex["production_plant"]["per_vehicle_usd"], factory_plan['plant_cost_envelope_usd'])
    factory_ready = factory_plan['factory_ready_working_day']
    source_paths.append(factory_plan_path)
    factory_buckets = []
    factory_contracts = []
    for bucket, amount in (("production_plant", factory_usd), ("epc_overhead", factory_usd*capex["overhead"]["epc_fraction"])):
        share = capex["procurement_origin"]["imported_share"][bucket]
        factory_buckets.append({"bucket": bucket, "total_usd": amount, "imported_usd": amount*share})
        factory_contracts.append({"bucket": bucket, "budget_usd": amount, "imported_share": share, "planned_start_day": 0, "planned_finish_day": factory_ready})
    # Eighteen-month city-sized factory allowance, with quotations/release open.
    factory = build_financing(factory_buckets, factory_contracts,
        {"low_capacity_use": {"annual_revenue_usd": 0}, "high_capacity_use": {"annual_revenue_usd": 0}}, 0, config)
    components = {**cities, "Baghdad factory": factory}
    quality_path = country / "Baghdad/baghdad.design-quality.yaml"
    source_paths.append(quality_path)
    coverage = next(float(line.split(":", 1)[1]) for line in quality_path.read_text().splitlines() if line.strip().startswith("high_demand_coverage:"))
    city_model = city_models["Baghdad"]
    income_path = ROOT / "lib/templates/country-finance.toml"
    source_paths.append(income_path)
    country_income = tomllib.loads(income_path.read_text())["countries"]["IQ"]["median_monthly_income_usd"]
    route_km = sum(line["length_m"] for line in design["lines"]) / 1000
    fx = config["model"]["iqd_per_usd"]
    imported_usd = city_model["capex_usd"]["imported_external_capital"] + sum(b["imported_usd"] for b in factory_buckets)
    original_component_invoices_usd = sum(b["imported_usd"] * sum(config["eligible_imports"].get(b["bucket"], {}).values()) for b in city_model["capex_usd"]["procurement_origin_buckets"] + factory_buckets)
    unconfirmed_expanded_loan_usd = (imported_usd-original_component_invoices_usd) * config["model"]["export_invoice_advance"]
    local_usd = city_model["capex_usd"]["local_capital"] + sum(b["total_usd"]-b["imported_usd"] for b in factory_buckets)
    fare_iqd = city_model["revenue_basis"]["single_trip_fare_usd"] * fx
    annual_trips = city_model["cases"]["low_capacity_use"]["annual_paid_trips"]
    nonfare = city_model["revenue_basis"]["nonfare_revenue_usd_per_year"]
    commercial = _station_commercial_revenue_eur(design, country_income)
    retail_usd = commercial["retail_eur"] / _USD_TO_EUR
    advertising_usd = commercial["ads_eur"] / _USD_TO_EUR
    if abs(retail_usd + advertising_usd - nonfare) > .01:
        raise ValueError("Station retail and advertising must reconcile to existing nonfare revenue")
    operating_receipts = {
        "farebox_annual_usd": annual_trips * city_model["revenue_basis"]["single_trip_fare_usd"],
        "station_retail_annual_usd": retail_usd,
        "station_advertising_annual_usd": advertising_usd,
        "existing_nonfare_annual_usd": nonfare,
        "total_annual_usd": annual_trips * city_model["revenue_basis"]["single_trip_fare_usd"] + nonfare,
        "annual_paid_trips": annual_trips,
        "planning_monthly_income_iqd": country_income * fx,
        "rentable_sqm": commercial["rentable_sqm"],
        "advertising_boards": commercial["ad_boards"],
        "retail_rent_iqd_m2_month": commercial["retail_rent_usd_m2_month"] * fx,
        "advertising_board_iqd_month": commercial["ad_board_usd_month"] * fx,
        "retail_occupancy": .88, "advertising_occupancy": .85,
        "basis": "Steady-state low-capacity-use planning assumptions; phased receipts follow opened-fleet shares and each line's revenue ramp. Existing shop/kiosk and advertising receipts are already included, not additional gap funding. Occupancy and income-based rental rates are uncalibrated; concession management costs and tenant demand need appraisal.",
    }
    opex = city_model["annual_opex_usd"]["total"]
    operating_only_fare_iqd = max(0, opex-nonfare) / annual_trips * fx
    # Compare the first complete operating year against its ramped trips. This
    # includes debt service and fees but excludes reserve deposits and CAPEX.
    op_start = cities["Baghdad"]["base"]["metrics"]["operations_start_month"]
    first_operating_year = cities["Baghdad"]["base"]["monthly"][op_start:op_start+12]
    ramp = config["model"]["revenue_ramp"][0]
    first_year_required_fare_iqd = max(0, sum(r["opex_usd"]+r["debt_service_usd"]+r["fees_usd"] for r in first_operating_year)-nonfare*ramp) / (annual_trips*ramp) * fx
    source_report = "https://www.aljazeera.net/ebusiness/2024/7/26/العراق-يختار-شركات-أجنبية-لتنفيذ"
    source_nic = "https://investpromo.gov.iq/announcement-of-an-international-investment-opportunity-no-3-of-2024-metro-baghdad-dbomft/"
    comparator = {
        "reported_scope": {"route_km": 148, "lines": 7, "stations": 64, "capital_estimate_usd": 18_000_000_000, "report_date": "2024-07-26"},
        "source_report": source_report, "source_nic": source_nic, "checked_as_of": config["model"]["as_of"],
        "currency_basis": "User-requested 100% USD funding scenario (foreign loans plus government USD), not verified contracted funding terms; foreign-debt/government split unknown",
        "coverage_basis": "Reported 80% city coverage ambition has no comparable walk-distance/population denominator; not measured population access",
        "fare_basis": "Third-party contracted fare and debt/OPEX schedule unavailable; no claimed fare advantage against an invented comparator fare",
        "scope_limitations": "Historical estimate and OSR unquoted planning budgets differ in scope, price date and maturity; no like-for-like qualified bid saving is established",
    }
    comparison = {"third_party": comparator,
        "osr_route_km": route_km, "osr_lines": len(design["lines"]), "osr_stations": len(design["stations"]),
        "osr_imported_purchases_usd": imported_usd, "osr_local_purchases_usd": local_usd,
        "planning_population": design["city"]["population"], "anchor_weighted_coverage": coverage,
        "anchor_based_resident_proxy": None,
        "coverage_measure_deprecation": "Legacy anchor_weighted_coverage key retains a routing high-demand cell fraction; it is not population coverage. Former resident multiplication retired.",
        "fare_iqd": fare_iqd, "annual_low_case_paid_trips": annual_trips,
        "fare_basis": "Modelled average single-trip yield from income proxy; no adopted tariff or unlimited pass assumed",
        "operating_only_neutral_fare_iqd_at_low_trips": operating_only_fare_iqd,
        "first_operating_year_neutral_fare_iqd_including_debt_and_fees": first_year_required_fare_iqd,
        "first_operating_year_paid_trips": annual_trips*ramp,
        "operating_fte": city_model["workforce"]["total_fte"], "operating_labour_annual_iqd": city_model["workforce"]["annual_labour_usd"]*fx,
        "construction_job_count": None, "construction_job_basis": "Local procurement budgets are not payroll or job counts; workforce-hours, wage and productivity qualification required",
    }
    # These are conditional requirements, not a forecast of approved subsidies.
    # The public cash cap includes only the 25% capital contribution. Additional
    # support from the underlying city/factory appraisals remains unfunded.
    flow_keys = ("capex_usd", "government_capital_received_usd", "government_capital_usd_cash", "chinese_export_credit_draw_usd", "domestic_bonds_draw_usd", "bank_credit_draw_usd", "chinese_export_credit_debt_service_usd", "revenue_usd", "opex_usd", "debt_service_usd", "fees_usd", "government_operations_and_debt_support_usd")
    monthly_by_month = {}
    for funding in components.values():
        for row in funding["base"]["monthly"]:
            target = monthly_by_month.setdefault(row["month"], {"month": row["month"], "year": row["year"], **{k: 0.0 for k in flow_keys}})
            for key in flow_keys:
                target[key] += row[key]
            target.setdefault("government_capital_iqd", 0.0)
            target.setdefault("domestic_bonds_draw_iqd", 0.0)
            target.setdefault("bank_credit_draw_iqd", 0.0)
            target.setdefault("domestic_debt_service_iqd", 0.0)
            target.setdefault("revenue_iqd", 0.0)
            target.setdefault("opex_iqd", 0.0)
            target.setdefault("additional_funding_required_iqd", 0.0)
            target["government_capital_iqd"] += row["government_capital_iqd_cash"]
            target["domestic_bonds_draw_iqd"] += row["domestic_bonds_draw_native"]
            target["bank_credit_draw_iqd"] += row["bank_credit_draw_native"]
            target["domestic_debt_service_iqd"] += sum(row[f"{t}_{k}_native"] for t in ("domestic_bonds", "bank_credit") for k in ("interest", "principal"))
            target["revenue_iqd"] += row["revenue_usd"] * row["iqd_per_usd"]
            target["opex_iqd"] += row["opex_usd"] * row["iqd_per_usd"]
            target["additional_funding_required_iqd"] += row["government_operations_and_debt_support_usd"] * row["iqd_per_usd"]
    monthly = [monthly_by_month[m] for m in sorted(monthly_by_month)]
    cumulative_gap = 0.0
    for row in monthly:
        row["government_cash_with_25_percent_cap_usd"] = row["government_capital_received_usd"]
        row["additional_funding_required_with_25_percent_cap_usd"] = row["government_operations_and_debt_support_usd"]
        cumulative_gap += row["additional_funding_required_with_25_percent_cap_usd"]
        row["cumulative_additional_funding_required_usd"] = cumulative_gap
        row["conditional_total_public_cash_required_usd"] = row["government_capital_received_usd"] + row["government_operations_and_debt_support_usd"]
    annual_by_year = {}
    for row in monthly:
        target = annual_by_year.setdefault(row["year"], {"year": row["year"], **{k: 0.0 for k in row if k not in {"month", "year", "cumulative_additional_funding_required_usd"}}})
        for key in target:
            if key not in {"year", "cumulative_additional_funding_required_usd"}:
                target[key] += row[key]
        target["cumulative_additional_funding_required_usd"] = row["cumulative_additional_funding_required_usd"]
    annual = [annual_by_year[y] for y in sorted(annual_by_year)]
    sources = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    summary = {"schema_version": 2, "status": "planning-uncommitted", "funding_committed": False,
               "scope": "Baghdad and one Baghdad manufacturing plant only; Samawah, Mosul and all other cities excluded",
               "government_capital_contribution_basis": "25% direct budget contribution includes USD import cash and IQD local cash; it does not cap sovereign bond liabilities, guarantees or lifetime cash support",
               "included_cities": ["Baghdad"], "government_share_of_total_capital": config["model"]["government_share_of_total"],
               "calendar_basis": "Baghdad and its plant financial close at month zero; factory commissioning and city production sequencing require an accepted integrated baseline",
               "cashflow_basis": "Conditional debt/reserve payments require additional funding. Under the 25% public cash cap, that support is unfunded; modelled repayment is not a funded outcome.",
               "factory": {"cost_usd": factory_usd, "epc_usd": factory_usd*capex["overhead"]["epc_fraction"], "anchor_city": anchor, "vehicle_modules": modules[anchor], "planning_build_working_days": factory_ready,
                           "funding": factory},
               "capital_sources_usd": {k: sum(v["base"]["metrics"]["capital_sources_usd"][k] for v in components.values()) for k in factory["base"]["metrics"]["capital_sources_usd"]},
               "total_capex_usd": sum(v["base"]["metrics"]["total_capex_usd"] for v in components.values()),
               "additional_funding_required_with_25_percent_cap_usd": cumulative_gap,
               "conditional_total_public_cash_required_usd": sum(r["conditional_total_public_cash_required_usd"] for r in monthly),
               "peak_annual_government_capital_usd": max(r["government_cash_with_25_percent_cap_usd"] for r in annual),
               "peak_annual_additional_funding_required_usd": max(r["additional_funding_required_with_25_percent_cap_usd"] for r in annual),
               "peak_annual_conditional_public_cash_required_usd": max(r["conditional_total_public_cash_required_usd"] for r in annual),
               "comparison": comparison, "operating_receipts": operating_receipts,
               "monthly": monthly, "annual": annual, "sources_sha256": sources}
    if abs(summary["capital_sources_usd"]["government"] - summary["total_capex_usd"] * .25) > .01:
        raise ValueError("Government capital must equal 25% of total programme uses")
    if abs(sum(summary["capital_sources_usd"].values()) - summary["total_capex_usd"]) > .01:
        raise ValueError("Programme capital sources and uses do not reconcile")
    government_usd = sum(v["base"]["metrics"]["government_capital_usd_cash"] for v in components.values())
    government_iqd = sum(v["base"]["metrics"]["government_capital_iqd_cash"] for v in components.values())
    summary["capital_sources_native"] = {
        "chinese_export_credit": {"currency": "USD", "amount": summary["capital_sources_usd"]["chinese_export_credit"], "usd_equivalent": summary["capital_sources_usd"]["chinese_export_credit"]},
        "government_import_cash": {"currency": "USD", "amount": government_usd, "usd_equivalent": government_usd},
        "government_local_cash": {"currency": "IQD", "amount": government_iqd, "usd_equivalent": government_iqd/fx},
        **{k: {"currency": "IQD", "amount": summary["capital_sources_usd"][k]*fx, "usd_equivalent": summary["capital_sources_usd"][k]} for k in ("domestic_bonds", "bank_credit")},
    }
    summary["additional_funding_breakdown_usd"] = {
        "baghdad_before_full_network_opening": sum(r["government_operations_and_debt_support_usd"] for r in cities["Baghdad"]["base"]["monthly"] if r["month"] < op_start),
        "baghdad_operations_and_debt_tail": sum(r["government_operations_and_debt_support_usd"] for r in cities["Baghdad"]["base"]["monthly"] if r["month"] >= op_start),
        "plant_capital_financing": sum(r["government_operations_and_debt_support_usd"] for r in factory["base"]["monthly"]),
    }
    summary["model_horizon_months"] = len(monthly)
    summary["original_component_invoice_pool_usd"] = original_component_invoices_usd
    summary["uncovered_loan_if_only_original_components_eligible_usd"] = unconfirmed_expanded_loan_usd
    summary["government_capital_usd_cash"] = government_usd
    summary["government_capital_iqd_cash"] = government_iqd
    summary["usd_denominated_debt_principal_usd"] = summary["capital_sources_usd"]["chinese_export_credit"]
    summary["usd_denominated_capital_usd"] = summary["capital_sources_usd"]["chinese_export_credit"] + government_usd
    summary["usd_denominated_capital_share"] = summary["usd_denominated_capital_usd"] / summary["total_capex_usd"]
    summary["iqd_denominated_capital_share"] = 1-summary["usd_denominated_capital_share"]
    summary["non_chinese_credit_import_fx_requirement_usd"] = imported_usd-summary["capital_sources_usd"]["chinese_export_credit"]
    if abs(government_usd-imported_usd*.5) > .01 or abs(summary["capital_sources_usd"]["chinese_export_credit"]-imported_usd*.5) > .01:
        raise ValueError("Imports must be funded 50% government USD cash and 50% USD credit")
    phased_city = cities["Baghdad"].get("phased_opening", {})
    phased_programme_cases = {}
    native_keys = ("government_capital_iqd", "domestic_bonds_draw_iqd", "bank_credit_draw_iqd", "domestic_debt_service_iqd", "revenue_iqd", "opex_iqd", "additional_funding_required_iqd")
    phased_keys = (*flow_keys, *native_keys, "reserve_deposit_usd", "reserve_release_usd")
    for name, case in phased_city.get("cases", {}).items():
        combined = {}
        for ledger in (case, factory["base"]):
            for row in ledger["monthly"]:
                target = combined.setdefault(row["month"], {"month": row["month"], "year": row["year"], **{key: 0.0 for key in phased_keys}})
                for key in (*flow_keys, "reserve_deposit_usd", "reserve_release_usd"):
                    target[key] += row[key]
                target["government_capital_iqd"] += row["government_capital_iqd_cash"]
                target["domestic_bonds_draw_iqd"] += row["domestic_bonds_draw_native"]
                target["bank_credit_draw_iqd"] += row["bank_credit_draw_native"]
                target["domestic_debt_service_iqd"] += sum(row[f"{t}_{k}_native"] for t in ("domestic_bonds", "bank_credit") for k in ("interest", "principal"))
                for key in ("revenue", "opex"):
                    target[key+"_iqd"] += row[key+"_usd"]*row["iqd_per_usd"]
                target["additional_funding_required_iqd"] += row["government_operations_and_debt_support_usd"]*row["iqd_per_usd"]
        phased_monthly = [combined[m] for m in sorted(combined)]
        phased_annual = {}
        for row in phased_monthly:
            target = phased_annual.setdefault(row["year"], {"year": row["year"], **{key: 0.0 for key in phased_keys}})
            for key in phased_keys:
                target[key] += row[key]
        phased_programme_cases[name] = {
            "metrics": case["metrics"], "final_city_unrestricted_cash_usd": case["metrics"]["final_unrestricted_cash_usd"], "monthly": phased_monthly, "annual": list(phased_annual.values()),
            "additional_funding_required_usd": sum(row["government_operations_and_debt_support_usd"] for row in phased_monthly),
            "plant_support_required_usd": summary["additional_funding_breakdown_usd"]["plant_capital_financing"],
            "conditional_total_public_cash_required_usd": sum(row["government_capital_received_usd"]+row["government_operations_and_debt_support_usd"] for row in phased_monthly),
        }
    summary["phased_opening"] = {"status": phased_city.get("status"), "phases": phased_city.get("phases", []),
        "weight_basis": phased_city.get("weight_basis"), "fixed_opex_share": phased_city.get("fixed_opex_share"), "cases": phased_programme_cases}
    with (country / "Baghdad/engineering/finance/funding-input.csv").open(newline="") as handle:
        city_contracts = list(csv.DictReader(handle))
    analysis = build_analysis(summary, cities["Baghdad"], factory, city_contracts, factory_contracts, config, options)
    summary["independent_recalculation"] = {
        "status": analysis["status"], "reconciliation": analysis["reconciliation"],
        "cases": {name: case["metrics"] for name, case in analysis["cases"].items()},
        "additional_receipts_threshold": analysis["additional_receipts_threshold"],
        "fare_uplift_threshold": analysis["fare_uplift_threshold"],
        "selected_pricing_sensitivity": analysis["selected_pricing_sensitivity"],
        "fare_pricing": {name: {key: value for key, value in case["fare_policy"].items() if key != "monthly_prices"}
                         for name, case in analysis["cases"].items() if "fare_policy" in case},
        "early_repayment": {**analysis["early_repayment"],
                            "cases": {name: case["metrics"] for name, case in analysis["early_repayment"]["cases"].items()},
                            "full_calculation": "finance/baghdad-early-repayment.json"},
        "full_calculation": "finance/baghdad-finance-reconciliation.json",
        "six_month_reference": "finance/baghdad-unfunded_reference-six-month-tranches.csv",
        "six_month_blended": "finance/baghdad-blended_candidate-six-month-tranches.csv",
    }
    directory = country / "finance"
    directory.mkdir(exist_ok=True)
    write_outputs(analysis, summary, directory, country)
    (directory / "baghdad-programme.json").write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n")
    for period, rows in (("monthly", monthly), ("annual", annual)):
        with (directory / f"baghdad-programme-{period}-cashflow.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    if phased_programme_cases:
        for period in ("monthly", "annual"):
            rows = phased_programme_cases["low_demand"][period]
            with (directory / f"baghdad-programme-phased-{period}-cashflow.csv").open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
    for legacy in ("three-city-programme.json", "three-city-annual-cashflow.csv"):
        (directory / legacy).unlink(missing_ok=True)
    write_comparison_chart(summary, directory)
    if phased_programme_cases:
        write_phasing_chart(summary, directory)
    lines = ["# Baghdad-only funding programme", "", "Scope: [Baghdad](Baghdad/README.md) and one manufacturing plant sized for Baghdad. **Samawah, Mosul and every other city are excluded.** All funding is proposed and uncommitted.", "",
        "## Consolidated sources and uses", "", "Government contributes **25% of total capital uses**, including the plant and EPC. Imported purchases are split **50% government USD cash and 50% proposed Chinese USD credit**, assuming the full imported basket can qualify. That USD government cash is inside the 25% total contribution; the rest of the government contribution is IQD. The remaining balance after those two sources is split 75% domestic IQD bonds and 25% IQD bank term credit.", "",
        "| Proposed capital source | Currency | Native amount, billions | USD equivalent, million | Share of total capital |", "|---|---|---:|---:|---:|"]
    lines.extend(f"| {k.replace('_', ' ')} | {v['currency']} | {v['amount']/1e9:,.3f} | {v['usd_equivalent']/1e6:,.2f} | {v['usd_equivalent']/summary['total_capex_usd']:.2%} |" for k, v in summary["capital_sources_native"].items())
    lines.extend([f"| **Total capital uses** | Mixed | — | **{summary['total_capex_usd']/1e6:,.2f}** | **100%** |", "",
        f"Baghdad city CAPEX is USD {cities['Baghdad']['base']['metrics']['total_capex_usd']/1e6:,.2f} million. The plant is counted **once** at USD {factory_usd/1e6:,.2f} million plus USD {summary['factory']['epc_usd']/1e6:,.2f} million EPC. Its sizing basis is {modules[anchor]:,} vehicle/car modules from Baghdad's controlled fleet and car count. Imported tooling receives proposed Chinese credit within that plant budget. The physical cell/floor/tooling envelope replaces the smaller module allowance where necessary; both remain unquoted engineering assumptions.", "",
        "## Currency and USD capital intensity", "", "![Funding currency and imported-purchase FX comparison](finance/baghdad-financing-comparison.png)", "",
        f"**Only Chinese credit is USD-denominated debt:** USD {summary['capital_sources_usd']['chinese_export_credit']/1e6:,.2f} million. Government additionally provides USD {government_usd/1e6:,.2f} million cash for imports. Combined USD capital funding is {summary['usd_denominated_capital_share']:.2%} of uses; **the remaining {summary['iqd_denominated_capital_share']:.2%} is IQD government cash, IQD bonds and IQD bank credit.** Revenue and local OPEX are also budgeted in IQD. At the historical planning conversion of {fx:,.0f} IQD/USD, the local government cash allowance is IQD {government_iqd/1e12:,.3f} trillion, alongside its separate USD import cash. Together they equal 25% of total capital. USD columns are comparison equivalents, not a requirement to borrow or appropriate those domestic amounts in dollars.", "",
        f"Funding currency and procurement currency differ. Estimated imported purchases total USD {imported_usd/1e6:,.2f} million ({imported_usd/summary['total_capex_usd']:.2%} of capital), including plant imports. The government supplies half directly in USD cash; proposed Chinese credit supplies half as USD debt. The full import pool, including categories beyond the initially selected solar, bogies, batteries, windows, doors and tooling, is assumed lender-eligible pending origin qualification. If that expanded basket cannot qualify, its loan funding is uncovered; it is not automatically replaced by IQD bank credit or another grant. IQD borrowing reduces the revenue/debt currency mismatch; it does not remove Chinese debt-service FX risk, imported maintenance costs, domestic interest, inflation or placement constraints.", "",
        f"Eligibility sensitivity: the original named-component categories cover USD {original_component_invoices_usd/1e6:,.2f} million of invoices. At a 50% advance, they alone support USD {original_component_invoices_usd*.5/1e6:,.2f} million of proposed credit. If the additional imported categories cannot qualify, **USD {unconfirmed_expanded_loan_usd/1e6:,.2f} million of planned capital loan proceeds remains uncovered**, in addition to the base support requirement below. Even the original categories remain unqualified; this screen is not a lender approval. No extra government contribution is assumed to replace that missing loan.", "",
        "## What the 25% government limit leaves unfunded", "",
        f"The 25% capital contribution is **USD {summary['capital_sources_usd']['government']/1e6:,.2f} million**. If that is also the limit on all public cash, the model leaves **USD {cumulative_gap/1e6:,.2f} million of additional funding requirements** across the full construction, operating and debt horizon. These are interest, fees, reserve and operating/debt cash needs after modelled revenue; they are not additional approved government contributions.", "",
        f"Peak annual capital contribution is USD {summary['peak_annual_government_capital_usd']/1e6:,.2f} million. Peak annual additional funding requirement is USD {summary['peak_annual_additional_funding_required_usd']/1e6:,.2f} million. If all additional support were provided publicly, conditional lifetime public cash would be USD {summary['conditional_total_public_cash_required_usd']/1e6:,.2f} million, with a combined annual peak of USD {summary['peak_annual_conditional_public_cash_required_usd']/1e6:,.2f} million. This exceeds the requested contribution and is shown only to expose the funding gap.", "",
        f"Across the {len(monthly)/12:.1f}-year nominal model horizon, additional requirements divide into USD {summary['additional_funding_breakdown_usd']['baghdad_before_full_network_opening']/1e6:,.2f} million before Baghdad's full-network opening, USD {summary['additional_funding_breakdown_usd']['baghdad_operations_and_debt_tail']/1e6:,.2f} million during Baghdad operations/debt tail, and USD {summary['additional_funding_breakdown_usd']['plant_capital_financing']/1e6:,.2f} million for plant capital financing. Principal repayment before opening is part of the pre-opening requirement. This base withholds all fares until full-network completion; the separate phased sensitivity below tests earlier revenue. Gross additional support is a liquidity requirement over time, not net lifetime loss: later retained cash cannot repay earlier obligations without an approved bridge.", "",
        "The programme CSVs distinguish the capped capital contribution, additional funding requirement and conditional payment requirements. Underlying city and factory ledgers calculate the support needed to pay scheduled obligations; their positive reserve balances and completed repayments are conditional on that support being raised. They are not a cash-solvent forecast under the public cash cap. No bridge, equity investor, rollover or extra appropriation is invented to close the gap.", "",
        "## Cash and contractual structure", "",
        "1. An Iraqi public sponsor seeks MoF authority for proposed sovereign IQD bonds through the established MoF/CBI issuance route, subject to legal review and placement. Municipal borrowing powers are not assumed. The 25% limit is the direct capital contribution, not a limit on sovereign bond liabilities, guarantees or lifetime public exposure.",
        "2. Chinese export buyer credit is allocated to qualified Chinese invoices for solar equipment, bogies, batteries, windows, doors and Baghdad plant tooling. The requested 50% loan advance is matched by 50% government USD cash. All other imported categories also require Chinese supplier-origin and lender qualification before the full-basket financing assumption is valid. Noneligible imports still need foreign currency. Eligibility and origin require supplier evidence.",
        "3. Government's 25% capital contribution covers the planned eligible downpayment; bonds and bank credit cover the remaining capital balance. Fees, construction interest and reserve funding are separate cash requirements, not silently capitalised or counted as capital-source proceeds.",
        "4. Each draw starts its own grace and repayment clock. Planned receipts match procurement milestones; no actual payment or lender commitment is asserted. Chinese credit uses USD, bonds and bank credit IQD. Terms remain unconfirmed appraisal assumptions: 5%/48-month grace/180-month repayment, 8%/24/180, and 9%/0/84 respectively.",
        "5. Revenue pays OPEX first and debt service next; subsidy is excluded from DSCR. Additional support shown by the city and plant models is an unfunded requirement under the cap. The factory model covers capital financing only; manufacturing income and factory OPEX need a separate business case.",
        "6. Declined Chinese finance, delayed contributions, FX changes and bullet redemption are separately tested in the Baghdad appraisal. None creates an automatic facility or refinancing source.", "",
        "## Rollout and financial close", "",
        f"Baghdad's current capital milestones span {cities['Baghdad']['base']['metrics']['construction_cash_months']} calendar months. Full-network fare revenue begins after all budget milestones. Lowering the capital grant increases borrowing and cash-service needs; it does not shorten this schedule. The city-sized Baghdad plant becomes available after {factory_ready} working days (18 months from NTP), followed by the separately scheduled first-article series-release gate. The separate phased sensitivity uses this integrated planning schedule; actual plant and line acceptance and a commissioned operating baseline remain pending.", "",
        "Required before financial close: approved sponsor and borrowing powers; appropriation limited to the agreed government contribution; a funded solution for the additional cash gap; supplier quotations and origin evidence; signed term sheets, guarantees and insurance; IQD placement/redemption plan; lender draw windows and FX access; surveyed demand/fare policy; tax, duty, land and utility pricing; accepted resource calendar and reserve covenants.", "",
        "## Model and evidence", "",
        "[Programme monthly cashflow](finance/baghdad-programme-monthly-cashflow.csv) · [annual cashflow](finance/baghdad-programme-annual-cashflow.csv) · [machine-readable programme](finance/baghdad-programme.json) · [Baghdad city appraisal](Baghdad/engineering/finance/FUNDING-MODEL.md) · [editable assumptions](../../../../lib/templates/iraq-funding.toml). Other Iraqi city appraisals remain standalone examples outside this programme.", "",
        "[IMF 2025 Article IV](https://www.imf.org/en/news/articles/2025/07/08/pr-25243-iraq-imf-executive-board-concludes-2025-article-iv-consultation) supplies the historical 2024 FX anchor, not a current dealing rate. [CBI fiscal-agent description](https://www.cbi.iq/page/26) and [Injaz issue example](https://cbi.iq/news/view/2620) support sovereign-bond context. [China Exim export buyer credit](https://english.eximbank.gov.cn/Business/CreditB/SupportingFT/201810/t20181016_6965.html) supports the instrument concept; numeric terms and eligibility are unconfirmed assumptions.", ""])
    comparison_lines = ["## Comparison with the historical 148 km third-party proposal", "",
        f"The [July 2024 report]({source_report}), citing the prime minister's adviser, gives USD 18 billion, 148 km, seven lines and 64 stations. The [NIC procurement notice]({source_nic}) describes DBOMFT and requires bidders to submit a funding plan. Neither establishes a final all-USD financing contract. The **100% USD foreign-loan/government-cash comparator below is the user's requested scenario**, not a verified split of debt and grants. The older USD estimate has not been restated to a common price date.", "",
        "| Measure | Current OpenSourceRail Baghdad plan | Historical proposal / requested USD scenario |", "|---|---:|---:|",
        f"| Route km (not track km) | {route_km:,.1f} | 148 |",
        f"| Lines / stations | {comparison['osr_lines']} / {comparison['osr_stations']} | 7 / 64 |",
        f"| Capital uses, USD equivalent bn | {summary['total_capex_usd']/1e9:.3f}, including one plant | 18.000, reported estimate |",
        f"| Capital intensity, USD equivalent m / route km | {summary['total_capex_usd']/route_km/1e6:.2f} | {18_000/148:.2f} |",
        f"| USD-denominated capital funding, USD bn | {summary['usd_denominated_capital_usd']/1e9:.3f}, half loan / half government cash | 18.000, assumed USD cash + loans |",
        f"| IQD-denominated capital funding, IQD tn | {(summary['total_capex_usd']-summary['usd_denominated_capital_usd'])*fx/1e12:.3f} | Zero in requested scenario |",
        f"| Imported-purchase FX exposure, USD bn | {imported_usd/1e9:.3f} | 18.000 only under all-USD purchase assumption |",
        f"| USD purchase intensity, USD m / route km | {imported_usd/route_km/1e6:.2f} | {18_000/148:.2f} under that assumption |",
        "| Contracted fares / debt terms | Planning fare and uncommitted facilities | Not established by these sources |", "",
        f"The OSR plan has {route_km/148:.2f} times the route length and {comparison['osr_stations']/64:.2f} times the stations. Its planning capital estimate is {1-summary['total_capex_usd']/18e9:.1%} below USD 18 billion. Under the requested all-USD funding scenario, USD-denominated capital funding is {1-summary['usd_denominated_capital_usd']/18e9:.1%} lower; under an all-USD purchase scenario, imported-purchase exposure is {1-imported_usd/18e9:.1%} lower. These measure different exposures and are not interchangeable debt-service savings.", "",
        f"The planning comparison is not a like-for-like qualified bid: route geometry, tunnelling/structures, land, utilities, taxes/duties, contingency, escalation, supplier qualification and acceptance maturity differ or remain unresolved. The older report's four-year completion expectation also differs substantially from OSR's current {cities['Baghdad']['base']['metrics']['construction_cash_months']}-month capital schedule. A lower capital estimate does not establish an earlier or more sustainable delivered service.", "",
        "## Fares, population access and financial sustainability", "",
        f"The modelled average paid-trip fare is **IQD {fare_iqd:,.0f}** (USD {fare_iqd/fx:.2f} comparison equivalent), denominated in IQD rather than automatically indexed to the USD loan. It derives from the retained USD {country_income:,.0f}/month income proxy, equivalent to IQD {country_income*fx:,.0f}/month at the planning anchor. Thirty paid trips consume {30*fare_iqd/(country_income*fx):.1%} of that proxy income; 44 commuter trips cost IQD {44*fare_iqd:,.0f}, or {44*fare_iqd/(country_income*fx):.1%}. This is an average-trip yield assumption, not an adopted tariff or unlimited monthly pass; concessions, transfers and family affordability need an explicit tariff and household survey.", "",
        f"Low/high capacity-use cases assume {annual_trips/365:,.0f} / {city_model['cases']['high_capacity_use']['annual_paid_trips']/365:,.0f} paid trips/day, not unique people or surveyed demand. Low-case steady annual revenue is IQD {city_model['cases']['low_capacity_use']['annual_revenue_usd']*fx/1e9:,.1f} billion; OPEX is IQD {opex*fx/1e9:,.1f} billion. At that trip volume, the OPEX-only neutral fare is IQD {operating_only_fare_iqd:,.0f}, with nonfare receipts held constant. It excludes capital, debt and reserve funding.", "",
        f"In the first complete operating year, the 50% revenue ramp produces {annual_trips*ramp/1e6:.1f} million paid trips. Holding those trips and nonfare receipts fixed, covering OPEX, scheduled debt service and fees requires approximately **IQD {first_year_required_fare_iqd:,.0f} per paid trip**, excluding reserve deposits and factory debt. This is a cash threshold, not a recommended tariff; higher fares can reduce demand. Minimum annual operating DSCR before support is {cities['Baghdad']['base']['metrics']['minimum_operating_dscr_before_public_support']:.2f}. Higher utilisation improves later cashflow but cannot fund the long pre-opening debt-service period. Neither this fare nor IQD denomination closes the additional funding gap shown above.", "",
        f"The design retains a planning population of {design['city']['population']:,}. The legacy **{coverage:.1%} routing-demand cell fraction** is not a population percentage; its former multiplication into a resident estimate is retired. See the [native population-count and multi-hop transfer audit](Baghdad/engineering/access/README.md) for radius sensitivities, date, bbox denominator and access limitations. The older report's 80% city-coverage ambition uses no published comparable denominator or access method; it cannot establish that either plan reaches more residents. The {len(design['stations'])} station platforms and {len(design['lines'])} routes offer a network to test, not proof of superior walking coverage.", "",
        "## Direct Iraqi labour and industrial benefits", "",
        f"Approximately **USD {local_usd/1e9:.3f} billion equivalent ({local_usd/summary['total_capex_usd']:.1%})** of programme procurement is assigned to local suppliers under the editable origin assumptions. This is potential local expenditure, not wages, GDP added or guaranteed Iraqi content. City civil works alone allocate USD {next(b['local_usd'] for b in city_model['capex_usd']['procurement_origin_buckets'] if b['bucket']=='civil')/1e9:.3f} billion locally; rolling stock allocates USD {next(b['local_usd'] for b in city_model['capex_usd']['procurement_origin_buckets'] if b['bucket']=='rolling_stock')/1e6:,.2f} million locally, with plant local expenditure separately counted.", "",
        "Local train assembly and fabrication create work in body modules, fit-out, wiring, coatings, systems integration, inspection and maintenance while bogies, batteries, windows and doors remain imported inputs requiring supplier and process qualification. Infrastructure work supports Iraqi concrete/precast production, civil erection, stations, utilities, solar installation and supervision. Tooling, training, process qualification and supplier access can leave reusable industrial capacity, shorter repair chains and retained skills after construction. Local employment and supplier income circulate in IQD and can generate Iraqi tax receipts; no multiplier or tax recovery is booked without evidence.", "",
        f"The operating allowance supports **{city_model['workforce']['total_fte']:,} indicative FTE** with annual labour cost of IQD {city_model['workforce']['annual_labour_usd']*fx/1e9:.2f} billion. These are operating positions, not construction or manufacturing job counts. Construction employment requires validated work hours, productivity, wage rates, shift cover and local-content contracts; no fabricated job total is assigned. The third-party proposal may also use Iraqi civil labour, so its local share cannot be assumed zero.", "",
        "A sustainable appraisal must demonstrate phased service before full-network completion, realistic paid demand and affordable tariffs, funded debt/interest/reserves within the public limit, placed IQD facilities, supplier and labour qualification, lifecycle replacement funding and an accepted environmental/physical design. Current software and ledger checks establish planning consistency, not those outcomes.", ""]
    if phased_programme_cases:
        pc = phased_programme_cases["low_demand"]
        pm = pc["metrics"]
        lines.extend(["## Recalculation: conditional phased opening", "",
            "The earlier USD 9.890 billion result combined whole-fleet stage batching, no fares before the final capital payment and reserve deposits always funded with additional public cash. Ready-task dispatch now pipelines work within the same resource limits, gates train production on the new plant, and funds reserves from available project cash before seeking support. The full-network-only result above remains a conservative comparator.", "",
            f"With line openings tied to completed line and shared/depot work plus a {config['model']['phased_commissioning_months']}-month commissioning allowance, first revenue begins in **month {pm['operations_start_month']}**, and all nine lines operate from **month {pm['full_network_operations_start_month']}** after financial close. These dates are conditional planning milestones, not authorisation to run trains.", "",
            "Each line's controlled trainset share allocates revenue and variable OPEX; its own 50% / 75% / 100% ramp applies. From first opening, 25% of full-network OPEX is fixed and 75% scales with opened fleet. This proxy can misstate early demand, central staffing and transfer benefits; a surveyed phase-specific operating plan is required. The same nominal fares, capital total, debt terms and 25% grant apply in every case.", "",
            "![Phased operating cash and additional liquidity](finance/baghdad-phased-cashflows.png)", "",
            "| Opening / demand scenario | Additional funding beyond 25% capital, USD bn | Conditional lifetime public cash, USD bn |", "|---|---:|---:|",
            f"| All fares after final capital payment | {cumulative_gap/1e9:.3f} | {summary['conditional_total_public_cash_required_usd']/1e9:.3f} |",
            *[f"| Phased: {name.replace('_', ' ')} | {case['additional_funding_required_usd']/1e9:.3f} | {case['conditional_total_public_cash_required_usd']/1e9:.3f} |" for name, case in phased_programme_cases.items()], "",
            "| Line | Planned opening month | Fleet / variable-cost share |", "|---|---:|---:|",
            *[f"| {phase['line']} | {phase['opening_month']} | {phase['weight']:.2%} |" for phase in phased_city['phases']], "",
            f"All these are gross nominal liquidity contributions, conditional on funding. Later operating surplus is retained and is not netted against earlier required injections. The phased city ledger ends with USD {pm['final_unrestricted_cash_usd']/1e9:.3f} billion of unrestricted cash; no distribution or return to the sponsor is assumed. The plant ledger has no manufacturing income/OPEX: it remains a capital-financing allowance. A 25% direct grant also does not cap sovereign IQD bond liabilities or guarantees.", "",
            "[Phased programme monthly cashflow](finance/baghdad-programme-phased-monthly-cashflow.csv) · [phased programme annual cashflow](finance/baghdad-programme-phased-annual-cashflow.csv)", ""])
    lines.extend(comparison_lines)
    rec = analysis["reconciliation"]
    updated = ["## Independent reconciliation, priced gap finance and six-month tranches", "",
        f"Capital sources still total USD {rec['capital_uses_usd']/1e6:,.3f}m. The independent pooled-cash reconstruction requires USD {rec['gross_additional_liquidity_usd']/1e6:,.3f}m of gross extra cash and retains USD {rec['later_retained_cash_usd']/1e6:,.3f}m later, leaving a **USD {rec['net_lifetime_liquidity_gap_usd']/1e6:,.3f}m nominal net deficit before pricing additional gap finance**. These three amounts answer different questions. The original capital principal is repaid in the lifetime cash ledger, not added to CAPEX a second time. City EPC is now spread over direct works; the initial baseline-freeze task no longer receives the full programme overhead allowance.", "",
        "[Detailed arithmetic and Iraqi financing routes](Baghdad/engineering/finance/FUNDING-RECONCILIATION.md) · [six-month reference bond/loan requirements](finance/baghdad-unfunded_reference-six-month-tranches.csv) · [six-month blended candidate](finance/baghdad-blended_candidate-six-month-tranches.csv) · [independent calculation](finance/baghdad-finance-reconciliation.json).", "",
        "Green debt replaces qualified conventional borrowing; grants replace domestic capital debt; guarantees supply credit enhancement rather than cash. The new sensitivity charges supplemental IQD funding for interest and fees, sweeps later surplus to repayment, and exposes cash beyond its illustrative IQD 13tn cap and any unpaid terminal loan. The earlier gross cash-support figures below assume external contributions; they are not a priced bridge-loan requirement.", "",
        "| Priced gap-finance sensitivity | Gross gap draws, IQD tn | Uncovered cash, IQD tn | Unpaid terminal loan, IQD tn |", "|---|---:|---:|---:|",
        *[f"| {name.replace('_', ' ')} | {case['metrics']['total_supplemental_draw_iqd']/1e12:.3f} | {case['metrics']['uncovered_support_iqd']/1e12:.3f} | {case['metrics']['terminal_supplemental_balance_iqd']/1e12:.3f} |" for name, case in analysis["cases"].items()], "",
        "The candidate mix is uncommitted: eligible IQD green bonds at an assumed 4% plus enhancement fees; USD 25m equivalent climate capital grant; USD 300m equivalent net development-rights proceeds; and USD 25m equivalent annual new net local receipts at full opening. The grant, valuation, legal powers and IQD concessional facility need evidence. Existing rents/fare receipts cannot be counted again. With constant nominal fares and OPEX, a terminal unpaid loan means that sensitivity has not achieved self-financing.", ""]
    indexed = analysis["cases"]["fare_5pct_opex_5pct"]
    priced = indexed["fare_policy"]
    updated.extend(["## Additional pricing and OPEX inflation sensitivities", "",
        f"The requested paired sensitivity increases fares and OPEX **5% annually from financial close**, while testing income growth separately. At 5% income growth and assumed -0.30 real-price elasticity, the illustrative blended case peaks at **IQD {indexed['metrics']['peak_supplemental_balance_iqd']/1e12:.3f}tn** supplemental debt and ends with IQD {indexed['metrics']['terminal_supplemental_balance_iqd']/1e12:.3f}tn unpaid. {repayment_outcome(indexed['metrics'])} Placed early financing, candidate grant/rights receipts, fixed nominal debt terms and income growth remain assumptions. It is not a committed funding outcome.", "",
        f"Average nominal tickets move from IQD {priced['first_opening']['average_paid_fare_iqd']:,.0f} at first opening to IQD {priced['full_opening']['average_paid_fare_iqd']:,.0f} at full opening; 44 trips remain {priced['full_opening']['forty_four_trips_income_share']:.1%} of the indexed income proxy when incomes grow 5%. Separate cases test 2% income growth, 7% OPEX inflation, peak/off-peak tiers, fixed demand, and rental indexation. Capital escalation and future FX changes remain outside these sensitivities.", "",
        "[Paired 5% six-month financing](finance/baghdad-fare_5pct_opex_5pct-six-month-tranches.csv) · [monthly tickets and affordability](finance/baghdad-fare_5pct_opex_5pct-monthly-prices.csv) · [variable-ticket six-month financing](finance/baghdad-variable_fare_5pct_opex_5pct-six-month-tranches.csv). The detailed report contains the NPV, all assumptions and downside cases.", ""])
    updated.extend(early_repayment_report(analysis, "finance"))
    lines[4:4] = updated
    (country / "IRAQ-FUNDING-PROGRAMME.md").write_text("\n".join(lines))
    print(f"wrote Baghdad programme: USD {summary['total_capex_usd']:,.2f}, government 25%, additional cash gap USD {cumulative_gap:,.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
