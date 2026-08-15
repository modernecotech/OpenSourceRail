"""Supplier-neutral COTS fixture envelopes for assembly integration."""

from __future__ import annotations

from osr_mech.cad import Box, Compound, Cylinder, Location


def anderson_sb50_envelope() -> Compound:
    """Anderson SB50 connector envelope."""

    c = Compound(children=[Box(length=60.0, width=35.0, height=25.0)])
    c.label = "Anderson SB50 reference envelope"
    return c


def camloc_quarter_turn_envelope() -> Compound:
    """Camloc quarter-turn fastener stud and receptacle envelope."""

    stud_dia = 12.0
    stud_len = 25.0
    receptacle_w = 20.0
    receptacle_h = 8.0
    stud = Cylinder(radius=stud_dia / 2, height=stud_len)
    receptacle = Box(length=receptacle_w, width=receptacle_w, height=receptacle_h).locate(
        Location((0, 0, -receptacle_h))
    )
    c = Compound(children=[stud, receptacle])
    c.label = "Camloc quarter-turn reference envelope"
    return c


def hiwin_hg_block_envelope() -> Compound:
    """HIWIN HG series linear guide block envelope."""

    c = Compound(children=[Box(length=120.0, width=60.0, height=40.0)])
    c.label = "HIWIN HG block reference envelope"
    return c


def skf_ge_envelope() -> Compound:
    """SKF GE series spherical plain bearing envelope."""

    bearing = Cylinder(radius=50.0, height=40.0)
    inner = Cylinder(radius=25.0, height=42.0)
    c = Compound(children=[bearing.cut(inner)])
    c.label = "SKF GE reference envelope"
    return c


def stabilus_gas_strut_envelope() -> Compound:
    """Stabilus gas strut body and rod envelope."""

    body = Cylinder(radius=10.0, height=300.0)
    rod = Cylinder(radius=5.0, height=150.0).locate(Location((0, 0, 150.0)))
    c = Compound(children=[body, rod])
    c.label = "Stabilus gas strut reference envelope"
    return c


FIXTURE_BUILDERS = {
    "anderson-sb50-envelope": anderson_sb50_envelope,
    "camloc-quarter-turn-envelope": camloc_quarter_turn_envelope,
    "hiwin-hg-block-envelope": hiwin_hg_block_envelope,
    "skf-ge-envelope": skf_ge_envelope,
    "stabilus-gas-strut-envelope": stabilus_gas_strut_envelope,
}

__all__ = [
    "FIXTURE_BUILDERS",
    "anderson_sb50_envelope",
    "camloc_quarter_turn_envelope",
    "hiwin_hg_block_envelope",
    "skf_ge_envelope",
    "stabilus_gas_strut_envelope",
]
