"""Render the same assembly meshes as the films under physical materials and lighting."""

import argparse
from hashlib import sha256
import importlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess

from render import world_vertices

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def export_view(module, key, target):
    frame = module.RENDERS[key]()
    eye = getattr(module, "RENDER_EYES", {}).get(key)
    record = {
        "view": key,
        "camera": {"target": frame.camera.target, "yaw": frame.camera.yaw,
                   "elevation": frame.camera.elevation, "width": frame.camera.width, "eye": eye},
        "items": [{"name": item.mesh.name, "vertices": world_vertices(item).tolist(),
                   "faces": item.mesh.faces, "color": item.color} for item in frame.items],
    }
    target.write_text(json.dumps(record, separators=(",", ":"), allow_nan=False))


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--view", action="append", help="Render only a named view")
    parser.add_argument("--blender", default="blender", help="Blender command or 'flatpak'")
    parser.add_argument("--samples", type=int, default=24, choices=range(4, 65), metavar="[4-64]")
    args = parser.parse_args()
    target = args.output.resolve()
    target.mkdir(parents=True, exist_ok=True)
    command = ["flatpak", "run", "org.blender.Blender"] if args.blender == "flatpak" else [args.blender]
    available = {key: module for name in ("train", "viaduct")
                 for module in (importlib.import_module(name),) for key in module.RENDERS}
    names = args.view or ["train-saloon", "viaduct-placement", *(
        name for name in available if name not in ("train-saloon", "viaduct-placement"))]
    if not set(names).issubset(available):
        parser.error(f"Available views: {', '.join(available)}")
    with TemporaryDirectory(dir=target, prefix=".render-geometry-") as tmp:
        scenes = []
        for name in names:
            path = Path(tmp) / f"{name}.json"
            export_view(available[name], name, path)
            scenes.append(path)
        version = subprocess.check_output([*command, "--background", "--version"], text=True).splitlines()[0]
        subprocess.run([*command, "--background", "--factory-startup", "--threads", "4",
                        "--python-exit-code", "1", "--python", str(HERE / "blender_views.py"), "--",
                        str(target), str(args.samples), *map(str, scenes)], check=True)
        source_files = {file for mod in available.values() for file in mod.SOURCES}
        source_files.update((HERE / file).relative_to(ROOT).as_posix() for file in
                            ("render_views.py", "blender_views.py", "scene.py", "train.py", "viaduct.py", "render.py"))
        receipt = dict(renderer=version, samples=args.samples,
                       sources={file: digest(ROOT / file) for file in sorted(source_files)},
                       views={file.stem: {"scene_sha256": digest(file),
                                          "render_sha256": digest(target / f"{file.stem}.jpg")} for file in scenes})
        (target / "views-receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
