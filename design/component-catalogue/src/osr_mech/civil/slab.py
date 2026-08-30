"""Ballastless slab trackforms for at-grade and elevated OSR sections.

The CAD parts here are planning/reference geometry for civil packages:

- `at_grade_slab_panel` is one transportable 6 m single-track OSR-ST6 panel
  with two continuous rail plinths and direct-fixation seats. Two independent
  panels form the standard 3.5 m-centre double-track section.
- `elevated_deck_slab_panel` is one 6 m single-track local-plinth package
  over a thin alignment layer. It deliberately omits the former 220 mm
  full-width topping slab.

Both panels use direct-fixation seats at the standard-urban 650 mm pitch.
The real deployment structural design still checks concrete grade,
reinforcement, shrinkage, drainage, stray-current protection, and local
foundation/viaduct interaction.
"""

from __future__ import annotations

from osr_mech.cad import Box, Color, Compound, Location, Part

from ..common import STANDARD_GAUGE_MM


PANEL_LENGTH_MM = 6000.0
FASTENER_PITCH_MM = 650.0

TRACK_CENTRE_SPACING_MM = 3500.0

AT_GRADE_PANEL_WIDTH_MM = 2900.0
AT_GRADE_BASE_THICKNESS_MM = 250.0
AT_GRADE_PLINTH_WIDTH_MM = 380.0
AT_GRADE_PLINTH_HEIGHT_MM = 160.0
AT_GRADE_EDGE_TROUGH_WIDTH_MM = 240.0
AT_GRADE_EDGE_TROUGH_HEIGHT_MM = 180.0

# Keep the poured alignment layer inside the 2.9 m Pi-beam flange.  The
# evacuation walkway is an independent outer cassette, not part of this pour.
ELEVATED_PANEL_WIDTH_MM = 2700.0
# Thin tolerance/alignment layer over the waterproofed structural floor.
# This is not a second structural deck slab.
ELEVATED_BASE_THICKNESS_MM = 40.0
ELEVATED_PLINTH_WIDTH_MM = 380.0
ELEVATED_PLINTH_HEIGHT_MM = 160.0
ELEVATED_CABLE_TROUGH_WIDTH_MM = 260.0
ELEVATED_CABLE_TROUGH_HEIGHT_MM = 180.0

BASEPLATE_PAD_LENGTH_MM = 260.0
BASEPLATE_PAD_WIDTH_MM = 220.0
BASEPLATE_PAD_HEIGHT_MM = 24.0


def _box(
    length_mm: float,
    width_mm: float,
    height_mm: float,
    *,
    label: str,
    color: Color,
    loc: tuple[float, float, float],
) -> Part:
    part = Box(length_mm, width_mm, height_mm).locate(Location(loc))
    part.label = label
    part.color = color
    return part


def _seat_x_positions(length_mm: float) -> list[float]:
    n = int(length_mm // FASTENER_PITCH_MM) + 1
    return [i * FASTENER_PITCH_MM for i in range(n)]


def at_grade_rail_y_positions() -> tuple[float, float]:
    """Rail Y positions local to one single-track OSR-ST6 panel."""

    half_gauge = STANDARD_GAUGE_MM / 2.0
    return (-half_gauge, half_gauge)


def at_grade_twin_rail_y_positions() -> tuple[float, float, float, float]:
    """Global rail positions for two OSR-ST6 panels at standard centres."""

    half_track = TRACK_CENTRE_SPACING_MM / 2.0
    return tuple(
        track_y + rail_y
        for track_y in (-half_track, half_track)
        for rail_y in at_grade_rail_y_positions()
    )


def elevated_rail_y_positions() -> tuple[float, float]:
    """Rail Y positions for one single-track elevated deck slab."""

    half_gauge = STANDARD_GAUGE_MM / 2.0
    return (-half_gauge, half_gauge)


def elevated_service_trough_y_positions() -> tuple[float]:
    """Service-trough centre on the non-egress (+Y) side only."""

    return (ELEVATED_PANEL_WIDTH_MM / 2.0 - ELEVATED_CABLE_TROUGH_WIDTH_MM / 2.0,)


def direct_fixation_seat_count(length_mm: float = PANEL_LENGTH_MM, rail_count: int = 2) -> int:
    """Number of direct-fixation rail seats in one panel."""

    return len(_seat_x_positions(length_mm)) * rail_count


def at_grade_concrete_volume_m3(length_mm: float = PANEL_LENGTH_MM) -> float:
    """Nominal concrete volume for one single-track OSR-ST6 panel."""

    length_m = length_mm / 1000.0
    base = length_m * (AT_GRADE_PANEL_WIDTH_MM / 1000.0) * (AT_GRADE_BASE_THICKNESS_MM / 1000.0)
    plinths = (
        length_m
        * (AT_GRADE_PLINTH_WIDTH_MM / 1000.0)
        * (AT_GRADE_PLINTH_HEIGHT_MM / 1000.0)
        * 2.0
    )
    return base + plinths


def at_grade_panel_mass_kg(
    length_mm: float = PANEL_LENGTH_MM,
    concrete_density_kg_per_m3: float = 2_500.0,
) -> float:
    """Planning mass of one bare OSR-ST6 panel."""

    return at_grade_concrete_volume_m3(length_mm) * concrete_density_kg_per_m3


def elevated_concrete_volume_m3(length_mm: float = PANEL_LENGTH_MM) -> float:
    """Nominal alignment-layer plus local-plinth concrete volume."""

    length_m = length_mm / 1000.0
    base = length_m * (ELEVATED_PANEL_WIDTH_MM / 1000.0) * (ELEVATED_BASE_THICKNESS_MM / 1000.0)
    plinths = (
        length_m
        * (ELEVATED_PLINTH_WIDTH_MM / 1000.0)
        * (ELEVATED_PLINTH_HEIGHT_MM / 1000.0)
        * 2.0
    )
    return base + plinths


def _baseplate_pads(
    rail_positions: tuple[float, ...],
    z_mm: float,
    length_mm: float,
) -> list[Part]:
    color = Color(0.20, 0.20, 0.22)
    pads: list[Part] = []
    for x in _seat_x_positions(length_mm):
        for y in rail_positions:
            pads.append(
                _box(
                    BASEPLATE_PAD_LENGTH_MM,
                    BASEPLATE_PAD_WIDTH_MM,
                    BASEPLATE_PAD_HEIGHT_MM,
                    label="Direct-fixation baseplate pad",
                    color=color,
                    loc=(x, y, z_mm + BASEPLATE_PAD_HEIGHT_MM / 2.0),
                )
            )
    return pads


def at_grade_slab_panel(length_mm: float = PANEL_LENGTH_MM) -> Compound:
    """Reference transportable 6 m single-track OSR-ST6 slab panel."""

    parts: list[Part] = []
    concrete = Color(0.72, 0.72, 0.70)
    dark_concrete = Color(0.60, 0.60, 0.58)

    parts.append(
        _box(
            length_mm,
            AT_GRADE_PANEL_WIDTH_MM,
            AT_GRADE_BASE_THICKNESS_MM,
            label="At-grade ballastless base slab",
            color=concrete,
            loc=(length_mm / 2.0, 0.0, AT_GRADE_BASE_THICKNESS_MM / 2.0),
        )
    )

    for rail_y in at_grade_rail_y_positions():
        parts.append(
            _box(
                length_mm,
                AT_GRADE_PLINTH_WIDTH_MM,
                AT_GRADE_PLINTH_HEIGHT_MM,
                label="Continuous direct-fixation rail plinth",
                color=concrete,
                loc=(
                    length_mm / 2.0,
                    rail_y,
                    AT_GRADE_BASE_THICKNESS_MM + AT_GRADE_PLINTH_HEIGHT_MM / 2.0,
                ),
            )
        )

    edge_y = AT_GRADE_PANEL_WIDTH_MM / 2.0 - AT_GRADE_EDGE_TROUGH_WIDTH_MM / 2.0
    for y in (-edge_y, edge_y):
        parts.append(
            _box(
                length_mm,
                AT_GRADE_EDGE_TROUGH_WIDTH_MM,
                AT_GRADE_EDGE_TROUGH_HEIGHT_MM,
                label="Edge drainage and cable trough",
                color=dark_concrete,
                loc=(
                    length_mm / 2.0,
                    y,
                    AT_GRADE_BASE_THICKNESS_MM + AT_GRADE_EDGE_TROUGH_HEIGHT_MM / 2.0,
                ),
            )
        )

    parts.extend(
        _baseplate_pads(
            at_grade_rail_y_positions(),
            AT_GRADE_BASE_THICKNESS_MM + AT_GRADE_PLINTH_HEIGHT_MM,
            length_mm,
        )
    )
    return Compound(label=f"OSR-ST6 single-track slab panel ({length_mm:.0f} mm)", children=parts)


def elevated_deck_slab_panel(length_mm: float = PANEL_LENGTH_MM) -> Compound:
    """Reference direct-fixation package for one decked pi-beam.

    The girder structural floor remains the deck. A project may omit even the
    thin alignment layer where surveyed casting and adjustable baseplates can
    recover the required rail geometry.
    """

    parts: list[Part] = []
    concrete = Color(0.70, 0.70, 0.68)
    cable_color = Color(0.48, 0.48, 0.50)

    parts.append(
        _box(
            length_mm,
            ELEVATED_PANEL_WIDTH_MM,
            ELEVATED_BASE_THICKNESS_MM,
            label="Thin non-structural alignment layer over waterproofing",
            color=concrete,
            loc=(length_mm / 2.0, 0.0, ELEVATED_BASE_THICKNESS_MM / 2.0),
        )
    )

    for rail_y in elevated_rail_y_positions():
        parts.append(
            _box(
                length_mm,
                ELEVATED_PLINTH_WIDTH_MM,
                ELEVATED_PLINTH_HEIGHT_MM,
                label="Elevated direct-fixation rail plinth",
                color=concrete,
                loc=(
                    length_mm / 2.0,
                    rail_y,
                    ELEVATED_BASE_THICKNESS_MM + ELEVATED_PLINTH_HEIGHT_MM / 2.0,
                ),
            )
        )

    # The -Y edge is the controlled 1.0 m escape ledge. Cable and drainage
    # hardware stays on +Y so its covers cannot reduce the clear egress width.
    for y in elevated_service_trough_y_positions():
        parts.append(
            _box(
                length_mm,
                ELEVATED_CABLE_TROUGH_WIDTH_MM,
                ELEVATED_CABLE_TROUGH_HEIGHT_MM,
                label="Elevated cable and drainage trough",
                color=cable_color,
                loc=(
                    length_mm / 2.0,
                    y,
                    ELEVATED_BASE_THICKNESS_MM + ELEVATED_CABLE_TROUGH_HEIGHT_MM / 2.0,
                ),
            )
        )

    parts.extend(
        _baseplate_pads(
            elevated_rail_y_positions(),
            ELEVATED_BASE_THICKNESS_MM + ELEVATED_PLINTH_HEIGHT_MM,
            length_mm,
        )
    )
    return Compound(label=f"Elevated deck slab panel ({length_mm:.0f} mm)", children=parts)


__all__ = [
    "AT_GRADE_BASE_THICKNESS_MM",
    "AT_GRADE_PANEL_WIDTH_MM",
    "AT_GRADE_PLINTH_HEIGHT_MM",
    "AT_GRADE_PLINTH_WIDTH_MM",
    "ELEVATED_BASE_THICKNESS_MM",
    "ELEVATED_PANEL_WIDTH_MM",
    "ELEVATED_PLINTH_HEIGHT_MM",
    "ELEVATED_PLINTH_WIDTH_MM",
    "FASTENER_PITCH_MM",
    "PANEL_LENGTH_MM",
    "TRACK_CENTRE_SPACING_MM",
    "at_grade_concrete_volume_m3",
    "at_grade_panel_mass_kg",
    "at_grade_rail_y_positions",
    "at_grade_twin_rail_y_positions",
    "at_grade_slab_panel",
    "direct_fixation_seat_count",
    "elevated_concrete_volume_m3",
    "elevated_deck_slab_panel",
    "elevated_rail_y_positions",
    "elevated_service_trough_y_positions",
]
