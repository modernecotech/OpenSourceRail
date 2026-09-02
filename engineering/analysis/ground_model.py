#!/usr/bin/env python3
"""Inspect a controlled surveyed-ground-model delivery without inventing data."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sqlite3
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from engineering.analysis import survey_control
except ModuleNotFoundError:  # Direct execution from engineering/analysis.
    import survey_control  # type: ignore[no-redef]


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REQUIREMENTS = REPO_ROOT / "lib/templates/ground-model-processing.toml"


def read_requirements(path: Path = DEFAULT_REQUIREMENTS) -> dict[str, Any]:
    value = tomllib.loads(path.read_text(encoding="utf-8"))
    inputs = list(value.get("input", []))
    keys = [(str(item.get("dataset_id", "")), str(item.get("file_role", ""))) for item in inputs]
    if not inputs or len(keys) != len(set(keys)) or any(not all(key) for key in keys):
        raise ValueError(f"{path}: dataset/file-role pairs must be present and unique")
    return value


def validate_receipt(
    manifest_path: Path,
    evidence_root: Path,
    requirements: dict[str, Any],
) -> tuple[dict[str, list[dict[str, str]]], list[str]]:
    inputs = {str(item["file_role"]): item for item in requirements["input"]}
    expected_pairs = {
        (str(item["dataset_id"]), str(item["file_role"])): item
        for item in requirements["input"]
    }
    required_metadata = tuple(requirements["receipt"]["required_metadata_fields"])
    allowed_statuses = set(requirements["receipt"]["allowed_acceptance_statuses"])
    received: dict[str, list[dict[str, str]]] = {role: [] for role in inputs}
    findings: list[str] = []
    storage_root = evidence_root.resolve()
    with manifest_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required_columns = {"dataset_id", "file_role", "file_path", "sha256", *required_metadata}
        missing_columns = sorted(required_columns - set(reader.fieldnames or []))
        if missing_columns:
            return received, [f"manifest missing columns: {', '.join(missing_columns)}"]
        seen: set[str] = set()
        for number, row in enumerate(reader, start=2):
            dataset_id = row.get("dataset_id", "").strip()
            file_role = row.get("file_role", "").strip()
            path_value = row.get("file_path", "").strip()
            if not file_role and not path_value:
                continue
            specification = expected_pairs.get((dataset_id, file_role))
            if specification is None:
                # The shared receipt also contains control and later design-package roles.
                continue
            label = f"manifest row {number}"
            try:
                relative = survey_control.safe_relative_path(path_value)
            except ValueError as exc:
                findings.append(f"{label}: {exc}")
                continue
            if relative is None:
                findings.append(f"{label}: file_path is required when file_role is set")
                continue
            relative_text = relative.as_posix()
            if relative_text in seen:
                findings.append(f"{label}: duplicate file_path {relative_text}")
                continue
            seen.add(relative_text)
            extensions = tuple(str(item).lower() for item in specification["extensions"])
            if not relative_text.lower().endswith(extensions):
                findings.append(f"{label}: {file_role} has an unsupported file extension")
            digest = row.get("sha256", "").strip().lower()
            if not survey_control.SHA256_RE.fullmatch(digest):
                findings.append(f"{label}: sha256 must contain 64 lowercase hexadecimal characters")
            missing_metadata = [field for field in required_metadata if not row.get(field, "").strip()]
            if missing_metadata:
                findings.append(f"{label}: missing metadata: {', '.join(missing_metadata)}")
            status = row.get("acceptance_status", "").strip()
            if status and status not in allowed_statuses:
                findings.append(f"{label}: unsupported acceptance_status {status!r}")
            source = evidence_root.joinpath(*relative.parts).resolve(strict=False)
            if not source.is_relative_to(storage_root):
                findings.append(f"{label}: received file resolves outside the evidence root")
            elif not source.is_file():
                findings.append(f"{label}: received file is missing from controlled storage")
            elif survey_control.SHA256_RE.fullmatch(digest) and survey_control.sha256(source) != digest:
                findings.append(f"{label}: sha256 does not match received file")
            received[file_role].append({**row, "file_path": relative_text, "sha256": digest})
    return received, findings


def _path(received: dict[str, list[dict[str, str]]], role: str, root: Path) -> Path:
    relative = PurePosixPath(received[role][0]["file_path"])
    return root.joinpath(*relative.parts)


def inspect_geopackage(path: Path) -> tuple[dict[str, Any], list[str]]:
    findings: list[str] = []
    try:
        connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        tables = {
            str(row[0])
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        required = {"gpkg_contents", "gpkg_spatial_ref_sys", "gpkg_geometry_columns"}
        if not required <= tables:
            findings.append("GeoPackage lacks required core tables")
            content_count = 0
        else:
            content_count = int(connection.execute("SELECT COUNT(*) FROM gpkg_contents").fetchone()[0])
            if content_count < 1:
                findings.append("GeoPackage contains no registered content")
            feature_count = int(
                connection.execute(
                    "SELECT COUNT(*) FROM gpkg_contents WHERE data_type='features'"
                ).fetchone()[0]
            )
            if feature_count < 1:
                findings.append("GeoPackage contains no registered feature layers")
            content_srs_ids = [
                int(row[0])
                for row in connection.execute(
                    "SELECT DISTINCT srs_id FROM gpkg_contents WHERE srs_id IS NOT NULL ORDER BY srs_id"
                )
            ]
            if len(content_srs_ids) != 1:
                findings.append("GeoPackage content does not use one registered project SRS")
            elif not connection.execute(
                "SELECT 1 FROM gpkg_spatial_ref_sys WHERE srs_id=?", (content_srs_ids[0],)
            ).fetchone():
                findings.append("GeoPackage content SRS is absent from gpkg_spatial_ref_sys")
        application_id = int(connection.execute("PRAGMA application_id").fetchone()[0])
        connection.close()
    except sqlite3.Error as exc:
        return {}, [f"GeoPackage is unreadable: {exc}"]
    if application_id != 0x47504B47:
        findings.append("SQLite application_id is not GeoPackage")
    return {
        "registered_content_count": content_count,
        "registered_feature_layer_count": feature_count if required <= tables else 0,
        "content_srs_ids": content_srs_ids if required <= tables else [],
        "application_id": application_id,
    }, findings


def inspect_file_signature(path: Path, role: str) -> list[str]:
    with path.open("rb") as handle:
        header = handle.read(16)
    if role in {"terrain_dtm", "orthophoto"} and header[:4] not in {b"II*\x00", b"MM\x00*"}:
        return [f"{role} is not a TIFF file"]
    if role == "registered_point_cloud":
        suffix = path.suffix.lower()
        valid = header.startswith(b"LASF") if suffix in {".las", ".laz"} else header.startswith(b"ASTM-E57")
        if not valid:
            return [f"{role} signature does not match {suffix}"]
    return []


def inspect_checkpoints(path: Path, requirements: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    findings: list[str] = []
    horizontal: list[float] = []
    vertical: list[float] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"point_id", "role", "horizontal_residual_m", "vertical_residual_m"}
        missing = sorted(required - set(reader.fieldnames or []))
        if missing:
            return {}, [f"checkpoint CSV missing columns: {', '.join(missing)}"]
        identifiers: set[str] = set()
        for number, row in enumerate(reader, start=2):
            if row["role"].strip() != "independent-check":
                continue
            identifier = row["point_id"].strip()
            if not identifier or identifier in identifiers:
                findings.append(f"checkpoint row {number}: point_id is empty or duplicated")
                continue
            identifiers.add(identifier)
            try:
                h_value = float(row["horizontal_residual_m"])
                v_value = float(row["vertical_residual_m"])
            except ValueError:
                findings.append(f"checkpoint row {number}: residual is not numeric")
                continue
            if not math.isfinite(h_value) or not math.isfinite(v_value):
                findings.append(f"checkpoint row {number}: residual is not finite")
                continue
            horizontal.append(h_value)
            vertical.append(v_value)
    count = len(horizontal)
    horizontal_rmse = math.sqrt(sum(value * value for value in horizontal) / count) if count else 0.0
    vertical_rmse = math.sqrt(sum(value * value for value in vertical) / count) if count else 0.0
    criteria = requirements["technical_screen"]
    if count < int(criteria["minimum_independent_checkpoints"]):
        findings.append("too few independent checkpoints")
    if horizontal_rmse > float(criteria["maximum_horizontal_rmse_m"]):
        findings.append("horizontal checkpoint RMSE exceeds provisional limit")
    if vertical_rmse > float(criteria["maximum_vertical_rmse_m"]):
        findings.append("vertical checkpoint RMSE exceeds provisional limit")
    return {
        "independent_checkpoint_count": count,
        "horizontal_rmse_m": round(horizontal_rmse, 6),
        "vertical_rmse_m": round(vertical_rmse, 6),
    }, findings


def inspect_json_report(
    path: Path, requirements: dict[str, Any], expected_tool: str
) -> tuple[dict[str, Any], list[str]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"processing report is unreadable: {exc}"]
    required = requirements["processing_report"]["required_fields"]
    missing = sorted(field for field in required if value.get(field) in (None, "", [], {}))
    findings = [f"processing report missing: {', '.join(missing)}"] if missing else []
    if value.get("status") != requirements["processing_report"]["accepted_status"]:
        findings.append("processing report status is not success")
    if value.get("tool") != expected_tool:
        findings.append(f"processing report tool is not {expected_tool}")
    for field in ("source_hashes", "output_hashes"):
        hashes = value.get(field)
        if isinstance(hashes, dict) and any(
            not survey_control.SHA256_RE.fullmatch(str(digest)) for digest in hashes.values()
        ):
            findings.append(f"processing report {field} contains an invalid SHA-256")
    summary = {
        key: value.get(key)
        for key in (
            "status", "tool", "version", "capture_epoch", "coordinate_system",
            "vertical_datum", "uncertainty_model",
        )
    }
    return summary, findings


def inspect_void_register(path: Path) -> list[str]:
    if path.suffix.lower() == ".gpkg":
        _, findings = inspect_geopackage(path)
        return findings
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"area_id", "status", "reason", "design_impact", "owner"}
        missing = sorted(required - set(reader.fieldnames or []))
    return [f"void register missing columns: {', '.join(missing)}"] if missing else []


def inspect_authority_record(
    path: Path,
    manifest_row: dict[str, str],
    requirements: dict[str, Any],
    expected_crs: str | None,
    expected_vertical_datum: str | None,
) -> list[str]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"ground-model acceptance record is unreadable: {exc}"]
    required = requirements["authority_record"]["required_fields"]
    missing = sorted(field for field in required if not str(value.get(field, "")).strip())
    findings = [f"ground-model acceptance record missing: {', '.join(missing)}"] if missing else []
    if value.get("decision") != requirements["authority_record"]["accepted_decision"]:
        findings.append("ground-model acceptance decision is not accepted")
    if manifest_row.get("acceptance_status") != "accepted":
        findings.append("ground-model acceptance manifest row is not accepted")
    if expected_crs and value.get("approved_horizontal_crs") != expected_crs:
        findings.append("ground-model acceptance CRS does not match the technical receipt")
    if expected_vertical_datum and value.get("approved_vertical_datum") != expected_vertical_datum:
        findings.append("ground-model acceptance vertical datum does not match the technical receipt")
    return findings


def build_report(
    city: str,
    manifest_path: Path,
    evidence_root: Path,
    requirements_path: Path = DEFAULT_REQUIREMENTS,
    inspect: bool = False,
) -> dict[str, Any]:
    requirements = read_requirements(requirements_path)
    received, receipt_findings = validate_receipt(manifest_path, evidence_root, requirements)
    technical_roles = [
        str(item["file_role"]) for item in requirements["input"] if item["required_for_technical_screen"]
    ]
    review_roles = [
        str(item["file_role"]) for item in requirements["input"] if item["required_for_authority_review"]
    ]
    missing_technical = [role for role in technical_roles if len(received[role]) != 1]
    duplicates = [role for role in received if len(received[role]) > 1]
    missing_review = [role for role in review_roles if not received[role]]
    unreviewed_technical = [
        role
        for role in technical_roles
        if received[role]
        and received[role][0].get("acceptance_status") not in {"checked", "accepted"}
    ]
    inspection_findings: list[str] = []
    inspection: dict[str, Any] = {}
    accepted_crs: str | None = None
    accepted_vertical_datum: str | None = None
    can_inspect = inspect and not receipt_findings and not missing_technical and not duplicates
    if can_inspect:
        try:
            control = json.loads(
                _path(received, "control_acceptance_report", evidence_root).read_text()
            )
        except (OSError, json.JSONDecodeError) as exc:
            control = {}
            inspection_findings.append(f"control acceptance report is unreadable: {exc}")
        inspection["control_authority_accepted"] = control.get("authority_accepted") is True
        if not inspection["control_authority_accepted"]:
            inspection_findings.append("survey control has not been accepted by the appointed authority")
        if unreviewed_technical:
            inspection_findings.append(
                "technical inputs are not checked or accepted: " + ", ".join(unreviewed_technical)
            )
        coordinate_systems = {
            rows[0]["coordinate_system"] for role, rows in received.items() if role in technical_roles and rows
        }
        vertical_datums = {
            rows[0]["vertical_datum"] for role, rows in received.items() if role in technical_roles and rows
        }
        inspection["coordinate_systems"] = sorted(coordinate_systems)
        inspection["vertical_datums"] = sorted(vertical_datums)
        if len(coordinate_systems) != 1:
            inspection_findings.append("technical inputs do not share one approved coordinate system")
        else:
            accepted_crs = next(iter(coordinate_systems))
        if len(vertical_datums) != 1:
            inspection_findings.append("technical inputs do not share one approved vertical datum")
        else:
            accepted_vertical_datum = next(iter(vertical_datums))
        for role in ("topographic_features", "master_ground_model"):
            summary, findings = inspect_geopackage(_path(received, role, evidence_root))
            inspection[role] = summary
            inspection_findings.extend(f"{role}: {item}" for item in findings)
            epsg_match = re.fullmatch(r"EPSG:(\d+)", accepted_crs or "")
            if epsg_match and summary.get("content_srs_ids") != [int(epsg_match.group(1))]:
                inspection_findings.append(f"{role}: GeoPackage SRS does not match the receipt")
        for role in ("terrain_dtm", "orthophoto", "registered_point_cloud"):
            inspection_findings.extend(
                inspect_file_signature(_path(received, role, evidence_root), role)
            )
        checkpoint_summary, findings = inspect_checkpoints(
            _path(received, "checkpoint_residuals", evidence_root), requirements
        )
        inspection["checkpoints"] = checkpoint_summary
        inspection_findings.extend(findings)
        for role in ("odm_processing_report", "cloudcompare_qa_report"):
            specification = next(item for item in requirements["input"] if item["file_role"] == role)
            summary, findings = inspect_json_report(
                _path(received, role, evidence_root), requirements, specification["expected_tool"]
            )
            inspection[role] = summary
            inspection_findings.extend(f"{role}: {item}" for item in findings)
            if accepted_crs and summary.get("coordinate_system") != accepted_crs:
                inspection_findings.append(f"{role}: coordinate system does not match the receipt")
            if accepted_vertical_datum and summary.get("vertical_datum") != accepted_vertical_datum:
                inspection_findings.append(f"{role}: vertical datum does not match the receipt")
        inspection_findings.extend(
            f"void_register: {item}"
            for item in inspect_void_register(_path(received, "void_register", evidence_root))
        )
    technical_screen_passed = bool(can_inspect and not inspection_findings)
    acceptance_findings = ["ground-model acceptance record not received"]
    if received["ground_model_acceptance_record"] and not receipt_findings:
        acceptance_findings = inspect_authority_record(
            _path(received, "ground_model_acceptance_record", evidence_root),
            received["ground_model_acceptance_record"][0],
            requirements,
            accepted_crs,
            accepted_vertical_datum,
        )
    authority_accepted = bool(
        technical_screen_passed and not missing_review and not acceptance_findings
    )
    if receipt_findings:
        status = "blocked-invalid-receipt"
    elif missing_technical:
        status = "awaiting-ground-model-data"
    elif duplicates:
        status = "blocked-duplicate-ground-model-role"
    elif not inspect:
        status = "ready-for-inspection"
    elif inspection_findings:
        status = "technical-screen-failed"
    elif not authority_accepted:
        status = "technical-screen-passed-awaiting-authority"
    else:
        status = "authority-accepted"
    return {
        "schema_version": "1.0",
        "analysis_id": f"OSR-GROUND-MODEL:{city}",
        "city": city,
        "status": status,
        "report_valid": not receipt_findings,
        "data_received": bool(any(received.values())),
        "receipt_findings": receipt_findings,
        "received_role_counts": {role: len(rows) for role, rows in received.items()},
        "received_files": [
            {"dataset_id": row["dataset_id"], "file_role": role, "file_path": row["file_path"], "sha256": row["sha256"]}
            for role in sorted(received)
            for row in received[role]
        ],
        "missing_technical_roles": missing_technical,
        "duplicate_roles": duplicates,
        "unreviewed_technical_roles": unreviewed_technical,
        "missing_authority_review_roles": missing_review,
        "inspection_requested": inspect,
        "inspection_completed": can_inspect,
        "inspection": inspection,
        "inspection_findings": inspection_findings,
        "technical_screen_criteria": requirements["technical_screen"],
        "technical_screen_passed": technical_screen_passed,
        "authority_record_findings": acceptance_findings,
        "authority_accepted": authority_accepted,
        "requirements_source": survey_control.display_path(requirements_path),
        "requirements_sha256": survey_control.sha256(requirements_path),
        "receipt_manifest_sha256": survey_control.sha256(manifest_path),
        "receipt_validator_sha256": survey_control.sha256(Path(survey_control.__file__)),
        "generator_sha256": survey_control.sha256(Path(__file__)),
        "raw_data_policy": requirements["raw_data_policy"],
        "technical_boundary": requirements["technical_boundary"],
        "acceptance_boundary": requirements["acceptance_boundary"],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# {report['city'].title()} surveyed-ground-model gate",
        "",
        f"- Status: **{report['status']}**",
        f"- Technical inspection completed: **{'yes' if report['inspection_completed'] else 'no'}**",
        f"- Technical screen passed: **{'yes' if report['technical_screen_passed'] else 'no'}**",
        f"- Survey authority accepted: **{'yes' if report['authority_accepted'] else 'no'}**",
        "",
        "> " + report["technical_boundary"],
        "",
        "> " + report["acceptance_boundary"],
        "",
        "## Current gates",
        "",
        f"- Missing technical roles: {', '.join(report['missing_technical_roles']) or 'none'}",
        f"- Duplicate roles: {', '.join(report['duplicate_roles']) or 'none'}",
        f"- Missing authority-review roles: {', '.join(report['missing_authority_review_roles']) or 'none'}",
    ]
    for title, findings in (
        ("Receipt findings", report["receipt_findings"]),
        ("Inspection findings", report["inspection_findings"]),
        ("Authority-record findings", report["authority_record_findings"]),
    ):
        if findings:
            lines.extend([f"- {title}:", *[f"  - {item}" for item in findings]])
    lines.extend(
        [
            "",
            "## Controlled workflow",
            "",
            report["raw_data_policy"],
            "",
            "1. Complete accepted survey control before registering terrain or clouds.",
            "2. Process imagery in OpenDroneMap and registration/comparison in CloudCompare; preserve settings, source/output hashes and QA reports.",
            "3. Build the federated master GeoPackage in the approved horizontal CRS and vertical datum.",
            "4. Add every derivative to the shared receipt with its immutable hash and independent checker.",
            "5. Run inspection, resolve residual/coverage findings, and obtain the controlled authority acceptance record.",
            "",
        ]
    )
    return "\n".join(lines)


def generate(
    city: str,
    manifest_path: Path,
    evidence_root: Path,
    output_dir: Path,
    requirements_path: Path = DEFAULT_REQUIREMENTS,
    inspect: bool = False,
) -> dict[str, Any]:
    report = build_report(
        city,
        manifest_path.resolve(),
        evidence_root.resolve(),
        requirements_path.resolve(),
        inspect,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    survey_control.atomic_json(output_dir / "ground-model-readiness.json", report)
    (output_dir / "ground-model-readiness.md").write_text(render_markdown(report), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--city", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--evidence-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--requirements", type=Path, default=DEFAULT_REQUIREMENTS)
    parser.add_argument("--inspect", action="store_true")
    parser.add_argument("--require-technical-screen", action="store_true")
    args = parser.parse_args()
    report = generate(
        args.city,
        args.manifest,
        args.evidence_root,
        args.output_dir,
        args.requirements,
        args.inspect,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report["report_valid"]:
        return 1
    if args.require_technical_screen and not report["technical_screen_passed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
