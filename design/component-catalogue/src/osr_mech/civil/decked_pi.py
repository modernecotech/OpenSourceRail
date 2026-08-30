"""Planning geometry for the transportable OSR decked pi-beam family.

OSR-Pi20 and OSR-Pi25 use one prestressed beam per track.  The upper flange
is the structural track deck and two stems sit beneath the rail lines.  This
module controls manufacturing and coordination envelopes only; it is not a
prestress, reinforcement, fatigue, derailment, vibration, or rail-structure
interaction design.
"""

from __future__ import annotations

from osr_mech.cad import Box, Color, Compound, Location, Part
from osr_mech.common import STANDARD_GAUGE_MM

PRIMARY_SPAN_M = 25.0
CLOSURE_SPAN_M = 20.0
CATALOGUE_SPANS_M = (CLOSURE_SPAN_M, PRIMARY_SPAN_M)

DECK_WIDTH_MM = 2_900.0
FLANGE_THICKNESS_MM = 220.0
STEM_WIDTH_MM = 300.0
STEM_DEPTH_MM = 935.0
OVERALL_DEPTH_MM = FLANGE_THICKNESS_MM + STEM_DEPTH_MM
STEM_CENTRE_OFFSET_MM = STANDARD_GAUGE_MM / 2.0

END_DIAPHRAGM_LENGTH_MM = 550.0
CLOSURE_EDGE_WIDTH_MM = 220.0
DERAILMENT_CURB_WIDTH_MM = 180.0
DERAILMENT_CURB_HEIGHT_MM = 220.0
WALKWAY_CASSETTE_WIDTH_MM = 1_000.0
WALKWAY_CASSETTE_THICKNESS_MM = 120.0
CONCRETE_DENSITY_KG_PER_M3 = 2_500.0


def _check_span(span_m: float) -> None:
    if span_m not in CATALOGUE_SPANS_M:
        raise ValueError(f"decked pi span must be one of {CATALOGUE_SPANS_M}, got {span_m:g} m")


def section_area_m2() -> float:
    """Bare beam section area used by the canonical quantity model."""

    flange = DECK_WIDTH_MM * FLANGE_THICKNESS_MM
    stems = 2.0 * STEM_WIDTH_MM * STEM_DEPTH_MM
    return (flange + stems) / 1_000_000.0


def approx_mass_kg(span_m: float, density_kg_per_m3: float = CONCRETE_DENSITY_KG_PER_M3) -> float:
    """Bare beam mass before local diaphragms and supplier optimisation."""

    _check_span(span_m)
    return section_area_m2() * span_m * density_kg_per_m3


def decked_pi_beam(span_m: float = PRIMARY_SPAN_M) -> Compound:
    """Return one OSR-Pi20/Pi25 manufacturing-envelope beam."""

    _check_span(span_m)
    length_mm = span_m * 1_000.0
    concrete = Color(0.69, 0.69, 0.66)
    parts: list[Part] = []
    flange = Box(length_mm, DECK_WIDTH_MM, FLANGE_THICKNESS_MM).locate(
        Location((length_mm / 2.0, 0.0, STEM_DEPTH_MM + FLANGE_THICKNESS_MM / 2.0))
    )
    flange.label = "Decked pi-beam full-depth track flange"
    flange.color = concrete
    parts.append(flange)
    for side in (-1.0, 1.0):
        stem = Box(length_mm, STEM_WIDTH_MM, STEM_DEPTH_MM).locate(
            Location((length_mm / 2.0, side * STEM_CENTRE_OFFSET_MM, STEM_DEPTH_MM / 2.0))
        )
        stem.label = "Prestressed longitudinal stem beneath rail line"
        stem.color = concrete
        parts.append(stem)
    return Compound(label=f"OSR-Pi{span_m:g} decked single-track beam", children=parts)


def decked_pi_structural_placeholder(span_m: float = PRIMARY_SPAN_M) -> Compound:
    """Add visible supplier-design and railway-interface zones."""

    _check_span(span_m)
    length_mm = span_m * 1_000.0
    interface = Color(0.30, 0.47, 0.60, 0.72)
    concrete = Color(0.62, 0.62, 0.59)
    parts: list[Part] = list(decked_pi_beam(span_m).children)
    for x_mm in (END_DIAPHRAGM_LENGTH_MM / 2.0, length_mm - END_DIAPHRAGM_LENGTH_MM / 2.0):
        diaphragm = Box(
            END_DIAPHRAGM_LENGTH_MM,
            DECK_WIDTH_MM,
            OVERALL_DEPTH_MM,
        ).locate(Location((x_mm, 0.0, OVERALL_DEPTH_MM / 2.0)))
        diaphragm.label = "End diaphragm, anchorage, bearing, lifting, and jacking design zone"
        diaphragm.color = interface
        parts.append(diaphragm)
    for side in (-1.0, 1.0):
        curb = Box(length_mm, DERAILMENT_CURB_WIDTH_MM, DERAILMENT_CURB_HEIGHT_MM).locate(
            Location(
                (
                    length_mm / 2.0,
                    side * (DECK_WIDTH_MM / 2.0 - DERAILMENT_CURB_WIDTH_MM / 2.0),
                    OVERALL_DEPTH_MM + DERAILMENT_CURB_HEIGHT_MM / 2.0,
                )
            )
        )
        curb.label = "Structural derailment-curb connection zone"
        curb.color = concrete
        parts.append(curb)
    return Compound(label=f"OSR-Pi{span_m:g} structural feature placeholder", children=parts)


def walkway_cassette(length_m: float = 6.0) -> Compound:
    """Lightweight replaceable outer evacuation-walkway cassette."""

    if length_m <= 0.0 or length_m > 12.0:
        raise ValueError("walkway cassette length must be positive and no more than 12 m")
    length_mm = length_m * 1_000.0
    concrete = Color(0.72, 0.72, 0.69)
    steel = Color(0.28, 0.32, 0.34)
    panel = Box(length_mm, WALKWAY_CASSETTE_WIDTH_MM, WALKWAY_CASSETTE_THICKNESS_MM).locate(
        Location((length_mm / 2.0, 0.0, WALKWAY_CASSETTE_THICKNESS_MM / 2.0))
    )
    panel.label = "Lightweight precast evacuation walkway panel"
    panel.color = concrete
    barrier = Box(length_mm, 80.0, 1_400.0).locate(
        Location((length_mm / 2.0, WALKWAY_CASSETTE_WIDTH_MM / 2.0 - 40.0, 700.0))
    )
    barrier.label = "Replaceable walkway barrier/screen socket cassette"
    barrier.color = steel
    return Compound(label=f"OSR-Pi walkway cassette ({length_m:g} m)", children=[panel, barrier])


__all__ = [
    "CATALOGUE_SPANS_M",
    "CLOSURE_SPAN_M",
    "DECK_WIDTH_MM",
    "FLANGE_THICKNESS_MM",
    "OVERALL_DEPTH_MM",
    "PRIMARY_SPAN_M",
    "STEM_CENTRE_OFFSET_MM",
    "STEM_DEPTH_MM",
    "STEM_WIDTH_MM",
    "WALKWAY_CASSETTE_WIDTH_MM",
    "approx_mass_kg",
    "decked_pi_beam",
    "decked_pi_structural_placeholder",
    "section_area_m2",
    "walkway_cassette",
]
