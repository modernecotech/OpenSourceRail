"""Tests for reproducible SWMM and ground/foundation deployment gates."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path

from engineering.analysis import drainage_ground_design
from engineering.analysis import route_station_fit


SWMM_FIXTURE = drainage_ground_design.REPO_ROOT / "engineering/analysis/benchmarks/swmm/simple-runoff.inp"


def design(path: Path) -> None:
    path.write_text(
        "[city]\nslug = \"test-city\"\n\n[[lines]]\nname = \"line-1\"\n\n"
        "[[stations]]\nid = \"station-a\"\nline = \"line-1\"\n\n"
        "[[stations]]\nid = \"station-b\"\nline = \"line-1\"\n"
    )


def receipt_row(role: str, path: Path, root: Path, status: str = "checked") -> dict[str, str]:
    return {
        "file_role": role, "package_revision": "A", "file_path": path.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "capture_date": "2026-09-02",
        "coordinate_system": "EPSG:32638", "vertical_datum": "test-project-datum",
        "producer": "test producer", "checker": "test checker", "acceptance_status": status,
    }


def manifest(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=route_station_fit.FIELDS, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def test_placeholder_manifest_is_pending_and_deterministic(tmp_path: Path) -> None:
    design_path = tmp_path / "design.toml"; design(design_path)
    receipt = tmp_path / "receipt.csv"
    requirements = drainage_ground_design.read_requirements()
    drainage_ground_design.write_placeholder_manifest(receipt, requirements)
    first = receipt.read_bytes(); drainage_ground_design.write_placeholder_manifest(receipt, requirements)
    report = drainage_ground_design.build_report(design_path, receipt, tmp_path)
    assert receipt.read_bytes() == first
    assert report["status"] == "awaiting-drainage-ground-evidence"
    assert len(report["missing_technical_roles"]) == 9
    assert report["technical_screen_passed"] is False


def test_swmm_foundation_and_authority_acceptance_path(tmp_path: Path) -> None:
    design_path = tmp_path / "design.toml"; design(design_path)
    requirements = drainage_ground_design.read_requirements()
    ground = tmp_path / "ground.json"; ground.write_text(json.dumps({"authority_accepted": True}))
    route_fit = tmp_path / "route-fit.json"; route_fit.write_text(json.dumps({"authority_accepted": True}))
    hydrology = tmp_path / "hydrology.json"; hydrology.write_text(json.dumps({"decision": "accepted", "storm": "test-only"}))
    swmm = tmp_path / "project.inp"; shutil.copy2(SWMM_FIXTURE, swmm)
    replay = drainage_ground_design.replay_swmm(swmm)
    swmm_report = tmp_path / "swmm-report.json"
    swmm_report.write_text(json.dumps({
        "status": "passed", "tool": replay["tool"], "version": replay["version"],
        "input_sha256": hashlib.sha256(swmm.read_bytes()).hexdigest(),
        "hydrology_basis_sha256": hashlib.sha256(hydrology.read_bytes()).hexdigest(),
        "ground_model_sha256": hashlib.sha256(ground.read_bytes()).hexdigest(),
        "coordinate_system": "EPSG:32638", "vertical_datum": "test-project-datum",
        "runoff_error_percent": replay["runoff_error_percent"], "routing_error_percent": replay["routing_error_percent"],
        "step_count": replay["step_count"], "design_checks": {"test-only": "passed"},
    }))
    geo = tmp_path / "geotechnical.json"; geo.write_text(json.dumps({"zones": ["GZ-1"], "boreholes": ["BH-1"]}))
    schedule = tmp_path / "foundation.csv"
    columns = requirements["foundation_schedule"]["required_columns"]
    with schedule.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n"); writer.writeheader()
        for scope_type, scope_id in (("line", "line-1"), ("station", "station-a"), ("station", "station-b")):
            writer.writerow({
                "support_id": f"{scope_type}-{scope_id}", "scope_type": scope_type, "scope_id": scope_id,
                "zone_id": "GZ-1", "system_kind": "foundation", "system_id": "shallow-spread",
                "actual_length_m": "", "actual_element_count": "0", "design_quantity": "18.0",
                "design_unit": "m3", "design_capacity": "1000", "predicted_settlement_mm": "5",
                "verification_method": "test-only calculation", "status": "checked",
            })
    ground_report = tmp_path / "ground-report.json"
    ground_report.write_text(json.dumps({
        "status": "passed", "geotechnical_model_sha256": hashlib.sha256(geo.read_bytes()).hexdigest(),
        "foundation_schedule_sha256": hashlib.sha256(schedule.read_bytes()).hexdigest(),
        "line_results": [{"line_id": "line-1", "drainage_status": "sized-and-checked", "ground_status": "sized-and-checked"}],
        "station_results": [
            {"station_id": station, "drainage_status": "sized-and-checked", "ground_status": "sized-and-checked"}
            for station in ("station-a", "station-b")
        ], "residual_risks": ["test fixture only"],
    }))
    decision = tmp_path / "groundwater.json"
    decision.write_text(json.dumps({
        "opengeosys_required": False, "evaluated_triggers": ["groundwater coupling"],
        "rationale": "not warranted in test fixture", "geotechnical_reviewer": "test reviewer",
        "reviewed_at": "2026-09-02T12:00:00Z",
    }))
    files = {
        "ground_model_readiness": ground, "route_station_fit_readiness": route_fit,
        "accepted_hydrology_basis": hydrology, "swmm_model": swmm,
        "swmm_processing_report": swmm_report, "geotechnical_ground_model": geo,
        "foundation_ground_schedule": schedule, "ground_design_verification_report": ground_report,
        "groundwater_coupling_decision": decision,
    }
    rows = [receipt_row(role, path, tmp_path) for role, path in files.items()]
    receipt = tmp_path / "receipt.csv"; manifest(receipt, rows)
    pending = drainage_ground_design.build_report(design_path, receipt, tmp_path, inspect=True)
    assert pending["technical_screen_passed"] is True
    assert pending["status"] == "technical-screen-passed-awaiting-authority"
    hashes = {item["file_role"]: item["sha256"] for item in rows}
    acceptance = tmp_path / "acceptance.json"
    acceptance.write_text(json.dumps({
        "decision": "accepted", "drainage_engineer": "test drainage engineer",
        "geotechnical_engineer": "test geotechnical engineer", "asset_owner": "test owner",
        "approving_authority": "test authority", "information_manager": "test manager",
        "signed_at": "2026-09-02T12:00:00Z", "document_revision": "A",
        "approved_horizontal_crs": "EPSG:32638", "approved_vertical_datum": "test-project-datum",
        "controlled_record_reference": "TEST-ONLY", "approved_evidence_hashes": hashes,
    }))
    rows.append(receipt_row("drainage_ground_acceptance_record", acceptance, tmp_path, "accepted")); manifest(receipt, rows)
    accepted = drainage_ground_design.build_report(design_path, receipt, tmp_path, inspect=True)
    assert accepted["inspection_findings"] == []
    assert accepted["authority_record_findings"] == []
    assert accepted["authority_accepted"] is True
    assert accepted["status"] == "authority-accepted"


def test_deep_foundation_requires_actual_length(tmp_path: Path) -> None:
    schedule = tmp_path / "foundation.csv"; requirements = drainage_ground_design.read_requirements()
    with schedule.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=requirements["foundation_schedule"]["required_columns"], lineterminator="\n"); writer.writeheader()
        writer.writerow({
            "support_id": "P-1", "scope_type": "line", "scope_id": "line-1", "zone_id": "GZ-1",
            "system_kind": "foundation", "system_id": "bored-shaft", "actual_length_m": "",
            "actual_element_count": "1", "design_quantity": "1", "design_unit": "each",
            "design_capacity": "1000", "predicted_settlement_mm": "5", "verification_method": "test", "status": "checked",
        })
    _, findings = drainage_ground_design.inspect_foundation_schedule(
        schedule, [{"id": "line-1"}], [], requirements
    )
    assert any("lacks actual length" in item for item in findings)
