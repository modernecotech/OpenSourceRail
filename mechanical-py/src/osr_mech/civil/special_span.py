"""Separately engineered double-track special-span interface envelope."""

from __future__ import annotations

from osr_mech.cad import Box, Color, Compound, Location, Part

SPECIAL_SPAN_MIN_M = 30.0
SPECIAL_SPAN_MAX_PLANNING_M = 60.0
SPECIAL_DECK_WIDTH_MM = 10_500.0


def special_span_envelope(span_m: float = 40.0) -> Compound:
    """Steel-composite/I-girder placeholder for crossings over 30 m.

    This model controls only the approach width and approximate depth. It is
    intentionally not an extension of OSR-U25 and has no procurement release.
    """

    if not SPECIAL_SPAN_MIN_M < span_m <= SPECIAL_SPAN_MAX_PLANNING_M:
        raise ValueError("special span planning envelope is >30 m and <=60 m")
    length_mm = span_m * 1000.0
    concrete = Color(0.68, 0.68, 0.66)
    steel = Color(0.28, 0.34, 0.40)
    parts: list[Part] = []
    deck = Box(length_mm, SPECIAL_DECK_WIDTH_MM, 350.0).locate(
        Location((length_mm / 2.0, 0.0, 1_600.0))
    )
    deck.label = "Special-span double-track composite deck interface"
    deck.color = concrete
    parts.append(deck)
    for y_mm in (-3_500.0, -1_200.0, 1_200.0, 3_500.0):
        girder = Box(length_mm, 450.0, 2_500.0).locate(
            Location((length_mm / 2.0, y_mm, 175.0))
        )
        girder.label = "Special-span steel/I-girder structural design zone"
        girder.color = steel
        parts.append(girder)
    return Compound(label=f"OSR-SP special crossing envelope ({span_m:g} m)", children=parts)


__all__ = ["SPECIAL_DECK_WIDTH_MM", "special_span_envelope"]
