"""Render FreeCAD-exported STL meshes into README-quality PNGs with Blender."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from math import radians
from pathlib import Path
import sys

import bpy
from mathutils import Vector


@dataclass(frozen=True)
class RenderJob:
    mesh: str
    output: str
    yaw_deg: float = -38.0
    height_factor: float = 0.22
    scale_factor: float = 1.08


RENDERS: tuple[RenderJob, ...] = (
    RenderJob("trainset-light-metro-3car.stl", "blender-trainset-light-metro-3car.png", -88.0, 0.18, 1.32),
    RenderJob("full-body-assembly-states.stl", "blender-full-body-assembly.png", -62.0, 0.28, 1.72),
    RenderJob("chassis-bogie-assembly-states.stl", "blender-chassis-bogie-assembly.png", -86.0, 0.22, 1.7),
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _mesh_root() -> Path:
    return Path(__file__).resolve().parents[2] / "catalog" / "render-meshes"


def _screenshots_root() -> Path:
    return _repo_root() / "docs" / "screenshots" / "freecad"


def _reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def _make_material(name: str, color: tuple[float, float, float, float], roughness: float = 0.55):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = 0.0
    return material


def _import_stl(path: Path):
    before = set(bpy.data.objects)
    if hasattr(bpy.ops.wm, "stl_import"):
        bpy.ops.wm.stl_import(filepath=str(path))
    else:
        bpy.ops.import_mesh.stl(filepath=str(path))
    imported = [obj for obj in bpy.data.objects if obj not in before and obj.type == "MESH"]
    if not imported:
        raise RuntimeError(f"no mesh objects imported from {path}")
    return imported


def _bounds(objects) -> tuple[Vector, Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    low = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    high = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    center = (low + high) * 0.5
    return low, high, center


def _look_at(obj, target: Vector) -> None:
    direction = target - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def _render_one(*, mesh_dir: Path, out_dir: Path, job: RenderJob) -> None:
    _reset_scene()
    mesh_path = mesh_dir / job.mesh
    if not mesh_path.exists():
        raise FileNotFoundError(f"missing render mesh: {mesh_path}")
    objects = _import_stl(mesh_path)

    clay = _make_material("warm grey engineering clay", (0.68, 0.71, 0.74, 1.0), 0.5)
    for obj in objects:
        obj.data.materials.append(clay)
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.shade_smooth()

    low, high, center = _bounds(objects)
    span = max(high.x - low.x, high.y - low.y, high.z - low.z)
    x_span = high.x - low.x
    z_span = high.z - low.z
    camera_angle = radians(job.yaw_deg)
    camera = bpy.data.cameras.new("Camera")
    camera_obj = bpy.data.objects.new("Camera", camera)
    bpy.context.collection.objects.link(camera_obj)
    distance = span * 1.35
    camera_obj.location = Vector(
        (
            center.x + distance * __import__("math").cos(camera_angle),
            center.y + distance * __import__("math").sin(camera_angle),
            center.z + span * job.height_factor,
        )
    )
    _look_at(camera_obj, center)
    camera.type = "ORTHO"
    camera.clip_start = 1.0
    camera.clip_end = span * 5.0
    camera.ortho_scale = max(z_span * 1.7, x_span / 1.72) * job.scale_factor
    bpy.context.scene.camera = camera_obj

    sun_data = bpy.data.lights.new("soft sun", "SUN")
    sun_data.energy = 2.3
    sun = bpy.data.objects.new("soft sun", sun_data)
    bpy.context.collection.objects.link(sun)
    sun.rotation_euler = (radians(48), radians(0), radians(-35))

    area_data = bpy.data.lights.new("large studio softbox", "AREA")
    area_data.energy = 520.0
    area_data.size = span * 0.55
    area = bpy.data.objects.new("large studio softbox", area_data)
    bpy.context.collection.objects.link(area)
    area.location = Vector((center.x - span * 0.35, center.y - span * 0.45, center.z + span * 0.55))
    _look_at(area, center)

    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.samples = 64
    bpy.context.scene.world.color = (0.985, 0.987, 0.99)
    bpy.context.scene.render.resolution_x = 2400
    bpy.context.scene.render.resolution_y = 1350
    bpy.context.scene.view_settings.view_transform = "Standard"
    bpy.context.scene.view_settings.look = "Medium High Contrast"
    bpy.context.scene.view_settings.exposure = -0.25
    bpy.context.scene.render.film_transparent = False

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / job.output
    bpy.context.scene.render.filepath = str(out_path)
    bpy.ops.render.render(write_still=True)
    print(f"wrote {out_path} ({out_path.stat().st_size // 1024} KB)", flush=True)


def render_all(*, mesh_dir: Path, out_dir: Path) -> None:
    for path in out_dir.glob("blender-*.png"):
        path.unlink()
        print(f"removed old Blender render {path}", flush=True)
    for job in RENDERS:
        _render_one(mesh_dir=mesh_dir, out_dir=out_dir, job=job)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render FreeCAD mesh exports with Blender.")
    parser.add_argument("--mesh-dir", type=Path, default=_mesh_root())
    parser.add_argument("--out-dir", type=Path, default=_screenshots_root())
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    render_all(mesh_dir=args.mesh_dir, out_dir=args.out_dir)


if __name__ == "__main__":
    script_args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    main(script_args)
