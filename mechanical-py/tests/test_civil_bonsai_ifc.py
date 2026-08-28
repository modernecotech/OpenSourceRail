"""Regression checks for the deterministic Bonsai/IFC civil handoff."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import ifcopenshell
import ifcopenshell.geom
import pytest
from bcf.v3.bcfxml import BcfXml
from ifcopenshell.util.classification import get_references
from ifcopenshell.util.element import get_elements_by_profile, get_material, get_psets

from engineering.interchange.civil_bonsai_ifc import (
    load_alignment,
    material_ids_from_assignment,
    write_outputs,
)


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
    assert ids_report["total_specifications_pass"] == 13
    assert ids_report["total_checks"] == ids_report["total_checks_pass"] == 1602
    assert bcf_index["topic_count"] == 3
    assert coordination is not None
    assert coordination.version.version_id == "3.0"
    assert len(coordination.topics) == 3
    assert index["summary"] == {
        "alignment_stationing_referents": 2,
        "assets": 95,
        "classification_references": 11,
        "classifications": 1,
        "classified_assets": 95,
        "construction_tasks": 18,
        "coordination_groups": 5,
        "document_associated_assets": 95,
        "documents": 15,
        "grouped_assets": 95,
        "horizontal_alignment_segments": 1,
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
        "interface_constraints": 9,
        "layer_associated_assets": 95,
        "material_associated_assets": 46,
        "materials": 3,
        "profiled_assets": 32,
        "profiles": 1,
        "presentation_layers": 4,
        "property_set_templates": 13,
        "property_templates": 77,
        "template_linked_definitions": 220,
        "template_matched_definitions": 224,
        "typed_assets": 93,
        "types": 17,
        "vertical_alignment_segments": 1,
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
    assert len(model.by_type("IfcAlignmentHorizontal")) == 1
    assert len(model.by_type("IfcAlignmentVertical")) == 1
    assert len(model.by_type("IfcAlignmentSegment")) == 4
    assert len(model.by_type("IfcGradientCurve")) == 1
    assert len(model.by_type("IfcReferent")) == 2
    assert index["alignment"]["semantic_model"] == (
        "native-ifc4.3-horizontal-and-vertical-layouts"
    )
    assert index["alignment"]["geometry_curve"] == "IfcGradientCurve"
    assert index["alignment"]["horizontal_segment_type"] == "LINE"
    assert index["alignment"]["vertical_segment_type"] == "CONSTANTGRADIENT"
    assert index["alignment"]["cant_status"].startswith("not-modelled")
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
    assert len(model.by_type("IfcMaterial")) == 3
    assert len(model.by_type("IfcRelAssociatesMaterial")) == 35
    assert sum(
        relationship.RelatingMaterial.is_a("IfcMaterialProfileSetUsage")
        for relationship in model.by_type("IfcRelAssociatesMaterial")
    ) == 32
    assert sum(get_material(product) is not None for product in model.by_type("IfcTypeProduct")) == 5
    assert all(
        material_ids_from_assignment(get_material(model.by_guid(row["ifc_guid"])))
        == ((row["material_id"],) if row["material_id"] else ())
        for row in index["objects"]
    )
    assert all(
        get_psets(material)["OSR_MaterialStatus"]["SpecificationStatus"]
        == "family-declared; grade-and-design-unresolved"
        for material in model.by_type("IfcMaterial")
    )
    assert len(model.by_type("IfcMaterialProfileSet")) == 1
    assert len(model.by_type("IfcMaterialProfile")) == 1
    assert len(model.by_type("IfcMaterialProfileSetUsage")) == 32
    assert len(model.by_type("IfcExtrudedAreaSolid")) == 32
    profile = next(
        item
        for item in model.by_type("IfcArbitraryClosedProfileDef")
        if item.ProfileName == "OSR-PROFILE-UIC-60E1-REVIEW"
    )
    assert len(get_elements_by_profile(profile)) == 32
    assert get_psets(profile)["OSR_Profile"]["GeometryStatus"] == (
        "simplified-straight-line-review-polygon"
    )
    profile_row = index["profiles"][0]
    assert profile_row["usage_count"] == 32
    assert all(
        row["detail_mode"] == "native-profile-extrusion"
        and row["source_net_volume_m3"]
        == pytest.approx(
            profile_row["area_m2"] * (row["bbox_m"][3] - row["bbox_m"][0]),
            abs=2e-6,
        )
        for row in index["objects"]
        if row["profile_id"]
    )
    profiled_row = next(row for row in index["objects"] if row["profile_id"])
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    shape = ifcopenshell.geom.create_shape(settings, model.by_guid(profiled_row["ifc_guid"]))
    vertices = list(zip(*(iter(shape.geometry.verts),) * 3))
    geometry_bbox = [min(point[axis] for point in vertices) for axis in range(3)] + [
        max(point[axis] for point in vertices) for axis in range(3)
    ]
    assert geometry_bbox == pytest.approx(profiled_row["bbox_m"], abs=1e-9)
    assert len(model.by_type("IfcDocumentInformation")) == 15
    assert len(model.by_type("IfcDocumentReference")) == 15
    assert len(model.by_type("IfcRelAssociatesDocument")) == 30
    document_information = {
        item.Identification: item for item in model.by_type("IfcDocumentInformation")
    }
    document_references = {
        item.Identification: item for item in model.by_type("IfcDocumentReference")
    }
    assert set(document_information) == set(document_references) == {
        row["document_id"] for row in index["documents"]
    }
    assert all(
        document_information[row["document_id"]].Revision == f"sha256:{row['sha256']}"
        and document_information[row["document_id"]].Location == row["location"]
        and document_references[row["document_id"]].ReferencedDocument
        == document_information[row["document_id"]]
        for row in index["documents"]
    )
    assert all(
        set(row["document_ids"])
        == {
            relationship.RelatingDocument.Identification
            for relationship in model.by_guid(row["ifc_guid"]).HasAssociations
            if relationship.is_a("IfcRelAssociatesDocument")
            and relationship.RelatingDocument.is_a("IfcDocumentReference")
        }
        for row in index["objects"]
    )
    document_pset = get_psets(model.by_type("IfcProject")[0])["OSR_DocumentRegister"]
    assert document_pset["DocumentCount"] == 15
    assert document_pset["HashAlgorithm"] == "SHA-256"
    assert document_pset["LocationPolicy"] == "repository-relative URI"
    assert document_pset["RegisterStatus"] == "native-ifc-hash-locked-repository-sources"
    assert len(model.by_type("IfcClassification")) == 1
    assert len(model.by_type("IfcClassificationReference")) == 11
    assert len(model.by_type("IfcRelAssociatesClassification")) == 12
    classification = model.by_type("IfcClassification")[0]
    assert classification.Name == "OpenSourceRail Asset Classification"
    assert classification.Edition == "1.0"
    assert classification.ReferenceTokens == (".",)
    assert {
        reference.Identification
        for reference in model.by_type("IfcClassificationReference")
    } == {reference["code"] for reference in index["classification"]["references"]}
    assert all(
        {
            reference.Identification
            for reference in get_references(
                model.by_guid(row["ifc_guid"]), should_inherit=True
            )
            if reference.is_a("IfcClassificationReference")
        }
        == {row["classification_code"]}
        for row in index["objects"]
    )
    classification_pset = get_psets(model.by_type("IfcProject")[0])[
        "OSR_Classification"
    ]
    assert classification_pset["ReferenceCount"] == 11
    assert (
        classification_pset["ExternalMappingStatus"]
        == "country-and-client-mapping-not-nominated"
    )
    assert len(model.by_type("IfcGroup")) == 5
    assert len(model.by_type("IfcRelAssignsToGroup")) == 5
    assert sorted(row["asset_count"] for row in index["groups"]) == [1, 2, 11, 12, 69]
    assert sum(
        len(relationship.RelatedObjects)
        for relationship in model.by_type("IfcRelAssignsToGroup")
    ) == 95
    groups_by_id = {
        get_psets(group)["OSR_CoordinationGroup"]["GroupId"]: group
        for group in model.by_type("IfcGroup")
    }
    assert set(groups_by_id) == {row["group_id"] for row in index["groups"]}
    assert all(
        groups_by_id[row["group_id"]].Name == row["name"]
        and get_psets(groups_by_id[row["group_id"]])["OSR_CoordinationGroup"]
        ["SourceZone"]
        == row["name"]
        and get_psets(groups_by_id[row["group_id"]])["OSR_CoordinationGroup"]
        ["GroupRole"]
        == "non-spatial-review-group"
        and get_psets(groups_by_id[row["group_id"]])["OSR_CoordinationGroup"]
        ["SpatialMeaning"]
        == "separated review layout; not a surveyed spatial zone"
        and get_psets(groups_by_id[row["group_id"]])["OSR_CoordinationGroup"]
        ["SystemMeaning"]
        == "inspection grouping; not a functional engineering system"
        for row in index["groups"]
    )
    assert all(
        {
            get_psets(relationship.RelatingGroup)["OSR_CoordinationGroup"][
                "GroupId"
            ]
            for relationship in model.by_guid(row["ifc_guid"]).HasAssignments
            if relationship.is_a("IfcRelAssignsToGroup")
        }
        == {row["coordination_group_id"]}
        for row in index["objects"]
    )
    assert len(model.by_type("IfcPresentationLayerAssignment")) == 4
    layers_by_id = {
        layer.Identifier: layer
        for layer in model.by_type("IfcPresentationLayerAssignment")
    }
    assert set(layers_by_id) == {row["layer_id"] for row in index["layers"]}
    assert sorted(row["asset_count"] for row in index["layers"]) == [2, 10, 34, 49]
    assert sum(len(layer.AssignedItems) for layer in layers_by_id.values()) == 95
    representation_layers = {
        representation.id(): layer.Identifier
        for layer in layers_by_id.values()
        for representation in layer.AssignedItems
    }
    assert len(representation_layers) == 95
    assert all(
        {
            representation_layers[representation.id()]
            for representation in model.by_guid(row["ifc_guid"])
            .Representation.Representations
        }
        == {row["presentation_layer_id"]}
        for row in index["objects"]
    )
    assert len(model.by_type("IfcObjective")) == 9
    assert not model.by_type("IfcMetric")
    assert len(model.by_type("IfcRelAssociatesConstraint")) == 9
    objectives_by_name = {
        objective.Name: objective for objective in model.by_type("IfcObjective")
    }
    assert set(objectives_by_name) == {
        row["constraint_id"] for row in index["constraints"]
    }
    assert all(
        objective.ConstraintGrade == "HARD"
        and objective.ObjectiveQualifier == "DESIGNINTENT"
        and objective.ConstraintSource
        == "mechanical-py/src/osr_mech/civil_systems_integration.py"
        and not objective.BenchmarkValues
        for objective in objectives_by_name.values()
    )
    assert all(
        len(relationship.RelatedObjects) == 1
        and relationship.RelatedObjects[0].is_a("IfcProject")
        for relationship in model.by_type("IfcRelAssociatesConstraint")
    )
    assert not any(
        definition.Name.startswith("Pset_OSR_")
        for ifc_class in (
            "IfcPropertySet",
            "IfcMaterialProperties",
            "IfcProfileProperties",
        )
        for definition in model.by_type(ifc_class)
    )
    assert len(model.by_type("IfcPropertySetTemplate")) == 13
    assert len(model.by_type("IfcSimplePropertyTemplate")) == 77
    assert len(model.by_type("IfcRelDefinesByTemplate")) == 11
    templates_by_name = {
        template.Name: template
        for template in model.by_type("IfcPropertySetTemplate")
    }
    assert set(templates_by_name) == {
        row["name"] for row in index["property_set_templates"]
    }
    assert templates_by_name["OSR_MaterialStatus"].TemplateType == (
        "PSET_MATERIALDRIVEN"
    )
    assert templates_by_name["OSR_Profile"].TemplateType == "PSET_PROFILEDRIVEN"
    quantity_templates = {
        template.Name: template.TemplateType
        for template in templates_by_name["OSR_CoordinationEnvelopeQuantities"]
        .HasPropertyTemplates
    }
    assert quantity_templates["OverallLength"] == "Q_LENGTH"
    assert quantity_templates["SourceNetVolume"] == "Q_VOLUME"
    assert sum(
        len(relationship.RelatedPropertySets)
        for relationship in model.by_type("IfcRelDefinesByTemplate")
    ) == 220
    declared_templates = {
        definition
        for relationship in model.by_type("IfcRelDeclares")
        for definition in relationship.RelatedDefinitions
        if definition.is_a("IfcPropertySetTemplate")
    }
    assert declared_templates == set(templates_by_name.values())
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
                "points": [
                    [0.0, 0.0, 10.0],
                    [100.0, 0.0, 12.0],
                    [150.0, 50.0, 15.0],
                ],
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
                "points": [
                    [0.0, 0.0, 10.0],
                    [100.0, 0.0, 12.0],
                    [150.0, 50.0, 15.0],
                ],
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
    assert index["alignment"]["horizontal_segment_count"] == 2
    assert index["alignment"]["vertical_segment_count"] == 2
    assert index["alignment"]["stationing_referent_count"] == 2
    assert index["alignment"]["total_horizontal_length_m"] == pytest.approx(
        170.710678
    )
    assert len(model.by_type("IfcAlignmentSegment")) == 6
    assert {
        segment.DesignParameters.PredefinedType
        for segment in model.by_type("IfcAlignmentSegment")
        if (
            getattr(segment.DesignParameters, "SegmentLength", None) != 0.0
            and getattr(segment.DesignParameters, "HorizontalLength", None) != 0.0
        )
    } == {"LINE", "CONSTANTGRADIENT"}
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

    duplicate = tmp_path / "duplicate-horizontal-point.json"
    duplicate.write_text(
        json.dumps({"points": [[0.0, 0.0, 0.0], [0.0, 0.0, 2.0]]}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="distinct horizontal coordinates"):
        load_alignment(duplicate)
