"""Deterministic planning model for short semi-continuous viaduct units."""

from __future__ import annotations

import math
from dataclasses import dataclass


CONTINUITY_RELEASE_GATES = (
    "continuous-welded-rail interaction analysis",
    "braking and traction load distribution",
    "temperature and shrinkage movement analysis",
    "seismic restraint and displacement analysis",
    "foundation-flexibility and soil-structure interaction analysis",
    "selected connection fatigue and waterproofing detail",
    "structural continuity load path and construction stages where bearings are shared",
)


@dataclass(frozen=True)
class SemiContinuousUnitPlan:
    route_length_m: float
    span_m: float
    spans: int
    unit_spans: int
    units: int
    link_slabs: int
    deck_gaps: int
    bearings: int
    internal_support_bearings: int
    expansion_support_bearings: int
    maximum_unit_length_m: float
    release_gates: tuple[str, ...]
    connection_scheme: str
    structural_continuity_accepted: bool = False


def semi_continuous_unit_plan(
    route_length_m: float,
    *,
    span_m: float = 25.0,
    unit_spans: int = 4,
    tracks: int = 2,
    webs_per_beam: int = 2,
    connection_scheme: str = "structural-continuity",
) -> SemiContinuousUnitPlan:
    """Group transportable beams into short units and count their interfaces.

    The structural-continuity option has one bearing line at internal supports.
    Simple spans with link slabs retain two independent girder-end lines.
    Adjacent units keep
    independent bearing lines at their shared expansion support, which is why
    a four-span, twin-track kilometre has 200 bearings rather than 164.
    """

    if route_length_m <= 0.0:
        raise ValueError("route length must be positive")
    if span_m not in (20.0, 25.0):
        raise ValueError("semi-continuous units use 20 m or 25 m catalogue spans")
    if unit_spans not in (4, 5):
        raise ValueError("semi-continuous units must contain four or five spans")
    if tracks < 1 or webs_per_beam < 1:
        raise ValueError("tracks and webs per beam must be positive")
    if connection_scheme not in {"structural-continuity", "simple-span-link-slab"}:
        raise ValueError("unknown connection scheme")

    spans = math.ceil(route_length_m / span_m)
    units = math.ceil(spans / unit_spans)
    bearings_per_line = tracks * webs_per_beam
    # Every unit owns a bearing line at both ends. At a unit boundary the two
    # lines remain separate so that the expansion joint can move.
    bearings = ((spans + units) if connection_scheme == "structural-continuity" else 2 * spans) * bearings_per_line
    link_slabs = spans - units
    return SemiContinuousUnitPlan(
        route_length_m=route_length_m,
        span_m=span_m,
        spans=spans,
        unit_spans=unit_spans,
        units=units,
        link_slabs=link_slabs,
        deck_gaps=units,
        bearings=bearings,
        internal_support_bearings=bearings_per_line if connection_scheme == "structural-continuity" else 2 * bearings_per_line,
        expansion_support_bearings=bearings_per_line * 2,
        maximum_unit_length_m=span_m * unit_spans,
        release_gates=CONTINUITY_RELEASE_GATES,
        connection_scheme=connection_scheme,
    )


__all__ = [
    "CONTINUITY_RELEASE_GATES",
    "SemiContinuousUnitPlan",
    "semi_continuous_unit_plan",
]
