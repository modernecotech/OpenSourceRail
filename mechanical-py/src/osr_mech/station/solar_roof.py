"""Solar roof panel — the per-bay canopy surface + integrated PV.

The canopy roof is a single sandwich panel per bay:

- Top layer: flexible CIGS or lightweight mono-crystalline silicon
  solar modules, adhesive-bonded to a standing-seam steel sheet.
  Nominal: 200 W/m², 15 kg/m² including frame + junction box.
- Core: 40 mm polyurethane-foam insulation (kills radiant heat load
  through the canopy onto the platform).
- Bottom layer: 0.7 mm galvanised steel tray, white-coated on the
  underside to maximise reflected daylight onto the platform.

Total panel thickness: 55 mm. Total mass: ~20 kg/m² including PV.

A bay roof is one panel 6000 mm × 4200 mm (bay length × platform
depth + eave), giving ~25 m² of PV surface at ~5 kWp per bay.
Panels are factory-bonded, shipped flat on edge (2 per lorry in a
dedicated rack), and bolted to the rafter through pre-drilled flanges
— no on-site sealing, no on-site wiring into the panel.

Panels come pre-terminated with MC4 connectors on a wiring loom; each
bay plugs to its neighbour so a finished canopy is a single DC string
per side.
"""

from __future__ import annotations

from build123d import (
    Align,
    BuildPart,
    BuildSketch,
    Color,
    Part,
    Rectangle,
    extrude,
)

PANEL_THICKNESS_MM = 55.0
PV_WATT_PER_M2 = 200.0
PANEL_MASS_KG_PER_M2 = 20.0
# Eave overhang beyond the platform edge — drains water onto the
# track shoulder, keeps rain off waiting passengers.
EAVE_OVERHANG_MM = 700.0


def solar_roof_panel(
    length_mm: float = 6000.0,
    depth_mm: float = 3500.0,
) -> Part:
    """One bay of solar-roof panel.

    Parameters
    ----------
    length_mm:
        Along-track extent of the panel (matches bay spacing).
    depth_mm:
        Across-track extent (platform depth; the panel adds the
        EAVE_OVERHANG_MM forward of that at render time).
    """

    total_depth = depth_mm + EAVE_OVERHANG_MM

    with BuildPart() as panel:
        with BuildSketch():
            Rectangle(length_mm, total_depth, align=(Align.MIN, Align.CENTER))
        extrude(amount=PANEL_THICKNESS_MM)

    p = panel.part
    p.color = Color(0.15, 0.2, 0.35)
    p.label = "Solar roof panel"
    return p


def panel_kwp(length_mm: float, depth_mm: float) -> float:
    """Peak PV output in kWp for a panel of the given size.

    Accounts for a 15 % packing loss for MC4 junction boxes,
    ventilation gaps, and edge framing — real PV area is ~85 % of
    the deck area.
    """
    area_m2 = (length_mm / 1000.0) * (depth_mm / 1000.0)
    return area_m2 * PV_WATT_PER_M2 / 1000.0 * 0.85


__all__ = [
    "EAVE_OVERHANG_MM",
    "PANEL_MASS_KG_PER_M2",
    "PANEL_THICKNESS_MM",
    "PV_WATT_PER_M2",
    "panel_kwp",
    "solar_roof_panel",
]
