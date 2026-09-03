"""Tests for the per-asset structural release gate."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from engineering.analysis import route_station_fit, structural_release


def design(path: Path) -> None:
    path.write_text("[city]\nslug=\"test-city\"\n[[lines]]\nname=\"line-1\"\n[[stations]]\nid=\"s1\"\nline=\"line-1\"\n")


def test_placeholder_manifest_is_deterministic_and_pending(tmp_path: Path) -> None:
    design_path = tmp_path / "design.toml"; design(design_path)
    manifest = tmp_path / "manifest.csv"; requirements = structural_release.read_requirements()
    structural_release.write_placeholder_manifest(manifest, requirements); first = manifest.read_bytes()
    structural_release.write_placeholder_manifest(manifest, requirements)
    report = structural_release.build_report(design_path, manifest, tmp_path)
    assert manifest.read_bytes() == first
    assert report["status"] == "awaiting-structural-evidence"
    assert len(report["missing_technical_roles"]) == 10
    assert report["technical_screen_passed"] is False


def test_schedule_requires_exact_line_coverage_and_valid_ranges(tmp_path: Path) -> None:
    requirements = structural_release.read_requirements(); schedule = tmp_path / "schedule.csv"
    fields = requirements["asset_schedule"]["required_columns"]
    with schedule.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n"); writer.writeheader()
        writer.writerow({"asset_id": "SP-1", "line_id": "line-1", "asset_type": "span", "from_station_m": "0", "to_station_m": "25", "variant_id": "Pi25", "foundation_ref": "F-1", "analysis_ids": "LC-1", "status": "checked"})
    rows, findings = structural_release.inspect_schedule(schedule, {"line-1"}, requirements)
    assert len(rows) == 1 and findings == []
    rows[0]["to_station_m"] = "0"
    with schedule.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    _, findings = structural_release.inspect_schedule(schedule, {"line-1"}, requirements)
    assert any("invalid chainage" in item for item in findings)


def test_solver_report_is_bound_to_input_and_convergence(tmp_path: Path) -> None:
    model = tmp_path / "model.py"; model.write_text("# deterministic test model\n")
    report = tmp_path / "report.json"
    report.write_text(json.dumps({"status": "passed", "tool": "OpenSeesPy", "version": "test", "input_sha256": hashlib.sha256(model.read_bytes()).hexdigest(), "model_revision": "A", "convergence": True, "load_case_ids": ["LC-1"], "output_hashes": {"result": "a" * 64}}))
    summary, findings = structural_release.inspect_solver(report, model, structural_release.read_requirements())
    assert summary["convergence"] is True and findings == []
    model.write_text("# changed\n")
    _, findings = structural_release.inspect_solver(report, model, structural_release.read_requirements())
    assert any("input hash" in item for item in findings)
