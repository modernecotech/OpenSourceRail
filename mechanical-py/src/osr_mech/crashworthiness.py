"""Crashworthiness energy-zone catalogue — RFC 0020.

Publishes the EN 15227 Zone-1 + Zone-2 + Zone-3 envelopes for each
reference consist family so an FEA vendor has a fixed target rather
than a moving spec.

This module is geometry-free: it publishes the constraints as a
dataclass. The car-body parametric CAD (`osr_mech.rolling_stock.car_body`)
reserves the volumes; verifying that the reservation meets the §6
constraints is a pytest concern.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CrashScenario(str, Enum):
    """EN 15227 reference scenarios that bind for urban rail."""

    C_I_TRAIN_TO_TRAIN = "C-I"
    C_III_TRAIN_TO_OBSTACLE = "C-III"


@dataclass(frozen=True)
class CrashEnergyBudget:
    """Absorption-zone allocation per consist end."""

    consist_label: str
    total_mass_tonnes: float
    closing_energy_mj: float
    zone1_share: float  # sacrificial cowl
    zone2_share: float  # under-frame crumple
    zone3_share: float  # anti-override bulkhead

    def zone_energy_mj(self, zone: int) -> float:
        share = {1: self.zone1_share, 2: self.zone2_share, 3: self.zone3_share}[zone]
        # Per-end = half the closing energy for C-I (two trainsets share).
        return 0.5 * self.closing_energy_mj * share


# Reference consist families — from RFC 0020 §4.
BUDGETS: dict[str, CrashEnergyBudget] = {
    "tram-2car": CrashEnergyBudget(
        consist_label="tram-2car",
        total_mass_tonnes=66.0,
        closing_energy_mj=1.65,
        zone1_share=0.30,
        zone2_share=0.40,
        zone3_share=0.30,
    ),
    "light-metro-3car": CrashEnergyBudget(
        consist_label="light-metro-3car",
        total_mass_tonnes=120.0,
        closing_energy_mj=3.00,
        zone1_share=0.30,
        zone2_share=0.40,
        zone3_share=0.30,
    ),
    "metro-4car": CrashEnergyBudget(
        consist_label="metro-4car",
        total_mass_tonnes=160.0,
        closing_energy_mj=4.00,
        zone1_share=0.30,
        zone2_share=0.40,
        zone3_share=0.30,
    ),
    "metro-6car": CrashEnergyBudget(
        consist_label="metro-6car",
        total_mass_tonnes=240.0,
        closing_energy_mj=6.00,
        zone1_share=0.30,
        zone2_share=0.40,
        zone3_share=0.30,
    ),
}


@dataclass(frozen=True)
class CrashZoneConstraints:
    """RFC 0020 §6 parametric geometry constraints."""

    zone1_crumple_length_mm: float = 900.0
    zone2_crumple_length_mm: float = 2_000.0
    anti_climber_height_mm: float = 760.0
    anti_climber_tolerance_mm: float = 25.0
    end_bulkhead_thickness_mm: float = 40.0
    passenger_envelope_survival_fraction: float = 0.95
    peak_decel_g: float = 7.5


CONSTRAINTS = CrashZoneConstraints()


def verify_cowl_length(cowl_length_mm: float) -> bool:
    """Sensor-cowl length must accommodate Zone 1 crumple."""
    return cowl_length_mm >= CONSTRAINTS.zone1_crumple_length_mm


def verify_underframe_length(underframe_length_mm: float) -> bool:
    """Forward under-frame length must accommodate Zone 2 crumple."""
    return underframe_length_mm >= CONSTRAINTS.zone2_crumple_length_mm


__all__ = [
    "BUDGETS",
    "CONSTRAINTS",
    "CrashEnergyBudget",
    "CrashScenario",
    "CrashZoneConstraints",
    "verify_cowl_length",
    "verify_underframe_length",
]
