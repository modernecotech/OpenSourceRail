"""Sleeper geometry and mass regression."""

from __future__ import annotations

from osr_mech.track.sleeper import (
    SLEEPER_LENGTH_MM,
    SLEEPER_MASS_KG,
    mono_block_sleeper,
    rail_seat_positions,
)

CONCRETE_DENSITY_KG_PER_M3 = 2500.0


def test_sleeper_mass_within_tolerance() -> None:
    s = mono_block_sleeper()
    v_m3 = s.volume / 1_000_000_000
    mass_kg = v_m3 * CONCRETE_DENSITY_KG_PER_M3
    # Published B70 mass = 320 kg. The model's loft is lighter than a
    # real sleeper because it omits the embedded shoulder inserts and
    # rebar cage. Accept anything in 250–350 kg.
    assert 250.0 <= mass_kg <= 350.0, (
        f"sleeper mass {mass_kg:.0f} kg outside envelope; published {SLEEPER_MASS_KG}"
    )


def test_rail_seats_symmetric_and_inset_from_ends() -> None:
    a, b = rail_seat_positions()
    assert a < b
    assert a + (SLEEPER_LENGTH_MM - b) == SLEEPER_LENGTH_MM / 2.0 * 0 + (SLEEPER_LENGTH_MM - b + a), (
        "rail seats must be symmetric about the sleeper centreline"
    )
    # More simply:
    assert a + b == SLEEPER_LENGTH_MM
    # And there must be at least 300 mm from the nearer end to the rail
    # seat (for ballast shoulder + fastener bolts).
    assert a >= 300.0
