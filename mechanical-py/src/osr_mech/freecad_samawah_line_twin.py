"""Build and animate the source-linked Samawah Line 1 FreeCAD twin."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from pathlib import Path

import FreeCAD as App  # type: ignore[import-not-found]
import FreeCADGui as Gui  # type: ignore[import-not-found]
import Part  # type: ignore[import-not-found]
from PySide import QtCore  # type: ignore[import-not-found]

from osr_mech.samawah_line_twin import (
    ANIMATED_TRAIN_COUNT,
    OVERVIEW_ROTATION_DEG,
    OVERVIEW_SCALE,
    TWIN_SCHEMA,
    SamawahLineTwin,
    assert_twin_checks,
    default_city_dir,
    load_samawah_line_twin,
    point_at_chainage,
    representative_train_states,
    station_stop_motion,
    write_manifest,
)


TRACK_Z_MM = 0.0
TRAIN_Z_MM = 3.0
STATION_COLOURS: dict[str, tuple[float, float, float]] = {
    "terminal": (0.88, 0.31, 0.18),
    "standard": (0.96, 0.70, 0.20),
    "major": (0.94, 0.45, 0.12),
    "interchange-elevated": (0.48, 0.23, 0.74),
    "halt": (0.45, 0.55, 0.62),
    "depot-terminal": (0.78, 0.12, 0.20),
}


def _safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", value.strip()).strip("_") or "Object"
    if cleaned[0].isdigit():
        cleaned = f"OSR_{cleaned}"
    return cleaned[:72]


def _local_xy(twin: SamawahLineTwin, easting_m: float, northing_m: float) -> tuple[float, float]:
    origin = twin.alignment[0]
    x = easting_m - origin.easting_m
    y = northing_m - origin.northing_m
    angle = math.radians(OVERVIEW_ROTATION_DEG)
    return (
        x * math.cos(angle) - y * math.sin(angle),
        x * math.sin(angle) + y * math.cos(angle),
    )


def _point(twin: SamawahLineTwin, chainage_m: float) -> tuple[float, float, float]:
    easting, northing, heading = point_at_chainage(twin, chainage_m)
    x, y = _local_xy(twin, easting, northing)
    return x, y, heading + OVERVIEW_ROTATION_DEG


def _overview_bounds(
    twin: SamawahLineTwin,
    *,
    aspect_ratio: float,
    margin: float = 900.0,
) -> tuple[float, float, float, float]:
    local_points = [
        _local_xy(twin, item.easting_m, item.northing_m) for item in twin.alignment
    ]
    xmin = min(point[0] for point in local_points) - margin
    xmax = max(point[0] for point in local_points) + margin
    ymin = min(point[1] for point in local_points) - margin
    ymax = max(point[1] for point in local_points) + margin
    x_span = xmax - xmin
    y_span = ymax - ymin
    if x_span / y_span > aspect_ratio:
        target_y_span = x_span / aspect_ratio
        padding = (target_y_span - y_span) / 2.0
        ymin -= padding
        ymax += padding
    else:
        target_x_span = y_span * aspect_ratio
        padding = (target_x_span - x_span) / 2.0
        xmin -= padding
        xmax += padding
    return xmin, xmax, ymin, ymax


def _range_points(
    twin: SamawahLineTwin,
    start_m: float,
    end_m: float,
) -> list[tuple[float, float]]:
    start_x, start_y, _ = _point(twin, start_m)
    end_x, end_y, _ = _point(twin, end_m)
    points = [(start_x, start_y)]
    for item in twin.alignment:
        if start_m < item.chainage_m < end_m:
            points.append(_local_xy(twin, item.easting_m, item.northing_m))
    points.append((end_x, end_y))
    return points


def _strip_segment(
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    width: float,
    height: float,
    z: float,
    lateral_offset: float = 0.0,
):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = math.hypot(dx, dy)
    if length <= 1e-6:
        return None
    shape = Part.makeBox(
        length,
        width,
        height,
        App.Vector(0.0, lateral_offset - width / 2.0, z),
    )
    shape.rotate(
        App.Vector(0.0, 0.0, 0.0),
        App.Vector(0.0, 0.0, 1.0),
        math.degrees(math.atan2(dy, dx)),
    )
    shape.translate(App.Vector(start[0], start[1], 0.0))
    return shape


def _strip(
    points: list[tuple[float, float]],
    *,
    width: float,
    height: float,
    z: float,
    lateral_offset: float = 0.0,
):
    segments = [
        shape
        for shape in (
            _strip_segment(
                start,
                end,
                width=width,
                height=height,
                z=z,
                lateral_offset=lateral_offset,
            )
            for start, end in zip(points, points[1:])
        )
        if shape is not None
    ]
    return Part.makeCompound(segments)


def _placed_shape(shape, x: float, y: float, heading_deg: float):
    placed = shape.copy()
    placed.rotate(
        App.Vector(0.0, 0.0, 0.0),
        App.Vector(0.0, 0.0, 1.0),
        heading_deg,
    )
    placed.translate(App.Vector(x, y, 0.0))
    return placed


def _add_twin_properties(feature, *, asset_id: str, asset_class: str, state: dict) -> None:
    feature.addProperty("App::PropertyString", "AssetId", "Digital twin")
    feature.AssetId = asset_id
    feature.addProperty("App::PropertyString", "AssetClass", "Digital twin")
    feature.AssetClass = asset_class
    feature.addProperty("App::PropertyString", "OperationalStateJson", "Digital twin")
    feature.OperationalStateJson = json.dumps(state, sort_keys=True, separators=(",", ":"))


def _make_train_symbol():
    cars = []
    for centre_x in (-142.0, 0.0, 142.0):
        body = Part.makeBox(
            126.0,
            96.0,
            27.0,
            App.Vector(centre_x - 63.0, -48.0, TRAIN_Z_MM),
        )
        roof = Part.makeBox(
            96.0,
            76.0,
            8.0,
            App.Vector(centre_x - 48.0, -38.0, TRAIN_Z_MM + 27.0),
        )
        cars.extend((body, roof))
    return Part.makeCompound(cars)


def _render_feature(
    doc,
    group,
    name: str,
    label: str,
    shape,
    colour: tuple[float, float, float],
):
    """Add one coloured component to the perspective operations scene."""

    feature = doc.addObject("Part::Feature", name)
    feature.Label = label
    feature.Shape = shape
    feature.ViewObject.ShapeColor = colour
    feature.ViewObject.LineColor = tuple(max(0.0, item * 0.48) for item in colour)
    feature.addProperty("App::PropertyBool", "RenderScene", "Visualization")
    feature.RenderScene = True
    group.addObject(feature)
    return feature


def _demo_train_shapes() -> dict[str, object]:
    """Return a 49.5 m, three-car LM3 consist in the 1 mm = 1 m scene scale."""

    bodies = []
    roofs = []
    windows = []
    bogies = []
    doors = []
    car_length = 15.7
    for centre_x in (-16.5, 0.0, 16.5):
        bodies.append(
            Part.makeBox(car_length, 4.2, 3.5, App.Vector(centre_x - car_length / 2.0, 2.9, 14.2))
        )
        roofs.append(
            Part.makeBox(car_length - 1.0, 3.55, 0.55, App.Vector(centre_x - (car_length - 1.0) / 2.0, 3.225, 17.7))
        )
        windows.extend(
            (
                Part.makeBox(10.6, 0.14, 1.15, App.Vector(centre_x - 5.3, 2.74, 16.0)),
                Part.makeBox(10.6, 0.14, 1.15, App.Vector(centre_x - 5.3, 7.11, 16.0)),
            )
        )
        for axle_x in (centre_x - 5.0, centre_x + 5.0):
            bogies.append(Part.makeBox(2.8, 3.3, 0.8, App.Vector(axle_x - 1.4, 3.35, 13.45)))
        doors.extend(
            (
                Part.makeBox(2.1, 0.18, 2.65, App.Vector(centre_x - 1.05, 2.70, 14.55)),
                Part.makeBox(2.1, 0.18, 2.65, App.Vector(centre_x - 1.05, 7.12, 14.55)),
            )
        )
    windscreens = [
        Part.makeBox(0.18, 3.25, 1.35, App.Vector(-24.84, 3.38, 15.85)),
        Part.makeBox(0.18, 3.25, 1.35, App.Vector(24.66, 3.38, 15.85)),
    ]
    return {
        "body": Part.makeCompound(bodies),
        "roof": Part.makeCompound(roofs),
        "glazing": Part.makeCompound(windows + windscreens),
        "bogies": Part.makeCompound(bogies),
        "doors": Part.makeCompound(doors),
    }


def _build_perspective_scene(doc, root):
    """Build the S5 elevated-station scene used for the real-time animation."""

    group = doc.addObject("App::DocumentObjectGroup", "07_PerspectiveOperationsScene")
    group.Label = "07 Perspective operations demonstrator — S5 elevated station"
    root.addObject(group)

    ground = _render_feature(
        doc,
        group,
        "RenderDesertGround",
        "Samawah urban ground plane",
        Part.makeBox(390.0, 230.0, 1.0, App.Vector(-195.0, -115.0, -1.0)),
        (0.82, 0.72, 0.54),
    )
    ground.ViewObject.LineColor = (0.82, 0.72, 0.54)

    # A shallow blue-green crossing and a perpendicular road give the viaduct
    # readable local context without claiming survey-grade urban geometry.
    _render_feature(
        doc,
        group,
        "RenderCrossingWater",
        "S5 blue-green crossing context",
        Part.makeBox(34.0, 230.0, 0.35, App.Vector(-73.0, -115.0, 0.02)),
        (0.18, 0.55, 0.68),
    )
    road = _render_feature(
        doc,
        group,
        "RenderCrossingRoad",
        "Road beneath S5 viaduct",
        Part.makeBox(24.0, 230.0, 0.25, App.Vector(38.0, -115.0, 0.05)),
        (0.23, 0.25, 0.26),
    )
    road.ViewObject.LineColor = (0.23, 0.25, 0.26)
    road_markings = [
        Part.makeBox(0.7, 7.0, 0.08, App.Vector(49.65, y, 0.32))
        for y in range(-110, 111, 14)
    ]
    _render_feature(
        doc,
        group,
        "RenderRoadMarkings",
        "Road centre markings",
        Part.makeCompound(road_markings),
        (0.95, 0.82, 0.20),
    )

    deck = _render_feature(
        doc,
        group,
        "RenderViaductDeck",
        "S5 twin-track U-girder deck",
        Part.makeBox(390.0, 23.0, 2.6, App.Vector(-195.0, -11.5, 9.8)),
        (0.72, 0.72, 0.69),
    )
    deck.ViewObject.LineColor = (0.30, 0.31, 0.31)
    edge_beams = Part.makeCompound(
        [
            Part.makeBox(390.0, 1.0, 2.3, App.Vector(-195.0, -11.5, 12.2)),
            Part.makeBox(390.0, 1.0, 2.3, App.Vector(-195.0, 10.5, 12.2)),
        ]
    )
    _render_feature(
        doc, group, "RenderDeckEdges", "U-girder edge beams", edge_beams, (0.86, 0.85, 0.80)
    )

    piers = []
    pier_caps = []
    for x in range(-180, 181, 30):
        piers.append(Part.makeBox(2.8, 6.0, 9.8, App.Vector(x - 1.4, -3.0, 0.0)))
        pier_caps.append(Part.makeBox(7.5, 15.0, 1.0, App.Vector(x - 3.75, -7.5, 8.8)))
    _render_feature(
        doc,
        group,
        "RenderViaductPiers",
        "Precast viaduct piers",
        Part.makeCompound(piers + pier_caps),
        (0.68, 0.69, 0.67),
    )

    rails = []
    sleepers = []
    for track_y in (-5.0, 5.0):
        for rail_y in (track_y - 0.72, track_y + 0.72):
            rails.append(Part.makeBox(390.0, 0.18, 0.28, App.Vector(-195.0, rail_y - 0.09, 13.18)))
        for x in range(-193, 194, 3):
            sleepers.append(Part.makeBox(1.5, 2.8, 0.16, App.Vector(x, track_y - 1.4, 13.0)))
    _render_feature(
        doc, group, "RenderSleepers", "Twin-track sleepers", Part.makeCompound(sleepers), (0.38, 0.32, 0.27)
    )
    _render_feature(
        doc, group, "RenderRails", "Twin running rails", Part.makeCompound(rails), (0.12, 0.14, 0.16)
    )

    platforms = Part.makeCompound(
        [
            Part.makeBox(74.0, 7.5, 1.05, App.Vector(-37.0, 11.5, 12.35)),
            Part.makeBox(74.0, 7.5, 1.05, App.Vector(-37.0, -19.0, 12.35)),
        ]
    )
    _render_feature(
        doc, group, "RenderPlatforms", "S5 side platforms", platforms, (0.79, 0.76, 0.67)
    )
    tactile = Part.makeCompound(
        [
            Part.makeBox(74.0, 0.65, 0.08, App.Vector(-37.0, 11.55, 13.42)),
            Part.makeBox(74.0, 0.65, 0.08, App.Vector(-37.0, -12.20, 13.42)),
        ]
    )
    _render_feature(
        doc, group, "RenderTactileEdges", "Yellow tactile platform edges", tactile, (0.96, 0.69, 0.08)
    )

    columns = []
    roofs = []
    for platform_y in (-15.0, 15.0):
        for x in (-28.0, -14.0, 0.0, 14.0, 28.0):
            columns.append(Part.makeCylinder(0.22, 5.5, App.Vector(x, platform_y, 13.4)))
        roofs.append(Part.makeBox(66.0, 6.8, 0.45, App.Vector(-33.0, platform_y - 3.4, 18.6)))
    _render_feature(
        doc, group, "RenderCanopyColumns", "S5 canopy columns", Part.makeCompound(columns), (0.18, 0.25, 0.30)
    )
    _render_feature(
        doc, group, "RenderCanopies", "S5 photovoltaic canopies", Part.makeCompound(roofs), (0.10, 0.35, 0.48)
    )
    pv_panels = []
    for platform_y in (-15.0, 15.0):
        for x in range(-30, 31, 6):
            pv_panels.append(Part.makeBox(5.2, 5.8, 0.12, App.Vector(x, platform_y - 2.9, 19.06)))
    _render_feature(
        doc, group, "RenderPVCanopyPanels", "Canopy photovoltaic panels", Part.makeCompound(pv_panels), (0.04, 0.18, 0.28)
    )

    stairs = []
    for y in (-18.0, 14.0):
        for step in range(12):
            stairs.append(
                Part.makeBox(1.2, 4.0, 0.75, App.Vector(22.0 + step * 1.2, y, step * 1.05))
            )
    _render_feature(
        doc, group, "RenderStationAccess", "S5 stairs and access cores", Part.makeCompound(stairs), (0.61, 0.63, 0.62)
    )

    buildings = []
    for x, y, sx, sy, sz in (
        (-175, 38, 36, 28, 20),
        (-125, 52, 30, 24, 15),
        (-28, 48, 42, 32, 23),
        (78, 42, 33, 27, 18),
        (126, 54, 48, 34, 26),
        (-150, -82, 45, 30, 13),
        (92, -92, 55, 35, 16),
    ):
        buildings.append(Part.makeBox(sx, sy, sz, App.Vector(x, y, 0.0)))
    _render_feature(
        doc, group, "RenderUrbanBlocks", "Samawah context massing", Part.makeCompound(buildings), (0.73, 0.57, 0.39)
    )

    palms_trunks = []
    palms_crowns = []
    for x, y in ((-105, -48), (-82, -72), (-18, -62), (72, -54), (148, -68), (110, 28), (-92, 27)):
        palms_trunks.append(Part.makeCylinder(0.6, 8.0, App.Vector(x, y, 0.0)))
        palms_crowns.append(Part.makeSphere(3.5, App.Vector(x, y, 8.5)))
    _render_feature(
        doc, group, "RenderPalmTrunks", "Palm trunks", Part.makeCompound(palms_trunks), (0.35, 0.22, 0.10)
    )
    _render_feature(
        doc, group, "RenderPalmCrowns", "Palm crowns", Part.makeCompound(palms_crowns), (0.15, 0.43, 0.18)
    )

    signal_posts = Part.makeCompound(
        [
            Part.makeCylinder(0.18, 4.2, App.Vector(x, -8.8, 13.4))
            for x in (-52.0, 52.0)
        ]
    )
    signal_heads = Part.makeCompound(
        [Part.makeSphere(0.55, App.Vector(x, -8.8, 17.8)) for x in (-52.0, 52.0)]
    )
    _render_feature(
        doc, group, "RenderSignalPosts", "Movement-authority signal posts", signal_posts, (0.15, 0.17, 0.18)
    )
    _render_feature(
        doc, group, "RenderSignalAspects", "Clear signal aspects", signal_heads, (0.10, 0.78, 0.27)
    )

    train_parts = {}
    train_colours = {
        "body": (0.96, 0.69, 0.06),
        "roof": (0.87, 0.88, 0.87),
        "glazing": (0.03, 0.13, 0.20),
        "bogies": (0.09, 0.10, 0.11),
        "doors": (0.82, 0.22, 0.12),
    }
    for kind, shape in _demo_train_shapes().items():
        feature = _render_feature(
            doc,
            group,
            f"RenderTrain{kind.title()}",
            f"Animated LM3 {kind}",
            shape,
            train_colours[kind],
        )
        feature.addProperty("App::PropertyBool", "AnimatedTrainPart", "Visualization")
        feature.AnimatedTrainPart = True
        feature.addProperty("App::PropertyString", "TrainPartKind", "Visualization")
        feature.TrainPartKind = kind
        train_parts[kind] = feature
    return tuple(train_parts.values())


def _camera_axis_angle(
    position: tuple[float, float, float],
    target: tuple[float, float, float],
) -> tuple[float, float, float, float]:
    """Return an Inventor axis-angle camera orientation looking at target."""

    backward = [position[index] - target[index] for index in range(3)]
    length = math.sqrt(sum(item * item for item in backward))
    backward = [item / length for item in backward]
    world_up = (0.0, 0.0, 1.0)
    right = [
        world_up[1] * backward[2] - world_up[2] * backward[1],
        world_up[2] * backward[0] - world_up[0] * backward[2],
        world_up[0] * backward[1] - world_up[1] * backward[0],
    ]
    right_length = math.sqrt(sum(item * item for item in right))
    right = [item / right_length for item in right]
    up = [
        backward[1] * right[2] - backward[2] * right[1],
        backward[2] * right[0] - backward[0] * right[2],
        backward[0] * right[1] - backward[1] * right[0],
    ]
    matrix = (
        (right[0], up[0], backward[0]),
        (right[1], up[1], backward[1]),
        (right[2], up[2], backward[2]),
    )
    trace = matrix[0][0] + matrix[1][1] + matrix[2][2]
    qw = math.sqrt(max(0.0, 1.0 + trace)) / 2.0
    if qw < 1e-8:
        return (0.0, 0.0, 1.0, 0.0)
    qx = (matrix[2][1] - matrix[1][2]) / (4.0 * qw)
    qy = (matrix[0][2] - matrix[2][0]) / (4.0 * qw)
    qz = (matrix[1][0] - matrix[0][1]) / (4.0 * qw)
    vector_length = math.sqrt(qx * qx + qy * qy + qz * qz)
    if vector_length < 1e-8:
        return (0.0, 0.0, 1.0, 0.0)
    angle = 2.0 * math.atan2(vector_length, qw)
    return qx / vector_length, qy / vector_length, qz / vector_length, angle


def _build_document(twin: SamawahLineTwin, model_path: Path):
    checks = assert_twin_checks(twin)
    doc = App.newDocument("OSRSamawahLine1DigitalTwin")
    doc.Label = "Samawah Line 1 complete planning and operational digital twin"
    root = doc.addObject("App::Part", "SamawahLine1Twin")
    root.Label = "Samawah Line 1 — full 25.5657 km overview twin"

    notes = doc.addObject("App::FeaturePython", "TwinReviewNotes")
    notes.Label = "Digital twin scope, provenance, and validation"
    for name, value in (
        ("TwinSchema", TWIN_SCHEMA),
        ("LineId", twin.line_id),
        ("EngineeringCrs", twin.crs),
        ("SourceStatus", twin.source_status),
        ("VisualScale", OVERVIEW_SCALE),
        ("OverviewRotation", f"{OVERVIEW_ROTATION_DEG:.1f} degrees counter-clockwise"),
    ):
        notes.addProperty("App::PropertyString", name, "Digital twin")
        setattr(notes, name, value)
    for name, value in (
        ("LineLengthM", twin.length_m),
        ("StationCount", len(twin.stations)),
        ("EnergySiteCount", len(twin.energy_sites)),
        ("FleetTrainsetCount", twin.fleet.trainset_count),
        ("AnimatedRepresentativeCount", ANIMATED_TRAIN_COUNT),
    ):
        property_type = "App::PropertyFloat" if isinstance(value, float) else "App::PropertyInteger"
        notes.addProperty(property_type, name, "Digital twin")
        setattr(notes, name, value)
    notes.addProperty("App::PropertyStringList", "PassedSourceChecks", "Digital twin")
    notes.PassedSourceChecks = [f"PASS — {item['name']}: {item['detail']}" for item in checks]
    root.addObject(notes)

    groups = {}
    for number, name in enumerate(
        ("Civil and track", "Stations", "Energy", "Depot", "Signalling", "Rolling stock"),
        start=1,
    ):
        group = doc.addObject("App::DocumentObjectGroup", _safe_name(f"{number:02d} {name}"))
        group.Label = f"{number:02d} {name}"
        root.addObject(group)
        groups[name] = group

    xmin, xmax, ymin, ymax = _overview_bounds(twin, aspect_ratio=1200.0 / 700.0)
    ground = doc.addObject("Part::Feature", "CityContextPlane")
    ground.Label = "Samawah Line 1 overview context plane"
    ground.Shape = Part.makeBox(
        xmax - xmin,
        ymax - ymin,
        0.4,
        App.Vector(xmin, ymin, -1.0),
    )
    ground.ViewObject.ShapeColor = (0.93, 0.90, 0.80)
    ground.ViewObject.LineColor = (0.93, 0.90, 0.80)
    _add_twin_properties(
        ground,
        asset_id="OSR-SAM-L1-CONTEXT",
        asset_class="visualization.context-plane",
        state={"geometry_role": "non-engineering-overview-background"},
    )
    groups["Civil and track"].addObject(ground)

    for index, segment in enumerate(
        (item for item in twin.civil_segments if item.civil_class == "elevated"),
        start=1,
    ):
        midpoint = (segment.start_m + segment.end_m) / 2.0
        x, y, heading = _point(twin, midpoint)
        water = Part.makeBox(
            1_100.0,
            460.0,
            0.8,
            App.Vector(-550.0, -230.0, -0.5),
        )
        feature = doc.addObject("Part::Feature", f"CrossingContext{index:02d}")
        feature.Label = f"Elevated crossing {index} context marker"
        feature.Shape = _placed_shape(water, x, y, heading + 90.0)
        feature.ViewObject.ShapeColor = (0.36, 0.70, 0.82)
        feature.ViewObject.LineColor = (0.24, 0.58, 0.72)
        _add_twin_properties(
            feature,
            asset_id=f"OSR-SAM-L1-CROSSING-CONTEXT-{index:02d}",
            asset_class="visualization.elevated-crossing-context",
            state={"geometry_role": "symbolically-exaggerated-overview-context"},
        )
        groups["Civil and track"].addObject(feature)

    for index, segment in enumerate(twin.civil_segments, start=1):
        points = _range_points(twin, segment.start_m, segment.end_m)
        z = 1.8 if segment.civil_class == "elevated" else TRACK_Z_MM
        feature = doc.addObject("Part::Feature", f"CivilSegment{index:03d}")
        feature.Label = (
            f"{segment.civil_class.title()} {segment.start_m:.1f}-{segment.end_m:.1f} m"
        )
        feature.Shape = _strip(points, width=56.0, height=2.0, z=z)
        feature.ViewObject.ShapeColor = (
            (0.20, 0.47, 0.70)
            if segment.civil_class == "elevated"
            else (0.49, 0.50, 0.48)
        )
        feature.ViewObject.LineColor = feature.ViewObject.ShapeColor
        _add_twin_properties(
            feature,
            asset_id=segment.asset_id,
            asset_class=f"civil.{segment.civil_class}",
            state={
                "health": "nominal",
                "from_chainage_m": segment.start_m,
                "to_chainage_m": segment.end_m,
            },
        )
        groups["Civil and track"].addObject(feature)

    route_points = [
        _local_xy(twin, point.easting_m, point.northing_m) for point in twin.alignment
    ]
    rails = doc.addObject("Part::Feature", "DoubleTrackRunningLines")
    rails.Label = "Line 1 double-track running rails — complete alignment"
    rails.Shape = Part.makeCompound(
        [
            _strip(route_points, width=7.0, height=2.0, z=2.1, lateral_offset=-16.0),
            _strip(route_points, width=7.0, height=2.0, z=2.1, lateral_offset=16.0),
        ]
    )
    rails.ViewObject.ShapeColor = (0.13, 0.15, 0.17)
    rails.ViewObject.LineColor = (0.13, 0.15, 0.17)
    _add_twin_properties(
        rails,
        asset_id="OSR-SAM-L1-TRACK",
        asset_class="track.double-running-line",
        state={"availability": "available", "gauge_mm": 1435},
    )
    groups["Civil and track"].addObject(rails)

    station_features = {}
    for index, station in enumerate(twin.stations, start=1):
        x, y, heading = _point(twin, station.chainage_m)
        platform = Part.makeBox(300.0, 130.0, 16.0, App.Vector(-150.0, -65.0, 3.0))
        beacon = Part.makeCylinder(68.0 if "interchange" not in station.archetype else 105.0, 28.0, App.Vector(0.0, 0.0, 4.0))
        feature = doc.addObject("Part::Feature", f"Station{index:02d}")
        feature.Label = f"S{index} {station.name} — {station.archetype}"
        feature.Shape = Part.makeCompound(
            [_placed_shape(platform, x, y, heading), _placed_shape(beacon, x, y, 0.0)]
        )
        colour = STATION_COLOURS[station.archetype]
        feature.ViewObject.ShapeColor = colour
        feature.ViewObject.LineColor = (0.16, 0.16, 0.18)
        _add_twin_properties(
            feature,
            asset_id=station.asset_id,
            asset_class=f"station.{station.archetype}",
            state={
                "availability": "available",
                "station_number": index,
                "chainage_m": station.chainage_m,
                "charging_power_kw": station.charging_power_kw,
            },
        )
        feature.addProperty("App::PropertyString", "ArabicName", "Station")
        feature.ArabicName = station.name
        feature.addProperty("App::PropertyFloat", "Latitude", "Station")
        feature.Latitude = station.latitude
        feature.addProperty("App::PropertyFloat", "Longitude", "Station")
        feature.Longitude = station.longitude
        feature.addProperty("App::PropertyFloat", "ChainageM", "Station")
        feature.ChainageM = station.chainage_m
        feature.addProperty("App::PropertyString", "Archetype", "Station")
        feature.Archetype = station.archetype
        groups["Stations"].addObject(feature)
        station_features[station.asset_id] = feature

        signal_shape = Part.makeCylinder(24.0, 38.0, App.Vector(0.0, 0.0, 4.0))
        signal = doc.addObject("Part::Feature", f"BlockBoundary{index:02d}")
        signal.Label = f"Movement-authority boundary S{index}"
        offset_x = x + math.cos(math.radians(heading + 90.0)) * 125.0
        offset_y = y + math.sin(math.radians(heading + 90.0)) * 125.0
        signal.Shape = _placed_shape(signal_shape, offset_x, offset_y, 0.0)
        signal.ViewObject.ShapeColor = (0.78, 0.08, 0.12)
        signal.ViewObject.LineColor = (0.78, 0.08, 0.12)
        _add_twin_properties(
            signal,
            asset_id=f"OSR-SAM-L1-SIGNAL-{index:02d}",
            asset_class="signalling.movement-authority-boundary",
            state={"interlocking": "available", "occupancy": "clear"},
        )
        groups["Signalling"].addObject(signal)

    energy_by_station = {site.station_id: site for site in twin.energy_sites}
    for index, station in enumerate(twin.stations, start=1):
        site = energy_by_station.get(station.asset_id)
        if site is None:
            continue
        x, y, heading = _point(twin, station.chainage_m)
        normal = math.radians(heading + 90.0)
        panel_x = x + math.cos(normal) * 260.0
        panel_y = y + math.sin(normal) * 260.0
        panel = Part.makeBox(240.0, 120.0, 10.0, App.Vector(-120.0, -60.0, 18.0))
        battery = Part.makeBox(90.0, 90.0, 28.0, App.Vector(-45.0, -45.0, 4.0))
        feature = doc.addObject("Part::Feature", f"EnergySite{index:02d}")
        feature.Label = f"S{index} {site.tier} PV, storage, and 500 kW charger"
        feature.Shape = Part.makeCompound(
            [
                _placed_shape(panel, panel_x, panel_y, heading),
                _placed_shape(battery, panel_x, panel_y, heading),
            ]
        )
        feature.ViewObject.ShapeColor = (0.10, 0.50, 0.72)
        feature.ViewObject.LineColor = (0.05, 0.20, 0.30)
        _add_twin_properties(
            feature,
            asset_id=site.asset_id,
            asset_class="energy.station-microgrid",
            state={
                "availability": "available",
                "storage_soc_percent": 50.0,
                "pv_nameplate_kw": site.pv_nameplate_kw,
                "storage_capacity_kwh": site.storage_capacity_kwh,
            },
        )
        feature.addProperty("App::PropertyFloat", "StorageSocPercent", "Operational")
        feature.StorageSocPercent = 50.0
        groups["Energy"].addObject(feature)

    depot_station = next(station for station in twin.stations if station.is_depot)
    depot_x, depot_y, depot_heading = _point(twin, depot_station.chainage_m)
    normal = math.radians(depot_heading - 90.0)
    depot_x += math.cos(normal) * 700.0
    depot_y += math.sin(normal) * 700.0
    depot_parts = [
        _placed_shape(
            Part.makeBox(900.0, 520.0, 50.0, App.Vector(-450.0, -260.0, 3.0)),
            depot_x,
            depot_y,
            depot_heading,
        )
    ]
    for offset in (-180.0, -60.0, 60.0, 180.0):
        road = Part.makeBox(1_100.0, 18.0, 6.0, App.Vector(-550.0, offset - 9.0, 54.0))
        depot_parts.append(_placed_shape(road, depot_x, depot_y, depot_heading))
    depot = doc.addObject("Part::Feature", "MainDepot")
    depot.Label = "Al-Jaraa main-heavy depot — 17 fleet stalls and 40 MWh storage"
    depot.Shape = Part.makeCompound(depot_parts)
    depot.ViewObject.ShapeColor = (0.52, 0.19, 0.12)
    depot.ViewObject.LineColor = (0.20, 0.12, 0.08)
    _add_twin_properties(
        depot,
        asset_id="OSR-SAM-L1-DEPOT-001",
        asset_class="depot.main-heavy",
        state={
            "availability": "available",
            "fleet_stalls": 17,
            "storage_capacity_kwh": 40_000,
        },
    )
    groups["Depot"].addObject(depot)

    train_shape = _make_train_symbol()
    train_features = []
    for index, motion in enumerate(representative_train_states(twin, 0.0), start=1):
        x, y = _local_xy(twin, motion.easting_m, motion.northing_m)
        feature = doc.addObject("Part::Feature", f"AnimatedTrain{index:02d}")
        feature.Label = f"Animated LM3 representative {index:02d}"
        feature.Shape = train_shape
        feature.Placement = App.Placement(
            App.Vector(x, y, 0.0),
            App.Rotation(
                App.Vector(0.0, 0.0, 1.0),
                motion.heading_deg + OVERVIEW_ROTATION_DEG,
            ),
        )
        feature.ViewObject.ShapeColor = (
            (0.96, 0.72, 0.08) if index == 1 else (0.05, 0.66, 0.30)
        )
        feature.ViewObject.LineColor = (0.02, 0.22, 0.10)
        _add_twin_properties(
            feature,
            asset_id=motion.trainset_id,
            asset_class="rolling-stock.light-metro-3car",
            state={
                "mode": "peak-service",
                "chainage_m": motion.chainage_m,
                "direction": motion.direction,
                "speed_kmh": motion.speed_kmh,
                "soc_percent": motion.soc_percent,
            },
        )
        feature.addProperty("App::PropertyFloat", "ChainageM", "Operational")
        feature.ChainageM = motion.chainage_m
        feature.addProperty("App::PropertyFloat", "SpeedKmh", "Operational")
        feature.SpeedKmh = motion.speed_kmh
        feature.addProperty("App::PropertyFloat", "SocPercent", "Operational")
        feature.SocPercent = motion.soc_percent
        feature.addProperty("App::PropertyString", "Direction", "Operational")
        feature.Direction = motion.direction
        groups["Rolling stock"].addObject(feature)
        train_features.append(feature)

    render_train_parts = _build_perspective_scene(doc, root)

    doc.recompute()
    invalid = [
        obj.Label
        for obj in doc.Objects
        if getattr(obj, "TypeId", "") == "Part::Feature"
        and (obj.Shape.isNull() or not obj.Shape.isValid())
    ]
    if invalid:
        App.closeDocument(doc.Name)
        raise RuntimeError("invalid Samawah twin shapes: " + "; ".join(invalid))
    model_path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveAs(str(model_path))
    write_manifest(model_path.with_suffix(".json"), twin, model_path=model_path)
    return doc, tuple(train_features), render_train_parts


def _render_frames(
    doc,
    twin: SamawahLineTwin,
    trains: tuple,
    out_dir: Path,
    *,
    frame_count: int,
    width: int,
    height: int,
) -> None:
    if frame_count < 46:
        raise ValueError("the real-time station sequence requires at least 46 frames")
    out_dir.mkdir(parents=True, exist_ok=True)
    for old_frame in out_dir.glob("frame-*.png"):
        old_frame.unlink()

    Gui.setActiveDocument(doc.Name)
    view = Gui.getDocument(doc.Name).activeView()
    for obj in doc.Objects:
        view_object = getattr(obj, "ViewObject", None)
        if view_object is None or not hasattr(view_object, "Visibility"):
            continue
        if getattr(obj, "TypeId", "") == "Part::Feature":
            view_object.Visibility = bool(getattr(obj, "RenderScene", False))
    try:
        view.setDrawStyle("Shaded")
    except Exception:
        pass
    Gui.updateGui()
    camera_position = (230.0, -300.0, 135.0)
    camera_target = (0.0, 0.0, 10.0)
    axis_x, axis_y, axis_z, angle = _camera_axis_angle(camera_position, camera_target)
    focal_distance = math.sqrt(
        sum((camera_position[index] - camera_target[index]) ** 2 for index in range(3))
    )
    view.setCamera(
        "#Inventor V2.1 ascii\n\n"
        "PerspectiveCamera {\n"
        "  viewportMapping ADJUST_CAMERA\n"
        f"  position {camera_position[0]:.6f} {camera_position[1]:.6f} {camera_position[2]:.6f}\n"
        f"  orientation {axis_x:.9f} {axis_y:.9f} {axis_z:.9f} {angle:.9f}\n"
        "  nearDistance 1\n"
        "  farDistance 1200\n"
        "  aspectRatio 1\n"
        f"  focalDistance {focal_distance:.6f}\n"
        "  heightAngle 0.550000\n"
        "}\n"
    )
    Gui.updateGui()

    state_path = out_dir / "frame-state.tsv"
    state_lines = ["frame\telapsed_s\tphase\tspeed_kmh\tacceleration_mps2\toffset_m\tdoors"]
    fps = frame_count / 46.0
    for frame_index in range(frame_count):
        elapsed_s = frame_index / fps
        motion = station_stop_motion(elapsed_s)
        for feature in trains:
            lateral_door_offset = -0.95 if (
                motion.doors_open and getattr(feature, "TrainPartKind", "") == "doors"
            ) else 0.0
            feature.Placement = App.Placement(
                App.Vector(motion.offset_m, lateral_door_offset, 0.0),
                App.Rotation(),
            )
            feature.ViewObject.Visibility = motion.phase != "SERVICE RESET"
        doc.recompute()
        Gui.updateGui()
        frame_path = out_dir / f"frame-{frame_index:03d}.png"
        view.saveImage(str(frame_path), width, height, "#d7e8ef")
        if not frame_path.exists() or frame_path.stat().st_size < 2_000:
            raise RuntimeError(f"FreeCAD produced an empty Samawah frame: {frame_path}")
        state_lines.append(
            f"{frame_index}\t{motion.elapsed_s:.1f}\t{motion.phase}\t"
            f"{motion.speed_kmh:.1f}\t{motion.acceleration_mps2:+.1f}\t"
            f"{motion.offset_m:.1f}\t{'OPEN' if motion.doors_open else 'CLOSED'}"
        )
        print(
            f"rendered {frame_path.name}: "
            f"t={motion.elapsed_s:.1f} s, {motion.phase}, "
            f"{motion.speed_kmh:.1f} km/h",
            flush=True,
        )
    state_path.write_text("\n".join(state_lines) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    city_dir = Path(os.environ.get("OSR_SAMAWAH_CITY_DIR", default_city_dir()))
    output_dir = city_dir / "engineering" / "digital-twin"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--city-dir", type=Path, default=city_dir)
    parser.add_argument(
        "--model",
        type=Path,
        default=Path(
            os.environ.get(
                "OSR_SAMAWAH_TWIN_MODEL",
                output_dir / "samawah-line1-digital-twin.FCStd",
            )
        ),
    )
    parser.add_argument(
        "--frames-dir",
        type=Path,
        default=Path(os.environ.get("OSR_SAMAWAH_TWIN_FRAME_DIR", output_dir / "frames")),
    )
    parser.add_argument(
        "--frames", type=int, default=int(os.environ.get("OSR_SAMAWAH_TWIN_FRAMES", "40"))
    )
    parser.add_argument(
        "--width", type=int, default=int(os.environ.get("OSR_SAMAWAH_TWIN_WIDTH", "1200"))
    )
    parser.add_argument(
        "--height", type=int, default=int(os.environ.get("OSR_SAMAWAH_TWIN_HEIGHT", "700"))
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    twin = load_samawah_line_twin(args.city_dir)
    doc, _overview_trains, render_train_parts = _build_document(twin, args.model)
    try:
        _render_frames(
            doc,
            twin,
            render_train_parts,
            args.frames_dir,
            frame_count=args.frames,
            width=args.width,
            height=args.height,
        )
        print(
            f"wrote {args.model} and {args.model.with_suffix('.json')} with "
            f"{len(twin.stations)} stations and {twin.fleet.trainset_count} fleet records",
            flush=True,
        )
        return 0
    finally:
        App.closeDocument(doc.Name)


if __name__ == "__main__":
    try:
        arguments = [] if os.environ.get("OSR_SAMAWAH_TWIN_RUN") == "1" else sys.argv[1:]
        sys.exit(main(arguments))
    finally:
        QtCore.QCoreApplication.quit()
