#!/usr/bin/env python3
"""Run actual local part families twice and verify bounded native search replay."""

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engineering.design_engine import runtime
from engineering.design_engine.contracts import fingerprint
from engineering.design_engine.export import export, verify_export
from engineering.design_engine.generated_parts import defaults
from engineering.design_engine.registry import dependencies
from engineering.design_engine.store import write_new


def validate(output):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    manager = runtime.Manager(output / "store")
    receipt = dict(schema="osr-native-recursive-pilot/1", runs=[], passed=False,
                   validation_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   execution="local-installed-native-tools", physical_release=False,
                   global_optimum_claimed=False)
    try:
        for family in ("mechanical-cleat", "civil-steel-beam"):
            scope = dict(schema="osr-design-identity/1", city="samawah", project="native-part-pilot",
                         environment="simulation", configuration_revision="research-native-parts-1",
                         baseline_sha256=None, run_id=None, asset_id=None, part_id=None)
            req = runtime.request(family, scope, recursive=dict(
                evaluations=12, confirmations=6, finite_exhaustive=True),
                budget=dict(evaluations=64, wall_seconds=1800))
            traces = []
            for repeat in range(2):
                job = manager.start(req)
                print(f"{family} repeat {repeat+1}: {job['id']}", flush=True)
                while manager.store.get(job["id"])["status"] not in runtime.TERMINAL:
                    time.sleep(.2)
                job = manager.store.get(job["id"])
                attempt = manager.store.root / "runs" / job["id"] / "attempt-0001"
                row = dict(family=family, repeat=repeat+1, job=job["id"], status=job["status"],
                           request_sha256=fingerprint(req), dependencies=req["dependencies"],
                           toolchain=req["toolchain"], attempt=str(attempt.relative_to(output)))
                receipt["runs"].append(row)
                if job["status"] != "completed":
                    raise ValueError("Native job did not complete: " + str(job.get("error")))
                manager.store.verify_attempt(job["id"], 1)
                report = runtime.comparison(manager.store, job["id"])
                search = report["recursive_search"]
                row.update(decision_trace_sha256=search["decision_trace_sha256"],
                           evaluations_spent=report["evaluations_spent"],
                           finite_domain_complete=search["finite_domain_complete"],
                           native_domain_complete=search["native_domain_complete"],
                           incumbent_id=search["incumbent_id"],
                           outcomes=search["outcomes"], termination_reason=search["termination_reason"])
                if not (len(report["candidates"]) == 6 and search["confirmations"] == 6
                        and report["evaluations_spent"] == 24 and search["native_domain_complete"]
                        and search["best_verified_in_tested_domain_claimed"]):
                    raise ValueError("Finite native domain did not close; inspect retained failed/unknown cases")
                winner = next(c for c in report["candidates"] if c["id"] == search["incumbent_id"])
                initial = next(c for c in report["candidates"] if c["variables"] == defaults(family))
                row.update(initial_mass_kg=initial["metrics"]["defined_mass_kg"],
                           selected_mass_kg=winner["metrics"]["defined_mass_kg"],
                           selected_variables=winner["variables"], candidates=[])
                if row["selected_mass_kg"] >= row["initial_mass_kg"]:
                    raise ValueError("This pilot did not demonstrate an improved feasible design")
                for candidate in report["candidates"]:
                    native = candidate["definition"]["native_confirmation"]
                    if native.get("failure") or native["definition_sha256"] != fingerprint(candidate["definition"]["model"]):
                        raise ValueError("Incomplete or mismatched actual native execution")
                    if any(candidate["checks"][key]["state"] != "unknown"
                           for key in ("physical_correlation", "independent_acceptance")):
                        raise ValueError("Numerical job changed physical qualification")
                    if candidate["physical_release"] or search["global_optimum_claimed"]:
                        raise ValueError("Invalid physical/global optimum claim")
                    row["candidates"].append(dict(id=candidate["id"], variables=candidate["variables"],
                        metrics=candidate["metrics"], checks=candidate["checks"],
                        native_artifacts_sha256=native["artifacts_sha256"]))
                traces.append(search["decision_trace_sha256"])
                if repeat == 0:
                    destination = output / (family + "-review")
                    export(manager.store, job["id"], destination, native=True)
                    verified = verify_export(destination)
                    row["review_manifest_sha256"] = hashlib.sha256((destination / "manifest.json").read_bytes()).hexdigest()
                    row["review_files"] = len(verified["files"])
                print(f"  mass {row['initial_mass_kg']:.6f} → {row['selected_mass_kg']:.6f} kg; trace {traces[-1]}", flush=True)
            if len(set(traces)) != 1:
                raise ValueError("Native search decisions differed on identical completed requests")
            if req["dependencies"] != dependencies(family) or req["toolchain"] != runtime.toolchain(family):
                raise ValueError("Source or actual tools changed during repeated pilot")
        receipt["passed"] = True
    except Exception as error:
        receipt["error"] = dict(type=type(error).__name__, message=str(error))
        raise
    finally:
        write_new(output / "receipt.json", receipt)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="Fresh immutable local output directory")
    args = parser.parse_args()
    result = validate(args.output)
    print(json.dumps(dict(passed=result["passed"], runs=len(result["runs"]), receipt=str(args.output / "receipt.json"))))
