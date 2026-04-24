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
    trainset_capacity_pax: int = 200  # 3-car light-metro crush + seated


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


def _load(path: Path) -> dict:
    return tomllib.loads(Path(path).read_text())


def _line_length_km(design_line: dict) -> float:
    return (
        sum(s.get("distance_from_prev_m", 0) for s in design_line.get("stations", []))
        / 1000.0
    )


def compute_stats(
    design: dict, scenario: dict, population: int
) -> NetworkStats:
    loc = design.get("location", {})
    city_name = loc.get("city") or design.get("design", {}).get("name", "Network")
    country_iso = loc.get("country", "??")

    lines = design.get("lines", [])
    line_count = len(lines)
    route_km = round(sum(_line_length_km(L) for L in lines), 1)
    unique_stations = {s["id"] for s in design.get("stations", [])}
    interchange_count = sum(
        1 for s in design.get("stations", [])
        if s.get("archetype") == "interchange"
    )

    # Transfer reachability.
    transfer = _transfer_reachability(lines)

    # Coverage — prefer a `[stats] coverage=` hint in design.toml;
    # otherwise fall back to "unknown" (0.0) and let the caller
    # provide it out-of-band.
    coverage = float(design.get("stats", {}).get("coverage", 0.0))

    # Fleet.
    revenue = sum(int(f.get("trainset_count", 0)) for f in design.get("fleets", []))
    spare = sum(int(f.get("spare_count", 0)) for f in design.get("fleets", []))
    reserve = sum(
        int(f.get("cold_reserve_count", 0)) for f in design.get("fleets", [])
    )
    if spare + reserve == 0:
        # Apply the template default (50 % spare+reserve).
        spare = revenue // 3
        reserve = revenue // 4

    # Peak headway (from the scenario's timetable section, if present).
    peak_headway_min = 5.0
    for sec in scenario.get("timetable", {}).get("sections", []):
        if sec.get("name", "").lower() in ("peak", "am-peak", "pm-peak"):
            peak_headway_min = min(peak_headway_min, float(sec.get("headway_min", 5.0)))

    service_hours = scenario.get("timetable", {}).get(
        "service_hours", "05:30-23:30"
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
        service_end=service_end.strip() or "23:30",
        total_pv_kw=total_pv,
        total_battery_kwh=total_batt,
        total_charging_kw=total_charging,
        consist_cars=int(consist.get("car_count", 3)),
        consist_length_m=int(consist.get("length_m", 68)),
        consist_battery_kwh=int(consist.get("battery_capacity_kwh", 320)),
        consist_max_speed_kmh=float(consist.get("max_speed_kmh", 80)),
        depot_count=len(design.get("depots", [])),
    )


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
    stats = compute_stats(design, scenario, population)

    screenshot_slug = screenshot_slug or (
        design.get("design", {}).get("id", "city").rsplit("/", 1)[-1].lower()
    )

    # Compute how many `..` to climb from the README's folder to repo root.
    rel_to_root = _rel_to_repo_root(design_path.parent)

    # Relative paths from the README's folder into the repo tree.
    def rel(*parts: str) -> str:
        return "/".join([rel_to_root, *parts]) if rel_to_root else "/".join(parts)

    # Ridership capacity.
    trains_per_hour_per_dir = 60 / stats.peak_headway_min
    per_line_pphpd = stats.trainset_capacity_pax if False else (
        cost.trainset_capacity_pax * trains_per_hour_per_dir
    )
    network_peak_per_h = per_line_pphpd * stats.line_count * 2
    daily_theoretical = network_peak_per_h * 10  # peak≈10% of daily
    catchment = int(stats.coverage * stats.population) if stats.coverage > 0 else None
    practical_daily_low = int((catchment or stats.population) * 0.10) if catchment else None
    practical_daily_high = int((catchment or stats.population) * 0.15) if catchment else None

    # Cost.
    track_cost = cost.track_cost_per_km_usd * stats.route_km
    solar_cost = cost.solar_cost_per_w_usd * stats.total_pv_kw * 1_000
    battery_kw_equiv = stats.total_battery_kwh / cost.battery_discharge_hours
    battery_cost = cost.battery_cost_per_w_usd * battery_kw_equiv * 1_000
    total_trainsets = stats.revenue_fleet + stats.spare_fleet + stats.reserve_fleet
    total_cars = total_trainsets * stats.consist_cars
    rolling_stock_cost = cost.train_car_cost_usd * total_cars
    station_cost = cost.station_cost_usd * stats.unique_station_count
    depot_cost = cost.depot_cost_usd * stats.depot_count
    total_capex = (
        track_cost + solar_cost + battery_cost
        + rolling_stock_cost + station_cost + depot_cost
    )

    # Per-line table.
    by_id = {s["id"]: s for s in design.get("stations", [])}
    fleet_by_line = {
        f["line"]: int(f.get("trainset_count", 0))
        for f in design.get("fleets", [])
    }
    line_rows: list[str] = []
    for L in design.get("lines", []):
        length_km = _line_length_km(L)
        station_ids = [s["id"] for s in L.get("stations", [])]
        first = by_id.get(station_ids[0], {}).get("name", station_ids[0]) if station_ids else ""
        last = by_id.get(station_ids[-1], {}).get("name", station_ids[-1]) if station_ids else ""
        trainsets = fleet_by_line.get(L["id"], 0)
        line_rows.append(
            f"| {L.get('name', L['id'])} | {length_km:4.1f} km | "
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
    coverage_str = f"{stats.coverage:.1%}" if stats.coverage > 0 else "— (set `[stats] coverage` in design.toml)"
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
        "Auto-planned by [`osr_planner`]("
        f"{rel('design-py/src/osr_planner/')}) using the linear-logic "
        "algorithm on Overpass-verified OpenStreetMap data. Every "
        "station sits on an aggregated POI cluster; every line "
        "polyline follows the OSM arterial graph "
        "(trunk / primary / secondary / tertiary — residential "
        "streets excluded, so lines cannot zigzag through a "
        "residential grid).\n"
    )

    out.append("## Network map\n")
    out.append(
        f"![{stats.city_name} rail network auto-planned by osr_planner]"
        f"({rel('docs/screenshots', f'{screenshot_slug}-network-map.png')})\n"
    )
    out.append(
        f"*Detail-zoom render: "
        f"[`{screenshot_slug}-network-map-detail.png`]"
        f"({rel('docs/screenshots', f'{screenshot_slug}-network-map-detail.png')}). "
        "Corridor GeoJSON for GIS / alignment tooling: "
        f"[`{screenshot_slug}-corridor.geojson`]"
        f"({rel('docs/screenshots', f'{screenshot_slug}-corridor.geojson')}).*\n"
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
    out.append("| Line | Length | Stations | Trainsets | Termini |")
    out.append("|---|---|---|---|---|")
    out.extend(line_rows)
    out.append(
        f"| **Total** | **{stats.route_km:.1f} km** | "
        f"**{stats.unique_station_count} unique** | "
        f"**{stats.revenue_fleet}** | |\n"
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
    out.append(f"| Nominal capacity | {cost.trainset_capacity_pax} pax (seated + standing) |\n")

    out.append("## Ridership capacity\n")
    out.append(
        f"- **Per-train capacity:** {cost.trainset_capacity_pax} passengers"
    )
    out.append(
        f"- **Peak frequency:** {trains_per_hour_per_dir:.0f} trains/hour/direction "
        f"({stats.peak_headway_min:.0f}-min headway)"
    )
    out.append(
        f"- **Peak capacity per line per direction:** "
        f"{cost.trainset_capacity_pax} × {trains_per_hour_per_dir:.0f} "
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

    out.append("## Cost estimate\n")
    out.append(
        "Rule-of-thumb unit rates (see [`CostAssumptions`]"
        "(../../../design-py/src/osr_scenario/network_readme.py) to "
        "override per-country):\n"
    )
    out.append("| Component | Unit cost | Quantity | Estimate |")
    out.append("|---|---|---|---|")
    out.append(
        f"| Civil track (double-track) | "
        f"${cost.track_cost_per_km_usd / 1e6:.1f} M/km | "
        f"{stats.route_km:.1f} km | **${track_cost / 1e6:.1f} M** |"
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
        f"({rel('docs/screenshots', f'{screenshot_slug}-network-map.png')}) "
        "| City-wide network map |"
    )
    out.append(
        f"| [`{screenshot_slug}-network-map-detail.png`]"
        f"({rel('docs/screenshots', f'{screenshot_slug}-network-map-detail.png')}) "
        "| Detail-zoom render |"
    )
    out.append(
        f"| [`{screenshot_slug}-corridor.geojson`]"
        f"({rel('docs/screenshots', f'{screenshot_slug}-corridor.geojson')}) "
        "| Line polylines + stations (GeoJSON) |\n"
    )

    out.append("## Reproducibility\n")
    out.append(
        "Run `python -m osr_planner --slug <slug> --bbox ... --population ...` "
        "to re-plan, then `python -m osr_scenario --design …/design.toml` + "
        "`python -m osr_scenario.render_map --design …/design.toml` + "
        "`python -m osr_scenario.network_readme --design …/design.toml "
        "--scenario …/scenario.toml --out …/README.md --population N` to "
        "regenerate this README.\n"
    )

    return "\n".join(out)


# --------------------------------------------------------------------------
# Utils
# --------------------------------------------------------------------------


def _hours(start: str, end: str) -> float:
    try:
        sh, sm = [int(x) for x in start.split(":")]
        eh, em = [int(x) for x in end.split(":")]
        return (eh * 60 + em - sh * 60 - sm) / 60.0
    except Exception:
        return 18.0


def _rel_to_repo_root(path: Path) -> str:
    """Return the relative-path prefix from `path` up to the repo root
    (containing Cargo.toml). Used to fix up links in the generated
    README regardless of how deeply the design folder is nested."""
    cur = path.resolve()
    for depth, parent in enumerate(cur.parents):
        if (parent / "Cargo.toml").exists():
            return "/".join([".."] * depth) if depth else ""
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
        "--population", type=int, required=True,
        help="urban population served (used for catchment estimates)",
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
        "--pax-per-trainset", type=int, default=200,
        help="passenger capacity per trainset (default: 200)",
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
    text = render_readme(
        design_path=args.design,
        scenario_path=args.scenario,
        population=args.population,
        cost=cost,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text)
    print(f"wrote {args.out}  ({len(text.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
