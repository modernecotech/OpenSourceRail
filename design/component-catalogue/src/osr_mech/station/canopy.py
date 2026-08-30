"""Full station canopy — the kit-of-parts assembly for one platform.

A canopy is N bays of portal frame + N solar-roof panels + a terminal
trailing column on the last bay. Everything bolts together on pad
footings.

Archetype → bay count is derived from RFC 0010 §5:

- halt:        ceil(platform_length / 6.0 m), using the reduced 6 m
               stopping/door-control clearance from RFC 0010.
- standard:    full platform length covered.
- major:       full platform length covered, plus two adjacent bays
               of "waiting area" extension at the concourse end.
- interchange: full platform length covered on both sides of every
               interchanged platform; the caller instantiates once per
               platform.
- interchange-elevated: the same platform canopy module on each level;
               lift/stair/concourse structures remain a civil assembly.
- terminal:    full platform length covered, plus a 4-bay end screen
               for the stop-block.
- depot-terminal: same as terminal.

The canopy is the only piece of architecture a "standard" station
needs. There is no station building — fare gates are on modular
rolled-steel plinths at the platform entry, and the PIS / CCTV /
lighting / radio mast is a single steel column per canopy.
"""

from __future__ import annotations

import math

from osr_mech.cad import Compound, Part

from ..common import (
    ConsistFamily,
    StationArchetype,
    archetype_platform_length_m,
)
from .portal import BAY_SPACING_MM, CLEAR_HEIGHT_MM, PLATFORM_DEPTH_MM, portal_frame
from .solar_roof import (
    EAVE_OVERHANG_MM,
    PANEL_MASS_KG_PER_M2,
    PV_WATT_PER_M2,
    solar_roof_panel,
)


ARCHETYPE_EXTRA_BAYS: dict[StationArchetype, int] = {
    StationArchetype.HALT: 0,
    StationArchetype.STANDARD: 0,
    StationArchetype.MAJOR: 2,  # +2 bays of waiting-area extension
    StationArchetype.INTERCHANGE: 0,
    StationArchetype.INTERCHANGE_ELEVATED: 0,
    StationArchetype.TERMINAL: 4,  # +4 bays of end-screen at stop-block
    StationArchetype.DEPOT_TERMINAL: 4,
}


def bay_count(
    archetype: StationArchetype = StationArchetype.STANDARD,
    consist: ConsistFamily = ConsistFamily.LIGHT_METRO_3CAR,
) -> int:
    """Number of 6 m bays needed to cover the archetype's platform,
    plus any archetype-specific extension bays."""
    platform_m = archetype_platform_length_m(archetype, consist)
    core = int(math.ceil(platform_m * 1000.0 / BAY_SPACING_MM))
    return core + ARCHETYPE_EXTRA_BAYS[archetype]


def station_canopy(
    archetype: StationArchetype = StationArchetype.STANDARD,
    consist: ConsistFamily = ConsistFamily.LIGHT_METRO_3CAR,
) -> Compound:
    """Full canopy assembly.

    Origin: platform-edge side of the first column, at grade. +X runs
    along the platform; +Y is toward the back wall. The canopy does
    not include the at-grade guideway edge or elevated platform L-units —
    those are separate `osr_mech.civil` products.
    """

    bays = bay_count(archetype, consist)
    parts: list[Part | Compound] = []

    for i in range(bays):
        frame = portal_frame()
        frame = frame.translate((i * BAY_SPACING_MM, 0.0, 0.0))
        parts.append(frame)

        roof = solar_roof_panel(length_mm=BAY_SPACING_MM, depth_mm=PLATFORM_DEPTH_MM)
        # The panel spans from the 700 mm track-side eave at -Y to the
        # rear-column line at +Y=PLATFORM_DEPTH_MM.
        roof_y = (PLATFORM_DEPTH_MM - EAVE_OVERHANG_MM) / 2.0
        roof = roof.translate((i * BAY_SPACING_MM, roof_y, CLEAR_HEIGHT_MM + 200.0))
        parts.append(roof)

    # Trailing column at the end of the last bay.
    from .portal import _column

    trailing = _column().translate(
        (bays * BAY_SPACING_MM, PLATFORM_DEPTH_MM - 100.0, 0.0)
    )
    parts.append(trailing)

    return Compound(
        label=f"Station canopy ({archetype.value}, {consist.value}, {bays} bays)",
        children=parts,
    )


def canopy_kwp(
    archetype: StationArchetype = StationArchetype.STANDARD,
    consist: ConsistFamily = ConsistFamily.LIGHT_METRO_3CAR,
) -> float:
    """Published peak PV generation for the canopy — used by RFC 0002
    energy sizing + tests."""
    bays = bay_count(archetype, consist)
    # Area per bay includes the eave overhang since PV goes right to
    # the eave lip.
    length_m = BAY_SPACING_MM / 1000.0
    depth_m = (PLATFORM_DEPTH_MM + EAVE_OVERHANG_MM) / 1000.0
    area_per_bay = length_m * depth_m
    return bays * area_per_bay * PV_WATT_PER_M2 / 1000.0 * 0.85  # 15 % pack loss


def canopy_steel_mass_kg(
    archetype: StationArchetype = StationArchetype.STANDARD,
    consist: ConsistFamily = ConsistFamily.LIGHT_METRO_3CAR,
) -> float:
    """Approximate shipped-steel mass — used for lorry-load sizing."""
    bays = bay_count(archetype, consist)
    # Per bay: 1 column (3200 mm × 42.3 kg/m) + 1 rafter (3500 mm × 35.5 kg/m)
    # + 1 brace (~2500 mm × 18.0 kg/m) + 5 % gussets/plates. Add the
    # trailing end column emitted by station_canopy() rather than silently
    # omitting it from the transport mass.
    per_bay_kg = (3.2 * 42.3) + (3.5 * 35.5) + (2.5 * 18.0)
    per_bay_kg *= 1.05
    trailing_column_kg = 3.2 * 42.3 * 1.05
    return bays * per_bay_kg + trailing_column_kg


__all__ = [
    "ARCHETYPE_EXTRA_BAYS",
    "bay_count",
    "canopy_kwp",
    "canopy_steel_mass_kg",
    "station_canopy",
]
