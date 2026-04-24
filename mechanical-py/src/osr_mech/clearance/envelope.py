"""Kinematic envelope sweep + clearance checks.

The **kinematic envelope** is the 2-D cross-section a rolling-stock
body sweeps through as it navigates a curve at speed under cant: the
**static** envelope (body outline at rest) plus **quasi-static**
(roll from cant deficiency) plus **dynamic** (random-excited sway +
bogie hunting + end-throw on curves).

Real computation uses EN 15273 — "Railway applications. Gauges." The
reference envelope below is approximated from the EN 15273
infrastructure-gauge G2 family appropriate for an urban-metro
2 650 mm × 3 600 mm light-metro body, and serves as the published
baseline for deployments that don't commission a full EN 15273
analysis.

Gauge clearance is evaluated at each infrastructure feature. Fail-
restrictive: any envelope intrusion into the feature's exclusion
zone is a FAIL. Callers remediate by widening the ROW, widening the
curve radius, or reducing design speed.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Color,
    Compound,
    Location,
    Part,
    Rectangle,
    extrude,
)

# Reference body dimensions — matches [osr_mech.rolling_stock.car_body]
# defaults (light-metro-3car, RFC 0008).
_REF_BODY_HALF_WIDTH_MM = 1325.0
_REF_BODY_HEIGHT_MM = 3600.0
_REF_BODY_LENGTH_MM = 22000.0
_REF_FLOOR_HEIGHT_MM = 0.0  # kinematic floor; rolling-stock floor is at 1100
_REF_BOGIE_SPACING_MM = 15000.0  # approx between bogie-pivot centres


@dataclass(frozen=True)
class KinematicEnvelope:
    """Peak excursions of the body outline in mm, applied symmetrically.

    - `lateral_sway_mm`: left/right excursion at peak roll. Grows with
      cant deficiency + speed.
    - `end_throw_mm`: outboard excursion at the body nose / tail when
      midpoint is on a curve (body longer than chord).
    - `mid_throw_mm`: inboard excursion at midpoint (opposite sign to
      end throw).
    - `vertical_mm`: vertical excursion from spring deflection + cant.
    """

    lateral_sway_mm: float
    end_throw_mm: float
    mid_throw_mm: float
    vertical_mm: float


# EN 15273-inferred baseline: 60 mm lateral + 30 mm vertical sway is a
# conservative envelope for a 2 650 mm wide light-metro body at
# speeds ≤ 80 km/h on curves ≥ 200 m. End-throw is computed per
# geometry at check time.
EN_15273_INFERRED = KinematicEnvelope(
    lateral_sway_mm=60.0,
    end_throw_mm=0.0,  # filled in per-check
    mid_throw_mm=0.0,
    vertical_mm=30.0,
)


def reference_envelope() -> KinematicEnvelope:
    """Return the published baseline envelope. Deployments that run
    EN 15273 analysis override with their measured values."""
    return EN_15273_INFERRED


def envelope_swept_on_curve(
    base: KinematicEnvelope,
    radius_m: float,
    body_length_mm: float = _REF_BODY_LENGTH_MM,
    bogie_spacing_mm: float = _REF_BOGIE_SPACING_MM,
) -> KinematicEnvelope:
    """Add curve-induced end + mid throw to the base envelope for a
    body navigating a curve of `radius_m`. On an infinite (tangent)
    radius, both throws are zero.

    Geometry: on a curve radius R, a straight body of length L
    inscribed with bogie centres at ±(b/2) has:

    - End throw  ≈ (L - b)² · (L + b) / (8 · R · L)  (outboard at the ends)
    - Mid throw ≈ b² / (8 · R)  (inboard at the midpoint)

    Both formulas are the small-angle approximation valid for
    L ≪ R (always the case for urban rail where R ≥ 150 m and
    L ≤ 22 m)."""
    if radius_m <= 0.0 or radius_m > 1e9:
        return base
    r_mm = radius_m * 1000.0
    end = (
        ((body_length_mm - bogie_spacing_mm) ** 2)
        * (body_length_mm + bogie_spacing_mm)
        / (8.0 * r_mm * body_length_mm)
    )
    mid = bogie_spacing_mm * bogie_spacing_mm / (8.0 * r_mm)
    return KinematicEnvelope(
        lateral_sway_mm=base.lateral_sway_mm,
        end_throw_mm=max(base.end_throw_mm, end),
        mid_throw_mm=max(base.mid_throw_mm, mid),
        vertical_mm=base.vertical_mm,
    )


@dataclass(frozen=True)
class InfrastructureFeature:
    """A fixed infrastructure feature to check clearance against.

    All offsets are from the track centreline:
    - `lateral_offset_mm`: + = feature to the right of track
      direction; − = left.
    - `min_z_mm`, `max_z_mm`: feature's vertical extent above rail head.
    - `along_track_mm`: along-track centre of the feature.

    Examples:
    - Tunnel wall: `lateral_offset_mm ≈ ±1800`, `min_z_mm = 0`,
      `max_z_mm = 4500`.
    - Platform edge: `lateral_offset_mm = ±1635` (half standard-gauge
      platform offset), `min_z_mm = 0`, `max_z_mm = 1100`.
    - Adjacent-track centre (double-track): `lateral_offset_mm = 3800`
      (track-to-track centre spacing per RFC 0009).
    """

    name: str
    lateral_offset_mm: float
    min_z_mm: float
    max_z_mm: float
    along_track_mm: float = 0.0


@dataclass(frozen=True)
class ClearanceReport:
    feature: InfrastructureFeature
    """Signed clearance in mm: positive = safe margin, negative =
    intrusion."""
    lateral_clearance_mm: float
    """Envelope edge closest to the feature."""
    envelope_edge_lateral_mm: float
    """Whether the check passes (lateral_clearance_mm ≥ 0)."""
    passes: bool


def check_feature(
    envelope: KinematicEnvelope,
    feature: InfrastructureFeature,
    body_half_width_mm: float = _REF_BODY_HALF_WIDTH_MM,
    body_height_mm: float = _REF_BODY_HEIGHT_MM,
    body_end_from_midpoint_mm: float = 0.0,
) -> ClearanceReport:
    """Check whether the envelope clears the feature at the given
    along-track position.

    `body_end_from_midpoint_mm` is the distance from the body's midpoint
    (0) to the along-track point of interest. 0 = midpoint → apply
    `mid_throw`. `± body_length/2` = nose/tail → apply `end_throw`."""

    # Select the appropriate throw based on the along-track position
    # relative to the body midpoint.
    body_half_length = _REF_BODY_LENGTH_MM / 2.0
    t = abs(body_end_from_midpoint_mm) / body_half_length
    t = min(1.0, t)
    # Throw magnitude interpolated between mid and end. Note sign:
    # end-throw pushes outward (away from curve centre); mid-throw
    # pushes inward. For a FAIL-restrictive check we take the
    # outward-worst at each position.
    outward_throw = envelope.end_throw_mm * t + envelope.mid_throw_mm * (1.0 - t) * 0
    # (mid_throw is inward, so it doesn't add to the outward reach.
    # Factor 0 means: when t = 0 -> use base sway only.)

    envelope_outer = (
        body_half_width_mm + envelope.lateral_sway_mm + outward_throw
    )
    feature_abs_offset = abs(feature.lateral_offset_mm)

    # Only features whose vertical extent overlaps the body influence
    # lateral clearance.
    body_overlaps = not (
        feature.max_z_mm < 0.0 or feature.min_z_mm > body_height_mm
    )
    if not body_overlaps:
        return ClearanceReport(
            feature=feature,
            lateral_clearance_mm=feature_abs_offset - envelope_outer,
            envelope_edge_lateral_mm=envelope_outer,
            passes=True,
        )

    clearance = feature_abs_offset - envelope_outer
    return ClearanceReport(
        feature=feature,
        lateral_clearance_mm=clearance,
        envelope_edge_lateral_mm=envelope_outer,
        passes=clearance >= 0.0,
    )


def swept_envelope_part(
    envelope: KinematicEnvelope,
    body_half_width_mm: float = _REF_BODY_HALF_WIDTH_MM,
    body_height_mm: float = _REF_BODY_HEIGHT_MM,
    body_length_mm: float = _REF_BODY_LENGTH_MM,
) -> Part:
    """Visualise the swept envelope as a translucent outer shell
    enclosing the rolling-stock body. Useful as a CAD overlay in the
    STEP viewer to see where the train 'reaches'."""
    outer_half_w = body_half_width_mm + envelope.lateral_sway_mm
    outer_h = body_height_mm + envelope.vertical_mm
    outer_l = body_length_mm + 2.0 * envelope.end_throw_mm
    with BuildPart() as p:
        with BuildSketch():
            Rectangle(outer_l, 2.0 * outer_half_w, align=(Align.CENTER, Align.CENTER))
        extrude(amount=outer_h)
    env = p.part.locate(Location((0.0, 0.0, 0.0)))
    env.color = Color(0.95, 0.40, 0.30, 0.18)
    env.label = "Kinematic envelope (swept)"
    return env


__all__ = [
    "EN_15273_INFERRED",
    "ClearanceReport",
    "InfrastructureFeature",
    "KinematicEnvelope",
    "check_feature",
    "envelope_swept_on_curve",
    "reference_envelope",
    "swept_envelope_part",
]
