"""Manufacturing-envelope regressions for the OSR-Pi20/Pi25 family."""

from __future__ import annotations

import pytest

from osr_mech.civil.decked_pi import (
    DECK_WIDTH_MM,
    STEM_CENTRE_OFFSET_MM,
    approx_mass_kg,
    decked_pi_beam,
    decked_pi_structural_placeholder,
    walkway_cassette,
)
from osr_mech.common import STANDARD_GAUGE_MM


def test_pi_catalogue_meets_shipping_and_lift_gates() -> None:
    assert DECK_WIDTH_MM <= 3_000.0
    assert 50_000.0 <= approx_mass_kg(20.0) <= 60_000.0
    assert 65_000.0 <= approx_mass_kg(25.0) <= 75_000.0
    assert STEM_CENTRE_OFFSET_MM == STANDARD_GAUGE_MM / 2.0


@pytest.mark.parametrize("span_m", [20.0, 25.0])
def test_pi_geometry_has_flange_and_two_rail_line_stems(span_m: float) -> None:
    beam = decked_pi_beam(span_m)
    assert f"Pi{span_m:g}" in beam.label
    assert len(beam.children) == 3
    assert sum("stem beneath rail" in child.label for child in beam.children) == 2
    box = beam.bounding_box()
    assert box.max.X - box.min.X == pytest.approx(span_m * 1_000.0)


def test_structural_placeholder_exposes_supplier_design_zones() -> None:
    placeholder = decked_pi_structural_placeholder(25.0)
    labels = [child.label for child in placeholder.children]
    assert sum("End diaphragm" in label for label in labels) == 2
    assert sum("derailment-curb" in label for label in labels) == 2
    assert len(walkway_cassette(6.0).children) == 2
    with pytest.raises(ValueError):
        decked_pi_beam(30.0)
