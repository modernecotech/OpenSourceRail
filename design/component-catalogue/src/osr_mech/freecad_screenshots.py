"""Capture FreeCAD PNG screenshots for rolling-stock review docs.

This script is intended to run under the FreeCAD GUI executable, not
FreeCADCmd, because it uses ``FreeCADGui.ActiveDocument.ActiveView`` to
save viewport images. The companion shell wrapper runs it under Xvfb so
captures are reproducible on headless CI/workstations.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path


try:
    import FreeCAD as App  # type: ignore[import-not-found]
    import FreeCADGui as Gui  # type: ignore[import-not-found]
    from PySide import QtCore  # type: ignore[import-not-found]
except Exception as exc:  # pragma: no cover - only exercised outside FreeCAD GUI.
    App = None  # type: ignore[assignment]
    Gui = None  # type: ignore[assignment]
    QtCore = None  # type: ignore[assignment]
    _FREECAD_IMPORT_ERROR = exc
else:
    _FREECAD_IMPORT_ERROR = None


@dataclass(frozen=True)
class Capture:
    doc: str
    output: str
    groups: tuple[str, ...] | None = None
    view: str = "axonometric"
    width: int = 1800
    height: int = 1100


CAPTURES: tuple[Capture, ...] = (
    Capture(
        doc="chassis-bogie-assembly-states.FCStd",
        output="freecad-chassis-bogie-assembled.png",
        groups=("Assembled State",),
    ),
    Capture(
        doc="chassis-bogie-assembly-states.FCStd",
        output="freecad-chassis-bogie-exploded.png",
        groups=("Disassembled / Exploded State",),
    ),
    Capture(
        doc="full-body-assembly-states.FCStd",
        output="freecad-full-body-assembled.png",
        groups=("Assembled State",),
        width=2200,
        height=1100,
    ),
    Capture(
        doc="full-body-assembly-states.FCStd",
        output="freecad-full-body-exploded.png",
        groups=("Disassembled / Exploded State",),
        width=2200,
        height=1100,
    ),
    Capture(
        doc="fea-screening-models.FCStd",
        output="freecad-fea-screening-models.png",
        width=2200,
        height=1000,
    ),
    Capture(
        doc="fea-screening-models.FCStd",
        output="freecad-fea-chassis-bogie-screen.png",
        groups=("Low-floor chassis supported at bogie connectors",),
    ),
    Capture(
        doc="fea-screening-models.FCStd",
        output="freecad-fea-bogie-frame-screen.png",
        groups=("Motor/trailer bogie H-frame screening model",),
    ),
    Capture(
        doc="fea-screening-models.FCStd",
        output="freecad-fea-full-body-frame-screen.png",
        groups=("Full car body side/roof frame screening model",),
    ),
    Capture(
        doc="trainset-light-metro-3car.FCStd",
        output="freecad-trainset-light-metro-3car.png",
        width=2200,
        height=950,
    ),
)


def _require_freecad_gui() -> None:
    if App is None or Gui is None or QtCore is None:
        raise SystemExit(
            "FreeCAD GUI modules are not importable. Run this with the FreeCAD GUI "
            "or design/component-catalogue/scripts/freecad_screenshots.sh.\n"
            f"Import error was: {_FREECAD_IMPORT_ERROR!r}"
        )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _catalog_freecad_root() -> Path:
    return Path(__file__).resolve().parents[2] / "models" / "cad"


def _screenshots_root() -> Path:
    return _repo_root() / "docs" / "screenshots" / "freecad"


def _refresh_latest_outputs(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for path in out_dir.glob("freecad-*.png"):
        if path.name.endswith("-result.png"):
            continue
        path.unlink()
        print(f"removed old FreeCAD screenshot {path}", flush=True)


def _walk(node):
    yield node
    for child in getattr(node, "OutList", []) or []:
        yield from _walk(child)


def _has_renderable_shape(obj) -> bool:
    shape = getattr(obj, "Shape", None)
    if shape is None:
        return False
    try:
        return not shape.isNull()
    except Exception:
        return False


def _visible_shape_objects(doc) -> list:
    return [obj for obj in doc.Objects if _has_renderable_shape(obj)]


def _hide_all(doc) -> None:
    for obj in doc.Objects:
        view = getattr(obj, "ViewObject", None)
        if view is not None and hasattr(view, "Visibility"):
            view.Visibility = False


def _show_all_shapes(doc) -> None:
    _hide_all(doc)
    for obj in _visible_shape_objects(doc):
        view = getattr(obj, "ViewObject", None)
        if view is not None and hasattr(view, "Visibility"):
            view.Visibility = True


def _find_group(doc, label: str):
    for obj in doc.Objects:
        if getattr(obj, "Label", "") == label or getattr(obj, "Name", "") == label:
            return obj
    raise ValueError(f"group not found in {doc.Name}: {label}")


def _show_groups(doc, labels: tuple[str, ...]) -> None:
    _hide_all(doc)
    for label in labels:
        group = _find_group(doc, label)
        for obj in _walk(group):
            view = getattr(obj, "ViewObject", None)
            if view is not None and hasattr(view, "Visibility"):
                view.Visibility = True


def _set_view(view, name: str) -> None:
    name = name.lower()
    if name in {"axonometric", "axo"}:
        view.viewAxonometric()
    elif name == "isometric":
        view.viewIsometric()
    elif name == "front":
        view.viewFront()
    elif name == "top":
        view.viewTop()
    elif name == "right":
        view.viewRight()
    else:
        raise ValueError(f"unknown view: {name}")


def _capture_one(*, catalog_dir: Path, out_dir: Path, capture: Capture) -> None:
    doc_path = catalog_dir / capture.doc
    if not doc_path.exists():
        raise FileNotFoundError(f"missing FreeCAD document: {doc_path}")
    print(f"opening {doc_path}", flush=True)
    doc = App.openDocument(str(doc_path))
    print(f"capturing {capture.output}", flush=True)
    Gui.setActiveDocument(doc.Name)
    gdoc = Gui.getDocument(doc.Name)
    view = gdoc.activeView()

    if capture.groups is None:
        _show_all_shapes(doc)
    else:
        _show_groups(doc, capture.groups)

    _set_view(view, capture.view)
    Gui.updateGui()
    view.fitAll()
    Gui.updateGui()
    view.fitAll()
    Gui.updateGui()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / capture.output
    view.saveImage(str(out_path), capture.width, capture.height, "White")
    print(f"wrote {out_path} ({out_path.stat().st_size // 1024} KB)", flush=True)
    App.closeDocument(doc.Name)


def capture_all(*, catalog_dir: Path, out_dir: Path) -> None:
    _require_freecad_gui()
    _refresh_latest_outputs(out_dir)
    for capture in CAPTURES:
        _capture_one(catalog_dir=catalog_dir, out_dir=out_dir, capture=capture)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture FreeCAD PNG screenshots.")
    parser.add_argument("--catalog-dir", type=Path, default=_catalog_freecad_root())
    parser.add_argument("--out-dir", type=Path, default=_screenshots_root())
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    capture_all(catalog_dir=args.catalog_dir, out_dir=args.out_dir)
    QtCore.QCoreApplication.quit()


def _running_as_freecad_script() -> bool:
    return bool(sys.argv[:1]) and Path(sys.argv[0]).name == "freecad_screenshots.py"


if __name__ == "__main__" or _running_as_freecad_script():
    main(sys.argv[1:])
