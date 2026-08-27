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
import math
import sys
import tomllib
import uuid
import zipfile
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from importlib.metadata import version
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Iterable

import numpy as np
from bcf.v3.bcfxml import BcfXml
from xsdata.models.datatype import XmlDateTime

REPO_ROOT = Path(__file__).resolve().parents[2]
MECHANICAL_SRC = REPO_ROOT / "mechanical-py/src"
if str(MECHANICAL_SRC) not in sys.path:
    sys.path.insert(0, str(MECHANICAL_SRC))

import ifcopenshell
import ifcopenshell.validate as ifc_validate
from ifctester import ids as ids_module
from ifctester import open as open_ids
from ifctester import reporter as ids_reporter
from ifcopenshell.api.aggregate import assign_object
from ifcopenshell.api.context import add_context
from ifcopenshell.api.geometry import (
    add_mesh_representation,
    assign_representation,
    edit_object_placement,
)
from ifcopenshell.api.georeference import add_georeferencing, edit_georeferencing
from ifcopenshell.api.project import create_file
from ifcopenshell.api.pset import add_pset, add_qto, edit_pset, edit_qto
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
from osr_mech.civil.quantity_model import structure_quantities_per_km


SCHEMA = "org.opensourcerail.bonsai-civil-ifc.v1"
NAMESPACE = uuid.UUID("5b6994b4-1642-48df-a10b-796985904590")
FIXED_HEADER_TIMESTAMP = "2026-01-01T00:00:00"
FIXED_REVIEW_TIMESTAMP = "2026-01-01T00:00:00Z"
FIXED_ZIP_TIMESTAMP = (2026, 1, 1, 0, 0, 0)
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


def stable_uuid(value: str) -> str:
    return str(uuid.uuid5(NAMESPACE, value))


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
    if asset_class in {
        "civil.pier",
        "civil.decked-pi-beam",
        "civil.walkway-cassette",
        "civil.u-girder",
        "civil.station-deck-interface",
    }:
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
        "civil.decked-pi-beam": ("IfcBeam", "GIRDER_SEGMENT"),
        "civil.walkway-cassette": ("IfcSlab", "USERDEFINED"),
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


def set_quantities(
    model: ifcopenshell.file,
    product: Any,
    name: str,
    values: dict[str, Any],
) -> None:
    """Attach measured values as native IFC quantities, not generic properties."""

    quantity_set = add_qto(model, product=product, name=name)
    quantity_set.MethodOfMeasurement = "OSR deterministic geometry v1"
    edit_qto(model, qto=quantity_set, properties=values)


def validate_georeferencing(value: Any) -> dict[str, Any] | None:
    """Validate an explicit survey/GIS transform without inventing project coordinates."""

    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError("georeferencing must be an object")
    allowed = {
        "crs_name",
        "description",
        "geodetic_datum",
        "vertical_datum",
        "map_projection",
        "map_zone",
        "eastings",
        "northings",
        "orthogonal_height",
        "x_axis_abscissa",
        "x_axis_ordinate",
        "scale",
        "source",
    }
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ValueError(f"unsupported georeferencing fields: {', '.join(unknown)}")
    required = {"crs_name", "eastings", "northings", "orthogonal_height"}
    missing = sorted(required - set(value))
    if missing:
        raise ValueError(f"georeferencing requires: {', '.join(missing)}")
    crs_name = value["crs_name"]
    if (
        not isinstance(crs_name, str)
        or not crs_name.startswith("EPSG:")
        or not crs_name[5:].isdigit()
    ):
        raise ValueError("georeferencing crs_name must be a single EPSG identifier such as EPSG:9306")
    numeric_fields = {
        "eastings": 0.0,
        "northings": 0.0,
        "orthogonal_height": 0.0,
        "x_axis_abscissa": 1.0,
        "x_axis_ordinate": 0.0,
        "scale": 1.0,
    }
    result = dict(value)
    for field, default in numeric_fields.items():
        number = result.get(field, default)
        if (
            isinstance(number, bool)
            or not isinstance(number, (int, float))
            or not math.isfinite(number)
        ):
            raise ValueError(f"georeferencing {field} must be a finite number")
        result[field] = float(number)
    if result["scale"] <= 0.0:
        raise ValueError("georeferencing scale must be greater than zero")
    if math.hypot(result["x_axis_abscissa"], result["x_axis_ordinate"]) < 1e-12:
        raise ValueError("georeferencing x-axis direction must be non-zero")
    for field in (
        "description",
        "geodetic_datum",
        "vertical_datum",
        "map_projection",
        "map_zone",
        "source",
    ):
        if field in result and (not isinstance(result[field], str) or not result[field].strip()):
            raise ValueError(f"georeferencing {field} must be a non-empty string")
    return result


def load_alignment(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    points = value.get("points")
    if not isinstance(points, list) or len(points) < 2:
        raise ValueError("alignment input requires at least two local XYZ points")
    for point in points:
        if (
            not isinstance(point, list)
            or len(point) != 3
            or not all(
                not isinstance(item, bool)
                and isinstance(item, (int, float))
                and math.isfinite(item)
                for item in point
            )
        ):
            raise ValueError("alignment points must be numeric [x, y, z] triples in metres")
    if "georeferencing" in value:
        value["georeferencing"] = validate_georeferencing(value["georeferencing"])
    return value


def apply_georeferencing(
    model: ifcopenshell.file,
    project: Any,
    alignment_input: dict[str, Any] | None,
) -> dict[str, Any]:
    """Write IFC map conversion only when an explicit, validated CRS is supplied."""

    georeferencing = validate_georeferencing((alignment_input or {}).get("georeferencing"))
    if georeferencing is None:
        result = {
            "mode": "local-engineering-grid",
            "native_ifc_georeferencing": False,
            "status": "project-crs-unresolved",
            "source": "No accepted CRS/map conversion supplied",
        }
    else:
        add_georeferencing(model, ifc_class="IfcMapConversion", name=georeferencing["crs_name"])
        projected_crs = {
            "Name": georeferencing["crs_name"],
        }
        for source_name, ifc_name in (
            ("description", "Description"),
            ("geodetic_datum", "GeodeticDatum"),
            ("vertical_datum", "VerticalDatum"),
            ("map_projection", "MapProjection"),
            ("map_zone", "MapZone"),
        ):
            if source_name in georeferencing:
                projected_crs[ifc_name] = georeferencing[source_name]
        coordinate_operation = {
            "Eastings": georeferencing["eastings"],
            "Northings": georeferencing["northings"],
            "OrthogonalHeight": georeferencing["orthogonal_height"],
            "XAxisAbscissa": georeferencing["x_axis_abscissa"],
            "XAxisOrdinate": georeferencing["x_axis_ordinate"],
            "Scale": georeferencing["scale"],
        }
        edit_georeferencing(
            model,
            projected_crs=projected_crs,
            coordinate_operation=coordinate_operation,
        )
        result = {
            "mode": "ifc-map-conversion",
            "native_ifc_georeferencing": True,
            "status": "declared-from-project-input",
            "crs_name": georeferencing["crs_name"],
            "source": georeferencing.get("source", "Alignment input"),
            "map_conversion": {
                "eastings": georeferencing["eastings"],
                "northings": georeferencing["northings"],
                "orthogonal_height": georeferencing["orthogonal_height"],
                "x_axis_abscissa": georeferencing["x_axis_abscissa"],
                "x_axis_ordinate": georeferencing["x_axis_ordinate"],
                "scale": georeferencing["scale"],
            },
        }
    pset_values = {
        "CoordinateReferenceStatus": result["status"],
        "NativeIfcGeoreferencing": result["native_ifc_georeferencing"],
        "TransformSource": result["source"],
    }
    if result.get("crs_name"):
        pset_values["ProjectedCrsName"] = result["crs_name"]
    set_properties(model, project, "Pset_OSR_Georeferencing", pset_values)
    return result


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
        "viaduct": {
            "civil.pier",
            "civil.decked-pi-beam",
            "civil.walkway-cassette",
            "civil.u-girder",
            "civil.trackform",
            "track.rail",
        },
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
        "IfcElementQuantity": ("Quantities",),
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
    cost_model_path = REPO_ROOT / "lib/templates/civil-cost-model.toml"
    cost_model = tomllib.loads(cost_model_path.read_text(encoding="utf-8"))
    cost_model_hash = sha256_bytes(cost_model_path.read_bytes())
    civil_quantities = structure_quantities_per_km()
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
    georeferencing = apply_georeferencing(model, project, alignment_input)

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
    set_properties(
        model,
        project,
        "Pset_OSR_CostModel",
        {
            "Maturity": cost_model["schema"]["maturity"],
            "CostModelSha256": cost_model_hash,
            "AtGradeUsdPerRouteKm": float(cost_model["civil_usd_per_km"]["at_grade"]),
            "ElevatedUsdPerRouteKm": float(cost_model["civil_usd_per_km"]["elevated"]),
            "BridgeUsdPerRouteKm": float(cost_model["civil_usd_per_km"]["bridge"]),
            "Regeneration": "python3 scripts/generate-civil-cost-model.py",
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
        # These four discipline containers are a vertical organisation of the
        # railway, as described by the IFC4.3 railway-domain guidance.
        part.UsageType = "VERTICAL"
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
        if predefined_type == "USERDEFINED":
            product.ObjectType = asset_class
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
        set_quantities(
            model,
            product,
            "OSR_CoordinationEnvelopeQuantities",
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
    for row in index_rows:
        row["ifc_guid"] = products[row["asset_id"]].GlobalId
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
        "cost_model": {
            "path": "lib/templates/civil-cost-model.toml",
            "sha256": cost_model_hash,
            "maturity": cost_model["schema"]["maturity"],
            "civil_usd_per_km": cost_model["civil_usd_per_km"],
            "quantities_per_route_km": civil_quantities,
        },
        "georeferencing": georeferencing,
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


def build_civil_ids(index: dict[str, Any]) -> ids_module.Ids:
    """Build the information requirements for the generated IFC exchange."""

    document = ids_module.Ids(
        title="OSR IFC4.3 civil information requirements",
        version="1.0",
        description=(
            "Machine-checkable requirements for the OpenSourceRail design-reference "
            "civil coordination exchange. Passing does not constitute construction release."
        ),
        author="OpenSourceRail",
        date="2026-01-01",
        purpose="Civil BIM federation, coordination, and review",
        milestone="Design reference",
    )
    concrete_elements = sorted({row["ifc_class"].upper() for row in index["objects"]})
    asset_specification = ids_module.Specification(
        name="Civil elements carry stable OSR identity and coordination quantities",
        description="Every exported physical or virtual asset remains traceable to its deterministic source.",
        instructions="Do not accept untagged or revision-ambiguous objects into the civil federation.",
        minOccurs=1,
        maxOccurs="unbounded",
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-CIV-001",
    )
    asset_specification.applicability.append(
        ids_module.Entity(name=ids_module.Restriction({"enumeration": concrete_elements}))
    )
    asset_specification.requirements.extend(
        [
            ids_module.Attribute(name="Name"),
            ids_module.Attribute(name="Tag"),
            ids_module.Property(propertySet="Pset_OSR_Asset", baseName="AssetId"),
            ids_module.Property(propertySet="Pset_OSR_Asset", baseName="AssetClass"),
            ids_module.Property(propertySet="Pset_OSR_Asset", baseName="SourceSha256"),
            ids_module.Property(propertySet="Pset_OSR_Asset", baseName="RevisionId"),
            ids_module.Property(propertySet="Pset_OSR_Asset", baseName="LifecycleState"),
            ids_module.Property(
                propertySet="OSR_CoordinationEnvelopeQuantities", baseName="OverallLength"
            ),
            ids_module.Property(
                propertySet="OSR_CoordinationEnvelopeQuantities", baseName="OverallWidth"
            ),
            ids_module.Property(
                propertySet="OSR_CoordinationEnvelopeQuantities", baseName="OverallHeight"
            ),
        ]
    )
    document.specifications.append(asset_specification)

    alignment_specification = ids_module.Specification(
        name="Alignment exposes authority and revision",
        description="The IFC axis declares that detailed alignment engineering remains upstream in OSR.",
        minOccurs=1,
        maxOccurs=1,
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-ALN-001",
    )
    alignment_specification.applicability.append(ids_module.Entity(name="IFCALIGNMENT"))
    alignment_specification.requirements.extend(
        [
            ids_module.Attribute(name="Name"),
            ids_module.Property(propertySet="Pset_OSR_AlignmentAuthority", baseName="Authority"),
            ids_module.Property(propertySet="Pset_OSR_AlignmentAuthority", baseName="RevisionId"),
            ids_module.Property(propertySet="Pset_OSR_AlignmentAuthority", baseName="GeometryRole"),
        ]
    )
    document.specifications.append(alignment_specification)

    provenance_specification = ids_module.Specification(
        name="Project declares deterministic provenance and release status",
        description="The exchange identifies its source revision, canonical content hash, and maturity boundary.",
        minOccurs=1,
        maxOccurs=1,
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-PROV-001",
    )
    provenance_specification.applicability.append(ids_module.Entity(name="IFCPROJECT"))
    provenance_specification.requirements.extend(
        [
            ids_module.Property(propertySet="Pset_OSR_Provenance", baseName="CanonicalSourceSha256"),
            ids_module.Property(propertySet="Pset_OSR_Provenance", baseName="RevisionId"),
            ids_module.Property(propertySet="Pset_OSR_Provenance", baseName="GeometryAuthority"),
            ids_module.Property(propertySet="Pset_OSR_Provenance", baseName="ReleaseStatus"),
            ids_module.Property(
                propertySet="Pset_OSR_Georeferencing",
                baseName="CoordinateReferenceStatus",
            ),
        ]
    )
    document.specifications.append(provenance_specification)
    return document


def write_and_validate_ids(
    ifc_path: Path,
    ids_path: Path,
    report_path: Path,
    index: dict[str, Any],
) -> dict[str, Any]:
    requirements = build_civil_ids(index)
    requirements.to_xml(ids_path)
    reopened_requirements = open_ids(ids_path)
    if reopened_requirements is None:
        raise ValueError("written civil IDS could not be reopened")
    reopened_requirements.validate(
        ifcopenshell.open(str(ifc_path)),
        should_filter_version=True,
        filepath=ifc_path.name,
    )
    report = ids_reporter.Json(reopened_requirements)
    report.report()
    result = json.loads(report.to_string())
    result.update(
        {
            "schema": "org.opensourcerail.bonsai-civil-ids-report.v1",
            "date": FIXED_REVIEW_TIMESTAMP,
            "filepath": ifc_path.name,
            "filename": ifc_path.name,
            "ids_filename": ids_path.name,
        }
    )
    # IfcTester records passing entities in sets. Preserve its full evidence but
    # canonicalise those arrays before hashing or presenting the report.
    for specification in result["specifications"]:
        specification["applicable_entities"].sort(
            key=lambda item: (item.get("global_id") or "", item.get("id") or 0)
        )
        for requirement in specification["requirements"]:
            for key in ("passed_entities", "failed_entities"):
                requirement[key].sort(
                    key=lambda item: (item.get("global_id") or "", item.get("id") or 0)
                )
    report_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not result["status"]:
        raise ValueError("written civil IFC failed its IDS information requirements")
    return result


def canonicalize_zip(source: Path, destination: Path) -> None:
    """Rewrite a ZIP with stable ordering and metadata for byte reproducibility."""

    with zipfile.ZipFile(source, "r") as incoming, zipfile.ZipFile(
        destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as outgoing:
        for name in sorted(incoming.namelist()):
            info = zipfile.ZipInfo(name, date_time=FIXED_ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 0
            info.external_attr = 0
            outgoing.writestr(info, incoming.read(name), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def _bbox_target(rows: list[dict[str, Any]]) -> np.ndarray:
    if not rows:
        return np.array([160.0, 0.0, 0.0], dtype=np.float64)
    union = bbox_union(tuple(row["bbox_m"]) for row in rows)
    return np.array(
        [(union[0] + union[3]) / 2.0, (union[1] + union[4]) / 2.0, (union[2] + union[5]) / 2.0],
        dtype=np.float64,
    )


def write_coordination_bcf(
    ifc_path: Path,
    bcf_path: Path,
    bcf_index_path: Path,
    index: dict[str, Any],
    alignment_input: dict[str, Any] | None,
) -> dict[str, Any]:
    """Write deterministic BCF 3.0 release issues linked to IFC GUIDs."""

    model = ifcopenshell.open(str(ifc_path))
    alignment = model.by_type("IfcAlignment")[0]
    decisions = {
        issue["id"]: issue
        for issue in (alignment_input or {}).get("coordination_issues", [])
        if isinstance(issue, dict) and isinstance(issue.get("id"), str)
    }
    bcf_statuses = {
        "open": "Open",
        "in-progress": "In Progress",
        "resolved": "Resolved",
        "closed": "Closed",
    }
    topic_definitions = [
        {
            "key": "alignment-survey-authority",
            "title": "Replace planning alignment with accepted survey geometry",
            "description": (
                "The current IfcAlignment is a deterministic coordination axis. Before design release, "
                "accept the project CRS, surveyed control, horizontal and vertical geometry, transitions, "
                "cant, tolerances, and design-speed checks in the authoritative OSR alignment model."
            ),
            "rows": [],
            "ifc_guids": [alignment.GlobalId],
            "target": np.array([160.0, 0.0, 0.0], dtype=np.float64),
        },
        {
            "key": "station-deck-release",
            "title": "Release elevated station deck structural design",
            "description": (
                "The elevated station deck is a coordination interface only. Resolve governing loads, "
                "member and reinforcement design, bearings, movements, drainage, seismic detailing, "
                "constructability, and engineer acceptance before construction use."
            ),
            "rows": [row for row in index["objects"] if row["asset_class"] == "civil.station-deck-interface"],
        },
        {
            "key": "viaduct-design-release",
            "title": "Complete viaduct span, bearing, pier, and foundation schedule",
            "description": (
                "Decked Pi-beams, walkway cassettes and piers currently define deterministic coordination envelopes. Confirm span "
                "arrangement, bearing schedule, ground model, foundation selection, load combinations, "
                "dynamic response, durability, drainage, and engineer-released reinforcement details."
            ),
            "rows": [
                row
                for row in index["objects"]
                if row["asset_class"]
                in {"civil.decked-pi-beam", "civil.walkway-cassette", "civil.u-girder", "civil.pier"}
            ],
        },
    ]
    built_in_keys = {definition["key"] for definition in topic_definitions}
    rows_by_asset_id = {row["asset_id"]: row for row in index["objects"]}
    for issue_id in sorted(set(decisions) - built_in_keys):
        decision = decisions[issue_id]
        asset_ids = decision.get("asset_ids", [])
        if not issue_id.startswith("custom-") or not isinstance(asset_ids, list) or not asset_ids:
            raise ValueError(f"invalid custom coordination issue {issue_id!r}")
        title = str(decision.get("title", "")).strip()
        description = str(decision.get("description", "")).strip()
        if not (4 <= len(title) <= 160) or not (12 <= len(description) <= 2_000):
            raise ValueError(f"custom coordination issue {issue_id!r} has invalid title or description")
        missing_asset_ids = sorted(set(asset_ids) - set(rows_by_asset_id))
        if missing_asset_ids:
            raise ValueError(
                f"custom coordination issue {issue_id!r} selects unknown assets {missing_asset_ids!r}"
            )
        topic_definitions.append(
            {
                "key": issue_id,
                "title": title,
                "description": description,
                "rows": [rows_by_asset_id[asset_id] for asset_id in sorted(set(asset_ids))],
            }
        )

    bcf = BcfXml.create_new(project_name="OpenSourceRail civil coordination")
    if bcf.project is None:
        raise ValueError("BCF project metadata was not created")
    bcf.project.project_id = stable_uuid("bcf-project|civil-coordination")
    topic_rows = []
    for definition in topic_definitions:
        rows = definition["rows"]
        decision = decisions.get(definition["key"], {})
        intent_status = decision.get("status", "open")
        if intent_status not in bcf_statuses:
            raise ValueError(f"unsupported coordination status {intent_status!r}")
        bcf_status = bcf_statuses[intent_status]
        resolution = str(decision.get("resolution", "")).strip()
        reviewed_by = str(decision.get("reviewed_by", "")).strip()
        assignee = str(decision.get("assignee", "")).strip()
        description = definition["description"]
        if resolution:
            description += f"\n\nRecorded resolution: {resolution}"
        if reviewed_by:
            description += f"\nReviewed by: {reviewed_by}"
        selected_guids = definition.get("ifc_guids") or [row["ifc_guid"] for row in rows]
        target = definition.get("target") if "target" in definition else _bbox_target(rows)
        handler = bcf.add_topic(
            definition["title"],
            description,
            "engineering@opensourcerail.org",
            topic_type="Engineering",
            topic_status=bcf_status,
        )
        generated_topic_guid = handler.guid
        topic_guid = stable_uuid(f"bcf-topic|{definition['key']}")
        bcf.topics.pop(generated_topic_guid)
        handler.topic.guid = topic_guid
        handler.topic.creation_date = XmlDateTime.from_string(FIXED_REVIEW_TIMESTAMP)
        if assignee:
            handler.topic.assigned_to = assignee
        handler._topic_dir = Path(topic_guid)
        bcf.topics[topic_guid] = handler

        viewpoint = handler.add_viewpoint_from_point_and_guids(target, *selected_guids)
        generated_viewpoint_name = viewpoint.guid + ".bcfv"
        viewpoint_guid = stable_uuid(f"bcf-viewpoint|{definition['key']}")
        viewpoint.visualization_info.guid = viewpoint_guid
        handler.viewpoints.pop(generated_viewpoint_name)
        handler.viewpoints[viewpoint_guid + ".bcfv"] = viewpoint
        markup_viewpoint = handler.topic.viewpoints.view_point[-1]
        markup_viewpoint.guid = viewpoint_guid
        markup_viewpoint.viewpoint = viewpoint_guid + ".bcfv"
        topic_rows.append(
            {
                "topic_guid": topic_guid,
                "viewpoint_guid": viewpoint_guid,
                "title": definition["title"],
                "description": description,
                "type": "Engineering",
                "status": bcf_status,
                "intent_status": intent_status,
                "issue_id": definition["key"],
                "assignee": assignee,
                "resolution": resolution,
                "reviewed_by": reviewed_by,
                "asset_ids": [row["asset_id"] for row in rows],
                "ifc_guids": selected_guids,
            }
        )

    with TemporaryDirectory(prefix="osr-bcf-") as temporary:
        generated = Path(temporary) / "generated.bcf"
        bcf.save(generated)
        canonicalize_zip(generated, bcf_path)
    result = {
        "schema": "org.opensourcerail.bonsai-civil-bcf-index.v1",
        "bcf_version": "3.0",
        "project_id": bcf.project.project_id,
        "ifc_filename": ifc_path.name,
        "topic_count": len(topic_rows),
        "open_topic_count": sum(
            row["intent_status"] in {"open", "in-progress"} for row in topic_rows
        ),
        "topics": topic_rows,
    }
    bcf_index_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def validate_coordination_bcf(bcf_path: Path, ifc_path: Path) -> dict[str, Any]:
    coordination = BcfXml.load(bcf_path)
    if coordination is None:
        raise ValueError("written civil BCF could not be reopened")
    model = ifcopenshell.open(str(ifc_path))
    model_guids = {root.GlobalId for root in model.by_type("IfcRoot")}
    selected_guids: list[str] = []
    for topic in coordination.topics.values():
        for viewpoint in topic.viewpoints.values():
            selected_guids.extend(viewpoint.get_selected_guids() or [])
    return {
        "version": coordination.version.version_id,
        "topic_count": len(coordination.topics),
        "selected_ifc_guids": len(selected_guids),
        "all_selected_guids_resolve": bool(selected_guids) and set(selected_guids).issubset(model_guids),
    }


def validate_written(
    paths: dict[str, Path],
    index: dict[str, Any],
    sequence: dict[str, Any],
    ids_report: dict[str, Any],
    bcf_index: dict[str, Any],
) -> dict[str, Any]:
    ifc_path = paths["ifc"]
    reopened = ifcopenshell.open(str(ifc_path))
    schema_logger = ifc_validate.json_logger()
    ifc_validate.validate(str(ifc_path), schema_logger, express_rules=True)
    schema_issues = []
    for issue in schema_logger.statements:
        instance = issue.get("instance")
        schema_issues.append(
            {
                "level": issue.get("level"),
                "type": issue.get("type"),
                "message": (issue.get("message") or "").splitlines()[0],
                "attribute": issue.get("attribute"),
                "instance_id": instance.id() if instance is not None else None,
                "instance_type": instance.is_a() if instance is not None else None,
            }
        )
    schema_issues.sort(
        key=lambda issue: (
            issue["instance_id"] or 0,
            issue["attribute"] or "",
            issue["message"] or "",
        )
    )
    bcf_validation = validate_coordination_bcf(paths["bcf"], ifc_path)
    tagged = {product.Tag for product in reopened.by_type("IfcProduct") if getattr(product, "Tag", None)}
    expected = {row["asset_id"] for row in index["objects"]}
    projected_crs = reopened.by_type("IfcProjectedCRS")
    map_conversions = reopened.by_type("IfcMapConversion")
    georeferencing = index["georeferencing"]
    georeferencing_matches = (
        len(projected_crs) == len(map_conversions) == 1
        and georeferencing["native_ifc_georeferencing"]
        and projected_crs[0].Name == georeferencing["crs_name"]
    ) or (
        not georeferencing["native_ifc_georeferencing"]
        and not projected_crs
        and not map_conversions
    )
    checks = [
        {"id": "ifc4x3-schema", "passed": reopened.schema == "IFC4X3", "observed": reopened.schema},
        {"id": "ifc-schema-conformance", "passed": not schema_issues, "observed": len(schema_issues)},
        {"id": "stable-assets", "passed": tagged == expected, "observed": len(tagged)},
        {"id": "railway-spatial-root", "passed": len(reopened.by_type("IfcRailway")) == 1, "observed": len(reopened.by_type("IfcRailway"))},
        {"id": "railway-parts", "passed": len(reopened.by_type("IfcRailwayPart")) == 4, "observed": len(reopened.by_type("IfcRailwayPart"))},
        {"id": "alignment-reference", "passed": len(reopened.by_type("IfcAlignment")) == 1, "observed": len(reopened.by_type("IfcAlignment"))},
        {
            "id": "georeferencing-contract",
            "passed": georeferencing_matches,
            "observed": georeferencing["mode"],
        },
        {"id": "construction-schedule", "passed": len(reopened.by_type("IfcWorkSchedule")) == 1, "observed": len(reopened.by_type("IfcTask"))},
        {"id": "task-index-match", "passed": len(reopened.by_type("IfcTask")) == len(sequence["tasks"]), "observed": len(sequence["tasks"])},
        {"id": "all-interface-checks", "passed": all(item["passed"] for item in index["validation"]), "observed": len(index["validation"])},
        {"id": "ids-information-requirements", "passed": ids_report["status"], "observed": f"{ids_report['total_specifications_pass']}/{ids_report['total_specifications']} specifications"},
        {"id": "bcf3-coordination-topics", "passed": bcf_validation["version"] == "3.0" and bcf_validation["topic_count"] == bcf_index["topic_count"], "observed": bcf_validation["topic_count"]},
        {"id": "bcf-viewpoint-ifc-links", "passed": bcf_validation["all_selected_guids_resolve"], "observed": bcf_validation["selected_ifc_guids"]},
    ]
    return {
        "schema": "org.opensourcerail.bonsai-ifc-validation.v1",
        "passed": all(check["passed"] for check in checks),
        "checks": checks,
        "ifc_sha256": sha256_bytes(ifc_path.read_bytes()),
        "ifc_size_bytes": ifc_path.stat().st_size,
        "artifact_sha256": {
            kind: sha256_bytes(paths[kind].read_bytes())
            for kind in ("ifc", "ids", "ids_report", "bcf", "bcf_index")
        },
        "ids": {
            "specifications": ids_report["total_specifications"],
            "requirements": ids_report["total_requirements"],
            "checks": ids_report["total_checks"],
        },
        "bcf": bcf_validation,
        "schema_validation": {
            "engine": f"IfcOpenShell {version('ifcopenshell')}",
            "express_rules": True,
            "issue_count": len(schema_issues),
            "issues": schema_issues,
        },
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
        "ids": out_dir / "civil-information-requirements.ids",
        "ids_report": out_dir / "civil-information-requirements.report.json",
        "bcf": out_dir / "civil-coordination-issues.bcf",
        "bcf_index": out_dir / "civil-coordination-issues.index.json",
        "validation": out_dir / "civil-coordination.validation.json",
    }
    model.write(str(paths["ifc"]))
    ids_report = write_and_validate_ids(paths["ifc"], paths["ids"], paths["ids_report"], index)
    bcf_index = write_coordination_bcf(
        paths["ifc"], paths["bcf"], paths["bcf_index"], index, alignment_input
    )
    validation = validate_written(paths, index, sequence, ids_report, bcf_index)
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
