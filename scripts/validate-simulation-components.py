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
    "infrastructure_tick_controller",
    "backend_stream_processor",
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
        if category
        in {
            "tick_controller",
            "runtime_kernel",
            "infrastructure_tick_controller",
            "backend_stream_processor",
        }
    }
    absent_dependencies = sorted(expected_linked - dependencies)
    if absent_dependencies:
        issues.append("osr-sim missing linked dependencies: " + ", ".join(absent_dependencies))

    runtime_evidence = None
    if result_path is not None:
        result = json.loads(result_path.read_text(encoding="utf-8"))
        vehicle = result.get("vehicle_systems", {})
        onboard = result.get("onboard", {})
        embedded = result.get("embedded", {})
        infrastructure = result.get("infrastructure_systems", {})
        stations = infrastructure.get("stations", {})
        wayside = infrastructure.get("wayside", {})
        backend = result.get("backend_systems", {})
        time_sync = result.get("time_sync", {})
        habd = result.get("habd_systems", {})
        runtime_evidence = {
            "result": str(result_path),
            "result_sha256": digest(result_path),
            "vehicle_controller_ticks": int(vehicle.get("controller_ticks", 0)),
            "door_interlock_violations": int(vehicle.get("door_interlock_violations", 0)),
            "onboard_ticks": int(onboard.get("ticks_evaluated", 0)),
            "embedded_controller_ticks": int(embedded.get("controller_ticks", 0)),
            "event_records_written": int(embedded.get("event_records_written", 0)),
            "cbm_samples": int(embedded.get("cbm_samples", 0)),
            "t2g_transmissions": int(embedded.get("t2g_transmissions", 0)),
            "t2g_payloads_dropped": int(embedded.get("t2g_payloads_dropped", 0)),
            "tcms_departure_inhibit_ticks": int(
                embedded.get("tcms_departure_inhibit_ticks", 0)
            ),
            "tcms_travel_hold_ticks": int(embedded.get("tcms_travel_hold_ticks", 0)),
            "station_controller_ticks": int(stations.get("controller_ticks", 0)),
            "psd_panel_evaluations": int(stations.get("psd_panel_evaluations", 0)),
            "wayside_detector_ticks": int(wayside.get("detector_ticks", 0)),
            "cbm_backend_samples_received": int(backend.get("cbm_samples_received", 0)),
            "historian_samples_ingested": int(backend.get("historian_samples_ingested", 0)),
            "analytics_metrics_evaluated": int(backend.get("analytics_metrics_evaluated", 0)),
            "ptp_controller_ticks": int(time_sync.get("controller_ticks", 0)),
            "ptp_locked_ticks": int(time_sync.get("locked_ticks", 0)),
            "habd_detector_count": int(habd.get("detector_count", 0)),
            "habd_passages_evaluated": int(habd.get("passages_evaluated", 0)),
            "habd_warning_passages": int(habd.get("warning_passages", 0)),
            "habd_speed_restriction_ticks": int(
                habd.get("speed_restriction_ticks", 0)
            ),
            "habd_active_speed_restrictions": len(
                habd.get("active_speed_restrictions", [])
            ),
            "habd_active_stop_orders": len(habd.get("active_stop_orders", [])),
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
        for field in (
            "embedded_controller_ticks",
            "event_records_written",
            "cbm_samples",
            "t2g_transmissions",
            "station_controller_ticks",
            "psd_panel_evaluations",
            "wayside_detector_ticks",
            "cbm_backend_samples_received",
            "historian_samples_ingested",
            "analytics_metrics_evaluated",
            "ptp_controller_ticks",
            "ptp_locked_ticks",
            "habd_detector_count",
            "habd_passages_evaluated",
        ):
            if runtime_evidence[field] <= 0:
                issues.append(f"simulation result has no {field} evidence")
        if runtime_evidence["habd_active_stop_orders"]:
            issues.append("nominal simulation result contains active HABD stop orders")
        if runtime_evidence["habd_warning_passages"]:
            issues.append("nominal simulation result contains HABD warning passages")
        if runtime_evidence["habd_active_speed_restrictions"]:
            issues.append("nominal simulation result contains active HABD speed restrictions")

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
            "simulation treatment. Controllers and stream processors execute on their declared "
            "vehicle, infrastructure, or backend cadence; scenario_model and external_boundary "
            "entries remain visible gaps, "
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
