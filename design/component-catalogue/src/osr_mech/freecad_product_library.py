"""Generate one deterministic FreeCAD document per LM3 part and assembly.

Every document exposes native OCC solids, controlled identifiers, source
dimensions and the design-reference release boundary. Assembly documents carry
all descendant product geometries on a deterministic inspection fixture so a
reviewer can select every child and verify the complete EBOM/MBOM hierarchy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from osr_mech.cad import to_freecad_shape
from osr_mech.freecad_assembly_review import _canonicalise_fcstd
from osr_mech.freecad_occ_bridge import safe_name
from osr_mech.rolling_stock.product_geometry import (
    flatten_geometry,
    geometry_level,
    geometry_specs,
    product_geometry,
)


try:
    import FreeCAD as App  # type: ignore[import-not-found]
    import Part  # type: ignore[import-not-found]
except Exception as exc:  # pragma: no cover - FreeCAD runner exercises this.
    App = None  # type: ignore[assignment]
    Part = None  # type: ignore[assignment]
    _FREECAD_IMPORT_ERROR = exc
else:
    _FREECAD_IMPORT_ERROR = None


REPO_ROOT = Path(__file__).resolve().parents[4]
MANIFEST = REPO_ROOT / "design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.json"
DEFAULT_OUTPUT = REPO_ROOT / "design/component-catalogue/models/cad"
RELEASE_BOUNDARY = (
    "Design-reference geometry and assembly hierarchy only; supplier freeze, "
    "released drawings/tolerances, calculations, qualified processes and "
    "first-article tests remain mandatory."
)


def _require_freecad() -> None:
    if App is None or Part is None:
        raise SystemExit(
            "FreeCAD Python modules are not importable. Run with "
            "design/component-catalogue/scripts/freecad_product_library.sh.\n"
            f"Import error was: {_FREECAD_IMPORT_ERROR!r}"
        )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _report_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return path.name


def _property(obj, kind: str, name: str, value: object) -> None:
    obj.addProperty(kind, name, "OSR Product Library")
    setattr(obj, name, value)


def _metadata(doc, *, object_id: str, title: str, definition_type: str):
    meta = doc.addObject("App::FeaturePython", "ControlledDefinition")
    meta.Label = f"{object_id} — READ FIRST"
    _property(meta, "App::PropertyString", "OSRId", object_id)
    _property(meta, "App::PropertyString", "Title", title)
    _property(meta, "App::PropertyString", "DefinitionType", definition_type)
    _property(meta, "App::PropertyString", "GeometryStatus", "design-reference-not-released")
    _property(meta, "App::PropertyString", "ReleaseBoundary", RELEASE_BOUNDARY)
    _property(meta, "App::PropertyString", "ControlledManifest", str(MANIFEST.relative_to(REPO_ROOT)))
    _property(meta, "App::PropertyString", "ManifestSha256", _sha256(MANIFEST))
    return meta


def _add_product_geometry(doc, group, item: dict[str, object], placement: tuple[float, float, float], context: str) -> int:
    geometry = product_geometry(str(item["id"]), str(item["title"]))
    count = 0
    for index, leaf in enumerate(flatten_geometry(geometry), start=1):
        shape = to_freecad_shape(leaf)
        if shape is None or shape.isNull() or not shape.isValid() or shape.Volume <= 0:
            raise RuntimeError(f"invalid native shape for {item['id']} primitive {index}")
        obj = doc.addObject("Part::Feature", safe_name(f"{item['id']}_{context}_{index:03d}"))
        obj.Label = f"{item['id']} · {leaf.label or item['title']}"
        obj.Shape = shape
        obj.Placement = App.Placement(App.Vector(*placement), App.Rotation())
        if leaf.color is not None and getattr(obj, "ViewObject", None) is not None:
            obj.ViewObject.ShapeColor = (leaf.color.r, leaf.color.g, leaf.color.b)
            obj.ViewObject.Transparency = max(0, min(100, round((1.0 - leaf.color.a) * 100)))
        _property(obj, "App::PropertyString", "OSRId", str(item["id"]))
        _property(obj, "App::PropertyString", "PrimitiveId", f"{item['id']}-{index:03d}")
        _property(obj, "App::PropertyString", "Route", str(item["route"]))
        _property(obj, "App::PropertyString", "Maturity", str(item["maturity"]))
        _property(obj, "App::PropertyString", "GeometryLevel", geometry_level(str(item["id"]), str(item["route"]), str(item["maturity"])))
        _property(obj, "App::PropertyInteger", "QuantityPerTrainset", int(item["quantity_per_trainset"]))
        _property(obj, "App::PropertyString", "ParentAssembly", str(item["parent"]))
        _property(obj, "App::PropertyString", "RepresentationState", context)
        group.addObject(obj)
        count += 1
    return count


def _save(doc, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    doc.recompute()
    doc.saveAs(str(output))
    App.closeDocument(doc.Name)
    _canonicalise_fcstd(output)


def _validate_saved_document(
    output: Path,
    expected_product_ids: set[str],
    expected_assembly_ids: set[str],
    expected_shape_count: int,
) -> dict[str, object]:
    """Reopen a canonical FCStd and test native geometry and membership."""

    doc = App.openDocument(str(output))
    try:
        shapes = [obj for obj in doc.Objects if obj.TypeId == "Part::Feature"]
        invalid = [
            obj.Name
            for obj in shapes
            if obj.Shape.isNull() or not obj.Shape.isValid() or obj.Shape.Volume <= 0
        ]
        product_ids = {
            str(obj.OSRId) for obj in shapes if hasattr(obj, "OSRId") and str(obj.OSRId)
        }
        assembly_ids = {
            str(obj.OSRAssemblyId)
            for obj in doc.Objects
            if hasattr(obj, "OSRAssemblyId") and str(obj.OSRAssemblyId)
        }
        passed = bool(
            not invalid
            and len(shapes) == expected_shape_count
            and product_ids == expected_product_ids
            and assembly_ids == expected_assembly_ids
        )
        if not passed:
            raise RuntimeError(
                f"saved FreeCAD validation failed for {output.name}: "
                f"shapes={len(shapes)}/{expected_shape_count}, "
                f"products={sorted(product_ids ^ expected_product_ids)}, "
                f"assemblies={sorted(assembly_ids ^ expected_assembly_ids)}, "
                f"invalid={invalid}"
            )
        return {
            "reopen_validated": True,
            "native_shape_count": len(shapes),
            "validated_product_ids": sorted(product_ids),
            "validated_assembly_ids": sorted(assembly_ids),
        }
    finally:
        App.closeDocument(doc.Name)


def _write_part(item: dict[str, object], output: Path) -> dict[str, object]:
    product_id = str(item["id"])
    spec = geometry_specs()[product_id]
    doc = App.newDocument(safe_name(product_id))
    doc.Label = f"{product_id} — {item['title']}"
    root = doc.addObject("App::DocumentObjectGroup", "PartGeometry")
    root.Label = "Controlled part geometry"
    meta = _metadata(doc, object_id=product_id, title=str(item["title"]), definition_type="product-item")
    root.addObject(meta)
    _property(meta, "App::PropertyString", "Form", spec.form)
    _property(meta, "App::PropertyVector", "ControlledEnvelopeMm", App.Vector(*spec.envelope_mm))
    _property(meta, "App::PropertyString", "Representation", spec.representation)
    primitive_count = _add_product_geometry(doc, root, item, (0.0, 0.0, 0.0), "part-origin")
    _save(doc, output)
    report = {
        "id": product_id,
        "file": _report_path(output),
        "sha256": _sha256(output),
        "size_bytes": output.stat().st_size,
        "primitive_count": primitive_count,
        "envelope_mm": list(spec.envelope_mm),
    }
    report.update(
        _validate_saved_document(output, {product_id}, set(), primitive_count)
    )
    return report


def _graph(manifest: dict[str, object]) -> tuple[dict[str, dict[str, object]], dict[str, dict[str, object]]]:
    products = {str(item["id"]): item for item in manifest["product_items"]}
    assemblies = {str(item["id"]): item for item in manifest["assemblies"]}
    known = set(products) | set(assemblies)
    referenced: set[str] = set()
    for assembly in assemblies.values():
        children = [str(child) for child in assembly["children"]]
        missing = set(children) - known
        if missing:
            raise ValueError(f"{assembly['id']} references missing children {sorted(missing)}")
        referenced.update(children)
    roots = set(assemblies) - referenced
    if "LM3-TRAINSET-A000" not in roots:
        raise ValueError(f"trainset final assembly is not a graph root: {sorted(roots)}")
    return products, assemblies


def _descendant_products(assembly_id: str, products: dict[str, dict[str, object]], assemblies: dict[str, dict[str, object]]) -> list[str]:
    result: list[str] = []
    visiting: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in products:
            if node_id not in result:
                result.append(node_id)
            return
        if node_id in visiting:
            raise ValueError(f"cycle in assembly graph at {node_id}")
        visiting.add(node_id)
        for child_id in assemblies[node_id]["children"]:
            visit(str(child_id))
        visiting.remove(node_id)

    visit(assembly_id)
    return result


def _descendant_assemblies(
    assembly_id: str,
    assemblies: dict[str, dict[str, object]],
) -> list[str]:
    result: list[str] = []
    visiting: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in visiting:
            raise ValueError(f"cycle in assembly graph at {node_id}")
        visiting.add(node_id)
        if node_id not in result:
            result.append(node_id)
        for child_id in assemblies[node_id]["children"]:
            child = str(child_id)
            if child in assemblies:
                visit(child)
        visiting.remove(node_id)

    visit(assembly_id)
    return result


def _inspection_layout(product_ids: list[str], products: dict[str, dict[str, object]]) -> dict[str, tuple[float, float, float]]:
    specs = geometry_specs()
    maximum_x = max(specs[product_id].envelope_mm[0] for product_id in product_ids)
    maximum_y = max(specs[product_id].envelope_mm[1] for product_id in product_ids)
    columns = min(4, max(1, len(product_ids)))
    x_pitch = maximum_x + 800.0
    y_pitch = maximum_y + 800.0
    del products
    return {
        product_id: ((index % columns) * x_pitch, (index // columns) * y_pitch, 0.0)
        for index, product_id in enumerate(product_ids)
    }


def _write_assembly(
    assembly: dict[str, object],
    products: dict[str, dict[str, object]],
    assemblies: dict[str, dict[str, object]],
    output: Path,
) -> dict[str, object]:
    assembly_id = str(assembly["id"])
    descendants = _descendant_products(assembly_id, products, assemblies)
    assembly_nodes = _descendant_assemblies(assembly_id, assemblies)
    positions = _inspection_layout(descendants, products)
    doc = App.newDocument(safe_name(assembly_id))
    doc.Label = f"{assembly_id} — {assembly['title']}"
    root = doc.addObject("App::DocumentObjectGroup", "AssemblyGeometry")
    root.Label = "Complete descendant part geometry on deterministic assembly-inspection fixture"
    meta = _metadata(doc, object_id=assembly_id, title=str(assembly["title"]), definition_type="assembly-node")
    root.addObject(meta)
    _property(meta, "App::PropertyString", "Layer", str(assembly["layer"]))
    _property(meta, "App::PropertyString", "BuildCell", str(assembly["build_cell"]))
    _property(meta, "App::PropertyStringList", "DirectChildren", [str(value) for value in assembly["children"]])
    _property(meta, "App::PropertyStringList", "HoldPoints", [str(value) for value in assembly["hold_points"]])
    _property(meta, "App::PropertyString", "RepresentationState", "complete hierarchy / inspection-fixture layout")
    _property(meta, "App::PropertyInteger", "DescendantProductCount", len(descendants))

    hierarchy = doc.addObject("App::DocumentObjectGroup", "AssemblyHierarchy")
    hierarchy.Label = "Controlled assembly nodes"
    root.addObject(hierarchy)
    for node_id in assembly_nodes:
        node = doc.addObject("App::FeaturePython", safe_name(f"AssemblyNode_{node_id}"))
        node.Label = f"{node_id} — {assemblies[node_id]['title']}"
        _property(node, "App::PropertyString", "OSRAssemblyId", node_id)
        _property(node, "App::PropertyString", "Layer", str(assemblies[node_id]["layer"]))
        _property(node, "App::PropertyString", "BuildCell", str(assemblies[node_id]["build_cell"]))
        _property(node, "App::PropertyStringList", "DirectChildren", [str(value) for value in assemblies[node_id]["children"]])
        _property(node, "App::PropertyStringList", "HoldPoints", [str(value) for value in assemblies[node_id]["hold_points"]])
        hierarchy.addObject(node)

    primitive_count = 0
    for product_id in descendants:
        group = doc.addObject("App::DocumentObjectGroup", safe_name(f"Child_{product_id}"))
        group.Label = f"{product_id} — {products[product_id]['title']}"
        root.addObject(group)
        primitive_count += _add_product_geometry(
            doc,
            group,
            products[product_id],
            positions[product_id],
            "assembly-inspection-fixture",
        )
    _save(doc, output)
    report = {
        "id": assembly_id,
        "file": _report_path(output),
        "sha256": _sha256(output),
        "size_bytes": output.stat().st_size,
        "direct_children": [str(value) for value in assembly["children"]],
        "descendant_product_ids": descendants,
        "descendant_product_count": len(descendants),
        "assembly_node_ids": assembly_nodes,
        "assembly_node_count": len(assembly_nodes),
        "primitive_count": primitive_count,
        "representation_state": "complete hierarchy / inspection-fixture layout",
    }
    report.update(
        _validate_saved_document(
            output,
            set(descendants),
            set(assembly_nodes),
            primitive_count,
        )
    )
    return report


def _atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def build_library(output_root: Path) -> dict[str, object]:
    _require_freecad()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    products, assemblies = _graph(manifest)
    if set(products) != set(geometry_specs()):
        raise ValueError("product geometry registry does not exactly cover the current manifest")
    parts_dir = output_root / "lm3-parts"
    assemblies_dir = output_root / "lm3-assemblies"
    part_entries = [
        _write_part(products[product_id], parts_dir / f"{product_id}.FCStd")
        for product_id in sorted(products)
    ]
    assembly_entries = [
        _write_assembly(assemblies[assembly_id], products, assemblies, assemblies_dir / f"{assembly_id}.FCStd")
        for assembly_id in sorted(assemblies)
    ]
    expected_part_files = {f"{product_id}.FCStd" for product_id in products}
    expected_assembly_files = {f"{assembly_id}.FCStd" for assembly_id in assemblies}
    for directory, expected in ((parts_dir, expected_part_files), (assemblies_dir, expected_assembly_files)):
        unexpected = {path.name for path in directory.glob("*.FCStd")} - expected
        if unexpected:
            raise RuntimeError(f"stale FreeCAD product-library files in {directory}: {sorted(unexpected)}")
    report = {
        "schema": "org.opensourcerail.freecad-product-library.v1",
        "status": "design-reference-not-released",
        "release_boundary": RELEASE_BOUNDARY,
        "manifest": str(MANIFEST.relative_to(REPO_ROOT)),
        "manifest_sha256": _sha256(MANIFEST),
        "product_count": len(part_entries),
        "assembly_count": len(assembly_entries),
        "root_assembly": "LM3-TRAINSET-A000",
        "all_active_products_reach_root": set(
            _descendant_products("LM3-TRAINSET-A000", products, assemblies)
        ).issuperset(
            product_id
            for product_id, item in products.items()
            if int(item["quantity_per_trainset"]) > 0
        ),
        "optional_assembly_roots": sorted(
            set(assemblies)
            - {str(child) for assembly in assemblies.values() for child in assembly["children"]}
            - {"LM3-TRAINSET-A000"}
        ),
        "parts": part_entries,
        "assemblies": assembly_entries,
    }
    report["passed"] = bool(
        report["product_count"] == 120
        and report["assembly_count"] == 26
        and report["all_active_products_reach_root"]
        and all(
            entry["primitive_count"] > 0 and entry["reopen_validated"]
            for entry in [*part_entries, *assembly_entries]
        )
    )
    _atomic_json(output_root / "lm3-product-library.index.json", report)
    print(f"wrote {len(part_entries)} FreeCAD part documents and {len(assembly_entries)} assembly documents")
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(argv)


def _normalise_freecad_argv(argv: list[str]) -> list[str]:
    args = list(argv)
    if args and Path(args[0]).name == "freecad_product_library.py":
        args = args[1:]
    if args and args[0] == "--pass":
        args = args[1:]
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(_normalise_freecad_argv(argv or []))
    report = build_library(args.output_root.resolve())
    return 0 if report["passed"] else 1


def _running_as_freecad_script() -> bool:
    return bool(sys.argv[1:2]) and Path(sys.argv[1]).name == "freecad_product_library.py"


if __name__ == "__main__" or _running_as_freecad_script():
    raise SystemExit(main(sys.argv[1:]))
