"""Generate a concise, location-specific README.md for any city design.

Consumes a `design.toml` + the expanded `scenario.toml` produced by
`osr_scenario` (so the sized PV / battery / fleet numbers are already
resolved) and writes a local decision summary with:

- network, line, fleet, capacity and catchment results;
- local energy, civil CAPEX and funding results;
- passing evidence links; and
- the local regeneration command.

Shared routing, service, energy, cost, finance, QA and assurance explanations
live once in `docs/deployment-planning-reference.md`. The optional detailed
renderer remains available for ad-hoc analysis but is not committed into city
folders.

Usage:
    python -m osr_scenario.network_readme \\
        --design cities/catalogue/west-asia/Iraq/Samawah/design.toml \\
        --scenario cities/catalogue/west-asia/Iraq/Samawah/samawah.toml \\
        --out cities/catalogue/west-asia/Iraq/Samawah/README.md

The batch planner uses the same entry point for every catalogue city.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import tomllib
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .capital import (
    FOREIGN_TURNKEY_BASIS,
    FOREIGN_TURNKEY_EXTERNAL_SHARE,
    IMPORTED_SHARE,
    city_capital_breakdown,
    foreign_turnkey_cases,
    funding_plan,
)


# --------------------------------------------------------------------------
# Cost + capacity assumptions
# --------------------------------------------------------------------------

@lru_cache(maxsize=None)
def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "lib/templates").exists():
            return parent
    raise FileNotFoundError("repository root with lib/templates not found")


@lru_cache(maxsize=None)
def _template_toml(filename: str) -> dict:
    candidate = _repo_root() / "lib/templates" / filename
    if candidate.exists():
        return tomllib.loads(candidate.read_text())
    raise FileNotFoundError(f"lib/templates/{filename} not found")


@lru_cache(maxsize=None)
def _rolling_stock_bom_totals() -> dict[str, int]:
    """Return consist-level totals directly from the authoritative BOM."""

    path = _repo_root() / "docs/rolling-stock/light-metro-3car/bom-skeleton.md"
    factors = {"SOURCE": (0.85, 1.35), "MAKE": (0.80, 1.45), "BID": (0.75, 1.65)}
    values: list[tuple[int, str]] = []
    for raw in path.read_text().splitlines():
        cells = [cell.strip() for cell in raw.strip().strip("|").split("|")]
        if len(cells) != 6 or not re.fullmatch(r"[A-Z]\d+", cells[0]):
            continue
        base = int(float(cells[4].replace(" ", "").replace(",", "").replace("_", "")))
        values.append((base, cells[3]))
    if not values:
        raise ValueError(f"{path} has no BOM rows")
    direct = sum(base for base, _ in values)
    low = sum(round(base * factors.get(source, factors["BID"])[0]) for base, source in values)
    high = sum(round(base * factors.get(source, factors["BID"])[1]) for base, source in values)
    assembly_fraction = float(
        _template_toml("capex-costs.toml")["trainset_cost_basis"]["local_assembly_fraction"]
    )
    assembly = round(direct * assembly_fraction)
    return {
        "direct_usd": direct,
        "assembly_usd": assembly,
        "with_assembly_usd": direct + assembly,
        "low_direct_usd": low,
        "low_with_assembly_usd": low + round(low * assembly_fraction),
        "high_direct_usd": high,
        "high_with_assembly_usd": high + round(high * assembly_fraction),
        "assembly_fraction": assembly_fraction,
    }


def _capex_costs() -> dict:
    return _template_toml("capex-costs.toml")


def _civil_cost_model() -> dict:
    return _template_toml("civil-cost-model.toml")


def _demand_profiles() -> dict:
    return _template_toml("demand-profiles.toml")


def _economic_benefits() -> dict:
    return _template_toml("economic-benefits.toml")


def _construction_qa() -> dict:
    return _template_toml("construction-qa.toml")


def _maintenance_schedule() -> dict:
    return _template_toml("maintenance-schedule.toml")


def _float_map(table: dict) -> dict[str, float]:
    return {str(k): float(v) for k, v in table.items()}


_CAPEX_COSTS = _capex_costs()
_CIVIL_COST_MODEL = _civil_cost_model()
_DEMAND_PROFILES = _demand_profiles()
_ECONOMIC_BENEFITS = _economic_benefits()
_CONSTRUCTION_QA = _construction_qa()
_MAINTENANCE_SCHEDULE = _maintenance_schedule()
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
_BENEFIT_ACCESS = _ECONOMIC_BENEFITS["access"]
_BENEFIT_ENVIRONMENT = _ECONOMIC_BENEFITS["environment"]
_BENEFIT_STATION_AREA = _ECONOMIC_BENEFITS["station_area"]
_BENEFIT_LOCAL_RECIRC = _ECONOMIC_BENEFITS["local_recirculation"]
_BENEFIT_LOCAL_CAPEX_SHARE = {
    bucket: 1.0 - imported_share
    for bucket, imported_share in IMPORTED_SHARE.items()
}
_CIVIL_USD_PER_KM = _float_map(_CIVIL_COST_MODEL["civil_usd_per_km"])
_AT_GRADE_USD_PER_KM = _CIVIL_USD_PER_KM["at_grade"]
_ELEVATED_USD_PER_KM = _CIVIL_USD_PER_KM["elevated"]
_BRIDGE_USD_PER_KM = _CIVIL_USD_PER_KM["bridge"]
_LIGHT_METRO_3CAR_BOM_TOTALS = _rolling_stock_bom_totals()
_LIGHT_METRO_3CAR_BOM_DIRECT_USD = _LIGHT_METRO_3CAR_BOM_TOTALS["direct_usd"]
_LIGHT_METRO_3CAR_BOM_ASSEMBLY_USD = _LIGHT_METRO_3CAR_BOM_TOTALS["assembly_usd"]
_LIGHT_METRO_3CAR_BOM_WITH_ASSEMBLY_USD = _LIGHT_METRO_3CAR_BOM_TOTALS[
    "with_assembly_usd"
]
_LIGHT_METRO_3CAR_ASSEMBLY_FRACTION = _LIGHT_METRO_3CAR_BOM_TOTALS["assembly_fraction"]
_LIGHT_METRO_3CAR_LOCAL_UNIT_USD = _TRAINSET_UNIT_USD["light-metro-3car"]
_LIGHT_METRO_3CAR_QA_HANDOVER_USD = (
    _LIGHT_METRO_3CAR_LOCAL_UNIT_USD
    - _LIGHT_METRO_3CAR_BOM_WITH_ASSEMBLY_USD
)
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
_PRACTICAL_CAPACITY_LOAD_FACTOR = float(
    _RIDERSHIP_PLANNING["practical_capacity_load_factor"]
)
_CAPACITY_UTILIZATION_LOW = float(
    _RIDERSHIP_PLANNING.get("capacity_utilization_low", 0.50)
)
_CAPACITY_UTILIZATION_HIGH = float(
    _RIDERSHIP_PLANNING.get("capacity_utilization_high", 0.80)
)
_QA_GATES = list(_CONSTRUCTION_QA.get("construction_qa_gate", []))
_MAINTENANCE_INTERVALS = list(
    _MAINTENANCE_SCHEDULE.get("maintenance_interval", [])
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
    service_rotation_fleet: int
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
    scheduled_daily_train_journeys: float
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
    return float(design_line["length_m"]) / 1000.0


def compute_stats(
    design: dict, scenario: dict, population: int
) -> NetworkStats:
    city_block = design["city"]
    city_name = city_block.get("name") or str(city_block["slug"]).title()
    country_iso = str(city_block["country"])

    lines = design.get("lines", [])
    line_count = len(lines)
    route_km = round(sum(_line_length_km(L) for L in lines), 1)
    unique_stations = {s["id"] for s in design.get("stations", [])}
    explicit_groups = {
        s.get("junction_group") for s in design.get("stations", [])
        if s.get("junction_group") is not None
    }
    interchange_count = len(explicit_groups) or sum(
        1 for s in design.get("stations", [])
        if s.get("archetype") in ("interchange", "interchange-elevated")
    )

    # Transfer reachability.
    transfer = _transfer_reachability(design)

    coverage = float(design.get("_quality_coverage", 0.0))

    fleets = design.get("fleets", [])
    revenue = sum(int(f["peak_count"]) for f in fleets)
    spare = sum(int(f.get("spare_count", 0)) for f in fleets)
    reserve = sum(int(f.get("cold_reserve_count", 0)) for f in fleets)
    service_rotation = sum(
        int(f.get("service_rotation_count", 0)) for f in fleets
    )
    # Peak headway from generated fleet schedules.
    peak_headway_min = float("inf")
    for fleet in scenario.get("fleets", []):
        for window in fleet.get("schedule", []):
            peak_headway_min = min(
                peak_headway_min,
                float(window.get("headway_min", peak_headway_min)),
            )
    if peak_headway_min == float("inf"):
        raise ValueError("scenario has no fleet schedule windows")
    service_start = str(scenario["fleets"][0]["service_start"])
    service_end = str(scenario["fleets"][0]["service_end"])

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
        service_rotation_fleet=service_rotation,
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


def _scheduled_daily_train_journeys(design: dict, scenario: dict) -> float:
    """Daily one-way train journeys from the generated fleet schedules."""
    line_ids = {
        str(line.get("name") or line.get("id"))
        for line in design.get("lines", [])
    }
    daily_journeys = 0.0
    for fleet in scenario.get("fleets", []):
        if str(fleet.get("line")) not in line_ids:
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
        daily_journeys += trips_per_direction * 2.0
    return daily_journeys


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
    scheduled_daily_train_journeys = _scheduled_daily_train_journeys(
        design, scenario
    )
    scheduled_daily_train_km = _scheduled_daily_train_km(design, scenario)
    if scheduled_daily_train_km <= 0.0:
        raise ValueError("scenario schedules produce no daily train-km")
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
        scheduled_daily_train_journeys=scheduled_daily_train_journeys,
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


def _cost_usd_from_costs(costs: dict, stem: str) -> float:
    if f"{stem}_usd" in costs:
        return float(costs[f"{stem}_usd"])
    return float(costs.get(f"{stem}_eur", 0.0)) * _EUR_TO_USD


def _anchor_access_counts(design: dict) -> dict[str, int]:
    categories = {
        "education": (
            "school", "university", "college", "kindergarten", "academy",
        ),
        "healthcare": (
            "hospital", "clinic", "doctors", "pharmacy", "dentist",
        ),
        "commerce": (
            "market", "marketplace", "shop", "mall", "retail", "commercial",
            "office", "bank", "restaurant", "cafe",
        ),
        "entertainment": (
            "cinema", "theatre", "theater", "stadium", "park", "leisure",
            "tourism", "arts", "sports", "community_centre",
        ),
    }
    counts = {key: 0 for key in categories}
    counts["anchored"] = 0
    counts["service_nodes"] = 0
    service_archetypes = {
        "major", "terminal", "depot-terminal", "interchange",
        "interchange-elevated",
    }
    for station in design.get("stations", []):
        archetype = str(station.get("archetype", "standard"))
        if archetype in service_archetypes:
            counts["service_nodes"] += 1
        anchor_kind = str(station.get("anchor_kind", "")).lower()
        anchor_name = str(station.get("anchor_name", "")).lower()
        if anchor_kind or anchor_name:
            counts["anchored"] += 1
        signal = f"{anchor_kind} {anchor_name}"
        for category, needles in categories.items():
            if any(needle in signal for needle in needles):
                counts[category] += 1
    return counts


def _share_from_signal(base: float, maximum: float, signal: float) -> float:
    signal = min(max(signal, 0.0), 1.0)
    return min(maximum, base + (maximum - base) * signal)


def _benefit_number_range(low: float, high: float, suffix: str = "") -> str:
    return f"{low:,.0f}{suffix} - {high:,.0f}{suffix}"


def _broad_economic_benefits_section(
    design: dict,
    costs: dict,
    stats: NetworkStats,
    energy_plan: EnergyPlan,
    rel,
    *,
    daily_pax_low: int,
    daily_pax_high: int,
    capacity_utilization_low: float,
    capacity_utilization_high: float,
) -> list[str]:
    fin = _load_country_finance(stats.country_iso)
    if not fin:
        return []

    monthly_income = float(fin.get("median_monthly_income_usd", 600))
    median_annual_income = monthly_income * 12.0
    median_hourly_income = median_annual_income / (52.0 * 40.0)
    value_of_time = median_hourly_income * float(
        _BENEFIT_ACCESS["value_of_time_income_share"]
    )
    time_saving_min = float(_BENEFIT_ACCESS["time_saving_min_per_paid_trip"])
    reliability_min = float(_BENEFIT_ACCESS["reliability_buffer_min_per_paid_trip"])
    generalized_min_saved = time_saving_min + reliability_min
    value_per_trip = value_of_time * generalized_min_saved / 60.0

    service_days = energy_plan.service_days_per_year
    annual_pax_low = daily_pax_low * service_days
    annual_pax_high = daily_pax_high * service_days
    time_value_low = annual_pax_low * value_per_trip
    time_value_high = annual_pax_high * value_per_trip

    avg_line_km = stats.route_km / max(stats.line_count, 1)
    avg_trip_km = avg_line_km * float(
        _BENEFIT_ACCESS["average_trip_length_route_share"]
    )
    avg_trip_km = min(
        float(_BENEFIT_ACCESS["max_average_trip_km"]),
        max(float(_BENEFIT_ACCESS["min_average_trip_km"]), avg_trip_km),
    )
    road_shift = float(_BENEFIT_ACCESS["road_mode_shift_share"])
    road_occupancy = float(_BENEFIT_ACCESS["road_vehicle_occupancy"])
    road_vkm_low = annual_pax_low * avg_trip_km * road_shift / road_occupancy
    road_vkm_high = annual_pax_high * avg_trip_km * road_shift / road_occupancy

    road_kg_per_vkm = float(
        _BENEFIT_ENVIRONMENT["road_emission_kg_co2e_per_vehicle_km"]
    )
    rail_kg_per_kwh = float(
        _BENEFIT_ENVIRONMENT["rail_grid_emission_kg_co2e_per_kwh"]
    )
    road_co2_t_low = road_vkm_low * road_kg_per_vkm / 1000.0
    road_co2_t_high = road_vkm_high * road_kg_per_vkm / 1000.0
    rail_co2_t = energy_plan.residual_grid_import_kwh * rail_kg_per_kwh / 1000.0
    co2_avoided_low = max(0.0, road_co2_t_low - rail_co2_t)
    co2_avoided_high = max(0.0, road_co2_t_high - rail_co2_t)
    carbon_value = float(_BENEFIT_ENVIRONMENT["social_carbon_usd_per_tonne"])
    carbon_value_low = co2_avoided_low * carbon_value
    carbon_value_high = co2_avoided_high * carbon_value
    congestion_rate = float(_BENEFIT_ENVIRONMENT["congestion_usd_per_vehicle_km"])
    local_externality_rate = float(
        _BENEFIT_ENVIRONMENT["local_air_noise_safety_usd_per_vehicle_km"]
    )
    congestion_low = road_vkm_low * congestion_rate
    congestion_high = road_vkm_high * congestion_rate
    local_externality_low = road_vkm_low * local_externality_rate
    local_externality_high = road_vkm_high * local_externality_rate

    counts = _anchor_access_counts(design)
    anchored = max(counts["anchored"], 1)
    station_count = max(stats.unique_station_count, 1)
    service_node_signal = counts["service_nodes"] / station_count

    anchor_weight = float(_BENEFIT_ACCESS["anchor_signal_weight"])
    education_signal = anchor_weight * counts["education"] / anchored
    healthcare_signal = anchor_weight * counts["healthcare"] / anchored
    commerce_signal = max(
        anchor_weight * counts["commerce"] / anchored,
        service_node_signal * 0.75,
    )
    entertainment_signal = max(
        anchor_weight * counts["entertainment"] / anchored,
        service_node_signal * 0.35,
        min(1.0, max(0.0, (energy_plan.service_hours_per_day - 14.0) / 10.0))
        * 0.40,
    )
    education_share = _share_from_signal(
        float(_BENEFIT_ACCESS["education_base_trip_share"]),
        float(_BENEFIT_ACCESS["education_max_trip_share"]),
        education_signal,
    )
    healthcare_share = _share_from_signal(
        float(_BENEFIT_ACCESS["healthcare_base_trip_share"]),
        float(_BENEFIT_ACCESS["healthcare_max_trip_share"]),
        healthcare_signal,
    )
    commerce_share = _share_from_signal(
        float(_BENEFIT_ACCESS["commerce_base_trip_share"]),
        float(_BENEFIT_ACCESS["commerce_max_trip_share"]),
        commerce_signal,
    )
    entertainment_share = _share_from_signal(
        float(_BENEFIT_ACCESS["entertainment_base_trip_share"]),
        float(_BENEFIT_ACCESS["entertainment_max_trip_share"]),
        entertainment_signal,
    )

    spend_per_relevant_trip = max(
        float(_BENEFIT_STATION_AREA["minimum_spend_per_relevant_trip_usd"]),
        monthly_income
        * float(_BENEFIT_STATION_AREA["spend_per_relevant_trip_income_share"]),
    )
    commerce_spend_low = annual_pax_low * commerce_share * spend_per_relevant_trip
    commerce_spend_high = annual_pax_high * commerce_share * spend_per_relevant_trip
    entertainment_spend_low = (
        annual_pax_low * entertainment_share * spend_per_relevant_trip
    )
    entertainment_spend_high = (
        annual_pax_high * entertainment_share * spend_per_relevant_trip
    )

    quantified_low = (
        time_value_low + congestion_low + local_externality_low
        + carbon_value_low + commerce_spend_low + entertainment_spend_low
    )
    quantified_high = (
        time_value_high + congestion_high + local_externality_high
        + carbon_value_high + commerce_spend_high + entertainment_spend_high
    )

    def _daily_trips(share: float, daily: int) -> float:
        return share * daily

    def _annual_events(share: float, daily: int, days_key: str) -> float:
        days = float(_BENEFIT_ACCESS[days_key])
        return _daily_trips(share, daily) * days

    education_events_low = _annual_events(
        education_share, daily_pax_low, "education_service_days_per_year"
    )
    education_events_high = _annual_events(
        education_share, daily_pax_high, "education_service_days_per_year"
    )
    healthcare_events_low = _annual_events(
        healthcare_share, daily_pax_low, "healthcare_service_days_per_year"
    )
    healthcare_events_high = _annual_events(
        healthcare_share, daily_pax_high, "healthcare_service_days_per_year"
    )
    commerce_events_low = _annual_events(
        commerce_share, daily_pax_low, "commerce_service_days_per_year"
    )
    commerce_events_high = _annual_events(
        commerce_share, daily_pax_high, "commerce_service_days_per_year"
    )
    entertainment_events_low = _annual_events(
        entertainment_share, daily_pax_low, "entertainment_service_days_per_year"
    )
    entertainment_events_high = _annual_events(
        entertainment_share, daily_pax_high, "entertainment_service_days_per_year"
    )

    local_shares = _BENEFIT_LOCAL_CAPEX_SHARE
    capex_buckets = {
        "civil": _cost_usd_from_costs(costs, "civil_subtotal"),
        "stations": _cost_usd_from_costs(costs, "stations"),
        "depots": _cost_usd_from_costs(costs, "depots"),
        "rolling_stock": _cost_usd_from_costs(costs, "rolling_stock"),
        "production_plant": _cost_usd_from_costs(costs, "production_plant"),
        "solar_plant": energy_plan.solar_plant_capex_usd,
        "signalling": _cost_usd_from_costs(costs, "signalling"),
        "charging_microgrid": _cost_usd_from_costs(costs, "charging_microgrid"),
        "epc_overhead": _cost_usd_from_costs(costs, "epc_overhead"),
    }
    local_capex = sum(
        value * local_shares.get(bucket, 0.0)
        for bucket, value in capex_buckets.items()
    )
    total_capex = _cost_usd_from_costs(costs, "total") + energy_plan.solar_plant_capex_usd
    local_capex_share = local_capex / total_capex if total_capex > 0.0 else 0.0
    construction_multiplier = float(
        _BENEFIT_LOCAL_RECIRC["construction_multiplier"]
    )
    local_activity = local_capex * construction_multiplier
    construction_years = max(int(fin.get("capex_grace_years", 5)), 1)
    annual_local_activity = local_activity / construction_years
    job_output_multiple = float(
        _BENEFIT_LOCAL_RECIRC["job_year_output_multiple_of_median_income"]
    )
    job_years = (
        local_capex / max(median_annual_income * job_output_multiple, 1.0)
    )

    out: list[str] = []
    out.append("## Broad economic benefits (planning proxy)\n")
    assumptions_link = rel("lib/templates/economic-benefits.toml")
    out.append(
        "This is a broad-benefit screen, not a bankable benefit-cost "
        "analysis. The rows quantify useful channels for discussion — travel "
        "time, road externalities, access to essential services, station-area "
        "activity, and local CAPEX recirculation — but some channels overlap "
        "and should not be treated as audited fiscal revenue. Assumptions are "
        f"loaded from [`lib/templates/economic-benefits.toml`]({assumptions_link}).\n"
    )

    out.append("### Annual benefit / activity proxy\n")
    out.append("| Channel | Low scenario | High scenario | Basis |")
    out.append("|---|---:|---:|---|")
    out.append(
        f"| Travel time + reliability dividend | {_fmt_usd(time_value_low)} / yr | "
        f"{_fmt_usd(time_value_high)} / yr | {generalized_min_saved:.0f} min/trip "
        f"× ${value_of_time:.2f}/h value-of-time proxy |"
    )
    out.append(
        f"| Avoided road congestion | {_fmt_usd(congestion_low)} / yr | "
        f"{_fmt_usd(congestion_high)} / yr | "
        f"{_benefit_number_range(road_vkm_low / 1e6, road_vkm_high / 1e6, ' M')} "
        f"vehicle-km/yr avoided × ${congestion_rate:.2f}/vehicle-km |"
    )
    out.append(
        f"| Avoided CO2e | {_fmt_usd(carbon_value_low)} / yr | "
        f"{_fmt_usd(carbon_value_high)} / yr | "
        f"{co2_avoided_low / 1000.0:,.1f}–{co2_avoided_high / 1000.0:,.1f} ktCO2e/yr "
        f"after rail residual-grid emissions × ${carbon_value:.0f}/t |"
    )
    out.append(
        f"| Local air / noise / safety externalities | "
        f"{_fmt_usd(local_externality_low)} / yr | "
        f"{_fmt_usd(local_externality_high)} / yr | "
        f"avoided road vehicle-km × ${local_externality_rate:.2f}/vehicle-km |"
    )
    out.append(
        f"| Station-area commerce turnover supported | "
        f"{_fmt_usd(commerce_spend_low)} / yr | "
        f"{_fmt_usd(commerce_spend_high)} / yr | "
        f"{commerce_share:.0%} of paid trips × ${spend_per_relevant_trip:.2f} "
        "local spend proxy |"
    )
    out.append(
        f"| Entertainment / community activity supported | "
        f"{_fmt_usd(entertainment_spend_low)} / yr | "
        f"{_fmt_usd(entertainment_spend_high)} / yr | "
        f"{entertainment_share:.0%} of paid trips × ${spend_per_relevant_trip:.2f} "
        "local spend proxy |"
    )
    out.append(
        f"| **Annual quantified benefit / activity proxy** | "
        f"**{_fmt_usd(quantified_low)} / yr** | "
        f"**{_fmt_usd(quantified_high)} / yr** | "
        "sum of rows above; use as a screening envelope, not audited revenue |\n"
    )

    out.append("### Access to education, healthcare, commerce, and entertainment\n")
    out.append("| Access channel | Anchored stations / signal | Low scenario | High scenario |")
    out.append("|---|---:|---:|---:|")
    out.append(
        f"| Education | {counts['education']} education anchors | "
        f"{_daily_trips(education_share, daily_pax_low):,.0f} trips/school day; "
        f"{education_events_low / 1e6:.1f} M access-events/yr | "
        f"{_daily_trips(education_share, daily_pax_high):,.0f} trips/school day; "
        f"{education_events_high / 1e6:.1f} M access-events/yr |"
    )
    out.append(
        f"| Healthcare | {counts['healthcare']} healthcare anchors | "
        f"{_daily_trips(healthcare_share, daily_pax_low):,.0f} trips/day; "
        f"{healthcare_events_low / 1e6:.1f} M access-events/yr | "
        f"{_daily_trips(healthcare_share, daily_pax_high):,.0f} trips/day; "
        f"{healthcare_events_high / 1e6:.1f} M access-events/yr |"
    )
    out.append(
        f"| Commerce | {counts['service_nodes']} major/terminal/interchange nodes | "
        f"{_daily_trips(commerce_share, daily_pax_low):,.0f} trips/trading day; "
        f"{commerce_events_low / 1e6:.1f} M access-events/yr | "
        f"{_daily_trips(commerce_share, daily_pax_high):,.0f} trips/trading day; "
        f"{commerce_events_high / 1e6:.1f} M access-events/yr |"
    )
    out.append(
        f"| Entertainment / community | {energy_plan.service_hours_per_day:.1f} h/day service span | "
        f"{_daily_trips(entertainment_share, daily_pax_low):,.0f} trips/activity day; "
        f"{entertainment_events_low / 1e6:.1f} M access-events/yr | "
        f"{_daily_trips(entertainment_share, daily_pax_high):,.0f} trips/activity day; "
        f"{entertainment_events_high / 1e6:.1f} M access-events/yr |\n"
    )

    out.append("### Local recirculation of initial CAPEX\n")
    out.append("| Channel | Value | Basis |")
    out.append("|---|---:|---|")
    out.append(
        f"| CAPEX retained in local procurement / payroll | "
        f"{_fmt_usd(local_capex)} | {local_capex_share:.0%} of "
        f"{_fmt_usd(total_capex)} CAPEX using bucket local-content shares |"
    )
    out.append(
        f"| Construction-phase local economic activity | "
        f"{_fmt_usd(local_activity)} | retained CAPEX × "
        f"{construction_multiplier:.1f} local supplier / wage multiplier |"
    )
    out.append(
        f"| Annualised during construction | {_fmt_usd(annual_local_activity)} / yr | "
        f"spread across {construction_years} construction / grace years |"
    )
    out.append(
        f"| Construction employment supported | {job_years:,.0f} job-years | "
        f"retained CAPEX ÷ ({job_output_multiple:.1f} × median annual income) |"
    )
    out.append(
        f"| Annual paid-trip capacity used in revenue model | "
        f"{annual_pax_low / 1e6:.1f} M - {annual_pax_high / 1e6:.1f} M trips/yr | "
        f"{capacity_utilization_low:.0%}-{capacity_utilization_high:.0%} "
        "of practical service capacity |\n"
    )

    out.append(
        "_Interpretation: the strongest fiscal result remains the farebox + "
        "commercial revenue table above. The broader rows here capture welfare, "
        "access, avoided external costs, and local supplier circulation that "
        "usually matter to a finance ministry, city authority, or development "
        "bank even when they do not appear as railway revenue._\n"
    )
    return out


def _funding_and_affordability_section(
    design: dict,
    scenario: dict,
    costs: dict,
    stats: NetworkStats,
    energy_plan: EnergyPlan,
    rel,
    *,
    daily_pax_low: int,
    daily_pax_high: int,
    practical_daily_capacity: int,
    capacity_utilization_low: float,
    capacity_utilization_high: float,
) -> list[str]:
    """Emit the `## Funding & affordability` section: grant-free CAPEX
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

    capital = city_capital_breakdown(
        costs,
        energy_plan.solar_plant_capex_usd,
    )
    if capital.total_usd <= 0.0:
        return []
    plan = funding_plan(capital, fin)
    turnkey_cases = foreign_turnkey_cases(capital, plan)
    turnkey_default = turnkey_cases["default"]
    total_eur = capital.total_usd * _USD_TO_EUR
    imported_eur = capital.imported_usd * _USD_TO_EUR
    local_eur = capital.local_usd * _USD_TO_EUR
    grant_eur = plan.external_grant_usd * _USD_TO_EUR
    multi_eur = plan.external_debt_usd * _USD_TO_EUR
    bond_eur = plan.local_bond_usd * _USD_TO_EUR
    equity_eur = plan.local_equity_usd * _USD_TO_EUR
    grant_frac = plan.external_grant_usd / capital.total_usd
    multi_frac = plan.external_debt_usd / capital.total_usd
    bond_frac = plan.local_bond_usd / capital.total_usd
    equity_frac = plan.local_equity_usd / capital.total_usd

    multi_rate = plan.external_rate
    bond_rate = plan.local_bond_rate
    tenor = plan.tenor_years
    grace = plan.construction_years

    # Level annual debt service after grace, simple amortisation.
    def _annuity(principal: float, rate: float, years: int) -> float:
        if rate <= 0:
            return principal / max(years, 1)
        a = (1 - (1 + rate) ** -years)
        return principal * rate / a if a > 0 else principal / max(years, 1)

    repayment_years = plan.repayment_years
    multi_annuity = _annuity(multi_eur, multi_rate, repayment_years)
    bond_annuity = _annuity(bond_eur, bond_rate, repayment_years)
    annual_debt_service_eur = multi_annuity + bond_annuity

    # Construction-phase commitment. During the `grace` years the public
    # sponsor carries:
    #   • the equity tranche, drawn down evenly across construction;
    #   • interest-only service on repayable debt;
    # Principal repayment doesn't start until year `grace + 1`.
    construction_years = plan.construction_years
    annual_equity_eur = equity_eur / construction_years
    annual_grace_interest_eur = (multi_eur * multi_rate) + (bond_eur * bond_rate)
    annual_construction_commitment_eur = (
        annual_equity_eur + annual_grace_interest_eur
    )
    annual_external_capital_eur = imported_eur / construction_years
    annual_local_capital_eur = local_eur / construction_years
    annual_local_bond_eur = bond_eur / construction_years

    # OPEX model. Components, all in EUR / year internally because the
    # generated schema still carries `*_eur` compatibility fields. The
    # README renders USD-first. Each line covers one discrete asset
    # class — no double-counting between rolling-stock
    # maintenance and stop/depot charging microgrids. Traction energy
    # is charged only for the net grid/PPA top-up after on-site PV.
    #
    #   • rolling-stock maintenance — 4 % of rolling-stock CAPEX. Covers
    #     onboard motors, batteries, body, electronics, brakes, doors,
    #     HVAC, and the traction-battery lifecycle reserve.
    #     Onboard batteries appear ONLY here.
    #   • civil + station + depot maintenance — 2 % of (civil+stations+
    #     depots) CAPEX. Covers track, building, station canopy,
    #     **trackside PV array**, **trackside LFP stationary
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
    total_trainsets = (
        stats.revenue_fleet
        + stats.service_rotation_fleet
        + stats.spare_fleet
        + stats.reserve_fleet
    )
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
    # hours, fleet size, station count, route-km, and high-case paid trips.
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
    # monthly-pass share of country median income and solves the capacity use
    # needed after station retail + advertising revenue.
    target_pass_share = float(
        fin.get("revenue_case_monthly_pass_income_share", 0.08)
    )
    target_monthly_pass_usd = target_pass_share * monthly_income
    target_trip_usd = target_monthly_pass_usd / 30.0
    target_trip_eur = target_trip_usd * _USD_TO_EUR
    target_pass_pct = f"{target_pass_share * 100:.0f} %"

    # Farebox revenue at the operating-neutral fare, using the same
    # capacity-use scenarios reported in the capacity section.
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
        value_usd = _usd_from_eur(v_eur)
        if value_usd < 500.0:
            return _fmt_usd(0.0)
        return f"-{_fmt_usd(value_usd)}"

    def _usd_per_resident(v_eur: float) -> str:
        return f"${_usd_from_eur(v_eur):,.0f}"

    out: list[str] = []
    out.append("## Funding & affordability\n")
    finance_link = rel("lib/templates/country-finance.toml")
    out.append(
        "Planning-grade procurement-origin and financing model anchored to country financial "
        "parameters from "
        f"[`lib/templates/country-finance.toml`]({finance_link}). "
        "Imported content defines the minimum foreign-currency / international "
        "capital requirement; locally supplied content can be financed with "
        "domestic-currency bonds, public equity, or other local sources. It is a "
        "pure function of the [costs] block above + the country code — "
        "regenerate by re-running `tools/automation/regenerate-city.sh "
        f"{stats.city_name.split()[0].lower()}`.\n"
    )

    out.append("### Imported value and construction capital requirement\n")
    out.append(
        "The localization-first import percentage is calculated bucket by bucket from the controlled "
        f"procurement-origin assumptions in [`lib/templates/capex-costs.toml`]({rel('lib/templates/capex-costs.toml')}). "
        "It is not a tariff estimate: it identifies the value that must be paid in "
        "foreign currency or backed by an international financing source. The "
        "shared national trainset factory is outside this city CAPEX and appears "
        "once in the country `NATIONAL-BRIEF.md`.\n"
    )
    out.append("| Capital boundary | Share of city CAPEX | Total requirement | Annual draw during construction |")
    out.append("|---|---:|---:|---:|")
    out.append(
        f"| **External capital for imported components / machinery** | "
        f"**{capital.imported_share:.1%}** | **{_usd(imported_eur)}** | "
        f"**{_usd(annual_external_capital_eur)} / yr** |"
    )
    out.append(
        f"| **Local capital for domestic procurement / payroll** | "
        f"**{capital.local_share:.1%}** | **{_usd(local_eur)}** | "
        f"**{_usd(annual_local_capital_eur)} / yr** |"
    )
    out.append(
        f"| of which planned local bond issuance | {bond_frac:.1%} of total CAPEX | "
        f"{_usd(bond_eur)} | {_usd(annual_local_bond_eur)} / yr |"
    )
    out.append(
        f"| **Total city programme** | **100.0%** | **{_usd(total_eur)}** | "
        f"**{_usd(total_eur / construction_years)} / yr** |\n"
    )

    out.append("### Foreign-company turnkey comparison\n")
    out.append(
        "This is an editable like-for-like sensitivity, not a vendor quotation. "
        "It multiplies OSR CAPEX for an equivalent network, fleet, service, and "
        f"energy scope, then assumes {FOREIGN_TURNKEY_EXTERNAL_SHARE:.0%} of the "
        "foreign contractor price requires foreign currency or international "
        f"capital. {FOREIGN_TURNKEY_BASIS} Lifetime interest uses the same "
        f"{plan.external_rate:.1%} rate, {plan.construction_years}-year construction "
        f"interest period, and {plan.repayment_years}-year amortization for both cases; "
        "the comparator external requirement is assumed debt-financed.\n"
    )
    out.append(
        "| Foreign-turnkey case | Cost multiplier vs OSR | Foreign-company external capital | "
        "OSR external capital saved | External interest saved over financing life | Capital + interest saved |"
    )
    out.append("|---|---:|---:|---:|---:|---:|")
    for case, comparison in turnkey_cases.items():
        label = f"**{case.title()}**" if case == "default" else case.title()
        out.append(
            f"| {label} | {comparison.cost_multiplier:.2f}× | "
            f"{_fmt_usd(comparison.foreign_external_usd)} | "
            f"{_fmt_usd(comparison.external_capital_avoided_usd)} "
            f"({comparison.external_capital_reduction:.1%}) | "
            f"{_fmt_usd(comparison.external_interest_avoided_usd)} | "
            f"**{_fmt_usd(comparison.lifetime_external_financing_avoided_usd)}** |"
        )
    out.append(
        f"\nAt the default {turnkey_default.cost_multiplier:.2f}× case, OSR's "
        f"{_fmt_usd(capital.imported_usd)} external requirement is "
        f"{turnkey_default.external_capital_reduction:.1%} below the illustrative "
        f"foreign-company requirement of {_fmt_usd(turnkey_default.foreign_external_usd)}; "
        f"the associated lifetime external-interest saving is "
        f"{_fmt_usd(turnkey_default.external_interest_avoided_usd)}, and total project "
        f"CAPEX is {turnkey_default.total_capex_reduction:.1%} lower. "
        "Replace both variables with normalized bids before an investment decision.\n"
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
    cost_neutral_capacity_utilization = (
        cost_neutral_daily_pax / practical_daily_capacity
        if practical_daily_capacity > 0
        else 0.0
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
        f"(local public-equity drawdown + interest-only grace on external "
        f"import finance and local bonds; capital-raising draws are shown above; "
        f"no climate-development grant assumed); steady-state "
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
        f"| Steady-state, low capacity-use (year {construction_years + 1}+) | "
        f"**{_usd(steady_state_low)} / yr** | "
        f"{_usd_per_resident(steady_low_per_capita)} |"
    )
    out.append(
        f"| Steady-state, high capacity-use (year {construction_years + 1}+) | "
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
        f"_Population basis: {population:,} (city population per "
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

    out.append("### CAPEX funding sources\n")
    out.append("| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |")
    out.append("|---|---|---|---|---|---|")
    if grant_frac > 0.0:
        out.append(
            f"| Climate / development grant (override only) | "
            f"{grant_frac:.0%} | {_usd(grant_eur)} | — | — | — |"
        )
    out.append(
        f"| External climate/MDB debt for imported content (unconfirmed) | "
        f"{multi_frac:.0%} | {_usd(multi_eur)} | {multi_rate:.1%} | "
        f"{tenor} y, {grace} y grace | {_usd(multi_annuity)} / yr |"
    )
    if bond_frac > 0.0:
        out.append(
            f"| Local-currency sovereign / project bonds for local content | "
            f"{bond_frac:.0%} | {_usd(bond_eur)} | {bond_rate:.1%} | "
            f"{tenor} y, {grace} y grace | {_usd(bond_annuity)} / yr |"
        )
    out.append(
        f"| Local government equity / other domestic funding (no debt service) | "
        f"{equity_frac:.0%} | {_usd(equity_eur)} | — | — | — |"
    )
    out.append(
        f"| **Total** | **100%** | **{_usd(total_eur)}** | | | "
        f"**{_usd(annual_debt_service_eur)} / yr** |\n"
    )
    out.append(
        f"_During the {grace}-year grace period the public sponsor pays "
        f"interest only on repayable debt — external import-finance debt "
        f"{_usd(multi_eur * multi_rate)} / yr"
        f"{' + local bonds ' + _usd(bond_eur * bond_rate) + ' / yr' if bond_eur > 0.0 else ''} = "
        f"**{_usd(annual_grace_interest_eur)} / yr** total. The "
        "base case assumes no climate-development grant. Local public equity "
        "is drawn across construction "
        f"({_usd(annual_equity_eur)} / yr × {grace} yr). Principal "
        f"repayment begins in year {grace + 1} on a {repayment_years}-year "
        f"amortisation schedule._\n"
    )
    out.append(
        "_Loan availability note: this is a finance placeholder, not a "
        "committed lender offer. Plausible providers would be a national "
        "government borrowing through an MDB or a climate fund accredited "
        "entity, such as the World Bank/IBRD, Islamic Development Bank, "
        "Climate Investment Funds, or Green Climate Fund channels. Official "
        "GCF policy allows grants and concessional loans, and World Bank/CIF "
        "material documents below-market climate finance, but this project "
        "still needs a lender mandate, eligibility screen, and signed term "
        f"sheet before the {plan.external_rate * 100:.1f}% / {plan.tenor_years}-year "
        "assumption can be treated as real. "
        "Evidence anchors: "
        "[GCF financial instruments](https://www.greenclimate.fund/about/policies/financial-instruments), "
        "[GCF concessional-loan terms decision](https://www.greenclimate.fund/decision/b09-04), "
        "[World Bank concessional-finance explainer](https://www.worldbank.org/en/news/feature/2021/09/16/what-you-need-to-know-about-concessional-finance-for-climate-action), "
        "[CIF funding instruments](https://www.cif.org/cif-funding), and "
        "[IsDB GCF accreditation](https://www.greenclimate.fund/ae/isdb)._\n"
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

    out.extend(_maintenance_schedule_section(rel, stats, energy_plan))

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
        "Planning revenue is capacity-led: annual paid trips are calculated "
        "from practical daily service capacity "
        f"({practical_daily_capacity:,} trips/day) × "
        f"{service_days_per_year} service-days × capacity utilisation. "
        f"The low/high bracket uses {capacity_utilization_low:.0%}–"
        f"{capacity_utilization_high:.0%} of that practical capacity. "
        "The operating-neutral column solves the capacity utilisation needed so "
        "**farebox + station-shop leases + advertising = steady-state OPEX**. "
        "Gross post-grace repayable-debt service remains visible in the "
        "external/local CAPEX funding sources, while any operating surplus is netted from "
        "the budgetable government support line.\n"
    )
    out.append("| | Low scenario | High scenario | Operating-neutral target |")
    out.append("|---|---|---|---|")
    out.append(
        f"| Practical service capacity used | {capacity_utilization_low:.0%} | "
        f"{capacity_utilization_high:.0%} | {cost_neutral_capacity_utilization:.0%} |"
    )
    out.append(
        f"| Annual paid trips | {annual_pax_low / 1e6:,.1f} M | "
        f"{annual_pax_high / 1e6:,.1f} M | "
        f"{cost_neutral_annual_pax / 1e6:,.1f} M |"
    )
    out.append(
        f"| Annual paid trips / city resident | {annual_pax_low / population:,.0f} | "
        f"{annual_pax_high / population:,.0f} | "
        f"{cost_neutral_annual_pax / population:,.0f} |"
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
        "**Caveats:** The grant-free procurement-origin funding boundary, the "
        f"{target_pass_pct} operating-neutral fare target, the "
        f"{capacity_utilization_low:.0%}–{capacity_utilization_high:.0%} "
        "capacity-utilisation bracket, and the station-commercial assumptions are "
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
    0.0 when the file is missing or unparseable. This is a stdlib-only
    mini-parser because `yaml` is not a project-level dependency."""
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


def _transfer_reachability(design: dict) -> float:
    lines = design.get("lines", [])
    if len(lines) < 2:
        return 1.0
    line_ids = [str(line.get("id") or line.get("name")) for line in lines]
    connected: set[frozenset[str]] = set()
    for interchange in design.get("interchanges", []):
        members = [str(line) for line in interchange.get("lines", [])]
        for index, first in enumerate(members):
            for second in members[index + 1:]:
                if first != second:
                    connected.add(frozenset((first, second)))
    if not connected:
        grouped: dict[object, set[str]] = {}
        for station in design.get("stations", []):
            group = station.get("junction_group")
            if group is not None:
                grouped.setdefault(group, set()).add(str(station.get("line", "")))
        for members in grouped.values():
            ordered = sorted(member for member in members if member)
            for index, first in enumerate(ordered):
                for second in ordered[index + 1:]:
                    connected.add(frozenset((first, second)))
    pairs = shared = 0
    for i in range(len(line_ids)):
        for j in range(i + 1, len(line_ids)):
            pairs += 1
            if frozenset((line_ids[i], line_ids[j])) in connected:
                shared += 1
    return shared / pairs if pairs else 1.0


def _opportunity_charging_audit(design: dict, scenario: dict) -> list[dict]:
    """Return per-line energy balance using the emitted operating timetable."""
    scenario_stations = {
        str(station["id"]): station for station in scenario.get("stations", [])
    }
    site_efficiency = {
        str(site["station"]): float(site.get("charger_efficiency", 0.98))
        for site in scenario.get("sites", [])
    }
    design_lines = {
        str(line.get("id") or line.get("name")): line
        for line in design.get("lines", [])
    }
    consist = scenario["consist"]
    usable_pack_kwh = float(consist["battery_capacity_kwh"]) * 0.80
    trainset_kwh_per_km = (
        int(consist["car_count"]) * float(consist["energy_kwh_per_car_km"])
    )
    ambient_c = float(scenario.get("climate", {}).get("ambient_c", 28.0))
    climate_uplift = float(
        scenario.get("climate", {}).get(
            "hvac_uplift_frac",
            min(max((ambient_c - 25.0) / 25.0, 0.0), 0.25),
        )
    )
    energy_margin = float(
        design.get("operations", {})
        .get("ring_service", {})
        .get("minimum_traversal_energy_margin", 1.10)
    )
    audits: list[dict] = []
    for scenario_line in scenario.get("lines", []):
        line_id = str(scenario_line["id"])
        design_line = design_lines[line_id]
        line_length_m = float(design_line["length_m"])
        traversal_kwh = (
            line_length_m / 1000.0 * trainset_kwh_per_km * (1.0 + climate_uplift)
        )
        chainage_m = 0.0
        powered: list[tuple[float, dict]] = []
        for index, line_station in enumerate(scenario_line.get("stations", [])):
            if index:
                chainage_m += float(line_station.get("distance_from_prev_m", 0.0))
            station = scenario_stations[str(line_station["id"])]
            if float(station.get("charging_power_kw", 0.0)) > 0.0:
                powered.append((chainage_m, station))
        delivered_kwh = sum(
            float(station["charging_power_kw"])
            * float(station["dwell_seconds"])
            / 3600.0
            * site_efficiency.get(str(station["id"]), 0.98)
            for _, station in powered
        )
        powered_chainages = [chainage for chainage, _ in powered]
        is_ring = bool(scenario_line.get("is_ring"))
        gaps_m: list[float] = []
        if powered_chainages:
            gaps_m.extend(
                powered_chainages[index + 1] - powered_chainages[index]
                for index in range(len(powered_chainages) - 1)
            )
            if is_ring:
                gaps_m.append(
                    line_length_m - powered_chainages[-1] + powered_chainages[0]
                )
            else:
                gaps_m.extend(
                    (powered_chainages[0], line_length_m - powered_chainages[-1])
                )
        worst_gap_m = max(gaps_m, default=line_length_m)
        worst_gap_kwh = (
            worst_gap_m / 1000.0 * trainset_kwh_per_km * (1.0 + climate_uplift)
        )
        audits.append(
            {
                "line_id": line_id,
                "is_ring": is_ring,
                "powered_stops": len(powered),
                "traversal_kwh": traversal_kwh,
                "delivered_kwh": delivered_kwh,
                "net_margin_kwh": delivered_kwh - traversal_kwh * energy_margin,
                "worst_gap_km": worst_gap_m / 1000.0,
                "worst_gap_kwh": worst_gap_kwh,
                "pack_margin_kwh": usable_pack_kwh - worst_gap_kwh,
                "usable_pack_kwh": usable_pack_kwh,
            }
        )
    return audits


# --------------------------------------------------------------------------
# README rendering
# --------------------------------------------------------------------------


def render_readme(
    design_path: Path,
    scenario_path: Path,
    *,
    screenshot_slug: str | None = None,
    detailed: bool = False,
) -> str:
    """Return a concise local README, or the legacy detailed report on request."""
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
    stats = compute_stats(design, scenario, int(design["city"]["population"]))
    energy_plan = _energy_plan(design, scenario, stats)
    charging_audit = _opportunity_charging_audit(design, scenario)
    headline_capital = city_capital_breakdown(
        design["costs"], energy_plan.solar_plant_capex_usd
    )
    headline_plan = funding_plan(
        headline_capital, _load_country_finance(stats.country_iso)
    )
    headline_turnkey = foreign_turnkey_cases(
        headline_capital, headline_plan
    )["default"]

    screenshot_slug = screenshot_slug or str(design["city"]["slug"])

    # Compute how many `..` to climb from the README's folder to repo root.
    rel_to_root = _rel_to_repo_root(design_path.parent)

    # Relative paths from the README's folder into the repo tree.
    def rel(*parts: str) -> str:
        return "/".join([rel_to_root, *parts]) if rel_to_root else "/".join(parts)

    # Ridership capacity. Per-train capacity comes from the
    # rolling-stock family (RFC 0008 §1) — Samawah's 3-car
    # `light-metro-3car` carries 360 nominal pax / 480 crush,
    # Baghdad-class 6-car corridors carry 720 nominal / 960 crush.
    trains_per_hour_per_dir = 60 / stats.peak_headway_min
    capacity_pax = stats.trainset_capacity_pax
    total_fleet_trainsets = (
        stats.revenue_fleet
        + stats.service_rotation_fleet
        + stats.spare_fleet
        + stats.reserve_fleet
    )
    revenue_fleet_capacity_pax = stats.revenue_fleet * capacity_pax
    total_fleet_capacity_pax = total_fleet_trainsets * capacity_pax
    revenue_fleet_crush_pax = stats.revenue_fleet * stats.trainset_crush_capacity_pax
    total_fleet_crush_pax = total_fleet_trainsets * stats.trainset_crush_capacity_pax
    per_line_pphpd = capacity_pax * trains_per_hour_per_dir
    network_peak_per_h = per_line_pphpd * stats.line_count * 2
    scheduled_daily_journeys = energy_plan.scheduled_daily_train_journeys
    if scheduled_daily_journeys <= 0.0:
        raise ValueError("scenario schedules produce no daily train journeys")
    daily_theoretical = scheduled_daily_journeys * capacity_pax
    daily_capacity_basis = (
        f"{scheduled_daily_journeys:,.0f} scheduled one-way train journeys/day "
        f"× {capacity_pax} AW2 pax"
    )
    practical_daily_capacity = int(daily_theoretical * _PRACTICAL_CAPACITY_LOAD_FACTOR)
    catchment = int(stats.coverage * stats.population) if stats.coverage > 0 else None
    capacity_utilization_low = _CAPACITY_UTILIZATION_LOW
    capacity_utilization_high = _CAPACITY_UTILIZATION_HIGH
    if capacity_utilization_high < capacity_utilization_low:
        capacity_utilization_low, capacity_utilization_high = (
            capacity_utilization_high,
            capacity_utilization_low,
        )
    practical_daily_low = int(practical_daily_capacity * capacity_utilization_low)
    practical_daily_high = int(practical_daily_capacity * capacity_utilization_high)
    annual_paid_low = practical_daily_low * 365
    annual_paid_high = practical_daily_high * 365

    # Per-line table.
    by_id = {s["id"]: s for s in design.get("stations", [])}
    # Lines emitted by `osr-design` carry `name` (slug-style id) — use
    # it for both keying and display.
    fleet_by_line = {
        f["line"]: int(f.get("trainset_count", 0))
        for f in design.get("fleets", [])
    }
    # Build per-line ordered station lists from the flat station list.
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
        inline_sts = stations_by_line.get(line_id, [])
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

    if not detailed:
        # Reuse the detailed finaliser as a fail-closed evidence validator, but
        # keep its explanatory output on the canonical common reference page.
        _finalise_readme(
            [], design_path, scenario_path, stats, screenshot_slug, rel
        )

        total_fleet = (
            stats.revenue_fleet
            + stats.service_rotation_fleet
            + stats.spare_fleet
            + stats.reserve_fleet
        )
        coverage = f"{stats.coverage:.1%}" if stats.coverage > 0 else "unavailable"
        catchment_text = f"{catchment:,}" if catchment is not None else "unavailable"
        common_reference = rel("docs/deployment-planning-reference.md")
        national_brief = "../NATIONAL-BRIEF.md"
        quality_file = f"{screenshot_slug}.design-quality.yaml"
        operations_manifest = (
            design_path.parent
            / "operations"
            / f"{screenshot_slug}-operations-manifest.json"
        )

        finance_path = design_path.parent / "engineering/finance/summary.json"
        finance = json.loads(finance_path.read_text()) if finance_path.is_file() else {}
        simulation_path = (
            design_path.parent / "engineering/simulation/validation-summary.json"
        )
        simulation = (
            json.loads(simulation_path.read_text()) if simulation_path.is_file() else {}
        )
        crosscheck_path = (
            design_path.parent / "engineering/simulation/operations-crosscheck.json"
        )
        operations_crosscheck = (
            json.loads(crosscheck_path.read_text()) if crosscheck_path.is_file() else {}
        )
        engineering = {}
        for package in ("sumo", "gis", "energy"):
            path = design_path.parent / "engineering" / package / "summary.json"
            engineering[package] = json.loads(path.read_text()) if path.is_file() else {}
        operations = (
            json.loads(operations_manifest.read_text())
            if operations_manifest.is_file()
            else {}
        )

        worst_gap = max(charging_audit, key=lambda row: row["worst_gap_kwh"])
        lowest_margin = min(charging_audit, key=lambda row: row["net_margin_kwh"])
        capital_labels = {
            "civil": "Civil works",
            "stations": "Stations",
            "depots": "Depots",
            "rolling_stock": "Rolling stock",
            "solar_plant": "Dedicated solar plant",
            "signalling": "Residual train control",
            "charging_microgrid": "Charging microgrids",
            "epc_overhead": "EPC / project services",
        }

        out: list[str] = [
            f"# {stats.city_name} — Urban Rail Network",
            "",
            f"**Country:** {stats.country_iso} · **Population:** {stats.population:,} · "
            f"[National brief]({national_brief})",
            "",
            f"This page contains only {stats.city_name}-specific results. Shared routing, "
            f"service, energy, civil, cost, finance, QA and validation methods are defined "
            f"once in the [deployment planning reference]({common_reference}).",
            "",
            "> [!IMPORTANT]",
            f"> **Foreign-capital advantage:** against the default equivalent "
            f"foreign-turnkey sensitivity, this local "
            f"plan avoids **{_fmt_usd(headline_turnkey.external_capital_avoided_usd)} "
            f"({headline_turnkey.external_capital_reduction:.1%}) of external capital** "
            f"and **{_fmt_usd(headline_turnkey.external_interest_avoided_usd)} of external "
            f"interest**. Capital plus saved interest totals "
            f"**{_fmt_usd(headline_turnkey.lifetime_external_financing_avoided_usd)}**. "
            f"See the common reference for interpretation and limitations.",
            "",
            "Auto-planned by the OpenSourceRail design pipeline from the controlled city "
            "catalogue, source-locked geospatial inputs and shared templates.",
            "",
            "## Network",
            "",
            f"![{stats.city_name} rail network on OpenStreetMap]"
            f"({screenshot_slug}-network-map.png)",
            "",
            "| Local measure | Value |",
            "|---|---:|",
            f"| Lines / unique stations / interchanges | {stats.line_count} / "
            f"{stats.unique_station_count} / {stats.interchange_count} |",
            f"| Route length | {stats.route_km:.1f} km double track |",
            f"| Coverage / transfer reachability | {coverage} / "
            f"{stats.transfer_reachability:.0%} |",
            f"| Estimated station catchment | {catchment_text} residents |",
            f"| Service span / peak headway | {stats.service_start}–{stats.service_end} / "
            f"{stats.peak_headway_min:.0f} min |",
            f"| Fleet | {total_fleet} × {stats.consist_cars}-car "
            f"`{stats.consist_family}` trainsets ({stats.revenue_fleet} peak revenue) |",
            f"| Peak network throughput | {network_peak_per_h:,.0f} passengers/hour |",
            f"| Practical service capacity | {practical_daily_capacity:,} passenger-trips/day |",
            f"| Annual paid-trip planning range | {annual_paid_low / 1e6:.1f}–"
            f"{annual_paid_high / 1e6:.1f} M |",
            "",
            "### Lines",
            "",
            "| Line | Length | Stations | Trainsets | Termini |",
            "|---|---:|---:|---:|---|",
            *line_rows,
            f"| **Total** | **{stats.route_km:.1f} km** | "
            f"**{stats.unique_station_count} unique** | **{total_fleet}** | |",
            "",
            "## Energy",
            "",
            "| Local measure | Value |",
            "|---|---:|",
            f"| Scheduled service | {energy_plan.scheduled_daily_train_journeys:,.0f} "
            f"one-way journeys / {energy_plan.scheduled_daily_train_km:,.0f} train-km/day |",
            f"| Annual traction demand | {energy_plan.annual_energy_kwh / 1e6:,.1f} GWh |",
            f"| Station/depot PV / storage | {stats.total_pv_kw / 1000:,.1f} MW / "
            f"{stats.total_battery_kwh / 1000:,.1f} MWh |",
            f"| Aggregate charging power | {stats.total_charging_kw / 1000:,.1f} MW |",
            f"| Dedicated solar plant | {energy_plan.solar_plant_kw / 1000:,.1f} MW |",
            f"| Residual grid/PPA import | {energy_plan.residual_grid_import_kwh / 1e6:,.1f} GWh/yr |",
            f"| Worst powered-stop gap | {worst_gap['line_id']}: "
            f"{worst_gap['worst_gap_km']:.1f} km / {worst_gap['worst_gap_kwh']:,.0f} kWh |",
            f"| Lowest traversal charging margin | {lowest_margin['line_id']}: "
            f"{lowest_margin['net_margin_kwh']:,.0f} kWh |",
            "",
            "## Capital And Funding",
            "",
            "| Local CAPEX bucket | Planning value |",
            "|---|---:|",
        ]
        out.extend(
            f"| {capital_labels.get(bucket.name, bucket.name)} | "
            f"{_fmt_usd(bucket.total_usd)} |"
            for bucket in headline_capital.buckets
        )
        out.extend(
            [
                f"| **Total city programme** | **{_fmt_usd(headline_capital.total_usd)}** |",
                "",
                "| Local funding measure | Planning value |",
                "|---|---:|",
                f"| Imported / external capital | {_fmt_usd(headline_capital.imported_usd)} "
                f"({headline_capital.imported_share:.1%}) |",
                f"| Domestic / local capital | {_fmt_usd(headline_capital.local_usd)} "
                f"({headline_capital.local_share:.1%}) |",
                f"| Annual public construction commitment | "
                f"{_fmt_usd(headline_plan.annual_public_construction_commitment_usd)} / yr "
                f"for {headline_plan.construction_years} years |",
                f"| Annual post-grace debt service | "
                f"{_fmt_usd(headline_plan.annual_debt_service_usd)} / yr |",
                f"| External capital saved vs default turnkey sensitivity | "
                f"{_fmt_usd(headline_turnkey.external_capital_avoided_usd)} |",
                f"| Capital + lifetime external interest saved | "
                f"{_fmt_usd(headline_turnkey.lifetime_external_financing_avoided_usd)} |",
            ]
        )
        if finance:
            out.append(
                f"| Annual OPEX | {_fmt_usd(finance['annual_opex_usd']['total'])} / yr |"
            )

        out.extend(
            [
                "",
                "## Local Evidence",
                "",
                "| Package | Current status | Evidence |",
                "|---|---|---|",
                f"| Finance | {'pass' if finance.get('passed') else 'missing/fail'} | "
                "[`summary.json`](engineering/finance/summary.json) |",
                f"| Native simulation + degraded cases | "
                f"{'pass' if simulation.get('passed') else 'missing/fail'} | "
                "[`validation-summary.json`](engineering/simulation/validation-summary.json) |",
                f"| SUMO timetable | "
                f"{'pass' if engineering['sumo'].get('simulation_passed') else 'missing/fail'} | "
                "[`summary.json`](engineering/sumo/summary.json) |",
                f"| Independent OSR/SUMO running-time cross-check | "
                f"{'pass' if operations_crosscheck.get('automatic_crosscheck_passed') else 'missing/fail'}; "
                f"junction/authority gate {'closed' if operations_crosscheck.get('authority_accepted') else 'open'} | "
                "[`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |",
                f"| GIS package | "
                f"{'pass' if engineering['gis'].get('generation_passed') else 'missing/fail'} | "
                "[`summary.json`](engineering/gis/summary.json) |",
                f"| Grid/charging/solar | "
                f"{'pass' if engineering['energy'].get('solver_passed') else 'missing/fail'} | "
                "[`summary.json`](engineering/energy/summary.json) |",
                f"| Operations, QA and maintenance | "
                f"{operations.get('totals', {}).get('assets', 0):,} assets / "
                f"{operations.get('totals', {}).get('maintenance_tasks', 0):,} tasks | "
                f"[`{operations_manifest.name}`](operations/{operations_manifest.name}) |",
                "",
                "## Local Files And Regeneration",
                "",
                "| File | Local role |",
                "|---|---|",
                "| [`design.toml`](design.toml) | Authoritative generated city design |",
                f"| [`{scenario_path.name}`]({scenario_path.name}) | Expanded simulator scenario |",
                f"| [`{screenshot_slug}.corridor.geojson`]"
                f"({screenshot_slug}.corridor.geojson) | GIS corridor and stations |",
                f"| [`{quality_file}`]({quality_file}) | Coverage, source and civil-quality gates |",
                "",
                "```bash",
                f"tools/automation/regenerate-city.sh {design['city']['slug']}",
                "```",
                "",
            ]
        )
        return "\n".join(out)

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
        f"≈ **{annual_paid_low / 1e6:,.1f} – {annual_paid_high / 1e6:,.1f} M "
        f"paid trips/year** at {capacity_utilization_low:.0%}–"
        f"{capacity_utilization_high:.0%} practical capacity utilisation"
        if practical_daily_capacity > 0 else "*(requires a valid service capacity)*"
    )

    out: list[str] = []
    out.append(f"# {stats.city_name} — Urban Rail Network\n")
    out.append(
        f"**Country:** {stats.country_iso} · "
        f"**Population:** {stats.population:,}\n"
    )
    out.append(
        "> [!IMPORTANT]\n"
        "> **Foreign-capital advantage:** against the default equivalent foreign-turnkey "
        f"case, this OSR plan avoids **{_fmt_usd(headline_turnkey.external_capital_avoided_usd)} "
        f"({headline_turnkey.external_capital_reduction:.1%}) of external capital** and "
        f"**{_fmt_usd(headline_turnkey.external_interest_avoided_usd)} of external interest**. "
        f"Capital plus saved interest totals **{_fmt_usd(headline_turnkey.lifetime_external_financing_avoided_usd)} "
        f"over the {headline_plan.tenor_years}-year financing life**. Both cases use the "
        f"same {headline_plan.external_rate:.1%} external rate and financing schedule; the "
        "turnkey external requirement is assumed debt-financed, and the benchmark "
        "remains an editable sensitivity, not a vendor quote.\n"
    )
    out.append(
        "Auto-planned by the OpenSourceRail design pipeline: "
        f"[`osr_geo`]({rel('design/city-generation/src/osr_geo/')}) rasterises "
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
    out.append(f"| Interchange-class stations | {stats.interchange_count} |")
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
        f"| Dedicated depot-service rotation fleet | "
        f"{stats.service_rotation_fleet} (off-peak service uses peak-fleet surplus) |"
    )
    out.append(
        f"| Spare + cold-reserve | "
        f"{stats.spare_fleet + stats.reserve_fleet} × "
        f"{stats.consist_cars}-car trainsets |"
    )
    out.append(f"| Peak headway | {stats.peak_headway_min:.0f} min |")
    out.append(
        "| Station spacing policy | 1.6 km central / 3 km urban / "
        "up to 7 km on suburban approaches and the lowest-demand outer fringe |"
    )
    out.append(
        "| City-centre consolidation | Cross-line platforms within the "
        "600 m station-complex envelope are emitted as one interchange |"
    )
    out.append(
        f"| Service hours | "
        f"{stats.service_start} – {stats.service_end} "
        f"({_hours(stats.service_start, stats.service_end):.1f} h/day) |"
    )
    out.append("")

    out.append("## Turnaround inspection and recharge\n")
    out.append(
        "During the 07:00–09:00 and 15:00–17:00 peaks, trains make the normal "
        "quick terminal turnback: no depot-service hold is inserted, allowing "
        "more battery depletion while the 20% dispatch-reserve gate remains "
        "mandatory. In the 6- and 12-minute lower-frequency windows, each "
        "line's deterministic energy controller may widen the published "
        "headway when actual charging delivery leaves a departing set below "
        "the 40% normal-service SoC target (up to 3× the published headway). "
        "This automatically matches offered off-peak service to available "
        "traction energy without buying a separate service-rotation fleet. "
        "In those lower-frequency windows, each "
        "train receives a **12-minute service slot** at its designated powered "
        "service point. This may be a staffed terminal platform or the main "
        "depot; only defects and maintenance require a depot move. Interior "
        "cleaning, exterior and "
        "running-gear walk-around, door/coupler/emergency-equipment checks, "
        "fault-log download, and a 150 kW low-C recharge run concurrently. "
        "A red defect holds the set for maintenance; a clear inspection "
        "returns it to the revenue rotation.\n"
    )
    out.append(
        "The fleet is sized for the 3-minute peaks; when service relaxes to "
        "6 or 12 minutes, the same peak fleet provides enough idle cover for "
        f"service-point work. Therefore **{stats.service_rotation_fleet} additional "
        "trainsets** are required for depot service; only the existing "
        f"{stats.spare_fleet} planned-maintenance spares and "
        f"{stats.reserve_fleet} cold-reserve sets are included in the "
        "rolling-stock, production-plant, maintenance, labour, and total "
        "CAPEX/OPEX figures below.\n"
    )
    out.append("## Distributed overnight stabling\n")
    out.append(
        "At service close, telemetry-healthy trainsets remain at selected "
        "powered passenger stations near their first morning departures. "
        "Every occupied station must provide at least 150 kW low-C charging, "
        "CCTV, remote traction isolation, protected emergency access, and an "
        "OCC-assigned train/track slot. Sets with red defects, overdue heavy "
        "maintenance, failed isolation, or failed security return to the "
        "main-heavy depot. OCC verifies charge completion and remote self-test "
        "before releasing all station-stabled sets together at service start. "
        "The generated default therefore builds one maintenance-focused main "
        "depot, not a parking depot at every terminus.\n"
    )
    ring_lines = [
        line
        for line in design.get("lines", [])
        if line.get("shape") == "ring" or line.get("is_ring")
    ]
    if ring_lines:
        ring_policy = design.get("operations", {}).get("ring_service", {})
        ring_dwells = [
            int(
                line.get(
                    "charging_dwell_seconds",
                    ring_policy.get("minimum_dwell_seconds", 120),
                )
            )
            for line in ring_lines
        ]
        dwell_text = (
            f"{ring_dwells[0]} seconds"
            if len(set(ring_dwells)) == 1
            else f"{min(ring_dwells)}–{max(ring_dwells)} seconds by line"
        )
        out.append(
            "Circumferential lines use the same demand-based stop-spacing "
            f"policy as radials ({float(ring_policy.get('station_spacing_multiplier', 1.0)):.1f}× "
            "the equivalent radial spacing), while every forced radial-transfer "
            "platform is retained. Charging-platform dwell is "
            f"{dwell_text}, calculated from one circuit's climate-adjusted "
            "energy and the line's aggregate charging power; non-charging "
            "halts keep their ordinary dwell.\n"
        )

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
    # (peak + service rotation + spare + cold-reserve, as written by `osr-design` to
    # `[[fleets]] trainset_count`). The footer must be the sum of
    # those — i.e. the full fleet (revenue + rotation + spare + cold-reserve),
    # not the revenue-only number — or the row totals don't add up.
    total_fleet = (
        stats.revenue_fleet
        + stats.service_rotation_fleet
        + stats.spare_fleet
        + stats.reserve_fleet
    )
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
    usable_battery_kwh = stats.consist_battery_kwh * 0.80
    out.append(
        f"| Onboard battery | {usable_battery_kwh:,.0f} kWh usable / "
        f"{stats.consist_battery_kwh:,.0f} kWh nameplate per trainset |"
    )
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
        f"({total_fleet_crush_pax:,} AW3 crush, incl. service rotation + spare + reserve) |"
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
        f"({total_fleet_crush_pax:,} AW3 crush, incl. service rotation + spare + reserve)"
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
        f"- **Scheduled one-way train journeys:** "
        f"**{scheduled_daily_journeys:,.0f}/day**"
    )
    out.append(
        f"- **Daily theoretical capacity from timetable:** "
        f"{daily_capacity_basis} = **{daily_theoretical:,.0f} passenger-trips/day**"
    )
    out.append(
        f"- **Practical daily service capacity** "
        f"({_PRACTICAL_CAPACITY_LOAD_FACTOR:.0%} load factor): "
        f"≈ **{practical_daily_capacity:,} passenger-trips/day**"
    )
    out.append(
        f"- **Planning annual paid-trip scenario** "
        f"(capacity-led): {daily_practical_str}\n"
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
        f"{usable_battery_kwh:,.0f} kWh usable "
        f"({stats.consist_battery_kwh:,.0f} kWh nameplate) battery covers running.\n"
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
    trainset_kwh_per_km = stats.consist_cars * _ENERGY_KWH_PER_CAR_KM
    dispatch_reserve_kwh = stats.consist_battery_kwh - usable_battery_kwh
    worst_gap = max(charging_audit, key=lambda row: row["worst_gap_kwh"])
    lowest_energy_margin = min(charging_audit, key=lambda row: row["net_margin_kwh"])
    reserve_ratio = usable_battery_kwh / max(float(worst_gap["worst_gap_kwh"]), 1e-9)
    battery_interpretation = (
        f"OK: {stats.consist_battery_kwh:,.0f} kWh nameplate, "
        f"{dispatch_reserve_kwh:,.0f} kWh protected reserve, and "
        f"{float(worst_gap['pack_margin_kwh']):,.0f} kWh usable margin across "
        f"the worst powered-stop gap ({worst_gap['line_id']})"
        if float(worst_gap["pack_margin_kwh"]) >= 0.0
        else (
            f"Fail: {abs(float(worst_gap['pack_margin_kwh'])):,.0f} kWh usable "
            f"short across the worst powered-stop gap ({worst_gap['line_id']})"
        )
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
        f"| Onboard battery adequacy | {reserve_ratio:.1f}× worst inter-charge run | "
        f"{battery_interpretation} |"
    )
    out.append(
        f"| Lowest traversal charging margin | "
        f"{float(lowest_energy_margin['net_margin_kwh']):,.0f} kWh | "
        f"{lowest_energy_margin['line_id']} after climate load, 98% conversion, "
        "and the required 10% operating margin |"
    )
    out.append(
        f"| PV daily yield proxy | {pv_daily_mwh:,.0f} MWh/day | "
        f"{energy_plan.peak_sun_hours:.1f} peak-sun-hour planning proxy before local derates |"
    )
    out.append(
        f"| Scheduled one-way train journeys | "
        f"{energy_plan.scheduled_daily_train_journeys:,.0f} / day | "
        "Train departures across both directions and all lines |"
    )
    out.append(
        f"| Scheduled train journey-km | "
        f"{energy_plan.scheduled_daily_train_km:,.0f} train-km/day | "
        "One-way train journeys × route length |"
    )
    out.append(
        f"| Annual service work | {energy_plan.annual_train_km / 1e6:,.1f} M train-km/yr | "
        f"Includes {_NON_REVENUE_TRAIN_KM_FACTOR:.0%} depot/deadhead factor |"
    )
    out.append(
        f"| Scheduled traction demand | {traction_daily_mwh:,.0f} MWh/day | "
        f"{energy_plan.annual_car_km / 1e6:.1f} M car-km/yr × "
        f"{_ENERGY_KWH_PER_CAR_KM:.1f} kWh/car-km |"
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
        "Distributed LFP buffer for charging peaks and grid outages |\n"
    )
    out.append(
        "Opportunity charging is checked line by line; ring trains remain in "
        "service while receiving the longer planned dwell at every powered platform."
    )
    out.append("")
    out.append("| Line | Powered stops | Climate-adjusted traversal | Delivered per traversal | Required-margin surplus | Worst powered-stop gap |")
    out.append("|---|---:|---:|---:|---:|---:|")
    for audit in charging_audit:
        out.append(
            f"| {audit['line_id']} | {audit['powered_stops']} | "
            f"{audit['traversal_kwh']:,.0f} kWh | "
            f"{audit['delivered_kwh']:,.0f} kWh | "
            f"{audit['net_margin_kwh']:,.0f} kWh | "
            f"{audit['worst_gap_km']:.1f} km / {audit['worst_gap_kwh']:,.0f} kWh |"
        )
    out.append("")

    rust_costs = design["costs"]
    out.extend(_rich_capex_section(design, rust_costs, stats, energy_plan))
    out.extend(_construction_qa_section(rel))
    out.extend(_funding_and_affordability_section(
        design, scenario, rust_costs, stats, energy_plan, rel,
        daily_pax_low=practical_daily_low,
        daily_pax_high=practical_daily_high,
        practical_daily_capacity=practical_daily_capacity,
        capacity_utilization_low=capacity_utilization_low,
        capacity_utilization_high=capacity_utilization_high,
    ))
    out.extend(_broad_economic_benefits_section(
        design, rust_costs, stats, energy_plan, rel,
        daily_pax_low=practical_daily_low,
        daily_pax_high=practical_daily_high,
        capacity_utilization_low=capacity_utilization_low,
        capacity_utilization_high=capacity_utilization_high,
    ))
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
    """Append the files, evidence, and reproducibility sections."""
    finance_path = design_path.parent / "engineering/finance/summary.json"
    if finance_path.is_file():
        finance = json.loads(finance_path.read_text())
        sources = finance.get("sources", {})
        design_hash = hashlib.sha256(design_path.read_bytes()).hexdigest()
        scenario_hash = hashlib.sha256(scenario_path.read_bytes()).hexdigest()
        source_paths = {
            "generator_sha256": _repo_root() / "tools/automation/generate-city-finance.py",
            "capital_model_sha256": _repo_root()
            / "design/city-generation/src/osr_scenario/capital.py",
            "network_finance_model_sha256": Path(__file__),
            "capex_costs_sha256": _repo_root() / "lib/templates/capex-costs.toml",
            "civil_cost_model_sha256": _repo_root()
            / "lib/templates/civil-cost-model.toml",
            "country_finance_sha256": _repo_root()
            / "lib/templates/country-finance.toml",
        }
        sources_current = all(
            sources.get(key) == hashlib.sha256(path.read_bytes()).hexdigest()
            for key, path in source_paths.items()
        )
        if (
            finance.get("schema_version") != 4
            or not finance.get("passed")
            or sources.get("design_sha256") != design_hash
            or sources.get("scenario_sha256") != scenario_hash
            or not sources_current
        ):
            raise ValueError(f"{finance_path} contains failed or stale financial evidence")
        capex = finance["capex_usd"]
        turnkey = finance.get("foreign_turnkey_comparator", {}).get(
            "default_comparison"
        )
        opex = finance["annual_opex_usd"]
        low = finance["cases"]["low_capacity_use"]
        high = finance["cases"]["high_capacity_use"]
        low_irr = low.get("project_irr")
        high_irr = high.get("project_irr")
        irr_text = (
            f"{low_irr:.1%} / {high_irr:.1%}"
            if low_irr is not None and high_irr is not None
            else "not resolved"
        )
        out.append("## Financial validation\n")
        out.append(
            "The machine-readable finance check reconciles the design-base CAPEX "
            "with the scenario-dependent solar plant and records deterministic "
            "cash-flow sensitivities. It is a planning screen, not financial close.\n"
        )
        out.append("| Check | Result |")
        out.append("|---|---:|")
        out.append(f"| Authoritative design-base CAPEX | {_fmt_usd(capex['authoritative_design_base'])} |")
        out.append(f"| Timetable-sized dedicated solar CAPEX | {_fmt_usd(capex['timetable_sized_dedicated_solar'])} |")
        out.append(f"| **Reconciled project CAPEX** | **{_fmt_usd(capex['reconciled_project_total'])}** |")
        out.append(
            f"| Imported / external-capital requirement | "
            f"{_fmt_usd(capex['imported_external_capital'])} "
            f"({float(capex['imported_percentage_of_total']):.1%}) |"
        )
        out.append(
            f"| Local-content / local-funding requirement | "
            f"{_fmt_usd(capex['local_capital'])} "
            f"({float(capex['local_percentage_of_total']):.1%}) |"
        )
        if turnkey:
            out.append(
                f"| Default foreign-turnkey external-capital comparison | "
                f"{_fmt_usd(turnkey['foreign_company_external_capital_usd'])}; "
                f"OSR saves {_fmt_usd(turnkey['osr_external_capital_saving_usd'])} "
                f"({float(turnkey['osr_external_capital_reduction']):.1%}) |"
            )
            out.append(
                f"| Lifetime external interest and combined financing saving | "
                f"{_fmt_usd(turnkey['osr_external_interest_saving_usd'])} interest; "
                f"{_fmt_usd(turnkey['osr_lifetime_external_financing_saving_usd'])} "
                f"capital + interest |"
            )
        out.append(f"| 15%–25% planning risk envelope | {_fmt_usd(capex['risk_envelope_15_percent'])}–{_fmt_usd(capex['risk_envelope_25_percent'])} |")
        out.append(f"| Annual OPEX | {_fmt_usd(opex['total'])} / yr |")
        out.append(f"| Low/high project NPV at 8% | {_fmt_usd(low['project_npv_usd_at_8_percent'])} / {_fmt_usd(high['project_npv_usd_at_8_percent'])} |")
        out.append(f"| Low/high project IRR | {irr_text} |")
        out.append(f"| Low/high steady-state DSCR | {low['steady_state_dscr']:.2f} / {high['steady_state_dscr']:.2f} |\n")
        out.append(
            "Evidence and limitations: "
            "[`engineering/finance/summary.json`](engineering/finance/summary.json).\n"
        )

    validation_path = design_path.parent / "engineering/simulation/validation-summary.json"
    if validation_path.is_file():
        validation = json.loads(validation_path.read_text())
        expected_hash = str(validation.get("scenario_sha256", ""))
        actual_hash = hashlib.sha256(scenario_path.read_bytes()).hexdigest()
        if expected_hash != actual_hash:
            raise ValueError(
                f"{validation_path} describes scenario SHA-256 "
                f"{expected_hash or '<missing>'}, but {scenario_path} is "
                f"{actual_hash}; rerun and update the validation evidence"
            )
        out.append("## Simulation validation\n")
        out.append(
            "The results below are measured `osr-sim` outputs for the "
            "scenario hash recorded in the city-local validation file, not "
            "timetable or spreadsheet projections.\n"
        )
        windows = validation.get("service_windows", [])
        if windows:
            out.append("| Local time | Headway | Operating treatment |")
            out.append("|---|---:|---|")
            for window in windows:
                out.append(
                    f"| {window['from']}–{window['to']} | "
                    f"{window['headway_min']} min | {window['treatment']} |"
                )
            out.append("")
        out.append("| Verified run | Result |")
        out.append("|---|---|")
        for run in validation.get("runs", []):
            active = int(run.get("depot_services_active_at_cutoff", 0))
            active_text = f" ({active} active at cutoff)" if active else ""
            service_text = ""
            if "service_completion_ratio" in run:
                service_text = (
                    f"; {run['service_completion_ratio']:.1%} of scheduled "
                    "train-km delivered"
                )
            warning_text = (
                f"; {int(run.get('soc_warning_events', 0))} SoC warnings"
                if run.get("soc_warning_events")
                else ""
            )
            adaptive_count = int(run.get("energy_adaptive_dispatches", 0))
            adaptive_text = (
                f"; {adaptive_count:,} energy-adapted off-peak departures, "
                f"maximum {int(run.get('maximum_effective_headway_min', 0))} min headway"
                if adaptive_count
                else ""
            )
            out.append(
                f"| {run['label']} | {run['train_km']:,.2f} train-km; "
                f"{run['energy_consumed_kwh']:,.2f} kWh consumed; "
                f"{run['energy_charged_kwh']:,.2f} kWh charged; "
                f"{run['depot_services_completed']:,} depot services completed"
                f"{active_text}; minimum SoC {run['minimum_soc_percent']:.0f}%; "
                f"{run['onboard_emergencies']} onboard emergencies; "
                f"{run['invariant_violations']} invariant violations"
                f"{service_text}{warning_text}{adaptive_text} |"
            )
        out.append("")
        resilience_cases = validation.get("resilience_cases", [])
        if resilience_cases:
            out.append("### Mandatory degraded-energy cases\n")
            out.append("| Case | Minimum SoC | Service delivered / required | Result |")
            out.append("|---|---:|---:|---:|")
            for case in resilience_cases:
                out.append(
                    f"| {case['label']} | {case['minimum_soc_percent']:.1f}% | "
                    f"{case['service_completion_ratio']:.1%} / "
                    f"{case['minimum_service_completion_ratio']:.0%} | "
                    f"{'pass' if case.get('passed') else 'FAIL'} |"
                )
            out.append("")
        out.append(
            f"**Simulation acceptance:** "
            f"{'passed' if validation.get('passed') else 'failed'} — "
            f"{validation.get('interpretation', 'see machine-readable evidence')}\n"
        )
        out.append(
            f"Full evidence and provenance: "
            f"[`engineering/simulation/validation-summary.json`]"
            f"(engineering/simulation/validation-summary.json)."
        )
        crosscheck_path = validation_path.parent / "operations-crosscheck.json"
        if crosscheck_path.is_file():
            crosscheck = json.loads(crosscheck_path.read_text())
            expected_sources = {
                "design_sha256": design_path,
                "sumo_summary_sha256": design_path.parent / "engineering/sumo/summary.json",
                "simulation_summary_sha256": validation_path,
            }
            if any(
                crosscheck.get("evidence_hashes", {}).get(key)
                != hashlib.sha256(path.read_bytes()).hexdigest()
                for key, path in expected_sources.items()
            ):
                raise ValueError(
                    f"{crosscheck_path} is stale; rerun the operations cross-check"
                )
            out.append("")
            out.append("### Independent OSR/SUMO running-time cross-check\n")
            out.append("| Line | OSR reference | SUMO mean | Difference | Result |")
            out.append("|---|---:|---:|---:|---|")
            for row in crosscheck.get("line_comparisons", []):
                out.append(
                    f"| {row['line_id']} | {row['osr_reference_trip_time_s']:.1f} s | "
                    f"{row['sumo_mean_trip_time_s']:.1f} s | "
                    f"{row['delta_percent_of_osr']:+.1f}% | "
                    f"{'pass' if row.get('passed') else 'FAIL'} |"
                )
            out.extend(
                [
                    "",
                    f"Automatic comparison status: **{'passed' if crosscheck.get('automatic_crosscheck_passed') else 'failed'}**. "
                    f"Junction/authority release: **{'accepted' if crosscheck.get('authority_accepted') else 'open'}**. "
                    "The generated SUMO model is an independent movement/timetable screen but not a conflict-capable junction release model. "
                    "See [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md).",
                ]
            )
        screenshot_dir = design_path.parent / "engineering/screenshots"
        dashboard = screenshot_dir / f"{screenshot_slug}-simulation-dashboard.png"
        visualizer = screenshot_dir / f"{screenshot_slug}-network-visualizer.png"
        if dashboard.is_file() and visualizer.is_file():
            out.append("")
            out.append("| Simulation dashboard | Network visualizer |")
            out.append("|---|---|")
            out.append(
                f"| ![{stats.city_name} energy and battery simulation dashboard]"
                f"(engineering/screenshots/{dashboard.name}) | "
                f"![{stats.city_name} simulator network visualizer]"
                f"(engineering/screenshots/{visualizer.name}) |"
            )
        out.append("")

    engineering_dir = design_path.parent / "engineering"
    engineering_summaries = {
        name: engineering_dir / name / "summary.json"
        for name in ("sumo", "gis", "energy")
    }
    if all(path.is_file() for path in engineering_summaries.values()):
        sumo = json.loads(engineering_summaries["sumo"].read_text())
        gis = json.loads(engineering_summaries["gis"].read_text())
        energy = json.loads(engineering_summaries["energy"].read_text())
        design_hash = hashlib.sha256(design_path.read_bytes()).hexdigest()
        scenario_hash = hashlib.sha256(scenario_path.read_bytes()).hexdigest()
        corridor_path = design_path.parent / f"{screenshot_slug}.corridor.geojson"
        corridor_hash = hashlib.sha256(corridor_path.read_bytes()).hexdigest()
        current = (
            sumo.get("simulation_passed")
            and sumo.get("design_sha256") == design_hash
            and sumo.get("corridor_sha256") == corridor_hash
            and gis.get("generation_passed")
            and gis.get("design_sha256") == design_hash
            and gis.get("corridor_sha256") == corridor_hash
            and gis.get("scenario_sha256") == scenario_hash
            and energy.get("solver_passed")
            and energy.get("design_sha256") == design_hash
            and energy.get("scenario_sha256") == scenario_hash
        )
        if not current:
            raise ValueError(
                f"{engineering_dir} contains failed or stale engineering evidence; "
                "rerun tools/automation/generate-city-engineering.py before publishing the README"
            )
        out.append("## SUMO, QGIS, and energy screening\n")
        out.append(
            "These are executed city-specific screening runs. They establish "
            "model consistency and expose planning findings; they are not a "
            "calibrated operational or construction acceptance.\n"
        )
        out.append("| Package | Current result |")
        out.append("|---|---|")
        out.append(
            f"| SUMO | {sumo.get('arrived_services', 0)}/"
            f"{sumo.get('scheduled_services', 0)} screening services arrived; "
            f"{len(sumo.get('input_issues', []))} input findings; "
            f"status `{sumo.get('simulation_status', 'unknown')}` |"
        )
        layers = gis.get("layers", {})
        out.append(
            f"| QGIS/GDAL | GeoPackage generated with "
            f"{layers.get('corridors', 0)} corridors, "
            f"{layers.get('stations', 0)} line platforms, "
            f"{layers.get('interchanges', 0)} interchange complexes, "
            f"{layers.get('civil_segments', 0)} civil segments, and "
            f"{len(gis.get('input_issues', []))} input findings |"
        )
        cases = energy.get("cases", {})
        grid_case = cases.get("peak_charge_grid_only", {})
        coordinated = cases.get("coordinated_daylight", {})
        out.append(
            f"| pandapower/pvlib | Solver "
            f"{'passed' if energy.get('solver_passed') else 'failed'}; "
            f"grid-only max transformer loading "
            f"{grid_case.get('maximum_transformer_loading_percent', 0):.1f}%; "
            f"coordinated-daylight max "
            f"{coordinated.get('maximum_transformer_loading_percent', 0):.1f}%; "
            f"{len(energy.get('design_findings', []))} open screening findings |"
        )
        out.append("")
        out.append(
            "Evidence: [`engineering/sumo/summary.json`]"
            "(engineering/sumo/summary.json), "
            "[`engineering/gis/summary.json`](engineering/gis/summary.json), "
            "and [`engineering/energy/summary.json`]"
            "(engineering/energy/summary.json).\n"
        )
        visual_dir = engineering_dir / "screenshots"
        visual_manifest_path = visual_dir / "manifest.json"
        if visual_manifest_path.is_file():
            visual_manifest = json.loads(visual_manifest_path.read_text())
            visual_sources = visual_manifest.get("sources", {})
            source_paths = {
                "sumo_summary_sha256": engineering_summaries["sumo"],
                "gis_summary_sha256": engineering_summaries["gis"],
                "energy_summary_sha256": engineering_summaries["energy"],
            }
            visuals_current = bool(visual_manifest.get("passed")) and (
                visual_sources.get("design_sha256") == design_hash
                and visual_sources.get("scenario_sha256") == scenario_hash
                and all(
                    visual_sources.get(key) == hashlib.sha256(path.read_bytes()).hexdigest()
                    for key, path in source_paths.items()
                )
            )
            screenshot_records = visual_manifest.get("screenshots", {})
            visuals_current = visuals_current and all(
                (visual_dir / record.get("path", "")).is_file()
                and hashlib.sha256((visual_dir / record.get("path", "")).read_bytes()).hexdigest()
                == record.get("sha256")
                for record in screenshot_records.values()
            )
            if not visuals_current:
                raise ValueError(
                    f"{visual_manifest_path} is stale; rerun the engineering visual renderer"
                )
            qgis_image = screenshot_records.get("qgis_engineering_map", {}).get("path")
            sumo_image = screenshot_records.get("sumo_validation", {}).get("path")
            if qgis_image and sumo_image:
                out.append("| QGIS engineering-layer review | SUMO executed timetable review |")
                out.append("|---|---|")
                out.append(
                    f"| ![{stats.city_name} QGIS engineering layers]"
                    f"(engineering/screenshots/{qgis_image}) | "
                    f"![{stats.city_name} SUMO timetable validation]"
                    f"(engineering/screenshots/{sumo_image}) |"
                )
                out.append("")

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
    out.append("")
    out.append(
        "Run the city regeneration command below to refresh the full engineering and "
        "operations bundle in this city folder.\n"
    )

    out.append("## Reproducibility\n")
    slug = stats.city_name.split(" ")[0].lower()
    out.append(
        f"```bash\n"
        f"# 1. raster bundle from OpenStreetMap (cached by query hash)\n"
        f"python -m osr_geo.cli --slug {slug}\n"
        f"\n"
        f"# 2. full generated design, scenario, engineering, and operations bundle\n"
        f"tools/automation/regenerate-city.sh {slug}\n"
        f"```\n"
        f"\n"
        f"The generated design, scenario, engineering, and operations evidence share "
        f"this canonical city directory.\n"
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
    """Canonical charging-microgrid CAPEX."""
    return float(costs.get("charging_microgrid_eur", 0.0))


def _qa_gates_for_readme() -> list[dict]:
    preferred = [
        "qa-00-design-freeze",
        "qa-10-carbody-structure",
        "qa-11-bogie-wheelset",
        "qa-12-traction-brake-battery",
        "qa-13-passenger-systems",
        "qa-14-onboard-control",
        "qa-15-first-article-trainset",
        "qa-20-survey-geotech",
        "qa-21-earthworks-drainage",
        "qa-22-trackform-rail",
        "qa-23-structures",
        "qa-24-stations-depots-plant",
        "qa-25-power-energy",
        "qa-26-wayside-comms-safety",
        "qa-30-integrated-trial-running",
    ]
    by_id = {str(g.get("id")): g for g in _QA_GATES}
    return [by_id[i] for i in preferred if i in by_id]


def _maintenance_rows_for_readme() -> list[dict]:
    preferred = [
        "rs-daily",
        "rs-weekly",
        "rs-monthly",
        "rs-wheel-reprofile",
        "rs-bogie-overhaul",
        "rs-body-overhaul",
        "station-daily",
        "station-weekly",
        "station-monthly",
        "station-annual",
        "track-weekly",
        "track-geometry",
        "switch-monthly",
        "structures-annual",
        "energy-daily",
        "energy-monthly",
        "energy-annual",
        "systems-daily",
        "systems-monthly",
        "systems-quarterly",
        "depot-tooling",
    ]
    by_id = {str(row.get("id")): row for row in _MAINTENANCE_INTERVALS}
    return [by_id[i] for i in preferred if i in by_id]


def _construction_qa_section(rel) -> list[str]:
    out: list[str] = []
    out.append("## Construction QA system\n")
    out.append(
        "Every locally built trainset and every fixed-asset package moves "
        "through owner-controlled hold points before the next construction "
        "stage starts. The machine-readable gate list is in "
        f"[`lib/templates/construction-qa.toml`]({rel('lib/templates/construction-qa.toml')}); "
        "the governing doctrine is "
        f"[RFC 0028]({rel('docs/rfcs/0028-construction-quality-assurance.md')}).\n"
    )
    out.append("| Gate | Domain | Asset coverage | Hold point / evidence |")
    out.append("|---|---|---|---|")
    for gate in _qa_gates_for_readme():
        gate_id = str(gate.get("id", ""))
        domain = str(gate.get("domain", ""))
        asset = str(gate.get("asset", ""))
        stage = str(gate.get("stage", ""))
        evidence = str(gate.get("evidence", ""))
        out.append(
            f"| `{gate_id}` | {domain} | {asset} | "
            f"{stage}: {evidence} |"
        )
    out.append("")
    return out


def _maintenance_schedule_section(
    rel,
    stats: NetworkStats,
    energy_plan: EnergyPlan,
) -> list[str]:
    total_fleet = (
        stats.revenue_fleet
        + stats.service_rotation_fleet
        + stats.spare_fleet
        + stats.reserve_fleet
    )
    policy = _MAINTENANCE_SCHEDULE.get("policy", {})
    escalation = str(policy.get("condition_based_escalation", ""))
    record_system = str(policy.get("record_system", ""))
    out: list[str] = []
    out.append("## Maintenance schedule system\n")
    out.append(
        f"Baseline scheduled work covers {total_fleet} trainsets, "
        f"{stats.unique_station_count} stations, {stats.route_km:.1f} route-km, "
        f"{stats.line_count} lines, and "
        f"{energy_plan.scheduled_daily_train_km:,.0f} scheduled train-km/day. "
        "Intervals are defined in "
        f"[`lib/templates/maintenance-schedule.toml`]({rel('lib/templates/maintenance-schedule.toml')}) "
        "and governed by "
        f"[RFC 0029]({rel('docs/rfcs/0029-maintenance-schedule-system.md')}).\n"
    )
    out.append("| Asset group | Cadence / trigger | Scope | Evidence owner |")
    out.append("|---|---|---|---|")
    for row in _maintenance_rows_for_readme():
        domain = str(row.get("domain", ""))
        cadence = str(row.get("cadence", ""))
        trigger = str(row.get("trigger", ""))
        scope = str(row.get("scope", ""))
        owner = str(row.get("owner", ""))
        evidence = str(row.get("evidence", ""))
        out.append(
            f"| {domain} | {cadence}; {trigger} | {scope} | "
            f"{evidence}; {owner} |"
        )
    out.append(f"\n_{escalation} {record_system}_\n")
    return out


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
    fleet_total = (
        stats.revenue_fleet
        + stats.service_rotation_fleet
        + stats.spare_fleet
        + stats.reserve_fleet
    )
    vehicle_count = fleet_total * _family_car_count(family)
    rs_unit = _TRAINSET_UNIT_USD.get(
        family, _TRAINSET_UNIT_USD["light-metro-3car"]
    )

    out: list[str] = []
    out.append("## CAPEX (planning grade)\n")
    out.append(
        "Base figures come from the `[costs]` block in "
        "`design.toml` — emitted by the `osr-design` Rust planner per "
        "RFC 0011 §9. Full generated bundles add the scenario-dependent "
        "dedicated solar plant and finance reconciliation under `build/`. "
        "The procurement basis is **USD direct-supplier "
        "planning pricing**; `*_eur` fields are explicit converted reporting "
        f"views at {_USD_TO_EUR:.2f} USD→EUR. "
        "**OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke "
        "architectural cladding), distributed overnight stabling that reduces "
        "depot parking and local commissioning-bay scope, at-grade depots "
        "without overhead bridge cranes, **trainset-family rolling-stock "
        "units** (for example "
        f"{_money_unit_usd(_LIGHT_METRO_3CAR_LOCAL_UNIT_USD)} per 3-car "
        "light-metro trainset, with the raw marketplace BOM retained only "
        "as an audit floor), commodity LFP packs + heavy-vehicle PMSM motors "
        "+ matched commercial traction controllers, **onboard-first train control "
        "with only residual wayside** (no trackside fibre backbone, no "
        "proprietary CBTC vendor stack, no trackside computer "
        "interlockings — the function moves into the trainset, already "
        "counted in rolling-stock CAPEX), no overhead catenary, a dedicated "
        "solar plant when the generated timetable exceeds station/depot PV, "
        "and self-EPC overhead. The rolling-stock line includes direct "
        "material, local assembly/labour, nominal per-train QA/acceptance, "
        "and modest local handover logistics. "
        "Fixtures, tooling, and production-readiness live in one shared "
        "national railway production plant at "
        f"{_money_unit_usd(_PRODUCTION_PLANT_PER_VEHICLE_USD)} per "
        "supported vehicle/car module, with "
        f"{_money_unit_usd(_PRODUCTION_PLANT_HIGH_PER_VEHICLE_USD)} "
        "retained as the high sensitivity check. That national asset is excluded "
        "from city CAPEX and costed once in the country brief; "
        "warranty, spares, and routine commissioning support are OPEX "
        "rather than repeated train CAPEX. "
        "`country-costs.toml` applies the per-country labour/material "
        "multiplier downstream where a local tender view is needed.\n"
    )

    out.append("### Civil works\n")
    out.append(
        "Rates are **design-derived planning targets**, generated from the "
        "parametric CAD quantity model and the reviewed benchmark calibration in "
        "`lib/templates/civil-cost-calibration.toml`. They are not quotations; "
        "foundation-zone schedules and normalized supplier offers remain release gates.\n"
    )
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
        "At-grade workshop and inspection facilities sized for maintenance, "
        "not fleet-wide parking. Healthy trainsets stable and recharge at "
        "powered passenger stations overnight; depot roads retain defect, "
        "wheel, wash, inspection, and heavy-maintenance functions.\n"
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
        "Rolling stock is costed by **local-owner trainset-family unit**, "
        "not by multiplying an inflated per-car price. The anchor "
        "3-car light-metro BOM floor is "
        f"{_LIGHT_METRO_3CAR_BOM_DIRECT_USD:,.0f} USD direct material plus "
        f"{_LIGHT_METRO_3CAR_ASSEMBLY_FRACTION * 100:.0f} % local assembly/labour allowance = "
        f"{_LIGHT_METRO_3CAR_BOM_WITH_ASSEMBLY_USD:,.0f} USD per 3-car "
        "consist. City CAPEX rounds this to a "
        f"{_money_unit_usd(_LIGHT_METRO_3CAR_LOCAL_UNIT_USD)} "
        "local-owner unit for a 3-car light-metro trainset, leaving only "
        "nominal QA/acceptance evidence and handover inside the trainset "
        "line. Fixtures, tooling, and production-readiness are carried in "
        "the railway production plant line below. Warranty, initial spares, "
        "and routine commissioning support are treated as operating costs. "
        "Motors, sensors, train-control computers, onboard batteries, roof "
        "PV, and charge hardware appear here ONLY — never re-billed "
        "elsewhere in the city cost stack.\n"
    )
    out.append("| 3-car light-metro anchor bucket | Basis | Cost |")
    out.append("|---|---|---|")
    out.append(f"| Direct material BOM floor | Welded frame, panels, glazing, doors, articulation/gangways, end couplers, bogies, suspension air supply, traction, batteries, HVAC, electronics, interiors | {_money_value_usd(_LIGHT_METRO_3CAR_BOM_DIRECT_USD)} |")
    out.append(f"| Local assembly/labour allowance | {_LIGHT_METRO_3CAR_ASSEMBLY_FRACTION * 100:.0f}% BOM allowance after one-shift clip-on body installation; includes fit-out, harnessing, paint, shop supervision, utilities, and rework reserve | {_money_value_usd(_LIGHT_METRO_3CAR_BOM_ASSEMBLY_USD)} |")
    out.append(f"| Nominal QA + handover allowance | Acceptance evidence, test dossier, local movement, manuals/training handover; warranty/spares stay in OPEX | {_money_value_usd(_LIGHT_METRO_3CAR_QA_HANDOVER_USD)} |")
    out.append(f"| **Total per 3-car trainset** | Local-owner production planning unit | **{_money_value_usd(_LIGHT_METRO_3CAR_LOCAL_UNIT_USD)}** |\n")
    out.append("| Item | Count | Unit | Subtotal |")
    out.append("|---|---|---|---|")
    out.append(
        f"| `{family}` (revenue + service rotation + spare + cold reserve) | "
        f"{fleet_total} | {_money_unit_usd(rs_unit)} | "
        f"{_money('rolling_stock')} |"
    )
    out.append("")

    technology = costs.get("technology_basis", {})
    if technology:
        out.append("#### 800 V procurement basis\n")
        out.append(
            "The following RFC 0021 commodity-component reconciliation is "
            "already included in the delivered rolling-stock and charging-site "
            "planning units; it is shown for auditability and is not additive.\n"
        )
        out.append("| Component | Current design basis |")
        out.append("|---|---:|")
        out.append(
            f"| Onboard architecture | {technology['onboard_architecture']} |"
        )
        out.append(
            f"| Gross traction battery | "
            f"{float(technology['gross_battery_kwh_per_car']):,.0f} kWh/car; "
            f"{float(technology['traction_battery_system_usd_per_car']):,.0f} USD/car |"
        )
        out.append(
            f"| PMSM motor + controller sets | "
            f"{int(technology['motor_controller_sets_per_car'])}/car @ "
            f"{float(technology['motor_controller_set_usd']):,.0f} USD/set |"
        )
        out.append(
            f"| Core electrical subtotal | "
            f"{float(technology['core_electrical_usd_per_car']):,.0f} USD/car; "
            f"{float(technology['core_electrical_usd_per_trainset']):,.0f} USD/trainset |"
        )
        out.append(
            f"| Normal 500 kWh / 500 kW station equipment | "
            f"{float(technology['station_equipment_total_usd']):,.0f} USD; "
            f"{float(technology['normal_integrated_charging_site_usd']):,.0f} USD integrated allowance |"
        )
        out.append("")

    out.append("### Shared national railway production plant\n")
    out.append(
        "This city does **not** carry a separate trainset factory. One national "
        "plant supplies every city through a phased production programme, while "
        "rails, viaducts, stations, and depots remain city/regional delivery scope. "
        "The national plant includes tooling, fixtures, plant services, "
        "production-readiness, and commissioning-bay setup. Standard 1 m fiberglass body moulds, "
        "dry clips, and compact gauges replace a full-length body mould and "
        "adhesive cure hall. It is costed per vehicle/car module, "
        "not per trainset, and the factory is sized to the largest single-city "
        "fleet programme rather than duplicated for every network. See "
        "[`../NATIONAL-BRIEF.md`](../NATIONAL-BRIEF.md).\n"
    )
    out.append("| City treatment | Indicative modules | National sizing unit | City CAPEX |")
    out.append("|---|---:|---:|---:|")
    out.append(
        f"| Fleet demand passed to national production plan | {vehicle_count} | "
        f"{_money_unit_usd(_PRODUCTION_PLANT_PER_VEHICLE_USD)} | "
        f"**{_money('production_plant')}** |"
    )
    out.append(
        f"| National high sensitivity (shown for scale, not added here) | {vehicle_count} | "
        f"{_money_unit_usd(_PRODUCTION_PLANT_HIGH_PER_VEHICLE_USD)} | "
        f"$0 |"
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
    out.append(f"| Shared national railway production plant (outside city CAPEX) | {_money('production_plant')} |")
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
    capital = city_capital_breakdown(costs, energy_plan.solar_plant_capex_usd)
    out.append("\n### Procurement origin and foreign-capital exposure\n")
    out.append("| Bucket | Total | Imported share | Imported / external capital | Local content / local funding |")
    out.append("|---|---:|---:|---:|---:|")
    labels = {
        "civil": "Civil works",
        "stations": "Stations",
        "depots": "Depots",
        "rolling_stock": "Rolling stock",
        "solar_plant": "Dedicated solar plant",
        "signalling": "Residual signalling / train control",
        "charging_microgrid": "Charging microgrids",
        "epc_overhead": "EPC / project services",
    }
    for bucket in capital.buckets:
        out.append(
            f"| {labels.get(bucket.name, bucket.name)} | {_fmt_usd(bucket.total_usd)} | "
            f"{bucket.imported_share:.0%} | {_fmt_usd(bucket.imported_usd)} | "
            f"{_fmt_usd(bucket.local_usd)} |"
        )
    out.append(
        f"| **Total city CAPEX** | **{_fmt_usd(capital.total_usd)}** | "
        f"**{capital.imported_share:.1%}** | **{_fmt_usd(capital.imported_usd)}** | "
        f"**{_fmt_usd(capital.local_usd)}** |\n"
    )
    return out


def _rel_to_repo_root(path: Path) -> str:
    """Return the relative-path prefix from `path` up to the repo root
    (containing Cargo.toml). Used to fix up links in the generated
    README regardless of how deeply the design folder is nested.

    `enumerate(cur.parents)` counts the *number of `..` segments* to
    walk: depth 0 = immediate parent (one `..` up), depth 3 = great-
    great-grandparent (four `..` up). For a design at
    `cities/catalogue/west-asia/Iraq/Samawah/`, the repo root is the 4th parent
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
    args = ap.parse_args(argv)
    text = render_readme(
        design_path=args.design,
        scenario_path=args.scenario,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text)
    print(f"wrote {args.out}  ({len(text.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
