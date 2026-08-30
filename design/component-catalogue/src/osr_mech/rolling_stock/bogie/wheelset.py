"""Wheelset — one axle + 2 wheels + 2 bearings + 1 brake disc.

Dimensions per RFC 0022 §3:

- Wheel diameter new: 760 mm.
- Axle length across bearings: 1 950 mm (fits the 2 400 mm
  bogie-frame width with clearance).
- Axle diameter (journal): 130 mm.
- Axle diameter (between wheels): 160 mm.
- Wheel-tread width: 135 mm.
- Wheel-flange height: 28 mm.

The CAD represents the wheel as a stepped cylinder with a flange
(simplified — the real UIC S1002 profile has a tapered tread and
a radiused flange; this approximation is accurate to within 1 %
on mass and silhouette).
"""

from __future__ import annotations

from math import cos, pi, sin

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
)

# Wheelset dimensions (RFC 0022 §3).
WHEEL_DIAMETER_NEW_MM = 760.0
WHEEL_DIAMETER_WORN_MM = 680.0
WHEEL_TREAD_WIDTH_MM = 135.0
WHEEL_FLANGE_HEIGHT_MM = 28.0
WHEEL_FLANGE_WIDTH_MM = 25.0
WHEEL_HUB_DIAMETER_MM = 240.0

AXLE_LENGTH_MM = 1_950.0
AXLE_JOURNAL_DIAMETER_MM = 130.0
AXLE_BODY_DIAMETER_MM = 160.0
AXLE_JOURNAL_LENGTH_MM = 120.0

BRAKE_DISC_DIAMETER_MM = 400.0
BRAKE_DISC_THICKNESS_MM = 45.0

BEARING_HOUSING_DIAMETER_MM = 260.0
BEARING_HOUSING_LENGTH_MM = 200.0

COLOR_WHEEL = Color(0.32, 0.32, 0.35)
COLOR_AXLE = Color(0.38, 0.38, 0.42)
COLOR_BRAKE_DISC = Color(0.22, 0.22, 0.25)
COLOR_BEARING = Color(0.55, 0.45, 0.30)
COLOR_WEB = Color(0.26, 0.27, 0.30)
COLOR_FASTENER = Color(0.62, 0.63, 0.65)
COLOR_WEAR = Color(0.10, 0.11, 0.12)


def _cylinder(radius_mm: float, length_mm: float, y_centre: float = 0.0) -> Part:
    """A cylinder with axis along Y, centred on y = y_centre."""
    from osr_mech.cad import Plane

    with BuildPart() as b:
        with BuildSketch(Plane.XZ):
            Circle(radius_mm)
        extrude(amount=length_mm)
    # extrude on Plane.XZ goes along the plane normal (-Y in
    # the CAD backend's default handedness). So the raw part spans
    # y = 0 to y = -length. Translate to put its centre at y_centre.
    p = b.part.translate((0.0, y_centre + length_mm / 2.0, 0.0))
    return p


def _wheel(wheel_diameter_mm: float) -> Compound:
    """One wheel — simplified cylinder + flange disc. Origin: wheel
    centre at y = 0, rotation axis along Y."""
    r_tread = wheel_diameter_mm / 2.0
    r_flange = r_tread + WHEEL_FLANGE_HEIGHT_MM

    tread = _cylinder(r_tread, WHEEL_TREAD_WIDTH_MM)
    tread.color = COLOR_WHEEL
    tread.label = "Wheel tread"

    flange = _cylinder(
        r_flange,
        WHEEL_FLANGE_WIDTH_MM,
        y_centre=-WHEEL_TREAD_WIDTH_MM / 2.0 + WHEEL_FLANGE_WIDTH_MM / 2.0,
    )
    flange.color = COLOR_WHEEL
    flange.label = "Wheel flange"

    web = _cylinder(r_tread - 58.0, 22.0)
    web.color = COLOR_WEB
    web.label = "Wheel web plate with shallow dish"

    hub = _cylinder(WHEEL_HUB_DIAMETER_MM / 2.0, 180.0)
    hub.color = COLOR_AXLE
    hub.label = "Pressed wheel hub"

    children: list[Part] = [tread, flange, web, hub]
    for face_y in (-98.0, 98.0):
        cover = _cylinder(92.0, 12.0, y_centre=face_y)
        cover.color = COLOR_FASTENER
        cover.label = "Wheel hub retaining cover"
        children.append(cover)
        for index in range(8):
            angle = 2.0 * pi * index / 8.0
            x = 145.0 * cos(angle)
            z = 145.0 * sin(angle)
            bolt = _cylinder(12.0, 14.0, y_centre=face_y)
            bolt = bolt.translate((x, 0.0, z))
            bolt.color = COLOR_FASTENER
            bolt.label = "Wheel web bolted retainer"
            children.append(bolt)

    for index in range(12):
        angle = 2.0 * pi * index / 12.0
        x = (r_tread - 36.0) * cos(angle)
        z = (r_tread - 36.0) * sin(angle)
        witness = _cylinder(7.0, 10.0, y_centre=WHEEL_TREAD_WIDTH_MM / 2.0 + 8.0)
        witness = witness.translate((x, 0.0, z))
        witness.color = COLOR_WEAR
        witness.label = "Wheel tyre wear witness plug"
        children.append(witness)

    return Compound(label="Wheel", children=children)


def _axle() -> Part:
    p = _cylinder(AXLE_BODY_DIAMETER_MM / 2.0, AXLE_LENGTH_MM)
    p.color = COLOR_AXLE
    p.label = "Axle"
    return p


def _brake_disc() -> Part:
    p = _cylinder(BRAKE_DISC_DIAMETER_MM / 2.0, BRAKE_DISC_THICKNESS_MM)
    p.color = COLOR_BRAKE_DISC
    p.label = "Brake disc"
    return p


def _brake_disc_details() -> list[Part]:
    out: list[Part] = []
    hub = _cylinder(82.0, BRAKE_DISC_THICKNESS_MM + 18.0)
    hub.color = COLOR_FASTENER
    hub.label = "Brake disc mounting bell"
    out.append(hub)

    for index in range(10):
        angle = 2.0 * pi * index / 10.0
        x = 132.0 * cos(angle)
        z = 132.0 * sin(angle)
        slot = _cylinder(9.0, BRAKE_DISC_THICKNESS_MM + 20.0)
        slot = slot.translate((x, 0.0, z))
        slot.color = COLOR_WEAR
        slot.label = "Brake disc ventilation drill pattern"
        out.append(slot)

    for index in range(6):
        angle = 2.0 * pi * index / 6.0
        x = 68.0 * cos(angle)
        z = 68.0 * sin(angle)
        bolt = _cylinder(11.0, BRAKE_DISC_THICKNESS_MM + 28.0)
        bolt = bolt.translate((x, 0.0, z))
        bolt.color = COLOR_FASTENER
        bolt.label = "Brake disc hub bolt"
        out.append(bolt)
    return out


def _bearing_housing(y_centre: float) -> Part:
    p = _cylinder(BEARING_HOUSING_DIAMETER_MM / 2.0, BEARING_HOUSING_LENGTH_MM, y_centre)
    p.color = COLOR_BEARING
    p.label = "Axle bearing housing"
    return p


def _bearing_end_details(y_centre: float, y_sign: float) -> list[Part]:
    out: list[Part] = []
    cover_y = y_centre + y_sign * (BEARING_HOUSING_LENGTH_MM / 2.0 + 11.0)
    cover = _cylinder(96.0, 22.0, cover_y)
    cover.color = COLOR_FASTENER
    cover.label = "Axlebox bearing end cover"
    out.append(cover)

    for index in range(6):
        angle = 2.0 * pi * index / 6.0
        x = 92.0 * cos(angle)
        z = 92.0 * sin(angle)
        bolt = _cylinder(9.0, 24.0, cover_y + y_sign * 3.0)
        bolt = bolt.translate((x, 0.0, z))
        bolt.color = COLOR_FASTENER
        bolt.label = "Axlebox cover bolt head"
        out.append(bolt)

    sensor = _cylinder(20.0, 36.0, y_centre - y_sign * 72.0)
    sensor = sensor.translate((0.0, 0.0, BEARING_HOUSING_DIAMETER_MM / 2.0 + 28.0))
    sensor.color = COLOR_WEAR
    sensor.label = "Wheel-speed sensor pickup boss"
    out.append(sensor)
    return out


def wheelset(
    wheel_diameter_mm: float = WHEEL_DIAMETER_NEW_MM,
    track_gauge_mm: float = 1_435.0,
) -> Compound:
    """One complete wheelset — 2 wheels + 1 axle + 2 bearing housings
    + 1 brake disc. Origin: axle centre at origin; axis of rotation
    along +Y. Caller sets Z = wheel-radius to put the wheels on
    the rail head."""
    parts: list[Part | Compound] = []
    parts.append(_axle())
    parts.append(_brake_disc())
    parts.extend(_brake_disc_details())
    for y_sign in (-1.0, 1.0):
        # Wheel centre = half-gauge + half-tread — puts inner face of
        # the tread on the inside edge of the gauge line.
        wheel_y = y_sign * (track_gauge_mm / 2.0 + WHEEL_TREAD_WIDTH_MM / 2.0)
        wheel = _wheel(wheel_diameter_mm)
        # Flatten the wheel Compound into Parts so .translate works
        # and the wheelset's .volume reports correctly.
        for child in list(wheel.children):
            parts.append(child.translate((0.0, wheel_y, 0.0)))
        # Bearing housing outboard of each wheel.
        bearing_y = y_sign * (
            track_gauge_mm / 2.0 + WHEEL_TREAD_WIDTH_MM + BEARING_HOUSING_LENGTH_MM / 2.0 + 20.0
        )
        parts.append(_bearing_housing(bearing_y))
        parts.extend(_bearing_end_details(bearing_y, y_sign))
    return Compound(label="Wheelset (760 mm new, 1435 mm gauge)", children=parts)


__all__ = [
    "AXLE_BODY_DIAMETER_MM",
    "AXLE_JOURNAL_DIAMETER_MM",
    "AXLE_JOURNAL_LENGTH_MM",
    "AXLE_LENGTH_MM",
    "BRAKE_DISC_DIAMETER_MM",
    "BRAKE_DISC_THICKNESS_MM",
    "BEARING_HOUSING_DIAMETER_MM",
    "BEARING_HOUSING_LENGTH_MM",
    "WHEEL_DIAMETER_NEW_MM",
    "WHEEL_DIAMETER_WORN_MM",
    "WHEEL_FLANGE_HEIGHT_MM",
    "WHEEL_TREAD_WIDTH_MM",
    "wheelset",
]
