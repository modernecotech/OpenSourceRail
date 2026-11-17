"""Reproduce bounded car mass, CG and static reactions for the joined v0.7 concept.

Only modelled geometry and declared mass budgets enter the calculation. Unknown
component centroids remain explicit intervals. No weighing or physical fit is
inferred from this digital result.
"""
from __future__ import annotations

import argparse
import gzip
from hashlib import sha256
from itertools import product
import json
from math import fsum, isclose
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[2]
INPUT = Path("docs/reference-v07/digital/vehicle/input.json")
OUTPUT = Path("docs/reference-v07/digital/vehicle/result.json")
G = 9.81


def encoded(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def identity(value: object) -> str:
    return sha256(encoded(value)).hexdigest()


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _read(root: Path, path: str) -> object:
    file = root / path
    if file.is_symlink() or not file.is_file():
        raise ValueError("Regular source required: " + path)
    if path.endswith(".gz"):
        with gzip.open(file, "rt") as stream:
            return json.load(stream)
    if path.endswith(".toml"):
        return tomllib.loads(file.read_text())
    return json.loads(file.read_bytes())


def _bounds(located: list[tuple[float, list[float]]],
            uncertain: list[tuple[tuple[float, float], list[list[float]]]]) -> dict:
    """Extrema for independent mass and centroid interval assumptions."""
    extrema = [[float("inf"), float("-inf")] for _ in range(3)]
    reactions = {"left_bogie_N": [float("inf"), float("-inf")],
                 "right_bogie_N": [float("inf"), float("-inf")]}
    fixed_mass = fsum(m for m, _ in located)
    fixed_moments = [fsum(m * xyz[axis] for m, xyz in located) for axis in range(3)]
    for ends in product((0, 1), repeat=len(uncertain)):
        masses = [row[0][end] for row, end in zip(uncertain, ends)]
        total = fixed_mass + fsum(masses)
        moments = []
        for axis in range(3):
            low = fixed_moments[axis] + fsum(
                m * row[1][axis][0] for m, row in zip(masses, uncertain))
            high = fixed_moments[axis] + fsum(
                m * row[1][axis][1] for m, row in zip(masses, uncertain))
            extrema[axis][0] = min(extrema[axis][0], low / total)
            extrema[axis][1] = max(extrema[axis][1], high / total)
            moments.append((low, high))
        left_low = G * (total / 2 - moments[0][1] / 12.8)
        left_high = G * (total / 2 - moments[0][0] / 12.8)
        right_low = G * (total / 2 + moments[0][0] / 12.8)
        right_high = G * (total / 2 + moments[0][1] / 12.8)
        reactions["left_bogie_N"][0] = min(reactions["left_bogie_N"][0], left_low)
        reactions["left_bogie_N"][1] = max(reactions["left_bogie_N"][1], left_high)
        reactions["right_bogie_N"][0] = min(reactions["right_bogie_N"][0], right_low)
        reactions["right_bogie_N"][1] = max(reactions["right_bogie_N"][1], right_high)
    return {"mass_kg": [
                fixed_mass + fsum(row[0][0] for row in uncertain),
                fixed_mass + fsum(row[0][1] for row in uncertain)],
            "cg_interval_car_xyz_m": [
                {"minimum_m": low, "maximum_m": high} for low, high in extrema],
            "bogie_reaction_interval_N": reactions,
            "equal_share_axle_reaction_interval_N": {
                name.replace("bogie", "axle"): [low / 2, high / 2]
                for name, (low, high) in reactions.items()}}


def build(root: Path = ROOT) -> dict:
    root = Path(root)
    inp = _read(root, str(INPUT))
    if inp.get("schema") != "osr-v07-joined-digital-car-input/1":
        raise ValueError("Input schema differs")
    if identity({k: v for k, v in inp.items() if k != "input_id"}) != inp.get("input_id"):
        raise ValueError("Input identity differs")
    for name, expected in inp["source_sha256"].items():
        if digest(root / name) != expected:
            raise ValueError("Pinned source differs: " + name)
    joined = _read(root, "docs/reference-v07/integration/candidate.toml")
    powered = _read(root, "docs/design-engine/v07-powered-vehicle/plan.json")
    bundle = _read(root, "docs/design-engine/v07-prototype-bundle/packet/result.json")
    civil = _read(root, "docs/design-engine/v07-simple-span/plan.json")
    selected = _read(root, "docs/design-engine/current/evaluation.json.gz")
    manifest = _read(root, "docs/design-engine/current/manifest.json")
    if (joined["physical_candidate_id"] != inp["joined_physical_candidate_id"]
            or joined["selection_id"] != inp["joined_selection_id"]
            or joined["vehicle"]["cars_per_train"] != 6
            or joined["vehicle"]["driven_axles_per_train"] != 24
            or joined["civil"]["beam_length_m"] != 10
            or joined["performance"]["dc_nominal_voltage_v"] != 1500
            or bundle["candidate"]["candidate_id"] != joined["ancestry"]["powered_vehicle_physical_candidate_id"]
            or civil["physical_candidate_id"] != joined["ancestry"]["joint_free_span_physical_candidate_id"]
            or powered["selected_parent_candidate_id"] != selected["candidate_id"]
            or bundle["candidate"]["physical_definition"]["mechanical_vehicle_component_id"] != powered["physical_candidate_id"]
            or civil["vehicle_research_child_id"] != powered["physical_candidate_id"]
            or bundle["evaluation"]["native_ifc"]["sha256"] != inp["source_sha256"]["docs/design-engine/v07-prototype-bundle/packet/nominal-prototype-interface.ifc"]
            or manifest["files_sha256"]["evaluation.json.gz"] != inp["source_sha256"]["docs/design-engine/current/evaluation.json.gz"]):
        raise ValueError("Mixed physical or selected-source identities")
    if (powered["installed_mass_complete"] is not False
            or bundle["evaluation"]["mass_account"]["installed_CG_m"] is not None
            or civil["complete_installed_mass_kg_per_car"] is not None):
        raise ValueError("A newer installed account requires a new method")

    parts = selected["vehicle"]["geometry_parts"]
    selected_mass = selected["vehicle"]["mass"]
    if not isclose(fsum(p["mass_kg"] for p in parts), selected_mass["located_material_kg"], abs_tol=1e-6):
        raise ValueError("Selected CAD occurrence mass differs")
    removed = [p for p in parts if p["id"].startswith("station-secondary/")]
    if not isclose(fsum(p["mass_kg"] for p in removed),
                   powered["mass_budget"]["counted_removed_secondary_kg_per_car"], abs_tol=1e-6):
        raise ValueError("Retired component mass differs")
    removed_ids = {p["id"] for p in removed}
    located = [(float(p["mass_kg"]), p["cg_m"]) for p in parts if p["id"] not in removed_ids]
    modelled_geometry_mass = fsum(m for m, _ in located)
    by_system: dict[str, list[float]] = {}
    for part in parts:
        if part["id"] not in removed_ids:
            group = by_system.setdefault(part.get("system", "unspecified"), [])
            group.append(float(part["mass_kg"]))
    box = inp["unplaced_car_centroid_box_m"]
    uncertain = []
    placed_equipment_count = 0
    for row in powered["mass_budget"]["rows"]:
        centres = row["nominal_centres_car_m"]
        lo, hi = row["mass_each_budget_kg"]
        if centres is None:
            uncertain.append(((lo, hi), box))
        else:
            if len(centres) != row["count_per_car"]:
                raise ValueError("Placed powered-equipment count differs")
            placed_equipment_count += len(centres)
            # A component's unknown mass is modelled at its nominal centre.
            for centre in centres:
                uncertain.append(((lo, hi), [[v, v] for v in centre]))
    residual = powered["mass_budget"]["selected_unlocated_account_kg_per_car"]
    uncertain.append(((residual, residual), box))
    tare = _bounds(located, uncertain)
    expected = powered["mass_budget"]["conditional_accounted_tare_arithmetic_kg_per_car"]
    for got, want in zip(tare["mass_kg"], expected):
        if not isclose(got, want, abs_tol=1e-5):
            raise ValueError("Joined tare budget does not reconcile")
    passenger = (selected_mass["accounted_cap_loaded_kg_per_car"]
                 - selected_mass["accounted_tare_kg_per_car"])
    normal = _bounds(located, [*uncertain, ((passenger, passenger), box)])
    crowd_passenger = (selected_mass["accounted_160_control_kg_per_car"]
                       - selected_mass["accounted_tare_kg_per_car"])
    crowd = _bounds(located, [*uncertain, ((crowd_passenger, crowd_passenger), box)])
    if not isclose(normal["mass_kg"][1],
                   bundle["evaluation"]["mass_account"]["normal_accounted_upper_kg_per_car"]
                   - (2400 - (expected[1] - selected_mass["accounted_tare_kg_per_car"])),
                   abs_tol=1e-5):
        raise ValueError("Normal mass and conservative service ceiling differ unexpectedly")
    screen = powered["nominal_geometry_screen"]
    gap = (joined["station"]["nominal_track_centre_to_platform_edge_m"]
           - joined["vehicle"]["car_body_width_m"] / 2)
    if not isclose(gap, joined["station"]["nominal_static_body_to_platform_gap_m"], abs_tol=1e-9):
        raise ValueError("Station edge geometric gap differs")

    result = dict(
        schema="osr-v07-joined-digital-car-result/1",
        joined_physical_candidate_id=joined["physical_candidate_id"],
        evaluation_purpose="digital placement and bounded mass/statics screen",
        selection_id=joined["selection_id"],
        input_id=inp["input_id"],
        producer_sha256=digest(Path(__file__)),
        source_sha256=inp["source_sha256"],
        modelled_parent_candidate_id=selected["candidate_id"],
        powered_vehicle_candidate_id=bundle["candidate"]["candidate_id"],
        powered_vehicle_evaluation_id=bundle["evaluation"]["evaluation_id"],
        civil_candidate_id=civil["physical_candidate_id"],
        civil_evaluation_id=civil["evaluation_id"],
        ifc_reference=dict(path="docs/design-engine/v07-prototype-bundle/packet/nominal-prototype-interface.ifc",
                           sha256=bundle["evaluation"]["native_ifc"]["sha256"],
                           nominal_interface_box_count=bundle["evaluation"]["native_ifc"]["part_count"]),
        component_handoff=dict(
            inherited_modelled_geometry=[dict(system=system, occurrences=len(masses),
                                             located_mass_kg=fsum(masses))
                                         for system, masses in sorted(by_system.items())],
            retired_passive_secondary=dict(occurrences=len(removed),
                                           mass_kg=fsum(p["mass_kg"] for p in removed)),
            powered_equipment=[dict(id=row["id"], count_per_car=row["count_per_car"],
                                    mass_each_budget_kg=row["mass_each_budget_kg"],
                                    nominal_centres_car_m=row["nominal_centres_car_m"])
                               for row in powered["mass_budget"]["rows"]]),
        method=dict(geometry_occurrences_inherited=len(parts),
                    removed_passive_occurrences=len(removed),
                    modelled_retained_geometry_kg=modelled_geometry_mass,
                    nominal_placed_powered_occurrences=placed_equipment_count,
                    existing_account_without_CAD_placement_kg=residual,
                    passenger_mass_without_CAD_placement_kg=passenger,
                    crowd_passenger_mass_without_CAD_placement_kg=crowd_passenger,
                    assumed_centroid_box_car_xyz_m=box,
                    bogie_centres_car_x_m=[-6.4, 6.4],
                    axle_split="equal half per bogie; static analytical assumption",
                    interval_method="enumerate independent budget endpoints and centroid-box corners"),
        tare_analytical=tare, normal_analytical=normal,
        crowd_160_structural_control=crowd,
        conservative_normal_service_ceiling_kg_per_car=bundle["evaluation"]["mass_account"]["normal_accounted_upper_kg_per_car"],
        conservative_crowd_structural_ceiling_kg_per_car=bundle["evaluation"]["mass_account"]["crowd_160_accounted_upper_kg_per_car"],
        nominal_clearances_m=dict(motor_side_after_50mm_reservation=screen["motor_swept_lateral_clearance_each_side_m"],
                                  motor_top_to_floor_after_50mm_reservation=screen["motor_swept_top_to_floor_underside_m"],
                                  straight_static_body_to_platform_edge=gap,
                                  brake_stowed_bottom_above_rail=powered["physical_definition"]["track_brake_module"]["stowed_pair_box_bottom_m"],
                                  proposed_collector_top_above_rail=powered["physical_definition"]["roof_collector"]["proposed_deployed_top_above_rail_m"]),
        dynamic_max_axle_reaction_N=None,
        complete_installed_mass_kg_per_car=None,
        complete_installed_CG_car_xyz_m=None,
        full_bogie_sweep_or_platform_gap_verified=False,
        native_joined_FEA_executed=False,
        physical_accepted=False,
        fabrication_release=False,
    )
    result["evaluation_id"] = identity(result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "check"))
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    raw = encoded(build())
    if args.action == "build":
        if args.output.exists():
            raise ValueError("Fresh output path required")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(raw)
    elif args.output.read_bytes() != raw:
        raise ValueError("Joined digital-car result differs from current inputs")
    d = json.loads(raw)
    print(json.dumps({k: d[k] for k in ("joined_physical_candidate_id", "evaluation_id",
                                          "physical_accepted")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
