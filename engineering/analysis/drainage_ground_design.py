#!/usr/bin/env python3
"""Replay and gate deployment drainage and ground-design evidence."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import tempfile
from importlib.metadata import version
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from engineering.analysis import route_station_fit, survey_control, surveyed_alignment
except ModuleNotFoundError:
    import route_station_fit  # type: ignore[no-redef]
    import survey_control  # type: ignore[no-redef]
    import surveyed_alignment  # type: ignore[no-redef]

from osr_mech.civil.foundation import foundation_catalog, foundation_type, ground_improvement_type


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REQUIREMENTS = REPO_ROOT / "lib/templates/drainage-ground-design-processing.toml"


def read_requirements(path: Path = DEFAULT_REQUIREMENTS) -> dict[str, Any]:
    return route_station_fit.read_requirements(path)


def write_placeholder_manifest(path: Path, requirements: dict[str, Any]) -> None:
    route_station_fit.write_placeholder_manifest(path, requirements)


def _path(received: dict[str, list[dict[str, str]]], role: str, root: Path) -> Path:
    relative = PurePosixPath(received[role][0]["file_path"])
    return root.joinpath(*relative.parts)


def replay_swmm(path: Path) -> dict[str, Any]:
    from pyswmm import Simulation

    with tempfile.TemporaryDirectory(prefix="osr-project-swmm-") as temporary:
        replay = Path(temporary) / path.name
        shutil.copy2(path, replay)
        with Simulation(str(replay)) as simulation:
            steps = sum(1 for _ in simulation)
            runoff = float(simulation.runoff_error)
            routing = float(simulation.flow_routing_error)
    return {
        "tool": "EPA SWMM via PySWMM", "version": version("pyswmm"), "step_count": steps,
        "runoff_error_percent": runoff, "routing_error_percent": routing,
    }


def inspect_swmm(
    report_path: Path, model_path: Path, hydrology_path: Path, ground_path: Path,
    requirements: dict[str, Any], receipt_row: dict[str, str],
) -> tuple[dict[str, Any], list[str]]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    rules = requirements["swmm"]
    findings = [f"SWMM report missing {field}" for field in rules["required_report_fields"] if report.get(field) in (None, "", [], {})]
    if report.get("status") != rules["accepted_status"]:
        findings.append("SWMM report status is not passed")
    hashes = {
        "input_sha256": survey_control.sha256(model_path),
        "hydrology_basis_sha256": survey_control.sha256(hydrology_path),
        "ground_model_sha256": survey_control.sha256(ground_path),
    }
    for field, digest in hashes.items():
        if report.get(field) != digest:
            findings.append(f"SWMM report {field} does not match received evidence")
    if report.get("coordinate_system") != receipt_row["coordinate_system"] or report.get("vertical_datum") != receipt_row["vertical_datum"]:
        findings.append("SWMM report CRS or vertical datum does not match receipt")
    replay = replay_swmm(model_path)
    if replay["step_count"] <= 0:
        findings.append("SWMM replay produced no routing steps")
    if abs(replay["runoff_error_percent"]) > float(rules["maximum_absolute_runoff_error_percent"]):
        findings.append("SWMM replay runoff continuity error exceeds limit")
    if abs(replay["routing_error_percent"]) > float(rules["maximum_absolute_routing_error_percent"]):
        findings.append("SWMM replay routing continuity error exceeds limit")
    for field in ("step_count", "runoff_error_percent", "routing_error_percent"):
        if abs(float(report.get(field, -999999)) - float(replay[field])) > 1e-6:
            findings.append(f"SWMM report {field} does not match deterministic replay")
    return replay, findings


def inspect_foundation_schedule(
    path: Path, lines: list[dict[str, Any]], stations: list[dict[str, Any]], requirements: dict[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    findings: list[str] = []
    rules = requirements["foundation_schedule"]
    known_lines = {str(line["id"]) for line in lines}
    known_stations = {str(station["id"]) for station in stations}
    covered_lines: set[str] = set()
    covered_stations: set[str] = set()
    identifiers: set[str] = set()
    foundation_ids = {str(item["id"]) for item in foundation_catalog()["foundation_types"]}
    improvement_ids = {str(item["id"]) for item in foundation_catalog()["ground_improvement_types"]}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = sorted(set(rules["required_columns"]) - set(reader.fieldnames or []))
        if missing:
            return {}, [f"foundation schedule missing columns: {', '.join(missing)}"]
        rows = list(reader)
    for number, row in enumerate(rows, start=2):
        support_id = row["support_id"].strip()
        if not support_id or support_id in identifiers:
            findings.append(f"foundation row {number}: support_id is empty or duplicated")
        identifiers.add(support_id)
        scope_type, scope_id = row["scope_type"], row["scope_id"]
        if scope_type == "line" and scope_id in known_lines:
            covered_lines.add(scope_id)
        elif scope_type == "station" and scope_id in known_stations:
            covered_stations.add(scope_id)
        else:
            findings.append(f"foundation row {number}: invalid scope")
        kind, system_id = row["system_kind"], row["system_id"]
        if kind == "foundation" and system_id in foundation_ids:
            selected = foundation_type(system_id)
            if selected["project_length_required"] and float(row["actual_length_m"] or 0) <= 0:
                findings.append(f"foundation row {number}: deep foundation lacks actual length")
        elif kind == "ground-improvement" and system_id in improvement_ids:
            ground_improvement_type(system_id)
        else:
            findings.append(f"foundation row {number}: unknown system kind/id")
        for field in ("actual_element_count", "design_quantity", "design_capacity", "predicted_settlement_mm"):
            try:
                if float(row[field]) < 0:
                    raise ValueError
            except ValueError:
                findings.append(f"foundation row {number}: {field} is not non-negative numeric")
        if not row["zone_id"].strip() or not row["design_unit"].strip() or not row["verification_method"].strip():
            findings.append(f"foundation row {number}: design metadata is incomplete")
        if row["status"] != rules["accepted_status"]:
            findings.append(f"foundation row {number}: status is not checked")
    if covered_lines != known_lines:
        findings.append("foundation schedule does not cover every design line")
    if covered_stations != known_stations:
        findings.append("foundation schedule does not cover every design station")
    return {"row_count": len(rows), "covered_line_count": len(covered_lines), "covered_station_count": len(covered_stations)}, findings


def inspect_ground_report(
    path: Path, geo_path: Path, schedule_path: Path, lines: list[dict[str, Any]], stations: list[dict[str, Any]], requirements: dict[str, Any]
) -> list[str]:
    report = json.loads(path.read_text(encoding="utf-8"))
    rules = requirements["ground_design"]
    findings = [f"ground-design report missing {field}" for field in rules["required_report_fields"] if report.get(field) in (None, "", [], {})]
    if report.get("status") != rules["accepted_status"]:
        findings.append("ground-design report status is not passed")
    if report.get("geotechnical_model_sha256") != survey_control.sha256(geo_path) or report.get("foundation_schedule_sha256") != survey_control.sha256(schedule_path):
        findings.append("ground-design source hashes do not match received evidence")
    accepted = rules["accepted_result_status"]
    expected_lines = {str(line["id"]) for line in lines}
    expected_stations = {str(station["id"]) for station in stations}
    line_results = {str(item.get("line_id", "")): item for item in report.get("line_results", [])}
    station_results = {str(item.get("station_id", "")): item for item in report.get("station_results", [])}
    if set(line_results) != expected_lines or len(report.get("line_results", [])) != len(expected_lines):
        findings.append("ground-design report does not contain exactly one result per line")
    if set(station_results) != expected_stations or len(report.get("station_results", [])) != len(expected_stations):
        findings.append("ground-design report does not contain exactly one result per station")
    for scope, result in [*line_results.items(), *station_results.items()]:
        if result.get("drainage_status") != accepted or result.get("ground_status") != accepted:
            findings.append(f"{scope}: drainage/ground result is not sized-and-checked")
    return findings


def build_report(design_path: Path, manifest_path: Path, evidence_root: Path, requirements_path: Path = DEFAULT_REQUIREMENTS, inspect: bool = False) -> dict[str, Any]:
    city, lines, stations = surveyed_alignment.load_design(design_path)
    requirements = read_requirements(requirements_path)
    received, receipt_findings = route_station_fit.validate_receipt(manifest_path, evidence_root, requirements)
    authority_role = "drainage_ground_acceptance_record"
    base_roles = [str(item["file_role"]) for item in requirements["input"] if item["category"] not in {"authority", "conditional"}]
    missing = [role for role in base_roles if not received[role]]
    duplicates = [role for role, rows in received.items() if len(rows) > 1]
    unreviewed = [role for role in base_roles if received[role] and received[role][0].get("acceptance_status") not in {"checked", "accepted"}]
    findings: list[str] = []
    inspection: dict[str, Any] = {}
    can_inspect = inspect and not receipt_findings and not missing and not duplicates
    conditional_required = False
    crs_values = {received[role][0]["coordinate_system"] for role in base_roles if received[role]}
    datum_values = {received[role][0]["vertical_datum"] for role in base_roles if received[role]}
    if can_inspect:
        if len(crs_values) != 1 or len(datum_values) != 1:
            findings.append("technical inputs do not share one CRS and vertical datum")
        for role in ("ground_model_readiness", "route_station_fit_readiness"):
            prerequisite = json.loads(_path(received, role, evidence_root).read_text())
            if prerequisite.get("authority_accepted") is not True:
                findings.append(f"{role} is not authority accepted")
        if unreviewed:
            findings.append("technical inputs are not checked or accepted: " + ", ".join(unreviewed))
        swmm, swmm_findings = inspect_swmm(
            _path(received, "swmm_processing_report", evidence_root), _path(received, "swmm_model", evidence_root),
            _path(received, "accepted_hydrology_basis", evidence_root), _path(received, "ground_model_readiness", evidence_root),
            requirements, received["swmm_model"][0],
        )
        inspection["swmm_replay"] = swmm
        findings.extend(swmm_findings)
        schedule, schedule_findings = inspect_foundation_schedule(
            _path(received, "foundation_ground_schedule", evidence_root), lines, stations, requirements
        )
        inspection["foundation_schedule"] = schedule
        findings.extend(schedule_findings)
        findings.extend(inspect_ground_report(
            _path(received, "ground_design_verification_report", evidence_root),
            _path(received, "geotechnical_ground_model", evidence_root),
            _path(received, "foundation_ground_schedule", evidence_root), lines, stations, requirements,
        ))
        decision = json.loads(_path(received, "groundwater_coupling_decision", evidence_root).read_text())
        for field in requirements["groundwater_decision"]["required_fields"]:
            if decision.get(field) in (None, "", []):
                findings.append(f"groundwater decision missing {field}")
        conditional_required = decision.get("opengeosys_required") is True
        if conditional_required:
            for role in ("opengeosys_project", "opengeosys_processing_report"):
                if len(received[role]) != 1:
                    findings.append(f"{role} is required by the groundwater decision")
            if all(received[role] for role in ("opengeosys_project", "opengeosys_processing_report")):
                ogs = json.loads(_path(received, "opengeosys_processing_report", evidence_root).read_text())
                if ogs.get("status") != "passed" or ogs.get("project_sha256") != received["opengeosys_project"][0]["sha256"]:
                    findings.append("OpenGeoSys report did not pass or does not match the project")
    technical_passed = bool(can_inspect and not findings)
    evidence_hashes = {role: rows[0]["sha256"] for role, rows in received.items() if role != authority_role and rows}
    authority_findings = ["drainage/ground acceptance record not received"]
    if received[authority_role] and not receipt_findings:
        value = json.loads(_path(received, authority_role, evidence_root).read_text())
        authority_findings = [f"acceptance record missing {field}" for field in requirements["authority_record"]["required_fields"] if value.get(field) in (None, "", {})]
        if value.get("decision") != requirements["authority_record"]["accepted_decision"]:
            authority_findings.append("acceptance decision is not accepted")
        if received[authority_role][0].get("acceptance_status") != "accepted":
            authority_findings.append("acceptance manifest row is not accepted")
        if value.get("approved_evidence_hashes") != evidence_hashes:
            authority_findings.append("approved hashes do not match received evidence")
        if len(crs_values) == 1 and value.get("approved_horizontal_crs") != next(iter(crs_values)):
            authority_findings.append("approved CRS does not match inspected evidence")
        if len(datum_values) == 1 and value.get("approved_vertical_datum") != next(iter(datum_values)):
            authority_findings.append("approved vertical datum does not match inspected evidence")
    authority_accepted = bool(technical_passed and not authority_findings)
    if receipt_findings:
        status = "blocked-invalid-receipt"
    elif missing:
        status = "awaiting-drainage-ground-evidence"
    elif duplicates:
        status = "blocked-duplicate-role"
    elif not inspect:
        status = "ready-for-inspection"
    elif findings:
        status = "technical-screen-failed"
    elif not authority_accepted:
        status = "technical-screen-passed-awaiting-authority"
    else:
        status = "authority-accepted"
    return {
        "schema_version": "1.0", "analysis_id": f"OSR-DRAINAGE-GROUND:{city}", "city": city,
        "status": status, "report_valid": not receipt_findings, "line_ids": [line["id"] for line in lines],
        "station_ids": [station["id"] for station in stations], "receipt_findings": receipt_findings,
        "missing_technical_roles": missing, "duplicate_roles": duplicates, "unreviewed_technical_roles": unreviewed,
        "inspection_requested": inspect, "inspection_completed": can_inspect, "inspection": inspection,
        "inspection_findings": findings, "opengeosys_required": conditional_required,
        "technical_screen_passed": technical_passed, "authority_record_findings": authority_findings,
        "authority_accepted": authority_accepted, "evidence_hashes": evidence_hashes,
        "requirements_source": survey_control.display_path(requirements_path), "requirements_sha256": survey_control.sha256(requirements_path),
        "design_source": survey_control.display_path(design_path), "design_sha256": survey_control.sha256(design_path),
        "receipt_manifest_sha256": survey_control.sha256(manifest_path), "generator_sha256": survey_control.sha256(Path(__file__)),
        "technical_boundary": requirements["technical_boundary"], "acceptance_boundary": requirements["acceptance_boundary"],
        "controlled_storage_policy": requirements["controlled_storage_policy"],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [f"# {report['city'].title()} drainage and ground-design gate", "",
        f"- Status: **{report['status']}**", f"- Lines/stations: {len(report['line_ids'])} / {len(report['station_ids'])}",
        f"- SWMM/ground technical screen passed: **{'yes' if report['technical_screen_passed'] else 'no'}**",
        f"- OpenGeoSys required by received decision: **{'yes' if report['opengeosys_required'] else 'no'}**",
        f"- Authority accepted: **{'yes' if report['authority_accepted'] else 'no'}**", "",
        "> " + report["technical_boundary"], "", "> " + report["acceptance_boundary"], "", "## Current gates", "",
        f"- Missing technical roles: {', '.join(report['missing_technical_roles']) or 'none'}",
        f"- Duplicate roles: {', '.join(report['duplicate_roles']) or 'none'}"]
    for title, values in (("Receipt findings", report["receipt_findings"]), ("Inspection findings", report["inspection_findings"]), ("Authority findings", report["authority_record_findings"])):
        if values:
            lines.extend([f"- {title}:", *[f"  - {item}" for item in values]])
    lines.extend(["", "## Controlled workflow", "", report["controlled_storage_policy"], "",
        "1. Accept the ground model, route fit, hydrology basis and geotechnical model.",
        "2. Run the project SWMM model; retain its input, report, source hashes and continuity results.",
        "3. Size a checked catalogue foundation or ground-treatment system for every line and station scope.",
        "4. Record whether groundwater/coupled analysis is warranted; require OpenGeoSys evidence only when the reviewed triggers say yes.",
        "5. Close residual risks and obtain the signed drainage/geotechnical acceptance record.", ""])
    return "\n".join(lines)


def generate(design_path: Path, manifest_path: Path, evidence_root: Path, output_dir: Path, requirements_path: Path = DEFAULT_REQUIREMENTS, inspect: bool = False) -> dict[str, Any]:
    report = build_report(design_path.resolve(), manifest_path.resolve(), evidence_root.resolve(), requirements_path.resolve(), inspect)
    output_dir.mkdir(parents=True, exist_ok=True)
    survey_control.atomic_json(output_dir / "drainage-ground-readiness.json", report)
    (output_dir / "drainage-ground-readiness.md").write_text(render_markdown(report), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", required=True, type=Path); parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--evidence-root", required=True, type=Path); parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--requirements", type=Path, default=DEFAULT_REQUIREMENTS)
    parser.add_argument("--write-placeholder-manifest", action="store_true"); parser.add_argument("--inspect", action="store_true")
    parser.add_argument("--require-technical-screen", action="store_true")
    args = parser.parse_args(); requirements = read_requirements(args.requirements)
    if args.write_placeholder_manifest: write_placeholder_manifest(args.manifest, requirements)
    report = generate(args.design, args.manifest, args.evidence_root, args.output_dir, args.requirements, args.inspect)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if not report["report_valid"] or (args.require_technical_screen and not report["technical_screen_passed"]) else 0


if __name__ == "__main__": raise SystemExit(main())
