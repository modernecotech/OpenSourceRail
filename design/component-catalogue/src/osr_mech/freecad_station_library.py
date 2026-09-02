"""Generate native FreeCAD coordination assemblies for all station variants."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from osr_mech.cad import to_freecad_shape
from osr_mech.freecad_assembly_review import _canonicalise_fcstd
from osr_mech.freecad_occ_bridge import safe_name
from osr_mech.station.product_geometry import flatten_geometry, geometry_specs, station_product_geometry

try:
    import FreeCAD as App  # type: ignore[import-not-found]
except Exception as exc:  # pragma: no cover - FreeCAD runner only
    App = None  # type: ignore[assignment]
    _FREECAD_IMPORT_ERROR = exc
else:
    _FREECAD_IMPORT_ERROR = None


REPO_ROOT = Path(__file__).resolve().parents[4]
MANIFEST = REPO_ROOT / "design/component-catalogue/catalog/buildable-stations/station-kit-manifest.json"
DEFAULT_OUTPUT = REPO_ROOT / "design/component-catalogue/models/cad/stations"
RELEASE_BOUNDARY = (
    "Design-reference station geometry only; site survey, supplier freeze, "
    "structural calculations, local-code review and construction release remain mandatory."
)


def _require_freecad() -> None:
    if App is None:
        raise SystemExit(
            "FreeCAD Python modules are not importable. Run with "
            "design/component-catalogue/scripts/freecad_station_library.sh.\n"
            f"Import error was: {_FREECAD_IMPORT_ERROR!r}"
        )


def _property(obj, kind: str, name: str, value: object) -> None:
    obj.addProperty(kind, name, "OSR Station Library")
    setattr(obj, name, value)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _save(doc, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    doc.recompute()
    doc.saveAs(str(output))
    App.closeDocument(doc.Name)
    _canonicalise_fcstd(output)


def _write_variant(variant: dict[str, object], output: Path) -> dict[str, object]:
    archetype = str(variant["archetype"])
    doc = App.newDocument(safe_name(f"station_{archetype}"))
    doc.Label = f"OSR {archetype} station coordination assembly"
    root = doc.addObject("App::DocumentObjectGroup", "StationAssembly")
    root.Label = f"{archetype} station product assembly"
    meta = doc.addObject("App::FeaturePython", "ControlledDefinition")
    meta.Label = "READ FIRST — station release boundary"
    _property(meta, "App::PropertyString", "Archetype", archetype)
    _property(meta, "App::PropertyString", "GeometryStatus", "coordinated-design-reference-geometry")
    _property(meta, "App::PropertyString", "ReleaseBoundary", RELEASE_BOUNDARY)
    _property(meta, "App::PropertyString", "ControlledManifest", str(MANIFEST.relative_to(REPO_ROOT)))
    _property(meta, "App::PropertyString", "ManifestSha256", _sha256(MANIFEST))
    root.addObject(meta)

    hierarchy = doc.addObject("App::DocumentObjectGroup", "AssemblyHierarchy")
    hierarchy.Label = "Controlled station assembly hierarchy"
    root.addObject(hierarchy)
    for assembly in variant["assemblies"]:
        node = doc.addObject("App::FeaturePython", safe_name(f"Assembly_{assembly['id']}"))
        node.Label = f"{assembly['id']} — {assembly['title']}"
        _property(node, "App::PropertyString", "OSRAssemblyId", str(assembly["id"]))
        _property(node, "App::PropertyStringList", "DirectChildren", [str(value) for value in assembly["children"]])
        _property(node, "App::PropertyString", "WorkCell", str(assembly["work_cell"]))
        _property(node, "App::PropertyStringList", "HoldPoints", [str(value) for value in assembly["hold_points"]])
        hierarchy.addObject(node)

    specs = geometry_specs()
    primitive_count = 0
    product_ids: list[str] = []
    for item in variant["product_items"]:
        product_id = str(item["id"])
        product_ids.append(product_id)
        group = doc.addObject("App::DocumentObjectGroup", safe_name(f"Product_{product_id}"))
        group.Label = f"{product_id} — {item['title']}"
        root.addObject(group)
        built = station_product_geometry(item, variant["parameters"])
        for index, leaf in enumerate(flatten_geometry(built), start=1):
            shape = to_freecad_shape(leaf)
            if shape is None or shape.isNull() or not shape.isValid() or shape.Volume <= 0:
                raise RuntimeError(f"invalid native station shape {archetype}/{product_id}/{index}")
            obj = doc.addObject("Part::Feature", safe_name(f"{product_id}_{index:03d}"))
            obj.Label = f"{product_id} · {leaf.label or item['title']}"
            obj.Shape = shape
            if leaf.color is not None and getattr(obj, "ViewObject", None) is not None:
                obj.ViewObject.ShapeColor = (leaf.color.r, leaf.color.g, leaf.color.b)
                obj.ViewObject.Transparency = max(0, min(100, round((1.0 - leaf.color.a) * 100)))
            _property(obj, "App::PropertyString", "OSRId", product_id)
            _property(obj, "App::PropertyString", "PrimitiveId", f"{product_id}-{index:03d}")
            _property(obj, "App::PropertyString", "ParentAssembly", str(item["parent"]))
            _property(obj, "App::PropertyString", "Route", str(item["route"]))
            _property(obj, "App::PropertyString", "Maturity", str(item["maturity"]))
            _property(obj, "App::PropertyString", "GeometryLevel", specs[product_id].geometry_level)
            _property(obj, "App::PropertyString", "IFCClass", specs[product_id].ifc_class)
            group.addObject(obj)
            primitive_count += 1
    _save(doc, output)

    reopened = App.openDocument(str(output))
    try:
        shapes = [obj for obj in reopened.Objects if obj.TypeId == "Part::Feature"]
        found = {str(obj.OSRId) for obj in shapes if hasattr(obj, "OSRId")}
        invalid = [obj.Name for obj in shapes if obj.Shape.isNull() or not obj.Shape.isValid() or obj.Shape.Volume <= 0]
        if found != set(product_ids) or len(shapes) != primitive_count or invalid:
            raise RuntimeError(
                f"station FreeCAD round-trip failed for {archetype}: "
                f"missing={sorted(set(product_ids) - found)}, shapes={len(shapes)}/{primitive_count}, invalid={invalid}"
            )
    finally:
        App.closeDocument(reopened.Name)
    return {
        "archetype": archetype,
        "file": str(output.relative_to(REPO_ROOT)),
        "sha256": _sha256(output),
        "size_bytes": output.stat().st_size,
        "product_count": len(product_ids),
        "assembly_count": len(variant["assemblies"]),
        "primitive_count": primitive_count,
        "reopen_validated": True,
    }


def build_library(output_root: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    _require_freecad()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    variants = [
        _write_variant(variant, output_root / f"station-{variant['archetype']}.FCStd")
        for variant in manifest["variants"]
    ]
    report = {
        "schema": "org.opensourcerail.station-freecad-library.v1",
        "status": "design-reference-not-released",
        "release_boundary": RELEASE_BOUNDARY,
        "manifest": str(MANIFEST.relative_to(REPO_ROOT)),
        "manifest_sha256": _sha256(MANIFEST),
        "variant_count": len(variants),
        "variants": variants,
        "passed": len(variants) == 7 and all(value["reopen_validated"] for value in variants),
    }
    index = output_root / "station-library.index.json"
    index.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"variant_count": len(variants), "passed": report["passed"]}, indent=2))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    return 0 if build_library(args.output_root.resolve())["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
