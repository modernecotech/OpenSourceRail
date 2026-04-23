"""Nose-cone sensor cowl — replaces the driver cab per RFC 0015.

The cowl is a rounded fairing that holds the T-OBS sensor pack. It
is *identical at both ends of the trainset* — there is no "front"
or "rear"; either end can lead on a given run.

Geometry:

- Length (along-track): 1800 mm.
- Width at the car interface: matches the car body.
- Height at the car interface: matches the car body.
- Profile: lofted taper from the car-body rectangle (at the
  interface) to a smaller, lower rounded rectangle at the leading
  face (600 mm wide × 2400 mm tall). Vertical edges of the cowl
  are filleted at 200 mm to match the car body.
- Leading face carries three visual cutouts:
  - A central sensor window (1200 × 1000 mm, RF-transparent
    polycarbonate) — radar + ultrasonic see through it.
  - Two LED headlight clusters (200 × 120 mm) flanking the sensor
    window.
- A livery band continues from the car body onto both flanks of
  the cowl — visual continuity between nose and car.

The cowl is a service item: 10-year replacement interval per
RFC 0013 M5.
"""

from __future__ import annotations

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Color,
    Compound,
    Location,
    Part,
    Plane,
    Rectangle,
    extrude,
    fillet,
    loft,
)

from .car_body import (
    COLOR_BODY,
    COLOR_LIVERY,
    LIVERY_BAND_HEIGHT_MM,
    LIVERY_BAND_PROUD_MM,
    LIVERY_BAND_Z_MM,
    VERTICAL_CORNER_RADIUS_MM,
)


COWL_LENGTH_MM = 1800.0
LEADING_FACE_WIDTH_MM = 600.0
LEADING_FACE_HEIGHT_MM = 2400.0
SENSOR_WINDOW_WIDTH_MM = 1200.0
SENSOR_WINDOW_HEIGHT_MM = 1000.0
SENSOR_WINDOW_INSET_MM = 80.0
HEADLIGHT_WIDTH_MM = 200.0
HEADLIGHT_HEIGHT_MM = 120.0

COLOR_SENSOR_WINDOW = Color(0.10, 0.12, 0.18)
COLOR_HEADLIGHT = Color(0.98, 0.95, 0.85)


def _cowl_shell(car_width_mm: float, car_height_mm: float) -> Part:
    """Lofted tapered body with a rounded leading face + sensor /
    headlight apertures cut through the front."""

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

    # Sensor window — centred horizontally, at ~60 % of leading-face
    # height.
    window_centre_z = LEADING_FACE_HEIGHT_MM * 0.60
    window_cut = Box(
        SENSOR_WINDOW_INSET_MM + 20.0,
        SENSOR_WINDOW_WIDTH_MM,
        SENSOR_WINDOW_HEIGHT_MM,
    ).locate(
        Location(
            (
                COWL_LENGTH_MM - SENSOR_WINDOW_INSET_MM / 2.0,
                0.0,
                window_centre_z,
            )
        )
    )
    cowl = cowl - window_cut

    # Headlights — two clusters flanking the sensor window, lower.
    for y_sign in (-1.0, 1.0):
        hc = Box(
            SENSOR_WINDOW_INSET_MM + 20.0,
            HEADLIGHT_WIDTH_MM,
            HEADLIGHT_HEIGHT_MM,
        ).locate(
            Location(
                (
                    COWL_LENGTH_MM - SENSOR_WINDOW_INSET_MM / 2.0,
                    y_sign * (SENSOR_WINDOW_WIDTH_MM / 2.0 + HEADLIGHT_WIDTH_MM),
                    window_centre_z - SENSOR_WINDOW_HEIGHT_MM * 0.35,
                )
            )
        )
        cowl = cowl - hc

    cowl.color = COLOR_BODY
    cowl.label = "Sensor cowl shell"
    return cowl


def _sensor_window_insert() -> Part:
    """Dark polycarbonate panel filling the sensor aperture — the
    RF-transparent radar window."""
    window_centre_z = LEADING_FACE_HEIGHT_MM * 0.60
    p = Box(
        20.0,
        SENSOR_WINDOW_WIDTH_MM - 20.0,
        SENSOR_WINDOW_HEIGHT_MM - 20.0,
    ).locate(
        Location(
            (
                COWL_LENGTH_MM - SENSOR_WINDOW_INSET_MM / 2.0,
                0.0,
                window_centre_z,
            )
        )
    )
    p.color = COLOR_SENSOR_WINDOW
    p.label = "Sensor window (polycarbonate)"
    return p


def _headlight_inserts() -> list[Part]:
    """Warm-white LED clusters filling each headlight aperture."""
    window_centre_z = LEADING_FACE_HEIGHT_MM * 0.60
    out: list[Part] = []
    for y_sign in (-1.0, 1.0):
        p = Box(
            20.0,
            HEADLIGHT_WIDTH_MM - 20.0,
            HEADLIGHT_HEIGHT_MM - 20.0,
        ).locate(
            Location(
                (
                    COWL_LENGTH_MM - SENSOR_WINDOW_INSET_MM / 2.0,
                    y_sign * (SENSOR_WINDOW_WIDTH_MM / 2.0 + HEADLIGHT_WIDTH_MM),
                    window_centre_z - SENSOR_WINDOW_HEIGHT_MM * 0.35,
                )
            )
        )
        p.color = COLOR_HEADLIGHT
        p.label = "Headlight (LED)"
        out.append(p)
    return out


def _livery_band_tapered(
    car_width_mm: float,
) -> list[Part]:
    """Continuation of the car-body livery band onto each flank of
    the cowl — simplified as a thin flat strip on each side."""
    out: list[Part] = []
    # The cowl tapers in width; approximate the band as a strip on a
    # vertical plane offset to the interface-face width. Visually
    # good enough at README scale.
    for y_sign in (-1.0, 1.0):
        y = y_sign * (car_width_mm / 2.0 + LIVERY_BAND_PROUD_MM / 2.0)
        band = Box(
            COWL_LENGTH_MM - 400.0,
            LIVERY_BAND_PROUD_MM,
            LIVERY_BAND_HEIGHT_MM,
        ).locate(
            Location(
                (
                    (COWL_LENGTH_MM - 400.0) / 2.0,
                    y,
                    LIVERY_BAND_Z_MM + LIVERY_BAND_HEIGHT_MM / 2.0,
                )
            )
        )
        band.color = COLOR_LIVERY
        band.label = "Livery band (nose)"
        out.append(band)
    return out


def sensor_cowl(
    car_width_mm: float = 2650.0,
    car_height_mm: float = 3600.0,
) -> Compound:
    """Full sensor cowl: shell + sensor window + headlights + livery.

    Origin: at the car-body interface face, centred on car centreline,
    at floor level (z = 0 is rail head). The cowl extends in +X
    along the forward-of-car direction.
    """
    parts: list[Part | Compound] = []
    parts.append(_cowl_shell(car_width_mm, car_height_mm))
    parts.append(_sensor_window_insert())
    parts.extend(_headlight_inserts())
    parts.extend(_livery_band_tapered(car_width_mm))
    return Compound(label="Nose sensor cowl (RFC 0015)", children=parts)


__all__ = [
    "COWL_LENGTH_MM",
    "HEADLIGHT_HEIGHT_MM",
    "HEADLIGHT_WIDTH_MM",
    "LEADING_FACE_HEIGHT_MM",
    "LEADING_FACE_WIDTH_MM",
    "SENSOR_WINDOW_HEIGHT_MM",
    "SENSOR_WINDOW_WIDTH_MM",
    "sensor_cowl",
]
