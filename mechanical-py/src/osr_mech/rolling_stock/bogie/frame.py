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
    Cylinder,
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
COLOR_BRACKET = Color(0.30, 0.32, 0.38)
COLOR_FASTENER = Color(0.62, 0.63, 0.65)
COLOR_WEAR = Color(0.12, 0.13, 0.15)


def _detail_box(
    length: float,
    width: float,
    height: float,
    loc: tuple[float, float, float],
    label: str,
    color: Color = COLOR_BRACKET,
) -> Part:
    p = Box(length, width, height).locate(Location(loc))
    p.color = color
    p.label = label
    return p


def _bolt(
    radius: float,
    height: float,
    loc: tuple[float, float, float],
    label: str,
) -> Part:
    p = Cylinder(radius=radius, height=height).locate(Location(loc))
    p.color = COLOR_FASTENER
    p.label = label
    return p


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


def _side_beam_detail(y_sign: float) -> list[Part]:
    """Visible welded plates, access covers, and bracket lands."""

    y_outer = y_sign * (FRAME_WIDTH_MM / 2.0 + 8.0)
    y_inner = y_sign * (FRAME_WIDTH_MM / 2.0 - SIDE_BEAM_WIDTH_MM - 18.0)
    y_top = y_sign * (FRAME_WIDTH_MM / 2.0 - SIDE_BEAM_WIDTH_MM / 2.0)
    out: list[Part] = []

    out.append(
        _detail_box(
            FRAME_LENGTH_MM - 360.0,
            24.0,
            32.0,
            (0.0, y_outer, FRAME_HEIGHT_MM + 16.0),
            "Bogie side beam welded top cover plate",
        )
    )
    out.append(
        _detail_box(
            FRAME_LENGTH_MM - 520.0,
            22.0,
            34.0,
            (0.0, y_outer, 30.0),
            "Bogie side beam lower doubler plate",
        )
    )

    for x in (-1180.0, -420.0, 420.0, 1180.0):
        cover = _detail_box(
            430.0,
            18.0,
            118.0,
            (x, y_outer + y_sign * 4.0, 150.0),
            "Bogie side beam oval lightening opening doubler",
            COLOR_WEAR,
        )
        out.append(cover)
        for bolt_x in (x - 150.0, x + 150.0):
            out.append(
                _bolt(
                    17.0,
                    18.0,
                    (bolt_x, y_outer + y_sign * 9.0, 214.0),
                    "Side-beam cover plate bolt head",
                )
            )

    for x in (-1050.0, 1050.0):
        out.append(
            _detail_box(
                360.0,
                145.0,
                95.0,
                (x, y_inner, -48.0),
                "Primary suspension pedestal bracket",
            )
        )
        out.append(
            _detail_box(
                220.0,
                105.0,
                90.0,
                (x + 190.0, y_inner, 312.0),
                "Brake hanger clevis bracket",
            )
        )
        out.append(
            _detail_box(
                210.0,
                95.0,
                92.0,
                (x - 225.0, y_inner, 316.0),
                "Motor reaction-link clevis bracket",
            )
        )
        for bolt_x in (x - 130.0, x + 130.0):
            out.append(
                _bolt(
                    20.0,
                    20.0,
                    (bolt_x, y_top, FRAME_HEIGHT_MM + 24.0),
                    "Primary pedestal top M24 bolt head",
                )
            )

    for x in (-1520.0, 1520.0):
        out.append(
            _detail_box(
                180.0,
                132.0,
                210.0,
                (x, y_inner, 142.0),
                "End cross-member triangular gusset plate",
            )
        )

    return out


def _bolster_detail() -> list[Part]:
    """Secondary suspension pads, wear plates, and pivot fasteners."""

    out: list[Part] = []
    for y in (-670.0, 670.0):
        pad = Cylinder(radius=185.0, height=34.0).locate(Location((0.0, y, FRAME_HEIGHT_MM + 22.0)))
        pad.color = COLOR_WEAR
        pad.label = "Secondary air-spring wear plate"
        out.append(pad)
        for x in (-95.0, 95.0):
            out.append(
                _bolt(
                    18.0,
                    24.0,
                    (x, y, FRAME_HEIGHT_MM + 52.0),
                    "Air-spring plate countersunk fastener",
                )
            )

    out.append(
        _detail_box(
            BOLSTER_LENGTH_MM + 340.0,
            88.0,
            72.0,
            (0.0, 0.0, FRAME_HEIGHT_MM + 74.0),
            "Centre pivot yaw-damper bracket beam",
        )
    )
    for angle_x, angle_y in ((-118.0, -118.0), (-118.0, 118.0), (118.0, -118.0), (118.0, 118.0)):
        out.append(
            _bolt(
                22.0,
                28.0,
                (angle_x, angle_y, FRAME_HEIGHT_MM + PIVOT_BOSS_HEIGHT_MM + 18.0),
                "Pivot boss bolted retaining cap",
            )
        )
    return out


def _end_cross_detail(x_sign: float) -> list[Part]:
    """End cross-member cable tray brackets and jacking pads."""

    x = x_sign * (FRAME_LENGTH_MM / 2.0 - END_CROSS_LENGTH_MM / 2.0)
    out: list[Part] = []
    out.append(
        _detail_box(
            64.0,
            END_CROSS_WIDTH_MM - 220.0,
            58.0,
            (x + x_sign * 170.0, 0.0, FRAME_HEIGHT_MM + 28.0),
            "End cross-member top closing plate",
        )
    )
    for y in (-780.0, 780.0):
        out.append(
            _detail_box(
                180.0,
                170.0,
                46.0,
                (x, y, -36.0),
                "Bogie jacking and lifting pad",
                COLOR_FASTENER,
            )
        )
        out.append(
            _detail_box(
                280.0,
                86.0,
                72.0,
                (x - x_sign * 190.0, y, 286.0),
                "Brake pipe and speed-sensor cable tray bracket",
            )
        )
    return out


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
    parts.extend(_side_beam_detail(-1.0))
    parts.extend(_side_beam_detail(1.0))
    parts.extend(_bolster_detail())
    parts.extend(_end_cross_detail(-1.0))
    parts.extend(_end_cross_detail(1.0))
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
