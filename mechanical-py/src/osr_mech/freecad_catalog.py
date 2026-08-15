"""Generate native FreeCAD replacements for the complete OSR CAD catalogue."""

from __future__ import annotations

import sys
from pathlib import Path

import FreeCAD as App  # type: ignore[import-not-found]

from osr_mech.freecad_sources import source_shape


CATALOGUE = {
    "Civil infrastructure": [
        ("civil-at-grade-slab-panel", "At-grade ballastless slab panel"),
        ("civil-elevated-deck-slab-panel", "Elevated deck slab panel"),
        ("civil-u-girder-25m", "Precast U-girder, 25 m"),
        ("civil-viaduct-pier-8m", "Shared double-track viaduct pier, 8 m"),
        ("civil-viaduct-abutment", "Shared double-track viaduct abutment"),
        ("platform-l-unit", "Precast platform L-unit"),
    ],
    "Track and permanent way": [
        ("track-panel-standard-urban", "Standard urban track panel"),
        ("track-rail-60e1-6m", "UIC 60E1 rail bar, 6 m"),
        ("track-mono-block-sleeper", "Monoblock sleeper"),
        ("track-fastener-assembly", "Direct-fixation fastener assembly"),
        ("track-turnout-1-9", "1:9 turnout"),
    ],
    "Stations and facilities": [
        ("station-portal-frame", "Station canopy portal frame"),
        ("station-solar-roof-panel", "Station solar roof panel"),
        ("station-canopy-standard", "Standard station canopy assembly"),
        ("station-auxiliary-canopy-standard", "Standard station auxiliary solar canopy, 7 bays"),
        ("station-guideway-channel-edge", "At-grade station guideway-channel edge module"),
        ("station-fare-lane-plinth", "Fare lane / validator rolled-steel plinth"),
        ("station-tvm-plinth", "Ticket-vending-machine rolled-steel plinth"),
        ("depot-main-heavy", "Main-heavy depot layout"),
    ],
    "Rolling-stock fabrication templates": [
        ("template-main-frame", "Rolling-stock main frame"),
        ("template-sandwich-panel", "Side sandwich panel"),
        ("template-door-leaf", "COTS-style door leaf"),
        ("template-body-sheet-metal-kit", "Body sheet-metal kit"),
        ("template-bogie-adapter", "Bogie adapter"),
        ("template-bolster", "Bogie bolster"),
        ("template-motor-cradle", "Motor cradle"),
        ("template-chassis-interface-assembly", "Chassis interface assembly"),
    ],
}


def _feature(doc, key: str, label: str, *, group=None, placement=(0.0, 0.0, 0.0)):
    obj = doc.addObject("Part::Feature", key.replace("-", "_"))
    obj.Label = label
    shape = source_shape(key, clean=False)
    if placement != (0.0, 0.0, 0.0):
        shape = shape.copy()
        shape.translate(App.Vector(*placement))
    obj.Shape = shape
    obj.addProperty("App::PropertyString", "SourceKey", "OSR catalogue")
    obj.SourceKey = key
    obj.addProperty("App::PropertyString", "GeometryAuthority", "OSR catalogue")
    obj.GeometryAuthority = "osr_mech source geometry; native FreeCAD export"
    if group is not None:
        group.addObject(obj)
    return obj


def _catalogue(path: Path) -> None:
    doc = App.newDocument("OSRNativeCatalogue")
    root = doc.addObject("App::DocumentObjectGroup", "NativeCatalogue")
    root.Label = "OSR native FreeCAD catalogue"
    for category, entries in CATALOGUE.items():
        group = doc.addObject("App::DocumentObjectGroup", category.replace(" ", "_"))
        group.Label = category
        root.addObject(group)
        for key, label in entries:
            _feature(doc, key, label, group=group)
    doc.recompute()
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveAs(str(path))
    App.closeDocument(doc.Name)


def _assembly(path: Path, title: str, entries) -> None:
    doc = App.newDocument(title.replace(" ", "_"))
    root = doc.addObject("App::Part", "Assembly")
    root.Label = title
    notes = doc.addObject("App::FeaturePython", "AssemblyNotes")
    notes.Label = "Native FreeCAD assembly — source-keyed parts"
    notes.addProperty("App::PropertyString", "DesignStatus", "Review")
    notes.DesignStatus = "Replacement assembly generated from canonical OSR source geometry"
    root.addObject(notes)
    for key, label, placement in entries:
        _feature(doc, key, label, group=root, placement=placement)
    doc.recompute()
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveAs(str(path))
    App.closeDocument(doc.Name)


def build(output_dir: Path) -> None:
    _catalogue(output_dir / "native-catalogue-parts.FCStd")
    # At-grade platform: platform edge, slab, and a complete track panel.
    _assembly(
        output_dir / "platform-at-grade-assembly.FCStd",
        "OSR at-grade platform and track assembly",
        [
            ("civil-at-grade-slab-panel", "At-grade platform slab panel", (0, 0, 0)),
            ("platform-l-unit", "Platform edge L-unit", (0, 1500, 0)),
            ("track-panel-standard-urban", "Track panel", (0, 0, 280)),
        ],
    )
    # Elevated platform: U-girder support, topping slab, and track.
    _assembly(
        output_dir / "platform-elevated-assembly.FCStd",
        "OSR elevated platform and track assembly",
        [
            ("civil-u-girder-25m", "25 m U-girder", (0, 0, 0)),
            ("civil-elevated-deck-slab-panel", "Elevated deck slab panel", (0, 0, 1450)),
            ("track-panel-standard-urban", "Elevated track panel", (0, 0, 1900)),
        ],
    )
    # Architectural station assembly shares the same platform datum.
    _assembly(
        output_dir / "station-platform-canopy-assembly.FCStd",
        "OSR station platform and canopy assembly",
        [
            ("platform-l-unit", "Platform edge and deck", (0, 1500, 0)),
            ("track-panel-standard-urban", "Track panel", (0, 0, 280)),
            ("station-canopy-standard", "Standard canopy with portal, roof and PV", (0, 3000, 0)),
        ],
    )


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "catalog/freecad"
    build(target)
