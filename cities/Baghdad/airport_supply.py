"""Bound the Baghdad Airport collector voltage against the actual opening workings."""
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import pairwise
import json
from math import ceil, isclose, isfinite, sqrt
from pathlib import Path
from copy import deepcopy
import tomllib

from cities.Baghdad.engineering.mechanical.vehicle import power_interface

CITY = Path(__file__).resolve().parent
TRIAL = CITY / "engineering/mechanical/vehicle/section-trial.toml"


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _pulse_windows(service, route_km, pulse_s, speed_m_s):
    """Group intervals of identical station-departure pulse footprints over the operating day."""
    changes = defaultdict(Counter)
    pulses = 0

    def add(start, end, footprint):
        nonlocal pulses
        if not isfinite(start) or not isfinite(end) or end <= start:
            raise ValueError("A traction interval needs a finite positive duration")
        changes[start][footprint] += 1
        changes[end][footprint] -= 1
        pulses += 1

    trips = [*service["trips"], *service.get("positioning_trips", [])]
    for _, side, dep, arr in trips:
        pattern = service["patterns"][side]
        if not isclose(arr - dep, pattern[-1]["arrival_s"]):
            raise ValueError("Airport feeder replay needs the applicable station times on each trip")
        changes[arr]
        for leg_index, (origin, destination) in enumerate(pairwise(pattern)):
            f, g = origin["fraction"], destination["fraction"]
            if not 0 <= f < g <= 1:
                raise ValueError("Station fractions must increase in each direction")
            leg_s = destination["arrival_s"] - origin["departure_s"]
            pulse = max(pulse_s, ceil(service["leg_profiles"][side][leg_index]["acceleration_s"]))
            if leg_s < pulse:
                raise ValueError("A station departure pulse exceeds its running leg")
            # Bound position throughout the entire pulse using the route speed cap.
            # A train near a break can count against each adjacent feed in separate bounds.
            reach = min((g - f) * route_km, pulse * speed_m_s / 1000)
            start_km = (f if side == 0 else 1 - f) * route_km
            end_km = start_km + (reach if side == 0 else -reach)
            add(dep + origin["departure_s"], dep + origin["departure_s"] + pulse,
                tuple(sorted((round(start_km, 9), round(end_km, 9)))))
    for move in service.get("terminal", {}).get("yard_moves", []):
        # Full traction throughout the local move loads the Airport bus. The short
        # depot branch downstream of that bus requires its own return and protection study.
        add(move["start_s"], move["end_s"], (0., 0.))
    if not changes:
        raise ValueError("Airport replay needs at least one train working")
    active, windows = Counter(), {}
    for now, later in pairwise(sorted(changes)):
        active.update(changes[now])
        footprints = tuple(sorted(active.elements()))
        if footprints not in windows:
            windows[footprints] = {"first_s": now, "seconds": 0}
        windows[footprints]["seconds"] += later - now
    return windows, pulses


def _voltage_row(sources_kv, floor_kv, loop_ohm, mw):
    peak = power_interface.load_bus(sources_kv, loop_ohm, mw)
    if peak is None:
        return {"collector_kv": None, "current_ka": None, "loss_kw": None,
                "status": "no stable constant-power operating point"}
    v, current = peak
    return {"collector_kv": v, "current_ka": current, "loss_kw": 1000 * loop_ohm * current**2,
            "status": "within planning floor" if v >= floor_kv else "below planning floor"}


def _replay(sites, windows, source_kv, floor_kv, droop, resistance_per_km, traction, auxiliaries):
    """Upper bound each source using nearest-live-site radial feeding and bounded train positions."""
    outages = []
    duration = sum(window["seconds"] for window in windows.values())
    for failed in [None, *range(len(sites))]:
        live = [(index, x) for index, x in enumerate(sites) if index != failed]
        worst, max_rms, max_heat = None, 0., 0.
        for i, (index, x) in enumerate(live):
            # The break at the isolated site's chainage divides adjacent restored
            # feeds, including when the surveyed bays have unequal lengths.
            left = sites[0] if not i else ((x + sites[index-1]) / 2 if live[i-1][0] == index-1 else sites[index-1])
            right = sites[-1] if i+1 == len(live) else ((x + sites[index+1]) / 2
                        if live[i+1][0] == index+1 else sites[index+1])
            distance = max(right - x, x - left)
            loop = droop + distance * resistance_per_km
            squared_current_seconds = 0
            for footprints, window in windows.items():
                count = sum(lo <= right and hi >= left for lo, hi in footprints)
                load = auxiliaries + count * traction
                result = _voltage_row(source_kv, floor_kv, loop, load)
                # Negative discriminants lose their operating point. Preserve that
                # case ahead of cases still admitting a positive high-voltage root.
                voltage = result["collector_kv"]
                if worst is None or (voltage or 0.) < (worst["collector_kv"] or 0.):
                    worst = {**result, "site": index, "first_local_s": window["first_s"],
                             "simultaneous_pulses": count, "furthest_fed_km": distance,
                             "collector_load_bound_mw": load, "loop_ohm_bound": loop}
                if voltage is None:
                    squared_current_seconds = float("inf")
                else:
                    squared_current_seconds += window["seconds"] * result["current_ka"]**2
            max_rms = max(max_rms, sqrt(squared_current_seconds / duration))
            max_heat = max(max_heat, squared_current_seconds / duration * distance * resistance_per_km * 1000)
        outages.append({"failed_site": failed, "worst": worst,
                        "site_rms_ka_upper": max_rms if isfinite(max_rms) else None,
                        "conductor_heat_kw_upper_per_site": max_heat if isfinite(max_heat) else None})
    return outages


def _sources():
    paths = (Path(__file__).resolve(), Path(power_interface.__file__).resolve(), TRIAL, CITY / "system.toml")
    return {p.relative_to(CITY.parents[1]).as_posix(): sha256(p.read_bytes()).hexdigest() for p in paths}


def _load_id(power, route_km):
    screen = power["traction"]["electrical_screen"]
    return digest({"route_km": float(route_km), "option": power["option"], "service": power["common_service"],
                   "vehicle": power["vehicle"], "protected_track_km": power["supply"]["protected_conductor_track_km"],
                   "traction_rating_mw": power["traction"]["dc_input_rating_request_mw"],
                   "source_kv": screen["voltage_kv_not_selected"], "low_voltage_fraction": screen["low_voltage_fraction"]})


def bind_supply(result, service, final_power, route_km):
    """Bind a reproducible voltage replay to the final costed configuration without evaluating it twice."""
    payload = {key: value for key, value in result.items() if key != "evaluation_id"}
    if (result.get("evaluation_id") != digest(payload) or result["selected"] is None
            or result["source_sha256"] != _sources() or result["service_id"] != digest(service)
            or result["load_id"] != _load_id(final_power, route_km)
            or final_power.get("feeder_design_id") != result["design_id"]
            or final_power["supply"]["grid_sites"] != result["grid_sites"]
            or final_power["supply"]["powered_section_count"] != result["procurement"]["feed_half_bays"]):
        raise ValueError("Final power case must match the replay sources, service, vehicle, loads and feeder design")
    bound = deepcopy(payload)
    bound.update(power_candidate_id=final_power["physical_candidate_id"], power_evaluation_id=final_power["evaluation_id"])
    return {**bound, "evaluation_id": digest(bound)}


def build_supply(service, power, route_km):
    """Derive a preliminary supply variant, using one service and its protected-conductor vehicle."""
    route_km = float(route_km)
    trial = tomllib.loads(TRIAL.read_text())
    screen = power["traction"]["electrical_screen"]
    source_kv = screen["voltage_kv_not_selected"]
    floor_kv = source_kv * screen["low_voltage_fraction"]
    common = power["common_service"]
    sets = len({train for train, *_ in service["trips"]})
    if (power["option"] != "protected_conductor" or not isclose(route_km, 12)
            or not isclose(route_km, common["route_km"]) or sets != common["active_trainsets"]
            or common["peak_headway_s"] != service["peak_headway_s"]
            or not isclose(source_kv, 1.5) or not isclose(floor_kv, 1.35)
            or common["stations"] != 6 or len(service["trips"]) * route_km * common["service_days_per_year"]
            != common["annual_train_km"]):
        raise ValueError("Airport traction study needs the same 12 km service, fleet and 1.5 kV power case")
    traction = power["traction"]["dc_input_rating_request_mw"]
    per_train_aux = trial["auxiliaries_mw_per_train"]
    pulse_s = trial["pulse_seconds"]
    droop = trial["source_droop_ohm"]
    loop_per_km = trial["outward_ohm_per_km"] + trial["return_ohm_per_km"]
    cfg = tomllib.loads((CITY / "system.toml").read_text())
    speed = cfg["vehicle"]["speed_cap_kmh"] / 3.6
    vehicle = cfg["power_assumptions"]
    uphill = vehicle["adverse_grade"] * 9.81 + vehicle["resistance_accel_m_s2"]
    cruise = traction * uphill / (uphill + vehicle["required_net_accel_m_s2"])
    # Include uphill cruise at the speed cap for every set outside a traction
    # pulse, including sets actually stopped. The result bounds the assumed duty.
    increment = traction - cruise
    windows, pulses = _pulse_windows(service, route_km, pulse_s, speed)
    duration = sum(row["seconds"] for row in windows.values())
    aux = max(sets, 2) * per_train_aux
    background = aux + max(sets, 2) * cruise
    load = 2 * increment + background
    limit_ohm = floor_kv * (source_kv - floor_kv) / load
    # Closest live feed reaches one full site spacing with either end or an
    # interior source isolated. Two coincident trains can be anywhere on either track.
    maximum_spacing = (limit_ohm - droop) / loop_per_km
    reference_rows = power_interface.section_rows(trial, source_kv, floor_kv, route_km / 4,
                                                   traction, service["peak_headway_s"])
    preliminary = {
        "reference": {"grid_sites": 3, "site_chainage_km": [0., route_km / 2, route_km],
                      "midpoint_cases": reference_rows,
                      "status": "retained comparison",
                      "replay": _replay([0., route_km / 2, route_km], windows, source_kv, floor_kv,
                                        droop, loop_per_km, increment, background)},
        "source_kv": source_kv, "floor_kv": floor_kv, "physical_accepted": False,
        "source_sha256": _sources(), "load_id": _load_id(power, route_km), "service_id": digest(service),
        "power_candidate_id": power["physical_candidate_id"], "power_evaluation_id": power["evaluation_id"],
        "braking_reception": power_interface.braking_reception(
            power["vehicle"]["mass_t"], speed, trial["braking_deceleration_m_s2"],
            trial["braking_wheel_to_bus_efficiency"], per_train_aux, traction + per_train_aux),
        "assumptions": {
            "source_droop_ohm": droop, "outward_ohm_per_km": trial["outward_ohm_per_km"],
            "return_ohm_per_km": trial["return_ohm_per_km"], "pulse_seconds": pulse_s,
            "train_traction_rating_mw": traction, "uphill_cruise_bound_mw_per_nonaccelerating_set": cruise, "auxiliaries_mw_per_train": per_train_aux,
            "speed_cap_m_s": speed, "design_two_pulse_load_plus_all_working_auxiliaries_mw": load,
            "two_pulse_loop_limit_ohm": limit_ohm, "maximum_spacing_km_for_two_pulses": maximum_spacing,
            "topology": "Two radial tracks. Both sides of each intermediate site have independent outgoing breakers. Open ties at bay midpoints. After a source outage, isolate its DC bus and close healthy adjacent ties; the break at the failed site separates the restored feeds.",
            "load": "Apply the declared traction rating over the longer of the registered pulse and the booked acceleration phase after each station departure. Each remaining set draws an upper allowance for uphill cruising at the speed cap, even during stops. Attribute all working-set auxiliaries and cruise background to each source in turn. The independent two-train stress adds two full rating pulses at the most distant collector.",
            "thermal": "Daytime RMS current and conductor heat use the upper current from the maximum radial path for each site and pulse combination. Obtain conductor temperatures, shoe current sharing and rectifier duty from measured losses, ambient and thermal impedances.",
            "outage": "Replay restored radial feeding with one complete site unavailable. A conductor fault, a lost utility bus common to several sites, time to isolate and service during switching need separate operating rules.",
        },
        "replay": {"revenue_trips": len(service["trips"]), "positioning_trips": len(service.get("positioning_trips", [])),
                   "local_yard_moves": len(service.get("terminal", {}).get("yard_moves", [])),
                   "pulses": pulses, "peak_simultaneous_pulses_linewide": max(map(len, windows)),
                   "operating_envelope_s": duration,
                   "collector_energy_upper_mwh": (background * duration + increment * sum(len(g) * w["seconds"] for g, w in windows.items())) / 3600},
        "holds": [
            "Obtain surveyed site parcels, running-rail bonds, hot conductor and joint resistances, rectifier regulation, current limits and actual train current traces including cruise and braking.",
            "Prove train detection, isolated breakers and ties, no backfeed across work zones or shoes, touch and stray-current limits, earthing, evacuation walkways, rescue and witnessed lockout.",
            "Scope depot switchgear and the voltage drop from the Airport bus to the yard, utility short-circuit levels, transformer and standby loads, protection selectivity and simultaneous losses.",
            "Verify brake duty at zero line receptivity and overvoltage during regeneration. The pulse replay gives no regeneration credit.",
        ],
    }
    # A 10% resistance allowance represents a procurement sensitivity. The
    # supplier must substantiate the design hot path, joints and source regulation.
    impedance_factor = 1.10
    hot_spacing = (limit_ohm / impedance_factor - droop) / loop_per_km
    preliminary["assumptions"].update(impedance_sensitivity_multiplier=impedance_factor,
                                      maximum_spacing_including_impedance_sensitivity_km=hot_spacing)
    if hot_spacing <= 0 or ceil(route_km / hot_spacing) >= 64:
        status = ("site spacing cannot overcome assumed source droop under the impedance sensitivity"
                  if hot_spacing <= 0 else "site count exceeds the 64-site bounded replay domain")
        failed = {**preliminary, "design_id": None, "grid_sites": None, "selected": None, "procurement": None,
                  "status": status}
        return {**failed, "evaluation_id": digest(failed)}

    nominal_n = max(3, 1 + ceil(route_km / maximum_spacing))
    n = max(3, 1 + ceil(route_km / hot_spacing))
    sites = [i * route_km / (n-1) for i in range(n)]
    spacing = route_km / (n-1)
    def stress(spacing_km, source_ohm, conductor_ohm_km):
        cases = []
        for unavailable, distance in ((False, spacing_km / 2), (True, spacing_km)):
            for trains in (1, 2):
                row = _voltage_row(source_kv, floor_kv, source_ohm + conductor_ohm_km * distance,
                                   background + trains * increment)
                cases.append({**row, "one_site_unavailable": unavailable, "accelerating_trains": trains,
                              "max_source_distance_km": distance})
        return cases

    effective_droop = droop * impedance_factor
    effective_loop = loop_per_km * impedance_factor
    outages = _replay(sites, windows, source_kv, floor_kv, effective_droop, effective_loop, increment, background)
    independent = stress(spacing, effective_droop, effective_loop)
    nominal_spacing = route_km / (nominal_n - 1)
    preliminary["minimum_without_impedance_reserve"] = {
        "grid_sites": nominal_n, "spacing_km": nominal_spacing,
        "nominal_two_train_outage": stress(nominal_spacing, droop, loop_per_km)[-1],
        "sensitivity_two_train_outage": stress(nominal_spacing, effective_droop, effective_loop)[-1]}
    # An alternate electrical family places a source at each stop in the current
    # equal-chainage timetable, with half source droop and one-third loop resistance.
    # These are effective hot resistance requirements, including shared upstream impedance.
    station_sites = [route_km * stop["fraction"] for stop in service["patterns"][0]]
    alt_spacing = max(b-a for a, b in pairwise(station_sites))
    alt_droop, alt_loop = effective_droop / 2, effective_loop / 3
    alt_stress = stress(alt_spacing, alt_droop, alt_loop)
    alt_replay = _replay(station_sites, windows, source_kv, floor_kv, alt_droop, alt_loop, increment, background)
    alt_rows = alt_stress + [outage["worst"] for outage in alt_replay]
    alt_ok = all(row["status"] == "within planning floor" for row in alt_rows)
    preliminary["station_sited_quote_variant"] = {
        "grid_sites": len(station_sites), "site_chainage_km": station_sites,
        "nominal_source_droop_ohm": droop / 2, "nominal_outward_ohm_per_km": trial["outward_ohm_per_km"] / 3,
        "nominal_return_ohm_per_km": trial["return_ohm_per_km"] / 3,
        "impedance_sensitivity_multiplier": impedance_factor, "independent_cases": alt_stress,
        "minimum_collector_kv": min(row["collector_kv"] for row in alt_rows) if alt_ok else None,
        "minimum_site_peak_dc_mw": max(row["current_ka"] for row in alt_rows) * source_kv if alt_ok else None,
        "dc_outgoing_breaker_circuits": 4 * (len(station_sites)-1),
        "normally_open_track_ties": 2 * (len(station_sites)-1), "installed_price_usd": None,
        "status": "voltage screen passed, quotation required" if alt_ok else "voltage screen failed",
        "supplier_scope": "Price six lower-droop source groups and the heavier positive and return circuits, joints, cable supports, installation and replacements. Demonstrate independence and full circuit resistance with one complete site isolated."}

    rows = independent + [outage["worst"] for outage in outages]
    ok = all(row["status"] == "within planning floor" for row in rows)
    site_peak = max(row["current_ka"] for row in rows) * source_kv if ok else None
    design = {"feed_system": "sectioned radial with midpoint ties", "grid_sites": n,
              "site_chainage_km": sites, "route_km": route_km, "source_kv": source_kv,
              "droop_ohm": droop, "outward_ohm_per_km": trial["outward_ohm_per_km"],
              "return_ohm_per_km": trial["return_ohm_per_km"]}
    procurement = {
        "feed_half_bays": 4 * (n-1), "dc_outgoing_breaker_circuits": 4 * (n-1),
        "normally_open_track_ties": 2 * (n-1), "dc_source_groups": n,
        "additional_grid_sites_over_reference": n - 3,
        "protected_track_km": power["supply"]["protected_conductor_track_km"],
        "minimum_site_peak_dc_mw": site_peak,
        "pricing_scope": "Apply site, tie-in and section equipment rates to the restored-feed layout. Quote two-track midpoint ties, utility input capacity, redundant protection and installation separately where their scope exceeds existing rates.",
    }
    variant = {**design, "design_id": digest(design), "independent_cases": independent,
               "outages": outages, "impedance_sensitivity_multiplier": impedance_factor,
               "minimum_collector_kv": min(r["collector_kv"] for r in rows)
               if all(r["collector_kv"] is not None for r in rows) else None}
    result = {**preliminary, "design_id": variant["design_id"] if ok else None, "grid_sites": n if ok else None,
              "selected": variant if ok else None, "tested_variant": None if ok else variant,
              "procurement": procurement, "status": "within planning voltage floor" if ok else "voltage screen failed"}
    result["evaluation_id"] = digest(result)
    return result
