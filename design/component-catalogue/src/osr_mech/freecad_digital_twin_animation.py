"""Render the civil/rolling-stock digital twin as deterministic PNG frames.

Run through ``design/component-catalogue/scripts/freecad_digital_twin_animation.sh`` so the
FreeCAD GUI and virtual display are configured consistently.
"""

from __future__ import annotations

import argparse
import math
import os
import sys
from pathlib import Path

try:
    import FreeCAD as App  # type: ignore[import-not-found]
    import FreeCADGui as Gui  # type: ignore[import-not-found]
    from PySide import QtCore  # type: ignore[import-not-found]
except Exception as exc:  # pragma: no cover - exercised only inside FreeCAD GUI.
    App = None  # type: ignore[assignment]
    Gui = None  # type: ignore[assignment]
    QtCore = None  # type: ignore[assignment]
    _FREECAD_IMPORT_ERROR = exc
else:
    _FREECAD_IMPORT_ERROR = None


GROUND_TRAIN_LABEL = "Ground-station complete light-metro trainset"
ELEVATED_TRAIN_LABEL = "Elevated-station complete light-metro trainset"

GROUND_VISIBLE_ZONES = {
    "01 At-grade ground station",
    "02 At-grade junction",
    "05 Rolling stock",
}
ELEVATED_VISIBLE_ZONES = {
    "03 Viaduct approaches and substructure",
    "04 Elevated station",
    "05 Rolling stock",
}


def _require_freecad_gui() -> None:
    if App is None or Gui is None or QtCore is None:
        raise SystemExit(
            "FreeCAD GUI modules are unavailable. Run this through "
            "design/component-catalogue/scripts/freecad_digital_twin_animation.sh.\n"
            f"Import error was: {_FREECAD_IMPORT_ERROR!r}"
        )


def _catalog_root() -> Path:
    return Path(__file__).resolve().parents[2] / "models" / "cad"


def _frames_root() -> Path:
    return Path(__file__).resolve().parents[2] / "catalog" / "animation-frames"


def _find_by_label(doc, label: str):
    matches = [obj for obj in doc.Objects if getattr(obj, "Label", "") == label]
    if len(matches) != 1:
        raise RuntimeError(f"expected one FreeCAD object labelled {label!r}; found {len(matches)}")
    return matches[0]


def _has_shape(obj) -> bool:
    shape = getattr(obj, "Shape", None)
    if shape is None:
        return False
    try:
        return not shape.isNull()
    except Exception:
        return False


def _set_scene_visibility(doc, *, zones: set[str], train_label: str) -> None:
    for obj in doc.Objects:
        view = getattr(obj, "ViewObject", None)
        if view is None or not hasattr(view, "Visibility"):
            continue
        if not _has_shape(obj):
            view.Visibility = True
            continue
        zone = str(getattr(obj, "IntegrationZone", ""))
        visible = zone in zones
        if zone == "05 Rolling stock":
            visible = getattr(obj, "Label", "") == train_label
        view.Visibility = visible


def _set_train_x(train, *, target_center_x_mm: float) -> None:
    shape_center_x = (train.Shape.BoundBox.XMin + train.Shape.BoundBox.XMax) / 2.0
    placement = train.Placement
    # Source geometry is already translated to its model datum inside Shape.
    # Object Placement is therefore a delta, not another absolute model X.
    # Applying the target as an absolute Placement double-translates the train
    # and was the cause of the tiny/off-camera historical GIF.
    placement.Base = App.Vector(
        target_center_x_mm - shape_center_x,
        placement.Base.y,
        placement.Base.z,
    )
    train.Placement = placement


def _capture_frame(view, *, path: Path, width: int, height: int) -> None:
    Gui.updateGui()
    view.saveImage(str(path), width, height, "White")
    if not path.exists() or path.stat().st_size < 1_000:
        raise RuntimeError(f"FreeCAD produced an empty or undersized frame: {path}")


def _visible_bounds(doc) -> tuple[float, float, float, float, float, float]:
    bounds = [
        obj.Shape.BoundBox
        for obj in doc.Objects
        if _has_shape(obj) and getattr(getattr(obj, "ViewObject", None), "Visibility", False)
    ]
    if not bounds:
        raise RuntimeError("the animation scene has no visible source geometry")
    return (
        min(box.XMin for box in bounds),
        max(box.XMax for box in bounds),
        min(box.YMin for box in bounds),
        max(box.YMax for box in bounds),
        min(box.ZMin for box in bounds),
        max(box.ZMax for box in bounds),
    )


def _set_close_camera(
    view,
    *,
    center_x_mm: float,
    center_y_mm: float,
    center_z_mm: float,
    height_mm: float,
) -> None:
    """Use a readable local engineering view instead of fitting a whole site."""
    distance = height_mm * 2.4
    camera_offset = distance / math.sqrt(3.0)
    view.setCamera(
        "#Inventor V2.1 ascii\n\n"
        "OrthographicCamera {\n"
        "  viewportMapping ADJUST_CAMERA\n"
        f"  position {center_x_mm + camera_offset:.6f} "
        f"{center_y_mm - camera_offset:.6f} {center_z_mm + camera_offset:.6f}\n"
        "  orientation 0.74290609 0.30772209 0.59447283 1.2171158\n"
        "  nearDistance 0\n"
        f"  farDistance {distance * 3.0:.6f}\n"
        "  aspectRatio 1\n"
        f"  focalDistance {distance:.6f}\n"
        f"  height {height_mm:.6f}\n"
        "}\n"
    )
    Gui.updateGui()


def _render_sequence(
    *,
    doc,
    view,
    out_dir: Path,
    start_index: int,
    frame_count: int,
    phase: str,
    zones: set[str],
    train_label: str,
    start_center_x_mm: float,
    end_center_x_mm: float,
    width: int,
    height: int,
) -> int:
    if frame_count < 2:
        raise ValueError("each animation phase requires at least two frames")
    train = _find_by_label(doc, train_label)
    _set_scene_visibility(doc, zones=zones, train_label=train_label)
    _set_train_x(train, target_center_x_mm=start_center_x_mm)
    doc.recompute()
    Gui.updateGui()
    view.viewAxonometric()
    try:
        view.setDrawStyle("Shaded")
    except Exception:
        pass

    visible = [
        obj.Label
        for obj in doc.Objects
        if _has_shape(obj) and getattr(getattr(obj, "ViewObject", None), "Visibility", False)
    ]
    print(f"{phase} scene: {len(visible)} visible source features", flush=True)
    bounds = _visible_bounds(doc)
    print(
        f"{phase} bounds: "
        f"x={bounds[0]:.1f}..{bounds[1]:.1f}, "
        f"y={bounds[2]:.1f}..{bounds[3]:.1f}, "
        f"z={bounds[4]:.1f}..{bounds[5]:.1f}",
        flush=True,
    )
    for offset in range(frame_count):
        fraction = offset / (frame_count - 1)
        # Smoothstep gives readable acceleration and braking without requiring
        # a physics engine for this design-reference visualization.
        progress = fraction * fraction * (3.0 - 2.0 * fraction)
        target_x = start_center_x_mm + (end_center_x_mm - start_center_x_mm) * progress
        _set_train_x(train, target_center_x_mm=target_x)
        # Track most, but not all, of the train motion. This keeps the consist
        # large enough to inspect while visible infrastructure still moves
        # through the frame and demonstrates genuine translation.
        camera_progress = progress * 0.78
        camera_x = start_center_x_mm + (
            end_center_x_mm - start_center_x_mm
        ) * camera_progress
        elevated = phase == "elevated"
        _set_close_camera(
            view,
            center_x_mm=camera_x,
            center_y_mm=0.0,
            center_z_mm=10_800.0 if elevated else 2_400.0,
            height_mm=62_000.0 if elevated else 50_000.0,
        )
        state = str(getattr(train, "OperationalStateJson", "{}"))
        train.OperationalStateJson = state.replace('"speed_kmh":0.0', '"speed_kmh":35.0')
        doc.recompute()
        frame_index = start_index + offset
        path = out_dir / f"frame-{frame_index:03d}-{phase}.png"
        _capture_frame(view, path=path, width=width, height=height)
        print(f"rendered {path.name} at x={target_x / 1000.0:.1f} m", flush=True)
    return start_index + frame_count


def render_animation_frames(
    *,
    model: Path,
    out_dir: Path,
    ground_frames: int,
    elevated_frames: int,
    width: int,
    height: int,
) -> int:
    _require_freecad_gui()
    if not model.exists():
        raise FileNotFoundError(f"digital-twin FreeCAD model is missing: {model}")
    out_dir.mkdir(parents=True, exist_ok=True)
    for path in out_dir.glob("frame-*.png"):
        path.unlink()

    doc = App.openDocument(str(model))
    try:
        Gui.setActiveDocument(doc.Name)
        view = Gui.getDocument(doc.Name).activeView()
        next_index = _render_sequence(
            doc=doc,
            view=view,
            out_dir=out_dir,
            start_index=0,
            frame_count=ground_frames,
            phase="ground",
            zones=GROUND_VISIBLE_ZONES,
            train_label=GROUND_TRAIN_LABEL,
            start_center_x_mm=25_500.0,
            end_center_x_mm=70_000.0,
            width=width,
            height=height,
        )
    finally:
        App.closeDocument(doc.Name)

    # Reopen the source document for the second shot. Coin3D can retain stale
    # group visibility after switching a large scene in place; a fresh view
    # also ensures phase-one train transforms never leak into phase two.
    doc = App.openDocument(str(model))
    try:
        Gui.setActiveDocument(doc.Name)
        view = Gui.getDocument(doc.Name).activeView()
        next_index = _render_sequence(
            doc=doc,
            view=view,
            out_dir=out_dir,
            start_index=next_index,
            frame_count=elevated_frames,
            phase="elevated",
            zones=ELEVATED_VISIBLE_ZONES,
            train_label=ELEVATED_TRAIN_LABEL,
            start_center_x_mm=140_000.0,
            end_center_x_mm=290_000.0,
            width=width,
            height=height,
        )
        return next_index
    finally:
        App.closeDocument(doc.Name)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        type=Path,
        default=Path(
            os.environ.get(
                "OSR_TWIN_MODEL",
                _catalog_root() / "civil-systems-integration-test.FCStd",
            )
        ),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(os.environ.get("OSR_TWIN_FRAME_DIR", _frames_root())),
    )
    parser.add_argument(
        "--ground-frames",
        type=int,
        default=int(os.environ.get("OSR_TWIN_GROUND_FRAMES", "14")),
    )
    parser.add_argument(
        "--elevated-frames",
        type=int,
        default=int(os.environ.get("OSR_TWIN_ELEVATED_FRAMES", "18")),
    )
    parser.add_argument("--width", type=int, default=int(os.environ.get("OSR_TWIN_WIDTH", "960")))
    parser.add_argument("--height", type=int, default=int(os.environ.get("OSR_TWIN_HEIGHT", "540")))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    count = render_animation_frames(
        model=args.model,
        out_dir=args.out_dir,
        ground_frames=args.ground_frames,
        elevated_frames=args.elevated_frames,
        width=args.width,
        height=args.height,
    )
    print(f"rendered {count} digital-twin animation frames", flush=True)
    return 0


if __name__ == "__main__":
    try:
        arguments = (
            [] if os.environ.get("OSR_TWIN_ANIMATION_RUN") == "1" else sys.argv[1:]
        )
        sys.exit(main(arguments))
    finally:
        if QtCore is not None:
            QtCore.QCoreApplication.quit()
