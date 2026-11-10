#!/usr/bin/env python3
"""Run bounded Samawah route-simplification screens from the merged-stop parent."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import resource
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOLERANCES_M = (25.0, 50.0, 100.0)
BODY_ID = "75075df9247dfff7082a78eadc273d3a99f37e5486450621536c43b1bfa2f797"
BODY_EVAL_ID = "c6c5efe577bd302c507756af53238a8f162c6e2cbeaefd2aa11fecd343b93fb3"
CITY_INPUT_ID = "7377b6fc01b0caaefd6f656f966a1902fcde5164ea36a43f5d3b97f6663a8ca0"
BASELINE_EVAL_ID = "96759ca63bea3f7dff686565185ddd8261ca02f543293f15d7237e8b735f7dd5"
MERGED_CITY_INPUT_PATH = "docs/design-engine/v06-design-closure/samawah-station-consolidation-current-source-attempt-03/derived-city.json"
MERGED_PACKET_DIR = "docs/design-engine/v06-design-closure/samawah-station-consolidation-current-source-attempt-03"
PRESERVED = [
    "docs/design-engine/v06-design-closure/samawah-station-consolidation-current-source-attempt-03/manifest.json",
    "docs/design-engine/v06-design-closure/samawah-alignment-straightening-current-source-attempt-06/manifest.json",
    "docs/design-engine/v06-design-closure/samawah-merged-alignment-screen-current-source-attempt-02/manifest.json",
    "docs/design-engine/v06-design-closure/compact-drive-source-replay-01/manifest.json",
    "docs/design-engine/v06-design-closure/samawah-city-recalculation-current-source/manifest.json",
    "docs/design-engine/v06-design-closure/samawah-candidate-cost-bridge-current-source-attempt-03/manifest.json",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def identity(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def render_readme(request: dict, summary: dict, execution: dict) -> str:
    baseline = summary["baseline"]
    first = summary["scenarios"][0]
    first_failure = first["definition_failures"][0] if first["definition_failures"] else None
    close_gap = None if first_failure is None else first_failure["legs"][0]["distance_m"]
    platform_note = (
        f"All three alternatives still have one 120 m platform-envelope definition failure. "
        f"The close line-1 stop pair is {close_gap:.3f} m apart after simplification; route straightening alone does not resolve it."
        if close_gap is not None else
        "No platform-envelope screen failure remains in these alternatives; this still does not establish a buildable station."
    )
    rows = [
        "| Map | Route km | 120 m platform-envelope failures | Geometry points | Conditional total trainsets low/base/high | Line-1 runtime request (s) |",
        "|---|---:|---:|---:|---:|---:|",
        f"| Merged-stop parent | {baseline['route_km']:.3f} | {baseline['definition_failure_count']} | {baseline['geometry_points']} | {baseline['fleet_low_base_high']} | {baseline['line1_runtime_s']:.1f} |",
    ]
    for scenario in summary["scenarios"]:
        rows.append(
            f"| {scenario['tolerance_m']:.0f} m maximum-deviation screen | {scenario['route_km']:.3f} "
            f"| {scenario['definition_failure_count']} | {scenario['geometry_points']} ({scenario['point_reduction_percent']:.1f}% fewer) "
            f"| {scenario['fleet_low_base_high']} | {scenario['line1_runtime_s']:.1f} |"
        )
    hold_sets = [baseline["holds"], *(row["holds"] for row in summary["scenarios"])]
    shared_holds = hold_sets[0] if all(rows == hold_sets[0] for rows in hold_sets) else None
    hold_section = (
        "Each of the merged-stop parent and three route screens retains the same evaluator holds:\n\n"
        + "\n".join(f"- {hold}" for hold in shared_holds)
        if shared_holds is not None else
        "Evaluator holds by scenario remain in `summary.json` and each exact city evaluation."
    )
    quantity_names = {
        "standard_beams": "Reference 20 m beam units",
        "standard_shared_bents": "Shared bent positions",
        "running_rail_m": "Running rail metres",
        "running_fastening_sets": "Complete fastening sets",
    }
    quantity_columns = [baseline, *summary["scenarios"]]
    quantity_rows = [
        f"| {label} | " + " | ".join(
            f"{item['guideway_quantity_screen'][key]:,.0f}"
            for item in quantity_columns
        ) + " |"
        for key, label in quantity_names.items()
    ]
    return f"""# Samawah merged-stop route-straightening screens

This packet compares three **unselected planning geometries** against the
source-bound close-stop consolidation alternative and exact package-07 vehicle body. Each route is
simplified only between its existing stop markers; station coordinates and all
stop IDs are held fixed. The active map is unchanged.

## Candidate and source identities

- Merged city input: `{request['city_input_id']}`; station-merge candidate/evaluation ancestry: `{request['station_merge_candidate_id']}` / `{request['station_merge_evaluation_id']}`.
- Re-evaluated merged-parent outline candidate/evaluation: `{summary['baseline_candidate_id']}` / `{summary['baseline_evaluation_id']}`.
- Vehicle body: `{request['body_candidate_id']}` / `{request['body_evaluation_id']}`.
- Source commit: `{execution['source_commit']}`.
- Tolerances are maximum sampled deviation from each original stop-to-stop polyline: 25 m, 50 m and 100 m, measured in a local mean-latitude equirectangular projection.

## Recalculated planning comparison

{chr(10).join(rows)}

### Recalculated guideway quantity screen

| Quantity (not priced) | Merged-stop parent | 25 m | 50 m | 100 m |
|---|---:|---:|---:|---:|
{chr(10).join(quantity_rows)}

These reference quantities are not a complete civil takeoff. Foundations,
joints, reinforcement, bearings, station interfaces and construction quantities
remain unverified.

The results are conditional geometry/runtime/fleet calculations. Route and stop
locations remain within the declared mapped corridor band, but the source OSM
coverage is incomplete. No route has been checked against surveyed right-of-way,
land ownership, road crossings, full building records, utilities, ground,
accessibility paths or local construction constraints. The current civil-class
chainages are proportionally transferred to the revised route length only as a
planning assumption and require reassessment; no civil loads are calculated.

{platform_note}

## Remaining evaluator holds

{hold_section}

These are separate from the zero platform-envelope definition failures. The
evaluator has not declared the candidate complete or accepted.

The evaluator's 0.4 m/s² acceleration remains a shared study control, not a
selected train capability. Available propulsion force, braking, curvature,
grade, passenger demand, protected schedules and physical service remain
unverified. All fourteen full city cost scopes remain unknown. The body BOM
subtotal is not complete installed corridor cost.

No tolerance is recommended or selected. A larger tolerance permits more
geometric simplification but can cut across mapped obstacles or unsuitable
land. A route geometry pass is not buildability evidence.

## Reproduction

From the repository root:

```sh
tools/automation/osr-python docs/design-engine/v06-design-closure/samawah-merged-alignment-runner-01/run.py --output-dir /tmp/osr-samawah-merged-alignment-screen
```

The packet contains each derived city and outline evaluation, editable GeoJSON,
the exact worker/runner, source checks, resource usage and a recursive SHA-256
manifest. The worker had 60 CPU seconds and 1 GiB address-space limits with a
60-second parent timeout. The source tree remained writable; no OS-level
read-only sandbox is claimed. No GIS, CAD, FEM, ERPNext or network client was
invoked.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        raise SystemExit("Output directory must be empty")

    worker_source = HERE / "worker.py"
    worker = out / "worker.py"
    shutil.copyfile(worker_source, worker)
    shutil.copyfile(Path(__file__).resolve(), out / "run.py")
    source_commit = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    before = {name: digest(ROOT / name) for name in PRESERVED}
    request = {
        "schema": "osr-samawah-merged-stop-straightening-request/1",
        "city_input_source_path": MERGED_CITY_INPUT_PATH,
        "station_merge_packet_id": "",
        "station_merge_candidate_id": "f3e6532304d2a5f56d44e77ab32b523f4ab3a20850bed633741b68eb33861ea2",
        "station_merge_evaluation_id": BASELINE_EVAL_ID,
        "repository": str(ROOT),
        "source_commit": source_commit,
        "body_candidate_id": BODY_ID,
        "body_evaluation_id": BODY_EVAL_ID,
        "city_input_id": CITY_INPUT_ID,
        "maximum_deviation_tolerances_m": list(TOLERANCES_M),
        "station_coordinates_fixed": True,
        "active_map_update_allowed": False,
        "civil_load_reuse_allowed": False,
        "worker_sha256": digest(worker_source),
        "runner_sha256": digest(Path(__file__).resolve()),
        "preserved_packet_before_hashes": before,
        "cpu_limit_s": 60,
        "address_space_limit_bytes": 1024 ** 3,
        "wall_timeout_s": 60,
        "native_GIS_CAD_FEM_allowed": False,
        "repository_edits_allowed": False,
        "physical_accepted": False,
    }
    merge_manifest = json.loads((ROOT / MERGED_PACKET_DIR / "manifest.json").read_bytes())
    request["station_merge_packet_id"] = merge_manifest["packet_id"]
    request["request_id"] = identity(request)
    (out / "request.json").write_bytes(canonical(request))

    def limits() -> None:
        resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
        resource.setrlimit(resource.RLIMIT_AS, (1024 ** 3, 1024 ** 3))

    started = time.monotonic()
    prior_child = resource.getrusage(resource.RUSAGE_CHILDREN)
    try:
        proc = subprocess.run([sys.executable, "-I", "-B", str(worker)], cwd=out,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=limits, timeout=60)
        (out / "stdout.log").write_bytes(proc.stdout)
        (out / "stderr.log").write_bytes(proc.stderr)
        code = proc.returncode
    except subprocess.TimeoutExpired as exc:
        (out / "stdout.log").write_bytes(exc.stdout or b"")
        (out / "stderr.log").write_bytes(exc.stderr or b"")
        code = 124
    elapsed = time.monotonic() - started
    child = resource.getrusage(resource.RUSAGE_CHILDREN)
    after = {name: digest(ROOT / name) for name in PRESERVED}
    unchanged = before == after
    execution = {
        "schema": "osr-samawah-merged-stop-straightening-execution/1",
        "source_commit": source_commit,
        "request_id": request["request_id"],
        "executed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "returncode": code,
        "resources": {
            "wall_seconds": elapsed,
            "child_cpu_user_seconds_delta": child.ru_utime - prior_child.ru_utime,
            "child_cpu_system_seconds_delta": child.ru_stime - prior_child.ru_stime,
            "child_max_rss_kib": child.ru_maxrss,
            "hard_limits_applied": True,
        },
        "preserved_packet_before_hashes": before,
        "preserved_packet_after_hashes": after,
        "preserved_packets_unchanged": unchanged,
        "execution_boundary": {
            "gis": False, "cad": False, "fem": False, "erpnext": False,
            "network_client_invoked": False, "os_sandbox_enforced": False,
            "source_tree_writable": True,
        },
    }
    (out / "execution.json").write_bytes(canonical(execution))
    if code != 0 or not unchanged:
        raise SystemExit(f"Screen not admitted: returncode={code}; source_packets_unchanged={unchanged}")

    summary = json.loads((out / "summary.json").read_bytes())
    (out / "README.md").write_text(render_readme(request, summary, execution), encoding="utf-8")
    files = {
        path.relative_to(out).as_posix(): digest(path)
        for path in sorted(out.rglob("*")) if path.is_file() and path.name != "manifest.json"
    }
    manifest = {
        "schema": "osr-samawah-merged-stop-straightening-packet/1",
        "source_commit": source_commit,
        "request_id": request["request_id"],
        "baseline_candidate_id": summary["baseline"]["candidate_id"],
        "scenario_candidate_ids": {str(row["tolerance_m"]): row["candidate_id"] for row in summary["scenarios"]},
        "scenario_evaluation_ids": {str(row["tolerance_m"]): row["evaluation_id"] for row in summary["scenarios"]},
        "file_count": len(files),
        "files_sha256": files,
        "integrity_scope": "All regular files recursively below this packet, using relative POSIX paths; manifest excludes itself.",
        "selected": False,
        "physical_accepted": False,
        "gate_closed": False,
    }
    manifest["packet_id"] = identity(manifest)
    (out / "manifest.json").write_bytes(canonical(manifest))
    print(json.dumps({"packet_id": manifest["packet_id"], "scenario_count": len(summary["scenarios"]),
        "candidate_ids": manifest["scenario_candidate_ids"], "returncode": code,
        "wall_seconds": elapsed}, sort_keys=True))


if __name__ == "__main__":
    main()
