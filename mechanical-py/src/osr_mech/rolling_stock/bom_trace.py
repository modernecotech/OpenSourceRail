"""Trace the commercial light-metro BOM into the engineering product tree.

The procurement BOM is intentionally cost-oriented: one line can fund several
fabricated parts, and one bought-in engineering kit can consolidate several
commercial lines.  This module is the controlled many-to-many bridge between
the ``B/G/T/E/A`` cost lines and the ``LM3-*`` engineering identifiers used by
definitions, assembly nodes, and shop travelers.
"""

from __future__ import annotations


PROCUREMENT_BOM_ENGINEERING_IDS: dict[str, tuple[str, ...]] = {
    # Body, exterior, and interior.
    "B1": ("LM3-BDY-P010", "LM3-BDY-P020", "LM3-BDY-P060", "LM3-BDY-P070", "LM3-BDY-P080", "LM3-BDY-P090"),
    "B2": ("LM3-BDY-P030", "LM3-BDY-P040", "LM3-BDY-P050", "LM3-BDY-P100", "LM3-BDY-P110", "LM3-ART-P010"),
    "B3": ("LM3-BDY-SA110", "LM3-BDY-SA120"),
    "B4": ("LM3-BDY-SA110", "LM3-BDY-SA120", "LM3-BOG-SA610", "LM3-BOG-SA620"),
    "B5": ("LM3-SHELL-A200",),
    "B6": ("LM3-SHELL-A200", "LM3-BDY-P130", "LM3-EXT-P080"),
    "B7": ("LM3-SHELL-A200", "LM3-BDY-P130", "LM3-BDY-P140", "LM3-EXT-P090", "LM3-ROOF-SA410", "LM3-INT-P040"),
    "B8": ("LM3-CWL-SA710", "LM3-CWL-P010", "LM3-CWL-P011", "LM3-CWL-P012", "LM3-CWL-P013", "LM3-CWL-P014", "LM3-CWL-P015", "LM3-CWL-P016"),
    "B9": ("LM3-ART-P020",),
    "B10": ("LM3-EXT-P020",),
    "B11": ("LM3-EXT-P010",),
    "B12": ("LM3-BDY-P060", "LM3-EXT-P060"),
    "B13": ("LM3-EXT-P060",),
    "B14": ("LM3-EXT-P060",),
    "B15": ("LM3-EXT-P060",),
    "B16": ("LM3-EXT-P060",),
    "B17": ("LM3-END-SA700", "LM3-END-P050"),
    "B18": ("LM3-EXT-P060",),
    "B19": ("LM3-EXT-P060",),
    "B20": ("LM3-SHELL-A200",),
    "B21": ("LM3-INT-P020", "LM3-INT-P030", "LM3-INT-P040", "LM3-INT-P050"),
    "B22": ("LM3-END-P010", "LM3-END-P040"),
    "B23": ("LM3-END-P010",),
    "B24": ("LM3-ART-P030",),
    "B25": ("LM3-EXT-P010", "LM3-BDY-P100"),
    "B26": ("LM3-BDY-SA110", "LM3-BDY-P120", "LM3-END-SA700"),
    "B27": ("LM3-EXT-P030",),
    "B28": ("LM3-SHELL-A200",),
    "B29": ("LM3-ART-P010",),
    # Bogies.
    "G1": ("LM3-BOG-P010",),
    "G2": ("LM3-BOG-P020",),
    "G3": ("LM3-BOG-P040", "LM3-BOG-P041"),
    "G4": ("LM3-BOG-P040", "LM3-BOG-P041"),
    "G5": ("LM3-BOG-P040", "LM3-BOG-P041"),
    "G6": ("LM3-BOG-P040", "LM3-BOG-P041"),
    "G7": ("LM3-BOG-P040", "LM3-BOG-P041"),
    "G8": ("LM3-BOG-P040", "LM3-BOG-P041"),
    "G9": ("LM3-BOG-P040", "LM3-BOG-P041"),
    "G10": ("LM3-BOG-P040", "LM3-BOG-P041"),
    "G11": ("LM3-BOG-P040", "LM3-BOG-P041"),
    "G12": ("LM3-BOG-P040", "LM3-BOG-P041"),
    "G13": ("LM3-BOG-P030", "LM3-BOG-P031"),
    "G14": ("LM3-BOG-P040", "LM3-BOG-P041", "LM3-BOG-P060", "LM3-BOG-P061"),
    "G15": ("LM3-BOG-P040", "LM3-BOG-P041", "LM3-BOG-P060", "LM3-BOG-P061"),
    "G16": ("LM3-BOG-P040", "LM3-BOG-P041"),
    "G17": ("LM3-BOG-P060", "LM3-BOG-P061"),
    "G18": ("LM3-BOG-P010", "LM3-BOG-P050"),
    "G19": ("LM3-TRC-P020",),
    "G20": ("LM3-BOG-P030", "LM3-BOG-P031"),
    "G21": ("LM3-BOG-SA610", "LM3-BOG-SA620", "LM3-AUX-P010"),
    # Traction, battery, auxiliary power, charging, and roof PV.
    "T1": ("LM3-TRC-P010",),
    "T2": ("LM3-TRC-P020",),
    "T3": ("LM3-TRC-P030",),
    "T4": ("LM3-TRC-P030", "LM3-HV-P030"),
    "T5": ("LM3-TRC-P040",),
    "T6": ("LM3-TRC-P040",),
    "T7": ("LM3-TRC-P030", "LM3-HV-P030"),
    "T8": ("LM3-HV-P010",),
    "T9": ("LM3-SAF-P010",),
    "T10": ("LM3-SAF-P010",),
    "T11": ("LM3-TRC-P070",),
    "T12": ("LM3-TRC-P060",),
    "T13": ("LM3-TRC-P030",),
    "T14": ("LM3-EXT-P040", "LM3-ROOF-P010", "LM3-INT-P010"),
    "T15": ("LM3-TRC-P050",),
    "T16": ("LM3-TRC-P070",),
    "T17": ("LM3-BDY-P050", "LM3-HV-P030"),
    "T18": ("LM3-HV-P020",),
    "T19": ("LM3-TRC-P060",),
    "T20": ("LM3-TRC-P030", "LM3-HV-P030"),
    "T21": ("LM3-EXT-P050",),
    "T22": ("LM3-ROOF-P020",),
    "T23": ("LM3-TRC-P030",),
    # Electronics and safety control.
    "E1": ("LM3-CTRL-P010",),
    "E2": ("LM3-CTRL-P010",),
    "E3": ("LM3-CTRL-P020",),
    "E4": ("LM3-CTRL-P020",),
    "E5": ("LM3-CTRL-P020",),
    "E6": ("LM3-CTRL-P010", "LM3-CTRL-P020"),
    "E7": ("LM3-CTRL-P020",),
    "E8": ("LM3-CTRL-P020",),
    "E9": ("LM3-CTRL-P050",),
    "E10": ("LM3-CTRL-P030",),
    "E11": ("LM3-CTRL-P030",),
    "E12": ("LM3-CTRL-P030",),
    "E13": ("LM3-CTRL-P030",),
    "E14": ("LM3-CTRL-P010", "LM3-EXT-P060"),
    "E15": ("LM3-CTRL-P010", "LM3-EXT-P060", "LM3-END-P020"),
    "E16": ("LM3-CTRL-P030",),
    "E17": ("LM3-CTRL-P040", "LM3-END-P040"),
    "E18": ("LM3-END-P020",),
    "E19": ("LM3-END-P020", "LM3-END-P030"),
    "E20": ("LM3-CTRL-P040", "LM3-EXT-P010"),
    "E21": ("LM3-CTRL-P020", "LM3-EXT-P070"),
    "E22": ("LM3-CTRL-P040",),
    "E23": ("LM3-CTRL-P050",),
    # Accessibility and emergency fit-out.
    "A1": ("LM3-EXT-P060",),
    "A2": ("LM3-EXT-P060",),
    "A3": ("LM3-EXT-P060",),
    "A4": ("LM3-EXT-P060",),
}


MATERIAL_BOM_LINES = frozenset({"B1", "B2", "B4", "B6", "B7", "B20", "B21", "B28"})
PROCESS_BOM_LINES = frozenset({"B3", "B5"})


def bom_scope(line_id: str) -> str:
    """Classify a commercial row for EBOM/MBOM roll-up."""

    if line_id in MATERIAL_BOM_LINES:
        return "material-or-consumable"
    if line_id in PROCESS_BOM_LINES:
        return "manufacturing-process"
    return "component-or-kit"


def engineering_ids_for_bom_line(line_id: str) -> tuple[str, ...]:
    return PROCUREMENT_BOM_ENGINEERING_IDS[line_id]


def bom_line_ids_for_engineering_id(engineering_id: str) -> tuple[str, ...]:
    return tuple(
        line_id
        for line_id, engineering_ids in PROCUREMENT_BOM_ENGINEERING_IDS.items()
        if engineering_id in engineering_ids
    )


__all__ = [
    "MATERIAL_BOM_LINES",
    "PROCESS_BOM_LINES",
    "PROCUREMENT_BOM_ENGINEERING_IDS",
    "bom_line_ids_for_engineering_id",
    "bom_scope",
    "engineering_ids_for_bom_line",
]
