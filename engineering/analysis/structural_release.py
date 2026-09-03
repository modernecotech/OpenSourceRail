#!/usr/bin/env python3
"""Gate project per-asset structural analyses and independent release."""

from __future__ import annotations

import argparse
import csv
import json
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from engineering.analysis import route_station_fit, survey_control, surveyed_alignment
except ModuleNotFoundError:
    import route_station_fit  # type: ignore[no-redef]
    import survey_control  # type: ignore[no-redef]
    import surveyed_alignment  # type: ignore[no-redef]

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REQUIREMENTS = REPO_ROOT / "lib/templates/structural-release-processing.toml"


def read_requirements(path: Path = DEFAULT_REQUIREMENTS) -> dict[str, Any]:
    return route_station_fit.read_requirements(path)


def write_placeholder_manifest(path: Path, requirements: dict[str, Any]) -> None:
    route_station_fit.write_placeholder_manifest(path, requirements)


def _path(received: dict[str, list[dict[str, str]]], role: str, root: Path) -> Path:
    relative = PurePosixPath(received[role][0]["file_path"])
    return root.joinpath(*relative.parts)


def inspect_schedule(path: Path, line_ids: set[str], requirements: dict[str, Any]) -> tuple[list[dict[str, str]], list[str]]:
    rules = requirements["asset_schedule"]
    findings: list[str] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = sorted(set(rules["required_columns"]) - set(reader.fieldnames or []))
        if missing:
            return [], [f"structural schedule missing columns: {', '.join(missing)}"]
        rows = list(reader)
    ids: set[str] = set(); covered: set[str] = set()
    for number, row in enumerate(rows, start=2):
        asset_id = row["asset_id"].strip(); line_id = row["line_id"].strip()
        if not asset_id or asset_id in ids: findings.append(f"schedule row {number}: asset_id is empty or duplicated")
        ids.add(asset_id)
        if line_id not in line_ids: findings.append(f"schedule row {number}: unknown line_id")
        else: covered.add(line_id)
        if row["asset_type"] not in rules["allowed_asset_types"]: findings.append(f"schedule row {number}: unsupported asset_type")
        try:
            start, end = float(row["from_station_m"]), float(row["to_station_m"])
            if start < 0 or end <= start: raise ValueError
        except ValueError: findings.append(f"schedule row {number}: invalid chainage range")
        if not all(row[field].strip() for field in ("variant_id", "foundation_ref", "analysis_ids")):
            findings.append(f"schedule row {number}: design references are incomplete")
        if row["status"] != rules["accepted_status"]: findings.append(f"schedule row {number}: status is not checked")
    if covered != line_ids: findings.append("structural schedule does not cover every design line")
    if not rows: findings.append("structural schedule is empty")
    return rows, findings


def inspect_solver(report_path: Path, input_path: Path, requirements: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    value = json.loads(report_path.read_text(encoding="utf-8")); rules = requirements["solver_report"]
    findings = [f"solver report missing {field}" for field in rules["required_fields"] if value.get(field) in (None, "", [], {})]
    if value.get("status") != rules["accepted_status"]: findings.append("solver report status is not passed")
    if value.get("input_sha256") != survey_control.sha256(input_path): findings.append("solver input hash does not match received model")
    if value.get("convergence") is not True: findings.append("solver report does not claim convergence")
    if any(not survey_control.SHA256_RE.fullmatch(str(digest)) for digest in value.get("output_hashes", {}).values()):
        findings.append("solver output hashes are invalid")
    return value, findings


def inspect_verification(path: Path, received: dict[str, list[dict[str, str]]], asset_ids: set[str], requirements: dict[str, Any]) -> list[str]:
    value = json.loads(path.read_text(encoding="utf-8")); rules = requirements["verification_report"]
    findings = [f"structural verification missing {field}" for field in rules["required_fields"] if value.get(field) in (None, "", [], {})]
    if value.get("status") != rules["accepted_status"]: findings.append("structural verification status is not passed")
    expected = {
        "design_basis_sha256": received["structural_design_basis"][0]["sha256"],
        "asset_schedule_sha256": received["structural_asset_schedule"][0]["sha256"],
        "load_case_register_sha256": received["load_case_register"][0]["sha256"],
    }
    for field, digest in expected.items():
        if value.get(field) != digest: findings.append(f"structural verification {field} does not match receipt")
    solver_hashes = {role: received[role][0]["sha256"] for role in ("opensees_model", "opensees_report", "calculix_input", "calculix_report")}
    if value.get("solver_evidence_hashes") != solver_hashes: findings.append("structural verification solver hashes do not match receipt")
    results = {str(item.get("asset_id", "")): item for item in value.get("asset_results", [])}
    if set(results) != asset_ids or len(value.get("asset_results", [])) != len(asset_ids): findings.append("structural verification does not contain exactly one result per scheduled asset")
    for asset_id, result in results.items():
        for field in rules["asset_status_fields"]:
            if result.get(field) != rules["accepted_result_status"]: findings.append(f"{asset_id}: {field} is not passed")
    return findings


def build_report(design_path: Path, manifest_path: Path, evidence_root: Path, requirements_path: Path = DEFAULT_REQUIREMENTS, inspect: bool = False) -> dict[str, Any]:
    city, lines, _ = surveyed_alignment.load_design(design_path); requirements = read_requirements(requirements_path)
    received, receipt_findings = route_station_fit.validate_receipt(manifest_path, evidence_root, requirements)
    authority_role = "structural_acceptance_record"; technical_roles = [role for role in received if role != authority_role]
    missing = [role for role in technical_roles if not received[role]]; duplicates = [role for role, rows in received.items() if len(rows) > 1]
    unreviewed = [role for role in technical_roles if received[role] and received[role][0].get("acceptance_status") not in {"checked", "accepted"}]
    findings: list[str] = []; inspection: dict[str, Any] = {}; can_inspect = inspect and not receipt_findings and not missing and not duplicates
    if can_inspect:
        prerequisite = json.loads(_path(received, "drainage_ground_readiness", evidence_root).read_text())
        if prerequisite.get("authority_accepted") is not True: findings.append("drainage/ground design is not authority accepted")
        if unreviewed: findings.append("technical inputs are not checked or accepted: " + ", ".join(unreviewed))
        rows, schedule_findings = inspect_schedule(_path(received, "structural_asset_schedule", evidence_root), {line["id"] for line in lines}, requirements)
        inspection["scheduled_asset_count"] = len(rows); findings.extend(schedule_findings)
        solver_cases: dict[str, Any] = {}
        for name, report_role, input_role in (("opensees", "opensees_report", "opensees_model"), ("calculix", "calculix_report", "calculix_input")):
            summary, solver_findings = inspect_solver(_path(received, report_role, evidence_root), _path(received, input_role, evidence_root), requirements)
            solver_cases[name] = {key: summary.get(key) for key in ("tool", "version", "model_revision", "load_case_ids")}
            findings.extend(f"{name}: {item}" for item in solver_findings)
        inspection["solvers"] = solver_cases
        findings.extend(inspect_verification(_path(received, "structural_verification_report", evidence_root), received, {row["asset_id"] for row in rows}, requirements))
        independent = json.loads(_path(received, "independent_check_record", evidence_root).read_text()); rules = requirements["independent_check"]
        findings.extend(f"independent check missing {field}" for field in rules["required_fields"] if independent.get(field) in (None, "", {}))
        if independent.get("status") != rules["accepted_status"] or independent.get("comments_closed") is not True: findings.append("independent check is not accepted with comments closed")
        expected_check_hashes = {role: received[role][0]["sha256"] for role in technical_roles if role not in {"independent_check_record", "drainage_ground_readiness"}}
        if independent.get("evidence_hashes") != expected_check_hashes: findings.append("independent-check hashes do not match received evidence")
    technical_passed = bool(can_inspect and not findings)
    evidence_hashes = {role: rows[0]["sha256"] for role, rows in received.items() if role != authority_role and rows}
    authority_findings = ["structural acceptance record not received"]
    if received[authority_role] and not receipt_findings:
        value = json.loads(_path(received, authority_role, evidence_root).read_text()); rules = requirements["authority_record"]
        authority_findings = [f"structural acceptance missing {field}" for field in rules["required_fields"] if value.get(field) in (None, "", {})]
        if value.get("decision") != rules["accepted_decision"]: authority_findings.append("structural acceptance decision is not accepted")
        if received[authority_role][0].get("acceptance_status") != "accepted": authority_findings.append("structural acceptance receipt is not accepted")
        if value.get("approved_evidence_hashes") != evidence_hashes: authority_findings.append("approved hashes do not match structural evidence")
    authority_accepted = bool(technical_passed and not authority_findings)
    if receipt_findings: status = "blocked-invalid-receipt"
    elif missing: status = "awaiting-structural-evidence"
    elif duplicates: status = "blocked-duplicate-role"
    elif not inspect: status = "ready-for-inspection"
    elif findings: status = "technical-screen-failed"
    elif not authority_accepted: status = "technical-screen-passed-awaiting-authority"
    else: status = "authority-accepted"
    return {"schema_version": "1.0", "analysis_id": f"OSR-STRUCTURAL-RELEASE:{city}", "city": city, "status": status,
        "report_valid": not receipt_findings, "line_ids": [line["id"] for line in lines], "receipt_findings": receipt_findings,
        "missing_technical_roles": missing, "duplicate_roles": duplicates, "unreviewed_technical_roles": unreviewed,
        "inspection_requested": inspect, "inspection_completed": can_inspect, "inspection": inspection, "inspection_findings": findings,
        "technical_screen_passed": technical_passed, "authority_record_findings": authority_findings, "authority_accepted": authority_accepted,
        "evidence_hashes": evidence_hashes, "requirements_source": survey_control.display_path(requirements_path),
        "requirements_sha256": survey_control.sha256(requirements_path), "design_source": survey_control.display_path(design_path),
        "design_sha256": survey_control.sha256(design_path), "receipt_manifest_sha256": survey_control.sha256(manifest_path),
        "generator_sha256": survey_control.sha256(Path(__file__)), "technical_boundary": requirements["technical_boundary"], "acceptance_boundary": requirements["acceptance_boundary"]}


def render_markdown(report: dict[str, Any]) -> str:
    lines = [f"# {report['city'].title()} structural-release gate", "", f"- Status: **{report['status']}**",
        f"- Lines: {len(report['line_ids'])}", f"- Technical screen passed: **{'yes' if report['technical_screen_passed'] else 'no'}**",
        f"- Authority accepted: **{'yes' if report['authority_accepted'] else 'no'}**", "", "> " + report["technical_boundary"], "", "> " + report["acceptance_boundary"], "", "## Current gates", "",
        f"- Missing technical roles: {', '.join(report['missing_technical_roles']) or 'none'}", f"- Duplicate roles: {', '.join(report['duplicate_roles']) or 'none'}"]
    for title, values in (("Receipt findings", report["receipt_findings"]), ("Inspection findings", report["inspection_findings"]), ("Authority findings", report["authority_record_findings"])):
        if values: lines.extend([f"- {title}:", *[f"  - {item}" for item in values]])
    lines.extend(["", "## Controlled workflow", "", "1. Accept drainage/ground design and freeze the project structural basis and load combinations.", "2. Schedule every span, pier, abutment, foundation and special structure against line chainage.", "3. Preserve OpenSees global/seismic/soil-spring and CalculiX component input/output hashes and convergence evidence.", "4. Reconcile foundation, wind, seismic, fatigue and bearing/movement results per scheduled asset.", "5. Close independent-check comments and obtain the signed structural release.", ""])
    return "\n".join(lines)


def generate(design_path: Path, manifest_path: Path, evidence_root: Path, output_dir: Path, requirements_path: Path = DEFAULT_REQUIREMENTS, inspect: bool = False) -> dict[str, Any]:
    report = build_report(design_path.resolve(), manifest_path.resolve(), evidence_root.resolve(), requirements_path.resolve(), inspect); output_dir.mkdir(parents=True, exist_ok=True)
    survey_control.atomic_json(output_dir / "structural-release-readiness.json", report); (output_dir / "structural-release-readiness.md").write_text(render_markdown(report), encoding="utf-8"); return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--design", required=True, type=Path); parser.add_argument("--manifest", required=True, type=Path); parser.add_argument("--evidence-root", required=True, type=Path); parser.add_argument("--output-dir", required=True, type=Path); parser.add_argument("--requirements", type=Path, default=DEFAULT_REQUIREMENTS); parser.add_argument("--write-placeholder-manifest", action="store_true"); parser.add_argument("--inspect", action="store_true"); parser.add_argument("--require-technical-screen", action="store_true"); args = parser.parse_args(); requirements = read_requirements(args.requirements)
    if args.write_placeholder_manifest: write_placeholder_manifest(args.manifest, requirements)
    report = generate(args.design, args.manifest, args.evidence_root, args.output_dir, args.requirements, args.inspect); print(json.dumps(report, indent=2, sort_keys=True)); return 1 if not report["report_valid"] or (args.require_technical_screen and not report["technical_screen_passed"]) else 0


if __name__ == "__main__": raise SystemExit(main())
