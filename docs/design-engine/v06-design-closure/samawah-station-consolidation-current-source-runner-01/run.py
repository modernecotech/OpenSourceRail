#!/usr/bin/env python3
"""Run a source-bound midpoint-merger city study in a private output directory."""
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
ROOT = HERE.parents[4]
CASES = ("low", "base", "high")
BODY_FILE = "docs/design-engine/v06-design-closure/compact-drive-source-replay-01/compact-737-h100/body.json.gz"
BODY_ID = "75075df9247dfff7082a78eadc273d3a99f37e5486450621536c43b1bfa2f797"
BODY_EVALUATION_ID = "c6c5efe577bd302c507756af53238a8f162c6e2cbeaefd2aa11fecd343b93fb3"
CITY_INPUT_ID = "dd952bf0526a58894757dee67031894cece6cd4fc45c074d711a8c76188405de"
BASELINE_EVALUATION_ID = "eaa84ee07efbff5763ec11e490142f88d2701c1196d09c63b7bfc9b18ce61a16"
MARKERS = ["line-1-0485-0464-s009300", "line-1-0487-0466-s009380"]
PRESERVED = [
    "docs/design-engine/v06-design-closure/compact-drive-source-replay-01/manifest.json",
    "docs/design-engine/v06-design-closure/samawah-city-recalculation-current-source/manifest.json",
    "docs/design-engine/v06-design-closure/samawah-station-consolidation/manifest.json",
    "docs/design-engine/v06-design-closure/samawah-candidate-cost-bridge-current-source-attempt-03/manifest.json",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def identity(value: object) -> str:
    return hashlib.sha256(encoded(value)).hexdigest()


def snapshot() -> dict[str, str]:
    return {name: digest(ROOT / name) for name in PRESERVED}


def tri(values: dict) -> str:
    return " / ".join(f"{values[c]:,.0f}" for c in CASES)


def render_readme(request: dict, result: dict, comparison: dict, derivation: dict, execution: dict) -> str:
    baseline = comparison["baseline"]
    revised = comparison["midpoint_scenario"]
    return f"""# Samawah close-stop planning alternative — current body source

This is a source-bound planning alternative that merges the line-1 station markers
`{MARKERS[0]}` and `{MARKERS[1]}` at their along-route midpoint. It leaves the
published city map and active reference untouched. It is not an approved station
relocation or an engineering-accepted corridor.

## Exact candidate and source

- City input: `{request['city_input_id']}`; body: `{request['body_candidate_id']}` / evaluation `{request['body_evaluation_id']}`.
- Current-source baseline city evaluation: `{request['reference_outline_evaluation_id']}`.
- Alternative city candidate/evaluation: `{result['candidate_id']}` / `{result['evaluation_id']}`.
- Source commit: `{execution['source_commit']}`.
- Source marker separation: 79.977 m; midpoint chainage: {derivation['midpoint_chainage_m']:.3f} m.

## Recalculated outline quantities

| Measure | Current map | Midpoint alternative |
|---|---:|---:|
| Route length (m) | {baseline['route_m']:,.1f} | {revised['route_m']:,.1f} |
| Station markers | {baseline['station_markers']} | {revised['station_markers']} |
| Line-1 one-way kinematic request (s) | {baseline['line1_runtime_s']:,.1f} | {revised['line1_runtime_s']:,.1f} |
| Counted BOM/process subtotal (USD) | ${baseline['known_counted_BOM_process_subtotal_usd']['base']:,.0f} base | ${revised['known_counted_BOM_process_subtotal_usd']['base']:,.0f} base |
| Total trainsets | {tri({c: baseline['fleet_request_cases'][c]['total_trainsets'] for c in CASES})} | {tri({c: revised['fleet_request_cases'][c]['total_trainsets'] for c in CASES})} |

Route, station counts and one-way runtime are single values; the displayed
fleet request and body BOM subtotal retain their low/base/high cases. The body
evaluation and all other line geometries are held constant. The merge
removes the local 120 m platform-envelope definition conflict; it does not prove
that the retained hospital-area access, interchange, catchment, station footprint,
utilities, or right-of-way remain adequate. Available force, braking, grade,
charging, thermal duty and detailed civil loads remain unknown. Fleet and journey
values are conditional calculations, not a protected timetable or achieved service.

No historical total city cost or NPV is transferred. The complete fourteen-scope
city cost, installed CAPEX and lifecycle NPV remain unknown for this alternate
planning identity. This packet ran no CAD, FEM, native GIS, ERPNext or network
client and does not grant physical, engineering, manufacturing or operating
acceptance.

## Reproduction

From the repository root, run the committed source worker with a fresh private
output directory:

```sh
tools/automation/osr-python docs/design-engine/v06-design-closure/samawah-station-consolidation-current-source-runner-01/run.py --output-dir /tmp/osr-samawah-station-consolidation-replay
```

The packet records the exact worker, request, source hashes, resource limits,
stdout/stderr and an integrity manifest. Linux child limits were 60 CPU seconds
and 1 GiB address space with a 60 second parent timeout; the repository source
filesystem remained writable and no OS read-only sandbox is claimed.
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
    before = snapshot()
    request = {
        "schema": "osr-samawah-current-source-station-consolidation-request/1",
        "repository": str(ROOT),
        "source_commit": source_commit,
        "body_candidate_id": BODY_ID,
        "body_evaluation_id": BODY_EVALUATION_ID,
        "runner_sha256": digest(Path(__file__).resolve()),
        "city_input_id": CITY_INPUT_ID,
        "reference_outline_evaluation_id": BASELINE_EVALUATION_ID,
        "source_marker_ids": MARKERS,
        "operation": "Merge only the named line-1 pair at mean chainage on the unchanged mapped polyline; preserve all other stops, lines, interchanges except exact retired-ID rebinding, service policy and body.",
        "worker_sha256": digest(worker_source),
        "retained_packet_before_hashes": before,
        "cpu_limit_s": 60,
        "address_space_limit_bytes": 1024 ** 3,
        "wall_timeout_s": 60,
        "native_GIS_CAD_FEM_allowed": False,
        "network_client_allowed": False,
        "repository_edits_allowed": False,
        "physical_accepted": False,
    }
    request["request_id"] = identity(request)
    (out / "request.json").write_bytes(encoded(request))

    def limits() -> None:
        resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
        resource.setrlimit(resource.RLIMIT_AS, (1024 ** 3, 1024 ** 3))

    command = [sys.executable, "-I", "-B", str(worker)]
    started = time.monotonic()
    prior_child = resource.getrusage(resource.RUSAGE_CHILDREN)
    try:
        proc = subprocess.run(command, cwd=out, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              preexec_fn=limits, timeout=60)
        (out / "stdout.log").write_bytes(proc.stdout)
        (out / "stderr.log").write_bytes(proc.stderr)
        returncode = proc.returncode
    except subprocess.TimeoutExpired as exc:
        (out / "stdout.log").write_bytes(exc.stdout or b"")
        (out / "stderr.log").write_bytes(exc.stderr or b"")
        returncode = 124
    elapsed = time.monotonic() - started
    child = resource.getrusage(resource.RUSAGE_CHILDREN)
    after = snapshot()
    retained_unchanged = before == after
    (out / "execution.json").write_bytes(encoded({
        "schema": "osr-samawah-current-source-station-consolidation-execution/1",
        "executed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_commit": source_commit,
        "request_id": request["request_id"],
        "returncode": returncode,
        "resources": {
            "wall_seconds": elapsed,
            "child_cpu_user_seconds_delta": child.ru_utime - prior_child.ru_utime,
            "child_cpu_system_seconds_delta": child.ru_stime - prior_child.ru_stime,
            "child_max_rss_kib": child.ru_maxrss,
            "hard_limits_applied": True,
        },
        "retained_packet_before_hashes": before,
        "retained_packet_after_hashes": after,
        "retained_packets_unchanged": retained_unchanged,
        "execution_boundary": {
            "cad": False, "fem": False, "gis": False, "erpnext": False,
            "network_client_invoked": False, "os_sandbox_enforced": False,
            "source_tree_writable": True,
        },
    }))
    if returncode != 0 or not retained_unchanged:
        raise SystemExit(f"Candidate study not admitted: returncode={returncode}; retained_unchanged={retained_unchanged}")

    result = json.loads((out / "result.json").read_bytes())
    comparison = json.loads((out / "comparison.json").read_bytes())
    derivation = json.loads((out / "derivation.json").read_bytes())
    (out / "README.md").write_text(render_readme(request, result, comparison, derivation,
        json.loads((out / "execution.json").read_bytes())), encoding="utf-8")
    files = {p.name: digest(p) for p in sorted(out.iterdir()) if p.is_file() and p.name != "manifest.json"}
    manifest = {
        "schema": "osr-samawah-current-source-station-consolidation-packet/1",
        "source_commit": source_commit,
        "request_id": request["request_id"],
        "candidate_id": result["candidate_id"],
        "body_candidate_id": result["body_candidate_id"],
        "body_evaluation_id": result["body_evaluation_id"],
        "evaluation_id": result["evaluation_id"],
        "files_sha256": files,
        "file_count": len(files),
        "physical_accepted": False,
        "gate_closed": False,
    }
    manifest["packet_id"] = identity(manifest)
    (out / "manifest.json").write_bytes(encoded(manifest))
    print(json.dumps({"packet_id": manifest["packet_id"], "candidate_id": result["candidate_id"],
                      "evaluation_id": result["evaluation_id"], "body_evaluation_id": result["body_evaluation_id"],
                      "returncode": returncode, "wall_seconds": elapsed}, sort_keys=True))


if __name__ == "__main__":
    main()
