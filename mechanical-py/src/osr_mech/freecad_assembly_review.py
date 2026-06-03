"""Create FreeCAD assembled/exploded review states and shape checks.

The build123d STEP catalogue remains the geometry authority. This
bridge imports selected rolling-stock STEP artifacts into FreeCAD,
creates assembled and disassembled/exploded review groups, and writes a
small geometry report for validity/bounding-box inspection.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


try:
    import FreeCAD as App  # type: ignore[import-not-found]
    import Part  # type: ignore[import-not-found]
except Exception as exc:  # pragma: no cover - exercised only outside FreeCAD.
    App = None  # type: ignore[assignment]
    Part = None  # type: ignore[assignment]
    _FREECAD_IMPORT_ERROR = exc
else:
    _FREECAD_IMPORT_ERROR = None


CAR_LENGTH_MM = 17_000.0
BOGIE_X_MM = CAR_LENGTH_MM / 2.0 - 2_100.0

COLOURS = {
    "structure": (0.52, 0.54, 0.56, 0.0),
    "body": (0.88, 0.91, 0.92, 0.0),
    "systems": (0.18, 0.39, 0.68, 0.0),
    "interface": (0.95, 0.68, 0.18, 0.0),
    "bogie": (0.12, 0.12, 0.12, 0.0),
}


@dataclass(frozen=True)
class ReviewItem:
    path: Path
    name: str
    x_mm: float = 0.0
    y_mm: float = 0.0
    z_mm: float = 0.0
    yaw_deg: float = 0.0
    colour: tuple[float, float, float, float] | None = None


@dataclass(frozen=True)
class ShapeCheck:
    name: str
    path: Path
    valid: bool
    check_ok: bool
    solids_valid: bool
    solids: int
    volume_mm3: float
    bbox_mm: tuple[float, float, float]
    issue: str | None = None


def _summarise_occ_issue(exc: Exception) -> str:
    text = str(exc)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    counter: Counter[str] = Counter()
    for line in lines:
        if "BOPAlgo" in line:
            counter[line] += 1
    if counter:
        common = ", ".join(f"{count}x {label}" for label, count in counter.most_common(4))
        return f"OCC compound check reported overlaps/self-intersections: {common}"
    return lines[0] if lines else repr(exc)


def _require_freecad() -> None:
    if App is None or Part is None:
        raise SystemExit(
            "FreeCAD Python modules are not importable. Run this with FreeCADCmd "
            "or mechanical-py/scripts/freecad_assembly_review.sh.\n"
            f"Import error was: {_FREECAD_IMPORT_ERROR!r}"
        )


def _catalog_root() -> Path:
    return Path(__file__).resolve().parents[2] / "catalog"


def _safe_name(name: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in name).strip("_")


def _shape_from_step(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"missing STEP input: {path}")
    shape = Part.Shape()
    shape.read(str(path))
    return shape


def _add_shape(doc, item: ReviewItem, group):
    shape = _shape_from_step(item.path)
    obj = doc.addObject("Part::Feature", _safe_name(item.name))
    obj.Label = item.name
    obj.Shape = shape
    obj.Placement = App.Placement(
        App.Vector(item.x_mm, item.y_mm, item.z_mm),
        App.Rotation(App.Vector(0, 0, 1), item.yaw_deg),
    )
    view_object = getattr(obj, "ViewObject", None)
    if item.colour is not None and view_object is not None:
        view_object.ShapeColor = item.colour
    group.addObject(obj)
    return obj


def _check_shape(item: ReviewItem) -> ShapeCheck:
    try:
        shape = _shape_from_step(item.path)
        check_ok = True
        issue = None
        try:
            shape.check(True)
        except Exception as exc:  # FreeCAD returns detailed OCC text here.
            check_ok = False
            issue = _summarise_occ_issue(exc)
        bbox = shape.BoundBox
        size = (bbox.XLength, bbox.YLength, bbox.ZLength)
        valid = bool(shape.isValid())
        solids_valid = all(solid.isValid() for solid in shape.Solids)
        if bbox.XLength <= 0.0 or bbox.YLength <= 0.0 or bbox.ZLength <= 0.0:
            valid = False
            issue = issue or "zero-size bounding box axis"
        return ShapeCheck(
            name=item.name,
            path=item.path,
            valid=valid,
            check_ok=check_ok,
            solids_valid=solids_valid,
            solids=len(shape.Solids),
            volume_mm3=float(shape.Volume),
            bbox_mm=size,
            issue=issue,
        )
    except Exception as exc:
        return ShapeCheck(
            name=item.name,
            path=item.path,
            valid=False,
            check_ok=False,
            solids_valid=False,
            solids=0,
            volume_mm3=0.0,
            bbox_mm=(0.0, 0.0, 0.0),
            issue=str(exc),
        )


def _chassis_bogie_items(catalog: Path, *, exploded: bool) -> list[ReviewItem]:
    rolling = catalog / "rolling_stock"
    interfaces = rolling / "interfaces"
    bogie = catalog / "bogie"
    if not exploded:
        return [
            ReviewItem(interfaces / "low-floor-chassis.step", "Low-floor chassis", colour=COLOURS["structure"]),
            ReviewItem(
                interfaces / "bogie-to-chassis-connector.step",
                "Bogie-to-chassis connector package",
                colour=COLOURS["interface"],
            ),
            ReviewItem(
                bogie / "motor-bogie.step",
                "A-end motor bogie",
                x_mm=-BOGIE_X_MM,
                colour=COLOURS["bogie"],
            ),
            ReviewItem(
                bogie / "trailer-bogie.step",
                "B-end trailer bogie",
                x_mm=BOGIE_X_MM,
                colour=COLOURS["bogie"],
            ),
            ReviewItem(
                interfaces / "bogie-to-motor-connector.step",
                "A-end bogie-to-motor connector",
                x_mm=-BOGIE_X_MM,
                colour=COLOURS["interface"],
            ),
        ]
    return [
        ReviewItem(
            interfaces / "low-floor-chassis.step",
            "Exploded low-floor chassis",
            z_mm=1_650.0,
            colour=COLOURS["structure"],
        ),
        ReviewItem(
            interfaces / "bogie-to-chassis-connector.step",
            "Exploded bogie-to-chassis connector package",
            z_mm=850.0,
            colour=COLOURS["interface"],
        ),
        ReviewItem(
            bogie / "motor-bogie.step",
            "Exploded A-end motor bogie",
            x_mm=-BOGIE_X_MM,
            y_mm=-2_100.0,
            z_mm=-650.0,
            colour=COLOURS["bogie"],
        ),
        ReviewItem(
            bogie / "trailer-bogie.step",
            "Exploded B-end trailer bogie",
            x_mm=BOGIE_X_MM,
            y_mm=2_100.0,
            z_mm=-650.0,
            colour=COLOURS["bogie"],
        ),
        ReviewItem(
            interfaces / "bogie-to-motor-connector.step",
            "Exploded A-end bogie-to-motor connector",
            x_mm=-BOGIE_X_MM,
            y_mm=-3_250.0,
            z_mm=180.0,
            colour=COLOURS["interface"],
        ),
    ]


def _full_body_items(catalog: Path, *, exploded: bool) -> list[ReviewItem]:
    rolling = catalog / "rolling_stock"
    interfaces = rolling / "interfaces"
    if not exploded:
        return [
            ReviewItem(rolling / "car-body-structure.step", "Body primary structure", colour=COLOURS["structure"]),
            ReviewItem(rolling / "car-body-exterior.step", "Body exterior layer", colour=COLOURS["body"]),
            ReviewItem(rolling / "car-body-interior.step", "Body interior layer", colour=COLOURS["systems"]),
            ReviewItem(rolling / "car-body-services.step", "Body service layers", colour=COLOURS["systems"]),
            ReviewItem(rolling / "car-systems.step", "Car systems package", colour=COLOURS["systems"]),
            ReviewItem(
                interfaces / "mechanical-interface-package.step",
                "Mechanical interface package",
                colour=COLOURS["interface"],
            ),
        ]
    return [
        ReviewItem(
            rolling / "car-body-structure.step",
            "Exploded body primary structure",
            colour=COLOURS["structure"],
        ),
        ReviewItem(
            rolling / "car-body-exterior.step",
            "Exploded body exterior layer",
            y_mm=-4_200.0,
            colour=COLOURS["body"],
        ),
        ReviewItem(
            rolling / "car-body-interior.step",
            "Exploded body interior layer",
            y_mm=4_200.0,
            colour=COLOURS["systems"],
        ),
        ReviewItem(
            rolling / "car-body-services.step",
            "Exploded body service layers",
            z_mm=3_350.0,
            colour=COLOURS["systems"],
        ),
        ReviewItem(
            rolling / "car-systems.step",
            "Exploded car systems package",
            z_mm=-1_650.0,
            colour=COLOURS["systems"],
        ),
        ReviewItem(
            interfaces / "mechanical-interface-package.step",
            "Exploded mechanical interface package",
            y_mm=0.0,
            z_mm=1_900.0,
            colour=COLOURS["interface"],
        ),
    ]


def _write_review_doc(
    *,
    catalog: Path,
    output: Path,
    title: str,
    assembled_items: list[ReviewItem],
    exploded_items: list[ReviewItem],
) -> list[ShapeCheck]:
    _require_freecad()
    doc = App.newDocument(_safe_name(title))
    doc.Label = title
    assembled_group = doc.addObject("App::DocumentObjectGroup", "Assembled_State")
    assembled_group.Label = "Assembled State"
    exploded_group = doc.addObject("App::DocumentObjectGroup", "Disassembled_State")
    exploded_group.Label = "Disassembled / Exploded State"

    checks: list[ShapeCheck] = []
    for item in assembled_items:
        _add_shape(doc, item, assembled_group)
        checks.append(_check_shape(item))
    for item in exploded_items:
        _add_shape(doc, item, exploded_group)

    notes = doc.addObject("App::DocumentObjectGroup", "SourceNotes")
    notes.Label = "Generated from build123d STEP catalogue; assembled and exploded states are placement views"
    doc.recompute()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    doc.saveAs(str(output))
    print(f"wrote {output}")
    App.closeDocument(doc.Name)
    return checks


def _write_report(path: Path, checks_by_doc: dict[str, list[ShapeCheck]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# FreeCAD Assembly Geometry Review",
        "",
        "Generated from the build123d STEP catalogue. The checks below use FreeCAD/OCC",
        "`Shape.isValid()`, `Shape.check(True)`, solid counts, volume, and bounding-box",
        "sanity checks on each assembled-state input.",
        "",
    ]
    issues = []
    for doc_name, checks in checks_by_doc.items():
        lines.extend(
            [
                f"## {doc_name}",
                "",
                "| Item | Valid | OCC check | Solids | Volume mm^3 | Bounding box mm | Issue |",
                "|---|---:|---:|---:|---:|---|---|",
            ]
        )
        for check in checks:
            bbox = " x ".join(f"{v:.0f}" for v in check.bbox_mm)
            issue = check.issue or ""
            if issue or not check.valid or not check.check_ok:
                issues.append(f"{doc_name}: {check.name}: {issue or 'invalid shape'}")
            lines.append(
                f"| {check.name} | {check.valid and check.solids_valid} | {check.check_ok} | "
                f"{check.solids} | {check.volume_mm3:.0f} | {bbox} | {issue} |"
            )
        lines.append("")
    lines.extend(["## Geometry Issues", ""])
    if issues:
        lines.extend(f"- {issue}" for issue in issues)
        lines.append("")
        lines.append(
            "Note: several interface packages are review compounds made from overlapping "
            "rectangular solids. `Shape.isValid()` and child-solid validity can still be true "
            "while OCC's Boolean-operation checker reports compound self-intersections at "
            "welded/contacting envelope overlaps. Treat these as geometry cleanup flags before "
            "solid/shell meshing, not as missing STEP imports."
        )
    else:
        lines.append("- No invalid imported STEP shapes or zero-size bounding boxes detected.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {path}")


def build_review_documents(*, catalog: Path, out_dir: Path) -> None:
    chassis_out = out_dir / "chassis-bogie-assembly-states.FCStd"
    body_out = out_dir / "full-body-assembly-states.FCStd"
    checks_by_doc = {
        "Chassis + Bogie Assembly": _write_review_doc(
            catalog=catalog,
            output=chassis_out,
            title="OSR chassis and bogie assembly states",
            assembled_items=_chassis_bogie_items(catalog, exploded=False),
            exploded_items=_chassis_bogie_items(catalog, exploded=True),
        ),
        "Full Body Assembly": _write_review_doc(
            catalog=catalog,
            output=body_out,
            title="OSR full body assembly states",
            assembled_items=_full_body_items(catalog, exploded=False),
            exploded_items=_full_body_items(catalog, exploded=True),
        ),
    }
    _write_report(out_dir / "assembly-geometry-review.md", checks_by_doc)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build FreeCAD assembled/exploded review documents.")
    parser.add_argument("--catalog", type=Path, default=_catalog_root())
    parser.add_argument("--out-dir", type=Path, default=_catalog_root() / "freecad")
    return parser.parse_args(argv)


def _normalise_freecad_argv(argv: list[str]) -> list[str]:
    args = list(argv)
    if args and Path(args[0]).name == "freecad_assembly_review.py":
        args = args[1:]
    if args and args[0] == "--pass":
        args = args[1:]
    return args


def main(argv: list[str] | None = None) -> None:
    args = parse_args(_normalise_freecad_argv(argv or []))
    build_review_documents(catalog=args.catalog, out_dir=args.out_dir)


def _running_as_freecad_script() -> bool:
    return bool(sys.argv[1:2]) and Path(sys.argv[1]).name == "freecad_assembly_review.py"


if __name__ == "__main__" or _running_as_freecad_script():
    main(sys.argv[1:])
