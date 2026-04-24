"""Bogie frame — H-frame welded from hollow steel sections.

Two longitudinal side beams connected by a transverse central
bolster + two end cross-members. The central bolster carries the
pivot + secondary air-spring mounts. The end cross-members carry
the primary-suspension pedestals + traction-motor reaction links.

Represented as a set of rectangular-section beams joined at
right angles. Pocket cut-outs on the side beams are approximated
by the beam cross-section only (no actual material removal).
"""

from __future__ import annotations

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Color,
    Compound,
    Location,
    Part,
    Rectangle,
    extrude,
)

FRAME_LENGTH_MM = 3_500.0  # along track
FRAME_WIDTH_MM = 2_400.0  # across track (outer-to-outer of side beams)
FRAME_HEIGHT_MM = 280.0

SIDE_BEAM_WIDTH_MM = 160.0  # wall thickness of the H
SIDE_BEAM_TOP_Z_MM = 280.0

BOLSTER_LENGTH_MM = 500.0  # along track
BOLSTER_WIDTH_MM = FRAME_WIDTH_MM - 2 * SIDE_BEAM_WIDTH_MM
BOLSTER_HEIGHT_MM = 260.0

END_CROSS_LENGTH_MM = 300.0
END_CROSS_WIDTH_MM = BOLSTER_WIDTH_MM
END_CROSS_HEIGHT_MM = 200.0

PIVOT_BOSS_DIAMETER_MM = 320.0
PIVOT_BOSS_HEIGHT_MM = 120.0

COLOR_FRAME = Color(0.22, 0.25, 0.32)
COLOR_PIVOT_BOSS = Color(0.45, 0.45, 0.50)


def _side_beam(y_sign: float) -> Part:
    """One of the two longitudinal side beams."""
    y = y_sign * (FRAME_WIDTH_MM / 2.0 - SIDE_BEAM_WIDTH_MM / 2.0)
    with BuildPart() as b:
        with BuildSketch():
            Rectangle(FRAME_LENGTH_MM, SIDE_BEAM_WIDTH_MM, align=(Align.CENTER, Align.CENTER))
        extrude(amount=FRAME_HEIGHT_MM)
    p = b.part.locate(Location((0.0, y, 0.0)))
    p.color = COLOR_FRAME
    p.label = "Bogie side beam"
    return p


def _central_bolster() -> Part:
    """Transverse bolster at the centre — carries pivot + air-spring
    mounts."""
    with BuildPart() as b:
        with BuildSketch():
            Rectangle(BOLSTER_LENGTH_MM, BOLSTER_WIDTH_MM, align=(Align.CENTER, Align.CENTER))
        extrude(amount=BOLSTER_HEIGHT_MM)
    p = b.part.locate(Location((0.0, 0.0, (FRAME_HEIGHT_MM - BOLSTER_HEIGHT_MM) / 2.0)))
    p.color = COLOR_FRAME
    p.label = "Central bolster"
    return p


def _end_cross(x_sign: float) -> Part:
    x = x_sign * (FRAME_LENGTH_MM / 2.0 - END_CROSS_LENGTH_MM / 2.0)
    with BuildPart() as b:
        with BuildSketch():
            Rectangle(END_CROSS_LENGTH_MM, END_CROSS_WIDTH_MM, align=(Align.CENTER, Align.CENTER))
        extrude(amount=END_CROSS_HEIGHT_MM)
    p = b.part.locate(Location((x, 0.0, (FRAME_HEIGHT_MM - END_CROSS_HEIGHT_MM) / 2.0)))
    p.color = COLOR_FRAME
    p.label = "End cross-member"
    return p


def _pivot_boss() -> Part:
    """Central ball-joint pivot boss — where the car body rests."""
    from build123d import Circle

    with BuildPart() as b:
        with BuildSketch():
            Circle(PIVOT_BOSS_DIAMETER_MM / 2.0)
        extrude(amount=PIVOT_BOSS_HEIGHT_MM)
    p = b.part.locate(Location((0.0, 0.0, FRAME_HEIGHT_MM)))
    p.color = COLOR_PIVOT_BOSS
    p.label = "Pivot boss (300 mm ball joint)"
    return p


def bogie_frame() -> Compound:
    """Welded H-frame. Origin: geometric centre of the frame; +X
    along track; +Y across track; +Z vertical."""
    parts: list[Part | Compound] = []
    parts.append(_side_beam(-1.0))
    parts.append(_side_beam(1.0))
    parts.append(_central_bolster())
    parts.append(_end_cross(-1.0))
    parts.append(_end_cross(1.0))
    parts.append(_pivot_boss())
    return Compound(label="Bogie frame (welded H-frame)", children=parts)


__all__ = [
    "FRAME_HEIGHT_MM",
    "FRAME_LENGTH_MM",
    "FRAME_WIDTH_MM",
    "PIVOT_BOSS_DIAMETER_MM",
    "PIVOT_BOSS_HEIGHT_MM",
    "SIDE_BEAM_WIDTH_MM",
    "bogie_frame",
]
