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
COLOR_ELECTRONICS = Color(0.18, 0.35, 0.25)
COLOR_SENSOR = Color(0.05, 0.08, 0.10)
COLOR_ACCESS = Color(0.95, 0.80, 0.10)

COUPLER_FACE_HEIGHT_MM = 720.0
BATTERY_MODULES_PER_CAR = 8
BATTERY_MODULE_LENGTH_MM = 1450.0
BATTERY_MODULE_WIDTH_MM = BATTERY_STRAKE_WIDTH_MM - 70.0
BATTERY_MODULE_HEIGHT_MM = BATTERY_STRAKE_HEIGHT_MM - 80.0


@dataclass(frozen=True)
class TrainsetSystemLayout:
    """System placement context for one trainset."""

    car_centres_x: tuple[float, ...]
    total_length_mm: float
    dims: CarDimensions


def system_layout(dims: CarDimensions, car_count: int) -> TrainsetSystemLayout:
    """Return X placement anchors matching `trainset.trainset`."""

    total_length_mm = (
        2 * COWL_LENGTH_MM
        + car_count * dims.body_length_mm
        + (car_count - 1) * 1000.0
    )
    x_cursor = -total_length_mm / 2.0 + COWL_LENGTH_MM
    centres = []
    for index in range(car_count):
        centres.append(x_cursor + dims.body_length_mm / 2.0)
        x_cursor += dims.body_length_mm
        if index + 1 < car_count:
            x_cursor += 1000.0
    return TrainsetSystemLayout(
        car_centres_x=tuple(centres),
        total_length_mm=total_length_mm,
        dims=dims,
    )


def _part(part: Part, label: str, color: Color) -> Part:
    part.label = label
    part.color = color
    return part


def end_coupler(end_sign: float = 1.0) -> Compound:
    """Scharfenberg Type 10 end coupler + crash absorber envelope."""

    head = _part(
        Box(360.0, 520.0, 360.0).locate(Location((end_sign * 180.0, 0.0, COUPLER_FACE_HEIGHT_MM))),
        "Scharfenberg Type 10 coupler head",
        COLOR_COUPLER,
    )
    shank = _part(
        Box(620.0, 260.0, 220.0).locate(Location((-end_sign * 200.0, 0.0, COUPLER_FACE_HEIGHT_MM))),
        "Coupler shank and electric-head carrier",
        COLOR_COUPLER,
    )
    crash = _part(
        Box(780.0, 760.0, 420.0).locate(Location((-end_sign * 720.0, 0.0, COUPLER_FACE_HEIGHT_MM))),
        "EN 15227 crash absorber cartridge",
        COLOR_CRASH,
    )
    c = Compound(label="End coupler and crash-energy assembly", children=[head, shank, crash])
    return c


def inter_car_articulation() -> Compound:
    """Semi-permanent inter-car connection with drag-chain trainline."""

    bellows = _part(
        Box(850.0, 2350.0, 2850.0).locate(Location((0.0, 0.0, 1850.0))),
        "Inter-car articulation bellows envelope",
        Color(0.18, 0.18, 0.20),
    )
    drawbar = _part(
        Box(900.0, 360.0, 220.0).locate(Location((0.0, 0.0, COUPLER_FACE_HEIGHT_MM))),
        "Semi-permanent drawbar",
        COLOR_COUPLER,
    )
    trainline = _part(
        Box(900.0, 120.0, 180.0).locate(Location((0.0, 900.0, 1250.0))),
        "TCN-E / CAN-FD / auxiliary drag-chain",
        COLOR_HV,
    )
    c = Compound(label="Inter-car articulation and trainline assembly", children=[bellows, drawbar, trainline])
    return c


def door_system_pair() -> Compound:
    """Door cassette pair, sill gap filler, lock, and external release."""

    parts: list[Part] = []
    for y_sign in (-1.0, 1.0):
        y = y_sign * 1365.0
        cassette = _part(
            Box(DOOR_WIDTH_MM + 260.0, 180.0, DOOR_HEIGHT_MM + 260.0).locate(
                Location((0.0, y, DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM / 2.0))
            ),
            "COTS electric door cassette",
            COLOR_DOOR,
        )
        gap_filler = _part(
            Box(DOOR_WIDTH_MM + 180.0, 90.0, 70.0).locate(
                Location((0.0, y_sign * 1440.0, DOOR_SILL_HEIGHT_MM - 40.0))
            ),
            "Door sill gap-filler flap",
            COLOR_ACCESS,
        )
        lock = _part(
            Box(180.0, 80.0, 260.0).locate(
                Location((DOOR_WIDTH_MM / 2.0 + 120.0, y_sign * 1425.0, 1250.0))
            ),
            "Door lock and external emergency release",
            COLOR_CRASH,
        )
        parts.extend([cassette, gap_filler, lock])
    return Compound(label="Door cassette and platform-gap assembly", children=parts)


def battery_pack_set(dims: CarDimensions = CarDimensions()) -> Compound:
    """Eight under-seat battery module envelopes for one car."""

    parts: list[Part] = []
    x_offsets = (-6100.0, -4200.0, 4200.0, 6100.0)
    z = BATTERY_STRAKE_BASE_Z_MM + BATTERY_STRAKE_HEIGHT_MM / 2.0
    for side in (-1.0, 1.0):
        y = side * (dims.body_width_mm / 2.0 - BATTERY_STRAKE_WIDTH_MM / 2.0 - 40.0)
        for x in x_offsets:
            module = _part(
                Box(
                    BATTERY_MODULE_LENGTH_MM,
                    BATTERY_MODULE_WIDTH_MM,
                    BATTERY_MODULE_HEIGHT_MM,
                ).locate(Location((x, y, z))),
                "Na-ion battery module envelope",
                COLOR_BATTERY,
            )
            parts.append(module)
    hv_box = _part(
        Box(900.0, 520.0, 460.0).locate(Location((0.0, 0.0, 620.0))),
        "HV contactor, fuse, and BMS cabinet",
        COLOR_HV,
    )
    parts.append(hv_box)
    return Compound(label="Under-seat battery pack assembly", children=parts)


def traction_power_rack() -> Compound:
    """Inverter, auxiliary converter, coolant, and charge-interface envelopes."""

    inverter = _part(
        Box(900.0, 600.0, 420.0).locate(Location((-1850.0, 0.0, -360.0))),
        "SiC traction inverter and cold plate",
        COLOR_HV,
    )
    aux = _part(
        Box(820.0, 520.0, 380.0).locate(Location((1850.0, 0.0, -340.0))),
        "Aux inverter 400 V / 110 V / 24 V",
        COLOR_ELECTRONICS,
    )
    coolant = _part(
        Box(780.0, 360.0, 320.0).locate(Location((0.0, 0.0, -370.0))),
        "Coolant pump and manifold",
        Color(0.12, 0.45, 0.62),
    )
    charge = _part(
        Box(420.0, 220.0, 360.0).locate(Location((0.0, -1500.0, 760.0))),
        "Station side-pin charging connector",
        COLOR_HV,
    )
    return Compound(
        label="Traction power and charging assembly",
        children=[inverter, aux, coolant, charge],
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
    return Compound(label="Per-end electronics cabinet assembly", children=[safety, app, recorder])


def tobs_sensor_pack(end_sign: float = 1.0) -> Compound:
    """Obstacle-detection sensor pack behind one sensor cowl."""

    lidar = _part(
        Box(420.0, 300.0, 180.0).locate(Location((end_sign * 260.0, 0.0, 2550.0))),
        "T-OBS solid-state LIDAR envelope",
        COLOR_SENSOR,
    )
    radar = _part(
        Box(320.0, 260.0, 160.0).locate(Location((end_sign * 300.0, 0.0, 2200.0))),
        "T-OBS mmWave radar envelope",
        COLOR_SENSOR,
    )
    stereo = _part(
        Box(640.0, 120.0, 120.0).locate(Location((end_sign * 320.0, 0.0, 1850.0))),
        "T-OBS stereo camera pair envelope",
        COLOR_SENSOR,
    )
    ultrasonics = []
    for y in (-520.0, 520.0):
        for z in (1500.0, 2500.0):
            ultrasonics.append(
                _part(
                    Cylinder(radius=55.0, height=60.0).locate(Location((end_sign * 520.0, y, z))),
                    "T-OBS ultrasonic transducer",
                    COLOR_SENSOR,
                )
            )
    return Compound(
        label="T-OBS nose sensor pack assembly",
        children=[lidar, radar, stereo, *ultrasonics],
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
        door_system_pair(),
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
    "electronics_cabinet",
    "end_coupler",
    "inter_car_articulation",
    "system_layout",
    "tobs_sensor_pack",
    "traction_power_rack",
    "trainset_systems",
]
