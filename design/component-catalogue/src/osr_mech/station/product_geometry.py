"""Deterministic design-reference geometry for station product-tree items.

The station manifest remains the quantity and assembly authority.  Geometry in
this module gives each product a spatially coherent, inspectable representation
for FreeCAD and IFC coordination.  Bought-in equipment is represented by its
mounting, access and service envelope; site-dependent foundations and structures
remain visibly provisional until the relevant survey and calculation is released.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from osr_mech.cad import Box, Color, Compound, Cylinder, Location, Part
from osr_mech.depot.bogie_change import depot_bogie_change_bay


CONCRETE = Color(0.70, 0.70, 0.66)
STEEL = Color(0.38, 0.43, 0.48)
SYSTEM = Color(0.18, 0.39, 0.68)
SAFETY = Color(0.90, 0.48, 0.10)
GLASS = Color(0.24, 0.55, 0.72, 0.55)
PV = Color(0.08, 0.18, 0.28)
GROUND = Color(0.55, 0.50, 0.40)

# Station-library local coordinate contract.  Deployment models may translate
# this complete package to a surveyed project datum, but must preserve the
# 350 mm vertical boarding interface.
PLATFORM_SURFACE_Z_MM = 420.0
PLATFORM_TO_TOR_HEIGHT_MM = 350.0
TOP_OF_RAIL_Z_MM = PLATFORM_SURFACE_Z_MM - PLATFORM_TO_TOR_HEIGHT_MM
TURNOUT_NATIVE_RAIL_HEAD_Z_MM = 386.0
TURNOUT_TO_STATION_Z_MM = TOP_OF_RAIL_Z_MM - TURNOUT_NATIVE_RAIL_HEAD_Z_MM


@dataclass(frozen=True)
class StationGeometrySpec:
    product_id: str
    ifc_class: str
    geometry_level: str
    representation: str


_SEMANTICS: dict[str, tuple[str, str]] = {
    "STN-CIV-P010": ("IfcSlab", "platform/guideway structural envelope"),
    "STN-CIV-P020": ("IfcSlab", "sub-base, levelling and closure zones"),
    "STN-CIV-P030": ("IfcPipeSegment", "drain channels, catch pits and outlet"),
    "STN-CIV-P040": ("IfcBeam", "guideway edge, coping carrier and service trough"),
    "STN-PLT-P010": ("IfcCovering", "coping, tactile and warning-line system"),
    "STN-CNP-P010": ("IfcMember", "portal columns, rafter and knee braces"),
    "STN-CNP-P020": ("IfcVirtualElement", "site-dependent footing and anchor interface"),
    "STN-CNP-P030": ("IfcRoof", "supplier roof/PV panel interface envelope"),
    "STN-CNP-P040": ("IfcCableCarrierSegment", "PV string and downlink routes"),
    "STN-CNP-P050": ("IfcRoof", "auxiliary solar-roof bay envelope"),
    "STN-CNP-P060": ("IfcMember", "auxiliary truss members and columns"),
    "STN-CNP-P070": ("IfcVirtualElement", "site-dependent auxiliary footing interface"),
    "STN-CNP-P080": ("IfcCableCarrierSegment", "auxiliary PV string routes"),
    "STN-CNP-P090": ("IfcDistributionElement", "gutter, downpipe and access route"),
    "STN-MEP-P010": ("IfcElectricDistributionBoard", "services cabinet, plinth and access zones"),
    "STN-MEP-P020": ("IfcElectricDistributionBoard", "LV/UPS/earthing equipment envelope"),
    "STN-MEP-P030": ("IfcLightFixture", "platform and emergency luminaires"),
    "STN-MEP-P040": ("IfcAlarm", "fire detection and evacuation equipment"),
    "STN-PAX-P010": ("IfcCommunicationsAppliance", "station compute rack envelope"),
    "STN-PAX-P020": ("IfcAudioVisualAppliance", "passenger display and route-strip envelope"),
    "STN-PAX-P030": ("IfcCommunicationsAppliance", "CCTV, PA, help point and LAN envelope"),
    "STN-PAX-P040": ("IfcTransportElement", "fare/accessible gate operating envelope"),
    "STN-PAX-P050": ("IfcBuildingElementProxy", "ticket-vending equipment envelope"),
    "STN-PAX-P060": ("IfcFurniture", "seating and accessibility amenity layout"),
    "STN-PAX-P070": ("IfcDiscreteAccessory", "fare-lane plinth and cable void"),
    "STN-PAX-P080": ("IfcDiscreteAccessory", "TVM plinth and protected service entry"),
    "STN-ACC-P010": ("IfcRamp", "step-free approach and boundary envelope"),
    "STN-ACC-P020": ("IfcTransportElement", "lift/stair core and maintenance envelope"),
    "STN-ACC-P030": ("IfcSlab", "overbridge/concourse structure and enclosure envelope"),
    "STN-CHG-P010": ("IfcElectricDistributionBoard", "charger, connector and protected reach envelope"),
    "STN-CHG-P020": ("IfcTransformer", "traction substation interface envelope"),
    "STN-TRK-P010": ("IfcRail", "stock, switch and closure rail geometry"),
    "STN-TRK-P020": ("IfcDiscreteAccessory", "frog, check rail, stretcher and lock geometry"),
    "STN-TRK-P030": ("IfcTrackElement", "turnout sleepers, slide chairs and fasteners"),
    "STN-TRK-P040": ("IfcActuator", "point machine, crank and hand-wind envelope"),
    "STN-TRK-P050": ("IfcSensor", "dual detection, junction and harness routes"),
    "STN-TRK-P060": ("IfcSpaceHeater", "points-heating and isolation envelope"),
    "STN-TRK-P070": ("IfcDiscreteAccessory", "stop block, marker and fixing interface"),
    "STN-DEP-P010": ("IfcSlab", "depot formation, road, drainage and boundary layout"),
    "STN-DEP-P020": ("IfcRail", "stabling, inspection and wash-track layout"),
    "STN-DEP-P030": ("IfcElementAssembly", "depot throat turnout envelope"),
    "STN-DEP-P040": ("IfcElectricDistributionBoard", "stall charger, reel and data dock"),
    "STN-DEP-P050": ("IfcEnergyConversionDevice", "PV, inverter, switchgear and storage envelope"),
    "STN-DEP-P060": ("IfcBuildingElementProxy", "workshop, pits, crane and equipment zones"),
    "STN-DEP-P070": ("IfcDistributionElement", "depot services distribution envelope"),
}


def geometry_specs() -> dict[str, StationGeometrySpec]:
    return {
        product_id: StationGeometrySpec(
            product_id,
            ifc_class,
            "interface-detailed" if product_id.startswith(("STN-CIV", "STN-CNP-P01", "STN-PAX-P07", "STN-PAX-P08", "STN-TRK")) else "coordination-envelope",
            description,
        )
        for product_id, (ifc_class, description) in _SEMANTICS.items()
    }


def _part(shape: Part, label: str, colour: Color) -> Part:
    shape.label = label
    shape.color = colour
    return shape


def _box(size: tuple[float, float, float], label: str, colour: Color, at: tuple[float, float, float]) -> Part:
    return _part(Box(*size), label, colour).locate(Location(at))


def _equipment(label: str, at: tuple[float, float, float], size: tuple[float, float, float]) -> Compound:
    x, y, z = size
    px, py, pz = at
    return Compound(label=label, children=[
        _box((x, y, z), f"{label} enclosure", SYSTEM, at),
        _box((x * 1.15, y * 1.10, 100), f"{label} anchored plinth", STEEL, (px, py, pz - z / 2 - 50)),
        _box((x * 0.35, 180, z * 0.18), f"{label} keyed service interface", SAFETY, (px + x * 0.28, py - y / 2 - 90, pz)),
        _box((x + 900, y + 900, z + 300), f"{label} maintenance clearance", Color(0.25, 0.55, 0.80, 0.18), at),
    ])


def _platform_centres(parameters: dict[str, Any]) -> list[tuple[float, float]]:
    count = int(parameters["platform_count"])
    elevated = parameters.get("platform_layout") == "stacked"
    if count == 1:
        return [(5_000.0, 0.0)]
    if count == 2:
        return [(-5_000.0, 0.0), (5_000.0, 0.0)]
    if elevated:
        return [(-5_000.0, 9_000.0), (5_000.0, 9_000.0), (-5_000.0, 17_000.0), (5_000.0, 17_000.0)]
    return [(-11_000.0, 0.0), (-5_000.0, 0.0), (5_000.0, 0.0), (11_000.0, 0.0)]


def _platform_parts(product_id: str, parameters: dict[str, Any], label: str) -> Compound:
    length = float(parameters["platform_length_m"]) * 1000.0
    centres = _platform_centres(parameters)
    children: list[Part] = []
    for index, (y, level) in enumerate(centres, start=1):
        if product_id == "STN-CIV-P010":
            children.append(_box((length, 3_000, 420), f"{label} platform {index}", CONCRETE, (0, y, level + 210)))
        elif product_id == "STN-CIV-P020":
            children.append(_box((length, 3_250, 180), f"{label} levelling bed {index}", GROUND, (0, y, level - 90)))
        elif product_id == "STN-CIV-P030":
            edge = y - 1_650 if y > 0 else y + 1_650
            children.append(_box((length, 220, 260), f"{label} grated channel {index}", STEEL, (0, edge, level + 120)))
            for x in (-length * 0.35, length * 0.35):
                children.append(_part(Cylinder(180, 800), f"{label} catch pit {index}", CONCRETE).locate(Location((x, edge, level - 400))))
        elif product_id == "STN-CIV-P040":
            edge = y - 1_500 if y > 0 else y + 1_500
            children.extend([
                _box((length, 320, 650), f"{label} edge beam {index}", CONCRETE, (0, edge, level + 325)),
                _box((length, 240, 240), f"{label} service trough {index}", STEEL, (0, edge + (420 if y > 0 else -420), level + 120)),
            ])
        elif product_id == "STN-PLT-P010":
            edge = y - 1_500 if y > 0 else y + 1_500
            children.extend([
                _box((length, 420, 80), f"{label} coping {index}", CONCRETE, (0, edge, level + 460)),
                _box((length, 320, 35), f"{label} tactile strip {index}", SAFETY, (0, edge + (360 if y > 0 else -360), level + 505)),
            ])
    return Compound(label=label, children=children)


def _canopy(product_id: str, parameters: dict[str, Any], label: str) -> Compound:
    length = float(parameters["platform_length_m"]) * 1000.0
    centres = _platform_centres(parameters)
    children: list[Part] = []
    for platform, (y, level) in enumerate(centres, start=1):
        roof_z = level + 3_900
        if product_id == "STN-CNP-P010":
            for x in (-length * 0.40, -length * 0.20, 0.0, length * 0.20, length * 0.40):
                children.extend([
                    _box((180, 180, 3_400), f"{label} column {platform}", STEEL, (x, y, level + 1_700)),
                    _box((180, 3_600, 220), f"{label} rafter {platform}", STEEL, (x, y, roof_z - 150)),
                    _box((500, 120, 500), f"{label} knee brace {platform}", STEEL, (x, y - 1_350, level + 3_100)),
                ])
        elif product_id == "STN-CNP-P020":
            for x in (-length * 0.40, -length * 0.20, 0.0, length * 0.20, length * 0.40):
                children.extend([
                    _box((900, 900, 350), f"{label} provisional pad {platform}", CONCRETE, (x, y, level - 175)),
                    _box((360, 360, 35), f"{label} base plate {platform}", STEEL, (x, y, level + 18)),
                ])
                for dx in (-130, 130):
                    for dy in (-130, 130):
                        children.append(_part(Cylinder(18, 420), f"{label} anchor bolt {platform}", STEEL).locate(Location((x + dx, y + dy, level))))
        elif product_id in {"STN-CNP-P030", "STN-CNP-P050"}:
            width = 4_200 if product_id == "STN-CNP-P030" else 8_500
            children.extend([
                _box((length, width, 160), f"{label} sandwich roof {platform}", STEEL, (0, y, roof_z)),
                _box((length * 0.92, width * 0.86, 45), f"{label} PV laminate {platform}", PV, (0, y, roof_z + 105)),
            ])
        elif product_id in {"STN-CNP-P040", "STN-CNP-P080"}:
            children.extend([
                _box((length * 0.88, 80, 80), f"{label} DC route {platform}", SYSTEM, (0, y, roof_z + 170)),
                _box((110, 110, 3_300), f"{label} protected downlink {platform}", SAFETY, (length * 0.38, y, level + 1_650)),
            ])
        elif product_id == "STN-CNP-P090":
            children.extend([
                _box((length, 180, 180), f"{label} gutter {platform}", STEEL, (0, y + 2_100, roof_z - 50)),
                _box((140, 140, 3_400), f"{label} downpipe {platform}", STEEL, (length * 0.42, y + 2_100, level + 1_700)),
                _box((length * 0.75, 650, 80), f"{label} maintenance walkway {platform}", SAFETY, (0, y, roof_z + 160)),
            ])
    if product_id == "STN-CNP-P060":
        span = 22_000.0
        for x in (-length * 0.35, 0.0, length * 0.35):
            children.extend([
                _box((220, 220, 4_500), f"{label} north column", STEEL, (x, -span / 2, 2_250)),
                _box((220, 220, 4_500), f"{label} south column", STEEL, (x, span / 2, 2_250)),
                _box((220, span, 220), f"{label} bottom chord", STEEL, (x, 0, 4_350)),
                _box((220, span, 220), f"{label} top chord", STEEL, (x, 0, 5_050)),
            ])
            for segment in range(-4, 5):
                children.append(_box((160, 2_600, 160), f"{label} alternating web", STEEL, (x, segment * 2_400, 4_700)))
    if product_id == "STN-CNP-P070":
        for x in (-length * 0.35, 0.0, length * 0.35):
            for y in (-11_000.0, 11_000.0):
                children.extend([
                    _box((1_400, 1_400, 450), f"{label} provisional pad", CONCRETE, (x, y, -225)),
                    _box((420, 420, 40), f"{label} anchor template", STEEL, (x, y, 20)),
                ])
    return Compound(label=label, children=children)


def _turnout(product_id: str, label: str) -> Compound:
    children: list[Part] = []
    if product_id == "STN-TRK-P010":
        for y in (-717.5, 717.5):
            children.append(_box((27_000, 75, 172), f"{label} stock rail", STEEL, (0, y, 300)))
        for side in (-1, 1):
            for segment in range(12):
                x = -9_500 + segment * 650
                y = side * (450 + segment * 24)
                children.append(_box((700, 48, 130), f"{label} tapered switch/closure segment", STEEL, (x, y, 315)))
    elif product_id == "STN-TRK-P020":
        children.extend([
            _box((1_500, 1_100, 180), f"{label} crossing frog", STEEL, (8_000, 0, 310)),
            _box((5_000, 70, 150), f"{label} left check rail", STEEL, (5_500, -520, 310)),
            _box((5_000, 70, 150), f"{label} right check rail", STEEL, (5_500, 520, 310)),
            _box((2_300, 65, 80), f"{label} stretcher bar", SAFETY, (-7_500, 0, 180)),
            _box((520, 320, 260), f"{label} mechanical lock", SAFETY, (-7_500, 1_100, 260)),
        ])
    elif product_id == "STN-TRK-P030":
        for index in range(21):
            children.append(_box((260, 3_200 + index * 70, 210), f"{label} sleeper {index + 1}", CONCRETE, (-12_000 + index * 1_200, 0, 105)))
        for x in (-9_000, -3_000, 3_000, 9_000):
            for y in (-717.5, 717.5):
                children.append(_box((280, 260, 55), f"{label} slide chair/fastener", STEEL, (x, y, 235)))
    elif product_id == "STN-TRK-P040":
        children.append(_equipment(label, (-7_500, 1_900, 520), (1_250, 650, 650)))
    elif product_id == "STN-TRK-P050":
        children.extend([
            _equipment(f"{label} normal detector", (-8_200, -1_200, 420), (360, 220, 240)),
            _equipment(f"{label} reverse detector", (-6_800, -1_200, 420), (360, 220, 240)),
            _box((5_000, 90, 90), f"{label} protected harness route", SYSTEM, (-5_500, -1_500, 220)),
        ])
    elif product_id == "STN-TRK-P060":
        children.extend([
            _box((7_800, 70, 45), f"{label} stock-rail heater", SAFETY, (-6_000, -680, 220)),
            _box((7_800, 70, 45), f"{label} switch-rail heater", SAFETY, (-6_000, 680, 220)),
            _equipment(f"{label} isolation cabinet", (-4_000, 2_100, 620), (650, 420, 900)),
        ])
    elif product_id == "STN-TRK-P070":
        children.extend([
            _box((1_100, 3_200, 1_000), f"{label} stop block", STEEL, (12_500, 0, 500)),
            _box((180, 180, 2_000), f"{label} marker post", STEEL, (13_400, 0, 1_000)),
            _box((700, 700, 350), f"{label} foundation interface", CONCRETE, (13_400, 0, -175)),
        ])
    return Compound(label=label, children=children).locate(Location((0.0, 0.0, TURNOUT_TO_STATION_Z_MM)))


def _depot(product_id: str, label: str) -> Compound:
    children: list[Part | Compound] = []
    if product_id == "STN-DEP-P010":
        children.extend([
            _box((100_000, 80_000, 280), f"{label} formation", GROUND, (85_000, 0, -140)),
            _box((90_000, 6_000, 180), f"{label} service road", STEEL, (85_000, 31_000, 90)),
            _box((90_000, 300, 420), f"{label} main drain", CONCRETE, (85_000, -31_000, -100)),
        ])
    elif product_id == "STN-DEP-P020":
        for y in (-12_000, -4_000, 4_000, 12_000):
            for offset in (-717.5, 717.5):
                children.append(_box((78_000, 75, 172), f"{label} running rail", STEEL, (88_000, y + offset, 300)))
        children.extend([
            _box((24_000, 1_400, 1_200), f"{label} inspection pit", CONCRETE, (75_000, -4_000, -600)),
            _box((18_000, 1_800, 700), f"{label} wash/recovery channel", CONCRETE, (75_000, 4_000, -350)),
        ])
    elif product_id == "STN-DEP-P030":
        return _turnout("STN-TRK-P010", label)
    elif product_id == "STN-DEP-P040":
        for y in (-12_000, -4_000, 4_000, 12_000):
            children.append(_equipment(f"{label} stall", (58_000, y + 2_500, 900), (900, 650, 1_400)))
            children.append(_box((2_800, 100, 100), f"{label} suspended cable reel", SAFETY, (59_400, y + 1_600, 2_200)))
    elif product_id == "STN-DEP-P050":
        children.extend([
            _box((42_000, 24_000, 180), f"{label} PV canopy", PV, (88_000, 20_000, 7_500)),
            _equipment(f"{label} inverter/switchgear", (110_000, 20_000, 1_200), (3_000, 1_500, 2_200)),
            _equipment(f"{label} stationary battery", (114_000, 20_000, 1_400), (4_000, 2_200, 2_600)),
        ])
    elif product_id == "STN-DEP-P060":
        children.extend([
            _box((48_000, 34_000, 8_000), f"{label} workshop envelope", Color(0.55, 0.60, 0.65, 0.22), (92_000, 0, 4_000)),
            _box((30_000, 400, 500), f"{label} crane runway north", STEEL, (92_000, -12_000, 7_000)),
            _box((30_000, 400, 500), f"{label} crane runway south", STEEL, (92_000, 12_000, 7_000)),
            _box((3_500, 3_500, 2_500), f"{label} wheel-lathe cell", SYSTEM, (104_000, 0, 1_250)),
            _box((10_000, 5_000, 3_000), f"{label} stores/racking zone", SAFETY, (75_000, 11_000, 1_500)),
            depot_bogie_change_bay(top_of_rail_z_mm=TOP_OF_RAIL_Z_MM).locate(Location((90_000, -8_000, 0.0))),
        ])
    elif product_id == "STN-DEP-P070":
        children.extend([
            _box((42_000, 180, 180), f"{label} overhead services spine", SYSTEM, (92_000, 0, 6_500)),
            _box((42_000, 90, 90), f"{label} compressed-air ring", SAFETY, (92_000, -10_000, 5_800)),
            _box((42_000, 90, 90), f"{label} fire-main route", Color(0.75, 0.08, 0.06), (92_000, 10_000, 5_800)),
        ])
    return Compound(label=label, children=children)


def station_product_geometry(item: dict[str, Any], parameters: dict[str, Any]) -> Compound:
    """Return one coordinated product representation at station coordinates."""

    product_id = str(item["id"])
    label = f"{product_id} {item['title']}"
    if product_id not in _SEMANTICS:
        raise KeyError(f"no station geometry specification for {product_id}")
    if product_id.startswith("STN-CIV-") or product_id == "STN-PLT-P010":
        return _platform_parts(product_id, parameters, label)
    if product_id.startswith("STN-CNP-"):
        return _canopy(product_id, parameters, label)
    if product_id.startswith("STN-TRK-"):
        return _turnout(product_id, label)
    if product_id.startswith("STN-DEP-"):
        return _depot(product_id, label)

    length = float(parameters["platform_length_m"]) * 1000.0
    anchor_x = -length * 0.36
    if product_id == "STN-MEP-P010":
        return _equipment(label, (anchor_x, 8_500, 1_100), (2_200, 1_200, 2_000))
    if product_id == "STN-MEP-P020":
        return _equipment(label, (anchor_x + 2_800, 8_500, 1_100), (2_400, 900, 2_000))
    if product_id == "STN-MEP-P030":
        return Compound(label=label, children=[
            _box((1_800, 140, 90), f"{label} maintained luminaire", SAFETY, (x, y, z + 3_300))
            for x in (-length * 0.30, 0.0, length * 0.30)
            for y, z in _platform_centres(parameters)
        ])
    if product_id == "STN-MEP-P040":
        return Compound(label=label, children=[
            _equipment(f"{label} alarm panel", (anchor_x + 5_600, 8_500, 900), (700, 350, 1_400)),
            _part(Cylinder(110, 220), f"{label} detector", SAFETY).locate(Location((0, 5_000, 3_300))),
            _box((500, 180, 700), f"{label} extinguisher/sign", SAFETY, (2_000, 7_000, 700)),
        ])
    if product_id == "STN-PAX-P010":
        return _equipment(label, (anchor_x + 6_800, 8_500, 1_050), (800, 800, 1_900))
    if product_id == "STN-PAX-P020":
        return Compound(label=label, children=[
            _box((1_600, 140, 750), f"{label} display", SYSTEM, (0, y, z + 2_400))
            for y, z in _platform_centres(parameters)
        ])
    if product_id == "STN-PAX-P030":
        return Compound(label=label, children=[
            _part(Cylinder(180, 260), f"{label} CCTV/PA node", SYSTEM).locate(Location((x, y, z + 3_100)))
            for x in (-length * 0.25, length * 0.25)
            for y, z in _platform_centres(parameters)
        ] + [_box((length * 0.8, 80, 80), f"{label} LAN backbone", SYSTEM, (0, 8_000, 2_800))])
    if product_id == "STN-PAX-P040":
        return Compound(label=label, children=[
            _box((1_000, 180, 1_150), f"{label} gate pedestal", STEEL, (anchor_x + index * 1_300, -8_000, 575))
            for index in range(min(6, max(2, int(float(item["quantity"])))))
        ] + [_box((8_000, 2_000, 2_200), f"{label} operating/egress clearance", Color(0.25, 0.55, 0.80, 0.18), (anchor_x + 3_000, -8_000, 1_100))])
    if product_id == "STN-PAX-P050":
        return _equipment(label, (anchor_x, -10_500, 900), (1_000, 700, 1_700))
    if product_id == "STN-PAX-P060":
        return Compound(label=label, children=[
            _box((2_000, 650, 850), f"{label} bench", STEEL, (x, y, z + 425))
            for x in (-length * 0.20, length * 0.20)
            for y, z in _platform_centres(parameters)
        ] + [_box((1_500, 1_500, 25), f"{label} wheelchair zone", SAFETY, (0, _platform_centres(parameters)[0][0], _platform_centres(parameters)[0][1] + 475))])
    if product_id in {"STN-PAX-P070", "STN-PAX-P080"}:
        width = 1_000 if product_id == "STN-PAX-P070" else 1_200
        return Compound(label=label, children=[
            _box((width, 650, 180), f"{label} rolled plinth", STEEL, (anchor_x, -8_000 if product_id.endswith("070") else -10_500, 90)),
            _box((width * 0.55, 300, 120), f"{label} protected cable void", SYSTEM, (anchor_x, -8_000 if product_id.endswith("070") else -10_500, 120)),
        ])
    if product_id == "STN-ACC-P010":
        return Compound(label=label, children=[
            _box((12_000, 3_000, 250), f"{label} step-free approach", CONCRETE, (-length / 2 - 5_000, -5_000, 125)),
            _box((12_000, 180, 1_100), f"{label} protected boundary", STEEL, (-length / 2 - 5_000, -6_500, 550)),
        ])
    if product_id == "STN-ACC-P020":
        return Compound(label=label, children=[
            _box((3_500, 3_500, 18_000), f"{label} lift/stair core", Color(0.60, 0.68, 0.72, 0.35), (-10_000 + index * 7_000, 0, 9_000))
            for index in range(min(4, int(float(item["quantity"]))))
        ] + [_box((4_200, 4_200, 3_500), f"{label} maintenance clearance", Color(0.25, 0.55, 0.80, 0.18), (-10_000, 0, 18_000))])
    if product_id == "STN-ACC-P030":
        return Compound(label=label, children=[
            _box((5_000, 24_000, 650), f"{label} bridge deck", STEEL, (0, 0, 13_000)),
            _box((5_000, 24_000, 3_000), f"{label} glazed enclosure", GLASS, (0, 0, 14_800)),
            _box((6_000, 25_000, 180), f"{label} roof", STEEL, (0, 0, 16_400)),
        ])
    if product_id == "STN-CHG-P010":
        return Compound(label=label, children=[
            _equipment(f"{label} cabinet", (length * 0.34, 8_500, 1_200), (2_000, 1_000, 2_200)),
            _box((4_500, 120, 120), f"{label} protected charge cable", SAFETY, (length * 0.34, 6_300, 900)),
            _box((900, 650, 1_100), f"{label} wayside connector/shutter", STEEL, (length * 0.34, 4_600, 900)),
        ])
    if product_id == "STN-CHG-P020":
        return Compound(label=label, children=[
            _equipment(f"{label} transformer", (length * 0.26, 11_500, 1_400), (3_000, 2_200, 2_600)),
            _equipment(f"{label} rectifier/protection", (length * 0.33, 11_500, 1_300), (2_400, 1_500, 2_400)),
        ])
    raise AssertionError(f"unimplemented station geometry for {product_id}")


def flatten_geometry(value: Part | Compound) -> list[Part]:
    if isinstance(value, Compound):
        result: list[Part] = []
        for child in value.children:
            result.extend(flatten_geometry(child))
        return result
    return [value]


__all__ = [
    "PLATFORM_SURFACE_Z_MM",
    "PLATFORM_TO_TOR_HEIGHT_MM",
    "TOP_OF_RAIL_Z_MM",
    "StationGeometrySpec",
    "flatten_geometry",
    "geometry_specs",
    "station_product_geometry",
]
