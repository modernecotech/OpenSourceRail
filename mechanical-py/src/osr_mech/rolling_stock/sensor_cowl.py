"""Nose-cone sensor cowl — replaces the driver cab per RFC 0015.

The cowl is a rounded fairing that holds the T-OBS sensor pack. It is
*identical at both ends of the trainset* — there is no "front" or
"rear"; either end can lead on a given run. The cowl is a service
item: 10-year replacement interval per RFC 0013 M5.

Geometry:

- Length (along-track): 1800 mm.
- Width at car interface: matches car body (typ. 2650 mm for
  `light-metro-3car`).
- Height: matches car body (typ. 3600 mm).
- Profile: quarter-ellipse taper from the car interface down to a
  rounded leading face 600 mm wide × 2400 mm tall.
- Leading face carries a sensor-window cutout: 1200 mm × 1000 mm,
  RF-transparent polycarbonate (8 mm). Radar + ultrasonic see
  through it; LIDAR and cameras look through dedicated apertures.

The cowl is represented in STEP as a solid outer shell (no internal
detail — the sensor mounts are shown in the T-OBS hardware drawings
at `hardware/t-obs/schematics/v2-spec/`).
"""

from __future__ import annotations

from build123d import (
    Align,
    BuildPart,
    BuildSketch,
    Color,
    Mode,
    Part,
    Plane,
    Rectangle,
    extrude,
    loft,
)

COWL_LENGTH_MM = 1800.0
LEADING_FACE_WIDTH_MM = 600.0
LEADING_FACE_HEIGHT_MM = 2400.0
SENSOR_WINDOW_WIDTH_MM = 1200.0
SENSOR_WINDOW_HEIGHT_MM = 1000.0
SENSOR_WINDOW_INSET_MM = 200.0  # from the leading face


def sensor_cowl(
    car_width_mm: float = 2650.0,
    car_height_mm: float = 3600.0,
) -> Part:
    """One nose-cone cowl as a solid tapered body with a sensor window.

    Origin: at the car-body interface face, centred on car centreline,
    at floor level (y = 0 is the rail head). The cowl extends in +X
    along the forward-of-car direction.
    """

    # Build as a loft between the car-interface rectangle and the
    # leading-face rectangle.
    with BuildPart() as body:
        with BuildSketch(Plane.YZ) as s0:
            Rectangle(
                car_width_mm,
                car_height_mm,
                align=(Align.CENTER, Align.MIN),
            )
        with BuildSketch(Plane.YZ.offset(COWL_LENGTH_MM)) as s1:
            Rectangle(
                LEADING_FACE_WIDTH_MM,
                LEADING_FACE_HEIGHT_MM,
                align=(Align.CENTER, Align.MIN),
            )
        loft([s0.sketch, s1.sketch])

    cowl = body.part

    # Cut the sensor window out of the leading face. The window is an
    # inset rectangle on the +X face, centred vertically at 60 % of
    # the leading-face height (matches the real T-OBS sensor mount
    # height — 2.1 m above rail head for the light-metro family).
    window_centre_z = LEADING_FACE_HEIGHT_MM * 0.60
    with BuildPart() as cutter:
        with BuildSketch(Plane.YZ.offset(COWL_LENGTH_MM - SENSOR_WINDOW_INSET_MM)):
            Rectangle(
                SENSOR_WINDOW_WIDTH_MM,
                SENSOR_WINDOW_HEIGHT_MM,
                align=(Align.CENTER, Align.MIN),
            )
        extrude(amount=SENSOR_WINDOW_INSET_MM + 10.0)

    cowl = cowl - cutter.part.translate((0.0, 0.0, window_centre_z - SENSOR_WINDOW_HEIGHT_MM / 2.0))

    cowl.color = Color(0.90, 0.90, 0.92)
    cowl.label = "Nose sensor cowl"
    return cowl


__all__ = [
    "COWL_LENGTH_MM",
    "LEADING_FACE_HEIGHT_MM",
    "LEADING_FACE_WIDTH_MM",
    "SENSOR_WINDOW_HEIGHT_MM",
    "SENSOR_WINDOW_WIDTH_MM",
    "sensor_cowl",
]
