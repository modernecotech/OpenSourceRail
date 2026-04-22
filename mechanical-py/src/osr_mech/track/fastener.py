"""Pandrol-style elastic rail fastener — shoulder + clip + pad + insulator.

Every rail-seat on every sleeper has a fastener on each side (4 per
sleeper). The real Pandrol clip is a cold-formed spring-steel wire;
the STEP artifact approximates it as a curved rod, which is fine for
clearance + assembly purposes. Vendors supply the actual clip to the
Pandrol datasheet.
"""

from __future__ import annotations

from build123d import (
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    Color,
    Compound,
    Location,
    Part,
    Plane,
    Polygon,
    Rectangle,
    extrude,
)


SHOULDER_WIDTH_MM = 60.0
SHOULDER_DEPTH_MM = 40.0
SHOULDER_HEIGHT_MM = 35.0

PAD_WIDTH_MM = 160.0
PAD_DEPTH_MM = 160.0
PAD_THICKNESS_MM = 10.0

CLIP_WIRE_DIA_MM = 18.0
CLIP_HEIGHT_MM = 30.0


def _rail_pad() -> Part:
    """Rubber rail pad — rectangular slab between rail foot and sleeper."""
    with BuildPart() as pad:
        with BuildSketch():
            Rectangle(PAD_WIDTH_MM, PAD_DEPTH_MM, align=(Align.CENTER, Align.CENTER))
        extrude(amount=PAD_THICKNESS_MM)
    p = pad.part
    p.color = Color(0.15, 0.15, 0.15)
    p.label = "Rail pad (EVA)"
    return p


def _shoulder() -> Part:
    """Cast-iron shoulder embedded in the sleeper — one per clip side."""
    with BuildPart() as sh:
        with BuildSketch():
            Rectangle(SHOULDER_WIDTH_MM, SHOULDER_DEPTH_MM, align=(Align.CENTER, Align.CENTER))
        extrude(amount=SHOULDER_HEIGHT_MM)
    p = sh.part
    p.color = Color(0.4, 0.4, 0.45)
    p.label = "Shoulder"
    return p


def _clip_rod() -> Part:
    """Pandrol-style spring clip — simplified as an extruded curved rod."""
    with BuildPart() as clip:
        with BuildSketch():
            Circle(CLIP_WIRE_DIA_MM / 2.0)
        extrude(amount=SHOULDER_WIDTH_MM)
    p = clip.part
    # Orient the rod so it spans across the rail foot.
    p = p.rotate(Axis.Y, 90)
    p = p.translate((-SHOULDER_WIDTH_MM / 2.0, 0.0, PAD_THICKNESS_MM + CLIP_HEIGHT_MM / 2.0))
    p.color = Color(0.75, 0.2, 0.1)
    p.label = "Pandrol clip"
    return p


def fastener_assembly() -> Compound:
    """One fastener kit as placed at a rail-seat: pad + two shoulders +
    two clips. Rail foot sits on the pad; shoulders flank the rail foot
    at the pad's long edges; clips hook over the rail foot into the
    shoulder grooves.

    Origin: centre of the rail-foot bottom face. The caller places this
    at the sleeper rail-seat.
    """

    parts = []

    pad = _rail_pad()
    parts.append(pad)

    gap = 95.0  # half-gap between rail foot centre and shoulder centre
    sh1 = _shoulder().translate((0.0, -gap, PAD_THICKNESS_MM))
    sh2 = _shoulder().translate((0.0, gap, PAD_THICKNESS_MM))
    parts.extend([sh1, sh2])

    c1 = _clip_rod().translate((0.0, -gap, 0.0))
    c2 = _clip_rod().translate((0.0, gap, 0.0))
    parts.extend([c1, c2])

    c = Compound(label="Fastener assembly", children=parts)
    return c


__all__ = [
    "PAD_DEPTH_MM",
    "PAD_THICKNESS_MM",
    "PAD_WIDTH_MM",
    "fastener_assembly",
]
