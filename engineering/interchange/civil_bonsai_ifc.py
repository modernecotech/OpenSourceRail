#!/usr/bin/env python3
"""Generate a deterministic IFC4.3 civil coordination model for Bonsai.

OpenSourceRail remains authoritative for alignment rules and parametric civil
geometry.  This exporter turns the checked design-reference twin into a native
IFC project with rail-domain spatial structure, inspectable geometry,
quantities, provenance, and an IfcWorkSchedule suitable for Bonsai's 4D tools.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from importlib.metadata import version
from pathlib import Path
from typing import Any, Iterable

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
MECHANICAL_SRC = REPO_ROOT / "mechanical-py/src"
if str(MECHANICAL_SRC) not in sys.path:
    sys.path.insert(0, str(MECHANICAL_SRC))

import ifcopenshell
from ifcopenshell.api.aggregate import assign_object
from ifcopenshell.api.context import add_context
from ifcopenshell.api.geometry import (
    add_mesh_representation,
    assign_representation,
    edit_object_placement,
)
from ifcopenshell.api.project import create_file
from ifcopenshell.api.pset import add_pset, edit_pset
from ifcopenshell.api.root import create_entity
from ifcopenshell.api.sequence import (
    add_task,
    add_task_time,
    add_work_schedule,
    assign_product,
    assign_sequence,
    edit_task_time,
)
from ifcopenshell.api.spatial import assign_container
from ifcopenshell.api.style import add_style, add_surface_style, assign_representation_styles
from ifcopenshell.api.unit import assign_unit

from osr_mech.cad import Compound, Part
from osr_mech.civil_systems_integration import (
    asset_class_for_component,
    asset_id_for_component,
    assert_integration_checks,
    digital_twin_manifest,
    integration_components,
)
from osr_mech.fabrication_assembly_twin import fabrication_streams


SCHEMA = "org.opensourcerail.bonsai-civil-ifc.v1"
NAMESPACE = uuid.UUID("5b6994b4-1642-48df-a10b-796985904590")
FIXED_HEADER_TIMESTAMP = "2026-01-01T00:00:00"
DEFAULT_START = datetime(2026, 1, 5, 8, 0, tzinfo=timezone.utc)
MAX_DETAIL_PARTS = 450

BOX_FACES = [
    [0, 1, 3, 2],
    [4, 6, 7, 5],
    [0, 4, 5, 1],
    [2, 3, 7, 6],
    [0, 2, 6, 4],
    [1, 5, 7, 3],
]

DISCIPLINES = {
    "track": ("Track", "TRACK"),
    "substructure": ("Substructure", "SUBSTRUCTURE"),
    "above-track": ("Stations and above-track systems", "ABOVETRACK"),
    "lineside": ("Clearance and lineside coordination", "LINESIDE"),
}

COLOURS = {
    "track": (0.12, 0.18, 0.23),
    "substructure": (0.58, 0.64, 0.68),
    "above-track": (0.10, 0.55, 0.62),
    "lineside": (0.95, 0.48, 0.13),
}


def stable_guid(value: str) -> str:
    return ifcopenshell.guid.compress(uuid.uuid5(NAMESPACE, value).hex)


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def flatten_parts(part: Part | Compound) -> list[Part]:
    if isinstance(part, Compound):
        leaves: list[Part] = []
        for child in part.children:
            leaves.extend(flatten_parts(child))
        return leaves
    return [part]


def bbox_tuple(part: Part) -> tuple[float, float, float, float, float, float]:
    box = part.bounding_box()
    return (box.min.X, box.min.Y, box.min.Z, box.max.X, box.max.Y, box.max.Z)


def bbox_union(boxes: Iterable[tuple[float, float, float, float, float, float]]) -> tuple[float, ...]:
    values = list(boxes)
    return (
        min(box[0] for box in values),
        min(box[1] for box in values),
        min(box[2] for box in values),
        max(box[3] for box in values),
        max(box[4] for box in values),
        max(box[5] for box in values),
    )


def box_mesh(box: tuple[float, ...], origin: tuple[float, float, float]) -> list[tuple[float, float, float]]:
    x0, y0, z0, x1, y1, z1 = (value / 1000.0 for value in box)
    ox, oy, oz = origin
    return [
        (x - ox, y - oy, z - oz)
        for x in (x0, x1)
        for y in (y0, y1)
        for z in (z0, z1)
    ]


def component_discipline(asset_class: str) -> str:
    if asset_class in {"track.rail", "track.turnout", "civil.trackform"}:
        return "track"
    if asset_class in {"civil.pier", "civil.u-girder", "civil.station-deck-interface"}:
        return "substructure"
    if asset_class.startswith("station.") or asset_class == "rolling-stock.trainset":
        return "above-track"
    return "lineside"


def ifc_type(asset_class: str) -> tuple[str, str | None]:
    return {
        "track.rail": ("IfcRail", "RAIL"),
        "track.turnout": ("IfcElementAssembly", "USERDEFINED"),
        "civil.trackform": ("IfcSlab", "BASESLAB"),
        "civil.pier": ("IfcColumn", None),
        "civil.u-girder": ("IfcBeam", "GIRDER_SEGMENT"),
        "civil.station-deck-interface": ("IfcSlab", "BASESLAB"),
        "station.solar-canopy": ("IfcRoof", None),
        "station.platform-interface": ("IfcSlab", "FLOOR"),
        "clearance.reference-envelope": ("IfcVirtualElement", None),
        "rolling-stock.trainset": ("IfcBuildingElementProxy", None),
    }.get(asset_class, ("IfcCivilElement", None))


def make_style(model: ifcopenshell.file, name: str, colour: tuple[float, float, float], transparency: float = 0.0):
    style = add_style(model, name=name)
    add_surface_style(
        model,
        style=style,
        ifc_class="IfcSurfaceStyleRendering",
        attributes={
            "SurfaceColour": {"Name": None, "Red": colour[0], "Green": colour[1], "Blue": colour[2]},
            "Transparency": transparency,
            "ReflectanceMethod": "NOTDEFINED",
        },
    )
    return style


def set_properties(model: ifcopenshell.file, product: Any, name: str, values: dict[str, Any]) -> None:
    pset = add_pset(model, product=product, name=name)
    edit_pset(model, pset=pset, properties=values)


def load_alignment(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    points = value.get("points")
    if not isinstance(points, list) or len(points) < 2:
        raise ValueError("alignment input requires at least two local XYZ points")
    for point in points:
        if not isinstance(point, list) or len(point) != 3 or not all(isinstance(item, (int, float)) for item in point):
            raise ValueError("alignment points must be numeric [x, y, z] triples in metres")
    return value


def add_alignment(
    model: ifcopenshell.file,
    axis_context: Any,
    track_part: Any,
    alignment_input: dict[str, Any] | None,
    revision_id: str,
) -> Any:
    name = (alignment_input or {}).get("line_slug", "osr-civil-reference-axis")
    alignment = create_entity(model, ifc_class="IfcAlignment", name=name)
    points = (alignment_input or {}).get("points", [[0.0, 0.0, 0.0], [320.0, 0.0, 0.0]])
    point_list = model.create_entity("IfcCartesianPointList3D", CoordList=points)
    curve = model.create_entity("IfcIndexedPolyCurve", Points=point_list, Segments=None, SelfIntersect=False)
    representation = model.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=axis_context,
        RepresentationIdentifier="Axis",
        RepresentationType="Curve3D",
        Items=[curve],
    )
    assign_representation(model, product=alignment, representation=representation)
    edit_object_placement(model, product=alignment, matrix=np.eye(4), is_si=True)
    assign_container(model, products=[alignment], relating_structure=track_part)
    set_properties(
        model,
        alignment,
        "Pset_OSR_AlignmentAuthority",
        {
            "Authority": "OpenSourceRail deterministic alignment engine",
            "RevisionId": revision_id,
            "DesignSpeedKmh": float((alignment_input or {}).get("design_speed_kmh", 80.0)),
            "GeometryRole": "IFC reference axis; engineering rules remain upstream",
            "PointCount": len(points),
        },
    )
    return alignment


def add_schedule(
    model: ifcopenshell.file,
    products: dict[str, Any],
    product_classes: dict[str, str],
    product_names: dict[str, str],
) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
    schedule = add_work_schedule(
        model,
        name="OSR civil fabrication and construction sequence",
        predefined_type="PLANNED",
        start_time=DEFAULT_START,
    )
    stream_classes = {
        "track": {"track.rail", "track.turnout", "civil.trackform"},
        "station": {"station.solar-canopy", "station.platform-interface", "civil.station-deck-interface"},
        "viaduct": {"civil.pier", "civil.u-girder", "civil.trackform", "track.rail"},
    }
    schedule_rows: list[dict[str, Any]] = []
    assignments: dict[str, list[str]] = {}
    cursor_by_stream: dict[str, datetime] = {}
    tasks_by_id: dict[str, Any] = {}
    for stream in fabrication_streams():
        if stream.id not in stream_classes:
            continue
        cursor = cursor_by_stream.setdefault(stream.id, DEFAULT_START)
        for stage in stream.stages:
            task = add_task(
                model,
                work_schedule=schedule,
                name=stage.title,
                description=f"{stage.work_center}; QA hold: {stage.qa_hold}",
                identification=stage.id,
                predefined_type="CONSTRUCTION",
            )
            task_time = add_task_time(model, task=task)
            finish = cursor + timedelta(days=stage.duration_days)
            edit_task_time(
                model,
                task_time=task_time,
                attributes={
                    "ScheduleStart": cursor,
                    "ScheduleFinish": finish,
                    "ScheduleDuration": f"P{stage.duration_days:g}D",
                },
            )
            if stage.predecessor and stage.predecessor in tasks_by_id:
                assign_sequence(
                    model,
                    relating_process=tasks_by_id[stage.predecessor],
                    related_process=task,
                    sequence_type="FINISH_START",
                )
            tasks_by_id[stage.id] = task
            assigned_ids = []
            for asset_id in products:
                asset_class = product_classes[asset_id]
                name = product_names[asset_id]
                if asset_class not in stream_classes[stream.id]:
                    continue
                if stream.id == "track" and not (
                    name.startswith("Ground-station") or "turnout" in name.lower()
                ):
                    continue
                if stream.id == "viaduct" and not (
                    name.startswith("Viaduct")
                    or name.startswith("Shared double-track pier")
                    or name.startswith("Elevated-station")
                ):
                    continue
                assigned_ids.append(asset_id)
            # Assign every matching product to the final installation/erection
            # stage, while earlier tasks retain QA and schedule semantics.
            if stage is stream.stages[-1]:
                for asset_id in assigned_ids:
                    assign_product(model, relating_product=products[asset_id], related_object=task)
                assignments[stage.id] = assigned_ids
            schedule_rows.append(
                {
                    "id": stage.id,
                    "stream": stream.id,
                    "title": stage.title,
                    "start": cursor.isoformat(),
                    "finish": finish.isoformat(),
                    "duration_days": stage.duration_days,
                    "predecessor": stage.predecessor,
                    "qa_hold": stage.qa_hold,
                    "evidence": list(stage.evidence),
                    "assigned_asset_ids": assigned_ids if stage is stream.stages[-1] else [],
                }
            )
            cursor = finish
        cursor_by_stream[stream.id] = cursor
    return schedule_rows, assignments


def deterministic_roots(model: ifcopenshell.file) -> None:
    counters: Counter[tuple[str, str]] = Counter()
    for root in model.by_type("IfcRoot"):
        key = (root.is_a(), getattr(root, "Name", None) or getattr(root, "Identification", None) or "")
        counters[key] += 1
        root.GlobalId = stable_guid(f"{key[0]}|{key[1]}|{counters[key]}")


def stabilize_unordered_collections(model: ifcopenshell.file) -> None:
    """Canonicalise IFC SET attributes whose Python order is hash-randomised."""

    attributes = {
        "IfcUnitAssignment": ("Units",),
        "IfcRelAggregates": ("RelatedObjects",),
        "IfcRelContainedInSpatialStructure": ("RelatedElements",),
        "IfcRelAssignsToControl": ("RelatedObjects",),
        "IfcRelAssignsToProcess": ("RelatedObjects",),
        "IfcRelDefinesByProperties": ("RelatedObjects",),
    }
    for ifc_class, names in attributes.items():
        for entity in model.by_type(ifc_class):
            for name in names:
                values = getattr(entity, name, None)
                if values:
                    setattr(entity, name, tuple(sorted(values, key=lambda item: item.id())))


def build_model(
    *,
    alignment_input: dict[str, Any] | None,
    revision_id: str,
) -> tuple[ifcopenshell.file, dict[str, Any], dict[str, Any]]:
    assert_integration_checks()
    twin = digital_twin_manifest()
    source_hash = sha256_bytes(canonical_json({"twin": twin, "alignment": alignment_input}))

    model = create_file("IFC4X3")
    model.header.file_name.name = "civil-coordination.ifc"
    model.header.file_name.time_stamp = FIXED_HEADER_TIMESTAMP
    model.header.file_name.author = ("OpenSourceRail",)
    model.header.file_name.organization = ("OpenSourceRail",)
    model.header.file_name.preprocessor_version = f"IfcOpenShell {version('ifcopenshell')}"
    model.header.file_name.originating_system = "OpenSourceRail deterministic Bonsai civil exporter"
    model.header.file_name.authorization = "design-reference / not for construction"

    project = create_entity(model, ifc_class="IfcProject", name="OpenSourceRail civil coordination")
    site = create_entity(model, ifc_class="IfcSite", name="OSR local engineering grid")
    railway = create_entity(model, ifc_class="IfcRailway", name="OpenSourceRail reference railway")
    assign_unit(model, length={"is_metric": True, "raw": "METERS"})
    model_context = add_context(model, context_type="Model")
    body_context = add_context(
        model,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=model_context,
    )
    axis_context = add_context(
        model,
        context_type="Model",
        context_identifier="Axis",
        target_view="GRAPH_VIEW",
        parent=model_context,
    )
    assign_object(model, products=[site], relating_object=project)
    assign_object(model, products=[railway], relating_object=site)
    edit_object_placement(model, product=site, matrix=np.eye(4), is_si=True)
    edit_object_placement(model, product=railway, matrix=np.eye(4), is_si=True)

    set_properties(
        model,
        project,
        "Pset_OSR_Provenance",
        {
            "Schema": SCHEMA,
            "RevisionId": revision_id,
            "CanonicalSourceSha256": source_hash,
            "IfcOpenShellVersion": version("ifcopenshell"),
            "GeometryAuthority": "OpenSourceRail parametric civil and alignment models",
            "CoordinationEnvironment": "Bonsai 0.8.5 / IFC4.3",
            "ReleaseStatus": "design-reference; not for construction",
        },
    )

    spatial_parts: dict[str, Any] = {}
    for key, (name, predefined_type) in DISCIPLINES.items():
        part = create_entity(
            model,
            ifc_class="IfcRailwayPart",
            predefined_type=predefined_type,
            name=name,
        )
        assign_object(model, products=[part], relating_object=railway)
        edit_object_placement(model, product=part, matrix=np.eye(4), is_si=True)
        spatial_parts[key] = part

    styles = {
        key: make_style(model, f"OSR {key}", colour, 0.72 if key == "lineside" else 0.0)
        for key, colour in COLOURS.items()
    }
    add_alignment(model, axis_context, spatial_parts["track"], alignment_input, revision_id)

    products: dict[str, Any] = {}
    product_classes: dict[str, str] = {}
    product_names: dict[str, str] = {}
    index_rows: list[dict[str, Any]] = []
    for component in integration_components():
        asset_id = asset_id_for_component(component)
        asset_class = asset_class_for_component(component)
        discipline = component_discipline(asset_class)
        ifc_class, predefined_type = ifc_type(asset_class)
        product = create_entity(
            model,
            ifc_class=ifc_class,
            predefined_type=predefined_type,
            name=component.label,
        )
        product.Tag = asset_id
        built = component.build()
        leaves = [leaf for leaf in flatten_parts(built) if leaf.bounding_box().volume > 0.0]
        detail_mode = "component-parts"
        if len(leaves) > MAX_DETAIL_PARTS:
            leaves = [built]
            detail_mode = "coordination-envelope"
        boxes = [bbox_tuple(leaf) for leaf in leaves]
        overall = bbox_union(boxes)
        origin = (
            (overall[0] + overall[3]) / 2000.0,
            (overall[1] + overall[4]) / 2000.0,
            (overall[2] + overall[5]) / 2000.0,
        )
        vertices = [box_mesh(box, origin) for box in boxes]
        faces = [[face[:] for face in BOX_FACES] for _ in boxes]
        representation = add_mesh_representation(
            model,
            context=body_context,
            vertices=vertices,
            faces=faces,
            unit_scale=1.0,
        )
        assign_representation(model, product=product, representation=representation)
        matrix = np.eye(4)
        matrix[:3, 3] = origin
        edit_object_placement(model, product=product, matrix=matrix, is_si=True)
        assign_container(model, products=[product], relating_structure=spatial_parts[discipline])
        assign_representation_styles(model, shape_representation=representation, styles=[styles[discipline]])

        length_m = (overall[3] - overall[0]) / 1000.0
        width_m = (overall[4] - overall[1]) / 1000.0
        height_m = (overall[5] - overall[2]) / 1000.0
        source_volume_m3 = built.volume / 1_000_000_000.0
        set_properties(
            model,
            product,
            "Pset_OSR_Asset",
            {
                "AssetId": asset_id,
                "AssetClass": asset_class,
                "SourceGeometry": component.source,
                "SourceSha256": sha256_bytes(canonical_json({"asset_id": asset_id, "source": component.source})),
                "RevisionId": revision_id,
                "DetailMode": detail_mode,
                "LifecycleState": "design-reference",
            },
        )
        set_properties(
            model,
            product,
            "Qto_OSR_CoordinationEnvelope",
            {
                "OverallLength": round(length_m, 6),
                "OverallWidth": round(width_m, 6),
                "OverallHeight": round(height_m, 6),
                "SourceNetVolume": round(source_volume_m3, 6),
                "RepresentationParts": len(boxes),
            },
        )
        products[asset_id] = product
        product_classes[asset_id] = asset_class
        product_names[asset_id] = component.label
        index_rows.append(
            {
                "asset_id": asset_id,
                "name": component.label,
                "asset_class": asset_class,
                "ifc_class": product.is_a(),
                "ifc_predefined_type": getattr(product, "PredefinedType", None),
                "discipline": discipline,
                "source_geometry": component.source,
                "detail_mode": detail_mode,
                "representation_parts": len(boxes),
                "bbox_m": [round(value / 1000.0, 6) for value in overall],
                "source_net_volume_m3": round(source_volume_m3, 6),
            }
        )

    schedule_rows, assignments = add_schedule(model, products, product_classes, product_names)
    for work_schedule in model.by_type("IfcWorkSchedule"):
        work_schedule.CreationDate = DEFAULT_START.isoformat()
    deterministic_roots(model)
    stabilize_unordered_collections(model)
    index_rows.sort(key=lambda row: row["asset_id"])
    index = {
        "schema": SCHEMA,
        "revision_id": revision_id,
        "canonical_source_sha256": source_hash,
        "ifc_schema": "IFC4X3",
        "ifcopenshell_version": version("ifcopenshell"),
        "authority_boundary": {
            "authoritative": ["OSR alignment rules", "OSR parametric civil geometry", "OSR validation gates"],
            "bonsai_ifc": ["federation", "civil detail review", "quantities", "drawings", "4D construction sequence"],
        },
        "summary": {
            "assets": len(index_rows),
            "ifc_classes": dict(sorted(Counter(row["ifc_class"] for row in index_rows).items())),
            "disciplines": dict(sorted(Counter(row["discipline"] for row in index_rows).items())),
            "interface_checks": len(assert_integration_checks()),
            "construction_tasks": len(schedule_rows),
        },
        "objects": index_rows,
        "validation": [asdict(check) for check in assert_integration_checks()],
        "limitations": twin["limitations"] + [
            "IFC geometry is deterministic review/detail geometry, not engineer-released analysis geometry.",
            "Bonsai is not used to calculate alignment radii, transitions, cant, sight distance, earthworks, or structural capacity.",
        ],
    }
    sequence = {
        "schema": "org.opensourcerail.bonsai-construction-sequence.v1",
        "revision_id": revision_id,
        "schedule_name": "OSR civil fabrication and construction sequence",
        "start": DEFAULT_START.isoformat(),
        "tasks": schedule_rows,
        "product_assignments": assignments,
        "animation": {
            "fps": 24,
            "duration_seconds": 48,
            "frame_start": 1,
            "frame_end": 1152,
            "semantics": "normalized review animation; IFC task dates retain planning durations",
        },
    }
    return model, index, sequence


def validate_written(ifc_path: Path, index: dict[str, Any], sequence: dict[str, Any]) -> dict[str, Any]:
    reopened = ifcopenshell.open(str(ifc_path))
    tagged = {product.Tag for product in reopened.by_type("IfcProduct") if getattr(product, "Tag", None)}
    expected = {row["asset_id"] for row in index["objects"]}
    checks = [
        {"id": "ifc4x3-schema", "passed": reopened.schema == "IFC4X3", "observed": reopened.schema},
        {"id": "stable-assets", "passed": tagged == expected, "observed": len(tagged)},
        {"id": "railway-spatial-root", "passed": len(reopened.by_type("IfcRailway")) == 1, "observed": len(reopened.by_type("IfcRailway"))},
        {"id": "railway-parts", "passed": len(reopened.by_type("IfcRailwayPart")) == 4, "observed": len(reopened.by_type("IfcRailwayPart"))},
        {"id": "alignment-reference", "passed": len(reopened.by_type("IfcAlignment")) == 1, "observed": len(reopened.by_type("IfcAlignment"))},
        {"id": "construction-schedule", "passed": len(reopened.by_type("IfcWorkSchedule")) == 1, "observed": len(reopened.by_type("IfcTask"))},
        {"id": "task-index-match", "passed": len(reopened.by_type("IfcTask")) == len(sequence["tasks"]), "observed": len(sequence["tasks"])},
        {"id": "all-interface-checks", "passed": all(item["passed"] for item in index["validation"]), "observed": len(index["validation"])},
    ]
    return {
        "schema": "org.opensourcerail.bonsai-ifc-validation.v1",
        "passed": all(check["passed"] for check in checks),
        "checks": checks,
        "ifc_sha256": sha256_bytes(ifc_path.read_bytes()),
        "ifc_size_bytes": ifc_path.stat().st_size,
        "entity_count": sum(1 for _ in reopened),
    }


def write_outputs(out_dir: Path, *, alignment_path: Path | None, revision_id: str) -> dict[str, Path]:
    alignment_input = load_alignment(alignment_path)
    model, index, sequence = build_model(alignment_input=alignment_input, revision_id=revision_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "ifc": out_dir / "civil-coordination.ifc",
        "index": out_dir / "civil-coordination.index.json",
        "sequence": out_dir / "civil-construction-sequence.json",
        "validation": out_dir / "civil-coordination.validation.json",
    }
    model.write(str(paths["ifc"]))
    validation = validate_written(paths["ifc"], index, sequence)
    if not validation["passed"]:
        raise ValueError("written civil IFC failed validation")
    index["ifc_sha256"] = validation["ifc_sha256"]
    index["ifc_size_bytes"] = validation["ifc_size_bytes"]
    paths["index"].write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    paths["sequence"].write_text(json.dumps(sequence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    paths["validation"].write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--alignment-input", type=Path)
    parser.add_argument("--revision-id", default="working-tree")
    args = parser.parse_args(argv)
    paths = write_outputs(args.out_dir, alignment_path=args.alignment_input, revision_id=args.revision_id)
    for kind, path in paths.items():
        print(f"{kind}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
