"""Regression checks for the end-to-end civil systems review example."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from osr_mech.clearance import reference_envelope, swept_envelope_part
from osr_mech.civil_systems_integration import (
    ELEVATED_PLATFORM_SURFACE_Z_MM,
    ELEVATED_TOR_Z_MM,
    GROUND_PLATFORM_SURFACE_Z_MM,
    GROUND_TOR_Z_MM,
    PLATFORM_HORIZONTAL_GAP_MM,
    ZONE_ASSET_IDS,
    asset_id_for_component,
    assert_integration_checks,
    digital_twin_manifest,
    integration_components,
    write_digital_twin_manifest,
)
from osr_mech.rolling_stock.baseline import PROMOTED_LIGHT_METRO_CAR_OVERALL_HEIGHT_MM


def test_integration_manifest_contains_every_requested_system() -> None:
    components = integration_components()
    zones = {component.zone for component in components}
    assert zones == {
        "01 At-grade ground station",
        "02 At-grade junction",
        "03 Viaduct approaches and substructure",
        "04 Elevated station",
        "05 Rolling stock",
    }
    assert any("turnout" in component.source for component in components)
    assert sum("25 m U-girder" in component.label for component in components) == 12
    assert sum("Shared double-track pier" in component.label for component in components) == 9
    assert sum("standard solar canopy" in component.label for component in components) == 4
    assert sum("rolling_stock.trainset" in component.source for component in components) == 2


def test_all_integration_interface_checks_pass() -> None:
    checks = assert_integration_checks()
    assert len(checks) == 9
    assert all(check.passed for check in checks)


def test_station_boarding_datums_are_shared_and_explicit() -> None:
    assert GROUND_PLATFORM_SURFACE_Z_MM - GROUND_TOR_Z_MM == pytest.approx(350.0)
    assert ELEVATED_PLATFORM_SURFACE_Z_MM - ELEVATED_TOR_Z_MM == pytest.approx(350.0)
    assert PLATFORM_HORIZONTAL_GAP_MM == 75.0


def test_every_integration_component_has_nonempty_geometry() -> None:
    for component in integration_components():
        box = component.build().bounding_box()
        assert box.volume > 0.0, component.label


def test_complete_trainsets_fit_along_both_sixty_metre_platforms() -> None:
    trains = [
        component
        for component in integration_components()
        if "rolling_stock.trainset" in component.source
    ]
    assert len(trains) == 2
    for train in trains:
        source = train.builder()
        assert len(source.children) == 12
        box = train.build().bounding_box()
        platform_start = train.translation_mm[0] - 30_000.0
        platform_end = train.translation_mm[0] + 30_000.0
        assert box.min.X >= platform_start
        assert box.max.X <= platform_end


def test_complete_trainset_roof_equipment_fits_controlled_vertical_envelope() -> None:
    train_component = next(
        component
        for component in integration_components()
        if component.label == "Ground-station complete light-metro trainset"
    )
    source_box = train_component.builder().bounding_box()
    assert source_box.max.Z == pytest.approx(3868.0)
    assert source_box.max.Z <= PROMOTED_LIGHT_METRO_CAR_OVERALL_HEIGHT_MM

    envelope_box = swept_envelope_part(reference_envelope()).bounding_box()
    assert envelope_box.max.Z == pytest.approx(PROMOTED_LIGHT_METRO_CAR_OVERALL_HEIGHT_MM + 30.0)


def test_digital_twin_manifest_has_unique_assets_states_and_relationships() -> None:
    components = integration_components()
    ids = [asset_id_for_component(component) for component in components]
    assert len(ids) == len(set(ids)) == 82

    manifest = digital_twin_manifest()
    assert manifest["schema"] == "org.opensourcerail.civil-rolling-stock-twin.v1"
    assert len(manifest["zones"]) == len(ZONE_ASSET_IDS) == 5
    assert len(manifest["assets"]) == 82
    assert len(manifest["relationships"]) == 86

    assets = {asset["asset_id"]: asset for asset in manifest["assets"]}
    assert assets["OSR-LM3-TEST-001"]["state"]["mode"] == "stationary-dwell-charging"
    assert assets["OSR-LM3-TEST-002"]["state"]["mode"] == "stationary-dwell"
    assert assets["OSR-LM3-TEST-001"]["geometry_role"] == "physical-plus-interface-reservations"


def test_digital_twin_writer_hashes_the_exact_native_model(tmp_path: Path) -> None:
    model = tmp_path / "example.FCStd"
    model.write_bytes(b"deterministic native model placeholder")
    manifest_path = tmp_path / "example.json"
    write_digital_twin_manifest(
        manifest_path,
        model_path=model,
        native_clash_checks=("PASS — example clearance",),
    )
    payload = json.loads(manifest_path.read_text())
    assert payload["model"]["file"] == "example.FCStd"
    assert payload["model"]["size_bytes"] == model.stat().st_size
    assert len(payload["model"]["sha256"]) == 64
    assert payload["validation"]["native_clearance_clash_checks"] == [
        "PASS — example clearance"
    ]
