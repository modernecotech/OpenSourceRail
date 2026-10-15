"""Actual BRep -> Gmsh quadratic tetrahedra -> CalculiX elastic part evidence.

Native CAD uses mm; the deck uses N, mm and MPa. Public metrics use SI.
Fixtures are ideal clamps, and stress demand is not a resistance assessment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
import uuid
import zipfile


class NativeFailure(RuntimeError):
    pass


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _write(path, value):
    Path(path).write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )


def toolchain():
    """Stable actual runtime identities, suitable for source/cache binding."""
    result = dict(schema="osr-generated-parts-toolchain/1", available=True, missing=[])
    try:
        import gmsh

        library = Path(gmsh.lib._name).resolve()
        result["gmsh"] = dict(
            version=gmsh.__version__,
            module_path=gmsh.__file__,
            module_sha256=_sha(gmsh.__file__),
            library_path=str(library),
            library_sha256=_sha(library),
        )
    except (ImportError, OSError) as error:
        result["missing"].append("gmsh Python/native library")
        result["gmsh"] = dict(error=type(error).__name__)
    ccx = shutil.which("ccx")
    if ccx:
        proc = subprocess.run([ccx, "-v"], capture_output=True, text=True, timeout=10)
        text = proc.stdout + proc.stderr
        match = re.search(r"Version\s+([0-9.]+)", text)
        if not match:
            result["missing"].append("CalculiX version")
        result["calculix"] = dict(
            path=ccx,
            resolved_path=str(Path(ccx).resolve()),
            binary_sha256=_sha(Path(ccx).resolve()),
            version=match.group(1) if match else None,
        )
    else:
        result["missing"].append("CalculiX")
    freecad = shutil.which("FreeCADCmd") or shutil.which("freecadcmd")
    if freecad:
        result["freecad"] = dict(
            kind="binary", path=freecad, binary_sha256=_sha(Path(freecad).resolve())
        )
    elif shutil.which("flatpak"):
        try:
            commit = subprocess.check_output(
                ["flatpak", "info", "--show-commit", "org.freecad.FreeCAD"],
                text=True,
                timeout=10,
            ).strip()
            info = subprocess.check_output(
                ["flatpak", "info", "org.freecad.FreeCAD"], text=True, timeout=10
            )
            runtime = subprocess.check_output(
                ["flatpak", "info", "--show-runtime", "org.freecad.FreeCAD"],
                text=True,
                timeout=10,
            ).strip()
            runtime_commit = subprocess.check_output(
                ["flatpak", "info", "--show-commit", runtime], text=True, timeout=10
            ).strip()
            version = re.search(r"Version:\s+(\S+)", info)
            result["freecad"] = dict(
                kind="flatpak",
                application="org.freecad.FreeCAD",
                commit=commit,
                version=version.group(1) if version else None,
                runtime=runtime,
                runtime_commit=runtime_commit,
            )
        except (subprocess.SubprocessError, OSError):
            result["missing"].append("FreeCAD")
    else:
        result["missing"].append("FreeCAD")
    result["available"] = not result["missing"]
    return result


class _Time:
    def __init__(self, remaining):
        self.callback = remaining if callable(remaining) else None
        self.deadline = (
            None
            if remaining is None or callable(remaining)
            else time.monotonic() + remaining
        )

    def timeout(self, maximum):
        remaining = (
            self.callback()
            if self.callback
            else (self.deadline - time.monotonic() if self.deadline else maximum)
        )
        if not math.isfinite(remaining) or remaining <= 0:
            raise TimeoutError("native part wall-time budget exhausted")
        return min(maximum, remaining)


def _run(command, folder, log, budget, maximum=60):
    timeout = budget.timeout(maximum)
    env = dict(
        os.environ,
        OMP_NUM_THREADS="1",
        OPENBLAS_NUM_THREADS="1",
        MKL_NUM_THREADS="1",
        CCX_NPROC_RESULTS="1",
        CCX_NPROC_EQUATION_SOLVER="1",
    )
    with Path(log).open("w") as stream:
        stream.write(json.dumps(dict(command=command, timeout_seconds=timeout)) + "\n")
        stream.flush()
        # Inherit the design worker's group: the common watchdog must also own
        # CAD/mesh/solver children if it kills the worker abruptly.
        process = subprocess.Popen(
            command, cwd=folder, env=env, stdout=stream, stderr=subprocess.STDOUT
        )
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            _stop_owned_descendants(process)
            raise TimeoutError(
                "native subprocess exceeded declared remaining budget; raw log retained"
            )
        finally:
            if process.poll() is None:
                _stop_owned_descendants(process)
    if code:
        raise NativeFailure(
            "native subprocess failed exit " + str(code) + "; inspect " + str(log)
        )


def _stop_owned_descendants(process):
    """Narrow Linux cleanup using pinned kernel PIDfds, never the shared PGID."""
    if process.poll() is not None:
        return
    if not hasattr(os, "pidfd_open") or not Path("/proc/self/stat").is_file():
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        return
    records = {}
    for path in Path("/proc").iterdir():
        if not path.name.isdigit():
            continue
        try:
            text = (path / "stat").read_text()
            fields = text[text.rfind(")") + 2 :].split()
            records[int(path.name)] = (int(fields[1]), int(fields[19]))
        except (OSError, ValueError):
            continue
    owned = {process.pid}
    for _ in range(len(records)):
        added = {pid for pid, (parent, _) in records.items() if parent in owned} - owned
        if not added:
            break
        owned.update(added)
    handles = []
    try:
        for pid in sorted(owned, reverse=True):
            if pid not in records:
                continue
            descriptor = None
            try:
                descriptor = os.pidfd_open(pid)
                text = (Path("/proc") / str(pid) / "stat").read_text()
                fields = text[text.rfind(")") + 2 :].split()
                if int(fields[19]) != records[pid][1]:
                    os.close(descriptor)
                    continue
                signal.pidfd_send_signal(descriptor, signal.SIGTERM)
                handles.append(descriptor)
            except (ProcessLookupError, FileNotFoundError):
                if descriptor is not None:
                    os.close(descriptor)
                continue
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            pass
        for descriptor in handles:
            try:
                signal.pidfd_send_signal(descriptor, signal.SIGKILL)
            except ProcessLookupError:
                pass
        process.wait(timeout=2)
    finally:
        for descriptor in handles:
            os.close(descriptor)


def native_cad_export(model_path, output):
    """FreeCADCmd entry point: only controlled primitive definitions are consumed."""
    import FreeCAD as App
    import Part

    model = json.loads(Path(model_path).read_text())
    output = Path(output)
    primitives = model["parts"][0]["geometry"]["components"]
    shape = None
    for row in primitives:
        centre = [v * 1000 for v in row["centre_m"]]
        if row["shape"] == "box":
            dimensions = [v * 1000 for v in row["dimensions_m"]]
            # Through cuts extend beyond end faces; occupied overlap remains
            # exactly the signed primitive volume in the physical definition.
            if (
                row["operation"] == "subtract"
                and dimensions[0] == primitives[0]["dimensions_m"][0] * 1000
            ):
                dimensions[0] += 2
            origin = App.Vector(*(centre[i] - dimensions[i] / 2 for i in range(3)))
            primitive = Part.makeBox(*dimensions, origin)
        elif row["shape"] == "cylinder-z":
            length = row["length_m"] * 1000 + 2
            primitive = Part.makeCylinder(
                row["radius_m"] * 1000,
                length,
                App.Vector(centre[0], centre[1], centre[2] - length / 2),
            )
        else:
            raise ValueError("unknown controlled primitive")
        shape = (
            primitive
            if shape is None
            else (
                shape.fuse(primitive)
                if row["operation"] == "add"
                else shape.cut(primitive)
            )
        )
    shape = shape.removeSplitter()
    if not shape.isValid() or len(shape.Solids) != 1 or shape.Volume <= 0:
        raise ValueError("native cut solid is invalid/disconnected")
    document = App.newDocument("GeneratedResearchPart")
    obj = document.addObject("Part::Feature", "ResearchPart")
    obj.Shape = shape
    obj.addProperty("App::PropertyString", "PhysicalDefinitionSHA256")
    obj.PhysicalDefinitionSHA256 = model["physical_definition_sha256"]
    obj.addProperty("App::PropertyBool", "ProductionReleased")
    obj.ProductionReleased = False
    document.recompute()
    shape.exportBrep(str(output / "part.brep"))
    Part.export([obj], str(output / "part.step"))
    document.saveAs(str(output / "part.FCStd"))
    # STEP transport header time/path does not define geometry.
    step = (output / "part.step").read_text()
    step = re.sub(
        r"FILE_NAME\(.*?\);",
        "FILE_NAME('part.step','1970-01-01T00:00:00',('OpenSourceRail'),(''),'FreeCAD','OpenCASCADE','');",
        step,
        flags=re.S,
    )
    (output / "part.step").write_text(step)
    restored = Part.read(str(output / "part.step"))
    if not restored.isValid() or abs(restored.Volume / shape.Volume - 1) > 1e-8:
        raise ValueError("STEP round-trip volume/validity failed")
    density = model["materials"][model["parts"][0]["material"]]["density_kg_m3"]
    solid = shape.Solids[0]
    inertia = [
        [
            getattr(solid.MatrixOfInertia, f"A{i+1}{j+1}") * density / 1e15
            for j in range(3)
        ]
        for i in range(3)
    ]
    report = dict(
        valid=True,
        solids=len(shape.Solids),
        volume_m3=shape.Volume / 1e9,
        mass_kg=shape.Volume * density / 1e9,
        cg_m=[
            solid.CenterOfMass.x / 1000,
            solid.CenterOfMass.y / 1000,
            solid.CenterOfMass.z / 1000,
        ],
        inertia_tensor_kg_m2=inertia,
        freecad_version=list(App.Version()),
        opencascade_version=Part.OCC_VERSION,
        step_roundtrip_valid=True,
        definition_sha256=model["physical_definition_sha256"],
        physical_release=False,
    )
    # Orthographic inspection projections of the actual native edges.
    width = model["parts"][0]["geometry"]["envelope_m"][0] * 1000
    scale = 700 / max(width, 1)
    paths = []
    for view, axis in enumerate((1, 2)):
        for edge in shape.Edges:
            points = edge.discretize(Deflection=0.1)
            projected = [
                (
                    40 + p.x * scale,
                    140 + view * 220 - (p.y if axis == 1 else p.z) * scale,
                )
                for p in points
            ]
            if len(projected) > 1:
                paths.append(
                    '<polyline fill="none" stroke="#17324d" stroke-width="0.7" points="'
                    + " ".join(f"{x:.6f},{y:.6f}" for x, y in projected)
                    + '"/>'
                )
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500" viewBox="0 0 800 500"><rect width="800" height="500" fill="white"/>'
    svg += '<text x="30" y="25">Actual native solid projections — UNISSUED RESEARCH INSPECTION</text>'
    svg += (
        "".join(paths)
        + '<text x="30" y="465">Clearance holes do not establish bolt/contact resistance. Dimensions in model SI; projection uses mm.</text></svg>'
    )
    (output / "inspection.svg").write_text(svg)
    _write(output / "native-cad.json", report)
    App.closeDocument(document.Name)
    _canonical_fcstd(output / "part.FCStd", model["physical_definition_sha256"])


def _canonical_fcstd(path, definition_hash):
    """Normalize transport dates/UUIDs while preserving every shape byte."""
    with zipfile.ZipFile(path) as source:
        entries = [(info, source.read(info.filename)) for info in source.infolist()]
    temporary = Path(path).with_suffix(".canonical")
    with zipfile.ZipFile(temporary, "w") as target:
        for info, data in entries:
            if info.filename == "Document.xml":
                text = data.decode()
                text = re.sub(
                    r'(<Property name="(?:CreationDate|LastModifiedDate)"[^>]*>\s*<String value=")[^"]+',
                    r"\g<1>2000-01-01T00:00:00Z",
                    text,
                )
                text = re.sub(
                    r'(<Property name="Uid"[^>]*>\s*<Uuid value=")[^"]+',
                    lambda m: m[1]
                    + str(uuid.uuid5(uuid.NAMESPACE_URL, definition_hash)),
                    text,
                )
                text = re.sub(
                    r'(<Object type="[^"]+" name="[^"]+" id=")\d+("\s*/>)',
                    r"\g<1>1\2",
                    text,
                )
                data = text.encode()
            canonical = zipfile.ZipInfo(info.filename, date_time=(2000, 1, 1, 0, 0, 0))
            canonical.compress_type = info.compress_type
            canonical.external_attr = info.external_attr
            target.writestr(canonical, data)
    temporary.replace(path)


def _mesh_worker(brep, output, size_m, length_m):
    import gmsh
    import numpy as np

    output = Path(output)
    gmsh.initialize([])
    try:
        for name, value in {
            "General.NumThreads": 1,
            "Mesh.MaxNumThreads3D": 1,
            "Mesh.MeshSizeMin": min(size_m * 1000, 1.5),
            "Mesh.MeshSizeMax": size_m * 1000,
            "Mesh.ElementOrder": 2,
            "Mesh.MeshSizeFromCurvature": 12,
            "Mesh.SecondOrderLinear": 0,
            "Mesh.RandomSeed": 1,
            "Mesh.RandomFactor": 1e-9,
            "Mesh.MshFileVersion": 2.2,
        }.items():
            gmsh.option.setNumber(name, value)
        gmsh.model.occ.importShapes(str(brep))
        gmsh.model.occ.synchronize()
        if len(gmsh.model.getEntities(3)) != 1:
            raise ValueError("mesh must consume exactly the same single CAD solid")
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.optimize("HighOrder")
        gmsh.write(str(output / "mesh.msh"))
        gmsh.write(str(output / "mesh-native.inp"))
        tags, coordinates, _ = gmsh.model.mesh.getNodes()
        nodes = {
            int(tag): xyz.tolist()
            for tag, xyz in zip(tags, np.asarray(coordinates).reshape(-1, 3))
        }
        roots, ends = [], []
        for _, surface in gmsh.model.getEntities(2):
            bounds = gmsh.model.getBoundingBox(2, surface)
            plane = bounds[3] - bounds[0] < 1e-4
            if plane and abs(bounds[0]) < 1e-4:
                roots.append(surface)
            if plane and abs(bounds[0] - length_m * 1000) < 1e-4:
                ends.append(surface)
        root_nodes = set()
        for surface in roots:
            boundary_tags, _, _ = gmsh.model.mesh.getNodes(
                2, surface, includeBoundary=True
            )
            root_nodes.update(map(int, boundary_tags))
        weights = {}
        end_area = 0.0
        for surface in ends:
            types, _, connectivities = gmsh.model.mesh.getElements(2, surface)
            for kind, connectivity in zip(types, connectivities):
                if kind != 9:
                    raise ValueError(
                        "quadratic triangular end-face traction mesh required"
                    )
                for triangle in np.asarray(connectivity).reshape(-1, 6):
                    xyz = np.asarray([nodes[int(t)] for t in triangle[:3]])
                    area = float(
                        np.linalg.norm(np.cross(xyz[1] - xyz[0], xyz[2] - xyz[0])) / 2
                    )
                    end_area += area
                    # Integral N_i: zero at T6 corners, A/3 at midsides.
                    for tag in triangle[3:]:
                        weights[int(tag)] = weights.get(int(tag), 0.0) + area / 3
        types, element_tags, _ = gmsh.model.mesh.getElements(3)
        if list(types) != [11] or not root_nodes or not weights or end_area <= 0:
            raise ValueError("complete C3D10 volume/root/end map required")
        points, integration_weights = gmsh.model.mesh.getIntegrationPoints(11, "Gauss4")
        _, determinants, _ = gmsh.model.mesh.getJacobians(11, points)
        determinants = np.asarray(determinants).reshape(-1, len(integration_weights))
        if not np.isfinite(determinants).all() or determinants.min() <= 0:
            raise ValueError("nonpositive quadratic tetrahedron Jacobian")
        volume = float(np.sum(determinants * np.asarray(integration_weights))) / 1e9
        if len(nodes) > 60000 or sum(map(len, element_tags)) > 30000:
            raise ValueError("declared small-part mesh budget exceeded")
        result = dict(
            nodes=nodes,
            root_nodes=sorted(root_nodes),
            tip_weights={str(k): v / end_area for k, v in sorted(weights.items())},
            end_area_mm2=end_area,
            volume_m3=volume,
            elements=sum(map(len, element_tags)),
            minimum_jacobian_mm3=float(determinants.min()),
            mesh_size_m=size_m,
            element_ids=sorted(int(t) for group in element_tags for t in group),
            gmsh_version=gmsh.__version__,
            cad_brep_sha256=_sha(brep),
        )
        _write(output / "mesh.json", result)
    finally:
        gmsh.finalize()


def _read_native_elements(path):
    elements, mode = {}, False
    for line in Path(path).read_text().splitlines():
        if line.startswith("*"):
            mode = line.upper().startswith(
                "*ELEMENT"
            ) and "TYPE=C3D10" in line.upper().replace(" ", "")
            continue
        if mode and line.strip():
            numbers = [int(x) for x in line.split(",") if x.strip()]
            if len(numbers) != 11:
                raise NativeFailure(
                    "Gmsh Abaqus C3D10 connectivity absent or malformed"
                )
            elements[numbers[0]] = numbers[1:]
    if not elements:
        raise NativeFailure("Gmsh native Abaqus export contains no C3D10 solids")
    return elements


def write_deck(model, mesh, elements, path):
    nodes = mesh["nodes"]
    if not mesh["root_nodes"] or not mesh["tip_weights"]:
        raise NativeFailure("missing actual geometric support/load faces")
    if set(map(str, mesh["root_nodes"])) & set(mesh["tip_weights"]):
        raise NativeFailure("load and root faces overlap")
    if abs(sum(mesh["tip_weights"].values()) - 1) > 1e-10:
        raise NativeFailure("traction weights do not conserve applied force")
    material = model["materials"][model["parts"][0]["material"]]
    rows = [
        "*HEADING",
        "Same CAD solid, quadratic tetrahedra; N mm MPa; ideal clamp only",
        "*NODE",
    ]
    rows += [
        str(tag) + "," + ",".join(f"{v:.14g}" for v in xyz)
        for tag, xyz in sorted(nodes.items(), key=lambda x: int(x[0]))
    ]
    rows += ["*ELEMENT,TYPE=C3D10,ELSET=SOLID"]
    rows += [
        str(tag) + "," + ",".join(map(str, connectivity))
        for tag, connectivity in sorted(elements.items())
    ]
    rows += [
        "*MATERIAL,NAME=RESEARCH_STEEL",
        "*ELASTIC",
        f"{material['young_pa']/1e6},{material['poisson_ratio']}",
        "*SOLID SECTION,ELSET=SOLID,MATERIAL=RESEARCH_STEEL",
        "*NSET,NSET=ROOT",
    ]
    root = mesh["root_nodes"]
    rows += [",".join(map(str, root[i : i + 12])) for i in range(0, len(root), 12)]
    rows += [
        "*NSET,NSET=ALL",
        *[
            ",".join(map(str, list(nodes)[i : i + 12]))
            for i in range(0, len(nodes), 12)
        ],
        "*BOUNDARY",
        "ROOT,1,3",
        "*STEP",
        "*STATIC",
        "*CLOAD",
    ]
    force = model["loads"][0]["force_n"][2]
    rows += [
        f"{tag},3,{force*weight:.14g}" for tag, weight in mesh["tip_weights"].items()
    ]
    rows += [
        "*NODE PRINT,NSET=ALL",
        "U",
        "*NODE PRINT,NSET=ROOT",
        "RF",
        "*EL PRINT,ELSET=SOLID",
        "S",
        "*END STEP",
    ]
    Path(path).write_text("\n".join(rows) + "\n")


def read_results(path, mesh, applied_force_n):
    displacements, reactions, stresses = {}, {}, {}
    mode = None
    for line in Path(path).read_text().splitlines():
        lower = line.lower()
        if "displacements" in lower:
            mode = "u"
        elif "forces" in lower:
            mode = "rf"
        elif "stresses" in lower:
            mode = "s"
        fields = line.split()
        if mode in {"u", "rf"} and len(fields) == 4 and fields[0].isdigit():
            values = [float(x.replace("D", "E")) for x in fields[1:]]
            (displacements if mode == "u" else reactions)[int(fields[0])] = values
        if (
            mode == "s"
            and len(fields) == 8
            and fields[0].isdigit()
            and fields[1].isdigit()
        ):
            sxx, syy, szz, sxy, sxz, syz = [
                float(x.replace("D", "E")) for x in fields[2:]
            ]
            key = (int(fields[0]), int(fields[1]))
            if key in stresses:
                raise NativeFailure("duplicate native stress integration point")
            stresses[key] = (
                math.sqrt(
                    ((sxx - syy) ** 2 + (syy - szz) ** 2 + (szz - sxx) ** 2) / 2
                    + 3 * (sxy * sxy + sxz * sxz + syz * syz)
                )
                * 1e6
            )
    node_ids = set(map(int, mesh["nodes"]))
    expected_stresses = {
        (tag, point) for tag in mesh["element_ids"] for point in (1, 2, 3, 4)
    }
    if (
        set(displacements) != node_ids
        or set(reactions) != set(mesh["root_nodes"])
        or set(stresses) != expected_stresses
    ):
        raise NativeFailure(
            "complete finite displacement/reaction/stress evidence absent"
        )
    if not all(
        math.isfinite(v)
        for group in (displacements, reactions)
        for vector in group.values()
        for v in vector
    ) or not all(map(math.isfinite, stresses.values())):
        raise NativeFailure("nonfinite native result")
    tip = (
        sum(
            displacements[int(tag)][2] * weight
            for tag, weight in mesh["tip_weights"].items()
        )
        / 1000
    )
    reaction = [sum(v[i] for v in reactions.values()) for i in range(3)]
    balance = math.sqrt(
        sum((reaction[i] + applied_force_n[i]) ** 2 for i in range(3))
    ) / max(1, math.sqrt(sum(v * v for v in applied_force_n)))
    moments = [0.0] * 3
    for tag, vector in reactions.items():
        x, y, z = [v / 1000 for v in mesh["nodes"][str(tag)]]
        moments[0] += y * vector[2] - z * vector[1]
        moments[1] += z * vector[0] - x * vector[2]
        moments[2] += x * vector[1] - y * vector[0]
    applied_moment = [0.0] * 3
    for tag, weight in mesh["tip_weights"].items():
        x, y, z = [v / 1000 for v in mesh["nodes"][tag]]
        fx, fy, fz = [v * weight for v in applied_force_n]
        applied_moment[0] += y * fz - z * fy
        applied_moment[1] += z * fx - x * fz
        applied_moment[2] += x * fy - y * fx
    moment_balance = math.sqrt(
        sum((moments[i] + applied_moment[i]) ** 2 for i in range(3))
    ) / max(1, math.sqrt(sum(v * v for v in applied_moment)))
    return dict(
        loaded_face_deflection_m=abs(tip),
        signed_loaded_face_displacement_m=tip,
        maximum_displacement_m=max(
            math.sqrt(sum(v * v for v in u)) for u in displacements.values()
        )
        / 1000,
        peak_von_mises_pa=max(stresses.values()),
        support_reaction_n=reaction,
        applied_force_n=applied_force_n,
        support_moment_nm=moments,
        applied_moment_nm=applied_moment,
        reaction_balance_relative_error=balance,
        moment_balance_relative_error=moment_balance,
        displacement_nodes=len(displacements),
        stress_integration_points=len(stresses),
    )


def _cad(model, output, root, budget):
    output.mkdir(parents=True, exist_ok=False)
    _write(output / "definition.json", model)
    source = Path(__file__).resolve()
    wrapper = output / "run-freecad.py"
    wrapper.write_text(
        "import runpy\nmodule=runpy.run_path("
        + repr(str(source))
        + ")\nmodule['native_cad_export']("
        + repr(str(output / "definition.json"))
        + ","
        + repr(str(output))
        + ")\n"
    )
    binary = shutil.which("FreeCADCmd") or shutil.which("freecadcmd")
    command = (
        [binary]
        if binary
        else [
            "flatpak",
            "run",
            "--filesystem=" + str(root),
            "--filesystem=" + str(output),
            "--command=FreeCADCmd",
            "org.freecad.FreeCAD",
        ]
    )
    _run([*command, str(wrapper)], root, output / "freecad.log", budget)
    if not (output / "native-cad.json").is_file():
        raise NativeFailure(
            "FreeCAD did not complete native validity/STEP correspondence"
        )
    return json.loads((output / "native-cad.json").read_text())


def _solve(model, cad, folder, size, root, budget, charge, phase):
    folder.mkdir(parents=True, exist_ok=False)
    length = model["parts"][0]["geometry"]["envelope_m"][0]
    command = [
        sys.executable,
        "-m",
        "engineering.design_engine.generated_parts_native",
        "mesh",
        str(cad / "part.brep"),
        str(folder),
        str(size),
        str(length),
    ]
    _run(command, root, folder / "gmsh.log", budget)
    if not (folder / "mesh.json").is_file():
        raise NativeFailure("Gmsh completed without physical mesh map")
    mesh = json.loads((folder / "mesh.json").read_text())
    elements = _read_native_elements(folder / "mesh-native.inp")
    if len(elements) != mesh["elements"]:
        raise NativeFailure("native Abaqus export and same mesh element map differ")
    write_deck(model, mesh, elements, folder / "part.inp")
    budget.timeout(60)
    if charge:
        charge(1, phase)
    ccx = shutil.which("ccx")
    if not ccx:
        raise NativeFailure("CalculiX unavailable; no analytical fallback")
    _run([ccx, "-i", "part"], folder, folder / "calculix.log", budget)
    log = (folder / "calculix.log").read_text()
    if (
        "*ERROR" in log.upper()
        or not (folder / "part.dat").is_file()
        or "Job finished" not in log
    ):
        raise NativeFailure(
            "CalculiX did not complete a valid solve; raw deck/log retained"
        )
    result = read_results(folder / "part.dat", mesh, model["loads"][0]["force_n"])
    result.update(
        mesh_size_m=size,
        elements=mesh["elements"],
        nodes=len(mesh["nodes"]),
        mesh_volume_m3=mesh["volume_m3"],
        cad_brep_sha256=mesh["cad_brep_sha256"],
    )
    _write(folder / "result.json", result)
    return result


def _control(output, root, budget, charge):
    from .generated_parts import _box, _model

    length, width, height, force = 0.2, 0.02, 0.02, 10.0
    section = dict(
        area_m2=width * height,
        iy_m4=width * height**3 / 12,
        basis="Independent unperforated analytical cantilever",
    )
    model = _model(
        "independent-cantilever-control",
        {},
        length,
        width,
        height,
        [_box((length, width, height), (length / 2, 0, 0), "add")],
        force,
        0.001,
        section,
    )
    _cad(model, output / "cad", root, budget)
    result = _solve(
        model,
        output / "cad",
        output / "mesh",
        0.008,
        root,
        budget,
        charge,
        "native-independent-cantilever-control",
    )
    young, nu = 210e9, 0.3
    eb = force * length**3 / (3 * young * section["iy_m4"])
    shear = force * length / ((5 / 6) * (young / (2 * (1 + nu))) * section["area_m2"])
    reference = eb + shear
    error = abs(result["loaded_face_deflection_m"] / reference - 1)
    report = dict(
        reference_euler_bernoulli_m=eb,
        reference_timoshenko_shear_m=shear,
        reference_total_m=reference,
        actual_solid_deflection_m=result["loaded_face_deflection_m"],
        relative_error=error,
        declared_relative_tolerance=0.05,
        passed=error <= 0.05 and result["reaction_balance_relative_error"] <= 1e-5,
        scope="Independent slender unperforated rectangular cantilever only; not bolt-hole or strength qualification",
    )
    _write(output / "benchmark.json", report)
    return report


def native_screen(
    definition, output, root, mesh_sizes_m=None, remaining_seconds=None, charge=None
):
    from .contracts import fingerprint
    from .generated_parts import validate_definition, screen_definition

    validate_definition(definition)
    original = fingerprint(definition)
    output, root = Path(output).resolve(), Path(root).resolve()
    sources = [
        Path(__file__).resolve(),
        Path(__file__).resolve().with_name("generated_parts.py"),
        Path(__file__).resolve().with_name("contracts.py"),
    ]
    source_before = {p.relative_to(root).as_posix(): _sha(p) for p in sources}
    output.mkdir(parents=True, exist_ok=False)
    budget = _Time(remaining_seconds)
    sizes = mesh_sizes_m or (
        (0.012, 0.008) if definition["family"] == "mechanical-cleat" else (0.060, 0.040)
    )
    if (
        len(sizes) < 2
        or len(sizes) > 3
        or any(not math.isfinite(v) or v <= 0 for v in sizes)
        or any(a <= b for a, b in zip(sizes, sizes[1:]))
    ):
        raise ValueError("two or three strictly finer bounded mesh sizes required")
    result = dict(
        schema="osr-generated-part-native-screen/1",
        definition_sha256=original,
        physical_definition_sha256=definition["physical_definition_sha256"],
        checks=screen_definition(definition)["checks"],
        metrics={},
        meshes=[],
        toolchain=toolchain(),
        physical_release=False,
        independently_accepted=False,
        caveats=[
            "Small displacement isotropic elasticity only",
            "Ideal full-face clamp, no bolt/contact model",
            "Clamp and hole stress demands are not accepted resistance/fatigue checks",
            "Mesh screen concerns displacement/equilibrium; stress convergence remains open",
        ],
    )
    for name in ("geometry", "mass_inertia"):
        result["checks"][name] = dict(
            state="not-run", basis="Native OCC correspondence not yet executed"
        )
    try:
        if not result["toolchain"]["available"]:
            raise NativeFailure("native tool prerequisites unavailable")
        native = _cad(definition, output / "cad", root, budget)
        result["native_cad"] = native
        expected = definition["parts"][0]["properties"]
        volume_error = abs(native["volume_m3"] / expected["volume_m3"] - 1)
        cg_error = math.sqrt(
            sum((a - b) ** 2 for a, b in zip(native["cg_m"], expected["cg_m"]))
        )
        numerator = sum(
            (a - b) ** 2
            for ra, rb in zip(
                native["inertia_tensor_kg_m2"], expected["inertia_tensor_kg_m2"]
            )
            for a, b in zip(ra, rb)
        )
        denominator = sum(
            a * a for row in expected["inertia_tensor_kg_m2"] for a in row
        )
        inertia_error = math.sqrt(numerator / denominator)
        correspondence = (
            volume_error <= 1e-8 and cg_error <= 1e-9 and inertia_error <= 1e-7
        )
        result["checks"]["geometry"] = dict(
            state="passed",
            basis="Valid connected native boolean solid and STEP round-trip from the compiled definition",
        )
        result["checks"]["mass_inertia"] = dict(
            state="passed" if correspondence else "failed",
            basis="Native OCC volume/CG/inertia compared with independent signed primitive integrals",
            volume_relative_error=volume_error,
            cg_error_m=cg_error,
            inertia_relative_error=inertia_error,
        )
        if not correspondence:
            raise NativeFailure(
                "native/analytical mass-centre-inertia correspondence failed"
            )
        for index, size in enumerate(sizes):
            result["meshes"].append(
                _solve(
                    definition,
                    output / "cad",
                    output / ("mesh-" + str(index)),
                    size,
                    root,
                    budget,
                    charge,
                    "native-part-mesh-" + str(index),
                )
            )
        coarse, fine = result["meshes"][-2:]
        relative = abs(
            fine["loaded_face_deflection_m"] - coarse["loaded_face_deflection_m"]
        ) / max(fine["loaded_face_deflection_m"], 1e-15)
        volume_errors = [
            abs(row["mesh_volume_m3"] / native["volume_m3"] - 1)
            for row in result["meshes"]
        ]
        equilibrium = max(
            max(
                row["reaction_balance_relative_error"],
                row["moment_balance_relative_error"],
            )
            for row in result["meshes"]
        )
        result["checks"]["load_equilibrium"] = dict(
            state="passed" if equilibrium <= 1e-5 else "failed",
            basis="Summed actual root nodal reactions and moments balance same end-face integrated load",
            maximum_relative_residual=equilibrium,
        )
        result["checks"]["mesh_refinement"] = dict(
            state=(
                "passed"
                if relative <= 0.05 and max(volume_errors) <= 0.002
                else "failed"
            ),
            basis="Declared5% consecutive displacement screen and0.2% actual mesh/CAD volume screen; local stress not converged",
            relative_displacement_change=relative,
            declared_relative_tolerance=0.05,
            mesh_volume_relative_errors=volume_errors,
        )
        limit = definition["displacement_limit_m"]
        result["checks"]["linear_service"] = dict(
            state="passed" if fine["loaded_face_deflection_m"] <= limit else "failed",
            basis=definition["limit_basis"],
            loaded_face_deflection_m=fine["loaded_face_deflection_m"],
            limit_m=limit,
        )
        result["benchmark"] = _control(
            output / "independent-control", root, budget, charge
        )
        result["checks"]["independent_benchmark"] = dict(
            state="passed" if result["benchmark"]["passed"] else "failed",
            basis=result["benchmark"]["scope"],
            relative_error=result["benchmark"]["relative_error"],
        )
        result["metrics"] = dict(
            defined_mass_kg=expected["mass_kg"],
            defined_volume_m3=expected["volume_m3"],
            native_measured_mass_kg=native["mass_kg"],
            native_measured_volume_m3=native["volume_m3"],
            loaded_face_deflection_m=fine["loaded_face_deflection_m"],
            maximum_displacement_m=fine["maximum_displacement_m"],
            peak_von_mises_pa=fine["peak_von_mises_pa"],
            mesh_relative_displacement_change=relative,
            reaction_balance_relative_error=equilibrium,
            attachment_count=1,
        )
    except (NativeFailure, TimeoutError, OSError) as error:
        result["failure"] = dict(kind=type(error).__name__, message=str(error))
        for name in (
            "geometry",
            "mass_inertia",
            "linear_service",
            "load_equilibrium",
            "mesh_refinement",
            "independent_benchmark",
        ):
            if result["checks"][name]["state"] == "not-run":
                result["checks"][name] = dict(
                    state="unavailable",
                    basis="Native execution incomplete: " + str(error),
                )
    if fingerprint(definition) != original:
        raise ValueError("native solver mutated the compiled physical definition")
    if {p.relative_to(root).as_posix(): _sha(p) for p in sources} != source_before:
        raise ValueError(
            "native source changed during execution; retained evidence is unaccepted"
        )
    result["source_sha256"] = source_before
    result["artifacts_sha256"] = {
        p.relative_to(output).as_posix(): _sha(p)
        for p in sorted(output.rglob("*"))
        if p.is_file()
    }
    _write(output / "native-result.json", result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["mesh"])
    parser.add_argument("brep", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("size", type=float)
    parser.add_argument("length", type=float)
    args = parser.parse_args()
    _mesh_worker(args.brep, args.output, args.size, args.length)


if __name__ == "__main__":
    main()
