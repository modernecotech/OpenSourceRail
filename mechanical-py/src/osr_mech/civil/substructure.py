"""Parametric viaduct pier and abutment planning kits.

The standard elevated bay uses two single-track decked pi-beams on one shared
double-track substructure.  Geometry is a repeatable interface envelope;
deployment geotechnics, reinforcement, seismic, collision, scour, utilities,
and stamped calculations remain mandatory release gates.
"""

from __future__ import annotations

from dataclasses import dataclass
from osr_mech.cad import Box, Color, Compound, Cylinder, Location, Part
from .decked_pi import STEM_CENTRE_OFFSET_MM
from .foundation import foundation_type


PIER_COLUMN_X_MM = 1_500.0
PIER_COLUMN_Y_MM = 2_000.0
PIER_MIN_HEIGHT_M = 5.0
PIER_MAX_HEIGHT_M = 12.0
PIER_CAP_X_MM = 2_500.0
PIER_CAP_Y_MM = 7_000.0
PIER_CAP_HEIGHT_MM = 1_200.0
GIRDER_CENTRE_SPACING_MM = 3_500.0
BEARING_X_MM = 600.0
BEARING_Y_MM = 500.0
BEARING_HEIGHT_MM = 100.0
BEARING_ROW_SPACING_MM = 900.0
# Bearings sit under the web centrelines, not at a legacy fixed offset.
WEB_BEARING_OFFSET_MM = STEM_CENTRE_OFFSET_MM
ABUTMENT_WIDTH_MM = 8_500.0
ABUTMENT_FOUNDATION_WIDTH_MM = 9_000.0


@dataclass(frozen=True)
class CivilKitItem:
    id: str
    title: str
    quantity: float
    unit: str
    release_gate: str


def _part(size: tuple[float, float, float], loc: tuple[float, float, float], label: str, color: Color) -> Part:
    item = Box(*size).locate(Location(loc))
    item.label = label
    item.color = color
    return item


def _bearing_parts(z_mm: float, *, double_bearing_line: bool) -> list[Part]:
    bearing = Color(0.18, 0.18, 0.20)
    parts: list[Part] = []
    row_x_positions = (
        (-BEARING_ROW_SPACING_MM / 2.0, BEARING_ROW_SPACING_MM / 2.0)
        if double_bearing_line
        else (0.0,)
    )
    for girder_y in (-GIRDER_CENTRE_SPACING_MM / 2.0, GIRDER_CENTRE_SPACING_MM / 2.0):
        for offset_y in (-WEB_BEARING_OFFSET_MM, WEB_BEARING_OFFSET_MM):
            for row_x in row_x_positions:
                parts.append(
                    _part(
                        (BEARING_X_MM, BEARING_Y_MM, BEARING_HEIGHT_MM),
                        (row_x, girder_y + offset_y, z_mm + BEARING_HEIGHT_MM / 2.0),
                        "Elastomeric/PTFE girder bearing",
                        bearing,
                    )
                )
    return parts


def _jacking_shelf_parts(z_mm: float) -> list[Part]:
    """Four permanent web-line interfaces for bearing replacement."""

    steel = Color(0.32, 0.36, 0.38)
    parts: list[Part] = []
    for girder_y in (-GIRDER_CENTRE_SPACING_MM / 2.0, GIRDER_CENTRE_SPACING_MM / 2.0):
        for offset_y in (-WEB_BEARING_OFFSET_MM, WEB_BEARING_OFFSET_MM):
            parts.append(
                _part(
                    (250.0, 500.0, 80.0),
                    (0.0, girder_y + offset_y, z_mm + 40.0),
                    "Permanent bearing-replacement jacking shelf interface",
                    steel,
                )
            )
    return parts


def _pier_cap_shell(loc_z_mm: float) -> Part:
    """Hollow/precast-shell planning cap, not an 84-tonne solid block."""

    outer = Box(PIER_CAP_X_MM, PIER_CAP_Y_MM, PIER_CAP_HEIGHT_MM).locate(
        Location((0.0, 0.0, loc_z_mm))
    )
    void = Box(2_000.0, 6_500.0, 800.0).locate(Location((0.0, 0.0, loc_z_mm)))
    shell = outer - void
    shell.label = "Hollow/precast-shell shared pier cap envelope"
    shell.color = Color(0.66, 0.66, 0.64)
    return shell


def _foundation_part(variant: str, actual_length_m: float | None = None) -> Part:
    concrete = Color(0.70, 0.70, 0.68)
    if variant == "interface-only":
        return _part(
            (2_500.0, 2_500.0, 500.0),
            (0.0, 0.0, -250.0),
            "Common pier-to-foundation interface; foundation depth intentionally not modelled",
            concrete,
        )
    item = foundation_type(variant)
    if bool(item["project_length_required"]) and actual_length_m is None:
        depth_m = float(item["interface_depth_m"])
        depth_note = "actual pile/shaft length required and intentionally not modelled"
    else:
        depth_m = actual_length_m or float(item["interface_depth_m"])
        depth_note = f"project length {depth_m:g} m"
    if variant == "bored-shaft":
        diameter_mm = float(item["interface_width_m"]) * 1_000.0
        depth_mm = depth_m * 1_000.0
        part = Cylinder(diameter_mm / 2.0, depth_mm).locate(
            Location((0.0, 0.0, -depth_mm / 2.0))
        )
        part.label = f"Bored-shaft foundation interface ({depth_note})"
        part.color = concrete
        return part
    return _part(
        (
            float(item["interface_length_m"]) * 1_000.0,
            float(item["interface_width_m"]) * 1_000.0,
            float(item["interface_depth_m"]) * 1_000.0,
        ),
        (0, 0, -float(item["interface_depth_m"]) * 500.0),
        f"{variant} foundation interface ({depth_note})",
        concrete,
    )


def viaduct_pier(
    height_m: float = 8.0,
    foundation: str = "interface-only",
    actual_foundation_length_m: float | None = None,
    continuity_role: str = "internal",
) -> Compound:
    """Shared pier for a short semi-continuous unit.

    Foundation selection comes from a geotechnical zone. Deep-element length
    is never inferred from this CAD interface. Internal link-slab/diaphragm
    supports use one bearing line; expansion-unit boundaries keep two.
    """

    if not PIER_MIN_HEIGHT_M <= height_m <= PIER_MAX_HEIGHT_M:
        raise ValueError(f"pier height {height_m:g} m outside {PIER_MIN_HEIGHT_M:g}..{PIER_MAX_HEIGHT_M:g} m catalogue")
    if continuity_role not in {"internal", "expansion"}:
        raise ValueError("continuity role must be 'internal' or 'expansion'")
    height_mm = height_m * 1000.0
    concrete = Color(0.70, 0.70, 0.68)
    parts = [
        _foundation_part(foundation, actual_foundation_length_m),
        _part((PIER_COLUMN_X_MM, PIER_COLUMN_Y_MM, height_mm), (0, 0, height_mm / 2), "Single reinforced-concrete pier column", concrete),
        _pier_cap_shell(height_mm + PIER_CAP_HEIGHT_MM / 2),
    ]
    parts.extend(_jacking_shelf_parts(height_mm + PIER_CAP_HEIGHT_MM))
    parts.extend(
        _bearing_parts(
            height_mm + PIER_CAP_HEIGHT_MM,
            double_bearing_line=continuity_role == "expansion",
        )
    )
    return Compound(
        label=(
            f"Standard double-track viaduct pier ({height_m:g} m, {foundation}, "
            f"{continuity_role} unit support)"
        ),
        children=parts,
    )


def viaduct_abutment() -> Compound:
    """Standard paired-girder end support, wing walls, approach, and bearings."""

    concrete = Color(0.69, 0.69, 0.67)
    dark = Color(0.58, 0.58, 0.57)
    shelf_z = 2_000.0
    parts = [
        _part((5_000.0, ABUTMENT_FOUNDATION_WIDTH_MM, 1_500.0), (0, 0, -750), "Abutment foundation interface envelope", concrete),
        _part((2_000.0, ABUTMENT_WIDTH_MM, 3_500.0), (0, 0, 1_750), "Abutment bearing shelf and backwall", concrete),
        _part((5_000.0, 500.0, 2_500.0), (1_500, -ABUTMENT_WIDTH_MM / 2.0 - 250.0, 1_250), "Abutment wing wall LH", concrete),
        _part((5_000.0, 500.0, 2_500.0), (1_500, ABUTMENT_WIDTH_MM / 2.0 + 250.0, 1_250), "Abutment wing wall RH", concrete),
        _part((6_000.0, ABUTMENT_WIDTH_MM, 350.0), (4_000, 0, 175), "Reinforced approach slab", concrete),
        _part((500.0, ABUTMENT_WIDTH_MM, 180.0), (1_250, 0, shelf_z + 90), "Replaceable expansion-joint interface", dark),
    ]
    parts.extend(_bearing_parts(shelf_z, double_bearing_line=False))
    return Compound(label="Standard double-track viaduct abutment", children=parts)


def pier_bom(
    height_m: float = 8.0,
    foundation: str = "interface-only",
    continuity_role: str = "internal",
) -> tuple[CivilKitItem, ...]:
    if not PIER_MIN_HEIGHT_M <= height_m <= PIER_MAX_HEIGHT_M:
        raise ValueError("pier height outside catalogue")
    if continuity_role not in {"internal", "expansion"}:
        raise ValueError("continuity role must be 'internal' or 'expansion'")
    bearing_count = 4 if continuity_role == "internal" else 8
    bearing_lines = "one longitudinal line" if continuity_role == "internal" else "two longitudinal lines"
    return (
        CivilKitItem("CIV-PIER-P010", f"{foundation} selected foundation interface", 1, "foundation set", "site geotechnical zone, actual length/cost, and foundation test release"),
        CivilKitItem("CIV-PIER-P020", "1.5 m × 2.0 m reinforced-concrete pier column", height_m, "vertical m", "reinforcement/seismic/collision calculation"),
        CivilKitItem("CIV-PIER-P030", "7 m hollow/precast-shell shared pier cap", 1, "ea", "lifting, reinforcement, connection, and cap calculation"),
        CivilKitItem("CIV-PIER-P040", f"elastomeric/PTFE girder bearing in {bearing_lines}", bearing_count, "ea", "supplier freeze and bearing/movement schedule"),
        CivilKitItem("CIV-PIER-P045", "permanent bearing-replacement jacking shelf interface", 4, "ea", "jacking and maintenance-load calculation"),
        CivilKitItem("CIV-PIER-P050", "drainage, earthing, access, and identification kit", 1, "pier kit", "site services and inspection release"),
    )


def abutment_bom() -> tuple[CivilKitItem, ...]:
    return (
        CivilKitItem("CIV-ABT-P010", "abutment foundation interface", 1, "foundation set", "site geotechnical and foundation release"),
        CivilKitItem("CIV-ABT-P020", "bearing shelf and backwall", 1, "ea", "structural and drainage calculation"),
        CivilKitItem("CIV-ABT-P030", "reinforced-concrete wing wall", 2, "ea", "earth-pressure and retaining-wall release"),
        CivilKitItem("CIV-ABT-P040", "elastomeric/PTFE girder bearing", 4, "ea", "supplier freeze and bearing schedule"),
        CivilKitItem("CIV-ABT-P050", "replaceable expansion-joint kit", 1, "ea", "thermal movement and supplier freeze"),
        CivilKitItem("CIV-ABT-P060", "approach slab, drainage, earthing, and access kit", 1, "abutment kit", "settlement, drainage, and inspection release"),
    )


PIER_ASSEMBLY_INSTRUCTIONS = (
    "release survey, utilities, geotechnical model, pile/foundation design, and temporary works",
    "select from the soil/access foundation catalogue, record actual lengths/costs, construct and test the released foundation",
    "cast/erect the standard column and precast cap; complete reinforcement, concrete, and dimensional records",
    "install four internal-support bearings in one line, or eight at an expansion-unit boundary, and survey level, spacing, orientation, and movement axes",
    "after span erection, complete the released reinforced diaphragm or link-slab continuity connection",
    "erect the two single-track decked pi-beams only after substructure and lifting hold points close",
)

ABUTMENT_ASSEMBLY_INSTRUCTIONS = (
    "release earthworks, geotechnical, drainage, thermal movement, and foundation design",
    "construct foundation, bearing shelf, backwall, wing walls, and approach slab in the approved sequence",
    "install four scheduled bearings and the replaceable expansion-joint interface",
    "survey girder seats, backwall clearance, approach settlement datum, drainage, and inspection access",
)


__all__ = [
    "ABUTMENT_WIDTH_MM",
    "ABUTMENT_ASSEMBLY_INSTRUCTIONS",
    "CivilKitItem",
    "GIRDER_CENTRE_SPACING_MM",
    "PIER_ASSEMBLY_INSTRUCTIONS",
    "PIER_MAX_HEIGHT_M",
    "PIER_MIN_HEIGHT_M",
    "WEB_BEARING_OFFSET_MM",
    "abutment_bom",
    "pier_bom",
    "viaduct_abutment",
    "viaduct_pier",
]
