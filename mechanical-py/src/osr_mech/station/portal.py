"""Steel portal frame — the single station-canopy bay.

Two hot-dip-galvanised universal-column sections stand on pad footings,
with a trussed rafter bridging between them. Bolted connections
everywhere; no on-site welding. One lorry takes 12 bays flat-packed.

Every element is a standard EN 10365 steel profile so the deployment
partner can source material from any European, Indian, or Chinese
mill without special rolling:

- Columns: HEA 200 (W 200 × 200 mm, 42.3 kg/m).
- Rafter: HEA 180 (W 180 × 180 mm, 35.5 kg/m).
- Bracing: SHS 100 × 100 × 6 mm (18.0 kg/m).

The truss rafter gives the 3.5 m cantilever over the platform that
keeps columns out of the passenger circulation zone — columns sit at
the platform rear edge and the roof extends forward over the platform.

Bay spacing: 6.0 m. Clear height under rafter: 3.0 m.
Overall height to ridge: 4.2 m (with 1:15 mono-pitch roof).
"""

from __future__ import annotations

from osr_mech.cad import (
    Align,
    Axis,
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

# Standard bay.
BAY_SPACING_MM = 6000.0
PLATFORM_DEPTH_MM = 3500.0  # platform edge → rear column
CLEAR_HEIGHT_MM = 3000.0
ROOF_PITCH = 1.0 / 15.0  # mono-pitch, 1:15 fall

# Column / rafter nominals.
COLUMN_SIZE_MM = 200.0
RAFTER_SIZE_MM = 180.0
BRACE_SIZE_MM = 100.0


def _column() -> Part:
    """HEA 200 column — represented as a rectangular tube for visualisation."""
    with BuildPart() as col:
        with BuildSketch():
            Rectangle(COLUMN_SIZE_MM, COLUMN_SIZE_MM, align=(Align.CENTER, Align.CENTER))
        extrude(amount=CLEAR_HEIGHT_MM + 200.0)  # 200 mm embedded base plate zone
    p = col.part
    p.color = Color(0.85, 0.85, 0.88)
    p.label = "Column (HEA 200)"
    return p


def _rafter(length_mm: float) -> Part:
    """HEA 180 rafter spanning platform width."""
    with BuildPart() as r:
        with BuildSketch():
            Rectangle(RAFTER_SIZE_MM, RAFTER_SIZE_MM, align=(Align.CENTER, Align.CENTER))
        extrude(amount=length_mm)
    p = r.part
    p = p.rotate(Axis.X, 90)
    p.color = Color(0.85, 0.85, 0.88)
    p.label = "Rafter (HEA 180)"
    return p


def _brace(length_mm: float) -> Part:
    """SHS 100 cross-brace."""
    with BuildPart() as b:
        with BuildSketch():
            Rectangle(BRACE_SIZE_MM, BRACE_SIZE_MM, align=(Align.CENTER, Align.CENTER))
        extrude(amount=length_mm)
    p = b.part
    p.color = Color(0.7, 0.7, 0.75)
    p.label = "Brace (SHS 100)"
    return p


def portal_frame() -> Compound:
    """One bay portal frame + rafter + bracing.

    Origin at the platform-edge side, column base. +X is along-track
    (bay runs from 0 .. BAY_SPACING_MM), +Y is across-platform toward
    the back wall.
    """

    parts: list[Part | Compound] = []

    # Two columns per bay (front + rear), at x = 0 and x = BAY_SPACING_MM.
    # Bay is bounded by the NEXT bay's columns on the other end, so each
    # portal bay contributes its leading pair of columns only. The final
    # bay of the canopy adds the trailing pair via a sentinel.
    for x in (0.0,):
        # Rear column at y = PLATFORM_DEPTH_MM.
        c_rear = _column().translate(
            (x, PLATFORM_DEPTH_MM - COLUMN_SIZE_MM / 2.0, 0.0)
        )
        parts.append(c_rear)

        # Optional front column: we omit it to keep the platform edge
        # unobstructed. The rafter cantilevers instead.

    # Rafter at top of column, cantilevered from the rear column out
    # over the platform.
    rafter_z = CLEAR_HEIGHT_MM
    r = _rafter(PLATFORM_DEPTH_MM)
    # Place rafter so it starts at the rear column and runs forward (-Y).
    r = r.translate((0.0, 0.0, rafter_z))
    parts.append(r)

    # Diagonal brace from rear-column top back down into a haunch at
    # the rafter mid-span; keeps sway stiffness in the across-track
    # direction without needing a moment connection at the column base.
    # Simplified as a short cross-tube.
    import math

    brace_len = math.hypot(PLATFORM_DEPTH_MM / 2.0, CLEAR_HEIGHT_MM / 2.0)
    b = _brace(brace_len)
    # Not rotated into the diagonal: the review model uses an
    # axial simplification. A real structural drawing would show the
    # exact haunch angle.
    b = b.translate((0.0, PLATFORM_DEPTH_MM / 2.0, CLEAR_HEIGHT_MM / 2.0))
    parts.append(b)

    return Compound(label="Portal frame bay", children=parts)


__all__ = [
    "BAY_SPACING_MM",
    "CLEAR_HEIGHT_MM",
    "PLATFORM_DEPTH_MM",
    "portal_frame",
]
