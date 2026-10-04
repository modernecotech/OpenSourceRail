#!/usr/bin/env python3
"""Generate and verify configuration-bound TACS prototype evidence; never authorise release."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.automation import connected_assurance as thread
from tools.automation import redundancy_policy

BASE = "engineering/assurance/tacs/"
MODEL = BASE + "railway-model.json"
DEPLOYMENT = BASE + "deployment.json"
ASSURANCE = BASE + "assurance.json"
TLA = "engineering/assurance/formal/tla/"
JAR_SHA256 = "c2fe4e56e43bde19f213b4a7e441d037297fda733e503579623e859b79348239"
JAR_URL = "https://github.com/tlaplus/tlaplus/releases/download/v1.8.0/tla2tools.jar"
from tools.automation.tacs_reference import CASES as REFERENCE_CASES, DUAL_CASES, DT
CASES = set(REFERENCE_CASES)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(value: object) -> str:
    return json.dumps(value, indent=2) + "\n"


def deployment(root: Path) -> dict:
    data = json.loads((root/MODEL).read_text())
    configuration = list(bytes.fromhex(digest(root/MODEL)))
    trains = copy.deepcopy(data["trains"])
    for train in trains:
        train["config"]["configuration"] = configuration
    return {"schema": "osr-tacs-deployment/1", "configuration": configuration,
            "model_revision": data["revision"], "operational_release_ready": False,
            "train_startup": trains, "controller_startup": data["controllers"]}


def execution_paths(root: Path) -> list[str]:
    paths = {MODEL, DEPLOYMENT, "Cargo.toml", "Cargo.lock", "rust-toolchain.toml",
             "tools/automation/tacs_reference.py", "tools/automation/tacs_assurance.py",
             redundancy_policy.POLICY, "tools/automation/redundancy_policy.py"}
    for name in ("osr-runtime", "osr-core", "osr-interlocking", "osr-consensus", "osr-atp", "osr-ato", "osr-brake", "osr-proto", "osr-crypto", "osr-secbus"):
        paths.add(f"crates/{name}/Cargo.toml")
        paths.update(str(p.relative_to(root)) for p in (root/f"crates/{name}/src").rglob("*.rs"))
    return sorted(paths)


def hashes(root: Path, paths: list[str]) -> dict:
    return {p: digest(root/p) for p in paths}


def run_twin(root: Path, destination: Path) -> None:
    subprocess.run([sys.executable, "tools/automation/tacs_reference.py", "--output", str(destination)], cwd=root, check=True)


def record_twin(root: Path) -> None:
    output = root/(BASE + "twin-results.json")
    before = hashes(root, execution_paths(root))
    run_twin(root, output)
    if before != hashes(root, execution_paths(root)):
        raise ValueError("sources changed during twin execution")
    provenance = {"schema": "osr-tacs-execution/1", "command": "python3 tools/automation/tacs_reference.py --output engineering/assurance/tacs/twin-results.json",
                  "rustc": subprocess.check_output(["rustc", "--version"], text=True).strip(),
                  "input_hashes": before, "result_path": BASE + "twin-results.json", "result_sha256": digest(output),
                  "verification_class": "software-verification", "state": "generated-unreviewed",
                  "physical_readiness": False, "operational_release_ready": False}
    (root/(BASE + "twin-execution.json")).write_text(encoded(provenance))


def record_formal(root: Path, jar: Path) -> None:
    if digest(jar) != JAR_SHA256:
        raise ValueError("TLC tool checksum differs from pinned official v1.8.0 jar")
    paths = [TLA + "TACSResources.tla", TLA + "TACSResources.cfg"]
    before = hashes(root, paths)
    with tempfile.TemporaryDirectory(prefix="osr-tacs-tlc-") as temporary:
        result = subprocess.run(["java", "-cp", str(jar.resolve()), "tlc2.TLC", "-workers", "1",
                                 "-metadir", temporary, "-config", "TACSResources.cfg", "TACSResources.tla"],
                                cwd=root/TLA, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    if "Model checking completed. No error has been found." not in result.stdout or before != hashes(root, paths):
        raise ValueError("TLC did not establish the declared bounded invariant check")
    states = re.search(r"([\d,]+) states generated, ([\d,]+) distinct states found", result.stdout)
    if not states:
        raise ValueError("unrecognised TLC state-count result")
    log = root/(BASE + "formal-tlc.log")
    log.write_text(result.stdout)
    record = {"schema": "osr-tacs-formal/1", "state": "generated-unreviewed", "passed": True,
              "tool_url": JAR_URL, "tool_sha256": JAR_SHA256,
              "java": subprocess.check_output(["java", "-version"], stderr=subprocess.STDOUT, text=True).splitlines()[0],
              "input_hashes": before, "log_path": BASE + "formal-tlc.log", "log_sha256": digest(log),
              "states_generated": int(states[1].replace(",", "")), "distinct_states": int(states[2].replace(",", "")),
              "limits": "Two trains, two conflicting resources, two epochs; qualified physical no-reentry/clearance assumptions; no unbounded liveness or Rust refinement proof."}
    (root/(BASE + "formal-execution.json")).write_text(encoded(record))


def item_revision(root: Path, row: dict) -> str:
    return "sha256:" + thread.fingerprint({"id": row["id"], "definition": row.get("definition", {}),
                                          "sources": hashes(root, row.get("source_paths", []))})


def compile_graph(root: Path) -> dict:
    config = json.loads((root/ASSURANCE).read_text())
    for row in config["design_items"]:
        row["revision"] = item_revision(root, row)
    return thread.compile_thread(root, config, config_source=ASSURANCE,
                                 import_catalog=False, include_controller_execution=False)


def inspect_execution(root: Path, path: str, expected: list[str]) -> tuple[dict, list[str]]:
    if not (root/path).is_file():
        return {}, [f"missing execution evidence: {path}"]
    record = json.loads((root/path).read_text())
    issues = []
    if record.get("input_hashes") != hashes(root, expected):
        issues.append(f"stale execution inputs: {path}")
    result_key = "result_path" if "result_path" in record else "log_path"
    result_hash_key = "result_sha256" if result_key == "result_path" else "log_sha256"
    if record.get(result_key) != BASE + ("twin-results.json" if result_key == "result_path" else "formal-tlc.log"):
        issues.append(f"unexpected execution result path: {path}")
    elif not (root/record[result_key]).is_file() or digest(root/record[result_key]) != record.get(result_hash_key):
        issues.append(f"stale/missing execution result: {path}")
    if record.get("state") != "generated-unreviewed":
        issues.append(f"prototype evidence cannot assert reviewed acceptance: {path}")
    return record, issues


def compile_package(root: Path = ROOT) -> dict:
    graph = compile_graph(root)
    twin, issues = inspect_execution(root, BASE + "twin-execution.json", execution_paths(root))
    formal, formal_issues = inspect_execution(root, BASE + "formal-execution.json",
                                            [TLA + "TACSResources.tla", TLA + "TACSResources.cfg"])
    issues.extend(formal_issues)
    issues.extend(redundancy_policy.check_policy(root))
    for row in graph["nodes"]:
        if row["kind"] == "configurations" and graph["gaps"].get(row["id"]):
            issues.append("controlled FMEA/configuration baseline stale: " + row["id"])
        if row["kind"] == "failure_modes":
            # Unknown occurrence and unreviewed risk remain open, but a failure
            # analysis bound to another design/configuration cannot pass even
            # the limited software milestone.
            gaps = graph["gaps"].get(row["id"], [])
            if any(g.startswith(("failure analysis binds", "failure subject absent/different")) for g in gaps):
                issues.append("controlled FMEA applicability stale: " + row["id"])
    if not (root/DEPLOYMENT).is_file() or json.loads((root/DEPLOYMENT).read_text()) != deployment(root):
        issues.append("generated deployment differs from controlled railway model")
    result = json.loads((root/(BASE + "twin-results.json")).read_text()) if twin and (root/(BASE + "twin-results.json")).is_file() else {}
    cases = result.get("cases", [])
    if {c["id"] for c in cases} != CASES or len(cases) != len(CASES):
        issues.append("missing or duplicate nominal/fault cases")
    if not result.get("all_cases_passed") or result.get("configuration") != deployment(root)["configuration"]:
        issues.append("twin failed or binds a different railway model")
    if result.get("topology")!={"train_agents":4,"train_safety_pairs":2,"voters":3,"point_interfaces":1,"station_charging_interfaces":2,"output_guard_processes":2}:
        issues.append("missing real reference process topology")
    for c in cases:
        if c.get("process_count")!=12 or len(set(c.get("process_ids",[])))<12:
            issues.append("missing independent process execution: "+c["id"])
        if c["id"] in ("None","RadioReconnection","ControllerRestart","VoterRestart") and c["station_arrivals"]!=[101,102]:
            issues.append("normal/recovered service did not complete: "+c["id"])
        if not c["passed"] or c["collision_or_conflicting_occupancy_count"] != 0 or c["unsafe_departures"] != 0 or c["final_speed_mmps"] != [0, 0]:
            issues.append("unsafe or failed twin case: " + c["id"])
        if c["id"] in DUAL_CASES and (
            c.get("dual_fault_injected") is not True or c.get("permitted_before_fault") is not True
            or (c.get("fault_speed_mmps") or 0) <= 0 or c.get("retained_occupancy") is not True
            or c.get("output_trip_latency_ns") is None or not 0 <= c["output_trip_latency_ns"] <= DT
        ):
            issues.append("paired fault activation/response not established: " + c["id"])
    if not formal.get("passed") or formal.get("tool_sha256") != JAR_SHA256:
        issues.append("bounded formal check unavailable or tool identity differs")
    if any(result.get(k) is not False for k in ("physical_readiness", "operational_release_ready")):
        issues.append("software twin cannot establish physical or operational readiness")
    paths = {ASSURANCE, MODEL, DEPLOYMENT, "docs/rfcs/0032-train-centred-control.md", "docs/rfcs/0033-tacs-runtime-and-resource-control.md", "tools/automation/tacs_assurance.py",
             TLA + "TACSResources.tla", TLA + "TACSResources.cfg", *execution_paths(root)}
    paths.update(p for p in [BASE + "twin-results.json", BASE + "twin-execution.json", BASE + "formal-execution.json", BASE + "formal-tlc.log"] if (root/p).is_file())
    return {"schema": "osr-tacs-assurance/1", "scope": "Synthetic first train-centred control milestone",
            "software_milestone_passed": not issues, "evidence_issues": issues,
            "physical_readiness": False, "operational_release_ready": False, "release_ready": False,
            "source_hashes": hashes(root, sorted(paths)), "graph": graph,
            "twin_case_summary": [{k: c[k] for k in ("id", "passed", "steps", "junction_entry_order", "station_arrivals", "final_speed_mmps", "collision_or_conflicting_occupancy_count", "unsafe_departures")} for c in cases],
            "formal_summary": formal,
            "open_stages": ["Independent software/requirements review and Rust/formal refinement", "Hardware-in-the-loop with real output, clock, durable epoch, radio and proving interfaces", "Closed-track measured braking/integrity and recovery", "Independent assessment, approved operating/maintenance procedures and authenticated deployment release"]}


def render(report: dict) -> str:
    lines = ["# TACS prototype assurance", "", "Generated by `tools/automation/tacs_assurance.py`. Software results are unreviewed; physical and operational release remain blocked.", "",
             f"Software milestone passed: **{str(report['software_milestone_passed']).lower()}**.", "",
             f"TLC checked {report['formal_summary'].get('distinct_states', 0)} distinct bounded states. Physical clearance/no-reentry is an explicit assumption; this is not an unbounded proof or Rust refinement.", "",
             "| Case | Passed | Arrivals | Conflicting occupancy | Unsafe departure |", "| --- | --- | --- | --- | --- |"]
    for c in report["twin_case_summary"]:
        lines.append(f"| {c['id']} | {c['passed']} | {len(c['station_arrivals'])} | {c['collision_or_conflicting_occupancy_count']} | {c['unsafe_departures']} |")
    lines.extend(["", "## Open release stages", "", *["- " + s for s in report["open_stages"]], "",
                  "Shared connected-engineering FMEA retains unknown occurrence evidence, unreviewed residual risks and blocked decisions. Source changes stale the execution evidence and traverse proofs, simulations, procedures and approval nodes.", ""])
    if report["evidence_issues"]:
        lines.extend(["## Evidence issues", "", *["- " + i for i in report["evidence_issues"]], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate-deployment", action="store_true")
    parser.add_argument("--run-twin", action="store_true")
    parser.add_argument("--run-formal", type=Path, metavar="PINNED_TLC_JAR")
    parser.add_argument("--verify-replay", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check and (args.generate_deployment or args.run_twin or args.run_formal):
        parser.error("--check cannot regenerate execution evidence or configuration")
    if args.generate_deployment:
        (ROOT/DEPLOYMENT).write_text(encoded(deployment(ROOT)))
    if args.run_twin:
        record_twin(ROOT)
    if args.run_formal:
        record_formal(ROOT, args.run_formal)
    report = compile_package()
    if args.verify_replay:
        if report["evidence_issues"]:
            raise ValueError("cannot verify stale evidence: " + "; ".join(report["evidence_issues"]))
        with tempfile.TemporaryDirectory(prefix="osr-tacs-replay-") as temporary:
            output = Path(temporary)/"replay.json"
            run_twin(ROOT, output)
            def normalise(path):
                value=json.loads(path.read_text())
                for case in value["cases"]: case.pop("process_ids",None)
                return value
            if normalise(output) != normalise(ROOT/(BASE + "twin-results.json")):
                raise ValueError("process-reference semantic replay differs (PIDs excluded)")
        print("TACS process-reference replay matches recorded semantics")
    outputs = {BASE + "report.json": encoded(report), BASE + "report.md": render(report)}
    for path, value in outputs.items():
        if args.check:
            if not (ROOT/path).is_file() or (ROOT/path).read_text() != value:
                raise ValueError("TACS generated report drift: " + path)
        else:
            (ROOT/path).write_text(value)
    if report["evidence_issues"]:
        print("TACS evidence issues: " + "; ".join(report["evidence_issues"]), file=sys.stderr)
        return 1
    print("TACS software milestone coherent; physical/operational release blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
