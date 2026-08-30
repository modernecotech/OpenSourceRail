"""Export generated FreeCAD review documents to meshes for external rendering."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys

try:
    import FreeCAD as App  # type: ignore[import-not-found]
    import Mesh  # type: ignore[import-not-found]
    import MeshPart  # type: ignore[import-not-found]
except Exception as exc:  # pragma: no cover - only exercised outside FreeCAD.
    App = None  # type: ignore[assignment]
    Mesh = None  # type: ignore[assignment]
    MeshPart = None  # type: ignore[assignment]
    _FREECAD_IMPORT_ERROR = exc
else:
    _FREECAD_IMPORT_ERROR = None


@dataclass(frozen=True)
class MeshExport:
    doc: str
    output: str
    linear_deflection_mm: float = 45.0
    angular_deflection_rad: float = 0.45


EXPORTS: tuple[MeshExport, ...] = (
    MeshExport("trainset-light-metro-3car.FCStd", "trainset-light-metro-3car.stl", 60.0, 0.45),
    MeshExport("full-body-assembly-states.FCStd", "full-body-assembly-states.stl", 45.0, 0.4),
    MeshExport("chassis-bogie-assembly-states.FCStd", "chassis-bogie-assembly-states.stl", 35.0, 0.35),
)


def _require_freecad() -> None:
    if App is None or Mesh is None or MeshPart is None:
        raise SystemExit(
            "FreeCAD mesh modules are not importable. Run this with FreeCADCmd "
            "or design/component-catalogue/scripts/freecad_mesh_exports.sh.\n"
            f"Import error was: {_FREECAD_IMPORT_ERROR!r}"
        )


def _catalog_freecad_root() -> Path:
    return Path(__file__).resolve().parents[2] / "models" / "cad"


def _mesh_root() -> Path:
    return Path(__file__).resolve().parents[2] / "catalog" / "render-meshes"


def _has_shape(obj) -> bool:
    shape = getattr(obj, "Shape", None)
    if shape is None:
        return False
    try:
        return not shape.isNull()
    except Exception:
        return False


def _export_one(*, catalog_dir: Path, out_dir: Path, export: MeshExport) -> None:
    doc_path = catalog_dir / export.doc
    if not doc_path.exists():
        raise FileNotFoundError(f"missing FreeCAD document: {doc_path}")
    print(f"opening {doc_path}", flush=True)
    doc = App.openDocument(str(doc_path))
    combined = Mesh.Mesh()
    shape_count = 0
    for obj in doc.Objects:
        if not _has_shape(obj):
            continue
        mesh = MeshPart.meshFromShape(
            Shape=obj.Shape,
            LinearDeflection=export.linear_deflection_mm,
            AngularDeflection=export.angular_deflection_rad,
            Relative=False,
        )
        if getattr(mesh, "CountFacets", 0) <= 0:
            continue
        combined.addMesh(mesh)
        shape_count += 1
    if shape_count == 0:
        raise RuntimeError(f"no exportable shapes in {doc_path}")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / export.output
    combined.write(str(out_path))
    print(f"wrote {out_path} from {shape_count} shapes ({out_path.stat().st_size // 1024} KB)", flush=True)
    App.closeDocument(doc.Name)


def export_all(*, catalog_dir: Path, out_dir: Path) -> None:
    _require_freecad()
    out_dir.mkdir(parents=True, exist_ok=True)
    for path in out_dir.glob("*.stl"):
        path.unlink()
        print(f"removed old render mesh {path}", flush=True)
    for export in EXPORTS:
        _export_one(catalog_dir=catalog_dir, out_dir=out_dir, export=export)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export FreeCAD review documents to STL render meshes.")
    parser.add_argument("--catalog-dir", type=Path, default=_catalog_freecad_root())
    parser.add_argument("--out-dir", type=Path, default=_mesh_root())
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    export_all(catalog_dir=args.catalog_dir, out_dir=args.out_dir)


if __name__ == "__main__":
    main(sys.argv[1:])
