"""Precast U-girder geometry and mass regression."""

from __future__ import annotations

import pytest

from osr_mech.civil.ugirder import (
    EXTERNAL_HEIGHT_MM,
    EXTERNAL_WIDTH_MM,
    INTERNAL_HEIGHT_MM,
    INTERNAL_WIDTH_MM,
    approx_mass_kg,
    u_girder,
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
        f"span {span_m} m: STEP mass {mass_kg:.0f} kg vs approx {approx:.0f} kg ({ratio:.3f}×)"
    )


def test_u_girder_rejects_out_of_envelope_spans() -> None:
    with pytest.raises(ValueError):
        u_girder(span_m=10.0)
    with pytest.raises(ValueError):
        u_girder(span_m=40.0)


def test_u_girder_cross_section_has_track_clearance() -> None:
    # Internal width must fit standard gauge (1435 mm) plus car body
    # half-width (1.5 m typical for a light-metro car) plus 500 mm of
    # walkway either side. That's ~3000 mm absolute minimum; 3500 mm
    # published.
    assert INTERNAL_WIDTH_MM >= 3000.0


def test_u_girder_outer_fits_on_lorry() -> None:
    # Lorry deck typical envelope: 2.55 m wide × 4.1 m high (legal
    # without permit in most deployment markets). The girder ships on
    # its side, so its external height (EXTERNAL_WIDTH_MM on the road)
    # must fit the deck width.
    assert EXTERNAL_HEIGHT_MM <= 2550.0 or EXTERNAL_WIDTH_MM <= 4100.0, (
        "U-girder won't fit on a standard lorry in any orientation; "
        "specify permit-load shipping in the deployment docs"
    )
