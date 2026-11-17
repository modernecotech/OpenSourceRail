"""Bounded planning edits for the joined v0.7 synthetic corridor.

This recalculates quantities and a declared cost/energy allowance. It does not
run a vehicle, brake, structural or site evaluator and cannot release hardware.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal
from hashlib import sha256
import json
from math import ceil, isfinite, sqrt
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]
PRODUCER = Path("engineering/v07_reference_journey.py")
CONCEPT = Path("docs/reference-v07/concept.toml")
JOINED = Path("docs/reference-v07/integration/candidate.toml")
BASIS = Path("docs/reference-v07/cost/basis.csv")
BOM = Path("docs/reference-v07/manufacturing/bom.csv")
ROUTING = Path("docs/reference-v07/manufacturing/routing.csv")
LIFECYCLE = Path("docs/reference-v07/manufacturing/lifecycle-draft.json")

# Explicit concept-budget assumptions, not observed traction duty or timetable.
DWELL_S = 35.0
SPEED_M_S = 20.0
ACCEL_M_S2 = 0.4
DECEL_M_S2 = 0.6
GRID_KWH_PER_TRAIN_KM = 8.0
INCREMENTAL_LAUNCH_EFFICIENCY = 0.8
PEAK_HOURS_PER_DAY = 4
OTHER_HOURS_PER_DAY = 14
OTHER_TRAINS_PER_HOUR_PER_DIRECTION = 12
SERVICE_DAYS_PER_YEAR = 365
STATION_GWH_PER_YEAR_AT_BASELINE = 12.0
ENERGY_USD_PER_KWH = 0.12


def _sha(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _id(value: object) -> str:
    return _sha(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())


def _leg_time(distance_m: float, speed_m_s: float) -> tuple[float, float]:
    accel_distance = speed_m_s * speed_m_s / (2 * ACCEL_M_S2)
    brake_distance = speed_m_s * speed_m_s / (2 * DECEL_M_S2)
    if distance_m >= accel_distance + brake_distance:
        return (speed_m_s / ACCEL_M_S2 + speed_m_s / DECEL_M_S2
                + (distance_m - accel_distance - brake_distance) / speed_m_s, speed_m_s)
    peak = sqrt(2 * distance_m / (1 / ACCEL_M_S2 + 1 / DECEL_M_S2))
    return peak / ACCEL_M_S2 + peak / DECEL_M_S2, peak


def _running_time(route_km: float, stations: int, speed_m_s: float) -> tuple[float, float]:
    leg_s, attained_speed = _leg_time(route_km * 1000 / (stations - 1), speed_m_s)
    return (stations - 1) * leg_s + (stations - 2) * DWELL_S, attained_speed


def evaluate(*, route_km: float = 30.0, stations: int = 12,
             expected_parent_candidate_id: str, root: Path = ROOT) -> dict:
    """Return a source-bound planning scenario; caller supplies exact joined ID."""
    root = Path(root)
    paths = (PRODUCER, CONCEPT, JOINED, BASIS, BOM, ROUTING, LIFECYCLE)
    raw = {str(path): (root / path).read_bytes() for path in paths}
    sources = {name: _sha(content) for name, content in raw.items()}
    concept = tomllib.loads(raw[str(CONCEPT)].decode())
    joined = tomllib.loads(raw[str(JOINED)].decode())
    lifecycle = json.loads(raw[str(LIFECYCLE)])
    parent_id = joined["physical_candidate_id"]
    if (concept["configuration_id"] != joined["ancestry"]["planning_configuration_id"]
            or expected_parent_candidate_id != parent_id
            or lifecycle["joined_physical_candidate_id"] != parent_id
            or lifecycle["configuration_id"] != concept["configuration_id"]):
        raise ValueError("Mixed joined candidate or planning configuration")
    if any(lifecycle.get(key) is not False for key in
           ("external_transactions_performed", "posted", "ready_for_import",
            "physical_accepted", "manufacturing_release")):
        raise ValueError("Joined lifecycle draft cannot claim an ERP or physical release")
    for path in (BOM, ROUTING):
        assemblies = {row["assembly"] for row in csv.DictReader(raw[str(path)].decode().splitlines())}
        if not {"17m-powered-car", "10m-beam", "station-power-site"} <= assemblies:
            raise ValueError("Joined manufacturing assemblies are incomplete")
    if (concept["vehicle"]["cars_per_train"] != joined["vehicle"]["cars_per_train"]
            or concept["vehicle"]["driven_axles_per_train"] != joined["vehicle"]["driven_axles_per_train"]
            or concept["vehicle"]["dc_voltage_v"] != joined["performance"]["dc_nominal_voltage_v"]
            or concept["civil"]["span_m"] != joined["civil"]["beam_length_m"]):
        raise ValueError("Joined vehicle, power or civil interface differs")
    if (not isinstance(route_km, (int, float)) or isinstance(route_km, bool)
            or not isfinite(route_km) or not 1 <= route_km <= 100
            or not isinstance(stations, int) or isinstance(stations, bool)
            or not 2 <= stations <= 100):
        raise ValueError("Bounded finite route and station count required")
    route_km = float(route_km)
    original_km = concept["corridor"]["route_km"]
    original_stations = concept["corridor"]["stations"]
    if original_km != joined["corridor"]["route_km"] or original_stations != joined["corridor"]["station_count"]:
        raise ValueError("Joined corridor baseline differs")
    speed = joined["performance"]["speed_cap_kmh"] / 3.6
    if abs(speed - SPEED_M_S) > 1e-9:
        raise ValueError("Declared stop model speed differs from joined candidate")
    baseline_one_way_s, _ = _running_time(original_km, original_stations, speed)
    edited_one_way_s, attained_speed = _running_time(route_km, stations, speed)
    additional_round_trip_s = 2 * (edited_one_way_s - baseline_one_way_s)
    headway_s = concept["service"]["peak_headway_s"]
    baseline_active = concept["service"]["fleet_active"]
    baseline_reserve = concept["service"]["fleet_reserve"]
    # The published fleet is the control. Only the added cycle time is sized.
    active = max(1, ceil((baseline_active * headway_s + additional_round_trip_s) / headway_s - 1e-12))
    reserve = ceil(active * baseline_reserve / baseline_active)
    fleet = active + reserve
    tracks = concept["corridor"]["tracks"]
    bays_per_track = ceil(route_km * 1000 / concept["civil"]["span_m"])
    beams = bays_per_track * tracks
    supports = (bays_per_track + 1) * tracks
    bearings = beams * joined["civil"]["bearing_units_per_beam"]
    track_km = route_km * tracks
    grid_sites = ceil(route_km * 6 / original_km)
    quantities = {
        "powered_six_car_sets": fleet, "powered_cars": fleet * concept["vehicle"]["cars_per_train"],
        "powered_bogies": fleet * joined["vehicle"]["motorized_bogies_per_train"],
        "driven_axles": fleet * joined["vehicle"]["driven_axles_per_train"],
        "independent_brake_modules": fleet * joined["vehicle"]["independent_rail_brake_modules_per_train"],
        "roof_collectors": fleet * concept["vehicle"]["cars_per_train"],
        "door_openings": fleet * concept["vehicle"]["cars_per_train"] * joined["vehicle"]["doors_per_car"],
        "ten_metre_beams": beams, "beam_lifts": beams, "support_positions": supports,
        "bearings": bearings, "track_km": track_km, "stations": stations,
        "station_auxiliary_feeds": stations, "rectifier_grid_sites": grid_sites,
        "terminal_turnbacks": joined["corridor"]["terminal_turnbacks"],
    }
    if route_km == original_km and stations == original_stations:
        if (beams != concept["civil"]["beam_lifts"] or supports != concept["civil"]["support_positions"]
                or bearings != concept["civil"]["bearings"] or fleet != baseline_active + baseline_reserve):
            raise ValueError("Published baseline quantities do not reconcile")
    rows = list(csv.DictReader(raw[str(BASIS)].decode().splitlines()))
    priced = []
    for row in rows:
        component = row["component"]
        if component == "twenty-percent-of-counted-direct-cost":
            continue
        quantity = {
            "powered-six-car-set": fleet,
            "precast-10m-beam-and-bearings": beams,
            "pier-and-footing-position": supports,
            "beam-haul-lift-and-placement": beams,
            "two-rail-track-and-walkway": track_km,
            "station-launch-equipment-absent": 0,
            "rigid-overhead-return-sectioning-and-feeder": track_km,
            "rectifier-substation-and-grid-connection": grid_sites,
            "elevated-station-and-vertical-access": stations,
            "protected-terminal-turnback-and-control": quantities["terminal_turnbacks"],
            "station-auxiliary-grid-and-charge-feed": stations,
            "depot-tooling-land-and-utilities": 1,
            "commissioning-spares-and-rescue-assets": 1,
            "prototype-qualification-assurance-and-import-tax": 1,
        }.get(component)
        if quantity is None:
            raise ValueError("Unmapped cost component: " + component)
        rate = Decimal(row["unit_rate_usd_m"])
        if route_km == original_km and stations == original_stations:
            if (Decimal(row["quantity"]) != Decimal(str(quantity))
                    or Decimal(row["amount_usd_m"]) != Decimal(str(quantity)) * rate):
                raise ValueError("Published capital line does not reconcile: " + component)
        priced.append(dict(scope=row["scope"], component=component, quantity=quantity,
                           unit=row["unit"], amount_usd_m=float(Decimal(str(quantity)) * rate),
                           local_work_fraction=float(row["local_work_fraction"])))
    direct = sum(Decimal(str(row["amount_usd_m"])) for row in priced)
    contingency_rows = [row for row in rows if row["component"] == "twenty-percent-of-counted-direct-cost"]
    if len(contingency_rows) != 1:
        raise ValueError("One direct-cost contingency required")
    contingency = direct * Decimal(contingency_rows[0]["unit_rate_usd_m"])
    priced.append(dict(scope=contingency_rows[0]["scope"], component="twenty-percent-of-counted-direct-cost",
                       quantity=float(direct), unit="direct-cost-usd-m", amount_usd_m=float(contingency),
                       local_work_fraction=0.0))
    scopes = {}
    for row in priced:
        scopes[row["scope"]] = scopes.get(row["scope"], 0.0) + row["amount_usd_m"]
    if len(scopes) != 14:
        raise ValueError("Fourteen complete capital scopes required")
    installed = direct + contingency
    if route_km == original_km and stations == original_stations:
        if abs(installed - Decimal(str(concept["economics"]["installed_capital_usd_m"]))) > Decimal("0.000001"):
            raise ValueError("Joined baseline cost does not reconcile")
    one_way_trips_per_day = 2 * (PEAK_HOURS_PER_DAY * 3600 / headway_s
                                + OTHER_HOURS_PER_DAY * OTHER_TRAINS_PER_HOUR_PER_DIRECTION)
    normal_mass_kg = concept["vehicle"]["normal_analytical_t_per_car"] * 1000 * concept["vehicle"]["cars_per_train"]
    baseline_peak_speed = _running_time(original_km, original_stations, speed)[1]
    launch_delta_kwh = (0.5 * normal_mass_kg * (stations - 1) * attained_speed ** 2
                        - 0.5 * normal_mass_kg * (original_stations - 1) * baseline_peak_speed ** 2) / 3.6e6
    one_way_grid_kwh = (GRID_KWH_PER_TRAIN_KM * route_km
                        + launch_delta_kwh / INCREMENTAL_LAUNCH_EFFICIENCY)
    if one_way_grid_kwh <= 0:
        raise ValueError("Energy allowance outside its useful domain")
    annual_vehicle_kwh = one_way_grid_kwh * one_way_trips_per_day * SERVICE_DAYS_PER_YEAR
    annual_station_kwh = STATION_GWH_PER_YEAR_AT_BASELINE * 1e6 * stations / original_stations
    physical_id = (parent_id if route_km == original_km and stations == original_stations else
                   "osr-v07-joined-corridor-" + _id(dict(parent=parent_id, route_km=route_km,
                                                       stations=stations))[:24])
    result = dict(schema="osr-v07-reference-journey/1", parent_physical_candidate_id=parent_id,
                  physical_candidate_id=physical_id, planning_configuration_id=concept["configuration_id"],
                  corridor=dict(route_km=route_km, stations=stations, tracks=tracks,
                                synthetic_alignment=True, level_route_with_separate_grade_sizing=True),
                  fixed_interfaces=dict(cars_per_train=6, normal_places_per_train=276,
                                        driven_axles_per_train=24, dc_voltage_v=1500,
                                        ten_metre_beams=True, traction_battery=False),
                  service=dict(headway_s=headway_s, peak_places_per_hour_per_direction=concept["vehicle"]["normal_places_per_train"] * 3600 / headway_s,
                               baseline_active_trainsets=baseline_active, baseline_reserve_trainsets=baseline_reserve,
                               additional_round_trip_s=round(additional_round_trip_s, 6),
                               analytical_one_way_s=round(edited_one_way_s, 6),
                               active_trainsets=active, reserve_trainsets=reserve, trainsets=fleet,
                               station_dwell_s=DWELL_S, speed_cap_kmh=72),
                  energy=dict(planning_grid_kwh_per_one_way=round(one_way_grid_kwh, 6),
                              annual_vehicle_kwh=round(annual_vehicle_kwh, 3),
                              annual_station_kwh=round(annual_station_kwh, 3),
                              annual_total_kwh=round(annual_vehicle_kwh + annual_station_kwh, 3),
                              status="budget allowance, not measured traction or auxiliary duty",
                              base_kwh_per_train_km=GRID_KWH_PER_TRAIN_KM,
                              incremental_launch_efficiency_assumption=INCREMENTAL_LAUNCH_EFFICIENCY),
                  civil=dict(beam_lifts=beams, support_positions=supports, bearings=bearings,
                             track_km=track_km, station_count=stations, site_surveyed=False),
                  cost=dict(currency="USD", price_year=concept["price_year"],
                            direct_usd_m=float(direct), contingency_usd_m=float(contingency),
                            installed_capital_usd_m=float(installed), scope_totals_usd_m=scopes,
                            lines=priced, estimate_status="Class C concept, not supplier quote"),
                  manufacturing=dict(quantity_schedule=quantities, bom_path=str(BOM), routing_path=str(ROUTING),
                                     lifecycle_draft_path=str(LIFECYCLE), erpnext_posted=False,
                                     manufacturing_release=False),
                  assumptions=dict(peak_hours_per_day=PEAK_HOURS_PER_DAY, other_hours_per_day=OTHER_HOURS_PER_DAY,
                                   other_trains_per_hour_per_direction=OTHER_TRAINS_PER_HOUR_PER_DIRECTION,
                                   service_days_per_year=SERVICE_DAYS_PER_YEAR,
                                   station_gwh_per_year_at_baseline=STATION_GWH_PER_YEAR_AT_BASELINE,
                                   energy_usd_per_kwh=ENERGY_USD_PER_KWH,
                                   fleet_method="published 44+7 control plus incremental round-trip time; no absolute timetable recalibration"),
                  source_sha256=sources, physical_accepted=False, engineering_accepted=False,
                  manufacturing_release=False, operating_release=False)
    result["evaluation_id"] = _id(result)
    result["selection_id"] = _id(dict(evaluation_id=result["evaluation_id"],
                                       purpose="concept comparison for prototype quotation"))
    result["selection_purpose"] = "concept comparison for prototype quotation"
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the joined v0.7 digital corridor budget")
    parser.add_argument("--route-km", type=float, default=30.0)
    parser.add_argument("--stations", type=int, default=12)
    args = parser.parse_args()
    parent = tomllib.loads((ROOT / JOINED).read_text())["physical_candidate_id"]
    print(json.dumps(evaluate(route_km=args.route_km, stations=args.stations,
                              expected_parent_candidate_id=parent), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
