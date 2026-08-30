"""PRM (Persons of Reduced Mobility) zones — EN 16584 / 16585 scaffold.

Each passenger car receives:

- **Two wheelchair bays** per car, symmetrically placed opposite a
  door, with securement rails on the wall + a floor anchor pattern.
- **Priority seats** flanking each bay (2 seats per bay = 4 per car).
- **Tactile signage** paving strip along the floor leading to each
  door (visualised as a contrasting-colour strip).

The station side receives:

- **Tactile guidance path** 600 mm wide from each platform entry to
  the nearest PSD, continued along the platform edge as the EN 16584
  warning strip.
"""

from __future__ import annotations

from dataclasses import dataclass

from osr_mech.cad import (
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
from osr_mech.rolling_stock.baseline import (
    PROMOTED_LIGHT_METRO_CAR_LENGTH_MM,
    PROMOTED_LIGHT_METRO_CAR_WIDTH_MM,
)

# EN 16585-1 wheelchair bay minimums, in mm.
WHEELCHAIR_BAY_WIDTH_MM = 750.0
WHEELCHAIR_BAY_DEPTH_MM = 1_350.0
WHEELCHAIR_BAY_HEIGHT_MM = 1_500.0

TACTILE_PATH_WIDTH_MM = 600.0
TACTILE_PATH_THICKNESS_MM = 5.0

COLOR_WHEELCHAIR_ZONE = Color(0.95, 0.85, 0.20, 0.55)  # high-viz yellow
COLOR_PRIORITY_SEAT = Color(0.20, 0.55, 0.85)
COLOR_TACTILE = Color(0.98, 0.80, 0.10)


@dataclass(frozen=True)
class AccessibilitySpec:
    """Per-car accessibility quantities."""

    wheelchair_bays_per_car: int
    priority_seats_per_car: int
    help_buttons_per_car: int
    tactile_strip_count: int


# The controlled 16.5 m car ships two bays and two door pairs per side.
ACCESSIBILITY_SPEC = AccessibilitySpec(
    wheelchair_bays_per_car=2,
    priority_seats_per_car=4,
    help_buttons_per_car=4,
    tactile_strip_count=2,  # one per controlled door pair
)


@dataclass(frozen=True)
class WheelchairBay:
    """Bay envelope + location within a car (car-local coordinates)."""

    centre_x_mm: float
    centre_y_mm: float
    centre_z_mm: float  # floor level


def _wheelchair_bay_part(bay: WheelchairBay) -> Part:
    with BuildPart() as p:
        with BuildSketch():
            Rectangle(
                WHEELCHAIR_BAY_DEPTH_MM,
                WHEELCHAIR_BAY_WIDTH_MM,
                align=(Align.CENTER, Align.CENTER),
            )
        extrude(amount=WHEELCHAIR_BAY_HEIGHT_MM)
    part = p.part.locate(
        Location((bay.centre_x_mm, bay.centre_y_mm, bay.centre_z_mm))
    )
    part.color = COLOR_WHEELCHAIR_ZONE
    part.label = "Wheelchair bay (EN 16585-1)"
    return part


def _priority_seat_part(x_mm: float, y_mm: float) -> Part:
    with BuildPart() as p:
        with BuildSketch():
            Rectangle(600.0, 500.0, align=(Align.CENTER, Align.CENTER))
        extrude(amount=900.0)
    part = p.part.locate(Location((x_mm, y_mm, 0.0)))
    part.color = COLOR_PRIORITY_SEAT
    part.label = "Priority seat (EN 16585-1)"
    return part


def _tactile_strip(x_mm: float, body_width_mm: float) -> Part:
    """Yellow tactile strip leading from the door centreline inboard."""
    with BuildPart() as p:
        with BuildSketch():
            Rectangle(
                TACTILE_PATH_WIDTH_MM,
                body_width_mm - 200.0,
                align=(Align.CENTER, Align.CENTER),
            )
        extrude(amount=TACTILE_PATH_THICKNESS_MM)
    part = p.part.locate(Location((x_mm, 0.0, TACTILE_PATH_THICKNESS_MM / 2.0)))
    part.color = COLOR_TACTILE
    part.label = "Tactile guidance strip (EN 16584-3)"
    return part


def add_prm_zones_to_car(
    body_length_mm: float = PROMOTED_LIGHT_METRO_CAR_LENGTH_MM,
    body_width_mm: float = PROMOTED_LIGHT_METRO_CAR_WIDTH_MM,
    doors_per_side: int = 2,
) -> Compound:
    """Return a Compound of PRM features placed at a standard car
    layout. Designed to be appended to
    [osr_mech.rolling_stock.car_body.car_body] when a PRM-compliant
    model is requested."""
    door_spacing = body_length_mm / (doors_per_side + 1)
    door_xs = [
        -body_length_mm / 2.0 + (i + 1) * door_spacing for i in range(doors_per_side)
    ]
    parts: list[Part | Compound] = []

    # Two wheelchair bays — at the two outermost doors, +Y side.
    for door_idx in (0, len(door_xs) - 1):
        x = door_xs[door_idx]
        bay = WheelchairBay(
            centre_x_mm=x,
            centre_y_mm=body_width_mm / 2.0 - WHEELCHAIR_BAY_WIDTH_MM / 2.0 - 200.0,
            centre_z_mm=0.0,
        )
        parts.append(_wheelchair_bay_part(bay))
        # Two priority seats flanking the bay along X.
        for sign in (-1.0, 1.0):
            parts.append(
                _priority_seat_part(
                    x + sign * (WHEELCHAIR_BAY_DEPTH_MM / 2.0 + 500.0),
                    bay.centre_y_mm,
                )
            )

    # Tactile strips at every door.
    for x in door_xs:
        parts.append(_tactile_strip(x, body_width_mm))

    return Compound(label="PRM accessibility zones", children=parts)


@dataclass(frozen=True)
class PrmPlatformZone:
    """A section of tactile path on the platform."""

    centre_x_mm: float
    length_mm: float
    platform_width_mm: float


def platform_tactile_path(
    platform_length_m: float,
    platform_width_mm: float = 3_500.0,
) -> Compound:
    """Emit the platform tactile-warning strip: a raised-stud 600 mm
    band running the full platform length, offset 800 mm from the
    platform edge per EN 16584-3. Single contiguous strip (no gaps)."""
    length_mm = platform_length_m * 1000.0
    with BuildPart() as p:
        with BuildSketch():
            Rectangle(
                length_mm,
                TACTILE_PATH_WIDTH_MM,
                align=(Align.CENTER, Align.CENTER),
            )
        extrude(amount=TACTILE_PATH_THICKNESS_MM)
    strip = p.part.locate(
        Location(
            (
                length_mm / 2.0,
                platform_width_mm / 2.0 - TACTILE_PATH_WIDTH_MM / 2.0 - 800.0,
                TACTILE_PATH_THICKNESS_MM / 2.0,
            )
        )
    )
    strip.color = COLOR_TACTILE
    strip.label = "Platform tactile warning strip (EN 16584-3)"
    return Compound(label="Platform PRM path", children=[strip])


__all__ = [
    "ACCESSIBILITY_SPEC",
    "AccessibilitySpec",
    "PrmPlatformZone",
    "WheelchairBay",
    "add_prm_zones_to_car",
    "platform_tactile_path",
]
