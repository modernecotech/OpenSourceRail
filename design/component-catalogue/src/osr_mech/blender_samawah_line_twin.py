"""Render the Samawah S5 operations demonstrator with Blender Eevee.

FreeCAD remains the engineering review/model source.  This scene uses the
same promoted LM3 dimensions and the checked real-time station motion model,
but gives them presentation materials, lighting, shadows, a perspective
camera, and a visibly resolved driverless end-cowl design.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


SOURCE_ROOT = Path(__file__).resolve().parents[1]
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from osr_mech.samawah_line_twin import (
    LM3_BODY_HEIGHT_M,
    LM3_DOOR_HEIGHT_M,
    LM3_DOOR_SILL_M,
    LM3_WINDOW_HEIGHT_M,
    LM3_WINDOW_SILL_M,
    S5_PLATFORM_HEIGHT_ABOVE_TOR_M,
    station_stop_motion,
)


RAIL_TOP_Z_M = 10.67


def _reset() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.materials, bpy.data.curves, bpy.data.meshes):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def _material(
    name: str,
    colour: tuple[float, float, float, float],
    *,
    metallic: float = 0.0,
    roughness: float = 0.52,
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
):
    material = bpy.data.materials.new(name)
    material.diffuse_color = colour
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = colour
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if emission is not None:
            emission_input = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
            if emission_input is not None:
                emission_input.default_value = emission
            strength_input = bsdf.inputs.get("Emission Strength")
            if strength_input is not None:
                strength_input.default_value = emission_strength
    return material


def _cube(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material,
    *,
    bevel: float = 0.0,
    parent=None,
):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material is not None:
        obj.data.materials.append(material)
    if bevel > 0.0:
        modifier = obj.modifiers.new("soft production edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
    obj.parent = parent
    return obj


def _cylinder(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    depth: float,
    material,
    *,
    vertices: int = 24,
    parent=None,
):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    obj.parent = parent
    return obj


def _lofted_cab(name: str, sign: float, material, parent):
    """Create the smooth tapered A/B-end cowl inside the 49.5 m envelope."""

    interface_x = sign * 22.95
    leading_x = sign * 24.75
    rings = (
        (interface_x, 1.425, 0.00, LM3_BODY_HEIGHT_M, 0.24),
        (sign * 24.00, 1.30, 0.08, 3.25, 0.30),
        (leading_x, 1.06, 0.18, 2.98, 0.36),
    )
    vertices: list[tuple[float, float, float]] = []
    for x, half_width, z_min, z_max, radius in rings:
        outline = (
            (-half_width + radius, z_min),
            (half_width - radius, z_min),
            (half_width, z_min + radius),
            (half_width, z_max - radius),
            (half_width - radius, z_max),
            (-half_width + radius, z_max),
            (-half_width, z_max - radius),
            (-half_width, z_min + radius),
        )
        vertices.extend((x, y, z) for y, z in outline)
    faces: list[tuple[int, ...]] = []
    ring_size = 8
    for ring_index in range(len(rings) - 1):
        start = ring_index * ring_size
        target = (ring_index + 1) * ring_size
        for point in range(ring_size):
            next_point = (point + 1) % ring_size
            faces.append((start + point, start + next_point, target + next_point, target + point))
    faces.append(tuple(range((len(rings) - 1) * ring_size, len(rings) * ring_size)))
    mesh = bpy.data.meshes.new(f"{name} sculpted mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    obj.parent = parent
    bevel = obj.modifiers.new("cowl surface radii", "BEVEL")
    bevel.width = 0.12
    bevel.segments = 4
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    return obj


def _build_train(materials: dict[str, object]):
    train = bpy.data.objects.new("LM3 49.5 m three-car trainset", None)
    bpy.context.collection.objects.link(train)

    body_specs = (
        (-15.60, 14.70),
        (0.0, 16.50),
        (15.60, 14.70),
    )
    for car_index, (centre_x, length) in enumerate(body_specs, start=1):
        _cube(
            f"Car {car_index} structural body",
            (centre_x, 0.0, LM3_BODY_HEIGHT_M / 2.0),
            (length, 2.82, LM3_BODY_HEIGHT_M),
            materials["body"],
            bevel=0.24,
            parent=train,
        )
        _cube(
            f"Car {car_index} roof fairing",
            (centre_x, 0.0, 3.60),
            (length - 0.55, 2.48, 0.30),
            materials["roof"],
            bevel=0.16,
            parent=train,
        )
        _cube(
            f"Car {car_index} teal livery stripe",
            (centre_x, -1.425, 0.99),
            (length - 0.30, 0.055, 0.22),
            materials["teal"],
            bevel=0.03,
            parent=train,
        )
        _cube(
            f"Car {car_index} far-side livery stripe",
            (centre_x, 1.425, 0.99),
            (length - 0.30, 0.055, 0.22),
            materials["teal"],
            bevel=0.03,
            parent=train,
        )

        window_xs = (
            centre_x - length * 0.35,
            centre_x - length * 0.19,
            centre_x,
            centre_x + length * 0.19,
            centre_x + length * 0.35,
        )
        door_xs = (centre_x - length / 6.0, centre_x + length / 6.0)
        for side in (-1.0, 1.0):
            for window_index, window_x in enumerate(window_xs, start=1):
                if min(abs(window_x - door_x) for door_x in door_xs) < 1.0:
                    continue
                _cube(
                    f"Car {car_index} side {side:+.0f} window {window_index}",
                    (window_x, side * 1.431, LM3_WINDOW_SILL_M + LM3_WINDOW_HEIGHT_M / 2.0),
                    (1.75, 0.045, LM3_WINDOW_HEIGHT_M),
                    materials["glass"],
                    bevel=0.09,
                    parent=train,
                )
            for door_index, door_x in enumerate(door_xs, start=1):
                _cube(
                    f"Car {car_index} side {side:+.0f} door aperture {door_index}",
                    (door_x, side * 1.432, LM3_DOOR_SILL_M + LM3_DOOR_HEIGHT_M / 2.0),
                    (1.38, 0.050, LM3_DOOR_HEIGHT_M + 0.04),
                    materials["rubber"],
                    bevel=0.04,
                    parent=train,
                )
                door = _cube(
                    f"Car {car_index} side {side:+.0f} passenger door {door_index}",
                    (door_x, side * 1.438, LM3_DOOR_SILL_M + LM3_DOOR_HEIGHT_M / 2.0),
                    (1.35, 0.065, LM3_DOOR_HEIGHT_M),
                    materials["door"],
                    bevel=0.05,
                    parent=train,
                )
                door["closed_x"] = door_x
                door["slide_sign"] = -1.0 if door_index == 1 else 1.0
                door["animated_door"] = True
                _cube(
                    f"Car {car_index} door glass {door_index} side {side:+.0f}",
                    (0.0, side * 0.039, 0.42),
                    (0.82, 0.025, 0.82),
                    materials["glass"],
                    bevel=0.04,
                    parent=door,
                )

        for bogie_offset in (-length * 0.34, length * 0.34):
            bogie_x = centre_x + bogie_offset
            _cube(
                f"Car {car_index} bogie frame {bogie_offset:+.1f}",
                (bogie_x, 0.0, 0.72),
                (2.55, 2.10, 0.42),
                materials["undercar"],
                bevel=0.10,
                parent=train,
            )
            for axle_x in (bogie_x - 0.82, bogie_x + 0.82):
                for side in (-1.0, 1.0):
                    wheel = _cylinder(
                        f"LM3 wheel {car_index} {axle_x:.2f} {side:+.0f}",
                        (axle_x, side * 1.03, 0.48),
                        0.46,
                        0.18,
                        materials["wheel"],
                        vertices=32,
                        parent=train,
                    )
                    wheel.rotation_euler.x = math.pi / 2.0
                    wheel["animated_wheel"] = True

    for joint_x in (-8.25, 8.25):
        _cube(
            f"Inter-car bellows {joint_x:+.2f}",
            (joint_x, 0.0, LM3_BODY_HEIGHT_M / 2.0),
            (0.32, 2.54, 3.18),
            materials["rubber"],
            bevel=0.08,
            parent=train,
        )

    for sign, end_name in ((-1.0, "A"), (1.0, "B")):
        _lofted_cab(f"{end_name}-end sculpted driverless cowl", sign, materials["nose"], train)
        leading_x = sign * 24.82
        glass = _cube(
            f"{end_name}-end panoramic passenger and sensor glass",
            (leading_x, 0.0, 1.85),
            (0.08, 1.96, 1.78),
            materials["glass"],
            bevel=0.20,
            parent=train,
        )
        # The upper edge is inboard of the lower edge: a conventional inward
        # windscreen rake at both symmetric ends, rather than an outward lean.
        glass.rotation_euler.y = -sign * math.radians(10.0)
        for side in (-1.0, 1.0):
            lamp = _cube(
                f"{end_name}-end LED headlamp {side:+.0f}",
                (sign * 24.92, side * 0.63, 0.72),
                (0.12, 0.30, 0.15),
                materials["headlight"],
                bevel=0.06,
                parent=train,
            )
            lamp.rotation_euler.y = -sign * math.radians(10.0)
            _cube(
                f"{end_name}-end marker light {side:+.0f}",
                (sign * 24.90, side * 0.58, 0.93),
                (0.13, 0.48, 0.055),
                materials["marker"],
                bevel=0.025,
                parent=train,
            )
        _cube(
            f"{end_name}-end anti-climber",
            (sign * 24.58, 0.0, 0.34),
            (0.42, 1.72, 0.16),
            materials["undercar"],
            bevel=0.04,
            parent=train,
        )

    for car_centre in (-15.6, 0.0, 15.6):
        for panel_x in (car_centre - 5.2, car_centre - 1.7, car_centre + 1.7, car_centre + 5.2):
            _cube(
                f"Roof photovoltaic panel {panel_x:.1f}",
                (panel_x, 0.0, 3.81),
                (2.95, 1.72, 0.08),
                materials["solar"],
                bevel=0.025,
                parent=train,
            )
    return train


def _look_at(obj, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def _join_meshes(objects: list[object], name: str):
    """Bake modifiers and combine like-moving meshes to reduce render overhead."""

    objects = [obj for obj in objects if obj is not None and obj.type == "MESH"]
    if not objects:
        return None
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.convert(target="MESH")
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    objects[0].name = name
    return objects[0]


def _build_scene(materials: dict[str, object]) -> None:
    _cube("Desert ground", (0.0, 0.0, -0.55), (360.0, 190.0, 1.0), materials["sand"])
    _cube("Blue-green water crossing", (-63.0, 0.0, 0.03), (28.0, 190.0, 0.12), materials["water"])
    _cube("Road beneath viaduct", (48.0, 0.0, 0.08), (22.0, 190.0, 0.16), materials["asphalt"])
    for y in range(-88, 89, 12):
        _cube("Road centre marking", (48.0, float(y), 0.19), (0.5, 6.0, 0.06), materials["yellow"])

    _cube("Elevated twin-track deck", (0.0, 0.0, 8.95), (360.0, 22.0, 2.5), materials["concrete"], bevel=0.28)
    for edge_y in (-10.7, 10.7):
        _cube("U-girder edge beam", (0.0, edge_y, 10.75), (360.0, 0.75, 2.0), materials["light_concrete"], bevel=0.12)
    for x in range(-165, 166, 30):
        _cube("Viaduct pier", (float(x), 0.0, 4.0), (2.7, 5.5, 8.0), materials["concrete"], bevel=0.18)
        _cube("Viaduct pier cap", (float(x), 0.0, 8.15), (8.0, 14.0, 0.75), materials["concrete"], bevel=0.16)

    for track_y in (-3.3, 3.3):
        for rail_y in (track_y - 0.718, track_y + 0.718):
            _cube("Running rail", (0.0, rail_y, 10.58), (360.0, 0.11, 0.18), materials["steel"], bevel=0.025)
        for x in range(-178, 179, 2):
            _cube("Track sleeper", (float(x), track_y, 10.40), (1.25, 2.65, 0.13), materials["sleeper"])

    platform_top_z = RAIL_TOP_Z_M + S5_PLATFORM_HEIGHT_ABOVE_TOR_M
    for platform_y in (-8.0, 8.0):
        _cube("S5 side platform", (0.0, platform_y, platform_top_z - 0.525), (78.0, 6.0, 1.05), materials["platform"], bevel=0.12)
        edge_y = platform_y - math.copysign(2.69, platform_y)
        _cube("Tactile platform edge", (0.0, edge_y, platform_top_z + 0.04), (78.0, 0.62, 0.08), materials["yellow"])
        for x in (-32.0, -16.0, 0.0, 16.0, 32.0):
            _cylinder("Canopy column", (x, platform_y, 13.62), 0.18, 5.2, materials["steel"], vertices=20)
        _cube("S5 sweeping canopy", (0.0, platform_y, 16.28), (68.0, 6.5, 0.42), materials["teal"], bevel=0.18)
        for x in range(-30, 31, 6):
            _cube("Canopy PV panel", (float(x), platform_y, 16.53), (5.3, 5.2, 0.07), materials["solar"], bevel=0.03)

    for x, y, sx, sy, sz in (
        (-155, 35, 32, 24, 18),
        (-112, 48, 28, 22, 14),
        (-42, 43, 38, 30, 22),
        (72, 40, 33, 26, 17),
        (120, 50, 45, 32, 25),
        (-142, -70, 44, 28, 13),
        (92, -75, 52, 31, 16),
    ):
        _cube("Samawah context building", (x, y, sz / 2.0), (sx, sy, sz), materials["building"], bevel=0.35)

    for x, y in ((-104, -45), (-82, -67), (-18, -58), (73, -51), (142, -62), (108, 27), (-91, 25)):
        _cylinder("Palm trunk", (x, y, 3.5), 0.38, 7.0, materials["trunk"], vertices=16)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=3.1, location=(x, y, 7.5))
        bpy.context.object.name = "Palm crown"
        bpy.context.object.scale = (1.0, 1.0, 0.52)
        bpy.context.object.data.materials.append(materials["palm"])

    sign = _cube("S5 station sign board", (0.0, 10.42, 14.2), (14.5, 0.18, 1.6), materials["navy"], bevel=0.08)
    del sign
    curve = bpy.data.curves.new("Station sign lettering", "FONT")
    curve.body = "S5  SAMAWAH CENTRAL"
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = 0.66
    curve.extrude = 0.015
    label = bpy.data.objects.new("S5 station name", curve)
    bpy.context.collection.objects.link(label)
    label.location = (0.0, 10.30, 14.2)
    label.rotation_euler = (math.pi / 2.0, 0.0, 0.0)
    label.data.materials.append(materials["white"])


def _animate(train, camera, camera_target, *, fps: int, still_time: float | None = None) -> None:
    frame_end = 46 * fps
    wheel_radius = 0.46
    doors = [obj for obj in train.children_recursive if obj.get("animated_door")]
    wheels = [obj for obj in train.children_recursive if obj.get("animated_wheel")]
    if still_time is not None:
        motion = station_stop_motion(still_time)
        # Use the camera-side track so the S5 platform/door interface is
        # directly visible during the dwell close-up.
        train.location = (motion.offset_m, -3.3, RAIL_TOP_Z_M)
        camera.location = (52.0, -38.0, 21.0)
        camera_target.location.x = 12.0 if motion.doors_open else max(-40.0, min(40.0, motion.offset_m * 0.24))
        for door in doors:
            closed_x = float(door["closed_x"])
            slide_sign = float(door["slide_sign"])
            door.location.x = closed_x + (1.10 * slide_sign if motion.doors_open else 0.0)
        return
    for elapsed_s, location in (
        (0.0, (62.0, -82.0, 31.0)),
        (17.0, (58.0, -74.0, 28.0)),
        (20.0, (52.0, -38.0, 21.0)),
        (25.0, (52.0, -38.0, 21.0)),
        (28.0, (58.0, -74.0, 28.0)),
        (46.0, (62.0, -82.0, 31.0)),
    ):
        camera.location = location
        camera.keyframe_insert(data_path="location", frame=int(elapsed_s * fps) + 1)
    previous_offset = station_stop_motion(0.0).offset_m
    wheel_angle = 0.0
    for frame in range(1, frame_end + 1):
        elapsed_s = (frame - 1) / fps
        motion = station_stop_motion(elapsed_s)
        train.location.x = motion.offset_m
        train.location.y = -3.3
        train.location.z = RAIL_TOP_Z_M
        train.keyframe_insert(data_path="location", frame=frame)
        camera_target.location.x = (
            12.0 if motion.doors_open else max(-40.0, min(40.0, motion.offset_m * 0.24))
        )
        camera_target.keyframe_insert(data_path="location", frame=frame)
        wheel_angle -= (motion.offset_m - previous_offset) / wheel_radius
        previous_offset = motion.offset_m
        for wheel in wheels:
            wheel.rotation_euler.y = wheel_angle
            wheel.keyframe_insert(data_path="rotation_euler", frame=frame)
        for door in doors:
            closed_x = float(door["closed_x"])
            slide_sign = float(door["slide_sign"])
            door.location.x = closed_x + (1.10 * slide_sign if motion.doors_open else 0.0)
            door.keyframe_insert(data_path="location", frame=frame)


def _configure_render(args: argparse.Namespace):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = args.width
    scene.render.resolution_y = args.height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.fps = args.fps
    scene.frame_start = 1
    scene.frame_end = 46 * args.fps
    scene.render.film_transparent = False
    scene.render.use_file_extension = True
    scene.render.image_settings.color_depth = "8"
    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = args.samples
    if hasattr(scene.render, "use_motion_blur"):
        scene.render.use_motion_blur = True
    if hasattr(scene.render, "motion_blur_shutter"):
        scene.render.motion_blur_shutter = 0.36
    scene.view_settings.look = "AgX - Medium High Contrast"

    world = scene.world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.16, 0.36, 0.55, 1.0)
    background.inputs["Strength"].default_value = 0.42


def build(args: argparse.Namespace) -> None:
    _reset()
    materials = {
        "sand": _material("warm Samawah sand", (0.57, 0.38, 0.20, 1.0), roughness=0.92),
        "water": _material("blue-green water", (0.02, 0.28, 0.42, 1.0), metallic=0.08, roughness=0.22),
        "asphalt": _material("road asphalt", (0.045, 0.052, 0.060, 1.0), roughness=0.88),
        "yellow": _material("safety yellow", (0.95, 0.58, 0.025, 1.0), roughness=0.44),
        "concrete": _material("warm precast concrete", (0.49, 0.48, 0.44, 1.0), roughness=0.78),
        "light_concrete": _material("light U-girder concrete", (0.69, 0.67, 0.61, 1.0), roughness=0.72),
        "steel": _material("rail steel", (0.12, 0.14, 0.16, 1.0), metallic=0.76, roughness=0.25),
        "sleeper": _material("sleepers", (0.24, 0.20, 0.16, 1.0), roughness=0.83),
        "platform": _material("platform paving", (0.62, 0.57, 0.46, 1.0), roughness=0.80),
        "building": _material("sun-baked masonry", (0.56, 0.34, 0.18, 1.0), roughness=0.88),
        "trunk": _material("palm trunk", (0.22, 0.11, 0.045, 1.0), roughness=0.92),
        "palm": _material("palm crown", (0.045, 0.28, 0.08, 1.0), roughness=0.82),
        "body": _material("LM3 ivory composite body", (0.82, 0.84, 0.82, 1.0), metallic=0.05, roughness=0.33),
        "nose": _material("LM3 golden end cowls", (0.93, 0.48, 0.035, 1.0), metallic=0.03, roughness=0.29),
        "roof": _material("LM3 roof", (0.42, 0.45, 0.47, 1.0), metallic=0.22, roughness=0.38),
        "teal": _material("OSR teal livery", (0.015, 0.30, 0.31, 1.0), metallic=0.10, roughness=0.27),
        "glass": _material("smoked laminated glazing", (0.008, 0.035, 0.055, 1.0), metallic=0.08, roughness=0.12),
        "door": _material("LM3 passenger doors", (0.80, 0.83, 0.82, 1.0), metallic=0.16, roughness=0.31),
        "undercar": _material("underframe equipment", (0.035, 0.042, 0.048, 1.0), metallic=0.55, roughness=0.36),
        "wheel": _material("wheel steel", (0.055, 0.060, 0.066, 1.0), metallic=0.86, roughness=0.24),
        "rubber": _material("inter-car bellows", (0.018, 0.021, 0.023, 1.0), roughness=0.88),
        "solar": _material("photovoltaic glass", (0.008, 0.045, 0.12, 1.0), metallic=0.25, roughness=0.16),
        "headlight": _material("warm LED headlights", (1.0, 0.82, 0.42, 1.0), emission=(1.0, 0.68, 0.22, 1.0), emission_strength=8.0, roughness=0.15),
        "marker": _material("white marker lights", (0.72, 0.92, 1.0, 1.0), emission=(0.52, 0.86, 1.0, 1.0), emission_strength=5.0, roughness=0.15),
        "navy": _material("station navy", (0.015, 0.12, 0.20, 1.0), roughness=0.34),
        "white": _material("sign white", (0.95, 0.97, 1.0, 1.0), emission=(0.95, 0.97, 1.0, 1.0), emission_strength=1.2),
    }
    _build_scene(materials)
    _join_meshes(
        [obj for obj in bpy.context.scene.objects if obj.type == "MESH" and obj.parent is None],
        "Optimized static Samawah S5 scene",
    )
    train = _build_train(materials)
    _join_meshes(
        [
            obj
            for obj in list(train.children)
            if obj.type == "MESH"
            and not obj.get("animated_door")
            and not obj.get("animated_wheel")
        ],
        "LM3 body, cowls, glazing, systems, and livery",
    )

    target = bpy.data.objects.new("Camera tracking target", None)
    bpy.context.collection.objects.link(target)
    target.location = (0.0, 0.0, 10.0)

    camera_data = bpy.data.cameras.new("Perspective operations camera")
    camera = bpy.data.objects.new("Perspective operations camera", camera_data)
    bpy.context.collection.objects.link(camera)
    camera.location = (57.0, -72.0, 28.0)
    camera_data.lens = 52.0
    camera_data.sensor_width = 36.0
    constraint = camera.constraints.new(type="TRACK_TO")
    constraint.target = target
    constraint.track_axis = "TRACK_NEGATIVE_Z"
    constraint.up_axis = "UP_Y"
    bpy.context.scene.camera = camera

    sun_data = bpy.data.lights.new("late afternoon sun", "SUN")
    sun_data.energy = 3.0
    sun_data.angle = math.radians(7.0)
    sun = bpy.data.objects.new("late afternoon sun", sun_data)
    bpy.context.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(33.0), math.radians(-18.0), math.radians(-38.0))

    area_data = bpy.data.lights.new("station fill light", "AREA")
    area_data.energy = 850.0
    area_data.shape = "DISK"
    area_data.size = 34.0
    area = bpy.data.objects.new("station fill light", area_data)
    bpy.context.collection.objects.link(area)
    area.location = (-12.0, -28.0, 39.0)
    _look_at(area, Vector((0.0, 0.0, 10.0)))

    _animate(train, camera, target, fps=args.fps, still_time=args.still_time)
    _configure_render(args)
    args.blend.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.blend))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frames-dir", type=Path, required=True)
    parser.add_argument("--blend", type=Path, required=True)
    parser.add_argument("--width", type=int, default=800)
    parser.add_argument("--height", type=int, default=450)
    parser.add_argument("--fps", type=int, default=5)
    parser.add_argument("--samples", type=int, default=4)
    parser.add_argument("--still-time", type=float)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    args.frames_dir.mkdir(parents=True, exist_ok=True)
    for frame in args.frames_dir.glob("frame-*.png"):
        frame.unlink()
    build(args)
    scene = bpy.context.scene
    if args.still_time is not None:
        frame = min(scene.frame_end, max(scene.frame_start, int(args.still_time * args.fps) + 1))
        scene.frame_set(frame)
        scene.render.filepath = str(args.frames_dir / "preview.png")
        bpy.ops.render.render(write_still=True)
        print(f"wrote {scene.render.filepath}", flush=True)
        return
    scene.render.filepath = str(args.frames_dir / "frame-")
    bpy.ops.render.render(animation=True)
    print(f"wrote {scene.frame_end} Blender frames to {args.frames_dir}", flush=True)


if __name__ == "__main__":
    script_args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    main(script_args)
