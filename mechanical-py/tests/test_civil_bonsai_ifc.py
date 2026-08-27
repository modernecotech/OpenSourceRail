"""Regression checks for the deterministic Bonsai/IFC civil handoff."""

from __future__ import annotations

import json
from pathlib import Path

import ifcopenshell
from bcf.v3.bcfxml import BcfXml

from engineering.interchange.civil_bonsai_ifc import write_outputs


def test_civil_ifc_has_rail_semantics_geometry_schedule_and_stable_ids(tmp_path: Path) -> None:
    paths = write_outputs(tmp_path / "first", alignment_path=None, revision_id="test-revision")
    index = json.loads(paths["index"].read_text(encoding="utf-8"))
    validation = json.loads(paths["validation"].read_text(encoding="utf-8"))
    ids_report = json.loads(paths["ids_report"].read_text(encoding="utf-8"))
    bcf_index = json.loads(paths["bcf_index"].read_text(encoding="utf-8"))
    model = ifcopenshell.open(str(paths["ifc"]))
    coordination = BcfXml.load(paths["bcf"])

    assert validation["passed"]
    assert ids_report["status"]
    assert ids_report["total_specifications_pass"] == 3
    assert ids_report["total_checks"] == ids_report["total_checks_pass"] == 828
    assert bcf_index["topic_count"] == 3
    assert coordination is not None
    assert coordination.version.version_id == "3.0"
    assert len(coordination.topics) == 3
    assert index["summary"] == {
        "assets": 82,
        "construction_tasks": 16,
        "disciplines": {
            "above-track": 10,
            "lineside": 2,
            "substructure": 22,
            "track": 48,
        },
        "ifc_classes": {
            "IfcBeam": 12,
            "IfcBuildingElementProxy": 2,
            "IfcColumn": 9,
            "IfcElementAssembly": 1,
            "IfcRail": 32,
            "IfcRoof": 4,
            "IfcSlab": 20,
            "IfcVirtualElement": 2,
        },
        "interface_checks": 9,
    }
    assert model.schema == "IFC4X3"
    assert len(model.by_type("IfcRailway")) == 1
    assert len(model.by_type("IfcRailwayPart")) == 4
    assert len(model.by_type("IfcAlignment")) == 1
    assert len(model.by_type("IfcTask")) == 16
    assert len({item.Tag for item in model.by_type("IfcElement") if item.Tag}) == 82


def test_civil_ifc_is_byte_deterministic(tmp_path: Path) -> None:
    first = write_outputs(tmp_path / "first", alignment_path=None, revision_id="same")
    second = write_outputs(tmp_path / "second", alignment_path=None, revision_id="same")
    assert first.keys() == second.keys()
    for kind in first:
        assert first[kind].read_bytes() == second[kind].read_bytes(), kind


def test_coordination_decision_is_carried_into_bcf_without_mutating_topic_identity(tmp_path: Path) -> None:
    alignment = tmp_path / "alignment.json"
    alignment.write_text(
        json.dumps(
            {
                "line_slug": "review-line",
                "points": [[0.0, 0.0, 0.0], [320.0, 0.0, 0.0]],
                "coordination_issues": [
                    {
                        "id": "station-deck-release",
                        "status": "resolved",
                        "assignee": "Structures",
                        "resolution": "Engineer-released deck calculation and drawing package accepted.",
                        "reviewed_by": "Civil design authority",
                    },
                    {
                        "id": "custom-0123456789abcdef",
                        "title": "Confirm rail fastening interface",
                        "description": "Confirm the selected rail fastening interface against the released supplier assembly.",
                        "asset_ids": ["OSR-DT-416916837E"],
                        "status": "open",
                        "assignee": "Track engineering",
                        "resolution": "",
                        "reviewed_by": "",
                    },
                ],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    paths = write_outputs(tmp_path / "reviewed", alignment_path=alignment, revision_id="reviewed")
    bcf_index = json.loads(paths["bcf_index"].read_text(encoding="utf-8"))
    station_topic = next(
        topic for topic in bcf_index["topics"] if topic["issue_id"] == "station-deck-release"
    )
    custom_topic = next(
        topic for topic in bcf_index["topics"] if topic["issue_id"] == "custom-0123456789abcdef"
    )

    assert bcf_index["topic_count"] == 4
    assert bcf_index["open_topic_count"] == 3
    assert station_topic["intent_status"] == "resolved"
    assert station_topic["status"] == "Resolved"
    assert station_topic["assignee"] == "Structures"
    assert station_topic["reviewed_by"] == "Civil design authority"
    assert "Engineer-released" in station_topic["description"]
    assert custom_topic["asset_ids"] == ["OSR-DT-416916837E"]
    assert custom_topic["assignee"] == "Track engineering"

    repeated = write_outputs(
        tmp_path / "reviewed-repeat", alignment_path=alignment, revision_id="reviewed"
    )
    assert paths["bcf"].read_bytes() == repeated["bcf"].read_bytes()
    assert paths["bcf_index"].read_bytes() == repeated["bcf_index"].read_bytes()
