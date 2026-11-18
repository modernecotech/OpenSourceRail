"""Selected digital controls produce an observation-only FUXA preview."""

import json
from pathlib import Path

import pytest

from services.integration.osr_integration import v07_supervision


ROOT = Path(__file__).resolve().parents[1]


def _sources(tmp_path):
    for path in (v07_supervision.SELECTION, v07_supervision.HANDOFF,
                 v07_supervision.INTERFACES, v07_supervision.INTERFACE_GENERATOR,
                 Path("control-electronics/reference-v07.toml")):
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(ROOT / path)


def test_selected_controls_generate_read_only_station_grid_and_section_views():
    package = v07_supervision.simulation_package()
    views = v07_supervision.simulation_view()
    assert package["physical_candidate_id"] == "osr-v07-joined-civil-518dad57a3af5046f40c8f4f"
    assert package["environment"] == "simulation"
    assert len(package["equipment"]) == len(views["devices"]) == len(views["hmi"]["views"]) == 40
    assert {row["equipment_type"] for row in package["equipment"]} == {
        "station-dispatch-controller", "grid-protection-gateway", "section-control-gateway"}
    assert all(row["source_id"] == "simulator" and row["commands"] == {}
               and not row["physical_serial_id"] for row in package["equipment"])
    assert all(row["daq"]["enabled"] is False for device in views["devices"].values()
               for row in device["tags"].values())


def test_changed_or_mixed_production_handoff_is_rejected(tmp_path):
    _sources(tmp_path)
    target = tmp_path / v07_supervision.HANDOFF
    target.unlink()
    data = json.loads((ROOT / v07_supervision.HANDOFF).read_text())
    data["physical_candidate_id"] = "different"
    target.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="identities differ"):
        v07_supervision.simulation_package(tmp_path)
    data["physical_candidate_id"] = "osr-v07-joined-civil-518dad57a3af5046f40c8f4f"
    data["production"]["beam_count"] += 1
    target.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="identities differ"):
        v07_supervision.simulation_package(tmp_path)
