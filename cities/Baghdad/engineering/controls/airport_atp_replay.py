"""Run an offline interlocking and ATP sensitivity using the Airport GIS study."""

import argparse
from hashlib import sha256
import json
from math import ceil, floor
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from cities.Baghdad.engineering.simulation import airport_alignment, scenario, site_layers, site_profile, vehicle_audit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SITE = HERE.parent / "simulation" / "site-study.json"
EXAMPLE = ROOT / "crates/osr-atp/examples/airport_protection_replay.rs"
OUTPUT = HERE / "airport-atp-replay.json"


def encode(record):
    return (json.dumps(record, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def match_study(site):
    settings = site["settings"]
    horizontal = airport_alignment.evaluate()
    layers = site_layers.load_site_layers(alignment=horizontal)
    profile = site_profile.derive_site_profile(
        layers, horizontal, soffit_clearance_m=settings["soffit_clearance_m"],
        max_grade_pct=settings["max_grade_pct"], platform_length_m=settings["platform_length_m"],
        rail_to_soffit_m=settings["rail_to_soffit_m"],
    )
    build = ROOT / "build"
    build.mkdir(exist_ok=True)
    with TemporaryDirectory(prefix="airport-protection-", dir=build) as directory:
        geometry = Path(directory) / "desk-study-centreline.json"
        geometry.write_bytes(scenario.encode(profile["alignment_input"]))
        alignment = airport_alignment.evaluate(survey=geometry)
    route_grade = max(abs(grade) for grade in alignment["grade_profile"]["grades_pct"])
    vehicle = vehicle_audit.evaluate(alignment=alignment, grade_pct=route_grade)
    selection = site["design_screen"]["paired6"]
    if (profile["site_profile_id"] != site["site_profile_id"]
            or alignment["record_id"] != site["alignment_record_id"]
            or alignment["alignment_id"] != site["alignment_id"]
            or alignment["alignment_id"] != selection["assemblies"]["alignment"]
            or vehicle["candidate_id"] != selection["assemblies"]["train"]
            or vehicle["evaluation_id"] != site["vehicle_evaluation_id"]
            or vehicle["mass_cases"]["high"]["loaded_train_kg"] != site["vehicle_loaded_mass_kg"]["high"]):
        raise ValueError("Reconstructed route and vehicle must match the paired six-site GIS study")
    return alignment, vehicle, selection


def replay():
    site_bytes = SITE.read_bytes()
    site = json.loads(site_bytes)
    alignment, vehicle, selection = match_study(site)
    sensitivity = next(case for case in vehicle["braking"]["high"]
                       if case["downgrade_pct"] == 2.0 and case["coast_delay_s"] == 2.0
                       and case["wheel_adhesion_assumed"] == .08 and case["target_net_deceleration_m_s2"] == .6)
    degraded = sensitivity["cases"]["none_wheel_brakes/1_rail_modules_out"]
    comparator = degraded["stop_at_comparator"]
    inputs = dict(
        chainages_mm=[round(km * 1_000_000) for km in alignment["chainages_km"]],
        length_mm=ceil(vehicle["physical"]["length_m"] * 1000),
        loaded_mass_kg=ceil(vehicle["mass_cases"]["high"]["loaded_train_kg"]),
        approach_speed_mmps=ceil(vehicle["inputs"]["speed_kmh"] / 3.6 * 1000),
        after_coast_speed_mmps=ceil(comparator["build_up_entry_speed_m_s"] * 1000),
        coast_distance_mm=ceil(comparator["delay_distance_m"] * 1000),
        net_deceleration_mmps2=floor(comparator["net_deceleration_m_s2"] * 1000),
    )
    command = ["cargo", "run", "--quiet", "--locked", "-p", "osr-atp", "--example", EXAMPLE.stem]
    cases = json.loads(subprocess.check_output(command, cwd=ROOT, input=encode(inputs), timeout=120))
    sources = {**vehicle["source_sha256"], **{
        path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest()
        for path in [SITE, Path(__file__), EXAMPLE, ROOT / "Cargo.lock", ROOT / "Cargo.toml",
                     *(Path(module.__file__) for module in (airport_alignment, scenario, site_layers, site_profile, vehicle_audit)),
                     *(path for crate in ("osr-core", "osr-atp", "osr-interlocking")
                       for path in sorted((ROOT / "crates" / crate / "src").rglob("*.rs")))]
    }}
    result = dict(
        schema="osr-baghdad-airport-atp-replay/1", reference_candidate_id=selection["physical_candidate_id"],
        alignment_id=alignment["alignment_id"], alignment_record_id=alignment["record_id"],
        vehicle_candidate_id=vehicle["candidate_id"], vehicle_evaluation_id=vehicle["evaluation_id"],
        site_evaluation_id=site["evaluation_id"], brake_duty_id=vehicle["duty_id"], source_sha256=sources,
        study_brake=dict(
            loaded_mass_kg=site["vehicle_loaded_mass_kg"]["high"], wheel_brakes_available=False,
            failed_rail_modules=1, rail_module_force_kn=degraded["proposed_comparator_per_module_kn"],
            downgrade_pct=sensitivity["downgrade_pct"], coast_delay_s=sensitivity["coast_delay_s"],
            stopping_distance_m=comparator["stop_distance_m"],
        ),
        rust_inputs=inputs, cases=cases, protection_layout_screen="open", physical_acceptance=False,
        scope="Synthetic lead- and following-train snapshots on the mapped interstation distances. "
              "ATP starts after the separately calculated downhill coast and uses a zero additional delay. "
              "The station boundaries, train positions and uncertainty are fixture inputs. "
              "The 2% comparator is an adverse load sensitivity. The desktop route maximum grade is separate.",
        open_evidence=["Surveyed front-to-protected-limit distances and withheld overlaps",
                       "Qualified brake force, speed, thermal and timing evidence",
                       "Localisation and independent stopping trials with installed controllers",
                       "Resource ownership, directional authority topology and communications validation"],
    )
    result["evaluation_id"] = sha256(encode(result)).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true")
    group.add_argument("--output", type=Path, help="Write evidence to an explicitly selected file")
    options = parser.parse_args()
    result = encode(replay())
    if options.check:
        if result != OUTPUT.read_bytes():
            raise SystemExit("Airport ATP replay differs from the published evidence")
        print(json.loads(result)["evaluation_id"])
    elif options.output:
        options.output.write_bytes(result)
    else:
        print(result.decode(), end="")


if __name__ == "__main__":
    main()
