"""Disc brake — caliper + electromagnetic actuator + pads.

RFC 0022 §6. One axle-mounted disc per axle; electromagnetic
caliper actuation clamps the disc. The disc itself ships with the
wheelset (see `wheelset.py`); this module models the caliper +
actuator.

Represented as a C-shaped clamshell housing straddling the disc,
plus a cylindrical actuator pack on the inboard face.
"""

from __future__ import annotations

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Circle,
    Color,
    Compound,
    Location,
    Part,
    Rectangle,
    extrude,
)

CALIPER_OUTER_DIAMETER_MM = 460.0  # wraps the 400 mm disc
CALIPER_WIDTH_MM = 150.0  # along axle axis
CALIPER_HEIGHT_MM = 220.0  # chord height
CALIPER_ARC_ANGLE_DEG = 60.0  # angular span of the caliper arms
ACTUATOR_PACK_DIAMETER_MM = 90.0
ACTUATOR_PACK_LENGTH_MM = 90.0

COLOR_CALIPER = Color(0.22, 0.22, 0.28)
COLOR_ACTUATOR_PACK = Color(0.45, 0.48, 0.55)


def _caliper_body() -> Part:
    """Simplified caliper: a short cylindrical band with a slot for
    the disc. Represented as a rectangular block straddling the disc
    plane; a real caliper is C-shaped, but a block is enough for
    CAD-sanity at this level."""
    with BuildPart() as b:
        with BuildSketch():
            Rectangle(CALIPER_WIDTH_MM, CALIPER_HEIGHT_MM, align=(Align.CENTER, Align.CENTER))
        extrude(amount=80.0)
    p = b.part.rotate(Axis.X, 90)
    p = p.locate(Location((0.0, 0.0, CALIPER_OUTER_DIAMETER_MM / 2.0 - 50.0)))
    p.color = COLOR_CALIPER
    p.label = "Brake caliper"
    return p


def _actuator_pack() -> Part:
    """Cylindrical electromagnetic actuator pack on the caliper face."""
    with BuildPart() as b:
        with BuildSketch():
            Circle(ACTUATOR_PACK_DIAMETER_MM / 2.0)
        extrude(amount=ACTUATOR_PACK_LENGTH_MM)
    p = b.part.rotate(Axis.X, 90)
    p = p.locate(
        Location(
            (
                0.0,
                -CALIPER_WIDTH_MM / 2.0 - ACTUATOR_PACK_LENGTH_MM / 2.0,
                CALIPER_OUTER_DIAMETER_MM / 2.0 - 50.0,
            )
        )
    )
    p.color = COLOR_ACTUATOR_PACK
    p.label = "Electromagnetic actuator pack"
    return p


def brake_unit() -> Compound:
    """One disc-brake actuator unit: caliper + actuator pack.
    Origin: on the wheelset axle axis (Y = axle axis)."""
    return Compound(
        label="Brake unit (electromagnetic caliper, Knorr-Bremse class)",
        children=[_caliper_body(), _actuator_pack()],
    )


__all__ = [
    "CALIPER_OUTER_DIAMETER_MM",
    "CALIPER_WIDTH_MM",
    "brake_unit",
]
