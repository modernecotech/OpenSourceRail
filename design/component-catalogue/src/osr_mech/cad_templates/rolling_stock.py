"""Rolling-stock fabrication templates.

These are supplier-neutral manufacturing templates: not homologated
shop drawings, but concrete enough for fit-up review, fixture design,
supplier envelope checks, and first-article routing. They model the
sheet-metal/chassis features a workshop actually needs: formed side
sills, cross bearers, bolsters, battery trays, door posts, roof bows,
flanges, access panels, datums, and COTS fixture interfaces.
"""

from __future__ import annotations

from math import cos, radians, sin

from osr_mech.cad import Box, Compound, Cylinder, Location

from .fixtures import (
    anderson_sb50_envelope,
    camloc_quarter_turn_envelope,
    hiwin_hg_block_envelope,
    skf_ge_envelope,
    stabilus_gas_strut_envelope,
)
from .params import DEFAULT_PARAMS, TemplateParams


def _with_label(part, label: str):
    part.label = label
    return part


def main_frame(params: TemplateParams = DEFAULT_PARAMS) -> Compound:
    """Sheet-metal underframe ladder with formed sills and equipment trays."""

    parts = []
    length = params.car_length_mm
    width = params.car_width_mm
    height = params.frame_beam_height_mm
    beam_thickness = params.frame_beam_thickness_mm
    y_left = -width / 2.0 + beam_thickness / 2.0
    y_right = width / 2.0 - beam_thickness / 2.0

    left_beam = _with_label(
        Box(length=length, width=beam_thickness, height=height).locate(
            Location((0, y_left, 0))
        ),
        "Folded C-channel side sill",
    )
    right_beam = _with_label(
        Box(length=length, width=beam_thickness, height=height).locate(
            Location((0, y_right, 0))
        ),
        "Folded C-channel side sill",
    )
    parts.extend([left_beam, right_beam])

    parts.append(
        _with_label(
            Box(length=6400.0, width=width - 520.0, height=70.0).locate(Location((0.0, 0.0, -110.0))),
            "Dropped low-floor centre pan fixture",
        )
    )
    for x_sign in (-1.0, 1.0):
        x = x_sign * (length / 2.0 - 2380.0)
        parts.append(
            _with_label(
                Box(length=4200.0, width=width - 460.0, height=170.0).locate(Location((x, 0.0, 260.0))),
                "Raised high-floor bogie-end deck support",
            )
        )
        parts.append(
            _with_label(
                Box(length=1100.0, width=width - 600.0, height=85.0).locate(Location((x_sign * 3750.0, 0.0, 90.0))),
                "Stepped transition support between low and high floor",
            )
        )

    cross_count = max(1, int(length / params.cross_spacing_mm))
    for index in range(1, cross_count):
        x = -length / 2 + index * params.cross_spacing_mm
        cross = _with_label(
            Box(length=beam_thickness, width=width - 2 * beam_thickness, height=height).locate(
                Location((x, 0, 0))
            ),
            "Pressed cross-bearer with lightening holes",
        )
        for y in (-520.0, 0.0, 520.0):
            cross = cross.cut(Cylinder(radius=95.0, height=beam_thickness + 2.0).locate(Location((x, y, 0))))
        parts.append(cross)

    for x in (-length * 0.32, length * 0.32):
        parts.append(
            _with_label(
                Box(length=1250.0, width=width - 320.0, height=180.0).locate(Location((x, 0, -20.0))),
                "Welded bogie bolster box",
            )
        )
        parts.append(
            _with_label(
                Cylinder(radius=180.0, height=28.0).locate(Location((x, 0, 100.0))),
                "Machined centre-pivot boss",
            )
        )
        for y in (-620.0, 620.0):
            parts.append(
                _with_label(
                    Box(length=520.0, width=140.0, height=90.0).locate(Location((x, y, 120.0))),
                    "Air-spring mounting pad",
                )
            )

    for side in (-1.0, 1.0):
        y = side * (width / 2.0 - 360.0)
        for x in (-6100.0, -4200.0, 4200.0, 6100.0):
            parts.append(
                _with_label(
                    Box(length=1580.0, width=420.0, height=80.0).locate(Location((x, y, -120.0))),
                    "Folded under-seat battery tray",
                )
            )
    for x in (-length / 2 + 900.0, length / 2 - 900.0):
        parts.append(
            _with_label(
                Box(length=720.0, width=width - 220.0, height=260.0).locate(Location((x, 0, 40.0))),
                "Coupler pocket folded box",
            )
        )
    c = Compound(children=parts)
    c.label = "Rolling-stock sheet-metal underframe template"
    return c


def sandwich_panel(params: TemplateParams = DEFAULT_PARAMS) -> Compound:
    """Keyed composite cassette with 3-2-1 datums and removable services."""

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
    result.label = "Panel skin with bonded window aperture"
    edge_parts = [
        _with_label(
            Box(length=width + 20.0, width=28.0, height=thickness).locate(Location((-10, -14, 0))),
            "Folded panel edge flange",
        ),
        _with_label(
            Box(length=width + 20.0, width=28.0, height=thickness).locate(Location((-10, height - 14, 0))),
            "Folded panel edge flange",
        ),
        _with_label(
            Box(length=28.0, width=height, height=thickness).locate(Location((-14, height / 2, 0))),
            "Vertical panel splice flange",
        ),
        _with_label(
            Box(length=28.0, width=height, height=thickness).locate(Location((width + 14, height / 2, 0))),
            "Vertical panel splice flange",
        ),
    ]
    retainers = []
    for x in (120.0, width - 120.0):
        for y in (160.0, height - 160.0):
            retainers.append(
                _with_label(
                    Cylinder(radius=16.0, height=thickness + 8.0).locate(Location((x, y, thickness / 2))),
                    "Quarter-turn retainer datum",
                )
            )
    poka_yoke = [
        _with_label(
            Cylinder(radius=12.0, height=thickness + 18.0).locate(
                Location((90.0, 90.0, thickness / 2))
            ),
            "3-2-1 primary round locating pin",
        ),
        _with_label(
            Box(length=28.0, width=18.0, height=thickness + 18.0).locate(
                Location((width - 110.0, 90.0, thickness / 2))
            ),
            "3-2-1 secondary diamond locating pin",
        ),
        _with_label(
            Box(length=44.0, width=24.0, height=thickness + 18.0).locate(
                Location((90.0, height - 110.0, thickness / 2))
            ),
            "Asymmetric anti-reversal locator key",
        ),
        _with_label(
            Box(length=width - 120.0, width=18.0, height=8.0).locate(
                Location((60.0, 42.0, thickness + 4.0))
            ),
            "Controlled adhesive and sealant groove witness",
        ),
        _with_label(
            Cylinder(radius=10.0, height=thickness + 22.0).locate(
                Location((width - 70.0, height - 70.0, thickness / 2))
            ),
            "Composite cassette electrical bonding stud",
        ),
        _with_label(
            Box(length=90.0, width=55.0, height=42.0).locate(
                Location((width / 2, 70.0, thickness + 21.0))
            ),
            "Keyed removable-service quick-connector datum",
        ),
    ]
    c = Compound(children=[result, *edge_parts, *retainers, *poka_yoke])
    c.label = "Poka-yoke side sandwich cassette manufacturing template"
    return c


def door_leaf(params: TemplateParams = DEFAULT_PARAMS) -> Compound:
    """COTS-style plug/sliding door leaf with skins, glass, and seals."""

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
    leaf_solid = leaf.cut(glazing)
    leaf_solid.label = "Pressed aluminium door leaf shell"
    glass = _with_label(
        Box(length=glazing_width - 40.0, width=thickness / 2.0, height=glazing_height - 40.0).locate(
            Location((width / 2, thickness / 2, height / 2))
        ),
        "Bonded door glazing cassette",
    )
    seals = [
        _with_label(Box(length=width, width=8.0, height=24.0).locate(Location((width / 2, -4.0, 14.0))), "EPDM lower door seal"),
        _with_label(Box(length=width, width=8.0, height=24.0).locate(Location((width / 2, -4.0, height - 14.0))), "EPDM upper door seal"),
        _with_label(Box(length=18.0, width=8.0, height=height).locate(Location((10.0, -4.0, height / 2))), "EPDM vertical door seal"),
        _with_label(Box(length=18.0, width=8.0, height=height).locate(Location((width - 10.0, -4.0, height / 2))), "EPDM vertical door seal"),
    ]
    rollers = [
        _with_label(Cylinder(radius=32.0, height=24.0).locate(Location((x, thickness + 18.0, height + 28.0))), "Door hanger roller")
        for x in (width * 0.25, width * 0.75)
    ]
    c = Compound(children=[leaf_solid, glass, *seals, *rollers])
    c.label = "Door leaf manufacturing template"
    return c


def body_sheet_metal_kit(params: TemplateParams = DEFAULT_PARAMS) -> Compound:
    """Body/chassis sheet-metal kit for manufacturing and fixture review."""

    length = params.car_length_mm
    width = params.car_width_mm
    height = 3000.0
    parts = [main_frame(params)]
    for side in (-1.0, 1.0):
        y = side * (width / 2.0 - 55.0)
        for x in (-7100.0, -5200.0, -3000.0, 3000.0, 5200.0, 7100.0):
            parts.append(
                _with_label(
                    Box(length=120.0, width=110.0, height=height).locate(Location((x, y, height / 2.0 + 120.0))),
                    "Pressed side-wall post",
                )
            )
        for x in (-length / 4.0, length / 4.0):
            parts.append(
                _with_label(
                    Box(length=980.0, width=130.0, height=height - 260.0).locate(Location((x, y, height / 2.0 + 250.0))),
                    "Door portal reinforcement",
                )
            )
        parts.append(
            _with_label(
                Box(length=length - 800.0, width=90.0, height=110.0).locate(Location((0.0, y, 2550.0))),
                "Rolled cant rail",
            )
        )
        parts.append(
            _with_label(
                Box(length=length - 800.0, width=80.0, height=90.0).locate(Location((0.0, y, 1150.0))),
                "Pressed waist rail",
            )
        )
        parts.append(
            _with_label(
                Box(length=6400.0, width=90.0, height=180.0).locate(Location((0.0, y, 520.0))),
                "Lowered side rail at low-floor door zone",
            )
        )
        for x_sign in (-1.0, 1.0):
            parts.append(
                _with_label(
                    Box(length=4200.0, width=95.0, height=260.0).locate(Location((x_sign * (length / 2.0 - 2380.0), y, 780.0))),
                    "Raised side plinth rail over standard bogie",
                )
            )
    for x in (-7600.0, -5600.0, -3600.0, -1600.0, 1600.0, 3600.0, 5600.0, 7600.0):
        parts.append(
            _with_label(
                Box(length=120.0, width=width - 260.0, height=95.0).locate(Location((x, 0.0, 3180.0))),
                "Roll-formed roof bow",
            )
        )
    for x in (-length / 2.0 + 650.0, length / 2.0 - 650.0):
        parts.append(
            _with_label(
                Box(length=180.0, width=width - 160.0, height=2650.0).locate(Location((x, 0.0, 1600.0))),
                "End bulkhead ring frame",
            )
        )
    c = Compound(children=parts)
    c.label = "Body and chassis sheet-metal kit"
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
        guide = hiwin_hg_block_envelope().locate(
            Location((x, plate_h / 2, plate_t + 32.0))
        )
        guide.label = "HIWIN HG guide block envelope"
        guide_blocks.append(guide)
    access_fasteners = []
    for x in (dowel_off, plate_w - dowel_off):
        fastener = camloc_quarter_turn_envelope().locate(
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
    bearing = skf_ge_envelope().locate(Location((0, 0, plate_thickness / 2)))
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
    connector = anderson_sb50_envelope().locate(
        Location((plate_l + 35.0, plate_w / 2, plate_t + 15.0))
    )
    connector.label = "Anderson SB50 traction connector envelope"
    service_strut = stabilus_gas_strut_envelope().locate(
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
