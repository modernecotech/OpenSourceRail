"""Resource-driven civil production and erection planning equations."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CivilProductionInputs:
    route_m: float
    elevated_m: float
    at_grade_m: float
    constrained_at_grade_m: float = 0.0
    primary_span_m: float = 25.0
    beam_mould_count: int = 2
    beam_cure_cycle_days: float = 2.0
    piling_rig_count: int = 1
    foundations_per_rig_shift: float = 1.0
    gantry_count: int = 1
    bays_per_gantry_shift: float = 1.0
    panel_gantry_count: int = 1
    panels_per_gantry_shift: float = 40.0
    slipform_metres_per_shift: float = 200.0
    working_days_per_week: int = 6
    foundations_ahead_bays: int = 12


@dataclass(frozen=True)
class CivilProductionPlan:
    route_m: float
    elevated_bays: int
    foundations: int
    primary_beams: int
    single_track_panels: int
    slipformed_route_m: float
    beam_production_days: int
    foundation_days: int
    erection_days: int
    panel_placement_days: int
    slipform_days: int
    minimum_buffer_beams: int
    foundations_ahead_bays: int
    elevated_critical_path_days: int
    at_grade_critical_path_days: int
    programme_working_days: int
    programme_calendar_weeks: float
    assumptions: dict[str, float | int]


def civil_production_plan(inputs: CivilProductionInputs) -> CivilProductionPlan:
    """Calculate durations from quantities and resources, never fixed section days."""

    if inputs.route_m <= 0 or inputs.elevated_m < 0 or inputs.at_grade_m < 0:
        raise ValueError("route length must be positive and class lengths non-negative")
    if inputs.elevated_m + inputs.at_grade_m > inputs.route_m + 0.001:
        raise ValueError("civil class lengths exceed route length")
    if not 0.0 <= inputs.constrained_at_grade_m <= inputs.at_grade_m:
        raise ValueError("constrained at-grade length must lie within at-grade length")
    positive_resources = (
        inputs.beam_mould_count,
        inputs.beam_cure_cycle_days,
        inputs.piling_rig_count,
        inputs.foundations_per_rig_shift,
        inputs.gantry_count,
        inputs.bays_per_gantry_shift,
        inputs.panel_gantry_count,
        inputs.panels_per_gantry_shift,
        inputs.slipform_metres_per_shift,
        inputs.working_days_per_week,
    )
    if any(value <= 0 for value in positive_resources):
        raise ValueError("production resources and rates must be positive")
    if inputs.primary_span_m not in (20.0, 25.0):
        raise ValueError("primary span must use the 20 m or 25 m catalogue")
    if not 10 <= inputs.foundations_ahead_bays <= 15:
        raise ValueError("foundations must be planned 10-15 bays ahead of erection")

    bays = math.ceil(inputs.elevated_m / inputs.primary_span_m)
    foundations = bays + 1 if bays else 0
    beams = bays * 2
    panels = math.ceil(inputs.constrained_at_grade_m / 6.0) * 2
    slipformed_m = inputs.at_grade_m - inputs.constrained_at_grade_m
    beam_days = math.ceil(
        math.ceil(beams / inputs.beam_mould_count) * inputs.beam_cure_cycle_days
    )
    foundation_days = math.ceil(
        foundations / (inputs.piling_rig_count * inputs.foundations_per_rig_shift)
    )
    erection_days = math.ceil(bays / (inputs.gantry_count * inputs.bays_per_gantry_shift))
    panel_days = math.ceil(
        panels / (inputs.panel_gantry_count * inputs.panels_per_gantry_shift)
    )
    slipform_days = math.ceil(slipformed_m / inputs.slipform_metres_per_shift)
    buffer_bays = min(inputs.foundations_ahead_bays, bays)
    buffer_foundation_days = math.ceil(
        (buffer_bays + (1 if buffer_bays else 0))
        / (inputs.piling_rig_count * inputs.foundations_per_rig_shift)
    )
    buffer_beams = buffer_bays * 2
    buffer_beam_days = math.ceil(
        math.ceil(buffer_beams / inputs.beam_mould_count) * inputs.beam_cure_cycle_days
    )
    erection_start = max(buffer_foundation_days, buffer_beam_days)
    elevated_critical = max(beam_days, foundation_days, erection_start + erection_days)
    at_grade_critical = panel_days + slipform_days
    programme = max(elevated_critical, at_grade_critical)
    assumptions = asdict(inputs)
    assumptions.pop("route_m")
    assumptions.pop("elevated_m")
    assumptions.pop("at_grade_m")
    return CivilProductionPlan(
        route_m=inputs.route_m,
        elevated_bays=bays,
        foundations=foundations,
        primary_beams=beams,
        single_track_panels=panels,
        slipformed_route_m=slipformed_m,
        beam_production_days=beam_days,
        foundation_days=foundation_days,
        erection_days=erection_days,
        panel_placement_days=panel_days,
        slipform_days=slipform_days,
        minimum_buffer_beams=buffer_beams,
        foundations_ahead_bays=buffer_bays,
        elevated_critical_path_days=elevated_critical,
        at_grade_critical_path_days=at_grade_critical,
        programme_working_days=programme,
        programme_calendar_weeks=round(programme / inputs.working_days_per_week, 2),
        assumptions=assumptions,
    )


__all__ = ["CivilProductionInputs", "CivilProductionPlan", "civil_production_plan"]
