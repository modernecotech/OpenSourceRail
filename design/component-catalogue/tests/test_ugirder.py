"""Precast U-girder geometry and mass regression."""

from __future__ import annotations

import pytest

from osr_mech.civil.ugirder import (
    EXTERNAL_HEIGHT_MM,
    EXTERNAL_WIDTH_MM,
    INTERNAL_HEIGHT_MM,
    INTERNAL_WIDTH_MM,
    MIN_REQUIRED_INTERNAL_WIDTH_MM,
    approx_mass_kg,
    u_girder,
    u_girder_structural_placeholder,
)

CONCRETE_DENSITY_KG_PER_M3 = 2500.0


@pytest.mark.parametrize("span_m", [20.0, 25.0, 30.0])
def test_u_girder_mass_matches_approximation(span_m: float) -> None:
    g = u_girder(span_m=span_m)
    v_m3 = g.volume / 1_000_000_000
    mass_kg = v_m3 * CONCRETE_DENSITY_KG_PER_M3
    approx = approx_mass_kg(span_m=span_m)
    ratio = mass_kg / approx
    assert 0.95 <= ratio <= 1.05, (
        f"span {span_m} m: model mass {mass_kg:.0f} kg vs approx {approx:.0f} kg ({ratio:.3f}×)"
    )


def test_u_girder_rejects_out_of_envelope_spans() -> None:
    with pytest.raises(ValueError):
        u_girder(span_m=10.0)
    with pytest.raises(ValueError):
        u_girder(span_m=40.0)


def test_u_girder_cross_section_has_track_clearance() -> None:
    assert INTERNAL_WIDTH_MM >= MIN_REQUIRED_INTERNAL_WIDTH_MM


def test_u_girder_uses_shared_civil_axes() -> None:
    box = u_girder().bounding_box()
    assert box.min.X == pytest.approx(0.0)
    assert box.max.X == pytest.approx(25_000.0)
    assert box.min.Y == pytest.approx(-EXTERNAL_WIDTH_MM / 2.0)
    assert box.max.Y == pytest.approx(EXTERNAL_WIDTH_MM / 2.0)
    assert box.min.Z == pytest.approx(0.0)
    assert box.max.Z == pytest.approx(EXTERNAL_HEIGHT_MM)


def test_u_girder_requires_permit_load_transport_envelope() -> None:
    assert EXTERNAL_WIDTH_MM > 4100.0
    assert EXTERNAL_HEIGHT_MM < 2100.0


def test_structural_placeholder_exposes_mandatory_design_zones() -> None:
    model = u_girder_structural_placeholder()
    labels = [child.label for child in model.children]
    assert any("escape-ledge" in label for label in labels)
    assert labels.count("End diaphragm, bearing, jacking, and anchorage zone") == 2
    assert any("Drainage" in label for label in labels)
