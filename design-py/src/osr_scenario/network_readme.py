"""Generate a per-network README.md for any city design.

Consumes a `design.toml` + the expanded `scenario.toml` produced by
`osr_scenario` (so the sized PV / battery / fleet numbers are already
resolved) and writes a human-readable summary with:

- Network map reference (screenshots produced by
  `osr_scenario.render_map`)
- At-a-glance stats (lines, stations, coverage, transfer
  reachability, route-km, fleet, headway)
- Per-line table (length, stations, trainsets, termini)
- Rolling-stock spec
- Ridership capacity (peak pphpd, network throughput, daily
  theoretical, practical estimate)
- Catchment population
- Energy infrastructure (PV + battery per tier, totals)
- Cost estimate at configurable unit rates
  ($2M/km track, $1/W solar, $1/W battery by default)
- File map + reproducibility command

Usage:
    python -m osr_scenario.network_readme \\
        --design designs/west-asia/Iraq/Samawah/design.toml \\
        --scenario designs/west-asia/Iraq/Samawah/samawah.toml \\
        --out designs/west-asia/Iraq/Samawah/README.md \\
        --population 220000

Can be driven from the batch planner too — `plan_city(...)` emits
the `design.toml`; this module then produces the README as a
one-liner per city in a 500-city run.
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


# --------------------------------------------------------------------------
# Cost + capacity assumptions
# --------------------------------------------------------------------------


@dataclass
class CostAssumptions:
    """Rule-of-thumb unit rates. Override for a city/country-specific
    estimate (Iraqi labour/materials differ from, say, French ones)."""

    track_cost_per_km_usd: float = 2_000_000.0
    solar_cost_per_w_usd: float = 1.0
    battery_cost_per_w_usd: float = 1.0
    battery_discharge_hours: float = 4.0  # BESS typical 4-hour duration
    train_car_cost_usd: float = 1_000_000.0  # cost per CAR; a 3-car trainset = 3 × this
    station_cost_usd: float = 1_000_000.0
    depot_cost_usd: float = 5_000_000.0
    # Bridges/viaducts run $20 M/km (vs $2 M/km for at-grade). This
    # fraction of the total route is assumed to be elevated — river
    # crossings, highway overpasses, urban-core RoW constraints.
    bridge_fraction: float = 0.15
    bridge_cost_per_km_usd: float = 20_000_000.0
    # `None` means "use the family-specific value resolved in
    # NetworkStats from rolling-stock.toml". Pass `--pax-per-trainset`
    # at the CLI to override (what-if analysis only — production runs
    # should rely on the family table).
    trainset_capacity_pax: int | None = None


# --------------------------------------------------------------------------
# Stat extraction
# --------------------------------------------------------------------------


@dataclass
class NetworkStats:
    city_name: str
    country_iso: str
    population: int

    line_count: int
    unique_station_count: int
    interchange_count: int
    route_km: float
    transfer_reachability: float
    coverage: float

    revenue_fleet: int
    spare_fleet: int
    reserve_fleet: int

    peak_headway_min: float
    service_start: str
    service_end: str

    total_pv_kw: float
    total_battery_kwh: float
    total_charging_kw: float

    depot_count: int

    consist_cars: int
    consist_length_m: int
    consist_battery_kwh: int
    consist_max_speed_kmh: float
    consist_family: str
    trainset_capacity_pax: int


def _load(path: Path) -> dict:
    return tomllib.loads(Path(path).read_text())


def _line_length_km(design_line: dict) -> float:
    # Prefer the rust-emitted `length_m` field on the line itself; the
    # older schema nested `stations = [{ distance_from_prev_m, ... }]`
    # inside each line, but `osr-design` now writes a flat station list
    # keyed by `line` and a top-level `length_m` per [[lines]] block.
    if "length_m" in design_line:
        return float(design_line["length_m"]) / 1000.0
    return (
        sum(s.get("distance_from_prev_m", 0) for s in design_line.get("stations", []))
        / 1000.0
    )


def compute_stats(
    design: dict, scenario: dict, population: int
) -> NetworkStats:
    # The rust `osr-design` emitter writes `[city]` with `slug` /
    # `country` / `population`; older python-side designs used
    # `[location]` with `city` / `country`. Read both for back-compat.
    loc = design.get("location", {})
    city_block = design.get("city", {})
    city_name = (
        loc.get("city")
        or city_block.get("name")
        or (city_block.get("slug") or "").title()
        or design.get("design", {}).get("name", "Network")
    )
    country_iso = loc.get("country") or city_block.get("country", "??")

    lines = design.get("lines", [])
    line_count = len(lines)
    route_km = round(sum(_line_length_km(L) for L in lines), 1)
    unique_stations = {s["id"] for s in design.get("stations", [])}
    interchange_count = sum(
        1 for s in design.get("stations", [])
        if s.get("archetype") in ("interchange", "interchange-elevated")
    )

    # Transfer reachability.
    transfer = _transfer_reachability(lines)

    # Coverage — `render_readme` injects `_quality_coverage` after
    # reading `<slug>.design-quality.yaml` next to the design.toml
    # (the auto-gate's anchor-weighted reachability score). Falls
    # back to a `[stats] coverage=` override in design.toml, then 0.0.
    coverage = float(
        design.get("_quality_coverage")
        or design.get("stats", {}).get("coverage", 0.0)
    )

    # Fleet. The rust emitter writes `peak_count` (revenue),
    # `spare_count`, `cold_reserve_count`, and `trainset_count`
    # (= peak + spare + reserve). Older designs may carry only
    # `trainset_count` — fall back to that when `peak_count` is
    # absent so the revenue/spare/reserve split still resolves.
    fleets = design.get("fleets", [])
    revenue = sum(
        int(f.get("peak_count") or f.get("trainset_count", 0))
        for f in fleets
    )
    spare = sum(int(f.get("spare_count", 0)) for f in fleets)
    reserve = sum(int(f.get("cold_reserve_count", 0)) for f in fleets)
    if spare + reserve == 0:
        # Apply the template default (50 % spare+reserve).
        spare = revenue // 3
        reserve = revenue // 4

    # Peak headway (from the scenario's timetable section, if present).
    peak_headway_min = 5.0
    for sec in scenario.get("timetable", {}).get("sections", []):
        if sec.get("name", "").lower() in ("peak", "am-peak", "pm-peak"):
            peak_headway_min = min(peak_headway_min, float(sec.get("headway_min", 5.0)))

    # Default service window 05:30–02:00 (20.5 h/day) — hot-climate
    # cities run later than the European 18 h day. Operator can
    # override per scenario by setting `[timetable] service_hours`.
    service_hours = scenario.get("timetable", {}).get(
        "service_hours", "05:30-02:00"
    )
    service_start, _, service_end = service_hours.partition("-")

    # Energy (from expanded scenario).
    total_pv = sum(
        float(s.get("pv_nameplate_kw", 0.0)) for s in scenario.get("sites", [])
    )
    total_batt = sum(
        float(s.get("storage_capacity_kwh", 0.0)) for s in scenario.get("sites", [])
    )
    total_charging = sum(
        float(s.get("charging_power_kw", 0.0)) for s in scenario.get("stations", [])
    )

    consist = scenario.get("consist", {})
    # Resolve the rolling-stock family so we can look up family-
    # specific passenger capacity. The rust emitter writes
    # `rolling_stock = "<family>"` on every [[lines]] block; older
    # designs may carry it on the consist directly.
    family_lines = design.get("lines", [])
    family = (
        consist.get("family")
        or (family_lines[0].get("rolling_stock") if family_lines else None)
        or "light-metro-3car"
    )
    capacity_pax = _trainset_capacity_for_family(family)

    return NetworkStats(
        city_name=city_name,
        country_iso=country_iso,
        population=population,
        line_count=line_count,
        unique_station_count=len(unique_stations),
        interchange_count=interchange_count,
        route_km=route_km,
        transfer_reachability=transfer,
        coverage=coverage,
        revenue_fleet=revenue,
        spare_fleet=spare,
        reserve_fleet=reserve,
        peak_headway_min=peak_headway_min,
        service_start=service_start.strip() or "05:30",
        service_end=service_end.strip() or "02:00",
        total_pv_kw=total_pv,
        total_battery_kwh=total_batt,
        total_charging_kw=total_charging,
        consist_cars=int(consist.get("car_count", 3)),
        consist_length_m=int(consist.get("length_m", 68)),
        consist_battery_kwh=int(consist.get("battery_capacity_kwh", 320)),
        consist_max_speed_kmh=float(consist.get("max_speed_kmh", 80)),
        consist_family=family,
        trainset_capacity_pax=capacity_pax,
        depot_count=len(design.get("depots", [])),
    )


_FAMILY_CAPACITY_FALLBACK: dict[str, int] = {
    "tram-2car": 220,
    "light-metro-3car": 360,
    "metro-4car": 540,
    "metro-6car": 900,
}


def _load_country_finance(country: str) -> dict:
    """Read country financial parameters from
    `lib/templates/country-finance.toml`. Falls back to the `XX`
    middle-income default if the country isn't listed."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "lib/templates/country-finance.toml"
        if candidate.exists():
            try:
                doc = tomllib.loads(candidate.read_text())
                table = doc.get("countries", {})
                if country.upper() in table:
                    return table[country.upper()]
                return table.get("XX", {})
            except Exception:
                break
            break
    return {}


def _funding_and_affordability_section(
    design: dict, costs: dict, stats: NetworkStats, rel
) -> list[str]:
    """Emit the `## Funding & affordability` section: CAPEX funding
    stack (multilateral + sovereign + equity), annual OPEX, ticket
    pricing anchored to median income, and farebox-recovery shortfall.

    Pure function of the costs block + country-finance config — no
    network calls. Designed so any new city listed in
    `lib/city-batches/world-sample.toml` automatically gets a finance
    section without code changes.
    """
    fin = _load_country_finance(stats.country_iso)
    if not fin:
        return []

    total_eur = float(costs.get("total_eur", 0.0))
    if total_eur <= 0:
        return []

    # Funding stack — three-tranche default that mirrors how IBRD /
    # AfDB / ADB-financed urban-rail projects in target regions are
    # actually capitalised. Multilateral + sovereign-bond + equity
    # split is parametrised here so deployments can override per the
    # specific MoU.
    multi_frac = 0.60
    bond_frac = 0.25
    equity_frac = 0.15
    multi_eur = total_eur * multi_frac
    bond_eur = total_eur * bond_frac
    equity_eur = total_eur * equity_frac

    multi_rate = float(fin.get("multilateral_loan_rate", 0.045))
    bond_rate = float(fin.get("sovereign_bond_rate", 0.07))
    tenor = int(fin.get("loan_tenor_years", 25))
    grace = int(fin.get("capex_grace_years", 5))

    # Level annual debt service after grace, simple amortisation.
    def _annuity(principal: float, rate: float, years: int) -> float:
        if rate <= 0:
            return principal / max(years, 1)
        a = (1 - (1 + rate) ** -years)
        return principal * rate / a if a > 0 else principal / max(years, 1)

    multi_annuity = _annuity(multi_eur, multi_rate, tenor - grace)
    bond_annuity = _annuity(bond_eur, bond_rate, tenor - grace)
    annual_debt_service_eur = multi_annuity + bond_annuity

    # OPEX model. Components, all in EUR / year. Each line covers one
    # discrete asset class — no double-counting between rolling-stock
    # maintenance and traction power, no electricity charge on top of
    # solar self-generation.
    #
    #   • rolling-stock maintenance — 4 % of rolling-stock CAPEX. Covers
    #     onboard motors, batteries, body, electronics, brakes, doors,
    #     HVAC, cell-replacement amortised over the 12 y Na-ion life.
    #     Onboard batteries appear ONLY here.
    #   • civil + station + depot maintenance — 2 % of (civil+stations+
    #     depots) CAPEX. Covers track, building, station canopy,
    #     **trackside PV array**, **trackside Na-ion stationary
    #     storage**, and depot-side power infrastructure. Stationary
    #     batteries appear ONLY here.
    #   • signalling + comms maintenance — 5 % of signalling CAPEX
    #     (fast cycles for trackside electronics).
    #   • traction energy — **€0 / yr in the steady state**. The
    #     network is self-sufficient on its own trackside PV per
    #     RFC 0002 §6 (~$30 M energy-subsystem CAPEX sized for the
    #     deployment's full kWh/car-km demand). Earlier OPEX models
    #     billed €0.10/kWh × annual car-km on top of that — i.e. they
    #     paid for the same electricity twice (once in the PV CAPEX,
    #     once as a phantom utility bill). Removed 2026-04-26 per the
    #     operator-review correction.
    #   • labour — derived from headcount × country-median salary.
    rs_maint = 0.04 * float(costs.get("rolling_stock_eur", 0.0))
    civil_maint = 0.02 * (
        float(costs.get("civil_subtotal_eur", 0.0))
        + float(costs.get("stations_eur", 0.0))
        + float(costs.get("depots_eur", 0.0))
    )
    sig_maint = 0.05 * float(costs.get("signalling_eur", 0.0))

    # Annual train-km from realistic per-trainset utilisation:
    #   service-hours per day × 365 service-days × commercial speed
    #   × revenue-factor (terminal turnarounds + dwells + off-peak
    #   headway slack + daily depot turnaround + ~2 % maintenance
    #   downtime).
    #
    # Service hours bumped 2026-04-26 from a 18 h / 280-day model
    # (typical northern-Europe operating hours) to **20.5 h / 365 d**
    # — operator brief: hot-climate cities run later (Samawah,
    # Baghdad, Cairo, Karachi all have post-midnight street life and
    # benefit from late service). 5:30 → 02:00 = 20.5 h.
    consist_cars = stats.consist_cars
    revenue_trainsets = stats.revenue_fleet
    service_hours_per_day = 20.5  # 05:30–02:00
    service_days_per_year = 365
    commercial_speed_kmh = {
        "tram-2car": 22.0,
        "light-metro-3car": 30.0,
        "metro-4car": 35.0,
        "metro-6car": 35.0,
    }.get(stats.consist_family, 30.0)
    revenue_factor = 0.75
    annual_km_per_trainset = (
        service_hours_per_day
        * service_days_per_year
        * commercial_speed_kmh
        * revenue_factor
    )
    annual_train_km = revenue_trainsets * annual_km_per_trainset
    annual_car_km = annual_train_km * consist_cars

    # Annual traction energy demand at 4 kWh/car-km. Reported for
    # reference; **not** charged in OPEX because trackside PV provides
    # it. Grid-tie standby is part of civil_maint.
    annual_energy_gwh = annual_car_km * 4.0 / 1e6
    energy_eur = 0.0

    # Labour. OSR-discipline headcount per RFC 0014 §4 + RFC 0013
    # rulebook: GoA 4 driverless (no train drivers), open-source CBTC
    # (no proprietary signalling contract), reduced station staff
    # (level boarding + PSDs handle most platform safety). Industry
    # benchmark for legacy metros is ~45–70 FTE per route-km
    # (Singapore SMRT, Hong Kong MTR); OSR-discipline target is
    # ~6 FTE per route-km plus a 12-person admin/OCC core.
    ops_fte_per_km = 6.0
    headcount = int(round(ops_fte_per_km * stats.route_km)) + 12
    monthly_income = float(fin.get("median_monthly_income_usd", 600))
    # Salary mix: country-median × 12 × engineer-premium 1.4
    # (mainline maintainers / dispatchers / inspectors paid 1.5–2 ×
    # median; station staff ~1.0; weighted blend ≈ 1.4).
    labour_usd = headcount * monthly_income * 12 * 1.4
    labour_eur = labour_usd * 0.92  # USD→EUR

    annual_opex_eur = rs_maint + civil_maint + sig_maint + energy_eur + labour_eur

    # Affordability-anchored ticket pricing.
    #   • Monthly pass priced at 5 % of country median monthly income.
    #   • Single trip = 1/30 of monthly pass (assumes ~60 trips/month
    #     for a daily commuter, monthly pass is a 50 % bulk discount).
    target_monthly_pass_usd = 0.05 * monthly_income
    target_trip_usd = target_monthly_pass_usd / 30.0
    target_trip_eur = target_trip_usd * 0.92

    # Farebox revenue at affordability price, given network capacity.
    # Daily realisation 5–10 % of population × 365 service-days
    # (matches the OPEX service-year model — 5:30 to 02:00, 365 days).
    daily_pax_low = 0.05 * stats.population
    daily_pax_high = 0.10 * stats.population
    annual_pax_low = daily_pax_low * service_days_per_year
    annual_pax_high = daily_pax_high * service_days_per_year
    farebox_low_eur = annual_pax_low * target_trip_eur
    farebox_high_eur = annual_pax_high * target_trip_eur

    target_recovery = float(fin.get("farebox_recovery_target", 0.5))

    def _eur(v: float) -> str:
        if v >= 1e9:
            return f"€{v / 1e9:.2f} bn"
        if v >= 1e7:
            return f"€{v / 1e6:.0f} M"
        if v >= 1e6:
            return f"€{v / 1e6:.1f} M"
        return f"€{v / 1e3:.0f} k"

    out: list[str] = []
    out.append("## Funding & affordability\n")
    finance_link = rel("lib/templates/country-finance.toml")
    out.append(
        "Planning-grade financing model anchored to country financial "
        "parameters from "
        f"[`lib/templates/country-finance.toml`]({finance_link}). "
        "Pure function of the [costs] block above + the country code — "
        "regenerate by re-running `scripts/regenerate-city.sh "
        f"{stats.city_name.split()[0].lower()}`.\n"
    )

    out.append("### CAPEX funding stack\n")
    out.append("| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |")
    out.append("|---|---|---|---|---|---|")
    out.append(
        f"| Multilateral concessional loan (IBRD / AfDB / ADB class) | "
        f"{multi_frac:.0%} | {_eur(multi_eur)} | {multi_rate:.1%} | "
        f"{tenor} y, {grace} y grace | {_eur(multi_annuity)} / yr |"
    )
    out.append(
        f"| Sovereign bonds (10-y benchmark + project) | "
        f"{bond_frac:.0%} | {_eur(bond_eur)} | {bond_rate:.1%} | "
        f"{tenor} y, {grace} y grace | {_eur(bond_annuity)} / yr |"
    )
    out.append(
        f"| Government equity (no debt service) | "
        f"{equity_frac:.0%} | {_eur(equity_eur)} | — | — | — |"
    )
    out.append(
        f"| **Total** | **100%** | **{_eur(total_eur)}** | | | "
        f"**{_eur(annual_debt_service_eur)} / yr** |\n"
    )

    out.append("### Annual OPEX (steady state)\n")
    out.append("| Component | Basis | Annual cost |")
    out.append("|---|---|---|")
    out.append(
        f"| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | "
        f"{_eur(rs_maint)} |"
    )
    out.append(
        f"| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | "
        f"{_eur(civil_maint)} |"
    )
    out.append(
        f"| Signalling + comms maintenance | 5 % of signalling CAPEX | "
        f"{_eur(sig_maint)} |"
    )
    out.append(
        f"| Traction energy ({annual_energy_gwh:.1f} GWh / yr) | "
        f"trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | "
        f"{_eur(energy_eur)} |"
    )
    out.append(
        f"| Labour ({headcount:,} FTE) | "
        f"~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | "
        f"{_eur(labour_eur)} |"
    )
    out.append(
        f"| **OPEX subtotal** | | **{_eur(annual_opex_eur)} / yr** |\n"
    )
    out.append(
        f"_Annual fleet utilisation: {revenue_trainsets} revenue trainsets × "
        f"{service_hours_per_day:.1f} h/day × {service_days_per_year} d/yr × "
        f"{commercial_speed_kmh:.0f} km/h commercial × {revenue_factor:.0%} "
        f"revenue factor = {annual_train_km / 1e6:.1f} M train-km / yr "
        f"(~{annual_km_per_trainset / 1e3:.0f} k km / trainset / yr)._\n"
    )

    out.append("### Ticket pricing anchored to median income\n")
    out.append(
        f"Country median monthly income: **${monthly_income:,.0f} USD** "
        f"(per [`lib/templates/country-finance.toml`]({rel('lib/templates/country-finance.toml')})). "
        f"Target affordability: monthly unlimited pass at 5 % of "
        f"median income → single-trip price set by the 30:1 pass / trip "
        f"ratio used by every operator in the affordability literature "
        f"(STIB, Delhi Metro, Cairo Metro).\n"
    )
    out.append("| Product | Price target |")
    out.append("|---|---|")
    out.append(
        f"| Single-trip fare | "
        f"€{target_trip_eur:.2f} (~${target_trip_usd:.2f} USD) |"
    )
    out.append(
        f"| Day pass (3 trips) | "
        f"€{(target_trip_eur * 3 * 0.85):.2f} (15 % bulk discount) |"
    )
    out.append(
        f"| Monthly unlimited pass | "
        f"€{(target_monthly_pass_usd * 0.92):.2f} (~5 % of median monthly income) |"
    )
    out.append(
        f"| Annual pass | "
        f"€{(target_monthly_pass_usd * 0.92 * 11):.2f} (10 × monthly = ~1 free month) |\n"
    )

    out.append("### Farebox & operating subsidy\n")
    out.append(
        f"Practical-ridership bracket = 5–10 % of urban population × "
        f"{service_days_per_year} service-days. At the affordability-anchored fare:\n"
    )
    out.append("| | Low scenario | High scenario |")
    out.append("|---|---|---|")
    out.append(
        f"| Annual paid trips | {annual_pax_low / 1e6:,.1f} M | "
        f"{annual_pax_high / 1e6:,.1f} M |"
    )
    out.append(
        f"| Farebox revenue | {_eur(farebox_low_eur)} / yr | "
        f"{_eur(farebox_high_eur)} / yr |"
    )
    out.append(
        f"| Farebox / OPEX recovery | "
        f"{(farebox_low_eur / annual_opex_eur):.0%} | "
        f"{(farebox_high_eur / annual_opex_eur):.0%} |"
    )
    out.append(
        f"| Country target recovery | "
        f"{target_recovery:.0%} | {target_recovery:.0%} |"
    )
    target_revenue = target_recovery * annual_opex_eur
    operating_subsidy_low = max(0.0, target_revenue - farebox_low_eur)
    operating_subsidy_high = max(0.0, target_revenue - farebox_high_eur)
    out.append(
        f"| Operating subsidy needed | "
        f"{_eur(operating_subsidy_low)} / yr | "
        f"{_eur(operating_subsidy_high)} / yr |"
    )
    debt_subsidy_low = annual_debt_service_eur + operating_subsidy_low
    debt_subsidy_high = annual_debt_service_eur + operating_subsidy_high
    out.append(
        f"| **Total annual government burden** | "
        f"**{_eur(debt_subsidy_low)} / yr** | "
        f"**{_eur(debt_subsidy_high)} / yr** |\n"
    )

    out.append(
        "**Caveats:** The funding-stack 60/25/15 split, the 5 % "
        "income-share affordability target, and the 5–10 % daily-pax "
        "bracket are project-level defaults. Real deployments will negotiate "
        "the share with the financing institutions and will tune fares "
        "iteratively from boarding data. Treat the numbers above as a "
        "first-iteration sanity check, not as a bid-ready financial close.\n"
    )

    return out


def _coverage_from_quality_yaml(design_path: Path) -> float:
    """Read the `high_demand_coverage` field from
    `<slug>.design-quality.yaml` next to the design.toml. Returns
    0.0 when the file is missing or unparseable — the caller falls
    through to the legacy `[stats] coverage` override or the
    placeholder text. Stdlib-only mini-parser since `yaml` isn't a
    project-level dependency."""
    parent = design_path.parent
    candidates = list(parent.glob("*.design-quality.yaml"))
    if not candidates:
        return 0.0
    try:
        for line in candidates[0].read_text().splitlines():
            stripped = line.strip()
            if stripped.startswith("high_demand_coverage:"):
                value = stripped.split(":", 1)[1].strip()
                # Strip trailing comments and quotes.
                value = value.split("#", 1)[0].strip().strip('"').strip("'")
                return float(value)
    except Exception:
        return 0.0
    return 0.0


def _trainset_capacity_for_family(family: str) -> int:
    """Resolve `passenger_capacity` for a rolling-stock family.

    Source of truth is `lib/templates/rolling-stock.toml` (RFC 0008
    family catalogue). Falls back to a baked table if the template
    isn't reachable from the cwd (e.g. when this is run from a
    detached scenario folder during tests)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "lib/templates/rolling-stock.toml"
        if candidate.exists():
            try:
                doc = tomllib.loads(candidate.read_text())
                profiles = doc.get("profiles", {})
                if family in profiles and "passenger_capacity" in profiles[family]:
                    return int(profiles[family]["passenger_capacity"])
            except Exception:
                break
            break
    return _FAMILY_CAPACITY_FALLBACK.get(family, 360)


def _transfer_reachability(lines: list[dict]) -> float:
    if len(lines) < 2:
        return 1.0
    sets = [{s["id"] for s in L.get("stations", [])} for L in lines]
    pairs = shared = 0
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            pairs += 1
            if sets[i] & sets[j]:
                shared += 1
    return shared / pairs if pairs else 1.0


# --------------------------------------------------------------------------
# README rendering
# --------------------------------------------------------------------------


def render_readme(
    design_path: Path,
    scenario_path: Path,
    *,
    population: int,
    cost: CostAssumptions | None = None,
    screenshot_slug: str | None = None,
) -> str:
    """Return the README text for this network."""
    cost = cost or CostAssumptions()
    design = _load(design_path)
    scenario = _load(scenario_path)
    # Surface anchor-weighted coverage from the `osr-design`-emitted
    # `<slug>.design-quality.yaml` so the README can report a real
    # coverage figure (and a derived catchment estimate) instead of
    # the "*(requires a coverage score)*" placeholder.
    design.setdefault(
        "_quality_coverage",
        _coverage_from_quality_yaml(design_path),
    )
    stats = compute_stats(design, scenario, population)

    # Map-image filename slug. The rust `osr-design` emitter writes
    # `[city] slug = "samawah"` and `osr_scenario.render_map` writes
    # `<slug>-network-map.png` next to the design.toml. Older
    # hand-crafted designs used `[design] id` (sometimes namespaced
    # as `iraq/samawah`); strip to the basename for either case.
    # If neither is set, fall back to the design.toml's parent
    # directory name (e.g. "Samawah") rather than the literal
    # "city" — that placeholder pointed at a file that never exists.
    screenshot_slug = screenshot_slug or (
        design.get("city", {}).get("slug")
        or design.get("design", {}).get("id", "").rsplit("/", 1)[-1]
        or design_path.parent.name
    ).lower()

    # Compute how many `..` to climb from the README's folder to repo root.
    rel_to_root = _rel_to_repo_root(design_path.parent)

    # Relative paths from the README's folder into the repo tree.
    def rel(*parts: str) -> str:
        return "/".join([rel_to_root, *parts]) if rel_to_root else "/".join(parts)

    # Ridership capacity. Per-train capacity comes from the
    # rolling-stock family (RFC 0008 §1) — Samawah's 3-car
    # `light-metro-3car` carries 360 pax, Baghdad's 6-car
    # `metro-6car` carries 900. The CLI override
    # (`--pax-per-trainset`) wins when present so what-if analysis
    # still works.
    trains_per_hour_per_dir = 60 / stats.peak_headway_min
    capacity_pax = (
        cost.trainset_capacity_pax
        if cost.trainset_capacity_pax is not None
        else stats.trainset_capacity_pax
    )
    per_line_pphpd = capacity_pax * trains_per_hour_per_dir
    network_peak_per_h = per_line_pphpd * stats.line_count * 2
    daily_theoretical = network_peak_per_h * 10  # peak≈10% of daily
    catchment = int(stats.coverage * stats.population) if stats.coverage > 0 else None
    practical_daily_low = int((catchment or stats.population) * 0.10) if catchment else None
    practical_daily_high = int((catchment or stats.population) * 0.15) if catchment else None

    # Cost.
    # Route-km split: any ring line is assumed to be 100 % viaduct
    # (its whole value is crossing empty land fast without following
    # road RoW). Radial lines carry the usual 85/15 at-grade/bridge
    # mix. Ring detected by `line-ring` id or "Ring" in the name.
    ring_km = 0.0
    for L in design.get("lines", []):
        if L.get("id") == "line-ring" or "ring" in L.get("name", "").lower():
            ring_km += sum(
                s.get("distance_from_prev_m", 0)
                for s in L.get("stations", [])
            ) / 1000.0
    radial_km = max(0.0, stats.route_km - ring_km)
    bridge_km_radials = radial_km * cost.bridge_fraction
    at_grade_km = radial_km - bridge_km_radials
    track_cost = cost.track_cost_per_km_usd * at_grade_km
    bridge_cost = cost.bridge_cost_per_km_usd * bridge_km_radials
    ring_cost = cost.bridge_cost_per_km_usd * ring_km
    solar_cost = cost.solar_cost_per_w_usd * stats.total_pv_kw * 1_000
    battery_kw_equiv = stats.total_battery_kwh / cost.battery_discharge_hours
    battery_cost = cost.battery_cost_per_w_usd * battery_kw_equiv * 1_000
    total_trainsets = stats.revenue_fleet + stats.spare_fleet + stats.reserve_fleet
    total_cars = total_trainsets * stats.consist_cars
    rolling_stock_cost = cost.train_car_cost_usd * total_cars
    station_cost = cost.station_cost_usd * stats.unique_station_count
    depot_cost = cost.depot_cost_usd * stats.depot_count
    total_capex = (
        track_cost + bridge_cost + ring_cost
        + solar_cost + battery_cost
        + rolling_stock_cost + station_cost + depot_cost
    )

    # Per-line table.
    by_id = {s["id"]: s for s in design.get("stations", [])}
    # Lines emitted by `osr-design` carry `name` (slug-style id) — use
    # it for both keying and display.
    fleet_by_line = {
        f["line"]: int(f.get("trainset_count", 0))
        for f in design.get("fleets", [])
    }
    # Build per-line ordered station lists from the flat station list
    # (rust schema). Falls back to inline `stations = [...]` arrays
    # if a design.toml carries them (older schema).
    stations_by_line: dict[str, list[dict]] = {}
    for s in design.get("stations", []):
        stations_by_line.setdefault(s.get("line", ""), []).append(s)
    for sts in stations_by_line.values():
        sts.sort(key=lambda s: float(s.get("s_m", 0.0)))

    # Terminus tagging — compass quadrant + radial band relative to the
    # network's geometric centroid. Replaces raw OSM `anchor_name`
    # display (which mixed Arabic / English / Russian / fallback IDs
    # like "line-7-1088-2164" depending on what OSM happened to label
    # each cell) with a clean planning-grade label like "N Outer" /
    # "SE Mid". `Inner < 0.33 R`, `0.33 R ≤ Mid ≤ 0.67 R`,
    # `Outer > 0.67 R`, where R is the network's outermost
    # station-to-centroid distance.
    terminus_tag = _build_terminus_tagger(design.get("stations", []))

    line_rows: list[str] = []
    for L in design.get("lines", []):
        line_id = L.get("id") or L["name"]
        line_name = L.get("name", line_id)
        length_km = _line_length_km(L)
        inline_sts = L.get("stations") or stations_by_line.get(line_id, [])
        station_ids = [s["id"] for s in inline_sts]

        first = terminus_tag(station_ids[0]) if station_ids else ""
        last = terminus_tag(station_ids[-1]) if station_ids else ""
        trainsets = fleet_by_line.get(line_id, 0)
        line_rows.append(
            f"| {line_name} | {length_km:4.1f} km | "
            f"{len(station_ids)} | {trainsets} | {first} ↔ {last} |"
        )

    # Energy sites grouped by tier.
    tier_groups: dict[str, list[dict]] = {}
    for s in scenario.get("sites", []):
        tier = s.get("tier", "standard")
        tier_groups.setdefault(tier, []).append(s)
    tier_rows: list[str] = []
    for tier in sorted(tier_groups):
        sites = tier_groups[tier]
        pv_each = sites[0].get("pv_nameplate_kw", 0)
        batt_each = sites[0].get("storage_capacity_kwh", 0)
        tier_rows.append(
            f"| {tier.title()} | {len(sites)} | "
            f"{pv_each:.0f} kW | {batt_each:.0f} kWh |"
        )

    # -- Assemble --
    coverage_str = (
        f"{stats.coverage:.1%}"
        if stats.coverage > 0
        else "— (re-emit design.toml — `<slug>.design-quality.yaml` is missing `high_demand_coverage`)"
    )
    catchment_str = (
        f"**≈ {catchment:,}** (within ~800 m walk of a station)"
        if catchment else "*(run the planner with a fresh coverage score)*"
    )
    daily_practical_str = (
        f"≈ **{practical_daily_low:,} – {practical_daily_high:,} trips/day**"
        if practical_daily_low else "*(requires a coverage score)*"
    )

    out: list[str] = []
    out.append(f"# {stats.city_name} — Urban Rail Network\n")
    out.append(
        f"**Country:** {stats.country_iso} · "
        f"**Population:** {stats.population:,}\n"
    )
    out.append(
        "Auto-planned by the OpenSourceRail design pipeline: "
        f"[`osr_geo`]({rel('design-py/src/osr_geo/')}) rasterises "
        "Overpass-verified OpenStreetMap features (arterial road graph, "
        "buildings, water, protected land, demand-anchor POIs) onto a "
        "20 m cost / demand / buildability grid; "
        f"[`osr-design`]({rel('crates/osr-design/')}) (rust) runs a "
        "demand-rewarded Dijkstra on that grid to synthesise corridors, "
        "places stations against the demand surface, and classifies "
        "every segment (at-grade / elevated / bridge — no tunnels per "
        "[RFC 0011](" + rel('docs/rfcs/0011-civil-infrastructure-design-standard.md') + ")). "
        "Population, country, and bbox are read from the canonical city "
        f"catalog at [`lib/city-batches/world-sample.toml`]({rel('lib/city-batches/world-sample.toml')}).\n"
    )

    out.append("## Network map\n")
    # Single auto-fit map of the whole network, rendered by
    # `osr_scenario.render_map`. (An earlier "inner-core detail"
    # variant was retired — the auto-fit map covers the same ground
    # without needing a second file.)
    out.append(
        f"![{stats.city_name} rail network on OpenStreetMap]"
        f"({screenshot_slug}-network-map.png)\n"
    )
    out.append(
        "*Every line visible end-to-end — radials out to the city "
        "edge, forced-coverage suburbs, and the ring line if "
        "present. Auto-fit zoom based on the network's actual "
        "bounding box.*\n"
    )
    out.append(
        f"Corridor polylines + stations as GeoJSON for GIS / "
        f"alignment tooling: "
        f"[`{screenshot_slug}.corridor.geojson`]"
        f"({screenshot_slug}.corridor.geojson).\n"
    )

    out.append("## At a glance\n")
    out.append("| Metric | Value |")
    out.append("|---|---|")
    out.append(f"| Lines | {stats.line_count} |")
    out.append(f"| Unique stations | {stats.unique_station_count} |")
    out.append(f"| Interchange stations | {stats.interchange_count} |")
    out.append(
        f"| Multi-line transfer reachability | "
        f"{stats.transfer_reachability:.0%} (line-pairs sharing ≥ 1 station) |"
    )
    out.append(f"| Anchor-weighted coverage | {coverage_str} |")
    out.append(f"| Route length (double track) | {stats.route_km:.1f} km |")
    out.append(
        f"| Revenue fleet | {stats.revenue_fleet} × "
        f"{stats.consist_cars}-car trainsets |"
    )
    out.append(
        f"| Spare + cold-reserve | "
        f"{stats.spare_fleet + stats.reserve_fleet} × "
        f"{stats.consist_cars}-car trainsets |"
    )
    out.append(f"| Peak headway | {stats.peak_headway_min:.0f} min |")
    out.append(
        f"| Service hours | "
        f"{stats.service_start} – {stats.service_end} "
        f"(≈ {_hours(stats.service_start, stats.service_end):.0f} h/day) |"
    )
    out.append("")

    out.append("## Lines\n")
    out.append(
        "*Termini are tagged by compass quadrant + radial band "
        "(Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where "
        "R is the network's outermost station-to-centre distance).*\n"
    )
    out.append("| Line | Length | Stations | Trainsets | Termini |")
    out.append("|---|---|---|---|---|")
    out.extend(line_rows)
    # Per-line `Trainsets` columns carry the **total** per line
    # (peak + spare + cold-reserve, as written by `osr-design` to
    # `[[fleets]] trainset_count`). The footer must be the sum of
    # those — i.e. the full fleet (revenue + spare + cold-reserve),
    # not the revenue-only number — or the row totals don't add up.
    total_fleet = stats.revenue_fleet + stats.spare_fleet + stats.reserve_fleet
    out.append(
        f"| **Total** | **{stats.route_km:.1f} km** | "
        f"**{stats.unique_station_count} unique** | "
        f"**{total_fleet}** | |\n"
    )

    out.append("## Rolling stock\n")
    out.append("| Property | Value |")
    out.append("|---|---|")
    out.append(
        f"| Consist | {stats.consist_cars}-car, "
        f"{stats.consist_length_m} m |"
    )
    out.append(f"| Max speed | {stats.consist_max_speed_kmh:.0f} km/h |")
    out.append(f"| Onboard battery | {stats.consist_battery_kwh} kWh per trainset |")
    out.append(
        f"| Nominal capacity | {capacity_pax} pax (seated + standing, "
        f"`{stats.consist_family}` per RFC 0008 §1) |\n"
    )

    out.append("## Ridership capacity\n")
    out.append(
        f"- **Per-train capacity:** {capacity_pax} passengers "
        f"(`{stats.consist_family}`)"
    )
    out.append(
        f"- **Peak frequency:** {trains_per_hour_per_dir:.0f} trains/hour/direction "
        f"({stats.peak_headway_min:.0f}-min headway)"
    )
    out.append(
        f"- **Peak capacity per line per direction:** "
        f"{capacity_pax} × {trains_per_hour_per_dir:.0f} "
        f"= **{per_line_pphpd:,.0f} pphpd**"
    )
    out.append(
        f"- **Network peak throughput (all lines, both directions):** "
        f"{stats.line_count} lines × 2 directions × {per_line_pphpd:,.0f} "
        f"= **{network_peak_per_h:,.0f} passengers/hour**"
    )
    out.append(
        f"- **Daily theoretical capacity (peak × 10):** ≈ **{daily_theoretical:,.0f} passenger-trips/day**"
    )
    out.append(
        f"- **Practical daily ridership estimate** (10–15 % of catchment): "
        f"{daily_practical_str}\n"
    )

    out.append("## Catchment\n")
    out.append(f"- City population: **{stats.population:,}**")
    out.append(f"- Anchor-weighted coverage: {coverage_str}")
    out.append(f"- Catchment population: {catchment_str}\n")

    out.append("## Energy infrastructure (solar + battery)\n")
    out.append(
        "On-site trackside + depot PV and battery storage. "
        f"Per-tier sizing (from [`{rel('lib/templates/energy-sites.toml')}`]"
        f"({rel('lib/templates/energy-sites.toml')})):\n"
    )
    out.append("| Tier | Sites | PV each | Battery each |")
    out.append("|---|---|---|---|")
    out.extend(tier_rows)
    out.append(
        f"| **Total installed** | "
        f"**{sum(len(v) for v in tier_groups.values())}** | "
        f"**{stats.total_pv_kw:,.0f} kW** | "
        f"**{stats.total_battery_kwh:,.0f} kWh** |\n"
    )
    out.append(
        f"Aggregate station-rail charging power: "
        f"**{stats.total_charging_kw:,.0f} kW**. Trains opportunity-charge "
        f"during station dwell per RFC 0002; onboard "
        f"{stats.consist_battery_kwh} kWh battery covers running.\n"
    )

    # Prefer the rust-emitted [costs] block (RFC 0011 §9 OSR-discipline
    # planning-grade CAPEX) over the rule-of-thumb per-unit calc — when
    # design.toml carries one, the CAPEX section is broken out by
    # archetype and references the design-discipline reasoning.
    rust_costs = design.get("costs")
    if rust_costs:
        out.extend(_rich_capex_section(design, rust_costs, stats))
        # Funding & affordability section — CAPEX funding stack, annual
        # OPEX estimate, ticket pricing anchored to country median
        # income. Reads `lib/templates/country-finance.toml`.
        out.extend(_funding_and_affordability_section(design, rust_costs, stats, rel))
        # Skip the per-unit fallback section below; jump to "## Files".
        return _finalise_readme(
            out, design_path, scenario_path, stats, screenshot_slug, rel
        )

    out.append("## Cost estimate\n")
    cost_link = rel("design-py/src/osr_scenario/network_readme.py")
    out.append(
        f"Rule-of-thumb unit rates (see [`CostAssumptions`]({cost_link}) "
        "to override per-country):\n"
    )
    out.append("| Component | Unit cost | Quantity | Estimate |")
    out.append("|---|---|---|---|")
    out.append(
        f"| Civil track (at-grade, double-track, radials) | "
        f"${cost.track_cost_per_km_usd / 1e6:.1f} M/km | "
        f"{at_grade_km:.1f} km "
        f"({(1 - cost.bridge_fraction) * 100:.0f} % of radial route) | "
        f"**${track_cost / 1e6:.1f} M** |"
    )
    out.append(
        f"| Bridges / viaducts on radials (river + highway crossings) | "
        f"${cost.bridge_cost_per_km_usd / 1e6:.1f} M/km | "
        f"{bridge_km_radials:.1f} km "
        f"({cost.bridge_fraction * 100:.0f} % of radial route) | "
        f"**${bridge_cost / 1e6:.1f} M** |"
    )
    if ring_km > 0:
        out.append(
            f"| Ring line (dedicated viaduct, straight across suburbs) | "
            f"${cost.bridge_cost_per_km_usd / 1e6:.1f} M/km | "
            f"{ring_km:.1f} km (100 % viaduct) | "
            f"**${ring_cost / 1e6:.1f} M** |"
        )
    out.append(
        f"| Solar PV (installed) | ${cost.solar_cost_per_w_usd:.2f}/W | "
        f"{stats.total_pv_kw:,.0f} kW | **${solar_cost / 1e6:.1f} M** |"
    )
    out.append(
        f"| Battery (power rating, "
        f"{stats.total_battery_kwh:,.0f} kWh ÷ "
        f"{cost.battery_discharge_hours:.0f} h) | "
        f"${cost.battery_cost_per_w_usd:.2f}/W | "
        f"{battery_kw_equiv:,.0f} kW | **${battery_cost / 1e6:.1f} M** |"
    )
    out.append(
        f"| Rolling stock ({total_trainsets} trainsets × "
        f"{stats.consist_cars} cars) | "
        f"${cost.train_car_cost_usd / 1e6:.1f} M/car | "
        f"{total_cars} cars | **${rolling_stock_cost / 1e6:.1f} M** |"
    )
    out.append(
        f"| Stations (civil + fit-out) | "
        f"${cost.station_cost_usd / 1e6:.1f} M/station | "
        f"{stats.unique_station_count} stations | "
        f"**${station_cost / 1e6:.1f} M** |"
    )
    out.append(
        f"| Depots | ${cost.depot_cost_usd / 1e6:.1f} M/depot | "
        f"{stats.depot_count} depots | "
        f"**${depot_cost / 1e6:.1f} M** |"
    )
    out.append(
        f"| **Total capex (planning-grade)** | | | "
        f"**${total_capex / 1e6:,.1f} M** |\n"
    )
    out.append(
        "**Exclusions:** signalling / OCC / comms / cybersecurity, "
        "land acquisition, contingency reserve (typically 15–25 % of "
        "the above), design + engineering fees, financing. The "
        "above is a planning-grade bracket for sizing and "
        "stakeholder conversations, not a bid-ready estimate.\n"
    )

    return _finalise_readme(
        out, design_path, scenario_path, stats, screenshot_slug, rel
    )


def _finalise_readme(
    out: list[str],
    design_path: Path,
    scenario_path: Path,
    stats: NetworkStats,
    screenshot_slug: str,
    rel,
) -> str:
    """Append the Files + Reproducibility tail and join. Shared between
    the rich `[costs]` path and the legacy per-unit fallback."""
    out.append("## Files\n")
    out.append("| File | Role |")
    out.append("|---|---|")
    out.append("| [`design.toml`](design.toml) | Authoritative design |")
    # Scenario lives alongside the design (post-scenarios/ folder
    # consolidation). Link by basename if so; otherwise fall back
    # to a repo-root-relative path.
    try:
        scen_rel = scenario_path.resolve().relative_to(
            design_path.parent.resolve()
        )
    except ValueError:
        scen_rel = Path(rel("scenarios", scenario_path.name))
    out.append(
        f"| [`{scenario_path.name}`]({scen_rel}) "
        "| Expanded simulation scenario (input to `osr-sim`) |"
    )
    out.append(
        f"| [`{screenshot_slug}-network-map.png`]"
        f"({screenshot_slug}-network-map.png) "
        "| Auto-fit network map (rendered by `osr_scenario.render_map`) |"
    )
    out.append(
        f"| [`{screenshot_slug}.corridor.geojson`]"
        f"({screenshot_slug}.corridor.geojson) "
        "| Line polylines + stations (GeoJSON) |"
    )
    out.append(
        f"| [`{screenshot_slug}.stations.json`]"
        f"({screenshot_slug}.stations.json) "
        "| Machine-readable station list |"
    )
    out.append(
        f"| [`{screenshot_slug}.design-quality.yaml`]"
        f"({screenshot_slug}.design-quality.yaml) "
        "| Coverage / anchor-hit / civil-mix metrics + auto-gate result |\n"
    )

    out.append("## Reproducibility\n")
    slug = stats.city_name.split(" ")[0].lower()
    out.append(
        f"```bash\n"
        f"# 1. raster bundle from OpenStreetMap (cached by query hash)\n"
        f"python -m osr_geo.cli --slug {slug}\n"
        f"\n"
        f"# 2. design.toml + corridor.geojson + design-quality.yaml\n"
        f"#    (population + country pulled from "
        f"lib/city-batches/world-sample.toml)\n"
        f"cargo run --release --bin osr-design -- --slug {slug} \\\n"
        f"    --sidecar .cache/osr-pipeline/rasters/{slug}.grid.json \\\n"
        f"    --out-dir designs/.../{stats.city_name}\n"
        f"\n"
        f"# 3. scenario.toml + map PNGs + this README\n"
        f"python -m osr_scenario --design designs/.../design.toml\n"
        f"python -m osr_scenario.render_map --design designs/.../design.toml\n"
        f"python -m osr_scenario.network_readme \\\n"
        f"    --design designs/.../design.toml \\\n"
        f"    --scenario designs/.../{slug}.toml \\\n"
        f"    --out designs/.../README.md\n"
        f"```\n"
        f"\n"
        f"`scripts/regenerate-{slug}.sh` chains steps 3 + drift tests "
        f"into a single command.\n"
    )

    return "\n".join(out)


# --------------------------------------------------------------------------
# Utils
# --------------------------------------------------------------------------


def _hours(start: str, end: str) -> float:
    """Service hours per day. Wraps past midnight (e.g. 05:30 → 02:00
    = 20.5 h, not -3.5 h)."""
    try:
        sh, sm = [int(x) for x in start.split(":")]
        eh, em = [int(x) for x in end.split(":")]
        delta = (eh * 60 + em) - (sh * 60 + sm)
        if delta <= 0:
            delta += 24 * 60
        return delta / 60.0
    except Exception:
        return 20.5


def _build_terminus_tagger(stations: list[dict]):
    """Returns a callable that maps a station id to a "<quadrant> <band>"
    label like "N Outer" or "SE Mid", computed from the network's
    geometric centroid.

    Replaces raw OSM `anchor_name` strings — which legitimately mix
    Arabic / English / Russian / Cyrillic / placeholder IDs depending
    on what the underlying OSM data happened to label each cell — with
    a script-neutral planning-grade label that's stable across
    networks. Operators get a tag they can read at a glance ("the line
    runs from the SE-mid suburbs to the N-outer terminus") without
    needing to read the local toponym.
    """
    import math

    by_id = {s["id"]: s for s in stations if "lat" in s and "lon" in s}
    if not by_id:
        return lambda sid: sid
    # Geometric centroid (simple mean of lat/lon — fine for any
    # network smaller than a few hundred km, where flat-earth error
    # is well below the band granularity).
    n = len(by_id)
    cx_lat = sum(float(s["lat"]) for s in by_id.values()) / n
    cx_lon = sum(float(s["lon"]) for s in by_id.values()) / n

    # Per-station distance from centroid (in degrees-equivalent —
    # we only need ratios for the band check).
    def _dist(s: dict) -> float:
        dlat = float(s["lat"]) - cx_lat
        # Cosine-correct longitudinal distance so the network's
        # bearing classification works at any latitude.
        dlon = (float(s["lon"]) - cx_lon) * math.cos(math.radians(cx_lat))
        return math.hypot(dlat, dlon)

    radii = {sid: _dist(s) for sid, s in by_id.items()}
    r_max = max(radii.values()) if radii else 1.0
    if r_max == 0.0:
        r_max = 1.0  # degenerate single-point network — avoid div-by-zero

    # 8-way compass binning from bearing (0° = north, increasing
    # clockwise). Bins are centered on each cardinal/intercardinal,
    # 45° wide.
    quadrants = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

    def _quadrant(s: dict) -> str:
        dlat = float(s["lat"]) - cx_lat
        dlon = (float(s["lon"]) - cx_lon) * math.cos(math.radians(cx_lat))
        if dlat == 0 and dlon == 0:
            return "Centre"
        # math.atan2(x, y) returns bearing-from-north when x = dlon (east)
        # and y = dlat (north). Result range -π..π.
        bearing = math.degrees(math.atan2(dlon, dlat))
        if bearing < 0:
            bearing += 360.0
        # Bin: rotate by half a bin so each cardinal is centred.
        idx = int(((bearing + 22.5) // 45) % 8)
        return quadrants[idx]

    def _band(sid: str) -> str:
        ratio = radii.get(sid, 0.0) / r_max
        if ratio < 0.33:
            return "Inner"
        if ratio < 0.67:
            return "Mid"
        return "Outer"

    def tag(sid: str) -> str:
        s = by_id.get(sid)
        if s is None:
            return sid
        q = _quadrant(s)
        if q == "Centre":
            return "Centre"
        return f"{q} {_band(sid)}"

    return tag


# Per-archetype unit costs — mirror of the constants in
# `crates/osr-design/src/emit.rs` (RFC 0011 §9 OSR-discipline costs).
# Keeping this table in sync with the rust source is part of the
# cost-discipline review. See the matching comment in emit.rs.
_STATION_UNIT_EUR: dict[str, float] = {
    "halt": 400_000.0,
    "standard": 1_500_000.0,
    "major": 3_000_000.0,
    "terminal": 2_500_000.0,
    "depot-terminal": 3_000_000.0,
    "interchange": 4_500_000.0,
    "interchange-elevated": 4_500_000.0,
}
_DEPOT_UNIT_EUR: dict[str, float] = {
    "main-heavy": 25_000_000.0,
    "secondary-medium": 10_000_000.0,
    "layup-minimal": 3_000_000.0,
}
_TRAINSET_UNIT_EUR: dict[str, float] = {
    "tram-2car": 1_200_000.0,
    "light-metro-3car": 2_000_000.0,
    "metro-4car": 3_000_000.0,
    "metro-6car": 4_500_000.0,
}
_AT_GRADE_EUR_PER_KM = 3_500_000.0
_ELEVATED_EUR_PER_KM = 18_000_000.0
_BRIDGE_EUR_PER_KM = 25_000_000.0
_JUNCTION_PREMIUM_EUR = 20_000_000.0
_SIGNALLING_EUR_PER_KM = 400_000.0
_POWER_EUR_PER_KM = 800_000.0
_EPC_OVERHEAD_FRAC = 0.07


def _rich_capex_section(
    design: dict, costs: dict, stats: NetworkStats
) -> list[str]:
    """Emit the per-archetype CAPEX breakdown sourced from
    `design.toml`'s `[costs]` block (rust `osr-design` planner).
    The rust emitter only writes subtotals; per-archetype rows are
    re-derived here from the station / depot / line tables and the
    unit-cost mirror above."""

    def _eur(v: float) -> str:
        if v >= 1e9:
            return f"€{v / 1e9:.2f} bn"
        return f"€{v / 1e6:.0f} M" if v >= 1e7 else f"€{v / 1e6:.1f} M"

    archetype_counts: dict[str, int] = {}
    for s in design.get("stations", []):
        a = s.get("archetype", "standard")
        archetype_counts[a] = archetype_counts.get(a, 0) + 1
    depot_counts: dict[str, int] = {}
    for d in design.get("depots", []):
        a = d.get("archetype", "main-heavy")
        depot_counts[a] = depot_counts.get(a, 0) + 1

    # Civil mix.
    at_grade_km = float(costs.get("at_grade_eur", 0.0)) / _AT_GRADE_EUR_PER_KM
    elevated_km = float(costs.get("elevated_eur", 0.0)) / _ELEVATED_EUR_PER_KM
    bridge_km = float(costs.get("bridge_eur", 0.0)) / _BRIDGE_EUR_PER_KM
    junction_count = int(
        round(
            float(costs.get("junction_premium_eur", 0.0)) / _JUNCTION_PREMIUM_EUR
        )
    ) if costs.get("junction_premium_eur") else 0

    family = (
        design.get("lines", [{}])[0].get("rolling_stock", "tram-2car")
    )
    fleet_total = stats.revenue_fleet + stats.spare_fleet + stats.reserve_fleet

    out: list[str] = []
    out.append("## CAPEX (planning grade)\n")
    out.append(
        "All figures come from the `[costs]` block in "
        "`design.toml` — emitted by the `osr-design` Rust planner per "
        "RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame "
        "canopies (no bespoke architectural cladding), at-grade depots "
        "without overhead bridge cranes, commodity Na-ion cells + "
        "tier-2 PMSM motors + DIY SiC inverters in rolling stock, "
        "open-source CBTC on commodity SBCs (no proprietary signalling "
        "vendor), no overhead catenary, and self-EPC overhead. "
        "Conventional metro budgets land 2–3× higher because of the "
        "line items OSR has architected away. `country-costs.toml` "
        "applies the per-country labour/material multiplier "
        "downstream.\n"
    )

    out.append("### Civil works\n")
    out.append("| Bucket | Value |")
    out.append("|---|---|")
    if at_grade_km > 0:
        out.append(
            f"| At-grade ({at_grade_km:.1f} km @ €3.5 M/km) | "
            f"{_eur(costs['at_grade_eur'])} |"
        )
    if elevated_km > 0:
        out.append(
            f"| Elevated ({elevated_km:.1f} km @ €18 M/km) | "
            f"{_eur(costs['elevated_eur'])} |"
        )
    if bridge_km > 0:
        out.append(
            f"| Bridges ({bridge_km:.1f} km @ €25 M/km) | "
            f"{_eur(costs['bridge_eur'])} |"
        )
    if junction_count > 0:
        out.append(
            f"| Elevated-interchange premium ({junction_count} sites @ €20 M) | "
            f"{_eur(costs['junction_premium_eur'])} |"
        )
    out.append(
        f"| **Civil subtotal** | **{_eur(costs['civil_subtotal_eur'])}** |\n"
    )

    out.append("### Stations\n")
    out.append(
        "Prefab portal-frame canopy + factory-bonded PV sandwich panel "
        "(RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, "
        "3–5 day erection). Precast L-unit platform edge. Vertical "
        "circulation per archetype.\n"
    )
    out.append("| Archetype | Count | Unit | Subtotal |")
    out.append("|---|---|---|---|")
    # Stable archetype order for output.
    arch_order = [
        "halt", "standard", "major", "terminal", "depot-terminal",
        "interchange", "interchange-elevated",
    ]
    for a in arch_order:
        n = archetype_counts.get(a, 0)
        if n == 0:
            continue
        unit = _STATION_UNIT_EUR.get(a, 1_500_000.0)
        out.append(
            f"| `{a}` | {n} | {_eur(unit)} | {_eur(unit * n)} |"
        )
    out.append(
        f"| **Stations subtotal** | | | **{_eur(costs['stations_eur'])}** |\n"
    )

    out.append("### Depots\n")
    out.append(
        "At-grade portal-frame workshop sheds; pit tracks with stinger "
        "+ portable wheel lathe (no overhead bridge crane); on-site PV "
        "array; Na-ion stationary storage; no traction substation.\n"
    )
    out.append("| Archetype | Count | Unit | Subtotal |")
    out.append("|---|---|---|---|")
    depot_order = ["main-heavy", "secondary-medium", "layup-minimal"]
    for a in depot_order:
        n = depot_counts.get(a, 0)
        if n == 0:
            continue
        unit = _DEPOT_UNIT_EUR.get(a, 8_000_000.0)
        out.append(
            f"| `{a}` | {n} | {_eur(unit)} | {_eur(unit * n)} |"
        )
    out.append(
        f"| **Depots subtotal** | | | **{_eur(costs['depots_eur'])}** |\n"
    )

    out.append("### Rolling stock\n")
    out.append(
        "Per-trainset BOM at OSR-discipline pricing: **onboard** Na-ion "
        "traction battery (~$80/kWh, RFC 0021 §3 — distinct from the "
        "trackside stationary battery in the *Systems* section below), "
        "tier-2 PMSM motors + SiC inverters (RFC 0022 §10, RFC 0008 §3.2), "
        "DIY safety electronics (~$5 680/trainset, RFC 0019), "
        "aluminium-extrusion or steel space-frame body. Motors and "
        "onboard batteries appear here ONLY — never re-billed elsewhere "
        "in the cost stack.\n"
    )
    out.append("| Item | Count | Unit | Subtotal |")
    out.append("|---|---|---|---|")
    rs_unit = _TRAINSET_UNIT_EUR.get(family, 2_000_000.0)
    out.append(
        f"| `{family}` (revenue + spare + cold reserve) | "
        f"{fleet_total} | {_eur(rs_unit)} | "
        f"{_eur(costs['rolling_stock_eur'])} |"
    )
    out.append("")

    out.append("### Systems\n")
    out.append("| Item | Basis | Subtotal |")
    out.append("|---|---|---|")
    out.append(
        f"| Signalling (open-source CBTC on commodity SBCs, RFC 0019) | "
        f"{stats.route_km:.1f} km × €0.4 M/km | "
        f"{_eur(costs['signalling_eur'])} |"
    )
    out.append(
        f"| Traction power (**trackside** stationary PV + Na-ion + grid-tie at every station, no OCS, RFC 0002 §6) | "
        f"{stats.route_km:.1f} km × €0.8 M/km | "
        f"{_eur(costs['power_eur'])} |"
    )
    out.append(
        f"| EPC integration + project management ({_EPC_OVERHEAD_FRAC:.0%}) | "
        f"on subtotal | {_eur(costs['epc_overhead_eur'])} |\n"
    )

    out.append("### Total\n")
    out.append("| Bucket | Value |")
    out.append("|---|---|")
    out.append(
        f"| Civil works | {_eur(costs['civil_subtotal_eur'])} |"
    )
    out.append(f"| Stations | {_eur(costs['stations_eur'])} |")
    out.append(f"| Depots | {_eur(costs['depots_eur'])} |")
    out.append(f"| Rolling stock | {_eur(costs['rolling_stock_eur'])} |")
    out.append(
        f"| Signalling + power | "
        f"{_eur(costs['signalling_eur'] + costs['power_eur'])} |"
    )
    out.append(
        f"| EPC overhead ({_EPC_OVERHEAD_FRAC:.0%}) | "
        f"{_eur(costs['epc_overhead_eur'])} |"
    )
    total = float(costs["total_eur"])
    out.append(f"| **CAPEX total** | **{_eur(total)}** |")
    if stats.route_km > 0:
        per_km = total / stats.route_km
        out.append(f"| Per-route-km | {_eur(per_km)} / km |")
    if stats.population > 0:
        per_capita = total / stats.population
        out.append(
            f"| Per-capita (city pop) | "
            f"€{per_capita:,.0f} / person |\n"
        )
    return out


def _rel_to_repo_root(path: Path) -> str:
    """Return the relative-path prefix from `path` up to the repo root
    (containing Cargo.toml). Used to fix up links in the generated
    README regardless of how deeply the design folder is nested.

    `enumerate(cur.parents)` counts the *number of `..` segments* to
    walk: depth 0 = immediate parent (one `..` up), depth 3 = great-
    great-grandparent (four `..` up). For a design at
    `designs/west-asia/Iraq/Samawah/`, the repo root is the 4th parent
    (depth 3) so we need `(depth + 1) = 4` dotdots to reach it.
    """
    cur = path.resolve()
    for depth, parent in enumerate(cur.parents):
        if (parent / "Cargo.toml").exists():
            return "/".join([".."] * (depth + 1))
    return ".."


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="osr_scenario.network_readme",
        description="Generate a per-network README.md from design.toml + scenario.toml.",
    )
    ap.add_argument("--design", type=Path, required=True)
    ap.add_argument("--scenario", type=Path, required=True)
    ap.add_argument(
        "--out", type=Path, required=True,
        help="output path (typically <design-folder>/README.md)",
    )
    ap.add_argument(
        "--population", type=int, default=None,
        help="urban population served (default: read from design.toml [city] population)",
    )
    ap.add_argument(
        "--track-cost-per-km", type=float, default=2_000_000.0,
        help="civil track unit cost, USD/km (default: 2,000,000)",
    )
    ap.add_argument(
        "--solar-cost-per-w", type=float, default=1.0,
        help="solar PV unit cost, USD/W (default: 1.00)",
    )
    ap.add_argument(
        "--battery-cost-per-w", type=float, default=1.0,
        help="battery unit cost, USD/W at rated discharge power (default: 1.00)",
    )
    ap.add_argument(
        "--battery-hours", type=float, default=4.0,
        help="BESS discharge duration, hours (default: 4)",
    )
    ap.add_argument(
        "--train-car-cost", type=float, default=1_000_000.0,
        help="rolling-stock unit cost, USD per CAR (default: 1,000,000). "
             "A 3-car trainset costs 3 × this.",
    )
    ap.add_argument(
        "--station-cost", type=float, default=1_000_000.0,
        help="civil+fit-out unit cost, USD/station (default: 1,000,000)",
    )
    ap.add_argument(
        "--depot-cost", type=float, default=5_000_000.0,
        help="per-depot unit cost, USD/depot (default: 5,000,000)",
    )
    ap.add_argument(
        "--pax-per-trainset", type=int, default=None,
        help=(
            "passenger capacity per trainset (default: read from "
            "lib/templates/rolling-stock.toml for the design's "
            "rolling_stock family — 220 for tram-2car, 360 for "
            "light-metro-3car, 540 for metro-4car, 900 for metro-6car). "
            "Pass an integer here only for what-if analysis."
        ),
    )
    args = ap.parse_args(argv)

    cost = CostAssumptions(
        track_cost_per_km_usd=args.track_cost_per_km,
        solar_cost_per_w_usd=args.solar_cost_per_w,
        battery_cost_per_w_usd=args.battery_cost_per_w,
        battery_discharge_hours=args.battery_hours,
        train_car_cost_usd=args.train_car_cost,
        station_cost_usd=args.station_cost,
        depot_cost_usd=args.depot_cost,
        trainset_capacity_pax=args.pax_per_trainset,
    )
    population = args.population
    if population is None:
        # Fall back to `[city] population` in the design.toml. Older
        # designs without that field require an explicit --population.
        try:
            doc = tomllib.loads(args.design.read_text())
            population = int(doc.get("city", {}).get("population", 0))
        except Exception:
            population = 0
        if not population:
            print(
                "error: --population is required (no [city] population "
                "field in the design.toml)",
                file=sys.stderr,
            )
            return 2
    text = render_readme(
        design_path=args.design,
        scenario_path=args.scenario,
        population=population,
        cost=cost,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text)
    print(f"wrote {args.out}  ({len(text.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
