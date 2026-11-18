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
from xml.etree import ElementTree

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


def load(root: Path = ROOT, network: str | None = None) -> dict:
    root = Path(root)
    cfg = tomllib.loads((root / CONFIG).read_text())
    if (cfg.get("schema") != "opensourcerail.baghdad.system.1"
            or cfg["tunnel_km"] != 0 or cfg["underground_stations"] != 0
            or cfg["revenue_guideway"] != "all elevated"
            or cfg["track_count"] != 2
            or cfg["alignment_surveyed"] or cfg["vertical_clearance_mapped"]
            or cfg["ground_characterised"] or cfg["airport_terminal_entrance_fixed"]):
        raise ValueError("Baghdad zero-tunnel digital planning scope differs")
    if network not in (None, "first", "metropolitan"):
        raise ValueError("Known Baghdad network required")
    map_keys = (("first", "metropolitan", "waypoints") if network is None else
                ("first", "waypoints") if network == "first" else ("metropolitan",))
    for key in map_keys:
        path = root / cfg["map_sources"][key + "_path"]
        if not path.is_file() or _hash(path) != cfg["map_sources"][key + "_sha256"]:
            raise ValueError("Baghdad map source differs: " + key)
    if set(cfg["power_assumptions"]) != set(asdict(PowerAssumptions())):
        raise ValueError("All power assumptions must be in the one Baghdad scenario")
    if set(cfg["civil_rates"]) != set(asdict(PlanningRates())):
        raise ValueError("All civil planning rates must be in the one Baghdad scenario")
    for name, row in cfg["networks"].items():
        if (row["route_km"] <= 0 or row["stations"] <= row["lines"]
                or not row["construction_start_year"] <= row["civil_start_year"]
                       <= row["civil_finish_year"] <= row["construction_finish_year"]
                or row["fleet_trainsets"] < row["active_trainsets"]):
            raise ValueError("Baghdad network controls differ: " + name)
    return cfg


def _lines(root: Path, cfg: dict, network: str) -> tuple[dict[str, float], str, dict]:
    row = cfg["networks"][network]
    map_path = root / cfg["map_sources"][network + "_path"]
    geo = json.loads(map_path.read_bytes())
    if network == "first":
        lines = row["lines_km"]
        features = [f for f in geo["features"] if f["geometry"]["type"] == "LineString"]
        mapped = {f["properties"]["line"]: f["properties"]["rfi_nominal_km"]
                  for f in features}
        if lines != mapped or not isclose(sum(lines.values()), row["route_km"], abs_tol=1e-6):
            raise ValueError("First-programme RFI line lengths differ from pinned map")
        drawn = sum(_geo_km(f["geometry"]["coordinates"]) for f in features)
        return lines, "RFI nominal line lengths; drawn polylines are schematic", {
            "drawn_polyline_km": drawn, "costed_route_km": row["route_km"],
            "planning_length_adjustment_km": row["route_km"] - drawn,
            "all_costed_sections_have_service_paths": True, "unassigned_sections_km": {}}
    segments = [f for f in geo["features"] if f["geometry"]["type"] == "LineString"
                and f["properties"].get("map_layer") == "railway route"]
    route_ids = {f["properties"].get("route_id") for f in segments}
    groups = row["service_groups"]
    served = set().union(*(set(parts) for parts in groups.values()))
    unassigned = row["unassigned_sections"]
    if (len(groups) != row["lines"] or any(not set(parts) <= route_ids for parts in groups.values())
            or served & set(unassigned) or served | set(unassigned) != route_ids
            or any(not reason.strip() for reason in unassigned.values())
            or not {"B-A01", "B-A02", "B-A03", "B-A04", "B-A05", "B-A06"} <= route_ids
            or any(f["properties"].get("standalone_shuttle") for f in segments)):
        raise ValueError("Independent metropolitan through-service route schedule differs")
    raw = [_geo_km(f["geometry"]["coordinates"]) for f in segments]
    if not raw or min(raw) <= 0:
        raise ValueError("Metropolitan schematic route segments required")
    ratio = row["route_km"] / sum(raw)
    lines = {f["properties"]["route_id"]: km * ratio for f, km in zip(segments, raw)}
    if len(lines) != len(segments):
        raise ValueError("Unique metropolitan route IDs required")
    return lines, "Independent GIS physical sections scaled to the declared 605.652 km planning length", {
        "drawn_polyline_km": sum(raw), "costed_route_km": row["route_km"],
        "planning_length_adjustment_km": row["route_km"] - sum(raw),
        "all_costed_sections_have_service_paths": not unassigned,
        "unassigned_sections_km": {key: lines[key] for key in sorted(unassigned)},
        "unassigned_section_purposes": dict(sorted(unassigned.items()))}


def _selected_input_id(cfg: dict, network: str) -> str:
    """Identify only the selected network and common railway assumptions."""
    shared = {key: value for key, value in cfg.items()
              if key not in ("networks", "map_sources")}
    selected = {"common": shared, "network": cfg["networks"][network],
                "map": {key: cfg["map_sources"][network + "_" + key]
                        for key in ("path", "sha256")}}
    if network == "first":
        selected["waypoints"] = {key: cfg["map_sources"]["waypoints_" + key]
                                  for key in ("path", "sha256")}
    return _id(selected)


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


def _control_electronics(cfg: dict, network: dict, power: dict,
                         capital_scopes: dict) -> dict:
    """Count the selected control equipment within existing capital scopes."""
    c = cfg["control_electronics"]
    p = cfg["control_electronics_price_allocations_usd_m"]
    v = cfg["vehicle"]
    fleet = network["fleet_trainsets"]
    cars = fleet * v["cars_per_train"]
    doors = cars * v["door_openings_per_car_each_side"] * 2
    bogies = cars * 2
    sections = power["supply"]["powered_section_count"]
    quantities = {
        "atp_channels": fleet * c["atp_channels_per_train"],
        "radio_links": fleet * c["radio_links_per_train"],
        "tcms_nodes": cars * c["tcms_nodes_per_car"],
        "door_controllers": doors * c["door_controllers_per_opening"],
        "brake_controllers": bogies * c["brake_controllers_per_bogie"],
        "train_service_power_units": fleet * c["train_service_power_units"],
        "shoe_status_channels": (fleet * cfg["vehicle_geometry"]["shoe_sets_per_train"]
                                 * c["shoe_status_channels_per_shoe_set"]
                                 if power["supply"]["protected_conductor_track_km"] > 0 else 0),
        "inverter_control_units": fleet * c["inverter_control_units_per_train"],
        "station_dispatch_controllers": network["stations"] * c["station_dispatch_controllers"],
        "section_control_gateways": sections * c["section_control_gateways"],
        "grid_protection_gateways": network["traction_supply_sites"] * c["grid_protection_gateways"],
        "occ_equipment_sets": network["control_centres"] * c["occ_equipment_sets"],
    }
    allocations = {
        "vehicles": sum(quantities[key] * p[price] for key, price in (
            ("atp_channels", "atp_channel"), ("radio_links", "radio_link"),
            ("tcms_nodes", "tcms_node"), ("door_controllers", "door_controller"),
            ("brake_controllers", "brake_controller"),
            ("train_service_power_units", "train_service_power_unit"),
            ("shoe_status_channels", "shoe_status_channel"),
            ("inverter_control_units", "inverter_control_unit"))),
        "stations_access": quantities["station_dispatch_controllers"] * p["station_dispatch_controller"],
        "signalling_comms": (quantities["section_control_gateways"] * p["section_control_gateway"]
                             + network["route_km"] * p["train_detection_per_route_km"]),
        "grid_charging_buffers": quantities["grid_protection_gateways"] * p["grid_protection_gateway"],
        "depots_control": quantities["occ_equipment_sets"] * p["occ_equipment_set"],
    }
    if any(amount < 0 or amount > capital_scopes[scope]
           for scope, amount in allocations.items()):
        raise ValueError("Control equipment allocation exceeds its parent capital scope")
    installed = cfg["control_electronics_installed"]
    train_items = {
        "atp_channel": c["atp_channels_per_train"],
        "radio_link": c["radio_links_per_train"],
        "tcms_node": v["cars_per_train"] * c["tcms_nodes_per_car"],
        "door_controller": v["cars_per_train"] * v["door_openings_per_car_each_side"] * 2
                           * c["door_controllers_per_opening"],
        "brake_controller": v["cars_per_train"] * 2 * c["brake_controllers_per_bogie"],
        "train_service_power_unit": c["train_service_power_units"],
        "shoe_status_channel": (cfg["vehicle_geometry"]["shoe_sets_per_train"]
                                * c["shoe_status_channels_per_shoe_set"]
                                if power["supply"]["protected_conductor_track_km"] > 0 else 0),
        "inverter_control_unit": c["inverter_control_units_per_train"],
    }
    if (any(type(count) is not int or count < 0 for count in train_items.values())
            or any(type(value) not in (float, int) or value < 0 for value in installed.values())):
        raise ValueError("Baghdad installed control schedule needs positive counts and nonnegative allowances")
    mass_kg = sum(count * installed[name + "_kg"] for name, count in train_items.items())
    mass_kg += installed["harness_enclosure_kg_per_train"]
    continuous_w = sum(count * installed[name + "_w"] for name, count in train_items.items())
    if (mass_kg <= 0 or continuous_w <= 0
            or mass_kg > c["train_mass_allowance_t"] * 1000
            or continuous_w > c["train_auxiliary_power_allowance_kw"] * 1000
            or continuous_w > cfg["service_power"]["control_continuous_kw"] * 1000):
        raise ValueError("Baghdad installed control mass or continuous power exceeds train reserve")
    return {"quantities": quantities, "allocation_within_capital_scopes_usd_m": allocations,
            "train_mass_allowance_within_base_t": c["train_mass_allowance_t"],
            "train_auxiliary_power_allowance_kw": c["train_auxiliary_power_allowance_kw"],
            "installed_train_items": train_items,
            "installed_train_mass_kg": mass_kg,
            "installed_train_continuous_w": continuous_w,
            "mass_residual_kg": c["train_mass_allowance_t"] * 1000 - mass_kg,
            "control_power_residual_w": c["train_auxiliary_power_allowance_kw"] * 1000 - continuous_w,
            "basis": "Baghdad-specific installed equipment and harness planning schedule within vehicle mass, power and price reserves"}


def _station_interfaces(cfg: dict) -> dict:
    """Screen the common straight-station train and conductor datums."""
    v, s = cfg["vehicle_geometry"], cfg["station_geometry"]
    doors = v["door_centres_m"]
    if (len(doors) != cfg["vehicle"]["door_openings_per_car_each_side"]
            or doors != sorted(doors) or len(set(doors)) != len(doors)
            or v["car_body_length_m"] <= 0 or v["body_width_m"] <= 0
            or v["door_clear_width_m"] <= 0 or v["floor_above_rail_m"] <= 0
            or v["shoe_sets_per_train"] <= 0 or len(v["bogie_centres_m"]) != 2):
        raise ValueError("Baghdad vehicle geometry is incomplete or inconsistent")
    gap = s["straight_platform_edge_offset_m"] - v["body_width_m"] / 2
    end = v["car_body_length_m"] / 2 - max(abs(x) for x in doors) - v["door_clear_width_m"] / 2
    between = min(b - a - v["door_clear_width_m"] for a, b in zip(doors, doors[1:]))
    margin = (s["platform_clear_length_m"] - v["train_length_m"]) / 2
    conductor_clear = v["contact_rail_outboard_offset_m"] - v["body_width_m"] / 2
    if (not 0 < gap <= 0.15 or end <= 0 or between <= 0 or margin <= 0
            or conductor_clear <= 0.2 or
            not isclose(s["straight_track_centre_spacing_m"],
                        s["island_width_m"] + 2 * s["straight_platform_edge_offset_m"],
                        abs_tol=1e-6)):
        raise ValueError("Baghdad straight-station or door geometry fails its planning screen")
    return {"vehicle": v, "station": s, "static_body_edge_gap_m": gap,
            "door_end_clearance_m": end, "minimum_door_separation_m": between,
            "centred_platform_end_margin_m": margin,
            "conductor_offset_beyond_body_m": conductor_clear,
            "conductor_side": "outboard of each track, opposite the island"}


def _service_power(cfg: dict, capital_scopes: dict, fleet: int) -> dict:
    """Bound outage power within the declared service-battery allocation."""
    p = cfg["service_power"]
    continuous = p["control_continuous_kw"] + p["other_essential_continuous_kw"]
    demand = (continuous * p["protected_outage_hours"] + p["brake_event_kwh"]
              + p["door_egress_event_kwh"]) * (1 + p["energy_reserve_fraction"])
    usable = p["battery_nominal_kwh"] * p["usable_fraction"]
    recharge_kw = p["battery_nominal_kwh"] / p["recharge_hours"] / p["recharge_efficiency"]
    if (min(p.values()) <= 0 or p["usable_fraction"] > 1
            or p["energy_reserve_fraction"] > 1 or usable < demand
            or p["control_continuous_kw"] != cfg["control_electronics"]["train_auxiliary_power_allowance_kw"]
            or p["battery_mass_allowance_t"] + cfg["control_electronics"]["train_mass_allowance_t"]
            >= cfg["vehicle"]["crowd_mass_t_per_train_before_supply"]
            or fleet * p["battery_price_allocation_usd_m_per_train"] > capital_scopes["vehicles"]):
        raise ValueError("Baghdad independent service-power allowance does not close")
    return {"continuous_essential_kw": continuous, "outage_hours": p["protected_outage_hours"],
            "required_usable_kwh_with_reserve": demand, "declared_usable_kwh": usable,
            "nominal_battery_kwh_per_train": p["battery_nominal_kwh"],
            "battery_mass_allowance_within_base_t": p["battery_mass_allowance_t"],
            "fleet_price_allocation_within_vehicles_usd_m":
                fleet * p["battery_price_allocation_usd_m_per_train"],
            "recharge_input_kw_per_train": recharge_kw,
            "recharge_loss_heat_kw_per_train": recharge_kw * (1 - p["recharge_efficiency"]),
            "scope": "Independent controls, light, brake and egress duty; traction supply excluded"}


def _station_svg(cfg: dict) -> bytes:
    g = _station_interfaces(cfg)
    v, s = g["vehicle"], g["station"]
    scale = 60
    left_edge = 500 - s["island_width_m"] * scale / 2
    right_edge = 500 + s["island_width_m"] * scale / 2
    left_track = left_edge - s["straight_platform_edge_offset_m"] * scale
    right_track = right_edge + s["straight_platform_edge_offset_m"] * scale
    half_car = v["body_width_m"] * scale / 2
    conductor = v["contact_rail_outboard_offset_m"] * scale
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 340" role="img" aria-label="Baghdad straight island station and outboard protected conductor planning section">',
        '<rect width="1000" height="340" fill="#f7fafb"/>',
        '<text x="40" y="28" font-family="sans-serif" font-size="18" fill="#17364a">Baghdad straight station — nominal train and power section</text>',
        f'<rect x="{left_edge:g}" y="200" width="{s["island_width_m"] * scale:g}" height="70" fill="#d6e1d0" stroke="#47664b" stroke-width="2"/>',
        f'<text x="450" y="230" font-family="sans-serif" font-size="15" fill="#294b34">{s["island_width_m"]:g} m island</text>',
        '<line x1="35" y1="270" x2="965" y2="270" stroke="#64717b" stroke-width="4"/>',
    ]
    for centre, rail in ((left_track, left_track - conductor),
                         (right_track, right_track + conductor)):
        lines.extend([
            f'<rect x="{centre - half_car:g}" y="94" width="{2 * half_car:g}" height="106" fill="#d7e8f0" stroke="#17364a" stroke-width="2"/>',
            f'<line x1="{centre:g}" y1="198" x2="{centre:g}" y2="281" stroke="#17364a" stroke-width="2" stroke-dasharray="5 4"/>',
            f'<rect x="{rail - 7:g}" y="242" width="14" height="25" fill="#bd583d" stroke="#7e2b23" stroke-width="2"/>',
            f'<rect x="{rail - 16:g}" y="232" width="32" height="40" fill="none" stroke="#bd583d" stroke-width="2" stroke-dasharray="4 3"/>',
        ])
    lines.extend([
        '<text x="36" y="67" font-family="sans-serif" font-size="13" fill="#17364a">Protected contact rail and guard are outboard of each train, away from the island.</text>',
        f'<text x="36" y="307" font-family="sans-serif" font-size="13" fill="#17364a">Body {v["body_width_m"]:g} m · static platform gap {g["static_body_edge_gap_m"] * 1000:.0f} mm · floor {v["floor_above_rail_m"]:g} m above rail</text>',
        f'<text x="36" y="328" font-family="sans-serif" font-size="11" fill="#596e78">Track centres {s["straight_track_centre_spacing_m"]:g} m · contact rail {v["contact_rail_outboard_offset_m"]:g} m outboard of track centre. Straight nominal section; access and insulation require detailed design.</text>',
        '</svg>',
    ])
    return ('\n'.join(lines) + '\n').encode()


def _check_vehicle_layout(cfg: dict, root: Path) -> None:
    svg = ElementTree.parse(root / 'cities/Baghdad/vehicle-layout.svg').getroot()
    v = cfg["vehicle_geometry"]
    if (float(svg.attrib.get('data-body-width-m', 0)) != v["body_width_m"]
            or float(svg.attrib.get('data-door-width-m', 0)) != v["door_clear_width_m"]):
        raise ValueError("Baghdad vehicle drawing dimensions differ from system input")
    ns = '{http://www.w3.org/2000/svg}'
    doors = svg.find(f"{ns}g[@fill='#72b6cc']")
    if doors is None or len(doors) != 2 * len(v["door_centres_m"]):
        raise ValueError("Baghdad vehicle drawing door count differs")
    for rect, centre in zip(list(doors)[:len(v["door_centres_m"])], v["door_centres_m"]):
        drawn_centre = (float(rect.attrib['x']) + float(rect.attrib['width']) / 2 - 50) / 50 - 8.5
        if abs(drawn_centre - centre) > 0.02:
            raise ValueError("Baghdad vehicle drawing door centres differ")


def evaluate(network: str, supply: str, *, span_m: int = 10,
             common_pier: bool = False, root: Path = ROOT,
             _prepared: tuple | None = None) -> dict:
    root = Path(root)
    cfg = _prepared[0] if _prepared is not None else load(root, network=network)
    if network not in cfg["networks"] or supply not in (
            "station_battery", "protected_conductor", "limited_conductor_battery", "overhead"):
        raise ValueError("Known Baghdad network and supply option required")
    if span_m not in SUPPORTED_SPANS_M or type(common_pier) is not bool:
        raise ValueError("Declared Baghdad span and pier option required")
    n = cfg["networks"][network]
    v = cfg["vehicle"]
    station_interfaces = _station_interfaces(cfg)
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
    power = (_prepared[2][supply] if _prepared is not None else
             compare_power(power_network, PowerAssumptions(**cfg["power_assumptions"]))[supply])
    lines, length_basis, coverage = _prepared[1] if _prepared is not None else _lines(root, cfg, network)
    civil = civil_evaluate(lines, span_m=span_m, common_pier=common_pier,
                           physical_candidate_id=power["physical_candidate_id"],
                           rates=PlanningRates(**cfg["civil_rates"]),
                           target_years=n["civil_finish_year"] - n["civil_start_year"] + 1,
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
    controls = _control_electronics(cfg, n, power, common)
    service_power = _service_power(cfg, common, n["fleet_trainsets"])
    if (controls["allocation_within_capital_scopes_usd_m"]["vehicles"]
            + service_power["fleet_price_allocation_within_vehicles_usd_m"] > common["vehicles"]):
        raise ValueError("Train control and service-battery allocations exceed fleet price")
    direct = sum(common.values())
    design = direct * cr["design_fraction"]
    test = direct * cr["testing_fraction"]
    subtotal = direct + design + test
    contingency = subtotal * cr["project_allowance_fraction"]
    installed = subtotal + contingency
    scopes = {**common, "design_assurance": design,
              "testing_commissioning": test, "project_allowance": contingency}
    local_delivery = None
    if "local_contract_fraction" in n:
        fractions = n["local_contract_fraction"]
        priced_scopes = set(scopes) - {"project_allowance"}
        if set(fractions) != priced_scopes or any(type(value) not in (float, int) or
                                                 not 0 <= value <= 1 for value in fractions.values()):
            raise ValueError("Metropolitan local-contract planning shares do not cover priced scopes")
        addressable = {scope: scopes[scope] * fractions[scope] for scope in priced_scopes}
        local_delivery = {"planning_local_contract_usd_m": sum(addressable.values()),
                          "scope_local_contract_usd_m": addressable,
                          "planning_share_of_non_contingency_capital":
                              sum(addressable.values()) / (installed - contingency),
                          "project_allowance_unassigned_usd_m": contingency,
                          "actual_supplier_origin_established": False,
                          "royalty_or_ip_savings_in_capital_usd_m": None,
                          "basis": "Indicative Iraqi contract opportunity at declared scope shares; no deduction from installed capital"}
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
    installed_rates = cfg["control_electronics_installed"]
    selected_controls = {name: {"count": count,
                                "mass_kg_each": installed_rates[name + "_kg"],
                                "continuous_w_each": installed_rates[name + "_w"]}
                         for name, count in controls["installed_train_items"].items() if count}
    control_physical = {"items": selected_controls,
                        "harness_enclosure_kg_per_train": installed_rates["harness_enclosure_kg_per_train"]}
    result = {
        "schema": SCHEMA, "parent_candidate_id": cfg["candidate_id"],
        "physical_candidate_id": _id({"network": network, "power": power["physical_candidate_id"],
                                      "civil": civil["civil_option_physical_id"],
                                      "station_interfaces": station_interfaces,
                                      "service_power": cfg["service_power"],
                                      "control_installation": control_physical}),
        "selection_purpose": "equal-service planning comparison",
        "infrastructure": {"tunnel_km": cfg["tunnel_km"],
                           "underground_stations": cfg["underground_stations"],
                           "at_grade_km": 0.0, "elevated_route_km": route_km,
                           "track_count": cfg["track_count"]},
        "network": network, "supply": supply, "span_m": span_m, "common_pier": common_pier,
        "map_length_basis": length_basis,
        "map_and_service_coverage": coverage,
        "service": {"route_km": route_km, "stations": n["stations"],
                    "line_count": n["lines"],
                    "normal_places_per_train": v["normal_places_per_train"],
                    "offered_places_per_hour_direction": v["normal_places_per_train"] * 3600 / v["peak_headway_s"],
                    "annual_train_km": annual_train_km,
                    "fleet_trainsets": n["fleet_trainsets"]},
        "vehicle": power["vehicle"], "traction": power["traction"],
        "energy": power["energy"], "supply_quantities": power["supply"],
        "control_electronics": controls,
        "local_delivery": local_delivery,
        "station_interfaces": station_interfaces, "service_power": service_power,
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
        "source_sha256": {str(CONFIG) + "#selected-" + network: _selected_input_id(cfg, network),
                          cfg["map_sources"][network + "_path"]:
                              cfg["map_sources"][network + "_sha256"],
                          **({cfg["map_sources"]["waypoints_path"]:
                              cfg["map_sources"]["waypoints_sha256"]} if network == "first" else {}),
                          "engineering/outline/baghdad_system.py": _hash(Path(__file__)),
                          "engineering/outline/baghdad_power.py": _hash(root / "engineering/outline/baghdad_power.py"),
                          "engineering/outline/baghdad_viaduct.py": _hash(root / "engineering/outline/baghdad_viaduct.py")},
        "site_or_physical_accepted": False,
    }
    result["evaluation_id"] = _id(result)
    return result


def compare(network: str, root: Path = ROOT) -> dict:
    cfg = load(root, network=network)
    n, v = cfg["networks"][network], cfg["vehicle"]
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
    prepared = (cfg, _lines(root, cfg, network),
                compare_power(power_network, PowerAssumptions(**cfg["power_assumptions"])))
    fixed_span = cfg["selected_span_m"]
    fixed_common = cfg["selected_pier_family"] == "common-crosshead"
    supply_rows = {key: evaluate(network, key, span_m=fixed_span,
                                 common_pier=fixed_common, root=root, _prepared=prepared)
                   for key in ("station_battery", "protected_conductor",
                               "limited_conductor_battery", "overhead")}
    preferred = min(supply_rows, key=lambda key: supply_rows[key]["whole_life_30y_present_usd_m"])
    civil_rows = {f"{span}m-{'common' if common else 'separate'}":
                  evaluate(network, preferred, span_m=span, common_pier=common,
                           root=root, _prepared=prepared)
                  for span in SUPPORTED_SPANS_M for common in (False, True)}
    protected = supply_rows["protected_conductor"]
    overhead = supply_rows["overhead"]
    advantage = (overhead["whole_life_30y_present_usd_m"]
                 - protected["whole_life_30y_present_usd_m"])
    track_km = protected["supply_quantities"]["protected_conductor_track_km"]
    cr = cfg["capital_rates_usd_m"]
    rate_slope = track_km * (1 + cr["design_fraction"] + cr["testing_fraction"]) * (1 + cr["project_allowance_fraction"])
    rate_slope += (track_km * cfg["power_assumptions"]["line_equipment_renewal_fraction_year_25"]
                   / (1 + cfg["discount_rate_real"]) ** 25)
    annuity = sum((1 + cfg["discount_rate_real"]) ** -year
                  for year in range(1, cfg["comparison_years"] + 1))
    sensitivity = {
        "basis": "One protected-conductor input varied against overhead; all other assumptions fixed",
        "protected_advantage_usd_m": advantage,
        "protected_price_uplift_to_overhead_usd_m_per_track_km": advantage / rate_slope,
        "protected_price_break_even_usd_m_per_track_km":
            cfg["power_price_allowances_usd_m"]["protected_conductor_per_track_km"] + advantage / rate_slope,
        "extra_annual_maintenance_to_overhead_usd_m_per_track_km": advantage / (track_km * annuity),
        "extra_annual_grid_gwh_to_overhead":
            advantage / (annuity * cfg["operation_rates"]["delivered_energy_usd_per_kwh"]),
    }
    return {"schema": "opensourcerail.baghdad.system-comparison.1",
            "network": network, "candidate_id": cfg["candidate_id"],
            "digital_cost_leader": preferred,
            "preferred_offwire": preferred != "overhead",
            "selected_digital_civil_family": f"{fixed_span}m-{'common' if fixed_common else 'separate'}",
            "power_cases": supply_rows, "civil_cases": civil_rows,
            "power_cost_sensitivity": sensitivity,
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
            "selected_control_electronics": selected["control_electronics"],
            "selected_station_interfaces": selected["station_interfaces"],
            "selected_service_power": selected["service_power"],
            "selected_local_delivery": selected["local_delivery"],
            "map_and_service_coverage": selected["map_and_service_coverage"],
            "selected_civil_delivery": selected["civil"]["delivery"],
            "power_cost_sensitivity": comparison["power_cost_sensitivity"],
            "service_groups": cfg["networks"][name].get("service_groups"),
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
    p.add_argument("--write-drawings", action="store_true")
    p.add_argument("--check-drawings", action="store_true")
    args = p.parse_args()
    if args.write_drawings or args.check_drawings:
        cfg = load()
        _check_vehicle_layout(cfg, ROOT)
        target = ROOT / 'cities/Baghdad/station-interface.svg'
        raw = _station_svg(cfg)
        if args.check_drawings:
            if not target.is_file() or target.read_bytes() != raw:
                raise ValueError("Baghdad station drawing differs from system input")
            print("Baghdad train and station drawings current", sha256(raw).hexdigest())
        else:
            target.write_bytes(raw)
            print("wrote", target, sha256(raw).hexdigest())
        return
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
