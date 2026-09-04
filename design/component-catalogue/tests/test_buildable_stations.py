from __future__ import annotations

import csv
import json
from pathlib import Path

from osr_mech.buildable_stations import (
    DEFAULT_TEMPLATE,
    _template_archetypes,
    open_release_items,
    render_gap_register,
    render_traveler,
    render_variant_page,
    station_variant,
    write_outputs,
)
from osr_mech.common import ConsistFamily, StationArchetype


def _variants():
    configs = _template_archetypes(DEFAULT_TEMPLATE)
    return {
        archetype: station_variant(archetype, configs[archetype.value])
        for archetype in StationArchetype
    }


def test_every_station_catalogue_entry_has_a_resolved_product_tree() -> None:
    variants = _variants()
    assert len(variants) == 7
    for variant in variants.values():
        item_ids = {item.id for item in variant.product_items}
        assembly_ids = {node.id for node in variant.assemblies}
        assert len(item_ids) == len(variant.product_items)
        assert "STN-STATION-A900" in assembly_ids
        for item in variant.product_items:
            assert item.quantity > 0
            assert item.parent in assembly_ids
            assert item.acceptance
            assert item.source_refs
        for node in variant.assemblies:
            assert node.instructions
            assert node.hold_points
            assert set(node.children) <= item_ids | assembly_ids
        product_owners = {
            item_id: [node.id for node in variant.assemblies if item_id in node.children]
            for item_id in item_ids
        }
        for item in variant.product_items:
            assert product_owners[item.id] == [item.parent]


def test_standard_light_metro_station_quantities_match_geometry_and_template() -> None:
    standard = _variants()[StationArchetype.STANDARD]
    items = {item.id: item for item in standard.product_items}
    assert standard.parameters["platform_length_m"] == 59.5
    assert standard.parameters["canopy_bays_per_platform"] == 10
    assert standard.parameters["total_canopy_bays"] == 20
    assert standard.parameters["platform_canopy_area_m2"] == 504.0
    assert standard.parameters["auxiliary_canopy_required_area_m2"] == 1296.0
    assert standard.parameters["auxiliary_canopy_module_count"] == 7
    assert standard.parameters["auxiliary_canopy_installed_area_m2"] == 1309.0
    assert items["STN-CIV-P010"].quantity == 10
    assert items["STN-CIV-P040"].quantity == 40
    assert items["STN-CNP-P020"].quantity == 22
    assert items["STN-CNP-P030"].quantity == 20
    assert items["STN-CHG-P010"].quantity == 500
    assert items["STN-CNP-P050"].quantity == 7
    assert items["STN-CNP-P060"].quantity == 8
    assert items["STN-CNP-P070"].quantity == 16
    assert items["STN-CNP-P050"].maturity == "buildable-after-supplier-and-structural-release"
    assert items["STN-PAX-P070"].quantity == 4
    assert items["STN-PAX-P080"].quantity == 2


def test_variant_specific_station_components_are_not_hidden_in_prose() -> None:
    variants = _variants()
    elevated = {item.id: item for item in variants[StationArchetype.INTERCHANGE_ELEVATED].product_items}
    terminal = {item.id for item in variants[StationArchetype.TERMINAL].product_items}
    depot = {item.id for item in variants[StationArchetype.DEPOT_TERMINAL].product_items}
    assert elevated["STN-ACC-P020"].quantity == 4
    assert elevated["STN-ACC-P030"].quantity == 2
    assert "STN-CIV-P040" not in elevated
    assert {f"STN-TRK-P0{i}0" for i in range(1, 8)} <= terminal
    assert {f"STN-TRK-P0{i}0" for i in range(1, 8)} | {
        f"STN-DEP-P0{i}0" for i in range(1, 8)
    } <= depot
    terminal_variant = variants[StationArchetype.TERMINAL]
    terminal_items = {item.id: item for item in terminal_variant.product_items}
    assert terminal_variant.parameters["turnout_tangent"] == "1:9"
    assert terminal_variant.parameters["turnout_total_length_m"] == 27
    assert terminal_items["STN-TRK-P030"].quantity == 42
    assert terminal_items["STN-TRK-P070"].quantity == 2
    depot_variant = variants[StationArchetype.DEPOT_TERMINAL]
    depot_items = {item.id: item for item in depot_variant.product_items}
    assert depot_variant.parameters["depot_archetype"] == "main-heavy"
    assert depot_variant.parameters["depot_reference_stalls"] == 4
    assert depot_variant.parameters["depot_throat_turnouts"] == 2
    assert depot_items["STN-DEP-P020"].quantity == 400
    assert depot_items["STN-DEP-P040"].quantity == 4
    assert "outdoor/open-sided" in depot_items["STN-DEP-P040"].title
    assert "supplier loss/duty and maximum-ambient declaration" in depot_items["STN-DEP-P040"].acceptance
    assert "separated outdoor" in depot_items["STN-DEP-P050"].title
    assert "cell-to-pack propagation and heat-release evidence" in depot_items["STN-DEP-P050"].acceptance
    assert "cooled controls room" in depot_items["STN-DEP-P070"].title
    assert "2 x 30 kW packaged-DX schedule and 30 kW single-unit thermal duty proof" in depot_items["STN-DEP-P070"].acceptance
    assert "STN-PAX-P050" not in {
        item.id for item in variants[StationArchetype.HALT].product_items
    }


def test_station_gap_register_is_derived_from_nonreleased_bom_rows() -> None:
    variants = tuple(_variants().values())
    gaps = open_release_items(variants)
    rendered = render_gap_register(variants)
    assert gaps
    assert all(gap["maturity"] != "release-candidate" for gap in gaps)
    assert {"STN-CNP-P050", "STN-CNP-P060", "STN-CNP-P070"} <= {
        str(gap["engineering_id"]) for gap in gaps
    }
    assert "`STN-CNP-P050`" in rendered
    assert "Package-level exclusions" in rendered


def test_station_traveler_reuses_the_same_bom_ids() -> None:
    standard = _variants()[StationArchetype.STANDARD]
    traveler = render_traveler(standard)
    for item in standard.product_items:
        assert f"`{item.id}`" in traveler
    for node in standard.assemblies:
        assert f"`{node.id}`" in traveler
    assert "unsigned template" in traveler
    assert "operator/AOR handover" in traveler


def test_station_variant_page_bridges_every_product_and_assembly_id() -> None:
    variants = _variants()
    standard = variants[StationArchetype.STANDARD]
    for variant in variants.values():
        rendered = render_variant_page(variant, standard)
        assert "deterministic design-reference package" in rendered
        assert "installed/exploded" in rendered
        for item in variant.product_items:
            assert f"`{item.id}`" in rendered
            assert f"`{item.id}-DRW-{variant.archetype.upper()}`" in rendered
        for node in variant.assemblies:
            assert f"`{node.id}`" in rendered


def test_station_catalogue_writer_emits_all_boms_manifest_and_travelers(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog"
    boms = tmp_path / "bom"
    variants = write_outputs(DEFAULT_TEMPLATE, catalog, boms, ConsistFamily.LIGHT_METRO_3CAR)
    assert len(variants) == 7
    manifest = json.loads((catalog / "station-kit-manifest.json").read_text())
    assert len(manifest["variants"]) == 7
    assert manifest["open_release_items"]
    assert (catalog / "open-release-gaps.md").exists()
    assert (catalog / "factory-release-work-packages.json").exists()
    assert (catalog / "factory-release-work-packages.md").exists()
    assert (catalog / "factory-release-readiness.md").exists()
    assert (catalog / "evidence/factory-release-record-template.json").exists()
    assert (catalog / "default-product-specifications.json").exists()
    assert (catalog / "default-product-specifications.md").exists()
    for variant in variants:
        bom_path = boms / f"{variant.archetype}.csv"
        traveler_path = catalog / "travelers" / f"{variant.archetype}.md"
        definition_path = catalog / "variants" / f"{variant.archetype}.md"
        assert bom_path.exists()
        assert traveler_path.exists()
        assert definition_path.exists()
        with bom_path.open() as handle:
            rows = list(csv.DictReader(handle))
        assert len(rows) == len(variant.product_items)
        assert {row["engineering_id"] for row in rows} == {
            item.id for item in variant.product_items
        }
