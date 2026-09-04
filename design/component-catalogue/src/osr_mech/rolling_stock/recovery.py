"""Planning load cases and source geometry for LM3 field rerailing.

This module deliberately separates portable rail-recovery equipment from the
depot lifting columns.  It sizes a supplier-neutral hydraulic kit against the
controlled train mass and shared J1--J4 vehicle datum.  The calculations are
coordination checks only: a competent recovery engineer must release every
vehicle condition, support arrangement, ground reaction and operating method.
"""

from __future__ import annotations

from dataclasses import dataclass

from osr_mech.cad import Box, Color, Compound, Cylinder, Location, Part
from osr_mech.maintenance_interface import lm3_field_recovery_datum

from .baseline import PROMOTED_LIGHT_METRO_TRAINSET_MASS_KG


STANDARD_GRAVITY_M_S2 = 9.80665
LM3_CAR_COUNT = 3

STEEL = Color(0.35, 0.39, 0.44)
ALUMINIUM = Color(0.69, 0.72, 0.75)
HYDRAULIC = Color(0.12, 0.35, 0.66)
SAFETY = Color(0.93, 0.50, 0.08)
TIMBER = Color(0.52, 0.32, 0.16)
CLEARANCE = Color(0.90, 0.24, 0.12, 0.14)


@dataclass(frozen=True)
class RecoveryMassScenario:
    """One controlled-tare sensitivity case."""

    id: str
    tare_reduction_fraction: float
    train_mass_kg: float

    @property
    def car_mass_kg(self) -> float:
        return self.train_mass_kg / LM3_CAR_COUNT

    @property
    def ideal_four_point_reaction_kn(self) -> float:
        return self.car_mass_kg * STANDARD_GRAVITY_M_S2 / 4.0 / 1_000.0


@dataclass(frozen=True)
class RecoveryLoadCase:
    """Preliminary maximum reaction model for a permitted lift arrangement."""

    id: str
    description: str
    supported_car_mass_fraction: float
    active_lift_points: int
    unequal_load_factor: float = 1.35
    action_factor: float = 1.50

    def maximum_point_reaction_kn(self, car_mass_kg: float) -> float:
        if car_mass_kg <= 0.0:
            raise ValueError("car mass must be positive")
        if not 0.0 < self.supported_car_mass_fraction <= 1.0:
            raise ValueError("supported car-mass fraction must be in (0, 1]")
        if self.active_lift_points < 2:
            raise ValueError("a permitted recovery lift needs at least two active points")
        if self.unequal_load_factor < 1.0 or self.action_factor < 1.0:
            raise ValueError("load and action factors must be at least 1.0")
        supported_weight_kn = (
            car_mass_kg
            * self.supported_car_mass_fraction
            * STANDARD_GRAVITY_M_S2
            / 1_000.0
        )
        return (
            supported_weight_kn
            / self.active_lift_points
            * self.unequal_load_factor
            * self.action_factor
        )


@dataclass(frozen=True)
class RecoveryCapacityCheck:
    """Comparison of a load case with the field-kit coordination capacity."""

    load_case: RecoveryLoadCase
    required_point_capacity_kn: float
    available_point_capacity_kn: float

    @property
    def margin_kn(self) -> float:
        return self.available_point_capacity_kn - self.required_point_capacity_kn

    @property
    def passes(self) -> bool:
        return self.margin_kn >= 0.0


def recovery_mass_scenarios(
    controlled_train_mass_kg: float = PROMOTED_LIGHT_METRO_TRAINSET_MASS_KG,
) -> tuple[RecoveryMassScenario, ...]:
    """Return the controlled case plus explicit 10% and 20% sensitivities."""

    if controlled_train_mass_kg <= 0.0:
        raise ValueError("controlled train mass must be positive")
    reductions = (
        ("controlled-planning-tare", 0.0),
        ("tare-minus-10-percent", 0.10),
        ("tare-minus-20-percent", 0.20),
    )
    return tuple(
        RecoveryMassScenario(
            id=scenario_id,
            tare_reduction_fraction=reduction,
            train_mass_kg=controlled_train_mass_kg * (1.0 - reduction),
        )
        for scenario_id, reduction in reductions
    )


def field_recovery_load_cases() -> tuple[RecoveryLoadCase, ...]:
    """Return permitted preliminary configurations for an upright vehicle.

    The one-end case places 60% of the car mass at the lifted end to cover a
    planning longitudinal centre-of-gravity envelope.  The 1.35 unequal-load
    and 1.50 action factors are conservative design-reference assumptions, not
    substitutes for the released structural and incident lift calculations.
    """

    return (
        RecoveryLoadCase(
            id="full-car-four-point",
            description="Complete car and retained running gear on J1--J4",
            supported_car_mass_fraction=1.0,
            active_lift_points=4,
        ),
        RecoveryLoadCase(
            id="one-end-two-point",
            description="One car end and retained bogie on its transverse jack pair",
            supported_car_mass_fraction=0.60,
            active_lift_points=2,
        ),
    )


def controlled_recovery_capacity_checks() -> tuple[RecoveryCapacityCheck, ...]:
    """Check controlled-tare cases against the portable cylinder envelope."""

    car_mass_kg = recovery_mass_scenarios()[0].car_mass_kg
    capacity_kn = lm3_field_recovery_datum().portable_cylinder_min_capacity_kn
    return tuple(
        RecoveryCapacityCheck(
            load_case=load_case,
            required_point_capacity_kn=load_case.maximum_point_reaction_kn(car_mass_kg),
            available_point_capacity_kn=capacity_kn,
        )
        for load_case in field_recovery_load_cases()
    )


def _part(shape: Part, label: str, colour: Color, at: tuple[float, float, float]) -> Part:
    shape.label = label
    shape.color = colour
    return shape.locate(Location(at))


def _box(
    size: tuple[float, float, float],
    label: str,
    colour: Color,
    at: tuple[float, float, float],
) -> Part:
    return _part(Box(*size), label, colour, at)


def portable_field_rerailing_kit() -> Compound:
    """Four-point portable hydraulic lift and lateral-traverse review model.

    The model reserves component and access envelopes; it is not an instruction
    to deploy all parts in every incident.  Automotive scissor jacks, unilateral
    side lifts and work beneath an uncribbed hydraulic load are excluded.
    """

    datum = lm3_field_recovery_datum()
    parts: list[Part] = []
    bridge_z = -260.0
    cylinder_z = bridge_z + 150.0

    for x, y in datum.jack_positions_mm:
        parts.extend(
            [
                _box(
                    (700.0, 700.0, 55.0),
                    "Wide-area cylinder baseplate and ground spreader",
                    STEEL,
                    (x, y, bridge_z - 55.0),
                ),
                _part(
                    Cylinder(105.0, datum.cylinder_closed_height_envelope_mm),
                    "Portable rail-rated 200 kN telescopic rerailing cylinder envelope",
                    HYDRAULIC,
                    (x, y, cylinder_z),
                ),
                _box(
                    (300.0, 300.0, 65.0),
                    "Tilting jack head and keyed LM3 pad adapter",
                    SAFETY,
                    (x, y, cylinder_z + datum.cylinder_closed_height_envelope_mm),
                ),
                _box(
                    (420.0, 520.0, 90.0),
                    "Locking lateral-traverse sled",
                    ALUMINIUM,
                    (x, y, bridge_z + 45.0),
                ),
            ]
        )

    half_x = datum.jack_longitudinal_spacing_mm / 2.0
    for x in (-half_x, half_x):
        parts.append(
            _box(
                (520.0, datum.transverse_rerailing_bridge_length_mm, 180.0),
                "Transverse aluminium rerailing bridge",
                ALUMINIUM,
                (x, 0.0, bridge_z),
            )
        )
        for y in (-1_650.0, 1_650.0):
            parts.append(
                _box(
                    (520.0, 420.0, 300.0),
                    "Mechanical cribbing and secondary retention pack",
                    TIMBER,
                    (x + 700.0, y, bridge_z - 30.0),
                )
            )

    parts.extend(
        [
            _box(
                (900.0, 650.0, 650.0),
                "Four-circuit synchronized hydraulic pump and remote control",
                HYDRAULIC,
                (-half_x, -3_300.0, 325.0),
            ),
            _box(
                (datum.exclusion_zone_length_mm, datum.exclusion_zone_width_mm, 2_500.0),
                "Incident lift exclusion and controlled-access envelope",
                CLEARANCE,
                (0.0, 0.0, 1_250.0),
            ),
        ]
    )
    return Compound(label="LM3 portable hydraulic field-rerailing kit assembly", children=parts)


__all__ = [
    "LM3_CAR_COUNT",
    "RecoveryCapacityCheck",
    "RecoveryLoadCase",
    "RecoveryMassScenario",
    "controlled_recovery_capacity_checks",
    "field_recovery_load_cases",
    "portable_field_rerailing_kit",
    "recovery_mass_scenarios",
]
