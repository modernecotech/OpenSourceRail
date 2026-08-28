"""Regression checks for the deterministic Bonsai/IFC civil handoff."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import ifcopenshell
import pytest
from bcf.v3.bcfxml import BcfXml

from engineering.interchange.civil_bonsai_ifc import load_alignment, write_outputs


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
    assert ids_report["total_specifications_pass"] == 4
    assert ids_report["total_checks"] == ids_report["total_checks_pass"] == 1112
    assert bcf_index["topic_count"] == 3
    assert coordination is not None
    assert coordination.version.version_id == "3.0"
    assert len(coordination.topics) == 3
    assert index["summary"] == {
        "assets": 95,
        "construction_tasks": 18,
        "disciplines": {
            "above-track": 10,
            "lineside": 2,
            "substructure": 34,
            "track": 49,
        },
        "ifc_classes": {
            "IfcBeam": 12,
            "IfcBuildingElementProxy": 2,
            "IfcColumn": 9,
            "IfcElementAssembly": 1,
            "IfcRail": 32,
            "IfcRoof": 4,
            "IfcSlab": 33,
            "IfcVirtualElement": 2,
        },
        "interface_checks": 9,
        "typed_assets": 93,
        "types": 17,
    }
    assert index["cost_model"]["maturity"] == "planning-target-not-a-quotation"
    with (Path(__file__).resolve().parents[2] / "lib/templates/civil-cost-model.toml").open(
        "rb"
    ) as handle:
        expected_cost_model = tomllib.load(handle)
    assert index["cost_model"]["civil_usd_per_km"] == expected_cost_model[
        "civil_usd_per_km"
    ]
    assert index["cost_model"]["quantities_per_route_km"]["elevated"][
        "bearings_per_km"
    ] == 200
    assert model.schema == "IFC4X3"
    assert len(model.by_type("IfcRailway")) == 1
    assert len(model.by_type("IfcRailwayPart")) == 4
    assert {part.UsageType for part in model.by_type("IfcRailwayPart")} == {"VERTICAL"}
    assert len(model.by_type("IfcAlignment")) == 1
    assert len(model.by_type("IfcTask")) == 18
    assert len({item.Tag for item in model.by_type("IfcElement") if item.Tag}) == 95
    assert len(model.by_type("IfcTypeProduct")) == 17
    assert len(model.by_type("IfcRelDefinesByType")) == 17
    assert sum(
        len(relationship.RelatedObjects)
        for relationship in model.by_type("IfcRelDefinesByType")
    ) == 93
    assert {
        product.Tag for product in model.by_type("IfcTypeProduct")
    } == {row["type_id"] for row in index["types"]}
    assert all(
        product.RepresentationMaps is None
        for product in model.by_type("IfcTypeProduct")
    )
    assert all(
        not product.IsTypedBy for product in model.by_type("IfcVirtualElement")
    )
    assert all(
        len(model.by_guid(row["ifc_guid"]).IsTypedBy) == (1 if row["ifc_type_id"] else 0)
        for row in index["objects"]
    )
    assert len(model.by_type("IfcElementQuantity")) == 95
    assert {
        quantity_set.Name for quantity_set in model.by_type("IfcElementQuantity")
    } == {"OSR_CoordinationEnvelopeQuantities"}
    assert not model.by_type("IfcProjectedCRS")
    assert index["georeferencing"]["status"] == "project-crs-unresolved"
    assert validation["schema_validation"]["issue_count"] == 0


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


def test_explicit_project_georeferencing_creates_native_ifc_map_conversion(tmp_path: Path) -> None:
    alignment = tmp_path / "georeferenced-alignment.json"
    alignment.write_text(
        json.dumps(
            {
                "line_slug": "surveyed-line",
                "points": [[0.0, 0.0, 0.0], [320.0, 0.0, 0.0]],
                "georeferencing": {
                    "crs_name": "EPSG:9306",
                    "description": "Accepted project compound CRS",
                    "eastings": 198765.4,
                    "northings": 431234.5,
                    "orthogonal_height": 18.25,
                    "x_axis_abscissa": 0.999847695,
                    "x_axis_ordinate": -0.017452406,
                    "scale": 0.99995,
                    "source": "Accepted survey control revision S-04",
                },
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    paths = write_outputs(tmp_path / "georeferenced", alignment_path=alignment, revision_id="survey-S-04")
    model = ifcopenshell.open(str(paths["ifc"]))
    index = json.loads(paths["index"].read_text(encoding="utf-8"))
    validation = json.loads(paths["validation"].read_text(encoding="utf-8"))
    projected_crs = model.by_type("IfcProjectedCRS")
    map_conversions = model.by_type("IfcMapConversion")

    assert len(projected_crs) == len(map_conversions) == 1
    assert projected_crs[0].Name == "EPSG:9306"
    assert map_conversions[0].Eastings == 198765.4
    assert map_conversions[0].Northings == 431234.5
    assert map_conversions[0].OrthogonalHeight == 18.25
    assert map_conversions[0].Scale == 0.99995
    assert index["georeferencing"]["native_ifc_georeferencing"]
    assert index["georeferencing"]["source"] == "Accepted survey control revision S-04"
    assert validation["schema_validation"]["issue_count"] == 0


def test_invalid_georeferencing_is_rejected_before_ifc_generation(tmp_path: Path) -> None:
    alignment = tmp_path / "invalid-georeferencing.json"
    alignment.write_text(
        json.dumps(
            {
                "points": [[0.0, 0.0, 0.0], [10.0, 0.0, 0.0]],
                "georeferencing": {
                    "crs_name": "EPSG:9306",
                    "eastings": 0.0,
                    "northings": 0.0,
                    "orthogonal_height": 0.0,
                    "scale": 0.0,
                },
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="scale must be greater than zero"):
        load_alignment(alignment)
