"""Build the Baghdad first-article mechanical quotation schedule (standard library)."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import tomllib

from drawing import drawing


HERE = Path(__file__).resolve().parent
CITY = HERE.parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def identity(value):
    return digest(json.dumps(value, separators=(",", ":"), sort_keys=True).encode())


def moving_load(axles, span, step, axle_kn):
    """Sample all train positions. For each pose, exact simple-span point-load statics."""
    if not 0 < step <= span or not axles:
        raise ValueError("Positive translation step and axles required")
    max_shear = (0, 0)
    max_moment = (0, 0, 0)
    start = -max(axles)
    steps = math.ceil((span - min(axles) - start) / step)
    for i in range(steps + 1):
        car_shift = start + i * step
        xs = [max(0, min(span, x + car_shift)) for x in axles
              if -1e-9 <= x + car_shift <= span + 1e-9]
        left = sum(1 - x / span for x in xs) * axle_kn
        right = len(xs) * axle_kn - left
        max_shear = max(max_shear, (max(left, right), car_shift))
        for x in xs:
            moment = left * x - sum(max(0, x - xp) for xp in xs) * axle_kn
            max_moment = max(max_moment, (moment, car_shift, x))
    return {
        "max_end_reaction_kn_sampled": round(max_shear[0], 3),
        "reaction_pose_train_centre_m_from_left_support": round(max_shear[1], 3),
        "max_live_moment_knm_sampled": round(max_moment[0], 3),
        "moment_pose_train_centre_m_from_left_support": round(max_moment[1], 3),
        "moment_location_m_from_left_support": round(max_moment[2], 3),
    }


def evaluate():
    design = tomllib.loads((HERE / "quotation.toml").read_text())
    cfg = tomllib.loads((CITY / "system.toml").read_text())
    system = json.loads((CITY / "system-results.json").read_text())
    network = system["networks"][design["network"]]
    supply = network["power_cases"][design["supply"]]
    civil = network["civil_cases"][design["civil"]]
    geom = cfg["vehicle_geometry"]
    stn = cfg["station_geometry"]
    vehicle = cfg["vehicle"]
    rig = design["rig"]
    screen = design["screen"]
    if (cfg["candidate_id"] != system["candidate_id"]
            or system["source_sha256"]["cities/Baghdad/system.toml"] != digest((CITY / "system.toml").read_bytes())
            or cfg["preferred_supply"].replace("-", "_") != design["supply"]
            or network["selected_candidate_id"] != supply["physical_candidate_id"]
            or network["selected_digital_civil_family"] != design["civil"]
            or network["selected_station_interfaces"]["vehicle"] != geom
            or network["selected_station_interfaces"]["station"] != stn):
        raise ValueError("Inconsistent Baghdad system, station or civil selection")
    n = vehicle["cars_per_train"]
    h = geom["car_body_length_m"] / 2
    w = geom["body_width_m"] / 2
    pivots = geom["bogie_centres_m"]
    if len(pivots) != 2 or pivots[1] != -pivots[0] or n < 2:
        raise ValueError("This screen requires a symmetric two-bogie car in a multi-car formation")
    intercar_gap = (geom["train_length_m"] - 2 * h * n) / (n - 1)
    if intercar_gap < 0:
        raise ValueError("Train shorter than sum of body lengths")
    centre_pitch = 2 * h + intercar_gap
    centres = [(i - (n - 1) / 2) * centre_pitch for i in range(n)]
    axle_offsets = [p + d * rig["wheelbase_m"] / 2 for p in pivots for d in (-1, 1)]
    axles = [x + a for x in centres for a in axle_offsets]
    if len(axles) != vehicle["axles_per_train"] or len(axles) != supply["driven_axles"]:
        raise ValueError("Drive layout and train axle counts differ")
    door_centres = geom["door_centres_m"]
    stop_error = screen["station_stop_error_m"]
    half_open = geom["door_clear_width_m"] / 2
    platform_half = stn["platform_clear_length_m"] / 2
    doors = []
    for i, x in enumerate(centres, start=1):
        for d in door_centres:
            station_x = x + d
            if abs(station_x) + half_open + stop_error > platform_half:
                raise ValueError("Door sweep exceeds island")
            doors.append({
                "car": i, "platform_x_m": round(station_x, 3),
                "edge_keep_clear_x_m": [round(station_x - half_open - stop_error, 3),
                                        round(station_x + half_open + stop_error, 3)],
            })
    if len(doors) != vehicle["door_openings_per_car_each_side"] * n:
        raise ValueError("Door quantity disagrees with vehicle schedule")
    curves = []
    for radius in screen["curve_radii_m"]:
        # Car centre follows the chord connecting the two pivot centres.
        apothem = math.sqrt(radius**2 - pivots[1]**2)
        mid_throw = radius - apothem
        end_throw = math.hypot(apothem + w, h) - (radius + w)
        curves.append({"radius_m": radius, "inward_midbody_throw_mm": round(mid_throw*1000, 1),
                       "outward_corner_throw_mm": round(end_throw*1000, 1),
                       "bogie_yaw_deg": round(math.degrees(math.asin(pivots[1]/radius)), 2)})
    axle_load = supply["train_crowd_mass_t"] * 9.80665 / len(axles)
    span = cfg["selected_span_m"]
    inset = design["civil_seat"]["longitudinal_inset_m"]
    effective_span = span - 2 * inset
    y_seat = design["civil_seat"]["lateral_m"]
    bays = stn["platform_clear_length_m"] / design["platform"]["deck_bay_m"]
    if not bays.is_integer():
        raise ValueError("Platform needs an explicit non-uniform end bay")
    # Keep identical physical proposals stable when only evaluation hypotheses change.
    assembly = {"parent_physical_id": supply["physical_candidate_id"],
                "vehicle": geom, "station": stn, "car_count": n,
                "rig": rig, "platform_frame": design["platform"],
                "civil_option_id": civil["civil_option_physical_id"],
                "civil_seat": design["civil_seat"]}
    return {
        "study": design["study"], "purpose": "prototype quotation and interface screening",
        "parent_project_id": cfg["candidate_id"], "network": design["network"],
        "parent_selected_candidate_id": supply["physical_candidate_id"],
        "parent_evaluation_id": network["selected_evaluation_id"],
        "study_physical_id": identity(assembly),
        "study_evaluation_id": identity([assembly, screen, network["selected_evaluation_id"],
                                         digest(Path(__file__).read_bytes())]),
        "sources_sha256": {p.name: digest(p.read_bytes()) for p in (
            CITY / "system.toml", CITY / "system-results.json", HERE / "quotation.toml", HERE / "drawing.py", Path(__file__))},
        "schemes": {"system_selected": False, "fabrication_released": False, "physically_accepted": False},
        "train": {"uniform_intercar_gap_m_assumption": round(intercar_gap, 3),
                  "car_centres_m": centres, "body_bogie_x_m": pivots,
                  "body_axle_x_m": [round(x, 3) for x in axle_offsets],
                  "crowd_mean_static_axle_kn": round(axle_load, 3),
                  "crowd_mean_static_secondary_seat_kn": round(axle_load, 3),
                  "crowd_mean_static_primary_seat_kn": round(axle_load/2, 3),
                  "reaction_scope": "Equal lumped gravity split, ignores sprung/unsprung split and unequal loading",
                  "curve_screen": curves},
        "bogie_exchange": {
            "minimum_plan_lane_width_m": max(rig["frame_width_m"], rig["transfer_pallet_width_m"])
                                         + 2*rig["handling_standoff_m"],
            "outward_translation_m_to_clear_body_end":
                round(h - pivots[1] + rig["frame_length_m"]/2 + rig["handling_standoff_m"], 3),
            "scope": "Separated straight car, frame and pallet widths only; wheels, fittings, lines, shop and overhead obstructions unresolved"},
        "station": {"platform_edge_schedule_per_boarding_side": doors,
                    "bent_x_m_from_platform_midpoint": [
                        -platform_half+i*design["platform"]["deck_bay_m"] for i in range(int(bays)+1)],
                    "paired_column_y_m": [-design["platform"]["bent_column_lateral_m"],
                                           design["platform"]["bent_column_lateral_m"]]},
        "viaduct": {"beam_stock_length_m": span, "effective_span_m_hypothesis": effective_span,
                    "bearing_seat_xy_m_from_stock_end": [[x,y] for x in (inset, span-inset)
                                                          for y in (-y_seat, y_seat)],
                    "bearing_units_provisional": 4*civil["beam_count"],
                    "track_beam_count": civil["beam_count"],
                    "separate_support_positions": civil["pier_foundation_count"],
                    "moving_gravity_only": moving_load(axles, effective_span, screen["load_step_m"], axle_load)},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    geometry = tomllib.loads((CITY / "system.toml").read_text())["vehicle_geometry"]
    rig = tomllib.loads((HERE / "quotation.toml").read_text())["rig"]
    outputs = {
        HERE / "schedule.json": json.dumps(evaluate(), indent=2, allow_nan=False) + "\n",
        HERE / "bogie-interface.svg": drawing(geometry, rig),
    }
    for output, expected in outputs.items():
        if args.check:
            if output.read_text() != expected:
                raise SystemExit(f"Mechanical output is stale: {output.name}")
        else:
            output.write_text(expected)
    if args.check:
        print("Mechanical schedule and drawing match")
