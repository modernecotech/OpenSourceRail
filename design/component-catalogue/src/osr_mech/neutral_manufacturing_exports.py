"""Export controlled LM3 MAKE geometry to neutral STEP and inspection DXF.

STEP contains the same design-reference solids as the FreeCAD product library.
DXF is deliberately an XY inspection projection, not a developed sheet-metal
flat pattern.  Released flat patterns remain a drawing-package gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from html import escape
from pathlib import Path

from osr_mech.cad import to_freecad_shape
from osr_mech.rolling_stock.product_geometry import flatten_geometry, geometry_level, product_geometry

try:
    import FreeCAD as App  # type: ignore[import-not-found]
    import Part  # type: ignore[import-not-found]
except Exception as exc:  # pragma: no cover - FreeCAD runner only
    App = None  # type: ignore[assignment]
    Part = None  # type: ignore[assignment]
    _FREECAD_IMPORT_ERROR = exc
else:
    _FREECAD_IMPORT_ERROR = None


REPO_ROOT = Path(__file__).resolve().parents[4]
MANIFEST = REPO_ROOT / "design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.json"
DEFAULT_OUTPUT = REPO_ROOT / "design/component-catalogue/models/manufacturing-reference"
FIXED_TIMESTAMP = "2026-09-02T00:00:00"
RELEASE_BOUNDARY = (
    "Design-reference neutral geometry only; not an NC file, developed flat "
    "pattern, tolerance drawing, supplier release or authority-approved design."
)


def _require_freecad() -> None:
    if App is None or Part is None:
        raise SystemExit(
            "FreeCAD Python modules are not importable. Run with "
            "design/component-catalogue/scripts/freecad_neutral_exports.sh.\n"
            f"Import error was: {_FREECAD_IMPORT_ERROR!r}"
        )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonicalise_step(path: Path, product_id: str) -> None:
    text = path.read_text(encoding="utf-8", errors="strict")
    text = re.sub(
        r"FILE_NAME\([^;]+;",
        f"FILE_NAME('{product_id}.step','{FIXED_TIMESTAMP}',('OpenSourceRail'),('OpenSourceRail'),'FreeCAD 1.1','OpenSourceRail','design-reference / not for construction');",
        text,
        count=1,
        flags=re.DOTALL,
    )
    path.write_text(text, encoding="utf-8")


def _inspection_dxf(product_id: str, leaves: list[object], output: Path) -> None:
    lines = [
        "0", "SECTION", "2", "HEADER", "9", "$ACADVER", "1", "AC1015", "0", "ENDSEC",
        "0", "SECTION", "2", "ENTITIES",
    ]
    for index, leaf in enumerate(leaves, start=1):
        box = leaf.bounding_box()
        layer = f"{product_id}-{index:03d}"
        points = (
            (box.min.X, box.min.Y),
            (box.max.X, box.min.Y),
            (box.max.X, box.max.Y),
            (box.min.X, box.max.Y),
        )
        lines.extend(["0", "LWPOLYLINE", "8", layer, "90", "4", "70", "1"])
        for x, y in points:
            lines.extend(["10", f"{x:.6f}", "20", f"{y:.6f}"])
    lines.extend(["0", "ENDSEC", "0", "EOF", ""])
    output.write_text("\n".join(lines), encoding="ascii")


def _inspection_svg(product_id: str, title: str, leaves: list[object], output: Path) -> None:
    """Write a deterministic three-view envelope sheet for workshop review.

    This is intentionally a reference sheet rather than an implied tolerance or
    production drawing.  Individual primitive rectangles make hidden overlaps
    visible while keeping the format usable in browsers and vector editors.
    """
    overall = [leaf.bounding_box() for leaf in leaves]
    minimum = (
        min(box.min.X for box in overall),
        min(box.min.Y for box in overall),
        min(box.min.Z for box in overall),
    )
    maximum = (
        max(box.max.X for box in overall),
        max(box.max.Y for box in overall),
        max(box.max.Z for box in overall),
    )
    dimensions = tuple(maximum[index] - minimum[index] for index in range(3))
    views = (
        ("PLAN X/Y", 0, 1, 35.0, 72.0),
        ("SIDE X/Z", 0, 2, 345.0, 72.0),
        ("END Y/Z", 1, 2, 655.0, 72.0),
    )
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" viewBox="0 0 960 540">',
        '<rect width="960" height="540" fill="white" stroke="#162332" stroke-width="2"/>',
        f'<text x="28" y="35" font-family="sans-serif" font-size="20" font-weight="bold">{escape(product_id)} — {escape(title)}</text>',
        '<text x="28" y="56" font-family="sans-serif" font-size="11">DESIGN-REFERENCE ENVELOPE SHEET · NOT FOR MANUFACTURE</text>',
    ]
    for label, first, second, origin_x, origin_y in views:
        span_x = max(dimensions[first], 1.0)
        span_y = max(dimensions[second], 1.0)
        scale = min(260.0 / span_x, 300.0 / span_y)
        svg.append(f'<text x="{origin_x:.1f}" y="{origin_y:.1f}" font-family="sans-serif" font-size="12">{label}</text>')
        for index, box in enumerate(overall, start=1):
            mins = (box.min.X, box.min.Y, box.min.Z)
            maxs = (box.max.X, box.max.Y, box.max.Z)
            x = origin_x + (mins[first] - minimum[first]) * scale
            y = origin_y + 315.0 - (maxs[second] - minimum[second]) * scale
            width = max((maxs[first] - mins[first]) * scale, 0.5)
            height = max((maxs[second] - mins[second]) * scale, 0.5)
            svg.append(
                f'<rect x="{x:.3f}" y="{y:.3f}" width="{width:.3f}" height="{height:.3f}" '
                f'fill="none" stroke="#167d8d" stroke-width="0.8" data-primitive="{index:03d}"/>'
            )
        svg.append(
            f'<text x="{origin_x:.1f}" y="407" font-family="monospace" font-size="10">'
            f'{dimensions[first]:.1f} × {dimensions[second]:.1f} mm</text>'
        )
    svg.extend([
        '<line x1="28" y1="442" x2="932" y2="442" stroke="#162332"/>',
        f'<text x="28" y="466" font-family="monospace" font-size="12">OVERALL X/Y/Z: {dimensions[0]:.1f} / {dimensions[1]:.1f} / {dimensions[2]:.1f} mm</text>',
        '<text x="28" y="490" font-family="sans-serif" font-size="11">Verify material, datums, tolerances, weld/laminate definition and process qualification before release.</text>',
        '<text x="28" y="514" font-family="sans-serif" font-size="10">Source: controlled LM3 product manifest and parametric geometry · units: mm · scale: fit to view</text>',
        '</svg>',
        '',
    ])
    output.write_text("\n".join(svg), encoding="utf-8")


def export(output_root: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    _require_freecad()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    step_root = output_root / "step"
    dxf_root = output_root / "dxf-inspection-projections"
    drawing_root = output_root / "drawing-references"
    step_root.mkdir(parents=True, exist_ok=True)
    dxf_root.mkdir(parents=True, exist_ok=True)
    drawing_root.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, object]] = []
    for item in manifest["product_items"]:
        if item["route"] != "MAKE":
            continue
        product_id = str(item["id"])
        leaves = flatten_geometry(product_geometry(product_id, str(item["title"])))
        native = [to_freecad_shape(leaf) for leaf in leaves]
        if any(shape is None or shape.isNull() or not shape.isValid() for shape in native):
            raise RuntimeError(f"invalid neutral-export shape for {product_id}")
        compound = Part.makeCompound(native)
        step = step_root / f"{product_id}.step"
        compound.exportStep(str(step))
        _canonicalise_step(step, product_id)
        imported = Part.read(str(step))
        if imported.isNull() or not imported.isValid():
            raise RuntimeError(f"STEP round-trip failed for {product_id}")
        dxf = dxf_root / f"{product_id}.dxf"
        _inspection_dxf(product_id, leaves, dxf)
        drawing = drawing_root / f"{product_id}.svg"
        _inspection_svg(product_id, str(item["title"]), leaves, drawing)
        entries.append({
            "id": product_id,
            "title": item["title"],
            "geometry_level": geometry_level(product_id, str(item["route"]), str(item["maturity"])),
            "primitive_count": len(leaves),
            "step": str(step.relative_to(REPO_ROOT)),
            "step_sha256": _sha256(step),
            "dxf": str(dxf.relative_to(REPO_ROOT)),
            "dxf_sha256": _sha256(dxf),
            "dxf_role": "XY inspection projection; not a developed flat pattern",
            "drawing": str(drawing.relative_to(REPO_ROOT)),
            "drawing_sha256": _sha256(drawing),
            "drawing_role": "three-view envelope reference; not a tolerance drawing",
            "step_round_trip_valid": True,
            "release_evidence": item["acceptance"],
        })
    expected_step = {f"{entry['id']}.step" for entry in entries}
    expected_dxf = {f"{entry['id']}.dxf" for entry in entries}
    expected_svg = {f"{entry['id']}.svg" for entry in entries}
    stale = {
        *({path.name for path in step_root.glob("*.step")} - expected_step),
        *({path.name for path in dxf_root.glob("*.dxf")} - expected_dxf),
        *({path.name for path in drawing_root.glob("*.svg")} - expected_svg),
    }
    if stale:
        raise RuntimeError(f"stale neutral reference files: {sorted(stale)}")
    report = {
        "schema": "org.opensourcerail.neutral-manufacturing-reference.v1",
        "status": "design-reference-not-released",
        "release_boundary": RELEASE_BOUNDARY,
        "manifest": str(MANIFEST.relative_to(REPO_ROOT)),
        "manifest_sha256": _sha256(MANIFEST),
        "make_product_count": len(entries),
        "entries": entries,
        "passed": len(entries) == 62 and all(entry["step_round_trip_valid"] for entry in entries),
    }
    index = output_root / "index.json"
    index.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    readme = output_root / "README.md"
    readme.write_text(
        "# LM3 neutral manufacturing reference\n\n"
        "This folder tracks DXF XY inspection projections, browser-viewable three-view\n"
        "SVG reference sheets and the controlled hashes for deterministic STEP geometry\n"
        "for the 62 locally manufactured (`MAKE`) product rows. Generate the local-only\n"
        "STEP handoffs with `tools/automation/freecad-generate.sh --neutral-exports`;\n"
        "they are excluded from Git as reproducible, bulky CAD interchange outputs.\n"
        "DXF and SVG control only design-reference envelopes; they are not sheet-metal\n"
        "flat patterns, tolerance drawings or NC files.\n\n"
        "The complete hashes, fidelity levels and release gates are in\n"
        "[`index.json`](index.json). Supplier freeze, detailed tolerance drawings,\n"
        "developed flat patterns, weld maps, calculations and first-article evidence\n"
        "remain mandatory before manufacture.\n",
        encoding="utf-8",
    )
    print(json.dumps({"make_product_count": len(entries), "passed": report["passed"]}, indent=2))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    return 0 if export(args.output_root.resolve())["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
