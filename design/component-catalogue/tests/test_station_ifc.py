"""Determinism checks for the generated station IFC handoff."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import ifcopenshell

from osr_mech.station.product_geometry import (
    PLATFORM_SURFACE_Z_MM,
    PLATFORM_TO_TOR_HEIGHT_MM,
    TOP_OF_RAIL_Z_MM,
    station_product_geometry,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
EXPORTER = REPO_ROOT / "engineering/interchange/station_ifc.py"
MANIFEST = (
    REPO_ROOT
    / "design/component-catalogue/catalog/buildable-stations/station-kit-manifest.json"
)


def test_station_ifc_is_byte_deterministic(tmp_path: Path) -> None:
    module = runpy.run_path(str(EXPORTER))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    standard = next(
        variant for variant in manifest["variants"] if variant["archetype"] == "standard"
    )
    first = tmp_path / "first.ifc"
    second = tmp_path / "second.ifc"

    first_report = module["export_variant"](standard, first)
    second_report = module["export_variant"](standard, second)

    assert first.read_bytes() == second.read_bytes()
    assert first_report["ifc_sha256"] == second_report["ifc_sha256"]
    assert first_report["geometry_status"] == "coordinated-design-reference-geometry"
    assert first_report["represented_product_count"] == first_report["product_item_count"]
    assert first_report["primitive_count"] > first_report["product_item_count"]
    reopened = ifcopenshell.open(str(first))
    represented = {
        str(item.Tag)
        for item in reopened.by_type("IfcProduct")
        if getattr(item, "Tag", None) and getattr(item, "Representation", None)
    }
    assert represented.issuperset(item["id"] for item in standard["product_items"])
    assert reopened.by_type("IfcSlab")
    assert reopened.by_type("IfcElectricDistributionBoard")
    assert module["FIXED_HEADER_TIMESTAMP"] in first.read_text(encoding="utf-8")


def test_station_platform_and_terminal_turnout_share_the_boarding_datum() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    standard = next(row for row in manifest["variants"] if row["archetype"] == "standard")
    terminal = next(row for row in manifest["variants"] if row["archetype"] == "terminal")
    slab_item = next(row for row in standard["product_items"] if row["id"] == "STN-CIV-P010")
    rail_item = next(row for row in terminal["product_items"] if row["id"] == "STN-TRK-P010")
    platform = station_product_geometry(slab_item, standard["parameters"])
    turnout_rail = station_product_geometry(rail_item, terminal["parameters"])

    assert platform.bounding_box().max.Z == PLATFORM_SURFACE_Z_MM
    assert turnout_rail.bounding_box().max.Z == TOP_OF_RAIL_Z_MM
    assert PLATFORM_SURFACE_Z_MM - TOP_OF_RAIL_Z_MM == PLATFORM_TO_TOR_HEIGHT_MM
