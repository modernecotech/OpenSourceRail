#!/usr/bin/env python3
"""Export the complete LM3 product/method/tooling graph as deterministic IFC4.3."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import uuid
from collections import defaultdict
from importlib.metadata import version
from pathlib import Path
from typing import Any

import numpy as np
import ifcopenshell
from ifcopenshell.api.aggregate import assign_object
from ifcopenshell.api.context import add_context
from ifcopenshell.api.geometry import add_mesh_representation, assign_representation, edit_object_placement
from ifcopenshell.api.spatial import assign_container
from ifcopenshell.api.unit import assign_unit


REPO_ROOT = Path(__file__).resolve().parents[2]
MECHANICAL_SRC = REPO_ROOT / "design/component-catalogue/src"
if str(MECHANICAL_SRC) not in sys.path:
    sys.path.insert(0, str(MECHANICAL_SRC))

from osr_mech.cad import Compound, Part  # noqa: E402
from osr_mech.rolling_stock.manufacturing_tooling import TOOL_BUILDERS  # noqa: E402
from osr_mech.trainset_manufacturing_methods import load_and_validate  # noqa: E402
from osr_mech.trainset_supplier_anchors import load_and_validate as load_supplier_anchors  # noqa: E402


NAMESPACE = uuid.UUID("0b91bf10-87f2-51e4-bd5a-70b43a1a2351")
DEFAULT_OUTPUT = (
    REPO_ROOT / "engineering/models/bim/reference/lm3-manufacturing-reference.ifc"
)
DEFAULT_INDEX = (
    REPO_ROOT / "engineering/models/bim/reference/lm3-manufacturing-reference.index.json"
)
DEFINITIONS = REPO_ROOT / "design/component-catalogue/catalog/buildable-trainset/definitions"
MANIFEST = (
    REPO_ROOT
    / "design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.json"
)
BOX_FACES = (
    (0, 1, 3, 2),
    (4, 6, 7, 5),
    (0, 4, 5, 1),
    (2, 3, 7, 6),
    (0, 2, 6, 4),
    (1, 5, 7, 3),
)


def gid(value: str) -> str:
    return ifcopenshell.guid.compress(uuid.uuid5(NAMESPACE, value).hex)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repository_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def entity(model: ifcopenshell.file, ifc_class: str, identity: str, **kwargs: Any):
    return model.create_entity(ifc_class, GlobalId=gid(identity), **kwargs)


def nominal_value(model: ifcopenshell.file, value: Any):
    if isinstance(value, bool):
        return model.create_entity("IfcBoolean", value)
    if isinstance(value, int):
        return model.create_entity("IfcInteger", value)
    if isinstance(value, float):
        return model.create_entity("IfcReal", value)
    return model.create_entity("IfcText", str(value))


def property_set(
    model: ifcopenshell.file,
    product: Any,
    name: str,
    values: dict[str, Any],
) -> None:
    properties = [
        model.create_entity(
            "IfcPropertySingleValue",
            Name=key,
            NominalValue=nominal_value(model, value),
        )
        for key, value in values.items()
    ]
    pset = entity(
        model,
        "IfcPropertySet",
        f"pset:{product.GlobalId}:{name}",
        Name=name,
        HasProperties=properties,
    )
    entity(
        model,
        "IfcRelDefinesByProperties",
        f"defines:{product.GlobalId}:{name}",
        RelatedObjects=[product],
        RelatingPropertyDefinition=pset,
    )


def product_ifc_class(product: dict[str, Any]) -> str:
    product_id = product["id"]
    if product_id == "LM3-FIX-P020":
        return "IfcMechanicalFastener"
    if product_id == "LM3-EXT-P010":
        return "IfcDoor"
    if product_id in {"LM3-EXT-P020", "LM3-EXT-P030"}:
        return "IfcWindow"
    if product_id in {"LM3-EXT-P062", "LM3-EXT-P063", "LM3-FIX-P030"}:
        return "IfcFurniture"
    if product_id == "LM3-EXT-P061":
        return "IfcCovering"
    if product_id in {"LM3-LGT-P010", "LM3-LGT-P020"}:
        return "IfcLightFixture"
    if product_id == "LM3-TRC-P010":
        return "IfcElectricMotor"
    if product_id == "LM3-EXT-P040":
        return "IfcUnitaryEquipment"
    return "IfcBuildingElementProxy"


def definition_payloads() -> dict[str, dict[str, Any]]:
    index = json.loads((DEFINITIONS / "index.json").read_text(encoding="utf-8"))
    result: dict[str, dict[str, Any]] = {}
    for entry in index["entries"]:
        path = DEFINITIONS / entry["json"]
        result[entry["id"]] = json.loads(path.read_text(encoding="utf-8"))
    return result


def flatten(part: Part | Compound) -> list[Part]:
    if isinstance(part, Compound):
        leaves: list[Part] = []
        for child in part.children:
            leaves.extend(flatten(child))
        return leaves
    return [part]


def box_geometry(part: Part, origin: tuple[float, float, float]) -> list[tuple[float, float, float]]:
    box = part.bounding_box()
    ox, oy, oz = origin
    return [
        (x / 1000.0 - ox, y / 1000.0 - oy, z / 1000.0 - oz)
        for x in (box.min.X, box.max.X)
        for y in (box.min.Y, box.max.Y)
        for z in (box.min.Z, box.max.Z)
    ]


def add_tool_geometry(
    model: ifcopenshell.file,
    body_context: Any,
    tool: Any,
    tool_id: str,
    position: tuple[float, float, float],
) -> int:
    built = TOOL_BUILDERS[tool_id]()
    leaves = [leaf for leaf in flatten(built) if leaf.bounding_box().volume > 0]
    representation = add_mesh_representation(
        model,
        context=body_context,
        vertices=[box_geometry(leaf, (0.0, 0.0, 0.0)) for leaf in leaves],
        faces=[[list(face) for face in BOX_FACES] for _ in leaves],
        unit_scale=1.0,
    )
    assign_representation(model, product=tool, representation=representation)
    matrix = np.eye(4)
    matrix[:3, 3] = position
    edit_object_placement(model, product=tool, matrix=matrix, is_si=True)
    return len(leaves)


def duration(minutes: int) -> str:
    hours, mins = divmod(minutes, 60)
    if hours and mins:
        return f"PT{hours}H{mins}M"
    if hours:
        return f"PT{hours}H"
    return f"PT{mins}M"


def canonicalise_root_ids(model: ifcopenshell.file) -> None:
    """Replace API-created random relationship IDs in stable creation order."""

    counters: dict[str, int] = defaultdict(int)
    for root in model.by_type("IfcRoot"):
        ifc_class = root.is_a()
        counters[ifc_class] += 1
        root.GlobalId = gid(f"canonical:{ifc_class}:{counters[ifc_class]:05d}")

    def entity_key(value: Any) -> tuple[str, str, str, str, int]:
        return (
            str(getattr(value, "Tag", "") or ""),
            str(getattr(value, "Identification", "") or ""),
            str(getattr(value, "Name", "") or ""),
            str(getattr(value, "GlobalId", "") or ""),
            value.id(),
        )

    # IFC SET attributes may be emitted in hash order by the API. Sort every
    # set used by this exporter before writing so byte identity is repeatable.
    for ifc_class, attribute in (
        ("IfcUnitAssignment", "Units"),
        ("IfcRelAggregates", "RelatedObjects"),
        ("IfcRelNests", "RelatedObjects"),
        ("IfcRelContainedInSpatialStructure", "RelatedElements"),
        ("IfcRelAssignsToControl", "RelatedObjects"),
        ("IfcRelAssignsToProcess", "RelatedObjects"),
        ("IfcRelDefinesByProperties", "RelatedObjects"),
    ):
        for relationship in model.by_type(ifc_class):
            values = getattr(relationship, attribute, None)
            if values:
                setattr(relationship, attribute, tuple(sorted(values, key=entity_key)))


def build_model() -> tuple[ifcopenshell.file, dict[str, Any]]:
    methods = load_and_validate()
    supplier_data = load_supplier_anchors()
    anchors = {anchor["id"]: anchor for anchor in supplier_data["anchor"]}
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    definitions = definition_payloads()
    model = ifcopenshell.file(schema="IFC4X3")
    model.header.file_name.name = "lm3-manufacturing-reference.ifc"
    model.header.file_name.time_stamp = "2026-08-30T00:00:00+00:00"
    model.header.file_name.author = ("OpenSourceRail",)
    model.header.file_name.organization = ("OpenSourceRail",)
    model.header.file_name.preprocessor_version = f"IfcOpenShell {version('ifcopenshell')}"
    model.header.file_name.originating_system = "OpenSourceRail LM3 manufacturing exporter"
    model.header.file_name.authorization = "design-reference / not for construction"

    project = entity(model, "IfcProject", "project", Name="OpenSourceRail LM3 manufacturing reference")
    site = entity(model, "IfcSite", "site", Name="Local railway manufacturing programme", CompositionType="ELEMENT")
    factory = entity(model, "IfcBuilding", "factory", Name="LM3 local pilot factory", CompositionType="ELEMENT")
    assign_unit(model, length={"is_metric": True, "raw": "METERS"})
    context = add_context(model, context_type="Model")
    body_context = add_context(
        model,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=context,
    )
    assign_object(model, products=[site], relating_object=project)
    assign_object(model, products=[factory], relating_object=site)
    edit_object_placement(model, product=site, matrix=np.eye(4), is_si=True)
    edit_object_placement(model, product=factory, matrix=np.eye(4), is_si=True)

    project.Description = methods["release_boundary"]
    property_set(
        model,
        project,
        "OSR_ManufacturingReference",
        {
            "Schema": methods["schema"],
            "Revision": methods["revision"],
            "Status": methods["status"],
            "MethodSource": methods["source_file"],
            "MethodSourceSha256": methods["source_sha256"],
            "ProductManifest": methods["product_manifest"],
            "ProductManifestSha256": methods["product_manifest_sha256"],
            "ReleaseBoundary": methods["release_boundary"],
            "SupplierAnchorSource": supplier_data["source_file"],
            "SupplierAnchorSourceSha256": supplier_data["source_sha256"],
            "SupplierAnchorCheckedOn": supplier_data["checked_on"],
            "SupplierAnchorReleaseBoundary": supplier_data["release_boundary"],
        },
    )

    products: dict[str, Any] = {}
    for assembly in manifest["assemblies"]:
        ifc_class = "IfcVehicle" if assembly["layer"] == "trainset" else "IfcElementAssembly"
        product = entity(
            model,
            ifc_class,
            f"product:{assembly['id']}",
            Name=assembly["title"],
            Description=" | ".join(assembly["hold_points"]),
            Tag=assembly["id"],
        )
        products[assembly["id"]] = product
        payload = definitions[assembly["id"]]
        property_set(
            model,
            product,
            "OSR_AssemblyDefinition",
            {
                "OSRId": assembly["id"],
                "Layer": assembly["layer"],
                "BuildCell": assembly["build_cell"],
                "HoldPoints": " | ".join(assembly["hold_points"]),
                "ToolingBasis": payload["process_spec"]["tooling_basis"],
                "ReleaseLevel": payload["process_spec"]["release_level"],
            },
        )
    class_counts: dict[str, int] = {}
    for item in manifest["product_items"]:
        ifc_class = product_ifc_class(item)
        class_counts[ifc_class] = class_counts.get(ifc_class, 0) + 1
        product = entity(
            model,
            ifc_class,
            f"product:{item['id']}",
            Name=item["title"],
            Description=item["make_or_buy_basis"],
            Tag=item["id"],
        )
        products[item["id"]] = product
        payload = definitions[item["id"]]
        material = payload["material_spec"]
        process = payload["process_spec"]
        property_set(
            model,
            product,
            "OSR_ProductDefinition",
            {
                "OSRId": item["id"],
                "Layer": item["layer"],
                "Route": item["route"],
                "Maturity": item["maturity"],
                "Parent": item["parent"],
                "QuantityPerTrainset": item["quantity_per_trainset"],
                "Unit": item["unit"],
                "MaterialFamily": material["material_family"],
                "GradeOrPartClass": material["grade_or_part_class"],
                "GoverningStandard": material["governing_standard"],
                "FinishOrProtection": material["finish_or_protection"],
                "Traceability": material["traceability"],
                "JoiningMethods": " | ".join(process["joining_methods"]),
                "ToolingBasis": process["tooling_basis"],
                "InspectionMethods": " | ".join(process["inspection_methods"]),
                "ReleaseLevel": process["release_level"],
                "Acceptance": " | ".join(item["acceptance"]),
                "SourceRefs": " | ".join(item["source_refs"]),
            },
        )
        anchor_id = supplier_data["product_to_anchor"].get(item["id"])
        if anchor_id:
            anchor = anchors[anchor_id]
            property_set(
                model,
                product,
                "OSR_SupplierAnchor",
                {
                    "AnchorId": anchor_id,
                    "Manufacturer": anchor["manufacturer"],
                    "ProductFamily": anchor["product_family"],
                    "ManufacturerUrl": anchor["manufacturer_url"],
                    "AnchorType": anchor["anchor_type"],
                    "ProcurementState": anchor["procurement_state"],
                    "LocalEquivalentAllowed": True,
                    "LocalisationRoute": anchor["localisation"],
                    "KnownFitGaps": " | ".join(anchor["fit_gaps"]),
                    "EquivalenceDossier": " | ".join(supplier_data["equivalence"]["required"]),
                },
            )

    for assembly in manifest["assemblies"]:
        assign_object(
            model,
            products=[products[child] for child in assembly["children"]],
            relating_object=products[assembly["id"]],
        )
    assign_container(
        model,
        products=[products["LM3-TRAINSET-A000"]],
        relating_structure=factory,
    )

    schedule = entity(
        model,
        "IfcWorkSchedule",
        "schedule",
        Name="LM3 manufacturing-method planning schedule",
        Description=methods["planning_basis"],
        Identification="LM3-MFG-SCHEDULE-A-DRAFT",
        PredefinedType="PLANNED",
    )
    entity(
        model,
        "IfcRelAssignsToControl",
        "schedule-project",
        RelatedObjects=[project],
        RelatingControl=schedule,
    )

    tools: list[Any] = []
    tasks: list[Any] = []
    tool_part_count = 0
    for method_index, method in enumerate(methods["method"]):
        method_task = entity(
            model,
            "IfcTask",
            f"task:{method['id']}",
            Name=method["title"],
            Description=method["release_gate"],
            Identification=method["id"],
            Status="DESIGN-REFERENCE",
            IsMilestone=False,
        )
        method_task.TaskTime = model.create_entity(
            "IfcTaskTime", Name=f"{method['id']} planning cycle", ScheduleDuration=duration(method["planning_cycle_minutes"])
        )
        tasks.append(method_task)
        entity(
            model,
            "IfcRelAssignsToControl",
            f"schedule:{method['id']}",
            RelatedObjects=[method_task],
            RelatingControl=schedule,
        )
        entity(
            model,
            "IfcRelAssignsToProcess",
            f"method-products:{method['id']}",
            RelatedObjects=[products[item_id] for item_id in method["product_ids"]],
            RelatingProcess=method_task,
        )
        step_tasks: list[Any] = []
        for step in method["steps"]:
            task = entity(
                model,
                "IfcTask",
                f"task:{method['id']}:{step['sequence']}",
                Name=step["name"],
                Description=step["instruction"],
                Identification=f"{method['id']}-{step['sequence']}",
                Status="HOLD-POINT" if step["hold_point"] else "PLANNED",
                IsMilestone=False,
            )
            task.TaskTime = model.create_entity(
                "IfcTaskTime",
                Name=f"{task.Identification} planning allowance",
                ScheduleDuration=duration(step["planning_minutes"]),
            )
            step_tasks.append(task)
            tasks.append(task)
        entity(
            model,
            "IfcRelNests",
            f"task-nests:{method['id']}",
            RelatingObject=method_task,
            RelatedObjects=step_tasks,
        )
        for previous, following in zip(step_tasks, step_tasks[1:]):
            entity(
                model,
                "IfcRelSequence",
                f"task-sequence:{previous.Identification}:{following.Identification}",
                RelatingProcess=previous,
                RelatedProcess=following,
                SequenceType="FINISH_START",
            )

        for tool_index, tool_id in enumerate(method["tooling_ids"]):
            tool = entity(
                model,
                "IfcDiscreteAccessory",
                f"tool:{tool_id}",
                Name=tool_id,
                Description=f"{method['title']} — supplier-neutral design-reference tooling",
                Tag=tool_id,
            )
            position = (float(tool_index * 28), float(method_index * 14), 0.0)
            tool_part_count += add_tool_geometry(model, body_context, tool, tool_id, position)
            assign_container(model, products=[tool], relating_structure=factory)
            property_set(
                model,
                tool,
                "OSR_ManufacturingTool",
                {
                    "OSRId": tool_id,
                    "MethodId": method["id"],
                    "DetailStatus": "design-reference-not-released",
                    "Representation": "multi-part coordination geometry; not an NC/fabrication surface",
                    "WorkCenter": method["work_center"],
                    "PlanningCycleMinutes": method["planning_cycle_minutes"],
                    "JoiningParts": " | ".join(method["joining_parts"]),
                    "ReleaseGate": method["release_gate"],
                },
            )
            entity(
                model,
                "IfcRelAssignsToProcess",
                f"tool-method:{tool_id}",
                RelatedObjects=[tool],
                RelatingProcess=method_task,
            )
            tools.append(tool)

    index = {
        "analysis_id": "OSR-AN-IFC-LM3-MFG-001",
        "schema": model.schema,
        "status": methods["status"],
        "passed": True,
        "assembly_count": len(manifest["assemblies"]),
        "product_item_count": len(manifest["product_items"]),
        "method_count": len(methods["method"]),
        "task_count": len(tasks),
        "tooling_count": len(tools),
        "tooling_representation_part_count": tool_part_count,
        "supplier_anchor_count": supplier_data["coverage"]["anchor_count"],
        "supplier_anchored_external_product_count": supplier_data["coverage"]["covered_external_product_rows"],
        "ifc_class_counts": dict(sorted(class_counts.items())),
        "method_source": methods["source_file"],
        "method_source_sha256": methods["source_sha256"],
        "supplier_anchor_source": supplier_data["source_file"],
        "supplier_anchor_source_sha256": supplier_data["source_sha256"],
        "product_manifest": str(MANIFEST.relative_to(REPO_ROOT)),
        "product_manifest_sha256": sha256(MANIFEST),
        "release_boundary": methods["release_boundary"],
    }
    canonicalise_root_ids(model)
    return model, index


def write(output: Path, index_path: Path) -> dict[str, Any]:
    model, index = build_model()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    model.write(str(temporary))
    os.replace(temporary, output)
    reopened = ifcopenshell.open(str(output))
    expected_tags = {
        *[item.Tag for item in reopened.by_type("IfcElement") if getattr(item, "Tag", None)],
    }
    required = {"LM3-TRAINSET-A000", *TOOL_BUILDERS}
    missing = sorted(required - expected_tags)
    if missing:
        raise RuntimeError(f"written LM3 manufacturing IFC is missing tags: {missing}")
    index["ifc_file"] = repository_path(output)
    index["ifc_sha256"] = sha256(output)
    index["missing_required_tags"] = missing
    index["passed"] = not missing
    with tempfile.NamedTemporaryFile(
        "w", dir=index_path.parent, delete=False, encoding="utf-8"
    ) as handle:
        json.dump(index, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary_index = Path(handle.name)
    os.replace(temporary_index, index_path)
    return index


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    args = parser.parse_args(argv)
    result = write(args.output, args.index)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
