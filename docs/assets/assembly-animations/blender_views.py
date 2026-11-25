"""Headless Blender materials and camera setup for the Baghdad assembly views."""

from functools import lru_cache
import json
from math import cos, radians, sin, tan
from pathlib import Path
import random
import sys

import bpy
from mathutils import Vector


def srgb(value):
    value /= 255
    return value / 12.92 if value < 0.04045 else ((value + 0.055) / 1.055) ** 2.4


@lru_cache(maxsize=None)
def material(color, finish):
    code = color.lstrip("#")
    rgb = tuple(srgb(int(code[i:i + 2], 16)) for i in (0, 2, 4))
    result = bpy.data.materials.new(f"{finish} {color}")
    result.diffuse_color = (*rgb, 1)
    result.use_nodes = True
    bsdf = result.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = {
        "glazing": .14, "painted": .29, "metal": .36, "ground": .84, "concrete": .72, "vinyl": .56,
    }.get(finish, .46)
    bsdf.inputs["Metallic"].default_value = {"metal": .61, "painted": .17, "glazing": .28}.get(finish, 0)
    if finish == "painted":
        bsdf.inputs["Coat Weight"].default_value = .22
    if finish in ("ground", "concrete"):
        nodes = result.node_tree.nodes
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 52
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .18
        bump.inputs["Distance"].default_value = .028
        result.node_tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        result.node_tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    if finish == "lamp":
        bsdf.inputs["Emission Color"].default_value = (*rgb, 1)
        bsdf.inputs["Emission Strength"].default_value = 1.1
    return result


def finish_for(name):
    name = name.lower()
    if any(term in name for term in ("floor", "seats", "seat_", "bellows", "buffer", "trim", "rubber", "lining")):
        return "vinyl"
    if any(term in name for term in ("glass", "windscreen", "glazing", "window")):
        return "glazing"
    if any(term in name for term in ("lamp", "light", "_led", "headlight", "taillight")):
        return "lamp"
    if any(term in name for term in ("gantry", "front", "nose", "cab_shell", "skin", "panel", "door", "cabinet")):
        return "painted"
    if any(term in name for term in ("footing", "pier", "cap_", "crosshead", "girder", "deck", "foundation")):
        return "concrete"
    if any(term in name for term in ("rail", "wheel", "axle", "coupler", "strand", "bolt", "rebar", "strap")):
        return "metal"
    if any(term in name for term in ("street", "ground", "road", "terrain", "corridor")):
        return "ground"
    return "satin"


def exact_mesh(item, elevation):
    mesh = bpy.data.meshes.new(item["name"])
    mesh.from_pydata(item["vertices"], [], item["faces"])
    mesh.update()
    obj = bpy.data.objects.new(item["name"], mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.location.z = elevation
    mesh.materials.append(material(item["color"], finish_for(item["name"])))
    return obj


def cube(name, center, dimensions, color, finish="concrete", bevel=.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material(color, finish))
    if bevel:
        modifier = obj.modifiers.new("Edge radius", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
    return obj


def textured_sky():
    world = bpy.context.scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    sky = nodes.new("ShaderNodeTexSky")
    sky.sky_type = "HOSEK_WILKIE"
    sky.sun_direction = (-.42, -.52, .64)
    sky.turbidity = 2.8
    background = nodes.get("Background")
    background.inputs["Strength"].default_value = .55
    world.node_tree.links.new(sky.outputs["Color"], background.inputs["Color"])


def lighting(target, distance, studio):
    textured_sky()
    bpy.ops.object.light_add(type="SUN", location=target + Vector((-8, -12, 18)))
    sun = bpy.context.object
    sun.rotation_euler = (target - sun.location).to_track_quat("-Z", "Y").to_euler()
    sun.data.energy = 1.8 if studio else 2.45
    sun.data.angle = radians(8 if studio else 3)
    sun.data.color = (1, .88, .73)
    bpy.ops.object.light_add(type="AREA", location=target + Vector((distance * .15, -distance * .42, distance * .72)))
    fill = bpy.context.object
    fill.rotation_euler = (target - fill.location).to_track_quat("-Z", "Y").to_euler()
    fill.data.energy = distance ** 2 * (30 if studio else 12)
    fill.data.shape = "DISK"
    fill.data.size = distance * .68
    fill.data.color = (.77, .88, 1)


def palm(x, y, z, height, rng):
    bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=.22, radius2=.125, depth=height,
                                    location=(x, y, z + height / 2))
    bpy.context.object.data.materials.append(material("#89765a", "ground"))
    vertices, faces = [], []
    for i in range(13):
        a = radians(i * 360 / 13) + rng.uniform(-.12, .12)
        length = rng.uniform(1.3, 2.35)
        start = len(vertices)
        for j in range(7):
            fraction = j / 6
            radius = length * fraction
            spine = z + height + .58 * sin(fraction * 3.7) - .32 * fraction
            breadth = .26 * sin(fraction * 3.14159)
            vertices.extend((x + radius * cos(a) - side * breadth * sin(a),
                             y + radius * sin(a) + side * breadth * cos(a), spine)
                            for side in (-1, 1))
            if j:
                k = start + j * 2
                faces.append((k - 2, k, k + 1, k - 1))
    exact_mesh(dict(name="Context date palm", vertices=vertices, faces=faces, color="#688052"), 0)


def context(name, target, width):
    x, y, _ = target
    if not name.startswith("viaduct") and name != "train-exterior":
        return
    civil = name.startswith("viaduct")
    ground_z = -.12
    cube("Context ground", (x, y, ground_z - .07), (max(900, width * 6), 820, .13),
         "#cabda8" if civil else "#a79680", "ground", 0)
    if name == "viaduct-placement":
        return
    side_offset = 14 if civil else 8
    if not civil:
        z = target.z - 1.61
        length = max(145, width * 3)
        cube("Illustrative deck", (x, -2.0, z - .90), (length, 8.4, 1.26), "#b2ada3")
        cube("Adjacent track bed", (x, -4.35, z - .23), (length, 3.55, .32), "#8d8780")
        for side in (-5.08, -3.62):
            cube("Running rail", (x, side, z - .035), (length, .065, .07), "#8f8a87", "metal")
        for i in range(-3, 5):
            pier_x = x + 13 + 20 * i
            cube("Shared pier", (pier_x, -2.05, (z - 1.6) / 2), (1.6, 1.8, z - 1.6), "#b4afa5", bevel=.08)
            cube("Pier cap", (pier_x, -2.05, z - 1.94), (2.25, 8.55, .72), "#bbb7aa", bevel=.08)
    for sign in (-1, 1):
        street_y = y + sign * side_offset
        cube("Street", (x, street_y, ground_z + .005), (width * 2.5, 7.8, .065), "#706965", "ground", .03)
        cube("Kerb", (x, street_y + sign * 4.2, ground_z + .045), (width * 2.5, 1, .13), "#b5ab99")
        for i in range(-9, 10):
            cube("Lane divider", (x + i * width / 7, street_y, ground_z + .047),
                 (width / 14, .08, .015), "#e9dcc6", bevel=0)
    # Simple context gives scale without implying a surveyed station site.
    randomizer = random.Random(38)
    for i in range(-11, 12):
        hx = x + i * 8.8 + randomizer.uniform(-1, 1)
        height = randomizer.uniform(3.8, 8.7)
        hy = y + side_offset + 14 + randomizer.uniform(-2, 3)
        width_m = randomizer.uniform(4.8, 7.3)
        tone = randomizer.choice(("#d5c1a2", "#cdb59b", "#e2d1b7", "#c7b8a4"))
        cube("Context building", (hx, hy, ground_z + height / 2), (width_m, 8, height), tone)
        cube("Parapet", (hx, hy, ground_z + height), (width_m + .05, 8.05, .28), tone)
        for z in range(2, int(height), 2):
            for delta in (-1.6, 0, 1.6):
                cube("Context window", (hx + delta, hy - 4.025, ground_z + z), (.75, .06, 1.01),
                     "#697b7f", "glazing", .01)
    for i in range(-7, 9):
        palm(x + i * 10.7, y + side_offset + 5.1, ground_z, randomizer.uniform(4.0, 6.9), randomizer)


def render(record, output, samples):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    material.cache_clear()
    scene = bpy.context.scene
    scene.world = bpy.data.worlds.new("Indirect daylight")
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1440
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.quality = 91
    scene.view_settings.view_transform = "AgX"

    camera = record["camera"]
    name = record["view"]
    elevation = 6.4 if name == "train-exterior" else 0
    target = Vector(camera["target"]) + Vector((0, 0, elevation))
    width = camera["width"]
    context(name, target, width)
    for item in record["items"]:
        exact_mesh(item, elevation)

    studio = name not in ("train-exterior", "viaduct-completed", "viaduct-placement")
    lighting(target, width, studio)
    if name == "train-saloon":
        for x in (-6, -3, 0, 3, 6):
            for y in (-.64, .64):
                bpy.ops.object.light_add(type="AREA", location=(x, y, 2.76))
                lamp = bpy.context.object
                lamp.data.energy = 32
                lamp.data.shape = "RECTANGLE"
                lamp.data.size = 2.6
                lamp.data.size_y = .085
                lamp.data.color = (1, .94, .84)
    bpy.ops.object.camera_add()
    obj = bpy.context.object
    scene.camera = obj
    if camera["eye"]:
        eye, focus = camera["eye"]
        obj.location = eye
        obj.rotation_euler = (Vector(focus) - obj.location).to_track_quat("-Z", "Y").to_euler()
        obj.data.lens = 22
        obj.data.clip_start = .025
    else:
        azimuth, elevation = map(radians, (camera["yaw"], camera["elevation"]))
        direction = Vector((cos(azimuth) * cos(elevation), sin(azimuth) * cos(elevation), sin(elevation)))
        obj.data.lens = 64 if studio else 45
        distance = (width / 2) / tan(obj.data.angle_x / 2) * 1.12
        obj.location = target + direction * distance
        obj.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
        obj.data.clip_end = max(1000, distance * 5)
    scene.render.filepath = str(output / f"{name}.jpg")
    bpy.ops.render.render(write_still=True)


def main():
    output, samples, *views = sys.argv[sys.argv.index("--") + 1:]
    for file in views:
        record = json.loads(Path(file).read_text())
        render(record, Path(output), int(samples))


main()
