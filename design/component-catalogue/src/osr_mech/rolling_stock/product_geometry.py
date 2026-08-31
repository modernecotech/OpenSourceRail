"""Controlled design-reference geometry for every LM3 product-tree item.

The product manifest is the EBOM/MBOM authority.  This module supplies the
shared geometric representation used by the per-part FreeCAD and IFC files.
It deliberately models inspectable manufacturing envelopes, interfaces and
major members rather than inventing supplier-internal detail or claiming that
these are released production drawings.
"""

from __future__ import annotations

from dataclasses import dataclass

from osr_mech.cad import Axis, Box, Color, Compound, Cylinder, Location, Part


STEEL = Color(0.38, 0.43, 0.48)
COMPOSITE = Color(0.84, 0.87, 0.88)
GLASS = Color(0.24, 0.55, 0.72, 0.55)
SYSTEM = Color(0.18, 0.39, 0.68)
SAFETY = Color(0.90, 0.48, 0.10)
ELASTOMER = Color(0.08, 0.08, 0.09)
INTERIOR = Color(0.69, 0.74, 0.78)


@dataclass(frozen=True)
class ProductGeometrySpec:
    product_id: str
    form: str
    envelope_mm: tuple[float, float, float]
    representation: str


_SPECS: dict[str, ProductGeometrySpec] = {}


def _register(ids: str, form: str, envelope: tuple[float, float, float], representation: str) -> None:
    for product_id in ids.split():
        if product_id in _SPECS:
            raise ValueError(f"duplicate geometry specification for {product_id}")
        _SPECS[product_id] = ProductGeometrySpec(product_id, form, envelope, representation)


# Primary body, exterior and end structures. Dimensions are controlled review
# envelopes in millimetres, not supplier tolerances or NC geometry.
_register("LM3-BDY-P010", "beam", (16_000, 180, 260), "one side-sill member with end datum faces")
_register("LM3-BDY-P020", "underframe", (15_800, 2_650, 380), "centre spine and repeated cross-bearers")
_register("LM3-BDY-P030", "bolster", (1_700, 2_650, 420), "bolster box, spring pads and pivot land")
_register("LM3-BDY-P040", "coupler-pocket", (1_250, 1_100, 620), "coupler pocket and crash-can shear structure")
_register("LM3-BDY-P050", "tray", (6_200, 900, 520), "battery support rails, vent plenum and service gutter")
_register("LM3-BDY-P060", "floor", (15_600, 2_650, 460), "low-floor pan and raised bogie-end decks")
_register("LM3-BDY-P070", "side-frame", (15_800, 180, 2_850), "posts, door portals, waist and cant rails")
_register("LM3-BDY-P080", "roof-rack", (15_600, 2_500, 360), "roof bows and equipment/cable rails")
_register("LM3-BDY-P090", "frame", (2_700, 260, 2_900), "end ring and anti-climber datum")
_register("LM3-END-P060", "frame", (2_650, 280, 2_650), "reversible end carrier and option bolt grid")
_register("LM3-END-P061", "cowl", (1_250, 2_650, 2_650), "panoramic closeout, glass carrier and sensor datums")
_register("LM3-END-P062", "bellows", (1_300, 2_100, 2_350), "open portal, clamp, threshold and drain option")
_register("LM3-BDY-P100 LM3-DOOR-P010", "door-frame", (1_500, 260, 2_150), "door carrier/portal with threshold and four-point datum")
_register("LM3-BDY-P110 LM3-WIN-P010", "window-frame", (1_650, 140, 1_250), "replaceable glazing pressure frame, seal and drain")
_register("LM3-BDY-P120", "recovery-kit", (1_600, 900, 280), "jacking, lifting and towing interface kit")
_register("LM3-BDY-P130", "body-module", (1_000, 120, 3_050), "one-metre clip-on side/roof module with solid attachment lands")
_register("LM3-BDY-P140", "rail-kit", (15_800, 180, 160), "keyed clip rail, retainers and dry-seal route")
_register("LM3-ROOF-P010", "roof-equipment", (2_800, 1_800, 420), "HVAC curb, duct collar, tray and drains")
_register("LM3-ROOF-P020", "rail-kit", (14_000, 2_300, 140), "PV rails, bonded pads, jumpers and isolation datums")

# Multipart moulded end cowl.
_register("LM3-CWL-P010", "cowl-kit", (2_900, 2_800, 3_050), "laminate/insert material kit represented by the complete cowl envelope")
_register("LM3-CWL-P011", "cowl", (1_250, 2_750, 720), "upper brow and roof-cap cast")
_register("LM3-CWL-P012 LM3-CWL-P013", "cowl", (1_150, 700, 2_300), "handed cheek cast")
_register("LM3-CWL-P014", "cowl", (1_000, 2_650, 760), "lower apron and anti-climber cover cast")
_register("LM3-CWL-P015", "cowl-service", (650, 520, 420), "lamp/washer/service-hatch cast set")
_register("LM3-CWL-P016", "frame", (720, 120, 720), "backing-ring flange cast")

# Bogie, suspension and running gear.
_register("LM3-ART-P010", "frame", (2_400, 300, 2_400), "articulation adapter and anti-lift interface")
_register("LM3-BOG-P010 LM3-BOG-P020", "bogie-frame", (3_400, 2_500, 620), "welded H-frame with axlebox and bolster datums")
_register("LM3-BOG-P030 LM3-BOG-P031", "bogie-guards", (3_200, 2_350, 460), "guards, cable guides, brackets and covers")
_register("LM3-BOG-P050", "link-kit", (1_400, 420, 300), "motor torque link, stop and lanyard bracket")
_register("LM3-BOG-P060 LM3-BOG-P061", "harness", (3_000, 2_100, 220), "bogie harness route and junction brackets")
_register("LM3-BOG-P040 LM3-BOG-P041", "wheelset", (1_850, 2_200, 920), "wheelset, axle and axle-mounted brake discs")
_register("LM3-BOG-P042 LM3-BOG-P043", "axlebox", (820, 620, 620), "paired axleboxes, bearings and sensor datums")
_register("LM3-BOG-P044 LM3-BOG-P045", "spring-set", (1_800, 2_100, 520), "primary springs, guides and bump stops")
_register("LM3-BOG-P046 LM3-BOG-P047", "spring-set", (1_900, 2_200, 650), "secondary air/emergency springs, pivot, yaw links and dampers")
_register("LM3-BOG-P048 LM3-BOG-P049", "brake-kit", (2_100, 2_200, 520), "calipers, actuators, pads and WSP hardware")
_register("LM3-AUX-P010", "pneumatic-kit", (1_300, 850, 720), "compressor, dryer, reservoir and manifold")

# Bought-in exterior/interior systems and repeatable local interfaces.
_register("LM3-EXT-P010", "door-cassette", (1_350, 260, 2_050), "supplier door cassette envelope with twin leaves and drive")
_register("LM3-EXT-P020", "window", (1_520, 90, 1_100), "laminated side glazing cassette")
_register("LM3-EXT-P030", "window", (2_300, 110, 1_450), "heated panoramic end glazing")
_register("LM3-EXT-P040", "hvac", (2_600, 1_900, 620), "roof HVAC casing, fans and curb interface")
_register("LM3-EXT-P050", "pv", (1_700, 1_050, 45), "PV laminate and edge-clamp datums")
_register("LM3-EXT-P060", "floor-panel", (1_000, 1_300, 35), "numbered floor board/removable hatch module")
_register("LM3-EXT-P061", "floor-covering", (1_000, 1_300, 6), "resilient covering and welded-seam allowance")
_register("LM3-EXT-P062", "seat", (1_550, 620, 980), "longitudinal passenger-seat module and rail saddles")
_register("LM3-EXT-P063", "handrail", (2_300, 2_300, 2_050), "grab poles, rails and repeated adapters")
_register("LM3-EXT-P064", "pis", (1_100, 220, 420), "display, loudspeaker and amplifier module")
_register("LM3-EXT-P065", "camera-kit", (650, 420, 260), "CCTV/intercom modules and mounting datums")
_register("LM3-EXT-P066", "emergency-kit", (1_200, 650, 600), "PRM controls, signs, lamps and emergency equipment")
_register("LM3-FIX-P010", "service-rail", (15_000, 42, 18), "OSR-RAIL-42 extrusion with repeated datum marks")
_register("LM3-FIX-P020", "fastener-kit", (520, 360, 160), "four captive fastener families and isolators")
_register("LM3-FIX-P030", "adapter-kit", (520, 420, 180), "seat, handrail and equipment adapter variants")
_register("LM3-LGT-P010", "light", (1_200, 95, 45), "plug-in main LED cassette and captive mount")
_register("LM3-LGT-P020", "light-kit", (900, 360, 120), "emergency/doorway luminaires and keyed feeder")
_register("LM3-EXT-P070", "roof-equipment", (2_400, 1_500, 260), "antennas, walkway pads, covers and labels")
_register("LM3-EXT-P080", "body-module", (1_000, 120, 3_050), "side-module laminate/core material represented at cured envelope")
_register("LM3-EXT-P090", "roof-rack", (1_000, 2_700, 180), "roof-module laminate, seal and removable skirt envelope")
_register("LM3-INT-P010", "duct-kit", (6_000, 2_400, 320), "diffusers, returns, grilles and access panels")
_register("LM3-INT-P020", "liner", (1_000, 2_650, 260), "ceiling liner, light trough and plenum cover")
_register("LM3-INT-P030", "liner", (1_000, 140, 2_200), "sidewall liner, reveal and cable-cover panel")
_register("LM3-INT-P040", "liner", (4_800, 720, 780), "battery strake/seat-base/service-hatch shells")
_register("LM3-INT-P050", "liner", (1_100, 420, 1_050), "vestibule, PRM and door-pocket trim set")

# Traction, energy, controls and train-end interfaces.
_register("LM3-TRC-P010", "motor", (1_050, 720, 720), "axle traction motor with shaft and terminal box")
_register("LM3-TRC-P020", "gearbox", (760, 620, 620), "single-stage gearbox and coupling envelope")
_register("LM3-TRC-P030", "power-electronics", (2_200, 1_200, 620), "dual motor controllers and isolated auxiliaries")
_register("LM3-TRC-P040", "battery", (5_200, 780, 720), "side traction battery enclosure and module rows")
_register("LM3-HV-P010", "tray", (5_400, 900, 320), "sliding trays, retention and drain pan")
_register("LM3-HV-P020", "cable-tray", (14_000, 420, 180), "segregated HV tray, covers, grommets and studs")
_register("LM3-HV-P030", "piping", (6_500, 950, 260), "coolant manifolds, clamps and bleed/drain points")
_register("LM3-TRC-P050", "resistor", (1_900, 750, 420), "regen resistor bank and thermal shield")
_register("LM3-TRC-P060", "charger", (1_050, 620, 540), "side-pin connector, shutter, actuator and target")
_register("LM3-TRC-P070", "hv-panel", (1_500, 420, 1_050), "contactor/fuse/precharge/disconnect panel")
_register("LM3-SAF-P010", "fire-kit", (1_600, 900, 520), "detectors, mist reservoir/pump and distribution")
_register("LM3-END-P010", "coupler", (1_850, 760, 620), "automatic coupler and crash absorber")
_register("LM3-ART-P020", "pivot", (780, 780, 520), "lower spherical pivot, housing and pin")
_register("LM3-ART-P021", "link-kit", (1_200, 1_500, 420), "upper yaw links and retained spherical joints")
_register("LM3-ART-P022", "bellows", (1_100, 2_100, 2_300), "double-wall bellows and clamp frames")
_register("LM3-ART-P023", "bridge", (1_250, 1_850, 260), "passenger bridge, turntable and interior panels")
_register("LM3-ART-P024", "harness", (1_300, 1_600, 320), "trainline carrier, support arms and drains")
_register("LM3-CTRL-P010", "control-cabinet", (1_200, 550, 1_350), "train compute and safety-control cabinets")
_register("LM3-CTRL-P020", "sensor-kit", (1_500, 1_100, 420), "navigation, radio, GNSS/IMU and antenna kit")
_register("LM3-CTRL-P030", "control-panel", (1_100, 550, 650), "maintenance/depot/emergency controls and relays")
_register("LM3-CTRL-P040", "harness", (8_000, 2_000, 240), "LV trainline harness and distribution cabinets")
_register("LM3-CTRL-P050", "recorder", (520, 420, 280), "operational/crashworthy recorder modules")
_register("LM3-END-P020", "sensor-pack", (1_050, 1_850, 520), "T-OBS sensors, heated services and washer")
_register("LM3-END-P030", "cowl-service", (900, 700, 420), "service hatch, backing bracket and clipped services")
_register("LM3-END-P040", "harness", (1_700, 900, 260), "end jumper, recovery trainline and breakaway")
_register("LM3-END-P050", "lamp-kit", (1_600, 900, 280), "head/tail/marker/threshold lamps and harness")
_register("LM3-ART-P030", "harness", (1_400, 1_600, 360), "inter-car jumpers, hoses, energy chain and drain sleeve")
_register("LM3-ART-P040", "bellows", (1_450, 2_250, 2_400), "open-end gangway, drawbar and turntable cassette")
_register("LM3-ART-P041", "harness", (1_200, 850, 260), "transition harness, blanking and dust-cover kit")


def geometry_specs() -> dict[str, ProductGeometrySpec]:
    return dict(_SPECS)


def _part(shape: Part, label: str, colour: Color) -> Part:
    shape.label = label
    shape.color = colour
    return shape


def _box(dims: tuple[float, float, float], label: str, colour: Color = STEEL) -> Part:
    return _part(Box(*dims), label, colour)


def _frame(dims: tuple[float, float, float], label: str, colour: Color = STEEL) -> Compound:
    x, y, z = dims
    member = min(140.0, max(45.0, min(x, z) * 0.10))
    pieces = [
        _box((member, y, z), f"{label} left jamb", colour).locate(Location((-(x - member) / 2, 0, 0))),
        _box((member, y, z), f"{label} right jamb", colour).locate(Location(((x - member) / 2, 0, 0))),
        _box((x - 2 * member, y, member), f"{label} head", colour).locate(Location((0, 0, (z - member) / 2))),
        _box((x - 2 * member, y, member), f"{label} sill", colour).locate(Location((0, 0, -(z - member) / 2))),
    ]
    return Compound(label=label, children=pieces)


def _wheelset(dims: tuple[float, float, float], label: str) -> Compound:
    x, y, z = dims
    wheel_radius = z / 2
    wheel_width = min(150.0, y * 0.08)
    axle = _part(Cylinder(85, y - wheel_width).rotate(Axis.X, 90), f"{label} axle", STEEL)
    wheels = []
    for side in (-1, 1):
        wheels.append(
            _part(Cylinder(wheel_radius, wheel_width).rotate(Axis.X, 90), f"{label} wheel", ELASTOMER).locate(
                Location((0, side * (y - wheel_width) / 2, 0))
            )
        )
        wheels.append(
            _part(Cylinder(wheel_radius * 0.68, 35).rotate(Axis.X, 90), f"{label} brake disc", SAFETY).locate(
                Location((0, side * (y * 0.32), 0))
            )
        )
    del x
    return Compound(label=label, children=[axle, *wheels])


def _bogie_frame(dims: tuple[float, float, float], label: str) -> Compound:
    x, y, z = dims
    parts = []
    for side in (-1, 1):
        parts.append(_box((x, 220, z * 0.55), f"{label} side frame").locate(Location((0, side * (y - 220) / 2, 0))))
    for longitudinal in (-1, 0, 1):
        parts.append(_box((260, y - 300, z * 0.45), f"{label} cross member").locate(Location((longitudinal * x * 0.34, 0, 0))))
    return Compound(label=label, children=parts)


def _underframe(dims: tuple[float, float, float], label: str) -> Compound:
    x, y, z = dims
    parts = [_box((x, 220, z), f"{label} centre spine")]
    for station in (-0.46, -0.31, -0.16, 0.0, 0.16, 0.31, 0.46):
        parts.append(_box((180, y, z * 0.72), f"{label} cross bearer").locate(Location((station * x, 0, 0))))
    return Compound(label=label, children=parts)


def _side_frame(dims: tuple[float, float, float], label: str) -> Compound:
    x, y, z = dims
    parts = [
        _box((x, y, 120), f"{label} waist rail"),
        _box((x, y, 120), f"{label} cant rail").locate(Location((0, 0, z * 0.46))),
        _box((x, y, 120), f"{label} floor rail").locate(Location((0, 0, -z * 0.46))),
    ]
    for station in (-0.45, -0.30, -0.15, 0.0, 0.15, 0.30, 0.45):
        parts.append(_box((100, y, z), f"{label} post").locate(Location((station * x, 0, 0))))
    return Compound(label=label, children=parts)


def _spring_set(dims: tuple[float, float, float], label: str) -> Compound:
    x, y, z = dims
    parts = []
    for px in (-x * 0.32, x * 0.32):
        for py in (-y * 0.36, y * 0.36):
            parts.append(_part(Cylinder(min(x, y) * 0.12, z), f"{label} spring", ELASTOMER).locate(Location((px, py, 0))))
    parts.append(_box((x * 0.65, y * 0.35, z * 0.18), f"{label} pivot/yaw interface", SAFETY))
    return Compound(label=label, children=parts)


def _motor(dims: tuple[float, float, float], label: str) -> Compound:
    x, y, z = dims
    body = _part(Cylinder(min(x, z) * 0.42, y * 0.72).rotate(Axis.X, 90), f"{label} stator housing", SYSTEM)
    shaft = _part(Cylinder(min(x, z) * 0.12, y).rotate(Axis.X, 90), f"{label} shaft", STEEL)
    terminal = _box((x * 0.35, y * 0.32, z * 0.25), f"{label} terminal box", SAFETY).locate(Location((0, 0, z * 0.34)))
    return Compound(label=label, children=[body, shaft, terminal])


def _bellows(dims: tuple[float, float, float], label: str) -> Compound:
    x, y, z = dims
    parts = []
    for index in range(7):
        px = -x / 2 + (index + 0.5) * x / 7
        ring = _frame((y, max(35.0, x / 18), z), f"{label} corrugation", ELASTOMER).rotate(Axis.Z, 90)
        parts.append(ring.locate(Location((px, 0, 0))))
    return Compound(label=label, children=parts)


def _seat(dims: tuple[float, float, float], label: str) -> Compound:
    x, y, z = dims
    return Compound(
        label=label,
        children=[
            _box((x, y, z * 0.18), f"{label} cushion", INTERIOR).locate(Location((0, 0, -z * 0.18))),
            _box((x, z * 0.12, z * 0.62), f"{label} back", INTERIOR).locate(Location((0, y * 0.34, z * 0.18))),
            _box((x * 0.86, y * 0.72, z * 0.10), f"{label} common-rail saddle", STEEL).locate(Location((0, 0, -z * 0.43))),
        ],
    )


def _equipment(dims: tuple[float, float, float], label: str, colour: Color = SYSTEM) -> Compound:
    x, y, z = dims
    return Compound(
        label=label,
        children=[
            _box((x, y, z * 0.82), f"{label} enclosure", colour),
            _box((x * 0.82, y * 0.12, z * 0.12), f"{label} mounting datum", STEEL).locate(Location((0, -y * 0.44, -z * 0.42))),
            _box((x * 0.24, y * 0.14, z * 0.16), f"{label} keyed service interface", SAFETY).locate(Location((x * 0.30, y * 0.40, 0))),
        ],
    )


def product_geometry(product_id: str, title: str | None = None) -> Compound:
    """Return an inspectable native/facade geometry for one controlled item."""

    try:
        spec = _SPECS[product_id]
    except KeyError as exc:
        raise KeyError(f"no controlled LM3 geometry for {product_id}") from exc
    label = title or product_id
    dims = spec.envelope_mm
    form = spec.form

    if form in {"frame", "window-frame", "door-frame"}:
        return _frame(dims, label, STEEL)
    if form == "window":
        frame = _frame(dims, f"{label} retention", STEEL)
        pane = _box((dims[0] * 0.82, dims[1] * 0.45, dims[2] * 0.82), f"{label} glass", GLASS)
        return Compound(label=label, children=[*frame.children, pane])
    if form == "door-cassette":
        frame = _frame(dims, f"{label} cassette", STEEL)
        leaf_width = dims[0] * 0.42
        leaves = [
            _box((leaf_width, dims[1] * 0.45, dims[2] * 0.83), f"{label} leaf", COMPOSITE).locate(Location((side * dims[0] * 0.23, 0, 0)))
            for side in (-1, 1)
        ]
        return Compound(label=label, children=[*frame.children, *leaves])
    if form == "wheelset":
        return _wheelset(dims, label)
    if form == "bogie-frame":
        return _bogie_frame(dims, label)
    if form == "underframe":
        return _underframe(dims, label)
    if form == "side-frame":
        return _side_frame(dims, label)
    if form == "spring-set":
        return _spring_set(dims, label)
    if form == "motor":
        return _motor(dims, label)
    if form == "bellows":
        return _bellows(dims, label)
    if form == "seat":
        return _seat(dims, label)
    if form in {"light", "service-rail", "beam", "floor-panel", "floor-covering", "body-module", "liner"}:
        colour = INTERIOR if form in {"floor-covering", "liner", "seat"} else COMPOSITE if form == "body-module" else STEEL
        return Compound(label=label, children=[_box(dims, label, colour)])
    if form == "pv":
        return Compound(label=label, children=[_box(dims, f"{label} laminate", GLASS), _box((dims[0], dims[1] * 0.06, dims[2] * 0.90), f"{label} edge clamp", STEEL)])
    if form in {"roof-rack", "rail-kit", "cable-tray", "harness", "piping", "duct-kit", "handrail"}:
        x, y, z = dims
        children = [
            _box((x, max(20.0, y * 0.10), max(18.0, z * 0.24)), f"{label} route A", SYSTEM).locate(Location((0, -y * 0.32, 0))),
            _box((x, max(20.0, y * 0.10), max(18.0, z * 0.24)), f"{label} route B", SYSTEM).locate(Location((0, y * 0.32, 0))),
        ]
        for fraction in (-0.35, 0.0, 0.35):
            children.append(_box((max(30.0, x * 0.025), y * 0.80, max(20.0, z * 0.30)), f"{label} support", STEEL).locate(Location((x * fraction, 0, 0))))
        return Compound(label=label, children=children)
    if form in {"cowl", "cowl-kit", "cowl-service"}:
        x, y, z = dims
        return Compound(label=label, children=[
            _box((x, y, z * 0.36), f"{label} lower shell", COMPOSITE).locate(Location((0, 0, -z * 0.30))),
            _box((x * 0.78, y * 0.92, z * 0.34), f"{label} centre shell", COMPOSITE),
            _box((x * 0.52, y * 0.78, z * 0.26), f"{label} upper shell", COMPOSITE).locate(Location((0, 0, z * 0.31))),
        ])
    if form == "floor":
        x, y, z = dims
        return Compound(label=label, children=[
            _box((x * 0.62, y, z * 0.36), f"{label} low pan", STEEL),
            _box((x * 0.18, y, z), f"{label} end deck", STEEL).locate(Location((-x * 0.40, 0, z * 0.24))),
            _box((x * 0.18, y, z), f"{label} end deck", STEEL).locate(Location((x * 0.40, 0, z * 0.24))),
        ])
    if form in {"pneumatic-kit", "axlebox", "pivot"}:
        x, y, z = dims
        cylinder = _part(Cylinder(min(x, y) * 0.28, z * 0.72), f"{label} cylindrical unit", SYSTEM)
        base = _box((x, y, z * 0.24), f"{label} base/datum", STEEL).locate(Location((0, 0, -z * 0.38)))
        return Compound(label=label, children=[cylinder, base])
    if form == "coupler":
        x, y, z = dims
        return Compound(label=label, children=[
            _box((x * 0.68, y * 0.30, z * 0.30), f"{label} drawbar", STEEL),
            _box((x * 0.25, y, z), f"{label} head", SAFETY).locate(Location((x * 0.36, 0, 0))),
            _box((x * 0.22, y * 0.72, z * 0.72), f"{label} crash absorber", SYSTEM).locate(Location((-x * 0.38, 0, 0))),
        ])
    if form in {"fastener-kit", "adapter-kit", "recovery-kit", "link-kit", "brake-kit", "bogie-guards", "tray", "roof-equipment", "cowl-service", "bridge"}:
        x, y, z = dims
        return Compound(label=label, children=[
            _box((x, y * 0.42, z * 0.42), f"{label} primary member", STEEL),
            _box((x * 0.48, y, z * 0.32), f"{label} transverse member", STEEL),
            _box((x * 0.18, y * 0.22, z), f"{label} retained interface", SAFETY),
        ])
    if form == "bolster":
        x, y, z = dims
        return Compound(label=label, children=[
            _box((x, y, z * 0.62), f"{label} box", STEEL),
            _part(Cylinder(min(x, y) * 0.12, z), f"{label} centre-pivot insert", SAFETY),
        ])
    if form == "coupler-pocket":
        return _equipment(dims, label, STEEL)
    if form in {"hvac", "power-electronics", "battery", "gearbox", "resistor", "charger", "hv-panel", "fire-kit", "control-cabinet", "sensor-kit", "control-panel", "recorder", "sensor-pack", "lamp-kit", "pis", "camera-kit", "emergency-kit", "light-kit"}:
        return _equipment(dims, label)
    raise AssertionError(f"unimplemented LM3 geometry form {form!r} for {product_id}")


def flatten_geometry(value: Part | Compound) -> list[Part]:
    if isinstance(value, Compound):
        result: list[Part] = []
        for child in value.children:
            result.extend(flatten_geometry(child))
        return result
    return [value]


__all__ = ["ProductGeometrySpec", "flatten_geometry", "geometry_specs", "product_geometry"]
