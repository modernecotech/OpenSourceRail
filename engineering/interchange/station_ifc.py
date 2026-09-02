#!/usr/bin/env python3
"""Export and verify station product-structure IFC coordination skeletons."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import uuid
from importlib.metadata import version
from pathlib import Path

import ifcopenshell
from ifcopenshell.api.context import add_context
from ifcopenshell.api.geometry import add_mesh_representation, assign_representation
from ifcopenshell.api.unit import assign_unit


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MECHANICAL_SRC = REPOSITORY_ROOT / "design/component-catalogue/src"
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))
if str(MECHANICAL_SRC) not in sys.path:
    sys.path.insert(0, str(MECHANICAL_SRC))

from osr_mech.station.product_geometry import (  # noqa: E402
    flatten_geometry,
    geometry_specs,
    station_product_geometry,
)
from engineering.interchange.trainset_manufacturing_ifc import (  # noqa: E402
    canonicalise_root_ids,
    combine_meshes,
    primitive_geometry,
    set_local_placement,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / "design/component-catalogue/catalog/buildable-stations/station-kit-manifest.json"
NAMESPACE = uuid.UUID("35015482-428c-52e0-9de7-7c4532bc7190")
FIXED_HEADER_TIMESTAMP = "2026-08-30T00:00:00+00:00"


def gid(value: str) -> str:
    return ifcopenshell.guid.compress(uuid.uuid5(NAMESPACE, value).hex)


def report_path(path: Path) -> str:
    """Return a portable report path for repository and temporary outputs."""

    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return path.name


def property_set(model: ifcopenshell.file, product: object, name: str, values: dict[str, object]) -> None:
    properties = []
    for key, value in values.items():
        if isinstance(value, (int, float)):
            nominal = model.create_entity("IfcReal", float(value))
        else:
            nominal = model.create_entity("IfcLabel", str(value))
        properties.append(model.create_entity("IfcPropertySingleValue", Name=key, NominalValue=nominal))
    pset = model.create_entity("IfcPropertySet", GlobalId=gid(f"{name}:{product.GlobalId}"), Name=name, HasProperties=properties)
    model.create_entity("IfcRelDefinesByProperties", GlobalId=gid(f"defines:{name}:{product.GlobalId}"), RelatedObjects=[product], RelatingPropertyDefinition=pset)


def canonicalise_header(model: ifcopenshell.file, archetype: str) -> None:
    """Remove wall-clock and output-path variation from the STEP header."""

    model.header.file_name.name = f"station-{archetype}.ifc"
    model.header.file_name.time_stamp = FIXED_HEADER_TIMESTAMP
    model.header.file_name.author = ("OpenSourceRail",)
    model.header.file_name.organization = ("OpenSourceRail",)
    model.header.file_name.preprocessor_version = (
        f"IfcOpenShell {version('ifcopenshell')}"
    )
    model.header.file_name.originating_system = (
        "OpenSourceRail deterministic station IFC exporter"
    )
    model.header.file_name.authorization = "design-reference / not for construction"


def export_variant(variant: dict[str, object], output: Path) -> dict[str, object]:
    archetype = str(variant["archetype"])
    model = ifcopenshell.file(schema="IFC4X3")
    project = model.create_entity("IfcProject", GlobalId=gid(f"{archetype}:project"), Name=f"OSR {archetype} station coordination")
    site = model.create_entity("IfcSite", GlobalId=gid(f"{archetype}:site"), Name=f"{archetype} station site", CompositionType="ELEMENT")
    building = model.create_entity("IfcBuilding", GlobalId=gid(f"{archetype}:building"), Name=f"{archetype} station", CompositionType="ELEMENT")
    model.create_entity("IfcRelAggregates", GlobalId=gid(f"{archetype}:project-site"), RelatingObject=project, RelatedObjects=[site])
    model.create_entity("IfcRelAggregates", GlobalId=gid(f"{archetype}:site-building"), RelatingObject=site, RelatedObjects=[building])
    assign_unit(model, length={"is_metric": True, "raw": "METERS"})
    context = add_context(model, context_type="Model")
    body_context = add_context(
        model,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=context,
    )
    set_local_placement(model, site, (0.0, 0.0, 0.0))
    set_local_placement(model, building, (0.0, 0.0, 0.0))
    specs = geometry_specs()
    item_ids = {str(item["id"]) for item in variant["product_items"]}
    missing_specs = sorted(item_ids - set(specs))
    if missing_specs:
        raise RuntimeError(f"station geometry registry does not cover {missing_specs}")

    entities: dict[str, object] = {}
    for assembly in variant["assemblies"]:
        osr_id = str(assembly["id"])
        entity = model.create_entity("IfcElementAssembly", GlobalId=gid(f"{archetype}:{osr_id}"), Name=str(assembly["title"]), Description="; ".join(assembly["instructions"]), ObjectType="OSR station assembly", Tag=osr_id, PredefinedType="USERDEFINED")
        entities[osr_id] = entity
        property_set(model, entity, "OSR_Assembly", {"OSRId": osr_id, "Archetype": archetype, "WorkCell": assembly["work_cell"], "HoldPoints": " | ".join(assembly["hold_points"])})

    primitive_count = 0
    represented_ids: set[str] = set()
    for item in variant["product_items"]:
        osr_id = str(item["id"])
        spec = specs[osr_id]
        entity = model.create_entity(
            spec.ifc_class,
            GlobalId=gid(f"{archetype}:{osr_id}"),
            Name=str(item["title"]),
            Description=str(item["quantity_basis"]),
            ObjectType="OSR station product item",
            Tag=osr_id,
        )
        entities[osr_id] = entity
        built = station_product_geometry(item, variant["parameters"])
        leaves = [leaf for leaf in flatten_geometry(built) if leaf.bounding_box().volume > 0]
        if not leaves:
            raise RuntimeError(f"station product {osr_id} has no positive-volume geometry")
        vertices, faces = combine_meshes([primitive_geometry(leaf) for leaf in leaves])
        representation = add_mesh_representation(
            model,
            context=body_context,
            vertices=[vertices],
            faces=[faces],
            unit_scale=1.0,
        )
        assign_representation(model, product=entity, representation=representation)
        set_local_placement(model, entity, (0.0, 0.0, 0.0))
        represented_ids.add(osr_id)
        primitive_count += len(leaves)
        property_set(model, entity, "OSR_ProductItem", {"OSRId": osr_id, "Archetype": archetype, "Maturity": item["maturity"], "Route": item["route"], "Quantity": item["quantity"], "Unit": item["unit"], "ParentAssembly": item["parent"], "QuantityBasis": item["quantity_basis"], "Acceptance": " | ".join(item["acceptance"]), "SourceRefs": " | ".join(item["source_refs"]), "IFCClass": spec.ifc_class, "GeometryLevel": spec.geometry_level, "GeometryRepresentation": spec.representation, "ReleaseBoundary": "design-reference / not for construction"})

    for assembly in variant["assemblies"]:
        osr_id = str(assembly["id"])
        children = [entities[str(child)] for child in assembly["children"]]
        model.create_entity(
            "IfcRelAggregates",
            GlobalId=gid(f"{archetype}:{osr_id}:children"),
            RelatingObject=entities[osr_id],
            RelatedObjects=children,
        )
    root_assembly = entities["STN-STATION-A900"]
    model.create_entity("IfcRelContainedInSpatialStructure", GlobalId=gid(f"{archetype}:containment"), RelatedElements=[root_assembly], RelatingStructure=building)
    canonicalise_root_ids(model)
    canonicalise_header(model, archetype)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    model.write(str(temporary))
    os.replace(temporary, output)

    reopened = ifcopenshell.open(str(output))
    expected_ids = set(entities)
    exported_ids = {
        str(entity.Tag)
        for entity in reopened.by_type("IfcProduct")
        if getattr(entity, "Tag", None)
    }
    missing = sorted(expected_ids - exported_ids)
    unexpected = sorted(exported_ids - expected_ids)
    pset_ids: dict[str, str] = {}
    for relationship in reopened.by_type("IfcRelDefinesByProperties"):
        properties = relationship.RelatingPropertyDefinition.HasProperties
        identity = next((prop for prop in properties if prop.Name == "OSRId"), None)
        if identity is not None:
            for related in relationship.RelatedObjects:
                if getattr(related, "Tag", None):
                    pset_ids[str(related.Tag)] = str(identity.NominalValue.wrappedValue)
    property_mismatches = sorted(osr_id for osr_id in expected_ids if pset_ids.get(osr_id) != osr_id)
    expected_children = {str(assembly["id"]): list(assembly["children"]) for assembly in variant["assemblies"]}
    exported_children: dict[str, list[str]] = {}
    for relationship in reopened.by_type("IfcRelAggregates"):
        parent = getattr(relationship.RelatingObject, "Tag", None)
        if parent in expected_children:
            exported_children[str(parent)] = [str(child.Tag) for child in relationship.RelatedObjects]
    structure_mismatches = sorted(
        osr_id
        for osr_id, children in expected_children.items()
        if set(exported_children.get(osr_id, [])) != set(children)
    )
    if missing or unexpected or property_mismatches or structure_mismatches:
        raise RuntimeError(
            f"IFC drift for {archetype}: missing={missing}, unexpected={unexpected}, "
            f"property_mismatches={property_mismatches}, structure_mismatches={structure_mismatches}"
        )
    reopened_represented = {
        str(entity.Tag)
        for entity in reopened.by_type("IfcProduct")
        if getattr(entity, "Tag", None) and getattr(entity, "Representation", None)
    }
    missing_geometry = sorted(item_ids - reopened_represented)
    if missing_geometry:
        raise RuntimeError(f"station IFC geometry drift for {archetype}: {missing_geometry}")
    return {"archetype": archetype, "assembly_count": len(variant["assemblies"]), "geometry_status": "coordinated-design-reference-geometry", "ifc_file": report_path(output), "ifc_sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "missing_geometry_ids": missing_geometry, "missing_ids": missing, "primitive_count": primitive_count, "product_item_count": len(variant["product_items"]), "property_mismatches": property_mismatches, "represented_product_count": len(represented_ids), "schema": reopened.schema, "structure_mismatches": structure_mismatches, "unexpected_ids": unexpected}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "build/engineering/interchange/stations")
    parser.add_argument("--variant", action="append", dest="variants")
    parser.add_argument("--all-variants", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    variants = {variant["archetype"]: variant for variant in manifest["variants"]}
    if args.all_variants and args.variants:
        parser.error("--all-variants and --variant cannot be combined")
    if args.all_variants:
        selected = tuple(variants)
    elif args.variants:
        unknown = sorted(set(args.variants) - set(variants))
        if unknown:
            parser.error(f"unknown station variant(s): {', '.join(unknown)}")
        selected = tuple(dict.fromkeys(args.variants))
    else:
        selected = ("standard", "interchange-elevated")
    reports = [export_variant(variants[name], args.output_dir / f"station-{name}.ifc") for name in selected]
    summary = {"analysis_id": "OSR-AN-IFC-STN-001", "ifcopenshell_version": version("ifcopenshell"), "manifest": str(MANIFEST.relative_to(REPO_ROOT)), "manifest_sha256": hashlib.sha256(MANIFEST.read_bytes()).hexdigest(), "passed": all(not report["missing_ids"] and not report["missing_geometry_ids"] and not report["unexpected_ids"] and not report["property_mismatches"] and not report["structure_mismatches"] for report in reports), "scope": "stable-ID, geometric product representation, product-property, and assembly-hierarchy station IFC4.3 interchange", "variants": reports}
    summary_path = args.output_dir / "summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=summary_path.parent, delete=False, encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, summary_path)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
