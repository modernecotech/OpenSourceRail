"""Precast pre-stressed concrete mono-block sleeper (B70-class).

One sleeper per ~650 mm per RFC 0009 — cast at a regional yard,
trucked to site on a 40-tonne flatbed (≈ 120 sleepers/truck), placed
and aligned with a gantry before ballast is tamped.

Dimensions follow the EN 13230 B70 family:
- Length: 2600 mm.
- Cross-section (centre): 200 mm × 175 mm (W × H).
- Cross-section (rail seat): 300 mm × 230 mm (W × H, flared).
- Mass: ~320 kg (prestressed concrete).
"""

from __future__ import annotations

from build123d import (
    Align,
    BuildPart,
    BuildSketch,
    Color,
    Location,
    Part,
    Plane,
    Polygon,
    extrude,
    loft,
)

SLEEPER_LENGTH_MM = 2600.0
SLEEPER_END_WIDTH_MM = 300.0
SLEEPER_END_HEIGHT_MM = 230.0
SLEEPER_MID_WIDTH_MM = 200.0
SLEEPER_MID_HEIGHT_MM = 175.0
SLEEPER_MASS_KG = 320.0
SLEEPER_RAIL_SEAT_FROM_END_MM = 350.0


def mono_block_sleeper() -> Part:
    """Single EN 13230 B70-class prestressed mono-block sleeper.

    Built as a loft between three cross-sections — flared rail-seat,
    narrower centre, and flared rail-seat again — which captures the
    classic "dog-bone" side elevation without the interior pre-stressing
    strands (those are a vendor spec).
    """

    def _section_at(x_mm: float) -> tuple[tuple[float, float], ...]:
        # Linear blend between end-flare and centre-narrow bands.
        half_len = SLEEPER_LENGTH_MM / 2.0
        # Distance from nearer end.
        d_end = min(x_mm, SLEEPER_LENGTH_MM - x_mm)
        # Transition over 500 mm either side, then hold.
        band = min(d_end / 500.0, 1.0)
        w = SLEEPER_END_WIDTH_MM + (SLEEPER_MID_WIDTH_MM - SLEEPER_END_WIDTH_MM) * band
        h = SLEEPER_END_HEIGHT_MM + (SLEEPER_MID_HEIGHT_MM - SLEEPER_END_HEIGHT_MM) * band
        hw = w / 2.0
        return (
            (-hw, 0.0),
            (hw, 0.0),
            (hw, h),
            (-hw, h),
        )

    stations_mm = [0.0, 500.0, SLEEPER_LENGTH_MM / 2.0, SLEEPER_LENGTH_MM - 500.0, SLEEPER_LENGTH_MM]

    sketches = []
    with BuildPart() as sleeper:
        for x in stations_mm:
            with BuildSketch(Plane.YZ.offset(x)) as sk:
                Polygon(*_section_at(x), align=(Align.CENTER, Align.MIN))
            sketches.append(sk.sketch)
        loft(sketches)

    part = sleeper.part
    part.color = Color(0.7, 0.7, 0.68)
    part.label = "Mono-block sleeper (B70)"
    return part


def rail_seat_positions() -> tuple[float, float]:
    """X-positions (mm) of the two rail-seats along the sleeper, measured
    from the sleeper's -X end. The track-panel assembly uses these to
    place the rails."""
    return (SLEEPER_RAIL_SEAT_FROM_END_MM, SLEEPER_LENGTH_MM - SLEEPER_RAIL_SEAT_FROM_END_MM)


__all__ = [
    "SLEEPER_END_HEIGHT_MM",
    "SLEEPER_END_WIDTH_MM",
    "SLEEPER_LENGTH_MM",
    "SLEEPER_MASS_KG",
    "SLEEPER_MID_HEIGHT_MM",
    "SLEEPER_MID_WIDTH_MM",
    "SLEEPER_RAIL_SEAT_FROM_END_MM",
    "mono_block_sleeper",
    "rail_seat_positions",
]
