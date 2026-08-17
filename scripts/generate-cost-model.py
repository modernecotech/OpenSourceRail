#!/usr/bin/env python3
"""Render docs/cost-model.md from machine-readable cost sources."""

from __future__ import annotations

import argparse
import runpy
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CAPEX_PATH = REPO_ROOT / "lib/templates/capex-costs.toml"
COUNTRY_FINANCE_PATH = REPO_ROOT / "lib/templates/country-finance.toml"
ECONOMIC_BENEFITS_PATH = REPO_ROOT / "lib/templates/economic-benefits.toml"
BOM_SOURCE = REPO_ROOT / "docs/rolling-stock/light-metro-3car/bom-skeleton.md"
BOM_EXPORTER = REPO_ROOT / "scripts/export-light-metro-bom.py"
TRAINSET_BUILD_COST_PATH = REPO_ROOT / "mechanical-py/catalog/buildable-trainset/trainset-build-cost.json"
FACTORY_PLAN_PATH = REPO_ROOT / "mechanical-py/catalog/buildable-trainset/factory-plan.json"
DEFAULT_OUT = REPO_ROOT / "docs/cost-model.md"

TRAINSET_ORDER = [
    "urban-shuttle-1car",
    "tram-2car",
    "light-metro-3car",
    "metro-4car",
    "metro-6car",
]
STATION_ORDER = [
    "halt",
    "standard",
    "major",
    "terminal",
    "depot-terminal",
    "interchange",
    "interchange-elevated",
]
DEPOT_ORDER = ["main-heavy", "secondary-medium", "layup-minimal"]


def _load_toml(path: Path) -> dict:
    return tomllib.loads(path.read_text())


def _load_json(path: Path) -> dict:
    import json

    return json.loads(path.read_text())


def _money_short(value: float) -> str:
    value = float(value)
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.1f} M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.0f} k"
    return f"${value:.0f}"


def _usd_int(value: float) -> str:
    return f"{int(round(value)):,.0f} USD"


def _eur_mirror(value: float, usd_to_eur: float) -> str:
    return f"EUR {value * usd_to_eur / 1_000_000:.3f} M"


def _pct(value: float, digits: int = 0) -> str:
    rendered = f"{value * 100:.{digits}f}"
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return f"{rendered}%"


def _bom_rows() -> list[dict[str, str]]:
    module = runpy.run_path(str(BOM_EXPORTER))
    return module["export_rows"](BOM_SOURCE)


def _bom_totals(assembly_fraction: float) -> dict[str, int]:
    rows = _bom_rows()
    direct = sum(int(row["base_usd"]) for row in rows)
    low_direct = sum(int(row["cost_low_usd"]) for row in rows)
    high_direct = sum(int(row["cost_high_usd"]) for row in rows)
    assembly = round(direct * assembly_fraction)
    low_assembly = round(low_direct * assembly_fraction)
    high_assembly = round(high_direct * assembly_fraction)
    return {
        "direct": direct,
        "assembly": assembly,
        "with_assembly": direct + assembly,
        "low_direct": low_direct,
        "low_with_assembly": low_direct + low_assembly,
        "high_direct": high_direct,
        "high_with_assembly": high_direct + high_assembly,
    }


def render_cost_model() -> str:
    capex = _load_toml(CAPEX_PATH)
    trainset_build_cost = _load_json(TRAINSET_BUILD_COST_PATH)
    factory_plan = _load_json(FACTORY_PLAN_PATH)
    country_finance = _load_toml(COUNTRY_FINANCE_PATH)
    benefits = _load_toml(ECONOMIC_BENEFITS_PATH)
    assembly_fraction = float(capex["trainset_cost_basis"]["local_assembly_fraction"])
    bom = _bom_totals(assembly_fraction)

    usd_to_eur = float(capex["schema"]["usd_to_eur"])
    trainset_units = {str(k): float(v) for k, v in capex["trainset_unit_usd"].items()}
    plant_base = float(capex["production_plant"]["per_vehicle_usd"])
    plant_high = float(capex["production_plant"]["high_sensitivity_per_vehicle_usd"])
    factory_size = factory_plan["factory_size"]
    factory_machinery = factory_plan["machinery_cost"]
    light_unit = trainset_units["light-metro-3car"]
    recalculated_trainset = float(trainset_build_cost["total_build_cost_usd"])
    fitout_glazing_total = float(trainset_build_cost["included_fitout_doors_glazing_total_base_usd"])
    fitout_rows = {
        str(row["scope"]): row for row in trainset_build_cost["included_fitout_doors_glazing_scope"]
    }
    basic_fitout = float(
        fitout_rows["seats, floors, grab rails, and interior lighting"]["included_base_usd"]
    )
    hvac_fitout = float(fitout_rows["roof HVAC"]["included_base_usd"])
    doors_glazing = float(
        fitout_rows[
            "side windows, side doors, door sill/emergency kits, and panoramic end glass"
        ]["included_base_usd"]
    )
    qa_handover = light_unit - recalculated_trainset
    if qa_handover < 0:
        raise ValueError("light-metro-3car trainset unit is below recalculated build-cost floor")

    default_finance = country_finance["countries"]["XX"]
    pass_share = float(default_finance["revenue_case_monthly_pass_income_share"])
    farebox_target = float(default_finance["farebox_recovery_target"])
    local_multiplier = float(benefits["local_recirculation"]["construction_multiplier"])
    job_output_multiple = float(
        benefits["local_recirculation"]["job_year_output_multiple_of_median_income"]
    )
    social_carbon = float(benefits["environment"]["social_carbon_usd_per_tonne"])

    lines: list[str] = [
        "# OpenSourceRail Cost Model",
        "",
        "This file is generated by `scripts/generate-cost-model.py`.",
        "Do not hand-edit the numbers here; change the source data and regenerate.",
        "",
        "## Sources Of Truth",
        "",
        "| Number family | Source |",
        "|---|---|",
        "| CAPEX unit rates, USD/EUR reporting views, EPC, solar, charging | `lib/templates/capex-costs.toml` |",
        "| Light-metro 3-car BOM line items | `docs/rolling-stock/light-metro-3car/bom-skeleton.md` |",
        "| Generated rolling-stock BOM CSV | `build/bom/rolling_stock_bom.csv` via `scripts/export-light-metro-bom.py` |",
        "| Recalculated LM3 build cost | `mechanical-py/catalog/buildable-trainset/trainset-build-cost.json` |",
        "| Country finance and fare assumptions | `lib/templates/country-finance.toml` |",
        "| Broad-benefit assumptions | `lib/templates/economic-benefits.toml` |",
        "",
        "Generated `*_eur` fields are converted reporting views at "
        f"{usd_to_eur:.2f} USD->EUR.",
        "The detailed civil marketplace anchors live in "
        "[`docs/civil/marketplace-cost-anchors.md`](civil/marketplace-cost-anchors.md).",
        "",
        "## Rolling Stock",
        "",
        "Rolling stock is budgeted by **local-owner trainset-family planning "
        "unit**, not by multiplying an inflated per-car price. A 3-car "
        f"`light-metro-3car` trainset is **{_money_short(light_unit)} per "
        "trainset** with `*_eur` reporting views generated at "
        f"{usd_to_eur:.2f} USD->EUR.",
        "",
        "The current [`light-metro-3car` build-cost estimate]"
        "(../mechanical-py/catalog/buildable-trainset/trainset-build-cost.md) "
        f"uses the promoted design candidate cost of {_usd_int(trainset_build_cost['direct_material_and_supplier_cost_usd'])}, "
        f"adds {float(trainset_build_cost['labor_hours']):,.0f} h of direct labour at "
        f"${float(trainset_build_cost['labor_rate_usd_per_hour']):.0f}/h, then applies a "
        f"{_pct(float(trainset_build_cost['unexpected_cost_premium_fraction']))} unexpected-cost premium. "
        f"That gives {_usd_int(recalculated_trainset)} per 3-car consist. City CAPEX "
        f"keeps the rounded {_usd_int(light_unit)} trainset unit so there is still a small "
        "nominal QA/acceptance and local handover margin, while fixtures/tooling sit "
        "in the railway production plant and warranty, spares, and routine commissioning "
        "support sit in OPEX.",
        "",
        "The direct material/supplier-module bucket already includes the requested "
        f"passenger fit-out, HVAC, windows, and doors: {_money_short(basic_fitout)} for "
        "seats/floor systems/grab rails/interior lighting, "
        f"{_money_short(hvac_fitout)} for three roof HVAC units, and "
        f"{_money_short(doors_glazing)} for side windows, powered side doors, door sill/emergency kits, "
        f"and panoramic end glass. The included requested-scope subtotal is "
        f"{_money_short(fitout_glazing_total)} before labour and premium, so no extra "
        "$20k interior allowance is added unless a deployment chooses to carry a "
        "separate contingency.",
        "",
        "| 3-car trainset cost bucket | Basis | Cost |",
        "|---|---|---:|",
        "| Direct material and supplier modules | Promoted design candidate cost metric: frame, panels, glazing, doors, articulation/gangways, end couplers, bogies, suspension air supply, traction, batteries, HVAC, electronics, interiors | "
        f"{_money_short(trainset_build_cost['direct_material_and_supplier_cost_usd'])} |",
        "| Direct labour | "
        f"{float(trainset_build_cost['labor_hours']):,.0f} h explicit first-article/final-assembly plan at "
        f"${float(trainset_build_cost['labor_rate_usd_per_hour']):.0f}/h | "
        f"{_money_short(trainset_build_cost['labor_cost_usd'])} |",
        "| Unexpected-cost premium | "
        f"{_pct(float(trainset_build_cost['unexpected_cost_premium_fraction']))} for rework, logistics, consumables, local fabrication variation, and shop learning | "
        f"{_money_short(trainset_build_cost['unexpected_cost_premium_usd'])} |",
        "| Recalculated build estimate | Direct modules + labour + unexpected-cost premium | "
        f"{_money_short(recalculated_trainset)} |",
        "| Nominal QA + handover rounding margin | Acceptance evidence, test dossier, local movement, manuals/training handover; warranty/spares stay in OPEX | "
        f"{_money_short(qa_handover)} |",
        "| **Total per 3-car trainset** | Local-owner production planning unit | "
        f"**{_money_short(light_unit)}** |",
        "",
        "| Family | USD / trainset | EUR mirror |",
        "|---|---:|---:|",
    ]

    for family in TRAINSET_ORDER:
        value = trainset_units[family]
        lines.append(f"| `{family}` | {_money_short(value)} | {_eur_mirror(value, usd_to_eur)} |")

    lines.extend([
        "",
        "The base value assumes direct procurement, local final assembly, common "
        "bogie modules, one-metre clip-on fiberglass non-structural cladding, COTS "
        "doors/windows/HVAC/interior modules, open control electronics, and no "
        "proprietary CBTC onboard bundle. It includes labour, shop overhead, "
        "nominal per-unit QA/acceptance evidence, and local handover logistics. "
        "It does **not** repeat fixtures, tooling, production-readiness, "
        "warranty, initial spares, or routine commissioning support inside every "
        "trainset. Fixtures and tooling are carried in the production-plant line; "
        "spares, warranty response, and routine commissioning support are OPEX.",
        "",
        "The rolling-stock BOM carries line-level low/base/high bands in "
        "generated path `build/bom/rolling_stock_bom.csv`. "
        "For the `light-metro-3car`, the direct-material band is "
        f"{bom['low_direct']:,.0f}-{bom['high_direct']:,.0f} USD before labour; "
        f"adding the BOM's {_pct(assembly_fraction)} assembly allowance gives a "
        f"{bom['low_with_assembly']:,.0f}-{bom['high_with_assembly']:,.0f} USD "
        "older marketplace-floor consist band, with the base case landing at "
        f"{bom['with_assembly']:,.0f} USD. This remains an audit lower bound; "
        "the current build estimate above supersedes it for trainset planning.",
        "",
        "## Railway Production Plant",
        "",
        "Each country carries one shared railway production-plant setup allowance; "
        "cities do not duplicate the factory in city CAPEX. The national plant is "
        "sized to the largest single-city fleet programme and reused through a "
        "phased rollout. The base case is "
        f"**{_money_short(plant_base)} USD per vehicle/car module**, not per "
        "trainset; the earlier "
        f"**{_money_short(plant_high)} USD per vehicle/car module** value is "
        "kept as a high sensitivity check rather than the default.",
        "",
        "This line covers lean local production/assembly setup: reusable one-metre "
        "panel moulds, clip/drill gauges, basic steel fixtures, plant services, "
        "commissioning bay setup, material handling, "
        "homologation/production-readiness work, and first-article support. It is "
        "deliberately separate from the trainset unit above, so procurement costs "
        "and national plant setup remain auditable instead of being hidden in one "
        "large rolling-stock number.",
        "",
        "The generated LM3 pilot factory plan sizes the minimum enclosed building "
        f"at about {float(factory_size['recommended_enclosed_factory_area_m2']):,.0f} m2 "
        f"({float(factory_size['recommended_enclosed_factory_area_ft2']):,.0f} ft2), plus "
        f"{float(factory_size['outside_yard_and_test_apron_m2']):,.0f} m2 of outside yard/test apron "
        "and a separate short depot/test track. Its rough machinery and setup "
        f"list totals {_money_short(float(factory_machinery['rough_order_machinery_total_usd']))}, "
        f"including {_pct(float(factory_machinery['setup_contingency_fraction']))} equipment setup contingency. "
        "This one-time national factory setup remains separate from the per-trainset build estimate.",
        "",
        "| Example | Base plant allowance | High sensitivity |",
        "|---|---:|---:|",
        f"| 1-car vehicle module | {_money_short(plant_base)} | {_money_short(plant_high)} |",
        f"| 3-car `light-metro-3car` trainset | {_money_short(plant_base * 3)} | {_money_short(plant_high * 3)} |",
        "",
        "## Procurement Origin and Capital Boundary",
        "",
        "Each generated city and national brief separates imported value from "
        "local value. Imported value is the minimum foreign-currency / international "
        "capital requirement; local value can be funded with domestic-currency bonds, "
        "public equity, or other local sources. Until a country supplier audit is "
        "available, the controlled planning shares are:",
        "",
        "| CAPEX bucket | Imported share | Local share |",
        "|---|---:|---:|",
        *[
            f"| `{bucket}` | {float(imported):.0%} | {1.0 - float(imported):.0%} |"
            for bucket, imported in capex["procurement_origin"]["imported_share"].items()
        ],
        "",
        "These are localization-first targets: standard structures, fabrication, "
        "installation, wiring/cabinets, software integration, and project services "
        "are assigned locally, while specialist cells, power electronics, control "
        "hardware, PV equipment, and initial machinery remain imported. They are "
        "planning assumptions until replaced by a country rules-of-origin and "
        "supplier-capability audit.",
        "",
        "## Foreign-Turnkey Comparator",
        "",
        "The city finance summaries and national briefs include a controlled, "
        "editable foreign-company turnkey sensitivity. It is not a vendor quotation "
        "or a claim about any named supplier. The comparator applies a cost multiplier "
        "to the same OSR network, fleet, service, and energy scope, then estimates the "
        "share of that price requiring foreign currency or international capital.",
        "",
        "| Variable | Controlled value |",
        "|---|---:|",
        *[
            f"| `{case}` cost multiplier | {float(multiplier):.2f}× OSR CAPEX |"
            for case, multiplier in capex["foreign_turnkey_comparator"]["cost_multiplier"].items()
        ],
        f"| Foreign-turnkey external-capital share | {float(capex['foreign_turnkey_comparator']['external_capital_share']):.0%} |",
        "",
        str(capex["foreign_turnkey_comparator"]["basis"]),
        "The reported savings are calculated as foreign-turnkey external capital "
        "minus OSR imported content; annual savings use the same country construction "
        "period. Replace the multiplier and foreign-capital share with normalized bids "
        "before procurement or investment approval.",
        "Lifetime external-interest savings hold financing terms constant: both OSR "
        "and the foreign-turnkey case use the same country external rate, construction "
        "interest period, and repayment tenor. The comparator treats its external "
        "capital requirement as debt-financed. Interest comprises interest-only "
        "payments during construction plus total level debt service after grace less "
        "principal. The headline lifetime saving is avoided external capital plus "
        "avoided external interest; it does not include local-bond interest or OPEX.",
        "",
        "## Civil Works",
        "",
        "Civil work is costed as a direct-procurement floor for standard-gauge, "
        "double-track OSR alignments:",
        "",
        "| Civil class | Unit cost | Included scope |",
        "|---|---:|---|",
        f"| At-grade | {_money_short(capex['civil_usd_per_km']['at_grade'])} / route-km | UIC60 rail, ballastless slab/embedded trackform, direct-fixation fasteners, drainage, cable troughs, local installation |",
        f"| Elevated | {_money_short(capex['civil_usd_per_km']['elevated'])} / route-km | Repeatable precast guideway spans, piers, foundations, bearings, parapets, deck slab/trackform, erection |",
        f"| Bridge | {_money_short(capex['civil_usd_per_km']['bridge'])} / route-km | Longer-span/water-crossing version of the elevated stack with heavier foundation and protection allowance |",
        f"| Elevated-interchange premium | {_money_short(capex['junctions']['elevated_interchange_premium_usd'])} / site | Added stacked-platform and approach complexity where an interchange must grade-separate |",
        "",
        "These values are intentionally below turnkey metro-bid benchmarks because "
        "OSR excludes tunnels, overhead catenary, proprietary signalling civil "
        "plant, bespoke station architecture, and contractor-led EPC margin.",
        "",
        "## Stations",
        "",
        "Station costs are prefab portal-frame canopy + ground-level platform "
        "slab/guideway channel + direct pedestrian access + simple "
        "MEP/signs/CCTV/fare gates. Overbridges, lifts, stairs, and concourses "
        "are not the default at-grade station assumption; they appear only where "
        "an elevated/stacked interchange or local road-barrier override requires "
        "them.",
        "",
        "| Station archetype | Unit cost |",
        "|---|---:|",
    ])

    for archetype in STATION_ORDER:
        lines.append(f"| `{archetype}` | {_money_short(capex['station_unit_usd'][archetype])} |")

    lines.extend([
        "",
        "## Depots",
        "",
        "| Depot archetype | Unit cost |",
        "|---|---:|",
    ])

    for archetype in DEPOT_ORDER:
        lines.append(f"| `{archetype}` | {_money_short(capex['depot_unit_usd'][archetype])} |")

    lines.extend([
        "",
        "Depot scope is maintenance rather than fleet-wide parking: main-heavy "
        "workshop/inspection roads, pits, lifting and wheel tooling, wash/defect "
        "functions, and local PV/storage tie-in. Healthy sets stable and recharge "
        "at powered passenger stations overnight; secondary and layup sites are "
        "site-specific exceptions.",
        "",
        "## Charging Microgrids",
        "",
        "There is no route traction-power system in the OSR baseline: no OCS, "
        "third rail, feeder substations, or continuous traction distribution "
        "along the railway. The energy infrastructure cost in city designs is "
        "therefore **station/depot charging microgrid interface CAPEX**.",
        "",
        "| Station archetype | Unit cost | Included scope |",
        "|---|---:|---|",
    ])

    charging_scope = {
        "halt": "250 kW class charger, local protection, compact LV tie",
        "standard": "500 kW class conductive charger, switchgear, inverter interface",
        "major": "Larger queueing/anchor-stop charger and buffer tie",
        "terminal": "End-of-line charger with higher turnback utilization",
        "interchange": "Multi-platform charger/switchgear allowance",
        "interchange-elevated": "Elevated multi-platform charger/switchgear allowance",
        "depot-terminal": "Passenger-stop charger plus depot/yard charging interface",
    }
    for archetype in STATION_ORDER:
        value = capex["charging_microgrid_unit_usd"][archetype]
        lines.append(f"| `{archetype}` | {_money_short(value)} | {charging_scope[archetype]} |")

    solar = capex["solar_power_plant"]
    systems = capex["systems"]
    overhead = capex["overhead"]
    lines.extend([
        "",
        "Station PV canopies, stationary LFP packs, depot buildings, "
        "and train batteries are **not** re-billed here. They appear in station, "
        "energy-site/depot, and rolling-stock scopes respectively.",
        "",
        "## Dedicated Solar Plant",
        "",
        "Generated city READMEs add a separate utility-scale solar plant or "
        "contracted offsite solar PPA asset when the timetable traction-energy "
        "model exceeds station/depot PV generation. The plant is sized from the "
        "annual shortfall after on-site PV, with a "
        f"**{_pct(float(solar['coverage_margin']))} planning coverage margin**, "
        "and uses:",
        "",
        "| Item | Planning rate |",
        "|---|---:|",
        f"| Utility PV field | {_money_short(solar['utility_pv_usd_per_kw'])}/kW |",
        f"| Grid interconnection / PPA tie-in | {_money_short(solar['interconnection_usd_per_kw'])}/kW |",
        f"| Annual plant O&M | {_pct(float(solar['annual_maintenance_fraction']), 1)} of plant CAPEX |",
        "",
        "This plant is carried as infrastructure CAPEX. Its O&M is carried in "
        "annual traction-energy OPEX; grid/PPA energy purchases are charged only "
        "for any residual import after on-site PV plus the dedicated plant.",
        "",
        "## Train-Control Wayside",
        "",
        "Residual train-control wayside is budgeted at "
        f"**{_money_short(systems['signalling_usd_per_km'])} per route-km**. "
        "The expensive ATP/ATO function lives onboard in the trainset cost. The "
        "wayside scope is sparse W-Nodes at switches/stations, passive balises, "
        "validation beacons, LoRa gateways, and OCC interfaces.",
        "",
        "## Revenue Neutrality",
        "",
        "City READMEs include a post-opening operating-neutral revenue case. The "
        f"model uses an {_pct(pass_share)} median-income monthly pass for the "
        "stronger service/revenue case, derives annual paid trips from practical "
        "system capacity and the configured low/high `capacity_utilization_*` "
        "bracket, and adds station shop leases plus advertising boards. The "
        "operating-neutral column solves the capacity utilisation needed so:",
        "",
        "```text",
        "farebox + station-shop leases + advertising",
        "= annual OPEX",
        "```",
        "",
        "The default farebox-recovery reference in `country-finance.toml` is "
        f"{_pct(farebox_target)}. OPEX uses the generated fleet schedule for "
        "train-km. On-site PV generation offsets traction demand first, the "
        "dedicated solar plant covers the remaining planned shortfall, and only "
        "residual import is charged as grid/PPA energy using "
        "`grid_energy_usd_per_kwh` from `lib/templates/country-finance.toml`. "
        "Driverless labour is no longer a flat route-km scalar: the README roster "
        "scales with service hours, lines, revenue fleet, station archetypes, "
        "high-case paid trips, annual train-km, depots, and the RFC 0015 shift of "
        "safety staff from train cabs to OCC and platform posts.",
        "",
        "The maintenance percentages are planning-cost envelopes. The actual work "
        "content and inspection intervals are controlled by "
        "[RFC 0029](rfcs/0029-maintenance-schedule-system.md) and "
        "[`lib/templates/maintenance-schedule.toml`](../lib/templates/maintenance-schedule.toml), "
        "covering rolling stock, stations, track/civil, structures, energy, "
        "signalling/comms, depot equipment, and railway production-plant tools.",
        "",
        "Construction-period local equity and interest-only grace payments on the "
        "repayable tranches remain public capital commitments. The base finance "
        "boundary assumes **no climate/development grant**: imported value is the "
        "minimum external climate/MDB or foreign-currency requirement, while "
        f"{_pct(float(default_finance['local_bond_share_of_local_capex']))} of local "
        "value is assigned to domestic-currency bonds and the balance to local "
        "public equity or another domestic source. The external tranche is a placeholder "
        "for a lender term sheet, not evidence of an available loan. Plausible "
        "channels include MDB lending blended with climate funds such as GCF or "
        "CIF, or an equivalent national development bank / IsDB route where "
        "eligible. The operating-neutral case applies only to steady-state "
        "operations after opening. Where the capacity-use scenario produces "
        "revenue above OPEX, that operating surplus is netted against "
        "repayable-debt support in the government commitment summary; the gross "
        "post-grace external and local-bond debt-service figures remain visible.",
        "",
        "## Broad Economic Benefits",
        "",
        "Generated city READMEs include a `Broad economic benefits` screening "
        "section sourced from `lib/templates/economic-benefits.toml`. It is not a "
        "formal benefit-cost analysis; it is a transparent first-pass calculation "
        "for channels that matter to cities and development lenders but do not "
        "appear as railway revenue.",
        "",
        "The annual benefit/activity proxy quantifies:",
        "",
        "| Channel | Model basis |",
        "|---|---|",
        "| Travel time + reliability | Annual paid trips from capacity use x minutes saved x median-income value-of-time proxy |",
        "| Congestion relief | Paid trips x average trip length x road mode-shift share / vehicle occupancy |",
        f"| Environmental effect | Avoided road CO2e minus rail residual-grid CO2e, valued at ${social_carbon:.0f}/t social-carbon proxy |",
        "| Local road externalities | Avoided road vehicle-km x air/noise/safety proxy |",
        "| Commerce and entertainment | Relevant trip shares x a median-income local-spend proxy |",
        "",
        "The access table reports education, healthcare, commerce, and "
        "entertainment/community access-events per year. It uses station anchors "
        "(`anchor_kind` / `anchor_name`) where available, with conservative base "
        "shares so sparse-OSM cities do not report zero service-access benefit.",
        "",
        "The CAPEX recirculation table estimates how much of the initial capital "
        "programme is retained locally through civil works, station fabrication, "
        "depot works, shared national railway production-plant setup, rolling-stock assembly, "
        "charging microgrids, EPC labour, and solar-plant delivery. The retained "
        f"CAPEX is then multiplied by the {local_multiplier:.1f} construction "
        "local-supplier / wage multiplier and converted to approximate "
        "construction job-years using the country median-income table and the "
        f"{job_output_multiple:.1f}x job-output multiple. These rows are "
        "economic-activity indicators, not fiscal income.",
        "",
        "## EPC",
        "",
        "EPC integration and project management is "
        f"**{_pct(float(overhead['epc_fraction']))} of subtotal**:",
        "",
        "```text",
        "city: civil + stations + depots + rolling_stock",
        "+ residual_train_control_wayside + charging_microgrids",
        "national: one shared railway_production_plant",
        "```",
        "",
        "Dedicated solar plant CAPEX is then added as a separate infrastructure "
        "bucket when the generated energy plan requires it.",
        "",
        "Country labour/material multipliers are applied downstream through "
        "`lib/templates/country-costs.toml` when a local tender view is needed.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    args.out.write_text(render_cost_model())
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
