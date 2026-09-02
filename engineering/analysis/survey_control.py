#!/usr/bin/env python3
"""Validate and, when possible, process a controlled GNSS receipt with RTKLIB.

Raw observations stay in the supplied evidence root. The generated summary is
safe to track because it records relative references and hashes, not raw data.
Automated processing never substitutes for acceptance by a survey authority.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import tomllib
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REQUIREMENTS = REPO_ROOT / "lib/templates/survey-control-processing.toml"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return path.name


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def safe_relative_path(value: str) -> PurePosixPath | None:
    """Return a normalized controlled-storage path, rejecting traversal/absolute paths."""
    value = value.strip().replace("\\", "/")
    if not value:
        return None
    candidate = PurePosixPath(value)
    if candidate.is_absolute() or any(part in ("", ".", "..") for part in candidate.parts):
        raise ValueError("file_path must be a normalized path relative to the evidence root")
    return candidate


def read_requirements(path: Path = DEFAULT_REQUIREMENTS) -> dict[str, Any]:
    value = tomllib.loads(path.read_text(encoding="utf-8"))
    roles = list(value.get("file_role", []))
    role_ids = [str(role.get("id", "")) for role in roles]
    if not roles or len(role_ids) != len(set(role_ids)) or any(not role for role in role_ids):
        raise ValueError(f"{path}: file roles must be present and unique")
    return value


def extension_supported(path: str, role: dict[str, Any]) -> bool:
    lowered = path.lower()
    extensions = tuple(str(item).lower() for item in role.get("extensions", []))
    if extensions and lowered.endswith(extensions):
        return True
    short_types = "".join(str(item).lower() for item in role.get("rinex_short_type_letters", []))
    return bool(short_types and re.search(rf"\.\d{{2}}[{re.escape(short_types)}]$", lowered))


def validate_receipt(
    manifest_path: Path,
    evidence_root: Path,
    requirements: dict[str, Any],
) -> tuple[dict[str, list[dict[str, str]]], list[str]]:
    """Validate SUR-CTRL rows and their immutable file receipts."""
    roles = {str(role["id"]): role for role in requirements["file_role"]}
    required_metadata = tuple(requirements["receipt"]["required_metadata_fields"])
    allowed_statuses = set(requirements["receipt"]["allowed_acceptance_statuses"])
    received: dict[str, list[dict[str, str]]] = {role: [] for role in roles}
    findings: list[str] = []
    with manifest_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required_columns = {"dataset_id", "file_role", "file_path", "sha256", *required_metadata}
        missing_columns = sorted(required_columns - set(reader.fieldnames or []))
        if missing_columns:
            return received, [f"manifest missing columns: {', '.join(missing_columns)}"]
        seen_paths: set[str] = set()
        for number, row in enumerate(reader, start=2):
            if row.get("dataset_id", "").strip() != requirements["dataset_id"]:
                continue
            path_value = row.get("file_path", "").strip()
            role = row.get("file_role", "").strip()
            # A generated not-received placeholder is deliberately not an error.
            if not path_value and not role:
                continue
            label = f"manifest row {number}"
            if role not in roles:
                findings.append(f"{label}: unknown file_role {role!r}")
                continue
            try:
                relative = safe_relative_path(path_value)
            except ValueError as exc:
                findings.append(f"{label}: {exc}")
                continue
            if relative is None:
                findings.append(f"{label}: file_path is required when file_role is set")
                continue
            relative_text = relative.as_posix()
            if relative_text in seen_paths:
                findings.append(f"{label}: duplicate file_path {relative_text}")
                continue
            seen_paths.add(relative_text)
            if not extension_supported(relative_text, roles[role]):
                findings.append(f"{label}: {role} has an unsupported file extension")
            digest = row.get("sha256", "").strip().lower()
            if not SHA256_RE.fullmatch(digest):
                findings.append(f"{label}: sha256 must contain 64 lowercase hexadecimal characters")
            missing_metadata = [field for field in required_metadata if not row.get(field, "").strip()]
            if missing_metadata:
                findings.append(f"{label}: missing metadata: {', '.join(missing_metadata)}")
            status = row.get("acceptance_status", "").strip()
            if status and status not in allowed_statuses:
                findings.append(f"{label}: unsupported acceptance_status {status!r}")
            storage_root = evidence_root.resolve()
            source = evidence_root.joinpath(*relative.parts).resolve(strict=False)
            if not source.is_relative_to(storage_root):
                findings.append(f"{label}: received file resolves outside the evidence root")
            elif not source.is_file():
                findings.append(f"{label}: received file is missing from controlled storage")
            elif SHA256_RE.fullmatch(digest) and sha256(source) != digest:
                findings.append(f"{label}: sha256 does not match received file")
            received[role].append({**row, "file_path": relative_text, "sha256": digest})
    return received, findings


def parse_rtklib_solution(path: Path) -> dict[str, Any]:
    """Parse RTKLIB's documented Q field from position-solution data rows."""
    quality = Counter()
    malformed = 0
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("%") or line.startswith("#"):
            continue
        fields = line.split()
        if len(fields) < 7:
            malformed += 1
            continue
        try:
            code = int(fields[5])
        except ValueError:
            malformed += 1
            continue
        quality[code] += 1
    epochs = sum(quality.values())
    return {
        "epoch_count": epochs,
        "fixed_epoch_count": quality[1],
        "float_epoch_count": quality[2],
        "fixed_fraction": round(quality[1] / epochs, 6) if epochs else 0.0,
        "quality_code_counts": {str(key): quality[key] for key in sorted(quality)},
        "malformed_data_rows": malformed,
    }


def validate_rtklib_configuration(
    path: Path, requirements: dict[str, Any]
) -> tuple[dict[str, str], list[str]]:
    values: dict[str, str] = {}
    findings: list[str] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        content = raw.split("#", 1)[0].strip()
        if not content:
            continue
        if "=" not in content:
            findings.append(f"configuration line {number}: expected key=value")
            continue
        key, value = (item.strip() for item in content.split("=", 1))
        if not key or key in values:
            findings.append(f"configuration line {number}: key is empty or duplicated")
            continue
        values[key] = value
    required = requirements["rtklib_configuration"]["required_values"]
    for key, expected in required.items():
        if values.get(key) != expected:
            findings.append(f"configuration {key} must equal {expected!r}")
    if requirements["rtklib_configuration"]["forbid_external_file_options"]:
        populated = sorted(key for key, value in values.items() if key.startswith("file-") and value)
        if populated:
            findings.append(
                "configuration contains external file options outside the receipt: "
                + ", ".join(populated)
            )
    return {key: values.get(key, "") for key in required}, findings


def authority_record_valid(
    records: list[dict[str, str]], evidence_root: Path, requirements: dict[str, Any]
) -> tuple[bool, list[str]]:
    if len(records) != 1:
        return False, ["exactly one authority acceptance record is required"]
    path = evidence_root.joinpath(*PurePosixPath(records[0]["file_path"]).parts)
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, [f"authority acceptance record is unreadable: {exc}"]
    required = set(requirements["authority_record"]["required_fields"])
    missing = sorted(field for field in required if not str(record.get(field, "")).strip())
    findings = [f"authority acceptance record missing: {', '.join(missing)}"] if missing else []
    if record.get("decision") != requirements["authority_record"]["accepted_decision"]:
        findings.append("authority acceptance decision is not accepted")
    if records[0].get("acceptance_status") != "accepted":
        findings.append("authority acceptance manifest row is not accepted")
    return not findings, findings


def _one_path(received: dict[str, list[dict[str, str]]], role: str, root: Path) -> Path:
    relative = PurePosixPath(received[role][0]["file_path"])
    return root.joinpath(*relative.parts)


def run_rtklib(
    received: dict[str, list[dict[str, str]]],
    evidence_root: Path,
    run_dir: Path,
    solver: Path,
    maximum_runtime_seconds: int,
) -> dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=True)
    solution = run_dir / "control-solution.pos"
    log_path = run_dir / "rnx2rtkp.log"
    command = [
        str(solver),
        "-k", str(_one_path(received, "rtklib_configuration", evidence_root)),
        "-o", str(solution),
        str(_one_path(received, "rover_observation", evidence_root)),
        str(_one_path(received, "base_observation", evidence_root)),
        str(_one_path(received, "navigation", evidence_root)),
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=run_dir,
            text=True,
            capture_output=True,
            check=False,
            timeout=maximum_runtime_seconds,
        )
        return_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
        execution_error = None
    except subprocess.TimeoutExpired as exc:
        return_code = 124
        stdout = str(exc.stdout or "")
        stderr = str(exc.stderr or "")
        execution_error = f"solver exceeded {maximum_runtime_seconds} second runtime limit"
    except OSError as exc:
        return_code = 126
        stdout = ""
        stderr = str(exc)
        execution_error = "solver could not be executed"
    log_path.write_text(
        f"return_code={return_code}\nstdout:\n{stdout}\nstderr:\n{stderr}",
        encoding="utf-8",
    )
    artifacts = {
        path.relative_to(run_dir).as_posix(): {
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in sorted(run_dir.rglob("*"))
        if path.is_file()
    }
    return {
        "solver_sha256": sha256(solver),
        "return_code": return_code,
        "execution_error": execution_error,
        "solution_exists": solution.is_file(),
        "solution_sha256": sha256(solution) if solution.is_file() else None,
        "log_sha256": sha256(log_path),
        "controlled_run_artifacts": artifacts,
        "metrics": parse_rtklib_solution(solution) if solution.is_file() else None,
    }


def build_report(
    city: str,
    manifest_path: Path,
    evidence_root: Path,
    output_dir: Path,
    requirements_path: Path = DEFAULT_REQUIREMENTS,
    solver_path: Path | None = None,
    execute: bool = False,
) -> dict[str, Any]:
    requirements = read_requirements(requirements_path)
    received, findings = validate_receipt(manifest_path, evidence_root, requirements)
    processing_roles = [
        str(role["id"]) for role in requirements["file_role"] if role["required_for_processing"]
    ]
    review_roles = [
        str(role["id"]) for role in requirements["file_role"] if role["required_for_authority_review"]
    ]
    missing_processing = [role for role in processing_roles if len(received[role]) != 1]
    duplicate_processing = [role for role in processing_roles if len(received[role]) > 1]
    missing_review = [role for role in review_roles if not received[role]]
    configuration_values: dict[str, str] = {}
    configuration_findings: list[str] = []
    if not findings and not missing_processing and not duplicate_processing:
        configuration_values, configuration_findings = validate_rtklib_configuration(
            _one_path(received, "rtklib_configuration", evidence_root), requirements
        )
    resolved_solver = solver_path or (Path(found) if (found := shutil.which(requirements["solver"])) else None)
    solver_available = (
        bool(resolved_solver and resolved_solver.is_file() and os.access(resolved_solver, os.X_OK))
        if execute
        else None
    )
    processing: dict[str, Any] | None = None
    can_execute = bool(
        not findings
        and not missing_processing
        and not duplicate_processing
        and not configuration_findings
        and solver_available
    )
    if execute and can_execute and resolved_solver is not None:
        processing = run_rtklib(
            received,
            evidence_root,
            output_dir / "controlled-run",
            resolved_solver,
            int(requirements["rtklib_configuration"]["maximum_runtime_seconds"]),
        )
    criteria = requirements["technical_screen"]
    metrics = processing.get("metrics") if processing else None
    technical_screen_passed = bool(
        processing
        and processing["return_code"] == 0
        and metrics
        and metrics["epoch_count"] >= int(criteria["minimum_epochs"])
        and metrics["fixed_fraction"] >= float(criteria["minimum_fixed_fraction"])
        and set(int(key) for key in metrics["quality_code_counts"])
        <= set(int(value) for value in criteria["allowed_solution_quality_codes"])
        and metrics["malformed_data_rows"] == 0
    )
    authority_valid, authority_findings = (
        authority_record_valid(received["authority_acceptance_record"], evidence_root, requirements)
        if received["authority_acceptance_record"] and not findings
        else (False, ["authority acceptance record not received or receipt is invalid"])
    )
    authority_accepted = bool(technical_screen_passed and not missing_review and authority_valid)
    if findings:
        status = "blocked-invalid-receipt"
    elif missing_processing:
        status = "awaiting-field-data"
    elif configuration_findings:
        status = "blocked-invalid-processing-configuration"
    elif execute and not solver_available:
        status = "ready-for-processing-solver-missing"
    elif not execute:
        status = "ready-for-processing"
    elif not technical_screen_passed:
        status = "processing-complete-technical-screen-failed"
    elif not authority_accepted:
        status = "technical-screen-passed-awaiting-authority"
    else:
        status = "authority-accepted"
    return {
        "schema_version": "1.0",
        "analysis_id": f"OSR-SURVEY-CONTROL:{city}",
        "city": city,
        "status": status,
        "report_valid": not findings and not configuration_findings,
        "data_received": bool(any(received.values())),
        "receipt_findings": findings,
        "received_role_counts": {role: len(rows) for role, rows in received.items()},
        "received_files": [
            {"file_role": role, "file_path": row["file_path"], "sha256": row["sha256"]}
            for role in sorted(received)
            for row in received[role]
        ],
        "missing_processing_roles": missing_processing,
        "duplicate_processing_roles": duplicate_processing,
        "processing_configuration": configuration_values,
        "processing_configuration_findings": configuration_findings,
        "missing_authority_review_roles": missing_review,
        "solver": requirements["solver"],
        "solver_available": solver_available,
        "processing_requested": execute,
        "processing_completed": bool(processing and processing["return_code"] == 0),
        "processing": processing,
        "technical_screen_criteria": criteria,
        "technical_screen_passed": technical_screen_passed,
        "authority_record_valid": authority_valid,
        "authority_record_findings": authority_findings,
        "authority_accepted": authority_accepted,
        "requirements_source": display_path(requirements_path),
        "requirements_sha256": sha256(requirements_path),
        "receipt_manifest_sha256": sha256(manifest_path),
        "generator_sha256": sha256(Path(__file__)),
        "raw_data_policy": requirements["raw_data_policy"],
        "technical_boundary": requirements["technical_boundary"],
        "acceptance_boundary": requirements["acceptance_boundary"],
    }


def render_markdown(report: dict[str, Any]) -> str:
    solver_state = (
        "available" if report["solver_available"] is True
        else "missing" if report["solver_available"] is False
        else "not probed"
    )
    lines = [
        f"# {report['city'].title()} survey-control processing",
        "",
        f"- Status: **{report['status']}**",
        f"- RTKLIB runtime: **{solver_state}**",
        f"- Processing completed: **{'yes' if report['processing_completed'] else 'no'}**",
        f"- Technical screen passed: **{'yes' if report['technical_screen_passed'] else 'no'}**",
        f"- Survey authority accepted: **{'yes' if report['authority_accepted'] else 'no'}**",
        "",
        "> " + report["technical_boundary"],
        "",
        "> " + report["acceptance_boundary"],
        "",
        "## Current gates",
        "",
        f"- Missing processing roles: {', '.join(report['missing_processing_roles']) or 'none'}",
        f"- Duplicate processing roles: {', '.join(report['duplicate_processing_roles']) or 'none'}",
        f"- Processing-configuration findings: {len(report['processing_configuration_findings'])}",
        f"- Missing authority-review roles: {', '.join(report['missing_authority_review_roles']) or 'none'}",
    ]
    if report["receipt_findings"]:
        lines.extend(["- Receipt findings:", *[f"  - {item}" for item in report["receipt_findings"]]])
    if report["processing_configuration_findings"]:
        lines.extend(
            [
                "- Processing-configuration findings:",
                *[f"  - {item}" for item in report["processing_configuration_findings"]],
            ]
        )
    lines.extend(
        [
            "",
            "## Controlled-storage workflow",
            "",
            report["raw_data_policy"],
            "",
            "1. Put received files in access-controlled project storage.",
            "2. Add one `SUR-CTRL` manifest row per file, including `file_role`, metadata and SHA-256.",
            "3. Freeze the required RTKLIB settings, then run this processor; the four processing roles must occur exactly once.",
            "4. Review RTKLIB outputs, complete independent checks and network adjustment, then add the controlled acceptance record.",
            "5. Re-run; only the appointed survey authority's explicit record can close the authority gate.",
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
    solver_path: Path | None = None,
    execute: bool = False,
) -> dict[str, Any]:
    report = build_report(
        city, manifest_path.resolve(), evidence_root.resolve(), output_dir.resolve(),
        requirements_path.resolve(), solver_path.resolve() if solver_path else None, execute,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    atomic_json(output_dir / "control-processing-readiness.json", report)
    (output_dir / "control-processing-readiness.md").write_text(
        render_markdown(report), encoding="utf-8"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--city", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--evidence-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--requirements", type=Path, default=DEFAULT_REQUIREMENTS)
    parser.add_argument("--solver", type=Path)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--require-processing", action="store_true")
    args = parser.parse_args()
    report = generate(
        args.city,
        args.manifest,
        args.evidence_root,
        args.output_dir,
        args.requirements,
        args.solver,
        args.execute,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report["report_valid"]:
        return 1
    if args.require_processing and not report["processing_completed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
