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
  face (1800 mm wide × 2800 mm tall). Vertical edges of the cowl
  are filleted at 200 mm to match the car body.
- Leading face carries a segmented full-height dark panoramic glass
  pane assembly, heated and RF-transparent, so passengers see through
  the front/back of the driverless train while the T-OBS sensors see
  out through the same aperture.
- Two warm-white LED headlamp clusters plus slim marker/DRL bars sit
  below the glass, outside the passenger sightline.
- A livery band continues from the car body onto both flanks of
  the cowl — visual continuity between nose and car.

The cowl is a service item: 10-year replacement interval per
RFC 0013 M5.
"""

from __future__ import annotations

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
LEADING_FACE_WIDTH_MM = 1800.0
LEADING_FACE_HEIGHT_MM = 2800.0
SENSOR_WINDOW_WIDTH_MM = 1200.0
SENSOR_WINDOW_HEIGHT_MM = 1000.0
SENSOR_WINDOW_INSET_MM = 80.0
PANORAMIC_GLASS_WIDTH_MM = 1500.0
PANORAMIC_GLASS_HEIGHT_MM = 1780.0
PANORAMIC_GLASS_MULLION_WIDTH_MM = 56.0
PANORAMIC_GLASS_PANE_GAP_MM = 18.0
PANORAMIC_GLASS_SIDE_CLEARANCE_MM = 36.0
HEADLIGHT_WIDTH_MM = 260.0
HEADLIGHT_HEIGHT_MM = 145.0
MARKER_LIGHT_WIDTH_MM = 420.0
MARKER_LIGHT_HEIGHT_MM = 42.0

COLOR_SENSOR_WINDOW = Color(0.04, 0.09, 0.13)
COLOR_HEADLIGHT = Color(0.98, 0.95, 0.85)
COLOR_MARKER_LIGHT = Color(0.85, 0.94, 1.00)
COLOR_ENGINEERING = Color(0.62, 0.64, 0.66)
COLOR_SERVICE = Color(0.92, 0.68, 0.12)


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

    # Driverless panoramic glass — a large shared passenger/sensor
    # aperture rather than a tiny driver windscreen.
    window_centre_z = 1850.0
    window_cut = Box(
        SENSOR_WINDOW_INSET_MM + 40.0,
        PANORAMIC_GLASS_WIDTH_MM + 180.0,
        PANORAMIC_GLASS_HEIGHT_MM + 160.0,
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

    # Headlights and marker/DRL bars — mounted below the end glass panes.
    for y_sign in (-1.0, 1.0):
        hc = Box(
            SENSOR_WINDOW_INSET_MM + 20.0,
            HEADLIGHT_WIDTH_MM,
            HEADLIGHT_HEIGHT_MM,
        ).locate(
            Location(
                (
                    COWL_LENGTH_MM - SENSOR_WINDOW_INSET_MM / 2.0,
                    y_sign * 530.0,
                    720.0,
                )
            )
        )
        cowl = cowl - hc
        marker_cut = Box(
            SENSOR_WINDOW_INSET_MM + 20.0,
            MARKER_LIGHT_WIDTH_MM,
            MARKER_LIGHT_HEIGHT_MM,
        ).locate(
            Location(
                (
                    COWL_LENGTH_MM - SENSOR_WINDOW_INSET_MM / 2.0,
                    y_sign * 520.0,
                    930.0,
                )
            )
        )
        cowl = cowl - marker_cut

    cowl.color = COLOR_BODY
    cowl.label = "Glass-pane driverless sensor cowl shell"
    return cowl


def _sensor_window_inserts() -> list[Part]:
    """Dark laminated glass panes filling the end aperture.

    The trainset has no driver windscreen, but the passenger-facing
    end is still real glazing: segmented heated glass panes with
    RF-transparent coating for the T-OBS sensor path.
    """
    window_centre_z = 1850.0
    pane_width = (
        PANORAMIC_GLASS_WIDTH_MM
        - 2.0 * PANORAMIC_GLASS_SIDE_CLEARANCE_MM
        - 2.0 * (PANORAMIC_GLASS_MULLION_WIDTH_MM + PANORAMIC_GLASS_PANE_GAP_MM)
    ) / 3.0
    pane_spacing = (
        pane_width + PANORAMIC_GLASS_MULLION_WIDTH_MM + PANORAMIC_GLASS_PANE_GAP_MM
    )
    out: list[Part] = []
    for label, y in (
        ("Left laminated panoramic end glass pane", -pane_spacing),
        ("Centre laminated panoramic end glass pane", 0.0),
        ("Right laminated panoramic end glass pane", pane_spacing),
    ):
        p = Box(
            22.0,
            pane_width,
            PANORAMIC_GLASS_HEIGHT_MM - 24.0,
        ).locate(
            Location(
                (
                    COWL_LENGTH_MM - SENSOR_WINDOW_INSET_MM / 2.0,
                    y,
                    window_centre_z,
                )
            )
        )
        p.color = COLOR_SENSOR_WINDOW
        p.label = label
        out.append(p)
    return out


def _cowl_engineering(car_width_mm: float) -> list[Part]:
    """Serviceable hardware behind the segmented glass-pane end."""

    out: list[Part] = []
    x = COWL_LENGTH_MM - SENSOR_WINDOW_INSET_MM
    window_centre_z = 1850.0
    outer_width = PANORAMIC_GLASS_WIDTH_MM + 210.0
    outer_height = PANORAMIC_GLASS_HEIGHT_MM + 230.0
    frame_thickness = 86.0
    frame_depth = 118.0
    pane_width = (
        PANORAMIC_GLASS_WIDTH_MM
        - 2.0 * PANORAMIC_GLASS_SIDE_CLEARANCE_MM
        - 2.0 * (PANORAMIC_GLASS_MULLION_WIDTH_MM + PANORAMIC_GLASS_PANE_GAP_MM)
    ) / 3.0
    pane_spacing = (
        pane_width + PANORAMIC_GLASS_MULLION_WIDTH_MM + PANORAMIC_GLASS_PANE_GAP_MM
    )

    for label, y, z, width, height in (
        (
            "Bonded panoramic end glass upper frame rail",
            0.0,
            window_centre_z + outer_height / 2.0 - frame_thickness / 2.0,
            outer_width,
            frame_thickness,
        ),
        (
            "Bonded panoramic end glass lower frame rail",
            0.0,
            window_centre_z - outer_height / 2.0 + frame_thickness / 2.0,
            outer_width,
            frame_thickness,
        ),
        (
            "Bonded panoramic end glass side frame stile",
            -outer_width / 2.0 + frame_thickness / 2.0,
            window_centre_z,
            frame_thickness,
            outer_height,
        ),
        (
            "Bonded panoramic end glass side frame stile",
            outer_width / 2.0 - frame_thickness / 2.0,
            window_centre_z,
            frame_thickness,
            outer_height,
        ),
    ):
        member = Box(frame_depth, width, height).locate(Location((x - 70.0, y, z)))
        member.color = COLOR_ENGINEERING
        member.label = label
        out.append(member)

    for y in (-pane_spacing / 2.0, pane_spacing / 2.0):
        mullion = Box(
            frame_depth - 12.0,
            PANORAMIC_GLASS_MULLION_WIDTH_MM,
            PANORAMIC_GLASS_HEIGHT_MM - 70.0,
        ).locate(
            Location((x - 52.0, y, window_centre_z))
        )
        mullion.color = COLOR_ENGINEERING
        mullion.label = "Panoramic end glass vertical mullion"
        out.append(mullion)

    crash_width = PANORAMIC_GLASS_WIDTH_MM + 420.0
    crash_height = PANORAMIC_GLASS_HEIGHT_MM + 520.0
    crash_thickness = 145.0
    crash_depth = 150.0
    for y, z, width, height in (
        (
            0.0,
            window_centre_z + crash_height / 2.0 - crash_thickness / 2.0,
            crash_width,
            crash_thickness,
        ),
        (
            0.0,
            window_centre_z - crash_height / 2.0 + crash_thickness / 2.0,
            crash_width,
            crash_thickness,
        ),
        (
            -crash_width / 2.0 + crash_thickness / 2.0,
            window_centre_z,
            crash_thickness,
            crash_height,
        ),
        (
            crash_width / 2.0 - crash_thickness / 2.0,
            window_centre_z,
            crash_thickness,
            crash_height,
        ),
    ):
        ring = Box(crash_depth, width, height).locate(
            Location((x - 175.0, y, z))
        )
        ring.color = COLOR_ENGINEERING
        ring.label = "Cowl crash ring around panoramic end glass panes"
        out.append(ring)

    centre_heater = Box(24.0, 28.0, PANORAMIC_GLASS_HEIGHT_MM - 160.0).locate(
        Location((x + 8.0, 0.0, window_centre_z))
    )
    centre_heater.color = COLOR_SERVICE
    centre_heater.label = "Heated glass centre demist trace"
    out.append(centre_heater)

    for z in (1020.0, 2680.0):
        busbar = Box(28.0, PANORAMIC_GLASS_WIDTH_MM - 120.0, 26.0).locate(
            Location((x + 4.0, 0.0, z))
        )
        busbar.color = COLOR_SERVICE
        busbar.label = "Heated glass demist busbar"
        out.append(busbar)

    for y in (-420.0, 0.0, 420.0):
        nozzle = Box(75.0, 55.0, 42.0).locate(Location((x + 18.0, y, 2780.0)))
        nozzle.color = COLOR_SERVICE
        nozzle.label = "Washer nozzle and service access cover"
        out.append(nozzle)

    desk = Box(520.0, 760.0, 260.0).locate(
        Location((COWL_LENGTH_MM - 820.0, 0.0, 1110.0))
    )
    desk.color = COLOR_ENGINEERING
    desk.label = "Emergency recovery driving desk behind glass"
    out.append(desk)

    for y_sign in (-1.0, 1.0):
        handhold = Box(420.0, 55.0, 55.0).locate(
            Location((COWL_LENGTH_MM - 980.0, y_sign * (car_width_mm / 2.0 - 470.0), 1720.0))
        )
        handhold.color = COLOR_ENGINEERING
        handhold.label = "Open-end passenger handhold rail"
        out.append(handhold)

    return out


def _headlight_inserts() -> list[Part]:
    """Warm-white LED clusters filling each headlight aperture."""
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
                    y_sign * 530.0,
                    720.0,
                )
            )
        )
        p.color = COLOR_HEADLIGHT
        p.label = "LED headlamp cluster"
        out.append(p)
        marker = Box(
            18.0,
            MARKER_LIGHT_WIDTH_MM - 20.0,
            MARKER_LIGHT_HEIGHT_MM - 8.0,
        ).locate(
            Location(
                (
                    COWL_LENGTH_MM - SENSOR_WINDOW_INSET_MM / 2.0,
                    y_sign * 520.0,
                    930.0,
                )
            )
        )
        marker.color = COLOR_MARKER_LIGHT
        marker.label = "LED marker and daytime-running light bar"
        out.append(marker)
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
    car_width_mm: float = 2850.0,
    car_height_mm: float = 3450.0,
) -> Compound:
    """Full sensor cowl: end glass panes + sensors + LED lighting + livery.

    Origin: at the car-body interface face, centred on car centreline,
    at floor level (z = 0 is rail head). The cowl extends in +X
    along the forward-of-car direction.
    """
    parts: list[Part | Compound] = []
    parts.append(_cowl_shell(car_width_mm, car_height_mm))
    parts.extend(_sensor_window_inserts())
    parts.extend(_cowl_engineering(car_width_mm))
    parts.extend(_headlight_inserts())
    parts.extend(_livery_band_tapered(car_width_mm))
    return Compound(label="Nose sensor cowl (RFC 0015)", children=parts)


__all__ = [
    "COWL_LENGTH_MM",
    "HEADLIGHT_HEIGHT_MM",
    "HEADLIGHT_WIDTH_MM",
    "LEADING_FACE_HEIGHT_MM",
    "LEADING_FACE_WIDTH_MM",
    "MARKER_LIGHT_HEIGHT_MM",
    "MARKER_LIGHT_WIDTH_MM",
    "PANORAMIC_GLASS_HEIGHT_MM",
    "PANORAMIC_GLASS_WIDTH_MM",
    "SENSOR_WINDOW_HEIGHT_MM",
    "SENSOR_WINDOW_WIDTH_MM",
    "sensor_cowl",
]
