"""Source-bound Airport car mass, fit, traction and independent-stop screens."""
import argparse
import csv
from hashlib import sha256
import io
from itertools import product
import json
import math
from pathlib import Path
import tomllib
from zipfile import ZipFile

from cities.Baghdad.engineering.prototype import car, commercial, weights
from cities.Baghdad.engineering.simulation import airport_alignment, vehicle_civil

CITY = vehicle_civil.CITY
ROOT = CITY.parents[1]
PROTO = vehicle_civil.PROTOTYPE
GA = PROTO / "vehicle-factory/installed-ga.json"
BOM = GA.with_name("installed-fitout-bom.csv")
TRIAL = CITY / "engineering/mechanical/vehicle/section-trial.toml"
SYSTEM = CITY / "system.toml"
G = 9.80665
KWH = 3.6e6
MODULE_COMPARATOR_KN = 14.6  # VEHICLE.md, rounded demand at the original crowd mass
PHYSICAL_RETURNS = {
    "installed_mass": "Complete serialised item mass/CG and installed fluids; calibrated tare and ballast/loaded group and 4N axle records with checked balance, wheel-side split and orientation.",
    "traction": "Driven axle assignments/failed inverter mapping, hot tractive effort and duration versus speed and rail condition, instrumented axle loads, slip recovery and cooling.",
    "braking": "Command-to-force trace, wheel-slide series and independent rail force versus speed, at both load extremes, dry/contaminated rail, downgrade, lost axle/module and zero line receptivity; show the stopping position.",
    "brake_thermal": "Per-module duty, engagement energy, mount/disc/pad/rail thermal traces, allowable limits, cool-down, thermal fade, rail damage and inspection after repeated stops.",
    "brake_containment": "Wheel/rail and rail-brake compatibility, air gap and wear, all swept poses, stow and parking retention, common-cause protection, force transfer and protected tow.",
    "battery": "End-of-life hot/aged deliverable capacity and power through the two-hour outage, brake excitation and accessible egress; log voltage, current, retention, isolation and recharge.",
    "door_boarding": "Serialised loaded and empty fitted widths, leaf/guide/stop/lock/anti-drop and cable sweep, force and cycles; survey platform step and gap through yaw, roll, wheel wear and stopping error, including assisted boarding.",
    "suspension_exchange": "Survey all four secondary gaps, stacks, primary guides and stops, jounce/rebound and retained travel. Witness equipped extraction and reinstallation with hoses, wiring, slings, pallet, stands and tools.",
    "route_protection": "Survey direction-specific grade and speed transitions, detection and control latencies, authorised stopping limit and overlap, full-tail release and turnout protection.",
}


def sha(raw):
    return sha256(raw).hexdigest()


def source_data():
    members = ("mechanical.json", "civil-article.json", "fitout-interfaces.json",
               "opening.json", "revised-cuts.csv", "returns/weights.json", "returns/fitout.csv")
    with ZipFile(PROTO / "airport-prototype.zip") as packet:
        manifest_raw = packet.read("manifest.json")
        manifest = json.loads(manifest_raw)
        data = {name: packet.read(name) for name in members}
    hashes = {name: sha(raw) for name, raw in data.items()}
    if any(manifest["sha256"][name] != digest for name, digest in hashes.items()):
        raise ValueError("Airport article packet member hash mismatch")
    ga_raw, bom_raw = GA.read_bytes(), BOM.read_bytes()
    ga = json.loads(ga_raw)
    mechanical, cage, fit, opening = (json.loads(data[name]) for name in members[:4])
    parent = opening["candidate_id"]
    if (any(record["candidate_id"] != parent for record in (manifest, mechanical, cage, fit, ga))
            or ga["mechanical_evaluation_id"] != mechanical["evaluation_id"]
            or ga["opening_evaluation_id"] != opening["evaluation_id"]
            or ga["fitout_evaluation_id"] != fit["evaluation_id"]
            or ga["frame_revision"] != opening["bundle"]["vehicle_revision"]
            or ga["frame_revision"] != mechanical["frame_revision"]
            or ga["frame_revision"] != fit["frame_revision"]
            or fit["article_evaluation_id"] != mechanical["evaluation_id"]
            or cage["mechanical_evaluation_id"] != mechanical["evaluation_id"]
            or ga["evaluation_id"] != car.identity({key: value for key, value in ga.items() if key != "evaluation_id"})
            or any(manifest["sha256"][name] != digest for name, digest in ga["packet_member_sha256"].items())
            or ga["outputs_sha256"][BOM.name] != sha(bom_raw)):
        raise ValueError("Installed BOM, GA and Airport article ancestry differ")
    for path in (SYSTEM, TRIAL):
        if opening["sources"][path.relative_to(ROOT).as_posix()] != sha(path.read_bytes()):
            raise ValueError(f"Airport opening scenario source changed: {path.name}")
    files = (Path(__file__), Path(vehicle_civil.__file__), Path(weights.__file__),
             Path(commercial.__file__), Path(car.__file__), SYSTEM, TRIAL, GA, BOM, CITY / "VEHICLE.md",
             CITY / "airport_assembly.py", CITY / "engineering/mechanical/README.md")
    sources = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in files}
    sources.update({"prototype:" + name: value for name, value in hashes.items()})
    sources["prototype:manifest.json"] = sha(manifest_raw)
    cuts = csv.DictReader(io.StringIO(data["revised-cuts.csv"].decode()))
    bogie_stock = 2 * sum(float(row["gross_mass_kg"]) for row in cuts if row["assembly"] == "bogie")
    return mechanical, cage, fit, opening, ga, list(csv.DictReader(io.StringIO(bom_raw.decode()))), bogie_stock, sources


def mass_cases(record, bogie, service, cars, material, centres):
    axle_offsets = record["interfaces"]["body_from_axle_x_m"]
    cases = {}
    for state in vehicle_civil.STATES:
        row = vehicle_civil.load_case(record, bogie, service, cars, material, state)
        groups = {key: (x, z) for key, (_, z, x) in vehicle_civil.GROUPS.items()}
        groups.update(body_stock=(0, 1.8), bogie_frame_stock=(0, .55),
                      independent_service_pack=(-2.0, .85))
        allocations = {key: dict(mass_kg_per_car=mass, car_from_centroid_m=[groups[key][0], None, groups[key][1]])
                       for key, mass in row["group_kg_per_car"].items()}
        payload = (row["loaded_train_kg"] - row["tare_train_kg"]) / cars
        allocations["payload"] = dict(mass_kg_per_car=payload,
                                      car_from_centroid_m=[row["passenger_centroid_x_m"], None, 1.6])
        tare = row["tare_train_kg"] / cars
        tare_x = sum(a["mass_kg_per_car"] * a["car_from_centroid_m"][0]
                     for key, a in allocations.items() if key != "payload") / tare
        pivot = record["bogie_translations_m"][1]
        front = tare * (.5 + tare_x / (2 * pivot))
        tare_axles = [(tare - front) / 2] * 2 + [front / 2] * 2
        axle_rows = {}
        for i, centre in enumerate(centres, 1):
            for j, (offset, empty, loaded) in enumerate(zip(axle_offsets, tare_axles, row["axle_kg_per_car"], strict=True), 1):
                axle_rows[f"C{i}-A{j}"] = dict(train_x_m=centre + offset, car_x_m=offset, tare_kg=empty,
                                               loaded_kg=loaded, loaded_reaction_kn=loaded * G / 1000)
        cases[state] = {**row, "group_allocations": allocations, "axles": axle_rows, "tare_car_cg_x_m": tare_x,
                        "max_loaded_static_axle_kg": max(row["axle_kg_per_car"])}
    return cases


def stop(speed, delay, slope_accel, mass, wheel_kn, rail_kn):
    """Constant force after a coast delay; brake work includes downhill gravity."""
    entry = speed + delay * slope_accel
    coast = delay * (speed + entry) / 2
    net = (wheel_kn + rail_kn) * 1000 / mass - slope_accel
    distance = entry**2 / (2 * net) if net > 0 else None
    return dict(net_deceleration_m_s2=net, build_up_entry_speed_m_s=entry, delay_distance_m=coast,
                stop_distance_m=coast + distance if distance is not None else None,
                stop_time_s=delay + entry / net if distance is not None else None,
                wheel_dissipation_kwh=wheel_kn * 1000 * distance / KWH if distance is not None else None,
                rail_dissipation_kwh=rail_kn * 1000 * distance / KWH if distance is not None else None,
                work_energy_residual_kwh=((wheel_kn + rail_kn) * 1000 * distance
                    - mass * (speed**2 / 2 + slope_accel * (coast + distance))) / KWH if distance is not None else None)


def brake_case(row, speed, delay, grade, mu, modules, target, stop_room, overlap, length):
    mass = row["loaded_train_kg"]
    downhill = G * grade
    failed_axle = max(row["axles"], key=lambda name: row["axles"][name]["loaded_kg"])
    lost_kg = row["axles"][failed_axle]["loaded_kg"]
    cases = {}
    for wheel, active in product(("all", "one_out", "none"), (modules, modules - 1)):
        supported = {"all": mass, "one_out": mass - lost_kg, "none": 0.0}[wheel]
        wheel_force = mu * supported * G / 1000
        required = max(0.0, mass * (target + downhill) / 1000 - wheel_force)
        target_stop = stop(speed, delay, downhill, mass, min(wheel_force, mass * (target + downhill) / 1000), required)
        comparator = stop(speed, delay, downhill, mass, wheel_force, active * MODULE_COMPARATOR_KN)
        unassisted = stop(speed, delay, downhill, mass, wheel_force, 0)
        room_for_braking = None if stop_room is None or overlap is None else stop_room - overlap
        entry = target_stop["build_up_entry_speed_m_s"]
        target_distance = target_stop["stop_distance_m"]
        compare_distance = comparator["stop_distance_m"]
        cases[f"{wheel}_wheel_brakes/{modules - active}_rail_modules_out"] = dict(
            wheel_mode=wheel, rail_modules_available=active, wheel_force_upper_bound_kn=wheel_force,
            required_rail_force_kn=required, required_force_per_available_module_kn=required / active,
            proposed_comparator_per_module_kn=MODULE_COMPARATOR_KN,
            comparator_force_margin_per_module_kn=MODULE_COMPARATOR_KN - required / active,
            required_rail_energy_per_module_kwh=target_stop["rail_dissipation_kwh"] / active,
            required_peak_rail_interface_kw_per_module=required * entry / active,
            stop_at_target=target_stop, stop_at_comparator=comparator, stop_wheel_only=unassisted,
            all_rail_demand_kn=mass * (target + downhill) / 1000,
            target_front_stop_plus_train_and_overlap_m=None if overlap is None else target_distance + length + overlap,
            comparator_front_stop_plus_train_and_overlap_m=None if overlap is None or compare_distance is None
                else compare_distance + length + overlap,
            target_stop_room_margin_m=None if room_for_braking is None else room_for_braking - target_distance,
            comparator_stop_room_margin_m=None if room_for_braking is None or compare_distance is None
                else room_for_braking - compare_distance,
            documented_rail_interface_limit_kw=None, documented_repeat_duty=None)
    return dict(wheel_adhesion_assumed=mu, downgrade_pct=100 * grade, coast_delay_s=delay,
                target_net_deceleration_m_s2=target, lost_wheel_brake_axle=failed_axle, cases=cases)


def traction_case(row, power, grade):
    mass = row["loaded_train_kg"]
    mu = power["low_adhesion_mu"]
    demand = (power["required_net_accel_m_s2"] + power["resistance_accel_m_s2"] + G * grade) * mass
    factored = demand * power["adhesion_force_margin"]
    # Identical cars, with each powered pair sharing a bogie. For a partial-drive
    # layout show both bogie choices, retaining the heavier loss for each layout.
    patterns = [(0, 1), (2, 3), (0, 1, 2, 3)]
    axles = row["axle_kg_per_car"]
    cars = len(row["axles"]) // len(axles)
    layout = []
    for positions in patterns:
        nominal = cars * sum(axles[j] for j in positions)
        failed = max(positions, key=axles.__getitem__)
        for fault, supported in (("all_available", nominal), ("heaviest_driven_axle_out", nominal - axles[failed])):
            force = supported * G * mu
            layout.append(dict(driven_positions_per_car=[j + 1 for j in positions], fault=fault,
                               driven_axle_count=cars * len(positions) - (fault != "all_available"),
                               driven_static_load_fraction=supported / mass, adhesion_upper_bound_kn=force / 1000,
                               required_adhesion_with_margin=factored / (supported * G),
                               margin_kn=(force - factored) / 1000))
    return dict(upgrade_pct=100 * grade, roll_resistance_m_s2=power["resistance_accel_m_s2"],
                adhesion_assumed=mu, required_train_force_kn=demand / 1000, factored_train_force_kn=factored / 1000,
                min_driven_static_load_fraction=factored / (mass * G * mu), layouts=layout)


def battery_case(cfg):
    service = cfg["service_power"]
    load = service["control_continuous_kw"] + service["other_essential_continuous_kw"]
    demand = (load * service["protected_outage_hours"] + service["brake_event_kwh"]
              + service["door_egress_event_kwh"]) * (1 + service["energy_reserve_fraction"])
    nominal = service["battery_nominal_kwh"]
    usable = service["usable_fraction"]
    return dict(scope="One fixed per-train service pack in both studied formations; actual equipment position and consumption await evidence.",
                usable_new_kwh=nominal * usable, usable_at_80pct_retention_kwh=nominal * usable * .8,
                demand_with_reserve_kwh=demand, new_margin_kwh=nominal * usable - demand,
                end_of_life_margin_kwh=nominal * usable * .8 - demand,
                minimum_nominal_kwh_at_80pct_retention=demand / (usable * .8),
                minimum_retention_fraction=demand / (nominal * usable),
                nominal_kwh=nominal, continuous_kw=load, recharge_input_kw=nominal / (
                    service["recharge_hours"] * service["recharge_efficiency"]),
                brake_electrical_input_vs_4kwh_allocation=None, required_hot_discharge_peak_kw=None)


def fit_case(record, cage, fit, ga, rows, material):
    door = record["doorway"]
    edges = door["per_edge_allowances_m"]
    aperture = min(door["rough_widths_m"])
    allocated = aperture - 2 * sum(edges.values()) - door["required_fitted_m"]
    gap = min(pad["stock_face_gap_mm"] for bogie in fit["bogies"]
              for pad in bogie["pads"] if pad["type"] == "secondary_top")
    pivot = record["bogie_translations_m"][1]
    compression = {}
    for state, row in rows.items():
        payload = row["group_allocations"]["payload"]["mass_kg_per_car"]
        load_kn = payload * G / 2000 * (.5 + abs(row["passenger_centroid_x_m"]) / (2 * pivot))
        compression[state] = {str(k): dict(payload_compression_mm=load_kn / k,
                                           trial_40mm_stroke_margin_mm=40 - load_kn / k)
                              for k in (.6, 1.0, 1.6)}
    return dict(
        scope="Steel stock geometry at its nominal pose. Alternatives have no released aperture, joint or stack geometry."
        if material != "steel" else "Steel stock and passive-travel sensitivities. Installed interfaces need measurements.",
        steel_stock_door_sweep=door["leaf_sweep"], aperture_planes=ga["geometry"]["door_apertures"],
        nominal_allocated_portal_margin_mm=1000 * allocated,
        doubled_loaded_distortion_margin_mm=1000 * (allocated - 2 * edges["loaded_distortion_per_edge_m"]),
        straight_platform_gap_mm=1000 * cage["station_interfaces"]["static_level_horizontal_gap_m"],
        measured_boarding_pose=None, minimum_stock_secondary_gap_mm=gap,
        static_stack_margin_mm={str(s): gap - s for s in (145, 155, 165)},
        passive_incremental_payload_cases=compression, bogie_stock_transforms_and_sweeps=fit["bogies"],
        equipped_exchange_verified=False, installed_door_and_suspension_verified=False)


def assess_return(basis, submission, directory, *, route_bound=False):
    if submission is None:
        return dict(submission_id=None, claim=None, documents={}, submitted={}, missing=list(PHYSICAL_RETURNS),
                    physical_accepted=False)
    if (not isinstance(submission, dict) or submission.keys() != {"basis", "kind", "documents", "returns"}
            or submission["basis"] != basis
            or submission["kind"] not in ("supplier-declaration", "physical-measurement", "synthetic-fixture")):
        raise ValueError("Bind the evidence return to this exact vehicle and duty")
    docs = commercial.evidence(submission["documents"], directory)
    rows = submission["returns"]
    if not isinstance(rows, dict) or rows.keys() - PHYSICAL_RETURNS.keys():
        raise ValueError("Use the named vehicle evidence scopes")
    if "route_protection" in rows and not route_bound:
        raise ValueError("Bind the route protection return to an evaluated alignment")
    for scope, row in rows.items():
        if (not isinstance(row, dict) or row.keys() != {"document", "article_serial", "procedure_revision", "witness"}
                or not commercial.has_document(row["document"], docs)
                or not all(isinstance(row[k], str) and row[k].strip() for k in ("article_serial", "procedure_revision", "witness"))):
            raise ValueError(f"Incomplete candidate-specific attachment citation for {scope}")
    return dict(submission_id=car.identity(submission), claim=submission["kind"], documents=docs, submitted=rows,
                missing=sorted(PHYSICAL_RETURNS.keys() - rows.keys()), physical_accepted=False,
                scope="Attachment custody only. Authentication, approved limits, suitability for the exact duty and independent review remain open.")


def evaluate(*, cars=6, material="steel", grade_pct=None, available_stop_m=None, overlap_m=None,
             route=None, alignment=None, evidence_return=None, evidence_directory=None):
    """Audit a studied formation. A distance allowance includes the withheld overlap."""
    if type(cars) is not int or cars not in (3, 6) or material not in vehicle_civil.MATERIAL:
        raise ValueError("Choose a supported Airport train formation and body material")
    record, cage, fit, opening, ga, bom, bogie, sources = source_data()
    cfg = tomllib.loads(SYSTEM.read_text())
    design_grade = cfg["power_assumptions"]["adverse_grade"]
    if alignment is not None:
        if route is not None:
            raise ValueError("Supply one Airport alignment basis")
        airport_alignment.validate(alignment)
        if alignment["parent_candidate_id"] != opening["candidate_id"]:
            raise ValueError("Alignment and vehicle audit identify different Airport candidates")
    if route is not None:
        stops = [(s["id"], s["chainage_km"], s["register_id"]) for s in route["stops"]]
        route_basis = dict(parent=opening["candidate_id"], stops=stops, grade_pct=route["grade_pct"], cars=cars)
        if (route["candidate_id"] != vehicle_civil.digest(route_basis) or route["cars"] != cars
                or route["parent_candidate_id"] != opening["candidate_id"]
                or route["opening_evaluation_id"] != opening["evaluation_id"]
                or (grade_pct is not None and grade_pct != abs(route["grade_pct"]))):
            raise ValueError("Route and vehicle audit identify different candidates or grades")
        grade_pct = abs(route["grade_pct"])
    grade_pct = design_grade * 100 if grade_pct is None else grade_pct
    for value, label in ((grade_pct, "grade"), (available_stop_m, "stop allowance"), (overlap_m, "overlap")):
        if value is not None:
            commercial.number(value, label)
    if grade_pct > 100 * design_grade or (available_stop_m is not None and overlap_m is not None and overlap_m > available_stop_m):
        raise ValueError("Outside the Airport stopping-screen domain")

    pitch = ga["geometry"]["formation_body_from_car_x_m"][1] - ga["geometry"]["formation_body_from_car_x_m"][0]
    centres = [(i - (cars - 1) / 2) * pitch for i in range(cars)]
    length = cfg["vehicle_geometry"]["car_body_length_m"] + (cars - 1) * pitch
    cases = mass_cases(record, bogie, cfg["service_power"], cars, material, centres)
    speed = cfg["vehicle"]["speed_cap_kmh"] / 3.6
    net = tomllib.loads(TRIAL.read_text())["braking_deceleration_m_s2"]
    trial_inputs = dict(grade_pct=grade_pct, speed_kmh=speed * 3.6, available_stop_m=available_stop_m,
                        overlap_m=overlap_m, brake_delays_s=[0.0, 2.0], wheel_adhesions=[.08, cfg["power_assumptions"]["low_adhesion_mu"]],
                        net_decelerations_m_s2=[net, 1.0], rail_modules_per_car=2, published_comparator_kn=MODULE_COMPARATOR_KN,
                        route_candidate_id=None if route is None else route["candidate_id"])
    if alignment is not None:
        trial_inputs.update(alignment_id=alignment["alignment_id"], alignment_record_id=alignment["record_id"])
    physical = dict(parent_candidate_id=opening["candidate_id"], frame_revision=ga["frame_revision"],
                    formation_cars=cars, material=material, car_centres_train_x_m=centres,
                    length_m=length, powered_axle_positions_per_car=[1, 2, 3, 4], supply="protected_conductor")
    candidate_id = car.identity(physical)
    duty_id = car.identity(dict(candidate_id=candidate_id, controls=trial_inputs, sources=sources))
    basis = dict(physical_candidate_id=candidate_id, duty_id=duty_id, frame_revision=ga["frame_revision"],
                 opening_evaluation_id=opening["evaluation_id"], mechanical_evaluation_id=record["evaluation_id"])
    grades_pct = sorted({0., float(grade_pct), 100 * design_grade})
    braking = {state: [brake_case(row, speed, delay, grade / 100, mu, 2 * cars, target, available_stop_m, overlap_m, length)
                       for grade, delay, mu, target in product(grades_pct, trial_inputs["brake_delays_s"],
                           trial_inputs["wheel_adhesions"], trial_inputs["net_decelerations_m_s2"])]
               for state, row in cases.items() if state != "low"}
    level_force_reference = [{
        "downgrade_pct": grade, "coast_delay_s": delay,
        **stop(speed, delay, G * grade / 100, cases["central"]["loaded_train_kg"],
               cases["central"]["loaded_train_kg"] * net / 1000, 0),
    } for grade, delay in product(grades_pct, trial_inputs["brake_delays_s"])]
    selected = dict(candidate_id=candidate_id, physical=physical, inputs=trial_inputs, duty_id=duty_id, basis=basis,
                    source_sha256=sources, installed_ga_evaluation_id=ga["evaluation_id"],
                    parent_fitout_evaluation_id=fit["evaluation_id"], parent_civil_article_evaluation_id=cage["evaluation_id"],
                    room_scope="Front-to-protected-limit distance must come from the alignment and signalling design. Interstation distance cannot establish an overlap.",
                    mass_cases=cases, measured_installed_mass_kg=None,
                    mass_scope="Low, central and high planning allocations for identical car loads. Gross cut stock is untrimmed. No complete installed weight or certified axle bounds.",
                    released_bom_basis="Steel six-car article. Quantities label the source release even for other study formations. Blank installed masses remain unknown.",
                    released_steel_bom=[{**row, "installed_mass_kg": float(row["installed_mass_kg"]) if row["installed_mass_kg"] else None}
                                        for row in bom],
                    braking=braking, level_service_force_reference=level_force_reference,
                    traction={state: traction_case(row, cfg["power_assumptions"], grade_pct / 100)
                                              for state, row in cases.items() if state != "low"},
                    battery=battery_case(cfg), fit=fit_case(record, cage, fit, ga, cases, material),
                    return_assessment=assess_return(basis, evidence_return, evidence_directory,
                                                    route_bound=alignment is not None or route is not None),
                    return_template=dict(basis=basis, kind=None, documents={}, returns={}),
                    physical_measurements_required=PHYSICAL_RETURNS,
                    braking_scope="Static-load adhesion upper bounds, worst single-axle failure, constant-force analytical sensitivities with gravity during coast, no drag or regeneration. Rail-contact dissipation includes the rail and shoe; train excitation and equipment heat split are unknown.",
                    documented_weight_return="Use the prototype weights intake for a complete candidate-specific train-weight recalculation.",
                    physical_accepted=False)
    return {**selected, "evaluation_id": car.identity(selected)}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--cars", type=int, choices=(3, 6), default=6)
    cli.add_argument("--material", choices=vehicle_civil.MATERIAL, default="steel")
    cli.add_argument("--grade-pct", type=float)
    cli.add_argument("--available-stop-m", type=float)
    cli.add_argument("--overlap-m", type=float)
    cli.add_argument("--evidence-return", type=Path)
    args = vars(cli.parse_args())
    path = args.pop("evidence_return")
    if path is not None:
        args.update(evidence_return=json.loads(path.read_bytes()), evidence_directory=path.parent)
    print(json.dumps(evaluate(**args), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
