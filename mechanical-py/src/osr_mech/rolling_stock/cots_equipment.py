"""COTS interior-equipment catalogue + envelope reservations.

The car body from [`car_body`](./car_body.py) is a structural shell —
cabless box with door cutouts. Everything passengers actually see
(windows, seats, grab poles, lighting, HVAC, passenger screens,
intercom) is a commodity item bought from the open market. This
module is the catalogue: for each category we publish the
reference SKU class, envelope (L×W×H), mass, electric power
draw, and the bolt-pattern the car body reserves for it.

Why this matters:

- A builder who wants to swap vendors (Liebherr HVAC -> Merak HVAC,
  Compin-Fainsa seats -> Kiel seats, etc.) can check that the replacement
  fits inside the reserved envelope. The envelope is the
  contract; the SKU is a worked-example choice.
- The per-car fitting-out BOM aggregates to a per-trainset
  CAPEX line that plugs into RFC 0008 §6's costing table.
- For CAD-sanity, [`fit_out_car_body`](./cots_equipment.py)
  returns a Compound of the structural body plus every envelope
  in a distinct colour, so the whole fridge-freezer list is
  visible in the FreeCAD review assembly at once.

Nothing here is safety-rated. Door leaves + actuators, traction
converters, and the T-OBS sensor pack are handled elsewhere — this
file is exclusively the passenger-comfort + passenger-information
layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from osr_mech.cad import (
    Align,
    Box,
    BuildPart,
    BuildSketch,
    Color,
    Compound,
    Cylinder,
    Location,
    Part,
    Rectangle,
    extrude,
)

from .car_body import (
    DOOR_HEIGHT_MM,
    DOOR_SILL_HEIGHT_MM,
    DOOR_WIDTH_MM,
    CarDimensions,
    car_body,
)


# ---------------------------------------------------------------------------
# Catalogue data
# ---------------------------------------------------------------------------


class Category(str, Enum):
    """The seven commodity-equipment categories the car body reserves
    space for."""

    WINDOW = "window"
    HVAC_ROOF = "hvac-roof"
    LIGHTING = "lighting"
    PIS_SCREEN = "pis-screen"
    SEAT = "seat-bench"
    GRAB_POLE = "grab-pole"
    INTERCOM = "intercom"


@dataclass(frozen=True)
class CotsItem:
    """One row in the COTS catalogue."""

    category: Category
    """Human-readable name of the item."""
    name: str
    """Reference SKU class — a worked-example vendor/model. Any
    equivalent part that fits inside the envelope + power budget is
    a valid substitute."""
    sku_reference: str
    """Primary supplier/product-family page used to size and describe
    the reference envelope. This is a traceability aid, not a
    sole-source procurement lock."""
    supplier_reference_url: str
    """Other supplier/product families that procurement should keep in
    the tender set."""
    alternates: tuple[str, ...]
    """Short integration note copied into BOM/procurement reviews."""
    fit_note: str
    """Public source basis used to turn the reservation box into a
    recognisable component shape. Exact supplier CAD remains a v2
    controlled drawing input."""
    geometry_basis: str
    length_mm: float
    width_mm: float
    height_mm: float
    mass_kg: float
    """Nominal active-load power. `0.0` for passive items (windows,
    seats, grab poles)."""
    power_w: float
    """Human-readable mounting pattern — the car body must provide
    tapped holes / bonding surface per this spec."""
    mount_pattern: str
    """Planning-grade per-unit purchase-cost band. Tender-only rail
    items must be replaced by supplier quotes before procurement."""
    unit_cost_low_usd: float
    unit_cost_base_usd: float
    unit_cost_high_usd: float
    """Audit note for the cost band."""
    cost_basis: str
    """Visualisation colour for the reserved envelope in the CAD
    fit-out output (RGB 0..1)."""
    display_color: tuple[float, float, float]


CATALOGUE: dict[Category, CotsItem] = {
    Category.WINDOW: CotsItem(
        category=Category.WINDOW,
        name="Side glazing panel",
        sku_reference="Rail laminated safety glazing, AGC Lamisafe/Heatlight W class",
        supplier_reference_url="https://www.agc.com/en/everyday/mobility/train.html",
        alternates=(
            "Pilkington rail laminated glazing",
            "Saint-Gobain Sekurit transport glazing",
        ),
        fit_note="Bonded/gasketed cassette with drain channel and optional heated anti-fog pane.",
        geometry_basis="AGC rail glazing page: laminated Lamisafe front glass and Heatlight W heated anti-fog glass family; OSR aperture sets the panel size.",
        length_mm=1400.0,
        width_mm=40.0,
        height_mm=900.0,
        mass_kg=25.0,
        power_w=0.0,
        mount_pattern="Bonded frame, Sikaflex 252 bead 12 mm",
        unit_cost_low_usd=950.0,
        unit_cost_base_usd=1500.0,
        unit_cost_high_usd=2600.0,
        cost_basis="Derived from BOM B10: 18 cassettes / 27,000 USD base; rail glazing quotes vary with heating, curvature, and certification pack.",
        display_color=(0.55, 0.75, 0.90),
    ),
    Category.HVAC_ROOF: CotsItem(
        category=Category.HVAC_ROOF,
        name="Rooftop HVAC unit",
        sku_reference="Compact/split roof rail HVAC, Liebherr passenger-saloon class",
        supplier_reference_url=(
            "https://www.liebherr.com/en-ca/aerospace-and-transportation-systems/"
            "solutions-and-services/solutions-for-railway/on-board-systems/classical-hvac-7178128"
        ),
        alternates=(
            "Knorr-Bremse Merak roof HVAC",
            "Faiveley/Wabtec rail HVAC",
            "Hispacold rail HVAC",
        ),
        fit_note="Roof curb accepts compact or split unit, drop ducts, condensate drains, and diagnostics harness.",
        geometry_basis="Liebherr rail HVAC page: passenger saloon units integrate power supply, pressure protection, air ducts, diagnostics, and controls; available as compact/split, roof/floor mounted units.",
        length_mm=2700.0,
        width_mm=1900.0,
        height_mm=450.0,
        mass_kg=420.0,
        power_w=20_000.0,
        mount_pattern="10× M12 curb bolts, EPDM gasket, twin 450 × 260 drop ducts",
        unit_cost_low_usd=18_000.0,
        unit_cost_base_usd=25_000.0,
        unit_cost_high_usd=42_000.0,
        cost_basis="Derived from BOM T14: 3 HVAC units / 75,000 USD base; high end covers hot-climate rail-qualified package and pressure-protection options.",
        display_color=(0.70, 0.70, 0.75),
    ),
    Category.LIGHTING: CotsItem(
        category=Category.LIGHTING,
        name="Continuous LED ceiling strip",
        sku_reference="Teknoware rolling-stock main/emergency LED lighting rail",
        supplier_reference_url="https://www.teknoware.com/rail-road/rolling-stock-lighting-and-interiors/",
        alternates=(
            "Luminator interior rail lighting",
            "SBF Spezialleuchten rail LED lighting",
        ),
        fit_note="Two serviceable ceiling channels with emergency-input wiring and spring clips.",
        geometry_basis="Teknoware rail lighting catalogue family: interior lighting, main/emergency functions, serviceable rail-and-road vehicle modules.",
        length_mm=16_400.0,  # full usable saloon run; actual supply comes as short segments
        width_mm=100.0,
        height_mm=50.0,
        mass_kg=35.0,
        power_w=250.0,  # roughly 15 W/m over each usable saloon run
        mount_pattern="M6 clips at 600 mm pitch into ceiling channel",
        unit_cost_low_usd=900.0,
        unit_cost_base_usd=1500.0,
        unit_cost_high_usd=2500.0,
        cost_basis="Derived from BOM B16: 6 ceiling strip runs / 9,000 USD base; includes emergency-mode rail wiring allowance.",
        display_color=(1.0, 0.95, 0.80),
    ),
    Category.PIS_SCREEN: CotsItem(
        category=Category.PIS_SCREEN,
        name="Passenger-information LCD",
        sku_reference="Luminator on-board infotainment/destination display class",
        supplier_reference_url="https://www.luminator.com/en-us/products.html",
        alternates=(
            "Televic GSP onboard display/PIS",
            "Perrone/Vianova onboard display class",
            "Litemax EN 50155 display class",
        ),
        fit_note="Above-door VESA plate reserves Ethernet, 24 V DC, and anti-vibration isolators.",
        geometry_basis="Luminator LUM LED Rail S datasheet: 1125 × 210 × 45 mm housing, 5.4 kg max, 24 V DC, 31 W typical / 65 W max.",
        length_mm=1125.0,
        width_mm=45.0,
        height_mm=210.0,
        mass_kg=5.4,
        power_w=31.0,
        mount_pattern="VESA 200 × 100, 4× M4",
        unit_cost_low_usd=450.0,
        unit_cost_base_usd=800.0,
        unit_cost_high_usd=1800.0,
        cost_basis="Derived from BOM E14: 12 onboard displays / 9,600 USD base; high end covers rail LCD/LED display controller and EMC evidence.",
        display_color=(0.10, 0.10, 0.10),
    ),
    Category.SEAT: CotsItem(
        category=Category.SEAT,
        name="Longitudinal bench run",
        sku_reference="Compin-Fainsa SB09 Metro/LRV longitudinal seat class",
        supplier_reference_url="https://www.compinfainsa.com/product/railway-seats-and-interiors-sb09",
        alternates=(
            "Kiel Avant Metro",
            "Grammer Ipano longitudinal rail seat",
            "McConnell lightweight metro bench",
        ),
        fit_note="Cantilevered rail keeps battery covers serviceable; removable pads and EN 45545 evidence required.",
        geometry_basis="Compin-Fainsa SB09 page: longitudinal/transversal metro/LRV installation, removable pads, light alloy frame, EN45545 HL2/HL3 evidence.",
        length_mm=2700.0,
        width_mm=500.0,
        height_mm=950.0,
        mass_kg=40.0,
        power_w=0.0,
        mount_pattern=(
            "Cantilevered from the battery-strake bulkhead (RFC 0021 §5) "
            "— 4× M10 on 800 × 300 pitch into a welded strake-top rail. "
            "No floor penetrations (the aisle stays at level-boarding height)."
        ),
        unit_cost_low_usd=800.0,
        unit_cost_base_usd=1333.333,
        unit_cost_high_usd=2500.0,
        cost_basis="Derived from BOM B14: 60 seats / 24,000 USD, represented as 18 multi-seat bench runs per consist.",
        display_color=(0.20, 0.35, 0.55),
    ),
    Category.GRAB_POLE: CotsItem(
        category=Category.GRAB_POLE,
        name="Vertical grab pole",
        sku_reference="Rail interior stainless stanchion kit, Compin-Fainsa/Teknoware interior class",
        supplier_reference_url="https://www.compinfainsa.com/products",
        alternates=(
            "Teknoware interior structures",
            "FISA rail interior stanchion kit",
            "local 316L modular rail fabricator",
        ),
        fit_note="Stainless modular pole with replaceable flanges into floor and ceiling inserts.",
        geometry_basis="Rail interior stanchion class: stainless vertical pole with floor/ceiling flanges and modular grab-rail interfaces.",
        length_mm=35.0,
        width_mm=35.0,
        height_mm=2_300.0,  # floor to false-ceiling
        mass_kg=8.0,
        power_w=0.0,
        mount_pattern="Flanged floor + ceiling plates, 3× M8 each",
        unit_cost_low_usd=160.0,
        unit_cost_base_usd=333.0,
        unit_cost_high_usd=700.0,
        cost_basis="Derived from BOM B15: 24 primary stanchions / 8,000 USD base plus shared grab-rail fittings.",
        display_color=(0.85, 0.85, 0.85),
    ),
    Category.INTERCOM: CotsItem(
        category=Category.INTERCOM,
        name="Emergency intercom / help-point",
        sku_reference="Televic TRACS passenger communication unit / IP audio class",
        supplier_reference_url="https://www.televic.com/en/rail/products/audio-communication-system-for-trains",
        alternates=(
            "Luminator Audio Coach Controller + TIU",
            "Zenitel/Vingtor-Stentofon rail intercom",
            "Commend public-transport intercom",
        ),
        fit_note="Recessed help-point with SIP/Ethernet, 24 V DC, audio fallback, and labelled call button.",
        geometry_basis="Televic TRACS passenger communication class: recessed wall help-point, audio fallback, Ethernet/SIP train communication module.",
        length_mm=300.0,
        width_mm=100.0,
        height_mm=200.0,
        mass_kg=3.5,
        power_w=10.0,
        mount_pattern="Recessed 250 × 150 cutout, 4× M5 into backing plate",
        unit_cost_low_usd=350.0,
        unit_cost_base_usd=800.0,
        unit_cost_high_usd=1800.0,
        cost_basis="BOM B19 includes CCTV + intercom kit; this row assigns an 800 USD planning unit for the intercom/help-point module.",
        display_color=(0.80, 0.15, 0.15),
    ),
}


# ---------------------------------------------------------------------------
# Per-car quantity rules
# ---------------------------------------------------------------------------

# These are the "how many of each per car" rules driving the BOM. The
# current OSR module uses two wide low-floor door openings per side;
# the rules stay parametric so future variants can tune dwell capacity
# without rewriting the catalogue.


def _window_zone_count(dims: CarDimensions) -> int:
    """Window bays per car side.

    The car body has `doors_per_side` door cutouts; the remaining wall
    segments (between doors + between door and car end) are window
    zones. Count = doors_per_side + 1. Multiply by 2 for both sides."""
    return dims.doors_per_side + 1


def _seat_run_count(dims: CarDimensions) -> int:
    """Seat-bench runs per car side — same count as window zones. Each
    run occupies the wall segment below the window zone."""
    return dims.doors_per_side + 1


def _grab_pole_count(dims: CarDimensions) -> int:
    """Vertical grab poles — 2 per door opening on each side.
    Passengers grab onto poles at door edges; door leaves retract into
    the adjacent wall."""
    return dims.doors_per_side * 4


def _pis_screen_count(dims: CarDimensions) -> int:
    """PIS screens — 2 per door zone (one per side, visible to the
    queue about to alight)."""
    return dims.doors_per_side * 2


def _intercom_count(_dims: CarDimensions) -> int:
    """Intercom / help-point — 2 per car, one at each end."""
    return 2


def _hvac_count(_dims: CarDimensions) -> int:
    """One rooftop unit per car."""
    return 1


def _lighting_count(_dims: CarDimensions) -> int:
    """Two continuous ceiling strips — port and starboard."""
    return 2


_COUNT_RULES = {
    Category.WINDOW: lambda d: _window_zone_count(d) * 2,
    Category.HVAC_ROOF: _hvac_count,
    Category.LIGHTING: _lighting_count,
    Category.PIS_SCREEN: _pis_screen_count,
    Category.SEAT: lambda d: _seat_run_count(d) * 2,
    Category.GRAB_POLE: _grab_pole_count,
    Category.INTERCOM: _intercom_count,
}


def bom_per_car(dims: CarDimensions = CarDimensions()) -> list[tuple[CotsItem, int]]:
    """Per-car COTS BOM: the list of (item, quantity) tuples for one
    car of the given dimensions. Sum over a consist to get the full
    trainset fit-out."""
    return [(CATALOGUE[c], _COUNT_RULES[c](dims)) for c in Category]


def total_mass_kg(dims: CarDimensions = CarDimensions()) -> float:
    """Total interior-fit-out mass, kg — the weight the car body
    suspension budgets for on top of the structural shell."""
    return sum(item.mass_kg * qty for item, qty in bom_per_car(dims))


def total_active_power_w(dims: CarDimensions = CarDimensions()) -> float:
    """Simultaneous active-load power, W — the auxiliary-converter
    sizing input. Passive items contribute 0."""
    return sum(item.power_w * qty for item, qty in bom_per_car(dims))


# ---------------------------------------------------------------------------
# Placement — where each item goes on the car body
# ---------------------------------------------------------------------------


def _door_centres_x(dims: CarDimensions) -> list[float]:
    """X coordinates of each door centre along the car, matching
    `car_body`'s door cutout loop. Car is centred on X = 0."""
    spacing = dims.body_length_mm / (dims.doors_per_side + 1)
    return [
        -dims.body_length_mm / 2.0 + (i + 1) * spacing
        for i in range(dims.doors_per_side)
    ]


def _window_centres_x(dims: CarDimensions) -> list[float]:
    """X coordinates of each window zone centre — the midpoint of each
    wall segment between / outside the doors."""
    doors = _door_centres_x(dims)
    edges = [-dims.body_length_mm / 2.0] + doors + [dims.body_length_mm / 2.0]
    door_half = DOOR_WIDTH_MM / 2.0
    centres: list[float] = []
    for i in range(len(edges) - 1):
        left = edges[i] + (door_half if 0 < i else 0.0)
        right = edges[i + 1] - (door_half if i + 1 < len(edges) - 1 else 0.0)
        centres.append((left + right) / 2.0)
    return centres


def locations_for(category: Category, dims: CarDimensions) -> list[Location]:
    """Reference (x, y, z) placements for every instance of `category`
    on a car of `dims`. Y is across-track (positive = toward the "B"
    side), Z is rail-head-based."""

    if category == Category.WINDOW:
        y_offset = dims.body_width_mm / 2.0
        window_sill_z = DOOR_SILL_HEIGHT_MM + 300.0  # above door sill, below door head
        return [
            Location((x, side * y_offset, window_sill_z))
            for x in _window_centres_x(dims)
            for side in (-1.0, 1.0)
        ]

    if category == Category.HVAC_ROOF:
        # Centred on the car roof.
        return [Location((0.0, 0.0, dims.body_height_mm))]

    if category == Category.LIGHTING:
        # Two continuous strips ~200 mm from the ceiling corner.
        y_inset = dims.body_width_mm / 2.0 - 200.0
        z = dims.body_height_mm - 100.0
        return [
            Location((0.0, -y_inset, z)),
            Location((0.0, +y_inset, z)),
        ]

    if category == Category.PIS_SCREEN:
        # Above each door on both sides, facing inward.
        z = DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM + 150.0  # 150 mm above door head
        y_offset = dims.body_width_mm / 2.0 - 50.0
        return [
            Location((x, side * y_offset, z))
            for x in _door_centres_x(dims)
            for side in (-1.0, 1.0)
        ]

    if category == Category.SEAT:
        # Seat-bench runs below the windows along each wall segment.
        seat = CATALOGUE[Category.SEAT]
        y_inset = dims.body_width_mm / 2.0 - seat.width_mm / 2.0
        return [
            Location((x, side * y_inset, 0.0))
            for x in _window_centres_x(dims)
            for side in (-1.0, 1.0)
        ]

    if category == Category.GRAB_POLE:
        # Two poles per door — flanking the opening on each side.
        pole_x_offset = DOOR_WIDTH_MM / 2.0 + 150.0
        z = 0.0
        y_inset = dims.body_width_mm / 2.0 - 250.0
        return [
            Location((x + sign * pole_x_offset, side * y_inset, z))
            for x in _door_centres_x(dims)
            for sign in (-1.0, 1.0)
            for side in (-1.0, 1.0)
        ]

    if category == Category.INTERCOM:
        # One at each car end, mounted on the end wall.
        return [
            Location((-dims.body_length_mm / 2.0 + 500.0, 0.0, 1600.0)),
            Location((+dims.body_length_mm / 2.0 - 500.0, 0.0, 1600.0)),
        ]

    raise ValueError(f"no placement rule for {category!r}")


# ---------------------------------------------------------------------------
# Envelope visualisation
# ---------------------------------------------------------------------------


def _colour(item: CotsItem, alpha: float | None = None) -> Color:
    r, g, b = item.display_color
    return Color(r, g, b) if alpha is None else Color(r, g, b, alpha)


def _part(part: Part, label: str, color: Color) -> Part:
    part.label = label
    part.color = color
    return part


def _box(
    length: float,
    width: float,
    height: float,
    *,
    label: str,
    color: Color,
    loc: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> Part:
    x, y, z = loc
    return _part(
        Box(length, width, height).locate(Location((x, y, z + height / 2.0))),
        label,
        color,
    )


def _cylinder(
    radius: float,
    height: float,
    *,
    label: str,
    color: Color,
    loc: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> Part:
    x, y, z = loc
    return _part(
        Cylinder(radius=radius, height=height).locate(Location((x, y, z + height / 2.0))),
        label,
        color,
    )


def _source_shape(item: CotsItem) -> Compound | None:
    """Return a source-informed shape for catalogue items where public
    product pages provide enough cues to be more useful than a box."""

    color = _colour(item)
    shadow = _colour(item, 0.45)

    if item.category == Category.WINDOW:
        frame = Color(0.12, 0.14, 0.15)
        heater = Color(0.95, 0.62, 0.12)
        parts = [
            _box(item.length_mm, item.width_mm, item.height_mm, label="Laminated heated glass pane", color=shadow),
            _box(item.length_mm + 90.0, item.width_mm + 18.0, 42.0, label="Upper bonded glazing cassette rail", color=frame, loc=(0.0, 0.0, item.height_mm - 42.0)),
            _box(item.length_mm + 90.0, item.width_mm + 18.0, 42.0, label="Lower drain cassette rail", color=frame),
            _box(42.0, item.width_mm + 18.0, item.height_mm, label="Left glazing cassette stile", color=frame, loc=(-item.length_mm / 2.0, 0.0, 0.0)),
            _box(42.0, item.width_mm + 18.0, item.height_mm, label="Right glazing cassette stile", color=frame, loc=(item.length_mm / 2.0, 0.0, 0.0)),
            _box(item.length_mm - 180.0, 8.0, 12.0, label="Heatlight-style heater busbar", color=heater, loc=(0.0, -item.width_mm / 2.0 - 6.0, item.height_mm - 110.0)),
        ]
        c = Compound(children=parts)
        c.label = f"{item.name} (source-shaped cassette)"
        return c

    if item.category == Category.HVAC_ROOF:
        metal = Color(0.58, 0.60, 0.64)
        grille = Color(0.12, 0.14, 0.16)
        parts = [
            _box(item.length_mm, item.width_mm, 310.0, label="Compact rooftop HVAC casing", color=color),
            _box(item.length_mm + 140.0, item.width_mm + 120.0, 55.0, label="Roof curb and gasket flange", color=metal),
            _box(620.0, 360.0, 150.0, label="Supply-air drop duct", color=Color(0.12, 0.45, 0.62), loc=(-500.0, -item.width_mm / 2.0 + 250.0, -150.0)),
            _box(620.0, 360.0, 150.0, label="Return-air drop duct", color=Color(0.12, 0.45, 0.62), loc=(500.0, -item.width_mm / 2.0 + 250.0, -150.0)),
        ]
        for x in (-650.0, 650.0):
            parts.append(_cylinder(270.0, 28.0, label="Condenser fan guard", color=grille, loc=(x, 0.0, 330.0)))
            for y in (-160.0, 0.0, 160.0):
                parts.append(_box(440.0, 18.0, 16.0, label="Fan grille bar", color=metal, loc=(x, y, 360.0)))
        c = Compound(children=parts)
        c.label = f"{item.name} (source-shaped rooftop module)"
        return c

    if item.category == Category.LIGHTING:
        parts = [
            _box(item.length_mm, item.width_mm, 18.0, label="Extruded LED lighting rail", color=Color(0.86, 0.86, 0.80), loc=(0.0, 0.0, 16.0)),
            _box(item.length_mm - 80.0, item.width_mm - 24.0, 16.0, label="Continuous opal diffuser", color=Color(1.0, 0.96, 0.74, 0.65), loc=(0.0, 0.0, 0.0)),
        ]
        for x in range(-7600, 7601, 1200):
            parts.append(_box(80.0, item.width_mm + 22.0, 8.0, label="Ceiling spring clip", color=Color(0.54, 0.54, 0.54), loc=(float(x), 0.0, 38.0)))
        c = Compound(children=parts)
        c.label = f"{item.name} (source-shaped lighting run)"
        return c

    if item.category == Category.PIS_SCREEN:
        face_y = -item.width_mm / 2.0 - 4.0
        parts = [
            _box(item.length_mm, item.width_mm, item.height_mm, label="Aluminium passenger-display housing", color=Color(0.08, 0.08, 0.08)),
            _box(item.length_mm - 160.0, 8.0, item.height_mm - 60.0, label="LED display active area", color=Color(0.02, 0.03, 0.04), loc=(0.0, face_y, 30.0)),
            _box(240.0, 12.0, 60.0, label="M8 side mounting boss", color=Color(0.52, 0.52, 0.52), loc=(-item.length_mm / 2.0 + 130.0, item.width_mm / 2.0, item.height_mm / 2.0 - 30.0)),
            _box(240.0, 12.0, 60.0, label="M8 side mounting boss", color=Color(0.52, 0.52, 0.52), loc=(item.length_mm / 2.0 - 130.0, item.width_mm / 2.0, item.height_mm / 2.0 - 30.0)),
        ]
        c = Compound(children=parts)
        c.label = f"{item.name} (source-shaped display)"
        return c

    if item.category == Category.SEAT:
        parts = [
            _box(item.length_mm, item.width_mm, 95.0, label="Removable bench cushion pads", color=color, loc=(0.0, 0.0, 430.0)),
            _box(item.length_mm, 95.0, 460.0, label="Light-alloy backrest frame", color=Color(0.18, 0.30, 0.48), loc=(0.0, item.width_mm / 2.0 - 55.0, 470.0)),
            _box(item.length_mm - 180.0, 60.0, 52.0, label="Cantilever wall rail", color=Color(0.58, 0.60, 0.62), loc=(0.0, item.width_mm / 2.0 + 10.0, 370.0)),
        ]
        for x in (-item.length_mm / 2.0 + 360.0, 0.0, item.length_mm / 2.0 - 360.0):
            parts.append(_box(110.0, 420.0, 85.0, label="Seat support rib", color=Color(0.34, 0.36, 0.38), loc=(x, 0.0, 330.0)))
            parts.append(_box(28.0, 26.0, 330.0, label="Seat divider grab upright", color=Color(0.72, 0.72, 0.70), loc=(x, -item.width_mm / 2.0 + 30.0, 470.0)))
        c = Compound(children=parts)
        c.label = f"{item.name} (source-shaped bench)"
        return c

    if item.category == Category.GRAB_POLE:
        pole = _cylinder(item.length_mm / 2.0, item.height_mm, label="Stainless vertical grab pole", color=color)
        parts = [
            pole,
            _cylinder(95.0, 16.0, label="Floor mounting flange", color=Color(0.66, 0.66, 0.64)),
            _cylinder(95.0, 16.0, label="Ceiling mounting flange", color=Color(0.66, 0.66, 0.64), loc=(0.0, 0.0, item.height_mm - 16.0)),
        ]
        c = Compound(children=parts)
        c.label = f"{item.name} (source-shaped stanchion)"
        return c

    if item.category == Category.INTERCOM:
        parts = [
            _box(item.length_mm, item.width_mm, item.height_mm, label="Recessed intercom backbox", color=Color(0.18, 0.18, 0.19)),
            _box(item.length_mm + 35.0, 12.0, item.height_mm + 35.0, label="Help-point faceplate", color=color, loc=(0.0, -item.width_mm / 2.0 - 8.0, -17.5)),
            _box(72.0, 18.0, 72.0, label="Emergency call button", color=Color(0.95, 0.10, 0.08), loc=(-82.0, -item.width_mm / 2.0 - 22.0, 64.0)),
        ]
        for z in (44.0, 74.0, 104.0, 134.0):
            parts.append(_box(120.0, 16.0, 8.0, label="Speaker grille slot", color=Color(0.04, 0.04, 0.04), loc=(65.0, -item.width_mm / 2.0 - 24.0, z)))
        c = Compound(children=parts)
        c.label = f"{item.name} (source-shaped help point)"
        return c

    return None


def _plain_envelope(item: CotsItem) -> Part:
    with BuildPart() as p:
        with BuildSketch():
            Rectangle(item.length_mm, item.width_mm, align=(Align.CENTER, Align.CENTER))
        extrude(amount=item.height_mm)
    part = p.part
    part.color = _colour(item)
    part.label = f"{item.name} (envelope)"
    return part


def envelope_part(item: CotsItem) -> Part | Compound:
    """Build a source-informed component reservation for `item`.

    Shapes are still supplier-neutral envelopes: public product pages
    inform the recognisable features, while the exact vendor CAD remains
    a v2 procurement-controlled input.

    Origin: envelope centred on (0, 0, z_min = 0). Callers translate
    to the target location."""

    return _source_shape(item) or _plain_envelope(item)


def fit_out_car_body(dims: CarDimensions = CarDimensions()) -> Compound:
    """Build the car body plus every COTS envelope in its published
    location, for CAD-sanity visualisation.

    The returned Compound is *not* the structural car — it's the
    structural car *overlaid* with the reserved volumes in their
    catalogue colour. The FreeCAD review assembly gives a builder a
    compact view showing "here's the box + here's where every
    fridge-freezer goes".
    """

    # Flatten the car-body Compound into the fit-out Compound.
    # `Compound.volume` sums only direct Part children and
    # ignores nested Compounds, so nesting would hide the shell's
    # volume. Flatten once to preserve introspectability.
    car = car_body(dims)
    parts: list[Part | Compound] = list(car.children) if car.children else [car]
    for category in Category:
        item = CATALOGUE[category]
        env = envelope_part(item)
        for loc in locations_for(category, dims):
            parts.append(env.moved(loc))
    return Compound(
        label=f"Car body + COTS fit-out ({int(dims.body_length_mm / 1000)} m)",
        children=parts,
    )


__all__ = [
    "CATALOGUE",
    "Category",
    "CotsItem",
    "bom_per_car",
    "envelope_part",
    "fit_out_car_body",
    "locations_for",
    "total_active_power_w",
    "total_mass_kg",
]
