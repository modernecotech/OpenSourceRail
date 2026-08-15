"""Generate the first standalone FreeCAD-native civil design artifact."""

from __future__ import annotations

import sys
from pathlib import Path

import FreeCAD as App  # type: ignore[import-not-found]
import Part  # type: ignore[import-not-found]

from osr_mech.freecad_sources import source_shape
from osr_mech.civil.platform_l_unit import (
    DECK_THICKNESS_MM,
    DECK_WIDTH_MM,
    UNIT_LENGTH_MM,
    WALL_HEIGHT_MM,
    WALL_THICKNESS_MM,
)


def build(output: Path) -> None:
    doc = App.newDocument("PlatformLUnit")
    obj = doc.addObject("PartDesign::Feature", "PlatformLUnit")
    obj.Label = "OSR precast platform L-unit (3000 mm)"
    obj.Shape = source_shape("platform-l-unit")
    for name, value in (
        ("UnitLength", UNIT_LENGTH_MM),
        ("WallHeight", WALL_HEIGHT_MM),
        ("WallThickness", WALL_THICKNESS_MM),
        ("DeckWidth", DECK_WIDTH_MM),
        ("DeckThickness", DECK_THICKNESS_MM),
    ):
        obj.addProperty("App::PropertyLength", name, "Design parameters")
        setattr(obj, name, value)
    obj.addProperty("App::PropertyString", "Source", "Design authority")
    obj.Source = "osr_mech.civil.platform_l_unit"
    # FreeCADCmd has no view provider in headless mode, but the same source
    # should still be usable from the GUI.
    if getattr(obj, "ViewObject", None) is not None:
        obj.ViewObject.ShapeColor = (0.80, 0.80, 0.78)
    doc.recompute()
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.saveAs(str(output))
    print(f"wrote {output}", flush=True)


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "catalog/freecad/platform-l-unit.FCStd"
    build(target)
