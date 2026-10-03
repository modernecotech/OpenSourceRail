"""Schedule-linked Iraq funding appraisal with native-currency debt vintages.

This is a transparent budget and liquidity model, not a lending decision.
Loan grace runs from each draw: a delayed railway does not delay repayment.
"""
from __future__ import annotations

import copy
import math
from collections import defaultdict
from typing import Any

TRANCHES = ("chinese_export_credit", "domestic_bonds", "bank_credit")


def city_funding_config(config: dict, city: str) -> dict:
    """Apply the controlled city scenario without changing other Iraqi models."""
    result = copy.deepcopy(config)
    override = result.pop("city_overrides", {}).get(city, {}).get("model", {})
    result["model"].update(override)
    if "government_share_of_total" in result["model"]:
        for key in ("government_share_of_remainder", "bond_share_of_remainder", "credit_share_of_remainder"):
            result["model"].pop(key, None)
    validate(result)
    return result


def number(value: Any, label: str, *, maximum: float | None = None) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{label}: boolean is not a monetary assumption")
    result = float(value)
    if not math.isfinite(result) or result < 0 or (maximum is not None and result > maximum):
        raise ValueError(f"{label}: expected finite nonnegative value" + (f" <= {maximum}" if maximum is not None else ""))
    return result


def validate(config: dict) -> None:
    model = config["model"]
    for key in ("iqd_per_usd", "working_days_per_year", "operating_years"):
        if number(model[key], key) <= 0:
            raise ValueError(f"{key} must be positive")
        if key != "iqd_per_usd" and model[key] != int(model[key]):
            raise ValueError(f"{key} must be a whole count")
    if "government_share_of_total" in model:
        number(model["government_share_of_total"], "government_share_of_total", maximum=1)
        shares = [number(model[key], key, maximum=1) for key in (
            "bond_share_of_residual", "credit_share_of_residual")]
    else:
        shares = [number(model[key], key, maximum=1) for key in (
            "government_share_of_remainder", "bond_share_of_remainder", "credit_share_of_remainder")]
    if not math.isclose(sum(shares), 1, abs_tol=1e-10):
        raise ValueError("remainder funding shares must sum to one")
    number(model["export_invoice_advance"], "export_invoice_advance", maximum=1)
    scope = model.get("export_eligibility_scope", "selected-components")
    if scope not in {"selected-components", "all-imports-pending-qualification"}:
        raise ValueError("unknown export eligibility scope")
    if "government_usd_share_of_imports" in model:
        share = number(model["government_usd_share_of_imports"], "government_usd_share_of_imports", maximum=1)
        if scope != "all-imports-pending-qualification" or not math.isclose(share + model["export_invoice_advance"], 1):
            raise ValueError("USD government cash and loan must cover the import basket exactly")
    number(model["discount_rate"], "discount_rate", maximum=1)
    number(model["debt_service_reserve_months"], "debt_service_reserve_months")
    number(model["pre_ntp_working_days"], "pre_ntp_working_days")
    if not model["revenue_ramp"]:
        raise ValueError("revenue_ramp must not be empty")
    for value in model["revenue_ramp"]:
        number(value, "revenue_ramp", maximum=1)
    for name in TRANCHES:
        loan = config[name]
        expected = "USD" if name == "chinese_export_credit" else "IQD"
        if loan["currency"] != expected:
            raise ValueError(f"{name}: currency must be {expected}")
        for key in ("annual_rate", "arrangement_fee", "undrawn_commitment_fee"):
            number(loan[key], f"{name}.{key}", maximum=1)
        for key in ("grace_months_from_draw", "repayment_months"):
            value = number(loan[key], f"{name}.{key}")
            if value != int(value) or (key == "repayment_months" and value == 0):
                raise ValueError(f"{name}.{key}: invalid month count")
    for bucket, components in config["eligible_imports"].items():
        if sum(number(v, f"{bucket}.{k}", maximum=1) for k, v in components.items()) > 1 + 1e-10:
            raise ValueError(f"{bucket}: eligible imports exceed imported budget")


def eligible_components(buckets: list[dict], config: dict) -> list[dict]:
    result = []
    for bucket in buckets:
        imported = number(bucket["imported_usd"], "imported_usd")
        for component, share in config["eligible_imports"].get(bucket["bucket"], {}).items():
            result.append({"bucket": bucket["bucket"], "component": component,
                           "invoice_budget_usd": imported * share,
                           "origin_status": "assumed-Chinese-pending-qualification-and-quotes"})
        if config["model"].get("export_eligibility_scope") == "all-imports-pending-qualification":
            remainder = imported * (1-sum(config["eligible_imports"].get(bucket["bucket"], {}).values()))
            if remainder > .01:
                result.append({"bucket": bucket["bucket"], "component": "other_imports_pending_lender_and_origin_qualification",
                               "invoice_budget_usd": remainder,
                               "origin_status": "assumed-Chinese-pending-qualification-and-quotes"})
    return result


def scheduled_requirements(contracts: list[dict], buckets: list[dict], config: dict) -> list[dict]:
    """Map working-day milestones to assumed calendar months, including pre-NTP."""
    validate(config)
    totals = {b["bucket"]: number(b["total_usd"], b["bucket"]) for b in buckets}
    observed: dict[str, float] = defaultdict(float)
    rows: dict[int, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    m = config["model"]
    for contract in contracts:
        bucket = contract["bucket"]
        if bucket not in totals:
            raise ValueError(f"unknown capital bucket {bucket}")
        amount = number(contract["budget_usd"], "budget_usd")
        observed[bucket] += amount
        imported_share = number(contract["imported_share"], "imported_share", maximum=1)
        expected_bucket = next(b for b in buckets if b["bucket"] == bucket)
        expected_share = expected_bucket["imported_usd"] / expected_bucket["total_usd"] if expected_bucket["total_usd"] else 0
        if not math.isclose(imported_share, expected_share, abs_tol=1e-8):
            raise ValueError(f"{bucket}: stale procurement origin share")
        eligible_share = sum(config["eligible_imports"].get(bucket, {}).values())
        if m.get("export_eligibility_scope") == "all-imports-pending-qualification":
            eligible_share = 1.0
        start, finish = int(contract["planned_start_day"]), int(contract["planned_finish_day"])
        if start < 0 or finish < start:
            raise ValueError("invalid working-day schedule")
        for day, fraction in ((start - 30, .10), (start + (finish-start)//2, .55), (finish, .30), (finish+90, .05)):
            month = math.floor((day + m["pre_ntp_working_days"]) * 12 / m["working_days_per_year"])
            if month < 0:
                raise ValueError("pre-NTP cash precedes financial close assumption")
            rows[month]["capex_usd"] += amount * fraction
            rows[month]["imported_usd"] += amount * fraction * imported_share
            rows[month]["eligible_invoice_usd"] += amount * fraction * imported_share * eligible_share
    for bucket, total in totals.items():
        # Contract allocation is rounded to cents by the operations exporter.
        if abs(observed[bucket] - total) > max(.05, len(contracts) * .006):
            raise ValueError(f"{bucket}: contract budgets do not reconcile to current CAPEX")
    result = [{"month": month, **values} for month, values in sorted(rows.items())]
    if not result:
        raise ValueError("construction funding schedule is empty")
    # Reconcile harmless contract allocation rounding to authoritative budgets.
    result[-1]["capex_usd"] += sum(totals.values()) - sum(r["capex_usd"] for r in result)
    result[-1]["imported_usd"] += sum(b["imported_usd"] for b in buckets) - sum(r["imported_usd"] for r in result)
    target_eligible = sum(r["invoice_budget_usd"] for r in eligible_components(buckets, config))
    result[-1]["eligible_invoice_usd"] += target_eligible - sum(r["eligible_invoice_usd"] for r in result)
    return result


def annuity(principal: float, monthly_rate: float, months: int) -> float:
    if monthly_rate == 0:
        return principal / months
    return principal * monthly_rate / (1 - (1 + monthly_rate) ** -months)


def run_case(requirements: list[dict], annual_revenue_usd: float, annual_opex_usd: float,
             config: dict, *, capex_factor: float = 1, demand_factor: float = 1,
             fx_factor: float = 1, commissioning_delay_months: int = 0,
             export_available: bool = True, retail_bullet: bool = False,
             government_delay_months: int = 0, rate_increment: float = 0) -> dict:
    validate(config)
    for key, value in (("annual_revenue", annual_revenue_usd), ("annual_opex", annual_opex_usd),
                       ("capex_factor", capex_factor), ("demand_factor", demand_factor), ("fx_factor", fx_factor)):
        number(value, key)
    if fx_factor <= 0:
        raise ValueError("fx_factor must be positive")
    m = config["model"]
    construction_end = max(r["month"] for r in requirements)
    operating_start = construction_end + 1 + commissioning_delay_months
    operating_end = operating_start + int(m["operating_years"]) * 12
    end = max(operating_end, construction_end + max(int(config[t]["grace_months_from_draw"])+int(config[t]["repayment_months"]) for t in TRANCHES) + 1)
    by_month = {r["month"]: r for r in requirements}
    eligible_total = sum(r["eligible_invoice_usd"] for r in requirements) * capex_factor
    chinese_total = eligible_total * m["export_invoice_advance"]
    loans: dict[str, list[dict]] = {t: [] for t in TRANCHES}
    future_gov: dict[int, float] = defaultdict(float)
    future_gov_usd: dict[int, float] = defaultdict(float)
    reserve = cash = unfunded_capital = 0.0
    monthly = []
    for month in range(end):
        fx = m["iqd_per_usd"] * (fx_factor if month >= 60 else 1)
        req = by_month.get(month, {})
        capex = req.get("capex_usd", 0) * capex_factor
        planned_china = req.get("eligible_invoice_usd", 0) * capex_factor * m["export_invoice_advance"]
        remainder = capex - planned_china
        if "government_share_of_total" in m:
            scheduled_gov = capex * m["government_share_of_total"]
            residual = remainder - scheduled_gov
            if residual < -.01:
                raise ValueError("government plus planned Chinese credit exceed capital uses")
            bonds = max(0, residual) * m["bond_share_of_residual"]
            credit = max(0, residual) * m["credit_share_of_residual"]
        else:
            scheduled_gov = remainder * m["government_share_of_remainder"]
            bonds = remainder * m["bond_share_of_remainder"]
            credit = remainder * m["credit_share_of_remainder"]
        draws = {"chinese_export_credit": planned_china if export_available else 0,
                 "domestic_bonds": bonds, "bank_credit": credit}
        downpayment = req.get("eligible_invoice_usd", 0) * capex_factor * (1-m["export_invoice_advance"])
        if scheduled_gov + .01 < downpayment:
            raise ValueError("government capital share cannot cover the eligible invoice downpayment")
        future_gov[month + government_delay_months] += scheduled_gov
        scheduled_gov_usd = req.get("imported_usd", 0) * capex_factor * m.get("government_usd_share_of_imports", 0)
        if scheduled_gov_usd > scheduled_gov + .01:
            raise ValueError("government USD import cash exceeds total government capital contribution")
        future_gov_usd[month + government_delay_months] += scheduled_gov_usd
        received_gov = future_gov[month]
        row = {"month": month, "year": month // 12 + 1, "phase": "operations" if operating_start <= month < operating_end else "construction" if month < operating_start else "debt-tail",
               "iqd_per_usd": fx, "capex_usd": capex, "eligible_chinese_invoices_usd": req.get("eligible_invoice_usd", 0)*capex_factor,
               "government_capital_scheduled_usd": scheduled_gov, "government_capital_received_usd": received_gov,
               "imported_purchases_usd": req.get("imported_usd", 0)*capex_factor,
               "government_capital_usd_cash": future_gov_usd[month],
               "government_capital_iqd_cash": (received_gov-future_gov_usd[month])*fx}
        service = fees = 0.0
        for name in TRANCHES:
            terms = config[name]
            conversion = 1 if terms["currency"] == "USD" else fx
            draw = draws[name] * conversion
            rate = (terms["annual_rate"] + rate_increment)/12
            if draw:
                loans[name].append({"draw_month": month, "principal": draw, "balance": draw,
                    "payment": annuity(draw, rate, int(terms["repayment_months"]))})
            interest = principal = 0.0
            for loan in loans[name]:
                age = month - loan["draw_month"]
                balance = loan["balance"]
                interest += balance * rate * (.5 if age == 0 else 1)
                if retail_bullet and name == "domestic_bonds":
                    repayment = balance if age >= 48 else 0
                elif age > int(terms["grace_months_from_draw"]):
                    repayment = min(balance, max(0, loan["payment"] - balance * rate))
                else:
                    repayment = 0
                loan["balance"] = max(0, balance-repayment)
                principal += repayment
            commitment = 0.0
            if name == "chinese_export_credit" and export_available:
                # Phased facilities are assumed signed only at the first draw of
                # each annual procurement cohort; no decades-long free option.
                cohort = month // 12
                cohort_rows = [r for r in requirements if r["month"]//12 == cohort]
                if cohort_rows and month >= min(r["month"] for r in cohort_rows):
                    remaining = sum(r["eligible_invoice_usd"] for r in cohort_rows if r["month"] > month)
                    commitment = remaining * capex_factor * m["export_invoice_advance"] * terms["undrawn_commitment_fee"]/12
            fee = draws[name] * terms["arrangement_fee"] + commitment
            fees += fee
            debt_service = (principal + interest)/conversion
            service += debt_service
            row.update({f"{name}_draw_usd": draws[name], f"{name}_draw_native": draw,
                        f"{name}_interest_native": interest, f"{name}_principal_native": principal,
                        f"{name}_closing_balance_native": sum(l["balance"] for l in loans[name]),
                        f"{name}_debt_service_usd": debt_service, f"{name}_fees_usd": fee})
        revenue = opex = 0.0
        if operating_start <= month < operating_end:
            year = (month-operating_start)//12
            ramp = m["revenue_ramp"][min(year, len(m["revenue_ramp"])-1)]
            # IQD fares, non-fare revenue and domestic OPEX remain fixed nominal
            # at the historical FX anchor; no automatic USD-indexed fare rise.
            revenue = annual_revenue_usd/12 * demand_factor * ramp * m["iqd_per_usd"]/fx
            opex = annual_opex_usd/12 * m["iqd_per_usd"]/fx
        cfads = revenue-opex
        available = cash + cfads - service - fees
        support = max(0, -available)
        cash = max(0, available)
        # Reserve is restricted and held in USD equivalent; increase only from
        # explicit public contributions. It is released at the debt tail.
        desired = service * m["debt_service_reserve_months"] if operating_start <= month < operating_end else 0
        deposit = max(0, desired-reserve)
        release = max(0, reserve-desired)
        reserve += deposit-release
        support += deposit
        cash += release
        # A delayed appropriation or refused export facility stays visible as a
        # liquidity requirement. No invented refinancing/bridge line fills it.
        capital_gap = capex-sum(draws.values())-received_gov
        unfunded_capital += capital_gap
        outflow = capex+opex+service+fees+deposit
        inflow = revenue+sum(draws.values())+received_gov+support+release+capital_gap
        previous_cash = monthly[-1]["closing_cash_usd"] if monthly else 0
        residual = previous_cash+inflow-outflow-cash
        row.update({"revenue_usd": revenue, "opex_usd": opex, "cfads_usd": cfads,
                    "debt_service_usd": service, "fees_usd": fees,
                    "government_operations_and_debt_support_usd": support,
                    "reserve_deposit_usd": deposit, "reserve_release_usd": release,
                    "closing_restricted_reserve_usd": reserve, "closing_cash_usd": cash,
                    "unfunded_capital_cash_usd": capital_gap,
                    "closing_unfunded_capital_usd": max(0, unfunded_capital),
                    "government_total_cash_usd": received_gov+support,
                    "government_total_cash_iqd": (received_gov+support)*fx,
                    "cash_balance_residual_usd": residual})
        monthly.append(row)
    annual = []
    sum_keys = [k for k, v in monthly[0].items() if isinstance(v, (float, int)) and k not in {"month", "year", "iqd_per_usd"} and "closing_" not in k]
    for year in range(1, (end-1)//12+2):
        rows = [r for r in monthly if r["year"] == year]
        totals = {k: sum(r[k] for r in rows) for k in sum_keys}
        last = rows[-1]
        totals.update({k: v for k, v in last.items() if "closing_" in k})
        totals.update({"year": year, "phase": last["phase"], "dscr_before_public_support": totals["cfads_usd"]/totals["debt_service_usd"] if totals["debt_service_usd"] else None})
        annual.append(totals)
    operating_dscr = [r["dscr_before_public_support"] for r in annual if r["phase"] == "operations" and r["dscr_before_public_support"] is not None]
    return {"monthly": monthly, "annual": annual,
        "cash_basis": "Conditional planned payments. Explicit uncovered capital gaps require an approved facility before payment; they are not cash receipts.",
        "debt_vintages": {t: [{"draw_month": l["draw_month"], "currency": config[t]["currency"], "principal_native": l["principal"],
                               "first_repayment_month": l["draw_month"]+(48 if retail_bullet and t == "domestic_bonds" else int(config[t]["grace_months_from_draw"])+1),
                               "final_repayment_month": l["draw_month"]+(48 if retail_bullet and t == "domestic_bonds" else int(config[t]["grace_months_from_draw"])+int(config[t]["repayment_months"])),
                               "closing_balance_native": l["balance"]} for l in loans[t]] for t in TRANCHES},
        "metrics": {
        "construction_cash_months": construction_end+1, "operations_start_month": operating_start,
        "total_capex_usd": sum(r["capex_usd"] for r in monthly),
        "capital_sources_usd": {**{t: sum(r[f"{t}_draw_usd"] for r in monthly) for t in TRANCHES}, "government": sum(r["government_capital_scheduled_usd"] for r in monthly)},
        "government_capital_usd_cash": sum(r["government_capital_usd_cash"] for r in monthly),
        "government_capital_iqd_cash": sum(r["government_capital_iqd_cash"] for r in monthly),
        "imported_purchases_usd": sum(r["imported_purchases_usd"] for r in monthly),
        "minimum_operating_dscr_before_public_support": min(operating_dscr) if operating_dscr else None,
        "peak_annual_government_cash_usd": max(r["government_total_cash_usd"] for r in annual),
        "peak_annual_government_cash_iqd": max(r["government_total_cash_iqd"] for r in annual),
        "total_government_cash_usd": sum(r["government_total_cash_usd"] for r in monthly),
        "peak_monthly_unfunded_cash_usd": max(0, max(r["unfunded_capital_cash_usd"] for r in monthly)),
        "peak_cumulative_unfunded_capital_usd": max(r["closing_unfunded_capital_usd"] for r in monthly),
        "uncovered_export_finance_usd": chinese_total if not export_available else 0,
        "total_interest_usd_equivalent": sum(sum(r[f"{t}_debt_service_usd"]-r[f"{t}_principal_native"]/(1 if config[t]["currency"] == "USD" else r["iqd_per_usd"]) for t in TRANCHES) for r in monthly),
        "total_fees_usd": sum(r["fees_usd"] for r in monthly),
        "project_npv_usd": sum((-r["capex_usd"]+r["cfads_usd"])/(1+m["discount_rate"])**((r["month"]+1)/12) for r in monthly),
        "project_discount_rate": m["discount_rate"],
        "max_cash_balance_residual_usd": max(abs(r["cash_balance_residual_usd"]) for r in monthly),
        "final_debt_balances_native": {t: monthly[-1][f"{t}_closing_balance_native"] for t in TRANCHES},
    }}


def build_financing(buckets: list[dict], contracts: list[dict], revenue_cases: dict,
                    annual_opex_usd: float, config: dict) -> dict:
    requirements = scheduled_requirements(contracts, buckets, config)
    low = revenue_cases["low_capacity_use"]["annual_revenue_usd"]
    high = revenue_cases["high_capacity_use"]["annual_revenue_usd"]
    definitions = {
        "base_low_demand": (low, {}), "high_capacity_use": (high, {}),
        "capex_plus_25_percent": (low, {"capex_factor": 1.25}),
        "demand_minus_40_percent": (low, {"demand_factor": .60}),
        "iqd_depreciation_35_percent": (low, {"fx_factor": 1.35}),
        "commissioning_delay_two_years": (low, {"commissioning_delay_months": 24}),
        "china_credit_unavailable": (low, {"export_available": False}),
        "four_year_bullet_bonds": (low, {"retail_bullet": True}),
        "government_payment_delay_six_months": (low, {"government_delay_months": 6}),
        "interest_plus_three_points": (low, {"rate_increment": .03}),
        "combined_downside": (low, {"capex_factor": 1.25, "demand_factor": .60, "fx_factor": 1.35, "commissioning_delay_months": 24, "rate_increment": .03}),
    }
    cases = {name: run_case(requirements, revenue, annual_opex_usd, config, **options) for name, (revenue, options) in definitions.items()}
    base = cases["base_low_demand"]
    return {"schema_version": 1, "status": "planning-uncommitted", "funding_committed": False,
        "operational_release": False, "schedule_status": "linked-to-budget-work-packages",
        "assumptions": copy.deepcopy(config), "eligible_import_components": eligible_components(buckets, config),
        "base": base, "sensitivity_cases": {k: v["metrics"] for k, v in cases.items()},
        "checks": {"ledger_reconciles": all(v["metrics"]["max_cash_balance_residual_usd"] < .01 for v in cases.values()),
                   "debt_repaid_within_model_horizon": all(max(v["metrics"]["final_debt_balances_native"].values()) < .01 for v in cases.values())},
        "limitations": [
            "Working-day milestones use 260 working days/year and 30 working days before NTP; holidays and an approved local calendar are pending.",
            "No signed Chinese loan, supplier-origin qualification, guarantee, bond mandate, bank facility, appropriation or tax/duty assessment.",
            "Chinese origin and lender eligibility remain unqualified proxies. Default advance is 85%; Baghdad assumes all imports can qualify for 50% USD loan / 50% government USD cash. Additional imported categories require lender and supplier approval; neither assumption is a verified lender rule.",
            "Domestic bonds assume a proposed MoF sovereign IQD programme; municipal borrowing powers and market demand are not assumed.",
            "Long amortising domestic bonds are an appraisal target; the four-year bullet sensitivity exposes redemption without automatic refinancing.",
            "Construction cohorts need separately approved facilities. A long rollout does not imply a lender offers decades of draw availability.",
            "Interest is paid on drawn native balances; mid-month draw convention, monthly repayment, fees paid by government; no interest capitalisation.",
            "All cash is nominal; no inflation/escalation in base. IQD revenue and OPEX are translated at scenario FX; imported energy/parts OPEX needs a separate currency survey.",
            "Unquoted CAPEX budgets remain nominal USD planning values. IQD tranches and appropriations convert at draw-date FX; no automatic local supplier price benefit from depreciation is assumed.",
            "Income used for labour and fares is the retained country-finance planning proxy, not a verified current Iraqi household median or an agreed wage/fare contract.",
            "Government payment delays and unavailable China credit produce explicit capital cash gaps; no committed bridge credit is assumed.",
            "Restricted DSRA targets six times current monthly service. Support cash is a required contribution, not a commitment; repayments and reserve balances are conditional on it. Baghdad programme caps government capital at 25% and separately discloses the additional unfunded requirement. Future-service covenant testing is pending.",
            "Battery renewal reserve remains inside existing rolling-stock maintenance OPEX; no second battery CAPEX is added.",
            "Demand is capacity-led, not a surveyed forecast. Passing reconciliation does not demonstrate affordability or bankability.",
        ]}
