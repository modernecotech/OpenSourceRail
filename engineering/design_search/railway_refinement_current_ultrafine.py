"""One bounded 0.053125 m continuation of the exact current railway frame."""
from __future__ import annotations

import gzip
import gc
import json
import math
import os
import resource
import shutil
import subprocess
import time
from pathlib import Path

import numpy as np

from engineering.station_rail import ROOT, FLAGS
from engineering.station_rail.common import digest, encoded, identity
from . import (grammar_shell, railway_campaign, railway_fine_refinement,
               railway_native, railway_publication, railway_refinement,
               railway_refinement_current as current,
               railway_refinement_current_fine as preceding)

PRODUCER = "engineering/design_search/railway_refinement_current_ultrafine.py"
CANDIDATE_ID = current.CANDIDATE_ID
MESH_M = 0.053125
PREVIOUS_MESH_M = 0.10625
CELL_BUDGET = 320_000
EXPECTED_CELLS = 290_660
EXPECTED_NODES = 513_844
MEMORY_MB = 10_240
TIMEOUT_S = 600
ELEMENT_KIND = "C3D8I"
SOLVER_PATH = "/usr/bin/ccx"
OMP_THREADS = 1


def _check_sources(root: Path, source_sha256: dict[str, str]) -> None:
    root = Path(root).resolve()
    for name, expected in source_sha256.items():
        path = (root / name).resolve()
        if root not in path.parents or not path.is_file() or digest(path) != expected:
            raise ValueError(f"Source identity mismatch: {name}")


def _attempt_folders(root: Path, parent_result: Path, candidate_id: str) -> list[Path]:
    parent_sha = digest(parent_result)
    base = Path(root) / "build/coupled-railway/refinements" / candidate_id
    found = []
    for request_path in base.glob("*/request.json"):
        try:
            request = json.loads(request_path.read_bytes())
        except (OSError, ValueError, TypeError):
            continue
        if (request.get("schema") == "osr-current-source-ultrafine-refinement-request/1"
                and request.get("body_candidate_id") == candidate_id
                and request.get("mesh_m") == MESH_M
                and request.get("parent_result_sha256") == parent_sha
                and request_path.parent.name == identity(request)):
            found.append(request_path.parent)
    return sorted(found)


def _context(root=ROOT, *, parent_result: Path, candidate_id: str):
    root = Path(root).resolve()
    parent_result = Path(parent_result).resolve()
    if candidate_id != CANDIDATE_ID or not parent_result.is_file():
        raise ValueError("Exact current parent result and declared candidate are required")

    base, request_02125, base_folder, base_result, base_manifest = preceding._context(
        root, parent_result=parent_result, candidate_id=candidate_id)
    fine_request = preceding._request(root, base, request_02125, base_result, base_manifest)
    fine_folder = preceding._package(root, fine_request)
    fine_result, fine_report, fine_manifest = _verify_predecessor(
        root, fine_folder, fine_request, base[3], base[4])
    if (fine_result.get("execution") != "completed"
            or fine_result.get("numerical_validity") != "equilibrium_energy_confirmed_only"
            or fine_report.get("generated_mesh", {}).get("mesh_m") != PREVIOUS_MESH_M):
        raise ValueError("Exact 0.10625 m current-source package must verify and complete")

    # The preceding context already verified the exact 0.2125 m package. Read
    # its report and combine it with the independently checked 0.10625 m package
    # to reconstruct the frontier without invoking either verifier a second time.
    current_report = json.loads((base_folder / "report.json").read_bytes())
    current_refinement = dict(request=request_02125, result=base_result,
                              report=current_report)
    fine_refinement = dict(request=fine_request, result=fine_result,
                           report=fine_report)
    frontier = next((row for row in railway_publication._published_frontier(
        base[2], current_refinement, fine_refinement)
        if row.get("kind") == "unresolved-numerical-refinement"
        and row.get("body_candidate_id") == candidate_id
        and row.get("proposed_next_mesh_m") == MESH_M), None)
    if frontier is None:
        raise ValueError("Verified current-source frontier does not request 0.053125 m")

    bundle = base[4]
    if (bundle.get("body_candidate_id") != candidate_id
            or bundle.get("family_id") != "P1"):
        raise ValueError("The exact P1 railway bundle is required")

    sources = {
        PRODUCER: digest(root / PRODUCER),
        railway_publication.PRODUCER: digest(root / railway_publication.PRODUCER),
        preceding.PRODUCER: digest(root / preceding.PRODUCER),
        current.PRODUCER: digest(root / current.PRODUCER),
        railway_fine_refinement.PRODUCER: digest(root / railway_fine_refinement.PRODUCER),
        railway_refinement.PRODUCER: digest(root / railway_refinement.PRODUCER),
        railway_campaign.PRODUCER: digest(root / railway_campaign.PRODUCER),
        railway_native.PRODUCER: digest(root / railway_native.PRODUCER),
        grammar_shell.PRODUCER: digest(root / grammar_shell.PRODUCER),
        "engineering/station_rail/__init__.py": digest(root / "engineering/station_rail/__init__.py"),
        "engineering/station_rail/common.py": digest(root / "engineering/station_rail/common.py"),
    }
    sources.update(base[3].get("sources", {}))
    _check_sources(root, sources)
    if not Path(SOLVER_PATH).is_file():
        raise ValueError("Declared CalculiX executable is unavailable")
    return dict(root=root, parent_result=parent_result, parent=base[2], body=base[3],
                bundle=bundle, frontier=frontier, base=base,
                request_02125=request_02125, base_folder=base_folder,
                base_result=base_result, base_manifest=base_manifest,
                current_report=current_report,
                fine_request=fine_request,
                fine_folder=fine_folder, fine_result=fine_result,
                fine_report=fine_report, fine_manifest=fine_manifest,
                source_sha256=sources)


def _verify_predecessor(root: Path, folder: Path, request: dict,
                        body: dict, bundle: dict) -> tuple[dict, dict, dict]:
    """Verify the exact 0.10625 m package without rerunning its parent context."""
    if not folder.is_dir():
        raise ValueError("Current-source 0.10625 m predecessor package is missing")
    manifest_path = folder / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    actual = {p.relative_to(folder).as_posix(): digest(p) for p in folder.rglob("*")
              if p.is_file() and p.name != "manifest.json"}
    if (manifest.get("manifest_id") != identity(
            {k: v for k, v in manifest.items() if k != "manifest_id"})
            or manifest.get("request_id") != identity(request)
            or manifest.get("source_sha256") != request.get("source_sha256")
            or manifest.get("parent_result_sha256") != request.get("parent_result_sha256")
            or manifest.get("files_sha256") != actual
            or json.loads((folder / "request.json").read_bytes()) != request):
        raise ValueError("0.10625 m predecessor manifest, request, or payload differs")
    _check_sources(root, request["source_sha256"])
    result = json.loads((folder / "native/result.json").read_bytes())
    report = json.loads((folder / "report.json").read_bytes())
    definition = json.loads((folder / "native/definition.json").read_bytes())
    if (result.get("evaluation_id") != identity(
            {k: v for k, v in result.items() if k != "evaluation_id"})
            or result.get("evaluation_id") != manifest.get("evaluation_id")
            or result.get("candidate_id") != request.get("body_candidate_id")
            or result.get("definition_id") != request.get("body_definition_id")
            or result.get("source_sha256") != request.get("source_sha256")
            or result.get("mesh_summary", {}).get("mesh_m") != PREVIOUS_MESH_M
            or result.get("mesh_summary", {}).get("solid_elements") != 128_382
            or result.get("mesh_summary", {}).get("node_count") != 227_190
            or result.get("tool", {}).get("ccx_path") != request.get("solver", {}).get("path")
            or result.get("tool", {}).get("ccx_sha256") != request.get("solver", {}).get("sha256")
            or report.get("request_id") != identity(request)
            or report.get("evaluation_id") != result.get("evaluation_id")
            or report.get("generated_mesh", {}).get("mesh_m") != PREVIOUS_MESH_M
            or report.get("generated_mesh", {}).get("solid_elements") != 128_382
            or report.get("generated_mesh", {}).get("node_count") != 227_190
            or report.get("physical_and_engineering_acceptance") is not False
            or any(result.get(flag) is not False for flag in (
                "physical_accepted", "engineering_accepted",
                "manufacturing_release", "operating_release"))):
        raise ValueError("0.10625 m predecessor result or acceptance context differs")
    raw, regenerated, elements = railway_fine_refinement._fine_deck(
        body, bundle, mesh_m=PREVIOUS_MESH_M)
    if (raw.encode() != (folder / "native/model.inp").read_bytes()
            or definition != json.loads(encoded(regenerated))
            or len(elements) != 128_382):
        raise ValueError("0.10625 m predecessor deck does not regenerate from the exact candidate")
    return result, report, manifest


def _request(context: dict) -> dict:
    base = context["base"]
    estimate = railway_native.cell_estimate(context["body"], MESH_M)
    if estimate.get("solid_cells") != EXPECTED_CELLS or estimate.get("solid_cells") > CELL_BUDGET:
        raise ValueError("Exact 0.053125 m occupied-cell estimate differs from its declared budget")
    if estimate.get("coordinate_planes") != [427, 89, 90]:
        raise ValueError("Exact directional coordinate-plane preflight differs")
    preceding_runs = [
        dict(mesh_m=0.2125, request_id=context["base_manifest"]["request_id"],
             evaluation_id=context["base_result"]["evaluation_id"],
             manifest_id=context["base_manifest"]["manifest_id"]),
        dict(mesh_m=PREVIOUS_MESH_M,
             request_id=context["fine_manifest"]["request_id"],
             evaluation_id=context["fine_result"]["evaluation_id"],
             manifest_id=context["fine_manifest"]["manifest_id"]),
    ]
    load_basis = context["request_02125"]["load_basis"]
    if (context["request_02125"].get("load_case") != "normal"
            or context["request_02125"].get("element_kind") != ELEMENT_KIND
            or abs(float(context["request_02125"].get("load_mass_kg", 0.0))
                   - railway_fine_refinement.NORMAL_LOAD_KG) > 1e-6):
        raise ValueError("The exact same-candidate normal load and element basis are required")
    return dict(
        schema="osr-current-source-ultrafine-refinement-request/1",
        parent_campaign_id=context["parent"]["campaign_id"],
        parent_contract_id=context["parent"]["contract_id"],
        parent_run_id=context["parent"]["run_id"],
        parent_result_sha256=digest(context["parent_result"]),
        parent_frontier_item=context["frontier"],
        parent_evaluation_ids=[row[1] for row in base[6]],
        preceding_refinements=preceding_runs,
        body_candidate_id=context["body"]["candidate_id"],
        body_definition_id=context["body"]["definition_id"],
        bundle_id=context["bundle"]["candidate_id"],
        bundle_definition_id=context["bundle"]["definition_id"],
        load_case="normal", load_mass_kg=context["request_02125"]["load_mass_kg"],
        load_basis=load_basis, mesh_m=MESH_M, parent_mesh_m=PREVIOUS_MESH_M,
        element_kind=ELEMENT_KIND, computational_cell_estimate=estimate,
        computational_cell_budget=CELL_BUDGET, expected_solid_elements=EXPECTED_CELLS,
        expected_node_count=EXPECTED_NODES, memory_mb=MEMORY_MB, timeout_s=TIMEOUT_S,
        omp_threads=OMP_THREADS,
        solver=dict(path=SOLVER_PATH, sha256=digest(SOLVER_PATH)),
        solver_invocation_limit=1, retry_count=0,
        source_sha256=context["source_sha256"],
        purpose="Single bounded same-candidate numerical trend continuation; no engineering acceptance or physical qualification",
        **FLAGS)


def _package(root: Path, request: dict) -> Path:
    return Path(root) / "build/coupled-railway/refinements" / request["body_candidate_id"] / identity(request)


def _deck(candidate: dict, bundle: dict):
    """Generate the exact finite-face C3D8I normal-load deck at 0.053125 m."""
    if not grammar_shell.plan(candidate).get("admitted"):
        raise ValueError("Candidate failed the existing finite-face model admission")
    structural_ids = set(candidate["shell_model"]["structural_part_ids"])
    parts = [part for part in candidate["parts"] if part["id"] in structural_ids]
    nodes, elements, meta = grammar_shell._mesh(parts, MESH_M, ELEMENT_KIND)
    if (meta.get("finite_face_components") != 1
            or len(elements) != EXPECTED_CELLS
            or meta.get("solid_elements") != EXPECTED_CELLS
            or len(nodes) != EXPECTED_NODES
            or meta.get("node_count") != EXPECTED_NODES):
        raise ValueError("Generated grid differs from the exact 290660-cell/513844-node preflight")

    mass = float(bundle["normal_sprung_mass_hypothesis_kg"])
    if abs(mass - railway_fine_refinement.NORMAL_LOAD_KG) > 1e-6 or not math.isfinite(mass):
        raise ValueError("P1 normal sprung mass differs from the fixed same-load basis")
    load_basis = dict(bundle_id=bundle["candidate_id"],
                      bundle_definition_id=bundle["definition_id"], scope=bundle["mass_scope"])
    stock_mass = sum(element["volume_m3"]
                     * candidate["materials"][element["material_id"]]["density_kg_m3"]
                     for element in elements)
    if mass < stock_mass:
        raise ValueError("Normal sprung mass is below counted structural stock mass")

    loads = {node_id: np.zeros(3) for node_id in nodes}
    floor_area = 0.0
    for element in elements:
        weight = (element["volume_m3"]
                  * candidate["materials"][element["material_id"]]["density_kg_m3"]
                  * 9.80665)
        for node_id in element["nodes"]:
            loads[node_id][2] -= weight / 8.0
        if element["role"] == "floor" and abs(element["bounds"][5] - 1.0) < 1e-9:
            floor_area += ((element["bounds"][1] - element["bounds"][0])
                           * (element["bounds"][3] - element["bounds"][2]))
    if floor_area <= 0:
        raise ValueError("Counted passenger floor load surface is missing")
    pressure = (mass - stock_mass) * 9.80665 / floor_area
    for element in elements:
        if element["role"] == "floor" and abs(element["bounds"][5] - 1.0) < 1e-9:
            area = ((element["bounds"][1] - element["bounds"][0])
                    * (element["bounds"][3] - element["bounds"][2]))
            for node_id in element["nodes"][4:8]:
                loads[node_id][2] -= pressure * area / 4.0

    model = candidate["shell_model"]
    supports = {}
    patches = []
    for x in model["support_x_m"]:
        for y in model["support_y_m"]:
            patch_nodes = [node_id for node_id, point in nodes.items()
                           if abs(point[2] - model["support_z_m"]) < 1e-9
                           and abs(point[0] - x) <= 0.100001
                           and abs(point[1] - y) <= 0.090001]
            if len(patch_nodes) < 8:
                raise ValueError("Declared finite bearing pad is unresolved at 0.053125 m")
            for node_id in patch_nodes:
                supports[node_id] = {3}
            patches.append(dict(x_m=x, y_m=y, node_count=len(patch_nodes)))
    ordered = sorted(supports, key=lambda node_id: (nodes[node_id][0], nodes[node_id][1]))
    supports[ordered[0]].update((1, 2))
    supports[ordered[-1]].add(2)
    raw = grammar_shell._finish(
        grammar_shell._base(nodes, elements, candidate["materials"]), nodes, supports, loads)
    definition = dict(**meta, candidate_id=candidate["candidate_id"],
        definition_id=candidate["definition_id"], load_case="normal", load_mass_kg=mass,
        load_basis=load_basis, structural_selfweight_mass_kg=stock_mass,
        floor_lumped_remaining_mass_kg=mass-stock_mass,
        load_distribution="Consistent C3D8I selfweight plus uniform additional floor pressure; equipment and roof loads remain lumped",
        support_patches=patches,
        support_assumption="Rigid flat finite bearing pads, one XY datum and one Y datum; bogie compliance held",
        joint_assumption=model["joint_assumption"], nodes=nodes,
        supports={str(node_id): sorted(dofs) for node_id, dofs in supports.items()},
        loads_N={str(node_id): value.tolist() for node_id, value in loads.items()})
    return raw, definition, elements


def _execute_native(native: Path) -> dict:
    inherited = [value for value in resource.getrlimit(resource.RLIMIT_AS)
                 if value != resource.RLIM_INFINITY]
    cap = min([MEMORY_MB * 1024**2, *inherited]) if inherited else MEMORY_MB * 1024**2
    solver_hash = digest(SOLVER_PATH)
    tool = dict(ccx_path=SOLVER_PATH, ccx_sha256=solver_hash,
        requested_memory_mb=MEMORY_MB, RLIMIT_AS_bytes=cap, OMP_threads=OMP_THREADS,
        timeout_s=TIMEOUT_S,
        resource_control="POSIX RLIMIT_AS on native solver child; shared host workspace, no container isolation")
    started = time.monotonic()

    def apply_limit():
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))

    result = dict(execution="tool_error", numerical_validity="unknown", engineering_screen="unknown")
    try:
        proc = subprocess.run([SOLVER_PATH, "model"], cwd=native, capture_output=True,
            timeout=TIMEOUT_S, preexec_fn=apply_limit,
            env={**os.environ, "OMP_NUM_THREADS": str(OMP_THREADS)})
        (native / "stdout.log").write_bytes(proc.stdout)
        (native / "stderr.log").write_bytes(proc.stderr)
        result["returncode"] = proc.returncode
        if proc.returncode == 0:
            definition = json.loads((native / "definition.json").read_bytes())
            result.update(grammar_shell.analyse(definition, native / "model.dat"))
        elif b"ALLOCATE failure" in proc.stderr:
            result.update(execution="solver_allocation_failed", numerical_validity="not-produced",
                engineering_screen="not-evaluated",
                reason=f"CalculiX emitted an ALLOCATE failure under the declared {MEMORY_MB//1024} GiB address-space limit; no numerical result was produced.")
    except subprocess.TimeoutExpired as error:
        (native / "stdout.log").write_bytes(error.stdout or b"")
        (native / "stderr.log").write_bytes(error.stderr or b"")
        result.update(execution="interrupted", reason="bounded native time limit")
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        result["reason"] = str(error)
    peak = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    result["max_rss_kib"] = int(peak) if peak > 0 else None
    if digest(SOLVER_PATH) != solver_hash:
        raise ValueError("CalculiX executable changed during solver execution")
    result["tool"] = tool
    result["runtime_s"] = time.monotonic() - started
    summary = json.loads((native / "definition.json").read_bytes())
    result["mesh_summary"] = {k: v for k, v in summary.items()
                              if k not in ("nodes", "loads_N", "supports")}
    return result


def _same_request_except_runner(old: dict, current_request: dict) -> bool:
    old_value, current_value = dict(old), dict(current_request)
    old_sources = dict(old_value.pop("source_sha256", {}))
    current_sources = dict(current_value.pop("source_sha256", {}))
    old_sources.pop(PRODUCER, None)
    current_sources.pop(PRODUCER, None)
    old_sources.pop(railway_publication.PRODUCER, None)
    current_sources.pop(railway_publication.PRODUCER, None)
    return old_value == current_value and old_sources == current_sources


def _verify_recovered_package(context: dict, current_request: dict, folder: Path):
    """Verify a retained allocator failure without repeating its native solve."""
    old_request = json.loads((folder / "request.json").read_bytes())
    manifest = json.loads((folder / "manifest.json").read_bytes())
    if (not _same_request_except_runner(old_request, current_request)
            or old_request.get("retry_count") != 0
            or old_request.get("solver_invocation_limit") != 1):
        raise ValueError("Recovered native attempt is not the exact single bounded request")
    producer_snapshot = folder / "native/producer-source.py"
    if digest(producer_snapshot) != old_request.get("source_sha256", {}).get(PRODUCER):
        raise ValueError("Recovered execution producer snapshot differs from its request")
    sources = dict(old_request["source_sha256"])
    sources.pop(PRODUCER)
    publication_source = sources.pop(railway_publication.PRODUCER)
    _check_sources(context["root"], sources)
    if digest(SOLVER_PATH) != old_request.get("solver", {}).get("sha256"):
        raise ValueError("Recovered execution CalculiX executable differs")

    native = folder / "native"
    stdout = (native / "stdout.log").read_bytes()
    stderr = (native / "stderr.log").read_bytes()
    data = (native / "model.dat").read_bytes()
    status = (native / "model.sta").read_bytes()
    if (b"number of equations" not in stdout
            or b"4157109" not in stdout
            or b"ALLOCATE failure" not in stderr
            or b"S T E P" not in data
            or b"INC" not in status
            or len(data) > 512
            or len(status) > 256):
        raise ValueError("Retained native logs do not prove the recorded allocation failure")

    expected_raw, expected_definition, elements = _deck(context["body"], context["bundle"])
    definition = json.loads((native / "definition.json").read_bytes())
    if ((native / "model.inp").read_text() != expected_raw
            or definition != json.loads(encoded(expected_definition))
            or len(elements) != EXPECTED_CELLS):
        raise ValueError("Recovered native input does not regenerate from the current candidate")

    result = json.loads((native / "result.json").read_bytes())
    report = json.loads((folder / "report.json").read_bytes())
    actual = {p.relative_to(folder).as_posix(): digest(p) for p in folder.rglob("*")
              if p.is_file() and p.name != "manifest.json"}
    if (manifest.get("manifest_id") != identity(
            {k: v for k, v in manifest.items() if k != "manifest_id"})
            or manifest.get("schema") != "osr-current-source-ultrafine-recovery-manifest/1"
            or manifest.get("request_id") != identity(old_request)
            or manifest.get("parent_result_sha256") != old_request.get("parent_result_sha256")
            or manifest.get("source_sha256") != old_request.get("source_sha256")
            or manifest.get("files_sha256") != actual
            or result.get("evaluation_id") != identity(
                {k: v for k, v in result.items() if k != "evaluation_id"})
            or result.get("evaluation_id") != manifest.get("evaluation_id")
            or result.get("execution") != "solver_allocation_failed"
            or result.get("numerical_validity") != "not-produced"
            or result.get("returncode") is not None
            or result.get("max_rss_kib") is not None
            or result.get("source_sha256") != old_request.get("source_sha256")
            or result.get("source_bytes_unavailable") != {
                railway_publication.PRODUCER: publication_source}
            or report.get("request_id") != identity(old_request)
            or report.get("evaluation_id") != result.get("evaluation_id")
            or report.get("stderr_sha256") != digest(native / "stderr.log")
            or report.get("source_bytes_unavailable") != {
                railway_publication.PRODUCER: publication_source}
            or report.get("physical_and_engineering_acceptance") is not False
            or any(result.get(k) is not False for k in (
                "physical_accepted", "engineering_accepted",
                "manufacturing_release", "operating_release"))):
        raise ValueError("Recovered allocation-failure record or payload differs")
    source_epoch = context["root"] / "build/coupled-railway/source-epochs" / old_request["source_sha256"][PRODUCER]
    if not source_epoch.is_file() or digest(source_epoch) != old_request["source_sha256"][PRODUCER]:
        raise ValueError("Original refinement producer bytes were not retained")
    return result, report, manifest, old_request


def recover(root=ROOT, *, parent_result: Path, candidate_id: str) -> dict:
    """Seal a preserved native allocation failure; never launches CalculiX."""
    context = _context(root, parent_result=parent_result, candidate_id=candidate_id)
    current_request = _request(context)
    current_folder=_package(context["root"],current_request)
    if current_folder.is_dir() and (current_folder/"manifest.json").is_file():
        result,report,manifest=_verify_package_from_context(context,current_request)
        return {**FLAGS,"verified":True,"recovered":True,"request_id":manifest["request_id"],
            "manifest_id":manifest["manifest_id"],"evaluation_id":result["evaluation_id"],
            "execution":result["execution"],"numerical_validity":result["numerical_validity"],
            "candidate_id":candidate_id,"mesh_m":MESH_M,"memory_mb":MEMORY_MB,
            "returncode":result.get("returncode"),"max_rss_kib":result.get("max_rss_kib"),
            "physical_accepted":False,"engineering_accepted":False,
            "manufacturing_release":False,"operating_release":False}
    attempts=[]
    for path in _attempt_folders(context["root"],context["parent_result"],candidate_id):
        try:
            prior=json.loads((path/"native/result.json").read_bytes())
        except (OSError,ValueError,TypeError):
            continue
        if prior.get("execution")=="tool_error" and prior.get("tool",{}).get("requested_memory_mb")==current_request.get("memory_mb"):
            attempts.append(path)
    if len(attempts) != 1:
        raise ValueError("Recovery requires exactly one retained same-parent native attempt")
    folder = attempts[0]
    request = json.loads((folder / "request.json").read_bytes())
    if (folder / "manifest.json").is_file():
        stored_manifest=json.loads((folder/"manifest.json").read_bytes())
        if stored_manifest.get("schema")=="osr-current-source-ultrafine-recovery-manifest/1":
            result, report, manifest, request = _verify_recovered_package(
                context, current_request, folder)
        elif stored_manifest.get("schema")=="osr-current-source-ultrafine-refinement-manifest/1":
            result, report, manifest, request = _reconcile_exact_allocation_attempt(
                context, current_request, folder)
        else:
            raise ValueError("Retained ultrafine attempt has an unsupported immutable manifest")
    else:
        if not _same_request_except_runner(request, current_request):
            raise ValueError("Retained native attempt differs from the current candidate request")
        native = folder / "native"
        snapshot = native / "producer-source.py"
        if not snapshot.is_file() or digest(snapshot) != request["source_sha256"].get(PRODUCER):
            raise ValueError("Exact producer source for the retained attempt is unavailable")
        source_epoch = context["root"] / "build/coupled-railway/source-epochs" / request["source_sha256"][PRODUCER]
        source_epoch.parent.mkdir(parents=True, exist_ok=True)
        if source_epoch.exists() and digest(source_epoch) != request["source_sha256"][PRODUCER]:
            raise ValueError("Producer source epoch already contains different bytes")
        if not source_epoch.exists():
            source_epoch.write_bytes(snapshot.read_bytes())

        stderr = (native / "stderr.log").read_bytes()
        stdout = (native / "stdout.log").read_bytes()
        if b"ALLOCATE failure" not in stderr or b"4157109" not in stdout:
            raise ValueError("Retained native output is not the declared CalculiX allocation failure")
        definition = json.loads((native / "definition.json").read_bytes())
        mesh_summary = {k: v for k, v in definition.items()
                        if k not in ("nodes", "loads_N", "supports")}
        missing_source = {railway_publication.PRODUCER:
            request["source_sha256"][railway_publication.PRODUCER]}
        result = {**FLAGS, "schema":"osr-current-source-ultrafine-recovery-result/1",
            "execution":"solver_allocation_failed", "numerical_validity":"not-produced",
            "engineering_screen":"not-evaluated", "candidate_id":request["body_candidate_id"],
            "definition_id":request["body_definition_id"], "source_sha256":request["source_sha256"],
            "mesh_summary":mesh_summary, "returncode":None, "max_rss_kib":None,
            "resource_observations":dict(returncode="unavailable after runner postprocessing error",
                peak_rss="unavailable after runner postprocessing error",
                runtime="unavailable after runner postprocessing error"),
            "source_bytes_unavailable":missing_source,
            "tool":dict(ccx_path=SOLVER_PATH, ccx_sha256=request["solver"]["sha256"],
                requested_memory_mb=MEMORY_MB, RLIMIT_AS_bytes=MEMORY_MB*1024**2,
                OMP_threads=OMP_THREADS, timeout_s=TIMEOUT_S,
                resource_control="POSIX RLIMIT_AS on native solver child; shared host workspace, no container isolation"),
            "reason":f"CalculiX emitted an ALLOCATE failure while factoring the 4,157,109-equation system under the declared {MEMORY_MB//1024} GiB address-space limit. The solver return code, peak RSS and runtime were not retained by the postprocessing exception.",
            "physical_accepted":False, "engineering_accepted":False,
            "manufacturing_release":False, "operating_release":False,
            "configuration_adopted":False}
        result["evaluation_id"] = identity(result)
        report = dict(schema="osr-current-source-ultrafine-recovery-report/1",
            request_id=identity(request), evaluation_id=result["evaluation_id"],
            parent_campaign_id=request["parent_campaign_id"],
            parent_contract_id=request["parent_contract_id"],
            body_candidate_id=request["body_candidate_id"],
            body_definition_id=request["body_definition_id"],
            bundle_id=request["bundle_id"], bundle_definition_id=request["bundle_definition_id"],
            generated_mesh=dict(mesh_m=MESH_M, element_kind=ELEMENT_KIND,
                solid_elements=EXPECTED_CELLS, node_count=EXPECTED_NODES,
                solver_estimated_nodes=1_385_824, equation_count=4_157_109),
            solver_outcome="allocator failure during matrix factorization; no numerical result",
            returncode=None, max_rss_kib=None, runtime_s=None,
            stdout_sha256=digest(native / "stdout.log"),
            stderr_sha256=digest(native / "stderr.log"),
            model_dat_sha256=digest(native / "model.dat"),
            source_bytes_unavailable=missing_source,
            source_completeness="held; the source digest is recorded but the exact publication source bytes are unavailable",
            physical_and_engineering_acceptance=False,
            interpretation="The exact candidate deck was generated and submitted once. CalculiX failed during factorization under the declared address-space cap; no displacement, equilibrium or engineering result is available. This is a computational resource failure, not a physical failure or qualification.",
            **FLAGS)
        (native / "result.json").write_bytes(encoded(result))
        (folder / "report.json").write_bytes(encoded(report))
        files = {p.relative_to(folder).as_posix(): digest(p) for p in folder.rglob("*")
                 if p.is_file() and p.name != "manifest.json"}
        manifest = dict(schema="osr-current-source-ultrafine-recovery-manifest/1",
            request_id=identity(request), evaluation_id=result["evaluation_id"],
            parent_result_sha256=request["parent_result_sha256"],
            source_sha256=request["source_sha256"], files_sha256=files, **FLAGS)
        manifest["manifest_id"] = identity(manifest)
        (folder / "manifest.json").write_bytes(encoded(manifest))
        result, report, manifest, request = _verify_recovered_package(
            context, current_request, folder)
    return {**FLAGS, "verified":True, "recovered":True,
        "request_id":manifest["request_id"], "manifest_id":manifest["manifest_id"],
        "evaluation_id":result["evaluation_id"], "execution":result["execution"],
        "numerical_validity":result["numerical_validity"], "candidate_id":candidate_id,
        "mesh_m":MESH_M, "memory_mb":MEMORY_MB, "returncode":result.get("returncode"),
        "max_rss_kib":result.get("max_rss_kib"), "physical_accepted":False,
        "engineering_accepted":False, "manufacturing_release":False,
        "operating_release":False}


def _reconcile_exact_allocation_attempt(context: dict, current_request: dict, old_folder: Path):
    """Reclassify a preserved solver failure after fixing its result parser."""
    old_request=json.loads((old_folder/"request.json").read_bytes())
    old_manifest=json.loads((old_folder/"manifest.json").read_bytes())
    old_native=old_folder/"native"
    old_result=json.loads((old_native/"result.json").read_bytes())
    actual_old={p.relative_to(old_folder).as_posix():digest(p) for p in old_folder.rglob("*")
        if p.is_file() and p.name!="manifest.json"}
    if (old_manifest.get("manifest_id")!=identity({k:v for k,v in old_manifest.items() if k!="manifest_id"})
            or old_manifest.get("schema")!="osr-current-source-ultrafine-refinement-manifest/1"
            or old_manifest.get("request_id")!=identity(old_request)
            or old_manifest.get("files_sha256")!=actual_old
            or old_result.get("evaluation_id")!=identity({k:v for k,v in old_result.items() if k!="evaluation_id"})
            or old_result.get("execution")!="tool_error"
            or old_result.get("returncode")!=255
            or old_result.get("tool",{}).get("requested_memory_mb")!=current_request.get("memory_mb")
            or old_result.get("tool",{}).get("timeout_s")!=current_request.get("timeout_s")
            or not _same_request_except_runner(old_request,current_request)):
        raise ValueError("Preserved ultrafine result is not the exact same-parent allocation attempt")
    old_source_epoch=context["root"]/"build/coupled-railway/source-epochs"/old_request["source_sha256"][PRODUCER]
    if not old_source_epoch.is_file() or digest(old_source_epoch)!=old_request["source_sha256"][PRODUCER]:
        raise ValueError("Exact original runner source bytes for the allocation attempt are unavailable")
    stderr=(old_native/"stderr.log").read_bytes()
    stdout=(old_native/"stdout.log").read_bytes()
    if b"ALLOCATE failure" not in stderr or b"4157109" not in stdout:
        raise ValueError("Preserved native logs do not prove the declared allocation failure")

    raw,definition,elements=_deck(context["body"],context["bundle"])
    old_definition=json.loads((old_native/"definition.json").read_bytes())
    if ((old_native/"model.inp").read_text()!=raw
            or old_definition!=json.loads(encoded(definition))
            or len(elements)!=EXPECTED_CELLS
            or old_result.get("mesh_summary",{}).get("load_basis")!=current_request.get("load_basis")
            or old_result.get("tool",{}).get("ccx_sha256")!=current_request.get("solver",{}).get("sha256")):
        raise ValueError("Retained failure deck, candidate, load or solver differs from the current request")

    folder=_package(context["root"],current_request)
    if folder.exists():
        raise ValueError("Current ultrafine recovery destination already exists")
    native=folder/"native";native.mkdir(parents=True)
    (folder/"request.json").write_bytes(encoded(current_request))
    for path in old_native.iterdir():
        if path.is_file() and path.name not in ("result.json","candidate.json","producer-source.py"):
            shutil.copyfile(path,native/path.name)
    candidate=dict(candidate_id=current_request["body_candidate_id"],
        definition_id=current_request["body_definition_id"])
    (native/"candidate.json").write_bytes(encoded(candidate))
    (native/"producer-source.py").write_bytes((context["root"]/PRODUCER).read_bytes())
    reuse=dict(schema="osr-exact-failed-native-reuse/1",
        source_attempt_request_id=identity(old_request),source_attempt_manifest_id=old_manifest["manifest_id"],
        source_attempt_evaluation_id=old_result["evaluation_id"],source_attempt_payload_sha256=actual_old,
        source_attempt_runner_sha256=old_request["source_sha256"][PRODUCER],
        equivalence="Same current parent, body, bundle, generated deck, normal load, mesh, C3D8I method, CalculiX executable, memory cap and timeout; the runner source changed only to classify the preserved native allocator failure.",
        solver_invocation_repeated=False,physical_accepted=False,engineering_accepted=False)
    shutil.copyfile(old_source_epoch,native/"source-attempt-producer.py")
    (folder/"reuse-context.json").write_bytes(encoded(reuse))
    definition_summary={k:v for k,v in definition.items() if k not in ("nodes","loads_N","supports")}
    memory_gib=current_request["memory_mb"]/1024
    result={**FLAGS,"schema":"osr-current-source-ultrafine-refinement-result/1",
        "execution":"solver_allocation_failed","numerical_validity":"not-produced",
        "engineering_screen":"not-evaluated","candidate_id":current_request["body_candidate_id"],
        "definition_id":current_request["body_definition_id"],"source_sha256":current_request["source_sha256"],
        "mesh_summary":definition_summary,"returncode":old_result["returncode"],
        "max_rss_kib":old_result["max_rss_kib"],"runtime_s":old_result.get("runtime_s"),
        "tool":old_result["tool"],"resource_observations":dict(returncode=old_result["returncode"],
            max_rss_kib=old_result["max_rss_kib"],runtime_s=old_result.get("runtime_s")),
        "reuse_context_id":identity(reuse),
        "reason":f"CalculiX emitted an ALLOCATE failure while factoring the 4,157,109-equation system under the declared {memory_gib:g} GiB address-space limit. The exact same-parent native attempt is retained and reclassified; the solver was not run again.",
        "physical_accepted":False,"engineering_accepted":False,"manufacturing_release":False,
        "operating_release":False,"configuration_adopted":False}
    result["evaluation_id"]=identity(result)
    (native/"result.json").write_bytes(encoded(result))
    report=dict(schema="osr-current-source-ultrafine-refinement-report/1",
        request_id=identity(current_request),evaluation_id=result["evaluation_id"],
        parent_campaign_id=current_request["parent_campaign_id"],
        parent_contract_id=current_request["parent_contract_id"],
        body_candidate_id=current_request["body_candidate_id"],body_definition_id=current_request["body_definition_id"],
        bundle_id=current_request["bundle_id"],bundle_definition_id=current_request["bundle_definition_id"],
        preceding_refinements=current_request["preceding_refinements"],
        generated_mesh=dict(mesh_m=definition["mesh_m"],element_kind=definition["element_kind"],
            finite_face_components=definition["finite_face_components"],solid_elements=definition["solid_elements"],
            node_count=definition["node_count"],element_count=len(elements)),
        max_rss_kib=result["max_rss_kib"],mesh_and_residual_trend=current_request["preceding_refinements"],
        matched_point_displacement_comparisons=[dict(from_mesh_m=row["mesh_m"],to_mesh_m=MESH_M,
            from_evaluation_id=row["evaluation_id"],status="unavailable",
            reason="Native solver did not produce a numerical result")
            for row in current_request["preceding_refinements"]],solver_outcome="allocator failure; no numerical result",
        reuse_context_id=identity(reuse),physical_and_engineering_acceptance=False,
        interpretation="The exact same-parent candidate/load/mesh/solver/resource attempt was verified from its immutable native logs and deck, then classified without another solver invocation. No numerical structural result or physical qualification exists.",**FLAGS)
    (folder/"report.json").write_bytes(encoded(report))
    files={p.relative_to(folder).as_posix():digest(p) for p in folder.rglob("*")
        if p.is_file() and p.name!="manifest.json"}
    manifest=dict(schema="osr-current-source-ultrafine-refinement-manifest/1",
        request_id=identity(current_request),evaluation_id=result["evaluation_id"],
        parent_result_sha256=current_request["parent_result_sha256"],
        source_sha256=current_request["source_sha256"],files_sha256=files,**FLAGS)
    manifest["manifest_id"]=identity(manifest)
    (folder/"manifest.json").write_bytes(encoded(manifest))
    return result,report,manifest,current_request


def _external_integrity(context: dict, request: dict) -> None:
    if digest(context["parent_result"]) != request["parent_result_sha256"]:
        raise ValueError("Parent campaign changed during the finer mesh run")
    _check_sources(context["root"], request["source_sha256"])
    if digest(SOLVER_PATH) != request["solver"]["sha256"]:
        raise ValueError("Pinned solver executable changed during the finer mesh run")
    for folder_key, manifest_key, label in (
            ("base_folder", "base_manifest", "0.2125 m"),
            ("fine_folder", "fine_manifest", "0.10625 m")):
        folder = context[folder_key]
        manifest = json.loads((folder / "manifest.json").read_bytes())
        actual = {p.relative_to(folder).as_posix(): digest(p) for p in folder.rglob("*")
                  if p.is_file() and p.name != "manifest.json"}
        if (manifest.get("manifest_id") != context[manifest_key].get("manifest_id")
                or actual != context[manifest_key].get("files_sha256")):
            raise ValueError(f"Verified {label} predecessor package changed during the finer mesh run")


def run(root=ROOT, *, parent_result: Path, candidate_id: str) -> dict:
    context = _context(root, parent_result=parent_result, candidate_id=candidate_id)
    request = _request(context)
    folder = _package(context["root"], request)
    attempts = _attempt_folders(context["root"], context["parent_result"], candidate_id)
    if attempts and (len(attempts) != 1 or attempts[0] != folder):
        raise ValueError("A same-parent ultrafine solver attempt already exists; recover or verify it before any new solve")
    if folder.exists():
        if not (folder / "manifest.json").is_file():
            raise ValueError("Incomplete native attempt is preserved; use refine-current-ultrafine-recover")
        stored_manifest = json.loads((folder / "manifest.json").read_bytes())
        if stored_manifest.get("schema") == "osr-current-source-ultrafine-recovery-manifest/1":
            result, report, manifest, _old_request = _verify_recovered_package(
                context, request, folder)
            return dict(request_id=manifest["request_id"], evaluation_id=result["evaluation_id"],
                manifest_id=manifest["manifest_id"], execution=result.get("execution"),
                numerical_validity=result.get("numerical_validity"), output=str(folder),
                reused=True, recovered=True, **FLAGS)
        result, report, manifest = _verify_package_from_context(context, request)
        return dict(request_id=manifest["request_id"], evaluation_id=result["evaluation_id"],
            manifest_id=manifest["manifest_id"], execution=result.get("execution"),
            numerical_validity=result.get("numerical_validity"), max_rss_kib=result.get("max_rss_kib"),
            output=str(folder), reused=True, **FLAGS)

    estimate = request["computational_cell_estimate"]
    body, bundle = context["body"], context["bundle"]
    raw, definition, elements = _deck(body, bundle)
    if (definition.get("solid_elements") != estimate["solid_cells"]
            or definition.get("node_count") != EXPECTED_NODES
            or definition.get("load_basis") != request["load_basis"]
            or definition.get("load_mass_kg") != request["load_mass_kg"]):
        raise ValueError("Generated deck differs from its exact resource request")

    folder.mkdir(parents=True)
    (folder / "request.json").write_bytes(encoded(request))
    native = folder / "native"
    native.mkdir()
    (native / "model.inp").write_text(raw)
    (native / "definition.json").write_bytes(encoded(definition))
    generated_mesh = {key: definition[key] for key in
                      ("mesh_m", "element_kind", "finite_face_components", "solid_elements", "node_count")}
    generated_mesh["element_count"] = len(elements)
    del raw, definition, elements, body, bundle
    gc.collect()
    try:
        import ctypes
        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except (OSError, AttributeError):
        pass

    _external_integrity(context, request)
    result = _execute_native(native)
    _external_integrity(context, request)
    result.update({**FLAGS, "candidate_id": request["body_candidate_id"],
        "definition_id": request["body_definition_id"], "source_sha256": request["source_sha256"],
        "engineering_accepted": False, "manufacturing_release": False,
        "operating_release": False, "physical_accepted": False,
        "configuration_adopted": False})
    result["evaluation_id"] = identity(result)
    (native / "candidate.json").write_bytes(encoded(dict(
        candidate_id=request["body_candidate_id"], definition_id=request["body_definition_id"])))
    (native / "result.json").write_bytes(encoded(result))

    comparisons = []
    for mesh_m, source_eval, source_native, source_result in (
            (0.2125, context["base_result"]["evaluation_id"],
             context["base_folder"] / "native", context["base_result"]),
            (PREVIOUS_MESH_M, context["fine_result"]["evaluation_id"],
             context["fine_folder"] / "native", context["fine_result"])):
        delta = (railway_refinement._matched_point_delta(source_native, native)
                 if result.get("execution") == "completed"
                 else dict(status="unavailable", reason="Finer solve did not complete"))
        comparisons.append(dict(from_mesh_m=mesh_m, to_mesh_m=MESH_M,
            from_evaluation_id=source_eval, **delta))

    trend = []
    for mesh_m, evaluation_id, old in (
            (0.2125, context["base_result"]["evaluation_id"], context["base_result"]),
            (PREVIOUS_MESH_M, context["fine_result"]["evaluation_id"], context["fine_result"]),
            (MESH_M, result["evaluation_id"], result)):
        trend.append(dict(mesh_m=mesh_m, evaluation_id=evaluation_id,
            maximum_displacements=old.get("maximum_displacements"),
            external_work_J=old.get("external_work_J"),
            native_internal_energy_J=old.get("native_internal_energy_J"),
            energy_relative_residual=old.get("energy_relative_residual"),
            force_relative_residual=old.get("force_relative_residual"),
            moment_relative_residual=old.get("moment_relative_residual")))
    report = dict(schema="osr-current-source-ultrafine-refinement-report/1",
        request_id=identity(request), evaluation_id=result["evaluation_id"],
        parent_campaign_id=request["parent_campaign_id"], parent_contract_id=request["parent_contract_id"],
        body_candidate_id=request["body_candidate_id"], body_definition_id=request["body_definition_id"],
        bundle_id=request["bundle_id"], bundle_definition_id=request["bundle_definition_id"],
        preceding_refinements=request["preceding_refinements"], generated_mesh=generated_mesh,
        max_rss_kib=result.get("max_rss_kib"), mesh_and_residual_trend=trend,
        matched_point_displacement_comparisons=comparisons,
        physical_and_engineering_acceptance=False,
        interpretation="Same-candidate C3D8I numerical refinement only. Displacement and equilibrium/energy trends do not establish material or joint strength, fatigue, buckling, clearance, physical correlation, or qualification.",
        **FLAGS)
    (folder / "report.json").write_bytes(encoded(report))
    files = {p.relative_to(folder).as_posix(): digest(p) for p in folder.rglob("*")
             if p.is_file() and p.name != "manifest.json"}
    manifest = dict(schema="osr-current-source-ultrafine-refinement-manifest/1",
        request_id=identity(request), evaluation_id=result["evaluation_id"],
        parent_result_sha256=request["parent_result_sha256"],
        source_sha256=request["source_sha256"], files_sha256=files, **FLAGS)
    manifest["manifest_id"] = identity(manifest)
    (folder / "manifest.json").write_bytes(encoded(manifest))
    return dict(request_id=manifest["request_id"], evaluation_id=result["evaluation_id"],
        execution=result.get("execution"), numerical_validity=result.get("numerical_validity"),
        max_rss_kib=result.get("max_rss_kib"), output=str(folder), reused=False,
        manifest_id=manifest["manifest_id"], **FLAGS)


def _verify_package(root=ROOT, *, parent_result: Path, candidate_id: str):
    context = _context(root, parent_result=parent_result, candidate_id=candidate_id)
    request = _request(context)
    return _verify_package_from_context(context, request)


def _verify_package_from_context(context: dict, request: dict):
    """Verify a package after its parent and candidate context were checked."""
    root = context["root"]
    folder = _package(context["root"], request)
    if not folder.is_dir():
        raise ValueError("Current-source 0.053125 m package is missing")
    manifest = json.loads((folder / "manifest.json").read_bytes())
    actual = {p.relative_to(folder).as_posix(): digest(p) for p in folder.rglob("*")
              if p.is_file() and p.name != "manifest.json"}
    if (manifest.get("manifest_id") != identity({k: v for k, v in manifest.items() if k != "manifest_id"})
            or manifest.get("request_id") != identity(request)
            or manifest.get("parent_result_sha256") != request["parent_result_sha256"]
            or manifest.get("source_sha256") != request["source_sha256"]
            or manifest.get("files_sha256") != actual
            or json.loads((folder / "request.json").read_bytes()) != request):
        raise ValueError("Ultrafine manifest, request, or package payload differs")
    result = json.loads((folder / "native/result.json").read_bytes())
    report = json.loads((folder / "report.json").read_bytes())
    definition = json.loads((folder / "native/definition.json").read_bytes())
    if (result.get("evaluation_id") != identity({k: v for k, v in result.items() if k != "evaluation_id"})
            or result.get("evaluation_id") != manifest.get("evaluation_id")
            or result.get("source_sha256") != request["source_sha256"]
            or result.get("candidate_id") != request["body_candidate_id"]
            or result.get("definition_id") != request["body_definition_id"]
            or result.get("mesh_summary", {}).get("mesh_m") != MESH_M
            or result.get("mesh_summary", {}).get("solid_elements") != EXPECTED_CELLS
            or result.get("mesh_summary", {}).get("node_count") != EXPECTED_NODES
            or result.get("tool", {}).get("requested_memory_mb") != MEMORY_MB
            or result.get("tool", {}).get("timeout_s") != TIMEOUT_S
            or result.get("tool", {}).get("OMP_threads") != OMP_THREADS
            or result.get("tool", {}).get("ccx_path") != SOLVER_PATH
            or result.get("tool", {}).get("ccx_sha256") != request["solver"]["sha256"]
            or not isinstance(result.get("tool", {}).get("RLIMIT_AS_bytes"), int)
            or not 0 < result["tool"]["RLIMIT_AS_bytes"] <= MEMORY_MB * 1024**2
            or not isinstance(result.get("max_rss_kib"), int) or result["max_rss_kib"] <= 0
            or report.get("request_id") != identity(request)
            or report.get("evaluation_id") != result.get("evaluation_id")
            or report.get("generated_mesh", {}).get("solid_elements") != EXPECTED_CELLS
            or report.get("generated_mesh", {}).get("node_count") != EXPECTED_NODES
            or definition.get("solid_elements") != EXPECTED_CELLS
            or definition.get("node_count") != EXPECTED_NODES
            or report.get("max_rss_kib") != result.get("max_rss_kib")
            or report.get("physical_and_engineering_acceptance") is not False
            or any(result.get(flag) is not False for flag in FLAGS)):
        raise ValueError("Ultrafine result, mesh, resource, or acceptance context differs")
    _check_sources(context["root"], request["source_sha256"])
    raw, regenerated, elements = _deck(context["body"], context["bundle"])
    if ((folder / "native/model.inp").read_text() != raw
            or definition != json.loads(encoded(regenerated))
            or len(elements) != EXPECTED_CELLS):
        raise ValueError("Ultrafine deck does not regenerate from the exact candidate and load")
    return result, report, manifest


def verify(root=ROOT, *, parent_result: Path, candidate_id: str):
    context = _context(root, parent_result=parent_result, candidate_id=candidate_id)
    current_request = _request(context)
    attempts = _attempt_folders(context["root"], context["parent_result"], candidate_id)
    recovered = next((folder for folder in attempts
        if (folder / "manifest.json").is_file()
        and json.loads((folder / "manifest.json").read_bytes()).get("schema")
            == "osr-current-source-ultrafine-recovery-manifest/1"), None)
    if recovered is not None:
        result, report, manifest, _old_request = _verify_recovered_package(
            context, current_request, recovered)
    else:
        result, report, manifest = _verify_package_from_context(context, current_request)
    return {**FLAGS, "verified":True, "request_id":manifest["request_id"],
        "manifest_id":manifest["manifest_id"], "evaluation_id":result["evaluation_id"],
        "candidate_id":candidate_id, "body_definition_id":result["definition_id"],
        "mesh_m":report["generated_mesh"]["mesh_m"], "execution":result.get("execution"),
        "numerical_validity":result.get("numerical_validity"),
        "max_rss_kib":result.get("max_rss_kib"), "recovered":recovered is not None}
