"""Native manufactured solids, stable IDs, drawings and reopen correspondence.

Only controlled representation contracts are consumed; this creates documents
from known primitives instead of executing uploaded FreeCAD objects/macros.
"""

from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import shutil


def bbox_overlap_volume(left, right):
    """Intersection-box volume bounds the possible material overlap, in mm³.

    Face/edge contact has no positive volume. Avoid a Boolean for boxes whose
    entire overlap cannot exceed the existing material-collision tolerance;
    some OCC versions return a null shape for exact touching faces. Positive
    volume cases still execute the original Boolean and retain its failures.
    """
    volume = 1.
    for axis in 'XYZ':
        extent = min(getattr(left, axis+'Max'), getattr(right, axis+'Max')) - max(getattr(left, axis+'Min'), getattr(right, axis+'Min'))
        volume *= max(0., extent)
    return volume


def native(input_path, output):
    import FreeCAD as App
    import Part
    import numpy as np
    from osr_mech.automated_geometry import native_shape, primitive_volume
    from osr_mech.freecad_assembly_review import _canonicalise_fcstd
    from engineering.design_consistency.contracts import validate

    model = json.loads(Path(input_path).read_text())
    validate(model)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    doc = App.newDocument("ControlledCandidate")
    checks = []
    objects = []
    for index, p in enumerate(model["parts"]):
        obj = doc.addObject("Part::Feature", "Physical_" + str(index))
        obj.Label = p["id"]
        obj.Shape = native_shape(p["manufacturing"], Part, App)
        matrix = App.Matrix()
        for i in range(3):
            for j in range(3):
                setattr(matrix, f"A{i+1}{j+1}", p["placement"]["rotation"][i][j])
        obj.Placement = App.Placement(
            App.Vector(*(v * 1000 for v in p["placement"]["translation_m"])),
            App.Rotation(matrix),
        )
        for field, value in [
            ("PhysicalPartId", p["id"]),
            ("PartRevision", p["revision"]),
            ("MaterialIdentity", p["material"]),
            ("GeometrySHA256", p["analysis"]["geometry_sha256"]),
            ("InspectionCharacteristics", json.dumps(p["inspection_characteristics"])),
        ]:
            obj.addProperty("App::PropertyString", field)
            setattr(obj, field, value)
        obj.addProperty("App::PropertyBool", "ProductionReleased")
        obj.ProductionReleased = False
        shape = obj.Shape
        density = model["materials"][p["material"]]["density_kg_m3"]
        mass = shape.Volume / 1e9 * density
        centres = [
            np.array([s.CenterOfMass.x, s.CenterOfMass.y, s.CenterOfMass.z]) / 1000
            for s in shape.Solids
        ]
        masses = [s.Volume / 1e9 * density for s in shape.Solids]
        cg = sum((m * c for m, c in zip(masses, centres)), np.zeros(3)) / mass
        inertia = np.zeros((3, 3))
        for solid, m, c in zip(shape.Solids, masses, centres):
            own = (
                np.array(
                    [
                        [
                            getattr(solid.MatrixOfInertia, f"A{i+1}{j+1}")
                            for j in range(3)
                        ]
                        for i in range(3)
                    ]
                )
                * density
                / 1e15
            )
            delta = c - cg
            inertia += own + m * ((delta @ delta) * np.eye(3) - np.outer(delta, delta))
        expected = p["properties"]
        error = abs(mass / expected["mass_kg"] - 1)
        cg_error = float(np.linalg.norm(cg - expected["cg_m"]))
        inertia_error = float(
            np.linalg.norm(inertia - expected["inertia_tensor_kg_m2"])
            / np.linalg.norm(expected["inertia_tensor_kg_m2"])
        )
        if (
            not shape.isValid()
            or error > 1e-7
            or cg_error > 1e-7
            or inertia_error > 1e-7
        ):
            raise ValueError("native physical correspondence failed: " + p["id"])
        checks.append(
            dict(
                physical_id=p["id"],
                mass_relative_error=error,
                cg_error_m=cg_error,
                inertia_relative_error=inertia_error,
            )
        )
        objects.append(obj)
    collisions = []
    for i, obj in enumerate(objects):
        for other in objects[i + 1 :]:
            if bbox_overlap_volume(obj.Shape.BoundBox, other.Shape.BoundBox) > 1e-3:
                volume = obj.Shape.common(other.Shape).Volume
                if volume > 1e-3:
                    collisions.append(
                        dict(
                            left=obj.PhysicalPartId,
                            right=other.PhysicalPartId,
                            overlap_mm3=volume,
                        )
                    )
    if collisions:
        raise ValueError(
            "defined materials collide; native geometry retained for review"
        )
    page = doc.addObject("TechDraw::DrawPage", "UnissuedInspectionDrawing")
    template = doc.addObject("TechDraw::DrawSVGTemplate", "Template")
    template.Template = str(
        sorted((Path(App.getResourceDir()) / "Mod/TechDraw/Templates").glob("*.svg"))[0]
    )
    page.Template = template
    view = doc.addObject("TechDraw::DrawViewPart", "AssemblyProjection")
    view.Source = objects
    view.Direction = App.Vector(0, -1, 0)
    view.X = 148
    view.Y = 105
    view.Scale = 0.03
    page.addView(view)
    page.addProperty("App::PropertyBool", "DrawingIssued")
    page.DrawingIssued = False
    doc.recompute()
    edges = len(view.getVisibleEdges())
    if not edges:
        raise ValueError("empty native inspection drawing")
    model_file = output / "candidate.FCStd"
    step = output / "candidate.step"
    Part.export(objects, str(step))
    doc.saveAs(str(model_file))
    App.closeDocument(doc.Name)
    _canonicalise_fcstd(model_file)
    reopened = App.openDocument(str(model_file))
    restored = [o for o in reopened.Objects if "PhysicalPartId" in o.PropertiesList]
    if {o.PhysicalPartId for o in restored} != {p["id"] for p in model["parts"]} or any(
        not o.Shape.isValid() or o.ProductionReleased for o in restored
    ):
        raise ValueError("native reopen changed identities or release state")
    App.closeDocument(reopened.Name)
    shape = Part.read(str(step))
    expected_volume = (
        sum(
            primitive_volume(p)
            for part in model["parts"]
            for p in part["manufacturing"]["primitives"]
        )
        * 1e9
    )
    if not shape.isValid() or abs(shape.Volume / expected_volume - 1) > 1e-7:
        raise ValueError("STEP round-trip occupied volume differs")
    receipt = dict(
        schema="osr-candidate-native-cad/1",
        input_sha256=hashlib.sha256(Path(input_path).read_bytes()).hexdigest(),
        checks=checks,
        physical_ids_preserved=True,
        native_reopened=True,
        step_volume_reconciled=True,
        inspection_projection_edges=edges,
        freecad_version=list(App.Version()),
        opencascade_version=Part.OCC_VERSION,
        drawing_issued=False,
        physical_release=False,
        files_sha256={
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (model_file, step)
        },
    )
    (output / "native-cad.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    return receipt


def generate(contract_path, output, root):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    script = output / "generate.py"
    ok = output / "completed"
    source = Path(__file__).resolve()
    script.write_text(
        "import sys,runpy\nfrom pathlib import Path\n"
        "sys.path[:0]="
        + repr([str(root), str(root / "design/component-catalogue/src")])
        + "\n"
        "module=runpy.run_path(" + repr(str(source)) + ")\n"
        'module["native"]('
        + repr(str(Path(contract_path).resolve()))
        + ","
        + repr(str(output.resolve()))
        + ")\n"
        "Path(" + repr(str(ok.resolve())) + ').write_text("completed")\n'
    )
    binary = shutil.which("FreeCADCmd") or shutil.which("freecadcmd")
    command = (
        [binary]
        if binary
        else [
            "flatpak",
            "run",
            "--filesystem=" + str(root),
            "--filesystem=" + str(output.resolve()),
            "--command=FreeCADCmd",
            "org.freecad.FreeCAD",
        ]
    )
    with (output / "freecad.log").open("w") as log:
        subprocess.run(
            [*command, str(script.resolve())],
            stdout=log,
            stderr=subprocess.STDOUT,
            cwd=root,
            timeout=600,
            check=True,
        )
    if not ok.is_file() or not (output / "native-cad.json").is_file():
        raise RuntimeError("native CAD did not seal a successful correspondence result")
    return json.loads((output / "native-cad.json").read_text())
