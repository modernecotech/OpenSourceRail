"""Smoke tests for CAD templates consolidated into osr_mech."""

from __future__ import annotations

from osr_mech.cad_templates import (
    FIXTURE_BUILDERS,
    ROLLING_STOCK_TEMPLATE_BUILDERS,
    body_sheet_metal_kit,
    bogie_adapter,
    bolster,
    chassis_interface_assembly,
    motor_cradle,
)


def test_rolling_stock_templates_build_nonzero_geometry() -> None:
    for name, builder in ROLLING_STOCK_TEMPLATE_BUILDERS.items():
        part = builder()
        assert part.volume > 0.0, f"{name} template produced empty geometry"


def test_fixture_placeholders_build_nonzero_geometry() -> None:
    for name, builder in FIXTURE_BUILDERS.items():
        part = builder()
        assert part.volume > 0.0, f"{name} fixture produced empty geometry"


def _child_labels(part) -> set[str]:
    return {child.label for child in part.children if child.label}


def test_bolster_integrates_spherical_bearing_envelope() -> None:
    labels = _child_labels(bolster())
    assert "SKF GE spherical bearing envelope" in labels
    assert "Bolster lateral hard stop" in labels


def test_motor_cradle_integrates_connector_and_service_strut() -> None:
    labels = _child_labels(motor_cradle())
    assert "Anderson SB50 traction connector envelope" in labels
    assert "Stabilus service strut envelope" in labels
    assert "Motor cradle isolator boss" in labels


def test_bogie_adapter_integrates_guide_blocks_and_fasteners() -> None:
    labels = _child_labels(bogie_adapter())
    assert "HIWIN HG guide block envelope" in labels
    assert "Camloc access fastener envelope" in labels


def test_chassis_interface_assembly_contains_three_interfaces() -> None:
    labels = _child_labels(chassis_interface_assembly())
    assert labels == {
        "Bogie adapter interface assembly",
        "Bolster interface assembly",
        "Motor cradle interface assembly",
    }


def test_body_sheet_metal_kit_contains_manufacturing_features() -> None:
    labels = _child_labels(body_sheet_metal_kit())
    assert "Rolling-stock sheet-metal underframe template" in labels
    assert "Door portal reinforcement" in labels
    assert "Roll-formed roof bow" in labels
    assert "End bulkhead ring frame" in labels
