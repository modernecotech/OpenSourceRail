"""One Baghdad route, train, viaduct, power and 30-year cost calculation.

The two network lengths are declared planning controls. Their mapped lines are
schematic and cannot establish pier sites, grades or an airport entrance.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from math import asin, cos, isclose, radians, sin, sqrt
from pathlib import Path
import tomllib

from engineering.outline.baghdad_power import PowerAssumptions, PowerNetwork, compare_power
from engineering.outline.baghdad_viaduct import PlanningRates, SUPPORTED_SPANS_M, evaluate as civil_evaluate


ROOT = Path(__file__).resolve().parents[2]
CONFIG = Path("cities/Baghdad/system.toml")
SCHEMA = "opensourcerail.baghdad.joined-system.1"


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _id(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode()).hexdigest()


def _geo_km(coords: list[list[float]]) -> float:
    total = 0.0
    for (lon1, lat1), (lon2, lat2) in zip(coords, coords[1:]):
        p1, p2 = radians(lat1), radians(lat2)
        dp, dl = p2 - p1, radians(lon2 - lon1)
        a = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
        total += 2 * 6371.0088 * asin(min(1.0, sqrt(a)))
    return total


def load(root: Path = ROOT) -> dict:
    root = Path(root)
    cfg = tomllib.loads((root / CONFIG).read_text())
    if (cfg.get("schema") != "opensourcerail.baghdad.system.1"
            or cfg["tunnel_km"] != 0 or cfg["underground_stations"] != 0
            or cfg["revenue_guideway"] != "all elevated"
            or cfg["track_count"] != 2
            or cfg["alignment_surveyed"] or cfg["vertical_clearance_mapped"]
            or cfg["ground_characterised"] or cfg["airport_terminal_entrance_fixed"]):
        raise ValueError("Baghdad zero-tunnel digital planning scope differs")
    for key in ("first", "metropolitan", "waypoints"):
        path = root / cfg["map_sources"][key + "_path"]
        if not path.is_file() or _hash(path) != cfg["map_sources"][key + "_sha256"]:
            raise ValueError("Baghdad map source differs: " + key)
    if set(cfg["power_assumptions"]) != set(asdict(PowerAssumptions())):
        raise ValueError("All power assumptions must be in the one Baghdad scenario")
    if set(cfg["civil_rates"]) != set(asdict(PlanningRates())):
        raise ValueError("All civil planning rates must be in the one Baghdad scenario")
    for name, row in cfg["networks"].items():
        if (row["route_km"] <= 0 or row["stations"] <= row["lines"]
                or row["fleet_trainsets"] < row["active_trainsets"]):
            raise ValueError("Baghdad network controls differ: " + name)
    return cfg


def _lines(root: Path, cfg: dict, network: str) -> tuple[dict[str, float], str]:
    row = cfg["networks"][network]
    map_path = root / cfg["map_sources"][network + "_path"]
    geo = json.loads(map_path.read_bytes())
    if network == "first":
        lines = row["lines_km"]
        mapped = {f["properties"]["line"]: f["properties"]["rfi_nominal_km"]
                  for f in geo["features"] if f["geometry"]["type"] == "LineString"}
        if lines != mapped or not isclose(sum(lines.values()), row["route_km"], abs_tol=1e-6):
            raise ValueError("First-programme RFI line lengths differ from pinned map")
        return lines, "RFI nominal line lengths; drawn polylines are schematic"
    segments = [f for f in geo["features"] if f["geometry"]["type"] == "LineString"]
    raw = [_geo_km(f["geometry"]["coordinates"]) for f in segments]
    if not raw or min(raw) <= 0:
        raise ValueError("Metropolitan schematic route segments required")
    ratio = row["route_km"] / sum(raw)
    lines = {f"segment-{i + 1:02d}": km * ratio for i, km in enumerate(raw)}
    return lines, "Schematic GIS segment shares scaled to the declared 605.652 km planning length"


def _power_cost(case: dict, cfg: dict, network: dict) -> dict:
    rates = cfg["capital_rates_usd_m"]
    p = cfg["power_price_allowances_usd_m"]
    option = case["option"]
    supply = case["supply"]
    vehicle = case["vehicle"]
    if option == "overhead":
        line = supply["overhead_track_km"] * rates["overhead_and_feeders_per_track_km"]
        section_rate = 0.0
        fleet_delta_per_set = 0.0
        line_unit = rates["overhead_and_feeders_per_track_km"]
    else:
        line_unit = p["limited_conductor_per_track_km"] if option == "limited_conductor_battery" else p["protected_conductor_per_track_km"]
        section_rate = (p["limited_section_power_electronics_each"] if option == "limited_conductor_battery"
                        else p["protected_section_switchgear_each"] if option == "protected_conductor" else 0.0)
        line = supply["line_power_track_km"] * line_unit + supply["powered_section_count"] * section_rate
        contact_rate = (p["station_connector_sets_per_trainset"] if option == "station_battery"
                        else p["protected_shoe_sets_per_trainset"])
        battery_mwh = vehicle["traction_battery_kwh_per_train"] / 1000
        fleet_delta_per_set = (-p["roof_collection_credit_per_trainset"]
                               + vehicle["onboard_contact_sets"] / network["fleet_trainsets"] * contact_rate
                               + battery_mwh * (p["onboard_battery_per_mwh"]
                                                + p["onboard_battery_cooling_per_mwh"]))
    fleet_delta_per_set += (vehicle["driven_axles"] - vehicle["reference_driven_axles"]) * p["motor_inverter_module_per_axle"]
    fleet = network["fleet_trainsets"] * (rates["overhead_trainset"] + fleet_delta_per_set)
    extra_site_mw = max(0.0, supply["provisional_grid_site_rating_mw"]
                        - p["traction_supply_site_base_rating_mw"])
    grid = supply["grid_sites"] * (rates["traction_supply_site"]
                                  + extra_site_mw * p["additional_site_capacity_per_mw"])
    grid += (supply["station_charge_ports"] * supply["station_charge_port_mw"]
             * p["station_charger_per_mw_port"])
    grid += supply["stationary_buffer_mwh"] * p["station_buffer_per_mwh"]
    return dict(line_usd_m=line, grid_and_charging_usd_m=grid,
                fleet_usd_m=fleet, line_unit_usd_m=line_unit,
                section_unit_usd_m=section_rate,
                trainset_usd_m=rates["overhead_trainset"] + fleet_delta_per_set)


def _renewal_cost(event: dict, case: dict, cfg: dict, power_price: dict) -> float:
    p, rates = cfg["power_price_allowances_usd_m"], cfg["capital_rates_usd_m"]
    units = event["quantity"]
    item = event["component"]
    prices = {
        "onboard_traction_battery": p["onboard_battery_per_mwh"] + p["onboard_battery_cooling_per_mwh"],
        "station_buffer": p["station_buffer_per_mwh"],
        "charger_power_electronics": case["supply"]["station_charge_port_mw"] * p["station_charger_per_mw_port"],
        "grid_site_power_electronics": (rates["traction_supply_site"]
                                        + max(0.0, case["supply"]["provisional_grid_site_rating_mw"]
                                              - p["traction_supply_site_base_rating_mw"])
                                        * p["additional_site_capacity_per_mw"]),
        "line_section_protection": power_price["section_unit_usd_m"],
        "line_power_equipment": power_price["line_unit_usd_m"],
    }
    if item not in prices:
        raise ValueError("Unpriced Baghdad renewal item: " + item)
    return units * prices[item]


def evaluate(network: str, supply: str, *, span_m: int = 10,
             common_pier: bool = False, root: Path = ROOT) -> dict:
    root = Path(root)
    cfg = load(root)
    if network not in cfg["networks"] or supply not in (
            "station_battery", "protected_conductor", "limited_conductor_battery", "overhead"):
        raise ValueError("Known Baghdad network and supply option required")
    if span_m not in SUPPORTED_SPANS_M or type(common_pier) is not bool:
        raise ValueError("Declared Baghdad span and pier option required")
    n = cfg["networks"][network]
    v = cfg["vehicle"]
    annual_train_km = (n["active_trainsets"] * v["commercial_speed_kmh"]
                       * v["service_hours_per_day"] * v["service_days_per_year"])
    power_network = PowerNetwork(
        candidate_id=cfg["candidate_id"] + "-" + network,
        normal_places_per_train=v["normal_places_per_train"],
        route_km=n["route_km"], station_count=n["stations"], line_count=n["lines"],
        active_trainsets=n["active_trainsets"], fleet_trainsets=n["fleet_trainsets"],
        annual_train_km=annual_train_km, grid_site_count=n["traction_supply_sites"],
        train_mass_t=v["crowd_mass_t_per_train_before_supply"],
        train_energy_kwh_per_km=v["energy_kwh_per_train_km_overhead_comparator"],
        peak_headway_s=v["peak_headway_s"], dwell_s=v["dwell_s"],
        speed_cap_m_s=v["speed_cap_kmh"] / 3.6,
        service_hours_per_day=v["service_hours_per_day"],
        service_days_per_year=v["service_days_per_year"])
    power = compare_power(power_network, PowerAssumptions(**cfg["power_assumptions"]))[supply]
    lines, length_basis = _lines(root, cfg, network)
    civil = civil_evaluate(lines, span_m=span_m, common_pier=common_pier,
                           physical_candidate_id=power["physical_candidate_id"],
                           rates=PlanningRates(**cfg["civil_rates"]),
                           target_years=n["construction_finish_year"] - n["construction_start_year"] + 1,
                           train_crowd_mass_t=power["vehicle"]["mass_t"])
    cr = cfg["capital_rates_usd_m"]
    power_price = _power_cost(power, cfg, n)
    route_km, track_km = n["route_km"], n["route_km"] * cfg["track_count"]
    common = {
        "elevated_civil": civil["prices"]["changed_elevated_scope_usd"] / 1e6,
        "stations_access": n["stations"] * cr["station"],
        "track_walkways": track_km * cr["track_and_walkway_per_track_km"],
        "signalling_comms": route_km * cr["signalling_per_route_km"],
        "brake_protection_recovery": route_km * cr["wayside_brake_and_rescue_per_route_km"],
        "line_traction_supply": power_price["line_usd_m"],
        "grid_charging_buffers": power_price["grid_and_charging_usd_m"],
        "vehicles": power_price["fleet_usd_m"],
        "depots_control": n["depots"] * cr["depot"] + n["control_centres"] * cr["control_centre"],
        "land_utilities_disruption": route_km * cr["land_utilities_disruption_per_route_km"],
        "tooling_recovery": route_km * cr["tooling_and_recovery_per_route_km"] + cr["tooling_and_recovery_fixed"],
    }
    direct = sum(common.values())
    design = direct * cr["design_fraction"]
    test = direct * cr["testing_fraction"]
    subtotal = direct + design + test
    contingency = subtotal * cr["project_allowance_fraction"]
    installed = subtotal + contingency
    scopes = {**common, "design_assurance": design,
              "testing_commissioning": test, "project_allowance": contingency}
    op = cfg["operation_rates"]
    m = cfg["annual_power_maintenance_usd_m"]
    maintenance = 0.0
    if supply == "overhead":
        maintenance += power["supply"]["overhead_track_km"] * m["overhead_per_track_km"]
    elif supply == "protected_conductor":
        maintenance += power["supply"]["protected_conductor_track_km"] * m["protected_conductor_per_track_km"]
    elif supply == "limited_conductor_battery":
        maintenance += power["supply"]["protected_conductor_track_km"] * m["limited_conductor_per_track_km"]
    maintenance += (power["supply"]["station_charge_ports"]
                    * power["supply"]["station_charge_port_mw"] * m["station_charger_per_mw"])
    maintenance += power["supply"]["stationary_buffer_mwh"] * m["station_buffer_per_mwh"]
    maintenance += power["vehicle"]["fleet_battery_mwh"] * m["onboard_battery_per_mwh"]
    energy_usd_m_year = (power["energy"]["annual_grid_gwh"] * 1e6
                         * op["delivered_energy_usd_per_kwh"] / 1e6)
    annual_opex = (annual_train_km * op["non_energy_vehicle_operations_usd_per_train_km"] / 1e6
                   + n["stations"] * op["station_operations_usd_m_per_year"]
                   + energy_usd_m_year + maintenance)
    renewals = [{"year": 15, "component": "common_signalling_and_brake",
                 "usd_m": (common["signalling_comms"] + common["brake_protection_recovery"])
                 * op["year_15_common_systems_replacement_fraction"]},
                {"year": 25, "component": "fleet_major_renewal",
                 "usd_m": common["vehicles"] * op["year_25_fleet_replacement_fraction"]}]
    renewals.extend({"year": row["year"], "component": row["component"],
                     "usd_m": _renewal_cost(row, power, cfg, power_price)}
                    for row in power["renewal_events"])
    r = cfg["discount_rate_real"]
    annual_factor = sum((1 + r) ** -year for year in range(1, cfg["comparison_years"] + 1))
    life = installed + annual_opex * annual_factor + sum(
        row["usd_m"] / (1 + r) ** row["year"] for row in renewals)
    result = {
        "schema": SCHEMA, "parent_candidate_id": cfg["candidate_id"],
        "physical_candidate_id": _id({"network": network, "power": power["physical_candidate_id"],
                                      "civil": civil["civil_option_physical_id"]}),
        "selection_purpose": "equal-service planning comparison",
        "infrastructure": {"tunnel_km": cfg["tunnel_km"],
                           "underground_stations": cfg["underground_stations"],
                           "at_grade_km": 0.0, "elevated_route_km": route_km,
                           "track_count": cfg["track_count"]},
        "network": network, "supply": supply, "span_m": span_m, "common_pier": common_pier,
        "map_length_basis": length_basis,
        "service": {"route_km": route_km, "stations": n["stations"],
                    "normal_places_per_train": v["normal_places_per_train"],
                    "offered_places_per_hour_direction": v["normal_places_per_train"] * 3600 / v["peak_headway_s"],
                    "annual_train_km": annual_train_km,
                    "fleet_trainsets": n["fleet_trainsets"]},
        "vehicle": power["vehicle"], "traction": power["traction"],
        "energy": power["energy"], "supply_quantities": power["supply"],
        "civil": {"physical_candidate_id": civil["civil_option_physical_id"],
                  "evaluation_id": civil["evaluation_id"],
                  "quantities": civil["quantities"], "planning_prices": civil["prices"],
                  "physical_screen": civil["physical_screen"], "delivery": civil["delivery"]},
        "capital_usd_m": {"scope_rows": scopes, "direct": direct,
                          "design": design, "test": test, "project_allowance": contingency,
                          "installed": installed},
        "operation_usd_m_year": {"energy": energy_usd_m_year,
                                 "non_energy_and_station": annual_opex - energy_usd_m_year - maintenance,
                                 "power_maintenance": maintenance, "total": annual_opex},
        "renewals_usd_m": renewals,
        "whole_life_30y_present_usd_m": life,
        "source_sha256": {str(CONFIG): _hash(root / CONFIG),
                          **{cfg["map_sources"][key + "_path"]:
                             cfg["map_sources"][key + "_sha256"] for key in ("first", "metropolitan", "waypoints")},
                          "engineering/outline/baghdad_system.py": _hash(Path(__file__)),
                          "engineering/outline/baghdad_power.py": _hash(root / "engineering/outline/baghdad_power.py"),
                          "engineering/outline/baghdad_viaduct.py": _hash(root / "engineering/outline/baghdad_viaduct.py")},
        "site_or_physical_accepted": False,
    }
    result["evaluation_id"] = _id(result)
    return result


def compare(network: str, root: Path = ROOT) -> dict:
    cfg = load(root)
    fixed_span = cfg["selected_span_m"]
    fixed_common = cfg["selected_pier_family"] == "common-crosshead"
    supply_rows = {key: evaluate(network, key, span_m=fixed_span,
                                 common_pier=fixed_common, root=root)
                   for key in ("station_battery", "protected_conductor",
                               "limited_conductor_battery", "overhead")}
    preferred = min(supply_rows, key=lambda key: supply_rows[key]["whole_life_30y_present_usd_m"])
    civil_rows = {f"{span}m-{'common' if common else 'separate'}":
                  evaluate(network, preferred, span_m=span, common_pier=common, root=root)
                  for span in SUPPORTED_SPANS_M for common in (False, True)}
    return {"schema": "opensourcerail.baghdad.system-comparison.1",
            "network": network, "candidate_id": cfg["candidate_id"],
            "digital_cost_leader": preferred,
            "preferred_offwire": preferred != "overhead",
            "selected_digital_civil_family": f"{fixed_span}m-{'common' if fixed_common else 'separate'}",
            "power_cases": supply_rows, "civil_cases": civil_rows,
            "physical_accepted": False}


def release_summary(root: Path = ROOT) -> dict:
    """Compact public quantities and one cost per named candidate."""
    cfg = load(root)
    networks = {}
    for name in ("first", "metropolitan"):
        comparison = compare(name, root)
        selected = comparison["power_cases"][comparison["digital_cost_leader"]]
        networks[name] = {
            "route_km": selected["service"]["route_km"],
            "tunnel_km": selected["infrastructure"]["tunnel_km"],
            "underground_stations": selected["infrastructure"]["underground_stations"],
            "elevated_route_km": selected["infrastructure"]["elevated_route_km"],
            "stations_planning_allowance": selected["service"]["stations"],
            "digital_cost_leader": comparison["digital_cost_leader"],
            "selected_digital_civil_family": comparison["selected_digital_civil_family"],
            "selected_candidate_id": selected["physical_candidate_id"],
            "selected_evaluation_id": selected["evaluation_id"],
            "selected_capital_scope_usd_m": selected["capital_usd_m"]["scope_rows"],
            "selected_annual_opex_usd_m": selected["operation_usd_m_year"],
            "selected_renewals_usd_m": selected["renewals_usd_m"],
            "power_cases": {key: {
                "physical_candidate_id": row["physical_candidate_id"],
                "installed_capital_usd_m": row["capital_usd_m"]["installed"],
                "whole_life_30y_present_usd_m": row["whole_life_30y_present_usd_m"],
                "annual_grid_gwh": row["energy"]["annual_grid_gwh"],
                "train_crowd_mass_t": row["vehicle"]["mass_t"],
                "driven_axles": row["vehicle"]["driven_axles"],
                "battery_kwh_per_train": row["vehicle"]["traction_battery_kwh_per_train"],
                "station_charge_port_mw": row["supply_quantities"]["station_charge_port_mw"],
                "station_charge_ports": row["supply_quantities"]["station_charge_ports"],
                "protected_conductor_track_km": row["supply_quantities"]["protected_conductor_track_km"],
                "overhead_track_km": row["supply_quantities"]["overhead_track_km"],
                "civil_beams": row["civil"]["quantities"]["beam_count"],
                "civil_piers": row["civil"]["quantities"]["pier_foundation_count"],
            } for key, row in comparison["power_cases"].items()},
            "civil_cases": {key: {
                "civil_option_physical_id": row["civil"]["physical_candidate_id"],
                "direct_elevated_civil_usd_m": row["civil"]["planning_prices"]["changed_elevated_scope_usd"] / 1e6,
                "installed_capital_usd_m": row["capital_usd_m"]["installed"],
                "beam_count": row["civil"]["quantities"]["beam_count"],
                "pier_foundation_count": row["civil"]["quantities"]["pier_foundation_count"],
                "hook_surrogate_t_per_beam": row["civil"]["physical_screen"]["length_and_load_scaled_hook_surrogate_t_per_beam"],
                "factory_yards_needed": row["civil"]["delivery"]["factory_yards_needed_at_declared_rate"],
                "erection_fronts_needed": row["civil"]["delivery"]["erection_fronts_needed_at_declared_rate"],
                "structurally_qualified": False,
            } for key, row in comparison["civil_cases"].items()},
            "completion_year_planning": cfg["networks"][name]["construction_finish_year"],
        }
    result = {"schema": "opensourcerail.baghdad.public-cost-comparison.1",
              "candidate_id": cfg["candidate_id"], "source_sha256": {
                  str(CONFIG): _hash(root / CONFIG),
                  **{cfg["map_sources"][key + "_path"]: cfg["map_sources"][key + "_sha256"]
                     for key in ("first", "metropolitan", "waypoints")},
                  "engineering/outline/baghdad_power.py": _hash(root / "engineering/outline/baghdad_power.py"),
                  "engineering/outline/baghdad_viaduct.py": _hash(root / "engineering/outline/baghdad_viaduct.py"),
                  "engineering/outline/baghdad_system.py": _hash(Path(__file__)),
              }, "networks": networks,
              "scope": "digital planning comparison; no site or physical acceptance"}
    result["evaluation_id"] = _id(result)
    return result


def main() -> None:
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--network", choices=("first", "metropolitan"), default="first")
    p.add_argument("--supply", choices=("station_battery", "protected_conductor",
                                       "limited_conductor_battery", "overhead"))
    p.add_argument("--span-m", type=int, choices=SUPPORTED_SPANS_M, default=10)
    p.add_argument("--common-pier", action="store_true")
    p.add_argument("--summary", action="store_true")
    p.add_argument("--write-results", action="store_true")
    p.add_argument("--check-results", action="store_true")
    args = p.parse_args()
    if args.write_results or args.check_results:
        target = ROOT / "cities/Baghdad/system-results.json"
        raw = (json.dumps(release_summary(), indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
        if args.check_results:
            if not target.is_file() or target.read_bytes() != raw:
                raise ValueError("Baghdad joined system results differ from current inputs")
            print("Baghdad system results current", sha256(raw).hexdigest())
        else:
            target.write_bytes(raw)
            print("wrote", target, sha256(raw).hexdigest())
        return
    result = (evaluate(args.network, args.supply, span_m=args.span_m,
                       common_pier=args.common_pier) if args.supply else compare(args.network))
    if args.summary and args.supply is None:
        result = {"network": args.network, "digital_cost_leader": result["digital_cost_leader"],
                  "power_cases": {name: {"capital_usd_m": row["capital_usd_m"]["installed"],
                                         "whole_life_30y_present_usd_m": row["whole_life_30y_present_usd_m"],
                                         "train_mass_t": row["vehicle"]["mass_t"],
                                         "annual_grid_gwh": row["energy"]["annual_grid_gwh"]}
                                  for name, row in result["power_cases"].items()}}
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
