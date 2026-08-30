"""Primary + secondary suspension — RFC 0022 §5.

- **Primary** (axle → bogie frame): chevron rubber-metal block.
  Trelleborg Meta-C class. One per axle box; eight per bogie
  (two axles × two bearing housings × two chevron packs each).

- **Secondary** (bogie frame → car body): twin-bellows air spring
  with auxiliary rubber emergency bearer + lateral damper.
  Continental CF-series class.

Both represented geometrically as bodies with the characteristic
silhouette: chevron as a trapezoidal rubber block with visible
sandwich plates; air spring as a convoluted toroidal bellows.
"""

from __future__ import annotations

from osr_mech.cad import (
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    Color,
    Compound,
    Location,
    Part,
    Rectangle,
    extrude,
    loft,
    Plane,
)

# Chevron rubber-metal block.
CHEVRON_LENGTH_MM = 220.0
CHEVRON_WIDTH_MM = 140.0
CHEVRON_HEIGHT_MM = 110.0
CHEVRON_PLATE_THICKNESS_MM = 8.0

# Air spring.
AIR_SPRING_OUTER_DIAMETER_MM = 480.0
AIR_SPRING_INNER_DIAMETER_MM = 220.0  # top + bottom plate boss
AIR_SPRING_HEIGHT_MM = 220.0
AIR_SPRING_BELLOWS_DIAMETER_MM = 520.0  # bulge at mid-height

# Lateral damper.
DAMPER_DIAMETER_MM = 70.0
DAMPER_LENGTH_MM = 420.0

COLOR_RUBBER = Color(0.12, 0.12, 0.14)
COLOR_PLATE = Color(0.60, 0.60, 0.65)
COLOR_AIR_SPRING = Color(0.22, 0.24, 0.30)
COLOR_DAMPER = Color(0.52, 0.48, 0.35)


def _chevron_pack() -> Part:
    """Chevron rubber block with top + bottom metal plates.

    Origin: geometric centre at (0, 0, 0); axis of compression = Z."""
    with BuildPart() as b:
        # Bottom plate.
        with BuildSketch():
            Rectangle(CHEVRON_WIDTH_MM, CHEVRON_LENGTH_MM, align=(Align.CENTER, Align.CENTER))
        extrude(amount=CHEVRON_PLATE_THICKNESS_MM)
    bottom = b.part.locate(Location((0.0, 0.0, -CHEVRON_HEIGHT_MM / 2.0)))
    bottom.color = COLOR_PLATE
    bottom.label = "Chevron bottom plate"

    with BuildPart() as m:
        with BuildSketch():
            Rectangle(
                CHEVRON_WIDTH_MM - 10.0,
                CHEVRON_LENGTH_MM - 10.0,
                align=(Align.CENTER, Align.CENTER),
            )
        extrude(amount=CHEVRON_HEIGHT_MM - 2 * CHEVRON_PLATE_THICKNESS_MM)
    mid = m.part.locate(
        Location((0.0, 0.0, -CHEVRON_HEIGHT_MM / 2.0 + CHEVRON_PLATE_THICKNESS_MM))
    )
    mid.color = COLOR_RUBBER
    mid.label = "Chevron rubber block"

    with BuildPart() as t:
        with BuildSketch():
            Rectangle(CHEVRON_WIDTH_MM, CHEVRON_LENGTH_MM, align=(Align.CENTER, Align.CENTER))
        extrude(amount=CHEVRON_PLATE_THICKNESS_MM)
    top = t.part.locate(
        Location((0.0, 0.0, CHEVRON_HEIGHT_MM / 2.0 - CHEVRON_PLATE_THICKNESS_MM))
    )
    top.color = COLOR_PLATE
    top.label = "Chevron top plate"

    return Compound(
        label="Chevron rubber-metal pack",
        children=[bottom, mid, top],
    )


def primary_suspension() -> Compound:
    """One chevron pack for one axle-box side. Origin: at the pack
    centre; caller translates into position.

    A real bogie has 8 of these (2 axles × 2 bearing housings × 2
    packs each = 8 total); the `motor_bogie` assembly instances
    this at 8 positions."""
    pack = _chevron_pack()
    # Flatten: Compound.volume doesn't recurse, so nesting a
    # Compound inside a Compound loses the volume reporting path.
    children = list(pack.children) if pack.children else [pack]
    return Compound(
        label="Primary suspension (chevron rubber-metal, Trelleborg Meta-C class)",
        children=children,
    )


def _air_spring_top_plate() -> Part:
    with BuildPart() as p:
        with BuildSketch():
            Circle(AIR_SPRING_OUTER_DIAMETER_MM / 2.0)
        extrude(amount=12.0)
    part = p.part.locate(Location((0.0, 0.0, AIR_SPRING_HEIGHT_MM - 6.0)))
    part.color = COLOR_PLATE
    part.label = "Air spring top plate"
    return part


def _air_spring_bottom_plate() -> Part:
    with BuildPart() as p:
        with BuildSketch():
            Circle(AIR_SPRING_OUTER_DIAMETER_MM / 2.0)
        extrude(amount=12.0)
    part = p.part.locate(Location((0.0, 0.0, -6.0)))
    part.color = COLOR_PLATE
    part.label = "Air spring bottom plate"
    return part


def _air_spring_bellows() -> Part:
    """Convoluted bellows — approximated as a barrel-like lofted
    profile between the top and bottom plates."""
    with BuildPart() as b:
        # Lower rim.
        with BuildSketch() as s0:
            Circle(AIR_SPRING_OUTER_DIAMETER_MM / 2.0)
        # Mid bulge.
        with BuildSketch(Plane.XY.offset(AIR_SPRING_HEIGHT_MM / 2.0)) as s1:
            Circle(AIR_SPRING_BELLOWS_DIAMETER_MM / 2.0)
        # Upper rim.
        with BuildSketch(Plane.XY.offset(AIR_SPRING_HEIGHT_MM)) as s2:
            Circle(AIR_SPRING_OUTER_DIAMETER_MM / 2.0)
        loft([s0.sketch, s1.sketch, s2.sketch])
    p = b.part
    p.color = COLOR_AIR_SPRING
    p.label = "Air spring bellows (Continental CF-series class)"
    return p


def _lateral_damper() -> Part:
    """Lateral hydraulic damper — cylindrical body mounted
    transverse to the track."""
    with BuildPart() as b:
        with BuildSketch():
            Circle(DAMPER_DIAMETER_MM / 2.0)
        extrude(amount=DAMPER_LENGTH_MM)
    p = b.part.rotate(Axis.X, 90)
    p.color = COLOR_DAMPER
    p.label = "Lateral damper"
    return p


def secondary_suspension() -> Compound:
    """One secondary suspension group: air spring + lateral damper.

    Origin: air-spring bottom-plate centre at (0, 0, 0); air-spring
    axis along Z. Caller instances two of these per bogie."""
    parts: list[Part | Compound] = []
    parts.append(_air_spring_bottom_plate())
    parts.append(_air_spring_bellows())
    parts.append(_air_spring_top_plate())
    damper = _lateral_damper().locate(
        Location((0.0, -DAMPER_LENGTH_MM / 2.0, AIR_SPRING_HEIGHT_MM / 2.0 - 60.0))
    )
    parts.append(damper)
    return Compound(label="Secondary suspension (air spring + lateral damper)", children=parts)


__all__ = [
    "AIR_SPRING_HEIGHT_MM",
    "AIR_SPRING_OUTER_DIAMETER_MM",
    "CHEVRON_HEIGHT_MM",
    "CHEVRON_LENGTH_MM",
    "CHEVRON_WIDTH_MM",
    "DAMPER_LENGTH_MM",
    "primary_suspension",
    "secondary_suspension",
]
