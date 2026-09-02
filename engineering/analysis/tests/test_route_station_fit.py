"""Tests for route/station fit receipt, coverage, issue and authority gates."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from engineering.analysis import route_station_fit


def write_design(path: Path) -> None:
    path.write_text(
        "[city]\nslug = \"test-city\"\n\n[[lines]]\nname = \"line-1\"\n\n"
        "[[stations]]\nid = \"station-a\"\nline = \"line-1\"\n\n"
        "[[stations]]\nid = \"station-b\"\nline = \"line-1\"\n",
        encoding="utf-8",
    )


def row(role: str, path: Path, root: Path, status: str = "checked") -> dict[str, str]:
    return {
        "file_role": role, "package_revision": "A", "file_path": path.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "capture_date": "2026-09-02",
        "coordinate_system": "EPSG:32638", "vertical_datum": "test-project-datum",
        "producer": "test producer", "checker": "independent test checker", "acceptance_status": status,
    }


def write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=route_station_fit.FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def test_empty_manifest_is_deterministic_and_pending(tmp_path: Path) -> None:
    design = tmp_path / "design.toml"
    manifest = tmp_path / "manifest.csv"
    write_design(design)
    requirements = route_station_fit.read_requirements()
    route_station_fit.write_placeholder_manifest(manifest, requirements)
    first = manifest.read_bytes()
    route_station_fit.write_placeholder_manifest(manifest, requirements)

    report = route_station_fit.build_report(design, manifest, tmp_path)

    assert manifest.read_bytes() == first
    assert report["status"] == "awaiting-route-fit-evidence"
    assert len(report["missing_technical_roles"]) == 12
    assert report["technical_screen_passed"] is False
    assert report["authority_accepted"] is False


def test_complete_resolved_fixture_requires_and_accepts_signed_record(tmp_path: Path) -> None:
    design = tmp_path / "design.toml"
    write_design(design)
    requirements = route_station_fit.read_requirements()
    files: dict[str, Path] = {}
    for item in requirements["input"]:
        role = item["file_role"]
        if role in {"route_fit_verification_report", "route_fit_acceptance_record"}:
            continue
        path = tmp_path / f"{role}{item['extensions'][0]}"
        files[role] = path
        if role in {"ground_model_readiness", "surveyed_alignment_readiness"}:
            path.write_text(json.dumps({"authority_accepted": True}))
        elif role == "route_fit_issue_register":
            path.write_text("issue_id,scope_type,scope_id,domain,severity,status,owner,disposition,evidence_reference\n")
        else:
            path.write_text(json.dumps({"status": "checked", "role": role}))
    prerequisite_roles = [item["file_role"] for item in requirements["input"] if item["category"] == "prerequisite"]
    evidence_roles = [item["file_role"] for item in requirements["input"] if item["category"] == "evidence"]
    verification = tmp_path / "route_fit_verification_report.json"
    verification.write_text(json.dumps({
        "status": "passed", "coordinate_system": "EPSG:32638", "vertical_datum": "test-project-datum",
        "prerequisite_hashes": {role: hashlib.sha256(files[role].read_bytes()).hexdigest() for role in prerequisite_roles},
        "evidence_hashes": {role: hashlib.sha256(files[role].read_bytes()).hexdigest() for role in evidence_roles},
        "line_results": [{"line_id": "line-1", **{field: "resolved" for field in requirements["verification_report"]["line_status_fields"]}}],
        "station_results": [
            {"station_id": station, "line_id": "line-1", **{field: "resolved" for field in requirements["verification_report"]["station_status_fields"]}}
            for station in ("station-a", "station-b")
        ],
    }))
    files["route_fit_verification_report"] = verification
    rows = [row(role, path, tmp_path) for role, path in files.items()]
    manifest = tmp_path / "manifest.csv"
    write_manifest(manifest, rows)

    pending = route_station_fit.build_report(design, manifest, tmp_path, inspect=True)
    assert pending["technical_screen_passed"] is True
    assert pending["status"] == "technical-screen-passed-awaiting-authority"

    hashes = {item["file_role"]: item["sha256"] for item in rows}
    acceptance = tmp_path / "route_fit_acceptance_record.json"
    acceptance.write_text(json.dumps({
        "decision": "accepted", "engineer_of_record": "test engineer", "operator_representative": "test operator",
        "information_manager": "test manager", "utility_authority": "test utility authority",
        "land_authority": "test land authority", "drainage_authority": "test drainage authority",
        "highway_authority": "test highway authority", "signed_at": "2026-09-02T12:00:00Z",
        "document_revision": "A", "approved_horizontal_crs": "EPSG:32638",
        "approved_vertical_datum": "test-project-datum", "controlled_record_reference": "TEST-ONLY",
        "approved_evidence_hashes": hashes,
    }))
    rows.append(row("route_fit_acceptance_record", acceptance, tmp_path, "accepted"))
    write_manifest(manifest, rows)

    accepted = route_station_fit.build_report(design, manifest, tmp_path, inspect=True)
    assert accepted["inspection_findings"] == []
    assert accepted["authority_record_findings"] == []
    assert accepted["authority_accepted"] is True
    assert accepted["status"] == "authority-accepted"


def test_open_high_issue_and_path_escape_fail_closed(tmp_path: Path) -> None:
    issue_path = tmp_path / "issues.csv"
    issue_path.write_text(
        "issue_id,scope_type,scope_id,domain,severity,status,owner,disposition,evidence_reference\n"
        "FIT-1,line,line-1,utilities,high,open,utility lead,diversion pending,UTIL-1\n"
    )
    summary, findings = route_station_fit.inspect_issue_register(
        issue_path, route_station_fit.read_requirements(), {"line-1"}
    )
    assert summary["open_high_or_critical"] == 1
    assert any("unresolved high or critical" in item for item in findings)

    design = tmp_path / "design.toml"
    write_design(design)
    controlled = tmp_path / "controlled"
    controlled.mkdir()
    link = controlled / "ground.json"
    link.symlink_to(issue_path)
    bad = row("ground_model_readiness", link, controlled)
    manifest = tmp_path / "manifest.csv"
    write_manifest(manifest, [bad])
    report = route_station_fit.build_report(design, manifest, controlled)
    assert report["status"] == "blocked-invalid-receipt"
    assert any("outside the evidence root" in item for item in report["receipt_findings"])
