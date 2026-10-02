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
    assert len(report["missing_technical_roles"]) == 10
    assert report["technical_screen_passed"] is False


def test_swmm_foundation_and_authority_acceptance_path(tmp_path: Path) -> None:
    design_path = tmp_path / "design.toml"; design(design_path)
    requirements = drainage_ground_design.read_requirements()
    ground = tmp_path / "ground.json"; ground.write_text(json.dumps({"authority_accepted": True}))
    route_fit = tmp_path / "route-fit.json"; route_fit.write_text(json.dumps({"authority_accepted": True}))
    hydrology = tmp_path / "hydrology.json"; hydrology.write_text(json.dumps({"decision": "accepted", "storm": "test-only"}))
    swmm = tmp_path / "project.inp"
    swmm.write_text(SWMM_FIXTURE.read_text().replace("KINWAVE", "DYNWAVE").replace("ROUTING_STEP         00:00:30", "ROUTING_STEP         00:00:01"))
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
        for scope_type, scope_id in (("line", "line-1"), ("line", "line-1-end"), ("station", "station-a"), ("station", "station-b")):
            writer.writerow({
                "support_id": f"{scope_type}-{scope_id}", "chainage_m": "25" if scope_id == "line-1-end" else "0", "scope_type": scope_type, "scope_id": "line-1" if scope_id == "line-1-end" else scope_id,
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
    from engineering.analysis.civil_evidence import sha
    review = {"decision": "accepted", "producer": "test producer", "checker": "independent test checker", "signed_at": "2026-10-02", "controlled_reference": "TEST-ONLY"}
    register = tmp_path / "assets.json"
    supports = [{"support_id": f"{kind}-{scope}", "scope_type": kind, "scope_id": "line-1" if scope == "line-1-end" else scope, "chainage_m": 25 if scope == "line-1-end" else 0, "zone_id": "GZ-1"} for kind, scope in (("line", "line-1"), ("line", "line-1-end"), ("station", "station-a"), ("station", "station-b"))]
    register.write_text(json.dumps({"schema": "osr-civil-assets/1", "design_sha256": sha(design_path), "review": review,
        "assets": [{"asset_id": "SPAN-1", "line_id": "line-1", "asset_type": "span", "from_station_m": 0, "to_station_m": 25, "coverage_group": "track", "support_ids": ["line-line-1", "line-line-1-end"]}],
        "supports": supports, "coverage_intervals": [{"line_id": "line-1", "coverage_group": "track", "from_station_m": 0, "to_station_m": 25}]}))
    files["civil_asset_register"] = register
    from osr_mech.civil.foundation import foundation_candidates
    candidate_ids = foundation_candidates("rock", vibration_restricted=True)["candidate_ids"]
    site = dict(groundwater="TEST", chemistry="TEST", liquefaction="TEST", scour="TEST", utilities="TEST", construction_access="TEST", axial_demand_kN=800, lateral_demand_kN=50, settlement_limit_mm=10, differential_settlement_limit_mm=5,
        selection_review=dict(selected_id="shallow-spread", decision="accepted", engineer="TEST designer", checker="TEST checker", signed_at="2026-10-02", controlled_reference="TEST", comparison_rationale="TEST comparison"))
    comparison_rows = [dict(id=i, axial_capacity_kN=1000, lateral_capacity_kN=100, settlement_mm=5, differential_settlement_mm=2, constructable=True, chemistry_compatible=True, liquefaction_checked=True, scour_checked=True, calculation_reference="TEST") for i in candidate_ids]
    ground_summary = json.loads(ground_report.read_text())
    ground_summary["support_comparisons"] = {support["support_id"]: dict(ground_class="rock", vibration_restricted=True, clear_access=True, high_lateral_load=False, site=site, comparisons=comparison_rows) for support in supports}
    ground_report.write_text(json.dumps(ground_summary))
    # Fixtures vary conduit size; separate models and reviewed hashes are mandatory.
    scenarios = {"normal": swmm}
    for name, diameter in (("blocked-drain", "0.49"), ("backwater", "0.48")):
        target = tmp_path / f"{name}.inp"
        target.write_text(swmm.read_text().replace("CIRCULAR 0.5", f"CIRCULAR {diameter}") if name == "blocked-drain" else swmm.read_text().replace("O1     0    FREE            NO", "O1     0    FIXED 0.15      NO"))
        scenarios[name] = target
    limits = {"flow_units": "LPS", "system_units": "SI",
        "nodes": {"J1": {"peak_head": 2, "flooding_volume": 0, "surcharge_duration": 0}, "O1": {"peak_head": 2, "flooding_volume": 0, "surcharge_duration": 0, "outfall_peak_flow": 100}},
        "links": {"C1": {"peak_depth": 0.5, "surcharge_duration": 0}}}
    hydrology.write_text(json.dumps({"decision": "accepted", "review": review,
        "scenario_assumptions": {"blocked-drain": "TEST sensitivity", "backwater": "TEST sensitivity"},
        "scenario_model_hashes": {name: sha(path) for name,path in scenarios.items()},
        "performance_limits": {name: limits for name in scenarios}}))
    summary = json.loads(swmm_report.read_text())
    summary["hydrology_basis_sha256"] = sha(hydrology)
    summary["scenarios"] = {name: {"model_path": path.name, "sha256": sha(path)} for name,path in scenarios.items()}
    swmm_report.write_text(json.dumps(summary))
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
