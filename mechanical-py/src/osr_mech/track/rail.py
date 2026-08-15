"""Rail section (UIC 54E1 / 60E1).

The cross-section is the standard UIC straight-line polygon — head +
web + foot — which is sufficient for CAD review, clash detection, and
visualisation. Real rolling-mill profiles have filleted transitions;
deployment mills supply rail to the full UIC drawing, not to this
simplified review extrusion.
"""

from __future__ import annotations

from osr_mech.cad import (
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Color,
    Location,
    Part,
    Plane,
    Polygon,
    extrude,
)

from ..common import RAIL_GEOMETRY, RailProfile


def rail_section(profile: RailProfile = RailProfile.UIC_60E1) -> Part:
    """One-unit-length rail extrusion used for cross-section display.

    Length: 1000 mm. The section is centred on the rail-web centreline;
    top of the head sits at y = height_mm, foot sits on y = 0.
    """

    return rail_bar(profile=profile, length_mm=1000.0)


def rail_bar(
    profile: RailProfile = RailProfile.UIC_60E1,
    length_mm: float = 1000.0,
) -> Part:
    """Extruded rail bar of arbitrary length.

    Standard CWR strings are welded up from 25 m or 36 m bars, but for
    CAD review artifacts use one bar of the requested length; canopy
    and track assemblies use 1 m for layout purposes.
    """

    g = RAIL_GEOMETRY[profile]
    half_head_top = g.head_width_mm / 2.0
    half_head_base = g.head_base_width_mm / 2.0
    half_web = g.web_thickness_mm / 2.0
    half_foot_bot = g.foot_width_mm / 2.0
    half_foot_top = g.foot_top_width_mm / 2.0

    # Height bands measured from top of foot (y = 0) up to top of head.
    y_foot_top = g.foot_height_mm
    y_head_bottom = g.height_mm - g.head_height_mm
    y_head_top = g.height_mm

    # Tapered polygon tracing the full profile clockwise starting at
    # top-right of the head.
    pts = [
        (half_head_top, y_head_top),
        (half_head_top, y_head_top - 6.0),  # short vertical crown face
        (half_head_base, y_head_bottom),
        (half_web, y_head_bottom),
        (half_web, y_foot_top),
        (half_foot_top, y_foot_top),
        (half_foot_bot, 0.0),
        (-half_foot_bot, 0.0),
        (-half_foot_top, y_foot_top),
        (-half_web, y_foot_top),
        (-half_web, y_head_bottom),
        (-half_head_base, y_head_bottom),
        (-half_head_top, y_head_top - 6.0),
        (-half_head_top, y_head_top),
    ]

    with BuildPart() as bar:
        with BuildSketch(Plane.XY):
            Polygon(*pts, align=(Align.CENTER, Align.MIN))
        extrude(amount=length_mm)

    part = bar.part
    # Orient the rail along +X (traffic direction), which is what the
    # track-panel assembly expects. The BuildPart above extrudes along
    # +Z, so rotate about the X axis to bring foot onto the XY plane
    # with the length running along X.
    part = part.rotate(Axis.X, 90)
    part = part.rotate(Axis.Z, 90)
    part.color = Color(0.2, 0.2, 0.2)
    part.label = f"Rail {g.name}"
    return part


def linear_mass_kg_per_m(profile: RailProfile) -> float:
    """Published UIC linear mass — used by tests to validate volume."""

    return RAIL_GEOMETRY[profile].linear_mass_kg_per_m


__all__ = ["linear_mass_kg_per_m", "rail_bar", "rail_section"]
