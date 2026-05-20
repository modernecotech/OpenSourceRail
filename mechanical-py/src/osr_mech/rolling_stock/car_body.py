"""One passenger car — cabless per RFC 0015.

The car is a welded-aluminium monocoque shell with:

- Rounded vertical corners (200 mm radius) for a modern profile +
  better side-wind behaviour.
- Low-floor centre door zone at 350 mm rail-to-floor for level
  boarding from the OSR low platform; raised floor remains over the
  standard bogies.
- One wide centre double-leaf sliding door per side. Longer consists
  add cars, not extra door patterns, so every self-contained car stays
  mechanically identical.
- Large side windows between / outside the doors, sized to the
  wall segments. Laminated safety glass, bonded frame.
- A painted livery band running the full length at window-sill
  height — the only colour detail on the exterior.
- An underframe skirt concealing the equipment bay between the
  bogies (traction pack, battery module, auxiliary converter).
- No cab, no windscreen, no driver door. Both ends are
  structurally identical — the sensor cowl lives on the trainset,
  not on the car.

Default dimensions reflect one 17 m self-contained car module per
RFC 0008 §3.1.
"""

from __future__ import annotations

from dataclasses import dataclass

from build123d import (
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
    fillet,
)


# ---------------------------------------------------------------------------
# Dimensions
# ---------------------------------------------------------------------------

DOOR_WIDTH_MM = 1400.0
DOOR_HEIGHT_MM = 2000.0
DOOR_SILL_HEIGHT_MM = 350.0  # above rail head at the low-floor door zone

# Windows: one per wall segment (between / outside doors). Height +
# sill picked so the top of the window sits ~400 mm below the roof
# and the bottom is ~1.5 m above floor (comfortable viewing while
# standing).
WINDOW_HEIGHT_MM = 900.0
WINDOW_SILL_MM = 1500.0
# End-zone windows are wider than mid-zone windows (end zones are
# longer per the door-placement math); we compute per-zone below.
WINDOW_MARGIN_MM = 600.0  # spacing between window edge and door / nose

# Profile details
VERTICAL_CORNER_RADIUS_MM = 200.0

# Livery band. Visually we render it as a raised strake so the colour
# reads clearly at distance; in real manufacture it would be a paint
# band (no physical protrusion).
LIVERY_BAND_HEIGHT_MM = 220.0
LIVERY_BAND_Z_MM = 880.0  # Z of band's bottom edge — below window sill
LIVERY_BAND_PROUD_MM = 60.0

# Door leaves — inset into the opening, painted dark.
DOOR_LEAF_INSET_MM = 60.0
DOOR_LEAF_THICKNESS_MM = 40.0

# Window glazing — bonded flush with the body skin.
GLAZING_THICKNESS_MM = 28.0

# Underframe skirt — extends below the floor, concealing the
# equipment bay between the bogies.
SKIRT_DROP_MM = 500.0
SKIRT_THICKNESS_MM = 30.0
SKIRT_BOGIE_CLEAR_MM = 4200.0  # gap at each car end for the bogie

# Colours (v0.1 livery — operators override per-deployment).
COLOR_BODY = Color(0.93, 0.93, 0.95)
COLOR_LIVERY = Color(0.10, 0.35, 0.65)
COLOR_DOOR_LEAF = Color(0.08, 0.20, 0.38)
COLOR_GLAZING = Color(0.55, 0.75, 0.90, 0.45)
COLOR_SKIRT = Color(0.32, 0.33, 0.38)
COLOR_ROOF_EQUIPMENT = Color(0.55, 0.55, 0.58)
COLOR_BATTERY_STRAKE = Color(0.25, 0.30, 0.42)


# Traction-battery module placement per RFC 0021.
#
# OSR uses an **under-seat** pattern: sodium-ion modules are tiled
# along the inside of each body wall, under the longitudinal bench
# seats. The low-floor centre aisle and door zone stay clear. This is
# different from
# Stadler's Akku (rooftop) and from most Siemens / Alstom BEMUs
# (deep underfloor) — we pick under-seat because:
#
# - Low centre of gravity (better curve stability than rooftop).
# - Shaded from direct 50 °C Samawah sun (not sat on the hot roof).
# - Doesn't compete with traction inverter / brake resistor / aux
#   converter for underframe space (already crowded).
# - Station side-pin charging matches the physical location of the
#   battery string termination — no need to route HV DC from
#   a rooftop pack down through the shell.
# - Thermal runaway vents laterally out the body skin (not up into
#   passengers or down onto the track / bogie).
#
# Each visible module is a low slab running along the inside of the
# skin, with the longitudinal bench seat cantilevered on top.
BATTERY_STRAKE_WIDTH_MM = 320.0  # into the cabin from the skin
BATTERY_STRAKE_HEIGHT_MM = 450.0  # rests between floor and seat base
# Module sits from floor level up to the bench base (≈ 450 mm).
BATTERY_STRAKE_BASE_Z_MM = 20.0
# The COTS longitudinal bench is 950 mm tall (seat-pan + backrest
# zone). The battery module lives below it — 20 mm above floor to
# 470 mm. Above that is the seat structure.


@dataclass(frozen=True)
class CarDimensions:
    """Parametric footprint of a single passenger car."""

    body_length_mm: float = 17_000.0
    body_width_mm: float = 2650.0
    body_height_mm: float = 3600.0
    doors_per_side: int = 1


# ---------------------------------------------------------------------------
# Geometry helpers — door + window zone placement
# ---------------------------------------------------------------------------


def _door_centres_x(dims: CarDimensions) -> list[float]:
    spacing = dims.body_length_mm / (dims.doors_per_side + 1)
    return [
        -dims.body_length_mm / 2.0 + (i + 1) * spacing
        for i in range(dims.doors_per_side)
    ]


def _window_zones(dims: CarDimensions) -> list[tuple[float, float]]:
    """For each wall segment between / outside the doors, return the
    `(x_centre, width)` of a window sized to fill that segment with a
    `WINDOW_MARGIN_MM` margin on each side.

    There are `doors_per_side + 1` zones per side."""
    doors = _door_centres_x(dims)
    half_L = dims.body_length_mm / 2.0
    half_door = DOOR_WIDTH_MM / 2.0
    edges = [-half_L] + doors + [half_L]
    zones: list[tuple[float, float]] = []
    for i in range(len(edges) - 1):
        left = edges[i] + (half_door if 0 < i else 0.0)
        right = edges[i + 1] - (half_door if i + 1 < len(edges) - 1 else 0.0)
        width = max(0.0, right - left - 2 * WINDOW_MARGIN_MM)
        if width < 400.0:
            continue  # too small to bother — skip
        zones.append(((left + right) / 2.0, width))
    return zones


# ---------------------------------------------------------------------------
# Part builders
# ---------------------------------------------------------------------------


def _shell(dims: CarDimensions) -> Part:
    """Rounded-corner monocoque shell with door + window apertures
    cut through. No glazing, no door leaves — those are separate
    Parts bonded in.
    """

    with BuildPart() as b:
        with BuildSketch():
            Rectangle(
                dims.body_length_mm,
                dims.body_width_mm,
                align=(Align.CENTER, Align.CENTER),
            )
        extrude(amount=dims.body_height_mm)
        fillet(b.edges().filter_by(Axis.Z), radius=VERTICAL_CORNER_RADIUS_MM)

    p = b.part

    # Doors — through-cuts the full body thickness.
    for x in _door_centres_x(dims):
        door_cut = Box(
            DOOR_WIDTH_MM,
            dims.body_width_mm + 100.0,
            DOOR_HEIGHT_MM,
        ).locate(
            Location((x, 0.0, DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM / 2.0))
        )
        p = p - door_cut

    # Windows — through-cuts.
    for x, width in _window_zones(dims):
        window_cut = Box(
            width,
            dims.body_width_mm + 100.0,
            WINDOW_HEIGHT_MM,
        ).locate(
            Location((x, 0.0, WINDOW_SILL_MM + WINDOW_HEIGHT_MM / 2.0))
        )
        p = p - window_cut

    p.color = COLOR_BODY
    p.label = "Car-body shell (welded-aluminium monocoque)"
    return p


def _glazing(dims: CarDimensions) -> list[Part]:
    """Window glazing bonded into each aperture, both sides."""
    out: list[Part] = []
    for x, width in _window_zones(dims):
        for y_sign in (-1.0, 1.0):
            y = y_sign * (dims.body_width_mm / 2.0 - GLAZING_THICKNESS_MM / 2.0)
            glass = Box(width, GLAZING_THICKNESS_MM, WINDOW_HEIGHT_MM).locate(
                Location((x, y, WINDOW_SILL_MM + WINDOW_HEIGHT_MM / 2.0))
            )
            glass.color = COLOR_GLAZING
            glass.label = "Window glazing (laminated 8+1.52+8 PVB)"
            out.append(glass)
    return out


def _door_leaves(dims: CarDimensions) -> list[Part]:
    """Inset door panels — double-leaf slider, shown closed."""
    out: list[Part] = []
    leaf_width = (DOOR_WIDTH_MM - 30.0) / 2.0  # 15 mm gap between leaves
    for x in _door_centres_x(dims):
        for y_sign in (-1.0, 1.0):
            y = y_sign * (dims.body_width_mm / 2.0 - DOOR_LEAF_INSET_MM)
            for leaf_sign in (-1.0, 1.0):
                leaf_x = x + leaf_sign * (leaf_width / 2.0 + 8.0)
                leaf = Box(
                    leaf_width,
                    DOOR_LEAF_THICKNESS_MM,
                    DOOR_HEIGHT_MM - 30.0,
                ).locate(
                    Location((leaf_x, y, DOOR_SILL_HEIGHT_MM + (DOOR_HEIGHT_MM - 30.0) / 2.0 + 15.0))
                )
                leaf.color = COLOR_DOOR_LEAF
                leaf.label = "Door leaf"
                out.append(leaf)
    return out


def _livery_band(dims: CarDimensions) -> list[Part]:
    """Painted livery band running the full car length, both sides."""
    out: list[Part] = []
    for y_sign in (-1.0, 1.0):
        y = y_sign * (dims.body_width_mm / 2.0 + LIVERY_BAND_PROUD_MM / 2.0)
        band = Box(
            dims.body_length_mm - 2 * VERTICAL_CORNER_RADIUS_MM,
            LIVERY_BAND_PROUD_MM,
            LIVERY_BAND_HEIGHT_MM,
        ).locate(
            Location((0.0, y, LIVERY_BAND_Z_MM + LIVERY_BAND_HEIGHT_MM / 2.0))
        )
        band.color = COLOR_LIVERY
        band.label = "Livery band"
        out.append(band)
    return out


def _underframe_skirt(dims: CarDimensions) -> list[Part]:
    """Underframe skirts, both sides — conceal the equipment bay
    between the bogies. Clear the bogie footprint at each car end."""
    out: list[Part] = []
    length = max(0.0, dims.body_length_mm - SKIRT_BOGIE_CLEAR_MM)
    if length <= 0.0:
        return out
    for y_sign in (-1.0, 1.0):
        y = y_sign * (dims.body_width_mm / 2.0 - SKIRT_THICKNESS_MM / 2.0)
        skirt = Box(length, SKIRT_THICKNESS_MM, SKIRT_DROP_MM).locate(
            Location((0.0, y, -SKIRT_DROP_MM / 2.0))
        )
        skirt.color = COLOR_SKIRT
        skirt.label = "Underframe skirt"
        out.append(skirt)
    return out


def _roof_equipment(dims: CarDimensions) -> list[Part]:
    """Rooftop equipment — HVAC unit + a couple of aux boxes.

    Because OSR is catenary-free *and* side-wall battery per
    RFC 0021, the roof is deliberately sparse: no pantograph, no
    HV breaker, no battery pack. Just HVAC + radio / beacon aux.
    """
    out: list[Part] = []
    hvac = Box(1800.0, 1200.0, 400.0).locate(
        Location((0.0, 0.0, dims.body_height_mm + 200.0))
    )
    hvac.color = COLOR_ROOF_EQUIPMENT
    hvac.label = "HVAC roof unit"
    out.append(hvac)
    # Two small boxes flanking the HVAC — radio / beacon + aux cooling.
    for x_sign in (-1.0, 1.0):
        aux = Box(800.0, 600.0, 300.0).locate(
            Location(
                (
                    x_sign * (dims.body_length_mm / 2.0 - 3_000.0),
                    0.0,
                    dims.body_height_mm + 150.0,
                )
            )
        )
        aux.color = COLOR_ROOF_EQUIPMENT
        aux.label = "Roof auxiliary"
        out.append(aux)
    return out


def _battery_strakes(dims: CarDimensions) -> list[Part]:
    """Side-wall traction-battery strakes (RFC 0021 bustle-wall).

    Three strakes per side (one per inter-door zone + end zone)
    tiled along the inside of each body wall, from 20 mm above
    floor to ~470 mm. The longitudinal bench seats cantilever
    above them. The centre aisle stays clear.

    The strake layout mirrors the window-zone placement, so each
    seat run + window zone + battery strake occupy the same wall
    segment. An operator swapping a module at depot opens the bench
    cushion → removes the strake access panel → lifts out a module
    with standard lifting-eye hooks. No crane, no overhead access.
    """
    out: list[Part] = []

    # Zones are the same as the window zones — one strake per zone
    # per side, straddling the wall between door openings.
    for x, width in _window_zones(dims):
        for y_sign in (-1.0, 1.0):
            y = y_sign * (dims.body_width_mm / 2.0 - BATTERY_STRAKE_WIDTH_MM / 2.0 - 40.0)
            strake = Box(
                width - 100.0,  # leave a 50 mm gap each side
                BATTERY_STRAKE_WIDTH_MM,
                BATTERY_STRAKE_HEIGHT_MM,
            ).locate(
                Location(
                    (
                        x,
                        y,
                        BATTERY_STRAKE_BASE_Z_MM + BATTERY_STRAKE_HEIGHT_MM / 2.0,
                    )
                )
            )
            strake.color = COLOR_BATTERY_STRAKE
            strake.label = "Traction battery strake (RFC 0021)"
            out.append(strake)

    return out


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def car_body(dims: CarDimensions = CarDimensions()) -> Compound:
    """Full cabless passenger car.

    Origin: car centre at floor level (z = 0 is rail head); +X is
    along-track, +Y is across-track.

    Returns a Compound containing:
    - `Car-body shell` (aluminium monocoque with door + window cuts)
    - Window glazing (both sides)
    - Door leaves (both sides, double-leaf slider, shown closed)
    - Livery band (both sides, full length)
    - Underframe skirts (both sides, between the bogies)
    - Traction battery strakes (side-wall bustle, RFC 0021)
    - Rooftop equipment (HVAC + two aux boxes — no pantograph,
      no rooftop battery)
    """
    parts: list[Part | Compound] = []
    parts.append(_shell(dims))
    parts.extend(_glazing(dims))
    parts.extend(_door_leaves(dims))
    parts.extend(_livery_band(dims))
    parts.extend(_underframe_skirt(dims))
    parts.extend(_battery_strakes(dims))
    parts.extend(_roof_equipment(dims))
    return Compound(label="Passenger car (cabless, battery-electric)", children=parts)


__all__ = [
    "BATTERY_STRAKE_HEIGHT_MM",
    "BATTERY_STRAKE_WIDTH_MM",
    "COLOR_BATTERY_STRAKE",
    "COLOR_BODY",
    "COLOR_DOOR_LEAF",
    "COLOR_GLAZING",
    "COLOR_LIVERY",
    "COLOR_ROOF_EQUIPMENT",
    "COLOR_SKIRT",
    "CarDimensions",
    "DOOR_HEIGHT_MM",
    "DOOR_SILL_HEIGHT_MM",
    "DOOR_WIDTH_MM",
    "WINDOW_HEIGHT_MM",
    "WINDOW_SILL_MM",
    "car_body",
]
