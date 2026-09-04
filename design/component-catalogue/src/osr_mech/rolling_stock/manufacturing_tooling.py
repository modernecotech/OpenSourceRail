"""Supplier-neutral LM3 manufacturing tooling review geometry.

The shapes expose fixture intent, access and datum relationships in FreeCAD.
They are not NC surfaces, certified lifting devices, calibrated gauges or
released mould drawings.
"""

from __future__ import annotations

from osr_mech.cad import Box, Color, Compound, Cylinder, Location, Part


STEEL = Color(0.38, 0.43, 0.48)
DATUM = Color(0.96, 0.62, 0.10)
MOULD = Color(0.12, 0.56, 0.62)
SEAL = Color(0.08, 0.08, 0.09)
SAFETY = Color(0.88, 0.19, 0.16)
BOARD = Color(0.80, 0.73, 0.55)


def _part(shape: Part, label: str, colour: Color) -> Part:
    shape.label = label
    shape.color = colour
    return shape


def _compound(tool_id: str, parts: list[Part]) -> Compound:
    return Compound(label=tool_id, children=parts)


def steel_fixture() -> Compound:
    parts = [
        _part(Box(17_000, 3_600, 180).locate(Location((0, 0, 90))), "level fixture bed", STEEL),
    ]
    for x in (-7_500, -5_000, -2_500, 0, 2_500, 5_000, 7_500):
        parts.append(_part(Box(180, 3_200, 700).locate(Location((x, 0, 440))), "adjustable cross datum", STEEL))
        for y in (-1_350, 1_350):
            parts.append(_part(Cylinder(45, 850).locate(Location((x, y, 925))), "survey target / clamp post", DATUM))
    return _compound("LM3-TOOL-STEEL-FIXTURE", parts)


def datum_gauge() -> Compound:
    parts = [_part(Box(3_400, 180, 120), "portable datum beam", STEEL)]
    for y in (-1_350, 0, 1_350):
        parts.append(_part(Cylinder(22, 520).locate(Location((0, y, 300))), "removable datum pin", DATUM))
    return _compound("LM3-TOOL-DATUM-GAUGE", parts)


def side_mould() -> Compound:
    parts = [
        _part(Box(1_300, 3_600, 120).locate(Location((0, 0, 60))), "stiff mould back", STEEL),
        _part(Box(1_080, 3_250, 35).locate(Location((0, 0, 138))), "one-metre side-module female tool face", MOULD),
    ]
    for x in (-500, 500):
        for z in (-1_450, 1_450):
            parts.append(_part(Cylinder(14, 80).locate(Location((x, z, 205))), "vacuum / resin port", SAFETY))
    return _compound("LM3-TOOL-SIDE-MOULD", parts)


def roof_mould() -> Compound:
    parts = [_part(Box(1_300, 3_200, 120).locate(Location((0, 0, 60))), "roof mould base", STEEL)]
    for y, height in ((-1_350, 160), (-900, 260), (-450, 330), (0, 355), (450, 330), (900, 260), (1_350, 160)):
        parts.append(_part(Box(1_080, 90, height).locate(Location((0, y, 120 + height / 2))), "replaceable roof mould rib", MOULD))
    parts.append(_part(Box(1_080, 2_900, 28).locate(Location((0, 0, 490))), "fair tooling skin review envelope", MOULD))
    return _compound("LM3-TOOL-ROOF-MOULD", parts)


def cowl_mould() -> Compound:
    parts = [_part(Box(3_300, 3_400, 180).locate(Location((0, 0, 90))), "split-cowl mould base", STEEL)]
    for x in (-1_200, 0, 1_200):
        for y in (-1_300, 1_300):
            parts.append(_part(Box(700, 120, 2_100).locate(Location((x, y, 1_200))), "removable split mould segment", MOULD))
    parts.append(_part(Box(2_700, 2_450, 160).locate(Location((0, 0, 2_330))), "upper brow mould segment", MOULD))
    return _compound("LM3-TOOL-COWL-MOULD", parts)


def side_variant_nest() -> Compound:
    parts = [_part(Box(1_350, 3_550, 120).locate(Location((0, 0, 60))), "side-module vacuum trim nest", BOARD)]
    for y in (-1_400, -900, -400, 400, 900, 1_400):
        for x in (-470, 470):
            parts.append(_part(Cylinder(14, 95).locate(Location((x, y, 170))), "solid/window/door variant drill bushing", DATUM))
    parts.extend(
        [
            _part(Box(720, 80, 90).locate(Location((0, 0, 180))), "removable window-edge trim fence", MOULD),
            _part(Box(420, 80, 90).locate(Location((0, -900, 180))), "removable door-pocket trim fence", SAFETY),
        ]
    )
    return _compound("LM3-TOOL-SIDE-VARIANT-NEST", parts)


def roof_fairing_mould() -> Compound:
    parts = [_part(Box(3_600, 2_900, 150).locate(Location((0, 0, 75))), "roof fairing mould base", STEEL)]
    for x in (-1_350, -450, 450, 1_350):
        parts.append(_part(Box(120, 2_500, 520).locate(Location((x, 0, 410))), "replaceable HVAC/PV fairing mould rib", MOULD))
    parts.extend(
        [
            _part(Box(2_850, 1_850, 70).locate(Location((0, 0, 700))), "HVAC curb/fairing female tool face", MOULD),
            _part(Box(850, 520, 120).locate(Location((1_100, 800, 720))), "PV gland and antenna closeout insert", SAFETY),
        ]
    )
    return _compound("LM3-TOOL-ROOF-FAIRING-MOULD", parts)


def glass_carrier_nest() -> Compound:
    parts = list(_portal_tool("glass-carrier-base", 2_300, 1_780, "panoramic glass-carrier checking nest").children)
    for x in (-820, -410, 0, 410, 820):
        parts.append(_part(Cylinder(16, 280).locate(Location((x, 0, 330))), "carrier/seal compression witness pin", DATUM))
    parts.append(_part(Box(1_500, 160, 80).locate(Location((0, 0, 260))), "setting-block and drained-sill datum", SAFETY))
    return _compound("LM3-TOOL-GLASS-CARRIER-NEST", parts)


def lamp_aim_jig() -> Compound:
    parts = [
        _part(Box(2_200, 1_100, 160).locate(Location((0, 0, 80))), "lamp cassette fixture base", STEEL),
        _part(Box(1_850, 100, 120).locate(Location((0, 0, 420))), "reversible lamp datum beam", DATUM),
        _part(Box(80, 900, 1_200).locate(Location((0, 0, 1_080))), "photometric target-plane carrier", BOARD),
    ]
    for x in (-620, 620):
        parts.append(_part(Cylinder(22, 480).locate(Location((x, 0, 420))), "aiming-axis datum arbor", SAFETY))
    return _compound("LM3-TOOL-LAMP-AIM", parts)


def interior_ceiling_mould() -> Compound:
    parts = [_part(Box(1_350, 2_950, 120).locate(Location((0, 0, 60))), "ceiling liner mould base", STEEL)]
    for y, height in ((-1_150, 180), (-600, 280), (0, 340), (600, 280), (1_150, 180)):
        parts.append(_part(Box(1_100, 100, height).locate(Location((0, y, 120 + height / 2))), "ceiling/plenum mould rib", MOULD))
    parts.append(_part(Box(1_050, 240, 100).locate(Location((0, 0, 500))), "replaceable light/HVAC aperture insert", SAFETY))
    return _compound("LM3-TOOL-INT-CEILING-MOULD", parts)


def interior_side_mould() -> Compound:
    parts = [_part(Box(1_350, 2_450, 120).locate(Location((0, 0, 60))), "sidewall/reveal mould base", STEEL)]
    parts.append(_part(Box(1_050, 2_150, 45).locate(Location((0, 0, 150))), "sidewall visible tool face", MOULD))
    parts.append(_part(Box(760, 1_150, 110).locate(Location((0, 250, 220))), "removable window-reveal insert", SAFETY))
    return _compound("LM3-TOOL-INT-SIDE-MOULD", parts)


def interior_strake_mould() -> Compound:
    return _compound(
        "LM3-TOOL-INT-STRAKE-MOULD",
        [
            _part(Box(5_200, 1_050, 150).locate(Location((0, 0, 75))), "battery-strake mould base", STEEL),
            _part(Box(4_900, 780, 520).locate(Location((0, 0, 410))), "strake/seat-fairing tool face", MOULD),
            _part(Box(1_100, 520, 180).locate(Location((1_450, 0, 760))), "removable service-hatch insert", SAFETY),
        ],
    )


def interior_door_prm_mould() -> Compound:
    return _compound(
        "LM3-TOOL-INT-DOOR-PRM-MOULD",
        [
            _part(Box(2_800, 1_600, 140).locate(Location((0, 0, 70))), "door/PRM trim fixture base", STEEL),
            _part(Box(1_200, 1_100, 420).locate(Location((-650, 0, 350))), "PRM transition and step-cover tool", MOULD),
            _part(Box(1_050, 420, 1_850).locate(Location((700, 0, 995))), "door-pocket/jamb-cover tool", MOULD),
            _part(Box(900, 240, 80).locate(Location((-650, 0, 610))), "contrast-nosing and anti-slip datum", SAFETY),
        ],
    )


def film_template() -> Compound:
    parts = [_part(Box(8_500, 1_800, 40), "half-car livery-film cutting/vacuum table", BOARD)]
    for x in range(-3_750, 3_751, 500):
        parts.append(_part(Cylinder(8, 70).locate(Location((x, 0, 55))), "film bay/overlap datum", DATUM))
    parts.append(_part(Box(1_800, 1_500, 80).locate(Location((3_000, 0, 90))), "reversible cowl-film template", MOULD))
    return _compound("LM3-TOOL-FILM-TEMPLATE", parts)


def radiative_coupon() -> Compound:
    return _compound(
        "LM3-TOOL-RADIATIVE-COUPON",
        [
            _part(Box(300, 200, 4).locate(Location((-360, 0, 0))), "as-moulded GFRP control coupon", MOULD),
            _part(Box(300, 200, 4), "CaCO3-acrylic roof coating coupon", DATUM),
            _part(Box(300, 200, 4).locate(Location((360, 0, 0))), "aged wash/UV/abrasion coupon", SAFETY),
            _part(Box(1_100, 520, 60).locate(Location((0, 0, -35))), "masked spray/drawdown fixture", STEEL),
        ],
    )


def trim_drill_fixture() -> Compound:
    parts = [_part(Box(1_400, 3_800, 160).locate(Location((0, 0, 80))), "trim and drill vacuum table", BOARD)]
    for y in (-1_500, -1_000, -500, 0, 500, 1_000, 1_500):
        parts.append(_part(Cylinder(16, 110).locate(Location((-430, y, 215))), "hardened drill bushing", DATUM))
        parts.append(_part(Cylinder(16, 110).locate(Location((430, y, 215))), "hardened drill bushing", DATUM))
    return _compound("LM3-TOOL-TRIM-DRILL", parts)


def coating_rack() -> Compound:
    parts = []
    for y in (-1_500, 1_500):
        parts.append(_part(Box(4_000, 160, 180).locate(Location((0, y, 90))), "coating rack floor rail", STEEL))
        for x in (-1_800, 1_800):
            parts.append(_part(Box(160, 160, 2_600).locate(Location((x, y, 1_390))), "grounded coating rack post", STEEL))
    parts.append(_part(Box(3_600, 2_800, 40).locate(Location((0, 0, 1_600))), "hung module coating envelope", MOULD))
    return _compound("LM3-TOOL-COATING-RACK", parts)


def coating_coupon() -> Compound:
    return _compound(
        "LM3-TOOL-COATING-COUPON",
        [
            _part(Box(300, 200, 3).locate(Location((-330, 0, 0))), "GFRP witness coupon", MOULD),
            _part(Box(300, 200, 3), "steel witness coupon", STEEL),
            _part(Box(300, 200, 3).locate(Location((330, 0, 0))), "aged-cleaning witness coupon", DATUM),
        ],
    )


def _portal_tool(tool_id: str, width: float, height: float, label: str) -> Compound:
    parts = [
        _part(Box(width + 500, 240, 180).locate(Location((0, 0, 90))), f"{label} base", STEEL),
        _part(Box(160, 240, height).locate(Location((-(width + 160) / 2, 0, height / 2 + 180))), f"{label} left datum", STEEL),
        _part(Box(160, 240, height).locate(Location(((width + 160) / 2, 0, height / 2 + 180))), f"{label} right datum", STEEL),
        _part(Box(width + 320, 240, 160).locate(Location((0, 0, height + 260))), f"{label} head datum", STEEL),
    ]
    for x in (-width / 2, width / 2):
        for z in (420, height - 180):
            parts.append(_part(Cylinder(18, 320).locate(Location((x, 0, z))), "adjustable witness pin", DATUM))
    return _compound(tool_id, parts)


def window_gauge() -> Compound:
    return _portal_tool("LM3-TOOL-WINDOW-GAUGE", 1_650, 1_250, "window aperture/compression gauge")


def water_test() -> Compound:
    parts = list(_portal_tool("water-test-frame", 1_900, 1_600, "water-test support").children)
    for x in (-750, -250, 250, 750):
        parts.append(_part(Cylinder(20, 180).locate(Location((x, -500, 1_850))), "calibrated spray nozzle", SAFETY))
    return _compound("LM3-TOOL-WATER-TEST", parts)


def door_gauge() -> Compound:
    return _portal_tool("LM3-TOOL-DOOR-GAUGE", 1_500, 2_050, "door carrier datum gauge")


def seal_gauge() -> Compound:
    parts = []
    for x in (-700, 700):
        for z in (250, 1_000, 1_750):
            parts.append(_part(Box(80, 80, 30).locate(Location((x, 0, z))), "seal compression witness block", SEAL))
    return _compound("LM3-TOOL-SEAL-GAUGE", parts)


def floor_template() -> Compound:
    parts = [_part(Box(15_500, 2_700, 35), "full-car removable floor cutting/drill template", BOARD)]
    for x in range(-7_000, 7_001, 1_000):
        parts.append(_part(Cylinder(12, 80).locate(Location((x, -1_150, 55))), "floor/service-rail datum bushing", DATUM))
        parts.append(_part(Cylinder(12, 80).locate(Location((x, 1_150, 55))), "floor/service-rail datum bushing", DATUM))
    return _compound("LM3-TOOL-FLOOR-TEMPLATE", parts)


def fixture_proof() -> Compound:
    return _compound(
        "LM3-TOOL-FIXTURE-PROOF",
        [
            _part(Box(1_200, 900, 140).locate(Location((0, 0, 70))), "anchored proof frame", STEEL),
            _part(Box(80, 80, 1_800).locate(Location((0, 0, 1_040))), "fixture adapter sample", DATUM),
            _part(Cylinder(110, 420).locate(Location((0, 0, 2_150))), "calibrated load actuator envelope", SAFETY),
        ],
    )


def bogie_stand() -> Compound:
    parts = [
        _part(Box(4_200, 260, 220).locate(Location((0, -1_100, 110))), "bogie stand rail", STEEL),
        _part(Box(4_200, 260, 220).locate(Location((0, 1_100, 110))), "bogie stand rail", STEEL),
    ]
    for x in (-1_250, 1_250):
        for y in (-1_100, 1_100):
            parts.append(_part(Box(420, 420, 520).locate(Location((x, y, 480))), "adjustable axlebox stand", DATUM))
    return _compound("LM3-TOOL-BOGIE-STAND", parts)


def motor_align() -> Compound:
    return _compound(
        "LM3-TOOL-MOTOR-ALIGN",
        [
            _part(Box(2_200, 1_300, 160).locate(Location((0, 0, 80))), "motor alignment base", STEEL),
            _part(Cylinder(260, 900).locate(Location((-650, 0, 620))), "axle datum arbor", DATUM),
            _part(Cylinder(220, 900).locate(Location((650, 0, 620))), "motor shaft datum arbor", DATUM),
            _part(Box(1_400, 80, 80).locate(Location((0, 0, 1_180))), "laser/alignment target bar", SAFETY),
        ],
    )


def service_rail() -> Compound:
    parts = [_part(Box(4_000, 600, 80), "service-module preassembly rail", STEEL)]
    for x in range(-1_750, 1_751, 250):
        parts.append(_part(Cylinder(10, 100).locate(Location((x, 0, 90))), "50/250 mm module datum", DATUM))
    return _compound("LM3-TOOL-SERVICE-RAIL", parts)


def harness_board() -> Compound:
    parts = [_part(Box(8_000, 2_400, 60), "full harness form board", BOARD)]
    for x in range(-3_500, 3_501, 500):
        for y in (-850, 0, 850):
            parts.append(_part(Cylinder(16, 100).locate(Location((x, y, 80))), "removable routing pin", DATUM))
    return _compound("LM3-TOOL-HARNESS-BOARD", parts)


def lift_columns() -> Compound:
    parts = []
    for x in (-7_000, -3_500, 3_500, 7_000):
        for y in (-2_000, 2_000):
            parts.append(_part(Box(520, 520, 4_800).locate(Location((x, y, 2_400))), "synchronised lifting column envelope", SAFETY))
            parts.append(_part(Box(900, 900, 120).locate(Location((x, y, 60))), "certified column base envelope", STEEL))
    return _compound("LM3-TOOL-LIFT-COLUMNS", parts)


def final_datum() -> Compound:
    parts = [_part(Box(50_000, 120, 80), "final-road vehicle centreline datum", DATUM)]
    for x in range(-24_000, 24_001, 3_000):
        parts.append(_part(Cylinder(18, 300).locate(Location((x, 0, 190))), "survey monument", DATUM))
    return _compound("LM3-TOOL-FINAL-DATUM", parts)


TOOL_BUILDERS = {
    "LM3-TOOL-STEEL-FIXTURE": steel_fixture,
    "LM3-TOOL-DATUM-GAUGE": datum_gauge,
    "LM3-TOOL-SIDE-MOULD": side_mould,
    "LM3-TOOL-ROOF-MOULD": roof_mould,
    "LM3-TOOL-COWL-MOULD": cowl_mould,
    "LM3-TOOL-SIDE-VARIANT-NEST": side_variant_nest,
    "LM3-TOOL-ROOF-FAIRING-MOULD": roof_fairing_mould,
    "LM3-TOOL-GLASS-CARRIER-NEST": glass_carrier_nest,
    "LM3-TOOL-LAMP-AIM": lamp_aim_jig,
    "LM3-TOOL-INT-CEILING-MOULD": interior_ceiling_mould,
    "LM3-TOOL-INT-SIDE-MOULD": interior_side_mould,
    "LM3-TOOL-INT-STRAKE-MOULD": interior_strake_mould,
    "LM3-TOOL-INT-DOOR-PRM-MOULD": interior_door_prm_mould,
    "LM3-TOOL-FILM-TEMPLATE": film_template,
    "LM3-TOOL-RADIATIVE-COUPON": radiative_coupon,
    "LM3-TOOL-TRIM-DRILL": trim_drill_fixture,
    "LM3-TOOL-COATING-RACK": coating_rack,
    "LM3-TOOL-COATING-COUPON": coating_coupon,
    "LM3-TOOL-WINDOW-GAUGE": window_gauge,
    "LM3-TOOL-WATER-TEST": water_test,
    "LM3-TOOL-DOOR-GAUGE": door_gauge,
    "LM3-TOOL-SEAL-GAUGE": seal_gauge,
    "LM3-TOOL-FLOOR-TEMPLATE": floor_template,
    "LM3-TOOL-FIXTURE-PROOF": fixture_proof,
    "LM3-TOOL-BOGIE-STAND": bogie_stand,
    "LM3-TOOL-MOTOR-ALIGN": motor_align,
    "LM3-TOOL-SERVICE-RAIL": service_rail,
    "LM3-TOOL-HARNESS-BOARD": harness_board,
    "LM3-TOOL-LIFT-COLUMNS": lift_columns,
    "LM3-TOOL-FINAL-DATUM": final_datum,
}


def manufacturing_tool(tool_id: str) -> Compound:
    try:
        return TOOL_BUILDERS[tool_id]()
    except KeyError as exc:
        raise KeyError(f"unknown LM3 manufacturing tool {tool_id!r}") from exc
