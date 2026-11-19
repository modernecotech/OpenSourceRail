"""Generate separate rail-datum and independent-brake test schedules for the reference vehicles."""
import argparse
import gzip
import hashlib
import json
from math import asin, cos, degrees, hypot, sin
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "engineering/interface_studies/reference-rigs.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def envelope(parts, prefix):
    group = [p for p in parts if p["id"].startswith(prefix + "/")]
    if not group or any(p["kind"] != "box" for p in group):
        raise ValueError(f"Rectangular stock required for {prefix}")
    return [(min(p["at_m"][axis] for p in group),
             max(p["at_m"][axis] + p["size_m"][axis] for p in group))
            for axis in range(3)]


def sideframe_sweep(parts, pivots, inward_shift_m=0.0):
    """Signed transverse separation within coincident vertical and longitudinal intervals."""
    half_pitch = (pivots[1] - pivots[0]) / 2
    rows = []
    for radius in (None, 500., 250., 150.):
        yaw = asin(half_pitch / radius) if radius else 0.
        gaps = []
        hub_gaps = []
        for index, pivot in enumerate(pivots):
            for side in (-1, 1):
                frame = envelope(parts, f"bogie/{index}/sideframe/{side}")
                sill = envelope(parts, f"wheel-underframe/sill/{side}")
                if min(frame[2][1], sill[2][1]) <= max(frame[2][0], sill[2][0]):
                    raise ValueError("Frame and sill are vertically separated; use 3D clearance")
                frame[1] = tuple(y - side * inward_shift_m for y in frame[1])
                for axle in (0, 1):
                    hub_id = f"bogie/{index}/wheel/{axle}/{side}/hub"
                    hub = next(p for p in parts if p["id"] == hub_id)
                    x, y, z = hub["at_m"]
                    if not (hub["axis"] == [0, 1, 0] and frame[0][0] <= x <= frame[0][1]
                            and z < frame[2][0] < z + hub["radius_m"]):
                        raise ValueError("Hub/sideframe projection outside declared geometry")
                    hub_outer = max(side*y, side*(y + hub["length_m"]))
                    hub_gaps.append(min(side*y for y in frame[1]) - hub_outer)
                sill_near = min(side * y for y in sill[1])
                for angle in (yaw, -yaw):
                    corners = [(pivot + (x-pivot)*cos(angle) - y*sin(angle),
                                (x-pivot)*sin(angle) + y*cos(angle))
                               for x in frame[0] for y in frame[1]]
                    if any(x < sill[0][0] or x > sill[0][1] for x, _ in corners):
                        raise ValueError("Rotated stock leaves the sill length; use finite geometry")
                    gaps.append(sill_near - max(side*y for _, y in corners))
        rows.append(dict(curve_radius_m=radius, bogie_yaw_deg=degrees(yaw),
                         minimum_sideframe_to_sill_gap_m=min(gaps),
                         minimum_hub_to_sideframe_gap_m=min(hub_gaps)))
    return rows


def datum_schedule():
    selector = tomllib.loads((ROOT / "engineering/development-baseline.toml").read_text())
    brief_path = ROOT / selector["source_brief"]
    if digest(brief_path) != selector["source_brief_sha256"]:
        raise ValueError("Reference brief differs from selector")
    brief = tomllib.loads(brief_path.read_text())
    packet_path = ROOT / "docs/design-engine/current/evaluation.json.gz"
    with gzip.open(packet_path) as stream:
        packet = json.load(stream)
    if (packet["candidate_id"] != selector["vehicle_candidate_id"]
            or packet["support_component_id"] != selector["support_component_id"]
            or packet["body_candidate_id"] != selector["body_candidate_id"]):
        raise ValueError("Reference body or running gear differs from the selected packet")
    body, gear = brief["vehicle"], brief["support"]
    fin_bottom = brief["propulsion"]["secondary_bottom_above_rail_m"]
    wear = (gear["wheel_new_diameter_m"] - gear["wheel_worn_diameter_m"]) / 2
    rows = []
    for state, radius_loss, levelling in (
            ("new wheels", 0, 0), ("worn, uncompensated", wear, 0),
            ("worn, full body-height compensation", wear, wear)):
        offset = levelling - radius_loss
        rows.append(dict(state=state, floor_z_m=body["floor_top_above_rail_m"] + offset,
                         fin_bottom_z_m=fin_bottom + offset,
                         axle_z_m=gear["wheel_new_diameter_m"] / 2 - radius_loss,
                         assumed_body_lift_m=levelling))
    layout = packet["vehicle"]["seating_layout"]
    pitch = body["body_length_m"] + body["coupling_gap_m"]
    door_centres = [pitch * (i - (body["cars"] - 1) / 2) + door
                    for i in range(body["cars"]) for door in layout["door_centres_x_m"]]
    return dict(candidate_id=packet["candidate_id"], parent_evaluation=packet["evaluation_id"],
                packet_sha256=digest(packet_path), source_brief_sha256=digest(brief_path),
                per_car_axle_x_m=[pivot + side * gear["bogie_wheelbase_m"] / 2
                                  for pivot in gear["bogie_centres_x_m"] for side in (-1, 1)],
                door_centres_train_x_m=door_centres, opening_m=layout["door_width_m"],
                sideframe_sweep=sideframe_sweep(packet["vehicle"]["geometry_parts"], gear["bogie_centres_x_m"]),
                adjustable_jig=dict(sideframe_inward_offset_m=0.035,
                                    fixed_parts="wheels, axles and body sills",
                                    sweep=sideframe_sweep(packet["vehicle"]["geometry_parts"],
                                                          gear["bogie_centres_x_m"], 0.035)),
                vertical_setups=rows, suspension_stroke_available_m=None,
                installed_clearance_verified=False)


def brake_case(mass_kg, speed, grade_fraction, deceleration, delay, active):
    """Coast on downgrade during delay, then apply a constant net deceleration."""
    gravity = 9.80665 * grade_fraction / hypot(1, grade_fraction)
    entry_speed = speed + gravity * delay
    apply_distance = entry_speed ** 2 / (2 * deceleration)
    force = mass_kg * (deceleration + gravity)
    return dict(delay_s=delay, brake_entry_speed_m_s=entry_speed,
                stop_distance_m=speed * delay + gravity * delay ** 2 / 2 + apply_distance,
                longitudinal_force_N_per_active_module=force / active,
                peak_contact_power_W_per_active_module=force * entry_speed / active,
                interface_energy_J_per_active_module=force * apply_distance / active,
                static_grade_force_N_per_active_module=mass_kg * gravity / active)


def brake_schedule():
    digital = ROOT / "docs/reference-v07/digital"
    selection_path = digital / "selected.toml"
    sel = tomllib.loads(selection_path.read_text())
    base_path = digital.parent / "integration/candidate.toml"
    mass_path = digital / "vehicle/result.json"
    inputs = sel["source_sha256"]
    if (digest(base_path) != inputs["parent_joined_candidate"]
            or digest(mass_path) != inputs["digital_vehicle_result"]):
        raise ValueError("Brake rig requires the selected joined inputs")
    candidate = tomllib.loads(base_path.read_text())
    mass = json.loads(mass_path.read_text())
    if not (sel["parent_joined_physical_candidate_id"] == candidate["physical_candidate_id"]
            == mass["joined_physical_candidate_id"]):
        raise ValueError("Digital vehicle ancestry mismatch")
    p = candidate["performance"]
    modules = candidate["vehicle"]["independent_rail_brake_modules_per_train"]
    rows = []
    for duty, name in (("normal", "normal_kg_per_six_car_train"),
                       ("crowd structural sensitivity", "crowd_160_kg_per_six_car_train")):
        kg = mass["sizing_load_handoff"][name]
        for delay in (0.0, 1.0, 2.0):
            result = brake_case(kg, p["speed_cap_kmh"] / 3.6, p["grade_sizing_case_percent"] / 100,
                                p["service_deceleration_demand_mps2"], delay, modules - 1)
            rows.append(dict(duty=duty, analytical_mass_kg=kg, **result))
    return dict(candidate_id=sel["physical_candidate_id"], parent_evaluation=sel["evaluation_id"],
                selected_input_sha256=digest(selection_path), input_sha256=inputs,
                working_modules=modules - 1, available_force_N=None,
                delay_limit_s=None, cases=rows, physical_acceptance=False)


def build():
    result = dict(passive_datum_rig=datum_schedule(), powered_brake_rig=brake_schedule(),
                  evaluator_sha256=digest(Path(__file__)))
    result["study_id"] = hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()
    return json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = build()
    if args.check:
        if OUTPUT.read_text() != data:
            raise SystemExit("Regenerate the reference rig schedules")
    else:
        OUTPUT.write_text(data)
