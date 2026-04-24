"""Full trainset assembly — N cabless cars coupled end-to-end.

Each consist family from RFC 0008 §1 has a characteristic car count
and dimensions:

- `tram-2car`         : 2 cars × 15 m body.
- `light-metro-3car`  : 3 cars × 22 m body.
- `metro-4car`        : 4 cars × 22 m body.
- `metro-6car`        : 6 cars × 22 m body.

The trainset assembly places one sensor cowl at each end (RFC 0015
makes the trainset symmetric), N car bodies coupled by 1 m gaps, and
2 bogies per car. A `metro-6car` trainset at 22 m per car is
22 × 6 + 1 × 7 + 1.8 × 2 = 143.6 m — consistent with the 150 m
platform length RFC 0008 publishes for that family (accounting for
150 mm of stopping tolerance each end).
"""

from __future__ import annotations

from build123d import Axis, Compound, Part

from ..common import ConsistFamily, consist_platform_length_m
from .bogie import WHEELBASE_MM, motor_bogie, trailer_bogie
from .car_body import CarDimensions, car_body
from .sensor_cowl import COWL_LENGTH_MM, sensor_cowl


# Car body length per family (RFC 0008 §3.1).
_FAMILY_CAR_LENGTH_MM: dict[ConsistFamily, float] = {
    ConsistFamily.TRAM_2CAR: 15_000.0,
    ConsistFamily.LIGHT_METRO_3CAR: 22_000.0,
    ConsistFamily.METRO_4CAR: 22_000.0,
    ConsistFamily.METRO_6CAR: 22_000.0,
}
_FAMILY_CAR_COUNT: dict[ConsistFamily, int] = {
    ConsistFamily.TRAM_2CAR: 2,
    ConsistFamily.LIGHT_METRO_3CAR: 3,
    ConsistFamily.METRO_4CAR: 4,
    ConsistFamily.METRO_6CAR: 6,
}
COUPLING_GAP_MM = 1000.0


# Motorisation pattern per family (RFC 0022 §8).
# True = motor bogie on that car; False = trailer bogie.
_FAMILY_MOTORISED_CARS: dict[ConsistFamily, tuple[bool, ...]] = {
    ConsistFamily.TRAM_2CAR: (True, True),
    ConsistFamily.LIGHT_METRO_3CAR: (True, False, True),
    ConsistFamily.METRO_4CAR: (True, True, False, True),
    ConsistFamily.METRO_6CAR: (True, True, False, False, True, True),
}


def family_dimensions(family: ConsistFamily) -> CarDimensions:
    """Default `CarDimensions` for each consist family."""
    return CarDimensions(
        body_length_mm=_FAMILY_CAR_LENGTH_MM[family],
        doors_per_side=3 if family != ConsistFamily.TRAM_2CAR else 2,
    )


def family_motorisation(family: ConsistFamily) -> tuple[bool, ...]:
    """Return the per-car motorisation pattern (True = motor car,
    False = trailer car) for a given consist family per RFC 0022 §8."""
    return _FAMILY_MOTORISED_CARS[family]


def trainset(family: ConsistFamily = ConsistFamily.LIGHT_METRO_3CAR) -> Compound:
    """Full consist assembly — cowls + cars + bogies.

    Origin: midpoint of the trainset centreline, rail-head level.
    +X runs along the trainset in the "A-end" direction; the sensor
    cowl at the +X end is structurally identical to the one at -X.
    """

    dims = family_dimensions(family)
    car_count = _FAMILY_CAR_COUNT[family]

    parts: list[Part | Compound] = []

    # Stack cars along X, centred on X=0.
    total_length_mm = (
        2 * COWL_LENGTH_MM
        + car_count * dims.body_length_mm
        + (car_count - 1) * COUPLING_GAP_MM
    )
    x_cursor = -total_length_mm / 2.0

    # Leading-end cowl at -X (rotated 180° so its leading face points -X).
    cowl_minus = sensor_cowl(
        car_width_mm=dims.body_width_mm,
        car_height_mm=dims.body_height_mm,
    )
    cowl_minus = cowl_minus.rotate(Axis.Z, 180)
    # After rotation, cowl origin (the "at car interface" face) sits at
    # -COWL_LENGTH_MM; we want it at x_cursor + COWL_LENGTH_MM so the
    # interface aligns with the first car.
    cowl_minus = cowl_minus.translate((x_cursor + COWL_LENGTH_MM, 0.0, 0.0))
    parts.append(cowl_minus)
    x_cursor += COWL_LENGTH_MM

    # Car bodies + bogies per RFC 0022 motorisation pattern.
    motorised = _FAMILY_MOTORISED_CARS[family]
    for i in range(car_count):
        body = car_body(dims)
        car_centre_x = x_cursor + dims.body_length_mm / 2.0
        body = body.translate((car_centre_x, 0.0, 0.0))
        parts.append(body)

        # Two bogies per car — motor or trailer variant depending
        # on the family's motorisation pattern.
        bogie_builder = motor_bogie if motorised[i] else trailer_bogie
        for sign in (-1, 1):
            bog = bogie_builder()
            bog = bog.translate((car_centre_x + sign * (dims.body_length_mm / 2.0 - WHEELBASE_MM), 0.0, 0.0))
            parts.append(bog)

        x_cursor += dims.body_length_mm
        if i + 1 < car_count:
            x_cursor += COUPLING_GAP_MM

    # Trailing-end cowl at +X.
    cowl_plus = sensor_cowl(
        car_width_mm=dims.body_width_mm,
        car_height_mm=dims.body_height_mm,
    )
    cowl_plus = cowl_plus.translate((x_cursor, 0.0, 0.0))
    parts.append(cowl_plus)

    return Compound(
        label=f"Trainset ({family.value}, {car_count} cars, cabless)",
        children=parts,
    )


def trainset_length_m(family: ConsistFamily) -> float:
    """Total overall length of a trainset (cowl-to-cowl) in metres.

    Used by tests to validate the published platform length from RFC 0008
    §1 with a 150 mm stopping-tolerance allowance per end.
    """
    dims = family_dimensions(family)
    n = _FAMILY_CAR_COUNT[family]
    mm = (
        2 * COWL_LENGTH_MM
        + n * dims.body_length_mm
        + (n - 1) * COUPLING_GAP_MM
    )
    return mm / 1000.0


def expected_platform_length_m(family: ConsistFamily) -> float:
    """RFC 0008 published platform length (which trainset length must
    fit inside with stopping tolerance)."""
    return consist_platform_length_m(family)


__all__ = [
    "COUPLING_GAP_MM",
    "expected_platform_length_m",
    "family_dimensions",
    "family_motorisation",
    "trainset",
    "trainset_length_m",
]
