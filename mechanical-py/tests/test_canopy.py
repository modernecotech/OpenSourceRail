"""Canopy bay count, PV output, and steel mass regression."""

from __future__ import annotations

import pytest

from osr_mech.common import ConsistFamily, StationArchetype
from osr_mech.station.canopy import (
    bay_count,
    canopy_kwp,
    canopy_steel_mass_kg,
    station_canopy,
)
from osr_mech.station.solar_roof import panel_kwp


@pytest.mark.parametrize(
    "archetype, consist, expected_min_bays, expected_max_bays",
    [
        # Standard station × light-metro-3car = 75 m / 6 m ≈ 13 bays.
        (StationArchetype.STANDARD, ConsistFamily.LIGHT_METRO_3CAR, 12, 14),
        # Major = standard + 2 waiting-area bays.
        (StationArchetype.MAJOR, ConsistFamily.LIGHT_METRO_3CAR, 14, 16),
        # Terminal = standard + 4 end-screen bays.
        (StationArchetype.TERMINAL, ConsistFamily.LIGHT_METRO_3CAR, 16, 18),
        # Metro-4car = 100 m / 6 m ≈ 17 bays.
        (StationArchetype.STANDARD, ConsistFamily.METRO_4CAR, 16, 18),
        # Halt = 0.4 × 75 m = 30 m → 5 bays.
        (StationArchetype.HALT, ConsistFamily.LIGHT_METRO_3CAR, 4, 6),
    ],
)
def test_bay_counts(
    archetype: StationArchetype,
    consist: ConsistFamily,
    expected_min_bays: int,
    expected_max_bays: int,
) -> None:
    n = bay_count(archetype, consist)
    assert expected_min_bays <= n <= expected_max_bays, (
        f"{archetype.value}×{consist.value}: {n} bays outside [{expected_min_bays}, {expected_max_bays}]"
    )


def test_standard_canopy_generates_tens_of_kwp() -> None:
    # A 13-bay canopy at 6 m × 4.2 m per bay × 200 W/m² × 0.85 pack
    # factor ≈ 55 kWp — plenty to cover daytime station demand.
    kwp = canopy_kwp(StationArchetype.STANDARD, ConsistFamily.LIGHT_METRO_3CAR)
    assert 40.0 <= kwp <= 70.0, f"standard canopy PV = {kwp:.1f} kWp, expected 40–70"


def test_steel_mass_fits_two_lorries() -> None:
    # One articulated lorry can carry ~26 t of flat-pack steel. A
    # standard canopy should come in at <2 lorries — if it doesn't,
    # the bay design is too heavy and we need thinner sections.
    mass_kg = canopy_steel_mass_kg(
        StationArchetype.STANDARD, ConsistFamily.LIGHT_METRO_3CAR
    )
    assert mass_kg <= 52_000.0, f"{mass_kg / 1000:.1f} t exceeds 2-lorry budget"


def test_single_bay_panel_kwp_matches_spec() -> None:
    # 6 m × 3.5 m bay panel at 200 W/m² × 0.85 pack = 3.57 kWp.
    kwp = panel_kwp(6000.0, 3500.0)
    assert kwp == pytest.approx(3.57, abs=0.05)


def test_canopy_step_volume_nonzero() -> None:
    c = station_canopy(StationArchetype.STANDARD, ConsistFamily.LIGHT_METRO_3CAR)
    # The assembly is a Compound — volume is the sum across its children.
    # We just need to confirm STEP export sees non-trivial geometry.
    # Walk children and sum volumes.
    total = 0.0
    for ch in c.children:
        if hasattr(ch, "volume"):
            total += ch.volume
        if hasattr(ch, "children"):
            for sub in ch.children:
                if hasattr(sub, "volume"):
                    total += sub.volume
    assert total > 0.0
