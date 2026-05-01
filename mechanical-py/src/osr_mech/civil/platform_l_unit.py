"""Precast platform L-unit — the platform edge + rear kerb in one piece.

Each L-unit is 3 m long, cast at the same yard as the U-girder,
trucked to site, dropped onto a compacted sub-base, and grouted. A
light-metro platform uses full units plus a short closure pour at
the non-critical rear edge. No formwork, no wet concrete at the
rail-side edge, no structural design per station.

Cross-section:
- Vertical wall (platform edge): 1100 mm tall × 150 mm thick, sitting
  at the rail-side.
- Horizontal deck: 2500 mm wide × 200 mm thick, tying back from the
  wall into the platform surface.

The operator-side surface of the wall is at the nominal platform-edge
line (platform-to-rail gap per RFC 0010 §7).
"""

from __future__ import annotations

from build123d import (
    Align,
    BuildPart,
    BuildSketch,
    Color,
    Part,
    Plane,
    Polygon,
    extrude,
)

UNIT_LENGTH_MM = 3000.0
WALL_HEIGHT_MM = 1100.0
WALL_THICKNESS_MM = 150.0
DECK_WIDTH_MM = 2500.0
DECK_THICKNESS_MM = 200.0


def platform_l_unit() -> Part:
    """One precast L-unit (3 m long).

    Origin: outer rail-side corner at (0, 0, 0). Wall extends up in
    +Z; deck extends back in +Y. Length extends along +X.
    """

    # L-shaped cross-section as a six-point polygon, in the YZ plane.
    pts = [
        (0.0, 0.0),
        (WALL_THICKNESS_MM, 0.0),
        (WALL_THICKNESS_MM, WALL_HEIGHT_MM - DECK_THICKNESS_MM),
        (DECK_WIDTH_MM, WALL_HEIGHT_MM - DECK_THICKNESS_MM),
        (DECK_WIDTH_MM, WALL_HEIGHT_MM),
        (0.0, WALL_HEIGHT_MM),
    ]

    with BuildPart() as lu:
        with BuildSketch(Plane.YZ):
            Polygon(*pts, align=(Align.MIN, Align.MIN))
        extrude(amount=UNIT_LENGTH_MM)

    p = lu.part
    p.color = Color(0.8, 0.8, 0.78)
    p.label = "Platform L-unit"
    return p


def units_per_platform(platform_length_m: float) -> int:
    """How many L-units cover a platform of the requested length."""
    import math

    return int(math.ceil(platform_length_m * 1000.0 / UNIT_LENGTH_MM))


__all__ = [
    "DECK_THICKNESS_MM",
    "DECK_WIDTH_MM",
    "UNIT_LENGTH_MM",
    "WALL_HEIGHT_MM",
    "WALL_THICKNESS_MM",
    "platform_l_unit",
    "units_per_platform",
]
