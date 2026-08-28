#!/usr/bin/env python3
"""Fail closed when software inventory and simulator coverage drift apart."""

from __future__ import annotations

import argparse
import hashlib
import json
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEPLOYMENT = REPO_ROOT / "deployment/components.toml"
CONTRACT = REPO_ROOT / "lib/simulation-component-coverage.toml"
SIM_CARGO = REPO_ROOT / "crates/osr-sim/Cargo.toml"
CATEGORIES = (
    "tick_controller",
    "runtime_kernel",
    "scenario_model",
    "design_pipeline",
    "simulation_shell",
    "external_boundary",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_toml(path: Path) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def build_report(result_path: Path | None = None) -> dict:
    deployment = load_toml(DEPLOYMENT)
    contract = load_toml(CONTRACT)
    cargo = load_toml(SIM_CARGO)
    inventory = {item["name"] for item in deployment.get("component", [])}
    assignments: dict[str, str] = {}
    issues: list[str] = []
    for category in CATEGORIES:
        for name in contract.get(category, {}).get("components", []):
            previous = assignments.get(name)
            if previous:
                issues.append(f"{name} assigned to both {previous} and {category}")
            assignments[name] = category
    missing = sorted(inventory - assignments.keys())
    unknown = sorted(assignments.keys() - inventory)
    if missing:
        issues.append("unclassified deployment components: " + ", ".join(missing))
    if unknown:
        issues.append("coverage entries absent from deployment inventory: " + ", ".join(unknown))

    dependencies = set(cargo.get("dependencies", {}))
    expected_linked = {
        name
        for name, category in assignments.items()
        if category in {"tick_controller", "runtime_kernel"}
    }
    absent_dependencies = sorted(expected_linked - dependencies)
    if absent_dependencies:
        issues.append("osr-sim missing linked dependencies: " + ", ".join(absent_dependencies))

    runtime_evidence = None
    if result_path is not None:
        result = json.loads(result_path.read_text(encoding="utf-8"))
        vehicle = result.get("vehicle_systems", {})
        onboard = result.get("onboard", {})
        runtime_evidence = {
            "result": str(result_path),
            "result_sha256": digest(result_path),
            "vehicle_controller_ticks": int(vehicle.get("controller_ticks", 0)),
            "door_interlock_violations": int(vehicle.get("door_interlock_violations", 0)),
            "onboard_ticks": int(onboard.get("ticks_evaluated", 0)),
        }
        required_vehicle = (
            "door_controller_evaluations",
            "aux_power_controller_ticks",
            "hvac_controller_ticks",
            "lighting_controller_ticks",
            "pis_controller_ticks",
        )
        for field in required_vehicle:
            if int(vehicle.get(field, 0)) <= 0:
                issues.append(f"simulation result has no {field} evidence")
        if runtime_evidence["door_interlock_violations"]:
            issues.append("simulation result contains door interlock violations")

    counts = {
        category: sum(1 for value in assignments.values() if value == category)
        for category in CATEGORIES
    }
    return {
        "schema_version": 1,
        "passed": not issues,
        "issues": issues,
        "inventory_count": len(inventory),
        "classified_count": len(assignments),
        "linked_component_count": len(expected_linked),
        "category_counts": counts,
        "categories": {category: contract[category]["components"] for category in CATEGORIES},
        "deployment_inventory_sha256": digest(DEPLOYMENT),
        "coverage_contract_sha256": digest(CONTRACT),
        "simulator_cargo_sha256": digest(SIM_CARGO),
        "runtime_evidence": runtime_evidence,
        "interpretation": (
            "Complete means every deployable software component has exactly one explicit "
            "simulation treatment. Only tick_controller entries are claimed to execute per "
            "vehicle tick; scenario_model and external_boundary entries remain visible gaps, "
            "not simulated implementations."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, help="optional osr-sim JSON result to verify")
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "engineering/software/simulation-component-coverage.json",
    )
    args = parser.parse_args()
    report = build_report(args.result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"wrote {args.output} ({report['classified_count']}/{report['inventory_count']} "
        f"classified, passed={report['passed']})"
    )
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
