#!/usr/bin/env python3
"""Aggregate three current Iraq examples plus one shared manufacturing plant."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "design/city-generation/src"))
from osr_scenario.iraq_finance import build_financing


def main() -> int:
    country = ROOT / "cities/catalogue/west-asia/Iraq"
    config_path = ROOT / "lib/templates/iraq-funding.toml"
    config = tomllib.loads(config_path.read_text())
    capex = tomllib.loads((ROOT / "lib/templates/capex-costs.toml").read_text())
    cities = {}
    source_paths = [config_path, ROOT / "lib/templates/capex-costs.toml", Path(__file__),
                    ROOT / "design/city-generation/src/osr_scenario/iraq_finance.py"]
    modules = {}
    for name, cars in (("Baghdad", 6), ("Samawah", 3), ("Mosul", 4)):
        path = country / name / "engineering/finance/summary.json"
        finance = json.loads(path.read_text())
        funding = finance["structured_financing"]
        if funding.get("schedule_status") != "linked-to-budget-work-packages" or not all(funding["checks"].values()):
            raise ValueError(f"{name}: current reconciled funding schedule required")
        cities[name] = funding
        design_path = country / name / "design.toml"
        design = tomllib.loads(design_path.read_text())
        modules[name] = sum(f["trainset_count"] for f in design["fleets"]) * cars
        source_paths.extend([path, design_path])
    anchor = max(modules, key=modules.get)
    factory_usd = modules[anchor] * capex["production_plant"]["per_vehicle_usd"]
    factory_buckets = []
    factory_contracts = []
    for bucket, amount in (("production_plant", factory_usd), ("epc_overhead", factory_usd*capex["overhead"]["epc_fraction"])):
        share = capex["procurement_origin"]["imported_share"][bucket]
        factory_buckets.append({"bucket": bucket, "total_usd": amount, "imported_usd": amount*share})
        factory_contracts.append({"bucket": bucket, "budget_usd": amount, "imported_share": share, "planned_start_day": 0, "planned_finish_day": 520})
    # Two working years is an explicitly separate factory planning assumption,
    # not a commissioned facility or a vendor-backed construction programme.
    factory = build_financing(factory_buckets, factory_contracts,
        {"low_capacity_use": {"annual_revenue_usd": 0}, "high_capacity_use": {"annual_revenue_usd": 0}}, 0, config)
    components = {**cities, "Shared factory": factory}
    annual_by_year = {}
    keys = ("capex_usd", "government_capital_received_usd", "chinese_export_credit_draw_usd", "domestic_bonds_draw_usd", "bank_credit_draw_usd", "revenue_usd", "opex_usd", "debt_service_usd", "fees_usd", "government_operations_and_debt_support_usd", "government_total_cash_usd", "government_total_cash_iqd", "closing_cash_usd", "closing_restricted_reserve_usd")
    for funding in components.values():
        for row in funding["base"]["annual"]:
            target = annual_by_year.setdefault(row["year"], {"year": row["year"], **{k: 0.0 for k in keys}})
            for key in keys:
                target[key] += row[key]
    annual = [annual_by_year[y] for y in sorted(annual_by_year)]
    sources = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    summary = {"schema_version": 1, "status": "planning-uncommitted", "funding_committed": False,
               "scope": "Baghdad, Samawah, Mosul and one shared national plant; other Iraqi cities excluded",
               "calendar_basis": "All four financial closes at month zero: fiscal exposure comparison only; joint shared-factory resource sequencing not accepted",
               "factory": {"cost_usd": factory_usd, "epc_usd": factory_usd*capex["overhead"]["epc_fraction"], "anchor_city": anchor, "vehicle_modules": modules[anchor], "planning_build_working_days": 520,
                           "funding": factory},
               "capital_sources_usd": {k: sum(v["base"]["metrics"]["capital_sources_usd"][k] for v in components.values()) for k in factory["base"]["metrics"]["capital_sources_usd"]},
               "total_capex_usd": sum(v["base"]["metrics"]["total_capex_usd"] for v in components.values()),
               "peak_annual_public_cash_usd": max(r["government_total_cash_usd"] for r in annual), "annual": annual, "sources_sha256": sources}
    directory = country / "finance"
    directory.mkdir(exist_ok=True)
    (directory / "three-city-programme.json").write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n")
    with (directory / "three-city-annual-cashflow.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(annual[0]))
        writer.writeheader()
        writer.writerows(annual)
    lines = ["# Iraq three-city funding programme", "", "Current examples: [Baghdad](Baghdad/README.md), [Samawah](Samawah/README.md), [Mosul](Mosul/README.md). All funding is proposed and uncommitted.", "",
        "## Consolidated sources and uses", "", "| Source | USD million |", "|---|---:|"]
    lines.extend(f"| {k.replace('_', ' ')} | {v/1e6:,.2f} |" for k, v in summary["capital_sources_usd"].items())
    lines.extend([f"| **Total uses** | **{summary['total_capex_usd']/1e6:,.2f}** |", "",
        f"The shared factory is counted **once**: USD {factory_usd/1e6:,.2f} million plus USD {summary['factory']['epc_usd']/1e6:,.2f} million EPC. Its sizing basis is {modules[anchor]:,} vehicle modules for {anchor}, using the controlled per-module national planning rate. Imported tooling receives proposed Chinese export credit within the existing plant budget. Costs for the three- and four-/six-car families remain family-specific planning rates; the LM3 detailed build estimate is not a qualified metro4/metro6 factory bid.", "",
        f"Peak annual government cash under the simultaneous-close fiscal scenario: **USD {summary['peak_annual_public_cash_usd']/1e6:,.2f} million**. This includes capital, construction interest, fees, reserves and operating/debt support. It is not an appropriation.", "",
        "## Cash and contractual structure", "",
        "1. An Iraqi public programme sponsor seeks MoF borrowing authority and budget appropriations. A proposed sovereign IQD bond programme uses the established MoF/CBI issuance route, subject to legal review and placement. Municipal bond powers are not assumed.",
        "2. Chinese export buyer credit is proposed against qualified Chinese invoices for PV equipment, bogies, batteries, windows, doors and one national tooling programme. The assumed 85% advance leaves a 15% downpayment; the model does not treat every import as eligible Chinese content.",
        "3. Government covers 60% of capital remaining after proposed export-credit proceeds; domestic IQD bonds cover 30% and IQD term bank credit 10% of that remainder. Noneligible imports must still be purchased in foreign currency by the sponsor.",
        "4. Each financing draw starts its own grace and repayment clock. Funds go to milestone requirements; receipts, invoices and actual payments remain empty until recorded. Fees and interest are public cash outflows, not silently capitalised loan proceeds.",
        "5. Fare and station receipts pay OPEX first, then debt service. Cash deficits require an explicit public contribution. A restricted debt-service reserve is separately funded; subsidy is excluded from DSCR. Surplus is held as project cash.",
        "6. Delayed government payments and declined export credit create visible gaps. Domestic term credit is an explicit permanent capital tranche, not a fictitious unlimited bridge. Any later bridge, guarantee, rollover or refinancing needs a separate approved facility.", "",
        "## Rollout and financial close", "",
        "The city schedules expose the current constrained manufacturing/works capacity. Full-network fare revenue begins only after all budget milestones; phased openings need a new resource and revenue baseline. Concurrent financial closes in this consolidation compare fiscal exposure; they do not validate concurrent use of one plant. Joint factory sequencing, additional production lanes, city phasing and an approved Iraqi working calendar remain required. The separate two-working-year factory build assumption is unquoted and must be reconciled with that joint plan.", "",
        "Required before financial close: approved public sponsor/borrowing powers, appropriations and subsidy agreement; qualified origin and supplier quotations; lender guarantees/insurance and signed term sheets; IQD bond placement and redemption plan; lender draw-window and FX access approvals; surveyed demand and fare policy; tax, duty, land and utility pricing; independently reviewed resource calendar, cost contingency and reserve covenants.", "",
        "## Model and evidence", "",
        "[Combined annual cashflow](finance/three-city-annual-cashflow.csv) · [machine-readable programme](finance/three-city-programme.json) · [editable Iraq assumptions](../../../../lib/templates/iraq-funding.toml). City financing pages contain monthly native-currency debt and cash ledgers, charts and downside tests.", "",
        "[IMF 2025 Article IV](https://www.imf.org/en/news/articles/2025/07/08/pr-25243-iraq-imf-executive-board-concludes-2025-article-iv-consultation) supplies the historical 2024 FX anchor, not a current dealing rate. [CBI fiscal-agent description](https://www.cbi.iq/page/26) and [Injaz issue example](https://cbi.iq/news/view/2620) support the domestic sovereign-bond context. [China Exim export buyer credit](https://english.eximbank.gov.cn/Business/CreditB/SupportingFT/201810/t20181016_6965.html) supports the instrument concept; numeric terms and eligibility are unconfirmed appraisal assumptions.", ""])
    (country / "IRAQ-FUNDING-PROGRAMME.md").write_text("\n".join(lines))
    print(f"wrote Iraq programme: USD {summary['total_capex_usd']:,.2f}, shared plant counted once")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
