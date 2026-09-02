"""Generate native FreeCAD coordination assemblies for all station variants."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from osr_mech.cad import to_freecad_shape
from osr_mech.freecad_assembly_review import _canonicalise_fcstd
from osr_mech.freecad_occ_bridge import safe_name
from osr_mech.station.product_geometry import (
    PLATFORM_SURFACE_Z_MM,
    TOP_OF_RAIL_Z_MM,
    flatten_geometry,
    geometry_specs,
    station_product_geometry,
)

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

# Millimetre offsets used only by the second, hidden review state.  They are
# deliberately large enough to separate station work packages without changing
# the installed-coordinate geometry that remains the design authority.
EXPLODED_OFFSETS_MM: dict[str, tuple[float, float, float]] = {
    "STN-CIV-SA100": (0.0, -18_000.0, -3_000.0),
    "STN-PLT-SA200": (0.0, -10_000.0, 0.0),
    "STN-CNP-SA300": (0.0, 0.0, 9_000.0),
    "STN-MEP-SA400": (-18_000.0, 14_000.0, 2_000.0),
    "STN-PAX-SA500": (0.0, 18_000.0, 3_000.0),
    "STN-ACC-SA600": (-24_000.0, 0.0, 4_000.0),
    "STN-CHG-SA700": (18_000.0, 14_000.0, 2_000.0),
    "STN-TRK-SA800": (24_000.0, -12_000.0, 1_000.0),
    "STN-DEP-SA850": (35_000.0, 18_000.0, 4_000.0),
}

CONTROLLED_DATUMS = (
    ("DATUM-TRACK-CL", "track centreline", "x-axis at the station alignment origin"),
    ("DATUM-TOR", "top of rail", "local rail-head plane before deployment survey placement"),
    ("DATUM-PLATFORM-FACE", "platform face", "platform-side edge derived from the configured centre"),
    ("DATUM-BOARDING", "boarding level", "350 mm above local top of rail; survey/release required"),
    ("ZONE-TRAIN-KINEMATIC", "train kinematic envelope", "coordination zone; verified swept path remains deployment-specific"),
    ("ZONE-EDGE-SAFETY", "platform-edge safety zone", "coping, tactile, warning and edge-equipment interface"),
    ("ZONE-LIFTING", "installation/lifting zone", "temporary crane and exclusion zone; lift plan required"),
    ("ZONE-MAINTENANCE", "maintainability zone", "equipment access volumes encoded in product geometry"),
    ("INTERFACE-TRACK", "track interface", "alignment, top-of-rail and drainage handoff"),
    ("INTERFACE-TRAIN", "train interface", "vehicle swept-path and boarding-gap handoff"),
    ("INTERFACE-PSD", "optional platform screen-door interface", "reserved edge fixing/power/control handoff; PSD not in LM3 baseline"),
    ("INTERFACE-EDGE-PROTECTION", "edge-protection interface", "temporary and permanent barrier handoff outside the boarding opening"),
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


def _translated(shape, offset: tuple[float, float, float]):
    copied = shape.copy()
    copied.translate(App.Vector(*offset))
    return copied


def _datum_rows(variant: dict[str, object]) -> list[dict[str, object]]:
    """Return coordinate-bearing datum/interface definitions for one variant."""

    length = float(variant["parameters"]["platform_length_m"]) * 1000.0
    count = int(variant["parameters"]["platform_count"])
    stacked = variant["parameters"].get("platform_layout") == "stacked"
    if count == 1:
        platform_centres = [(5_000.0, 0.0)]
    elif count == 2:
        platform_centres = [(-5_000.0, 0.0), (5_000.0, 0.0)]
    elif stacked:
        platform_centres = [(-5_000.0, 9_000.0), (5_000.0, 9_000.0), (-5_000.0, 17_000.0), (5_000.0, 17_000.0)]
    else:
        platform_centres = [(-11_000.0, 0.0), (-5_000.0, 0.0), (5_000.0, 0.0), (11_000.0, 0.0)]
    interfaces = [
        {
            "platform_face_y_mm": y - (1_500.0 if y > 0 else -1_500.0),
            "track_centre_y_mm": y - (3_000.0 if y > 0 else -3_000.0),
            "top_of_rail_z_mm": level + TOP_OF_RAIL_Z_MM,
            "boarding_z_mm": level + PLATFORM_SURFACE_Z_MM,
            "static_vehicle_to_platform_gap_mm": 75.0,
            "dynamic_envelope_review_margin_mm": 15.0,
        }
        for y, level in platform_centres
    ]
    track_min_y = min(row["track_centre_y_mm"] - 1_485.0 for row in interfaces)
    track_max_y = max(row["track_centre_y_mm"] + 1_485.0 for row in interfaces)
    min_tor = min(row["top_of_rail_z_mm"] for row in interfaces)
    max_tor = max(row["top_of_rail_z_mm"] for row in interfaces)
    coordinate_map: dict[str, dict[str, object]] = {
        "DATUM-TRACK-CL": {"axis": "x", "origin_mm": [0.0, 0.0, 0.0]},
        "DATUM-TOR": {"interfaces": interfaces},
        "DATUM-PLATFORM-FACE": {"interfaces": interfaces},
        "DATUM-BOARDING": {"interfaces": interfaces},
        "ZONE-TRAIN-KINEMATIC": {"bounds_mm": [-length / 2, track_min_y, min_tor, length / 2, track_max_y, max_tor + 4500.0]},
        "ZONE-EDGE-SAFETY": {"bounds_mm": [-length / 2, -14500.0, 0.0, length / 2, 14500.0, 1400.0]},
        "ZONE-LIFTING": {"bounds_mm": [-length / 2 - 5000.0, -18000.0, 0.0, length / 2 + 5000.0, 18000.0, 12000.0]},
        "ZONE-MAINTENANCE": {"bounds_mm": [-length / 2, -15000.0, 0.0, length / 2, 15000.0, 6500.0]},
        "INTERFACE-TRACK": {"datum_ids": ["DATUM-TRACK-CL", "DATUM-TOR"]},
        "INTERFACE-TRAIN": {"datum_ids": ["DATUM-TOR", "DATUM-BOARDING", "ZONE-TRAIN-KINEMATIC"]},
        "INTERFACE-PSD": {"datum_ids": ["DATUM-PLATFORM-FACE", "DATUM-BOARDING"]},
        "INTERFACE-EDGE-PROTECTION": {"datum_ids": ["DATUM-PLATFORM-FACE", "ZONE-EDGE-SAFETY"]},
    }
    return [
        {"id": datum_id, "title": title, "definition": definition, **coordinate_map[datum_id]}
        for datum_id, title, definition in CONTROLLED_DATUMS
    ]


def _review_sidecar(
    variant: dict[str, object],
    output: Path,
    primitive_count: int,
) -> Path:
    archetype = str(variant["archetype"])
    product_rows = [
        {
            "product_id": str(item["id"]),
            "parent_assembly": str(item["parent"]),
            "installed_offset_mm": [0.0, 0.0, 0.0],
            "exploded_offset_mm": list(EXPLODED_OFFSETS_MM.get(str(item["parent"]), (0.0, 0.0, 0.0))),
        }
        for item in variant["product_items"]
    ]
    payload = {
        "schema": "org.opensourcerail.station-assembly-review.v1",
        "archetype": archetype,
        "status": "design-reference-not-released",
        "release_boundary": RELEASE_BOUNDARY,
        "manifest": str(MANIFEST.relative_to(REPO_ROOT)),
        "manifest_sha256": _sha256(MANIFEST),
        "freecad_file": str(output.relative_to(REPO_ROOT)),
        "assembly_ids": [str(row["id"]) for row in variant["assemblies"]],
        "product_ids": [row["product_id"] for row in product_rows],
        "datums_and_zones": _datum_rows(variant),
        "states": [
            {"id": "installed", "default_visible": True, "primitive_count": primitive_count},
            {"id": "exploded", "default_visible": False, "primitive_count": primitive_count},
        ],
        "products": product_rows,
    }
    sidecar = output.with_suffix(".assembly-review.json")
    sidecar.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return sidecar


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

    datums = doc.addObject("App::DocumentObjectGroup", "ControlledDatumsAndZones")
    datums.Label = "Controlled datums, interfaces, and review zones"
    root.addObject(datums)
    for row in _datum_rows(variant):
        datum_id = str(row["id"])
        title = str(row["title"])
        node = doc.addObject("App::FeaturePython", safe_name(datum_id))
        node.Label = f"{datum_id} — {title}"
        _property(node, "App::PropertyString", "OSRDatumId", datum_id)
        _property(node, "App::PropertyString", "Definition", str(row["definition"]))
        _property(node, "App::PropertyString", "CoordinateDefinition", json.dumps(row, sort_keys=True))
        datums.addObject(node)

    states = doc.addObject("App::DocumentObjectGroup", "ConfigurationStates")
    states.Label = "Installed and exploded review states"
    root.addObject(states)
    installed_state = doc.addObject("App::DocumentObjectGroup", "InstalledState")
    installed_state.Label = "INSTALLED — authoritative coordination coordinates"
    states.addObject(installed_state)
    exploded_state = doc.addObject("App::DocumentObjectGroup", "ExplodedState")
    exploded_state.Label = "EXPLODED — work-package inspection layout"
    states.addObject(exploded_state)

    specs = geometry_specs()
    primitive_count = 0
    product_ids: list[str] = []
    for item in variant["product_items"]:
        product_id = str(item["id"])
        product_ids.append(product_id)
        group = doc.addObject("App::DocumentObjectGroup", safe_name(f"Installed_{product_id}"))
        group.Label = f"INSTALLED · {product_id} — {item['title']}"
        installed_state.addObject(group)
        exploded_group = doc.addObject("App::DocumentObjectGroup", safe_name(f"Exploded_{product_id}"))
        exploded_group.Label = f"EXPLODED · {product_id} — {item['title']}"
        exploded_state.addObject(exploded_group)
        offset = EXPLODED_OFFSETS_MM.get(str(item["parent"]), (0.0, 0.0, 0.0))
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
            _property(obj, "App::PropertyString", "AssemblyState", "installed")
            _property(obj, "App::PropertyVector", "ReviewOffsetMm", App.Vector(0.0, 0.0, 0.0))
            group.addObject(obj)

            exploded = doc.addObject("Part::Feature", safe_name(f"Exploded_{product_id}_{index:03d}"))
            exploded.Label = f"EXPLODED · {product_id} · {leaf.label or item['title']}"
            exploded.Shape = _translated(shape, offset)
            if leaf.color is not None and getattr(exploded, "ViewObject", None) is not None:
                exploded.ViewObject.ShapeColor = (leaf.color.r, leaf.color.g, leaf.color.b)
                exploded.ViewObject.Transparency = max(0, min(100, round((1.0 - leaf.color.a) * 100)))
            _property(exploded, "App::PropertyString", "OSRId", product_id)
            _property(exploded, "App::PropertyString", "PrimitiveId", f"{product_id}-{index:03d}")
            _property(exploded, "App::PropertyString", "ParentAssembly", str(item["parent"]))
            _property(exploded, "App::PropertyString", "Route", str(item["route"]))
            _property(exploded, "App::PropertyString", "Maturity", str(item["maturity"]))
            _property(exploded, "App::PropertyString", "GeometryLevel", specs[product_id].geometry_level)
            _property(exploded, "App::PropertyString", "IFCClass", specs[product_id].ifc_class)
            _property(exploded, "App::PropertyString", "AssemblyState", "exploded")
            _property(exploded, "App::PropertyVector", "ReviewOffsetMm", App.Vector(*offset))
            exploded_group.addObject(exploded)
            primitive_count += 1
    if getattr(installed_state, "ViewObject", None) is not None:
        installed_state.ViewObject.Visibility = True
    if getattr(exploded_state, "ViewObject", None) is not None:
        exploded_state.ViewObject.Visibility = False
    _save(doc, output)

    sidecar = _review_sidecar(variant, output, primitive_count)

    reopened = App.openDocument(str(output))
    try:
        shapes = [obj for obj in reopened.Objects if obj.TypeId == "Part::Feature"]
        found = {str(obj.OSRId) for obj in shapes if hasattr(obj, "OSRId")}
        states_found = {str(obj.AssemblyState) for obj in shapes if hasattr(obj, "AssemblyState")}
        invalid = [obj.Name for obj in shapes if obj.Shape.isNull() or not obj.Shape.isValid() or obj.Shape.Volume <= 0]
        if found != set(product_ids) or len(shapes) != primitive_count * 2 or states_found != {"installed", "exploded"} or invalid:
            raise RuntimeError(
                f"station FreeCAD round-trip failed for {archetype}: "
                f"missing={sorted(set(product_ids) - found)}, shapes={len(shapes)}/{primitive_count * 2}, "
                f"states={sorted(states_found)}, invalid={invalid}"
            )
    finally:
        App.closeDocument(reopened.Name)
    return {
        "archetype": archetype,
        "file": str(output.relative_to(REPO_ROOT)),
        "sha256": _sha256(output),
        "size_bytes": output.stat().st_size,
        "product_count": len(product_ids),
        "product_ids": product_ids,
        "assembly_count": len(variant["assemblies"]),
        "assembly_ids": [str(row["id"]) for row in variant["assemblies"]],
        "primitive_count": primitive_count,
        "native_shape_count": primitive_count * 2,
        "configuration_states": ["installed", "exploded"],
        "assembly_review": str(sidecar.relative_to(REPO_ROOT)),
        "assembly_review_sha256": _sha256(sidecar),
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
