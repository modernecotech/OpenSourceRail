"""Small auditable interface calculations; none supplies a released joint design."""
from __future__ import annotations

import math


def finite(**values):
    if any(not math.isfinite(v) for v in values.values()):
        raise ValueError("all inputs must be finite")


def thermal_movement_mm(length_m, alpha_microstrain_per_k, delta_temperature_k):
    """Free movement alpha * L * delta T, signed; restraints require analysis."""
    finite(length=length_m, alpha=alpha_microstrain_per_k, temperature=delta_temperature_k)
    if length_m <= 0 or alpha_microstrain_per_k <= 0:
        raise ValueError("length and expansion coefficient must be positive")
    return length_m * alpha_microstrain_per_k * delta_temperature_k / 1000


def seal_compression_range(thickness_mm, thickness_tolerance_mm, gap_mm, gap_tolerance_mm):
    """Worst-case compression fraction (t-g)/t; negative means loss of contact."""
    finite(thickness=thickness_mm, thickness_tolerance=thickness_tolerance_mm,
           gap=gap_mm, gap_tolerance=gap_tolerance_mm)
    if min(thickness_tolerance_mm, gap_tolerance_mm) < 0 or thickness_mm <= thickness_tolerance_mm or gap_mm < gap_tolerance_mm:
        raise ValueError("invalid thickness/gap tolerance stack")
    return ((thickness_mm-thickness_tolerance_mm-gap_mm-gap_tolerance_mm)/(thickness_mm-thickness_tolerance_mm),
            (thickness_mm+thickness_tolerance_mm-gap_mm+gap_tolerance_mm)/(thickness_mm+thickness_tolerance_mm))


def preload_range_n(torque_nm, diameter_mm, nut_factor_min, nut_factor_max, torque_tolerance_fraction):
    """T=KFd sensitivity. K must come from the actual finish/lube/fastener trial."""
    finite(torque=torque_nm, diameter=diameter_mm, k_min=nut_factor_min,
           k_max=nut_factor_max, tolerance=torque_tolerance_fraction)
    if min(torque_nm, diameter_mm, nut_factor_min) <= 0 or nut_factor_max < nut_factor_min or not 0 <= torque_tolerance_fraction < 1:
        raise ValueError("invalid preload sensitivity inputs")
    return (torque_nm*(1-torque_tolerance_fraction)/(nut_factor_max*diameter_mm/1000),
            torque_nm*(1+torque_tolerance_fraction)/(nut_factor_min*diameter_mm/1000))


def cleaning_labour_hours(area_m2, measured_productivity_m2_per_hour, cycles, setup_minutes):
    """Person-hours, using measured productivity incl. access; not elapsed slot time."""
    finite(area=area_m2, productivity=measured_productivity_m2_per_hour, cycles=cycles, setup=setup_minutes)
    if min(area_m2, cycles, setup_minutes) < 0 or measured_productivity_m2_per_hour <= 0:
        raise ValueError("invalid cleaning workload inputs")
    return cycles*(area_m2/measured_productivity_m2_per_hour+setup_minutes/60)
