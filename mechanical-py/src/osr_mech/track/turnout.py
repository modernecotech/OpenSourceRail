"""Parametric turnouts — 1:9 / 1:14 / 1:18.5 per RFC 0012.

A turnout is modelled as three sub-assemblies:

- **Switch** — the two point-rails (switch blades) that shift laterally
  to route a train onto either the straight (`normal`) or diverging
  (`reverse`) track.
- **Crossing** (frog) — where the two running rails cross on the
  diverging route; comes in cast-manganese or bolted fabricated form.
- **Closure rails** — the rail panels between the switch and the
  crossing, curved on the diverging side.

The parametric model captures the geometry dimensions in plan view
needed for:

- Civil: turnout footprint for layout + permanent-way design.
- Clearance: swept-solid vs. rolling-stock kinematic envelope.
- Signalling: switch-machine mounting + derailer clearance.
- BOM: rail length by profile + sleeper count + switch-machine type.

This is *not* a structural rail-head design; real ordering uses
catalogue items from Voestalpine / Pandrol / ArcelorMittal. What OSR
supplies is the geometric shell + published dimensions so a partner
can drop a catalogue turnout into the same footprint.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

from osr_mech.cad import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Color,
    Compound,
    Location,
    Part,
    Plane,
    Rectangle,
    extrude,
)

from ..common import STANDARD_GAUGE_MM


# ---------------------------------------------------------------------------
# Turnout class (tangent ratio)
# ---------------------------------------------------------------------------


class TurnoutTangent(str, Enum):
    """RFC 0012 §1 — three tangent classes in scope."""

    T_1_9 = "1:9"
    T_1_14 = "1:14"
    T_1_18_5 = "1:18.5"


# Catalogue dimensions — RFC 0012 §2 tables, matched to UIC 60E1 rail.
@dataclass(frozen=True)
class TurnoutGeometry:
    """Plan-view dimensions of a standard-gauge turnout."""

    tangent: TurnoutTangent
    """Total along-track length from switch toe to crossing heel."""
    total_length_mm: float
    """Diverging-rail radius, metres — the minimum curve the turnout
    imposes on a train taking the reverse route."""
    diverging_radius_m: float
    """Switch blade length."""
    switch_blade_length_mm: float
    """Crossing (frog) length."""
    crossing_length_mm: float
    """Maximum diverging speed permitted through this turnout, km/h
    (RFC 0012 §2)."""
    max_reverse_speed_kmh: float
    """Sleeper count across the full turnout length."""
    sleeper_count: int


CATALOGUE: dict[TurnoutTangent, TurnoutGeometry] = {
    TurnoutTangent.T_1_9: TurnoutGeometry(
        tangent=TurnoutTangent.T_1_9,
        total_length_mm=27_000.0,
        diverging_radius_m=190.0,
        switch_blade_length_mm=7_800.0,
        crossing_length_mm=4_200.0,
        max_reverse_speed_kmh=40.0,
        sleeper_count=42,
    ),
    TurnoutTangent.T_1_14: TurnoutGeometry(
        tangent=TurnoutTangent.T_1_14,
        total_length_mm=43_000.0,
        diverging_radius_m=500.0,
        switch_blade_length_mm=11_800.0,
        crossing_length_mm=6_200.0,
        max_reverse_speed_kmh=60.0,
        sleeper_count=68,
    ),
    TurnoutTangent.T_1_18_5: TurnoutGeometry(
        tangent=TurnoutTangent.T_1_18_5,
        total_length_mm=60_000.0,
        diverging_radius_m=900.0,
        switch_blade_length_mm=16_200.0,
        crossing_length_mm=8_500.0,
        max_reverse_speed_kmh=80.0,
        sleeper_count=94,
    ),
}


# Colours for visual distinction in CAD review.
COLOR_STRAIGHT_RAIL = Color(0.45, 0.45, 0.5)
COLOR_DIVERGING_RAIL = Color(0.55, 0.35, 0.2)
COLOR_SWITCH_BLADE = Color(0.80, 0.55, 0.15)  # highlighted
COLOR_CROSSING = Color(0.25, 0.25, 0.3)
COLOR_SLEEPER = Color(0.55, 0.45, 0.35)


# ---------------------------------------------------------------------------
# Geometry builders
# ---------------------------------------------------------------------------


def _straight_rail(length_mm: float, y_mm: float) -> Part:
    """A single straight rail in plan view: 150 mm wide × 40 mm tall
    (simplified). Always follows the along-track axis."""
    with BuildPart() as p:
        with BuildSketch():
            Rectangle(length_mm, 150.0, align=(Align.MIN, Align.CENTER))
        extrude(amount=40.0)
    r = p.part.locate(Location((0.0, y_mm, 0.0)))
    r.color = COLOR_STRAIGHT_RAIL
    r.label = "Rail (straight)"
    return r


def _diverging_rail(geometry: TurnoutGeometry, from_y_mm: float) -> Part:
    """Approximate the diverging rail as a sequence of small straight
    segments along the circular arc defined by the tangent ratio.

    A 1:9 turnout with 190 m radius + 27 m length gives a heading
    change of about 27/190 = 0.142 rad = 8.1°, close to the
    atan(1/9) = 6.34° we'd expect. The approximation is visual; the
    straight-line sampling is dense enough (50 segments) for the
    review model to land inside the diverging-rail tolerance."""
    n = 50
    arc_len = geometry.total_length_mm
    radius = geometry.diverging_radius_m * 1000.0
    segments: list[Part] = []
    bearing = 0.0
    x, y = 0.0, from_y_mm
    ds = arc_len / n
    for _ in range(n):
        dx = ds * math.cos(bearing)
        dy = ds * math.sin(bearing)
        with BuildPart() as p:
            with BuildSketch():
                Rectangle(ds + 1.0, 150.0, align=(Align.CENTER, Align.CENTER))
            extrude(amount=40.0)
        seg = p.part.rotate(Axis.Z, math.degrees(bearing)).locate(
            Location((x + dx / 2.0, y + dy / 2.0, 0.0))
        )
        seg.color = COLOR_DIVERGING_RAIL
        seg.label = "Rail (diverging)"
        segments.append(seg)
        x += dx
        y += dy
        bearing += ds / radius
    return Compound(label="Diverging rail", children=segments)


def _switch_blade(geometry: TurnoutGeometry, y_mm: float) -> Part:
    """Highlight the active switch blade as a separate coloured part
    so it reads in the CAD viewer. The blade overlays the first
    `switch_blade_length_mm` of the straight rail (for the normal-to-
    normal route)."""
    with BuildPart() as p:
        with BuildSketch():
            Rectangle(
                geometry.switch_blade_length_mm,
                150.0,
                align=(Align.MIN, Align.CENTER),
            )
        extrude(amount=45.0)  # slightly taller, to render above rail
    b = p.part.locate(Location((0.0, y_mm, 0.0)))
    b.color = COLOR_SWITCH_BLADE
    b.label = "Switch blade (active tip)"
    return b


def _crossing(geometry: TurnoutGeometry) -> Part:
    """Cast-manganese (or fabricated) crossing at the heel of the
    turnout. Modelled as a small cuboid at the intersection of the
    straight and diverging rails."""
    with BuildPart() as p:
        with BuildSketch():
            Rectangle(
                geometry.crossing_length_mm,
                600.0,
                align=(Align.CENTER, Align.CENTER),
            )
        extrude(amount=60.0)
    c = p.part.locate(
        Location(
            (
                geometry.total_length_mm - geometry.crossing_length_mm / 2.0,
                0.0,
                0.0,
            )
        )
    )
    c.color = COLOR_CROSSING
    c.label = "Crossing (frog)"
    return c


def _sleepers(geometry: TurnoutGeometry) -> Compound:
    """Sleeper array spanning the turnout footprint. Wider than
    mainline sleepers to accommodate the diverging track."""
    parts: list[Part] = []
    spacing = geometry.total_length_mm / (geometry.sleeper_count + 1)
    # Sleepers get progressively longer along the turnout to span both
    # tracks as they separate.
    for i in range(geometry.sleeper_count):
        x = (i + 1) * spacing
        # Estimate separation from the diverging slope.
        slope = 1.0 / float(geometry.tangent.value.split(":")[1])
        separation = max(0.0, x * slope)
        width = STANDARD_GAUGE_MM + 300.0 + separation * 1.3
        with BuildPart() as p:
            with BuildSketch():
                Rectangle(260.0, width, align=(Align.CENTER, Align.CENTER))
            extrude(amount=200.0)
        s = p.part.locate(Location((x, separation / 2.0, -200.0)))
        s.color = COLOR_SLEEPER
        s.label = "Sleeper"
        parts.append(s)
    return Compound(label="Sleepers", children=parts)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def turnout(
    tangent: TurnoutTangent = TurnoutTangent.T_1_9,
) -> Compound:
    """Full parametric turnout assembly for one of the three tangent
    classes."""
    geometry = CATALOGUE[tangent]

    parts: list[Part | Compound] = []

    # Sleepers first (lowest z).
    parts.append(_sleepers(geometry))

    # Two straight rails on standard gauge.
    parts.append(_straight_rail(geometry.total_length_mm, -STANDARD_GAUGE_MM / 2.0))
    parts.append(_straight_rail(geometry.total_length_mm, +STANDARD_GAUGE_MM / 2.0))

    # Diverging rails: outer diverges; inner is the stock rail and
    # stays on the straight. Approximate with one diverging arc from
    # the outer straight rail's start.
    parts.append(_diverging_rail(geometry, from_y_mm=+STANDARD_GAUGE_MM / 2.0))

    # Switch blade on the diverging side.
    parts.append(_switch_blade(geometry, y_mm=+STANDARD_GAUGE_MM / 2.0 - 60.0))

    # Crossing.
    parts.append(_crossing(geometry))

    return Compound(
        label=f"Turnout ({tangent.value}, r={geometry.diverging_radius_m:.0f} m)",
        children=parts,
    )


def turnout_footprint_mm(
    tangent: TurnoutTangent = TurnoutTangent.T_1_9,
) -> tuple[float, float]:
    """Plan-view bounding footprint `(length, width)` in mm — used by
    [osr_routing] to check that the chosen tangent fits within the
    alignment's available ROW width."""
    geometry = CATALOGUE[tangent]
    # Width: standard gauge + diverging offset at the crossing end.
    slope = 1.0 / float(tangent.value.split(":")[1])
    diverging_offset = geometry.total_length_mm * slope
    return geometry.total_length_mm, STANDARD_GAUGE_MM + 300.0 + diverging_offset


__all__ = [
    "CATALOGUE",
    "TurnoutGeometry",
    "TurnoutTangent",
    "turnout",
    "turnout_footprint_mm",
]
