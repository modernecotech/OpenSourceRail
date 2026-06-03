"""Train-level systems layered onto the structural car + bogie CAD.

These are supplier-neutral envelope assemblies for the equipment that
turns the structural trainset into a complete train: couplers, inter-car
connections, door modules, batteries, charging contacts, cabinets, and
the T-OBS sensor package. They are deliberately envelope-first; the
selected supplier owns internal child-part detail in v2 drawings.
"""

from __future__ import annotations

from dataclasses import dataclass
from build123d import Box, Color, Compound, Cylinder, Location, Part

from .car_body import (
    BATTERY_STRAKE_BASE_Z_MM,
    BATTERY_STRAKE_HEIGHT_MM,
    BATTERY_STRAKE_WIDTH_MM,
    DOOR_HEIGHT_MM,
    DOOR_SILL_HEIGHT_MM,
    DOOR_WIDTH_MM,
    CarDimensions,
)
from .sensor_cowl import COWL_LENGTH_MM


COLOR_COUPLER = Color(0.16, 0.16, 0.18)
COLOR_CRASH = Color(0.75, 0.55, 0.22)
COLOR_DOOR = Color(0.08, 0.17, 0.30)
COLOR_BATTERY = Color(0.18, 0.28, 0.42)
COLOR_HV = Color(0.80, 0.15, 0.12)
COLOR_HVAC = Color(0.12, 0.45, 0.62)
COLOR_ELECTRONICS = Color(0.18, 0.35, 0.25)
COLOR_SENSOR = Color(0.05, 0.08, 0.10)
COLOR_ACCESS = Color(0.95, 0.80, 0.10)
COLOR_METAL = Color(0.62, 0.64, 0.66)
COLOR_RUBBER = Color(0.04, 0.04, 0.045)
COLOR_GLASS = Color(0.35, 0.58, 0.70, 0.50)

COUPLER_FACE_HEIGHT_MM = 720.0
BATTERY_MODULES_PER_CAR = 8
BATTERY_MODULE_LENGTH_MM = 1450.0
BATTERY_MODULE_WIDTH_MM = BATTERY_STRAKE_WIDTH_MM - 70.0
BATTERY_MODULE_HEIGHT_MM = BATTERY_STRAKE_HEIGHT_MM - 80.0
RAIL_LIDAR_LENGTH_MM = 165.0
RAIL_LIDAR_WIDTH_MM = 125.0
RAIL_LIDAR_HEIGHT_MM = 96.0


@dataclass(frozen=True)
class TrainsetSystemLayout:
    """System placement context for one trainset."""

    car_centres_x: tuple[float, ...]
    total_length_mm: float
    dims: CarDimensions


def system_layout(dims: CarDimensions, car_count: int) -> TrainsetSystemLayout:
    """Return X placement anchors matching `trainset.trainset`."""

    total_length_mm = car_count * dims.body_length_mm
    x_cursor = -total_length_mm / 2.0
    centres = []
    for index in range(car_count):
        centres.append(x_cursor + dims.body_length_mm / 2.0)
        x_cursor += dims.body_length_mm
    return TrainsetSystemLayout(
        car_centres_x=tuple(centres),
        total_length_mm=total_length_mm,
        dims=dims,
    )


def _door_centres_x(dims: CarDimensions) -> list[float]:
    spacing = dims.body_length_mm / (dims.doors_per_side + 1)
    return [
        -dims.body_length_mm / 2.0 + (i + 1) * spacing
        for i in range(dims.doors_per_side)
    ]


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


def end_coupler(end_sign: float = 1.0) -> Compound:
    """COTS automatic coupler integration model.

    The visible features follow the common Scharfenberg Type 10
    interface family: central coupling cone, guide horns, electrical
    head, brake-pipe hoses, shank, bolted shear plate, and crash
    absorber cartridge.
    """

    parts: list[Part] = [
        _box(
            330.0,
            470.0,
            300.0,
            (end_sign * 190.0, 0.0, COUPLER_FACE_HEIGHT_MM),
            "Scharfenberg Type 10 coupler head",
            COLOR_COUPLER,
        ),
        _cyl(
            125.0,
            160.0,
            (end_sign * 285.0, 0.0, COUPLER_FACE_HEIGHT_MM),
            "Coupling cone and centering face",
            COLOR_METAL,
        ),
        _box(
            210.0,
            120.0,
            160.0,
            (end_sign * 310.0, -330.0, COUPLER_FACE_HEIGHT_MM - 55.0),
            "Automatic electrical-head contact block",
            COLOR_HV,
        ),
        _box(
            700.0,
            250.0,
            210.0,
            (-end_sign * 220.0, 0.0, COUPLER_FACE_HEIGHT_MM),
            "Coupler shank and drawgear carrier",
            COLOR_COUPLER,
        ),
        _box(
            80.0,
            860.0,
            520.0,
            (-end_sign * 575.0, 0.0, COUPLER_FACE_HEIGHT_MM),
            "Bolted coupler shear plate",
            COLOR_METAL,
        ),
        _box(
            820.0,
            720.0,
            400.0,
            (-end_sign * 960.0, 0.0, COUPLER_FACE_HEIGHT_MM),
            "EN 15227 crash absorber cartridge",
            COLOR_CRASH,
        ),
    ]
    for y in (-255.0, 255.0):
        parts.append(
            _box(
                250.0,
                72.0,
                165.0,
                (end_sign * 240.0, y, COUPLER_FACE_HEIGHT_MM + 95.0),
                "Scharfenberg guide horn",
                COLOR_COUPLER,
            )
        )
        parts.append(
            _box(
                160.0,
                34.0,
                115.0,
                (end_sign * 375.0, y, COUPLER_FACE_HEIGHT_MM + 10.0),
                "Guide horn replaceable wear plate",
                COLOR_METAL,
            )
        )
    for y in (-135.0, 135.0):
        parts.append(
            _box(
                118.0,
                70.0,
                105.0,
                (end_sign * 365.0, y, COUPLER_FACE_HEIGHT_MM + 8.0),
                "Automatic coupler lock jaw block",
                COLOR_COUPLER,
            )
        )
    parts.append(
        _box(
            92.0,
            205.0,
            54.0,
            (end_sign * 376.0, 0.0, COUPLER_FACE_HEIGHT_MM + 168.0),
            "Coupler latch inspection cover",
            COLOR_METAL,
        )
    )
    parts.append(
        _box(
            54.0,
            360.0,
            38.0,
            (end_sign * 355.0, 0.0, COUPLER_FACE_HEIGHT_MM - 170.0),
            "Manual coupler release handle",
            COLOR_ACCESS,
        )
    )
    parts.append(
        _box(
            86.0,
            170.0,
            185.0,
            (end_sign * 334.0, -330.0, COUPLER_FACE_HEIGHT_MM + 118.0),
            "Electrical-head hinged protective cover",
            COLOR_METAL,
        )
    )
    for z in (-98.0, -42.0, 42.0, 98.0):
        parts.append(
            _cyl(
                16.0,
                28.0,
                (end_sign * 354.0, -330.0, COUPLER_FACE_HEIGHT_MM + z),
                "Electrical-head sprung contact pin",
                COLOR_METAL,
            )
        )
    for y in (-95.0, 95.0):
        parts.append(
            _cyl(
                28.0,
                140.0,
                (end_sign * 300.0, y, COUPLER_FACE_HEIGHT_MM - 205.0),
                "Brake-pipe hose coupling",
                COLOR_RUBBER,
            )
        )
        parts.append(
            _box(
                78.0,
                88.0,
                46.0,
                (end_sign * 318.0, y, COUPLER_FACE_HEIGHT_MM - 285.0),
                "Brake-pipe hose strain-relief saddle",
                COLOR_METAL,
            )
        )
    for y in (-310.0, -155.0, 155.0, 310.0):
        for z in (-170.0, 170.0):
            parts.append(
                _cyl(
                    20.0,
                    18.0,
                    (-end_sign * 535.0, y, COUPLER_FACE_HEIGHT_MM + z),
                    "Coupler pocket M24 bolt head",
                    COLOR_METAL,
                )
            )
    c = Compound(label="End coupler and crash-energy assembly", children=parts)
    return c


def inter_car_articulation() -> Compound:
    """Semi-permanent inter-car connection with drag-chain trainline."""

    parts: list[Part] = []
    for index, x in enumerate((-360.0, -240.0, -120.0, 0.0, 120.0, 240.0, 360.0)):
        parts.append(
            _box(
                68.0,
                2350.0 + (index % 2) * 120.0,
                2850.0 + (index % 2) * 90.0,
                (x, 0.0, 1850.0),
                "Inter-car articulation bellows pleat",
                Color(0.15, 0.15, 0.17),
            )
        )
    parts.append(
        _box(
            940.0,
            330.0,
            210.0,
            (0.0, 0.0, COUPLER_FACE_HEIGHT_MM),
            "Semi-permanent drawbar",
            COLOR_COUPLER,
        )
    )
    for x in (-430.0, 430.0):
        parts.append(
            _cyl(
                120.0,
                90.0,
                (x, 0.0, COUPLER_FACE_HEIGHT_MM),
                "Drawbar spherical joint housing",
                COLOR_METAL,
            )
        )
    for i in range(11):
        parts.append(
            _box(
                70.0,
                170.0,
                130.0,
                (-350.0 + i * 70.0, 900.0, 1250.0 + (i % 2) * 18.0),
                "TCN-E / CAN-FD / auxiliary drag-chain",
                COLOR_HV,
            )
        )
    parts.append(
        _box(
            900.0,
            1700.0,
            55.0,
            (0.0, 0.0, 420.0),
            "Articulation anti-slip floor bridge",
            COLOR_METAL,
        )
    )
    c = Compound(label="Inter-car articulation and trainline assembly", children=parts)
    return c


def door_system_pair(x_offset: float = 0.0) -> Compound:
    """Door cassette pair, sill gap filler, lock, and external release."""

    parts: list[Part] = []
    for y_sign in (-1.0, 1.0):
        y = y_sign * 1365.0
        frame_z = DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM / 2.0
        parts.append(
            _box(
                DOOR_WIDTH_MM + 260.0,
                80.0,
                DOOR_HEIGHT_MM + 260.0,
                (x_offset, y, frame_z),
                "COTS electric door cassette",
                COLOR_DOOR,
            )
        )
        parts.append(
            _box(
                DOOR_WIDTH_MM + 480.0,
                130.0,
                90.0,
                (x_offset, y_sign * 1390.0, DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM + 105.0),
                "Door top roller track and operator rail",
                COLOR_METAL,
            )
        )
        parts.append(
            _cyl(
                90.0,
                220.0,
                (
                    x_offset - DOOR_WIDTH_MM / 2.0 - 250.0,
                    y_sign * 1390.0,
                    DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM + 120.0,
                ),
                "COTS electric door motor gearbox",
                COLOR_ELECTRONICS,
            )
        )
        parts.append(
            _box(
                260.0,
                58.0,
                170.0,
                (x_offset - DOOR_WIDTH_MM / 2.0 - 540.0, y_sign * 1410.0, DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM + 25.0),
                "IFE/Knorr-Bremse door controller and diagnostics module",
                COLOR_ELECTRONICS,
            )
        )
        parts.append(
            _box(
                640.0,
                36.0,
                82.0,
                (x_offset + 330.0, y_sign * 1435.0, DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM + 5.0),
                "Sliding-plug door harness cable chain",
                COLOR_HV,
            )
        )
        leaf_w = (DOOR_WIDTH_MM - 30.0) / 2.0
        for leaf_sign in (-1.0, 1.0):
            leaf_x = x_offset + leaf_sign * (leaf_w / 2.0 + 12.0)
            parts.append(
                _box(
                    leaf_w,
                    55.0,
                    DOOR_HEIGHT_MM - 60.0,
                    (leaf_x, y_sign * 1420.0, DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM / 2.0),
                    "Powered sliding door leaf",
                    COLOR_DOOR,
                )
            )
            parts.append(
                _box(
                    leaf_w - 180.0,
                    18.0,
                    1180.0,
                    (leaf_x, y_sign * 1458.0, DOOR_SILL_HEIGHT_MM + 1120.0),
                    "Door glazing panel",
                    COLOR_GLASS,
                )
            )
            parts.append(
                _box(
                    34.0,
                    42.0,
                    DOOR_HEIGHT_MM - 180.0,
                    (
                        leaf_x - leaf_sign * (leaf_w / 2.0 - 28.0),
                        y_sign * 1478.0,
                        DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM / 2.0,
                    ),
                    "Door leaf anti-pinch pressure edge",
                    COLOR_RUBBER,
                )
            )
            for roller_x in (leaf_x - leaf_w / 3.0, leaf_x + leaf_w / 3.0):
                parts.append(
                    _cyl(
                        34.0,
                        28.0,
                        (roller_x, y_sign * 1435.0, DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM + 45.0),
                        "Door hanger roller",
                        COLOR_METAL,
                    )
                )
        parts.append(
            _box(
                DOOR_WIDTH_MM + 180.0,
                90.0,
                70.0,
                (x_offset, y_sign * 1440.0, DOOR_SILL_HEIGHT_MM - 40.0),
                "Door sill gap-filler flap",
                COLOR_ACCESS,
            )
        )
        for side_x, label in (
            (-DOOR_WIDTH_MM / 2.0 - 80.0, "Door obstruction light-curtain transmitter"),
            (DOOR_WIDTH_MM / 2.0 + 80.0, "Door obstruction light-curtain receiver"),
        ):
            parts.append(
                _box(
                    42.0,
                    28.0,
                    1560.0,
                    (x_offset + side_x, y_sign * 1485.0, DOOR_SILL_HEIGHT_MM + 900.0),
                    label,
                    COLOR_SENSOR,
                )
            )
        for drain_x in (-480.0, 0.0, 480.0):
            parts.append(
                _box(
                    90.0,
                    24.0,
                    26.0,
                    (x_offset + drain_x, y_sign * 1488.0, DOOR_SILL_HEIGHT_MM - 82.0),
                    "Door threshold drain scupper",
                    COLOR_METAL,
                )
            )
        for x in (-520.0, 0.0, 520.0):
            parts.append(
                _cyl(
                    18.0,
                    75.0,
                    (x_offset + x, y_sign * 1445.0, DOOR_SILL_HEIGHT_MM - 8.0),
                    "Gap-filler hinge knuckle",
                    COLOR_METAL,
                )
            )
        parts.append(
            _box(
                180.0,
                80.0,
                260.0,
                (x_offset + DOOR_WIDTH_MM / 2.0 + 120.0, y_sign * 1425.0, 1250.0),
                "Door lock and external emergency release",
                COLOR_CRASH,
            )
        )
        parts.append(
            _box(
                42.0,
                35.0,
                380.0,
                (x_offset + DOOR_WIDTH_MM / 2.0 + 255.0, y_sign * 1465.0, 1260.0),
                "External emergency release pull handle",
                COLOR_CRASH,
            )
        )
    return Compound(label="Door cassette and platform-gap assembly", children=parts)


def door_systems_for_car(dims: CarDimensions = CarDimensions()) -> Compound:
    """All door pairs for one car, aligned to the car-body cutouts."""

    return Compound(
        label="All door cassette and platform-gap assemblies for car",
        children=[door_system_pair(x) for x in _door_centres_x(dims)],
    )


def platform_safety_interface(dims: CarDimensions = CarDimensions()) -> Compound:
    """Platform-edge, PSD, ATO stopping, and door-interlock reservations."""

    parts: list[Part] = []
    for x in _door_centres_x(dims):
        for y_sign in (-1.0, 1.0):
            platform_y = y_sign * (dims.body_width_mm / 2.0 + 105.0)
            parts.append(
                _box(
                    DOOR_WIDTH_MM + 520.0,
                    35.0,
                    2200.0,
                    (x, platform_y, 1450.0),
                    "Platform screen-door alignment datum",
                    Color(0.92, 0.72, 0.18, 0.32),
                )
            )
            parts.append(
                _box(
                    760.0,
                    42.0,
                    70.0,
                    (x, platform_y, DOOR_SILL_HEIGHT_MM + 65.0),
                    "ATO stopping accuracy target envelope",
                    COLOR_SENSOR,
                )
            )
            parts.append(
                _box(
                    280.0,
                    55.0,
                    190.0,
                    (x + DOOR_WIDTH_MM / 2.0 + 290.0, platform_y, 1320.0),
                    "Door/platform safety interlock interface",
                    COLOR_ELECTRONICS,
                )
            )
            parts.append(
                _box(
                    DOOR_WIDTH_MM + 900.0,
                    28.0,
                    125.0,
                    (x, platform_y, 820.0),
                    "Platform intrusion sensor sightline reservation",
                    COLOR_SENSOR,
                )
            )
    return Compound(label="Platform door and automation safety interface", children=parts)


def battery_pack_set(dims: CarDimensions = CarDimensions()) -> Compound:
    """Eight under-seat battery module envelopes for one car."""

    parts: list[Part] = []
    x_offsets = (-6100.0, -4200.0, 4200.0, 6100.0)
    z = BATTERY_STRAKE_BASE_Z_MM + BATTERY_STRAKE_HEIGHT_MM / 2.0
    for side in (-1.0, 1.0):
        y = side * (dims.body_width_mm / 2.0 - BATTERY_STRAKE_WIDTH_MM / 2.0 - 40.0)
        for x in x_offsets:
            parts.append(
                _box(
                    BATTERY_MODULE_LENGTH_MM + 90.0,
                    BATTERY_MODULE_WIDTH_MM + 60.0,
                    70.0,
                    (x, y, BATTERY_STRAKE_BASE_Z_MM + 35.0),
                    "Folded battery tray with drain lip",
                    COLOR_METAL,
                )
            )
            parts.append(
                _box(
                    BATTERY_MODULE_LENGTH_MM,
                    BATTERY_MODULE_WIDTH_MM,
                    BATTERY_MODULE_HEIGHT_MM,
                    (x, y, z + 25.0),
                    "Na-ion battery module envelope",
                    COLOR_BATTERY,
                )
            )
            for cell_x in (-460.0, -230.0, 0.0, 230.0, 460.0):
                parts.append(
                    _box(
                        165.0,
                        BATTERY_MODULE_WIDTH_MM - 130.0,
                        54.0,
                        (x + cell_x, y, z + 28.0),
                        "Rail traction battery cell-module drawer",
                        Color(0.12, 0.22, 0.36),
                    )
                )
            parts.extend(
                [
                    _box(
                        BATTERY_MODULE_LENGTH_MM - 120.0,
                        BATTERY_MODULE_WIDTH_MM - 120.0,
                        22.0,
                        (x, y, z - BATTERY_MODULE_HEIGHT_MM / 2.0 + 48.0),
                        "Battery liquid cold plate",
                        Color(0.12, 0.45, 0.62),
                    ),
                    _box(
                        36.0,
                        BATTERY_MODULE_WIDTH_MM - 90.0,
                        BATTERY_MODULE_HEIGHT_MM - 86.0,
                        (x + 650.0, y, z + 12.0),
                        "Battery thermal-runaway barrier plate",
                        COLOR_CRASH,
                    ),
                    _box(
                        BATTERY_MODULE_LENGTH_MM - 220.0,
                        22.0,
                        34.0,
                        (x, y - side * (BATTERY_MODULE_WIDTH_MM / 2.0 - 52.0), z + 185.0),
                        "BMS sense-harness spine",
                        COLOR_HV,
                    ),
                ]
            )
            parts.append(
                _box(
                    BATTERY_MODULE_LENGTH_MM - 180.0,
                    BATTERY_MODULE_WIDTH_MM - 80.0,
                    28.0,
                    (x, y, z + BATTERY_MODULE_HEIGHT_MM / 2.0 + 55.0),
                    "Battery service lid with gasket land",
                    COLOR_METAL,
                )
            )
            for lug_x in (-520.0, 520.0):
                parts.append(
                    _box(
                        70.0,
                        20.0,
                        55.0,
                        (x + lug_x, y + side * (BATTERY_MODULE_WIDTH_MM / 2.0 + 20.0), z + 150.0),
                        "Battery module lifting lug",
                        COLOR_METAL,
                    )
                )
            parts.append(
                _box(
                    130.0,
                    95.0,
                    120.0,
                    (x - 610.0, y - side * 145.0, z + 70.0),
                    "Battery vent and pressure-relief port",
                    COLOR_CRASH,
                )
            )
            parts.append(
                _box(
                    BATTERY_MODULE_LENGTH_MM - 300.0,
                    18.0,
                    22.0,
                    (x, y + side * (BATTERY_MODULE_WIDTH_MM / 2.0 - 46.0), z + 212.0),
                    "Aspirating fire-detection capillary",
                    COLOR_ACCESS,
                )
            )
    for side in (-1.0, 1.0):
        y = side * (dims.body_width_mm / 2.0 - BATTERY_STRAKE_WIDTH_MM - 10.0)
        for x in (-5150.0, 5150.0):
            parts.append(
                _box(
                    1650.0,
                    22.0,
                    34.0,
                    (x, y, z + 210.0),
                    "Insulated battery string busbar",
                    COLOR_HV,
                )
            )
    hv_box = _part(
        Box(900.0, 520.0, 460.0).locate(Location((0.0, 0.0, 620.0))),
        "HV contactor, fuse, and BMS cabinet",
        COLOR_HV,
    )
    parts.append(hv_box)
    parts.append(
        _box(
            780.0,
            430.0,
            24.0,
            (0.0, 0.0, 862.0),
            "BMS cabinet bolted access lid",
            COLOR_METAL,
        )
    )
    for x in (-260.0, -90.0, 90.0, 260.0):
        parts.append(
            _cyl(28.0, 42.0, (x, -285.0, 640.0), "HV battery cable gland", COLOR_RUBBER)
        )
    return Compound(label="Under-seat battery pack assembly", children=parts)


def traction_power_rack() -> Compound:
    """Inverter, auxiliary converter, coolant, and charge-interface envelopes."""

    parts: list[Part] = []
    inverter = _part(
        Box(900.0, 600.0, 420.0).locate(Location((-1850.0, 0.0, -360.0))),
        "SiC traction inverter and cold plate",
        COLOR_HV,
    )
    parts.append(inverter)
    for i in range(11):
        parts.append(
            _box(
                820.0,
                18.0,
                120.0,
                (-1850.0, -250.0 + i * 50.0, -80.0),
                "Traction inverter cooling fin",
                Color(0.18, 0.18, 0.20),
            )
        )
    aux = _part(
        Box(820.0, 520.0, 380.0).locate(Location((1850.0, 0.0, -340.0))),
        "Aux inverter 400 V / 110 V / 24 V",
        COLOR_ELECTRONICS,
    )
    parts.append(aux)
    parts.append(
        _box(
            680.0,
            60.0,
            70.0,
            (1850.0, -315.0, -130.0),
            "Aux converter terminal strip",
            COLOR_METAL,
        )
    )
    coolant = _part(
        Box(780.0, 360.0, 320.0).locate(Location((0.0, 0.0, -370.0))),
        "Coolant pump and manifold",
        Color(0.12, 0.45, 0.62),
    )
    parts.append(coolant)
    parts.append(
        _cyl(
            95.0,
            250.0,
            (-245.0, 0.0, -130.0),
            "Electric coolant pump body",
            Color(0.12, 0.45, 0.62),
        )
    )
    for x in (-260.0, -90.0, 90.0, 260.0):
        parts.append(_cyl(32.0, 70.0, (x, -220.0, -245.0), "Coolant hose port", COLOR_RUBBER))
    charge = _part(
        Box(420.0, 220.0, 360.0).locate(Location((0.0, -1500.0, 760.0))),
        "Station side-pin charging connector",
        COLOR_HV,
    )
    parts.append(charge)
    for x in (-120.0, 0.0, 120.0):
        parts.append(_cyl(24.0, 90.0, (x, -1630.0, 810.0), "Spring-loaded charging contact pin", COLOR_METAL))
    for x in (-150.0, 150.0):
        parts.append(
            _cyl(
                26.0,
                75.0,
                (x, -1500.0, 590.0),
                "Charging connector ceramic standoff",
                Color(0.92, 0.88, 0.72),
            )
        )
    return Compound(
        label="Traction power and charging assembly",
        children=parts,
    )


def electronics_cabinet(end_sign: float = 1.0) -> Compound:
    """Per-end T-ECU/S, T-ECU/A, event-recorder, and power cabinet."""

    safety = _part(
        Box(520.0, 220.0, 720.0).locate(Location((end_sign * 160.0, -760.0, 1500.0))),
        "T-ECU/S safety cabinet",
        COLOR_ELECTRONICS,
    )
    app = _part(
        Box(520.0, 220.0, 720.0).locate(Location((end_sign * 160.0, -500.0, 1500.0))),
        "T-ECU/A application cabinet",
        COLOR_ELECTRONICS,
    )
    recorder = _part(
        Box(420.0, 260.0, 360.0).locate(Location((end_sign * 160.0, -220.0, 1340.0))),
        "Crashworthy event recorder",
        COLOR_CRASH,
    )
    parts = [safety, app, recorder]
    for y in (-885.0, -630.0, -500.0, -350.0):
        for z in (1280.0, 1510.0, 1740.0):
            parts.append(_box(420.0, 24.0, 18.0, (end_sign * 160.0, y, z), "DIN rail", COLOR_METAL))
    for y in (-885.0, -630.0, -500.0):
        for z in (1395.0, 1625.0):
            for i in (-1, 0, 1):
                parts.append(
                    _box(
                        160.0,
                        14.0,
                        100.0,
                        (end_sign * (10.0 + i * 95.0), y, z),
                        "Eurocard PCB on DIN carrier",
                        Color(0.05, 0.34, 0.12),
                    )
                )
    for x in (-140.0, -70.0, 0.0, 70.0, 140.0):
        parts.append(_cyl(18.0, 32.0, (end_sign * x, -105.0, 1260.0), "M12 cable gland", COLOR_RUBBER))
    for i in range(9):
        parts.append(
            _box(
                34.0,
                42.0,
                48.0,
                (end_sign * (-180.0 + i * 45.0), -85.0, 1480.0),
                "Wago terminal block",
                COLOR_ACCESS,
            )
        )
    for y in (-760.0, -500.0):
        parts.append(_cyl(16.0, 20.0, (end_sign * 435.0, y, 1680.0), "Quarter-turn cabinet latch", COLOR_METAL))
    return Compound(label="Per-end electronics cabinet assembly", children=parts)


def tobs_sensor_pack(end_sign: float = 1.0) -> Compound:
    """Obstacle-detection sensor pack behind one sensor cowl."""

    parts: list[Part] = [
        _box(
            80.0,
            1280.0,
            1380.0,
            (end_sign * 185.0, 0.0, 2030.0),
            "T-OBS adjustable sensor backplate",
            COLOR_METAL,
        ),
        _box(
            RAIL_LIDAR_LENGTH_MM,
            RAIL_LIDAR_WIDTH_MM,
            RAIL_LIDAR_HEIGHT_MM,
            (end_sign * 300.0, 0.0, 2550.0),
            "Rail-grade LIDAR envelope (Ouster OS1 / LSLiDAR class)",
            COLOR_SENSOR,
        ),
        _box(
            205.0,
            28.0,
            122.0,
            (end_sign * 380.0, 0.0, 2550.0),
            "Heated LIDAR optical window",
            COLOR_GLASS,
        ),
        _box(
            220.0,
            180.0,
            70.0,
            (end_sign * 300.0, 0.0, 2200.0),
            "T-OBS mmWave radar envelope",
            COLOR_SENSOR,
        ),
        _box(
            260.0,
            26.0,
            95.0,
            (end_sign * 410.0, 0.0, 2200.0),
            "Radar radome window",
            Color(0.20, 0.22, 0.24, 0.60),
        ),
        _box(
            620.0,
            70.0,
            90.0,
            (end_sign * 320.0, 0.0, 1850.0),
            "T-OBS stereo camera pair envelope",
            COLOR_SENSOR,
        ),
        _box(
            280.0,
            58.0,
            125.0,
            (end_sign * 330.0, -430.0, 2360.0),
            "Rail Vision class thermal camera pod",
            COLOR_SENSOR,
        ),
        _box(
            280.0,
            24.0,
            125.0,
            (end_sign * 415.0, -430.0, 2360.0),
            "Thermal camera germanium window heater",
            Color(0.16, 0.18, 0.20, 0.62),
        ),
        _box(
            430.0,
            78.0,
            92.0,
            (end_sign * 326.0, 430.0, 2360.0),
            "Narrow/wide field camera pair pod",
            COLOR_SENSOR,
        ),
        _box(
            480.0,
            36.0,
            70.0,
            (end_sign * 415.0, 430.0, 2360.0),
            "Camera wash/wipe manifold",
            COLOR_HVAC,
        ),
    ]
    for y in (-250.0, 250.0):
        parts.append(
            _cyl(
                38.0,
                35.0,
                (end_sign * 380.0, y, 1850.0),
                "Stereo camera lens and heater ring",
                COLOR_GLASS,
            )
        )
    for y in (-520.0, 520.0):
        for z in (1500.0, 2500.0):
            parts.append(
                _cyl(
                    55.0,
                    60.0,
                    (end_sign * 520.0, y, z),
                    "T-OBS ultrasonic transducer",
                    COLOR_SENSOR,
                )
            )
            parts.append(
                _cyl(
                    72.0,
                    12.0,
                    (end_sign * 555.0, y, z),
                    "Ultrasonic transducer retaining ring",
                    COLOR_METAL,
                )
            )
    for y in (-620.0, 620.0):
        for z in (1360.0, 2660.0):
            parts.append(_cyl(18.0, 14.0, (end_sign * 585.0, y, z), "Sensor cover captive screw", COLOR_METAL))
    return Compound(
        label="T-OBS nose sensor pack assembly",
        children=parts,
    )


def accessibility_and_safety_kit(dims: CarDimensions = CarDimensions()) -> Compound:
    """PRM fixtures, emergency lighting, signage, and call buttons for one car."""

    parts: list[Part] = []
    for x in (-2200.0, 2200.0):
        bay = _part(
            Box(1300.0, 760.0, 30.0).locate(Location((x, 0.0, 25.0))),
            "Wheelchair bay floor reservation",
            COLOR_ACCESS,
        )
        call = _part(
            Box(160.0, 40.0, 220.0).locate(Location((x, dims.body_width_mm / 2.0 - 80.0, 1150.0))),
            "Passenger emergency call point",
            COLOR_CRASH,
        )
        parts.extend([bay, call])
    for x in (-5000.0, 0.0, 5000.0):
        light = _part(
            Box(900.0, 80.0, 60.0).locate(Location((x, 0.0, 3300.0))),
            "Emergency lighting and exit marker",
            COLOR_ACCESS,
        )
        parts.append(light)
    return Compound(label="Accessibility and safety kit", children=parts)


def car_systems(dims: CarDimensions = CarDimensions()) -> Compound:
    """All equipment envelopes mounted to one self-contained car."""

    parts: list[Part | Compound] = [
        door_systems_for_car(dims),
        platform_safety_interface(dims),
        battery_pack_set(dims),
        traction_power_rack(),
        accessibility_and_safety_kit(dims),
    ]
    c = Compound(label="Complete car systems assembly", children=parts)
    return c


def trainset_systems(layout: TrainsetSystemLayout) -> Compound:
    """All non-structural train-level systems placed on the consist."""

    parts: list[Part | Compound] = []
    half = layout.total_length_mm / 2.0
    coupler_minus = end_coupler(-1.0).translate((-half - 50.0, 0.0, 0.0))
    coupler_minus.label = "A-end coupler and crash-energy assembly"
    coupler_plus = end_coupler(1.0).translate((half + 50.0, 0.0, 0.0))
    coupler_plus.label = "B-end coupler and crash-energy assembly"
    parts.extend([coupler_minus, coupler_plus])

    electronics_minus = electronics_cabinet(-1.0).translate(
        (-half + COWL_LENGTH_MM + 900.0, 0.0, 0.0)
    )
    electronics_minus.label = "A-end electronics cabinet assembly"
    electronics_plus = electronics_cabinet(1.0).translate(
        (half - COWL_LENGTH_MM - 900.0, 0.0, 0.0)
    )
    electronics_plus.label = "B-end electronics cabinet assembly"
    parts.extend([electronics_minus, electronics_plus])

    for centre_x in layout.car_centres_x:
        systems = car_systems(layout.dims).translate((centre_x, 0.0, 0.0))
        systems.label = "Car systems assembly"
        parts.append(systems)

    for left, right in zip(layout.car_centres_x, layout.car_centres_x[1:]):
        articulation_x = (left + right) / 2.0
        articulation = inter_car_articulation().translate((articulation_x, 0.0, 0.0))
        articulation.label = "Inter-car articulation assembly"
        parts.append(articulation)

    tobs_minus = tobs_sensor_pack(-1.0).translate((-half, 0.0, 0.0))
    tobs_minus.label = "A-end T-OBS sensor pack"
    tobs_plus = tobs_sensor_pack(1.0).translate((half, 0.0, 0.0))
    tobs_plus.label = "B-end T-OBS sensor pack"
    parts.extend([tobs_minus, tobs_plus])

    return Compound(label="Complete train systems assembly", children=parts)


__all__ = [
    "BATTERY_MODULES_PER_CAR",
    "accessibility_and_safety_kit",
    "battery_pack_set",
    "car_systems",
    "door_system_pair",
    "door_systems_for_car",
    "electronics_cabinet",
    "end_coupler",
    "inter_car_articulation",
    "platform_safety_interface",
    "system_layout",
    "tobs_sensor_pack",
    "traction_power_rack",
    "trainset_systems",
]
