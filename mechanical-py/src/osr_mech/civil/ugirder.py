"""Precast U-girder — the RFC 0011 reference elevated span.

A U-girder is a U-shaped precast concrete section that supports one
track per girder. It ships in one piece on a low-loader trailer; two
parallel girders drop onto each shared double-track pier cap, and the U's walls form both the parapet and the
ballast retainer — so there is no separate parapet to erect on site.

RFC 0011 §5 ships three span sizes from a single mould family:
- 20 m: standard urban viaduct.
- 25 m: longer spans across road junctions.
- 30 m: water-crossing maximum (anything longer goes to a truss bridge
  outside this catalogue).

The whole viaduct catalogue is driven by one precast yard. Every
deployment gets the same girder, the same moulds, the same QC.
"""

from __future__ import annotations

from osr_mech.cad import (
    Align,
    BuildPart,
    BuildSketch,
    Color,
    Part,
    Plane,
    Polygon,
    extrude,
)

WALL_THICKNESS_MM = 200.0
FLOOR_THICKNESS_MM = 250.0
INTERNAL_WIDTH_MM = 3500.0
INTERNAL_HEIGHT_MM = 1200.0
EXTERNAL_WIDTH_MM = INTERNAL_WIDTH_MM + 2 * WALL_THICKNESS_MM
EXTERNAL_HEIGHT_MM = INTERNAL_HEIGHT_MM + FLOOR_THICKNESS_MM


def u_girder(span_m: float = 25.0) -> Part:
    """Precast U-girder of the requested span.

    Parameters
    ----------
    span_m:
        Centre-to-centre pier span, in metres. Canonical sizes are 20,
        25, and 30; other values in the range 15–32 m are accepted but
        flag the structural design-check that the deployment partner
        must run for a non-catalogue span.
    """

    if not (15.0 <= span_m <= 32.0):
        raise ValueError(
            f"span_m={span_m} outside catalogue envelope (15 m .. 32 m); "
            "non-catalogue spans require a structural engineer design check"
        )

    length_mm = span_m * 1000.0

    half_ext = EXTERNAL_WIDTH_MM / 2.0
    half_int = INTERNAL_WIDTH_MM / 2.0

    # U-shaped cross-section traced clockwise from bottom-left.
    pts = [
        (-half_ext, 0.0),
        (half_ext, 0.0),
        (half_ext, EXTERNAL_HEIGHT_MM),
        (half_int, EXTERNAL_HEIGHT_MM),
        (half_int, FLOOR_THICKNESS_MM),
        (-half_int, FLOOR_THICKNESS_MM),
        (-half_int, EXTERNAL_HEIGHT_MM),
        (-half_ext, EXTERNAL_HEIGHT_MM),
    ]

    with BuildPart() as girder:
        with BuildSketch(Plane.XY):
            Polygon(*pts, align=(Align.CENTER, Align.MIN))
        extrude(amount=length_mm)

    result = girder.part
    result.color = Color(0.72, 0.72, 0.70)
    result.label = f"U-girder {span_m:.0f} m"
    return result


def approx_mass_kg(span_m: float, concrete_density_kg_per_m3: float = 2500.0) -> float:
    """Approximate mass of a U-girder, based on cross-section area × length.

    Used by tests to validate the model volume against a published
    reference. Real RFC 0011 mass includes pre-stressing strands +
    rebar, which bump the figure by ~3 %; the test tolerance absorbs
    that.
    """
    a_outer = (EXTERNAL_WIDTH_MM / 1000.0) * (EXTERNAL_HEIGHT_MM / 1000.0)
    a_cavity = (INTERNAL_WIDTH_MM / 1000.0) * (INTERNAL_HEIGHT_MM / 1000.0)
    a_concrete = a_outer - a_cavity
    return a_concrete * span_m * concrete_density_kg_per_m3


__all__ = [
    "EXTERNAL_HEIGHT_MM",
    "EXTERNAL_WIDTH_MM",
    "INTERNAL_HEIGHT_MM",
    "INTERNAL_WIDTH_MM",
    "WALL_THICKNESS_MM",
    "approx_mass_kg",
    "u_girder",
]
