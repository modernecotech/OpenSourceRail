"""Small native beam FEM for the joined v0.7 digital civil reference.

The model is a gross-elastic box beam with declared simply supported bearing
restraints. It evaluates one exact-event crowd train pose and a one-rail torsion
sensitivity. It does not model reinforcement, prestress transfer, soil or seats.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from math import atan2, ceil, isclose, isfinite
import os
from pathlib import Path
import re
import shutil
import subprocess

from engineering.development_baseline import selection
from engineering.design_search.frame_native import parse_frd_displacements
from engineering.station_rail import civil


ROOT = Path(__file__).resolve().parents[2]
JOINED = Path("docs/reference-v07/integration/candidate.toml")
SPAN = Path("docs/design-engine/v07-simple-span/plan.json")
CAR = Path("docs/reference-v07/digital/vehicle/result.json")
PRODUCER = Path("engineering/design_search/v07_joined_civil_fem.py")
SOURCES = (JOINED, SPAN, CAR, PRODUCER,
           Path("engineering/development-baseline.toml"),
           Path("engineering/development_baseline/selection.py"),
           Path("engineering/design_search/frame_native.py"),
           Path("engineering/station_rail/civil.py"))
SPAN_M = 10.0
NODE_STEP_M = 0.25
E_PA = 35e9  # same gross-elastic modulus as the existing civil screen
NU = 0.2  # declared isotropic torsion sensitivity assumption
RAIL_OFFSET_M = 1.435 / 2
G = 9.80665


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _identity(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode()).hexdigest()


def _load(root: Path) -> tuple[dict, dict, dict, dict, dict]:
    import tomllib
    joined = tomllib.loads((root / JOINED).read_text())
    span = json.loads((root / SPAN).read_text())
    car = json.loads((root / CAR).read_text())
    if (joined["physical_candidate_id"] != "osr-v07-joined-prototype-20261117"
            or joined["ancestry"]["joint_free_span_physical_candidate_id"] != span["physical_candidate_id"]
            or joined["civil"]["beam_length_m"] != SPAN_M
            or joined["civil"]["beam_width_m"] != 2.0
            or joined["civil"]["beam_depth_m"] != 1.4
            or joined["civil"]["bearing_units_per_beam"] != 4
            or joined["corridor"]["track_count"] != 2
            or car["joined_physical_candidate_id"] != joined["physical_candidate_id"]
            or car["civil_candidate_id"] != span["physical_candidate_id"]
            or not isclose(joined["vehicle"]["crowd_analytical_t_per_car"] * 1000,
                           span["crowd_control_accounted_mass_kg_per_car"], abs_tol=0.01)):
        raise ValueError("Joined candidate and beam/load ancestry differ")
    if not isclose(span["crowd_control_load"]["maximum_live_moment_Nm"],
                   585622.4572713629, rel_tol=1e-10):
        raise ValueError("Crowd moving-load control differs")
    selected = selection.load(root)["vehicle"]
    vehicle = selected["physical_definition"]["vehicle"]
    bogie = selected["physical_definition"]["support"]
    if (vehicle["cars"], vehicle["body_length_m"], vehicle["coupling_gap_m"],
            bogie["bogie_centres_x_m"], bogie["bogie_wheelbase_m"]) != (6, 17.0, 0.5, [-6.4, 6.4], 2.1):
        raise ValueError("Selected load geometry differs from joined reference")
    return joined, span, car, vehicle, bogie


def _critical_axles(span: dict, vehicle: dict, bogie: dict) -> tuple[list[float], float, float]:
    offsets = [car * (vehicle["body_length_m"] + vehicle["coupling_gap_m"])
               + vehicle["body_length_m"] / 2 + center + delta
               for car in range(vehicle["cars"])
               for center in bogie["bogie_centres_x_m"]
               for delta in (-bogie["bogie_wheelbase_m"] / 2, bogie["bogie_wheelbase_m"] / 2)]
    axle_n = span["crowd_control_accounted_mass_kg_per_car"] * G / 4 * 1.3
    envelope = civil.moving_envelope(SPAN_M, offsets, axle_n)
    peak = max(envelope, key=lambda row: row["max_live_moment_Nm"])
    if not isclose(peak["max_live_moment_Nm"],
                   span["crowd_control_load"]["maximum_live_moment_Nm"], rel_tol=1e-10):
        raise ValueError("Exact-event moving-load pose does not reproduce source packet")
    positions = [x + peak["critical_train_translation_m"] for x in offsets]
    positions = [x for x in positions if -1e-9 <= x <= SPAN_M + 1e-9]
    return positions, axle_n, peak["critical_train_translation_m"]


def _cg_bound_axles(car: dict, vehicle: dict, bogie: dict) -> tuple[list[tuple[float, float]], dict]:
    """Maximise section moment over exact events and consistent bogie orientations.

    Each car carries the upper digital mass and one high/one complementary low
    bogie. The high reaction and upper mass are combined conservatively, even
    though their original interval endpoints need not occur simultaneously.
    """
    interval = car["crowd_160_structural_control"]
    upper_mass = interval["mass_kg"][1] + car["sizing_load_handoff"]["additional_round_up_above_budget_upper_kg_per_car"]
    high_bogie = max(interval["bogie_reaction_interval_N"][side][1]
                     for side in ("left_bogie_N", "right_bogie_N"))
    low_bogie = upper_mass * G - high_bogie
    if low_bogie <= 0:
        raise ValueError("CG-bound lower bogie reaction must remain positive")
    high, low = high_bogie * 1.3 / 2, low_bogie * 1.3 / 2
    offsets = [[index * (vehicle["body_length_m"] + vehicle["coupling_gap_m"])
                + vehicle["body_length_m"] / 2 + center + delta
                for center in bogie["bogie_centres_x_m"]
                for delta in (-bogie["bogie_wheelbase_m"] / 2, bogie["bogie_wheelbase_m"] / 2)]
               for index in range(vehicle["cars"])]
    flat = [p for car_offsets in offsets for p in car_offsets]
    best = (-1.0, 0.0, 0.0, [])
    envelope = []
    for section_index in range(int(SPAN_M / NODE_STEP_M) + 1):
        x = section_index * NODE_STEP_M
        local_best = (-1.0, 0.0, [])
        translations = {point - p for p in flat for point in (0.0, x, SPAN_M)}
        for translation in translations:
            total, orientation = 0.0, []
            for group in offsets:
                factors = []
                for p0 in group:
                    p = p0 + translation
                    factors.append(0.0 if not 0 <= p <= SPAN_M else
                                   (SPAN_M - p) / SPAN_M * x - max(x - p, 0.0))
                left_high = high * sum(factors[:2]) + low * sum(factors[2:])
                right_high = low * sum(factors[:2]) + high * sum(factors[2:])
                choose_left = left_high >= right_high
                total += max(left_high, right_high)
                orientation.append("left" if choose_left else "right")
            if total > local_best[0]:
                local_best = (total, translation, orientation)
        envelope.append({"section_m": x, "max_live_moment_Nm": local_best[0]})
        if local_best[0] > best[0]:
            best = (local_best[0], x, local_best[1], local_best[2])
    moment, section, translation, orientation = best
    loads = []
    for group, high_side in zip(offsets, orientation):
        for axle_index, p0 in enumerate(group):
            p = p0 + translation
            if 0 <= p <= SPAN_M:
                axle_high = (axle_index < 2) == (high_side == "left")
                loads.append((p, high if axle_high else low))
    return loads, {
        "maximum_live_moment_Nm": moment, "critical_section_m": section,
        "train_translation_m": translation, "high_bogie_orientation_per_car": orientation,
        "high_static_axle_N": high / 1.3, "low_static_axle_N": low / 1.3,
        "dynamic_factor_hypothesis": 1.3,
        "per_car_mass_kg_conservative": upper_mass,
        "interval_endpoints_combined_conservatively": True,
        "weighted_moving_moment_envelope": envelope,
    }


def _revised_prestress(span: dict, cg_meta: dict) -> dict:
    """Smallest changed-strand child satisfying declared gross longitudinal screens."""
    original = span["crowd_control_load"]
    base_n = original["prestress_strands"]
    strand_area_m2, fpk_pa = 0.00014, 1860e6
    kg_per_strand = strand_area_m2 * SPAN_M * 7850 + 2 * 4.5
    p_initial_per_strand = strand_area_m2 * fpk_pa * 0.7
    p_effective_per_strand = p_initial_per_strand * 0.8
    box = civil.section("box-beam")
    area, inertia, c = box["area_m2"], box["I_m4"], box["c_top_m"]
    original_screens = None
    for strands in range(base_n, 33):
        mass = original["accounted_span_stock_mass_kg"] + (strands - base_n) * kg_per_strand
        q = mass * G / SPAN_M
        p0 = strands * p_initial_per_strand
        pe = strands * p_effective_per_strand
        service_tension, service_compression = -1e100, 0.0
        release_tension, release_compression = -1e100, 0.0
        for row in cg_meta["weighted_moving_moment_envelope"]:
            x = row["section_m"]
            dead = q * x * (SPAN_M - x) / 2
            eccentricity = 0.42 * 4 * x * (SPAN_M - x) / SPAN_M**2
            for moment in (dead, dead + row["max_live_moment_Nm"]):
                values = (-pe / area - pe * eccentricity * c / inertia + moment * c / inertia,
                          -pe / area + pe * eccentricity * c / inertia - moment * c / inertia)
                service_tension = max(service_tension, *values)
                service_compression = max(service_compression, *(-v for v in values))
            values = (-p0 / area - p0 * eccentricity * c / inertia + dead * c / inertia,
                      -p0 / area + p0 * eccentricity * c / inertia - dead * c / inertia)
            release_tension = max(release_tension, *values)
            release_compression = max(release_compression, *(-v for v in values))
        screens = {"service_tension_N_per_m2": service_tension,
                   "service_compression_N_per_m2": service_compression,
                   "release_tension_N_per_m2": release_tension,
                   "release_compression_N_per_m2": release_compression}
        if strands == base_n:
            original_screens = screens
        if (service_tension <= 0 and service_compression <= 0.45 * 50e6
                and release_tension <= 1e6 and release_compression <= 0.45 * 40e6):
            changed = strands != base_n
            beam_id = _identity({"parent": span["beam_component_id"], "strand_count": strands,
                                 "section": box, "prestress_eccentricity_max_m": 0.42})
            return {"parent_beam_component_id": span["beam_component_id"],
                    "revised_beam_component_id": beam_id,
                    "parent_joined_physical_candidate_id": "osr-v07-joined-prototype-20261117",
                    "revised_joined_physical_candidate_id": "osr-v07-joined-civil-" + _identity({
                        "parent": "osr-v07-joined-prototype-20261117", "beam_component_id": beam_id})[:24],
                    "physical_revision_required": changed,
                    "original_strands": base_n, "revised_strands": strands,
                    "revised_effective_prestress_N_hypothesis": pe,
                    "revised_initial_prestress_N_hypothesis": p0,
                    "additional_counted_steel_kg_per_beam": (strands - base_n) * kg_per_strand,
                    "additional_counted_steel_t_for_400_beams": (strands - base_n) * kg_per_strand * 0.4,
                    "additional_counted_steel_t_for_6000_beams": (strands - base_n) * kg_per_strand * 6,
                    "revised_counted_dead_mass_kg_per_beam": mass,
                    "revised_bare_beam_mass_t_hypothesis": (span["handling"]["one_piece_bare_kg_accounted"] + (strands - base_n) * kg_per_strand) / 1000,
                    "revised_hook_load_t_with_25pct_allowance": (span["handling"]["one_piece_bare_kg_accounted"] + (strands - base_n) * kg_per_strand) * 1.25 / 1000,
                    "original_gross_longitudinal_screens": original_screens,
                    "gross_longitudinal_screens": screens,
                    "screen_limits_Pa": {"service_tension": 0, "service_compression": 22.5e6,
                                         "release_tension": 1e6, "release_compression": 18e6},
                    "screen_is_structural_approval": False}
    raise ValueError("No bounded prestress revision satisfies gross longitudinal screens")


def _nodal_loads(axles: list[tuple[float, float]], dead_mass_kg: float,
                 one_rail: bool) -> tuple[list[float], list[float]]:
    count = int(SPAN_M / NODE_STEP_M) + 1
    downward = [dead_mass_kg * G / SPAN_M * NODE_STEP_M] * count
    downward[0] *= 0.5
    downward[-1] *= 0.5
    torsion = [0.0] * count
    for x, axle_n in axles:
        coordinate = min(max(x, 0.0), SPAN_M) / NODE_STEP_M
        left = min(int(coordinate), count - 2)
        right_fraction = coordinate - left
        for node, fraction in ((left, 1 - right_fraction), (left + 1, right_fraction)):
            downward[node] += axle_n * fraction
            if one_rail:
                torsion[node] += axle_n * RAIL_OFFSET_M * fraction
    if not isclose(sum(downward), dead_mass_kg * G + sum(force for _, force in axles), rel_tol=1e-12):
        raise ValueError("Nodal vertical force does not balance")
    return downward, torsion


def _deck(downward: list[float], torsion: list[float], title: str) -> str:
    n = len(downward)
    lines = ["*HEADING", title, "*NODE"]
    lines += [f"{i+1},{i*NODE_STEP_M:.9g},0,0" for i in range(n)]
    lines.append("*ELEMENT,TYPE=B32R,ELSET=BEAM")
    lines += [f"{k+1},{2*k+1},{2*k+2},{2*k+3}" for k in range((n-1)//2)]
    lines += ["*MATERIAL,NAME=CONCRETE", "*ELASTIC", f"{E_PA:.9g},{NU:.9g}",
              "*BEAM SECTION,ELSET=BEAM,MATERIAL=CONCRETE,SECTION=BOX",
              "2,1.4,0.18,0.18,0.18,0.18", "0,1,0",
              "*NSET,NSET=SUPPORTS", f"1,{n}", "*NSET,NSET=MID", str((n+1)//2),
              "*BOUNDARY", "1,1,3", f"{n},2,3", "1,4,4", f"{n},4,4",
              "*STEP", "*STATIC", "*CLOAD"]
    lines += [f"{i+1},3,{-force:.12g}" for i, force in enumerate(downward) if force]
    lines += [f"{i+1},4,{moment:.12g}" for i, moment in enumerate(torsion) if moment]
    lines += ["*NODE PRINT,NSET=SUPPORTS", "RF", "*NODE PRINT,NSET=MID", "U",
              "*NODE FILE,OUTPUT=3D", "U", "*END STEP", ""]
    return "\n".join(lines)


def _parse_dat(path: Path, right: int, middle: int) -> dict:
    text = path.read_text()
    if path.stat().st_size > 2 * 1024 * 1024:
        raise ValueError("Native DAT output exceeded resource limit")
    rows = {}
    active = None
    for line in text.splitlines():
        if "forces (fx,fy,fz)" in line.lower():
            active = "force"
        elif "displacements (vx,vy,vz)" in line.lower():
            active = "displacement"
        match = re.match(r"^\s*(\d+)\s+([+-]?\d[\deE+.-]*)\s+([+-]?\d[\deE+.-]*)\s+([+-]?\d[\deE+.-]*)\s*$", line)
        if match and active:
            rows[(active, int(match.group(1)))] = [float(match.group(i)) for i in range(2, 5)]
    if not all(key in rows for key in (("force", 1), ("force", right), ("displacement", middle))):
        raise ValueError("Missing native reactions or midspan displacement")
    return {"left_reaction_N": rows[("force", 1)],
            "right_reaction_N": rows[("force", right)],
            "midspan_displacement_m": rows[("displacement", middle)]}


def _midspan_twist(frd: Path) -> dict:
    coordinates, displacements = parse_frd_displacements(frd)
    corners = {}
    for node, (x, y, z) in coordinates.items():
        if (abs(x - 5.0) < 1e-8 and abs(z - 0.7) < 1e-8
                and abs(abs(y) - 1.0) < 1e-8 and node in displacements):
            corners[str(round(y))] = displacements[node][2]
    if set(corners) != {"-1", "1"}:
        raise ValueError("Native expanded midspan section corners unavailable")
    relative = corners["1"] - corners["-1"]
    angle = atan2(relative, 2.0)
    return {"expanded_midspan_top_corner_uz_m": corners,
            "midspan_twist_rad": angle,
            "rail_to_rail_vertical_difference_m": angle * 1.435}


def build(output: Path, root: Path = ROOT, solver: str = "ccx") -> dict:
    root = Path(root)
    output = Path(output)
    joined, span, car, vehicle, bogie = _load(root)
    positions, axle_n, pose = _critical_axles(span, vehicle, bogie)
    cg_loads, cg_meta = _cg_bound_axles(car, vehicle, bogie)
    revision = _revised_prestress(span, cg_meta)
    solver_path = shutil.which(solver)
    if not solver_path:
        raise FileNotFoundError("CalculiX ccx executable unavailable")
    if output.exists() and any(output.iterdir()):
        raise ValueError("Fresh output directory required")
    output.mkdir(parents=True, exist_ok=True)
    source_sha = {str(path): _hash(root / path) for path in SOURCES}
    input_record = {
        "schema": "osr-v07-joined-civil-native-input/1",
        "physical_candidate_id": joined["physical_candidate_id"],
        "parent_civil_candidate_id": span["physical_candidate_id"],
        "current_civil_evaluation_id": span["evaluation_id"],
        "ancestral_civil_evaluation_id": joined["ancestry"]["joint_free_span_evaluation_id"],
        "beam_component_id": span["beam_component_id"],
        "load_case": "160-person-per-car crowd structural control",
        "span_m": SPAN_M, "node_step_m": NODE_STEP_M,
        "section": civil.section("box-beam"), "gross_elastic_E_Pa": E_PA,
        "isotropic_nu_hypothesis": NU, "rail_offset_m": RAIL_OFFSET_M,
        "axle_positions_on_span_m": positions, "axle_force_N_factored": axle_n,
        "train_translation_m": pose,
        "cg_bound_axle_loads_position_m_force_N": [list(pair) for pair in cg_loads],
        "cg_bound_definition": cg_meta,
        "civil_revision_option": revision,
        "dead_mass_kg_spread": span["crowd_control_load"]["accounted_span_stock_mass_kg"],
        "bearing_boundary": "left xyz fixed, right yz fixed, end torsion fixed; bending rotations free",
        "source_sha256": source_sha,
        "ccx_executable_sha256": _hash(Path(solver_path)),
    }
    input_record["evaluation_id"] = _identity(input_record)
    (output / "input.json").write_text(json.dumps(input_record, indent=2, sort_keys=True) + "\n")
    cases = {}
    for name, axles, one_rail, revised in (
            ("equal-share", [(p, axle_n) for p in positions], False, False),
            ("cg-bound-original", cg_loads, False, False),
            ("cg-bound-revised", cg_loads, False, True),
            ("cg-bound-revised-one-rail", cg_loads, True, True)):
        dead_mass = (revision["revised_counted_dead_mass_kg_per_beam"] if revised else
                     input_record["dead_mass_kg_spread"])
        forces, moments = _nodal_loads(axles, dead_mass, one_rail)
        (output / f"{name}.inp").write_text(_deck(forces, moments, name))
        env = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"}
        execution = subprocess.run([solver_path, "-i", name], cwd=output, env=env,
                                   text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   timeout=90, check=False)
        (output / f"{name}.log").write_text(execution.stdout)
        if execution.returncode != 0 or not (output / f"{name}.dat").exists():
            raise RuntimeError(f"Native {name} solve failed; see {name}.log")
        response = _parse_dat(output / f"{name}.dat", len(forces), (len(forces)+1)//2)
        response.update(_midspan_twist(output / f"{name}.frd"))
        # CalculiX RF omits the externally applied load at a constrained node.
        # The support seats carry those two dead-load tributaries directly.
        left_total = response["left_reaction_N"][2] + forces[0]
        right_total = response["right_reaction_N"][2] + forces[-1]
        residual = abs(left_total + right_total - sum(forces)) / sum(forces)
        if not isfinite(residual) or residual > 1e-6:
            raise ValueError(f"Native {name} vertical force residual {residual:g}")
        cases[name] = {"physical_candidate_id": revision["revised_joined_physical_candidate_id"] if revised else joined["physical_candidate_id"],
                       "beam_component_id": revision["revised_beam_component_id"] if revised else span["beam_component_id"],
                       "applied_downward_N": sum(forces),
                       "applied_torsion_Nm": sum(moments), **response,
                       "left_total_support_vertical_N": left_total,
                       "right_total_support_vertical_N": right_total,
                       "vertical_force_relative_residual": residual,
                       "solver_exit_code": execution.returncode}
        for suffix in ("12d", "cvg", "sta"):
            (output / f"{name}.{suffix}").unlink(missing_ok=True)
    (output / "spooles.out").unlink(missing_ok=True)
    result = {
        "schema": "osr-v07-joined-civil-native-result/1",
        "input_evaluation_id": input_record["evaluation_id"],
        "physical_candidate_id": joined["physical_candidate_id"],
        "beam_component_id": span["beam_component_id"],
        "digital_civil_revision_option": revision,
        "cases": cases,
        "source_analytical_crowd_max_live_moment_Nm": span["crowd_control_load"]["maximum_live_moment_Nm"],
        "source_analytical_crowd_deflection_envelope_m": span["crowd_control_load"]["gross_elastic_deflection_envelope_m"],
        "quantity_context": {
            "two_track_2km_beams_and_lifts": joined["demonstrator"]["beam_lifts"],
            "two_track_2km_independent_supports": joined["demonstrator"]["independent_support_positions"],
            "two_track_2km_bearings_hypothesis": joined["demonstrator"]["provisional_bearings"],
            "two_track_30km_beams_and_lifts": int(joined["corridor"]["route_km"] * 1000 / SPAN_M) * joined["corridor"]["track_count"],
            "two_track_30km_continuous_supports": int(joined["corridor"]["route_km"] * 1000 / SPAN_M + 1) * joined["corridor"]["track_count"],
            "bare_beam_mass_t": joined["civil"]["bare_beam_mass_t"],
            "hook_load_t_hypothesis": joined["civil"]["provisional_hook_load_t"],
            "one_beam_per_trip_2km_hypothesis": joined["demonstrator"]["beam_lifts"],
            "provisional_crane_chart_t_at_12m": span["handling"]["provisional_crane_chart_kg_at_12m"] / 1000,
            "factory_days_at_four_beams_per_day_2km": ceil(joined["demonstrator"]["beam_lifts"] / 4),
            "lift_days_at_eight_per_day_2km": ceil(joined["demonstrator"]["beam_lifts"] / 8),
        },
        "scope": "gross-elastic 1D native FEM at exact-event crowd pose, with all counted beam/rail stock spread as gravity",
        "does_not_model": ["prestress and transfer", "reinforcement, crack and fatigue law",
                           "local rail seat, diaphragm and bearing stress", "bearing stiffness and ground",
                           "lateral/braking dynamic combinations", "handling and erection stability"],
        "site_or_physical_accepted": False,
    }
    result["artifact_sha256"] = {p.name: _hash(p) for p in sorted(output.iterdir()) if p.is_file()}
    result["evaluation_id"] = _identity(result)
    (output / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def check(output: Path, root: Path = ROOT) -> dict:
    output, root = Path(output), Path(root)
    inp = json.loads((output / "input.json").read_text())
    result = json.loads((output / "result.json").read_text())
    joined, span, car, vehicle, bogie = _load(root)
    if (inp["physical_candidate_id"] != joined["physical_candidate_id"]
            or inp["current_civil_evaluation_id"] != span["evaluation_id"]
            or inp["axle_positions_on_span_m"] != _critical_axles(span, vehicle, bogie)[0]
            or inp["cg_bound_axle_loads_position_m_force_N"] != [list(pair) for pair in _cg_bound_axles(car, vehicle, bogie)[0]]
            or inp["civil_revision_option"] != _revised_prestress(span, _cg_bound_axles(car, vehicle, bogie)[1])
            or inp["source_sha256"] != {str(path): _hash(root / path) for path in SOURCES}
            or inp["ccx_executable_sha256"] != _hash(Path(shutil.which("ccx")))):
        raise ValueError("Native input is stale or belongs to another candidate")
    expected_input_id = _identity({k: v for k, v in inp.items() if k != "evaluation_id"})
    if inp["evaluation_id"] != expected_input_id:
        raise ValueError("Native input identity differs")
    for name, digest in result["artifact_sha256"].items():
        if _hash(output / name) != digest:
            raise ValueError("Native artifact differs: " + name)
    expected_result_id = _identity({k: v for k, v in result.items() if k != "evaluation_id"})
    if (result["evaluation_id"] != expected_result_id
            or result["input_evaluation_id"] != inp["evaluation_id"]):
        raise ValueError("Native result identity differs")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "check"))
    parser.add_argument("--output", type=Path, default=Path("docs/reference-v07/digital/civil"))
    args = parser.parse_args()
    result = build(args.output) if args.command == "build" else check(args.output)
    print(json.dumps({"physical_candidate_id": result["physical_candidate_id"],
                      "evaluation_id": result["evaluation_id"],
                      "cases": result["cases"]}, indent=2))


if __name__ == "__main__":
    main()
