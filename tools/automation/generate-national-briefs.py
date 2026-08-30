#!/usr/bin/env python3
"""Generate one nationwide OSR implementation and capital brief per country."""

from __future__ import annotations

import argparse
import tempfile
import tomllib
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "design/city-generation/src"))

from osr_scenario.capital import (  # noqa: E402
    FOREIGN_TURNKEY_BASIS,
    FOREIGN_TURNKEY_EXTERNAL_SHARE,
    IMPORTED_SHARE,
    NATIONAL_FACTORY_PER_VEHICLE_USD,
    aggregate_breakdowns,
    city_capital_breakdown,
    foreign_turnkey_cases,
    funding_plan,
)
from osr_scenario.network_readme import (  # noqa: E402
    _energy_plan,
    _load_country_finance,
    compute_stats,
)


FAMILY_CARS = {
    "urban-shuttle-1car": 1,
    "tram-2car": 2,
    "light-metro-3car": 3,
    "metro-4car": 4,
    "metro-6car": 6,
}

PUBLIC_REGIONS = {
    "central-africa",
    "east-africa",
    "latin-america",
    "north-africa",
    "south-africa",
    "south-asia",
    "southeast-asia",
    "west-africa",
    "west-asia",
}


@dataclass(frozen=True)
class CityCapital:
    name: str
    slug: str
    population: int
    fleet_trainsets: int
    vehicle_modules: int
    breakdown: object


def money(value: float) -> str:
    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:,.2f} B"
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.1f} M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:,.0f} k"
    return f"${value:,.0f}"


def load_city(design_path: Path) -> tuple[str, CityCapital]:
    design = tomllib.loads(design_path.read_text())
    city = design["city"]
    slug = str(city["slug"])
    scenario_path = design_path.parent / f"{slug}.toml"
    scenario = tomllib.loads(scenario_path.read_text())
    stats = compute_stats(design, scenario, int(city["population"]))
    energy = _energy_plan(design, scenario, stats)
    families = {
        str(line.get("rolling_stock"))
        for line in design.get("lines", [])
        if line.get("rolling_stock")
    }
    family = next(iter(families)) if len(families) == 1 else "light-metro-3car"
    fleet = sum(int(row.get("trainset_count", 0)) for row in design.get("fleets", []))
    return str(city["country"]), CityCapital(
        name=design_path.parent.name.replace("-", " "),
        slug=slug,
        population=int(city["population"]),
        fleet_trainsets=fleet,
        vehicle_modules=fleet * FAMILY_CARS.get(family, 3),
        breakdown=city_capital_breakdown(
            design["costs"], energy.solar_plant_capex_usd
        ),
    )


def render_brief(
    country_code: str,
    country_name: str,
    cities: list[CityCapital],
    *,
    detailed: bool = False,
) -> str:
    cities = sorted(cities, key=lambda city: (-city.population, city.name))
    anchor = max(cities, key=lambda city: city.vehicle_modules)
    national_factory_usd = (
        anchor.vehicle_modules * NATIONAL_FACTORY_PER_VEHICLE_USD
    )
    national = aggregate_breakdowns(
        [city.breakdown for city in cities],
        national_factory_usd=national_factory_usd,
    )
    country_finance = _load_country_finance(country_code)
    plan = funding_plan(national, country_finance)
    turnkey_cases = foreign_turnkey_cases(national, plan)
    turnkey_default = turnkey_cases["default"]
    population = sum(city.population for city in cities)
    fleet = sum(city.fleet_trainsets for city in cities)
    modules = sum(city.vehicle_modules for city in cities)

    if not detailed:
        labels = {
            "civil": "Civil works",
            "stations": "Stations",
            "depots": "Depots",
            "rolling_stock": "Rolling stock",
            "production_plant": "Shared national trainset factory",
            "solar_plant": "Dedicated solar plants",
            "signalling": "Residual train control",
            "charging_microgrid": "Charging microgrids",
            "epc_overhead": "EPC / project services",
        }
        out = [
            f"# {country_name} National OpenSourceRail Strategy",
            "",
            f"This page contains only {country_name}-specific aggregation. Shared "
            "network, service, energy, civil, cost, finance, QA and validation "
            "methods are defined once in the "
            "[deployment planning reference](../../../../docs/deployment-planning-reference.md).",
            "",
            "> [!IMPORTANT]",
            f"> **Foreign-capital advantage:** against the default equivalent "
            f"foreign-turnkey sensitivity, this "
            f"national programme avoids **{money(turnkey_default.external_capital_avoided_usd)} "
            f"({turnkey_default.external_capital_reduction:.1%}) of external capital** "
            f"and **{money(turnkey_default.external_interest_avoided_usd)} of external "
            f"interest**. Capital plus saved interest totals "
            f"**{money(turnkey_default.lifetime_external_financing_avoided_usd)}**.",
            "",
            "## National Programme",
            "",
            "| Local measure | Planning value |",
            "|---|---:|",
            f"| Catalogue cities | {len(cities)} |",
            f"| Represented population | {population:,} |",
            f"| Trainsets / vehicle modules | {fleet:,} / {modules:,} |",
            f"| City infrastructure and fleet CAPEX | "
            f"{money(sum(city.breakdown.total_usd for city in cities))} |",
            f"| Shared national factory | {money(national_factory_usd)} |",
            f"| Factory sizing basis | {anchor.vehicle_modules:,} modules for "
            f"{anchor.name}, then reused nationally |",
            f"| **Total national programme** | **{money(national.total_usd)}** |",
            "",
            "## Capital And Funding",
            "",
            "| Local funding measure | Planning value |",
            "|---|---:|",
            f"| Imported / external capital | {money(national.imported_usd)} "
            f"({national.imported_share:.1%}) |",
            f"| Domestic / local capital | {money(national.local_usd)} "
            f"({national.local_share:.1%}) |",
            f"| Annual external capital draw | "
            f"{money(plan.annual_external_capital_draw_usd)} / yr |",
            f"| Annual local capital draw | {money(plan.annual_local_capital_draw_usd)} / yr |",
            f"| Annual public construction commitment | "
            f"{money(plan.annual_public_construction_commitment_usd)} / yr for "
            f"{plan.construction_years} years |",
            f"| Annual post-grace debt service | {money(plan.annual_debt_service_usd)} / yr |",
            f"| Default foreign-turnkey external capital | "
            f"{money(turnkey_default.foreign_external_usd)} |",
            f"| External capital saved | "
            f"{money(turnkey_default.external_capital_avoided_usd)} |",
            f"| Capital + lifetime external interest saved | "
            f"{money(turnkey_default.lifetime_external_financing_avoided_usd)} |",
            "",
            "### Procurement-Origin Composition",
            "",
            "| CAPEX bucket | Total | Imported | Local value |",
            "|---|---:|---:|---:|",
        ]
        for bucket in national.buckets:
            out.append(
                f"| {labels.get(bucket.name, bucket.name)} | "
                f"{money(bucket.total_usd)} | {money(bucket.imported_usd)} | "
                f"{money(bucket.local_usd)} |"
            )
        out.extend(
            [
                f"| **Total** | **{money(national.total_usd)}** | "
                f"**{money(national.imported_usd)}** | "
                f"**{money(national.local_usd)}** |",
                "",
                "## City Programme",
                "",
                "| City | Population | Fleet | City CAPEX | External capital | Local capital |",
                "|---|---:|---:|---:|---:|---:|",
            ]
        )
        for city in cities:
            out.append(
                f"| [{city.name}]({city.name.replace(' ', '-')}/README.md) | "
                f"{city.population:,} | {city.fleet_trainsets:,} | "
                f"{money(city.breakdown.total_usd)} | "
                f"{money(city.breakdown.imported_usd)} | "
                f"{money(city.breakdown.local_usd)} |"
            )
        out.extend(
            [
                "",
                "## Local Basis And Regeneration",
                "",
                f"Country finance parameters use `{country_code}` in "
                "`lib/templates/country-finance.toml`. The factory is counted once "
                "nationally and excluded from city CAPEX. City values come from each "
                "local `design.toml` and expanded scenario; common limitations and "
                "interpretation are not repeated here.",
                "",
                "```bash",
                "python3 tools/automation/generate-national-briefs.py",
                "```",
                "",
            ]
        )
        return "\n".join(out)

    out = [
        f"# {country_name} national OpenSourceRail strategy",
        "",
        "> [!IMPORTANT]",
        f"> **Foreign-capital advantage:** against the default equivalent foreign-turnkey "
        f"case, this national OSR programme avoids **{money(turnkey_default.external_capital_avoided_usd)} "
        f"({turnkey_default.external_capital_reduction:.1%}) of external capital** and "
        f"**{money(turnkey_default.external_interest_avoided_usd)} of external interest**. "
        f"Capital plus saved interest totals **{money(turnkey_default.lifetime_external_financing_avoided_usd)} "
        f"over the {plan.tenor_years}-year financing life**. Both cases use the same "
        f"{plan.external_rate:.1%} external rate and financing schedule; the comparator "
        "external requirement is assumed debt-financed, and the comparator is an "
        "editable sensitivity, not a vendor quote.",
        "",
        f"{country_name} should implement OpenSourceRail as one national industrial and "
        f"financing programme covering the {len(cities)} catalogue cities below, rather "
        "than as disconnected city projects. One centrally governed trainset factory "
        "builds the shared modular fleet in phases; city and regional contractors "
        "fabricate and install rails, viaducts, stations, depots, and local civil works. "
        "This concentrates scarce imported machinery, specialist tooling, engineering "
        "support, and foreign currency in one reusable national asset while maximizing "
        "domestic labour, materials, fabrication, and local-currency financing.",
        "",
        "## National programme at a glance",
        "",
        "| Measure | National planning value |",
        "|---|---:|",
        f"| Cities in catalogue | {len(cities)} |",
        f"| Served population represented | {population:,} |",
        f"| Trainsets across city plans | {fleet:,} |",
        f"| Vehicle/car modules to manufacture | {modules:,} |",
        f"| City infrastructure + fleet CAPEX | {money(sum(city.breakdown.total_usd for city in cities))} |",
        f"| One shared national trainset factory | {money(national_factory_usd)} |",
        f"| National factory sizing basis | {anchor.vehicle_modules:,} modules: largest single-city programme ({anchor.name}) |",
        f"| **Total national programme CAPEX** | **{money(national.total_usd)}** |",
        "",
        "The factory is sized to the largest single-city fleet programme and reused "
        "through a phased national rollout. This avoids duplicating factory buildings, "
        "moulds, welding fixtures, metrology, commissioning equipment, and imported "
        "machinery in every city. Final factory siting requires a national freight, "
        "power, workforce, land, and test-track study; this brief does not preselect a city.",
        "",
        "## External versus local capital",
        "",
        "Imported content is the minimum foreign-currency or international-capital "
        "requirement. Local content is the domestic funding envelope and can be raised "
        "through local-currency infrastructure bonds, public equity, pension/insurance "
        "capital, land-value capture, or other domestic sources.",
        "",
        "| Capital boundary | Share | Total | Annual draw during construction |",
        "|---|---:|---:|---:|",
        f"| **External capital for imports** | **{national.imported_share:.1%}** | **{money(national.imported_usd)}** | **{money(plan.annual_external_capital_draw_usd)} / yr** |",
        f"| **Local capital for domestic value** | **{national.local_share:.1%}** | **{money(national.local_usd)}** | **{money(plan.annual_local_capital_draw_usd)} / yr** |",
        f"| planned local-currency bond issuance | {plan.local_bond_usd / national.total_usd:.1%} of total | {money(plan.local_bond_usd)} | {money(plan.annual_local_bond_issuance_usd)} / yr |",
        f"| local public equity / other domestic funding | {plan.local_equity_usd / national.total_usd:.1%} of total | {money(plan.local_equity_usd)} | {money(plan.annual_local_equity_draw_usd)} / yr |",
        f"| **Total capital programme** | **100.0%** | **{money(national.total_usd)}** | **{money(national.total_usd / plan.construction_years)} / yr** |",
        "",
        f"The annual construction draw is spread evenly over {plan.construction_years} "
        "planning years. Post-grace annual debt service is "
        f"{money(plan.annual_external_debt_service_usd)} for external import finance "
        f"plus {money(plan.annual_local_bond_service_usd)} for local bonds, or "
        f"**{money(plan.annual_debt_service_usd)} per year** before railway operating "
        "cash flow. During construction, interest plus the local public-equity draw is "
        f"**{money(plan.annual_public_construction_commitment_usd)} per year**.",
        "",
        "## Foreign-company turnkey comparison",
        "",
        "This controlled comparison is an editable sensitivity, not a supplier "
        "quotation. It uses the same national network, fleet, service, and energy "
        f"scope, with {FOREIGN_TURNKEY_EXTERNAL_SHARE:.0%} of a foreign contractor's "
        "price assumed to require foreign currency or international capital. "
        f"{FOREIGN_TURNKEY_BASIS} Lifetime interest uses the same "
        f"{plan.external_rate:.1%} rate, {plan.construction_years}-year construction "
        f"interest period, and {plan.repayment_years}-year amortization for both cases; "
        "the comparator external requirement is assumed debt-financed.",
        "",
        "| Case | Cost multiplier vs OSR | Foreign-company external capital | OSR external capital saved | External interest saved over financing life | Capital + interest saved |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for case, comparison in turnkey_cases.items():
        label = f"**{case.title()}**" if case == "default" else case.title()
        out.append(
            f"| {label} | {comparison.cost_multiplier:.2f}× | "
            f"{money(comparison.foreign_external_usd)} | "
            f"{money(comparison.external_capital_avoided_usd)} "
            f"({comparison.external_capital_reduction:.1%}) | "
            f"{money(comparison.external_interest_avoided_usd)} | "
            f"**{money(comparison.lifetime_external_financing_avoided_usd)}** |"
        )
    out.extend(
        [
            "",
            f"At the default {turnkey_default.cost_multiplier:.2f}× case, the OSR "
            f"programme reduces external capital from {money(turnkey_default.foreign_external_usd)} "
            f"to {money(national.imported_usd)}, a saving of "
            f"**{money(turnkey_default.external_capital_avoided_usd)} "
            f"({turnkey_default.external_capital_reduction:.1%})**, plus "
            f"**{money(turnkey_default.external_interest_avoided_usd)}** of external "
            f"interest over the financing life. Total programme "
            f"CAPEX is {turnkey_default.total_capex_reduction:.1%} below the comparator. "
            "Replace both variables with scope-normalized bids before investment approval.",
            "",
            "## Procurement-origin composition",
            "",
            "| CAPEX bucket | Total | Imported share | External capital | Local value |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    labels = {
        "civil": "Civil works",
        "stations": "Stations",
        "depots": "Depots",
        "rolling_stock": "Rolling stock",
        "production_plant": "Shared national trainset factory",
        "solar_plant": "Dedicated solar plants",
        "signalling": "Residual signalling / train control",
        "charging_microgrid": "Charging microgrids",
        "epc_overhead": "EPC / project services",
    }
    for bucket in national.buckets:
        out.append(
            f"| {labels.get(bucket.name, bucket.name)} | {money(bucket.total_usd)} | "
            f"{bucket.imported_share:.0%} | {money(bucket.imported_usd)} | "
            f"{money(bucket.local_usd)} |"
        )
    out.extend(
        [
            f"| **Total** | **{money(national.total_usd)}** | **{national.imported_share:.1%}** | **{money(national.imported_usd)}** | **{money(national.local_usd)}** |",
            "",
            "## City programme",
            "",
            "Each city CAPEX below excludes the national factory. Its imported share "
            "varies with the local mix of civil structures, rolling stock, stations, "
            "charging, signalling, and solar infrastructure.",
            "",
            "| City | Population | Fleet | City CAPEX | Imported % | OSR external capital | Foreign-turnkey external capital (default) | External capital saved | Capital + lifetime external interest saved | Local capital |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for city in cities:
        city_plan = funding_plan(city.breakdown, country_finance)
        city_turnkey = foreign_turnkey_cases(city.breakdown, city_plan)["default"]
        out.append(
            f"| [{city.name}]({city.name.replace(' ', '-')}/README.md) | "
            f"{city.population:,} | {city.fleet_trainsets:,} | "
            f"{money(city.breakdown.total_usd)} | {city.breakdown.imported_share:.1%} | "
            f"{money(city.breakdown.imported_usd)} | "
            f"{money(city_turnkey.foreign_external_usd)} | "
            f"{money(city_turnkey.external_capital_avoided_usd)} | "
            f"{money(city_turnkey.lifetime_external_financing_avoided_usd)} | "
            f"{money(city.breakdown.local_usd)} |"
        )
    out.extend(
        [
            "",
            "## National implementation sequence",
            "",
            "1. Establish one national programme authority, common technical baseline, "
            "procurement-origin register, and local-content verification method.",
            "2. Procure the shared trainset-factory machinery and first-article imported "
            "kits once; qualify domestic steel, composites, wiring, interiors, and assembly.",
            "3. Launch city civil packages in parallel where local contractor capacity "
            "allows, using standardized rail, viaduct, station, depot, and charging interfaces.",
            "4. Sequence trainset production through the national factory by opening date, "
            "reusing fixtures and commissioning capability between cities.",
            "5. Issue local-currency bonds against the domestic-value programme and reserve "
            "international borrowing or foreign exchange for the imported-value schedule.",
            "6. Update these planning shares with supplier quotations, customs/tax treatment, "
            "country capability audits, and a signed financing plan before procurement.",
            "",
            "## Basis and limitations",
            "",
            "This is a planning strategy, not a financing commitment or supplier-origin "
            "audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, "
            "fleet, and cost data come from each generated `design.toml` and scenario. "
            "The foreign-turnkey multiplier and external share are illustrative variables, "
            "not received bids or named-vendor prices. "
            "The model excludes tax/duty, FX paths, land acquisition, utility relocation, "
            "and country-specific supplier qualification until controlled evidence exists.",
            "",
            f"Generated by `tools/automation/generate-national-briefs.py` for `{country_code}`. "
            f"Controlled imported-share keys: {', '.join(sorted(IMPORTED_SHARE))}.",
            "",
        ]
    )
    return "\n".join(out)


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", dir=path.parent, delete=False, encoding="utf-8"
    ) as handle:
        handle.write(text)
        temporary = Path(handle.name)
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if generated briefs differ instead of writing them",
    )
    args = parser.parse_args()
    country_names = tomllib.loads(
        (REPO_ROOT / "lib/templates/country-costs.toml").read_text()
    )["countries"]
    grouped: dict[tuple[str, Path], list[CityCapital]] = defaultdict(list)
    for design_path in sorted((REPO_ROOT / "cities/catalogue").glob("*/*/*/design.toml")):
        region = design_path.relative_to(REPO_ROOT / "cities/catalogue").parts[0]
        if region not in PUBLIC_REGIONS:
            continue
        code, city = load_city(design_path)
        grouped[(code, design_path.parent.parent)].append(city)

    drift: list[Path] = []
    for (code, country_dir), cities in sorted(grouped.items()):
        name = str(country_names.get(code, {}).get("name", country_dir.name))
        output = country_dir / "NATIONAL-BRIEF.md"
        text = render_brief(code, name, cities)
        if args.check:
            if not output.is_file() or output.read_text() != text:
                drift.append(output)
        else:
            atomic_write(output, text)
            print(f"wrote {output.relative_to(REPO_ROOT)}")
    if drift:
        for path in drift:
            print(f"stale: {path.relative_to(REPO_ROOT)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
