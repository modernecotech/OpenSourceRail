"""Repeatable forecourt/concourse solar-canopy row.

The passenger-platform canopy remains the 6 m cantilever product.  Site-area
targets that exceed it are closed with an 8.5 m by 22 m auxiliary bay derived
from the reviewed station-spanning truss envelope.  Adjacent bays share a
transverse frame, so a row of ``N`` roof modules uses ``N + 1`` frames and
``2 × (N + 1)`` column foundations.

This is controlled planning geometry and a quantified kit, not a stamped
site structure.  Wind, seismic, snow/dust, drainage, foundation, and egress
checks remain deployment release gates.
"""

from __future__ import annotations

import math

from osr_mech.cad import Box, Color, Compound, Part

from .solar_roof import PV_WATT_PER_M2, solar_roof_panel


AUX_MODULE_LENGTH_MM = 8_500.0
AUX_MODULE_WIDTH_MM = 22_000.0
AUX_CLEAR_HEIGHT_MM = 3_850.0
AUX_TRUSS_DEPTH_MM = 2_000.0
AUX_COLUMN_SIZE_MM = 200.0
AUX_CHORD_SIZE_MM = 150.0
AUX_MODULE_AREA_M2 = (AUX_MODULE_LENGTH_MM / 1000.0) * (
    AUX_MODULE_WIDTH_MM / 1000.0
)

_STEEL = Color(0.78, 0.78, 0.82)


def auxiliary_module_count(required_area_m2: float) -> int:
    """Minimum whole roof modules that meet or exceed an area requirement."""

    if required_area_m2 <= 0:
        return 0
    return int(math.ceil(required_area_m2 / AUX_MODULE_AREA_M2))


def auxiliary_installed_area_m2(module_count: int) -> float:
    return max(0, module_count) * AUX_MODULE_AREA_M2


def auxiliary_frame_count(module_count: int) -> int:
    return max(0, module_count) + 1 if module_count > 0 else 0


def auxiliary_foundation_count(module_count: int) -> int:
    return auxiliary_frame_count(module_count) * 2


def auxiliary_canopy_kwp(module_count: int) -> float:
    """PV nameplate after the same 15 percent panel packing allowance."""

    return auxiliary_installed_area_m2(module_count) * PV_WATT_PER_M2 / 1000.0 * 0.85


def _frame(x_mm: float, sequence: int) -> Compound:
    parts: list[Part] = []
    for y_mm in (-AUX_MODULE_WIDTH_MM / 2.0, AUX_MODULE_WIDTH_MM / 2.0):
        column = Box(AUX_COLUMN_SIZE_MM, AUX_COLUMN_SIZE_MM, AUX_CLEAR_HEIGHT_MM)
        column = column.translate((x_mm, y_mm, AUX_CLEAR_HEIGHT_MM / 2.0))
        column.color = _STEEL
        column.label = "Auxiliary canopy HSS 200 column"
        parts.append(column)

    for z_mm in (AUX_CLEAR_HEIGHT_MM, AUX_CLEAR_HEIGHT_MM + AUX_TRUSS_DEPTH_MM):
        chord = Box(AUX_CHORD_SIZE_MM, AUX_MODULE_WIDTH_MM, AUX_CHORD_SIZE_MM)
        chord = chord.translate((x_mm, 0.0, z_mm))
        chord.color = _STEEL
        chord.label = "Auxiliary canopy HSS 150 truss chord"
        parts.append(chord)

    # Planning-level web representation: five vertical panels preserve the
    # truss depth and frame spacing without pretending to be a released weld map.
    for panel in range(5):
        y_mm = -AUX_MODULE_WIDTH_MM / 2.0 + panel * AUX_MODULE_WIDTH_MM / 4.0
        web = Box(AUX_CHORD_SIZE_MM, AUX_CHORD_SIZE_MM, AUX_TRUSS_DEPTH_MM)
        web = web.translate((x_mm, y_mm, AUX_CLEAR_HEIGHT_MM + AUX_TRUSS_DEPTH_MM / 2.0))
        web.color = _STEEL
        web.label = "Auxiliary canopy truss web envelope"
        parts.append(web)

    return Compound(label=f"Auxiliary canopy transverse frame {sequence}", children=parts)


def auxiliary_canopy_row(module_count: int) -> Compound:
    """Build a straight row of shared frames and 8.5 m × 22 m PV roof bays."""

    if module_count < 1:
        return Compound(label="Auxiliary canopy (not installed)", children=[])

    parts: list[Part | Compound] = []
    for sequence in range(module_count + 1):
        parts.append(_frame(sequence * AUX_MODULE_LENGTH_MM, sequence + 1))
    for sequence in range(module_count):
        roof = solar_roof_panel(
            length_mm=AUX_MODULE_LENGTH_MM,
            depth_mm=AUX_MODULE_WIDTH_MM - 700.0,
        ).translate(
            (
                sequence * AUX_MODULE_LENGTH_MM,
                0.0,
                AUX_CLEAR_HEIGHT_MM + AUX_TRUSS_DEPTH_MM,
            )
        )
        roof.label = f"Auxiliary solar roof module {sequence + 1}"
        parts.append(roof)
    return Compound(
        label=f"Auxiliary solar canopy ({module_count} × 187 m2 modules)",
        children=parts,
    )


__all__ = [
    "AUX_CLEAR_HEIGHT_MM",
    "AUX_MODULE_AREA_M2",
    "AUX_MODULE_LENGTH_MM",
    "AUX_MODULE_WIDTH_MM",
    "auxiliary_canopy_kwp",
    "auxiliary_canopy_row",
    "auxiliary_foundation_count",
    "auxiliary_frame_count",
    "auxiliary_installed_area_m2",
    "auxiliary_module_count",
]
