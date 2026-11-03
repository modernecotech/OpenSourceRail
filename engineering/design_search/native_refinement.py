"""Source-bound axial-graph refinement for an existing physical candidate.

The truss is an axial/pin model, not a complete frame or bonded shell. A graph
mechanism holds this method only. Coarse solid-shell analysis and all physical
qualification are independent work.
"""
from __future__ import annotations

import json
import hashlib
import os
import platform
import resource
import stat
import sys
from copy import deepcopy
from pathlib import Path

import numpy as np

from engineering import station_rail
from engineering.station_rail import ROOT, common
from engineering.station_rail.common import digest, encoded, identity
from . import design_grammar, grammar_shell, grammar_structure

PRODUCER = "engineering/design_search/native_refinement.py"
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             configuration_adopted=False, manufacturing_release=False,
             operating_release=False, physical_journey_completed=False,
             installed_mass_complete=False)
MAX_FILE_BYTES = 32 * 1024 * 1024
MODULES = ((station_rail, "engineering/station_rail/__init__.py"),
           (common, "engineering/station_rail/common.py"),
           (design_grammar, design_grammar.PRODUCER),
           (grammar_structure, grammar_structure.PRODUCER),
           (grammar_shell, grammar_shell.PRODUCER))
LOADED = {name: digest(module.__file__) for module, name in MODULES}
LOADED[PRODUCER] = digest(__file__)
LIMITATIONS = [
    "Pin-jointed axial members do not represent bending, shell action or joint stiffness",
    "Compression buckling, short-member behaviour, connections and fastener masses remain unqualified",
    "Skin/core constitutive data, complete installed mass, CG and equipment locations remain incomplete",
    "Fatigue, fire, crash, clearance, propulsion, braking and independent physical testing remain open",
]


def _root(root):
    root = Path(root).resolve()
    if root != ROOT.resolve():
        raise ValueError("Use the source checkout from which the refinement modules were imported")
    for module, name in MODULES:
        if digest(module.__file__) != LOADED[name] or digest(root / name) != LOADED[name]:
            raise ValueError("Executing refinement source changed: " + name)
    if digest(__file__) != LOADED[PRODUCER] or digest(root / PRODUCER) != LOADED[PRODUCER]:
        raise ValueError("Executing refinement source changed: " + PRODUCER)
    return root


def _runtime():
    return dict(python_implementation=platform.python_implementation(),
                python_version=platform.python_version(), numpy_version=np.__version__,
                python_executable_sha256=digest(Path(sys.executable).resolve()),
                omp_num_threads=os.environ.get("OMP_NUM_THREADS"),
                openblas_num_threads=os.environ.get("OPENBLAS_NUM_THREADS"),
                mkl_num_threads=os.environ.get("MKL_NUM_THREADS"))


def _sources(candidate, root):
    if not isinstance(candidate.get("sources"), dict) or not candidate["sources"]:
        raise ValueError("Explicit source-bound physical candidate required")
    values = dict(candidate["sources"])
    graph_sources = candidate.get("structure", {}).get("source_sha256", {})
    if not isinstance(graph_sources, dict):
        raise ValueError("Explicit source-bound axial graph required")
    if candidate.get("structure", {}).get("schema") == "osr-axial-structure-graph/1" and not graph_sources:
        raise ValueError("Explicit source-bound axial graph required")
    for name, sha in graph_sources.items():
        if name in values and values[name] != sha:
            raise ValueError("Graph and candidate source identity differs: " + name)
        values[name] = sha
    for name, sha in LOADED.items():
        if name in values and values[name] != sha:
            raise ValueError("Candidate and executing source identity differs: " + name)
        values[name] = sha
    if not values or any(not isinstance(name, str) or not isinstance(sha, str)
                         or digest(root / name) != sha for name, sha in values.items()):
        raise ValueError("Candidate/refinement source bytes differ")
    return dict(sorted(values.items()))


def _candidate(candidate, root):
    if not isinstance(candidate, dict) or candidate.get("schema") != "osr-generative-body-candidate/1":
        raise ValueError("Explicit generated physical body candidate required")
    design_grammar.validate(candidate)
    if (any(candidate.get(key) is not False for key in
            ("physical_accepted", "engineering_accepted",
             "manufacturing_release", "operating_release"))
            or candidate.get("configuration_adopted", False) is not False
            or candidate.get("complete_installed_mass_kg") is not None):
        raise ValueError("Refinement input cannot grant engineering or physical release")
    if not isinstance(candidate.get("requirement_revision"), str) or not candidate["requirement_revision"]:
        raise ValueError("Explicit candidate requirement revision required")
    graph = candidate.get("structure", {})
    if graph.get("schema") == "osr-axial-structure-graph/1" and not isinstance(graph.get("load_basis"), dict):
        raise ValueError("Explicit axial load basis required")
    return _sources(candidate, root)


def assess(candidate, *, root=ROOT):
    """Return a reproducible pin-graph diagnosis and separate shell admission.

    A rigidity failure is scoped to the declared axial graph, never the whole
    body; a graph outside the method domain remains unknown and undispatched.
    """
    root = _root(root)
    sources = _candidate(candidate, root)
    graph = candidate["structure"]
    diagnostic = None
    reference = None
    linear_ratio = None
    reason = None
    try:
        if graph.get("schema") != "osr-axial-structure-graph/1":
            raise ValueError("This physical topology has no declared axial-graph adapter")
        diagnostic = grammar_structure.diagnose_rigidity(graph)
        if diagnostic["mechanism_count"]:
            axial_status = "graph-mechanism-model-only"
        else:
            try:
                reference = grammar_structure.linear_reference(graph)
                _, _, _, stock, _, _ = grammar_structure._validated(graph)
                displacements = reference["displacements_m"]
                linear_ratio = max(float(np.linalg.norm(
                    np.asarray(displacements[member["end_node"]]) -
                    np.asarray(displacements[member["start_node"]]))) / member["length_m"]
                    for member in stock)
                if not np.isfinite(linear_ratio):
                    raise ValueError("Non-finite analytical member displacement ratio")
                if linear_ratio >= 0.01:
                    axial_status = "outside-linear-domain-analytical"
                    reason = "Analytical member-relative displacement/length reaches the axial method limit of 0.01"
                else:
                    axial_status = "rigid-axial-graph-analytical-only"
            except np.linalg.LinAlgError as exc:
                axial_status = "axial-numerical-failure"
                reason = str(exc)
    except (ValueError, KeyError, TypeError, np.linalg.LinAlgError) as exc:
        axial_status = "axial-model-domain-unavailable"
        reason = str(exc)
    try:
        shell = grammar_shell.plan(candidate)
        shell_admission = dict(status="admitted-for-separate-method-check" if shell["admitted"]
                               else "held-by-shell-model-domain", plan=shell)
    except (ValueError, KeyError, TypeError, np.linalg.LinAlgError) as exc:
        shell_admission = dict(status="shell-model-domain-unavailable", reason=str(exc), plan=None)
    tasks = [dict(kind="shell-model-and-joint-evidence", state="open",
                  detail="Establish finite-face connections, material laws, loads and separate solid/shell validation"),
             dict(kind="installed-mass-and-physical-qualification", state="open",
                  detail="Locate equipment and obtain independent structural, braking and operational evidence")]
    if axial_status != "rigid-axial-graph-analytical-only":
        tasks.append(dict(kind="axial-graph-model-refinement", state="open",
                          detail="Resolve or explicitly model axial mechanisms/domain; do not reject a bonded or rigid shell"))
    if axial_status == "outside-linear-domain-analytical":
        tasks.append(dict(kind="nonlinear-or-revised-load-path-evaluator", state="open",
                          detail="Develop a suitable nonlinear or revised structural model; the axial small-displacement result is outside its method domain"))
    result = dict(schema="osr-native-axial-refinement-assessment/1",
                  candidate_id=candidate["candidate_id"], definition_id=candidate["definition_id"],
                  requirement_revision=candidate["requirement_revision"],
                  input_graph_id=identity(graph),
                  physical_graph_id=diagnostic["physical_graph_id"] if diagnostic is not None else None,
                  load_basis=deepcopy(graph.get("load_basis")), axial_status=axial_status,
                  axial_reason=reason, axial_diagnostic=diagnostic, axial_reference=reference,
                  analytical_maximum_member_relative_displacement_to_length=linear_ratio,
                  analytical_linear_domain_limit=0.01,
                  shell_admission=shell_admission, source_sha256=sources, runtime=_runtime(),
                  next_tasks=tasks, limitations=LIMITATIONS, whole_body_rejected=False,
                  available_force_map_id=None, integrated_selection=None,
                  scope=grammar_structure.SCOPE, **FLAGS)
    _root(root)
    if _sources(candidate, root) != sources:
        raise ValueError("Candidate sources changed during assessment")
    result["assessment_id"] = identity(result)
    return result


def _resources(native_jobs, memory_mb, timeout_s, subdivisions):
    if type(native_jobs) is not int or native_jobs not in (0, 1):
        raise ValueError("Explicit zero-or-one axial native job budget required")
    if type(memory_mb) is not int or memory_mb not in (1024, 2048):
        raise ValueError("Axial memory request must be 1024 or 2048 MiB")
    if type(timeout_s) is not int or timeout_s not in (30, 45):
        raise ValueError("Axial timeout must be 30 or 45 seconds")
    if type(subdivisions) is not int or subdivisions not in (1, 2, 4):
        raise ValueError("Axial subdivisions must be 1, 2 or 4")
    finite = [v for v in resource.getrlimit(resource.RLIMIT_AS) if v != resource.RLIM_INFINITY]
    cap = min([memory_mb * 1024**2, *finite])
    return dict(native_jobs=native_jobs, memory_mb=memory_mb, timeout_s=timeout_s,
                subdivisions=subdivisions, effective_RLIMIT_AS_bytes=cap, OMP_threads=1)


def _tool():
    path = Path("/usr/bin/ccx")
    if not path.is_file():
        return dict(path=str(path), sha256=None, available=False)
    return dict(path=str(path), sha256=digest(path), available=True)


def _request(assessment, resources, tool):
    value = dict(schema="osr-native-axial-refinement-request/1",
                 candidate_id=assessment["candidate_id"], definition_id=assessment["definition_id"],
                 requirement_revision=assessment["requirement_revision"],
                 input_graph_id=assessment["input_graph_id"], physical_graph_id=assessment["physical_graph_id"],
                 assessment_id=assessment["assessment_id"], load_basis=assessment["load_basis"],
                 source_sha256=assessment["source_sha256"], runtime=assessment["runtime"],
                 resources=resources, tool=tool)
    value["request_id"] = identity(value)
    return value


def request(candidate, *, root=ROOT, native_jobs=0, memory_mb=1024,
            timeout_s=30, subdivisions=1):
    """Build the exact source/tool/resource identity without writing or solving."""
    root = _root(root)
    resources = _resources(native_jobs, memory_mb, timeout_s, subdivisions)
    assessment = assess(candidate, root=root)
    tool = _tool()
    return _request(assessment, resources, tool)


def _inventory(root):
    records = {}
    for directory, subdirs, files in os.walk(root, followlinks=False):
        base = Path(directory)
        for name in subdirs:
            path = base / name
            if not stat.S_ISDIR(path.lstat().st_mode):
                raise ValueError("Non-directory/symlink in refinement package")
        for name in files:
            path = base / name
            rel = path.relative_to(root).as_posix()
            if rel == "manifest.json":
                continue
            raw = _read(path)
            records[rel] = dict(sha256=hashlib.sha256(raw).hexdigest(), size=len(raw))
    return dict(sorted(records.items()))


def _directories(root):
    return sorted((Path(directory) / name).relative_to(root).as_posix()
                  for directory, names, _ in os.walk(root, followlinks=False) for name in names)


def _read(path):
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except OSError as exc:
        raise ValueError("Regular refinement file required") from exc
    with os.fdopen(fd, "rb") as handle:
        info = os.fstat(handle.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_FILE_BYTES:
            raise ValueError("Bounded regular refinement file required")
        raw = handle.read(MAX_FILE_BYTES + 1)
        if len(raw) > MAX_FILE_BYTES:
            raise ValueError("Refinement file exceeds size budget")
        after = os.fstat(handle.fileno())
        try:
            current = os.stat(path, follow_symlinks=False)
        except OSError as exc:
            raise ValueError("Refinement file changed while reading") from exc
        fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
        if any(getattr(info, key) != getattr(after, key) or getattr(after, key) != getattr(current, key)
               for key in fields):
            raise ValueError("Refinement file changed while reading")
        return raw


def _write(path, value):
    with path.open("xb") as handle:
        handle.write(encoded(value))


def _result(candidate, assessment, request, native, native_state):
    value = dict(schema="osr-native-axial-refinement/1", request=request,
                 assessment_id=assessment["assessment_id"], candidate_id=candidate["candidate_id"],
                 definition_id=candidate["definition_id"], axial_status=assessment["axial_status"],
                 native_state=native_state, native_evaluation_id=native.get("evaluation_id") if native else None,
                 native_jobs_used=native.get("native_jobs_used", 0) if native else 0,
                 whole_body_rejected=False, integrated_selection=None,
                 available_force_map_id=None, limitations=LIMITATIONS, **FLAGS)
    value["evaluation_id"] = identity(value)
    return value


def evaluate(candidate, *, root=ROOT, output, native_jobs=0, memory_mb=1024,
             timeout_s=30, subdivisions=1):
    """Create a fresh immutable axial evidence package with an explicit budget."""
    root = _root(root)
    resources = _resources(native_jobs, memory_mb, timeout_s, subdivisions)
    assessment = assess(candidate, root=root)
    tool = _tool()
    if native_jobs and assessment["axial_status"] == "rigid-axial-graph-analytical-only" and not tool["available"]:
        raise ValueError("CalculiX is unavailable for the requested native job")
    request = _request(assessment, resources, tool)
    folder = Path(output)
    folder.mkdir(parents=True, exist_ok=False)
    _write(folder / "request.json", request)
    _write(folder / "assessment.json", assessment)
    native = None
    if not native_jobs:
        native_state = "not-requested"
    elif assessment["axial_status"] != "rigid-axial-graph-analytical-only":
        native_state = "held-by-axial-model-diagnostic"
    else:
        native = grammar_structure.run(candidate["structure"], folder / "native", subdivisions=subdivisions,
                                       root=root, memory_mb=memory_mb, timeout_s=timeout_s)
        native_state = native["execution"]
        if (native.get("candidate_id") != candidate["candidate_id"]
                or native.get("input_graph_id") != assessment["input_graph_id"]
                or native.get("physical_graph_id") != assessment["physical_graph_id"]
                or native.get("native_jobs_used") not in (0, 1)
                or any(native.get(k) is not False for k in
                       ("physical_accepted", "engineering_accepted", "manufacturing_release", "operating_release"))
                or native.get("configuration_adopted", False) is not False):
            raise ValueError("Native result differs from the bound axial candidate or release hold")
    _root(root)
    if _sources(candidate, root) != assessment["source_sha256"] or _tool() != tool:
        raise ValueError("Refinement source or native tool changed during execution")
    result = _result(candidate, assessment, request, native, native_state)
    _write(folder / "result.json", result)
    manifest = dict(schema="osr-native-axial-refinement-manifest/1", request_id=request["request_id"],
                    assessment_id=assessment["assessment_id"], evaluation_id=result["evaluation_id"],
                    files=_inventory(folder), directories=_directories(folder), **FLAGS)
    manifest["manifest_id"] = identity(manifest)
    _write(folder / "manifest.json", manifest)
    return result


def verify(output, candidate, *, root=ROOT, native_jobs=0, memory_mb=1024,
           timeout_s=30, subdivisions=1):
    """Check current candidate, source/tool, analytical and retained native bytes; never solve."""
    root = _root(root)
    folder = Path(output)
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError("Regular refinement package directory required")
    resources = _resources(native_jobs, memory_mb, timeout_s, subdivisions)
    assessment = assess(candidate, root=root)
    request = _request(assessment, resources, _tool())
    manifest = json.loads(_read(folder / "manifest.json"))
    should_have_native = bool(native_jobs and assessment["axial_status"] == "rigid-axial-graph-analytical-only")
    required = {"request.json", "assessment.json", "result.json"}
    actual = set(manifest.get("files", {}))
    if (set(manifest) != {"schema", "request_id", "assessment_id", "evaluation_id", "files", "directories", "manifest_id", *FLAGS}
            or manifest.get("schema") != "osr-native-axial-refinement-manifest/1"
            or manifest.get("manifest_id") != identity({k:v for k,v in manifest.items() if k != "manifest_id"})
            or manifest.get("files") != _inventory(folder)
            or manifest.get("directories") != _directories(folder)
            or manifest.get("directories") != (["native"] if should_have_native else [])
            or not required <= actual
            or (actual - required != set() if not should_have_native
                else any(not name.startswith("native/") for name in actual - required))
            or any(manifest.get(k) is not False for k in FLAGS)):
        raise ValueError("Refinement manifest or payload differs")
    if _read(folder / "request.json") != encoded(request) or _read(folder / "assessment.json") != encoded(assessment):
        raise ValueError("Refinement candidate, source, resource or analytical assessment differs")
    result = json.loads(_read(folder / "result.json"))
    if (result.get("evaluation_id") != identity({k:v for k,v in result.items() if k != "evaluation_id"})
            or result.get("request") != request or result.get("assessment_id") != assessment["assessment_id"]
            or result.get("candidate_id") != candidate["candidate_id"]
            or result.get("definition_id") != candidate["definition_id"]
            or result.get("whole_body_rejected") is not False or result.get("integrated_selection") is not None
            or result.get("available_force_map_id") is not None or any(result.get(k) is not False for k in FLAGS)
            or manifest.get("request_id") != request["request_id"]
            or manifest.get("assessment_id") != assessment["assessment_id"]
            or manifest.get("evaluation_id") != result["evaluation_id"]):
        raise ValueError("Refinement evaluation identity or disposition differs")
    if should_have_native:
        native_dir = folder / "native"
        native = json.loads(_read(native_dir / "result.json"))
        receipt = json.loads(_read(native_dir / "manifest.json"))
        if (receipt.get("manifest_id") != identity({k:v for k,v in receipt.items() if k != "manifest_id"})
                or receipt.get("files_sha256") != {k:v["sha256"] for k,v in _inventory(native_dir).items()}
                or native.get("evaluation_id") != identity({k:v for k,v in native.items() if k != "evaluation_id"})
                or receipt.get("evaluation_id") != native["evaluation_id"]
                or json.loads(_read(native_dir / "graph.json")) != candidate["structure"]
                or native.get("input_graph_id") != assessment["input_graph_id"]
                or native.get("physical_graph_id") != assessment["physical_graph_id"]
                or native.get("candidate_id") != candidate["candidate_id"]
                or native.get("subdivisions") != subdivisions
                or native.get("native_jobs_used") != 1
                or native.get("tool", {}).get("ccx_path") != request["tool"]["path"]
                or native.get("tool", {}).get("ccx_sha256") != request["tool"]["sha256"]
                or native.get("tool", {}).get("requested_memory_mb") != memory_mb
                or native.get("tool", {}).get("RLIMIT_AS_bytes") != resources["effective_RLIMIT_AS_bytes"]
                or native.get("tool", {}).get("timeout_s") != timeout_s
                or native.get("tool", {}).get("OMP_threads") != 1
                or native.get("source_sha256") != {**candidate["structure"].get("source_sha256", {}), grammar_structure.PRODUCER: LOADED[grammar_structure.PRODUCER]}
                or receipt.get("source_sha256") != native.get("source_sha256")
                or receipt.get("tool") != native.get("tool")
                or any(receipt.get(k) is not False for k in
                       ("physical_accepted", "engineering_accepted", "manufacturing_release", "operating_release"))
                or any(native.get(k) is not False for k in
                       ("physical_accepted", "engineering_accepted", "manufacturing_release", "operating_release"))
                or native.get("configuration_adopted", False) is not False
                or result.get("native_evaluation_id") != native["evaluation_id"]
                or result.get("native_jobs_used") != 1 or result.get("native_state") != native.get("execution")):
            raise ValueError("Retained native axial receipt differs")
        deck, expected_definition = grammar_structure.deck(candidate["structure"], subdivisions)
        if (_read(native_dir / "graph.inp") != deck.encode()
                or _read(native_dir / "definition.json") != encoded(expected_definition)
                or _read(native_dir / "rigidity.json") != encoded(assessment["axial_diagnostic"])):
            raise ValueError("Retained native input deck or axial diagnostic differs")
        if native.get("execution") == "completed":
            definition = json.loads(_read(native_dir / "definition.json"))
            replay = grammar_structure.analyse(candidate["structure"], definition, native_dir / "graph.dat")
            if any(native.get(k) != v for k, v in replay.items()):
                raise ValueError("Retained axial result differs from analytical/native data")
        elif (native.get("execution") not in ("tool_error", "interrupted")
              or native.get("numerical_validity") != "unknown"
              or native.get("engineering_screen") != "unknown"):
            raise ValueError("Failed native axial run cannot acquire a passing result")
    else:
        expected_state = "not-requested" if not native_jobs else "held-by-axial-model-diagnostic"
        if (result.get("native_state") != expected_state or result.get("native_jobs_used") != 0
                or result.get("native_evaluation_id") is not None or (folder / "native").exists()):
            raise ValueError("Unexpected native dispatch or unsupported axial model")
        native = None
    if result != _result(candidate, assessment, request, native, result["native_state"]):
        raise ValueError("Refinement result differs from the exact bound assessment")
    return dict(verified=True, evaluation_id=result["evaluation_id"], native_jobs_used=result["native_jobs_used"], **FLAGS)
