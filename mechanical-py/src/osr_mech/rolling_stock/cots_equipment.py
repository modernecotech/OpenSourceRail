"""COTS interior-equipment catalogue + envelope reservations.

The car body from [`car_body`](./car_body.py) is a structural shell —
cabless box with door cutouts. Everything passengers actually see
(windows, seats, grab poles, lighting, HVAC, passenger screens,
intercom) is a commodity item bought from the open market. This
module is the catalogue: for each category we publish the
reference SKU class, envelope (L×W×H), mass, electric power
draw, and the bolt-pattern the car body reserves for it.

Why this matters:

- A builder who wants to swap vendors (Sutrak HVAC → Hispacold,
  Kiel seats → Grammer, etc.) can check that the replacement
  fits inside the reserved envelope. The envelope is the
  contract; the SKU is a worked-example choice.
- The per-car fitting-out BOM aggregates to a per-trainset
  CAPEX line that plugs into RFC 0008 §6's costing table.
- For CAD-sanity, [`fit_out_car_body`](./cots_equipment.py)
  returns a Compound of the structural body plus every envelope
  in a distinct colour, so the whole fridge-freezer list is
  visible in the STEP viewer at once.

Nothing here is safety-rated. Door leaves + actuators, traction
converters, and the T-OBS sensor pack are handled elsewhere — this
file is exclusively the passenger-comfort + passenger-information
layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from build123d import (
    Align,
    BuildPart,
    BuildSketch,
    Color,
    Compound,
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
    """Visualisation colour for the reserved envelope in the STEP
    fit-out output (RGB 0..1)."""
    display_color: tuple[float, float, float]


CATALOGUE: dict[Category, CotsItem] = {
    Category.WINDOW: CotsItem(
        category=Category.WINDOW,
        name="Side glazing panel",
        sku_reference="Laminated 8+1.52 PVB+8, Pilkington Optilam class",
        length_mm=1400.0,
        width_mm=40.0,
        height_mm=900.0,
        mass_kg=25.0,
        power_w=0.0,
        mount_pattern="Bonded frame, Sikaflex 252 bead 12 mm",
        display_color=(0.55, 0.75, 0.90),
    ),
    Category.HVAC_ROOF: CotsItem(
        category=Category.HVAC_ROOF,
        name="Rooftop HVAC unit",
        sku_reference="15 kW bus-HVAC class — Sutrak CC 210 / Thermo King T-1080R / Hispacold Compact",
        length_mm=1800.0,
        width_mm=1200.0,
        height_mm=400.0,
        mass_kg=250.0,
        power_w=15_000.0,
        mount_pattern="8× M10 on 1200 × 600 pitch, EPDM gasket",
        display_color=(0.70, 0.70, 0.75),
    ),
    Category.LIGHTING: CotsItem(
        category=Category.LIGHTING,
        name="Continuous LED ceiling strip",
        sku_reference="Osram Ledvance T5-equivalent linear, 15 W/m @ 24 VDC",
        length_mm=22_000.0,  # full car length; actual supply comes as 1.5 m segments
        width_mm=100.0,
        height_mm=50.0,
        mass_kg=35.0,
        power_w=330.0,  # 15 W/m × 22 m
        mount_pattern="M6 clips at 600 mm pitch into ceiling channel",
        display_color=(1.0, 0.95, 0.80),
    ),
    Category.PIS_SCREEN: CotsItem(
        category=Category.PIS_SCREEN,
        name="Passenger-information LCD",
        sku_reference="21.5\" industrial LCD — Advantech OSD-215 / Lilliput FA1200-NP",
        length_mm=520.0,
        width_mm=50.0,
        height_mm=320.0,
        mass_kg=6.0,
        power_w=30.0,
        mount_pattern="VESA 200 × 100, 4× M4",
        display_color=(0.10, 0.10, 0.10),
    ),
    Category.SEAT: CotsItem(
        category=Category.SEAT,
        name="Longitudinal bench (2-seat unit)",
        sku_reference="Kiel Avant Metro / Grammer Ipano longitudinal, textile upholstery",
        length_mm=1000.0,
        width_mm=500.0,
        height_mm=950.0,
        mass_kg=25.0,
        power_w=0.0,
        mount_pattern=(
            "Cantilevered from the battery-strake bulkhead (RFC 0021 §5) "
            "— 4× M10 on 800 × 300 pitch into a welded strake-top rail. "
            "No floor penetrations (the aisle stays at level-boarding height)."
        ),
        display_color=(0.20, 0.35, 0.55),
    ),
    Category.GRAB_POLE: CotsItem(
        category=Category.GRAB_POLE,
        name="Vertical grab pole",
        sku_reference="Stainless 304, 35 mm OD × 2.5 mm wall, satin finish",
        length_mm=35.0,
        width_mm=35.0,
        height_mm=2_300.0,  # floor to false-ceiling
        mass_kg=8.0,
        power_w=0.0,
        mount_pattern="Flanged floor + ceiling plates, 3× M8 each",
        display_color=(0.85, 0.85, 0.85),
    ),
    Category.INTERCOM: CotsItem(
        category=Category.INTERCOM,
        name="Emergency intercom / help-point",
        sku_reference="Zenitel Vingtor-Stentofon TMIS-2 class, IP-SIP",
        length_mm=300.0,
        width_mm=100.0,
        height_mm=200.0,
        mass_kg=3.5,
        power_w=10.0,
        mount_pattern="Recessed 250 × 150 cutout, 4× M5 into backing plate",
        display_color=(0.80, 0.15, 0.15),
    ),
}


# ---------------------------------------------------------------------------
# Per-car quantity rules
# ---------------------------------------------------------------------------

# These are the "how many of each per car" rules driving the BOM. A
# tram-2car family gets fewer because it has 2 doors/side not 3, but the
# count rules are parametric in doors_per_side + body_length.


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
    """Vertical grab poles — 2 per door zone. Passengers grab onto
    poles at door edges; door leaves retract into the adjacent wall."""
    return dims.doors_per_side * 2


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


def envelope_part(item: CotsItem) -> Part:
    """Build a rectangular envelope for `item`, coloured per its
    catalogue entry. The box is a *reservation* — real hardware fits
    *inside* it, not beyond it.

    Origin: envelope centred on (0, 0, z_min = 0). Callers translate
    to the target location."""
    with BuildPart() as p:
        with BuildSketch():
            Rectangle(item.length_mm, item.width_mm, align=(Align.CENTER, Align.CENTER))
        extrude(amount=item.height_mm)
    part = p.part
    r, g, b = item.display_color
    part.color = Color(r, g, b)
    part.label = f"{item.name} (envelope)"
    return part


def fit_out_car_body(dims: CarDimensions = CarDimensions()) -> Compound:
    """Build the car body plus every COTS envelope in its published
    location, for CAD-sanity visualisation.

    The returned Compound is *not* the structural car — it's the
    structural car *overlaid* with the reserved volumes in their
    catalogue colour. Exporting this to STEP gives a builder a
    single file showing "here's the box + here's where every
    fridge-freezer goes".
    """

    # Flatten the car-body Compound into the fit-out Compound.
    # build123d's `Compound.volume` sums only direct Part children and
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
