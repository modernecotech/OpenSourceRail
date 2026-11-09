import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/automation/reconciled-pilot-workbench.py"
SPEC = importlib.util.spec_from_file_location("reconciled_pilot_workbench", SCRIPT)
workbench = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workbench)


def test_published_packet_pins_and_comparison_candidate_identities():
    data = workbench.build(ROOT)
    assert data["source"]["manifest_id"]
    assert data["source"]["study_id"] == data["identity"]["study_id"]
    assert all(row["candidate_id"] == data["identity"]["physical_candidate_id"] for row in data["journeys"])
    with_store = data["recovery_comparison"]["with_store"]
    no_store = data["recovery_comparison"]["without_store"]
    assert with_store["physical_candidate_id"] == data["identity"]["physical_candidate_id"]
    assert with_store["physical_candidate_id"] != no_store["physical_candidate_id"]
    assert with_store["case"]["headway_s"] == no_store["case"]["headway_s"] == 200
    assert with_store["case"]["opposite_phase_s"] == no_store["case"]["opposite_phase_s"] == 90
    assert with_store["case"]["capture_kwh"] > 0
    assert no_store["case"]["capture_kwh"] == 0
    assert all(value is False for value in data["status"].values() if isinstance(value, bool))
    assert "separately published physical research candidates" in data["recovery_comparison"]["description"]
    assert data["project_scope"]["route_km"] == 1.5
    assert data["project_scope"]["city_corridor_integration"] is False
    assert data["project_scope"]["city_outline_evaluation_id"] != data["identity"]["bundle_evaluation_id"]
    page = (ROOT / "docs/workbench/current/reconciled-pilot/index.html").read_text()
    assert "Recovery-disabled rows bypass recovery in the journey model" in page
    assert "This is not the Baghdad corridor" in page
    assert "No rail movement authority" in page


def test_source_pin_mismatch_is_rejected(tmp_path):
    payload = tmp_path / "record.json"
    payload.write_text('{"candidate":"source"}')
    expected = workbench.hashlib.sha256(payload.read_bytes()).hexdigest()
    workbench.verify_hashes(tmp_path, Path("."), {"record.json": expected})
    payload.write_text('{"candidate":"changed"}')
    with pytest.raises(ValueError, match="Source pin mismatch"):
        workbench.verify_hashes(tmp_path, Path("."), {"record.json": expected})


def test_mixed_bundle_candidate_is_rejected(monkeypatch):
    original = workbench.read_json

    def changed(root, relative):
        result = original(root, relative)
        if relative == workbench.PILOT / "bundle.json":
            result = dict(result, candidate_id="0" * 64)
        return result

    monkeypatch.setattr(workbench, "read_json", changed)
    with pytest.raises(ValueError, match="Summary and source study do not use"):
        workbench.build(ROOT)


def test_false_release_flags_cannot_be_projected():
    with pytest.raises(ValueError, match="physical_accepted=false"):
        workbench.verify_release_holds({"physical_accepted": True})
    with pytest.raises(ValueError, match="operating_release=false"):
        workbench.verify_release_holds({"operating_release": None})
