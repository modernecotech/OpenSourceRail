"""Native FreeCAD solids and FCStd/STEP reopen evidence for factory examples."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def export_native(model_path, output):
    import FreeCAD as App
    import Part
    from engineering.factory_examples.models import volume, global_size
    from osr_mech.freecad_assembly_review import _canonicalise_fcstd

    model_path, output = Path(model_path), Path(output)
    model = json.loads(model_path.read_text())
    output.mkdir(parents=True, exist_ok=True)
    doc = App.newDocument("FactoryDevelopment")
    checks = []
    objects = []

    def shape_bounds(shape):
        b = shape.BoundBox
        return [v / 1000 for v in (b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax)]

    for i, p in enumerate(model["parts"]):
        size = [v * 1000 for v in p["size_m"]]
        at = [v * 1000 for v in p["at_m"]]
        if p["kind"] == "cylinder":
            axis = p.get("cylinder_axis", "z")
            # size is local diameter, diameter, length; at is lower global bound.
            idx = "xyz".index(axis)
            origin = at.copy()
            for j in range(3):
                if j != idx:
                    origin[j] += size[0] / 2
            direction = [0, 0, 0]
            direction[idx] = 1
            shape = Part.makeCylinder(
                size[0] / 2, size[2], App.Vector(*origin), App.Vector(*direction)
            )
        else:
            shape = Part.makeBox(*size, App.Vector(*at))
            if p["kind"] == "tube":
                wall = p["wall_m"] * 1000
                inside = size.copy()
                start = at.copy()
                for j in range(3):
                    if j != p["axis"]:
                        inside[j] -= 2 * wall
                        start[j] += wall
                shape = shape.cut(Part.makeBox(*inside, App.Vector(*start)))
            for hole in p.get("holes", []):
                cut = Part.makeCylinder(
                    hole["diameter_m"] * 500,
                    size[2],
                    App.Vector(
                        at[0] + hole["x_m"] * 1000, at[1] + hole["y_m"] * 1000, at[2]
                    ),
                )
                shape = shape.cut(cut)
        expected = volume(p) * 1e9
        expected_bounds = p["at_m"] + [
            p["at_m"][j] + global_size(p)[j] for j in range(3)
        ]
        if (
            not shape.isValid()
            or not shape.Solids
            or abs(shape.Volume / expected - 1) > 1e-7
            or max(abs(x - y) for x, y in zip(shape_bounds(shape), expected_bounds))
            > 1e-8
        ):
            raise ValueError("native primitive correspondence: " + p["id"])
        obj = doc.addObject("Part::Feature", f"Object{i:04d}")
        obj.Label = p["id"]
        obj.Shape = shape
        for name, value in [
            ("DesignId", p["id"]),
            ("Role", p["role"]),
            ("Basis", p.get("basis", "OSR development geometry")),
        ]:
            obj.addProperty("App::PropertyString", name)
            setattr(obj, name, value)
        obj.addProperty("App::PropertyBool", "ProductionReleased")
        obj.ProductionReleased = False
        objects.append(obj)
        checks.append(
            dict(
                id=p["id"],
                volume_m3=shape.Volume / 1e9,
                bounds_m=[
                    v / 1000
                    for v in (
                        shape.BoundBox.XMin,
                        shape.BoundBox.YMin,
                        shape.BoundBox.ZMin,
                        shape.BoundBox.XMax,
                        shape.BoundBox.YMax,
                        shape.BoundBox.ZMax,
                    )
                ],
            )
        )
    # Tooling fixture contains separate materials: check actual positive common volume.
    collisions = []
    if model["id"] == "OSR-FIX-500":
        for i, obj in enumerate(objects):
            for other in objects[i + 1 :]:
                if obj.Shape.BoundBox.intersect(other.Shape.BoundBox):
                    overlap = obj.Shape.common(other.Shape).Volume
                    if overlap > 1e-3:
                        collisions.append(
                            dict(left=obj.DesignId, right=other.DesignId, mm3=overlap)
                        )
        if collisions:
            raise ValueError("fixture solid interference: " + str(collisions))
    doc.recompute()
    fcstd, step = output / "model.FCStd", output / "model.step"
    Part.export(objects, str(step))
    doc.saveAs(str(fcstd))
    App.closeDocument(doc.Name)
    _canonicalise_fcstd(fcstd)
    restored = App.openDocument(str(fcstd))
    found = [o for o in restored.Objects if "DesignId" in o.PropertiesList]
    expected_ids = {p["id"] for p in model["parts"]}
    if (
        len(expected_ids) != len(model["parts"])
        or {o.DesignId for o in found} != expected_ids
    ):
        raise ValueError("native reopen identity mismatch")
    by_id = {c["id"]: c for c in checks}
    for obj in found:
        if (
            obj.ProductionReleased
            or not obj.Shape.isValid()
            or abs(obj.Shape.Volume / 1e9 / by_id[obj.DesignId]["volume_m3"] - 1) > 1e-7
            or max(
                abs(x - y)
                for x, y in zip(
                    shape_bounds(obj.Shape), by_id[obj.DesignId]["bounds_m"]
                )
            )
            > 1e-8
        ):
            raise ValueError("native reopen state or shape changed")
    App.closeDocument(restored.Name)
    roundtrip = Part.read(str(step))
    expected_volume = sum(c["volume_m3"] for c in checks)
    if (
        not roundtrip.isValid()
        or abs(roundtrip.Volume / 1e9 / expected_volume - 1) > 1e-7
    ):
        raise ValueError("STEP occupied volume round-trip mismatch")
    receipt = dict(
        schema="osr-factory-native-cad/1",
        input_sha256=digest(model_path),
        exporter_sha256=digest(__file__),
        freecad_version=list(App.Version()),
        opencascade_version=Part.OCC_VERSION,
        part_count=len(checks),
        parts=checks,
        fcstd_reopened=True,
        step_reopened=True,
        volume_sum_m3=expected_volume,
        fixture_interferences_checked=model["id"] == "OSR-FIX-500",
        note="Other scenes intentionally overlay strand, concrete and manufacturing-state envelopes; no interference acceptance implied",
        physical_release=False,
        files_sha256={p.name: digest(p) for p in (fcstd, step)},
    )
    (output / "native-cad.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )


def generate(model_path, output, root):
    work = root / "build/factory-examples-native" / Path(output).name
    work.mkdir(parents=True, exist_ok=True)
    script, ok = work / "generate.py", work / "completed"
    ok.unlink(missing_ok=True)
    script.write_text(
        "import sys\nfrom pathlib import Path\n"
        "sys.path[:0]="
        + repr([str(root), str(root / "design/component-catalogue/src")])
        + "\n"
        "from engineering.factory_examples.native import export_native\n"
        "export_native("
        + repr(str(model_path.resolve()))
        + ","
        + repr(str(output.resolve()))
        + ")\n"
        "Path(" + repr(str(ok.resolve())) + ").write_text('complete')\n"
    )
    binary = shutil.which("FreeCADCmd") or shutil.which("freecadcmd")
    command = (
        [binary]
        if binary
        else [
            "flatpak",
            "run",
            "--filesystem=" + str(root),
            "--command=FreeCADCmd",
            "org.freecad.FreeCAD",
        ]
    )
    with (work / "freecad.log").open("w") as log:
        subprocess.run(
            [*command, str(script.resolve())],
            cwd=root,
            stdout=log,
            stderr=subprocess.STDOUT,
            timeout=600,
            check=True,
        )
    if not ok.is_file():
        raise RuntimeError(
            "Native CAD incomplete; inspect " + str(work / "freecad.log")
        )
    return json.loads((output / "native-cad.json").read_text())
