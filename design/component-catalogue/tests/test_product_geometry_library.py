"""Completeness and assembly tests for the split LM3 CAD/IFC library."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import ifcopenshell

from engineering.interchange.lm3_product_ifc_library import (
    MANIFEST,
    REPO_ROOT,
    descendants,
    export_assembly,
    export_part,
    graph,
)
from osr_mech.rolling_stock.product_geometry import (
    flatten_geometry,
    geometry_specs,
    product_geometry,
)


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_geometry_registry_exactly_covers_product_tree_and_envelopes() -> None:
    manifest = _manifest()
    product_ids = {str(item["id"]) for item in manifest["product_items"]}
    specs = geometry_specs()
    assert set(specs) == product_ids
    assert len(specs) == 101

    primitive_count = 0
    for product_id, spec in specs.items():
        geometry = product_geometry(product_id)
        leaves = flatten_geometry(geometry)
        primitive_count += len(leaves)
        assert leaves
        assert all(leaf.bounding_box().volume > 0.0 and leaf.volume > 0.0 for leaf in leaves)
        bounds = geometry.bounding_box()
        actual = (
            bounds.max.X - bounds.min.X,
            bounds.max.Y - bounds.min.Y,
            bounds.max.Z - bounds.min.Z,
        )
        assert all(value <= limit + 1e-6 for value, limit in zip(actual, spec.envelope_mm))
    assert primitive_count == 534


def test_geometry_forms_cover_key_build_and_bought_in_systems() -> None:
    specs = geometry_specs()
    assert specs["LM3-BDY-P020"].form == "underframe"
    assert specs["LM3-BOG-P010"].form == "bogie-frame"
    assert specs["LM3-BOG-P040"].form == "wheelset"
    assert specs["LM3-TRC-P010"].form == "motor"
    assert specs["LM3-EXT-P010"].form == "door-cassette"
    assert specs["LM3-WIN-P010"].form == "window-frame"
    assert specs["LM3-LGT-P010"].form == "light"


def test_recovery_kit_has_separate_inspectable_hardware() -> None:
    leaves = flatten_geometry(product_geometry("LM3-BDY-P120"))
    labels = [leaf.label for leaf in leaves]
    assert sum("replaceable jack pad" in label for label in labels) == 4
    assert sum("proof-marked lifting eye" in label for label in labels) == 2
    assert sum("towing/rerailing lug" in label for label in labels) == 2
    assert sum("recovery datum/label plate" in label for label in labels) == 2


def test_assembly_graph_is_acyclic_complete_and_reaches_final_trainset() -> None:
    products, assemblies = graph(_manifest())
    assert len(products) == 101
    assert len(assemblies) == 26
    root_products, root_assemblies = descendants("LM3-TRAINSET-A000", products, assemblies)
    active = {
        product_id
        for product_id, item in products.items()
        if int(item["quantity_per_trainset"]) > 0
    }
    assert active.issubset(root_products)
    assert "LM3-TRAINSET-A000" in root_assemblies
    for assembly_id in assemblies:
        product_ids, assembly_ids = descendants(assembly_id, products, assemblies)
        assert product_ids
        assert len(product_ids) == len(set(product_ids))
        assert len(assembly_ids) == len(set(assembly_ids))


def test_split_ifc_part_and_subassembly_round_trip_deterministically(tmp_path: Path) -> None:
    products, assemblies = graph(_manifest())
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()

    part_name = "LM3-BOG-P040.ifc"
    first_part = export_part(products["LM3-BOG-P040"], first / part_name)
    second_part = export_part(products["LM3-BOG-P040"], second / part_name)
    assert first_part["passed"] and second_part["passed"]
    assert first_part["primitive_count"] == 5
    assert hashlib.sha256((first / part_name).read_bytes()).digest() == hashlib.sha256(
        (second / part_name).read_bytes()
    ).digest()

    assembly_name = "LM3-BOG-SA610.ifc"
    first_assembly = export_assembly("LM3-BOG-SA610", products, assemblies, first / assembly_name)
    second_assembly = export_assembly("LM3-BOG-SA610", products, assemblies, second / assembly_name)
    assert first_assembly["passed"] and second_assembly["passed"]
    assert hashlib.sha256((first / assembly_name).read_bytes()).digest() == hashlib.sha256(
        (second / assembly_name).read_bytes()
    ).digest()

    reopened = ifcopenshell.open(str(first / assembly_name))
    expected_products, expected_assemblies = descendants("LM3-BOG-SA610", products, assemblies)
    tags = {
        str(item.Tag)
        for item in reopened.by_type("IfcProduct")
        if getattr(item, "Tag", None)
    }
    assert set(expected_products) | set(expected_assemblies) <= tags
    represented = {
        str(item.Tag)
        for item in reopened.by_type("IfcProduct")
        if getattr(item, "Tag", None) and getattr(item, "Representation", None)
    }
    assert set(expected_products) <= represented


def test_tracked_split_libraries_match_indexes_and_saved_validation() -> None:
    indexes = (
        REPO_ROOT / "engineering/models/bim/reference/lm3-product-library.index.json",
        REPO_ROOT / "design/component-catalogue/models/cad/lm3-product-library.index.json",
    )
    for index_path in indexes:
        index = json.loads(index_path.read_text(encoding="utf-8"))
        assert index["passed"] is True
        assert index["product_count"] == 101
        assert index["assembly_count"] == 26
        for entry in [*index["parts"], *index["assemblies"]]:
            artifact = REPO_ROOT / entry["file"]
            assert artifact.is_file()
            assert hashlib.sha256(artifact.read_bytes()).hexdigest() == entry["sha256"]
        if "all_active_products_reach_root" in index:
            assert index["all_active_products_reach_root"] is True
            assert all(entry["reopen_validated"] for entry in [*index["parts"], *index["assemblies"]])
            assert all(entry["native_shape_count"] > 0 for entry in [*index["parts"], *index["assemblies"]])
        else:
            assert index["all_active_products_reach_final_assembly"] is True
            assert all(entry["passed"] for entry in [*index["parts"], *index["assemblies"]])
