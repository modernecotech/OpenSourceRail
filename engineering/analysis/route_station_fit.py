#!/usr/bin/env python3
"""Gate controlled route and station fit evidence for a generated city."""

from __future__ import annotations

import argparse
import csv
import json
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from engineering.analysis import survey_control, surveyed_alignment
except ModuleNotFoundError:
    import survey_control  # type: ignore[no-redef]
    import surveyed_alignment  # type: ignore[no-redef]


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REQUIREMENTS = REPO_ROOT / "lib/templates/route-station-fit-processing.toml"
FIELDS = [
    "file_role", "package_revision", "file_path", "sha256", "capture_date",
    "coordinate_system", "vertical_datum", "producer", "checker", "acceptance_status",
]


def read_requirements(path: Path = DEFAULT_REQUIREMENTS) -> dict[str, Any]:
    requirements = tomllib.loads(path.read_text(encoding="utf-8"))
    roles = [str(item.get("file_role", "")) for item in requirements.get("input", [])]
    if not roles or len(roles) != len(set(roles)) or any(not role for role in roles):
        raise ValueError(f"{path}: input file roles must be present and unique")
    return requirements


def write_placeholder_manifest(path: Path, requirements: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        for item in requirements["input"]:
            writer.writerow({"file_role": item["file_role"], "acceptance_status": "not-received"})


def validate_receipt(
    manifest_path: Path, evidence_root: Path, requirements: dict[str, Any]
) -> tuple[dict[str, list[dict[str, str]]], list[str]]:
    specifications = {str(item["file_role"]): item for item in requirements["input"]}
    received: dict[str, list[dict[str, str]]] = {role: [] for role in specifications}
    findings: list[str] = []
    root = evidence_root.resolve()
    metadata = set(requirements["receipt"]["required_metadata_fields"])
    statuses = set(requirements["receipt"]["allowed_acceptance_statuses"])
    with manifest_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing_columns = sorted({"file_role", *metadata} - set(reader.fieldnames or []))
        if missing_columns:
            return received, [f"manifest missing columns: {', '.join(missing_columns)}"]
        for number, row in enumerate(reader, start=2):
            role = row.get("file_role", "").strip()
            path_value = row.get("file_path", "").strip()
            if role in received and not path_value:
                continue
            if role not in received:
                findings.append(f"manifest row {number}: unexpected file role {role!r}")
                continue
            try:
                relative = survey_control.safe_relative_path(path_value)
            except ValueError as exc:
                findings.append(f"manifest row {number}: {exc}")
                continue
            if relative is None:
                findings.append(f"manifest row {number}: file_path is required")
                continue
            if not relative.as_posix().lower().endswith(tuple(specifications[role]["extensions"])):
                findings.append(f"manifest row {number}: {role} has an unsupported extension")
            digest = row.get("sha256", "").strip().lower()
            if not survey_control.SHA256_RE.fullmatch(digest):
                findings.append(f"manifest row {number}: sha256 is invalid")
            absent = sorted(field for field in metadata if not row.get(field, "").strip())
            if absent:
                findings.append(f"manifest row {number}: missing metadata: {', '.join(absent)}")
            if row.get("acceptance_status", "").strip() not in statuses:
                findings.append(f"manifest row {number}: unsupported acceptance_status")
            source = root.joinpath(*relative.parts).resolve(strict=False)
            if not source.is_relative_to(root):
                findings.append(f"manifest row {number}: received file resolves outside the evidence root")
            elif not source.is_file():
                findings.append(f"manifest row {number}: received file is missing from controlled storage")
            elif survey_control.SHA256_RE.fullmatch(digest) and survey_control.sha256(source) != digest:
                findings.append(f"manifest row {number}: sha256 does not match received file")
            received[role].append({**row, "file_path": relative.as_posix(), "sha256": digest})
    return received, findings


def _path(received: dict[str, list[dict[str, str]]], role: str, root: Path) -> Path:
    relative = PurePosixPath(received[role][0]["file_path"])
    return root.joinpath(*relative.parts)


def inspect_issue_register(path: Path, requirements: dict[str, Any], scope_ids: set[str]) -> tuple[dict[str, int], list[str]]:
    findings: list[str] = []
    counts = {"total": 0, "open": 0, "open_high_or_critical": 0}
    rules = requirements["issue_register"]
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = sorted(set(rules["required_columns"]) - set(reader.fieldnames or []))
        if missing:
            return counts, [f"issue register missing columns: {', '.join(missing)}"]
        identifiers: set[str] = set()
        for number, row in enumerate(reader, start=2):
            counts["total"] += 1
            issue_id = row["issue_id"].strip()
            if not issue_id or issue_id in identifiers:
                findings.append(f"issue row {number}: issue_id is empty or duplicated")
            identifiers.add(issue_id)
            if row["scope_type"] not in {"city", "line", "station"}:
                findings.append(f"issue row {number}: unsupported scope_type")
            if row["scope_type"] != "city" and row["scope_id"] not in scope_ids:
                findings.append(f"issue row {number}: unknown scope_id {row['scope_id']!r}")
            severity = row["severity"].strip()
            if severity not in rules["allowed_severities"]:
                findings.append(f"issue row {number}: unsupported severity")
            if not all(row[field].strip() for field in ("domain", "status", "owner", "disposition", "evidence_reference")):
                findings.append(f"issue row {number}: closure metadata is incomplete")
            if row["status"] not in rules["closed_statuses"]:
                counts["open"] += 1
                if severity in {"high", "critical"}:
                    counts["open_high_or_critical"] += 1
    if counts["open_high_or_critical"]:
        findings.append("issue register contains unresolved high or critical issues")
    return counts, findings


def inspect_verification(
    path: Path,
    lines: list[dict[str, Any]],
    stations: list[dict[str, Any]],
    received: dict[str, list[dict[str, str]]],
    requirements: dict[str, Any],
) -> list[str]:
    value = json.loads(path.read_text(encoding="utf-8"))
    rules = requirements["verification_report"]
    findings = [f"verification report missing {field}" for field in rules["required_fields"] if value.get(field) in (None, "", [], {})]
    if value.get("status") != rules["accepted_status"]:
        findings.append("verification report status is not passed")
    technical_roles = [str(item["file_role"]) for item in requirements["input"] if item["category"] != "authority"]
    crs_values = {received[role][0]["coordinate_system"] for role in technical_roles}
    datum_values = {received[role][0]["vertical_datum"] for role in technical_roles}
    if len(crs_values) != 1 or value.get("coordinate_system") not in crs_values:
        findings.append("verification report CRS does not match one common receipt CRS")
    if len(datum_values) != 1 or value.get("vertical_datum") not in datum_values:
        findings.append("verification report vertical datum does not match one common receipt datum")
    prerequisite_roles = [str(item["file_role"]) for item in requirements["input"] if item["category"] == "prerequisite"]
    evidence_roles = [str(item["file_role"]) for item in requirements["input"] if item["category"] == "evidence"]
    expected_prerequisites = {role: received[role][0]["sha256"] for role in prerequisite_roles}
    expected_evidence = {role: received[role][0]["sha256"] for role in evidence_roles}
    if value.get("prerequisite_hashes") != expected_prerequisites:
        findings.append("verification prerequisite hashes do not match the receipt")
    if value.get("evidence_hashes") != expected_evidence:
        findings.append("verification evidence hashes do not match the receipt")
    expected_lines = {str(item["id"]) for item in lines}
    line_results = {str(item.get("line_id", "")): item for item in value.get("line_results", [])}
    if set(line_results) != expected_lines or len(value.get("line_results", [])) != len(expected_lines):
        findings.append("verification report does not contain exactly one result per design line")
    expected_stations = {str(item["id"]): str(item.get("line", "")) for item in stations}
    station_results = {str(item.get("station_id", "")): item for item in value.get("station_results", [])}
    if set(station_results) != set(expected_stations) or len(value.get("station_results", [])) != len(expected_stations):
        findings.append("verification report does not contain exactly one result per design station")
    accepted = rules["accepted_result_status"]
    for line_id, result in line_results.items():
        for field in rules["line_status_fields"]:
            if result.get(field) != accepted:
                findings.append(f"{line_id}: {field} is not resolved")
    for station_id, result in station_results.items():
        if result.get("line_id") != expected_stations.get(station_id):
            findings.append(f"{station_id}: line_id does not match the design")
        for field in rules["station_status_fields"]:
            if result.get(field) != accepted:
                findings.append(f"{station_id}: {field} is not resolved")
    return findings


def build_report(
    design_path: Path,
    manifest_path: Path,
    evidence_root: Path,
    requirements_path: Path = DEFAULT_REQUIREMENTS,
    inspect: bool = False,
) -> dict[str, Any]:
    city, lines, stations = surveyed_alignment.load_design(design_path)
    requirements = read_requirements(requirements_path)
    received, receipt_findings = validate_receipt(manifest_path, evidence_root, requirements)
    authority_role = "route_fit_acceptance_record"
    missing = [role for role, rows in received.items() if not rows and role != authority_role]
    duplicates = [role for role, rows in received.items() if len(rows) > 1]
    unreviewed = [role for role, rows in received.items() if rows and role != authority_role and rows[0].get("acceptance_status") not in {"checked", "accepted"}]
    findings: list[str] = []
    inspection: dict[str, Any] = {}
    can_inspect = inspect and not receipt_findings and not missing and not duplicates
    technical_roles = [role for role in received if role != authority_role]
    crs_values = {received[role][0]["coordinate_system"] for role in technical_roles if received[role]}
    datum_values = {received[role][0]["vertical_datum"] for role in technical_roles if received[role]}
    if can_inspect:
        if unreviewed:
            findings.append("technical inputs are not checked or accepted: " + ", ".join(unreviewed))
        ground = json.loads(_path(received, "ground_model_readiness", evidence_root).read_text())
        alignment = json.loads(_path(received, "surveyed_alignment_readiness", evidence_root).read_text())
        inspection["ground_model_authority_accepted"] = ground.get("authority_accepted") is True
        inspection["surveyed_alignment_authority_accepted"] = alignment.get("authority_accepted") is True
        if not inspection["ground_model_authority_accepted"]:
            findings.append("surveyed ground model is not authority accepted")
        if not inspection["surveyed_alignment_authority_accepted"]:
            findings.append("surveyed alignments are not authority accepted")
        findings.extend(inspect_verification(
            _path(received, "route_fit_verification_report", evidence_root), lines, stations, received, requirements
        ))
        scope_ids = {str(line["id"]) for line in lines} | {str(station["id"]) for station in stations}
        issue_summary, issue_findings = inspect_issue_register(
            _path(received, "route_fit_issue_register", evidence_root), requirements, scope_ids
        )
        inspection["issues"] = issue_summary
        findings.extend(issue_findings)
    technical_passed = bool(can_inspect and not findings)
    authority_findings = ["route-fit acceptance record not received"]
    evidence_hashes = {
        role: received[role][0]["sha256"]
        for role in received
        if role != authority_role and received[role]
    }
    if received[authority_role] and not receipt_findings:
        value = json.loads(_path(received, authority_role, evidence_root).read_text())
        authority_findings = [f"route-fit acceptance record missing {field}" for field in requirements["authority_record"]["required_fields"] if value.get(field) in (None, "", {})]
        if value.get("decision") != requirements["authority_record"]["accepted_decision"]:
            authority_findings.append("route-fit acceptance decision is not accepted")
        if received[authority_role][0].get("acceptance_status") != "accepted":
            authority_findings.append("route-fit acceptance manifest row is not accepted")
        if value.get("approved_evidence_hashes") != evidence_hashes:
            authority_findings.append("approved evidence hashes do not match inspected files")
        if len(crs_values) == 1 and value.get("approved_horizontal_crs") != next(iter(crs_values)):
            authority_findings.append("approved CRS does not match inspected files")
        if len(datum_values) == 1 and value.get("approved_vertical_datum") != next(iter(datum_values)):
            authority_findings.append("approved vertical datum does not match inspected files")
    authority_accepted = bool(technical_passed and not authority_findings)
    if receipt_findings:
        status = "blocked-invalid-receipt"
    elif missing:
        status = "awaiting-route-fit-evidence"
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
        "schema_version": "1.0", "analysis_id": f"OSR-ROUTE-STATION-FIT:{city}", "city": city,
        "status": status, "report_valid": not receipt_findings,
        "line_ids": [str(line["id"]) for line in lines], "station_ids": [str(station["id"]) for station in stations],
        "receipt_findings": receipt_findings, "missing_technical_roles": missing,
        "duplicate_roles": duplicates, "unreviewed_technical_roles": unreviewed,
        "inspection_requested": inspect, "inspection_completed": can_inspect,
        "inspection": inspection, "inspection_findings": findings,
        "technical_screen_passed": technical_passed,
        "authority_record_findings": authority_findings, "authority_accepted": authority_accepted,
        "evidence_hashes": evidence_hashes,
        "requirements_source": survey_control.display_path(requirements_path),
        "requirements_sha256": survey_control.sha256(requirements_path),
        "design_source": survey_control.display_path(design_path), "design_sha256": survey_control.sha256(design_path),
        "receipt_manifest_sha256": survey_control.sha256(manifest_path),
        "generator_sha256": survey_control.sha256(Path(__file__)),
        "controlled_storage_policy": requirements["controlled_storage_policy"],
        "technical_boundary": requirements["technical_boundary"], "acceptance_boundary": requirements["acceptance_boundary"],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# {report['city'].title()} route and station fit gate", "",
        f"- Status: **{report['status']}**", f"- Lines: {len(report['line_ids'])}",
        f"- Stations: {len(report['station_ids'])}",
        f"- Technical screen passed: **{'yes' if report['technical_screen_passed'] else 'no'}**",
        f"- Coordinated authority acceptance: **{'yes' if report['authority_accepted'] else 'no'}**", "",
        "> " + report["technical_boundary"], "", "> " + report["acceptance_boundary"], "", "## Current gates", "",
        f"- Missing technical roles: {', '.join(report['missing_technical_roles']) or 'none'}",
        f"- Duplicate roles: {', '.join(report['duplicate_roles']) or 'none'}",
    ]
    for title, values in (("Receipt findings", report["receipt_findings"]), ("Inspection findings", report["inspection_findings"]), ("Authority findings", report["authority_record_findings"])):
        if values:
            lines.extend([f"- {title}:", *[f"  - {item}" for item in values]])
    lines.extend(["", "## Controlled workflow", "", report["controlled_storage_policy"], "",
        "1. Accept survey control, the ground model and every surveyed alignment.",
        "2. Register checked utility, land, flood, station-access, yard/intercity, road, logistics and possession evidence.",
        "3. Reconcile exactly one resolved result for every current line and station, with source hashes.",
        "4. Close or formally transfer all high/critical issues in the controlled issue register.",
        "5. Obtain the coordinated authority acceptance record against the immutable evidence hashes.", ""])
    return "\n".join(lines)


def generate(design_path: Path, manifest_path: Path, evidence_root: Path, output_dir: Path, requirements_path: Path = DEFAULT_REQUIREMENTS, inspect: bool = False) -> dict[str, Any]:
    report = build_report(design_path.resolve(), manifest_path.resolve(), evidence_root.resolve(), requirements_path.resolve(), inspect)
    output_dir.mkdir(parents=True, exist_ok=True)
    survey_control.atomic_json(output_dir / "route-station-fit-readiness.json", report)
    (output_dir / "route-station-fit-readiness.md").write_text(render_markdown(report), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--evidence-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--requirements", type=Path, default=DEFAULT_REQUIREMENTS)
    parser.add_argument("--write-placeholder-manifest", action="store_true")
    parser.add_argument("--inspect", action="store_true")
    parser.add_argument("--require-technical-screen", action="store_true")
    args = parser.parse_args()
    requirements = read_requirements(args.requirements)
    if args.write_placeholder_manifest:
        write_placeholder_manifest(args.manifest, requirements)
    report = generate(args.design, args.manifest, args.evidence_root, args.output_dir, args.requirements, args.inspect)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if not report["report_valid"] or (args.require_technical_screen and not report["technical_screen_passed"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
