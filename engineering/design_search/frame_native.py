"""Optional source-bound CalculiX B32R/BOX frame comparison packages.

BOX uses thin-wall line integration in an expanded rectangular parent element.
Its section approximation and rigid shared-node coupling remain research
hypotheses. A completed native calculation cannot qualify the physical joints,
body, clearances, fatigue, buckling or composite material law.
"""
from math import fsum, isfinite, sqrt
import os
from pathlib import Path
import platform
import resource
import shutil
import stat
import subprocess
import sys
import time
import json

from engineering.station_rail import ROOT
from engineering.station_rail import common
from engineering.station_rail.common import digest, encoded, identity
from . import frame_analysis

PRODUCER = "engineering/design_search/frame_native.py"
MANUAL = "https://www.dhondt.de/ccx_2.23.pdf"
FLAGS = dict(physical_accepted=False, engineering_accepted=False, configuration_adopted=False,
    manufacturing_release=False, operating_release=False, selected_reference_changed=False)
RESOURCES = dict(maximum_seconds=30, maximum_memory_bytes=1024*1024**2, threads=1,
    enforcement="POSIX child RLIMIT_AS/RLIMIT_CPU and subprocess wall timeout; no filesystem sandbox")
SCOPE = ["CalculiX 2.23 manual sections 6.2.33, 6.3.2 and 7.3: B32R BOX and local section directions",
    "Width is local 1 (analytical local_y); height is local 2 (analytical local_z)",
    "BOX neglects individual-wall bending and resolves warping only approximately; no solid RHS replacement",
    "Shared beam nodes impose rigid continuity; real joints and offsets remain unvalidated",
    "DAT supplies translations, forces and energy; complete rotations/reaction moments are not recovered here"]
LOADED = {PRODUCER: digest(__file__), frame_analysis.PRODUCER: digest(frame_analysis.__file__),
    "engineering/station_rail/common.py": digest(common.__file__)}


def _reference(model):
    result = frame_analysis.evaluate(model)
    if result.get("state", "").startswith("held"):
        raise ValueError("Native dispatch held by the analytical frame model domain: " + result["state"])
    return result


def _vector(values):
    length = sqrt(fsum(float(v)**2 for v in values))
    if not isfinite(length) or length <= 1e-12:
        raise ValueError("Finite nonzero frame direction required")
    return [float(v)/length for v in values]


def deck(model, subdivisions=2):
    """Generate actual hollow BOX sections, including B32R quadratic midnodes."""
    _reference(model)
    if type(subdivisions) is not int or subdivisions not in (1, 2, 4, 8, 16):
        raise ValueError("Bounded frame subdivisions 1,2,4,8,16 required")
    if len(model["nodes"]) > 128 or len(model["members"])*subdivisions > 256:
        raise ValueError("Native frame node/element resource domain exceeded")
    ordered = sorted(model["nodes"], key=lambda n: n["id"])
    number = {node["id"]: i+1 for i, node in enumerate(ordered)}
    coordinates = {number[node["id"]]: node["at_m"] for node in ordered}
    xyz = {node["id"]: node["at_m"] for node in ordered}
    elements, groups = [], []
    for i, member in enumerate(sorted(model["members"], key=lambda m: m["id"])):
        a, b = xyz[member["start_node"]], xyz[member["end_node"]]
        x = _vector([v-u for u, v in zip(a, b)])
        supplied = member["local_y"]
        projection = fsum(v*u for v, u in zip(supplied, x))
        local_y = _vector([v-projection*u for v, u in zip(supplied, x)])
        chain = [number[member["start_node"]]]
        for k in range(1, 2*subdivisions):
            nid = len(coordinates)+1
            coordinates[nid] = [u+(v-u)*k/(2*subdivisions) for u, v in zip(a, b)]
            chain.append(nid)
        chain.append(number[member["end_node"]])
        ids = []
        for k in range(subdivisions):
            ids.append(len(elements)+1)
            elements.append([chain[2*k], chain[2*k+1], chain[2*k+2]])
        groups.append((i, member, ids, local_y))
    lines = ["*HEADING", "Conditional rigid-joint RHS frame; SI N-m-Pa-kg", "*NODE"]
    lines += [str(n)+","+",".join(f"{float(v):.16g}" for v in p) for n, p in coordinates.items()]
    for i, member, ids, local_y in groups:
        lines += [f"*ELEMENT,TYPE=B32R,ELSET=M{i}"]
        lines += [str(eid)+","+",".join(map(str, elements[eid-1])) for eid in ids]
        material = model["materials"][member["material_id"]]
        nu = material.get("nu", material["E_Pa"]/(2*material.get("G_Pa", 1.0))-1)
        section = member["section"]; w, h, t = [section[key] for key in ("width_m", "height_m", "wall_m")]
        lines += [f"*MATERIAL,NAME=MAT{i}", "*ELASTIC", f"{material['E_Pa']:.16g},{nu:.16g}",
            f"*BEAM SECTION,ELSET=M{i},MATERIAL=MAT{i},SECTION=BOX",
            ",".join(f"{float(v):.16g}" for v in (w, h, t, t, t, t)),
            ",".join(f"{float(v):.16g}" for v in local_y)]
    lines += ["*ELSET,ELSET=ALL"] + [",".join(f"M{i}" for i in range(a, min(a+12, len(groups)))) for a in range(0, len(groups), 12)]
    lines += ["*NSET,NSET=OUTPUT", ",".join(str(number[n["id"]]) for n in ordered), "*BOUNDARY"]
    lines += [f"{number[s['node_id']]},{d},{d}" for s in model["supports"] for d in sorted(s["dofs"])]
    lines += ["*STEP", "*STATIC", "*CLOAD"]
    for load in model["loads"]:
        for d, value in enumerate(load["force_N"]+load.get("moment_Nm", [0., 0., 0.]), 1):
            if value:
                lines.append(f"{number[load['node_id']]},{d},{value:.16g}")
    lines += ["*NODE PRINT,NSET=OUTPUT", "U", "*NODE PRINT,NSET=OUTPUT", "RF",
        "*EL PRINT,ELSET=ALL,TOTALS=ONLY", "ELSE", "*END STEP", ""]
    definition = dict(model_id=identity(model), original_node_numbers=number, subdivisions=subdivisions,
        element_type="B32R", section_type="BOX", element_count=len(elements), scope=SCOPE, manual=MANUAL)
    definition["deck_definition_id"] = identity(definition)
    return "\n".join(lines), definition


def parse_dat(path):
    displacements, forces, active, energy = {}, {}, None, None
    waiting = False
    if Path(path).stat().st_size > 16*1024**2:
        raise ValueError("Native DAT exceeds parser resource limit")
    for line in Path(path).read_text(errors="strict").splitlines():
        low, fields = line.lower(), line.split()
        if "displacements" in low: active = displacements
        elif "total internal energy" in low: active = None; waiting = True
        elif "forces" in low: active = forces
        elif waiting and len(fields) == 1:
            try: energy = float(fields[0]); waiting = False
            except ValueError: pass
        elif active is not None and len(fields) == 4:
            try: active[int(fields[0])] = [float(v) for v in fields[1:]]
            except ValueError: pass
    if not displacements or energy is None or not isfinite(energy) or energy < 0 or any(
            not isfinite(v) for row in list(displacements.values())+list(forces.values()) for v in row):
        raise ValueError("Native frame displacement/force/energy payload missing or nonfinite")
    return displacements, forces, energy


def _comparison(model, definition, path):
    reference = _reference(model)
    u, forces, energy = parse_dat(path)
    native = {key: u[n] for key, n in definition["original_node_numbers"].items()}
    errors = [sqrt(fsum((a-b)**2 for a, b in zip(native[key], value))) for key, value in reference["displacements_m"].items()]
    scale = max([sqrt(fsum(v*v for v in row)) for row in reference["displacements_m"].values()]+[1e-12])
    analytic_energy = reference.get("strain_energy_J")
    return dict(analytical_evaluation_id=reference["evaluation_id"], displacements_m=native,
        printed_forces_N={key: forces.get(n) for key, n in definition["original_node_numbers"].items()},
        native_strain_energy_J=energy, analytical_strain_energy_J=analytic_energy,
        maximum_translation_difference_m=max(errors), translation_relative_difference=max(errors)/scale,
        energy_relative_difference=None if analytic_energy is None else abs(energy-analytic_energy)/max(abs(analytic_energy), 1e-30),
        rotations_rad=None, reaction_moments_Nm=None, agreement_is_not_physical_qualification=True)


def _sources(root, supplied=None):
    values = dict(supplied or {})
    for name, expected in LOADED.items():
        if name in values and values[name] != expected:
            raise ValueError("Conflicting native frame source context: "+name)
    values.update(LOADED)
    for module, name in ((frame_analysis, frame_analysis.PRODUCER), (common, "engineering/station_rail/common.py")):
        if digest(module.__file__) != LOADED[name]:
            raise ValueError("Executing native frame dependency changed: "+name)
    if digest(__file__) != LOADED[PRODUCER]:
        raise ValueError("Executing native frame producer changed")
    for name, expected in values.items():
        path = Path(name)
        if path.is_absolute() or ".." in path.parts or not path.parts:
            raise ValueError("Native frame source context differs: "+name)
        source = Path(root)/path
        if not stat.S_ISREG(source.lstat().st_mode) or digest(source) != expected:
            raise ValueError("Native frame source context differs: "+name)
    return values


def _resources():
    def effective(kind, configured):
        limits = [v for v in resource.getrlimit(kind) if v != resource.RLIM_INFINITY]
        return min([configured]+limits)
    return dict(RESOURCES, effective_memory_bytes=effective(resource.RLIMIT_AS, RESOURCES["maximum_memory_bytes"]),
        effective_cpu_seconds=effective(resource.RLIMIT_CPU, RESOURCES["maximum_seconds"]))


def _limits(values):
    resource.setrlimit(resource.RLIMIT_AS, (values["effective_memory_bytes"],)*2)
    resource.setrlimit(resource.RLIMIT_CPU, (values["effective_cpu_seconds"],)*2)


def _tool():
    binary = shutil.which("ccx")
    if binary is None:
        return None
    path = Path(binary).resolve()
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError("Regular CalculiX executable required")
    return dict(path=str(path), sha256=digest(path))


def _runtime():
    return dict(python_implementation=platform.python_implementation(), python_version=platform.python_version(),
        python_executable_sha256=digest(Path(sys.executable).resolve()), numpy_version=frame_analysis.np.__version__,
        omp_num_threads=os.environ.get("OMP_NUM_THREADS"), openblas_num_threads=os.environ.get("OPENBLAS_NUM_THREADS"),
        mkl_num_threads=os.environ.get("MKL_NUM_THREADS"))


def run(model, output, *, execute=False, subdivisions=2, source_sha256=None, root=ROOT):
    """Prepare a fresh package and optionally execute exactly one bounded job."""
    if type(execute) is not bool:
        raise ValueError("Explicit Boolean native execution decision required")
    root, out = Path(root), Path(output)
    out.mkdir(parents=True, exist_ok=False)
    (out/"model.json").write_bytes(encoded(model))
    sources = _sources(root, source_sha256)
    result = dict(schema="osr-native-frame-result/1", model_id=identity(model), execution="not-run",
        numerical_validity="unknown", native_state="prepared-not-dispatched", native_jobs_used=0,
        comparison=None, elapsed_s=0., **FLAGS)
    try:
        text, definition = deck(model, subdivisions)
    except ValueError as exc:
        text, definition = "", None
        result.update(execution="held", native_state="held-model-domain", hold_reason=str(exc))
    (out/"frame.inp").write_text(text)
    tool = _tool(); resources = _resources()
    request = dict(schema="osr-native-frame-request/1", model_id=identity(model), definition=definition,
        execute=execute, tool=tool, source_sha256=sources, resources=resources, subdivisions=subdivisions,
        runtime=_runtime(), scope=SCOPE, manual=MANUAL)
    request["request_id"] = identity(request)
    (out/"input.json").write_bytes(encoded(request))
    (out/"solver.log").write_text("")
    if execute and definition is not None:
        if tool is None:
            result.update(execution="held", native_state="held-native-tool-unavailable")
        else:
            environment = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
                CCX_NPROC_RESULTS="1", CCX_NPROC_EQUATION_SOLVER="1", NUMBER_OF_CPUS="1")
            result["native_jobs_used"] = 1; start = time.monotonic()
            try:
                with (out/"solver.log").open("wb") as log:
                    value = subprocess.run([tool["path"], "-i", "frame"], cwd=out,
                        env=environment, stdout=log, stderr=subprocess.STDOUT,
                        timeout=resources["maximum_seconds"], preexec_fn=lambda: _limits(resources), check=False)
                result["returncode"] = value.returncode
                if value.returncode != 0:
                    raise ValueError("CalculiX returned an unsuccessful status")
                result.update(execution="completed", native_state="completed-native-frame-comparison",
                    numerical_validity="unqualified-native-frame-comparison",
                    comparison=_comparison(model, definition, out/"frame.dat"))
            except (ValueError, OSError, subprocess.SubprocessError) as exc:
                result.update(execution="failed", native_state="failed-or-interrupted-native-frame", failure=str(exc))
            result["elapsed_s"] = time.monotonic()-start
    result["native_request_id"] = request["request_id"]
    _sources(root, sources)
    result["evaluation_id"] = identity(result)
    (out/"result.json").write_bytes(encoded(result))
    manifest = dict(schema="osr-native-frame-package/1", request_id=request["request_id"],
        evaluation_id=result["evaluation_id"], source_sha256=sources,
        files_sha256={p.name: digest(p) for p in sorted(out.iterdir()) if p.is_file()}, **FLAGS)
    manifest["manifest_id"] = identity(manifest)
    (out/"manifest.json").write_bytes(encoded(manifest))
    return verify(out, root=root)


def verify(output, *, root=ROOT):
    """Check exact deck and reanalyse saved DAT; never execute a solver."""
    out = Path(output)
    if out.is_symlink() or not out.is_dir() or any(not stat.S_ISREG(p.lstat().st_mode) for p in out.iterdir()):
        raise ValueError("Regular native frame package files required")
    manifest = json.loads((out/"manifest.json").read_bytes())
    if manifest.get("schema") != "osr-native-frame-package/1":
        raise ValueError("Native frame manifest schema differs")
    if manifest["manifest_id"] != identity({k:v for k,v in manifest.items() if k != "manifest_id"}):
        raise ValueError("Native frame manifest identity differs")
    if manifest["files_sha256"] != {p.name:digest(p) for p in out.iterdir() if p.name != "manifest.json"}:
        raise ValueError("Native frame package payload differs")
    if not {"input.json", "model.json", "frame.inp", "solver.log", "result.json"} <= set(manifest["files_sha256"]):
        raise ValueError("Native frame required input, result or log payload is missing")
    request = json.loads((out/"input.json").read_bytes()); model = json.loads((out/"model.json").read_bytes())
    result = json.loads((out/"result.json").read_bytes())
    if (request.get("schema") != "osr-native-frame-request/1" or result.get("schema") != "osr-native-frame-result/1"
            or type(request.get("execute")) is not bool or request.get("resources") != _resources()
            or request.get("runtime") != _runtime() or request.get("tool") != _tool()
            or request.get("scope") != SCOPE or request.get("manual") != MANUAL):
        raise ValueError("Native frame tool, runtime or bounded resource request differs")
    if request["request_id"] != identity({k:v for k,v in request.items() if k != "request_id"}) or request["model_id"] != identity(model):
        raise ValueError("Native frame request/model identity differs")
    if request["source_sha256"] != _sources(root, request["source_sha256"]) or manifest["source_sha256"] != request["source_sha256"]:
        raise ValueError("Native frame package sources differ")
    try:
        text, definition = deck(model, request["subdivisions"])
        domain_hold = None
    except ValueError as exc:
        text, definition, domain_hold = "", None, str(exc)
    if text != (out/"frame.inp").read_text() or definition != request["definition"]:
        raise ValueError("Native frame deck differs from the exact model")
    if type(result.get("native_jobs_used")) is not int or type(result.get("elapsed_s")) not in (float, int) or not isfinite(result["elapsed_s"]) or result["elapsed_s"] < 0:
        raise ValueError("Native frame execution counters or runtime differ")
    if definition is None:
        expected = ("held", "held-model-domain", 0, "unknown")
        if result.get("hold_reason") != domain_hold: raise ValueError("Native frame model hold differs")
    elif not request["execute"]:
        expected = ("not-run", "prepared-not-dispatched", 0, "unknown")
    elif request["tool"] is None:
        expected = ("held", "held-native-tool-unavailable", 0, "unknown")
    elif result.get("execution") == "completed":
        expected = ("completed", "completed-native-frame-comparison", 1, "unqualified-native-frame-comparison")
        if result.get("returncode") != 0 or result.get("comparison") is None:
            raise ValueError("Completed native frame requires successful status and DAT comparison")
        if result["comparison"] != _comparison(model, definition, out/"frame.dat"):
            raise ValueError("Native frame comparison differs from saved solver payload")
    else:
        expected = ("failed", "failed-or-interrupted-native-frame", 1, "unknown")
        if not isinstance(result.get("failure"), str) or not result["failure"]:
            raise ValueError("Failed native frame must preserve a failure reason")
    actual = tuple(result.get(key) for key in ("execution", "native_state", "native_jobs_used", "numerical_validity"))
    if actual != expected or (expected[0] != "completed" and result.get("comparison") is not None) or (expected[2] == 0 and result["elapsed_s"] != 0):
        raise ValueError("Native frame execution state, job count or request binding differs")
    if result["evaluation_id"] != identity({k:v for k,v in result.items() if k != "evaluation_id"}) or manifest["evaluation_id"] != result["evaluation_id"]:
        raise ValueError("Native frame evaluation identity differs")
    if result["model_id"] != request["model_id"] or result["native_request_id"] != request["request_id"] or any(
            record.get(key) is not False for record in (manifest, result) for key in FLAGS):
        raise ValueError("Native frame identity or non-promoting disposition differs")
    if manifest["request_id"] != request["request_id"]:
        raise ValueError("Native frame manifest request identity differs")
    _sources(root, request["source_sha256"])
    return dict(verified=True, manifest_id=manifest["manifest_id"], **result)
