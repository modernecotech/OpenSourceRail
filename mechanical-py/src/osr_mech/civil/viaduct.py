"""Automated planning gates for the OSR Rapid Viaduct Kit.

These checks reject internally inconsistent catalogue geometry. They do not
replace bridge analysis, kinematic simulation, a transport-route survey, or a
licensed engineer's project-specific design release.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .ugirder import (
    CLEAR_WALKWAY_WIDTH_MM,
    DYNAMIC_TRAIN_WIDTH_MM,
    ESCAPE_LEDGE_HEIGHT_MM,
    EXTERNAL_HEIGHT_MM,
    FLOOR_THICKNESS_MM,
    INTERNAL_WIDTH_MM,
    OPPOSITE_SIDE_CLEARANCE_MM,
    approx_mass_kg,
)

DEFAULT_PARAPET_HEIGHT_ABOVE_WALKWAY_MM = 1_400.0
REFERENCE_PARAPET_HEIGHT_ABOVE_WALKWAY_MM = (
    EXTERNAL_HEIGHT_MM - FLOOR_THICKNESS_MM - ESCAPE_LEDGE_HEIGHT_MM
)
DEFAULT_APPROVED_TRANSPORT_MASS_KG = 130_000.0
DEFAULT_APPROVED_TRANSPORT_WIDTH_MM = 5_000.0
DEFAULT_APPROVED_TRANSPORT_HEIGHT_MM = 2_100.0


def required_internal_width_mm(
    dynamic_train_width_mm: float = DYNAMIC_TRAIN_WIDTH_MM,
    clear_walkway_width_mm: float = CLEAR_WALKWAY_WIDTH_MM,
    opposite_side_clearance_mm: float = OPPOSITE_SIDE_CLEARANCE_MM,
    tolerance_and_sway_mm: float = 220.0,
) -> float:
    """Minimum clear trough width before a curve-chord allowance is added."""

    return (
        dynamic_train_width_mm
        + clear_walkway_width_mm
        + opposite_side_clearance_mm
        + tolerance_and_sway_mm
    )


def straight_span_chord_offset_m(span_m: float, radius_m: float) -> float:
    """Maximum mid-span offset between a straight chord and circular arc."""

    if span_m <= 0.0 or radius_m <= 0.0 or span_m / 2.0 >= radius_m:
        raise ValueError("span and radius do not define a valid circular chord")
    return radius_m - math.sqrt(radius_m * radius_m - (span_m / 2.0) ** 2)


def required_interior_bearing_count(tracks: int = 2) -> int:
    """Two web bearings times two adjoining span ends per track."""

    if tracks < 1:
        raise ValueError("tracks must be at least one")
    return tracks * 2 * 2


def required_end_support_bearing_count(tracks: int = 2) -> int:
    """Two web bearings under one span end per track."""

    if tracks < 1:
        raise ValueError("tracks must be at least one")
    return tracks * 2


@dataclass(frozen=True)
class ViaductEnvelopeCheck:
    span_m: float = 25.0
    curve_radius_m: float = 300.0
    internal_width_mm: float = INTERNAL_WIDTH_MM
    dynamic_train_width_mm: float = DYNAMIC_TRAIN_WIDTH_MM
    clear_walkway_width_mm: float = CLEAR_WALKWAY_WIDTH_MM
    opposite_side_clearance_mm: float = OPPOSITE_SIDE_CLEARANCE_MM
    tolerance_and_sway_mm: float = 220.0
    parapet_height_above_walkway_mm: float = REFERENCE_PARAPET_HEIGHT_ABOVE_WALKWAY_MM
    required_parapet_height_mm: float = DEFAULT_PARAPET_HEIGHT_ABOVE_WALKWAY_MM
    tracks: int = 2
    interior_bearing_count: int = 8
    transport_mass_kg: float | None = None
    transport_width_mm: float = 4_900.0
    transport_height_mm: float = 1_850.0
    approved_transport_mass_kg: float = DEFAULT_APPROVED_TRANSPORT_MASS_KG
    approved_transport_width_mm: float = DEFAULT_APPROVED_TRANSPORT_WIDTH_MM
    approved_transport_height_mm: float = DEFAULT_APPROVED_TRANSPORT_HEIGHT_MM


def viaduct_envelope_issues(check: ViaductEnvelopeCheck) -> tuple[str, ...]:
    """Return all failed catalogue gates for a candidate full-span unit."""

    issues: list[str] = []
    required_width = required_internal_width_mm(
        check.dynamic_train_width_mm,
        check.clear_walkway_width_mm,
        check.opposite_side_clearance_mm,
        check.tolerance_and_sway_mm,
    )
    if check.internal_width_mm < required_width:
        issues.append(
            f"internal width {check.internal_width_mm:g} mm is below the "
            f"train-plus-egress requirement {required_width:g} mm"
        )

    # Chord offset consumes the residual lateral space after the train,
    # walkway, and opposite-side clearance. The tolerance/sway reserve remains
    # unavailable to deliberate geometric offset.
    residual_mm = check.internal_width_mm - (
        check.dynamic_train_width_mm
        + check.clear_walkway_width_mm
        + check.opposite_side_clearance_mm
    )
    try:
        chord_offset_mm = straight_span_chord_offset_m(check.span_m, check.curve_radius_m) * 1000.0
    except ValueError as exc:
        issues.append(str(exc))
    else:
        if chord_offset_mm > residual_mm:
            issues.append(
                f"straight-span chord offset {chord_offset_mm:.0f} mm exceeds "
                f"available trough lateral clearance {residual_mm:.0f} mm"
            )

    required_bearings = required_interior_bearing_count(check.tracks)
    if check.interior_bearing_count < required_bearings:
        issues.append(
            f"interior bearing count {check.interior_bearing_count} is below "
            f"tracks x two webs x two adjoining ends = {required_bearings}"
        )
    if check.parapet_height_above_walkway_mm < check.required_parapet_height_mm:
        issues.append(
            f"parapet height {check.parapet_height_above_walkway_mm:g} mm above "
            f"finished walkway is below {check.required_parapet_height_mm:g} mm"
        )

    transport_mass_kg = check.transport_mass_kg
    if transport_mass_kg is None:
        transport_mass_kg = approx_mass_kg(check.span_m)
    if transport_mass_kg > check.approved_transport_mass_kg:
        issues.append(
            f"transport mass {transport_mass_kg:.0f} kg exceeds approved "
            f"transporter/erection envelope {check.approved_transport_mass_kg:.0f} kg"
        )
    if check.transport_width_mm > check.approved_transport_width_mm:
        issues.append("transport width exceeds the approved route envelope")
    if check.transport_height_mm > check.approved_transport_height_mm:
        issues.append("transport height exceeds the approved route envelope")
    return tuple(issues)


def assert_viaduct_envelope(check: ViaductEnvelopeCheck) -> None:
    """Raise when any controlled planning gate fails."""

    issues = viaduct_envelope_issues(check)
    if issues:
        raise ValueError("; ".join(issues))


__all__ = [
    "ViaductEnvelopeCheck",
    "assert_viaduct_envelope",
    "required_end_support_bearing_count",
    "required_interior_bearing_count",
    "required_internal_width_mm",
    "straight_span_chord_offset_m",
    "viaduct_envelope_issues",
]
