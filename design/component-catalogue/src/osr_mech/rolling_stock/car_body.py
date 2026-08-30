"""One passenger car — cabless per RFC 0015.

The car is a welded steel primary frame with composite cladding,
matching the `solar-metro-trainset.png` concept:

- Rounded vertical corners (200 mm radius) and large dark glazing
  for a modern metro profile.
- Low-floor centre door zone at 350 mm rail-to-floor for level
  boarding from the OSR low platform; about 10 m remains low-floor
  between the raised standard-bogie end decks.
- Two wide double-leaf sliding doors per side in the low-floor centre
  zone. The repeated car module keeps dwell capacity high without
  changing the high-floor bogie-end layout.
- Large side windows between / outside the doors, sized to the
  wall segments. Laminated safety glass, bonded frame.
- A green painted livery band running the full length below the
  window line.
- An underframe skirt concealing the equipment bay between the
  bogies (traction pack, battery module, auxiliary converter).
- No cab and no driver door. Both ends are structurally identical;
  the trainset-level sensor cowls provide the single panoramic end glass.

Default dimensions reflect the promoted v2A light-metro module: one
16.5 m self-contained car selected by the design iterator.
"""

from __future__ import annotations

from dataclasses import dataclass

from osr_mech.cad import (
    Align,
    Axis,
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
    fillet,
)
from osr_mech.rolling_stock.baseline import (
    PROMOTED_LIGHT_METRO_CAR_HEIGHT_MM,
    PROMOTED_LIGHT_METRO_CAR_LENGTH_MM,
    PROMOTED_LIGHT_METRO_CAR_WIDTH_MM,
    PROMOTED_ROOF_SOLAR_MODULES_PER_CAR,
)
from osr_mech.rolling_stock.modular_fiberglass_body import fiberglass_cladding_system


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
COLOR_BODY = Color(0.90, 0.90, 0.88)
COLOR_LIVERY = Color(0.02, 0.34, 0.17)
COLOR_DOOR_LEAF = Color(0.07, 0.08, 0.08)
COLOR_GLAZING = Color(0.10, 0.16, 0.16, 0.55)
COLOR_SKIRT = Color(0.32, 0.33, 0.38)
COLOR_ROOF_EQUIPMENT = Color(0.55, 0.55, 0.58)
COLOR_BATTERY_STRAKE = Color(0.25, 0.30, 0.42)
COLOR_SOLAR = Color(0.03, 0.10, 0.24)
COLOR_SOLAR_MOUNT = Color(0.58, 0.61, 0.64)
COLOR_STRUCTURE = Color(0.62, 0.64, 0.66)
COLOR_LOW_FLOOR = Color(0.10, 0.42, 0.30)
COLOR_HIGH_FLOOR = Color(0.44, 0.47, 0.50)
COLOR_INTERIOR = Color(0.74, 0.70, 0.62)
COLOR_HVAC_DUCT = Color(0.76, 0.84, 0.88)
COLOR_LV_DATA = Color(0.05, 0.22, 0.55)
COLOR_HV_CABLE = Color(0.95, 0.38, 0.06)
COLOR_THERMAL = Color(0.10, 0.46, 0.60)
COLOR_SAFETY = Color(0.92, 0.68, 0.12)
COLOR_RUBBER = Color(0.035, 0.035, 0.040)
COLOR_GRILLE = Color(0.12, 0.13, 0.14)
COLOR_STAINLESS = Color(0.68, 0.69, 0.70)
COLOR_LABEL = Color(0.95, 0.82, 0.18)

FLOOR_PLATE_THICKNESS_MM = 95.0
LOW_FLOOR_HEIGHT_MM = DOOR_SILL_HEIGHT_MM
HIGH_FLOOR_HEIGHT_MM = 760.0
# Standard bogies are about 3 m long, so each raised end deck only
# needs to cover the bogie envelope and local service access. The
# remaining centre span stays low-floor for two door pairs, PRM bays,
# and passenger circulation.
END_HIGH_FLOOR_LENGTH_MM = 3000.0
LOW_FLOOR_CENTRE_LENGTH_MM = 10_000.0
FLOOR_TRANSITION_LENGTH_MM = 500.0
SIDE_SILL_HEIGHT_MM = 300.0
ROOF_RAIL_HEIGHT_MM = 170.0
CEILING_DUCT_Z_MM = 3130.0
UNDERFLOOR_SERVICE_Z_MM = -260.0


# Traction-battery module placement per RFC 0021.
#
# OSR uses an **under-seat** pattern: LFP modules are tiled
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

    body_length_mm: float = PROMOTED_LIGHT_METRO_CAR_LENGTH_MM
    body_width_mm: float = PROMOTED_LIGHT_METRO_CAR_WIDTH_MM
    body_height_mm: float = PROMOTED_LIGHT_METRO_CAR_HEIGHT_MM
    doors_per_side: int = 2


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
    """Structural envelope proxy with door and window apertures.

    The detailed steel frame members below carry the certified loads. The
    exterior weather skin is the separate one-metre fiberglass cladding
    system returned by :func:`car_body_exterior`.
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
    p.label = "Car-body structural shell envelope (steel load path)"
    return p


def _glazing(dims: CarDimensions) -> list[Part]:
    """Window glazing bonded into each aperture, both sides."""
    out: list[Part] = []
    for x, width in _window_zones(dims):
        for y_sign in (-1.0, 1.0):
            y = y_sign * (dims.body_width_mm / 2.0 - GLAZING_THICKNESS_MM / 2.0)
            outer_y = y_sign * (dims.body_width_mm / 2.0 + 8.0)
            glass = Box(width, GLAZING_THICKNESS_MM, WINDOW_HEIGHT_MM).locate(
                Location((x, y, WINDOW_SILL_MM + WINDOW_HEIGHT_MM / 2.0))
            )
            glass.color = COLOR_GLAZING
            glass.label = "Window glazing (laminated 8+1.52+8 PVB)"
            out.append(glass)

            top_z = WINDOW_SILL_MM + WINDOW_HEIGHT_MM + 22.0
            bottom_z = WINDOW_SILL_MM - 22.0
            for z, label in (
                (top_z, "Window black ceramic frit upper band"),
                (bottom_z, "Window black ceramic frit lower band"),
            ):
                frit = Box(width + 90.0, 18.0, 44.0).locate(Location((x, outer_y, z)))
                frit.color = COLOR_RUBBER
                frit.label = label
                out.append(frit)

            for edge_x in (x - width / 2.0 - 22.0, x + width / 2.0 + 22.0):
                side_frit = Box(44.0, 18.0, WINDOW_HEIGHT_MM + 90.0).locate(
                    Location((edge_x, outer_y, WINDOW_SILL_MM + WINDOW_HEIGHT_MM / 2.0))
                )
                side_frit.color = COLOR_RUBBER
                side_frit.label = "Window black ceramic frit side band"
                out.append(side_frit)

            retainer = Box(width + 160.0, 18.0, 30.0).locate(
                Location((x, y_sign * (dims.body_width_mm / 2.0 - 42.0), WINDOW_SILL_MM - 82.0))
            )
            retainer.color = COLOR_STAINLESS
            retainer.label = "Bonded window lower retainer and drain rail"
            out.append(retainer)

            busbar = Box(width - 240.0, 14.0, 18.0).locate(
                Location((x, outer_y + y_sign * 4.0, WINDOW_SILL_MM + 96.0))
            )
            busbar.color = COLOR_LABEL
            busbar.label = "Heated glazing demist busbar"
            out.append(busbar)
    return out


def _door_leaves(dims: CarDimensions) -> list[Part]:
    """Inset door panels — double-leaf slider, shown closed."""
    out: list[Part] = []
    leaf_width = (DOOR_WIDTH_MM - 30.0) / 2.0  # 15 mm gap between leaves
    for x in _door_centres_x(dims):
        for y_sign in (-1.0, 1.0):
            y = y_sign * (dims.body_width_mm / 2.0 - DOOR_LEAF_INSET_MM)
            outer_y = y_sign * (dims.body_width_mm / 2.0 + 10.0)
            operator = Box(DOOR_WIDTH_MM + 520.0, 58.0, 135.0).locate(
                Location((x, y_sign * (dims.body_width_mm / 2.0 - 48.0), DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM + 112.0))
            )
            operator.color = COLOR_STAINLESS
            operator.label = "Door top operator access cover"
            out.append(operator)

            track = Box(DOOR_WIDTH_MM + 420.0, 54.0, 44.0).locate(
                Location((x, y_sign * (dims.body_width_mm / 2.0 - 38.0), DOOR_SILL_HEIGHT_MM - 38.0))
            )
            track.color = COLOR_STAINLESS
            track.label = "Door lower guide rail and threshold extrusion"
            out.append(track)

            step_light = Box(DOOR_WIDTH_MM + 140.0, 18.0, 22.0).locate(
                Location((x, outer_y, DOOR_SILL_HEIGHT_MM + 64.0))
            )
            step_light.color = COLOR_LABEL
            step_light.label = "Door threshold warning light strip"
            out.append(step_light)

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

                window = Box(leaf_width - 180.0, 18.0, 980.0).locate(
                    Location((leaf_x, outer_y, DOOR_SILL_HEIGHT_MM + 1200.0))
                )
                window.color = COLOR_GLAZING
                window.label = "Door bonded glass vision panel"
                out.append(window)

                edge_seal = Box(34.0, 24.0, DOOR_HEIGHT_MM - 140.0).locate(
                    Location(
                        (
                            leaf_x - leaf_sign * (leaf_width / 2.0 - 20.0),
                            outer_y + y_sign * 4.0,
                            DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM / 2.0,
                        )
                    )
                )
                edge_seal.color = COLOR_RUBBER
                edge_seal.label = "Door anti-pinch rubber edge"
                out.append(edge_seal)

                pocket_cover = Box(leaf_width - 120.0, 20.0, 70.0).locate(
                    Location((leaf_x, outer_y, DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM - 155.0))
                )
                pocket_cover.color = COLOR_STAINLESS
                pocket_cover.label = "Door hanger cassette cover strip"
                out.append(pocket_cover)

            centre_seal = Box(38.0, 28.0, DOOR_HEIGHT_MM - 120.0).locate(
                Location((x, outer_y + y_sign * 6.0, DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM / 2.0))
            )
            centre_seal.color = COLOR_RUBBER
            centre_seal.label = "Door centre meeting seal and lock stile"
            out.append(centre_seal)

            for lock_z in (880.0, 1380.0):
                keeper = Box(58.0, 34.0, 92.0).locate(
                    Location((x + DOOR_WIDTH_MM / 2.0 + 90.0, outer_y, lock_z))
                )
                keeper.color = COLOR_STAINLESS
                keeper.label = "Door lock keeper and emergency-release detail"
                out.append(keeper)
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
        outer_y = y_sign * (dims.body_width_mm / 2.0 + 8.0)
        skirt = Box(length, SKIRT_THICKNESS_MM, SKIRT_DROP_MM).locate(
            Location((0.0, y, -SKIRT_DROP_MM / 2.0))
        )
        skirt.color = COLOR_SKIRT
        skirt.label = "Underframe skirt"
        out.append(skirt)

        panel_count = 8
        panel_pitch = length / panel_count
        for index in range(panel_count):
            panel_x = -length / 2.0 + panel_pitch * (index + 0.5)
            panel = Box(panel_pitch - 80.0, 18.0, SKIRT_DROP_MM - 110.0).locate(
                Location((panel_x, outer_y, -SKIRT_DROP_MM / 2.0 + 18.0))
            )
            panel.color = COLOR_SKIRT
            panel.label = "Hinged underframe equipment access panel"
            out.append(panel)

            latch = Box(46.0, 20.0, 60.0).locate(
                Location((panel_x + panel_pitch / 2.0 - 90.0, outer_y + y_sign * 4.0, -175.0))
            )
            latch.color = COLOR_STAINLESS
            latch.label = "Quarter-turn skirt latch"
            out.append(latch)

            if index % 2 == 0:
                grille = Box(panel_pitch - 260.0, 22.0, 95.0).locate(
                    Location((panel_x, outer_y + y_sign * 5.0, -360.0))
                )
                grille.color = COLOR_GRILLE
                grille.label = "Underframe converter cooling grille"
                out.append(grille)

            drain = Box(90.0, 22.0, 28.0).locate(
                Location((panel_x - panel_pitch / 2.0 + 120.0, outer_y + y_sign * 4.0, -514.0))
            )
            drain.color = COLOR_STAINLESS
            drain.label = "Skirt drain slot"
            out.append(drain)
    return out


def _roof_equipment(dims: CarDimensions) -> list[Part]:
    """Rooftop equipment — PV modules plus compact HVAC/end boxes.

    Because OSR is catenary-free and uses under-seat batteries, the
    concept reserves most roof area for PV panels. HVAC modules sit
    near the car ends, matching the concept roof plan.
    """
    out: list[Part] = []
    pv_length = dims.body_length_mm - 900.0
    pv_width = dims.body_width_mm - 300.0
    panel_rows = 2
    panel_columns = PROMOTED_ROOF_SOLAR_MODULES_PER_CAR // panel_rows
    panel_count = panel_columns * panel_rows
    panel_pitch_x = pv_length / panel_columns
    panel_pitch_y = pv_width / panel_rows
    panel_length = panel_pitch_x - 70.0
    panel_width = panel_pitch_y - 70.0
    for column in range(panel_columns):
        panel_x = -pv_length / 2.0 + panel_pitch_x * (column + 0.5)
        for row in range(panel_rows):
            index = column * panel_rows + row
            mount_y = -pv_width / 2.0 + panel_pitch_y * (row + 0.5)
            label = (
                "Bonded flexible rooftop solar laminate"
                if index < panel_count / 2
                else "Rail-clamped rooftop solar panel"
            )
            if index < panel_count / 2:
                pad = Box(panel_length + 50.0, panel_width + 42.0, 18.0).locate(
                    Location((panel_x, mount_y, dims.body_height_mm + 46.0))
                )
                pad.color = COLOR_RUBBER
                pad.label = "Bonded flexible rooftop solar laminate mount"
                out.append(pad)
                panel_z = dims.body_height_mm + 63.0
            else:
                for rail_y in (mount_y - panel_width / 2.0 + 80.0, mount_y + panel_width / 2.0 - 80.0):
                    rail = Box(panel_length + 80.0, 42.0, 46.0).locate(
                        Location((panel_x, rail_y, dims.body_height_mm + 70.0))
                    )
                    rail.color = COLOR_SOLAR_MOUNT
                    rail.label = "Rail-clamped raised rooftop solar panel mount"
                    out.append(rail)
                    for clamp_x in (panel_x - panel_length / 2.0 + 150.0, panel_x + panel_length / 2.0 - 150.0):
                        clamp = Box(54.0, 72.0, 54.0).locate(
                            Location((clamp_x, rail_y, dims.body_height_mm + 104.0))
                        )
                        clamp.color = COLOR_STAINLESS
                        clamp.label = "Roof solar module edge clamp"
                        out.append(clamp)
                panel_z = dims.body_height_mm + 132.0

            panel = Box(panel_length, panel_width, 34.0).locate(
                Location((panel_x, mount_y, panel_z))
            )
            panel.color = COLOR_SOLAR
            panel.label = label
            out.append(panel)

            junction = Box(130.0, 90.0, 48.0).locate(
                Location((panel_x + panel_length / 2.0 - 120.0, mount_y, panel_z + 36.0))
            )
            junction.color = COLOR_HV_CABLE
            junction.label = "Roof PV module junction box"
            out.append(junction)

    for y in (-pv_width / 4.0, pv_width / 4.0):
        string_bus = Box(pv_length - 500.0, 18.0, 22.0).locate(
            Location((0.0, y, dims.body_height_mm + 172.0))
        )
        string_bus.color = COLOR_HV_CABLE
        string_bus.label = "Roof PV string wiring raceway"
        out.append(string_bus)

    for x in (-pv_length / 2.0 + panel_pitch_x * 4.0, pv_length / 2.0 - panel_pitch_x):
        isolator = Box(360.0, 260.0, 115.0).locate(
            Location((x, 0.0, dims.body_height_mm + 170.0))
        )
        isolator.color = COLOR_SAFETY
        isolator.label = "Roof PV fire-isolation switch box"
        out.append(isolator)

    for x_sign in (-1.0, 1.0):
        hvac_x = x_sign * (dims.body_length_mm / 2.0 - 720.0)
        hvac_z = dims.body_height_mm + 180.0
        curb = Box(1260.0, 1160.0, 70.0).locate(
            Location((hvac_x, 0.0, dims.body_height_mm + 52.0))
        )
        curb.color = COLOR_RUBBER
        curb.label = "Roof HVAC gasketed mounting curb"
        out.append(curb)

        hvac = Box(1150.0, 1050.0, 360.0).locate(
            Location(
                (
                    hvac_x,
                    0.0,
                    hvac_z,
                )
            )
        )
        hvac.color = COLOR_ROOF_EQUIPMENT
        hvac.label = "Compact end HVAC roof unit"
        out.append(hvac)

        for fan_offset in (-250.0, 250.0):
            fan = Cylinder(radius=152.0, height=26.0).locate(
                Location((hvac_x + fan_offset, 0.0, dims.body_height_mm + 374.0))
            )
            fan.color = COLOR_GRILLE
            fan.label = "HVAC condenser fan grille"
            out.append(fan)

            hub = Cylinder(radius=52.0, height=32.0).locate(
                Location((hvac_x + fan_offset, 0.0, dims.body_height_mm + 386.0))
            )
            hub.color = COLOR_STAINLESS
            hub.label = "HVAC fan hub"
            out.append(hub)

        for y in (-548.0, 548.0):
            side_grille = Box(760.0, 28.0, 185.0).locate(
                Location((hvac_x, y, dims.body_height_mm + 212.0))
            )
            side_grille.color = COLOR_GRILLE
            side_grille.label = "HVAC side intake and return grille"
            out.append(side_grille)

        for x_local in (-420.0, 420.0):
            hatch = Box(270.0, 260.0, 18.0).locate(
                Location((hvac_x + x_local, -260.0, dims.body_height_mm + 372.0))
            )
            hatch.color = COLOR_STAINLESS
            hatch.label = "HVAC service hatch with captive fasteners"
            out.append(hatch)

        for lug_x in (-520.0, 520.0):
            for lug_y in (-470.0, 470.0):
                lug = Box(62.0, 42.0, 58.0).locate(
                    Location((hvac_x + lug_x, lug_y, dims.body_height_mm + 389.0))
                )
                lug.color = COLOR_STAINLESS
                lug.label = "HVAC lifting lug"
                out.append(lug)

        drain = Box(42.0, 92.0, 42.0).locate(
            Location((hvac_x - x_sign * 480.0, -590.0, dims.body_height_mm + 58.0))
        )
        drain.color = COLOR_STAINLESS
        drain.label = "HVAC condensate drain spigot"
        out.append(drain)
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


def _floor_and_structure(dims: CarDimensions) -> list[Part]:
    """Fabricated underframe and load paths inside the body shell."""

    out: list[Part] = []
    low_floor = Box(
        LOW_FLOOR_CENTRE_LENGTH_MM,
        dims.body_width_mm - 240.0,
        FLOOR_PLATE_THICKNESS_MM,
    ).locate(Location((0.0, 0.0, LOW_FLOOR_HEIGHT_MM - FLOOR_PLATE_THICKNESS_MM / 2.0)))
    low_floor.color = COLOR_LOW_FLOOR
    low_floor.label = "Low-floor centre door and PRM floor pan"
    out.append(low_floor)

    for x_sign in (-1.0, 1.0):
        bogie_x = x_sign * (dims.body_length_mm / 2.0 - 2100.0)
        high_floor = Box(
            END_HIGH_FLOOR_LENGTH_MM,
            dims.body_width_mm - 300.0,
            FLOOR_PLATE_THICKNESS_MM,
        ).locate(
            Location(
                (
                    x_sign * (dims.body_length_mm / 2.0 - END_HIGH_FLOOR_LENGTH_MM / 2.0 - 280.0),
                    0.0,
                    HIGH_FLOOR_HEIGHT_MM - FLOOR_PLATE_THICKNESS_MM / 2.0,
                )
            )
        )
        high_floor.color = COLOR_HIGH_FLOOR
        high_floor.label = "Raised high-floor bogie-end deck"
        out.append(high_floor)

        ramp_x = x_sign * (LOW_FLOOR_CENTRE_LENGTH_MM / 2.0 + FLOOR_TRANSITION_LENGTH_MM / 2.0)
        ramp = Box(
            FLOOR_TRANSITION_LENGTH_MM,
            dims.body_width_mm - 360.0,
            70.0,
        ).locate(
            Location(
                (
                    ramp_x,
                    0.0,
                    (LOW_FLOOR_HEIGHT_MM + HIGH_FLOOR_HEIGHT_MM) / 2.0,
                )
            )
        )
        ramp.color = COLOR_INTERIOR
        ramp.label = "Interior ramp between low centre and raised bogie floor"
        out.append(ramp)

        clearance = Box(3600.0, dims.body_width_mm + 260.0, 760.0).locate(
            Location((bogie_x, 0.0, 430.0))
        )
        clearance.color = Color(0.45, 0.58, 0.68, 0.18)
        clearance.label = "Bogie rotation and suspension-travel clearance envelope"
        out.append(clearance)

        drop_zone = Box(3200.0, dims.body_width_mm - 420.0, 120.0).locate(
            Location((bogie_x, 0.0, -120.0))
        )
        drop_zone.color = COLOR_SAFETY
        drop_zone.label = "Wheel-change and bogie drop clearance zone"
        out.append(drop_zone)

        end_ring = Box(150.0, dims.body_width_mm - 240.0, dims.body_height_mm - 420.0).locate(
            Location((x_sign * (dims.body_length_mm / 2.0 - 210.0), 0.0, 1710.0))
        )
        end_ring.color = COLOR_STRUCTURE
        end_ring.label = "End ring frame for single glass-pane cowl"
        out.append(end_ring)

        anti_climber = Box(260.0, dims.body_width_mm - 360.0, 260.0).locate(
            Location((x_sign * (dims.body_length_mm / 2.0 - 420.0), 0.0, 740.0))
        )
        anti_climber.color = COLOR_STRUCTURE
        anti_climber.label = "Anti-climber load beam"
        out.append(anti_climber)

    for y_sign in (-1.0, 1.0):
        y = y_sign * (dims.body_width_mm / 2.0 - 135.0)
        side_sill = Box(
            dims.body_length_mm - 1000.0,
            170.0,
            SIDE_SILL_HEIGHT_MM,
        ).locate(Location((0.0, y, SIDE_SILL_HEIGHT_MM / 2.0)))
        side_sill.color = COLOR_STRUCTURE
        side_sill.label = "Laser-cut side sill beam"
        out.append(side_sill)

        centre_sill = Box(
            LOW_FLOOR_CENTRE_LENGTH_MM + 2 * FLOOR_TRANSITION_LENGTH_MM,
            140.0,
            220.0,
        ).locate(Location((0.0, y_sign * (dims.body_width_mm / 2.0 - 120.0), LOW_FLOOR_HEIGHT_MM - 110.0)))
        centre_sill.color = COLOR_STRUCTURE
        centre_sill.label = "Lowered side sill through low-floor door zone"
        out.append(centre_sill)

        for x_sign in (-1.0, 1.0):
            plinth = Box(
                END_HIGH_FLOOR_LENGTH_MM,
                120.0,
                310.0,
            ).locate(
                Location(
                    (
                        x_sign * (dims.body_length_mm / 2.0 - END_HIGH_FLOOR_LENGTH_MM / 2.0 - 280.0),
                        y_sign * (dims.body_width_mm / 2.0 - 105.0),
                        HIGH_FLOOR_HEIGHT_MM - 155.0,
                    )
                )
            )
            plinth.color = COLOR_STRUCTURE
            plinth.label = "Raised side plinth over standard bogie zone"
            out.append(plinth)

        roof_rail = Box(
            dims.body_length_mm - 1300.0,
            135.0,
            ROOF_RAIL_HEIGHT_MM,
        ).locate(
            Location(
                (
                    0.0,
                    y_sign * (dims.body_width_mm / 2.0 - 120.0),
                    dims.body_height_mm - 170.0,
                )
            )
        )
        roof_rail.color = COLOR_STRUCTURE
        roof_rail.label = "Roof cantrail extrusion"
        out.append(roof_rail)

        for x, width in _window_zones(dims):
            waist = Box(width + 340.0, 120.0, 105.0).locate(
                Location((x, y_sign * (dims.body_width_mm / 2.0 - 120.0), WINDOW_SILL_MM - 120.0))
            )
            waist.color = COLOR_STRUCTURE
            waist.label = "Waist rail under window cassette"
            out.append(waist)

            for side in (-1.0, 1.0):
                post = Box(95.0, 115.0, WINDOW_HEIGHT_MM + 420.0).locate(
                    Location(
                        (
                            x + side * (width / 2.0 + 120.0),
                            y_sign * (dims.body_width_mm / 2.0 - 120.0),
                            WINDOW_SILL_MM + WINDOW_HEIGHT_MM / 2.0,
                        )
                    )
                )
                post.color = COLOR_STRUCTURE
                post.label = "Window post"
                out.append(post)

    for x in (-7600.0, -5100.0, -2500.0, 0.0, 2500.0, 5100.0, 7600.0):
        crossmember = Box(105.0, dims.body_width_mm - 420.0, 210.0).locate(
            Location((x, 0.0, 175.0))
        )
        crossmember.color = COLOR_STRUCTURE
        crossmember.label = "Underframe crossmember"
        out.append(crossmember)

    for x in _door_centres_x(dims):
        for y_sign in (-1.0, 1.0):
            header = Box(DOOR_WIDTH_MM + 420.0, 145.0, 170.0).locate(
                Location(
                    (
                        x,
                        y_sign * (dims.body_width_mm / 2.0 - 120.0),
                        DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM + 150.0,
                    )
                )
            )
            header.color = COLOR_STRUCTURE
            header.label = "Door portal header beam"
            out.append(header)
            for side in (-1.0, 1.0):
                post = Box(145.0, 145.0, DOOR_HEIGHT_MM + 360.0).locate(
                    Location(
                        (
                            x + side * (DOOR_WIDTH_MM / 2.0 + 150.0),
                            y_sign * (dims.body_width_mm / 2.0 - 120.0),
                            DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM / 2.0,
                        )
                    )
                )
                post.color = COLOR_STRUCTURE
                post.label = "Door portal post"
                out.append(post)

    return out


def _interior_fit_out(dims: CarDimensions) -> list[Part]:
    """Passenger-zone interior: seats, grab poles, PRM bays, and ceiling kit."""

    out: list[Part] = []

    aisle = Box(dims.body_length_mm - 2300.0, 950.0, 35.0).locate(
        Location((0.0, 0.0, LOW_FLOOR_HEIGHT_MM + 42.0))
    )
    aisle.color = Color(0.86, 0.74, 0.28, 0.45)
    aisle.label = "Main saloon egress aisle envelope"
    out.append(aisle)

    for x in (-2200.0, 2200.0):
        turn = Box(1500.0, 1500.0, 32.0).locate(
            Location((x, 0.0, LOW_FLOOR_HEIGHT_MM + 62.0))
        )
        turn.color = Color(0.92, 0.72, 0.18, 0.42)
        turn.label = "Wheelchair turning circle envelope"
        out.append(turn)

    for x_sign in (-1.0, 1.0):
        viewing = Box(1260.0, dims.body_width_mm - 760.0, 28.0).locate(
            Location((x_sign * (dims.body_length_mm / 2.0 - 940.0), 0.0, HIGH_FLOOR_HEIGHT_MM + 40.0))
        )
        viewing.color = Color(0.42, 0.64, 0.74, 0.35)
        viewing.label = "Glass-pane end passenger viewing zone"
        out.append(viewing)

    for x, width in _window_zones(dims):
        on_high_floor = abs(x) > LOW_FLOOR_CENTRE_LENGTH_MM / 2.0
        seat_base_z = (HIGH_FLOOR_HEIGHT_MM + 170.0) if on_high_floor else 520.0
        seat_back_z = (HIGH_FLOOR_HEIGHT_MM + 500.0) if on_high_floor else 850.0
        seat_label = (
            "Longitudinal bench seat base on raised bogie floor"
            if on_high_floor
            else "Longitudinal bench seat base over battery module"
        )
        for y_sign in (-1.0, 1.0):
            seat_base = Box(width - 240.0, 360.0, 120.0).locate(
                Location((x, y_sign * (dims.body_width_mm / 2.0 - 380.0), seat_base_z))
            )
            seat_base.color = COLOR_INTERIOR
            seat_base.label = seat_label
            out.append(seat_base)

            back = Box(width - 240.0, 70.0, 660.0).locate(
                Location((x, y_sign * (dims.body_width_mm / 2.0 - 205.0), seat_back_z))
            )
            back.color = COLOR_INTERIOR
            back.label = "Longitudinal bench seat back"
            out.append(back)

    for x in (-2700.0, 2700.0):
        bay = Box(1450.0, 860.0, 36.0).locate(Location((x, 0.0, LOW_FLOOR_HEIGHT_MM + 18.0)))
        bay.color = COLOR_SAFETY
        bay.label = "PRM wheelchair bay clear floor layer"
        out.append(bay)

    for x_sign in (-1.0, 1.0):
        for step_index, z in enumerate((LOW_FLOOR_HEIGHT_MM + 95.0, LOW_FLOOR_HEIGHT_MM + 235.0)):
            step = Box(760.0, dims.body_width_mm - 620.0, 45.0).locate(
                Location(
                    (
                        x_sign * (LOW_FLOOR_CENTRE_LENGTH_MM / 2.0 + 280.0 + step_index * 360.0),
                        0.0,
                        z,
                    )
                )
            )
            step.color = COLOR_SAFETY
            step.label = "Interior step tread to raised bogie-end floor"
            out.append(step)

        for y_sign in (-1.0, 1.0):
            rail = Box(1180.0, 55.0, 55.0).locate(
                Location(
                    (
                        x_sign * (LOW_FLOOR_CENTRE_LENGTH_MM / 2.0 + 660.0),
                        y_sign * 520.0,
                        HIGH_FLOOR_HEIGHT_MM + 780.0,
                    )
                )
            )
            rail.color = COLOR_STRUCTURE
            rail.label = "High-floor step handrail"
            out.append(rail)

    for x in (-6100.0, -3500.0, -1200.0, 1200.0, 3500.0, 6100.0):
        pole = Box(70.0, 70.0, 2400.0).locate(Location((x, 0.0, 1540.0)))
        pole.color = COLOR_STRUCTURE
        pole.label = "Stainless grab pole"
        out.append(pole)

    for y_sign in (-1.0, 1.0):
        handrail = Box(dims.body_length_mm - 3600.0, 55.0, 55.0).locate(
            Location((0.0, y_sign * 760.0, 2520.0))
        )
        handrail.color = COLOR_STRUCTURE
        handrail.label = "Overhead passenger handrail"
        out.append(handrail)

    for x in (-5200.0, 0.0, 5200.0):
        screen = Box(520.0, 55.0, 250.0).locate(Location((x, 0.0, 2620.0)))
        screen.color = COLOR_LV_DATA
        screen.label = "Passenger information display"
        out.append(screen)

    return out


def _hvac_ducting(dims: CarDimensions) -> list[Part]:
    """Supply, return, and drop ducts connecting roof HVAC to saloon."""

    out: list[Part] = []
    centre_supply = Box(dims.body_length_mm - 2600.0, 360.0, 210.0).locate(
        Location((0.0, 0.0, CEILING_DUCT_Z_MM))
    )
    centre_supply.color = COLOR_HVAC_DUCT
    centre_supply.label = "Molded roof-cassette empty HVAC centre supply plenum"
    out.append(centre_supply)

    for y_sign in (-1.0, 1.0):
        return_duct = Box(dims.body_length_mm - 3200.0, 180.0, 150.0).locate(
            Location((0.0, y_sign * 980.0, CEILING_DUCT_Z_MM - 120.0))
        )
        return_duct.color = COLOR_HVAC_DUCT
        return_duct.label = "Molded roof-cassette empty HVAC side return route"
        out.append(return_duct)

    for x in (-6100.0, -3050.0, 0.0, 3050.0, 6100.0):
        diffuser = Box(520.0, 720.0, 36.0).locate(Location((x, 0.0, 2945.0)))
        diffuser.color = COLOR_HVAC_DUCT
        diffuser.label = "Removable HVAC linear diffuser on molded boss"
        out.append(diffuser)

    for x in (-7100.0, 7100.0):
        riser = Box(430.0, 430.0, 780.0).locate(Location((x, 0.0, 3270.0)))
        riser.color = COLOR_HVAC_DUCT
        riser.label = "Removable HVAC roof-unit drop-duct cartridge"
        out.append(riser)

    return out


def _electrical_and_data_routing(dims: CarDimensions) -> list[Part]:
    """Low-voltage, controls, lighting, CCTV, and passenger comms layer."""

    out: list[Part] = []
    for y_sign in (-1.0, 1.0):
        cable_tray = Box(dims.body_length_mm - 2200.0, 105.0, 90.0).locate(
            Location((0.0, y_sign * 1120.0, 2790.0))
        )
        cable_tray.color = COLOR_LV_DATA
        cable_tray.label = "Electrical and data routing layer - LV/TCN cable tray"
        out.append(cable_tray)

        light_strip = Box(dims.body_length_mm - 3400.0, 55.0, 45.0).locate(
            Location((0.0, y_sign * 520.0, 2870.0))
        )
        light_strip.color = COLOR_SAFETY
        light_strip.label = "Continuous LED saloon lighting strip"
        out.append(light_strip)

    for x in (-6700.0, -2200.0, 2200.0, 6700.0):
        camera = Box(170.0, 120.0, 90.0).locate(Location((x, 0.0, 2860.0)))
        camera.color = COLOR_LV_DATA
        camera.label = "CCTV camera and passenger-count sensor"
        out.append(camera)

    for x in _door_centres_x(dims):
        for y_sign in (-1.0, 1.0):
            door_loop = Box(DOOR_WIDTH_MM + 560.0, 65.0, 65.0).locate(
                Location((x, y_sign * 1190.0, 2490.0))
            )
            door_loop.color = COLOR_LV_DATA
            door_loop.label = "Door-control harness loop"
            out.append(door_loop)

            intercom = Box(180.0, 60.0, 260.0).locate(
                Location((x + 560.0, y_sign * 1180.0, 1280.0))
            )
            intercom.color = COLOR_LV_DATA
            intercom.label = "Passenger intercom and help point"
            out.append(intercom)

    return out


def _traction_and_thermal_routing(dims: CarDimensions) -> list[Part]:
    """HV DC, roof-PV, battery, coolant, and fire-isolation paths."""

    out: list[Part] = []
    for y_sign in (-1.0, 1.0):
        hv_tray = Box(dims.body_length_mm - 3800.0, 120.0, 95.0).locate(
            Location((0.0, y_sign * (dims.body_width_mm / 2.0 - 500.0), 705.0))
        )
        hv_tray.color = COLOR_HV_CABLE
        hv_tray.label = "High-voltage traction routing layer - under-seat DC tray"
        out.append(hv_tray)

        coolant = Box(dims.body_length_mm - 4200.0, 70.0, 70.0).locate(
            Location((0.0, y_sign * (dims.body_width_mm / 2.0 - 650.0), 610.0))
        )
        coolant.color = COLOR_THERMAL
        coolant.label = "Battery thermal-management coolant pipe"
        out.append(coolant)

        vent = Box(dims.body_length_mm - 5000.0, 90.0, 180.0).locate(
            Location((0.0, y_sign * (dims.body_width_mm / 2.0 - 70.0), 690.0))
        )
        vent.color = COLOR_SAFETY
        vent.label = "Battery fire vent path to exterior burst panel"
        out.append(vent)

        mist_pipe = Box(dims.body_length_mm - 5000.0, 34.0, 34.0).locate(
            Location((0.0, y_sign * (dims.body_width_mm / 2.0 - 160.0), 930.0))
        )
        mist_pipe.color = COLOR_THERMAL
        mist_pipe.label = "Removable stainless battery water-mist pipe"
        out.append(mist_pipe)

    pv_spine = Box(dims.body_length_mm - 3200.0, 90.0, 90.0).locate(
        Location((0.0, 0.0, dims.body_height_mm + 115.0))
    )
    pv_spine.color = COLOR_HV_CABLE
    pv_spine.label = "Roof PV high-voltage combiner spine"
    out.append(pv_spine)

    down_riser = Box(160.0, 120.0, 2850.0).locate(
        Location((0.0, -dims.body_width_mm / 2.0 + 260.0, 1750.0))
    )
    down_riser.color = COLOR_HV_CABLE
    down_riser.label = "High-voltage traction routing layer - side charging riser"
    out.append(down_riser)

    for x in (-2550.0, 2550.0):
        underfloor = Box(1150.0, 260.0, 170.0).locate(
            Location((x, 0.0, UNDERFLOOR_SERVICE_Z_MM))
        )
        underfloor.color = COLOR_THERMAL
        underfloor.label = "Underfloor coolant and DC service manifold"
        out.append(underfloor)

    return out


def car_body_structure(dims: CarDimensions = CarDimensions()) -> Compound:
    """Primary fabricated structure layer for one car."""

    return Compound(
        label="Primary steel shell, floor, and portal structure subassembly",
        children=[_shell(dims), *_floor_and_structure(dims)],
    )


def car_body_exterior(dims: CarDimensions = CarDimensions()) -> Compound:
    """Exterior layer: clip-on fiberglass skin, glass, doors, roof, and skirts."""

    return Compound(
        label="Exterior 1 m clip-on fiberglass cladding, glazing, doors, solar, and skirt subassembly",
        children=[
            fiberglass_cladding_system(
                body_length_mm=dims.body_length_mm,
                body_width_mm=dims.body_width_mm,
                body_height_mm=dims.body_height_mm,
                door_centres_mm=tuple(_door_centres_x(dims)),
                door_width_mm=DOOR_WIDTH_MM,
                door_sill_mm=DOOR_SILL_HEIGHT_MM,
                door_height_mm=DOOR_HEIGHT_MM,
                window_zones=tuple(_window_zones(dims)),
                window_sill_mm=WINDOW_SILL_MM,
                window_height_mm=WINDOW_HEIGHT_MM,
            ),
            *_glazing(dims),
            *_door_leaves(dims),
            *_livery_band(dims),
            *_underframe_skirt(dims),
            *_roof_equipment(dims),
        ],
    )


def car_body_interior(dims: CarDimensions = CarDimensions()) -> Compound:
    """Passenger interior and under-seat battery bustle layer."""

    return Compound(
        label="Interior passenger fit-out and under-seat battery strake subassembly",
        children=[*_battery_strakes(dims), *_interior_fit_out(dims)],
    )


def car_body_services(dims: CarDimensions = CarDimensions()) -> Compound:
    """HVAC, electrical, high-voltage, thermal, and safety service layers."""

    return Compound(
        label="Car body service layers subassembly",
        children=[
            Compound(
                label="HVAC ducting layer",
                children=_hvac_ducting(dims),
            ),
            Compound(
                label="Electrical and data routing layer",
                children=_electrical_and_data_routing(dims),
            ),
            Compound(
                label="High-voltage traction, PV, thermal, and fire routing layer",
                children=_traction_and_thermal_routing(dims),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def car_body(dims: CarDimensions = CarDimensions()) -> Compound:
    """Full cabless passenger car as nested CAD assemblies.

    Origin: car centre at floor level (z = 0 is rail head); +X is
    along-track, +Y is across-track.

    Returns a Compound containing:
    - Primary steel shell, floor, and portal structure subassembly.
    - Exterior cladding, glazing, doors, livery, solar, and skirt subassembly.
    - Interior passenger fit-out and under-seat battery strake subassembly.
    - HVAC / electrical / high-voltage / thermal service layers.
    """
    return Compound(
        label="Passenger car complete layered body assembly (cabless solar train)",
        children=[
            car_body_structure(dims),
            car_body_exterior(dims),
            car_body_interior(dims),
            car_body_services(dims),
        ],
    )


__all__ = [
    "BATTERY_STRAKE_HEIGHT_MM",
    "BATTERY_STRAKE_WIDTH_MM",
    "COLOR_BATTERY_STRAKE",
    "COLOR_BODY",
    "COLOR_DOOR_LEAF",
    "COLOR_GLAZING",
    "COLOR_HV_CABLE",
    "COLOR_HVAC_DUCT",
    "COLOR_INTERIOR",
    "COLOR_HIGH_FLOOR",
    "COLOR_LOW_FLOOR",
    "COLOR_LIVERY",
    "COLOR_LV_DATA",
    "COLOR_ROOF_EQUIPMENT",
    "COLOR_SAFETY",
    "COLOR_SOLAR",
    "COLOR_SKIRT",
    "COLOR_STRUCTURE",
    "COLOR_THERMAL",
    "CarDimensions",
    "DOOR_HEIGHT_MM",
    "DOOR_SILL_HEIGHT_MM",
    "DOOR_WIDTH_MM",
    "END_HIGH_FLOOR_LENGTH_MM",
    "FLOOR_TRANSITION_LENGTH_MM",
    "HIGH_FLOOR_HEIGHT_MM",
    "LOW_FLOOR_CENTRE_LENGTH_MM",
    "LOW_FLOOR_HEIGHT_MM",
    "WINDOW_HEIGHT_MM",
    "WINDOW_SILL_MM",
    "car_body",
    "car_body_exterior",
    "car_body_interior",
    "car_body_services",
    "car_body_structure",
]
