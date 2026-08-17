"""Build and render FreeCAD station/track/train review scenes.

Run with the FreeCAD GUI runtime through the companion launcher:

    mechanical-py/scripts/freecad_station_scenes.sh

The output is a compact FreeCAD document plus stable PNGs for the docs.
The scenes are planning-review envelopes, not production drawings.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


try:
    import FreeCAD as App  # type: ignore[import-not-found]
    import FreeCADGui as Gui  # type: ignore[import-not-found]
    import Part  # type: ignore[import-not-found]
    from PySide import QtCore  # type: ignore[import-not-found]
except Exception as exc:  # pragma: no cover - only exercised inside FreeCAD.
    App = None  # type: ignore[assignment]
    Gui = None  # type: ignore[assignment]
    Part = None  # type: ignore[assignment]
    QtCore = None  # type: ignore[assignment]
    _FREECAD_IMPORT_ERROR = exc
else:
    _FREECAD_IMPORT_ERROR = None

try:
    from PIL import Image, ImageChops  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - optional screenshot polish.
    Image = None  # type: ignore[assignment]
    ImageChops = None  # type: ignore[assignment]


M = 1000.0

COLOURS: dict[str, tuple[float, float, float]] = {
    "ground": (0.77, 0.75, 0.68),
    "road": (0.30, 0.33, 0.36),
    "slab": (0.70, 0.72, 0.70),
    "concrete": (0.78, 0.78, 0.74),
    "dark_concrete": (0.52, 0.54, 0.53),
    "platform": (0.82, 0.78, 0.68),
    "platform_edge": (0.95, 0.76, 0.18),
    "rail": (0.08, 0.09, 0.10),
    "roof": (0.14, 0.42, 0.48),
    "roof_light": (0.47, 0.66, 0.70),
    "column": (0.52, 0.56, 0.60),
    "glass": (0.08, 0.20, 0.27),
    "train": (0.88, 0.91, 0.92),
    "train_band": (0.05, 0.45, 0.66),
    "train_dark": (0.06, 0.08, 0.10),
    "pv": (0.09, 0.15, 0.21),
    "access": (0.72, 0.81, 0.84),
    "core": (0.84, 0.86, 0.86),
    "stairs": (0.62, 0.66, 0.68),
}


@dataclass(frozen=True)
class Box:
    label: str
    center: tuple[float, float, float]
    size: tuple[float, float, float]
    colour: str
    transparency: int = 0


@dataclass(frozen=True)
class Capture:
    group_label: str
    output: str
    width: int = 2200
    height: int = 1250


AT_GRADE_STATION_LABEL = "At-grade ground-level side-platform station"
ELEVATED_STATION_LABEL = "Elevated side-platform station"
INTERCHANGE_STATION_LABEL = "Elevated interchange station"


CAPTURES: tuple[Capture, ...] = (
    Capture(AT_GRADE_STATION_LABEL, "freecad-at-grade-station-track-train.png"),
    Capture(ELEVATED_STATION_LABEL, "freecad-elevated-station-track-train.png"),
    Capture(INTERCHANGE_STATION_LABEL, "freecad-elevated-interchange-track-train.png", 2200, 1450),
)


def _require_freecad_gui() -> None:
    if App is None or Gui is None or Part is None or QtCore is None:
        raise SystemExit(
            "FreeCAD GUI modules are not importable. Run this with the FreeCAD GUI "
            "or mechanical-py/scripts/freecad_station_scenes.sh.\n"
            f"Import error was: {_FREECAD_IMPORT_ERROR!r}"
        )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _catalog_root() -> Path:
    return Path(__file__).resolve().parents[2] / "catalog" / "freecad"


def _screenshots_root() -> Path:
    return _repo_root() / "docs" / "screenshots" / "stations"


def _safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", value.strip())
    cleaned = cleaned.strip("_") or "Object"
    if cleaned[0].isdigit():
        cleaned = f"OSR_{cleaned}"
    return cleaned[:80]


def _group(doc, label: str):
    obj = doc.addObject("App::DocumentObjectGroup", _safe_name(label))
    obj.Label = label
    return obj


def _add_box(doc, group, box: Box):
    x, y, z = box.center
    lx, ly, lz = box.size
    shape = Part.makeBox(
        lx * M,
        ly * M,
        lz * M,
        App.Vector((x - lx / 2.0) * M, (y - ly / 2.0) * M, (z - lz / 2.0) * M),
    )
    obj = doc.addObject("Part::Feature", _safe_name(box.label))
    obj.Label = box.label
    obj.Shape = shape
    view = getattr(obj, "ViewObject", None)
    if view is not None:
        view.ShapeColor = COLOURS[box.colour]
        view.DisplayMode = "Flat Lines"
        if box.transparency:
            view.Transparency = box.transparency
    group.addObject(obj)
    return obj


def _add_boxes(doc, group, boxes: list[Box]) -> None:
    for box in boxes:
        _add_box(doc, group, box)


def _ground(doc, group, width: float, depth: float) -> None:
    _add_box(doc, group, Box("urban ground plane", (0, 0, -0.08), (width, depth, 0.16), "ground"))


def _double_track(doc, group, *, length: float, z: float, y_offset: float = 0.0, slab_width: float = 6.2) -> None:
    _add_box(doc, group, Box("double-track ballastless slab", (0, y_offset, z + 0.14), (length, slab_width, 0.28), "slab"))
    for track_center in (-1.75, 1.75):
        for rail_offset in (-0.72, 0.72):
            y = y_offset + track_center + rail_offset
            _add_box(doc, group, Box("continuous running rail", (0, y, z + 0.42), (length, 0.08, 0.14), "rail"))
            _add_box(doc, group, Box("direct-fixation rail plinth", (0, y, z + 0.27), (length, 0.36, 0.20), "dark_concrete"))
    for y in (y_offset - slab_width / 2.0 + 0.18, y_offset + slab_width / 2.0 - 0.18):
        _add_box(doc, group, Box("edge drainage and cable trough", (0, y, z + 0.42), (length, 0.25, 0.20), "dark_concrete"))


def _elevated_track(doc, group, *, length: float, z: float) -> None:
    for x in (-28, -14, 0, 14, 28):
        _add_box(doc, group, Box("standard shared single-column pier", (x, 0, z / 2.0), (1.5, 2.0, z), "concrete"))
        _add_box(doc, group, Box("hollow/precast-shell pier-cap envelope", (x, 0, z), (2.5, 11.0, 1.0), "concrete"))
    for y in (-2.65, 2.65):
        _add_box(doc, group, Box("single-track U-trough envelope", (0, y, z + 0.93), (length, 4.90, 1.85), "concrete"))
        _add_box(doc, group, Box("thin elevated alignment layer", (0, y, z + 0.29), (length, 4.10, 0.04), "slab"))
        for rail_offset in (-0.72, 0.72):
            _add_box(doc, group, Box("elevated running rail", (0, y + rail_offset, z + 0.51), (length, 0.08, 0.14), "rail"))


def _platform_pair(
    doc,
    group,
    *,
    length: float,
    z: float,
    y_centers: tuple[float, float],
    width: float = 3.2,
    height: float = 1.0,
) -> None:
    for y in y_centers:
        _add_box(doc, group, Box("side platform slab", (0, y, z + height / 2.0), (length, width, height), "platform"))
        edge_y = y - (1 if y > 0 else -1) * width / 2.0
        _add_box(doc, group, Box("tactile platform edge strip", (0, edge_y, z + height + 0.04), (length, 0.12, 0.08), "platform_edge"))


def _canopies(doc, group, *, length: float, z: float, y_centers: tuple[float, ...], width: float = 3.4) -> None:
    for y in y_centers:
        for x in (-20, -13, -6, 1, 8, 15, 22):
            if abs(x) > length / 2.0 - 2.0:
                continue
            _add_box(doc, group, Box("galvanised canopy column", (x, y - width / 2.0 + 0.45, z + 1.15), (0.18, 0.18, 2.30), "column"))
            _add_box(doc, group, Box("galvanised canopy column", (x, y + width / 2.0 - 0.45, z + 1.15), (0.18, 0.18, 2.30), "column"))
        _add_box(doc, group, Box("prefab solar canopy roof", (0, y, z + 2.42), (length + 2.0, width + 0.5, 0.20), "roof"))
        _add_box(doc, group, Box("roof PV strip", (0, y, z + 2.58), (length - 4.0, width - 0.6, 0.06), "pv"))


def _access_bridge(doc, group, *, x: float, span_y: float, z: float, width_x: float = 4.2) -> None:
    _add_box(doc, group, Box("covered pedestrian overbridge deck", (x, 0, z), (width_x, span_y, 0.42), "access", 15))
    _add_box(doc, group, Box("overbridge roof", (x, 0, z + 1.10), (width_x + 0.4, span_y + 0.4, 0.16), "roof_light"))
    _add_box(doc, group, Box("north lift and stair core", (x, -span_y / 2.0 - 0.85, z - 1.7), (3.2, 1.8, 3.4), "core", 8))
    _add_box(doc, group, Box("south lift and stair core", (x, span_y / 2.0 + 0.85, z - 1.7), (3.2, 1.8, 3.4), "core", 8))
    for y in (-span_y / 2.0 + 3.0, span_y / 2.0 - 3.0):
        _add_box(doc, group, Box("prefab stair flight", (x, y, z - 1.45), (width_x, 2.3, 0.25), "stairs"))


def _train_x(doc, group, *, x_center: float, y_center: float, bottom_z: float, cars: int = 3) -> None:
    car_len = 17.0
    gap = 0.12
    width = 2.85
    height = 3.25
    total = cars * car_len + (cars - 1) * gap
    start = x_center - total / 2.0 + car_len / 2.0
    for index in range(cars):
        cx = start + index * (car_len + gap)
        prefix = f"driverless car {index + 1}"
        _add_box(doc, group, Box(f"{prefix} body", (cx, y_center, bottom_z + height / 2.0), (car_len, width, height), "train"))
        _add_box(doc, group, Box(f"{prefix} continuous window band left", (cx, y_center - width / 2.0 - 0.03, bottom_z + 2.0), (car_len - 1.1, 0.08, 0.66), "glass", 35))
        _add_box(doc, group, Box(f"{prefix} continuous window band right", (cx, y_center + width / 2.0 + 0.03, bottom_z + 2.0), (car_len - 1.1, 0.08, 0.66), "glass", 35))
        _add_box(doc, group, Box(f"{prefix} blue side livery", (cx, y_center - width / 2.0 - 0.05, bottom_z + 1.10), (car_len - 1.0, 0.09, 0.18), "train_band"))
        _add_box(doc, group, Box(f"{prefix} roof equipment and PV strip", (cx, y_center, bottom_z + 3.38), (car_len - 1.6, width - 0.45, 0.10), "pv"))
        for door_x in (cx - 5.0, cx, cx + 5.0):
            _add_box(doc, group, Box(f"{prefix} wide passenger door", (door_x, y_center - width / 2.0 - 0.06, bottom_z + 1.18), (1.15, 0.09, 1.75), "roof_light"))
        for bogie_x in (cx - 5.2, cx + 5.2):
            _add_box(doc, group, Box(f"{prefix} bogie", (bogie_x, y_center, bottom_z - 0.18), (2.4, width - 0.35, 0.42), "train_dark"))
    _add_box(doc, group, Box("flat A-end sensor face, no driver cab", (x_center - total / 2.0 - 0.09, y_center, bottom_z + 1.65), (0.18, width, 2.35), "train_dark"))
    _add_box(doc, group, Box("flat B-end sensor face, no driver cab", (x_center + total / 2.0 + 0.09, y_center, bottom_z + 1.65), (0.18, width, 2.35), "train_dark"))


def _train_y(doc, group, *, x_center: float, y_center: float, bottom_z: float, cars: int = 3) -> None:
    car_len = 17.0
    gap = 0.12
    width = 2.85
    height = 3.25
    total = cars * car_len + (cars - 1) * gap
    start = y_center - total / 2.0 + car_len / 2.0
    for index in range(cars):
        cy = start + index * (car_len + gap)
        prefix = f"upper-level driverless car {index + 1}"
        _add_box(doc, group, Box(f"{prefix} body", (x_center, cy, bottom_z + height / 2.0), (width, car_len, height), "train"))
        _add_box(doc, group, Box(f"{prefix} continuous window band left", (x_center - width / 2.0 - 0.03, cy, bottom_z + 2.0), (0.08, car_len - 1.1, 0.66), "glass", 35))
        _add_box(doc, group, Box(f"{prefix} continuous window band right", (x_center + width / 2.0 + 0.03, cy, bottom_z + 2.0), (0.08, car_len - 1.1, 0.66), "glass", 35))
        _add_box(doc, group, Box(f"{prefix} roof equipment and PV strip", (x_center, cy, bottom_z + 3.38), (width - 0.45, car_len - 1.6, 0.10), "pv"))
        for bogie_y in (cy - 5.2, cy + 5.2):
            _add_box(doc, group, Box(f"{prefix} bogie", (x_center, bogie_y, bottom_z - 0.18), (width - 0.35, 2.4, 0.42), "train_dark"))
    _add_box(doc, group, Box("upper train flat A-end sensor face", (x_center, y_center - total / 2.0 - 0.09, bottom_z + 1.65), (width, 0.18, 2.35), "train_dark"))
    _add_box(doc, group, Box("upper train flat B-end sensor face", (x_center, y_center + total / 2.0 + 0.09, bottom_z + 1.65), (width, 0.18, 2.35), "train_dark"))


def _build_at_grade_scene(doc):
    group = _group(doc, AT_GRADE_STATION_LABEL)
    _ground(doc, group, 86, 38)
    _add_boxes(
        doc,
        group,
        [
            Box("parallel urban road north", (0, -12.0, 0.01), (86, 5.2, 0.03), "road"),
            Box("parallel urban road south", (0, 12.0, 0.01), (86, 5.2, 0.03), "road"),
        ],
    )
    # Rail datum is below the pedestrian-grade platform slab; the station
    # keeps level boarding without a raised access structure.
    _double_track(doc, group, length=72, z=-0.84)
    _platform_pair(doc, group, length=58, z=0.0, y_centers=(-5.0, 5.0), height=0.16)
    _canopies(doc, group, length=50, z=0.16, y_centers=(-5.0, 5.0))
    _add_box(doc, group, Box("north ground-level fare gate plinth", (-19.0, -5.0, 0.20), (6.0, 0.75, 0.24), "access", 10))
    _add_box(doc, group, Box("south ground-level fare gate plinth", (-19.0, 5.0, 0.20), (6.0, 0.75, 0.24), "access", 10))
    _add_box(doc, group, Box("west pedestrian forecourt paving", (-23.5, 0.0, 0.03), (8.0, 22.0, 0.06), "ground"))
    _add_box(doc, group, Box("services cabinet under canopy", (-22.0, 8.2, 0.75), (2.2, 1.2, 1.5), "core", 8))
    _train_x(doc, group, x_center=7.0, y_center=-1.75, bottom_z=0.01)
    return group


def _build_elevated_scene(doc):
    group = _group(doc, ELEVATED_STATION_LABEL)
    _ground(doc, group, 86, 38)
    _add_box(doc, group, Box("road under viaduct", (0, 0, 0.01), (86, 9.0, 0.03), "road"))
    _elevated_track(doc, group, length=72, z=7.4)
    _platform_pair(doc, group, length=56, z=7.85, y_centers=(-6.7, 6.7), width=3.0, height=0.9)
    _canopies(doc, group, length=48, z=8.75, y_centers=(-6.7, 6.7), width=3.2)
    _access_bridge(doc, group, x=-11.0, span_y=26.0, z=12.35)
    for y in (-14.2, 14.2):
        _add_box(doc, group, Box("street-to-platform lift and stair core", (-11.0, y, 5.90), (3.4, 2.2, 11.8), "core", 8))
    _train_x(doc, group, x_center=8.0, y_center=-2.65, bottom_z=8.50)
    return group


def _build_interchange_scene(doc):
    group = _group(doc, INTERCHANGE_STATION_LABEL)
    _ground(doc, group, 86, 86)
    _add_box(doc, group, Box("east-west arterial road", (0, 0, 0.01), (86, 8.5, 0.03), "road"))
    _add_box(doc, group, Box("north-south arterial road", (0, 0, 0.02), (8.5, 86, 0.04), "road"))
    _elevated_track(doc, group, length=74, z=7.6)
    _platform_pair(doc, group, length=50, z=8.05, y_centers=(-6.7, 6.7), width=2.9, height=0.9)
    _canopies(doc, group, length=43, z=8.95, y_centers=(-6.7, 6.7), width=3.0)
    _train_x(doc, group, x_center=-8.0, y_center=-2.65, bottom_z=8.70)

    for y in (-30, -15, 0, 15, 30):
        _add_box(doc, group, Box("upper-line shared tall pier", (0, y, 7.80), (1.5, 2.0, 15.6), "concrete"))
    for x in (-2.65, 2.65):
        _add_box(doc, group, Box("upper-level single-track U-trough envelope", (x, 0, 16.33), (4.90, 74, 1.85), "concrete"))
        _add_box(doc, group, Box("upper-level thin alignment layer", (x, 0, 15.69), (4.10, 74, 0.04), "slab"))
        for rail_offset in (-0.72, 0.72):
            _add_box(doc, group, Box("upper-level running rail", (x + rail_offset, 0, 15.91), (0.08, 72, 0.14), "rail"))
    for x in (-6.7, 6.7):
        _add_box(doc, group, Box("upper side platform slab", (x, 0, 16.95), (3.0, 52, 0.9), "platform"))
        edge_x = x - (1 if x > 0 else -1) * 1.5
        _add_box(doc, group, Box("upper tactile platform edge strip", (edge_x, 0, 17.44), (0.12, 52, 0.08), "platform_edge"))
        _add_box(doc, group, Box("upper platform canopy roof", (x, 0, 20.30), (3.2, 44, 0.20), "roof"))
        _add_box(doc, group, Box("upper platform PV strip", (x, 0, 20.46), (2.4, 39, 0.06), "pv"))
    _train_y(doc, group, x_center=2.65, y_center=9.0, bottom_z=16.10)

    _add_box(doc, group, Box("shared transfer concourse", (0, 0, 12.50), (11.0, 11.0, 0.70), "access", 12))
    _add_box(doc, group, Box("central lift/stair transfer core", (0, 0, 6.20), (5.2, 5.2, 12.4), "core", 8))
    _add_box(doc, group, Box("upper transfer hall", (0, 0, 18.35), (6.7, 6.7, 11.4), "core", 38))
    return group


def _walk(node):
    yield node
    for child in getattr(node, "OutList", []) or []:
        yield from _walk(child)


def _has_shape(obj) -> bool:
    shape = getattr(obj, "Shape", None)
    if shape is None:
        return False
    try:
        return not shape.isNull()
    except Exception:
        return False


def _hide_all(doc) -> None:
    for obj in doc.Objects:
        view = getattr(obj, "ViewObject", None)
        if view is not None and hasattr(view, "Visibility"):
            view.Visibility = False


def _show_group(doc, group_label: str) -> None:
    _hide_all(doc)
    for obj in doc.Objects:
        if getattr(obj, "Label", "") == group_label or getattr(obj, "Name", "") == group_label:
            for child in _walk(obj):
                view = getattr(child, "ViewObject", None)
                if view is not None and hasattr(view, "Visibility") and _has_shape(child):
                    view.Visibility = True
            return
    raise ValueError(f"group not found: {group_label}")


def _capture(doc, *, out_dir: Path, capture: Capture) -> None:
    print(f"capturing {capture.output}", flush=True)
    Gui.setActiveDocument(doc.Name)
    gdoc = Gui.getDocument(doc.Name)
    view = gdoc.activeView()
    _show_group(doc, capture.group_label)
    view.viewAxonometric()
    Gui.updateGui()
    view.fitAll()
    Gui.updateGui()
    view.fitAll()
    Gui.updateGui()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / capture.output
    view.saveImage(str(out_path), capture.width, capture.height, "White")
    _autocrop_png(out_path)
    print(f"wrote {out_path} ({out_path.stat().st_size // 1024} KB)", flush=True)


def _autocrop_png(path: Path, pad_px: int = 32) -> None:
    if Image is None or ImageChops is None:
        return
    img = Image.open(path).convert("RGB")
    background = Image.new("RGB", img.size, img.getpixel((0, 0)))
    bbox = ImageChops.difference(img, background).getbbox()
    if bbox is None:
        return
    left, top, right, bottom = bbox
    left = max(0, left - pad_px)
    top = max(0, top - pad_px)
    right = min(img.width, right + pad_px)
    bottom = min(img.height, bottom + pad_px)
    img.crop((left, top, right, bottom)).save(path)


def build_and_capture(*, freecad_out: Path, png_out_dir: Path) -> None:
    _require_freecad_gui()
    doc = App.newDocument("OSR_station_track_train_scenes")
    doc.Label = "OSR station, ballastless track, and driverless train scenes"
    _build_at_grade_scene(doc)
    _build_elevated_scene(doc)
    _build_interchange_scene(doc)
    notes = doc.addObject("App::DocumentObjectGroup", "SourceNotes")
    notes.Label = "Generated planning-review scenes; Python source remains design authority"
    doc.recompute()

    freecad_out.parent.mkdir(parents=True, exist_ok=True)
    if freecad_out.exists():
        freecad_out.unlink()
    doc.saveAs(str(freecad_out))
    print(f"wrote {freecad_out}", flush=True)

    for capture in CAPTURES:
        _capture(doc, out_dir=png_out_dir, capture=capture)
    App.closeDocument(doc.Name)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build and render FreeCAD station scene review artifacts.")
    parser.add_argument("--freecad-out", type=Path, default=_catalog_root() / "station-scenes.FCStd")
    parser.add_argument("--png-out-dir", type=Path, default=_screenshots_root())
    return parser.parse_args(argv)


def _normalise_freecad_argv(argv: list[str]) -> list[str]:
    args = list(argv)
    if args and Path(args[0]).name == "freecad_station_scenes.py":
        args = args[1:]
    if args and args[0] == "--pass":
        args = args[1:]
    return args


def main(argv: list[str] | None = None) -> None:
    args = parse_args(_normalise_freecad_argv(argv or []))
    build_and_capture(freecad_out=args.freecad_out, png_out_dir=args.png_out_dir)
    QtCore.QCoreApplication.quit()


def _running_as_freecad_script() -> bool:
    return bool(sys.argv[1:2]) and Path(sys.argv[1]).name == "freecad_station_scenes.py"


if __name__ == "__main__" or _running_as_freecad_script():
    main(sys.argv[1:])
