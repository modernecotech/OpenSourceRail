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
    sequence = json.loads(paths["sequence"].read_text(encoding="utf-8"))
    validation = json.loads(paths["validation"].read_text(encoding="utf-8"))
    ids_report = json.loads(paths["ids_report"].read_text(encoding="utf-8"))
    bcf_index = json.loads(paths["bcf_index"].read_text(encoding="utf-8"))
    model = ifcopenshell.open(str(paths["ifc"]))
    coordination = BcfXml.load(paths["bcf"])

    assert validation["passed"]
    assert ids_report["status"]
    assert ids_report["total_specifications_pass"] == 20
    assert ids_report["total_checks"] == ids_report["total_checks_pass"] == 3340
    assert bcf_index["topic_count"] == 3
    assert coordination is not None
    assert coordination.version.version_id == "3.0"
    assert len(coordination.topics) == 3
    assert index["summary"] == {
        "alignment_stationing_referents": 2,
        "assets": 185,
        "built_systems": 3,
        "bearing_connection_realizations": 60,
        "bearing_connection_relationships": 27,
        "classification_references": 15,
        "classifications": 1,
        "classified_assets": 185,
        "construction_tasks": 18,
        "connected_bearings": 36,
        "connected_pier_caps": 9,
        "connected_superstructure_assets": 13,
        "construction_output_tasks": 5,
        "coordination_groups": 5,
        "constraint_source_document_relationships": 1,
        "document_associated_assets": 185,
        "documents": 15,
        "external_engineering_decisions": 9,
        "foundation_interfaces": 9,
        "functional_systems": 6,
        "grouped_assets": 185,
        "horizontal_alignment_segments": 1,
        "disciplines": {
            "above-track": 10,
            "lineside": 2,
            "substructure": 124,
            "track": 49,
        },
        "ifc_classes": {
            "IfcBeam": 21,
            "IfcBearing": 36,
            "IfcColumn": 9,
            "IfcElementAssembly": 1,
            "IfcRail": 32,
            "IfcRoof": 4,
            "IfcSlab": 33,
            "IfcVehicle": 2,
            "IfcVirtualElement": 47,
        },
        "interface_checks": 9,
        "interface_constraint_asset_links": 91,
        "interface_constraint_group_links": 6,
        "interface_constraint_related_objects": 107,
        "interface_constraint_system_links": 1,
        "interface_constraints": 9,
        "interface_metrics": 6,
        "jacking_interfaces": 36,
        "layer_associated_assets": 185,
        "material_associated_assets": 46,
        "materials": 3,
        "native_bearings": 36,
        "native_rolling_stock_vehicles": 2,
        "profiled_assets": 32,
        "profiles": 1,
        "presentation_layers": 4,
        "planning_rate_items": 3,
        "planning_rate_schedules": 1,
        "pier_caps": 9,
        "pier_columns": 9,
        "property_set_templates": 16,
        "property_templates": 99,
        "qualitative_only_interface_constraints": 3,
        "system_associated_assets": 185,
        "system_spatial_part_references": 7,
        "scheduled_physical_assets": 134,
        "source_linked_constraint_resources": 15,
        "template_linked_definitions": 483,
        "template_matched_definitions": 487,
        "typed_assets": 138,
        "types": 19,
        "vehicle_base_quantity_sets": 2,
        "virtual_review_gate_assets": 45,
        "vertical_alignment_segments": 1,
    }
    assert index["cost_model"]["maturity"] == "planning-target-not-a-quotation"
    with (Path(__file__).resolve().parents[3] / "lib/templates/civil-cost-model.toml").open(
        "rb"
    ) as handle:
        expected_cost_model = tomllib.load(handle)
    assert index["cost_model"]["civil_usd_per_km"] == expected_cost_model[
        "civil_usd_per_km"
    ]
    cost_schedule = model.by_type("IfcCostSchedule")
    cost_items = {
        item.Identification: item for item in model.by_type("IfcCostItem")
    }
    assert len(cost_schedule) == 1
    assert cost_schedule[0].Identification == "OSR-COST-RATES-001"
    assert cost_schedule[0].PredefinedType == "SCHEDULEOFRATES"
    assert cost_schedule[0].Status == "planning-target-not-a-quotation"
    assert index["cost_schedule"]["source_sha256"] == index["cost_model"]["sha256"]
    assert index["cost_schedule"]["scope_boundary"].endswith("project total")
    assert set(cost_items) == {
        "OSR-RATE-AT-GRADE",
        "OSR-RATE-ELEVATED",
        "OSR-RATE-BRIDGE",
    }
    assert len(model.by_type("IfcCostValue")) == 3
    assert len(model.by_type("IfcMonetaryUnit")) == 1
    assert model.by_type("IfcMonetaryUnit")[0].Currency == "USD"
    for rate_row in index["cost_schedule"]["items"]:
        item = cost_items[rate_row["rate_id"]]
        assert not item.CostQuantities
        assert not item.Controls
        assert len(item.CostValues) == 1
        value = item.CostValues[0]
        assert value.AppliedValue.wrappedValue == rate_row["rate_usd_per_route_km"]
        assert value.UnitBasis.ValueComponent.wrappedValue == 1_000.0
        assert value.UnitBasis.UnitComponent.UnitType == "LENGTHUNIT"
        assert value.Category == "PLANNING_TARGET"
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
    assert {task_id: len(asset_ids) for task_id, asset_ids in sequence["product_assignments"].items()} == {
        "STN-40": 9,
        "TRK-50": 5,
        "VIA-05": 18,
        "VIA-50": 48,
        "VIA-60": 54,
    }
    assert {task_id: len(asset_ids) for task_id, asset_ids in sequence["review_gate_assignments"].items()} == {
        "VIA-05": 9,
        "VIA-50": 36,
    }
    assigned_asset_ids = {
        asset_id
        for asset_ids in sequence["product_assignments"].values()
        for asset_id in asset_ids
    }
    review_gate_asset_ids = {
        asset_id
        for asset_ids in sequence["review_gate_assignments"].values()
        for asset_id in asset_ids
    }
    assert assigned_asset_ids.isdisjoint(review_gate_asset_ids)
    assert {
        row["asset_class"] for row in index["objects"] if row["asset_id"] in review_gate_asset_ids
    } == {"civil.foundation-interface", "civil.jacking-interface"}
    task_product_relationships = model.by_type("IfcRelAssignsToProduct")
    assert len(task_product_relationships) == 179
    assert sum(len(relationship.RelatedObjects) for relationship in task_product_relationships) == 179
    assert sum(
        relationship.Name == "OSR physical construction output"
        for relationship in task_product_relationships
    ) == 134
    assert sum(
        relationship.Name == "OSR virtual review interface"
        and relationship.RelatingProduct.is_a() == "IfcVirtualElement"
        for relationship in task_product_relationships
    ) == 45
    assert len({item.Tag for item in model.by_type("IfcElement") if item.Tag}) == 185
    assert len(model.by_type("IfcTypeProduct")) == 19
    assert len(model.by_type("IfcVehicle")) == 2
    assert len(model.by_type("IfcVehicleType")) == 1
    assert not model.by_type("IfcBuildingElementProxy")
    assert not model.by_type("IfcBuildingElementProxyType")
    assert len(model.by_type("IfcBearing")) == 36
    assert len(model.by_type("IfcBearingType")) == 1
    bearing_connections = model.by_type("IfcRelConnectsWithRealizingElements")
    assert len(bearing_connections) == 27
    assert sum(len(connection.RealizingElements) for connection in bearing_connections) == 60
    assert all(
        connection.ConnectionType == "elastomeric/PTFE support"
        and connection.ConnectionGeometry is None
        and connection.RelatingElement.is_a("IfcBeam")
        and connection.RelatedElement.is_a() in {"IfcBeam", "IfcSlab"}
        and all(bearing.is_a("IfcBearing") for bearing in connection.RealizingElements)
        for connection in bearing_connections
    )
    assert sorted(
        len(bearing.IsConnectionRealization) for bearing in model.by_type("IfcBearing")
    ) == [1] * 12 + [2] * 24
    assert len(model.by_type("IfcRelDefinesByType")) == 19
    assert sum(
        len(relationship.RelatedObjects)
        for relationship in model.by_type("IfcRelDefinesByType")
    ) == 138
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
        vehicle.IsTypedBy[0].RelatingType.is_a() == "IfcVehicleType"
        and vehicle.IsTypedBy[0].RelatingType.PredefinedType == "ROLLINGSTOCK"
        and set(get_psets(vehicle)["Qto_VehicleBaseQuantities"])
        >= {"Length", "Width", "Height"}
        for vehicle in model.by_type("IfcVehicle")
    )
    assert all(
        bearing.IsTypedBy[0].RelatingType.is_a() == "IfcBearingType"
        and bearing.IsTypedBy[0].RelatingType.PredefinedType == "ELASTOMERIC"
        and get_psets(bearing)["OSR_BearingStatus"]["BearingFamily"]
        == "elastomeric/PTFE"
        and get_psets(bearing)["OSR_BearingStatus"]["SupplierSelectionStatus"]
        == "unresolved"
        and get_psets(bearing)["OSR_BearingConnectivity"]["RealizedConnectionCount"]
        == len(bearing.IsConnectionRealization)
        for bearing in model.by_type("IfcBearing")
    )
    assert len(index["bearing_connections"]) == 27
    assert sum(
        connection["realizing_bearing_count"]
        for connection in index["bearing_connections"]
    ) == 60
    assert all(
        row["bearing_connection_count"] in {1, 2}
        and len(row["bearing_connection_ids"]) == row["bearing_connection_count"]
        for row in index["objects"]
        if row["ifc_class"] == "IfcBearing"
    )
    foundation_rows = [
        row for row in index["objects"] if row["asset_class"] == "civil.foundation-interface"
    ]
    assert len(foundation_rows) == 9
    assert all(
        model.by_guid(row["ifc_guid"]).is_a() == "IfcVirtualElement"
        and get_psets(model.by_guid(row["ifc_guid"]))[
            "OSR_FoundationInterfaceStatus"
        ]["ActualFoundationDepth"]
        == "intentionally-not-modelled"
        and row["source_part_role"] == "foundation-interface"
        for row in foundation_rows
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
    cost_document = next(
        row
        for row in index["documents"]
        if row["document_id"] == "OSR-DOC-CIVIL-COST-CONTRACT"
    )
    assert cost_document["associated_cost_schedule"]
    assert cost_document["associated_object_count"] == 2
    constraint_source_document = next(
        row
        for row in index["documents"]
        if row["document_id"] == "OSR-DOC-SOURCE-CIVIL-INTEGRATION"
    )
    expected_constraint_resource_ids = sorted(
        [row["constraint_id"] for row in index["constraints"]]
        + [row["metric"]["metric_id"] for row in index["constraints"] if row["metric"]]
    )
    assert constraint_source_document["associated_constraint_count"] == 15
    assert constraint_source_document["associated_constraint_ids"] == (
        expected_constraint_resource_ids
    )
    assert len(model.by_type("IfcClassification")) == 1
    assert len(model.by_type("IfcClassificationReference")) == 15
    assert len(model.by_type("IfcRelAssociatesClassification")) == 16
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
    assert classification_pset["ReferenceCount"] == 15
    assert (
        classification_pset["ExternalMappingStatus"]
        == "country-and-client-mapping-not-nominated"
    )
    assert (
        len(
            [
                group
                for group in model.by_type("IfcGroup")
                if group.is_a() == "IfcGroup"
            ]
        )
        == 5
    )
    assert len(model.by_type("IfcSystem")) == 6
    assert len(model.by_type("IfcBuiltSystem")) == 3
    assert len(model.by_type("IfcRelAssignsToGroup")) == 11
    assert sorted(row["asset_count"] for row in index["groups"]) == [1, 2, 11, 12, 159]
    assert sum(
        len(relationship.RelatedObjects)
        for relationship in model.by_type("IfcRelAssignsToGroup")
        if relationship.RelatingGroup.is_a() == "IfcGroup"
    ) == 185
    groups_by_id = {
        get_psets(group)["OSR_CoordinationGroup"]["GroupId"]: group
        for group in model.by_type("IfcGroup")
        if group.is_a() == "IfcGroup"
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
            and relationship.RelatingGroup.is_a() == "IfcGroup"
        }
        == {row["coordination_group_id"]}
        for row in index["objects"]
    )
    systems_by_id = {
        system.ObjectType: system for system in model.by_type("IfcSystem")
    }
    assert set(systems_by_id) == {row["system_id"] for row in index["systems"]}
    assert sum(row["asset_count"] for row in index["systems"]) == 185
    assert sum(
        len(relationship.RelatedObjects)
        for relationship in model.by_type("IfcRelAssignsToGroup")
        if relationship.RelatingGroup.is_a("IfcSystem")
    ) == 185
    assert all(
        systems_by_id[row["system_id"]].Name == row["name"]
        and systems_by_id[row["system_id"]].Description == row["description"]
        and systems_by_id[row["system_id"]].is_a() == row["ifc_class"]
        and getattr(systems_by_id[row["system_id"]], "PredefinedType", None)
        == row["ifc_predefined_type"]
        and row["spatial_meaning"] == "none; not an IfcSpatialZone"
        and row["operational_status"]
        == "design-reference; not commissioned or operational"
        for row in index["systems"]
    )
    assert all(
        {
            relationship.RelatingGroup.ObjectType
            for relationship in model.by_guid(row["ifc_guid"]).HasAssignments
            if relationship.is_a("IfcRelAssignsToGroup")
            and relationship.RelatingGroup.is_a("IfcSystem")
        }
        == {row["functional_system_id"]}
        for row in index["objects"]
    )
    assert {
        system.ObjectType: getattr(system, "PredefinedType", None)
        for system in model.by_type("IfcSystem")
    } == {
        "OSR-SYS-CIVIL-INTERFACES": None,
        "OSR-SYS-CLEARANCE": None,
        "OSR-SYS-GUIDEWAY": "LOADBEARING",
        "OSR-SYS-ROLLING-STOCK": None,
        "OSR-SYS-STATION": "USERDEFINED",
        "OSR-SYS-TRACK": "RAILWAYTRACK",
    }
    spatial_system_relationships = model.by_type(
        "IfcRelReferencedInSpatialStructure"
    )
    assert len(spatial_system_relationships) == 4
    assert sum(
        len(relationship.RelatedElements)
        for relationship in spatial_system_relationships
    ) == 7
    assert all(
        {
            relationship.RelatingStructure.Name
            for relationship in systems_by_id[row["system_id"]].ReferencedInStructures
        }
        == set(row["spatial_part_names"])
        for row in index["systems"]
    )
    assert len(model.by_type("IfcPresentationLayerAssignment")) == 4
    layers_by_id = {
        layer.Identifier: layer
        for layer in model.by_type("IfcPresentationLayerAssignment")
    }
    assert set(layers_by_id) == {row["layer_id"] for row in index["layers"]}
    assert sorted(row["asset_count"] for row in index["layers"]) == [2, 10, 49, 124]
    assert sum(len(layer.AssignedItems) for layer in layers_by_id.values()) == 185
    representation_layers = {
        representation.id(): layer.Identifier
        for layer in layers_by_id.values()
        for representation in layer.AssignedItems
    }
    assert len(representation_layers) == 185
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
    assert len(model.by_type("IfcMetric")) == 6
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
        == "design/component-catalogue/src/osr_mech/civil_systems_integration.py"
        for objective in objectives_by_name.values()
    )
    metrics_by_name = {metric.Name: metric for metric in model.by_type("IfcMetric")}
    constraint_relationships = {
        relationship.RelatingConstraint.Name: relationship
        for relationship in model.by_type("IfcRelAssociatesConstraint")
    }
    assert sum(
        len(relationship.RelatedObjects)
        for relationship in constraint_relationships.values()
    ) == 107
    for row in index["constraints"]:
        relationship = constraint_relationships[row["constraint_id"]]
        observed_scope_ids = set()
        for related in relationship.RelatedObjects:
            if related.is_a("IfcProject"):
                observed_scope_ids.add("IfcProject")
            elif related.is_a() == "IfcGroup":
                observed_scope_ids.add(
                    get_psets(related)["OSR_CoordinationGroup"]["GroupId"]
                )
            elif related.is_a("IfcSystem"):
                observed_scope_ids.add(related.ObjectType)
            else:
                observed_scope_ids.add(related.Tag)
        assert relationship.Intent == "DESIGN VALIDATION EVIDENCE"
        assert len(relationship.RelatedObjects) == row["related_object_count"]
        assert observed_scope_ids == {
            "IfcProject",
            *row["related_asset_ids"],
            *row["related_group_ids"],
            *row["related_system_ids"],
        }
        assert row["external_source_document_ids"] == [
            "OSR-DOC-SOURCE-CIVIL-INTEGRATION"
        ]
        assert row["external_reference_relationship"] == (
            "IfcExternalReferenceRelationship"
        )
        metric_row = row["metric"]
        benchmark_values = list(objectives_by_name[row["constraint_id"]].BenchmarkValues or [])
        if metric_row is None:
            assert not benchmark_values
            assert row["metric_status"] == (
                "qualitative-objective; no fabricated numeric benchmark"
            )
        else:
            metric = metrics_by_name[metric_row["metric_id"]]
            assert benchmark_values == [metric]
            assert metric.Benchmark == "EQUALTO"
            assert metric.DataValue.is_a() == "IfcLengthMeasure"
            assert metric.DataValue.wrappedValue == pytest.approx(
                metric_row["target_value"]
            )
            assert metric_row["observed_value"] == pytest.approx(
                metric_row["target_value"]
            )
            assert metric.ReferencePath is None
            assert row["metric_status"] == "structured-native-ifc-metric"
    constraint_source_links = model.by_type("IfcExternalReferenceRelationship")
    assert len(constraint_source_links) == 1
    assert constraint_source_links[0].Name == "OSR constraint source-document linkage"
    assert constraint_source_links[0].RelatingReference == document_references[
        "OSR-DOC-SOURCE-CIVIL-INTEGRATION"
    ]
    assert {
        constraint.Name
        for constraint in constraint_source_links[0].RelatedResourceObjects
    } == set(expected_constraint_resource_ids)
    assert all(
        len(constraint.HasExternalReferences) == 1
        for constraint in [*objectives_by_name.values(), *metrics_by_name.values()]
    )
    assert index["capability_closure"] == {
        "status": "source-supported-ifc-work-complete",
        "implementable_open_task_count": 0,
        "external_decision_count": 9,
        "boundary": (
            "Further promotion requires named external engineering, client, "
            "supplier, commercial, survey or information-management evidence."
        ),
    }
    assert len(index["external_engineering_decisions"]) == 9
    assert len(
        {row["decision_id"] for row in index["external_engineering_decisions"]}
    ) == 9
    assert all(
        row["status"] == "external-evidence-required"
        and row["authority_required"]
        and row["evidence_required"]
        and row["blocked_capabilities"]
        and row["safe_current_state"]
        for row in index["external_engineering_decisions"]
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
    assert len(model.by_type("IfcPropertySetTemplate")) == 16
    assert len(model.by_type("IfcSimplePropertyTemplate")) == 99
    assert len(model.by_type("IfcRelDefinesByTemplate")) == 14
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
    ) == 483
    declared_templates = {
        definition
        for relationship in model.by_type("IfcRelDeclares")
        for definition in relationship.RelatedDefinitions
        if definition.is_a("IfcPropertySetTemplate")
    }
    assert declared_templates == set(templates_by_name.values())
    assert len(model.by_type("IfcElementQuantity")) == 187
    assert {
        quantity_set.Name for quantity_set in model.by_type("IfcElementQuantity")
    } == {"OSR_CoordinationEnvelopeQuantities", "Qto_VehicleBaseQuantities"}
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
