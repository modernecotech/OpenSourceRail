from __future__ import annotations

import hashlib
import json

import ifcopenshell
import pytest
from ifcopenshell.util.element import get_psets

from engineering.interchange.trainset_manufacturing_ifc import (
    build_model,
    write,
    write_and_validate_lm3_ids,
)
from osr_mech.rolling_stock.product_geometry import geometry_specs


def test_manufacturing_ifc_contains_complete_product_methods_and_tooling() -> None:
    model, index = build_model()
    assert model.schema == "IFC4X3"
    assert index["product_item_count"] == 120
    assert index["assembly_count"] == 26
    assert index["method_count"] == 9
    assert index["task_count"] == 59
    assert index["tooling_count"] == 30
    assert index["tooling_representation_part_count"] >= 200
    assert index["product_geometry_count"] == 120
    assert index["product_representation_part_count"] == 619
    assert index["supplier_anchor_count"] == 27
    assert index["supplier_anchored_external_product_count"] == 56
    assert index["mechanically_controlled_object_count"] == 39
    assert index["mechanical_interface_count"] == 12
    assert index["route_compatibility_gate_count"] == 7
    assert len(model.by_type("IfcVehicle")) == 1
    assert len(model.by_type("IfcMechanicalFastener")) == 1
    assert len(model.by_type("IfcDoor")) == 1
    assert len(model.by_type("IfcWindow")) == 2
    assert len(model.by_type("IfcFurniture")) == 3
    assert len(model.by_type("IfcCovering")) == 12
    assert len(model.by_type("IfcElectricMotor")) == 1
    # Includes semantic subtypes such as furniture, lights and fasteners.
    assert len(model.by_type("IfcDiscreteAccessory")) == 40
    assert len(model.by_type("IfcShapeRepresentation")) == 150
    represented_product_tags = {
        str(item.Tag)
        for item in model.by_type("IfcElement")
        if getattr(item, "Tag", "") and item.Representation
    }
    assert represented_product_tags.issuperset(geometry_specs())


def test_ifc_properties_keep_release_boundary_and_detailed_window_spec() -> None:
    model, _ = build_model()
    project_psets = get_psets(model.by_type("IfcProject")[0])
    assert project_psets["OSR_ManufacturingReference"]["Status"] == "design-reference-not-released"
    assert "Not a construction release" in project_psets["OSR_ManufacturingReference"]["ReleaseBoundary"]
    assert project_psets["OSR_DesignDetailRegister"]["MechanicalInterfaceCount"] == 12
    assert "not fabrication or construction release" in project_psets["OSR_DesignDetailRegister"]["ReleaseBoundary"]
    window = next(item for item in model.by_type("IfcElement") if item.Tag == "LM3-WIN-P010")
    values = get_psets(window)["OSR_ProductDefinition"]
    assert "aluminium" in values["MaterialFamily"]
    assert "elastomer" in values["MaterialFamily"]
    assert "timed cassette removal/refit" in values["InspectionMethods"]
    motor = next(item for item in model.by_type("IfcElement") if item.Tag == "LM3-TRC-P010")
    anchor = get_psets(motor)["OSR_SupplierAnchor"]
    assert anchor["Manufacturer"] == "ABB"
    assert anchor["ProductFamily"] == "AMXM railway traction motor"
    assert anchor["LocalEquivalentAllowed"] is True
    control = get_psets(motor)["OSR_MechanicalInterfaceControl"]
    assert control["InterfaceIds"] == "LM3-ICD-008"
    assert "LM3-LC-002" in control["LoadCaseIds"]
    assert control["ToleranceStatus"] == "allocation-open-until-stack-and-supplier-freeze"


def test_written_ifc_is_deterministic_and_round_trips(tmp_path) -> None:
    first = tmp_path / "first.ifc"
    second = tmp_path / "second.ifc"
    first_index = tmp_path / "first.json"
    second_index = tmp_path / "second.json"
    assert write(first, first_index)["passed"]
    assert write(second, second_index)["passed"]
    assert hashlib.sha256(first.read_bytes()).digest() == hashlib.sha256(second.read_bytes()).digest()
    reopened = ifcopenshell.open(str(first))
    assert reopened.schema == "IFC4X3"
    assert len(reopened.by_type("IfcTask")) == 59


def test_lm3_ids_validates_provenance_product_graph_and_mechanical_controls(tmp_path) -> None:
    ifc_path = tmp_path / "lm3.ifc"
    assert write(ifc_path, tmp_path / "index.json")["passed"]
    result = write_and_validate_lm3_ids(
        ifc_path,
        tmp_path / "requirements.ids",
        tmp_path / "report.json",
    )
    assert result["status"] is True
    assert len(result["specifications"]) == 4
    assert {row["total_applicable"] for row in result["specifications"]} == {1, 26, 39, 120}
    saved = json.loads((tmp_path / "report.json").read_text())
    assert saved["schema"] == "org.opensourcerail.lm3-ids-report.v1"
    assert saved["status"] is True
    first_ids = (tmp_path / "requirements.ids").read_bytes()
    first_report = (tmp_path / "report.json").read_bytes()
    write_and_validate_lm3_ids(
        ifc_path,
        tmp_path / "requirements.ids",
        tmp_path / "report.json",
    )
    assert (tmp_path / "requirements.ids").read_bytes() == first_ids
    assert (tmp_path / "report.json").read_bytes() == first_report


def test_lm3_ids_rejects_a_controlled_object_without_its_interface_pset(tmp_path) -> None:
    model, _ = build_model()
    motor = next(item for item in model.by_type("IfcElement") if item.Tag == "LM3-TRC-P010")
    relationship = next(
        rel
        for rel in model.by_type("IfcRelDefinesByProperties")
        if motor in rel.RelatedObjects
        and rel.RelatingPropertyDefinition.Name == "OSR_MechanicalInterfaceControl"
    )
    model.remove(relationship)
    broken = tmp_path / "broken.ifc"
    model.write(str(broken))
    with pytest.raises(ValueError, match="failed its IDS"):
        write_and_validate_lm3_ids(
            broken,
            tmp_path / "requirements.ids",
            tmp_path / "report.json",
        )
