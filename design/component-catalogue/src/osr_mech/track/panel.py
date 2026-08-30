"""Assembled track panel — two rails + N sleepers + fastener kits.

Used for visualising a span of track in the correct gauge, and for
clash-checking civil structures (U-girder, platform L-units) against
the actual rail envelope. Not shipped as a kit — sleepers and rails
are loaded separately and the panel is assembled on site.
"""

from __future__ import annotations

from osr_mech.cad import Axis, Compound, Part

from ..common import (
    STANDARD_GAUGE_MM,
    GeometryPreset,
    preset_rail_profile,
    preset_sleeper_spacing_mm,
)
from .fastener import fastener_assembly
from .rail import rail_bar
from .sleeper import SLEEPER_LENGTH_MM, mono_block_sleeper, rail_seat_positions


def track_panel(
    length_mm: float = 6500.0,
    preset: GeometryPreset = GeometryPreset.STANDARD_URBAN,
) -> Compound:
    """One assembled track panel of the requested length.

    Defaults: 6500 mm (ten sleepers at 650 mm spacing) — a convenient
    flatbed-friendly shippable unit for a depot-assembled panel.
    Everything larger is built up in place from rail bars + sleepers
    + fastener kits on the ballast.

    Coordinate frame: +X is traffic direction, rails extend along +X.
    Origin at the -X end, gauge-centre.
    """

    spacing = preset_sleeper_spacing_mm(preset)
    profile = preset_rail_profile(preset)

    parts: list[Part | Compound] = []

    # Sleepers placed perpendicular to the rail direction.
    n_sleepers = int(length_mm // spacing) + 1
    seat_a, seat_b = rail_seat_positions()
    half_seat_gap = (seat_b - seat_a) / 2.0

    for i in range(n_sleepers):
        x = i * spacing
        if x > length_mm:
            break
        s = mono_block_sleeper()
        # Centre sleeper on gauge-centre; sleeper is built along its own +X
        # axis. Rotate so it spans across the track (-Y .. +Y), then move
        # it to the correct x along the panel.
        s = s.rotate(Axis.Z, 90)
        # After rotation, sleeper length lies along Y. We want its centre
        # on y = 0 and its +X placement to match the sleeper index.
        s = s.translate((x, -SLEEPER_LENGTH_MM / 2.0, 0.0))
        parts.append(s)

        # Fastener kits at each rail seat, rail foot resting on pad.
        from .sleeper import SLEEPER_END_HEIGHT_MM

        # Rail seat Y positions (gauge / 2 on each side of centreline).
        for rail_y in (-STANDARD_GAUGE_MM / 2.0, STANDARD_GAUGE_MM / 2.0):
            f = fastener_assembly()
            f = f.translate((x, rail_y, SLEEPER_END_HEIGHT_MM))
            parts.append(f)

    # Rails — one per side.
    from .sleeper import SLEEPER_END_HEIGHT_MM
    from .fastener import PAD_THICKNESS_MM

    rail_base_z = SLEEPER_END_HEIGHT_MM + PAD_THICKNESS_MM

    for rail_y in (-STANDARD_GAUGE_MM / 2.0, STANDARD_GAUGE_MM / 2.0):
        r = rail_bar(profile=profile, length_mm=length_mm)
        r = r.translate((0.0, rail_y, rail_base_z))
        parts.append(r)

    return Compound(label=f"Track panel ({preset.value}, {length_mm:.0f} mm)", children=parts)


__all__ = ["track_panel"]
