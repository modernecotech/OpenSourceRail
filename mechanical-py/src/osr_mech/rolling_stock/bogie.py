"""Simplified 2-axle bogie under the car body.

Represented as a bounding-box outline + two wheel cylinders + a frame.
This is not a structural bogie design — for that, a dedicated
mechanical CAD package is needed. The purpose here is clearance-
checking: does the car body clear the bogie pivot, does the bogie
clear the track, does the wheelset pitch sit on gauge.

RFC 0008 §3.1 reference dimensions:

- Wheelbase (axle centres): 2 100 mm.
- Wheel diameter: 840 mm new, 780 mm worn (geometry uses 810 mm
  nominal for display).
- Bogie frame length: 3 500 mm.
- Bogie frame width: 2 400 mm (inside the car-body envelope).
"""

from __future__ import annotations

from build123d import (
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    Color,
    Compound,
    Part,
    Plane,
    Rectangle,
    extrude,
)

from ..common import STANDARD_GAUGE_MM

WHEELBASE_MM = 2100.0
WHEEL_DIAMETER_MM = 810.0
BOGIE_FRAME_LENGTH_MM = 3500.0
BOGIE_FRAME_WIDTH_MM = 2400.0
BOGIE_FRAME_HEIGHT_MM = 300.0


def _wheel() -> Part:
    """One wheel — simplified disc of WHEEL_DIAMETER_MM / 2 radius."""
    with BuildPart() as w:
        with BuildSketch():
            Circle(WHEEL_DIAMETER_MM / 2.0)
        extrude(amount=120.0)  # wheel tread width
    p = w.part
    p = p.rotate(Axis.Y, 90)
    p.color = Color(0.35, 0.35, 0.4)
    p.label = "Wheel"
    return p


def _frame() -> Part:
    """Bogie frame — flat box under the car."""
    with BuildPart() as f:
        with BuildSketch():
            Rectangle(
                BOGIE_FRAME_LENGTH_MM,
                BOGIE_FRAME_WIDTH_MM,
                align=(Align.CENTER, Align.CENTER),
            )
        extrude(amount=BOGIE_FRAME_HEIGHT_MM)
    p = f.part
    p.color = Color(0.25, 0.25, 0.3)
    p.label = "Bogie frame"
    return p


def bogie_assembly() -> Compound:
    """One 2-axle bogie assembly — frame + 4 wheels (2 axles, 2 wheels each).

    Origin: bogie centre (between the two axles), at the rail-head level
    (z = 0). +X along track direction.
    """

    parts: list[Part | Compound] = []

    # Frame sits above the wheels — its bottom face at z = WHEEL_DIA/2 + gap
    gap = 50.0
    frame_z = WHEEL_DIAMETER_MM / 2.0 + gap
    frame = _frame().translate((0.0, 0.0, frame_z))
    parts.append(frame)

    # Wheels at ±WHEELBASE/2 along X, ±GAUGE/2 along Y, centre at
    # z = WHEEL_DIA/2.
    for x_sign in (-1, 1):
        for y_sign in (-1, 1):
            w = _wheel()
            w = w.translate(
                (
                    x_sign * WHEELBASE_MM / 2.0,
                    y_sign * STANDARD_GAUGE_MM / 2.0,
                    WHEEL_DIAMETER_MM / 2.0,
                )
            )
            parts.append(w)

    return Compound(label="Bogie (2-axle, simplified)", children=parts)


def bogie_footprint_length_mm() -> float:
    """Along-track footprint used by `car_body` to place bogie pivots."""
    return BOGIE_FRAME_LENGTH_MM


__all__ = [
    "BOGIE_FRAME_HEIGHT_MM",
    "BOGIE_FRAME_LENGTH_MM",
    "BOGIE_FRAME_WIDTH_MM",
    "WHEELBASE_MM",
    "WHEEL_DIAMETER_MM",
    "bogie_assembly",
    "bogie_footprint_length_mm",
]
