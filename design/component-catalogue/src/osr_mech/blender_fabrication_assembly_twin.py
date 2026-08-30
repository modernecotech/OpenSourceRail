"""Render the OSR fabrication and assembly digital twin with Blender Eevee."""

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

from osr_mech.fabrication_assembly_twin import ANIMATION_DURATION_S, fabrication_streams


def _reset() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.materials, bpy.data.curves, bpy.data.meshes):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def _material(name, colour, *, metallic=0.0, roughness=0.5, emission=None, strength=0.0):
    material = bpy.data.materials.new(name)
    material.diffuse_color = colour
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = colour
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if emission is not None:
            socket = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
            if socket:
                socket.default_value = emission
            power = bsdf.inputs.get("Emission Strength")
            if power:
                power.default_value = strength
    return material


def _cube(name, location, dimensions, material, *, bevel=0.08, stage=None, offset=(0.0, 0.0, 8.0)):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    if bevel:
        modifier = obj.modifiers.new("fabrication edge radii", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
    if stage:
        obj["install_stage"] = stage
        obj["staging_offset"] = offset
    return obj


def _cylinder(name, location, radius, depth, material, *, stage=None, offset=(0.0, 0.0, 8.0), vertices=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    if stage:
        obj["install_stage"] = stage
        obj["staging_offset"] = offset
    return obj


def _label(body, location, material, *, size=1.05):
    curve = bpy.data.curves.new(f"{body} lettering", "FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.025
    obj = bpy.data.objects.new(body, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (math.pi / 2.0, 0.0, 0.0)
    obj.data.materials.append(material)
    return obj


def _track_cell(m, centre=(-22.0, -13.0)):
    x0, y0 = centre
    _cube("Track fixture bed", (x0, y0, 0.35), (32.0, 10.0, 0.7), m["floor"], bevel=0.18)
    for i in range(10):
        x = x0 - 13.5 + i * 3.0
        _cube(f"Trackform sleeper {i+1}", (x, y0, 1.05), (0.55, 5.2, 0.55), m["concrete"], stage="TRK-20", offset=(0, -9, 4))
        for side in (-1.0, 1.0):
            _cube(f"Baseplate {i+1} {side:+.0f}", (x, y0 + side * 1.45, 1.42), (0.42, 0.58, 0.16), m["yellow"], stage="TRK-30", offset=(0, side * 8, 3))
    for side in (-1.0, 1.0):
        _cube(f"Running rail {side:+.0f}", (x0, y0 + side * 1.45, 1.72), (29.0, 0.18, 0.34), m["steel"], bevel=0.04, stage="TRK-40", offset=(-18, 0, 5))
    _cube("Track geometry cart", (x0 + 10.0, y0, 2.15), (2.1, 4.0, 1.0), m["teal"], stage="TRK-50", offset=(13, 0, 0))


def _station_cell(m, centre=(22.0, -13.0)):
    x0, y0 = centre
    _cube("Station assembly apron", (x0, y0, 0.35), (34.0, 10.0, 0.7), m["floor"], bevel=0.18)
    for side in (-1.0, 1.0):
        _cube(f"Station platform {side:+.0f}", (x0, y0 + side * 3.0, 1.25), (31.0, 3.0, 1.1), m["platform"], stage="STN-10", offset=(0, side * 12, 5))
    for x in (x0 - 13.0, x0 - 6.5, x0, x0 + 6.5, x0 + 13.0):
        for side in (-1.0, 1.0):
            _cube("Canopy portal column", (x, y0 + side * 3.1, 4.15), (0.28, 0.28, 5.0), m["steel"], stage="STN-20", offset=(0, side * 10, 7))
    for side in (-1.0, 1.0):
        _cube(f"Station canopy {side:+.0f}", (x0, y0 + side * 3.1, 6.75), (31.5, 4.1, 0.36), m["teal"], stage="STN-30", offset=(0, side * 10, 9))
        for x in (x0 - 12, x0 - 6, x0, x0 + 6, x0 + 12):
            _cube("Station PV cassette", (x, y0 + side * 3.1, 7.04), (5.2, 3.1, 0.12), m["solar"], bevel=0.03, stage="STN-30", offset=(0, side * 10, 10))
    _cube("Station systems cabinet", (x0 + 12.8, y0, 2.1), (1.7, 2.0, 3.4), m["navy"], stage="STN-50", offset=(7, 0, 0))


def _viaduct_cell(m, centre=(-22.0, 13.0)):
    x0, y0 = centre
    _cube("Viaduct erection zone", (x0, y0, 0.22), (34.0, 11.0, 0.44), m["floor"], bevel=0.16)
    for x in (x0 - 13.0, x0 + 13.0):
        _cube("Viaduct pier", (x, y0, 3.0), (1.8, 3.2, 5.6), m["concrete"], stage="VIA-05", offset=(0, 0, -6))
        _cube("7 m hollow pier cap", (x, y0, 5.95), (2.5, 7.0, 0.55), m["concrete"], stage="VIA-05", offset=(0, 0, 7))
        for track_side in (-1.0, 1.0):
            for stem_side in (-1.0, 1.0):
                _cylinder("Elastomeric bearing", (x, y0 + track_side * 1.75 + stem_side * 0.72, 6.35), 0.24, 0.20, m["rubber"], stage="VIA-50", offset=(0, track_side * 7, 4))
    for side in (-1.0, 1.0):
        track_y = y0 + side * 1.75
        _cube(f"Pi25 deck flange {side:+.0f}", (x0, track_y, 7.50), (27.5, 2.9, 0.22), m["light_concrete"], stage="VIA-50", offset=(0, side * 13, 10))
        for stem_side in (-1.0, 1.0):
            _cube("Pi25 rail-line stem", (x0, track_y + stem_side * 0.72, 6.92), (27.5, 0.30, 0.94), m["light_concrete"], stage="VIA-50", offset=(0, side * 13, 10))
        _cube("Internal support link slab", (x0 + 13.0, track_y, 7.64), (1.4, 2.7, 0.18), m["gold"], stage="VIA-55", offset=(0, side * 8, 7))
        _cube("Outer walkway cassette", (x0, track_y + side * 1.95, 7.68), (27.5, 1.0, 0.12), m["platform"], stage="VIA-60", offset=(0, side * 13, 10))
        _cube("Outer containment screen", (x0, track_y + side * 2.42, 8.38), (27.5, 0.08, 1.4), m["steel"], stage="VIA-60", offset=(0, side * 13, 10))
        for rail_side in (-0.7, 0.7):
            _cube("Viaduct running rail", (x0, track_y + rail_side, 7.94), (27.0, 0.13, 0.24), m["steel"], bevel=0.025, stage="VIA-60", offset=(-15, 0, 5))
    for y in (y0 - 3.1, y0 + 3.1):
        _cube("Portal launcher longitudinal truss", (x0, y, 11.0), (33.0, 0.35, 0.55), m["yellow"], stage="VIA-50", offset=(-20, 0, 8))
    for x in (x0 - 12.5, x0 + 12.5):
        _cube("Portal launcher frame", (x, y0, 9.2), (0.4, 6.6, 0.5), m["yellow"], stage="VIA-50", offset=(-20, 0, 8))


def _train_cell(m, centre=(22.0, 13.0)):
    x0, y0 = centre
    _cube("Train final assembly road", (x0, y0, 0.30), (34.0, 11.0, 0.60), m["floor"], bevel=0.16)
    car_centres = (x0 - 10.8, x0, x0 + 10.8)
    for car_index, x in enumerate(car_centres, start=1):
        for bogie_x in (x - 3.2, x + 3.2):
            _cube(f"Car {car_index} bogie", (bogie_x, y0, 1.0), (2.3, 3.0, 0.65), m["undercar"], stage="RS-20-CARBODY-BOGIE", offset=(0, -10, 1))
            for side in (-1.0, 1.0):
                wheel = _cylinder("LM3 assembly wheel", (bogie_x, y0 + side * 1.25, 0.78), 0.56, 0.25, m["wheel"], stage="RS-20-CARBODY-BOGIE", offset=(0, -10, 1), vertices=24)
                wheel.rotation_euler.x = math.pi / 2.0
        _cube(f"Car {car_index} underframe", (x, y0, 1.65), (10.2, 3.4, 0.48), m["steel"], stage="RS-20-CARBODY-BOGIE", offset=(0, 0, 9))
        _cube(f"Car {car_index} body module", (x, y0, 3.35), (10.0, 3.3, 2.9), m["body"], stage="RS-25-CLIP-ON-BODY", offset=(0, 10, 7))
        _cube(f"Car {car_index} roof systems", (x, y0, 5.0), (9.5, 2.75, 0.35), m["roof"], stage="RS-30-TRACTION-BATTERY-CONTROL", offset=(0, 0, 9))
        for side in (-1.0, 1.0):
            _cube("LM3 teal waist band", (x, y0 + side * 1.67, 2.48), (9.8, 0.06, 0.18), m["teal"], bevel=0.025, stage="RS-25-CLIP-ON-BODY", offset=(0, side * 9, 4))
            for window_x in (x - 3.5, x, x + 3.5):
                _cube("LM3 glazing cassette", (window_x, y0 + side * 1.67, 3.65), (1.5, 0.06, 0.85), m["glass"], bevel=0.05, stage="RS-40-FITOUT-STATIC-TEST", offset=(0, side * 9, 4))
            for door_x in (x - 1.9, x + 1.9):
                _cube("LM3 low-floor door cassette", (door_x, y0 + side * 1.69, 3.18), (1.05, 0.07, 2.0), m["body"], bevel=0.045, stage="RS-40-FITOUT-STATIC-TEST", offset=(0, side * 9, 4))
    for sign in (-1.0, 1.0):
        _cube("LM3 finished end cowl", (x0 + sign * 16.2, y0, 3.15), (0.75, 2.9, 3.0), m["gold"], bevel=0.28, stage="RS-40-FITOUT-STATIC-TEST", offset=(sign * 8, 0, 5))


def _stage_frames(fps: int) -> dict[str, tuple[int, int]]:
    result = {}
    frame_end = int(ANIMATION_DURATION_S * fps)
    for stream in fabrication_streams():
        total = sum(stage.duration_days for stage in stream.stages)
        cursor = 0.0
        for stage in stream.stages:
            start = max(1, int(cursor / total * frame_end) + 1)
            cursor += stage.duration_days
            end = max(start + 1, int(cursor / total * frame_end))
            result[stage.id] = (start, min(frame_end, end))
    return result


def _animate_objects(fps: int, still_time: float | None) -> None:
    stage_frames = _stage_frames(fps)
    still_frame = None if still_time is None else int(min(ANIMATION_DURATION_S, max(0.0, still_time)) * fps) + 1
    for obj in bpy.context.scene.objects:
        stage_id = obj.get("install_stage")
        if not stage_id:
            continue
        start, end = stage_frames[stage_id]
        target = obj.location.copy()
        offset = Vector(tuple(obj["staging_offset"]))
        if still_frame is not None:
            if still_frame < start:
                obj.scale = (0.02, 0.02, 0.02)
                obj.location = target + offset
            elif still_frame < end:
                p = (still_frame - start) / (end - start)
                smooth = p * p * (3.0 - 2.0 * p)
                obj.scale = (max(0.02, smooth),) * 3
                obj.location = target + offset * (1.0 - smooth)
            continue
        obj.location = target + offset
        obj.scale = (0.02, 0.02, 0.02)
        obj.keyframe_insert(data_path="location", frame=max(1, start - 1))
        obj.keyframe_insert(data_path="scale", frame=max(1, start - 1))
        obj.location = target
        obj.scale = (1.0, 1.0, 1.0)
        obj.keyframe_insert(data_path="location", frame=end)
        obj.keyframe_insert(data_path="scale", frame=end)
def _look_at(obj, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def build(args: argparse.Namespace) -> None:
    _reset()
    m = {
        "ground": _material("factory ground", (0.055, 0.065, 0.075, 1), roughness=0.82),
        "floor": _material("assembly cell floor", (0.18, 0.20, 0.22, 1), metallic=0.1, roughness=0.62),
        "concrete": _material("precast concrete", (0.56, 0.57, 0.55, 1), roughness=0.72),
        "light_concrete": _material("U-girder concrete", (0.72, 0.71, 0.67, 1), roughness=0.70),
        "steel": _material("fabricated steel", (0.17, 0.20, 0.23, 1), metallic=0.72, roughness=0.27),
        "yellow": _material("quality witness yellow", (0.94, 0.56, 0.025, 1), roughness=0.40),
        "teal": _material("OSR teal", (0.015, 0.33, 0.34, 1), metallic=0.12, roughness=0.28),
        "solar": _material("PV glass", (0.008, 0.055, 0.15, 1), metallic=0.28, roughness=0.16),
        "platform": _material("station paving", (0.62, 0.58, 0.48, 1), roughness=0.78),
        "navy": _material("systems cabinet", (0.015, 0.11, 0.18, 1), metallic=0.15, roughness=0.32),
        "rubber": _material("bearing elastomer", (0.02, 0.023, 0.025, 1), roughness=0.86),
        "body": _material("LM3 body", (0.82, 0.84, 0.82, 1), metallic=0.05, roughness=0.32),
        "roof": _material("LM3 roof", (0.38, 0.42, 0.45, 1), metallic=0.25, roughness=0.36),
        "glass": _material("laminated glass", (0.006, 0.03, 0.05, 1), metallic=0.1, roughness=0.11),
        "gold": _material("LM3 end cowl", (0.93, 0.46, 0.025, 1), roughness=0.28),
        "undercar": _material("underframe", (0.03, 0.036, 0.043, 1), metallic=0.55, roughness=0.35),
        "wheel": _material("wheel steel", (0.05, 0.055, 0.06, 1), metallic=0.88, roughness=0.23),
        "white": _material("label white", (0.92, 0.96, 1.0, 1), emission=(0.75, 0.90, 1.0, 1), strength=1.5),
        "green": _material("released green", (0.02, 0.65, 0.22, 1), emission=(0.02, 1.0, 0.18, 1), strength=4.0),
    }
    _cube("Factory hall floor", (0, 0, -0.45), (84, 62, 0.7), m["ground"], bevel=0.25)
    _track_cell(m)
    _station_cell(m)
    _viaduct_cell(m)
    _train_cell(m)
    for title, pos in (
        ("TRACK PANEL", (-22, -19.0, 1.0)),
        ("STATION KIT", (22, -19.0, 1.0)),
        ("OSR-PI25 VIADUCT", (-22, 6.5, 1.0)),
        ("LM3 TRAINSET", (22, 6.5, 1.0)),
    ):
        _label(title, pos, m["white"], size=0.9)
    _label("SOURCE-LINKED FABRICATION + ASSEMBLY TWIN", (0, 29.0, 2.0), m["white"], size=1.25)

    for x, y, last_stage in ((-22, -13, "TRK-50"), (22, -13, "STN-50"), (-22, 13, "VIA-60"), (22, 13, "RS-50-DYNAMIC-COMMISSIONING")):
        _cylinder("QA release beacon", (x + 14.5, y - 4.0, 1.6), 0.42, 2.2, m["green"], stage=last_stage, offset=(0, 0, 5))

    _animate_objects(args.fps, args.still_time)

    target = bpy.data.objects.new("Factory camera target", None)
    bpy.context.collection.objects.link(target)
    target.location = (0, 0, 3.0)
    camera_data = bpy.data.cameras.new("Fabrication twin camera")
    camera = bpy.data.objects.new("Fabrication twin camera", camera_data)
    bpy.context.collection.objects.link(camera)
    camera_data.lens = 32.0
    camera.location = (64, -82, 52)
    constraint = camera.constraints.new(type="TRACK_TO")
    constraint.target = target
    constraint.track_axis = "TRACK_NEGATIVE_Z"
    constraint.up_axis = "UP_Y"
    bpy.context.scene.camera = camera
    if args.still_time is None:
        for elapsed, location in ((0, (64, -82, 52)), (18, (68, -82, 48)), (34, (-68, -82, 48)), (48, (-64, -82, 52))):
            camera.location = location
            camera.keyframe_insert(data_path="location", frame=int(elapsed * args.fps) + 1)
    else:
        # The centre of the orbit is its tightest framing condition.
        camera.location = (0, -82, 48)

    sun_data = bpy.data.lights.new("factory skylight sun", "SUN")
    sun_data.energy = 2.6
    sun_data.angle = math.radians(8)
    sun = bpy.data.objects.new("factory skylight sun", sun_data)
    bpy.context.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(28), math.radians(-20), math.radians(-35))
    area_data = bpy.data.lights.new("factory softbox", "AREA")
    area_data.energy = 1200
    area_data.shape = "DISK"
    area_data.size = 38
    area = bpy.data.objects.new("factory softbox", area_data)
    bpy.context.collection.objects.link(area)
    area.location = (0, -8, 42)
    _look_at(area, Vector((0, 0, 2)))

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = args.width
    scene.render.resolution_y = args.height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.fps = args.fps
    scene.frame_start = 1
    scene.frame_end = int(ANIMATION_DURATION_S * args.fps)
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = args.samples
    world = scene.world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.055, 0.085, 0.12, 1)
    background.inputs["Strength"].default_value = 0.34
    args.blend.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.blend))


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frames-dir", type=Path, required=True)
    parser.add_argument("--blend", type=Path, required=True)
    parser.add_argument("--width", type=int, default=720)
    parser.add_argument("--height", type=int, default=405)
    parser.add_argument("--fps", type=int, default=4)
    parser.add_argument("--samples", type=int, default=4)
    parser.add_argument("--still-time", type=float)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    args.frames_dir.mkdir(parents=True, exist_ok=True)
    build(args)
    scene = bpy.context.scene
    if args.still_time is not None:
        frame = min(scene.frame_end, max(1, int(args.still_time * args.fps) + 1))
        scene.frame_set(frame)
        scene.render.filepath = str(args.frames_dir / "preview.png")
        bpy.ops.render.render(write_still=True)
        print(f"wrote {scene.render.filepath}", flush=True)
        return
    scene.render.filepath = str(args.frames_dir / "frame-")
    bpy.ops.render.render(animation=True)
    print(f"wrote {scene.frame_end} fabrication twin frames", flush=True)


if __name__ == "__main__":
    script_args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    main(script_args)
