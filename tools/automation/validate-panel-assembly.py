#!/usr/bin/env python3
"""Execute common panel iteration and export actual full-assembly CAD/takeoff."""

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "design/component-catalogue/src")]

from engineering.design_engine import runtime
from engineering.design_engine.contracts import fingerprint
from engineering.design_engine.export import export, verify_export
from engineering.design_engine.generated_parts_native import toolchain
from engineering.design_engine.store import write_new


def validate(output):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    scope = dict(
        schema="osr-design-identity/1",
        city="samawah",
        project="panel-assembly-pilot",
        environment="simulation",
        configuration_revision="panel-assembly-research-1",
        baseline_sha256=None,
        run_id=None,
        asset_id=None,
        part_id=None,
    )
    req = runtime.request(
        "clipped-side-bay",
        scope,
        [dict(support_span_m=0.2, grade_density=80, core_m=0.0246, skin_m=0.0015)],
        recursive=dict(evaluations=4, confirmations=2),
        budget=dict(evaluations=256, wall_seconds=1800, artifact_mib=512),
    )
    tools = toolchain()
    if not tools["available"]:
        raise RuntimeError(
            "Required native assembly tools unavailable: " + ", ".join(tools["missing"])
        )
    manager = runtime.Manager(output / "store")
    job = manager.start(req)
    print("Actual panel assembly job:", job["id"], flush=True)
    while manager.store.get(job["id"])["status"] not in runtime.TERMINAL:
        time.sleep(0.2)
    job = manager.store.get(job["id"])
    if job["status"] != "completed":
        raise ValueError(
            "Panel assembly job did not complete: " + str(job.get("error"))
        )
    manager.store.verify_attempt(job["id"], 1)
    report = runtime.comparison(manager.store, job["id"])
    search = report["recursive_search"]
    if search["confirmations"] != 2 or not search["incumbent_id"]:
        raise ValueError(
            "Actual panel iteration did not confirm two candidates and a conditional incumbent"
        )
    destination = output / "review"
    print("Exporting represented multibody panel and native CAD", flush=True)
    manifest = export(manager.store, job["id"], destination, native=True)
    verify_export(destination)
    if tools != toolchain():
        raise ValueError("Actual native tools changed during assembly workflow")
    selected = next(
        c for c in report["candidates"] if c["id"] == search["incumbent_id"]
    )
    packet = json.loads(
        (
            destination / "panel-assemblies" / selected["id"] / "assembly-review.json"
        ).read_text()
    )
    native = next(
        n for n in manifest["native_exports"] if n["candidate"] == selected["id"]
    )
    if native["state"] != "numerically-verified":
        raise ValueError(
            "Native full assembly correspondence failed; diagnostic export retained"
        )
    if (
        packet["complete_installed_kit"]
        or packet["complete_installed_mass_kg"] is not None
    ):
        raise ValueError(
            "Missing sealing/retention/frame details cannot become a complete installed kit"
        )
    receipt = dict(
        schema="osr-panel-assembly-pilot/1",
        passed=True,
        job=job["id"],
        request_sha256=fingerprint(req),
        dependencies=req["dependencies"],
        native_tools=tools,
        driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        decision_trace_sha256=search["decision_trace_sha256"],
        termination_reason=search["termination_reason"],
        best_verified_in_tested_domain_claimed=search[
            "best_verified_in_tested_domain_claimed"
        ],
        candidates=[
            dict(
                id=c["id"],
                variables=c["variables"],
                metrics=c["metrics"],
                checks=c["checks"],
            )
            for c in report["candidates"]
        ],
        selected_id=selected["id"],
        represented_part_count=packet["represented_part_count"],
        represented_mass_kg=packet["represented_mass_kg"],
        represented_connection_count=len(packet["connections"]),
        manufacturing_region_count=len(packet["manufacturing_takeoff"]),
        clearance_hole_region_count=len(packet["machining"]),
        unresolved_allocations=packet["unresolved_allocations"],
        native_correspondence=native,
        exported_files=len(manifest["files"]),
        export_manifest_sha256=hashlib.sha256(
            (destination / "manifest.json").read_bytes()
        ).hexdigest(),
        complete_installed_mass_kg=None,
        complete_installed_kit=False,
        physical_release=False,
        independently_accepted=False,
    )
    write_new(output / "receipt.json", receipt)
    print(
        json.dumps(
            {
                key: receipt[key]
                for key in (
                    "passed",
                    "job",
                    "represented_part_count",
                    "represented_connection_count",
                    "represented_mass_kg",
                    "complete_installed_kit",
                )
            }
        )
    )
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Fresh immutable local output directory",
    )
    args = parser.parse_args()
    validate(args.output)
