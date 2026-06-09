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
- Cost estimate at configurable unit rates from the canonical CAPEX table
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
import math
import sys
import tomllib
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path


# --------------------------------------------------------------------------
# Cost + capacity assumptions
# --------------------------------------------------------------------------

@lru_cache(maxsize=None)
def _template_toml(filename: str) -> dict:
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "lib/templates" / filename
        if candidate.exists():
            return tomllib.loads(candidate.read_text())
    raise FileNotFoundError(f"lib/templates/{filename} not found")


def _capex_costs() -> dict:
    return _template_toml("capex-costs.toml")


def _demand_profiles() -> dict:
    return _template_toml("demand-profiles.toml")


def _float_map(table: dict) -> dict[str, float]:
    return {str(k): float(v) for k, v in table.items()}


_CAPEX_COSTS = _capex_costs()
_DEMAND_PROFILES = _demand_profiles()
_RIDERSHIP_PLANNING = _DEMAND_PROFILES["planning"]
_USD_TO_EUR = float(_CAPEX_COSTS["schema"]["usd_to_eur"])
_EUR_TO_USD = 1.0 / _USD_TO_EUR
_STATION_UNIT_USD = _float_map(_CAPEX_COSTS["station_unit_usd"])
_DEPOT_UNIT_USD = _float_map(_CAPEX_COSTS["depot_unit_usd"])
_TRAINSET_UNIT_USD = _float_map(_CAPEX_COSTS["trainset_unit_usd"])
_PRODUCTION_PLANT_PER_VEHICLE_USD = float(
    _CAPEX_COSTS["production_plant"]["per_vehicle_usd"]
)
_PRODUCTION_PLANT_HIGH_PER_VEHICLE_USD = float(
    _CAPEX_COSTS["production_plant"].get(
        "high_sensitivity_per_vehicle_usd",
        _PRODUCTION_PLANT_PER_VEHICLE_USD,
    )
)
_SOLAR_PLANT = _CAPEX_COSTS["solar_power_plant"]
_SOLAR_PLANT_UTILITY_USD_PER_KW = float(_SOLAR_PLANT["utility_pv_usd_per_kw"])
_SOLAR_PLANT_INTERCONNECTION_USD_PER_KW = float(
    _SOLAR_PLANT["interconnection_usd_per_kw"]
)
_SOLAR_PLANT_COVERAGE_MARGIN = float(_SOLAR_PLANT["coverage_margin"])
_SOLAR_PLANT_MAINT_FRAC = float(_SOLAR_PLANT["annual_maintenance_fraction"])
_CIVIL_USD_PER_KM = _float_map(_CAPEX_COSTS["civil_usd_per_km"])
_AT_GRADE_USD_PER_KM = _CIVIL_USD_PER_KM["at_grade"]
_ELEVATED_USD_PER_KM = _CIVIL_USD_PER_KM["elevated"]
_BRIDGE_USD_PER_KM = _CIVIL_USD_PER_KM["bridge"]
_DEFAULT_TRAIN_CAR_USD = _TRAINSET_UNIT_USD["urban-shuttle-1car"]
_DEFAULT_STATION_USD = _STATION_UNIT_USD["standard"]
_DEFAULT_DEPOT_USD = _DEPOT_UNIT_USD["main-heavy"]
_JUNCTION_PREMIUM_USD = float(
    _CAPEX_COSTS["junctions"]["elevated_interchange_premium_usd"]
)
_SIGNALLING_USD_PER_KM = float(
    _CAPEX_COSTS["systems"]["signalling_usd_per_km"]
)
_CHARGING_MICROGRID_UNIT_USD = _float_map(
    _CAPEX_COSTS["charging_microgrid_unit_usd"]
)
_EPC_OVERHEAD_FRAC = float(_CAPEX_COSTS["overhead"]["epc_fraction"])
_DAILY_RIDERSHIP_CATCHMENT_LOW = float(
    _RIDERSHIP_PLANNING["daily_ridership_catchment_low"]
)
_DAILY_RIDERSHIP_CATCHMENT_HIGH = float(
    _RIDERSHIP_PLANNING["daily_ridership_catchment_high"]
)
_DAILY_RIDERSHIP_POPULATION_FALLBACK_LOW = float(
    _RIDERSHIP_PLANNING["daily_ridership_population_fallback_low"]
)
_DAILY_RIDERSHIP_POPULATION_FALLBACK_HIGH = float(
    _RIDERSHIP_PLANNING["daily_ridership_population_fallback_high"]
)
_PAID_TRIPS_PER_DAILY_RIDER = float(
    _RIDERSHIP_PLANNING.get("paid_trips_per_daily_rider", 2.0)
)
_PRACTICAL_CAPACITY_LOAD_FACTOR = float(
    _RIDERSHIP_PLANNING["practical_capacity_load_factor"]
)


def _family_car_count(family: str) -> int:
    return {
        "urban-shuttle-1car": 1,
        "tram-2car": 2,
        "light-metro-3car": 3,
        "metro-4car": 4,
        "metro-6car": 6,
    }.get(family, 3)


def _pct_range(low: float, high: float) -> str:
    return f"{low * 100:.0f}-{high * 100:.0f}%"


@dataclass
class CostAssumptions:
    """Rule-of-thumb unit rates. Override for a city/country-specific
    estimate (Iraqi labour/materials differ from, say, French ones)."""

    track_cost_per_km_usd: float = field(
        default_factory=lambda: _AT_GRADE_USD_PER_KM
    )
    solar_cost_per_w_usd: float = 1.0
    battery_cost_per_w_usd: float = 1.0
    battery_discharge_hours: float = 4.0  # BESS typical 4-hour duration
    train_car_cost_usd: float = field(
        default_factory=lambda: _DEFAULT_TRAIN_CAR_USD
    )
    station_cost_usd: float = field(
        default_factory=lambda: _DEFAULT_STATION_USD
    )
    depot_cost_usd: float = field(
        default_factory=lambda: _DEFAULT_DEPOT_USD
    )
    # Bridges/viaducts run above the at-grade fallback. This
    # fraction of the total route is assumed to be elevated — river
    # crossings, highway overpasses, urban-core RoW constraints.
    bridge_fraction: float = 0.15
    bridge_cost_per_km_usd: float = field(
        default_factory=lambda: _BRIDGE_USD_PER_KM
    )
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
    trainset_seats: int
    trainset_crush_capacity_pax: int


@dataclass(frozen=True)
class EnergyPlan:
    service_days_per_year: int
    service_hours_per_day: float
    peak_sun_hours: float
    scheduled_daily_train_km: float
    annual_train_km: float
    annual_car_km: float
    annual_energy_kwh: float
    onsite_pv_kwh: float
    pre_plant_grid_import_kwh: float
    solar_plant_kw: float
    solar_plant_generation_kwh: float
    residual_grid_import_kwh: float
    solar_plant_capex_usd: float
    solar_plant_maintenance_usd: float
    train_km_basis: str


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

    # Peak headway (from generated fleet schedules, with older timetable
    # sections retained for back-compat).
    peak_headway_min = float("inf")
    for fleet in scenario.get("fleets", []):
        for window in fleet.get("schedule", []):
            peak_headway_min = min(
                peak_headway_min,
                float(window.get("headway_min", peak_headway_min)),
            )
    for sec in scenario.get("timetable", {}).get("sections", []):
        if sec.get("name", "").lower() in ("peak", "am-peak", "pm-peak"):
            peak_headway_min = min(
                peak_headway_min,
                float(sec.get("headway_min", peak_headway_min)),
            )
    if peak_headway_min == float("inf"):
        peak_headway_min = 3.0

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
    profile = _trainset_profile_for_family(family)
    capacity_pax = int(profile["passenger_capacity"])

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
        trainset_seats=int(profile["seat_count"]),
        trainset_crush_capacity_pax=int(profile["crush_capacity"]),
        depot_count=len(design.get("depots", [])),
    )


_FAMILY_CAPACITY_FALLBACK: dict[str, int] = {
    "urban-shuttle-1car": 100,
    "tram-2car": 240,
    "light-metro-3car": 360,
    "metro-4car": 480,
    "metro-6car": 720,
}

_FAMILY_SEATS_FALLBACK: dict[str, int] = {
    "urban-shuttle-1car": 20,
    "tram-2car": 40,
    "light-metro-3car": 60,
    "metro-4car": 80,
    "metro-6car": 120,
}

_FAMILY_CRUSH_FALLBACK: dict[str, int] = {
    "urban-shuttle-1car": 130,
    "tram-2car": 320,
    "light-metro-3car": 480,
    "metro-4car": 640,
    "metro-6car": 960,
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
                defaults = dict(table.get("XX", {}))
                if country.upper() in table:
                    defaults.update(table[country.upper()])
                return defaults
            except Exception:
                break
            break
    return {}


@dataclass(frozen=True)
class FundingStack:
    grant_frac: float
    multi_frac: float
    bond_frac: float
    equity_frac: float
    multi_rate: float
    bond_rate: float
    tenor: int
    grace: int


def _funding_stack(fin: dict) -> FundingStack:
    """Debt-light default finance stack for generated city reports.

    The previous model borrowed 85 % of CAPEX, including 25 % at sovereign
    bond rates. That made government debt-service figures dominate the
    README. The default here reflects the target OSR deployment posture:
    treat climate/development grants as the first source of capital, keep
    the bond market as a fallback only, and make the repayable portion a
    long-tenor concessional facility.
    """

    def _frac(key: str, default: float) -> float:
        return max(0.0, float(fin.get(key, default)))

    grant = _frac("climate_development_grant_share", 0.40)
    multi = _frac("multilateral_loan_share", 0.50)
    bond = _frac("sovereign_bond_share", 0.00)
    equity = _frac(
        "government_equity_share",
        max(0.0, 1.0 - grant - multi - bond),
    )
    total = grant + multi + bond + equity
    if total <= 0.0:
        grant, multi, bond, equity = 0.40, 0.50, 0.00, 0.10
        total = 1.0
    grant, multi, bond, equity = (
        grant / total,
        multi / total,
        bond / total,
        equity / total,
    )

    base_multi_rate = float(fin.get("multilateral_loan_rate", 0.045))
    climate_rate = float(fin.get("green_concessional_loan_rate", 0.020))
    multi_rate = min(base_multi_rate, climate_rate)
    bond_rate = float(fin.get("sovereign_bond_rate", 0.07))

    tenor = int(
        fin.get(
            "concessional_loan_tenor_years",
            max(int(fin.get("loan_tenor_years", 25)), 40),
        )
    )
    grace = int(fin.get("capex_grace_years", 5))
    tenor = max(tenor, 1)
    grace = min(max(grace, 0), tenor - 1)

    return FundingStack(
        grant_frac=grant,
        multi_frac=multi,
        bond_frac=bond,
        equity_frac=equity,
        multi_rate=multi_rate,
        bond_rate=bond_rate,
        tenor=tenor,
        grace=grace,
    )


def _station_commercial_revenue_eur(
    design: dict, monthly_income_usd: float
) -> dict[str, float]:
    """Annual station retail + ad revenue, returned in EUR.

    The rates deliberately scale from the same country-income table as
    fares: higher-income cities can sustain higher kiosk rents and
    advertising CPMs, while lower-income deployments keep rents low
    enough for local operators.
    """
    retail_program = {
        "halt": (1, 8.0),
        "standard": (4, 18.0),
        "major": (10, 20.0),
        "terminal": (8, 24.0),
        "depot-terminal": (6, 20.0),
        "interchange": (14, 24.0),
        "interchange-elevated": (16, 24.0),
    }
    ad_board_program = {
        "halt": 4,
        "standard": 16,
        "major": 36,
        "terminal": 40,
        "depot-terminal": 28,
        "interchange": 56,
        "interchange-elevated": 64,
    }
    rentable_sqm = 0.0
    ad_boards = 0
    for station in design.get("stations", []):
        archetype = station.get("archetype", "standard")
        shops, sqm_each = retail_program.get(archetype, retail_program["standard"])
        rentable_sqm += shops * sqm_each
        ad_boards += ad_board_program.get(archetype, ad_board_program["standard"])

    retail_rent_usd_m2_month = max(10.0, min(90.0, monthly_income_usd * 0.08))
    ad_board_usd_month = max(75.0, min(1_200.0, monthly_income_usd * 0.70))
    retail_occupancy = 0.88
    ad_occupancy = 0.85

    retail_usd = rentable_sqm * retail_rent_usd_m2_month * 12 * retail_occupancy
    ads_usd = ad_boards * ad_board_usd_month * 12 * ad_occupancy
    return {
        "rentable_sqm": rentable_sqm,
        "ad_boards": float(ad_boards),
        "retail_rent_usd_m2_month": retail_rent_usd_m2_month,
        "ad_board_usd_month": ad_board_usd_month,
        "retail_eur": retail_usd * _USD_TO_EUR,
        "ads_eur": ads_usd * _USD_TO_EUR,
        "total_eur": (retail_usd + ads_usd) * _USD_TO_EUR,
    }


_ENERGY_KWH_PER_CAR_KM = 4.0
_NON_REVENUE_TRAIN_KM_FACTOR = 1.08


def _scheduled_daily_train_km(design: dict, scenario: dict) -> float:
    """Daily train-km from the generated fleet schedules.

    Each schedule window is interpreted as departures per direction;
    train-km is therefore one-way line length × departures × 2 directions.
    """
    line_km = {
        str(line.get("name") or line.get("id")): _line_length_km(line)
        for line in design.get("lines", [])
    }
    daily_train_km = 0.0
    for fleet in scenario.get("fleets", []):
        length_km = line_km.get(str(fleet.get("line")))
        if not length_km:
            continue
        trips_per_direction = 0.0
        for window in fleet.get("schedule", []):
            headway = float(window.get("headway_min", 0.0))
            if headway <= 0.0:
                continue
            trips_per_direction += (
                _hours(str(window.get("from", "05:30")), str(window.get("to", "02:00")))
                * 60.0
                / headway
            )
        daily_train_km += length_km * trips_per_direction * 2.0
    return daily_train_km


def _station_posts_per_shift(design: dict) -> float:
    """Driverless-platform staff posts per shift by station archetype."""
    weights = {
        "halt": 0.25,
        "standard": 0.50,
        "major": 1.00,
        "terminal": 1.00,
        "depot-terminal": 1.50,
        "interchange": 2.00,
        "interchange-elevated": 2.00,
    }
    return sum(
        weights.get(str(station.get("archetype", "standard")), 0.50)
        for station in design.get("stations", [])
    )


def _driverless_workforce_breakdown(
    *,
    design: dict,
    stats: NetworkStats,
    service_hours_per_day: float,
    total_trainsets: int,
    annual_train_km: float,
    daily_paid_trips_high: int,
) -> dict[str, int]:
    """Deployment workforce that scales with service intensity.

    No train drivers are counted: RFC 0015 moves safety presence to OCC,
    remote-assist, platform/station, and maintenance roles.
    """
    shifts_per_day = max(1, math.ceil(service_hours_per_day / 8.0))
    roster_relief = 1.35
    remote_assist_posts = max(1, math.ceil(stats.revenue_fleet / 8))
    occ_posts = stats.line_count + remote_assist_posts + 2
    station_posts = _station_posts_per_shift(design)

    return {
        "occ_remote_assist": math.ceil(occ_posts * shifts_per_day * roster_relief),
        "station_platform": math.ceil(station_posts * shifts_per_day * roster_relief),
        "passenger_service": math.ceil(
            (stats.line_count * 4 * roster_relief)
            + (daily_paid_trips_high / 10_000)
        ),
        "fleet_maintenance": math.ceil(
            (total_trainsets * 0.30)
            + (annual_train_km / 300_000)
        ),
        "infrastructure_energy": math.ceil(
            (stats.route_km * 0.65)
            + (stats.unique_station_count * 0.35)
            + (stats.depot_count * 4)
        ),
        "admin_training": math.ceil(
            12 + stats.line_count * 2 + stats.depot_count * 3
        ),
    }


def _energy_plan(design: dict, scenario: dict, stats: NetworkStats) -> EnergyPlan:
    """Timetable-derived traction energy plan, including supplemental solar.

    On-site station/depot PV is counted first. If the generated timetable
    still has an annual traction-energy shortfall, a dedicated utility-scale
    solar plant (or contracted offsite PPA asset) is sized as infrastructure
    with a planning reserve margin.
    """
    service_days_per_year = 365
    service_hours_per_day = _hours(stats.service_start, stats.service_end)
    peak_sun_hours = float(scenario.get("climate", {}).get("peak_sun_hours", 5.0))
    commercial_speed_kmh = {
        "tram-2car": 22.0,
        "light-metro-3car": 30.0,
        "metro-4car": 35.0,
        "metro-6car": 35.0,
    }.get(stats.consist_family, 30.0)

    scheduled_daily_train_km = _scheduled_daily_train_km(design, scenario)
    if scheduled_daily_train_km > 0.0:
        annual_train_km = (
            scheduled_daily_train_km
            * service_days_per_year
            * _NON_REVENUE_TRAIN_KM_FACTOR
        )
        train_km_basis = (
            f"{scheduled_daily_train_km:,.0f} scheduled train-km/day × "
            f"{service_days_per_year} d/yr × "
            f"{_NON_REVENUE_TRAIN_KM_FACTOR:.0%} depot/deadhead factor"
        )
    else:
        utilisation_factor = 0.75
        annual_train_km = (
            stats.revenue_fleet
            * service_hours_per_day
            * service_days_per_year
            * commercial_speed_kmh
            * utilisation_factor
        )
        scheduled_daily_train_km = annual_train_km / service_days_per_year
        train_km_basis = (
            f"{stats.revenue_fleet} trainsets × {service_hours_per_day:.1f} h/day "
            f"× {commercial_speed_kmh:.0f} km/h × {utilisation_factor:.0%} "
            "utilisation fallback"
        )

    annual_car_km = annual_train_km * stats.consist_cars
    annual_energy_kwh = annual_car_km * _ENERGY_KWH_PER_CAR_KM
    onsite_pv_kwh = stats.total_pv_kw * peak_sun_hours * service_days_per_year
    pre_plant_grid_import_kwh = max(0.0, annual_energy_kwh - onsite_pv_kwh)

    solar_plant_kw = 0.0
    if pre_plant_grid_import_kwh > 0.0 and peak_sun_hours > 0.0:
        solar_plant_kw = (
            pre_plant_grid_import_kwh
            / (peak_sun_hours * service_days_per_year)
            * _SOLAR_PLANT_COVERAGE_MARGIN
        )
    solar_plant_generation_kwh = solar_plant_kw * peak_sun_hours * service_days_per_year
    residual_grid_import_kwh = max(
        0.0,
        annual_energy_kwh - onsite_pv_kwh - solar_plant_generation_kwh,
    )
    solar_plant_unit_usd_per_kw = (
        _SOLAR_PLANT_UTILITY_USD_PER_KW
        + _SOLAR_PLANT_INTERCONNECTION_USD_PER_KW
    )
    solar_plant_capex_usd = solar_plant_kw * solar_plant_unit_usd_per_kw
    solar_plant_maintenance_usd = solar_plant_capex_usd * _SOLAR_PLANT_MAINT_FRAC

    return EnergyPlan(
        service_days_per_year=service_days_per_year,
        service_hours_per_day=service_hours_per_day,
        peak_sun_hours=peak_sun_hours,
        scheduled_daily_train_km=scheduled_daily_train_km,
        annual_train_km=annual_train_km,
        annual_car_km=annual_car_km,
        annual_energy_kwh=annual_energy_kwh,
        onsite_pv_kwh=onsite_pv_kwh,
        pre_plant_grid_import_kwh=pre_plant_grid_import_kwh,
        solar_plant_kw=solar_plant_kw,
        solar_plant_generation_kwh=solar_plant_generation_kwh,
        residual_grid_import_kwh=residual_grid_import_kwh,
        solar_plant_capex_usd=solar_plant_capex_usd,
        solar_plant_maintenance_usd=solar_plant_maintenance_usd,
        train_km_basis=train_km_basis,
    )


def _funding_and_affordability_section(
    design: dict,
    scenario: dict,
    costs: dict,
    stats: NetworkStats,
    energy_plan: EnergyPlan,
    rel,
    *,
    daily_active_low: int,
    daily_active_high: int,
    daily_pax_low: int,
    daily_pax_high: int,
    ridership_basis_label: str,
    ridership_basis_population: int,
    ridership_low_share: float,
    ridership_high_share: float,
    paid_trips_per_daily_rider: float,
    practical_daily_capacity: int,
) -> list[str]:
    """Emit the `## Funding & affordability` section: grant-first CAPEX
    funding stack, annual OPEX, ticket pricing anchored to median income,
    and farebox-recovery shortfall.

    Pure function of the costs block + country-finance config — no
    network calls. Designed so any new city listed in
    `lib/city-batches/world-sample.toml` automatically gets a finance
    section without code changes.
    """
    fin = _load_country_finance(stats.country_iso)
    if not fin:
        return []

    base_total_eur = float(costs.get("total_eur", 0.0))
    if base_total_eur <= 0:
        return []
    solar_plant_eur = energy_plan.solar_plant_capex_usd * _USD_TO_EUR
    total_eur = base_total_eur + solar_plant_eur

    # Funding stack — grant-first and concessional-debt-heavy. The older
    # three-tranche default borrowed 85 % of CAPEX, including a large
    # sovereign-bond slice; that made government interest repayment dominate
    # otherwise affordable OSR deployments.
    stack = _funding_stack(fin)
    grant_frac = stack.grant_frac
    multi_frac = stack.multi_frac
    bond_frac = stack.bond_frac
    equity_frac = stack.equity_frac
    grant_eur = total_eur * grant_frac
    multi_eur = total_eur * multi_frac
    bond_eur = total_eur * bond_frac
    equity_eur = total_eur * equity_frac

    multi_rate = stack.multi_rate
    bond_rate = stack.bond_rate
    tenor = stack.tenor
    grace = stack.grace

    # Level annual debt service after grace, simple amortisation.
    def _annuity(principal: float, rate: float, years: int) -> float:
        if rate <= 0:
            return principal / max(years, 1)
        a = (1 - (1 + rate) ** -years)
        return principal * rate / a if a > 0 else principal / max(years, 1)

    repayment_years = max(tenor - grace, 1)
    multi_annuity = _annuity(multi_eur, multi_rate, repayment_years)
    bond_annuity = _annuity(bond_eur, bond_rate, repayment_years)
    annual_debt_service_eur = multi_annuity + bond_annuity

    # Construction-phase commitment. During the `grace` years the public
    # sponsor carries:
    #   • the equity tranche, drawn down evenly across construction;
    #   • interest-only service on repayable debt;
    #   • no repayment on the climate/development grant tranche.
    # Principal repayment doesn't start until year `grace + 1`.
    construction_years = max(grace, 1)
    annual_equity_eur = equity_eur / construction_years
    annual_grace_interest_eur = (multi_eur * multi_rate) + (bond_eur * bond_rate)
    annual_construction_commitment_eur = (
        annual_equity_eur + annual_grace_interest_eur
    )

    # OPEX model. Components, all in EUR / year internally because the
    # generated schema still carries `*_eur` compatibility fields. The
    # README renders USD-first. Each line covers one discrete asset
    # class — no double-counting between rolling-stock
    # maintenance and stop/depot charging microgrids. Traction energy
    # is charged only for the net grid/PPA top-up after on-site PV.
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
    #   • residual train-control wayside maintenance — 5 % of the
    #     small residual signalling CAPEX. Onboard ATP/ATO + T-OBS
    #     carry the expensive function; wayside is LoRa gateways,
    #     W-Nodes at switches/stations, passive balises, and OCC
    #     interfaces, maintained by the shared electronics team.
    #   • traction energy — timetable demand minus on-site PV and the
    #     dedicated solar plant. Earlier OPEX models made the opposite
    #     error in two directions: either billing all car-km despite PV
    #     CAPEX, or billing none even when the generated PV estate no
    #     longer covered the uplifted timetable. The row below charges
    #     only residual grid/PPA shortfall plus annual solar-plant O&M.
    #   • labour — derived from headcount × country-median salary.
    rs_maint = 0.04 * float(costs.get("rolling_stock_eur", 0.0))
    civil_maint = 0.02 * (
        float(costs.get("civil_subtotal_eur", 0.0))
        + float(costs.get("stations_eur", 0.0))
        + float(costs.get("depots_eur", 0.0))
    )
    sig_maint = 0.05 * float(costs.get("signalling_eur", 0.0))

    consist_cars = stats.consist_cars
    total_trainsets = stats.revenue_fleet + stats.spare_fleet + stats.reserve_fleet
    service_hours_per_day = energy_plan.service_hours_per_day
    service_days_per_year = energy_plan.service_days_per_year
    annual_train_km = energy_plan.annual_train_km
    annual_car_km = energy_plan.annual_car_km
    train_km_basis = energy_plan.train_km_basis

    # Annual traction energy demand. On-site station/depot PV offsets the
    # demand first, then the dedicated solar plant covers the remaining
    # generated-timetable shortfall. Grid-tie standby and local charger
    # maintenance stay in civil_maint.
    annual_energy_kwh = energy_plan.annual_energy_kwh
    annual_energy_gwh = annual_energy_kwh / 1e6
    onsite_pv_kwh = energy_plan.onsite_pv_kwh
    solar_plant_kwh = energy_plan.solar_plant_generation_kwh
    residual_grid_import_kwh = energy_plan.residual_grid_import_kwh
    grid_energy_usd_per_kwh = float(fin.get("grid_energy_usd_per_kwh", 0.10))
    residual_grid_eur = (
        residual_grid_import_kwh * grid_energy_usd_per_kwh * _USD_TO_EUR
    )
    solar_plant_maint_eur = energy_plan.solar_plant_maintenance_usd * _USD_TO_EUR
    energy_eur = residual_grid_eur + solar_plant_maint_eur
    onsite_pv_gwh = onsite_pv_kwh / 1e6
    solar_plant_gwh = solar_plant_kwh / 1e6
    residual_grid_import_gwh = residual_grid_import_kwh / 1e6
    pv_coverage_pct = (
        min(1.0, (onsite_pv_kwh + solar_plant_kwh) / annual_energy_kwh)
        if annual_energy_kwh > 0.0 else 1.0
    )

    # Labour. GoA 4 driverless (no train drivers), but RFC 0015 moves
    # safety presence to OCC remote assist, station/platform staff, and
    # maintenance. The headcount model therefore scales with service
    # hours, fleet size, station count, route-km, and high-case ridership.
    workforce = _driverless_workforce_breakdown(
        design=design,
        stats=stats,
        service_hours_per_day=service_hours_per_day,
        total_trainsets=total_trainsets,
        annual_train_km=annual_train_km,
        daily_paid_trips_high=daily_pax_high,
    )
    headcount = sum(workforce.values())
    monthly_income = float(fin.get("median_monthly_income_usd", 600))
    # Salary mix: country-median × 12 × engineer-premium 1.4
    # (mainline maintainers / dispatchers / inspectors paid 1.5–2 ×
    # median; station staff ~1.0; weighted blend ≈ 1.4).
    labour_usd = headcount * monthly_income * 12 * 1.4
    labour_eur = labour_usd * _USD_TO_EUR  # USD->EUR compatibility math

    annual_opex_eur = rs_maint + civil_maint + sig_maint + energy_eur + labour_eur

    # Affordability-anchored ticket pricing. The revenue case uses a
    # monthly-pass share of country median income and solves the ridership
    # needed after station retail + advertising revenue.
    target_pass_share = float(
        fin.get("revenue_case_monthly_pass_income_share", 0.08)
    )
    target_monthly_pass_usd = target_pass_share * monthly_income
    target_trip_usd = target_monthly_pass_usd / 30.0
    target_trip_eur = target_trip_usd * _USD_TO_EUR
    target_pass_pct = f"{target_pass_share * 100:.0f} %"

    # Farebox revenue at the operating-neutral fare, using the same
    # ridership scenarios reported in the capacity section.
    annual_pax_low = daily_pax_low * service_days_per_year
    annual_pax_high = daily_pax_high * service_days_per_year
    farebox_low_eur = annual_pax_low * target_trip_eur
    farebox_high_eur = annual_pax_high * target_trip_eur
    commercial = _station_commercial_revenue_eur(design, monthly_income)
    retail_eur = commercial["retail_eur"]
    ads_eur = commercial["ads_eur"]
    nonfare_eur = commercial["total_eur"]

    target_recovery = float(fin.get("farebox_recovery_target", 0.5))

    def _usd(v_eur: float) -> str:
        return _fmt_usd(_usd_from_eur(v_eur))

    def _usd_credit(v_eur: float) -> str:
        return f"-{_usd(v_eur)}" if v_eur > 0.0 else _usd(0.0)

    def _usd_per_resident(v_eur: float) -> str:
        return f"${_usd_from_eur(v_eur):,.0f}"

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

    # ============================================================
    # GOVERNMENT COMMITMENT SUMMARY — top-of-section budgetable view
    # ============================================================
    # We compute the commitment first so the finance ministry sees the
    # bottom-line annual budget allocation immediately. The breakdowns
    # below explain how those numbers are built up.
    #
    # Budget envelope split into two phases:
    #   Phase 1 — Construction (years 1..grace, typically 5–10 yrs)
    #     • equity drawdown (annual_equity_eur)
    #     • grace-period interest on multilateral + bonds
    #     • no farebox revenue, no debt-principal repayment
    #   Phase 2 — Steady-state operation (year grace+1 onwards)
    #     • full debt service (multilateral + bond principal + interest)
    #     • OPEX shortfall = max(0, OPEX − operating revenue)
    #     • operating surplus = max(0, operating revenue − OPEX), applied
    #       against repayable-debt support before asking government for
    #       a steady-state budget allocation.
    #
    # We place this summary table ahead of the detailed CAPEX/OPEX
    # breakdowns so a finance ministry can pull a single number into
    # next year's budget submission without reading the whole section.
    total_revenue_low = farebox_low_eur + nonfare_eur
    total_revenue_high = farebox_high_eur + nonfare_eur
    operating_shortfall_low = max(0.0, annual_opex_eur - total_revenue_low)
    operating_shortfall_high = max(0.0, annual_opex_eur - total_revenue_high)
    surplus_low = max(0.0, total_revenue_low - annual_opex_eur)
    surplus_high = max(0.0, total_revenue_high - annual_opex_eur)
    gross_steady_state_low = annual_debt_service_eur + operating_shortfall_low
    gross_steady_state_high = annual_debt_service_eur + operating_shortfall_high
    steady_state_low = max(0.0, gross_steady_state_low - surplus_low)
    steady_state_high = max(0.0, gross_steady_state_high - surplus_high)
    surplus_credit_low = min(surplus_low, gross_steady_state_low)
    surplus_credit_high = min(surplus_high, gross_steady_state_high)
    cost_neutral_farebox_eur = max(0.0, annual_opex_eur - nonfare_eur)
    cost_neutral_annual_pax = (
        cost_neutral_farebox_eur / target_trip_eur
        if target_trip_eur > 0.0
        else 0.0
    )
    cost_neutral_daily_pax = cost_neutral_annual_pax / service_days_per_year
    cost_neutral_daily_active = (
        cost_neutral_daily_pax / paid_trips_per_daily_rider
        if paid_trips_per_daily_rider > 0.0
        else cost_neutral_daily_pax
    )
    cost_neutral_basis_share = (
        cost_neutral_daily_active / max(ridership_basis_population, 1)
    )
    cost_neutral_revenue_eur = cost_neutral_farebox_eur + nonfare_eur
    cost_neutral_surplus = max(0.0, cost_neutral_revenue_eur - annual_opex_eur)
    gross_cost_neutral_steady_state = annual_debt_service_eur
    cost_neutral_steady_state = max(
        0.0,
        gross_cost_neutral_steady_state - cost_neutral_surplus,
    )
    cost_neutral_surplus_credit = min(
        cost_neutral_surplus,
        gross_cost_neutral_steady_state,
    )

    population = max(int(stats.population), 1)
    construction_per_capita = annual_construction_commitment_eur / population
    steady_low_per_capita = steady_state_low / population
    steady_high_per_capita = steady_state_high / population
    steady_neutral_per_capita = cost_neutral_steady_state / population

    # Lifecycle envelope: total cumulative gov outlay over the loan
    # tenor (construction + repayment phases).
    lifecycle_low = (
        construction_years * annual_construction_commitment_eur
        + repayment_years * steady_state_low
    )
    lifecycle_high = (
        construction_years * annual_construction_commitment_eur
        + repayment_years * steady_state_high
    )
    lifecycle_neutral = (
        construction_years * annual_construction_commitment_eur
        + repayment_years * cost_neutral_steady_state
    )

    out.append("### Government commitment summary (budgetable)\n")
    out.append(
        "Bottom line for next year's budget submission. "
        f"Construction phase runs **years 1–{construction_years}** "
        f"(public equity drawdown + interest-only grace on repayable "
        f"debt; grant disbursements are non-repayable); steady-state "
        f"operation begins **year {construction_years + 1}** "
        f"and runs for **{repayment_years} years** until the loans amortise.\n"
    )
    out.append("| Phase | Annual gov / municipal commitment | Per resident / yr |")
    out.append("|---|---|---|")
    out.append(
        f"| Construction (years 1–{construction_years}) | "
        f"**{_usd(annual_construction_commitment_eur)} / yr** | "
        f"{_usd_per_resident(construction_per_capita)} |"
    )
    out.append(
        f"| Steady-state, low-ridership (year {construction_years + 1}+) | "
        f"**{_usd(steady_state_low)} / yr** | "
        f"{_usd_per_resident(steady_low_per_capita)} |"
    )
    out.append(
        f"| Steady-state, high-ridership (year {construction_years + 1}+) | "
        f"**{_usd(steady_state_high)} / yr** | "
        f"{_usd_per_resident(steady_high_per_capita)} |"
    )
    out.append(
        f"| Steady-state, operating-neutral revenue case | "
        f"**{_usd(cost_neutral_steady_state)} / yr** | "
        f"{_usd_per_resident(steady_neutral_per_capita)} |"
    )
    out.append(
        f"| Lifecycle envelope (yr 1–{tenor}, low scenario) | "
        f"**{_usd(lifecycle_low)} cumulative** | "
        f"{_usd_per_resident(lifecycle_low / population)} |"
    )
    out.append(
        f"| Lifecycle envelope (yr 1–{tenor}, high scenario) | "
        f"**{_usd(lifecycle_high)} cumulative** | "
        f"{_usd_per_resident(lifecycle_high / population)} |"
    )
    out.append(
        f"| Lifecycle envelope (yr 1–{tenor}, operating-neutral after opening) | "
        f"**{_usd(lifecycle_neutral)} cumulative** | "
        f"{_usd_per_resident(lifecycle_neutral / population)} |\n"
    )
    out.append(
        f"_Population basis: {population:,} (catchment per "
        f"`lib/city-batches/world-sample.toml`). After year {tenor}, debt "
        f"service drops to zero; steady-state commitments below are net of "
        f"any operating surplus applied to repayable-debt support. The "
        f"operating-neutral case already covers steady-state OPEX from "
        f"fares, station shops, and advertising. "
        f"Low/high residual OPEX shortfall before debt is "
        f"{_usd(operating_shortfall_low)} / yr → "
        f"{_usd(operating_shortfall_high)} / yr; surplus applied to debt "
        f"support is {_usd(surplus_credit_low)} / yr → "
        f"{_usd(surplus_credit_high)} / yr._\n"
    )

    out.append("### CAPEX funding stack\n")
    out.append("| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |")
    out.append("|---|---|---|---|---|---|")
    out.append(
        f"| Climate / development grant (non-repayable) | "
        f"{grant_frac:.0%} | {_usd(grant_eur)} | — | — | — |"
    )
    out.append(
        f"| Green concessional loan (World Bank / AfDB / ADB / GCF class) | "
        f"{multi_frac:.0%} | {_usd(multi_eur)} | {multi_rate:.1%} | "
        f"{tenor} y, {grace} y grace | {_usd(multi_annuity)} / yr |"
    )
    out.append(
        f"| Sovereign / project bonds (fallback only) | "
        f"{bond_frac:.0%} | {_usd(bond_eur)} | {bond_rate:.1%} | "
        f"{tenor} y, {grace} y grace | {_usd(bond_annuity)} / yr |"
    )
    out.append(
        f"| Government equity (no debt service) | "
        f"{equity_frac:.0%} | {_usd(equity_eur)} | — | — | — |"
    )
    out.append(
        f"| **Total** | **100%** | **{_usd(total_eur)}** | | | "
        f"**{_usd(annual_debt_service_eur)} / yr** |\n"
    )
    out.append(
        f"_During the {grace}-year grace period the public sponsor pays "
        f"interest only on repayable debt — concessional loan "
        f"{_usd(multi_eur * multi_rate)} / yr + fallback bonds "
        f"{_usd(bond_eur * bond_rate)} / yr = "
        f"**{_usd(annual_grace_interest_eur)} / yr** total. The "
        f"{_usd(grant_eur)} grant tranche carries no repayment or coupon. "
        f"Government equity is drawn across construction "
        f"({_usd(annual_equity_eur)} / yr × {grace} yr). Principal "
        f"repayment begins in year {grace + 1} on a {repayment_years}-year "
        f"amortisation schedule._\n"
    )

    out.append("### Annual OPEX (steady state)\n")
    out.append("| Component | Basis | Annual cost |")
    out.append("|---|---|---|")
    out.append(
        f"| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | "
        f"{_usd(rs_maint)} |"
    )
    out.append(
        f"| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | "
        f"{_usd(civil_maint)} |"
    )
    out.append(
        f"| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | "
        f"{_usd(sig_maint)} |"
    )
    if energy_plan.solar_plant_kw > 0.0:
        solar_supply_basis = (
            f"on-site PV {onsite_pv_gwh:.1f} GWh/yr + dedicated solar plant "
            f"{energy_plan.solar_plant_kw / 1000.0:.1f} MW / "
            f"{solar_plant_gwh:.1f} GWh/yr ({pv_coverage_pct:.0%} coverage)"
        )
    else:
        solar_supply_basis = (
            f"on-site PV {onsite_pv_gwh:.1f} GWh/yr "
            f"({pv_coverage_pct:.0%} coverage)"
        )
    out.append(
        f"| Traction energy ({annual_energy_gwh:.1f} GWh / yr) | "
        f"{train_km_basis}; {consist_cars} cars × "
        f"{_ENERGY_KWH_PER_CAR_KM:.1f} kWh/car-km; "
        f"{solar_supply_basis}; residual grid/PPA top-up "
        f"{residual_grid_import_gwh:.1f} GWh/yr @ "
        f"${grid_energy_usd_per_kwh:.2f}/kWh; solar plant O&M "
        f"{_SOLAR_PLANT_MAINT_FRAC:.1%}/yr | "
        f"{_usd(energy_eur)} |"
    )
    out.append(
        f"| Labour ({headcount:,} FTE) | "
        f"driverless roster: OCC/remote {workforce['occ_remote_assist']}, "
        f"station/platform {workforce['station_platform']}, passenger service "
        f"{workforce['passenger_service']}, fleet maintenance "
        f"{workforce['fleet_maintenance']}, infrastructure/energy "
        f"{workforce['infrastructure_energy']}, admin/training "
        f"{workforce['admin_training']}; no train drivers × country median × "
        f"12 × engineer-premium 1.4 | "
        f"{_usd(labour_eur)} |"
    )
    out.append(
        f"| **OPEX subtotal** | | **{_usd(annual_opex_eur)} / yr** |\n"
    )
    out.append(
        f"_Annual service work: {train_km_basis} = "
        f"{annual_train_km / 1e6:.1f} M train-km / yr "
        f"({annual_car_km / 1e6:.1f} M car-km / yr). On-site PV covers "
        f"{onsite_pv_gwh:.1f} GWh/yr and the dedicated solar plant adds "
        f"{solar_plant_gwh:.1f} GWh/yr against {annual_energy_gwh:.1f} "
        f"GWh/yr traction demand before residual grid/PPA top-up "
        f"({residual_grid_import_gwh:.1f} GWh/yr). "
        f"Driverless labour follows RFC 0015: train drivers are not counted, "
        f"but OCC remote-assist, platform presence, passenger service, "
        f"and fleet/energy maintenance scale with the larger service._\n"
    )

    out.append("### Ticket pricing anchored to median income\n")
    out.append(
        f"Country median monthly income: **${monthly_income:,.0f} USD** "
        f"(per [`lib/templates/country-finance.toml`]({rel('lib/templates/country-finance.toml')})). "
        f"The revenue-forward case sets the monthly unlimited pass at "
        f"**{target_pass_pct} of median monthly income** and pairs it with "
        f"higher service uptake, more frequent trains, station retail, "
        f"and advertising. Single-trip fare is set so that 30 single trips equal one "
        f"monthly pass — a frequent commuter averaging ~50 trips / month "
        f"still receives an effective ~40 % bulk discount.\n"
    )
    out.append("| Product | Price target |")
    out.append("|---|---|")
    out.append(
        f"| Operating-neutral single-trip fare ({target_pass_pct} pass) | "
        f"${target_trip_usd:.2f} |"
    )
    out.append(
        f"| Day pass (3 trips) | "
        f"${(target_trip_usd * 3 * 0.85):.2f} (15 % bulk discount) |"
    )
    out.append(
        f"| Monthly unlimited pass | "
        f"${target_monthly_pass_usd:.2f} (~{target_pass_pct} of median monthly income) |"
    )
    out.append(
        f"| Annual pass | "
        f"${(target_monthly_pass_usd * 11):.2f} (11 × monthly = ~1 free month) |\n"
    )

    out.append("### Revenue & operating neutrality\n")
    out.append(
        f"Planning ridership bracket = daily active riders at "
        f"{_pct_range(ridership_low_share, ridership_high_share)} of "
        f"{ridership_basis_label}, converted to paid trips at "
        f"{paid_trips_per_daily_rider:g} trips/rider/day and capped by "
        f"practical service capacity ({practical_daily_capacity:,} trips/day). "
        f"Annual paid trips multiply daily paid trips by "
        f"{service_days_per_year} service-days at the operating-neutral fare. The "
        "operating-neutral column solves annual paid trips so "
        "**farebox + station-shop leases + advertising = steady-state OPEX**. "
        "Gross post-grace repayable-debt service remains visible in the "
        "CAPEX funding stack, while any operating surplus is netted from "
        "the budgetable government support line.\n"
    )
    out.append("| | Low scenario | High scenario | Operating-neutral target |")
    out.append("|---|---|---|---|")
    out.append(
        f"| Daily active riders | {daily_active_low:,.0f} | "
        f"{daily_active_high:,.0f} | {cost_neutral_daily_active:,.0f} |"
    )
    out.append(
        f"| Daily active riders / {ridership_basis_label} | "
        f"{daily_active_low / ridership_basis_population:.0%} | "
        f"{daily_active_high / ridership_basis_population:.0%} | "
        f"{cost_neutral_basis_share:.0%} |"
    )
    out.append(
        f"| Paid trips / active rider | "
        f"{paid_trips_per_daily_rider:g} | "
        f"{paid_trips_per_daily_rider:g} | "
        f"{paid_trips_per_daily_rider:g} |"
    )
    out.append(
        f"| Daily paid trips | {daily_pax_low:,.0f} | "
        f"{daily_pax_high:,.0f} | {cost_neutral_daily_pax:,.0f} |"
    )
    out.append(
        f"| Daily paid trips / city population | {daily_pax_low / population:.0%} | "
        f"{daily_pax_high / population:.0%} | "
        f"{cost_neutral_daily_pax / population:.0%} |"
    )
    out.append(
        f"| Annual paid trips | {annual_pax_low / 1e6:,.1f} M | "
        f"{annual_pax_high / 1e6:,.1f} M | "
        f"{cost_neutral_annual_pax / 1e6:,.1f} M |"
    )
    out.append(
        f"| Farebox revenue | {_usd(farebox_low_eur)} / yr | "
        f"{_usd(farebox_high_eur)} / yr | "
        f"{_usd(cost_neutral_farebox_eur)} / yr |"
    )
    out.append(
        f"| Station shop leases | {_usd(retail_eur)} / yr | "
        f"{_usd(retail_eur)} / yr | {_usd(retail_eur)} / yr |"
    )
    out.append(
        f"| Advertising boards | {_usd(ads_eur)} / yr | "
        f"{_usd(ads_eur)} / yr | {_usd(ads_eur)} / yr |"
    )
    out.append(
        f"| **Total revenue** | **{_usd(total_revenue_low)} / yr** | "
        f"**{_usd(total_revenue_high)} / yr** | "
        f"**{_usd(cost_neutral_revenue_eur)} / yr** |"
    )
    out.append(
        f"| Revenue / OPEX recovery | "
        f"{(total_revenue_low / annual_opex_eur):.0%} | "
        f"{(total_revenue_high / annual_opex_eur):.0%} | "
        f"100% |"
    )
    out.append(
        f"| Country farebox-only policy target (diagnostic) | "
        f"{target_recovery:.0%} | {target_recovery:.0%} | {target_recovery:.0%} |"
    )
    out.append(
        f"| Gross repayable-debt service + residual OPEX subsidy | "
        f"{_usd(gross_steady_state_low)} / yr | "
        f"{_usd(gross_steady_state_high)} / yr | "
        f"**{_usd(gross_cost_neutral_steady_state)} / yr** |"
    )
    out.append(
        f"| Operating surplus applied to debt support | "
        f"{_usd_credit(surplus_credit_low)} / yr | "
        f"{_usd_credit(surplus_credit_high)} / yr | "
        f"**{_usd_credit(cost_neutral_surplus_credit)} / yr** |"
    )
    out.append(
        f"| **Net gov repayable-debt support + residual OPEX subsidy** | "
        f"{_usd(steady_state_low)} / yr | "
        f"{_usd(steady_state_high)} / yr | "
        f"**{_usd(cost_neutral_steady_state)} / yr** |"
    )
    out.append(
        f"| Operating surplus after OPEX (before debt support) | "
        f"{_usd(surplus_low)} / yr | "
        f"{_usd(surplus_high)} / yr | "
        f"$0 / yr |\n"
    )
    out.append(
        f"_Commercial-revenue assumptions: {commercial['rentable_sqm']:,.0f} m² "
        f"of station shop/kiosk leases at "
        f"${commercial['retail_rent_usd_m2_month']:.0f}/m²/month and "
        f"{commercial['ad_boards']:,.0f} advertising boards at "
        f"${commercial['ad_board_usd_month']:.0f}/board/month, with "
        "occupancy derates applied._\n"
    )

    out.append(
        "**Caveats:** The grant-first funding stack, the "
        f"{target_pass_pct} operating-neutral fare target, the "
        f"{_pct_range(ridership_low_share, ridership_high_share)} "
        "daily-active-rider bracket, and the station-commercial assumptions are "
        "project-level defaults. "
        "Real deployments will negotiate the capital split with financing "
        "institutions and tune fares, retail mix, advertising inventory, "
        "and service frequency iteratively from boarding data. Treat the "
        "numbers above as a first-iteration sanity check, not as a "
        "bid-ready financial close.\n"
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


def _trainset_profile_for_family(family: str) -> dict[str, int]:
    """Resolve seat, nominal, and crush capacity for a family.

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
                    profile = profiles[family]
                    nominal = int(profile["passenger_capacity"])
                    return {
                        "passenger_capacity": nominal,
                        "seat_count": int(profile.get("seat_count", max(1, nominal // 5))),
                        "crush_capacity": int(profile.get("crush_capacity", round(nominal * 1.25))),
                    }
            except Exception:
                break
            break
    nominal = _FAMILY_CAPACITY_FALLBACK.get(family, 330)
    return {
        "passenger_capacity": nominal,
        "seat_count": _FAMILY_SEATS_FALLBACK.get(family, max(1, nominal // 5)),
        "crush_capacity": _FAMILY_CRUSH_FALLBACK.get(family, round(nominal * 1.25)),
    }


def _trainset_capacity_for_family(family: str) -> int:
    """Back-compat wrapper for older tests and CLI callers."""
    return _trainset_profile_for_family(family)["passenger_capacity"]


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
    energy_plan = _energy_plan(design, scenario, stats)

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
    # `light-metro-3car` carries 360 nominal pax / 480 crush,
    # Baghdad-class 6-car corridors carry 720 nominal / 960 crush.
    # The CLI override
    # (`--pax-per-trainset`) wins when present so what-if analysis
    # still works.
    trains_per_hour_per_dir = 60 / stats.peak_headway_min
    capacity_pax = (
        cost.trainset_capacity_pax
        if cost.trainset_capacity_pax is not None
        else stats.trainset_capacity_pax
    )
    total_fleet_trainsets = stats.revenue_fleet + stats.spare_fleet + stats.reserve_fleet
    revenue_fleet_capacity_pax = stats.revenue_fleet * capacity_pax
    total_fleet_capacity_pax = total_fleet_trainsets * capacity_pax
    revenue_fleet_crush_pax = stats.revenue_fleet * stats.trainset_crush_capacity_pax
    total_fleet_crush_pax = total_fleet_trainsets * stats.trainset_crush_capacity_pax
    per_line_pphpd = capacity_pax * trains_per_hour_per_dir
    network_peak_per_h = per_line_pphpd * stats.line_count * 2
    daily_theoretical = network_peak_per_h * 10  # peak≈10% of daily
    practical_daily_capacity = int(daily_theoretical * _PRACTICAL_CAPACITY_LOAD_FACTOR)
    catchment = int(stats.coverage * stats.population) if stats.coverage > 0 else None
    if catchment:
        ridership_basis_population = catchment
        ridership_basis_label = "catchment"
        ridership_low_share = _DAILY_RIDERSHIP_CATCHMENT_LOW
        ridership_high_share = _DAILY_RIDERSHIP_CATCHMENT_HIGH
    else:
        ridership_basis_population = stats.population
        ridership_basis_label = "city population"
        ridership_low_share = _DAILY_RIDERSHIP_POPULATION_FALLBACK_LOW
        ridership_high_share = _DAILY_RIDERSHIP_POPULATION_FALLBACK_HIGH
    uncapped_daily_active_low = int(ridership_basis_population * ridership_low_share)
    uncapped_daily_active_high = int(ridership_basis_population * ridership_high_share)
    paid_trips_per_daily_rider = _PAID_TRIPS_PER_DAILY_RIDER
    uncapped_daily_paid_low = int(
        uncapped_daily_active_low * paid_trips_per_daily_rider
    )
    uncapped_daily_paid_high = int(
        uncapped_daily_active_high * paid_trips_per_daily_rider
    )
    practical_daily_low = (
        min(uncapped_daily_paid_low, practical_daily_capacity)
        if ridership_basis_population > 0
        else None
    )
    practical_daily_high = (
        min(uncapped_daily_paid_high, practical_daily_capacity)
        if ridership_basis_population > 0
        else None
    )
    daily_active_low = (
        int(practical_daily_low / paid_trips_per_daily_rider)
        if practical_daily_low is not None and paid_trips_per_daily_rider > 0.0
        else 0
    )
    daily_active_high = (
        int(practical_daily_high / paid_trips_per_daily_rider)
        if practical_daily_high is not None and paid_trips_per_daily_rider > 0.0
        else 0
    )
    ridership_capped = (
        practical_daily_high is not None
        and uncapped_daily_paid_high > practical_daily_capacity
    )

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
        f"≈ **{practical_daily_low:,} – {practical_daily_high:,} paid trips/day** "
        f"({daily_active_low:,} – {daily_active_high:,} daily active riders "
        f"at {paid_trips_per_daily_rider:g} trips/rider/day)"
        if practical_daily_low is not None else "*(requires a coverage score)*"
    )
    cap_note = " (capped by practical service capacity)" if ridership_capped else ""

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
        f"| Revenue fleet passenger capacity | "
        f"{revenue_fleet_capacity_pax:,} AW2 pax "
        f"({revenue_fleet_crush_pax:,} AW3 crush) |"
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
        f"({_hours(stats.service_start, stats.service_end):.1f} h/day) |"
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
        f"| Seats | {stats.trainset_seats} longitudinal seats |"
    )
    out.append(
        f"| Nominal capacity (AW2) | {capacity_pax} pax (seated + standing, "
        f"`{stats.consist_family}` per RFC 0008 §1) |"
    )
    out.append(
        f"| Crush capacity (AW3) | {stats.trainset_crush_capacity_pax} pax, "
        "short-duration structural/egress reference |"
    )
    out.append(
        f"| Revenue fleet capacity | {revenue_fleet_capacity_pax:,} AW2 pax "
        f"({revenue_fleet_crush_pax:,} AW3 crush) |"
    )
    out.append(
        f"| Total fleet capacity | {total_fleet_capacity_pax:,} AW2 pax "
        f"({total_fleet_crush_pax:,} AW3 crush, incl. spare + reserve) |"
    )
    out.append("")

    out.append("## Ridership capacity\n")
    out.append(
        f"- **Per-train planning capacity:** {capacity_pax} AW2 passengers "
        f"(`{stats.consist_family}`)"
    )
    out.append(
        f"- **Revenue fleet simultaneous capacity:** "
        f"{stats.revenue_fleet} × {capacity_pax} = "
        f"**{revenue_fleet_capacity_pax:,} AW2 passengers** "
        f"({revenue_fleet_crush_pax:,} AW3 crush)"
    )
    out.append(
        f"- **Total fleet passenger capacity:** "
        f"{total_fleet_trainsets} × {capacity_pax} = "
        f"**{total_fleet_capacity_pax:,} AW2 passengers** "
        f"({total_fleet_crush_pax:,} AW3 crush, incl. spare + reserve)"
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
        f"- **Practical daily service capacity** "
        f"({_PRACTICAL_CAPACITY_LOAD_FACTOR:.0%} load factor): "
        f"≈ **{practical_daily_capacity:,} passenger-trips/day**"
    )
    out.append(
        f"- **Planning daily ridership scenario** "
        f"({_pct_range(ridership_low_share, ridership_high_share)} active-rider uptake of "
        f"{ridership_basis_label}{cap_note}): {daily_practical_str}\n"
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
    if energy_plan.solar_plant_kw > 0.0:
        out.append(
            "Dedicated utility-scale solar plant / contracted offsite PPA asset: "
            f"**{energy_plan.solar_plant_kw / 1000.0:,.1f} MW** sized to cover "
            "the generated timetable traction-energy gap after station/depot "
            f"PV, including a {_SOLAR_PLANT_COVERAGE_MARGIN:.0%} planning "
            "coverage margin. This is carried as infrastructure CAPEX below.\n"
        )
    out.append("### Energy Feasibility Check\n")
    avg_line_km = stats.route_km / max(stats.line_count, 1)
    trainset_kwh_per_km = stats.consist_cars * _ENERGY_KWH_PER_CAR_KM
    avg_line_energy_kwh = avg_line_km * trainset_kwh_per_km
    reserve_ratio = (
        stats.consist_battery_kwh / avg_line_energy_kwh
        if avg_line_energy_kwh > 0.0
        else 0.0
    )
    avg_stop_charger_kw = stats.total_charging_kw / max(stats.unique_station_count, 1)
    dwell_charge_kwh = avg_stop_charger_kw / 60.0
    stops_to_refill = (
        stats.consist_battery_kwh / dwell_charge_kwh
        if dwell_charge_kwh > 0.0
        else 0.0
    )
    traction_daily_mwh = (
        energy_plan.annual_energy_kwh
        / energy_plan.service_days_per_year
        / 1000.0
    )
    pv_daily_mwh = (
        energy_plan.onsite_pv_kwh
        / energy_plan.service_days_per_year
        / 1000.0
    )
    pre_plant_grid_daily_mwh = (
        energy_plan.pre_plant_grid_import_kwh
        / energy_plan.service_days_per_year
        / 1000.0
    )
    solar_plant_daily_mwh = (
        energy_plan.solar_plant_generation_kwh
        / energy_plan.service_days_per_year
        / 1000.0
    )
    residual_grid_daily_mwh = (
        energy_plan.residual_grid_import_kwh
        / energy_plan.service_days_per_year
        / 1000.0
    )
    storage_mwh = stats.total_battery_kwh / 1000.0
    out.append("| Check | Value | Interpretation |")
    out.append("|---|---:|---|")
    out.append(
        f"| Trainset line-haul intensity | {trainset_kwh_per_km:.1f} kWh/km | "
        f"{stats.consist_cars} cars × {_ENERGY_KWH_PER_CAR_KM:.1f} kWh/car-km planning basis |"
    )
    out.append(
        f"| Average one-way line energy | {avg_line_energy_kwh:,.0f} kWh | "
        f"{avg_line_km:.1f} km average line length |"
    )
    out.append(
        f"| Onboard battery coverage | {reserve_ratio:.1f}× average line run | "
        f"{stats.consist_battery_kwh} kWh usable pack |"
    )
    out.append(
        f"| Average 60 s dwell charge | {dwell_charge_kwh:.1f} kWh/stop | "
        f"{avg_stop_charger_kw:,.0f} kW average charger across stops |"
    )
    out.append(
        f"| Stops to refill one trainset pack | {stops_to_refill:.0f} stops | "
        "Opportunity charging supplements, not replaces, onboard reserve |"
    )
    out.append(
        f"| PV daily yield proxy | {pv_daily_mwh:,.0f} MWh/day | "
        f"{energy_plan.peak_sun_hours:.1f} peak-sun-hour planning proxy before local derates |"
    )
    out.append(
        f"| Scheduled traction demand | {traction_daily_mwh:,.0f} MWh/day | "
        f"{energy_plan.scheduled_daily_train_km:,.0f} scheduled train-km/day × "
        f"{_NON_REVENUE_TRAIN_KM_FACTOR:.0%} depot/deadhead factor |"
    )
    out.append(
        f"| On-site PV shortfall before solar plant | {pre_plant_grid_daily_mwh:,.0f} MWh/day | "
        "Gap used to size the dedicated plant / offsite solar PPA asset |"
    )
    out.append(
        f"| Dedicated solar plant | "
        f"{energy_plan.solar_plant_kw / 1000.0:,.1f} MW / "
        f"{solar_plant_daily_mwh:,.0f} MWh/day | "
        f"Utility PV + interconnection with {_SOLAR_PLANT_COVERAGE_MARGIN:.0%} "
        "planning coverage margin |"
    )
    out.append(
        f"| Residual grid/PPA top-up need | {residual_grid_daily_mwh:,.0f} MWh/day | "
        "Backup import after on-site PV plus the dedicated solar plant |"
    )
    out.append(
        f"| Station/depot stationary storage | {storage_mwh:,.0f} MWh | "
        "Distributed Na-ion buffer for charging peaks and grid outages |\n"
    )

    # Prefer the rust-emitted [costs] block (RFC 0011 §9 OSR-discipline
    # planning-grade CAPEX) over the rule-of-thumb per-unit calc — when
    # design.toml carries one, the CAPEX section is broken out by
    # archetype and references the design-discipline reasoning.
    rust_costs = design.get("costs")
    if rust_costs:
        out.extend(_rich_capex_section(design, rust_costs, stats, energy_plan))
        # Funding & affordability section — CAPEX funding stack, annual
        # OPEX estimate, ticket pricing anchored to country median
        # income. Reads `lib/templates/country-finance.toml`.
        out.extend(_funding_and_affordability_section(
            design,
            scenario,
            rust_costs,
            stats,
            energy_plan,
            rel,
            daily_active_low=daily_active_low,
            daily_active_high=daily_active_high,
            daily_pax_low=practical_daily_low or 0,
            daily_pax_high=practical_daily_high or 0,
            ridership_basis_label=ridership_basis_label,
            ridership_basis_population=ridership_basis_population,
            ridership_low_share=ridership_low_share,
            ridership_high_share=ridership_high_share,
            paid_trips_per_daily_rider=paid_trips_per_daily_rider,
            practical_daily_capacity=practical_daily_capacity,
        ))
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
        f"${cost.train_car_cost_usd / 1e3:.0f} k/car | "
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


def _fmt_usd(value: float) -> str:
    if value >= 1e9:
        return f"${value / 1e9:.2f} bn"
    if value >= 1e7:
        return f"${value / 1e6:.0f} M"
    if value >= 1e6:
        return f"${value / 1e6:.1f} M"
    return f"${value / 1e3:.0f} k"


def _fmt_usd_unit(value: float) -> str:
    if value < 1e6:
        return f"${value / 1e3:.0f} k"
    amount = value / 1e6
    if amount.is_integer():
        return f"${amount:.1f} M"
    return f"${amount:.2f} M"


def _usd_from_eur(value: float) -> float:
    return value * _EUR_TO_USD


def _charging_microgrid_unit_eur(archetype: str) -> float:
    """Per-stop charger + switchgear + microgrid tie-in allowance.

    This is not a route-km traction-power rate: OSR has no OCS, third rail,
    feeder substations, or continuous traction distribution.
    """
    unit = _CHARGING_MICROGRID_UNIT_USD.get(
        archetype,
        _CHARGING_MICROGRID_UNIT_USD["standard"],
    )
    return unit * _USD_TO_EUR


def _charging_microgrid_eur(costs: dict) -> float:
    """Canonical charging-microgrid CAPEX with legacy `power_eur` fallback."""
    return float(costs.get("charging_microgrid_eur", costs.get("power_eur", 0.0)))


def _rich_capex_section(
    design: dict,
    costs: dict,
    stats: NetworkStats,
    energy_plan: EnergyPlan,
) -> list[str]:
    """Emit the per-archetype CAPEX breakdown sourced from
    `design.toml`'s `[costs]` block (rust `osr-design` planner).
    The rust emitter only writes subtotals; per-archetype rows are
    re-derived here from the station / depot / line tables and the
    unit-cost mirror above."""

    def _cost_usd(stem: str) -> float:
        if f"{stem}_usd" in costs:
            return float(costs[f"{stem}_usd"])
        return float(costs.get(f"{stem}_eur", 0.0)) * _EUR_TO_USD

    def _money(stem: str) -> str:
        return _fmt_usd(_cost_usd(stem))

    def _money_value_usd(value: float) -> str:
        return _fmt_usd(value)

    def _money_unit_usd(value: float) -> str:
        return _fmt_usd_unit(value)

    archetype_counts: dict[str, int] = {}
    for s in design.get("stations", []):
        a = s.get("archetype", "standard")
        archetype_counts[a] = archetype_counts.get(a, 0) + 1
    depot_counts: dict[str, int] = {}
    for d in design.get("depots", []):
        a = d.get("archetype", "main-heavy")
        depot_counts[a] = depot_counts.get(a, 0) + 1

    # Civil mix.
    at_grade_km = _cost_usd("at_grade") / _AT_GRADE_USD_PER_KM
    elevated_km = _cost_usd("elevated") / _ELEVATED_USD_PER_KM
    bridge_km = _cost_usd("bridge") / _BRIDGE_USD_PER_KM
    junction_count = int(
        round(
            _cost_usd("junction_premium") / _JUNCTION_PREMIUM_USD
        )
    ) if costs.get("junction_premium_eur") or costs.get("junction_premium_usd") else 0

    family = (
        design.get("lines", [{}])[0].get("rolling_stock", "tram-2car")
    )
    fleet_total = stats.revenue_fleet + stats.spare_fleet + stats.reserve_fleet
    vehicle_count = fleet_total * _family_car_count(family)

    out: list[str] = []
    out.append("## CAPEX (planning grade)\n")
    out.append(
        "All figures come from the `[costs]` block in "
        "`design.toml` — emitted by the `osr-design` Rust planner per "
        "RFC 0011 §9. The procurement basis is **USD direct-supplier "
        "planning pricing**; `*_eur` fields remain in `design.toml` "
        f"only as compatibility mirrors at {_USD_TO_EUR:.2f} USD→EUR. "
        "**OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke "
        "architectural cladding), at-grade depots without overhead bridge "
        "cranes, **delivered rolling stock at about $1.4 M per "
        "self-contained car** (raw marketplace BOM retained only as an "
        "audit floor), commodity Na-ion cells + tier-2 PMSM motors + "
        "DIY SiC inverters, **onboard-first train control "
        "with only residual wayside** (no trackside fibre backbone, no "
        "proprietary CBTC vendor stack, no trackside computer "
        "interlockings — the function moves into the trainset, already "
        "counted in rolling-stock CAPEX), no overhead catenary, a dedicated "
        "solar plant when the generated timetable exceeds station/depot PV, "
        "and self-EPC overhead. The rolling-stock line now includes production labour, "
        "shop overhead, fixtures/tool amortisation, rail QA and "
        "homologation evidence, freight, duty, warranty, initial spares, "
        "training, commissioning, and acceptance testing. A separate lean "
        "railway production-plant setup line adds $100 k per vehicle/car "
        "module, with $200 k retained as the high sensitivity check. "
        "`country-costs.toml` applies the per-country labour/material "
        "multiplier downstream where a local tender view is needed.\n"
    )

    out.append("### Civil works\n")
    out.append("| Bucket | Value |")
    out.append("|---|---|")
    if at_grade_km > 0:
        out.append(
            f"| At-grade ({at_grade_km:.1f} km @ "
            f"{_money_unit_usd(_AT_GRADE_USD_PER_KM)}/km) | "
            f"{_money('at_grade')} |"
        )
    if elevated_km > 0:
        out.append(
            f"| Elevated ({elevated_km:.1f} km @ "
            f"{_money_unit_usd(_ELEVATED_USD_PER_KM)}/km) | "
            f"{_money('elevated')} |"
        )
    if bridge_km > 0:
        out.append(
            f"| Bridges ({bridge_km:.1f} km @ "
            f"{_money_unit_usd(_BRIDGE_USD_PER_KM)}/km) | "
            f"{_money('bridge')} |"
        )
    if junction_count > 0:
        out.append(
            f"| Elevated-interchange premium ({junction_count} sites @ "
            f"{_money_unit_usd(_JUNCTION_PREMIUM_USD)}) | "
            f"{_money('junction_premium')} |"
        )
    out.append(
        f"| **Civil subtotal** | **{_money('civil_subtotal')}** |\n"
    )

    out.append("### Stations\n")
    out.append(
        "Prefab portal-frame canopy + factory-bonded PV sandwich panel "
        "(RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, "
        "3–5 day erection). Ground-level platform slab with controlled "
        "pedestrian approaches; the rail datum drops through the station "
        "bay for level boarding. Overbridges, lifts, and stairs are only "
        "for elevated/stacked interchanges or site-specific road barriers.\n"
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
        unit = _STATION_UNIT_USD.get(a, _STATION_UNIT_USD["standard"])
        out.append(
            f"| `{a}` | {n} | {_money_unit_usd(unit)} | {_money_value_usd(unit * n)} |"
        )
    out.append(
        f"| **Stations subtotal** | | | **{_money('stations')}** |\n"
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
        unit = _DEPOT_UNIT_USD.get(a, _DEPOT_UNIT_USD["main-heavy"])
        out.append(
            f"| `{a}` | {n} | {_money_unit_usd(unit)} | {_money_value_usd(unit * n)} |"
        )
    out.append(
        f"| **Depots subtotal** | | | **{_money('depots')}** |\n"
    )

    out.append("### Rolling stock\n")
    out.append(
        "Rolling stock is costed at the **delivered production planning "
        "unit: $1.4 M per self-contained car**. The raw 3-car "
        "light-metro BOM floor remains 592,840 USD direct material plus "
        "35 % assembly allowance = 800,334 USD per consist, but city CAPEX "
        "now adds production labour, shop overhead, fixtures/tool "
        "amortisation, rail QA and homologation evidence, freight, duty, "
        "warranty, initial spares, training, commissioning, and acceptance "
        "testing. Motors, sensors, train-control computers, onboard "
        "batteries, roof PV, and charge hardware appear here ONLY — never "
        "re-billed elsewhere in the city cost stack.\n"
    )
    out.append("| Per-car cost bucket | Basis | Cost |")
    out.append("|---|---|---|")
    out.append("| Direct material BOM floor | Welded frame, panels, glazing, doors, bogies, traction, batteries, HVAC, electronics, interiors | $267 k |")
    out.append("| Production labour + shop overhead | Cut/bend/weld, fit-out, harnessing, paint, factory supervision, utilities, rework reserve | $420 k |")
    out.append("| Fixtures, tooling, QA, certification evidence | Jigs/fixtures, dimensional QA, EN 15085/45545 evidence, supplier audits, homologation dossier amortisation | $310 k |")
    out.append("| Logistics, warranty, spares, commissioning | Freight, duty, insurance, initial spares/tools, manuals/training, site testing, acceptance runs | $403 k |")
    out.append("| **Total per car** | Delivered production planning unit | **$1.4 M** |\n")
    out.append("| Item | Count | Unit | Subtotal |")
    out.append("|---|---|---|---|")
    rs_unit = _TRAINSET_UNIT_USD.get(family, _TRAINSET_UNIT_USD["light-metro-3car"])
    out.append(
        f"| `{family}` (revenue + spare + cold reserve) | "
        f"{fleet_total} | {_money_unit_usd(rs_unit)} | "
        f"{_money('rolling_stock')} |"
    )
    out.append("")

    out.append("### Railway production plant\n")
    out.append(
        "Each city carries a lean local railway production-plant setup "
        "allowance for tooling, basic fixtures, plant services, and "
        "commissioning bay setup. It is costed per vehicle/car module, "
        "not per trainset, and stays separate from the delivered "
        "rolling-stock procurement line.\n"
    )
    out.append("| Item | Count | Unit | Subtotal |")
    out.append("|---|---:|---:|---:|")
    out.append(
        f"| Vehicle/car modules supported by city fleet | {vehicle_count} | "
        f"{_money_unit_usd(_PRODUCTION_PLANT_PER_VEHICLE_USD)} | "
        f"{_money('production_plant')} |"
    )
    out.append(
        f"| High sensitivity check | {vehicle_count} | "
        f"{_money_unit_usd(_PRODUCTION_PLANT_HIGH_PER_VEHICLE_USD)} | "
        f"{_money_value_usd(vehicle_count * _PRODUCTION_PLANT_HIGH_PER_VEHICLE_USD)} |"
    )
    out.append("")

    out.append("### Dedicated solar power plant\n")
    out.append(
        "Station/depot PV is counted in the charging microgrid and depot "
        "asset lines. When the generated timetable still has a traction-energy "
        "shortfall, the README adds a separate utility-scale solar plant "
        "or contracted offsite PPA asset sized from that gap.\n"
    )
    out.append("| Item | Basis | Value |")
    out.append("|---|---|---:|")
    if energy_plan.solar_plant_kw > 0.0:
        utility_pv_usd = (
            energy_plan.solar_plant_kw * _SOLAR_PLANT_UTILITY_USD_PER_KW
        )
        interconnection_usd = (
            energy_plan.solar_plant_kw * _SOLAR_PLANT_INTERCONNECTION_USD_PER_KW
        )
        out.append(
            f"| Utility-scale PV field | "
            f"{energy_plan.solar_plant_kw:,.0f} kW @ "
            f"${_SOLAR_PLANT_UTILITY_USD_PER_KW:,.0f}/kW | "
            f"{_money_value_usd(utility_pv_usd)} |"
        )
        out.append(
            f"| Grid interconnection / PPA tie-in | "
            f"{energy_plan.solar_plant_kw:,.0f} kW @ "
            f"${_SOLAR_PLANT_INTERCONNECTION_USD_PER_KW:,.0f}/kW | "
            f"{_money_value_usd(interconnection_usd)} |"
        )
        out.append(
            f"| Annual generation proxy | "
            f"{energy_plan.solar_plant_kw / 1000.0:,.1f} MW × "
            f"{energy_plan.peak_sun_hours:.1f} peak-sun-h/day × "
            f"{energy_plan.service_days_per_year} d/yr | "
            f"{energy_plan.solar_plant_generation_kwh / 1e6:,.1f} GWh/yr |"
        )
    else:
        out.append(
            "| Supplemental plant | on-site station/depot PV covers generated timetable demand | $0 |"
        )
    out.append(
        f"| **Dedicated solar plant subtotal** | | "
        f"**{_money_value_usd(energy_plan.solar_plant_capex_usd)}** |\n"
    )

    out.append("### Systems\n")
    out.append("| Item | Basis | Subtotal |")
    out.append("|---|---|---|")
    out.append(
        f"| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | "
        f"{stats.route_km:.1f} km × ${_SIGNALLING_USD_PER_KM / 1_000_000:.3f} M/km | "
        f"{_money('signalling')} |"
    )
    out.append(
        f"| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | "
        f"per-stop allowance by station archetype | "
        f"{_money('charging_microgrid')} |"
    )
    out.append(
        f"| EPC integration + project management ({_EPC_OVERHEAD_FRAC:.0%}) | "
        f"on subtotal | {_money('epc_overhead')} |\n"
    )

    out.append("### Total\n")
    out.append("| Bucket | Value |")
    out.append("|---|---|")
    out.append(
        f"| Civil works | {_money('civil_subtotal')} |"
    )
    out.append(f"| Stations | {_money('stations')} |")
    out.append(f"| Depots | {_money('depots')} |")
    out.append(f"| Rolling stock | {_money('rolling_stock')} |")
    out.append(f"| Railway production plant | {_money('production_plant')} |")
    out.append(
        f"| Dedicated solar power plant | "
        f"{_money_value_usd(energy_plan.solar_plant_capex_usd)} |"
    )
    out.append(
        f"| Residual train-control wayside + charging microgrids | "
        f"{_fmt_usd(_cost_usd('signalling') + _cost_usd('charging_microgrid'))} |"
    )
    out.append(
        f"| EPC overhead ({_EPC_OVERHEAD_FRAC:.0%}) | "
        f"{_money('epc_overhead')} |"
    )
    total_usd = _cost_usd("total") + energy_plan.solar_plant_capex_usd
    out.append(f"| **CAPEX total** | **{_fmt_usd(total_usd)}** |")
    if stats.route_km > 0:
        per_km = total_usd / stats.route_km
        out.append(f"| Per-route-km | {_fmt_usd(per_km)} / km |")
    if stats.population > 0:
        per_capita = total_usd / stats.population
        out.append(
            f"| Per-capita (city pop) | "
            f"${per_capita:,.0f} / person |\n"
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
        "--track-cost-per-km", type=float, default=_AT_GRADE_USD_PER_KM,
        help=f"civil track unit cost, USD/km (default: {_AT_GRADE_USD_PER_KM:,.0f})",
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
        "--train-car-cost", type=float, default=_DEFAULT_TRAIN_CAR_USD,
        help=(
            "rolling-stock unit cost, USD per CAR "
            f"(default: {_DEFAULT_TRAIN_CAR_USD:,.0f}). "
            "A 3-car light-metro trainset costs about 4.2 M USD including "
            "labour, shop overhead, rail QA, freight/duty, warranty, spares, "
            "training, commissioning, and acceptance testing."
        ),
    )
    ap.add_argument(
        "--station-cost", type=float, default=_DEFAULT_STATION_USD,
        help=(
            "civil+fit-out unit cost, USD/station "
            f"(default: {_DEFAULT_STATION_USD:,.0f})"
        ),
    )
    ap.add_argument(
        "--depot-cost", type=float, default=_DEFAULT_DEPOT_USD,
        help=f"per-depot unit cost, USD/depot (default: {_DEFAULT_DEPOT_USD:,.0f})",
    )
    ap.add_argument(
        "--pax-per-trainset", type=int, default=None,
        help=(
            "passenger capacity per trainset (default: read from "
            "lib/templates/rolling-stock.toml for the design's "
            "rolling_stock family — 100 for urban-shuttle-1car, 240 for "
            "tram-2car, 360 for light-metro-3car, 480 for metro-4car, "
            "720 for metro-6car). "
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
