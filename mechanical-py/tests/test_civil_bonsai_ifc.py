"""Regression checks for the deterministic Bonsai/IFC civil handoff."""

from __future__ import annotations

import json
from pathlib import Path

import ifcopenshell

from engineering.interchange.civil_bonsai_ifc import write_outputs


def test_civil_ifc_has_rail_semantics_geometry_schedule_and_stable_ids(tmp_path: Path) -> None:
    paths = write_outputs(tmp_path / "first", alignment_path=None, revision_id="test-revision")
    index = json.loads(paths["index"].read_text(encoding="utf-8"))
    validation = json.loads(paths["validation"].read_text(encoding="utf-8"))
    model = ifcopenshell.open(str(paths["ifc"]))

    assert validation["passed"]
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
    assert first["ifc"].read_bytes() == second["ifc"].read_bytes()
