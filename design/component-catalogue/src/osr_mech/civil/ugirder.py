"""Planning geometry for the OSR Rapid Viaduct U-trough family.

The standard product is a full-span, prestressed, single-track concrete
U-trough. ``u_girder_envelope`` is deliberately only a clearance and
quantity envelope: it is not a reinforcement or prestressing design.
``u_girder_structural_placeholder`` adds the feature zones that a supplier
model must resolve without pretending that their dimensions are final.
"""

from __future__ import annotations

from osr_mech.cad import (
    Align,
    Box,
    BuildPart,
    BuildSketch,
    Color,
    Compound,
    Location,
    Part,
    Plane,
    Polygon,
    extrude,
)
from osr_mech.clearance import reference_dynamic_width_mm

WALL_THICKNESS_MM = 200.0
FLOOR_THICKNESS_MM = 250.0

# Civil CAD convention: +X traffic/chainage, +Y transverse, +Z vertical.
# Width is governed by the controlled train-plus-egress envelope, not gauge.
DYNAMIC_TRAIN_WIDTH_MM = reference_dynamic_width_mm()
CLEAR_WALKWAY_WIDTH_MM = 1_000.0
OPPOSITE_SIDE_CLEARANCE_MM = 250.0
KINEMATIC_AND_CONSTRUCTION_ALLOWANCE_MM = 220.0
MIN_REQUIRED_INTERNAL_WIDTH_MM = (
    DYNAMIC_TRAIN_WIDTH_MM
    + CLEAR_WALKWAY_WIDTH_MM
    + OPPOSITE_SIDE_CLEARANCE_MM
    + KINEMATIC_AND_CONSTRUCTION_ALLOWANCE_MM
)
# 4.72 m preserves the 220 mm sway/tolerance reserve while also providing
# the 261 mm chord allowance of a straight U25 on the preferred 300 m curve.
INTERNAL_WIDTH_MM = 4_720.0

# Local rail plinths do not consume a 220 mm full-width topping. This wall
# datum retains 1.4 m above the 180 mm integrated escape ledge.
INTERNAL_HEIGHT_MM = 1_600.0
EXTERNAL_WIDTH_MM = INTERNAL_WIDTH_MM + 2 * WALL_THICKNESS_MM
EXTERNAL_HEIGHT_MM = INTERNAL_HEIGHT_MM + FLOOR_THICKNESS_MM

PRIMARY_SPAN_M = 25.0
CLOSURE_SPAN_M = 20.0
MAX_FULL_SPAN_M = 30.0
MIN_FULL_SPAN_M = 20.0
CATALOGUE_SPANS_M = (CLOSURE_SPAN_M, PRIMARY_SPAN_M)

ESCAPE_LEDGE_WIDTH_MM = 1_000.0
ESCAPE_LEDGE_HEIGHT_MM = 180.0
UPPER_FLANGE_ZONE_WIDTH_MM = 300.0
END_DIAPHRAGM_ZONE_LENGTH_MM = 650.0


def _check_span(span_m: float) -> None:
    if not (MIN_FULL_SPAN_M <= span_m <= MAX_FULL_SPAN_M):
        raise ValueError(
            f"span_m={span_m:g} outside full-span U-trough envelope "
            f"({MIN_FULL_SPAN_M:g} m .. {MAX_FULL_SPAN_M:g} m); use a "
            "segmental or separately engineered special span"
        )


def u_girder_envelope(span_m: float = PRIMARY_SPAN_M) -> Part:
    """Return the geometric clearance/quantity extrusion for one U-trough.

    Values between 20 m and 30 m can be explored, but only 20 m and 25 m are
    released catalogue lengths. The 30 m option requires a project-specific
    lifting, transport-route, launcher/crane, and structural release.
    """

    _check_span(span_m)
    return _u_trough_extrusion(span_m * 1000.0, f"U-trough clearance envelope {span_m:g} m")


def _u_trough_extrusion(length_mm: float, label: str) -> Part:
    """Extrude the common cross-section along +X for full or match-cast units."""

    if length_mm <= 0.0:
        raise ValueError("U-trough length must be positive")
    half_ext = EXTERNAL_WIDTH_MM / 2.0
    half_int = INTERNAL_WIDTH_MM / 2.0

    # Constant thickness is an envelope only; final webs/floor require
    # haunches, prestressing, reinforcement, and three-dimensional analysis.
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
        # The polygon coordinates are (Y transverse, Z vertical); the YZ
        # plane normal is +X, matching every track/slab catalogue component.
        with BuildSketch(Plane.YZ):
            Polygon(*pts, align=(Align.CENTER, Align.MIN))
        extrude(amount=length_mm)

    result = girder.part
    result.color = Color(0.72, 0.72, 0.70)
    result.label = label
    return result


def u_girder_segment_envelope(length_m: float) -> Part:
    """One unreleased match-cast segment using the controlled cross-section."""

    return _u_trough_extrusion(
        length_m * 1000.0,
        f"Match-cast U-trough segment envelope {length_m:g} m",
    )


def u_girder_structural_placeholder(span_m: float = PRIMARY_SPAN_M) -> Compound:
    """Add visible supplier-design zones to the planning envelope.

    These are coordination placeholders. Their reinforcement, prestressing,
    anchorage, lifting, bearing, drainage, and derailment details are not
    released structural dimensions.
    """

    _check_span(span_m)
    length_mm = span_m * 1000.0
    concrete = Color(0.66, 0.66, 0.64)
    interface = Color(0.30, 0.45, 0.58, 0.65)
    half_int = INTERNAL_WIDTH_MM / 2.0
    parts: list[Part] = [u_girder_envelope(span_m)]

    ledge = Box(length_mm, ESCAPE_LEDGE_WIDTH_MM, ESCAPE_LEDGE_HEIGHT_MM).locate(
        Location(
            (
                length_mm / 2.0,
                -half_int + ESCAPE_LEDGE_WIDTH_MM / 2.0,
                FLOOR_THICKNESS_MM + ESCAPE_LEDGE_HEIGHT_MM / 2.0,
            )
        )
    )
    ledge.label = "Integrated escape-ledge structural zone"
    ledge.color = concrete
    parts.append(ledge)

    for side in (-1.0, 1.0):
        flange = Box(length_mm, UPPER_FLANGE_ZONE_WIDTH_MM, 250.0).locate(
            Location(
                (
                    length_mm / 2.0,
                    side * (EXTERNAL_WIDTH_MM / 2.0 - UPPER_FLANGE_ZONE_WIDTH_MM / 2.0),
                    EXTERNAL_HEIGHT_MM - 125.0,
                )
            )
        )
        flange.label = "Upper flange and screen-socket design zone"
        flange.color = concrete
        parts.append(flange)

    for x_mm in (
        END_DIAPHRAGM_ZONE_LENGTH_MM / 2.0,
        length_mm - END_DIAPHRAGM_ZONE_LENGTH_MM / 2.0,
    ):
        diaphragm = Box(
            END_DIAPHRAGM_ZONE_LENGTH_MM,
            EXTERNAL_WIDTH_MM,
            EXTERNAL_HEIGHT_MM,
        ).locate(Location((x_mm, 0.0, EXTERNAL_HEIGHT_MM / 2.0)))
        diaphragm.label = "End diaphragm, bearing, jacking, and anchorage zone"
        diaphragm.color = interface
        parts.append(diaphragm)

    for y_mm, label in (
        (0.0, "Drainage and replaceable-scuppers corridor"),
        (half_int - 350.0, "Cable, earthing, and communications corridor"),
    ):
        corridor = Box(length_mm, 300.0, 120.0).locate(
            Location((length_mm / 2.0, y_mm, FLOOR_THICKNESS_MM + 60.0))
        )
        corridor.label = label
        corridor.color = interface
        parts.append(corridor)

    return Compound(label=f"OSR-U structural feature placeholder ({span_m:g} m)", children=parts)


def u_girder(span_m: float = PRIMARY_SPAN_M) -> Part:
    """Backward-compatible name for the planning envelope."""

    return u_girder_envelope(span_m)


def approx_mass_kg(span_m: float, concrete_density_kg_per_m3: float = 2500.0) -> float:
    """Approximate bare envelope mass from section area times length."""

    _check_span(span_m)
    a_outer = (EXTERNAL_WIDTH_MM / 1000.0) * (EXTERNAL_HEIGHT_MM / 1000.0)
    a_cavity = (INTERNAL_WIDTH_MM / 1000.0) * (INTERNAL_HEIGHT_MM / 1000.0)
    return (a_outer - a_cavity) * span_m * concrete_density_kg_per_m3


def section_area_m2() -> float:
    """Constant-thickness planning section area used by the quantity model."""

    a_outer = (EXTERNAL_WIDTH_MM / 1000.0) * (EXTERNAL_HEIGHT_MM / 1000.0)
    a_cavity = (INTERNAL_WIDTH_MM / 1000.0) * (INTERNAL_HEIGHT_MM / 1000.0)
    return a_outer - a_cavity


__all__ = [
    "CATALOGUE_SPANS_M",
    "CLEAR_WALKWAY_WIDTH_MM",
    "CLOSURE_SPAN_M",
    "DYNAMIC_TRAIN_WIDTH_MM",
    "ESCAPE_LEDGE_HEIGHT_MM",
    "ESCAPE_LEDGE_WIDTH_MM",
    "EXTERNAL_HEIGHT_MM",
    "EXTERNAL_WIDTH_MM",
    "FLOOR_THICKNESS_MM",
    "INTERNAL_HEIGHT_MM",
    "INTERNAL_WIDTH_MM",
    "KINEMATIC_AND_CONSTRUCTION_ALLOWANCE_MM",
    "MAX_FULL_SPAN_M",
    "MIN_REQUIRED_INTERNAL_WIDTH_MM",
    "OPPOSITE_SIDE_CLEARANCE_MM",
    "PRIMARY_SPAN_M",
    "WALL_THICKNESS_MM",
    "approx_mass_kg",
    "u_girder",
    "u_girder_envelope",
    "u_girder_segment_envelope",
    "u_girder_structural_placeholder",
    "section_area_m2",
]
