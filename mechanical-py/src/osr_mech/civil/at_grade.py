"""Construction-method selection for the two-track at-grade trackform."""

from __future__ import annotations

import math
from dataclasses import dataclass


SLIPFORM_MINIMUM_OPEN_RUN_M = 200.0
PRECAST_PANEL_LENGTH_M = 6.0


@dataclass(frozen=True)
class AtGradeMethodSelection:
    method: str
    reason: str
    release_gates: tuple[str, ...]


@dataclass(frozen=True)
class AtGradeMethodQuantities:
    route_m: float
    slipformed_route_m: float
    constrained_route_m: float
    single_track_precast_panels: int


def select_at_grade_method(
    run_length_m: float,
    *,
    open_machine_access: bool = True,
    utility_crossings: bool = False,
    short_possession: bool = False,
    flood_prone: bool = False,
) -> AtGradeMethodSelection:
    if run_length_m <= 0.0:
        raise ValueError("at-grade run length must be positive")
    constrained = utility_crossings or short_possession or flood_prone
    if (
        run_length_m >= SLIPFORM_MINIMUM_OPEN_RUN_M
        and open_machine_access
        and not constrained
    ):
        return AtGradeMethodSelection(
            method="continuous-slipform",
            reason="long open run with machine access",
            release_gates=(
                "formation bearing and drainage release",
                "machine-control and survey trial",
                "concrete mix, curing and crack-control trial",
                "fastening-seat geometry acceptance",
            ),
        )
    return AtGradeMethodSelection(
        method="single-track-precast-st6",
        reason="constrained, replaceable, flood-prone, or short-possession zone",
        release_gates=(
            "formation and drainage release",
            "panel lifting and possession plan",
            "joint, grout and fastening survey acceptance",
        ),
    )


def at_grade_method_quantities(
    route_m: float,
    *,
    constrained_route_m: float = 0.0,
    tracks: int = 2,
) -> AtGradeMethodQuantities:
    if route_m < 0.0 or constrained_route_m < 0.0:
        raise ValueError("at-grade lengths must be non-negative")
    if constrained_route_m > route_m:
        raise ValueError("constrained at-grade length exceeds at-grade route length")
    if tracks < 1:
        raise ValueError("track count must be positive")
    panels = math.ceil(constrained_route_m / PRECAST_PANEL_LENGTH_M) * tracks
    return AtGradeMethodQuantities(
        route_m=route_m,
        slipformed_route_m=route_m - constrained_route_m,
        constrained_route_m=constrained_route_m,
        single_track_precast_panels=panels,
    )


__all__ = [
    "AtGradeMethodQuantities",
    "AtGradeMethodSelection",
    "PRECAST_PANEL_LENGTH_M",
    "SLIPFORM_MINIMUM_OPEN_RUN_M",
    "at_grade_method_quantities",
    "select_at_grade_method",
]
