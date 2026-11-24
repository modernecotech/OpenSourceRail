"""Airport train cooling and station passenger movement planning screens."""

import argparse
import hashlib
import json
import math
import random
import platform
import tomllib
from pathlib import Path

CITY = Path(__file__).resolve().parents[2]
SYSTEM = CITY / "system.toml"
TRIAL = CITY / "engineering/mechanical/vehicle/section-trial.toml"
DOOR = CITY / "engineering/prototype/doorway.toml"
EXIT_WIDTH_M = 3.0
FLOW_PER_M_S = 0.8
EDGE_RESERVE_M = 0.75
MOBILITY = (("walking", 1.25, 0.22), ("slow_walking", 0.75, 0.25), ("wheeled", 0.55, 0.36))
MODEL_LIMIT_S = 900


def sha(data):
    return hashlib.sha256(data).hexdigest()


def identity(value):
    return sha(json.dumps(value, sort_keys=True, allow_nan=False).encode())


def source_data():
    raw = {path: path.read_bytes() for path in (SYSTEM, TRIAL, DOOR)}
    config, trial, door = (tomllib.loads(raw[path].decode()) for path in (SYSTEM, TRIAL, DOOR))
    return config, trial, door, {str(path.relative_to(CITY)): sha(data) for path, data in raw.items()}


def humidity_ratio(c, relative_humidity):
    vapour_kpa = 0.61078 * math.exp(17.2694 * c / (c + 237.29)) * relative_humidity
    return 0.622 * vapour_kpa / (101.3 - vapour_kpa)


def cooling(cars, passengers, ambient, dwell, config, trial, case):
    # Enthalpy screen at a sea-level planning pressure. A humid case should
    # be supplied separately from the dry hot-day sensitivity.
    g = config["vehicle_geometry"]
    roof = g["body_width_m"] * g["car_body_length_m"]
    glazing = 20.0
    sides_ends = 2 * (g["car_body_length_m"] + g["body_width_m"]) * 3.0
    difference = max(0, ambient - 26.0)
    outdoor_rh = case.get("outdoor_relative_humidity", 0.25 if ambient <= 40 else 0.18)
    humidity = max(0, humidity_ratio(ambient, outdoor_rh) - humidity_ratio(26, 0.5))
    outside_air = passengers * 0.006 + cars * 0.055
    door_air = cars * 1.0 * min(1, dwell / case.get("door_open_cycle_s", 180))
    equipment_heat = 2.0 * cars
    terms = {
        "envelope_conduction": cars * difference * ((1.1 + 0.8) * roof + 1.1 * (sides_ends - glazing)
                                                     + 3.1 * glazing) / 1000,
        "solar_opaque_and_glazing": cars * (0.9 * roof * 0.50 * 1.1 / 18 + 0.60 * 10 * 0.42),
        "passenger_sensible": passengers * 0.075, "passenger_latent": passengers * 0.055,
        "outside_air_sensible": 1.18 * outside_air * 1.006 * difference,
        "outside_air_latent": 1.18 * outside_air * 2450 * humidity,
        "door_exchange_sensible": 1.18 * door_air * 1.006 * difference,
        "door_exchange_latent": 1.18 * door_air * 2450 * humidity,
        "internal_lighting_and_equipment": equipment_heat,
    }
    required = sum(terms.values())
    cop = max(1.4, 2.8 - max(0, ambient - 35) * 0.08)
    fans = 2.0 * cars
    per_car_nameplate = case.get("assumed_cooling_kw_per_car", 48.0)
    derating = max(0.55, 1 - max(0, ambient - 35) * 0.017)
    available = per_car_nameplate * cars * derating
    essential = config["service_power"]["control_continuous_kw"] + config["service_power"]["other_essential_continuous_kw"]
    non_hvac = essential + 3 * cars
    bus_allowance = trial["auxiliaries_mw_per_train"] * 1000 * cars / 6
    demand = required / cop + fans + non_hvac
    return {
        "ambient_c": ambient, "setpoint_c": 26.0, "outdoor_relative_humidity": outdoor_rh,
        "required_cooling_kw_thermal": required,
        "thermal_components_kw": terms, "cop": cop, "fan_kw": fans,
        "minimum_outside_air_m3_s": outside_air, "averaged_door_infiltration_m3_s": door_air,
        "trial_rated_cooling_kw_thermal": per_car_nameplate * cars,
        "trial_derated_cooling_kw_thermal": available,
        "trial_thermal_margin_kw": available - required, "actual_installed_cooling_kw_thermal": None,
        "non_hvac_kw": non_hvac, "reference_full_train_bus_allowance_kw": bus_allowance,
        "thermal_target_auxiliary_kw": demand, "trial_bus_margin_kw": bus_allowance - demand,
        "auxiliary_at_trial_equipment_limit_kw": min(available, required) / cop + fans + non_hvac,
        "basis": "Design thermal demand including fans and non-HVAC uses. Installed module and electrical performance require return.",
    }


def door_exchange(data, config, door, cars, peak, waiting):
    capacity = config["vehicle"]["normal_places_per_train"] * cars // 6
    active = config["vehicle"]["door_openings_per_car_each_side"] * cars
    clear = door["rough_opening_m"] - 2 * sum(door[f"{key}_per_edge_m"] for key in
        ("seal_projection", "fabrication_inward", "loaded_distortion", "fitting_and_wear"))
    clear -= 2 * door["liner_thickness_m"]
    doubled_clear = clear - 2 * door["loaded_distortion_per_edge_m"]
    required_clear = config["vehicle_geometry"]["door_clear_width_m"]
    board = data.get("boarding_passengers", min(waiting, peak))
    alight = data.get("alighting_passengers", min(round(peak * 0.25), capacity - peak + board))
    if type(alight) is not int or type(board) is not int:
        raise ValueError("Passenger exchanges are integer counts")
    incoming = peak + alight - board
    if min(alight, board, incoming) < 0 or board > waiting or alight > incoming or incoming > capacity:
        raise ValueError("Boarding and alighting conflict with the train load, queue or offered capacity")
    busy = min(alight + board, math.ceil(1.6 * (alight + board) / active))
    clear_time = busy / (max(clear, 0.1) * 0.85)
    mobility_extra = 12 if busy else 0
    fixed = 9.0
    walk_on_platform = (config["station_geometry"]["platform_clear_length_m"] -
                        (cars * config["vehicle_geometry"]["car_body_length_m"] + (cars - 1) * 0.5)) / 2
    return {
        "doors_active": active, "assumed_alighting": alight, "assumed_boarding": board,
        "arriving_load": incoming, "remaining_queue_after_departure": waiting - board,
        "busiest_door_movements": busy, "door_clear_nominal_trial_m": clear,
        "door_clear_if_trial_loaded_distortion_doubles_m": doubled_clear,
        "required_door_clear_m": required_clear, "nominal_clear_margin_m": clear - required_clear,
        "straight_gap_nominal_m": 0.075, "measured_step_m": None, "measured_gap_m": None,
        "transfer_s": clear_time, "opening_and_proving_s": fixed,
        "assisted_transfer_trial_s": mobility_extra,
        "total_unassisted_dwell_s": clear_time + fixed,
        "total_dwell_with_one_assisted_transfer_s": clear_time + fixed + mobility_extra,
        "assisted_dwell_margin_s": config["vehicle"]["dwell_s"] - clear_time - fixed - mobility_extra,
        "planned_dwell_s": config["vehicle"]["dwell_s"],
        "short_formation_tail_walk_m_from_island_end": walk_on_platform,
        "slow_walk_tail_s": walk_on_platform / MOBILITY[1][1],
        "accessible_passage_status": "open pending survey, bridge and loaded door trials",
    }


def mobility_counts(people):
    slow = math.floor(people * 0.15)
    wheels = math.ceil(people * 0.03)
    return dict(zip((item[0] for item in MOBILITY), (people - slow - wheels, slow, wheels)))


def station_screen(people, length, width, entrances):
    groups = mobility_counts(people)
    max_distance = length / (2 if entrances == 2 else 1)
    approach = {name: max_distance / speed for name, speed, _ in MOBILITY if groups[name]}
    fluid = people / (FLOW_PER_M_S * EXIT_WIDTH_M * entrances)
    return {
        "population": people, "groups": groups, "available_entrances": entrances,
        "max_horizontal_distance_m": max_distance, "free_travel_s_by_group": approach,
        "entrance_throughput_s": fluid, "serial_travel_plus_flow_s": max(approach.values(), default=0) + fluid,
        "density_people_m2": people / (length * width),
        "clearance_target_s": None,
    }


def compact_geometry(length, width, open_exits):
    inner = width - 2 * EDGE_RESERVE_M
    lo, hi = (inner - EXIT_WIDTH_M) / 2, (inner + EXIT_WIDTH_M) / 2
    left, right = (-5 if "west" in open_exits else 0), (length + 5 if "east" in open_exits else length)
    polygon = [(0, 0), (length, 0), (length, lo), (right, lo), (right, hi),
               (length, hi), (length, inner), (0, inner), (0, hi), (left, hi), (left, lo), (0, lo)]
    if right == length:
        del polygon[3:5]
    if left == 0:
        del polygon[-3:-1]
    exits = {}
    if left < 0:
        exits["west"] = [(left, lo), (left + 1.5, lo), (left + 1.5, hi), (left, hi)]
    if right > length:
        exits["east"] = [(right - 1.5, lo), (right, lo), (right, hi), (right - 1.5, hi)]
    return polygon, exits, inner


def native_case(length, width, people, open_exits, *, time_limit_s=MODEL_LIMIT_S, dt=0.05, checkpoint=None):
    import jupedsim

    if not 1 <= people <= 1000 or jupedsim.__version__ != "1.4.2":
        raise ValueError("Native budget requires 1–1000 pedestrians and JuPedSim 1.4.2")
    if dt not in (0.05, 0.025) or not 0 < time_limit_s <= MODEL_LIMIT_S or not open_exits:
        raise ValueError("Native time step, run duration or exit state falls outside the comparison")
    polygon, exits, clear_width = compact_geometry(length, width, open_exits)
    sim = jupedsim.Simulation(model=jupedsim.CollisionFreeSpeedModelV2(), geometry=polygon, dt=dt)
    journeys = {}
    for name, exit_polygon in exits.items():
        stage = sim.add_exit_stage(exit_polygon)
        journeys[name] = (sim.add_journey(jupedsim.JourneyDescription([stage])), stage)
    rng = random.Random(806)
    locations = [(2 + col * 0.81, 0.82 + row * 0.81)
                 for col in range(150) for row in range(7) if 2 + col * 0.81 < length - 1]
    if len(locations) < people:
        raise ValueError("Pedestrian budget exceeds separated start locations")
    rng.shuffle(locations)
    population = mobility_counts(people)
    assignments = [name for name, _, _ in MOBILITY for _ in range(population[name])]
    rng.shuffle(assignments)
    definitions = {item[0]: item[1:] for item in MOBILITY}
    assigned = {}
    for (x, y), group in zip(locations, assignments):
        target = min(exits, key=lambda name: x if name == "west" else length - x)
        journey, stage = journeys[target]
        speed, radius = definitions[group]
        agent = sim.add_agent(jupedsim.CollisionFreeSpeedModelV2AgentParameters(
            position=(x, y), desired_speed=speed, radius=radius, journey_id=journey, stage_id=stage,
        ))
        assigned[agent] = (group, target)
    progress = []
    time = 0
    for i in range(math.ceil(time_limit_s / dt)):
        if checkpoint and i % 500 == 0:
            checkpoint()
        sim.iterate()
        time = (i + 1) * dt
        remaining = sim.agent_count()
        if not remaining or (i + 1) % round(30 / dt) == 0:
            progress.append([round(time, 2), remaining])
        if not remaining:
            break
    uncleared = dict.fromkeys(population, 0)
    for agent in sim.agents():
        uncleared[assigned[agent.id][0]] += 1
    return {
        "tool": "JuPedSim", "version": jupedsim.__version__, "model": "CollisionFreeSpeedModelV2",
        "dt_s": dt, "budget_s": time_limit_s, "population": people, "groups": population,
        "exits": list(open_exits), "elapsed_s": time, "cleared": people - sim.agent_count(),
        "uncleared_by_mobility": uncleared, "native_status": "cleared" if not sim.agent_count() else "time-budget",
        "geometry": polygon, "exit_polygons": exits, "platform_clear_width_m": clear_width,
        "progress_elapsed_s_remaining": progress, "starting_position_seed": 806,
        "removed_agents_meaning": "Reached horizontal exit line. Continued path, stairs and protected place remain open.",
    }


def evaluate(inputs=None):
    case = dict(inputs or {})
    cfg, trial, door, sources = source_data()
    cars = case.get("cars", 6)
    headway = case.get("headway_min", 15)
    dwell = case.get("dwell_s", cfg["vehicle"]["dwell_s"])
    ambient = case.get("ambient_c", 48)
    peak = case.get("busiest_departure_load", 700 * cars // 6)
    waiting = case.get("platform_queue", 350)
    if (cars not in (3, 6) or type(peak) is not int or not 0 <= peak <= 700 * cars // 6 or
        type(waiting) is not int or not 0 <= waiting <= 1400 or headway <= 0 or not 25 <= ambient <= 55):
        raise ValueError("Passenger and climate inputs lie outside the Airport study domain")
    if not all(math.isfinite(case.get(key, value)) and low <= case.get(key, value) <= high for key, value, low, high in (
        ("outdoor_relative_humidity", 0.25, 0.0, 1.0), ("door_open_cycle_s", 180, 45, 900),
        ("assumed_cooling_kw_per_car", 48, 10, 120), ("headway_min", headway, 1, 120),
        ("dwell_s", dwell, 5, 120),
    )):
        raise ValueError("Airport climate and service assumptions exceed the bounded domain")
    if dwell != cfg["vehicle"]["dwell_s"]:
        cfg = {**cfg, "vehicle": {**cfg["vehicle"], "dwell_s": dwell}}
    exchange = door_exchange(case, cfg, door, cars, peak, waiting)
    open_s = min(exchange["planned_dwell_s"], max(0, exchange["total_unassisted_dwell_s"] - 5))
    hvac = cooling(cars, peak, ambient, open_s, cfg, trial, case)
    length = cfg["station_geometry"]["platform_clear_length_m"]
    width = cfg["station_geometry"]["island_width_m"]
    scenario_people = waiting + exchange["arriving_load"]
    out = {
        "inputs": case, "cars": cars, "headway_min": headway, "busiest_departure_load": peak, "platform_queue": waiting,
        "auxiliary_kw": hvac["thermal_target_auxiliary_kw"], "hvac": hvac,
        "summer_cases": {str(temp): cooling(cars, peak, temp, open_s, cfg, trial, case) for temp in (40, 48)},
        "door_exchange": exchange,
        "station_movement": {
            "length_m": length, "width_m": width, "edge_reserve_each_side_m": EDGE_RESERVE_M,
            "present_waiting_people": waiting,
            "outside_climate": {
                "open_plan": True, "air_temperature_c": ambient, "measured_globe_temperature_c": None,
                "trial_direct_solar_w_m2": 900, "trial_shaded_fraction": 0.8,
                "unshaded_waiting_area_m2_if_uniform": round(length * (width - 2 * EDGE_RESERVE_M) * 0.2, 2),
                "inputs_needed": ["Shade by sun angle at accessible queues", "Wind and local humidity",
                                  "Measured heat, refuge capacity, water and operating policies"],
            },
            "waiting_density_people_m2": waiting / (length * (width - 2 * EDGE_RESERVE_M)),
            "evacuation_population_basis": "Pre-arrival platform queue plus separately discharged arriving train",
            "two_exit_entries": station_screen(scenario_people, length, width - 2 * EDGE_RESERVE_M, 2),
            "one_exit_entry_unavailable": station_screen(scenario_people, length, width - 2 * EDGE_RESERVE_M, 1),
            "protected_accessible_vertical_route": None,
            "required_inputs": ["Surveyed pinch points, accessible vertical routes and lifts",
                                "Side access, equipment and edge envelopes", "Detection, staff response and pre-movement",
                                "Approved evacuation destination, smoke tenability and independent fire review"],
        },
        "fire_handoff": {
            "status": "inputs open",
            "geometry_m": {"platform": [length, width], "representative_train_length":
                           cars * cfg["vehicle_geometry"]["car_body_length_m"] + (cars - 1) * 0.5},
            "needed_for_smoke_model": ["Surveyed roof/void/edge and vertical shafts", "Design fire and car/luggage material data",
                "Openings and ventilation duty", "Exterior wind and boundaries", "Tenability criteria and mesh study"],
        },
        "source_sha256": sources, "method_sha256": sha(Path(__file__).read_bytes()),
        "physical_acceptance": "open",
    }
    out["evaluation_id"] = identity(out)
    return out


def native_benchmark(length, width, people, checkpoint=None):
    import jupedsim.native

    binary = Path(jupedsim.native.py_jps.__file__)
    return {
        "platform": platform.machine(), "python_version": platform.python_version(),
        "binary": {"name": binary.name, "sha256": sha(binary.read_bytes())},
        "source_artifact": "https://www.jupedsim.org/v1.4.2/api/jupedsim/index.html",
        "cases": [native_case(length, width, size, exits, dt=dt, checkpoint=checkpoint)
                  for size in people for dt in (0.05, 0.025) for exits in (("west", "east"), ("west",))],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", type=Path, help="Write native receipt to a new output path")
    parser.add_argument("--people", nargs="+", type=int, default=[350, 700])
    args = parser.parse_args()
    packet = evaluate()
    if not args.native:
        print(json.dumps(packet, indent=2, sort_keys=True))
        return
    from engineering.performance import check_disk_reservation, disk_reservation

    root = CITY.parents[1]
    with disk_reservation(root, args.native.parent, "Baghdad Airport JuPedSim replay", 1024**2) as lease:
        def check():
            check_disk_reservation(lease)

        length, width = (packet["station_movement"][f"{field}_m"] for field in ("length", "width"))
        packet["native"] = native_benchmark(length, width, args.people, check)
        packet["native_evaluation_id"] = identity(packet)
        check()
        with args.native.open("x") as stream:
            json.dump(packet, stream, indent=2, sort_keys=True)
            stream.write("\n")


if __name__ == "__main__":
    main()
