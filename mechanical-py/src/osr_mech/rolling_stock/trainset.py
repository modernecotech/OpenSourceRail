"""Full trainset assembly — N cabless cars coupled end-to-end.

Each consist family from RFC 0008 §1 has a characteristic car count
and dimensions:

- `urban-shuttle-1car`: 1 car × 17 m body.
- `tram-2car`         : 2 cars × 17 m body.
- `light-metro-3car`  : 3 cars × 17 m body.
- `metro-4car`        : 4 cars × 17 m body.
- `metro-6car`        : 6 cars × 17 m body.

The trainset assembly places one sensor cowl at each end (RFC 0015
makes the trainset symmetric), N car bodies joined by semi-permanent
articulation/gangway modules, and 2 bogies per car. Cowls and
articulation interfaces are overlays inside the repeated 17 m car
module envelope, so a `metro-6car` trainset at 17 m per car is
102.0 m — consistent with the 121 m platform length RFC 0008 publishes
for that family (accounting for stopping tolerance and door-control
clearance).
"""

from __future__ import annotations

from osr_mech.cad import Axis, Compound, Part

from ..common import ConsistFamily, consist_platform_length_m
from .bogie import WHEELBASE_MM, motor_bogie, trailer_bogie
from .car_body import CarDimensions, car_body
from .sensor_cowl import COWL_LENGTH_MM, sensor_cowl
from .systems import system_layout, trainset_systems


# Car body length per family (RFC 0008 §3.1).
_FAMILY_CAR_LENGTH_MM: dict[ConsistFamily, float] = {
    ConsistFamily.URBAN_SHUTTLE_1CAR: 17_000.0,
    ConsistFamily.TRAM_2CAR: 17_000.0,
    ConsistFamily.LIGHT_METRO_3CAR: 17_000.0,
    ConsistFamily.METRO_4CAR: 17_000.0,
    ConsistFamily.METRO_6CAR: 17_000.0,
}
_FAMILY_CAR_COUNT: dict[ConsistFamily, int] = {
    ConsistFamily.URBAN_SHUTTLE_1CAR: 1,
    ConsistFamily.TRAM_2CAR: 2,
    ConsistFamily.LIGHT_METRO_3CAR: 3,
    ConsistFamily.METRO_4CAR: 4,
    ConsistFamily.METRO_6CAR: 6,
}
COUPLING_GAP_MM = 0.0


# Motorisation pattern per family (RFC 0022 §8).
# True = the car carries one motor bogie and one trailer bogie.
# False = the car carries two trailer bogies. The light-metro concept
# uses powered end cars; every car keeps a low-floor centre with raised
# end decks over the standard bogies.
_FAMILY_MOTORISED_CARS: dict[ConsistFamily, tuple[bool, ...]] = {
    ConsistFamily.URBAN_SHUTTLE_1CAR: (True,),
    ConsistFamily.TRAM_2CAR: (True, True),
    ConsistFamily.LIGHT_METRO_3CAR: (True, False, True),
    ConsistFamily.METRO_4CAR: (True, True, True, True),
    ConsistFamily.METRO_6CAR: (True, True, True, True, True, True),
}


def family_dimensions(family: ConsistFamily) -> CarDimensions:
    """Default `CarDimensions` for each consist family."""
    return CarDimensions(
        body_length_mm=_FAMILY_CAR_LENGTH_MM[family],
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
    total_length_mm = car_count * dims.body_length_mm + (car_count - 1) * COUPLING_GAP_MM
    x_cursor = -total_length_mm / 2.0

    # Leading-end cowl at -X. The cowl is a nose overlay inside the
    # 17 m end-car envelope, so it does not add to consist length.
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

    # Car bodies + bogies per RFC 0022 motorisation pattern.
    motorised = _FAMILY_MOTORISED_CARS[family]
    for i in range(car_count):
        body = car_body(dims)
        car_centre_x = x_cursor + dims.body_length_mm / 2.0
        body = body.translate((car_centre_x, 0.0, 0.0))
        parts.append(body)

        # Two bogies per self-contained car: one powered, one trailer.
        # Coupled consists repeat the same module rather than changing the
        # motorisation pattern by train length.
        bogie_builders = (
            (motor_bogie, trailer_bogie) if motorised[i] else (trailer_bogie, trailer_bogie)
        )
        for sign, bogie_builder in zip((-1, 1), bogie_builders):
            bog = bogie_builder()
            bog = bog.translate((car_centre_x + sign * (dims.body_length_mm / 2.0 - WHEELBASE_MM), 0.0, 0.0))
            parts.append(bog)

        x_cursor += dims.body_length_mm
        if i + 1 < car_count:
            x_cursor += COUPLING_GAP_MM

    # Trailing-end cowl at +X, also inside the final car envelope.
    cowl_plus = sensor_cowl(
        car_width_mm=dims.body_width_mm,
        car_height_mm=dims.body_height_mm,
    )
    cowl_plus = cowl_plus.translate((x_cursor - COWL_LENGTH_MM, 0.0, 0.0))
    parts.append(cowl_plus)

    systems = trainset_systems(system_layout(dims, car_count))
    parts.append(systems)

    return Compound(
        label=f"Complete trainset ({family.value}, {car_count} cars, cabless)",
        children=parts,
    )


def trainset_length_m(family: ConsistFamily) -> float:
    """Total overall length of a trainset (cowl-to-cowl) in metres.

    Used by tests to validate the published platform length from RFC 0008
    §1 with a 150 mm stopping-tolerance allowance per end.
    """
    dims = family_dimensions(family)
    n = _FAMILY_CAR_COUNT[family]
    mm = n * dims.body_length_mm + (n - 1) * COUPLING_GAP_MM
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
