"""Mechanical interface and installation hardware for the OSR car.

The main rolling-stock modules model the body, systems, and supplier
envelopes. This module fills the handoff gap between those layers:
bolsters, backing plates, rails, bond lands, retention brackets,
mounting pads, service hatches, duct hangers, and sensor/coupler
mounts. Geometry is supplier-neutral but deliberately installation
aware so the FreeCAD review assemblies can be used for mark-up.
"""

from __future__ import annotations

from collections.abc import Callable

from osr_mech.cad import Box, Color, Compound, Cylinder, Location, Part

from .bogie import WHEELBASE_MM
from .car_body import (
    BATTERY_STRAKE_BASE_Z_MM,
    BATTERY_STRAKE_HEIGHT_MM,
    BATTERY_STRAKE_WIDTH_MM,
    DOOR_HEIGHT_MM,
    DOOR_SILL_HEIGHT_MM,
    DOOR_WIDTH_MM,
    END_HIGH_FLOOR_LENGTH_MM,
    FLOOR_PLATE_THICKNESS_MM,
    FLOOR_TRANSITION_LENGTH_MM,
    HIGH_FLOOR_HEIGHT_MM,
    LOW_FLOOR_CENTRE_LENGTH_MM,
    LOW_FLOOR_HEIGHT_MM,
    WINDOW_HEIGHT_MM,
    WINDOW_MARGIN_MM,
    WINDOW_SILL_MM,
    CarDimensions,
)
from .systems import (
    BATTERY_MODULE_LENGTH_MM,
    BATTERY_MODULE_WIDTH_MM,
    COUPLER_FACE_HEIGHT_MM,
)


COLOR_STEEL = Color(0.50, 0.52, 0.55)
COLOR_STAINLESS = Color(0.72, 0.72, 0.70)
COLOR_ALUMINIUM = Color(0.68, 0.70, 0.72)
COLOR_COMPOSITE = Color(0.86, 0.86, 0.80)
COLOR_RUBBER = Color(0.04, 0.04, 0.045)
COLOR_GLASS = Color(0.24, 0.48, 0.60, 0.48)
COLOR_ACCESS = Color(0.95, 0.74, 0.18)
COLOR_HV = Color(0.85, 0.18, 0.10)
COLOR_LV = Color(0.08, 0.22, 0.52)
COLOR_HVAC = Color(0.70, 0.82, 0.86)
COLOR_SENSOR = Color(0.05, 0.07, 0.09)
COLOR_SEAT = Color(0.22, 0.34, 0.50)

BOGIE_CENTRE_X_MM = CarDimensions().body_length_mm / 2.0 - WHEELBASE_MM


def _part(part: Part, label: str, color: Color) -> Part:
    part.label = label
    part.color = color
    return part


def _box(
    length: float,
    width: float,
    height: float,
    loc: tuple[float, float, float],
    label: str,
    color: Color,
) -> Part:
    return _part(Box(length, width, height).locate(Location(loc)), label, color)


def _cyl(
    radius: float,
    height: float,
    loc: tuple[float, float, float],
    label: str,
    color: Color,
) -> Part:
    return _part(Cylinder(radius=radius, height=height).locate(Location(loc)), label, color)


def _door_centres_x(dims: CarDimensions) -> list[float]:
    spacing = dims.body_length_mm / (dims.doors_per_side + 1)
    return [
        -dims.body_length_mm / 2.0 + (index + 1) * spacing
        for index in range(dims.doors_per_side)
    ]


def _window_zones(dims: CarDimensions) -> list[tuple[float, float]]:
    doors = _door_centres_x(dims)
    half_length = dims.body_length_mm / 2.0
    half_door = DOOR_WIDTH_MM / 2.0
    edges = [-half_length] + doors + [half_length]
    zones: list[tuple[float, float]] = []
    for index in range(len(edges) - 1):
        left = edges[index] + (half_door if index > 0 else 0.0)
        right = edges[index + 1] - (half_door if index + 1 < len(edges) - 1 else 0.0)
        width = max(0.0, right - left - 2.0 * WINDOW_MARGIN_MM)
        if width >= 400.0:
            zones.append(((left + right) / 2.0, width))
    return zones


def bogie_to_chassis_connector(dims: CarDimensions = CarDimensions()) -> Compound:
    """Bolster, air-spring, yaw-damper, and hard-stop interfaces."""

    parts: list[Part] = []
    for x_sign in (-1.0, 1.0):
        x = x_sign * (dims.body_length_mm / 2.0 - WHEELBASE_MM)
        parts.extend(
            [
                _box(
                    1450.0,
                    dims.body_width_mm - 460.0,
                    190.0,
                    (x, 0.0, HIGH_FLOOR_HEIGHT_MM - 185.0),
                    "Bogie-to-chassis welded bolster box",
                    COLOR_STEEL,
                ),
                _cyl(
                    235.0,
                    90.0,
                    (x, 0.0, HIGH_FLOOR_HEIGHT_MM - 45.0),
                    "Bogie centre-pivot spherical-bearing socket",
                    COLOR_STAINLESS,
                ),
                _cyl(
                    160.0,
                    42.0,
                    (x, 0.0, HIGH_FLOOR_HEIGHT_MM + 20.0),
                    "Removable centre-pivot wear plate",
                    COLOR_STAINLESS,
                ),
            ]
        )
        for y_sign in (-1.0, 1.0):
            y = y_sign * (dims.body_width_mm / 2.0 - 620.0)
            parts.extend(
                [
                    _box(
                        520.0,
                        300.0,
                        90.0,
                        (x, y, HIGH_FLOOR_HEIGHT_MM - 75.0),
                        "Secondary air-spring chassis pad",
                        COLOR_STEEL,
                    ),
                    _box(
                        420.0,
                        120.0,
                        150.0,
                        (x + x_sign * 520.0, y_sign * (dims.body_width_mm / 2.0 - 265.0), 775.0),
                        "Yaw-damper chassis clevis bracket",
                        COLOR_STEEL,
                    ),
                    _box(
                        180.0,
                        110.0,
                        210.0,
                        (x - x_sign * 580.0, y_sign * 735.0, 735.0),
                        "Bogie lateral hard-stop wear block",
                        COLOR_RUBBER,
                    ),
                ]
            )
            for bolt_x in (-180.0, 180.0):
                for bolt_y in (-90.0, 90.0):
                    parts.append(
                        _cyl(
                            24.0,
                            24.0,
                            (x + bolt_x, y + bolt_y, HIGH_FLOOR_HEIGHT_MM - 18.0),
                            "Air-spring pad M20 bolt head",
                            COLOR_STAINLESS,
                        )
                    )
        for y in (-420.0, 420.0):
            parts.append(
                _box(
                    980.0,
                    54.0,
                    64.0,
                    (x, y, HIGH_FLOOR_HEIGHT_MM - 245.0),
                    "Bogie lift/drop safety chain anchor rail",
                    COLOR_ACCESS,
                )
            )
    return Compound(label="Bogie-to-chassis connector interface", children=parts)


def bogie_to_motor_connector() -> Compound:
    """Motor bogie reaction links, cable clamps, and coolant handoff."""

    parts: list[Part] = []
    for x_sign in (-1.0, 1.0):
        x = x_sign * WHEELBASE_MM / 2.0
        motor_y = 1080.0
        parts.extend(
            [
                _box(
                    420.0,
                    95.0,
                    155.0,
                    (x, motor_y - 285.0, 690.0),
                    "Gearbox torque-arm bogie bracket",
                    COLOR_STEEL,
                ),
                _box(
                    660.0,
                    70.0,
                    95.0,
                    (x + x_sign * 220.0, motor_y - 90.0, 760.0),
                    "Motor reaction link with elastomer bushes",
                    COLOR_STAINLESS,
                ),
                _cyl(
                    72.0,
                    80.0,
                    (x + x_sign * 555.0, motor_y - 90.0, 760.0),
                    "Motor reaction-link rubber bush",
                    COLOR_RUBBER,
                ),
                _box(
                    260.0,
                    120.0,
                    180.0,
                    (x - x_sign * 430.0, motor_y + 230.0, 760.0),
                    "PMSM motor terminal-box mounting bracket",
                    COLOR_STEEL,
                ),
                _box(
                    300.0,
                    85.0,
                    120.0,
                    (x - x_sign * 600.0, motor_y + 315.0, 760.0),
                    "Traction-motor HV quick-disconnect cradle",
                    COLOR_HV,
                ),
                _box(
                    260.0,
                    46.0,
                    78.0,
                    (x + x_sign * 120.0, motor_y + 390.0, 640.0),
                    "Motor resolver and temperature-sensor cable clamp",
                    COLOR_LV,
                ),
            ]
        )
        for hose_x in (-70.0, 70.0):
            parts.append(
                _cyl(
                    28.0,
                    74.0,
                    (x + hose_x, motor_y + 430.0, 560.0),
                    "Motor coolant quick-coupler pair",
                    COLOR_HVAC,
                )
            )
        for shim in (-155.0, 0.0, 155.0):
            parts.append(
                _box(
                    85.0,
                    18.0,
                    8.0,
                    (x + shim, motor_y - 350.0, 778.0),
                    "Motor alignment shim pack",
                    COLOR_ACCESS,
                )
            )
    return Compound(label="Bogie-to-motor connector interface", children=parts)


def low_floor_chassis(dims: CarDimensions = CarDimensions()) -> Compound:
    """Underframe/chassis with raised bogie decks and low-floor centre.

    The first FEA screen showed the original shallow ladder met stress
    margin but missed stiffness. This revision keeps the centre aisle
    low by moving depth into the side/battery zones: deep perimeter
    torsion boxes, twin inboard keel beams below the floor pan, heavier
    cross-bearers, and transfer beams into the bogie bolsters.
    """

    parts: list[Part] = []
    parts.append(
        _box(
            LOW_FLOOR_CENTRE_LENGTH_MM,
            dims.body_width_mm - 540.0,
            FLOOR_PLATE_THICKNESS_MM,
            (0.0, 0.0, LOW_FLOOR_HEIGHT_MM - FLOOR_PLATE_THICKNESS_MM / 2.0),
            "Dropped stainless low-floor centre tub",
            COLOR_STAINLESS,
        )
    )
    for y_sign in (-1.0, 1.0):
        y = y_sign * (dims.body_width_mm / 2.0 - 150.0)
        parts.append(
            _box(
                LOW_FLOOR_CENTRE_LENGTH_MM + 2.0 * FLOOR_TRANSITION_LENGTH_MM,
                240.0,
                430.0,
                (0.0, y, LOW_FLOOR_HEIGHT_MM - 150.0),
                "Deep low-floor side torsion box",
                COLOR_STEEL,
            )
        )
        parts.append(
            _box(
                dims.body_length_mm - 950.0,
                165.0,
                260.0,
                (0.0, y_sign * (dims.body_width_mm / 2.0 - 435.0), 205.0),
                "Inboard low-floor longitudinal box stringer",
                COLOR_STEEL,
            )
        )
        parts.append(
            _box(
                LOW_FLOOR_CENTRE_LENGTH_MM + 600.0,
                90.0,
                145.0,
                (0.0, y_sign * (dims.body_width_mm / 2.0 - 695.0), 470.0),
                "Battery-strake upper chord tied into side sill",
                COLOR_STEEL,
            )
        )
    for y_sign in (-1.0, 1.0):
        parts.append(
            _box(
                LOW_FLOOR_CENTRE_LENGTH_MM - 300.0,
                150.0,
                250.0,
                (0.0, y_sign * 430.0, 205.0),
                "Twin low-floor keel box beam below aisle edge",
                COLOR_STEEL,
            )
        )
    for x_sign in (-1.0, 1.0):
        deck_x = x_sign * (dims.body_length_mm / 2.0 - END_HIGH_FLOOR_LENGTH_MM / 2.0 - 280.0)
        parts.extend(
            [
                _box(
                    END_HIGH_FLOOR_LENGTH_MM,
                    dims.body_width_mm - 430.0,
                    150.0,
                    (deck_x, 0.0, HIGH_FLOOR_HEIGHT_MM - 95.0),
                    "Raised bogie-end chassis deck",
                    COLOR_STEEL,
                ),
                _box(
                    FLOOR_TRANSITION_LENGTH_MM,
                    dims.body_width_mm - 520.0,
                    95.0,
                    (
                        x_sign * (LOW_FLOOR_CENTRE_LENGTH_MM / 2.0 + FLOOR_TRANSITION_LENGTH_MM / 2.0),
                        0.0,
                        (LOW_FLOOR_HEIGHT_MM + HIGH_FLOOR_HEIGHT_MM) / 2.0,
                    ),
                    "Bolted floor ramp support cassette",
                    COLOR_ALUMINIUM,
                ),
                _box(
                    1220.0,
                    dims.body_width_mm - 360.0,
                    260.0,
                    (x_sign * BOGIE_CENTRE_X_MM, 0.0, HIGH_FLOOR_HEIGHT_MM - 245.0),
                    "Bogie bolster load-spreader crossmember",
                    COLOR_STEEL,
                ),
                _box(
                    1760.0,
                    260.0,
                    280.0,
                    (x_sign * (BOGIE_CENTRE_X_MM - 740.0), -620.0, 315.0),
                    "Low-floor-to-bolster diagonal transfer beam envelope",
                    COLOR_STEEL,
                ),
                _box(
                    1760.0,
                    260.0,
                    280.0,
                    (x_sign * (BOGIE_CENTRE_X_MM - 740.0), 620.0, 315.0),
                    "Low-floor-to-bolster diagonal transfer beam envelope",
                    COLOR_STEEL,
                ),
            ]
        )
    for x in (-7600.0, -5850.0, -4100.0, -2400.0, -800.0, 800.0, 2400.0, 4100.0, 5850.0, 7600.0):
        parts.append(
            _box(
                125.0,
                dims.body_width_mm - 520.0,
                220.0,
                (x, 0.0, 220.0),
                "Deep laser-cut underframe cross bearer",
                COLOR_STEEL,
            )
        )
        if abs(x) <= LOW_FLOOR_CENTRE_LENGTH_MM / 2.0:
            parts.append(
                _box(
                    165.0,
                    1220.0,
                    180.0,
                    (x, 0.0, 470.0),
                    "Low-floor torsion-diaphragm cross tie",
                    COLOR_STEEL,
                )
            )
    for x in _door_centres_x(dims):
        parts.append(
            _box(
                DOOR_WIDTH_MM + 720.0,
                dims.body_width_mm - 360.0,
                120.0,
                (x, 0.0, DOOR_SILL_HEIGHT_MM - 45.0),
                "Door threshold cross bearer and drain trough",
                COLOR_STAINLESS,
            )
        )
        for y_sign in (-1.0, 1.0):
            parts.append(
                _box(
                    DOOR_WIDTH_MM + 360.0,
                    150.0,
                    210.0,
                    (x, y_sign * (dims.body_width_mm / 2.0 - 610.0), 250.0),
                    "Door-zone side sill doubler plate",
                    COLOR_STEEL,
                )
            )
    return Compound(label="Low-floor chassis and underframe design", children=parts)


def side_body_frame_attachments(dims: CarDimensions = CarDimensions()) -> Compound:
    """Side frame posts, rails, and interior attachment provisions."""

    parts: list[Part] = []
    for y_sign in (-1.0, 1.0):
        y = y_sign * (dims.body_width_mm / 2.0 - 95.0)
        for x, width in _window_zones(dims):
            parts.extend(
                [
                    _box(
                        width + 420.0,
                        112.0,
                        118.0,
                        (x, y, WINDOW_SILL_MM - 120.0),
                        "Side body waist rail with window nutplates",
                        COLOR_STEEL,
                    ),
                    _box(
                        width + 420.0,
                        90.0,
                        110.0,
                        (x, y, WINDOW_SILL_MM + WINDOW_HEIGHT_MM + 140.0),
                        "Side body window header rail",
                        COLOR_STEEL,
                    ),
                    _box(
                        width - 160.0,
                        74.0,
                        82.0,
                        (x, y_sign * (dims.body_width_mm / 2.0 - 340.0), 525.0),
                        "Bench and battery top attachment rail",
                        COLOR_STEEL,
                    ),
                ]
            )
            for side in (-1.0, 1.0):
                parts.append(
                    _box(
                        120.0,
                        125.0,
                        WINDOW_HEIGHT_MM + 620.0,
                        (
                            x + side * (width / 2.0 + 150.0),
                            y,
                            WINDOW_SILL_MM + WINDOW_HEIGHT_MM / 2.0,
                        ),
                        "Side body window/seat portal post",
                        COLOR_STEEL,
                    )
                )
        for door_x in _door_centres_x(dims):
            parts.append(
                _box(
                    DOOR_WIDTH_MM + 520.0,
                    150.0,
                    180.0,
                    (door_x, y, DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM + 175.0),
                    "Door aperture structural header and operator support",
                    COLOR_STEEL,
                )
            )
            for side in (-1.0, 1.0):
                parts.append(
                    _box(
                        150.0,
                        150.0,
                        DOOR_HEIGHT_MM + 520.0,
                        (
                            door_x + side * (DOOR_WIDTH_MM / 2.0 + 180.0),
                            y,
                            DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM / 2.0,
                        ),
                        "Door aperture portal post with weld-nut strip",
                        COLOR_STEEL,
                    )
                )
        for x in (-7000.0, -3500.0, 0.0, 3500.0, 7000.0):
            parts.append(
                _box(
                    210.0,
                    34.0,
                    380.0,
                    (x, y_sign * (dims.body_width_mm / 2.0 - 24.0), 1320.0),
                    "Composite side-panel floating attachment bracket",
                    COLOR_ALUMINIUM,
                )
            )
    return Compound(label="Train side body frame components and attachments", children=parts)


def composite_body_roof_attachments(dims: CarDimensions = CarDimensions()) -> Compound:
    """Composite side body, roof panels, bond lands, and roof fasteners."""

    parts: list[Part] = []
    for y_sign in (-1.0, 1.0):
        y_skin = y_sign * (dims.body_width_mm / 2.0 + 18.0)
        parts.extend(
            [
                _box(
                    dims.body_length_mm - 1150.0,
                    36.0,
                    1180.0,
                    (0.0, y_skin, 1930.0),
                    "Composite side body panel outer skin",
                    COLOR_COMPOSITE,
                ),
                _box(
                    dims.body_length_mm - 1400.0,
                    54.0,
                    72.0,
                    (0.0, y_sign * (dims.body_width_mm / 2.0 - 35.0), 2740.0),
                    "Composite-to-cant-rail bonded shear land",
                    COLOR_ACCESS,
                ),
                _box(
                    dims.body_length_mm - 1400.0,
                    54.0,
                    64.0,
                    (0.0, y_sign * (dims.body_width_mm / 2.0 - 35.0), 1110.0),
                    "Composite-to-waist-rail bonded shear land",
                    COLOR_ACCESS,
                ),
                _box(
                    dims.body_length_mm - 1450.0,
                    74.0,
                    110.0,
                    (0.0, y_sign * (dims.body_width_mm / 2.0 - 95.0), dims.body_height_mm - 160.0),
                    "Roof cantrail clamp extrusion",
                    COLOR_ALUMINIUM,
                ),
                _box(
                    dims.body_length_mm - 1750.0,
                    100.0,
                    76.0,
                    (0.0, y_sign * (dims.body_width_mm / 2.0 + 34.0), dims.body_height_mm - 300.0),
                    "Roof gutter and water-management rail",
                    COLOR_ALUMINIUM,
                ),
            ]
        )
        for x in (-7100.0, -5200.0, -3300.0, -1400.0, 1400.0, 3300.0, 5200.0, 7100.0):
            parts.append(
                _cyl(
                    22.0,
                    20.0,
                    (x, y_sign * (dims.body_width_mm / 2.0 - 72.0), dims.body_height_mm - 96.0),
                    "Roof panel M10 isolation insert",
                    COLOR_STAINLESS,
                )
            )
    for x in (-6100.0, -3600.0, -1100.0, 1100.0, 3600.0, 6100.0):
        parts.append(
            _box(
                115.0,
                dims.body_width_mm - 430.0,
                115.0,
                (x, 0.0, dims.body_height_mm - 130.0),
                "Composite roof bow and panel splice",
                COLOR_ALUMINIUM,
            )
        )
    parts.append(
        _box(
            dims.body_length_mm - 2900.0,
            dims.body_width_mm - 760.0,
            42.0,
            (0.0, 0.0, dims.body_height_mm + 48.0),
            "Removable composite roof service panel",
            COLOR_COMPOSITE,
        )
    )
    return Compound(label="Composite train body and roof attachment package", children=parts)


def window_installations(dims: CarDimensions = CarDimensions()) -> Compound:
    """Bonded glazing, retainers, drain paths, and service tabs."""

    parts: list[Part] = []
    for y_sign in (-1.0, 1.0):
        for x, width in _window_zones(dims):
            y = y_sign * (dims.body_width_mm / 2.0 + 16.0)
            parts.extend(
                [
                    _box(
                        width,
                        30.0,
                        WINDOW_HEIGHT_MM,
                        (x, y, WINDOW_SILL_MM + WINDOW_HEIGHT_MM / 2.0),
                        "Bonded laminated window glass installation",
                        COLOR_GLASS,
                    ),
                    _box(
                        width + 170.0,
                        42.0,
                        WINDOW_HEIGHT_MM + 160.0,
                        (x, y_sign * (dims.body_width_mm / 2.0 - 22.0), WINDOW_SILL_MM + WINDOW_HEIGHT_MM / 2.0),
                        "Window aluminium bonding frame and primer land",
                        COLOR_ALUMINIUM,
                    ),
                    _box(
                        width + 260.0,
                        54.0,
                        48.0,
                        (x, y_sign * (dims.body_width_mm / 2.0 - 38.0), WINDOW_SILL_MM - 75.0),
                        "Window condensate drain channel",
                        COLOR_HVAC,
                    ),
                    _box(
                        width - 260.0,
                        18.0,
                        34.0,
                        (x, y_sign * (dims.body_width_mm / 2.0 + 42.0), WINDOW_SILL_MM + WINDOW_HEIGHT_MM + 58.0),
                        "Heated laminated glass busbar cover",
                        COLOR_HV,
                    ),
                    _box(
                        180.0,
                        16.0,
                        46.0,
                        (x - width / 2.0 + 145.0, y_sign * (dims.body_width_mm / 2.0 + 44.0), WINDOW_SILL_MM + 82.0),
                        "Glazing supplier serial plate and replacement datum",
                        COLOR_STAINLESS,
                    ),
                ]
            )
            for clip_x in (-0.42, -0.14, 0.14, 0.42):
                parts.append(
                    _box(
                        82.0,
                        24.0,
                        64.0,
                        (x + clip_x * width, y_sign * (dims.body_width_mm / 2.0 - 58.0), WINDOW_SILL_MM + WINDOW_HEIGHT_MM + 112.0),
                        "Window cassette stainless retainer clip",
                        COLOR_STAINLESS,
                    )
                )
            for clip_x in (-0.33, 0.0, 0.33):
                parts.append(
                    _box(
                        64.0,
                        22.0,
                        42.0,
                        (x + clip_x * width, y_sign * (dims.body_width_mm / 2.0 - 58.0), WINDOW_SILL_MM - 132.0),
                        "Window emergency-removal service tab",
                        COLOR_ACCESS,
                    )
                )
    return Compound(label="Window installation assembly", children=parts)


def door_mounts(dims: CarDimensions = CarDimensions()) -> Compound:
    """Door operator rails, guide channels, motor mounts, and locks."""

    parts: list[Part] = []
    for x in _door_centres_x(dims):
        for y_sign in (-1.0, 1.0):
            y = y_sign * (dims.body_width_mm / 2.0 - 65.0)
            top_z = DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM + 115.0
            parts.extend(
                [
                    _box(
                        DOOR_WIDTH_MM + 620.0,
                        120.0,
                        120.0,
                        (x, y, top_z),
                        "Door top operator rail mount",
                        COLOR_STEEL,
                    ),
                    _box(
                        DOOR_WIDTH_MM + 460.0,
                        82.0,
                        74.0,
                        (x, y_sign * (dims.body_width_mm / 2.0 - 92.0), DOOR_SILL_HEIGHT_MM - 28.0),
                        "Door bottom guide channel mount",
                        COLOR_STAINLESS,
                    ),
                    _box(
                        340.0,
                        155.0,
                        220.0,
                        (x - DOOR_WIDTH_MM / 2.0 - 300.0, y, top_z + 75.0),
                        "Door operator motor mounting plate",
                        COLOR_STEEL,
                    ),
                    _box(
                        180.0,
                        95.0,
                        280.0,
                        (x + DOOR_WIDTH_MM / 2.0 + 240.0, y, 1240.0),
                        "Door lock keeper adjustable mount",
                        COLOR_STEEL,
                    ),
                ]
            )
            for roller_x in (-470.0, -160.0, 160.0, 470.0):
                parts.append(
                    _cyl(
                        42.0,
                        32.0,
                        (x + roller_x, y_sign * (dims.body_width_mm / 2.0 - 132.0), top_z - 8.0),
                        "Door hanger roller mounting boss",
                        COLOR_STAINLESS,
                    )
                )
            for shim_x in (-520.0, 0.0, 520.0):
                parts.append(
                    _box(
                        90.0,
                        14.0,
                        8.0,
                        (x + shim_x, y_sign * (dims.body_width_mm / 2.0 - 136.0), top_z + 82.0),
                        "Door rail adjustment shim pack",
                        COLOR_ACCESS,
                    )
                )
    return Compound(label="Door mount hardware assembly", children=parts)


def door_design() -> Compound:
    """Reference double-leaf door design with glazing and seals."""

    parts: list[Part] = []
    leaf_width = (DOOR_WIDTH_MM - 36.0) / 2.0
    for leaf_sign in (-1.0, 1.0):
        x = leaf_sign * (leaf_width / 2.0 + 9.0)
        parts.extend(
            [
                _box(
                    leaf_width,
                    58.0,
                    DOOR_HEIGHT_MM - 70.0,
                    (x, 0.0, DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM / 2.0),
                    "Pressed aluminium sliding door leaf shell",
                    COLOR_ALUMINIUM,
                ),
                _box(
                    leaf_width - 190.0,
                    24.0,
                    1140.0,
                    (x, 36.0, DOOR_SILL_HEIGHT_MM + 1120.0),
                    "Door bonded glazing cassette",
                    COLOR_GLASS,
                ),
                _box(
                    34.0,
                    70.0,
                    DOOR_HEIGHT_MM - 130.0,
                    (x - leaf_sign * (leaf_width / 2.0 - 22.0), 58.0, DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM / 2.0),
                    "Obstruction-sensitive leading-edge seal",
                    COLOR_RUBBER,
                ),
                _box(
                    leaf_width,
                    34.0,
                    38.0,
                    (x, 52.0, DOOR_SILL_HEIGHT_MM + 18.0),
                    "Door lower brush and weather seal",
                    COLOR_RUBBER,
                ),
                _box(
                    220.0,
                    80.0,
                    88.0,
                    (x, -22.0, DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM + 85.0),
                    "Door top hanger cassette",
                    COLOR_STAINLESS,
                ),
                _box(
                    120.0,
                    46.0,
                    64.0,
                    (x, -16.0, DOOR_SILL_HEIGHT_MM - 42.0),
                    "Door bottom guide shoe",
                    COLOR_STAINLESS,
                ),
            ]
        )
    parts.append(
        _box(
            120.0,
            64.0,
            DOOR_HEIGHT_MM - 160.0,
            (0.0, 74.0, DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM / 2.0),
            "Door centre meeting seal and latch strip",
            COLOR_RUBBER,
        )
    )
    return Compound(label="Door design reference assembly", children=parts)


def door_installations(dims: CarDimensions = CarDimensions()) -> Compound:
    """Door cassette, threshold, pocket, gap filler, and harness install."""

    parts: list[Part | Compound] = []
    for x in _door_centres_x(dims):
        for y_sign in (-1.0, 1.0):
            parts.extend(
                [
                    _box(
                        DOOR_WIDTH_MM + 320.0,
                        92.0,
                        DOOR_HEIGHT_MM + 340.0,
                        (x, y_sign * (dims.body_width_mm / 2.0 - 44.0), DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM / 2.0),
                        "Door cassette installed envelope",
                        Color(0.08, 0.18, 0.32),
                    ),
                    _box(
                        DOOR_WIDTH_MM + 610.0,
                        180.0,
                        86.0,
                        (x, y_sign * (dims.body_width_mm / 2.0 - 12.0), DOOR_SILL_HEIGHT_MM - 42.0),
                        "Door sill threshold extrusion with drainage",
                        COLOR_STAINLESS,
                    ),
                    _box(
                        DOOR_WIDTH_MM + 160.0,
                        98.0,
                        64.0,
                        (x, y_sign * (dims.body_width_mm / 2.0 + 56.0), DOOR_SILL_HEIGHT_MM + 22.0),
                        "Deployable door gap-filler cassette",
                        COLOR_ACCESS,
                    ),
                    _box(
                        540.0,
                        78.0,
                        132.0,
                        (x - DOOR_WIDTH_MM / 2.0 - 390.0, y_sign * (dims.body_width_mm / 2.0 - 84.0), 2260.0),
                        "Door cable-chain pocket and service loop",
                        COLOR_LV,
                    ),
                    _box(
                        DOOR_WIDTH_MM + 920.0,
                        42.0,
                        DOOR_HEIGHT_MM + 520.0,
                        (x, y_sign * (dims.body_width_mm / 2.0 + 92.0), DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM / 2.0),
                        "Door leaf swept-volume service clearance",
                        Color(0.92, 0.72, 0.18, 0.24),
                    ),
                ]
            )
            for pin_x in (-DOOR_WIDTH_MM / 2.0 - 165.0, DOOR_WIDTH_MM / 2.0 + 165.0):
                parts.append(
                    _cyl(
                        20.0,
                        40.0,
                        (x + pin_x, y_sign * (dims.body_width_mm / 2.0 - 120.0), DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM + 210.0),
                        "Door cassette datum pin",
                        COLOR_STAINLESS,
                    )
                )
    return Compound(label="Door installation assembly", children=parts)


def door_to_body_installations(dims: CarDimensions = CarDimensions()) -> Compound:
    """Body-side brackets and backing plates for fitting door modules."""

    parts: list[Part] = []
    for x in _door_centres_x(dims):
        for y_sign in (-1.0, 1.0):
            y = y_sign * (dims.body_width_mm / 2.0 - 112.0)
            parts.append(
                _box(
                    DOOR_WIDTH_MM + 760.0,
                    44.0,
                    98.0,
                    (x, y, DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM + 275.0),
                    "Door-to-body bolted header backing plate",
                    COLOR_STEEL,
                )
            )
            parts.append(
                _box(
                    DOOR_WIDTH_MM + 540.0,
                    38.0,
                    58.0,
                    (x, y_sign * (dims.body_width_mm / 2.0 - 62.0), DOOR_SILL_HEIGHT_MM - 98.0),
                    "Door-to-body sill backing plate",
                    COLOR_STEEL,
                )
            )
            for side in (-1.0, 1.0):
                post_x = x + side * (DOOR_WIDTH_MM / 2.0 + 210.0)
                parts.extend(
                    [
                        _box(
                            86.0,
                            42.0,
                            DOOR_HEIGHT_MM + 520.0,
                            (post_x, y, DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM / 2.0),
                            "Door-to-body vertical backing plate",
                            COLOR_STEEL,
                        ),
                        _box(
                            58.0,
                            26.0,
                            DOOR_HEIGHT_MM + 160.0,
                            (post_x + side * 76.0, y_sign * (dims.body_width_mm / 2.0 - 48.0), DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM / 2.0),
                            "Door bulb-seal compression land",
                            COLOR_RUBBER,
                        ),
                    ]
                )
                for z in (620.0, 1120.0, 1620.0, 2120.0):
                    parts.append(
                        _cyl(
                            18.0,
                            16.0,
                            (post_x, y_sign * (dims.body_width_mm / 2.0 - 142.0), z),
                            "Door body-side M12 weld-nut datum",
                            COLOR_STAINLESS,
                        )
                    )
    return Compound(label="Door installation onto body interface", children=parts)


def cabin_flooring(dims: CarDimensions = CarDimensions()) -> Compound:
    """Floor panels, access hatches, ramps, thresholds, and trims."""

    parts: list[Part] = [
        _box(
            LOW_FLOOR_CENTRE_LENGTH_MM - 480.0,
            980.0,
            42.0,
            (0.0, 0.0, LOW_FLOOR_HEIGHT_MM + 42.0),
            "Low-floor centre aisle anti-slip flooring panel",
            COLOR_ACCESS,
        )
    ]
    parts.append(
        _box(
            LOW_FLOOR_CENTRE_LENGTH_MM - 420.0,
            dims.body_width_mm - 980.0,
            8.0,
            (0.0, 0.0, LOW_FLOOR_HEIGHT_MM + 72.0),
            "Altro Transflor class 2 mm anti-slip floor covering",
            COLOR_RUBBER,
        )
    )
    for y_sign in (-1.0, 1.0):
        for x, width in _window_zones(dims):
            floor_z = HIGH_FLOOR_HEIGHT_MM + 42.0 if abs(x) > LOW_FLOOR_CENTRE_LENGTH_MM / 2.0 else LOW_FLOOR_HEIGHT_MM + 42.0
            parts.append(
                _box(
                    width - 220.0,
                    560.0,
                    42.0,
                    (x, y_sign * (dims.body_width_mm / 2.0 - 640.0), floor_z),
                    "Removable floor panel above service bay",
                    COLOR_ALUMINIUM,
                )
            )
            parts.append(
                _box(
                    min(width - 360.0, 1320.0),
                    420.0,
                    24.0,
                    (x, y_sign * (dims.body_width_mm / 2.0 - 525.0), floor_z + 36.0),
                    "Battery service hatch in cabin floor",
                    COLOR_STEEL,
                )
            )
            parts.append(
                _box(
                    width - 260.0,
                    520.0,
                    8.0,
                    (x, y_sign * (dims.body_width_mm / 2.0 - 640.0), floor_z + 68.0),
                    "Pre-cut rail flooring service-bay patch",
                    COLOR_RUBBER,
                )
            )
        for door_x in _door_centres_x(dims):
            parts.append(
                _box(
                    DOOR_WIDTH_MM + 360.0,
                    720.0,
                    46.0,
                    (door_x, y_sign * (dims.body_width_mm / 2.0 - 370.0), DOOR_SILL_HEIGHT_MM + 24.0),
                    "Door threshold floor insert",
                    COLOR_STAINLESS,
                )
            )
    for x_sign in (-1.0, 1.0):
        parts.append(
            _box(
                980.0,
                dims.body_width_mm - 760.0,
                58.0,
                (x_sign * (LOW_FLOOR_CENTRE_LENGTH_MM / 2.0 + 520.0), 0.0, (LOW_FLOOR_HEIGHT_MM + HIGH_FLOOR_HEIGHT_MM) / 2.0),
                "Cabin floor ramp cassette",
                COLOR_ALUMINIUM,
            )
        )
        for step in (0.0, 360.0):
            parts.append(
                _box(
                    320.0,
                    dims.body_width_mm - 840.0,
                    42.0,
                    (x_sign * (LOW_FLOOR_CENTRE_LENGTH_MM / 2.0 + 820.0 + step), 0.0, HIGH_FLOOR_HEIGHT_MM + 30.0),
                    "Raised-deck step tread insert",
                    COLOR_ACCESS,
                )
            )
    return Compound(label="Cabin flooring installation package", children=parts)


def battery_installations(dims: CarDimensions = CarDimensions()) -> Compound:
    """Battery trays, restraints, vents, isolation, and service hardware."""

    parts: list[Part] = []
    z_base = BATTERY_STRAKE_BASE_Z_MM
    z_mid = z_base + BATTERY_STRAKE_HEIGHT_MM / 2.0
    x_offsets = (-6100.0, -4200.0, 4200.0, 6100.0)
    for side in (-1.0, 1.0):
        y = side * (dims.body_width_mm / 2.0 - BATTERY_STRAKE_WIDTH_MM / 2.0 - 40.0)
        for x in x_offsets:
            parts.extend(
                [
                    _box(
                        BATTERY_MODULE_LENGTH_MM + 180.0,
                        BATTERY_MODULE_WIDTH_MM + 120.0,
                        86.0,
                        (x, y, z_base + 45.0),
                        "Battery installation sliding tray and drain pan",
                        COLOR_STEEL,
                    ),
                    _box(
                        BATTERY_MODULE_LENGTH_MM + 40.0,
                        34.0,
                        52.0,
                        (x, y - side * (BATTERY_MODULE_WIDTH_MM / 2.0 + 42.0), z_mid + 188.0),
                        "Battery module stainless retention strap",
                        COLOR_STAINLESS,
                    ),
                    _box(
                        BATTERY_MODULE_LENGTH_MM - 160.0,
                        48.0,
                        66.0,
                        (x, y + side * (BATTERY_MODULE_WIDTH_MM / 2.0 + 54.0), z_mid + 75.0),
                        "Battery vent manifold to exterior burst panel",
                        COLOR_HVAC,
                    ),
                    _box(
                        180.0,
                        96.0,
                        135.0,
                        (x - 590.0, y - side * 150.0, z_mid + 50.0),
                        "Battery service disconnect and interlock plug",
                        COLOR_HV,
                    ),
                    _box(
                        BATTERY_MODULE_LENGTH_MM + 80.0,
                        BATTERY_MODULE_WIDTH_MM + 70.0,
                        24.0,
                        (x, y, z_base + 96.0),
                        "Battery pack rubber isolation mat",
                        COLOR_RUBBER,
                    ),
                ]
            )
            for rail_y in (-1.0, 1.0):
                parts.append(
                    _box(
                        BATTERY_MODULE_LENGTH_MM + 120.0,
                        26.0,
                        38.0,
                        (x, y + rail_y * (BATTERY_MODULE_WIDTH_MM / 2.0 + 35.0), z_base + 128.0),
                        "Battery module sliding service rail",
                        COLOR_STAINLESS,
                    )
                )
        parts.append(
            _box(
                4120.0,
                32.0,
                42.0,
                (0.0, side * (dims.body_width_mm / 2.0 - 390.0), z_mid + 232.0),
                "Insulated battery string busbar retention rail",
                COLOR_HV,
            )
        )
    return Compound(label="Battery installation assembly", children=parts)


def bench_on_battery_installations(dims: CarDimensions = CarDimensions()) -> Compound:
    """Longitudinal bench seats mounted on top of battery strakes."""

    parts: list[Part] = []
    for x, width in _window_zones(dims):
        low_zone = abs(x) <= LOW_FLOOR_CENTRE_LENGTH_MM / 2.0
        seat_z = 520.0 if low_zone else HIGH_FLOOR_HEIGHT_MM + 170.0
        back_z = 870.0 if low_zone else HIGH_FLOOR_HEIGHT_MM + 520.0
        for y_sign in (-1.0, 1.0):
            y = y_sign * (dims.body_width_mm / 2.0 - 390.0)
            parts.extend(
                [
                    _box(
                        width - 260.0,
                        390.0,
                        120.0,
                        (x, y, seat_z),
                        "Bench seat pan above battery installation",
                        COLOR_SEAT,
                    ),
                    _box(
                        width - 260.0,
                        78.0,
                        680.0,
                        (x, y_sign * (dims.body_width_mm / 2.0 - 210.0), back_z),
                        "Bench backrest mounted to side frame",
                        COLOR_SEAT,
                    ),
                    _box(
                        width - 120.0,
                        64.0,
                        74.0,
                        (x, y_sign * (dims.body_width_mm / 2.0 - 485.0), BATTERY_STRAKE_BASE_Z_MM + BATTERY_STRAKE_HEIGHT_MM + 36.0),
                        "Bench cantilever rail over battery strake",
                        COLOR_STEEL,
                    ),
                    _box(
                        width - 320.0,
                        42.0,
                        58.0,
                        (x, y_sign * (dims.body_width_mm / 2.0 - 304.0), seat_z - 84.0),
                        "Hinged bench service-release rail",
                        COLOR_ACCESS,
                    ),
                ]
            )
            for bracket_x in (-0.38, -0.13, 0.13, 0.38):
                parts.append(
                    _box(
                        86.0,
                        120.0,
                        310.0,
                        (x + bracket_x * width, y_sign * (dims.body_width_mm / 2.0 - 470.0), seat_z - 180.0),
                        "Bench cantilever triangular support bracket",
                        COLOR_STEEL,
                    )
                )
    return Compound(label="Bench installation on top of batteries", children=parts)


def internal_lighting_installation(dims: CarDimensions = CarDimensions()) -> Compound:
    """LED strip mounts, emergency lighting, and ceiling cable support."""

    parts: list[Part] = []
    for y_sign in (-1.0, 1.0):
        y = y_sign * 545.0
        parts.append(
            _box(
                dims.body_length_mm - 3300.0,
                72.0,
                44.0,
                (0.0, y, 2920.0),
                "Internal LED light strip aluminium mounting channel",
                COLOR_ACCESS,
            )
        )
        for x in (-6500.0, -5300.0, -4100.0, -2900.0, -1700.0, -500.0, 700.0, 1900.0, 3100.0, 4300.0, 5500.0, 6700.0):
            parts.append(
                _box(
                    62.0,
                    94.0,
                    54.0,
                    (x, y, 2958.0),
                    "Lighting channel spring clip bracket",
                    COLOR_STAINLESS,
                )
            )
        parts.append(
            _box(
                dims.body_length_mm - 3900.0,
                42.0,
                54.0,
                (0.0, y_sign * 825.0, 2865.0),
                "Lighting low-voltage cable tray",
                COLOR_LV,
            )
        )
    for x in (-5600.0, -1850.0, 1850.0, 5600.0):
        parts.append(
            _box(
                360.0,
                135.0,
                70.0,
                (x, 0.0, 2940.0),
                "Emergency lighting and exit-sign bracket",
                COLOR_ACCESS,
            )
        )
    for x in _door_centres_x(dims):
        for y_sign in (-1.0, 1.0):
            parts.append(
                _box(
                    DOOR_WIDTH_MM + 280.0,
                    64.0,
                    54.0,
                    (x, y_sign * (dims.body_width_mm / 2.0 - 380.0), 2440.0),
                    "Doorway puddle-light mounting rail",
                    COLOR_ACCESS,
                )
            )
    return Compound(label="Internal lighting installation assembly", children=parts)


def hvac_roof_ducting_installation(dims: CarDimensions = CarDimensions()) -> Compound:
    """Rooftop HVAC curbs, ducts, diffusers, drains, and access panels."""

    parts: list[Part] = []
    hvac_x = dims.body_length_mm / 2.0 - 2_100.0
    for x in (-hvac_x, hvac_x):
        parts.extend(
            [
                _box(
                    1480.0,
                    1180.0,
                    86.0,
                    (x, 0.0, dims.body_height_mm + 45.0),
                    "Roof air-conditioner bolted curb and gasket land",
                    COLOR_STEEL,
                ),
                _box(
                    1320.0,
                    1020.0,
                    390.0,
                    (x, 0.0, dims.body_height_mm + 265.0),
                    "Roof-mounted air-conditioner service envelope",
                    COLOR_HVAC,
                ),
                _box(
                    1180.0,
                    52.0,
                    290.0,
                    (x, -535.0, dims.body_height_mm + 285.0),
                    "Rail HVAC condenser intake grille",
                    COLOR_STAINLESS,
                ),
                _box(
                    1180.0,
                    52.0,
                    290.0,
                    (x, 535.0, dims.body_height_mm + 285.0),
                    "Rail HVAC evaporator service grille",
                    COLOR_STAINLESS,
                ),
                _box(
                    410.0,
                    610.0,
                    74.0,
                    (x - 420.0, 0.0, dims.body_height_mm + 482.0),
                    "Fresh-air pressure-protection damper",
                    COLOR_STEEL,
                ),
                _box(
                    420.0,
                    430.0,
                    790.0,
                    (x, 0.0, 3220.0),
                    "HVAC roof-to-saloon drop duct",
                    COLOR_HVAC,
                ),
                _box(
                    680.0,
                    1040.0,
                    38.0,
                    (x, 0.0, dims.body_height_mm + 80.0),
                    "HVAC condensate drip tray and roof drain",
                    COLOR_STAINLESS,
                ),
                _box(
                    580.0,
                    420.0,
                    56.0,
                    (x + 410.0, 0.0, 3095.0),
                    "Return-air filter cassette access frame",
                    COLOR_STAINLESS,
                ),
            ]
        )
        for y in (-520.0, 520.0):
            parts.append(
                _cyl(
                    28.0,
                    70.0,
                    (x + 590.0, y, dims.body_height_mm + 62.0),
                    "HVAC roof drain downpipe connector",
                    COLOR_HVAC,
                )
            )
    parts.append(
        _box(
            dims.body_length_mm - 2850.0,
            380.0,
            230.0,
            (0.0, 0.0, 3130.0),
            "HVAC centre supply duct with insulation",
            COLOR_HVAC,
        )
    )
    for y_sign in (-1.0, 1.0):
        parts.append(
            _box(
                dims.body_length_mm - 3300.0,
                190.0,
                165.0,
                (0.0, y_sign * 980.0, 3005.0),
                "HVAC side return-air duct",
                COLOR_HVAC,
            )
        )
        for x in (-6100.0, -3050.0, 0.0, 3050.0, 6100.0):
            parts.append(
                _box(
                    540.0,
                    64.0,
                    46.0,
                    (x, y_sign * 420.0, 2922.0),
                    "HVAC diffuser mounting frame",
                    COLOR_STAINLESS,
                )
            )
    for x in (-5200.0, -2600.0, 0.0, 2600.0, 5200.0):
        parts.append(
            _box(
                80.0,
                520.0,
                52.0,
                (x, 0.0, 3258.0),
                "HVAC duct hanger bracket to roof bow",
                COLOR_STEEL,
            )
        )
    return Compound(label="HVAC ducting and roof air-conditioner installation", children=parts)


def screen_speaker_mountings(dims: CarDimensions = CarDimensions()) -> Compound:
    """Passenger screen, speaker, and PA/data mounting hardware."""

    parts: list[Part] = []
    for x in _door_centres_x(dims):
        for y_sign in (-1.0, 1.0):
            parts.extend(
                [
                    _box(
                        620.0,
                        58.0,
                        360.0,
                        (x, y_sign * (dims.body_width_mm / 2.0 - 215.0), 2580.0),
                        "Internal passenger screen VESA backing plate",
                        COLOR_STEEL,
                    ),
                    _box(
                        540.0,
                        52.0,
                        320.0,
                        (x, y_sign * (dims.body_width_mm / 2.0 - 180.0), 2580.0),
                        "Passenger information screen installed envelope",
                        COLOR_SENSOR,
                    ),
                    _box(
                        180.0,
                        70.0,
                        58.0,
                        (x + DOOR_WIDTH_MM / 2.0 + 260.0, y_sign * (dims.body_width_mm / 2.0 - 245.0), 2550.0),
                        "Screen harness strain-relief gland plate",
                        COLOR_LV,
                    ),
                ]
            )
    for x in (-6600.0, -4200.0, -1800.0, 1800.0, 4200.0, 6600.0):
        for y_sign in (-1.0, 1.0):
            parts.extend(
                [
                    _box(
                        210.0,
                        72.0,
                        72.0,
                        (x, y_sign * 840.0, 2870.0),
                        "Ceiling speaker pod mounting bracket",
                        COLOR_STEEL,
                    ),
                    _cyl(
                        88.0,
                        42.0,
                        (x, y_sign * 840.0, 2835.0),
                        "PA speaker grille and acoustic backbox",
                        COLOR_SENSOR,
                    ),
                ]
            )
    parts.append(
        _box(
            dims.body_length_mm - 3800.0,
            72.0,
            56.0,
            (0.0, 0.0, 2840.0),
            "PIS and speaker data trunking rail",
            COLOR_LV,
        )
    )
    parts.append(
        _box(
            640.0,
            330.0,
            170.0,
            (-6100.0, 0.0, 2690.0),
            "Televic/Luminator PA amplifier mounting tray",
            COLOR_LV,
        )
    )
    parts.append(
        _box(
            520.0,
            280.0,
            120.0,
            (6100.0, 0.0, 2690.0),
            "Passenger information controller service tray",
            COLOR_LV,
        )
    )
    return Compound(label="Internal screen mounting and speaker installation", children=parts)


def external_lighting_lidar_system(dims: CarDimensions = CarDimensions()) -> Compound:
    """Front/back exterior lights, LIDAR, radar, cameras, and washers."""

    parts: list[Part] = []
    for x_sign in (-1.0, 1.0):
        x = x_sign * (dims.body_length_mm / 2.0 + 55.0)
        parts.extend(
            [
                _box(
                    92.0,
                    1160.0,
                    1360.0,
                    (x, 0.0, 2070.0),
                    "Front/back external sensor mounting backplate",
                    COLOR_STEEL,
                ),
                _box(
                    170.0,
                    240.0,
                    120.0,
                    (x + x_sign * 76.0, 0.0, 2550.0),
                    "Front/back roofline LIDAR adjustable mount",
                    COLOR_SENSOR,
                ),
                _box(
                    240.0,
                    310.0,
                    175.0,
                    (x + x_sign * 110.0, 0.0, 2670.0),
                    "Railway LiDAR weatherproof service shroud",
                    COLOR_STEEL,
                ),
                _box(
                    180.0,
                    40.0,
                    96.0,
                    (x + x_sign * 152.0, 0.0, 2550.0),
                    "Heated LIDAR optical cover glass",
                    COLOR_GLASS,
                ),
                _box(
                    260.0,
                    220.0,
                    92.0,
                    (x + x_sign * 82.0, 0.0, 2190.0),
                    "Front/back mmWave radar and radome mount",
                    COLOR_SENSOR,
                ),
                _box(
                    520.0,
                    90.0,
                    130.0,
                    (x + x_sign * 112.0, 430.0, 2320.0),
                    "Rail Vision class front camera pod mount",
                    COLOR_SENSOR,
                ),
                _box(
                    320.0,
                    84.0,
                    125.0,
                    (x + x_sign * 112.0, -430.0, 2320.0),
                    "Thermal camera sealed mount and heater pad",
                    COLOR_SENSOR,
                ),
                _box(
                    710.0,
                    76.0,
                    94.0,
                    (x + x_sign * 96.0, 0.0, 1840.0),
                    "Stereo camera and washer-nozzle carrier",
                    COLOR_SENSOR,
                ),
            ]
        )
        for y in (-520.0, 520.0):
            parts.extend(
                [
                    _box(
                        200.0,
                        210.0,
                        160.0,
                        (x + x_sign * 98.0, y, 1320.0),
                        "LED headlight and marker-light sealed cassette",
                        COLOR_ACCESS,
                    ),
                    _box(
                        150.0,
                        54.0,
                        44.0,
                        (x + x_sign * 132.0, y, 1550.0),
                        "LED daytime-running-light blade mount",
                        COLOR_ACCESS,
                    ),
                    _cyl(
                        42.0,
                        26.0,
                        (x + x_sign * 150.0, y, 1840.0),
                        "Heated camera lens retaining ring",
                        COLOR_GLASS,
                    ),
                ]
            )
        for y in (-620.0, 620.0):
            parts.append(
                _box(
                    145.0,
                    70.0,
                    86.0,
                    (x + x_sign * 140.0, y, 1720.0),
                    "Sensor washer nozzle and heater block",
                    COLOR_HVAC,
                )
            )
    return Compound(label="External lighting and front/back LIDAR system", children=parts)


def train_connector_mount_pair(dims: CarDimensions = CarDimensions()) -> Compound:
    """End connector/coupler pockets for joining or recovering trains."""

    parts: list[Part] = []
    for x_sign in (-1.0, 1.0):
        x = x_sign * (dims.body_length_mm / 2.0 + 110.0)
        parts.extend(
            [
                _box(
                    920.0,
                    1060.0,
                    620.0,
                    (x, 0.0, COUPLER_FACE_HEIGHT_MM),
                    "Train connector mount crashworthy coupler pocket",
                    COLOR_STEEL,
                ),
                _box(
                    120.0,
                    920.0,
                    540.0,
                    (x - x_sign * 475.0, 0.0, COUPLER_FACE_HEIGHT_MM),
                    "Train connector mount bolted shear plate",
                    COLOR_STAINLESS,
                ),
                _box(
                    820.0,
                    290.0,
                    230.0,
                    (x + x_sign * 340.0, 0.0, COUPLER_FACE_HEIGHT_MM),
                    "Automatic train connector drawgear support",
                    Color(0.16, 0.16, 0.18),
                ),
                _box(
                    260.0,
                    180.0,
                    180.0,
                    (x + x_sign * 710.0, -330.0, COUPLER_FACE_HEIGHT_MM - 45.0),
                    "Train-to-train electrical jumper mounting head",
                    COLOR_HV,
                ),
                _box(
                    210.0,
                    120.0,
                    92.0,
                    (x + x_sign * 770.0, -330.0, COUPLER_FACE_HEIGHT_MM + 105.0),
                    "Dellner Type 10 D-REX Ethernet contact carrier",
                    COLOR_LV,
                ),
                _box(
                    360.0,
                    120.0,
                    145.0,
                    (x + x_sign * 705.0, 330.0, COUPLER_FACE_HEIGHT_MM - 35.0),
                    "Automatic coupler pneumatic manifold block",
                    COLOR_STAINLESS,
                ),
                _box(
                    1180.0,
                    dims.body_width_mm - 420.0,
                    240.0,
                    (x - x_sign * 255.0, 0.0, 930.0),
                    "Anti-climber and recovery tow load beam",
                    COLOR_STEEL,
                ),
            ]
        )
        for y in (-340.0, -170.0, 170.0, 340.0):
            for z in (-190.0, 190.0):
                parts.append(
                    _cyl(
                        24.0,
                        28.0,
                        (x - x_sign * 535.0, y, COUPLER_FACE_HEIGHT_MM + z),
                        "Train connector M24 pocket bolt head",
                        COLOR_STAINLESS,
                    )
                )
        for y in (-105.0, 105.0):
            parts.append(
                _cyl(
                    32.0,
                    120.0,
                    (x + x_sign * 720.0, y, COUPLER_FACE_HEIGHT_MM - 230.0),
                    "Train brake-pipe connector support",
                    COLOR_RUBBER,
                )
            )
    return Compound(label="Connector mount for other trains", children=parts)


def mechanical_interface_package(dims: CarDimensions = CarDimensions()) -> Compound:
    """All mechanical interface packages for one self-contained car."""

    return Compound(
        label="Complete mechanical interface package for one car",
        children=[
            bogie_to_chassis_connector(dims),
            bogie_to_motor_connector(),
            low_floor_chassis(dims),
            side_body_frame_attachments(dims),
            composite_body_roof_attachments(dims),
            window_installations(dims),
            door_mounts(dims),
            door_design().translate((0.0, 0.0, 0.0)),
            door_installations(dims),
            door_to_body_installations(dims),
            cabin_flooring(dims),
            battery_installations(dims),
            bench_on_battery_installations(dims),
            internal_lighting_installation(dims),
            hvac_roof_ducting_installation(dims),
            screen_speaker_mountings(dims),
            external_lighting_lidar_system(dims),
            train_connector_mount_pair(dims),
        ],
    )


INTERFACE_BUILDERS: dict[str, Callable[[], Compound]] = {
    "bogie-to-chassis-connector": bogie_to_chassis_connector,
    "bogie-to-motor-connector": bogie_to_motor_connector,
    "low-floor-chassis": low_floor_chassis,
    "side-body-frame-attachments": side_body_frame_attachments,
    "composite-body-roof-attachments": composite_body_roof_attachments,
    "window-installations": window_installations,
    "door-mounts": door_mounts,
    "door-design": door_design,
    "door-installations": door_installations,
    "door-to-body-installations": door_to_body_installations,
    "cabin-flooring": cabin_flooring,
    "battery-installations": battery_installations,
    "bench-on-battery-installations": bench_on_battery_installations,
    "internal-lighting-installation": internal_lighting_installation,
    "hvac-roof-ducting-installation": hvac_roof_ducting_installation,
    "screen-speaker-mountings": screen_speaker_mountings,
    "external-lighting-lidar-system": external_lighting_lidar_system,
    "train-connector-mount-pair": train_connector_mount_pair,
    "mechanical-interface-package": mechanical_interface_package,
}


__all__ = [
    "INTERFACE_BUILDERS",
    "battery_installations",
    "bench_on_battery_installations",
    "bogie_to_chassis_connector",
    "bogie_to_motor_connector",
    "cabin_flooring",
    "composite_body_roof_attachments",
    "door_design",
    "door_installations",
    "door_mounts",
    "door_to_body_installations",
    "external_lighting_lidar_system",
    "hvac_roof_ducting_installation",
    "internal_lighting_installation",
    "low_floor_chassis",
    "mechanical_interface_package",
    "screen_speaker_mountings",
    "side_body_frame_attachments",
    "train_connector_mount_pair",
    "window_installations",
]
