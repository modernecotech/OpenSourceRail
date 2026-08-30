"""Depot massing + stall layout generator — RFC 0014 archetypes.

The generator produces a Compound per archetype containing:

- A site pad (dark gravel)
- Stabling-track centrelines (paint stripes)
- Inspection / maintenance shed (roof + walls, glass)
- Wheelset-lathe bay (main-heavy only, smaller building)
- Training-wing block (optional; main-heavy only)
- Throat turnout ladder (one turnout per stall pair; straight mainline
  entry + diverging per stall)

Scaled to match the RFC 0014 footprint per archetype + per-deployment
stall count (clamped to the per-archetype ceiling from the RFC).
"""

from __future__ import annotations

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
    Rectangle,
    extrude,
)
from osr_mech.track.turnout import TurnoutTangent, turnout


class DepotArchetype(str, Enum):
    MAIN_HEAVY = "main-heavy"
    SECONDARY_MEDIUM = "secondary-medium"
    LAYUP_MINIMAL = "layup-minimal"


@dataclass(frozen=True)
class DepotFootprint:
    """Overall site + shed envelope for one depot archetype."""

    archetype: DepotArchetype
    stall_count: int
    """Length from throat turnout to stop-block, metres."""
    site_length_m: float
    """Width across all stabling tracks + throat + service road."""
    site_width_m: float
    """Shed dimensions — length x width x eave height, metres."""
    shed_length_m: float
    shed_width_m: float
    shed_height_m: float
    """Whether a wheel-lathe bay is included."""
    has_wheel_lathe: bool
    """Whether a training-wing block is included."""
    has_training_wing: bool


CEILING = {
    DepotArchetype.MAIN_HEAVY: 20,
    DepotArchetype.SECONDARY_MEDIUM: 12,
    DepotArchetype.LAYUP_MINIMAL: 6,
}

DEFAULT_STALLS = {
    DepotArchetype.MAIN_HEAVY: 10,
    DepotArchetype.SECONDARY_MEDIUM: 8,
    DepotArchetype.LAYUP_MINIMAL: 4,
}

# Per-archetype shed dimensions (from RFC 0014 §5 + typical metro
# workshop practice).
_ARCHETYPE_DEFAULTS = {
    DepotArchetype.MAIN_HEAVY: dict(
        shed_length_m=180.0,  # 2× 90 m overhaul bays end-to-end
        shed_width_m=45.0,
        shed_height_m=12.0,
        has_wheel_lathe=True,
    ),
    DepotArchetype.SECONDARY_MEDIUM: dict(
        shed_length_m=120.0,
        shed_width_m=30.0,
        shed_height_m=10.0,
        has_wheel_lathe=False,
    ),
    DepotArchetype.LAYUP_MINIMAL: dict(
        shed_length_m=0.0,
        shed_width_m=0.0,
        shed_height_m=0.0,
        has_wheel_lathe=False,
    ),
}


# Rolling-stock physical footprint — used to size stabling-track
# length (consist + coupling margin) and stall spacing.
_STABLING_TRACK_LENGTH_M = 160.0  # accommodates up to a 6-car consist
_STABLING_TRACK_SPACING_M = 6.0  # centre-to-centre
_THROAT_LENGTH_M = 120.0  # turnout ladder from mainline

COLOR_GRAVEL = Color(0.28, 0.27, 0.24)
COLOR_PAINT = Color(0.98, 0.98, 0.95)
COLOR_SHED_WALL = Color(0.82, 0.82, 0.85)
COLOR_SHED_ROOF = Color(0.32, 0.40, 0.55)
COLOR_SHED_GLAZING = Color(0.55, 0.75, 0.90, 0.5)
COLOR_WHEEL_LATHE = Color(0.18, 0.22, 0.32)
COLOR_TRAINING = Color(0.70, 0.55, 0.35)
COLOR_CHARGER = Color(0.85, 0.50, 0.15)


def depot_footprint(
    archetype: DepotArchetype,
    stalls: int | None = None,
    with_training_wing: bool = False,
) -> DepotFootprint:
    """Size a depot of the given archetype for `stalls` stabling tracks
    (clamped to the RFC 0014 per-archetype ceiling). If `stalls` is
    None, use the reference default; the catalogue maximum remains a clamp."""
    ceiling = CEILING[archetype]
    n = DEFAULT_STALLS[archetype] if stalls is None else max(1, min(stalls, ceiling))
    defaults = _ARCHETYPE_DEFAULTS[archetype]
    site_width = max(
        n * _STABLING_TRACK_SPACING_M + 20.0, defaults["shed_width_m"] + 20.0
    )
    site_length = (
        _THROAT_LENGTH_M + _STABLING_TRACK_LENGTH_M + defaults["shed_length_m"] + 40.0
    )
    return DepotFootprint(
        archetype=archetype,
        stall_count=n,
        site_length_m=site_length,
        site_width_m=site_width,
        shed_length_m=defaults["shed_length_m"],
        shed_width_m=defaults["shed_width_m"],
        shed_height_m=defaults["shed_height_m"],
        has_wheel_lathe=defaults["has_wheel_lathe"],
        has_training_wing=(
            with_training_wing and archetype == DepotArchetype.MAIN_HEAVY
        ),
    )


def _site_pad(fp: DepotFootprint) -> Part:
    """A thin pad representing the gravel site surface."""
    L = fp.site_length_m * 1000.0
    W = fp.site_width_m * 1000.0
    with BuildPart() as p:
        with BuildSketch():
            Rectangle(L, W, align=(Align.CENTER, Align.CENTER))
        extrude(amount=200.0)
    pad = p.part.locate(Location((L / 2.0, 0.0, -200.0)))
    pad.color = COLOR_GRAVEL
    pad.label = "Site pad (gravel)"
    return pad


def _stabling_tracks(fp: DepotFootprint) -> list[Part]:
    """Paint-stripe the centreline of each stabling track."""
    out: list[Part] = []
    track_len = _STABLING_TRACK_LENGTH_M * 1000.0
    track_start_x = (_THROAT_LENGTH_M + fp.shed_length_m + 20.0) * 1000.0
    y0 = -(fp.stall_count - 1) * _STABLING_TRACK_SPACING_M * 1000.0 / 2.0
    for i in range(fp.stall_count):
        y = y0 + i * _STABLING_TRACK_SPACING_M * 1000.0
        with BuildPart() as p:
            with BuildSketch():
                Rectangle(track_len, 200.0, align=(Align.MIN, Align.CENTER))
            extrude(amount=20.0)
        t = p.part.locate(Location((track_start_x, y, 0.0)))
        t.color = COLOR_PAINT
        t.label = f"Stabling track {i + 1}"
        out.append(t)
    return out


def throat_turnout_count(stall_count: int) -> int:
    """One 1:9 throat turnout for each pair of stabling tracks."""

    return (max(1, stall_count) + 1) // 2


def _throat_turnouts(fp: DepotFootprint) -> list[Compound]:
    """Place the controlled 1:9 turnout assemblies in the throat envelope."""

    count = throat_turnout_count(fp.stall_count)
    available_x = _THROAT_LENGTH_M * 1000.0 - 27_000.0
    x_pitch = available_x / max(1, count - 1)
    first_track_y = -(fp.stall_count - 1) * _STABLING_TRACK_SPACING_M * 1000.0 / 2.0
    turnouts: list[Compound] = []
    for index in range(count):
        first_stall = min(index * 2, fp.stall_count - 1)
        second_stall = min(first_stall + 1, fp.stall_count - 1)
        pair_y = first_track_y + (first_stall + second_stall) * _STABLING_TRACK_SPACING_M * 1000.0 / 2.0
        assembly = turnout(TurnoutTangent.T_1_9).locate(
            Location((index * x_pitch, pair_y, 0.0))
        )
        assembly.label = f"Depot throat turnout {index + 1} (1:9)"
        turnouts.append(assembly)
    return turnouts


def _shed(fp: DepotFootprint) -> list[Part]:
    """Maintenance shed — walls + roof box. Only if the archetype
    has one."""
    if fp.shed_length_m <= 0.0:
        return []
    L = fp.shed_length_m * 1000.0
    W = fp.shed_width_m * 1000.0
    H = fp.shed_height_m * 1000.0

    out: list[Part] = []
    # Walls: build a hollow box by subtracting an inner box.
    with BuildPart() as shell:
        with BuildSketch():
            Rectangle(L, W, align=(Align.CENTER, Align.CENTER))
        extrude(amount=H)
    with BuildPart() as inner:
        with BuildSketch():
            Rectangle(L - 400.0, W - 400.0, align=(Align.CENTER, Align.CENTER))
        extrude(amount=H - 400.0)
    walls = shell.part - inner.part.locate(Location((0.0, 0.0, 200.0)))
    walls = walls.locate(
        Location((_THROAT_LENGTH_M * 1000.0 + L / 2.0, 0.0, 0.0))
    )
    walls.color = COLOR_SHED_WALL
    walls.label = "Shed walls"
    out.append(walls)

    # Roof: shallow pitched metal plane (represented as a flat
    # rectangle 300 mm thick, slightly darker than the walls).
    with BuildPart() as roof:
        with BuildSketch():
            Rectangle(L + 1000.0, W + 1000.0, align=(Align.CENTER, Align.CENTER))
        extrude(amount=300.0)
    r = roof.part.locate(
        Location((_THROAT_LENGTH_M * 1000.0 + L / 2.0, 0.0, H))
    )
    r.color = COLOR_SHED_ROOF
    r.label = "Shed roof"
    out.append(r)

    # Glazing strip along the two long walls at 60–70 % height.
    glaze_h = 2_000.0
    glaze_z = H * 0.6
    for y_sign in (-1.0, 1.0):
        with BuildPart() as g:
            with BuildSketch():
                Rectangle(L - 2_000.0, 80.0, align=(Align.CENTER, Align.CENTER))
            extrude(amount=glaze_h)
        glaze = g.part.locate(
            Location(
                (
                    _THROAT_LENGTH_M * 1000.0 + L / 2.0,
                    y_sign * W / 2.0,
                    glaze_z,
                )
            )
        )
        glaze.color = COLOR_SHED_GLAZING
        glaze.label = "Shed clerestory glazing"
        out.append(glaze)

    return out


def _wheel_lathe(fp: DepotFootprint) -> list[Part]:
    """A small dedicated building for the wheelset lathe — `main-
    heavy` archetype only, per RFC 0014."""
    if not fp.has_wheel_lathe:
        return []
    L, W, H = 30_000.0, 15_000.0, 7_000.0
    with BuildPart() as b:
        with BuildSketch():
            Rectangle(L, W, align=(Align.CENTER, Align.CENTER))
        extrude(amount=H)
    p = b.part.locate(
        Location(
            (
                _THROAT_LENGTH_M * 1000.0 + fp.shed_length_m * 1000.0 / 2.0,
                fp.shed_width_m * 1000.0 / 2.0 + W / 2.0 + 5_000.0,
                0.0,
            )
        )
    )
    p.color = COLOR_WHEEL_LATHE
    p.label = "Wheel-lathe bay"
    return [p]


def _chargers(fp: DepotFootprint) -> list[Part]:
    """Plug-in fast-charger cabinet per stabling track (RFC 0021 §6.1).

    Each cabinet is a wall-mounted 600 VDC / 210 kW dock at the stop-
    block end of its stall, roughly 1.8 m tall, with a suspended
    flexible cable that reaches the +Y side of the parked trainset
    to the car-level charge receptacle (400 mm above rail head)."""
    out: list[Part] = []
    track_start_x = (_THROAT_LENGTH_M + fp.shed_length_m + 20.0) * 1000.0
    track_len = _STABLING_TRACK_LENGTH_M * 1000.0
    # Place the cabinet at the stop-block end of each stall (+X extreme).
    y0 = -(fp.stall_count - 1) * _STABLING_TRACK_SPACING_M * 1000.0 / 2.0
    for i in range(fp.stall_count):
        y = y0 + i * _STABLING_TRACK_SPACING_M * 1000.0
        with BuildPart() as p:
            with BuildSketch():
                Rectangle(800.0, 400.0, align=(Align.CENTER, Align.CENTER))
            extrude(amount=1_800.0)
        cab = p.part.locate(
            Location(
                (
                    track_start_x + track_len + 800.0,
                    y + 1_500.0,  # offset to the +Y side of the track
                    0.0,
                )
            )
        )
        cab.color = COLOR_CHARGER
        cab.label = f"Plug-in charger cabinet (210 kW DC)"
        out.append(cab)
    return out


def _training_wing(fp: DepotFootprint) -> list[Part]:
    """Operations-training block — dispatcher-console simulators,
    maintenance workshops, recovery-mode-crew briefing rooms.
    Optional on `main-heavy`. OSR is driverless (RFC 0015): there
    are no revenue-service drivers and therefore no driver-training
    simulators."""
    if not fp.has_training_wing:
        return []
    L, W, H = 30_000.0, 12_000.0, 5_500.0
    with BuildPart() as b:
        with BuildSketch():
            Rectangle(L, W, align=(Align.CENTER, Align.CENTER))
        extrude(amount=H)
    p = b.part.locate(
        Location(
            (
                _THROAT_LENGTH_M * 1000.0 / 2.0,
                -(fp.site_width_m * 1000.0 / 2.0 - W / 2.0 - 2_000.0),
                0.0,
            )
        )
    )
    p.color = COLOR_TRAINING
    p.label = "Training wing (dispatcher + maintainer + recovery crew)"
    return [p]


def depot_layout(
    archetype: DepotArchetype = DepotArchetype.MAIN_HEAVY,
    stalls: int | None = None,
    with_training_wing: bool = False,
) -> Compound:
    """Full depot massing assembly for one archetype."""
    fp = depot_footprint(archetype, stalls, with_training_wing)
    parts: list[Part | Compound] = []
    parts.append(_site_pad(fp))
    parts.extend(_throat_turnouts(fp))
    parts.extend(_stabling_tracks(fp))
    parts.extend(_chargers(fp))
    parts.extend(_shed(fp))
    parts.extend(_wheel_lathe(fp))
    parts.extend(_training_wing(fp))
    return Compound(
        label=(
            f"Depot ({archetype.value}, {fp.stall_count} stalls, "
            f"{fp.site_length_m:.0f} × {fp.site_width_m:.0f} m)"
        ),
        children=parts,
    )


__all__ = [
    "CEILING",
    "DEFAULT_STALLS",
    "DepotArchetype",
    "DepotFootprint",
    "depot_footprint",
    "depot_layout",
    "throat_turnout_count",
]
