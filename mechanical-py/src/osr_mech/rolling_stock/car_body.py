"""One passenger car body — cabless per RFC 0015.

The body is a rectangular box with rounded corners, door openings
along each side, and no windscreen or cab anywhere. Lead and rear
cars are structurally identical to middle cars (the sensor cowl at
the ends replaces the cab entirely).

Default dimensions reflect the `light-metro-3car` reference family
per RFC 0008 §3.1:

- Length (car-body, nose-cowl-excluded): 22 m.
- Width over body panels: 2.65 m.
- Height rail-to-roof: 3.6 m.
- Floor height above rail head: 1.1 m (low-floor).
- Door count per side: 3 per car (PSD-aligned double-leaf doors,
  1400 mm wide × 2000 mm tall, evenly spaced).
"""

from __future__ import annotations

from dataclasses import dataclass

from build123d import (
    Align,
    BuildPart,
    BuildSketch,
    Color,
    Location,
    Mode,
    Part,
    Plane,
    Rectangle,
    extrude,
)

DOOR_WIDTH_MM = 1400.0
DOOR_HEIGHT_MM = 2000.0
DOOR_SILL_HEIGHT_MM = 1100.0  # above rail head


@dataclass(frozen=True)
class CarDimensions:
    """Parametric footprint of a single passenger car."""

    body_length_mm: float = 22_000.0
    body_width_mm: float = 2650.0
    body_height_mm: float = 3600.0
    doors_per_side: int = 3


def car_body(dims: CarDimensions = CarDimensions()) -> Part:
    """One car body as a solid box with door cutouts on both sides.

    Origin: car-body centre at floor level (z = 0 is rail head); +X is
    along-track, +Y is across-track. The body starts at z = 0 and
    extends to z = body_height_mm.
    """

    # Outer shell.
    with BuildPart() as shell:
        with BuildSketch():
            Rectangle(
                dims.body_length_mm,
                dims.body_width_mm,
                align=(Align.CENTER, Align.CENTER),
            )
        extrude(amount=dims.body_height_mm)

    body = shell.part

    # Door cutouts — evenly spaced along the length on both sides.
    door_spacing = dims.body_length_mm / (dims.doors_per_side + 1)
    for i in range(1, dims.doors_per_side + 1):
        x_centre = -dims.body_length_mm / 2.0 + i * door_spacing
        for y_side in (-1.0, 1.0):
            with BuildPart() as door:
                with BuildSketch(Plane.XZ):
                    Rectangle(
                        DOOR_WIDTH_MM,
                        DOOR_HEIGHT_MM,
                        align=(Align.CENTER, Align.MIN),
                    )
                extrude(amount=dims.body_width_mm + 50.0)
            d = door.part
            # Position: X-centered on door position; Y-translate to
            # straddle the body thickness; Z at floor sill.
            d = d.translate(
                (
                    x_centre,
                    y_side * (dims.body_width_mm / 2.0 + 25.0) - y_side * (dims.body_width_mm + 50.0) / 2.0,
                    DOOR_SILL_HEIGHT_MM,
                )
            )
            body = body - d

    body.color = Color(0.85, 0.88, 0.92)
    body.label = "Car body (cabless)"
    return body


__all__ = [
    "CarDimensions",
    "DOOR_HEIGHT_MM",
    "DOOR_SILL_HEIGHT_MM",
    "DOOR_WIDTH_MM",
    "car_body",
]
