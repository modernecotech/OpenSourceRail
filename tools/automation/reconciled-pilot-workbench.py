#!/usr/bin/env python3
"""Build a candidate-bound Workbench view from the published closure packet."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path


PILOT = Path("docs/design-engine/reconciled-pilot")
NO_STORE_PILOT = Path("docs/design-engine/reconciled-pilot-no-store")
OUTPUT = Path("docs/workbench/current/reconciled-pilot")
CITY_INDEX = Path("docs/design-engine/city-dossiers/index.json")
CITY_MANIFEST = Path("docs/design-engine/city-dossiers/manifest.json")
RELEASE_FLAGS = ("engineering_accepted", "physical_accepted", "manufacturing_release", "operating_release", "movement_authority")


def read_json(root: Path, relative: Path):
    return json.loads((root / relative).read_text())


def verify_hashes(root: Path, base: Path, hashes: dict[str, str]):
    for relative, expected in hashes.items():
        path = root / base / relative
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Missing or unsafe source-pinned file: {path}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Source pin mismatch: {path}")


def verify_release_holds(*objects):
    for obj in objects:
        for flag in RELEASE_FLAGS:
            if flag in obj and obj[flag] is not False:
                raise ValueError(f"Published packet must retain {flag}=false")


def comparison_case(root: Path, packet: Path) -> dict:
    manifest = read_json(root, packet / "manifest.json")
    run_manifest = read_json(root, packet / "run-manifest.json")
    verify_hashes(root, packet, manifest["files_sha256"])
    verify_hashes(root, Path("."), manifest["source_sha256"])
    summary = read_json(root, packet / "summary.json")
    bundle = read_json(root, packet / "bundle.json")
    with gzip.open(root / packet / "study.json.gz", "rt", encoding="utf-8") as stream:
        study = json.load(stream)
    for obj in (manifest, run_manifest, summary, bundle, study):
        verify_release_holds(obj)
    if not (manifest["study_id"] == run_manifest["study_id"] == study["study_id"] == summary["study_id"]):
        raise ValueError("Comparison packet study identities differ")
    if summary["bundle"] != bundle or study["bundle"] != bundle:
        raise ValueError("Comparison packet summary/study bundle differs")
    candidate = bundle["candidate_id"]
    if candidate == "" or not candidate:
        raise ValueError("Comparison packet candidate identity is missing")
    rows = [row for row in summary["rows"] if row["experiment"] == "nominal"
            and row["headway_s"] == 200 and row["opposite_phase_s"] == 90]
    if len(rows) != 1:
        raise ValueError("Comparison needs one matching nominal 200 s / 90 s source case")
    row = rows[0]
    plan = next((value for value in study["service_plans"] if value["evaluation_id"] == row["service_id"]), None)
    if not plan or plan.get("candidate_id") != candidate:
        raise ValueError("Comparison journey is not bound to comparison candidate")
    record = next((value for value in study["records"]
                   if value.get("service", {}).get("evaluation_id") == row["service_id"]
                   and value.get("experiment") == "nominal"), None)
    if not record or record.get("cost", {}).get("canonical_bundle") != bundle:
        raise ValueError("Comparison cost record is not bound to comparison candidate")
    if row.get("cost_evaluation_id") is None or len(row["cost_evaluation_id"]) != 64:
        raise ValueError("Comparison cost evaluation identity is missing")
    return {"packet": str(packet), "manifest_id": manifest["manifest_id"], "study_id": study["study_id"],
            "physical_candidate_id": candidate, "bundle_evaluation_id": bundle["evaluation_id"],
            "pinned_payload_sha256": {"manifest.json": hashlib.sha256((root / packet / "manifest.json").read_bytes()).hexdigest(),
                                       **{name: manifest["files_sha256"][name] for name in
                                          ("summary.json", "bundle.json", "study.json.gz")}},
            "producer_source_sha256": manifest["source_sha256"],
            "route_km": summary["route_km"], "stations": summary["stations"],
            "case": {"service_evaluation_id": row["service_id"], "cost_evaluation_id": row["cost_evaluation_id"],
                     "headway_s": row["headway_s"], "opposite_phase_s": row["opposite_phase_s"],
                     "arrivals": row["arrivals"], "requested": row["requested"],
                     "grid_traction_kwh": row["grid_traction_kwh"], "capture_kwh": row["capture_kwh"],
                     "relaunch_kwh": row["relaunch_kwh"], "installed_capital_usd": row["cost"]["installed_capital_usd"],
                     "known_lifecycle_subtotal_usd": row["cost"]["known_lifecycle_subtotal_usd"],
                     "whole_life_NPV_usd": row["cost"]["whole_life_NPV_usd"]},
            "recovery_store_present": packet != NO_STORE_PILOT,
            "release_flags": {flag: False for flag in RELEASE_FLAGS},
            "source_links": [{"label": "Packet dossier", "href": "/" + str(packet / "README.md"),
                              "sha256": manifest["files_sha256"]["README.md"]},
                             {"label": "Source manifest", "href": "/" + str(packet / "manifest.json"),
                              "sha256": hashlib.sha256((root / packet / "manifest.json").read_bytes()).hexdigest()},
                             {"label": "Complete study", "href": "/" + str(packet / "study.json.gz"),
                              "sha256": manifest["files_sha256"]["study.json.gz"]}]}


def build(root: Path) -> dict:
    pilot = root / PILOT
    manifest = read_json(root, PILOT / "manifest.json")
    run_manifest = read_json(root, PILOT / "run-manifest.json")
    verify_hashes(root, PILOT, manifest["files_sha256"])
    # Both manifests pin producer inputs, in addition to pinning dossier payloads.
    verify_hashes(root, Path("."), manifest["source_sha256"])

    summary = read_json(root, PILOT / "summary.json")
    bundle = read_json(root, PILOT / "bundle.json")
    vehicle = read_json(root, PILOT / "vehicle/manifest.json")
    delivery = read_json(root, PILOT / "delivery/manifest.json")
    requirements = read_json(root, PILOT / "requirements.json")
    frontier = read_json(root, PILOT / "frontier.json")
    with gzip.open(pilot / "study.json.gz", "rt", encoding="utf-8") as stream:
        study = json.load(stream)

    for obj in (manifest, run_manifest, summary, bundle, vehicle, delivery, requirements, frontier, study):
        verify_release_holds(obj)
    study_id = summary["study_id"]
    candidate_id = bundle["candidate_id"]
    evaluation_id = bundle["evaluation_id"]
    if not (manifest["study_id"] == run_manifest["study_id"] == study["study_id"] == study_id):
        raise ValueError("Study identity differs between published sources")
    if summary["bundle"] != bundle or study["bundle"] != bundle:
        raise ValueError("Summary and source study do not use the published physical bundle")
    if requirements.get("candidate_id") != candidate_id or frontier.get("source_candidate_id") != candidate_id:
        raise ValueError("Requirements or frontier are not bound to the physical bundle")
    if vehicle["candidate_id"] != bundle["physical_definition"]["body_candidate_id"]:
        raise ValueError("Vehicle installation candidate differs from bundle body identity")
    if vehicle["evaluation_id"] != bundle["body_evaluation_id"]:
        raise ValueError("Vehicle installation evaluation differs from bundle body evaluation")
    if vehicle.get("files_sha256", {}).get("bom.csv") != hashlib.sha256((pilot / "vehicle/bom.csv").read_bytes()).hexdigest():
        raise ValueError("Manufacturing BOM is not the one pinned by its vehicle manifest")

    plans = {row["evaluation_id"]: row for row in study["service_plans"]}
    for record in study["records"]:
        canonical = record.get("cost", {}).get("canonical_bundle", {})
        if canonical != bundle or record.get("service", {}).get("candidate_id") != candidate_id:
            raise ValueError("Published journey or cost record mixes physical bundle identities")
    rows = []
    for row in summary["rows"]:
        plan = plans.get(row["service_id"])
        if plan is None or plan.get("candidate_id") != candidate_id:
            raise ValueError("Journey result is not bound to the reconciled bundle candidate")
        if (plan.get("headway_s"), plan.get("opposite_phase_s")) != (row["headway_s"], row["opposite_phase_s"]):
            raise ValueError("Journey identity does not match summary schedule")
        if not isinstance(row.get("cost_evaluation_id"), str) or len(row["cost_evaluation_id"]) != 64:
            raise ValueError("Cost evaluation identity is missing or malformed")
        rows.append({"candidate_id": candidate_id, **{key: row[key] for key in (
            "experiment", "headway_s", "opposite_phase_s", "active_trainsets", "spare_trainsets",
            "arrivals", "requested", "maximum_journey_s", "maximum_moving_jerk_m_s3",
            "planning_capacity_pphpd", "model_screen", "grid_traction_kwh", "capture_kwh", "relaunch_kwh",
            "service_id", "fleet_evaluation_id",
            "cost_evaluation_id", "cost")}})

    city_manifest = read_json(root, CITY_MANIFEST)
    verify_release_holds(city_manifest)
    if "docs/design-engine/city-dossiers/index.json" not in city_manifest["files_sha256"]:
        raise ValueError("City atlas index is not pinned by its publication manifest")
    verify_hashes(root, Path("."), {"docs/design-engine/city-dossiers/index.json":
                                     city_manifest["files_sha256"]["docs/design-engine/city-dossiers/index.json"]})
    city_index = read_json(root, CITY_INDEX)
    baghdad = next((row for row in city_index["cities"] if row["city"]["slug"] == "baghdad"), None)
    if baghdad is None:
        raise ValueError("Published Baghdad city brief is unavailable")
    if baghdad["path"] + "/README.md" not in city_manifest["files_sha256"]:
        raise ValueError("Baghdad brief is not pinned by the city dossier manifest")
    verify_hashes(root, Path("."), {baghdad["path"] + "/README.md":
                                      city_manifest["files_sha256"][baghdad["path"] + "/README.md"]})

    assets = manifest["files_sha256"]
    links = [
        {"label": "Published packet manifest", "href": "/docs/design-engine/reconciled-pilot/manifest.json", "sha256": hashlib.sha256((pilot / "manifest.json").read_bytes()).hexdigest()},
        {"label": "Published calculated summary", "href": "/docs/design-engine/reconciled-pilot/summary.json", "sha256": assets["summary.json"]},
        {"label": "Complete calculated study", "href": "/docs/design-engine/reconciled-pilot/study.json.gz", "sha256": assets["study.json.gz"]},
        {"label": "Counted vehicle BOM", "href": "/docs/design-engine/reconciled-pilot/vehicle/bom.csv", "sha256": vehicle["files_sha256"]["bom.csv"]},
        {"label": "Installed vehicle assembly (GLB)", "href": "/docs/design-engine/reconciled-pilot/vehicle/assembly.glb", "sha256": vehicle["files_sha256"]["assembly.glb"]},
        {"label": "Civil assembly drawing", "href": "/docs/design-engine/reconciled-pilot/civil-assembly.svg", "sha256": assets["civil-assembly.svg"]},
        {"label": "Verified stock STEP model", "href": "/docs/design-engine/reconciled-pilot/native-cad/solidcraft/assembly.step", "sha256": assets["native-cad/solidcraft/assembly.step"]},
        {"label": "Manufacturing and delivery review draft", "href": "/docs/design-engine/reconciled-pilot/delivery/README.md", "sha256": assets["delivery/README.md"]},
        {"label": "Unresolved engineering tasks", "href": "/docs/design-engine/reconciled-pilot/frontier.json", "sha256": assets["frontier.json"]},
        {"label": "Assumptions and requirement status", "href": "/docs/design-engine/reconciled-pilot/requirements.json", "sha256": assets["requirements.json"]},
    ]
    if vehicle.get("files_sha256", {}).get("assembly.glb") != assets.get("vehicle/assembly.glb"):
        raise ValueError("Vehicle gallery asset is not consistently pinned")
    no_store = comparison_case(root, NO_STORE_PILOT)
    if no_store["physical_candidate_id"] == candidate_id:
        raise ValueError("The no-store control must remain a distinct physical candidate")
    current_nominal = comparison_case(root, PILOT)
    return {
        "schema": "osr-reconciled-pilot-workbench/1",
        "source": {"manifest": str(PILOT / "manifest.json"), "manifest_id": manifest["manifest_id"],
                   "run_manifest_id": run_manifest["manifest_id"], "study_id": study_id,
                   "pinned_payload_sha256": {"manifest.json": hashlib.sha256((pilot / "manifest.json").read_bytes()).hexdigest(),
                                              **{name: manifest["files_sha256"][name] for name in
                                                 ("summary.json", "bundle.json", "study.json.gz")}},
                   "producer_source_sha256": manifest["source_sha256"]},
        "project_scope": {"route_km": summary["route_km"], "stations": summary["stations"],
                          "project_kind": "two-station pilot", "city_corridor_integration": False,
                          "city_brief": "/" + baghdad["path"] + "/README.md",
                          "city_atlas": "/?outlineCity=baghdad",
                          "city_outline_evaluation_id": baghdad["outline_evaluation_id"]},
        "identity": {"physical_candidate_id": candidate_id, "bundle_evaluation_id": evaluation_id,
                      "study_id": study_id, "body_candidate_id": vehicle["candidate_id"],
                      "body_evaluation_id": vehicle["evaluation_id"],
                      "civil_candidate_id": bundle["physical_definition"]["civil_candidate_id"],
                      "civil_evaluation_id": bundle["civil_evaluation_id"],
                      "installed_component_candidate_id": bundle["installed_component_candidate_id"],
                      "installed_mass_evaluation_id": bundle["installed_mass_evaluation_id"]},
        "status": {"outline": summary["status"]["outline"], "engineering": summary["status"]["engineering"],
                   "prototype": summary["status"]["prototype"], "release": summary["status"]["release"],
                   **{flag: False for flag in RELEASE_FLAGS}, "selected_reference_changed": False},
        "journeys": rows,
        "recovery_comparison": {"description": "These are two separately published physical research candidates evaluated at the same nominal timetable. This is not a software toggle or a selected design.",
                                "with_store": current_nominal, "without_store": no_store},
        "body_summary": {key: summary["body"][key] for key in
                         ("source_component_types", "proposed_component_types", "total_occurrences",
                          "nominal_part_mass_kg", "direct_parts_process_usd")},
        "mass_scopes": summary["mass_scopes"],
        "manufacturing": {"vehicle_manifest_id": vehicle["manifest_id"], "delivery_manifest_id": delivery["manifest_id"],
                          "installed_mass_complete": vehicle["installed_mass_complete"],
                          "engineering_accepted": delivery["engineering_accepted"],
                          "manufacturing_release": delivery["manufacturing_release"],
                          "task_status_counts": read_json(root, PILOT / "delivery/summary.json")["summary"]["task_status_counts"]},
        "assumptions": {"price_maturity": summary["price_maturity"], "packaging_screen": summary["packaging_screen"],
                        "requirement_interpretation": requirements["interpretation"], "purpose": bundle["purpose"]},
        "unresolved": frontier["tasks"],
        "downloads": links,
        "gallery": [{"label": "Civil assembly", "href": "/docs/design-engine/reconciled-pilot/civil-assembly.svg"},
                    {"label": "Installed vehicle assembly", "href": "/docs/design-engine/reconciled-pilot/vehicle/assembly.glb"}],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--write", action="store_true", help="write the generated Workbench projection")
    args = parser.parse_args(argv)
    data = build(args.root)
    raw = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if args.write:
        output = args.root / OUTPUT
        output.mkdir(parents=True, exist_ok=True)
        (output / "data.json").write_text(raw)
        print(f"Wrote {OUTPUT / 'data.json'}")
    else:
        print(raw, end="")


if __name__ == "__main__":
    main()
