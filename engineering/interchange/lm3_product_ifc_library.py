#!/usr/bin/env python3
"""Generate deterministic IFC4.3 files for every LM3 part and assembly."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from collections import defaultdict
from importlib.metadata import version
from pathlib import Path
from typing import Any

import ifcopenshell
from ifcopenshell.api.aggregate import assign_object
from ifcopenshell.api.context import add_context
from ifcopenshell.api.spatial import assign_container
from ifcopenshell.api.unit import assign_unit

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from engineering.interchange.trainset_manufacturing_ifc import (
    REPO_ROOT,
    add_product_geometry,
    entity,
    gid,
    product_ifc_class,
    property_set,
    set_local_placement,
)


MANIFEST = REPO_ROOT / "design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.json"
DEFAULT_ROOT = REPO_ROOT / "engineering/models/bim/reference"
FIXED_TIMESTAMP = "2026-08-30T00:00:00+00:00"
RELEASE_BOUNDARY = (
    "Design-reference geometry and assembly hierarchy only; supplier freeze, "
    "released drawings/tolerances, calculations, qualified processes and "
    "first-article tests remain mandatory."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def report_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return path.name


def graph(manifest: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    products = {str(item["id"]): item for item in manifest["product_items"]}
    assemblies = {str(item["id"]): item for item in manifest["assemblies"]}
    known = set(products) | set(assemblies)
    for assembly_id, assembly in assemblies.items():
        missing = {str(child) for child in assembly["children"]} - known
        if missing:
            raise ValueError(f"{assembly_id} references missing children {sorted(missing)}")
    if "LM3-TRAINSET-A000" not in assemblies:
        raise ValueError("LM3 final trainset assembly is missing")
    return products, assemblies


def descendants(
    assembly_id: str,
    products: dict[str, dict[str, Any]],
    assemblies: dict[str, dict[str, Any]],
) -> tuple[list[str], list[str]]:
    product_ids: list[str] = []
    assembly_ids: list[str] = []
    visiting: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in products:
            if node_id not in product_ids:
                product_ids.append(node_id)
            return
        if node_id in visiting:
            raise ValueError(f"cycle in assembly graph at {node_id}")
        visiting.add(node_id)
        if node_id not in assembly_ids:
            assembly_ids.append(node_id)
        for child in assemblies[node_id]["children"]:
            visit(str(child))
        visiting.remove(node_id)

    visit(assembly_id)
    return product_ids, assembly_ids


def base_model(file_name: str, title: str) -> tuple[ifcopenshell.file, Any, Any]:
    model = ifcopenshell.file(schema="IFC4X3")
    model.header.file_name.name = file_name
    model.header.file_name.time_stamp = FIXED_TIMESTAMP
    model.header.file_name.author = ("OpenSourceRail",)
    model.header.file_name.organization = ("OpenSourceRail",)
    model.header.file_name.preprocessor_version = f"IfcOpenShell {version('ifcopenshell')}"
    model.header.file_name.originating_system = "OpenSourceRail deterministic LM3 product-library exporter"
    model.header.file_name.authorization = "design-reference / not for construction"
    project = entity(model, "IfcProject", f"library:{file_name}:project", Name=title, Description=RELEASE_BOUNDARY)
    site = entity(model, "IfcSite", f"library:{file_name}:site", Name="LM3 product library", CompositionType="ELEMENT")
    facility = entity(model, "IfcBuilding", f"library:{file_name}:facility", Name="LM3 assembly inspection fixture", CompositionType="ELEMENT")
    assign_unit(model, length={"is_metric": True, "raw": "METERS"})
    context = add_context(model, context_type="Model")
    body = add_context(
        model,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=context,
    )
    assign_object(model, products=[site], relating_object=project)
    assign_object(model, products=[facility], relating_object=site)
    set_local_placement(model, site, (0.0, 0.0, 0.0))
    set_local_placement(model, facility, (0.0, 0.0, 0.0))
    property_set(
        model,
        project,
        "OSR_ProductLibrary",
        {
            "Status": "design-reference-not-released",
            "ReleaseBoundary": RELEASE_BOUNDARY,
            "Manifest": str(MANIFEST.relative_to(REPO_ROOT)),
            "ManifestSha256": sha256(MANIFEST),
        },
    )
    return model, body, facility


def canonicalise(model: ifcopenshell.file, file_key: str) -> None:
    counters: dict[str, int] = defaultdict(int)
    for root in model.by_type("IfcRoot"):
        ifc_class = root.is_a()
        counters[ifc_class] += 1
        root.GlobalId = gid(f"product-library:{file_key}:{ifc_class}:{counters[ifc_class]:05d}")

    def key(value: Any) -> tuple[str, str, str, str, int]:
        return (
            str(getattr(value, "Tag", "") or ""),
            str(getattr(value, "Identification", "") or ""),
            str(getattr(value, "Name", "") or ""),
            str(getattr(value, "GlobalId", "") or ""),
            value.id(),
        )

    for ifc_class, attribute in (
        ("IfcUnitAssignment", "Units"),
        ("IfcRelAggregates", "RelatedObjects"),
        ("IfcRelContainedInSpatialStructure", "RelatedElements"),
        ("IfcRelDefinesByProperties", "RelatedObjects"),
    ):
        for relationship in model.by_type(ifc_class):
            values = getattr(relationship, attribute, None)
            if values:
                setattr(relationship, attribute, tuple(sorted(values, key=key)))


def product_entity(model: ifcopenshell.file, item: dict[str, Any]) -> Any:
    from osr_mech.rolling_stock.product_geometry import geometry_level

    product = entity(
        model,
        product_ifc_class(item),
        f"library-product:{item['id']}",
        Name=str(item["title"]),
        Description=str(item["make_or_buy_basis"]),
        Tag=str(item["id"]),
    )
    property_set(
        model,
        product,
        "OSR_ProductDefinition",
        {
            "OSRId": item["id"],
            "Parent": item["parent"],
            "Route": item["route"],
            "Maturity": item["maturity"],
            "QuantityPerTrainset": item["quantity_per_trainset"],
            "Unit": item["unit"],
            "GeometryStatus": "design-reference-not-released",
            "GeometryLevel": geometry_level(str(item["id"]), str(item["route"]), str(item["maturity"])),
        },
    )
    return product


def assembly_entity(model: ifcopenshell.file, assembly: dict[str, Any]) -> Any:
    ifc_class = "IfcVehicle" if assembly["layer"] == "trainset" else "IfcElementAssembly"
    result = entity(
        model,
        ifc_class,
        f"library-assembly:{assembly['id']}",
        Name=str(assembly["title"]),
        Description=" | ".join(str(value) for value in assembly["hold_points"]),
        Tag=str(assembly["id"]),
    )
    property_set(
        model,
        result,
        "OSR_AssemblyDefinition",
        {
            "OSRId": assembly["id"],
            "Layer": assembly["layer"],
            "BuildCell": assembly["build_cell"],
            "QuantityPerTrainset": assembly["quantity_per_trainset"],
            "GeometryStatus": "complete-hierarchy-inspection-layout",
        },
    )
    return result


def write_model(model: ifcopenshell.file, output: Path, required_tags: set[str]) -> dict[str, Any]:
    output.parent.mkdir(parents=True, exist_ok=True)
    canonicalise(model, output.stem)
    temporary = output.with_suffix(output.suffix + ".tmp")
    model.write(str(temporary))
    os.replace(temporary, output)
    reopened = ifcopenshell.open(str(output))
    present_tags = {
        str(value.Tag)
        for value in reopened.by_type("IfcProduct")
        if getattr(value, "Tag", None)
    }
    missing = sorted(required_tags - present_tags)
    represented = {
        str(value.Tag)
        for value in reopened.by_type("IfcProduct")
        if getattr(value, "Tag", None) and getattr(value, "Representation", None)
    }
    return {
        "file": report_path(output),
        "sha256": sha256(output),
        "size_bytes": output.stat().st_size,
        "missing_tags": missing,
        "represented_product_tags": sorted(represented & required_tags),
        "passed": not missing,
    }


def export_part(item: dict[str, Any], output: Path) -> dict[str, Any]:
    model, body, facility = base_model(output.name, f"{item['id']} — {item['title']}")
    product = product_entity(model, item)
    primitive_count = add_product_geometry(model, body, product, item)
    assign_container(model, products=[product], relating_structure=facility)
    set_local_placement(model, product, (0.0, 0.0, 0.0))
    report = write_model(model, output, {str(item["id"])})
    report.update({"id": item["id"], "primitive_count": primitive_count, "definition_type": "product-item"})
    report["passed"] = bool(report["passed"] and report["represented_product_tags"] == [item["id"]])
    return report


def export_assembly(
    assembly_id: str,
    products: dict[str, dict[str, Any]],
    assemblies: dict[str, dict[str, Any]],
    output: Path,
) -> dict[str, Any]:
    product_ids, assembly_ids = descendants(assembly_id, products, assemblies)
    model, body, facility = base_model(output.name, f"{assembly_id} — {assemblies[assembly_id]['title']}")
    entities: dict[str, Any] = {}
    for child_assembly_id in assembly_ids:
        entities[child_assembly_id] = assembly_entity(model, assemblies[child_assembly_id])
    maximum_x = max(float(geometry_envelope(products[product_id])[0]) for product_id in product_ids)
    maximum_y = max(float(geometry_envelope(products[product_id])[1]) for product_id in product_ids)
    columns = min(4, max(1, len(product_ids)))
    primitive_count = 0
    positions: dict[str, tuple[float, float, float]] = {}
    for index, product_id in enumerate(product_ids):
        item = products[product_id]
        product = product_entity(model, item)
        entities[product_id] = product
        position = (
            float((index % columns) * (maximum_x + 800.0) / 1000.0),
            float((index // columns) * (maximum_y + 800.0) / 1000.0),
            0.0,
        )
        positions[product_id] = position
        primitive_count += add_product_geometry(model, body, product, item)
    included = set(entities)
    for child_assembly_id in assembly_ids:
        direct_children = [str(child) for child in assemblies[child_assembly_id]["children"] if str(child) in included]
        assign_object(
            model,
            products=[entities[child] for child in direct_children],
            relating_object=entities[child_assembly_id],
        )
    assign_container(model, products=[entities[assembly_id]], relating_structure=facility)
    for product_id in product_ids:
        set_local_placement(model, entities[product_id], positions[product_id])
    required = set(product_ids) | set(assembly_ids)
    report = write_model(model, output, required)
    report.update(
        {
            "id": assembly_id,
            "definition_type": "assembly-node",
            "assembly_node_count": len(assembly_ids),
            "descendant_product_count": len(product_ids),
            "descendant_product_ids": product_ids,
            "primitive_count": primitive_count,
            "representation_state": "complete hierarchy / inspection-fixture layout",
        }
    )
    report["passed"] = bool(
        report["passed"] and set(report["represented_product_tags"]) == set(product_ids)
    )
    return report


def geometry_envelope(item: dict[str, Any]) -> tuple[float, float, float]:
    from osr_mech.rolling_stock.product_geometry import geometry_specs

    return geometry_specs()[str(item["id"])].envelope_mm


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def build_library(output_root: Path) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    products, assemblies = graph(manifest)
    parts_dir = output_root / "lm3-parts"
    assemblies_dir = output_root / "lm3-assemblies"
    part_reports = [
        export_part(products[product_id], parts_dir / f"{product_id}.ifc")
        for product_id in sorted(products)
    ]
    assembly_reports = [
        export_assembly(assembly_id, products, assemblies, assemblies_dir / f"{assembly_id}.ifc")
        for assembly_id in sorted(assemblies)
    ]
    expected_parts = {f"{product_id}.ifc" for product_id in products}
    expected_assemblies = {f"{assembly_id}.ifc" for assembly_id in assemblies}
    for directory, expected in ((parts_dir, expected_parts), (assemblies_dir, expected_assemblies)):
        stale = {path.name for path in directory.glob("*.ifc")} - expected
        if stale:
            raise RuntimeError(f"stale IFC product-library files in {directory}: {sorted(stale)}")
    active_ids = {
        product_id
        for product_id, item in products.items()
        if int(item["quantity_per_trainset"]) > 0
    }
    root_product_ids = set(descendants("LM3-TRAINSET-A000", products, assemblies)[0])
    report = {
        "schema": "org.opensourcerail.lm3-ifc-product-library.v1",
        "status": "design-reference-not-released",
        "release_boundary": RELEASE_BOUNDARY,
        "manifest": str(MANIFEST.relative_to(REPO_ROOT)),
        "manifest_sha256": sha256(MANIFEST),
        "product_count": len(part_reports),
        "assembly_count": len(assembly_reports),
        "all_active_products_reach_final_assembly": active_ids.issubset(root_product_ids),
        "parts": part_reports,
        "assemblies": assembly_reports,
    }
    report["passed"] = bool(
        len(part_reports) == 101
        and len(assembly_reports) == 26
        and report["all_active_products_reach_final_assembly"]
        and all(value["passed"] for value in [*part_reports, *assembly_reports])
    )
    atomic_json(output_root / "lm3-product-library.index.json", report)
    print(json.dumps({key: report[key] for key in ("product_count", "assembly_count", "all_active_products_reach_final_assembly", "passed")}, indent=2, sort_keys=True))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args(argv)
    report = build_library(args.output_root.resolve())
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
