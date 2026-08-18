"""Curved match-cast segmental U/box planning family."""

from __future__ import annotations

import math
from typing import Literal

from osr_mech.cad import Axis, Box, Color, Compound, Location, Part

from .ugirder import (
    EXTERNAL_HEIGHT_MM,
    EXTERNAL_WIDTH_MM,
    u_girder_segment_envelope,
)

MIN_SEGMENT_LENGTH_M = 2.5
MAX_SEGMENT_LENGTH_M = 3.0
MIN_CURVE_RADIUS_M = 90.0


def _arc_pose(
    station_m: float,
    radius_m: float,
    direction: Literal["left", "right"],
) -> tuple[float, float, float]:
    """Return X, Y and tangent angle for an arc starting along +X."""

    sign = 1.0 if direction == "left" else -1.0
    theta = station_m / radius_m
    return (
        radius_m * math.sin(theta),
        sign * radius_m * (1.0 - math.cos(theta)),
        sign * math.degrees(theta),
    )


def segmental_u_envelope(
    span_m: float = 25.0,
    segment_length_m: float = 2.5,
    curve_radius_m: float = 200.0,
    direction: Literal["left", "right"] = "left",
) -> Compound:
    """Build faceted match-cast segments along a controlled circular arc.

    Each solid is a straight match-cast chord with its own surveyed placement
    and tangent rotation. This supports review of joint planes, curvature,
    tendon corridors, transport units and launcher geometry. The supplier
    model still owns shear keys, tendon profiles and casting tolerances.
    """

    if not MIN_SEGMENT_LENGTH_M <= segment_length_m <= MAX_SEGMENT_LENGTH_M:
        raise ValueError("match-cast segment length must be 2.5 m .. 3.0 m")
    if not math.isfinite(curve_radius_m) or curve_radius_m < MIN_CURVE_RADIUS_M:
        raise ValueError(f"curve radius must be at least {MIN_CURVE_RADIUS_M:g} m")
    if direction not in ("left", "right"):
        raise ValueError("direction must be 'left' or 'right'")
    count = round(span_m / segment_length_m)
    if count < 2 or abs(count * segment_length_m - span_m) > 1e-6:
        raise ValueError("span must divide into equal match-cast segments")

    segment_angle_rad = segment_length_m / curve_radius_m
    chord_m = 2.0 * curve_radius_m * math.sin(segment_angle_rad / 2.0)
    chord_mm = chord_m * 1_000.0
    parts: list[Part] = []
    marker = Color(0.25, 0.45, 0.62, 0.70)

    for index in range(count):
        station_m = (index + 0.5) * segment_length_m
        x_m, y_m, tangent_deg = _arc_pose(station_m, curve_radius_m, direction)
        segment = u_girder_segment_envelope(chord_m)
        segment = segment.translate((-chord_mm / 2.0, 0.0, 0.0))
        segment = segment.rotate(Axis.Z, tangent_deg)
        segment = segment.translate((x_m * 1_000.0, y_m * 1_000.0, 0.0))
        segment.label = f"Match-cast U segment {index + 1:02d} of {count:02d}"
        parts.append(segment)

        tendon = Box(chord_mm, 400.0, 200.0)
        tendon = tendon.rotate(Axis.Z, tangent_deg)
        tendon = tendon.locate(Location((x_m * 1_000.0, y_m * 1_000.0, 350.0)))
        tendon.label = "Curved post-tensioning tendon and grout QA corridor"
        tendon.color = marker
        parts.append(tendon)

    for index in range(1, count):
        station_m = index * segment_length_m
        x_m, y_m, tangent_deg = _arc_pose(station_m, curve_radius_m, direction)
        joint = Box(20.0, EXTERNAL_WIDTH_MM, EXTERNAL_HEIGHT_MM)
        joint = joint.rotate(Axis.Z, tangent_deg)
        joint = joint.locate(
            Location((x_m * 1_000.0, y_m * 1_000.0, EXTERNAL_HEIGHT_MM / 2.0))
        )
        joint.label = "Match-cast epoxy joint and shear-key design plane"
        joint.color = marker
        parts.append(joint)

    return Compound(
        label=(
            f"OSR-US curved segmental U/box coordination envelope "
            f"({count} segments, R={curve_radius_m:g} m {direction})"
        ),
        children=parts,
    )


__all__ = [
    "MAX_SEGMENT_LENGTH_M",
    "MIN_CURVE_RADIUS_M",
    "MIN_SEGMENT_LENGTH_M",
    "segmental_u_envelope",
]
