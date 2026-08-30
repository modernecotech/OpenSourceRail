"""Eligibility gate for reinforced-soil low viaduct approaches."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class ReinforcedSoilApproachPlan:
    eligible: bool
    system: str
    height_m: float
    length_m: float
    potentially_avoided_spans: int
    reason: str
    release_gates: tuple[str, ...]


def reinforced_soil_approach_plan(
    height_m: float,
    length_m: float,
    *,
    span_m: float = 25.0,
    maximum_height_m: float = 4.5,
    flood_or_scour: bool = False,
    severe_settlement_risk: bool = False,
    sufficient_right_of_way: bool = True,
) -> ReinforcedSoilApproachPlan:
    if height_m <= 0.0 or length_m <= 0.0:
        raise ValueError("approach height and length must be positive")
    if span_m not in (20.0, 25.0):
        raise ValueError("approach comparison uses 20 m or 25 m catalogue spans")
    exclusions: list[str] = []
    if height_m > maximum_height_m:
        exclusions.append("height exceeds the initial reinforced-soil catalogue")
    if flood_or_scour:
        exclusions.append("flood or scour exposure")
    if severe_settlement_risk:
        exclusions.append("severe settlement risk")
    if not sufficient_right_of_way:
        exclusions.append("insufficient right-of-way")
    eligible = not exclusions
    return ReinforcedSoilApproachPlan(
        eligible=eligible,
        system="reinforced-soil-retained-embankment" if eligible else "project-specific-transition",
        height_m=height_m,
        length_m=length_m,
        potentially_avoided_spans=math.ceil(length_m / span_m) if eligible else 0,
        reason="eligible after project checks" if eligible else "; ".join(exclusions),
        release_gates=(
            "cyclic rail-load deformation analysis",
            "total and differential settlement analysis",
            "reinforced fill and facing design",
            "global stability and bearing verification",
            "drainage and transition-slab design",
        ),
    )


__all__ = ["ReinforcedSoilApproachPlan", "reinforced_soil_approach_plan"]
