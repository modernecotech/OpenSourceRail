"""Three-metre at-grade station guideway-channel edge module.

The walking surface remains at pedestrian grade while the rail datum drops
350 mm through the station.  This module provides the repeatable rail-side
edge beam, coping carrier, tactile carrier, and drained service trough; the
deployment civil design owns the surrounding pavement and channel foundation.
"""

from __future__ import annotations

from osr_mech.cad import Box, Color, Compound, Location, Part


EDGE_MODULE_LENGTH_MM = 3_000.0
PLATFORM_TO_TOR_HEIGHT_MM = 350.0
EDGE_BEAM_WIDTH_MM = 350.0
COPING_WIDTH_MM = 450.0
TACTILE_CARRIER_WIDTH_MM = 600.0
DRAIN_WIDTH_MM = 250.0


def _part(length: float, width: float, height: float, label: str, loc: tuple[float, float, float], color: Color) -> Part:
    item = Box(length, width, height).locate(Location(loc))
    item.label = label
    item.color = color
    return item


def guideway_channel_edge_module(length_mm: float = EDGE_MODULE_LENGTH_MM) -> Compound:
    """One straight platform edge at the 350 mm platform/ToR datum."""

    concrete = Color(0.74, 0.74, 0.72)
    coping = Color(0.84, 0.84, 0.80)
    tactile = Color(0.92, 0.75, 0.12)
    drain = Color(0.34, 0.34, 0.36)
    return Compound(
        label=f"At-grade guideway-channel edge ({length_mm:.0f} mm)",
        children=[
            _part(length_mm, EDGE_BEAM_WIDTH_MM, 500.0, "Guideway edge beam", (length_mm / 2, 0, 250), concrete),
            _part(length_mm, COPING_WIDTH_MM, 120.0, "Replaceable platform coping carrier", (length_mm / 2, 50, 560), coping),
            _part(length_mm, TACTILE_CARRIER_WIDTH_MM, 80.0, "Tactile and warning-strip carrier", (length_mm / 2, 575, 540), tactile),
            _part(length_mm, DRAIN_WIDTH_MM, 200.0, "Guideway edge drain and service trough", (length_mm / 2, -300, 100), drain),
        ],
    )


__all__ = ["EDGE_MODULE_LENGTH_MM", "PLATFORM_TO_TOR_HEIGHT_MM", "guideway_channel_edge_module"]
