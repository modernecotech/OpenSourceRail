"""Automated planning gates for the OSR Rapid Viaduct Kit.

These checks reject internally inconsistent catalogue geometry. They do not
replace bridge analysis, kinematic simulation, a transport-route survey, or a
licensed engineer's project-specific design release.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .decked_pi import (
    DECK_WIDTH_MM,
    OVERALL_DEPTH_MM,
    WALKWAY_CASSETTE_WIDTH_MM,
    approx_mass_kg,
)
from .substructure import GIRDER_CENTRE_SPACING_MM, PIER_CAP_Y_MM

DEFAULT_PARAPET_HEIGHT_ABOVE_WALKWAY_MM = 1_400.0
DEFAULT_APPROVED_TRANSPORT_MASS_KG = 75_000.0
DEFAULT_APPROVED_TRANSPORT_WIDTH_MM = 3_000.0
DEFAULT_APPROVED_TRANSPORT_HEIGHT_MM = 1_300.0


def required_internal_width_mm(
    dynamic_train_width_mm: float = 2_970.0,
    clear_walkway_width_mm: float = WALKWAY_CASSETTE_WIDTH_MM,
    opposite_side_clearance_mm: float = 250.0,
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
    """One bearing line beneath two continuous web lines per track."""

    if tracks < 1:
        raise ValueError("tracks must be at least one")
    return tracks * 2


def required_expansion_support_bearing_count(tracks: int = 2) -> int:
    """Two independent unit-end bearing lines at an expansion support."""

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
    beam_width_mm: float = DECK_WIDTH_MM
    track_centres_mm: float = GIRDER_CENTRE_SPACING_MM
    clear_walkway_width_mm: float = WALKWAY_CASSETTE_WIDTH_MM
    overall_guideway_width_mm: float = 8_500.0
    cap_width_mm: float = PIER_CAP_Y_MM
    maximum_chord_adjustment_mm: float = 300.0
    parapet_height_above_walkway_mm: float = 1_400.0
    required_parapet_height_mm: float = DEFAULT_PARAPET_HEIGHT_ABOVE_WALKWAY_MM
    tracks: int = 2
    interior_bearing_count: int = 4
    transport_mass_kg: float | None = None
    transport_width_mm: float = DECK_WIDTH_MM
    transport_height_mm: float = OVERALL_DEPTH_MM
    approved_transport_mass_kg: float = DEFAULT_APPROVED_TRANSPORT_MASS_KG
    approved_transport_width_mm: float = DEFAULT_APPROVED_TRANSPORT_WIDTH_MM
    approved_transport_height_mm: float = DEFAULT_APPROVED_TRANSPORT_HEIGHT_MM


def viaduct_envelope_issues(check: ViaductEnvelopeCheck) -> tuple[str, ...]:
    """Return all failed catalogue gates for a candidate full-span unit."""

    issues: list[str] = []
    if check.span_m not in (20.0, 25.0):
        issues.append("decked pi catalogue span must be 20 m or 25 m")
    if check.beam_width_mm > check.approved_transport_width_mm:
        issues.append("primary beam width exceeds the 3.0 m DFMA shipping gate")
    if check.track_centres_mm != 3_500.0:
        issues.append("standard tangent track centres must be 3500 mm")
    if check.clear_walkway_width_mm < 1_000.0:
        issues.append("clear outer evacuation walkway is below 1000 mm")
    if not 8_500.0 <= check.overall_guideway_width_mm <= 9_000.0:
        # The 8.4 m bare geometry needs connection/tolerance margins to be
        # declared as an 8.5--9.0 m controlled envelope.
        issues.append("overall twin-track guideway envelope must be 8.5--9.0 m")
    if not 6_500.0 <= check.cap_width_mm <= 7_500.0:
        issues.append("pier-cap width must be 6.5--7.5 m")

    try:
        chord_offset_mm = straight_span_chord_offset_m(check.span_m, check.curve_radius_m) * 1000.0
    except ValueError as exc:
        issues.append(str(exc))
    else:
        if chord_offset_mm > check.maximum_chord_adjustment_mm:
            issues.append(
                f"straight-span chord offset {chord_offset_mm:.0f} mm exceeds "
                f"the adjustable fixation/edge allowance {check.maximum_chord_adjustment_mm:.0f} mm"
            )

    required_bearings = required_interior_bearing_count(check.tracks)
    if check.interior_bearing_count < required_bearings:
        issues.append(
            f"interior bearing count {check.interior_bearing_count} is below "
            f"tracks x two continuous web lines = {required_bearings}"
        )
    if check.parapet_height_above_walkway_mm < check.required_parapet_height_mm:
        issues.append(
            f"parapet height {check.parapet_height_above_walkway_mm:g} mm above "
            f"finished walkway is below {check.required_parapet_height_mm:g} mm"
        )

    transport_mass_kg = check.transport_mass_kg
    if transport_mass_kg is None:
        try:
            transport_mass_kg = approx_mass_kg(check.span_m)
        except ValueError:
            transport_mass_kg = 0.0
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
    "required_expansion_support_bearing_count",
    "required_interior_bearing_count",
    "required_internal_width_mm",
    "straight_span_chord_offset_m",
    "viaduct_envelope_issues",
]
