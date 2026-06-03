"""Create FreeCAD assembled/exploded review states and shape checks.

The review documents are generated directly from build123d source
geometry, then saved as compact FreeCAD documents. Assembled and
disassembled states are placement views for design review.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from osr_mech.freecad_occ_bridge import SourceGeometry, freecad_shape_from_source, safe_name


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
    source: SourceGeometry
    name: str
    x_mm: float = 0.0
    y_mm: float = 0.0
    z_mm: float = 0.0
    yaw_deg: float = 0.0
    colour: tuple[float, float, float, float] | None = None


@dataclass(frozen=True)
class ShapeCheck:
    name: str
    source_key: str
    valid: bool
    check_ok: bool
    solids_valid: bool
    solids: int
    volume_mm3: float
    bbox_mm: tuple[float, float, float]
    issue: str | None = None


def _source(key: str) -> SourceGeometry:
    return SourceGeometry(key=key)


def _interface_source(key: str) -> SourceGeometry:
    return _source(key)


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


def _artifact_root() -> Path:
    return Path(__file__).resolve().parents[2] / "catalog" / "freecad"


def _add_shape(
    doc,
    item: ReviewItem,
    group,
    shape_cache: dict[str, object],
    temp_dir: Path,
):
    shape = freecad_shape_from_source(
        item.source,
        part_module=Part,
        cache=shape_cache,
        temp_dir=temp_dir,
    )
    obj = doc.addObject("Part::Feature", safe_name(item.name))
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


def _check_shape(
    item: ReviewItem,
    shape_cache: dict[str, object],
    temp_dir: Path,
) -> ShapeCheck:
    try:
        shape = freecad_shape_from_source(
            item.source,
            part_module=Part,
            cache=shape_cache,
            temp_dir=temp_dir,
        )
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
            source_key=item.source.key,
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
            source_key=item.source.key,
            valid=False,
            check_ok=False,
            solids_valid=False,
            solids=0,
            volume_mm3=0.0,
            bbox_mm=(0.0, 0.0, 0.0),
            issue=str(exc),
        )


def _chassis_bogie_items(*, exploded: bool) -> list[ReviewItem]:
    if not exploded:
        return [
            ReviewItem(_interface_source("low-floor-chassis"), "Low-floor chassis", colour=COLOURS["structure"]),
            ReviewItem(
                _interface_source("bogie-to-chassis-connector"),
                "Bogie-to-chassis connector package",
                colour=COLOURS["interface"],
            ),
            ReviewItem(
                _source("motor-bogie"),
                "A-end motor bogie",
                x_mm=-BOGIE_X_MM,
                colour=COLOURS["bogie"],
            ),
            ReviewItem(
                _source("trailer-bogie"),
                "B-end trailer bogie",
                x_mm=BOGIE_X_MM,
                colour=COLOURS["bogie"],
            ),
            ReviewItem(
                _interface_source("bogie-to-motor-connector"),
                "A-end bogie-to-motor connector",
                x_mm=-BOGIE_X_MM,
                colour=COLOURS["interface"],
            ),
        ]
    return [
        ReviewItem(
            _interface_source("low-floor-chassis"),
            "Exploded low-floor chassis",
            z_mm=1_650.0,
            colour=COLOURS["structure"],
        ),
        ReviewItem(
            _interface_source("bogie-to-chassis-connector"),
            "Exploded bogie-to-chassis connector package",
            z_mm=850.0,
            colour=COLOURS["interface"],
        ),
        ReviewItem(
            _source("motor-bogie"),
            "Exploded A-end motor bogie",
            x_mm=-BOGIE_X_MM,
            y_mm=-2_100.0,
            z_mm=-650.0,
            colour=COLOURS["bogie"],
        ),
        ReviewItem(
            _source("trailer-bogie"),
            "Exploded B-end trailer bogie",
            x_mm=BOGIE_X_MM,
            y_mm=2_100.0,
            z_mm=-650.0,
            colour=COLOURS["bogie"],
        ),
        ReviewItem(
            _interface_source("bogie-to-motor-connector"),
            "Exploded A-end bogie-to-motor connector",
            x_mm=-BOGIE_X_MM,
            y_mm=-3_250.0,
            z_mm=180.0,
            colour=COLOURS["interface"],
        ),
    ]


def _full_body_items(*, exploded: bool) -> list[ReviewItem]:
    if not exploded:
        return [
            ReviewItem(_source("car-body-structure"), "Body primary structure", colour=COLOURS["structure"]),
            ReviewItem(_source("car-body-exterior"), "Body exterior layer", colour=COLOURS["body"]),
            ReviewItem(_source("car-body-interior"), "Body interior layer", colour=COLOURS["systems"]),
            ReviewItem(_source("car-body-services"), "Body service layers", colour=COLOURS["systems"]),
            ReviewItem(_source("car-systems"), "Car systems package", colour=COLOURS["systems"]),
            ReviewItem(
                _interface_source("mechanical-interface-package"),
                "Mechanical interface package",
                colour=COLOURS["interface"],
            ),
        ]
    return [
        ReviewItem(
            _source("car-body-structure"),
            "Exploded body primary structure",
            colour=COLOURS["structure"],
        ),
        ReviewItem(
            _source("car-body-exterior"),
            "Exploded body exterior layer",
            y_mm=-4_200.0,
            colour=COLOURS["body"],
        ),
        ReviewItem(
            _source("car-body-interior"),
            "Exploded body interior layer",
            y_mm=4_200.0,
            colour=COLOURS["systems"],
        ),
        ReviewItem(
            _source("car-body-services"),
            "Exploded body service layers",
            z_mm=3_350.0,
            colour=COLOURS["systems"],
        ),
        ReviewItem(
            _source("car-systems"),
            "Exploded car systems package",
            z_mm=-1_650.0,
            colour=COLOURS["systems"],
        ),
        ReviewItem(
            _interface_source("mechanical-interface-package"),
            "Exploded mechanical interface package",
            y_mm=0.0,
            z_mm=1_900.0,
            colour=COLOURS["interface"],
        ),
    ]


def _write_review_doc(
    *,
    output: Path,
    title: str,
    assembled_items: list[ReviewItem],
    exploded_items: list[ReviewItem],
) -> list[ShapeCheck]:
    _require_freecad()
    doc = App.newDocument(safe_name(title))
    doc.Label = title
    assembled_group = doc.addObject("App::DocumentObjectGroup", "Assembled_State")
    assembled_group.Label = "Assembled State"
    exploded_group = doc.addObject("App::DocumentObjectGroup", "Disassembled_State")
    exploded_group.Label = "Disassembled / Exploded State"

    checks: list[ShapeCheck] = []
    shape_cache: dict[str, object] = {}
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="osr-freecad-brep-", dir=output.parent) as tmp:
        temp_dir = Path(tmp)
        for item in assembled_items:
            _add_shape(doc, item, assembled_group, shape_cache, temp_dir)
            checks.append(_check_shape(item, shape_cache, temp_dir))
        for item in exploded_items:
            _add_shape(doc, item, exploded_group, shape_cache, temp_dir)

    notes = doc.addObject("App::DocumentObjectGroup", "SourceNotes")
    notes.Label = "Generated directly from build123d source geometry; assembled and exploded states are placement views"
    doc.recompute()
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
        "Generated directly from build123d source geometry. The checks below use FreeCAD/OCC",
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
                "| Item | Source | Valid | OCC check | Solids | Volume mm^3 | Bounding box mm | Issue |",
                "|---|---|---:|---:|---:|---:|---|---|",
            ]
        )
        for check in checks:
            bbox = " x ".join(f"{v:.0f}" for v in check.bbox_mm)
            issue = check.issue or ""
            if issue or not check.valid or not check.check_ok:
                issues.append(f"{doc_name}: {check.name}: {issue or 'invalid shape'}")
            lines.append(
                f"| {check.name} | `{check.source_key}` | {check.valid and check.solids_valid} | {check.check_ok} | "
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
            "solid/shell meshing."
        )
    else:
        lines.append("- No invalid source shapes or zero-size bounding boxes detected.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {path}")


def build_review_documents(*, out_dir: Path) -> None:
    chassis_out = out_dir / "chassis-bogie-assembly-states.FCStd"
    body_out = out_dir / "full-body-assembly-states.FCStd"
    checks_by_doc = {
        "Chassis + Bogie Assembly": _write_review_doc(
            output=chassis_out,
            title="OSR chassis and bogie assembly states",
            assembled_items=_chassis_bogie_items(exploded=False),
            exploded_items=_chassis_bogie_items(exploded=True),
        ),
        "Full Body Assembly": _write_review_doc(
            output=body_out,
            title="OSR full body assembly states",
            assembled_items=_full_body_items(exploded=False),
            exploded_items=_full_body_items(exploded=True),
        ),
    }
    _write_report(out_dir / "assembly-geometry-review.md", checks_by_doc)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build FreeCAD assembled/exploded review documents.")
    parser.add_argument("--out-dir", type=Path, default=_artifact_root())
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
    build_review_documents(out_dir=args.out_dir)


def _running_as_freecad_script() -> bool:
    return bool(sys.argv[1:2]) and Path(sys.argv[1]).name == "freecad_assembly_review.py"


if __name__ == "__main__" or _running_as_freecad_script():
    main(sys.argv[1:])
