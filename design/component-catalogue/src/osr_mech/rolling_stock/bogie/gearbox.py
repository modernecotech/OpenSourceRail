"""Single-stage parallel spur gearbox — RFC 0022 §4.2.

The CAD currently carries a 6.5:1 packaging seed only. Input shaft from motor; hollow output shaft rides on
the wheelset axle (i.e., the output gear wraps the axle, which is
then pressed through the output gear's bore).

Represented as a rectangular housing + input shaft stub +
centred on the wheelset axle.
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

GEARBOX_HOUSING_LENGTH_MM = 520.0  # along the axle
GEARBOX_HOUSING_WIDTH_MM = 380.0  # perpendicular to axle
GEARBOX_HOUSING_HEIGHT_MM = 420.0
GEARBOX_INPUT_BOSS_DIAMETER_MM = 180.0
GEARBOX_INPUT_BOSS_LENGTH_MM = 60.0
GEARBOX_OUTPUT_BORE_DIAMETER_MM = 180.0  # slides over axle
GEARBOX_FILTER_DIAMETER_MM = 60.0
GEARBOX_FILTER_LENGTH_MM = 140.0
# Packaging seed, not a released ratio. RFC 0021 requires re-selection from
# the qualified motor torque-speed map, new/worn wheel diameter, adhesion,
# grade, service speed, overspeed, regeneration, and 50 C thermal duty.
GEARBOX_RATIO_PROVISIONAL = 6.5
GEARBOX_RATIO = GEARBOX_RATIO_PROVISIONAL

COLOR_GEARBOX_HOUSING = Color(0.30, 0.32, 0.37)
COLOR_INPUT_BOSS = Color(0.45, 0.48, 0.55)
COLOR_FILTER = Color(0.70, 0.55, 0.20)


def _housing() -> Part:
    """Rectangular housing — holds oil + gears."""
    with BuildPart() as b:
        with BuildSketch():
            Rectangle(
                GEARBOX_HOUSING_WIDTH_MM,
                GEARBOX_HOUSING_LENGTH_MM,
                align=(Align.CENTER, Align.CENTER),
            )
        extrude(amount=GEARBOX_HOUSING_HEIGHT_MM)
    p = b.part.locate(Location((0.0, 0.0, -GEARBOX_HOUSING_HEIGHT_MM / 2.0)))
    p.color = COLOR_GEARBOX_HOUSING
    p.label = "Gearbox housing"
    return p


def _input_boss() -> Part:
    """Input boss — where the motor shaft couples in."""
    with BuildPart() as b:
        with BuildSketch():
            Circle(GEARBOX_INPUT_BOSS_DIAMETER_MM / 2.0)
        extrude(amount=GEARBOX_INPUT_BOSS_LENGTH_MM)
    p = b.part.rotate(Axis.X, 90)
    # Input boss on the +Y side of the housing, offset upward so
    # input shaft is above axle.
    p = p.locate(
        Location(
            (
                0.0,
                GEARBOX_HOUSING_LENGTH_MM / 2.0 + GEARBOX_INPUT_BOSS_LENGTH_MM / 2.0,
                140.0,
            )
        )
    )
    p.color = COLOR_INPUT_BOSS
    p.label = "Gearbox input boss"
    return p


def _oil_filter() -> Part:
    """Side-mounted oil filter — replaced from the pit."""
    with BuildPart() as b:
        with BuildSketch():
            Circle(GEARBOX_FILTER_DIAMETER_MM / 2.0)
        extrude(amount=GEARBOX_FILTER_LENGTH_MM)
    p = b.part.rotate(Axis.Y, 90)
    p = p.locate(
        Location(
            (
                GEARBOX_HOUSING_WIDTH_MM / 2.0 + GEARBOX_FILTER_LENGTH_MM / 2.0,
                0.0,
                -GEARBOX_HOUSING_HEIGHT_MM / 2.0 + 100.0,
            )
        )
    )
    p.color = COLOR_FILTER
    p.label = "Oil filter"
    return p


def gearbox() -> Compound:
    """Full gearbox assembly. Origin: on the wheelset axle (Y-axis is
    axle axis); housing straddles the axle axis at Z = 0."""
    parts: list[Part | Compound] = []
    parts.append(_housing())
    parts.append(_input_boss())
    parts.append(_oil_filter())
    return Compound(
        label=f"Gearbox (single-stage spur, {GEARBOX_RATIO}:1)",
        children=parts,
    )


__all__ = [
    "GEARBOX_HOUSING_HEIGHT_MM",
    "GEARBOX_HOUSING_LENGTH_MM",
    "GEARBOX_HOUSING_WIDTH_MM",
    "GEARBOX_RATIO",
    "gearbox",
]
