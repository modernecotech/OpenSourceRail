"""Trace a Baghdad weight return into a fixed-point DC supply quotation screen."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from math import isclose, isfinite, sqrt
from pathlib import Path
import sys
import tomllib

HERE = Path(__file__).resolve().parent
CITY = HERE.parents[2]
ROOT = CITY.parents[1]
sys.path.insert(0, str(ROOT))

from cities.Baghdad.engineering.mechanical.compare_returns import verified_record
from engineering.outline.baghdad_system import evaluate
from engineering.performance import check_disk_reservation, disk_reservation

# Each weight is for the entire six-car set, at operating fluid levels.
MASS_GROUPS = {
    "finished_body_bogie_frames": "Finished structural steel, welds, joint hardware and coatings",
    "wheelsets_running_gear": "Wheelsets, bearings, suspension, dampers, links and retention",
    "drive_and_brakes": "Motors, inverters, gearboxes, brake hardware, pumps and cooling fluids",
    "body_fitout": "Body skin, floor, glazing, doors, trim, seats, HVAC and wheelchair fittings",
    "power_and_control": "Shoes, service battery, protection, controllers, cabling and enclosures",
    "remaining_tare": "Couplers, gangways, lighting, pipes and remaining tare items",
    "crowd_payload": "Crowd load for the supplier's declared loading case",
}


def identity(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def mass_form(basis):
    return {"basis": basis, "train_mass_groups": {
        group: {"kg": None, "evidence": None} for group in MASS_GROUPS}}


def mass_return(form, basis):
    if set(form) != {"basis", "train_mass_groups"} or form["basis"] != basis:
        raise ValueError("Weight return must identify this network and braced frame revision")
    groups = form["train_mass_groups"]
    if not isinstance(groups, dict) or groups.keys() != MASS_GROUPS.keys():
        raise ValueError("Return every tare group and the crowd load")
    weights, missing = {}, []
    for group, row in groups.items():
        if not isinstance(row, dict) or row.keys() != {"kg", "evidence"}:
            raise ValueError(f"Invalid weight return for {group}")
        kg, evidence = row["kg"], row["evidence"]
        if kg is None and evidence is None:
            missing.append(group)
            continue
        if (type(kg) not in (int, float) or not isfinite(kg) or kg < 0
                or (kg == 0 and group != "remaining_tare")
                or not isinstance(evidence, str) or not evidence.strip()):
            raise ValueError(f"{group} requires a scoped train total in kg and its evidence reference")
        weights[group] = kg
    tare = None if set(missing) - {"crowd_payload"} else sum(
        kg for group, kg in weights.items() if group != "crowd_payload")
    return {"missing_groups": missing, "returned_tare_kg": tare,
            "returned_crowd_train_kg": None if missing else tare + weights["crowd_payload"],
            "weight_return": form}


def load_bus(source_kv, resistance_ohm, power_mw):
    """Stable high-voltage root of V = E - R P/V, using kV, kA and MW."""
    if not all(isfinite(x) and x > 0 for x in (source_kv, resistance_ohm, power_mw)):
        raise ValueError("Positive finite voltage, loop resistance and load required")
    discriminant = source_kv ** 2 - 4 * resistance_ohm * power_mw
    if discriminant < 0:
        return None
    voltage = (source_kv + sqrt(discriminant)) / 2
    return voltage, power_mw / voltage


def section_rows(controls, voltage, voltage_floor, half_bay_km, rating_mw, headway_s):
    path = controls["source_droop_ohm"] + half_bay_km * (
        controls["outward_ohm_per_km"] + controls["return_ohm_per_km"])
    aux = controls["auxiliaries_mw_per_train"]
    if (not isfinite(headway_s) or headway_s <= 0 or not controls["available_feeds"]
            or not controls["coincident_trains"]):
        raise ValueError("A positive headway and at least one feed and load case are required")
    duty = controls["pulse_seconds"] / headway_s
    if not (0 < duty <= 1 and 0.5 * voltage < voltage_floor < voltage
            and all(isfinite(x) and x > 0 for x in (aux, half_bay_km, rating_mw))
            and all(isfinite(controls[k]) and controls[k] >= 0 for k in (
                "source_droop_ohm", "outward_ohm_per_km", "return_ohm_per_km"))):
        raise ValueError("Check section resistance, voltage limits and pulse duty")
    rows = []
    for feeds in controls["available_feeds"]:
        for trains in controls["coincident_trains"]:
            if feeds not in (1, 2) or type(trains) is not int or trains < 1:
                raise ValueError("Positive train count and one or two symmetric feeds required")
            peak_mw = trains * (rating_mw + aux)
            limit_ohm = voltage_floor * (voltage - voltage_floor) / peak_mw
            row = {"feeds": feeds, "trains": trains, "peak_collector_mw": peak_mw,
                   "equivalent_loop_ohm": path / feeds, "maximum_loop_ohm_at_floor": limit_ohm}
            peak = load_bus(voltage, path / feeds, peak_mw)
            if peak is None:
                rows.append(dict(row, status="constant-power equilibrium unavailable"))
                continue
            v, current = peak
            branch_current = current / feeds
            _, idle_current = load_bus(voltage, path / feeds, trains * aux)
            branch_rms = sqrt(duty * branch_current ** 2 + (1 - duty) * (idle_current / feeds) ** 2)
            losses = current ** 2 * row["equivalent_loop_ohm"]
            if not isclose(voltage * current, peak_mw + losses, abs_tol=1e-8):
                raise ValueError("Source/load power balance failed")
            rows.append(dict(row, status="within voltage screen" if v >= voltage_floor else "below voltage screen",
                             collector_kv=v, branch_peak_ka=branch_current, branch_rms_ka=branch_rms,
                             peak_source_input_mw_per_feed=voltage * branch_current,
                             peak_return_conductor_drop_v=branch_current * half_bay_km
                             * controls["return_ohm_per_km"] * 1000,
                             peak_loop_loss_mw=losses,
                             cycle_average_conductor_heat_kw=feeds * branch_rms ** 2
                             * (path - controls["source_droop_ohm"]) * 1000,
                             cycle_average_loop_loss_kw=feeds * branch_rms ** 2 * path * 1000))
    return rows


def braking_reception(mass_t, speed_m_s, deceleration, efficiency, aux_mw, neighbor_mw):
    """One level stop, a non-reversible source and an ideal common DC bus."""
    if (not all(isfinite(x) and x > 0 for x in (
            mass_t, speed_m_s, deceleration, efficiency, aux_mw, neighbor_mw)) or efficiency > 1):
        raise ValueError("Positive braking inputs and wheel-to-bus efficiency up to unity required")
    duration_s = speed_m_s / deceleration
    kinetic_kwh = 0.5 * mass_t * speed_m_s ** 2 / 3600
    available_kwh = kinetic_kwh * efficiency
    peak_mw = mass_t * speed_m_s * deceleration * efficiency / 1000
    # Power offered falls linearly with speed. Above the sink limit, its area
    # is a similar triangle with both axes scaled by the peak excess fraction.
    cases = []
    for neighbors in (0, 1):
        sink_mw = aux_mw + neighbors * neighbor_mw
        fraction = max(0.0, 1 - sink_mw / peak_mw)
        excess_kwh = available_kwh * fraction ** 2
        cases.append({"accelerating_neighbors": neighbors, "sink_mw": sink_mw,
                      "potentially_received_kwh": available_kwh - excess_kwh,
                      "unreceived_kwh": excess_kwh,
                      "unreceived_peak_mw": max(0.0, peak_mw - sink_mw)})
    return {"duration_s": duration_s, "kinetic_kwh": kinetic_kwh, "offered_dc_kwh": available_kwh,
            "offered_peak_mw": peak_mw, "cases": cases}


def build(return_path=None):
    config = tomllib.loads((CITY / "system.toml").read_text())
    trial = tomllib.loads((HERE / "section-trial.toml").read_text())
    frame = verified_record(HERE / "result.json", ROOT)
    n = verified_record(CITY / "system-results.json", ROOT)["networks"]["first"]
    parent = evaluate("first", "protected_conductor")
    if (frame["parent_train_id"] != n["selected_candidate_id"]
            or parent["physical_candidate_id"] != n["selected_candidate_id"]
            or parent["evaluation_id"] != n["selected_evaluation_id"]
            or frame["parent_project_id"] != config["candidate_id"]):
        raise ValueError("Train, frame and selected first-network price must share the same parent")
    basis = {"first_network_id": parent["physical_candidate_id"], "network_evaluation": parent["evaluation_id"],
             "braced_revision": frame["braced_revision_id"], "frame_evaluation": frame["evaluation_id"]}
    form = json.loads(return_path.read_text()) if return_path else mass_form(basis)
    mass = mass_return(form, basis)
    vehicle, power = parent["vehicle"], parent["traction"]
    loaded_t = vehicle["mass_t"]
    if mass["returned_crowd_train_kg"] is not None:
        loaded_t = mass["returned_crowd_train_kg"] / 1000
    rating = power["dc_input_rating_request_mw"] * loaded_t / vehicle["mass_t"]
    bus = power["electrical_screen"]
    v = bus["voltage_kv_not_selected"]
    sites = config["networks"]["first"]["traction_supply_sites"]
    spacing = n["route_km"] / sites
    rates = config["capital_rates_usd_m"]
    installed_factor = (1 + rates["design_fraction"] + rates["testing_fraction"]) * (1 + rates["project_allowance_fraction"])
    advantage = n["power_cost_sensitivity"]["protected_advantage_usd_m"]
    result = {"basis": basis, "physical_accepted": False, "selection": None, "source_sha256": {
        str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in
        (HERE / "power_interface.py", HERE / "section-trial.toml", HERE / "result.json",
         HERE.parent / "compare_returns.py", CITY / "system-results.json")},
        "inputs": trial, "mass": mass,
        "bare_frame_stock_kg_per_train": config["vehicle"]["cars_per_train"] * frame["braced_body_and_two_bogie_cut_stock_kg_per_car"],
        "load_basis": "supplier return" if mass["returned_crowd_train_kg"] is not None else "selected planning load",
        "loaded_t": loaded_t, "reference_loaded_t": vehicle["mass_t"],
        "traction_and_supply_counts": {"driven_axles_per_train": vehicle["driven_axles"],
            "shoe_sets_per_train": config["vehicle_geometry"]["shoe_sets_per_train"],
            "protected_track_km": parent["supply_quantities"]["protected_conductor_track_km"],
            "powered_sections": parent["supply_quantities"]["powered_section_count"],
            "sites": sites},
        "axle_mean_t": loaded_t / config["vehicle"]["axles_per_train"],
        "traction_rating_mw": rating, "mw_per_added_loaded_t": rating / loaded_t,
        "source_kv": v, "voltage_floor_kv": v * bus["low_voltage_fraction"],
        "representative_feed_spacing_km": spacing,
        "section_cases": section_rows(trial, v, v * bus["low_voltage_fraction"], spacing / 2,
                                     rating, config["vehicle"]["peak_headway_s"]),
        "braking_reception": braking_reception(loaded_t, config["vehicle"]["speed_cap_kmh"] / 3.6,
            trial["braking_deceleration_m_s2"], trial["braking_wheel_to_bus_efficiency"],
            trial["auxiliaries_mw_per_train"], rating + trial["auxiliaries_mw_per_train"]),
        "cost": {"reference_30y_advantage_usd_m": advantage, "site_count": sites,
                 "direct_one_off_upgrade_break_even_usd_m_per_site": advantage / installed_factor / sites,
                 "conductor_price_uplift_break_even_usd_m_per_track_km":
                 n["power_cost_sensitivity"]["protected_price_uplift_to_overhead_usd_m_per_track_km"]}}
    result["evaluation_id"] = identity(result)
    return result


def report(data):
    r = data
    rows = [
        "# Train weight and traction supply for the first Baghdad network",
        "",
        f"The six-car train weighs **{r['loaded_t']:.3f} t** in the crowd-load planning case. "
        f"Six sets of braced carbody and bogie members account for {r['bare_frame_stock_kg_per_train']/1000:.3f} t of cut steel. "
        "The finished train tare and crowd payload are open. "
        "The supplier return keeps these accounts separate until every group has a scoped weight.",
        "",
        f"At the published uphill duty the train requests **{r['traction_rating_mw']:.3f} MW** of traction converter capacity. "
        f"Each additional loaded tonne changes this request by {1000*r['mw_per_added_loaded_t']:.1f} kW "
        "at the same speed, acceleration, grade, efficiency and rating margin. "
        "A complete weight return replaces the planning crowd total for this screen.",
        "",
        "## Can the supply support coincident trains?",
        "",
        f"Each trial uses a {r['source_kv']:.2f} kV open-circuit source and a {r['voltage_floor_kv']:.2f} kV planning floor. "
        f"Dividing the route length by the site allowance gives a representative {r['representative_feed_spacing_km']:.2f} km feed bay. "
        "Identical independent circuits feed one common collector bus halfway between the supplies. "
        "A coincident pair shares this bus in the electrical model. Actual positions, cross-feeds and section boundaries require a route design.",
        "",
        f"Each branch has {1000*r['inputs']['source_droop_ohm']:.0f} mΩ source droop, "
        f"{1000*r['inputs']['outward_ohm_per_km']:.0f} mΩ/km outward resistance and "
        f"{1000*r['inputs']['return_ohm_per_km']:.0f} mΩ/km return resistance. "
        f"A {r['inputs']['pulse_seconds']:g} s rectangular traction rating pulse repeats at the peak service headway, "
        f"with {r['inputs']['auxiliaries_mw_per_train']:.3f} MW per train of auxiliaries throughout. "
        "The single-feed case isolates one source while retaining the other path to the same midpoint.",
        "",
        "| Live feeds | Coincident trains | Collector kV | Peak kA/feed | RMS kA/feed | Mean conductor heat kW | Equivalent loop loss kW | Voltage result |",
        "|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for c in r["section_cases"]:
        if "collector_kv" not in c:
            rows.append(f"| {c['feeds']} | {c['trains']} | — | — | — | — | — | {c['status']} |")
        else:
            rows.append(f"| {c['feeds']} | {c['trains']} | {c['collector_kv']:.3f} | {c['branch_peak_ka']:.2f} "
                        f"| {c['branch_rms_ka']:.2f} | {c['cycle_average_conductor_heat_kw']:.1f} | {c['cycle_average_loop_loss_kw']:.1f} | {c['status']} |")
    counts = r["traction_and_supply_counts"]
    cost = r["cost"]
    braking = r["braking_reception"]
    alone, adjacent = braking["cases"]
    rows.extend([
        "",
        "Results below the floor quantify requested duty before converter derating, current limiting or protection operates. "
        "The circuit solves the high-voltage constant-power operating point. It retains loss of equilibrium when demand exceeds the transfer limit. "
        "Conductor heat covers the outward and return resistances. Equivalent loop loss also includes source droop, whose voltage regulation can have a different physical heat loss. Metal temperature, contact sharing and annual energy require measured duty and thermal impedances.",
        "",
        "## Where can braking energy go?",
        "",
        f"A level stop from the speed cap at {r['inputs']['braking_deceleration_m_s2']:.2f} m/s² takes "
        f"{braking['duration_s']:.1f} s in the trial. The initial kinetic energy is {braking['kinetic_kwh']:.2f} kWh. "
        f"At {r['inputs']['braking_wheel_to_bus_efficiency']:.0%} wheel-to-bus efficiency, "
        f"electrical braking offers up to {braking['offered_dc_kwh']:.2f} kWh, starting at {braking['offered_peak_mw']:.2f} MW. "
        "The calculation neglects drag, gradients and rotating inertia and holds the rectifier non-reversible.",
        "",
        f"With only the braking train's {alone['sink_mw']:.3f} MW auxiliary load receptive, "
        f"{alone['potentially_received_kwh']:.2f} kWh can be used and **{alone['unreceived_kwh']:.2f} kWh** needs "
        f"another sink or equivalent mechanical braking, up to {alone['unreceived_peak_mw']:.2f} MW electrical at the start. "
        f"If an accelerating train draws {adjacent['sink_mw']-alone['sink_mw']:.3f} MW on the same ideal bus throughout the stop, "
        f"up to {adjacent['potentially_received_kwh']:.2f} kWh can be used. "
        "The ideal-bus figure assumes full availability of those loads. Current limits, feeder separation, overvoltage and train timing can reduce reception. "
        "Budget independent stopping at zero network receptivity. No energy credit enters the published cost estimate from this trial.",
        "",
        "## What to price",
        "",
        f"The first network allows {counts['sites']} supply sites, {counts['powered_sections']} powered track sections "
        f"and {counts['protected_track_km']:.1f} track-km of conductor. Each train has {counts['driven_axles_per_train']} driven axles "
        f"and {counts['shoe_sets_per_train']} shoe sets. Ask the supplier to mark the feed lengths, rectifiers, outfeeds, "
        "section breakers and isolators, return bonds, cross-bonds, depot boundary, test points and isolation zones on its single-line drawing. "
        "Price installation, enclosures, access, cooling, testing, spares and replacement. Breaker and bond counts follow the approved topology.",
        "",
        f"The protected conductor has a **${cost['reference_30y_advantage_usd_m']:.2f}m** first-network present-cost advantage over overhead "
        f"under the current 30-year assumptions. A one-off **${cost['direct_one_off_upgrade_break_even_usd_m_per_site']:.3f}m direct premium per site** "
        f"across all {counts['sites']} sites would consume it after design, test and project allowances, with every other cost fixed. "
        f"The separate equipment-only threshold is **${cost['conductor_price_uplift_break_even_usd_m_per_track_km']:.3f}m extra per track-km** "
        "with line renewal included. These are alternative uses of the same margin. Deduct existing allowances and comparable overhead upgrades before comparing incremental returns.",
        "",
        "Return actual hot conductor, return and joint resistances, utility short-circuit levels and rectifier droop/current limits. "
        "Supply motoring, auxiliary and regenerative current traces, shoe-current sharing, conductor and cable thermal ratings, rail-to-earth measurements, "
        "accessible voltage limits, protection coordination and a witnessed isolation procedure. "
        "Replay the working timetable with train positions and measured load curves, including braking into a non-receptive section. "
        "Independent braking, touch voltage, faults and thermal qualification remain open.",
        "",
        "[Vehicle weight-return instructions](README.md#weighing-the-installed-train) · [Electrical trial inputs](section-trial.toml)",
        "",
    ])
    return "\n".join(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--mass-form", action="store_true", help="Print an empty supplier return")
    group.add_argument("--mass-return", type=Path, help="Use a scoped six-car supplier return")
    group.add_argument("--publish", action="store_true", help="Regenerate the operator sheet")
    group.add_argument("--check", action="store_true", help="Check the published operator sheet")
    args = parser.parse_args()
    result = build(args.mass_return)
    path = HERE / "SECTION-POWER.md"
    if args.publish:
        with disk_reservation(ROOT, HERE, "Baghdad section-power quotation sheet", 65536) as lease:
            check_disk_reservation(lease)
            path.write_text(report(result), encoding="utf-8")
        return
    if args.check:
        if path.read_text(encoding="utf-8") != report(result):
            raise SystemExit("Regenerate SECTION-POWER.md")
        print("Current Baghdad section screen", result["evaluation_id"])
        return
    print(json.dumps(mass_form(result["basis"]) if args.mass_form else result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
