"""Early rolling-stock fabrication templates.

These are deliberately simple envelope parts for progressing supplier and
fixture integration work. Detailed production geometry belongs in the main
rolling-stock modules once interfaces are frozen.
"""

from __future__ import annotations

from math import cos, radians, sin

from build123d import Box, Compound, Cylinder, Location

from .fixtures import (
    anderson_sb50_placeholder,
    camloc_quarter_turn_placeholder,
    hiwin_hg_block_placeholder,
    skf_ge_placeholder,
    stabilus_gas_strut_placeholder,
)
from .params import DEFAULT_PARAMS, TemplateParams


def _with_label(part, label: str):
    part.label = label
    return part


def main_frame(params: TemplateParams = DEFAULT_PARAMS) -> Compound:
    """Underframe ladder with longitudinal beams, cross-members, and bolster pocket."""

    parts = []
    length = params.car_length_mm
    width = params.car_width_mm
    height = params.frame_beam_height_mm
    beam_thickness = params.frame_beam_thickness_mm

    left_beam = Box(length=length, width=beam_thickness, height=height).locate(
        Location((0, 0, 0))
    )
    right_beam = left_beam.moved(Location((0, width - beam_thickness, 0)))
    parts.extend([left_beam, right_beam])

    cross_count = max(1, int(length / params.cross_spacing_mm))
    for index in range(1, cross_count):
        x = -length / 2 + index * params.cross_spacing_mm
        parts.append(
            Box(length=beam_thickness, width=width, height=height).locate(
                Location((x, 0, 0))
            )
        )

    parts.append(
        Cylinder(radius=150.0, height=20.0).locate(Location((0, width / 2, -10)))
    )
    c = Compound(children=parts)
    c.label = "Rolling-stock main frame template"
    return c


def sandwich_panel(params: TemplateParams = DEFAULT_PARAMS) -> Compound:
    """Side-wall sandwich panel with a window aperture and edge extrusion."""

    width = params.panel_width_mm
    height = params.panel_height_mm
    thickness = params.panel_thickness_mm
    skin_t = params.skin_thickness_mm

    panel = Box(length=width, width=height, height=thickness)
    win_w = min(1000.0, width - 100.0)
    win_h = min(400.0, height - 100.0)
    window = Box(length=win_w, width=win_h, height=skin_t + 1.0).locate(
        Location(((width - win_w) / 2, (height - win_h) / 2, skin_t))
    )
    result = panel.cut(window)
    edge = Box(length=width + 20.0, width=20.0, height=thickness).locate(
        Location((-10, -10, 0))
    )
    c = Compound(children=[result, edge])
    c.label = "Sandwich panel template"
    return c


def door_leaf(params: TemplateParams = DEFAULT_PARAMS) -> Compound:
    """Door leaf with a simple glazing cut-out."""

    width = params.door_width_mm
    height = params.door_height_mm
    thickness = params.door_thickness_mm

    leaf = Box(length=width, width=thickness, height=height)
    glazing_width = min(800.0, width - 100.0)
    glazing_height = min(1200.0, height - 200.0)
    glazing = Box(
        length=glazing_width,
        width=thickness + 1.0,
        height=glazing_height,
    ).locate(
        Location(
            (
                (width - glazing_width) / 2,
                thickness / 2 - 0.5,
                (height - glazing_height) / 2,
            )
        )
    )
    c = Compound(children=[leaf.cut(glazing)])
    c.label = "Door leaf template"
    return c


def bogie_adapter() -> Compound:
    """Bogie adapter plate with guide-block and access-fastener envelopes."""

    plate_w = 300.0
    plate_h = 200.0
    plate_t = 12.0
    dowel_dia = 25.0
    dowel_off = 30.0

    plate = _with_label(
        Box(length=plate_w, width=plate_h, height=plate_t),
        "Adapter shear plate",
    )
    for index in range(4):
        x = dowel_off if index % 2 == 0 else plate_w - dowel_off
        y = dowel_off if index < 2 else plate_h - dowel_off
        hole = Cylinder(radius=dowel_dia / 2, height=plate_t + 2).locate(
            Location((x, y, 0))
        )
        plate = plate.cut(hole)

    pocket = _with_label(
        Box(length=80.0, width=40.0, height=6.0).locate(
            Location(((plate_w - 80.0) / 2, (plate_h - 40.0) / 2, -6.0))
        ),
        "Adapter alignment pocket",
    )
    rail = _with_label(
        Box(length=plate_w - 60.0, width=18.0, height=12.0).locate(
            Location((plate_w / 2, plate_h / 2, plate_t))
        ),
        "Adapter linear-guide rail datum",
    )
    guide_blocks = []
    for x in (plate_w * 0.32, plate_w * 0.68):
        guide = hiwin_hg_block_placeholder().locate(
            Location((x, plate_h / 2, plate_t + 32.0))
        )
        guide.label = "HIWIN HG guide block envelope"
        guide_blocks.append(guide)
    access_fasteners = []
    for x in (dowel_off, plate_w - dowel_off):
        fastener = camloc_quarter_turn_placeholder().locate(
            Location((x, plate_h / 2, plate_t + 18.0))
        )
        fastener.label = "Camloc access fastener envelope"
        access_fasteners.append(fastener)
    c = Compound(children=[plate, pocket, rail, *guide_blocks, *access_fasteners])
    c.label = "Bogie adapter template"
    return c


def bolster() -> Compound:
    """Bolster / pivot plate with bearing, hard stops, and bolt circle."""

    plate_dia = 300.0
    plate_thickness = 20.0
    pivot_dia = 80.0
    bolt_hole_dia = 25.0
    bolt_circle = 220.0
    bolt_count = 8

    plate = _with_label(
        Cylinder(radius=plate_dia / 2, height=plate_thickness),
        "Bolster pivot plate",
    )
    pivot = Cylinder(radius=pivot_dia / 2, height=plate_thickness + 2)
    plate_solid = plate.cut(pivot)
    plate_solid.label = "Bolster pivot plate with recess"

    for index in range(bolt_count):
        angle = radians(index * 360.0 / bolt_count)
        x = bolt_circle / 2 * cos(angle)
        y = bolt_circle / 2 * sin(angle)
        hole = Cylinder(radius=bolt_hole_dia / 2, height=plate_thickness + 2).locate(
            Location((x, y, 0))
        )
        plate_solid = plate_solid.cut(hole)

    boss = _with_label(
        Cylinder(radius=50.0, height=10.0).locate(Location((0, 0, -10.0))),
        "Bolster locating boss",
    )
    bearing = skf_ge_placeholder().locate(Location((0, 0, plate_thickness / 2)))
    bearing.label = "SKF GE spherical bearing envelope"
    hard_stops = []
    for y_sign in (-1.0, 1.0):
        stop = _with_label(
            Box(length=80.0, width=22.0, height=30.0).locate(
                Location((0, y_sign * 130.0, plate_thickness + 15.0))
            ),
            "Bolster lateral hard stop",
        )
        hard_stops.append(stop)
    c = Compound(children=[plate_solid, boss, bearing, *hard_stops])
    c.label = "Bolster template"
    return c


def motor_cradle() -> Compound:
    """Motor cradle plate with isolator mounts, service strut, and connector."""

    plate_w = 300.0
    plate_l = 200.0
    plate_t = 12.0
    isolator_dia = 20.0
    isolator_off = 30.0

    plate = _with_label(
        Box(length=plate_l, width=plate_w, height=plate_t),
        "Motor cradle base plate",
    )
    coupling_cutout = Cylinder(radius=40.0, height=plate_t + 2).locate(
        Location((plate_l / 2, plate_w / 2, 0))
    )
    plate_solid = plate.cut(coupling_cutout)
    plate_solid.label = "Motor cradle base plate with coupling cutout"

    isolator_bosses = []
    for dx in (-1, 1):
        for dy in (-1, 1):
            x = plate_l / 2 + dx * (plate_l / 2 - isolator_off)
            y = plate_w / 2 + dy * (plate_w / 2 - isolator_off)
            hole = Cylinder(radius=isolator_dia / 2, height=plate_t + 2).locate(
                Location((x, y, 0))
            )
            plate_solid = plate_solid.cut(hole)
            isolator_bosses.append(
                _with_label(
                    Cylinder(radius=22.0, height=10.0).locate(
                        Location((x, y, plate_t + 5.0))
                    ),
                    "Motor cradle isolator boss",
                )
            )

    shim_slot = Box(length=60.0, width=6.0, height=6.0).locate(
        Location((plate_l / 2 - 30.0, plate_w / 2 - 3.0, plate_t - 6.0))
    )
    plate_solid = plate_solid.cut(shim_slot)
    plate_solid.label = "Motor cradle machined plate"
    connector = anderson_sb50_placeholder().locate(
        Location((plate_l + 35.0, plate_w / 2, plate_t + 15.0))
    )
    connector.label = "Anderson SB50 traction connector envelope"
    service_strut = stabilus_gas_strut_placeholder().locate(
        Location((-45.0, plate_w / 2, plate_t + 150.0))
    )
    service_strut.label = "Stabilus service strut envelope"
    c = Compound(children=[plate_solid, *isolator_bosses, connector, service_strut])
    c.label = "Motor cradle template"
    return c


def chassis_interface_assembly() -> Compound:
    """Grouped chassis interface stack for fixture-clearance review."""

    adapter = bogie_adapter().locate(Location((0, 0, 0)))
    adapter.label = "Bogie adapter interface assembly"
    bolster_part = bolster().locate(Location((450.0, 100.0, 80.0)))
    bolster_part.label = "Bolster interface assembly"
    cradle = motor_cradle().locate(Location((900.0, -50.0, 0.0)))
    cradle.label = "Motor cradle interface assembly"
    c = Compound(children=[adapter, bolster_part, cradle])
    c.label = "Chassis fixture integration assembly"
    return c
