"""PMSM traction motor — axle-hung per RFC 0022 §4.1.

Ratings: 180 kW continuous / 320 kW peak per axle at 750 VDC link.
Geometry: water-jacketed housing, end-bell, terminal box, drive-end
output shaft. Represented as a stepped cylinder + a rectangular
terminal box bolted to the top. Mass reference: ≤ 620 kg.
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
    extrude,
)

MOTOR_BODY_DIAMETER_MM = 470.0
MOTOR_BODY_LENGTH_MM = 780.0
MOTOR_ENDBELL_DIAMETER_MM = 500.0
MOTOR_ENDBELL_LENGTH_MM = 100.0
MOTOR_SHAFT_DIAMETER_MM = 80.0
MOTOR_SHAFT_LENGTH_MM = 180.0
MOTOR_TERMINAL_BOX_LENGTH_MM = 350.0
MOTOR_TERMINAL_BOX_WIDTH_MM = 240.0
MOTOR_TERMINAL_BOX_HEIGHT_MM = 180.0
MOTOR_COOLANT_PORT_DIAMETER_MM = 40.0

COLOR_MOTOR_BODY = Color(0.35, 0.38, 0.45)
COLOR_ENDBELL = Color(0.42, 0.45, 0.52)
COLOR_TERMINAL_BOX = Color(0.28, 0.30, 0.35)
COLOR_SHAFT = Color(0.55, 0.55, 0.58)


def _body() -> Part:
    with BuildPart() as b:
        with BuildSketch():
            Circle(MOTOR_BODY_DIAMETER_MM / 2.0)
        extrude(amount=MOTOR_BODY_LENGTH_MM)
    p = b.part.rotate(Axis.X, 90)
    p = p.locate(Location((0.0, -MOTOR_BODY_LENGTH_MM / 2.0, 0.0)))
    p.color = COLOR_MOTOR_BODY
    p.label = "Motor housing (water-jacketed)"
    return p


def _endbell(y: float, sign: float) -> Part:
    with BuildPart() as b:
        with BuildSketch():
            Circle(MOTOR_ENDBELL_DIAMETER_MM / 2.0)
        extrude(amount=MOTOR_ENDBELL_LENGTH_MM)
    p = b.part.rotate(Axis.X, 90)
    p = p.locate(Location((0.0, y + sign * MOTOR_ENDBELL_LENGTH_MM / 2.0, 0.0)))
    p.color = COLOR_ENDBELL
    p.label = "Motor end-bell"
    return p


def _shaft() -> Part:
    """Output shaft — emerges from the drive-end of the motor."""
    with BuildPart() as s:
        with BuildSketch():
            Circle(MOTOR_SHAFT_DIAMETER_MM / 2.0)
        extrude(amount=MOTOR_SHAFT_LENGTH_MM)
    p = s.part.rotate(Axis.X, 90)
    # Shaft protrudes from the +Y end of the motor (drive-end).
    p = p.locate(
        Location(
            (
                0.0,
                MOTOR_BODY_LENGTH_MM / 2.0 + MOTOR_ENDBELL_LENGTH_MM,
                0.0,
            )
        )
    )
    p.color = COLOR_SHAFT
    p.label = "Motor output shaft"
    return p


def _terminal_box() -> Part:
    """Three-phase + encoder + resolver terminal box, top of housing."""
    with BuildPart() as b:
        with BuildSketch():
            from build123d import Rectangle

            Rectangle(MOTOR_TERMINAL_BOX_WIDTH_MM, MOTOR_TERMINAL_BOX_LENGTH_MM)
        extrude(amount=MOTOR_TERMINAL_BOX_HEIGHT_MM)
    p = b.part.locate(
        Location(
            (
                0.0,
                0.0,
                MOTOR_BODY_DIAMETER_MM / 2.0 + MOTOR_TERMINAL_BOX_HEIGHT_MM / 2.0 - 30.0,
            )
        )
    )
    p.color = COLOR_TERMINAL_BOX
    p.label = "Terminal box (3-ph + encoder + resolver)"
    return p


def traction_motor() -> Compound:
    """Full PMSM motor assembly. Origin: motor centre at origin; axis
    along +Y; drive-end output shaft on +Y side."""
    parts: list[Part | Compound] = []
    parts.append(_body())
    parts.append(_endbell(-MOTOR_BODY_LENGTH_MM / 2.0, -1.0))
    parts.append(_endbell(MOTOR_BODY_LENGTH_MM / 2.0, 1.0))
    parts.append(_shaft())
    parts.append(_terminal_box())
    return Compound(
        label="PMSM traction motor (180 kW cont / 320 kW peak)",
        children=parts,
    )


__all__ = [
    "MOTOR_BODY_DIAMETER_MM",
    "MOTOR_BODY_LENGTH_MM",
    "MOTOR_ENDBELL_DIAMETER_MM",
    "MOTOR_ENDBELL_LENGTH_MM",
    "MOTOR_SHAFT_DIAMETER_MM",
    "MOTOR_SHAFT_LENGTH_MM",
    "traction_motor",
]
