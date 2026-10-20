"""Native FreeCAD solids and FCStd/STEP reopen evidence for factory examples."""

from __future__ import annotations

import hashlib
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import re
import tempfile
import uuid
import zipfile

FCSTD_NAMESPACE = uuid.UUID("f42effa5-2414-5f3f-a53c-1198e907e5e2")


def _canonicalise_fcstd(path: Path) -> None:
    """Remove FreeCAD save-time/UUID/ZIP metadata from a tracked review file."""

    with zipfile.ZipFile(path, "r") as source:
        entries = [(info, source.read(info.filename)) for info in source.infolist()]
        comment = source.comment
    canonical_entries: list[tuple[zipfile.ZipInfo, bytes]] = []
    document_uid = str(uuid.uuid5(FCSTD_NAMESPACE, path.name))
    for info, data in entries:
        if info.filename == "Document.xml":
            text = data.decode("utf-8")
            text = re.sub(
                r'(<Property name="(?:CreationDate|LastModifiedDate)"[^>]*>\s*<String value=")[^"]+',
                r"\g<1>2000-01-01T00:00:00Z",
                text,
            )
            text = re.sub(
                r'(<Property name="Uid"[^>]*>\s*<Uuid value=")[^"]+',
                rf"\g<1>{document_uid}",
                text,
            )
            object_id = 0

            def canonical_object_id(match: re.Match[str]) -> str:
                nonlocal object_id
                object_id += 1
                return f'{match.group(1)}{object_id}{match.group(2)}'

            text = re.sub(
                r'(<Object type="[^"]+" name="[^"]+" id=")\d+("\s*/>)',
                canonical_object_id,
                text,
            )
            data = text.encode("utf-8")
        canonical = zipfile.ZipInfo(info.filename, date_time=(2000, 1, 1, 0, 0, 0))
        canonical.compress_type = info.compress_type
        canonical.external_attr = info.external_attr
        canonical.internal_attr = info.internal_attr
        canonical.create_system = info.create_system
        canonical_entries.append((canonical, data))
    with tempfile.NamedTemporaryFile(
        "wb", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        temporary = Path(handle.name)
    try:
        with zipfile.ZipFile(temporary, "w") as target:
            target.comment = comment
            for info, data in canonical_entries:
                target.writestr(info, data)
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def export_native(model_path, output):
    import FreeCAD as App
    import Part
    from engineering.factory_examples.models import volume, global_size

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
        if p["kind"] == "stepped-cylinder":
            shape = None
            level = at[2]
            for step in p["steps"]:
                solid = Part.makeCylinder(
                    step["diameter_m"] * 500,
                    step["length_m"] * 1000,
                    App.Vector(at[0] + size[0] / 2, at[1] + size[1] / 2, level),
                )
                shape = solid if shape is None else shape.fuse(solid)
                level += step["length_m"] * 1000
        elif p["kind"] == "cylinder":
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
            axis = "xyz".index(hole.get("axis", "z"))
            start = at.copy()
            for j in range(3):
                start[j] += (
                    hole.get("start_m", 0) * 1000
                    if j == axis
                    else hole["xyz"[j] + "_m"] * 1000
                )
            direction = [0, 0, 0]
            direction[axis] = 1
            cut = Part.makeCylinder(
                hole["diameter_m"] * 500,
                hole.get("length_m", p["size_m"][axis]) * 1000,
                App.Vector(*start),
                App.Vector(*direction),
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
    # Check positive shared volume only for the explicitly selected physical roles.
    collisions = []
    interference_roles = model.get("interference_roles", [])
    check_objects = [o for o in objects if o.Role in interference_roles]
    if check_objects:
        for i, obj in enumerate(check_objects):
            for other in check_objects[i + 1 :]:
                if obj.Shape.BoundBox.intersect(other.Shape.BoundBox):
                    overlap = obj.Shape.common(other.Shape).Volume
                    if overlap > 1e-3:
                        collisions.append(
                            dict(left=obj.DesignId, right=other.DesignId, mm3=overlap)
                        )
        if collisions:
            raise ValueError("selected-role solid interference: " + str(collisions))
    interference_ids = [o.DesignId for o in check_objects]
    mesh_path = None
    if model.get("retain_native_tessellation"):
        mesh = []
        for obj, definition in zip(objects, model["parts"]):
            vertices, triangles = obj.Shape.tessellate(10.)
            mesh.append(dict(id=obj.DesignId, material=definition['material'],
                             vertices_m=[[v.x/1000, v.y/1000, v.z/1000] for v in vertices],
                             triangles=[list(t) for t in triangles],
                             centre_of_volume_m=[sum(s.Volume*tuple(s.CenterOfMass)[i] for s in obj.Shape.Solids)/obj.Shape.Volume/1000 for i in range(3)],
                             volume_m3=obj.Shape.Volume/1e9))
        mesh_path=output/'native-mesh.json.gz'
        mesh_path.write_bytes(gzip.compress(json.dumps(dict(schema='osr-native-tessellation/1',
            input_sha256=digest(model_path),linear_deflection_mm=10.,parts=mesh,
            scope='Actual native-solid tessellation for visual review; no motion or strength verification',
            physical_release=False),sort_keys=True).encode(),mtime=0))
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
        geometry_helpers_sha256=digest(Path(__file__).with_name("models.py")),
        freecad_version=list(App.Version()),
        opencascade_version=Part.OCC_VERSION,
        part_count=len(checks),
        parts=checks,
        fcstd_reopened=True,
        step_reopened=True,
        volume_sum_m3=expected_volume,
        checked_interference_roles=interference_roles,
        interference_checked_ids=interference_ids,
        note="Only declared role pairs receive positive-volume checks; other roles and envelopes have no interference acceptance",
        physical_release=False,
        files_sha256={p.name: digest(p) for p in (fcstd, step)},
    )
    if mesh_path is not None:
        receipt['files_sha256'][mesh_path.name]=digest(mesh_path)
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
        + repr([str(root)])
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
