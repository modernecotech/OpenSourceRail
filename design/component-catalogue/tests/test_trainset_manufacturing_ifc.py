from __future__ import annotations

import hashlib

import ifcopenshell
from ifcopenshell.util.element import get_psets

from engineering.interchange.trainset_manufacturing_ifc import build_model, write
from osr_mech.rolling_stock.product_geometry import geometry_specs


def test_manufacturing_ifc_contains_complete_product_methods_and_tooling() -> None:
    model, index = build_model()
    assert model.schema == "IFC4X3"
    assert index["product_item_count"] == 101
    assert index["assembly_count"] == 26
    assert index["method_count"] == 9
    assert index["task_count"] == 59
    assert index["tooling_count"] == 20
    assert index["tooling_representation_part_count"] >= 200
    assert index["product_geometry_count"] == 101
    assert index["product_representation_part_count"] == 523
    assert index["supplier_anchor_count"] == 25
    assert index["supplier_anchored_external_product_count"] == 54
    assert len(model.by_type("IfcVehicle")) == 1
    assert len(model.by_type("IfcMechanicalFastener")) == 1
    assert len(model.by_type("IfcDoor")) == 1
    assert len(model.by_type("IfcWindow")) == 2
    assert len(model.by_type("IfcFurniture")) == 3
    assert len(model.by_type("IfcCovering")) == 5
    assert len(model.by_type("IfcElectricMotor")) == 1
    # Includes semantic subtypes such as furniture, lights and fasteners.
    assert len(model.by_type("IfcDiscreteAccessory")) == 30
    assert len(model.by_type("IfcShapeRepresentation")) == 121
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
