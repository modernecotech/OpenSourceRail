#!/usr/bin/env python3
"""Load an OSR civil IFC in Bonsai and build a review render/animation scene.

Run through ``scripts/bonsai-civil.sh --render``.  This file is executed by
Blender's Python, not the repository virtual environment.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime
from pathlib import Path

import bpy
from mathutils import Vector


def parse_args() -> argparse.Namespace:
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--ifc", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--sequence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--detail-output", type=Path)
    parser.add_argument("--blend", type=Path, required=True)
    parser.add_argument("--animation-output", type=Path)
    return parser.parse_args(args)


def point_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def add_material(name: str, colour: tuple[float, float, float, float], metallic: float = 0.0):
    material = bpy.data.materials.new(name)
    material.diffuse_color = colour
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = colour
    principled.inputs["Roughness"].default_value = 0.56
    principled.inputs["Metallic"].default_value = metallic
    return material


def add_review_context() -> None:
    ground_material = add_material("OSR context ground", (0.075, 0.095, 0.105, 1.0))
    bpy.ops.mesh.primitive_plane_add(size=700, location=(160, 0, -0.08))
    ground = bpy.context.object
    ground.name = "OSR review ground datum"
    ground.data.materials.append(ground_material)

    for x in range(0, 326, 25):
        bpy.ops.mesh.primitive_cube_add(location=(x, 0, -0.035), scale=(0.025, 22, 0.025))
        marker = bpy.context.object
        marker.name = f"Chainage {x:03d} m"
        marker.data.materials.append(add_material(f"marker-{x}", (0.17, 0.22, 0.24, 1.0)))


def configure_camera_and_lighting() -> None:
    bpy.ops.object.camera_add(location=(165, -175, 105))
    camera = bpy.context.object
    camera.name = "OSR civil coordination camera"
    camera.data.lens = 54
    point_at(camera, (177, 0, 5.5))
    bpy.context.scene.camera = camera

    bpy.ops.object.light_add(type="AREA", location=(115, -55, 105))
    key = bpy.context.object
    key.name = "OSR key light"
    key.data.energy = 1700
    key.data.shape = "DISK"
    key.data.size = 55
    point_at(key, (175, 0, 3))

    bpy.ops.object.light_add(type="AREA", location=(250, 45, 65))
    fill = bpy.context.object
    fill.name = "OSR fill light"
    fill.data.energy = 900
    fill.data.size = 70
    point_at(fill, (190, 0, 6))

    bpy.ops.object.light_add(type="SUN", location=(160, -30, 120))
    sun = bpy.context.object
    sun.name = "OSR daylight"
    sun.data.energy = 3.2
    sun.data.angle = math.radians(18)
    sun.rotation_euler = (math.radians(28), math.radians(-22), math.radians(-24))

    world = bpy.context.scene.world or bpy.data.worlds.new("OSR civil world")
    bpy.context.scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.07, 0.105, 0.15, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8


def tag_objects() -> dict[str, list[bpy.types.Object]]:
    from bonsai.tool import Ifc

    materials = {
        "IfcRail": add_material("OSR rail steel", (0.055, 0.075, 0.09, 1.0), 0.82),
        "IfcBearing": add_material("OSR elastomeric bearing", (0.12, 0.13, 0.14, 1.0), 0.28),
        "IfcBeam": add_material("OSR precast girder", (0.48, 0.57, 0.62, 1.0)),
        "IfcColumn": add_material("OSR pier concrete", (0.39, 0.45, 0.48, 1.0)),
        "IfcSlab": add_material("OSR trackform and platform", (0.68, 0.72, 0.71, 1.0)),
        "IfcRoof": add_material("OSR station canopy", (0.035, 0.42, 0.52, 1.0), 0.18),
        "IfcElementAssembly": add_material("OSR turnout", (0.94, 0.42, 0.08, 1.0), 0.32),
        "IfcCivilElement": add_material("OSR civil interface", (0.12, 0.62, 0.57, 1.0)),
        "IfcVehicle": add_material("OSR rolling stock reference", (0.88, 0.22, 0.09, 1.0), 0.12),
    }
    by_tag: dict[str, list[bpy.types.Object]] = {}
    for obj in bpy.context.scene.objects:
        try:
            entity = Ifc.get_entity(obj)
        except Exception:
            entity = None
        tag = getattr(entity, "Tag", None) if entity else None
        if tag:
            by_tag.setdefault(tag, []).append(obj)
            obj["osr_asset_id"] = tag
            obj["osr_ifc_class"] = entity.is_a()
            if entity.is_a() == "IfcVirtualElement":
                # Keep the clearance object inspectable in Bonsai but omit its
                # opaque tessellation from presentation renders.
                obj.hide_render = True
            if isinstance(obj.data, bpy.types.Mesh) and entity.is_a() in materials:
                obj.data.materials.clear()
                obj.data.materials.append(materials[entity.is_a()])
    return by_tag


def animate_sequence(sequence: dict, by_tag: dict[str, list[bpy.types.Object]]) -> None:
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 192
    starts = [datetime.fromisoformat(task["start"]) for task in sequence["tasks"]]
    finishes = [datetime.fromisoformat(task["finish"]) for task in sequence["tasks"]]
    overall_start, overall_finish = min(starts), max(finishes)
    span_seconds = max((overall_finish - overall_start).total_seconds(), 1.0)
    task_by_id = {task["id"]: task for task in sequence["tasks"]}
    assigned: set[str] = set()
    for task_id, asset_ids in sequence["product_assignments"].items():
        task = task_by_id[task_id]
        finish = datetime.fromisoformat(task["finish"])
        frame = 10 + round((finish - overall_start).total_seconds() / span_seconds * 172)
        for asset_id in asset_ids:
            assigned.add(asset_id)
            for obj in by_tag.get(asset_id, []):
                obj.hide_render = True
                obj.hide_viewport = True
                obj.scale = (0.001, 0.001, 0.001)
                obj.keyframe_insert("hide_render", frame=max(1, frame - 2))
                obj.keyframe_insert("hide_viewport", frame=max(1, frame - 2))
                obj.keyframe_insert("scale", frame=max(1, frame - 2))
                obj.hide_render = False
                obj.hide_viewport = False
                obj.keyframe_insert("hide_render", frame=frame)
                obj.keyframe_insert("hide_viewport", frame=frame)
                obj.keyframe_insert("scale", frame=frame)
                obj.scale = (1, 1, 1)
                obj.keyframe_insert("scale", frame=min(scene.frame_end, frame + 8))
    # Rolling stock is a clearance/operations reference, not a civil work
    # package. Introduce it only after the constructed civil model is visible.
    for asset_id, objects in by_tag.items():
        if asset_id in assigned or not any(
            obj.get("osr_ifc_class") == "IfcVehicle" for obj in objects
        ):
            continue
        for obj in objects:
            obj.hide_render = True
            obj.hide_viewport = True
            obj.scale = (0.001, 0.001, 0.001)
            obj.keyframe_insert("hide_render", frame=176)
            obj.keyframe_insert("hide_viewport", frame=176)
            obj.keyframe_insert("scale", frame=176)
            obj.hide_render = False
            obj.hide_viewport = False
            obj.keyframe_insert("hide_render", frame=177)
            obj.keyframe_insert("hide_viewport", frame=177)
            obj.scale = (1, 1, 1)
            obj.keyframe_insert("scale", frame=185)
    scene["osr_schedule_name"] = sequence["schedule_name"]
    scene["osr_animated_assets"] = len(assigned)
    scene["osr_animation_semantics"] = sequence["animation"]["semantics"]
    scene.frame_set(scene.frame_end)


def render(args: argparse.Namespace) -> None:
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.blend.parent.mkdir(parents=True, exist_ok=True)
    index = json.loads(args.index.read_text(encoding="utf-8"))
    sequence = json.loads(args.sequence.read_text(encoding="utf-8"))

    bpy.ops.bim.load_project(filepath=str(args.ifc.resolve()), should_start_fresh_session=True)
    add_review_context()
    configure_camera_and_lighting()
    by_tag = tag_objects()
    animate_sequence(sequence, by_tag)

    scene = bpy.context.scene
    scene["osr_schema"] = index["schema"]
    scene["osr_revision_id"] = index["revision_id"]
    scene["osr_ifc_sha256"] = index["ifc_sha256"]
    scene["osr_authority_boundary"] = json.dumps(index["authority_boundary"], sort_keys=True)
    scene["osr_native_bearings"] = index["summary"]["native_bearings"]
    scene["osr_bearing_connections"] = index["summary"]["bearing_connection_relationships"]
    scene["osr_bearing_connection_realizations"] = index["summary"]["bearing_connection_realizations"]
    scene["osr_foundation_interfaces"] = index["summary"]["foundation_interfaces"]
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(args.output.resolve())
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.render.image_settings.color_depth = "8"
    bpy.ops.wm.save_as_mainfile(filepath=str(args.blend.resolve()))
    bpy.ops.render.render(write_still=True)

    if args.detail_output:
        args.detail_output.parent.mkdir(parents=True, exist_ok=True)
        camera = scene.camera
        # Support-end three-quarter view exposes the reduced common cap,
        # bearing lines, twin track decks and independent outer cassettes.
        camera.location = (94.0, -24.0, 18.0)
        camera.data.lens = 58
        point_at(camera, (113.0, 0.0, 7.2))
        scene.render.filepath = str(args.detail_output.resolve())
        bpy.ops.render.render(write_still=True)

    if args.animation_output:
        args.animation_output.parent.mkdir(parents=True, exist_ok=True)
        frames = args.animation_output.parent / f"{args.animation_output.stem}-frames"
        frames.mkdir(parents=True, exist_ok=True)
        scene.render.resolution_x = 960
        scene.render.resolution_y = 540
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGB"
        scene.render.filepath = str((frames / "frame-").resolve())
        scene.frame_set(scene.frame_start)
        bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    render(parse_args())
