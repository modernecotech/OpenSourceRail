"""Disc brake — caliper + electromagnetic actuator + pads.

RFC 0022 §6. One axle-mounted disc per axle; electromagnetic
caliper actuation clamps the disc. The disc itself ships with the
wheelset (see `wheelset.py`); this module models the caliper +
actuator.

Represented as a compact Knorr-Bremse/Wabtec-class wheel/axle brake
unit with a caliper bridge, pad carriers, actuator pack, parking-brake
spring cylinder, wear indicator, and service/bleed ports.
"""

from __future__ import annotations

from osr_mech.cad import (
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
COLOR_PAD = Color(0.12, 0.12, 0.13)
COLOR_HARDWARE = Color(0.62, 0.64, 0.66)
COLOR_SERVICE = Color(0.95, 0.74, 0.18)


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


def _details() -> list[Part]:
    """Pads, spring park brake, and service features."""

    parts: list[Part] = []
    for y in (-CALIPER_WIDTH_MM / 2.0 - 18.0, CALIPER_WIDTH_MM / 2.0 + 18.0):
        with BuildPart() as b:
            with BuildSketch():
                Rectangle(118.0, 34.0, align=(Align.CENTER, Align.CENTER))
            extrude(amount=96.0)
        p = b.part.rotate(Axis.X, 90)
        p = p.locate(Location((0.0, y, CALIPER_OUTER_DIAMETER_MM / 2.0 - 52.0)))
        p.color = COLOR_PAD
        p.label = "Replaceable brake pad carrier"
        parts.append(p)
    for x in (-58.0, 58.0):
        parts.append(
            Box(42.0, 198.0, 30.0).locate(
                Location((x, 0.0, CALIPER_OUTER_DIAMETER_MM / 2.0 + 54.0))
            )
        )
        parts[-1].color = COLOR_HARDWARE
        parts[-1].label = "Caliper bridge tie bolt"
    with BuildPart() as b:
        with BuildSketch():
            Circle(62.0)
        extrude(amount=110.0)
    p = b.part.rotate(Axis.X, 90)
    p = p.locate(
        Location(
            (
                0.0,
                CALIPER_WIDTH_MM / 2.0 + 70.0,
                CALIPER_OUTER_DIAMETER_MM / 2.0 - 42.0,
            )
        )
    )
    p.color = COLOR_ACTUATOR_PACK
    p.label = "SafePark spring parking-brake cylinder"
    parts.append(p)
    for x, label in ((-74.0, "Brake wear indicator pin"), (74.0, "Brake bleed and test port")):
        parts.append(
            Box(36.0, 24.0, 52.0).locate(
                Location((x, -CALIPER_WIDTH_MM / 2.0 - 112.0, CALIPER_OUTER_DIAMETER_MM / 2.0 + 18.0))
            )
        )
        parts[-1].color = COLOR_SERVICE
        parts[-1].label = label
    return parts


def brake_unit() -> Compound:
    """One disc-brake actuator unit: caliper + actuator pack.
    Origin: on the wheelset axle axis (Y = axle axis)."""
    return Compound(
        label="Brake unit (electromagnetic caliper, Knorr-Bremse class)",
        children=[_caliper_body(), _actuator_pack(), *_details()],
    )


__all__ = [
    "CALIPER_OUTER_DIAMETER_MM",
    "CALIPER_WIDTH_MM",
    "brake_unit",
]
