#!/usr/bin/env python3
"""Generate human- and machine-readable capital evidence from current city models."""

from __future__ import annotations

import argparse
import json
import runpy
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "design/city-generation/src"))

from osr_scenario.capital import (  # noqa: E402
    FOREIGN_TURNKEY_BASIS,
    NATIONAL_FACTORY_PER_VEHICLE_USD,
    aggregate_breakdowns,
    foreign_turnkey_cases,
    funding_plan,
)
from osr_scenario.network_readme import _load_country_finance  # noqa: E402

MARKDOWN_OUTPUT = REPO_ROOT / "docs/portfolio-summary.md"
JSON_OUTPUT = REPO_ROOT / "docs/portfolio-summary.json"
# Retained for callers written against the original single-output generator.
OUTPUT = MARKDOWN_OUTPUT
DEVELOPING_WORLD_REGIONS = {
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
class PortfolioData:
    city_count: int
    country_count: int
    totals: dict[str, float]
    imported_shares: list[float]
    case_totals: dict[str, dict[str, float]]


def money(value: float) -> str:
    if abs(value) >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:,.2f}T"
    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:,.2f}B"
    return f"${value / 1_000_000:,.1f}M"


def _portfolio_data() -> PortfolioData:
    """Calculate capital metrics and every controlled turnkey sensitivity."""

    load_city = runpy.run_path(
        str(REPO_ROOT / "tools/automation/generate-national-briefs.py")
    )["load_city"]
    grouped: dict[str, list[object]] = defaultdict(list)
    city_count = 0
    for path in sorted((REPO_ROOT / "cities/catalogue").glob("*/*/*/design.toml")):
        region = path.relative_to(REPO_ROOT / "cities/catalogue").parts[0]
        if region not in DEVELOPING_WORLD_REGIONS:
            continue
        code, city = load_city(path)
        grouped[code].append(city)
        city_count += 1

    totals = {
        key: 0.0
        for key in (
            "total", "external", "local", "bond", "equity", "annual_total",
            "annual_external", "annual_local", "foreign_total", "foreign_external",
            "external_saved", "interest_saved", "lifetime_saved",
        )
    }
    case_totals: dict[str, dict[str, float]] = defaultdict(
        lambda: defaultdict(float)
    )
    imported_shares: list[float] = []
    for code, cities in grouped.items():
        factory = max(city.vehicle_modules for city in cities) * NATIONAL_FACTORY_PER_VEHICLE_USD
        national = aggregate_breakdowns(
            [city.breakdown for city in cities], national_factory_usd=factory
        )
        plan = funding_plan(national, _load_country_finance(code))
        comparisons = foreign_turnkey_cases(national, plan)
        comparison = comparisons["default"]
        totals["total"] += national.total_usd
        totals["external"] += national.imported_usd
        totals["local"] += national.local_usd
        totals["bond"] += plan.local_bond_usd
        totals["equity"] += plan.local_equity_usd
        totals["annual_total"] += national.total_usd / plan.construction_years
        totals["annual_external"] += plan.annual_external_capital_draw_usd
        totals["annual_local"] += plan.annual_local_capital_draw_usd
        totals["foreign_total"] += comparison.foreign_total_usd
        totals["foreign_external"] += comparison.foreign_external_usd
        totals["external_saved"] += comparison.external_capital_avoided_usd
        totals["interest_saved"] += comparison.external_interest_avoided_usd
        totals["lifetime_saved"] += comparison.lifetime_external_financing_avoided_usd
        for case, candidate in comparisons.items():
            case_values = case_totals[case]
            case_values["multiplier"] = candidate.cost_multiplier
            case_values["foreign_total"] += candidate.foreign_total_usd
            case_values["foreign_external"] += candidate.foreign_external_usd
            case_values["external_saved"] += candidate.external_capital_avoided_usd
            case_values["interest_saved"] += candidate.external_interest_avoided_usd
            case_values[
                "lifetime_saved"
            ] += candidate.lifetime_external_financing_avoided_usd
        imported_shares.extend(city.breakdown.imported_share for city in cities)

    return PortfolioData(
        city_count=city_count,
        country_count=len(grouped),
        totals=totals,
        imported_shares=imported_shares,
        case_totals={case: dict(values) for case, values in case_totals.items()},
    )


def portfolio_metrics() -> tuple[int, int, dict[str, float], list[float]]:
    """Return the stable public metrics API used by other generators."""

    data = _portfolio_data()
    return data.city_count, data.country_count, data.totals, data.imported_shares


def build_summary(data: PortfolioData | None = None) -> str:
    data = data or _portfolio_data()
    city_count = data.city_count
    country_count = data.country_count
    totals = data.totals
    imported_shares = data.imported_shares
    case_totals = data.case_totals
    imported_pct = totals["external"] / totals["total"]
    reduction = totals["external_saved"] / totals["foreign_external"]
    out = [
        "# Portfolio capital summary",
        "",
        "<!-- Generated by tools/automation/generate-portfolio-summary.py; do not hand-edit. -->",
        "",
        "This is the current aggregation of generated city models in the developing-world "
        "evidence scope, including one shared trainset factory per country. European "
        "comparison designs remain in the engineering catalogue but are excluded here. "
        "This is a planning screen, not a financing commitment, audited origin "
        "declaration, supplier quotation, or vendor bid.",
        "",
        "Machine-readable values: [`portfolio-summary.json`](portfolio-summary.json).",
        "",
        f"| {city_count}-city / {country_count}-country catalogue | Planning value | Annual construction draw across country programmes |",
        "|---|---:|---:|",
        f"| External capital for imported components and machinery | **{money(totals['external'])} ({imported_pct:.1%})** | **{money(totals['annual_external'])}/year** |",
        f"| Local capital for domestic value | **{money(totals['local'])} ({1-imported_pct:.1%})** | **{money(totals['annual_local'])}/year** |",
        f"| of which planned local-currency bond issuance | {money(totals['bond'])} | — |",
        f"| local public equity / other domestic funding | {money(totals['equity'])} | — |",
        f"| **Total national programmes** | **{money(totals['total'])}** | **{money(totals['annual_total'])}/year** |",
        "",
        "## Foreign-turnkey sensitivity",
        "",
        "The comparison holds the modelled railway scope and each country's financing "
        "terms constant. It changes only the foreign-turnkey price multiplier; all "
        "cases assume 90% of that price needs foreign currency or international capital:",
        "",
        "```text",
        "turnkey price            = OpenSourceRail CAPEX × price multiplier",
        "turnkey external capital = turnkey price × 90%",
        "external capital avoided = turnkey external capital − OpenSourceRail imports",
        "```",
        "",
        "| Case | Price multiplier | Turnkey total | Turnkey external capital | External capital avoided | Capital + external interest avoided |",
        "|---|---:|---:|---:|---:|---:|",
        *[
            f"| {case.title()} | {values['multiplier']:.1f}× | "
            f"{money(values['foreign_total'])} | "
            f"{money(values['foreign_external'])} | "
            f"**{money(values['external_saved'])} "
            f"({values['external_saved'] / values['foreign_external']:.1%})** | "
            f"**{money(values['lifetime_saved'])}** |"
            for case, values in case_totals.items()
        ],
        "",
        f"The default row is the front-page illustration at portfolio scale: "
        f"{money(totals['external_saved'])} ({reduction:.1%}) less external capital "
        f"and {money(totals['interest_saved'])} less external interest. The comparator "
        "treats all foreign-turnkey external capital as debt; the OpenSourceRail case "
        "retains its generated grant/debt split. Debt on both sides uses the same country "
        "construction periods, rates and repayment tenors.",
        "",
        f"Individual city imported shares range from {min(imported_shares):.1%} to "
        f"{max(imported_shares):.1%}. Replace the imported shares, cost multiplier and "
        "financing terms with audited supplier capability, normalized bids and signed "
        "lender terms before an investment decision.",
        "",
        "Regenerate with `python3 tools/automation/generate-portfolio-summary.py` after city costs "
        "or country financing inputs change.",
        "",
    ]
    return "\n".join(out)


def build_json(data: PortfolioData | None = None) -> str:
    """Render the public machine-readable portfolio evidence."""

    data = data or _portfolio_data()
    totals = data.totals
    imported_share = totals["external"] / totals["total"]
    default_case = data.case_totals["default"]
    external_share = default_case["foreign_external"] / default_case["foreign_total"]

    payload = {
        "schema_version": 1,
        "currency": "USD",
        "scope": {
            "city_count": data.city_count,
            "country_count": data.country_count,
            "regions": sorted(DEVELOPING_WORLD_REGIONS),
            "european_comparison_models_excluded": True,
            "national_factory_treatment": "one shared trainset factory per country",
        },
        "open_source_rail": {
            "total_capex_usd": round(totals["total"], 2),
            "imported_external_capital_usd": round(totals["external"], 2),
            "imported_external_share": round(imported_share, 9),
            "local_domestic_value_usd": round(totals["local"], 2),
            "local_domestic_share": round(1.0 - imported_share, 9),
            "local_currency_bonds_usd": round(totals["bond"], 2),
            "local_public_equity_other_usd": round(totals["equity"], 2),
            "annual_total_construction_draw_usd": round(totals["annual_total"], 2),
            "annual_external_construction_draw_usd": round(
                totals["annual_external"], 2
            ),
            "annual_local_construction_draw_usd": round(totals["annual_local"], 2),
        },
        "foreign_turnkey_comparator": {
            "basis": FOREIGN_TURNKEY_BASIS,
            "external_capital_share": round(external_share, 9),
            "debt_treatment": (
                "All foreign-turnkey external capital is treated as debt; the "
                "OpenSourceRail case retains each country's generated grant/debt split."
            ),
            "formulas": {
                "turnkey_total": "open_source_rail_total_capex * price_multiplier",
                "turnkey_external_capital": (
                    "turnkey_total * external_capital_share"
                ),
                "external_capital_avoided": (
                    "turnkey_external_capital - open_source_rail_imported_capital"
                ),
            },
            "cases": {
                case: {
                    "price_multiplier": values["multiplier"],
                    "turnkey_total_usd": round(values["foreign_total"], 2),
                    "turnkey_external_capital_usd": round(
                        values["foreign_external"], 2
                    ),
                    "external_capital_avoided_usd": round(
                        values["external_saved"], 2
                    ),
                    "external_capital_reduction": round(
                        values["external_saved"] / values["foreign_external"], 9
                    ),
                    "external_interest_avoided_usd": round(
                        values["interest_saved"], 2
                    ),
                    "external_capital_plus_interest_avoided_usd": round(
                        values["lifetime_saved"], 2
                    ),
                }
                for case, values in data.case_totals.items()
            },
        },
        "observed_city_imported_share_range": {
            "minimum": round(min(data.imported_shares), 9),
            "maximum": round(max(data.imported_shares), 9),
        },
        "sources": [
            "lib/templates/capex-costs.toml",
            "lib/templates/country-finance.toml",
            "cities/catalogue/*/*/*/design.toml",
            "tools/automation/generate-national-briefs.py",
            "tools/automation/generate-portfolio-summary.py",
        ],
        "caveats": [
            "Planning sensitivity only; not a bid, financing offer, or audited origin declaration.",
            "Replace local/import shares with a country supplier and rules-of-origin audit.",
            "Replace comparator multipliers and financing terms with normalized bids and signed lender terms.",
            "Lifetime avoided financing excludes local-bond interest and operating expenditure.",
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = _portfolio_data()
    expected_outputs = {
        MARKDOWN_OUTPUT: build_summary(data),
        JSON_OUTPUT: build_json(data),
    }
    if args.check:
        stale = [
            path
            for path, expected in expected_outputs.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != expected
        ]
        for path in stale:
            print(f"stale: {path.relative_to(REPO_ROOT)}", file=sys.stderr)
        if stale:
            return 1
        print(
            "current: "
            + ", ".join(str(path.relative_to(REPO_ROOT)) for path in expected_outputs)
        )
        return 0
    for output, expected in expected_outputs.items():
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "w", dir=output.parent, delete=False, encoding="utf-8"
        ) as handle:
            handle.write(expected)
            temporary = Path(handle.name)
        temporary.replace(output)
        print(f"wrote {output.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
