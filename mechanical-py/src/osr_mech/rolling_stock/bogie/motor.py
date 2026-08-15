"""Heavy-vehicle-class PMSM adapted to the OSR powered bogie.

Planning ratings: 250 kW continuous / 350 kW short peak per axle on the
650–700 V nominal car DC link. Continuous duty remains a qualification
input rather than a claim about a named candidate product.
Geometry: water-jacketed housing, end-bell, terminal box, drive-end
output shaft. Represented as a TSA/ABB/Skoda-class rail motor with
cooling bands, lifting eyes, cable glands, resolver cover, nameplate,
and mounting feet. The geometry is an HM47-class RFQ envelope, not released
supplier installation data.
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
    extrude,
)
from osr_mech.rolling_stock.baseline import (
    PROMOTED_MOTOR_CONTINUOUS_KW,
    PROMOTED_MOTOR_PEAK_KW,
)

MOTOR_BODY_DIAMETER_MM = 500.0
MOTOR_BODY_LENGTH_MM = 840.0
MOTOR_ENDBELL_DIAMETER_MM = 530.0
MOTOR_ENDBELL_LENGTH_MM = 100.0
MOTOR_SHAFT_DIAMETER_MM = 88.0
MOTOR_SHAFT_LENGTH_MM = 180.0
MOTOR_TERMINAL_BOX_LENGTH_MM = 380.0
MOTOR_TERMINAL_BOX_WIDTH_MM = 260.0
MOTOR_TERMINAL_BOX_HEIGHT_MM = 195.0
MOTOR_COOLANT_PORT_DIAMETER_MM = 40.0

COLOR_MOTOR_BODY = Color(0.35, 0.38, 0.45)
COLOR_ENDBELL = Color(0.42, 0.45, 0.52)
COLOR_TERMINAL_BOX = Color(0.28, 0.30, 0.35)
COLOR_SHAFT = Color(0.55, 0.55, 0.58)
COLOR_HARDWARE = Color(0.62, 0.64, 0.66)
COLOR_HV = Color(0.80, 0.15, 0.12)


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
            from osr_mech.cad import Rectangle

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


def _accessories() -> list[Part]:
    """Small external features that make the motor visually reviewable."""

    parts: list[Part] = []
    for y in (-270.0, -90.0, 90.0, 270.0):
        parts.append(
            Box(520.0, 24.0, 28.0)
            .locate(Location((0.0, y, MOTOR_BODY_DIAMETER_MM / 2.0 - 52.0)))
        )
        parts[-1].color = COLOR_HARDWARE
        parts[-1].label = "Water-jacket cooling band"
    for x in (-170.0, 170.0):
        parts.append(
            Box(96.0, 82.0, 62.0)
            .locate(Location((x, -MOTOR_BODY_LENGTH_MM / 2.0 - 26.0, -MOTOR_BODY_DIAMETER_MM / 2.0 + 42.0)))
        )
        parts[-1].color = COLOR_HARDWARE
        parts[-1].label = "Motor mounting foot with slotted holes"
        parts.append(
            Box(96.0, 82.0, 62.0)
            .locate(Location((x, MOTOR_BODY_LENGTH_MM / 2.0 + 26.0, -MOTOR_BODY_DIAMETER_MM / 2.0 + 42.0)))
        )
        parts[-1].color = COLOR_HARDWARE
        parts[-1].label = "Motor mounting foot with slotted holes"
    for x in (-105.0, 0.0, 105.0):
        parts.append(
            Box(54.0, 48.0, 62.0)
            .locate(Location((x, -210.0, MOTOR_BODY_DIAMETER_MM / 2.0 + MOTOR_TERMINAL_BOX_HEIGHT_MM - 10.0)))
        )
        parts[-1].color = COLOR_HV
        parts[-1].label = "Traction motor HV cable gland"
    for x in (-120.0, 120.0):
        parts.append(
            Box(64.0, 36.0, 48.0)
            .locate(Location((x, 0.0, MOTOR_BODY_DIAMETER_MM / 2.0 + 42.0)))
        )
        parts[-1].color = COLOR_HARDWARE
        parts[-1].label = "Traction motor lifting eye"
    parts.append(
        Box(180.0, 24.0, 80.0).locate(
            Location((0.0, -MOTOR_BODY_LENGTH_MM / 2.0 - MOTOR_ENDBELL_LENGTH_MM - 22.0, 65.0))
        )
    )
    parts[-1].color = COLOR_TERMINAL_BOX
    parts[-1].label = "Resolver and speed-sensor cover"
    parts.append(
        Box(210.0, 12.0, 64.0).locate(
            Location((0.0, 250.0, MOTOR_BODY_DIAMETER_MM / 2.0 - 20.0))
        )
    )
    parts[-1].color = COLOR_HARDWARE
    parts[-1].label = "Supplier motor nameplate"
    return parts


def traction_motor() -> Compound:
    """Full PMSM motor assembly. Origin: motor centre at origin; axis
    along +Y; drive-end output shaft on +Y side."""
    parts: list[Part | Compound] = []
    parts.append(_body())
    parts.append(_endbell(-MOTOR_BODY_LENGTH_MM / 2.0, -1.0))
    parts.append(_endbell(MOTOR_BODY_LENGTH_MM / 2.0, 1.0))
    parts.append(_shaft())
    parts.append(_terminal_box())
    parts.extend(_accessories())
    return Compound(
        label=(
            "PMSM traction motor "
            f"(HM47-class RFQ envelope, {PROMOTED_MOTOR_CONTINUOUS_KW:.0f} kW planning cont / "
            f"{PROMOTED_MOTOR_PEAK_KW:.0f} kW peak)"
        ),
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
