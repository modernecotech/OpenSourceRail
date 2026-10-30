"""Resource-only retry study for the fixed 0.10625 m railway body case.

The 8 GiB/240 s request is a separate evaluation from the preserved failed
5 GiB attempt. Candidate, load, mesh, materials, joints, supports and solver
method remain fixed; numerical execution never implies physical acceptance.
"""
from __future__ import annotations

import json
import os
import resource
import subprocess
import time
from pathlib import Path

from engineering.station_rail import ROOT, FLAGS
from engineering.station_rail.common import digest, encoded, identity
from . import grammar_shell, railway_native, railway_refinement, railway_fine_refinement

PRODUCER = "engineering/design_search/railway_fine_refinement_resource.py"
CAMPAIGN_ID = "6ba19dff09e30606bb4d20ddd153deef033c86ab1d27adc8dab6ad842d68f99f"
CONTRACT_ID = railway_fine_refinement.CONTRACT_ID
CANDIDATE_ID = "8db92b830fda54c81ec231c541f811b24f938f2471b559448d2ed2683754f78b"
DEFINITION_ID = "21efbaf935ba954a6788d2c54e841b12c891a01b70afef4f7a2edd581af5458f"
BUNDLE_ID = "1e8d1d7c394fc0bdbd47e34fb21d413ebc34a49576bad60b31b254bd635dfb68"
FAILED_REQUEST_ID = "46dac2f71ff6b42ae0715b4219e1789534b0014d8cbae0bdb786bb55112f3b75"
FAILED_EVALUATION_ID = "7347006f979dba45aa8958599a49c2ef68ac5a543dc7a5a20a4f6ed6034ddc4d"
FAILED_MANIFEST_ID = "7e51fdfa20aba5a2783589a2c4678ea5385baf0ec6ff3686dd716d52d1d12ef9"
PREVIOUS_REQUEST_ID = railway_fine_refinement.PREVIOUS_REQUEST_ID
PREVIOUS_EVALUATION_ID = railway_fine_refinement.PREVIOUS_EVALUATION_ID
PREVIOUS_MANIFEST_ID = railway_fine_refinement.PREVIOUS_MANIFEST_ID
MESH_M = 0.10625
EXPECTED_CELLS = 128_382
CELL_BUDGET = 140_000
EXPECTED_NODES = 227_190
ELEMENT_KIND = "C3D8I"
NORMAL_LOAD_KG = 10_818.661193648113
OLD_MEMORY_MB = 5_120
OLD_TIMEOUT_S = 150
MEMORY_MB = 8_192
TIMEOUT_S = 240
OMP_THREADS = 1
CCX_PATH = "/usr/bin/ccx"
CCX_SHA256 = "373f7ef4c118a1b5e1b53041fe4f7ef1f1f854051326e0d3f1eeb890ec34885b"
FAILURE_CLASS = "calculix_allocation_failure_during_matrix_factorization"


def _checked_hashes(root: Path, sources: dict[str, str]) -> None:
    root = root.resolve()
    for name, expected in sources.items():
        path = (root / name).resolve()
        if root not in path.parents or not path.is_file() or digest(path) != expected:
            raise ValueError(f"Source identity mismatch: {name}")


def _requested_address_space_cap() -> int:
    requested = MEMORY_MB * 1024**2
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    limits = [requested] + [value for value in (soft, hard)
                            if value != resource.RLIM_INFINITY]
    effective = min(limits)
    if effective != requested:
        raise ValueError("The process address-space limit cannot honor the fixed 8,192 MiB revision")
    return effective


def _failed_attempt(root: Path, parent_result: Path, parent_sha256: str) -> dict:
    """Verify and fingerprint the immutable 5 GiB allocation failure."""
    verified = railway_fine_refinement.verify(
        root, parent_result=parent_result, candidate_id=CANDIDATE_ID)
    if (verified.get("verified") is not True
            or verified.get("request_id") != FAILED_REQUEST_ID
            or verified.get("evaluation_id") != FAILED_EVALUATION_ID
            or verified.get("manifest_id") != FAILED_MANIFEST_ID
            or verified.get("execution") != "tool_error"
            or verified.get("prior_request_id") != PREVIOUS_REQUEST_ID
            or verified.get("prior_evaluation_id") != PREVIOUS_EVALUATION_ID
            or verified.get("prior_manifest_id") != PREVIOUS_MANIFEST_ID):
        raise ValueError("Pinned 5 GiB fine-refinement package does not verify")
    folder = (root / "build/coupled-railway/refinements" / CANDIDATE_ID / FAILED_REQUEST_ID).resolve()
    package_root = (root / "build/coupled-railway/refinements" / CANDIDATE_ID).resolve()
    if package_root not in folder.parents:
        raise ValueError("Failed-attempt path escapes the private refinement tree")
    request_path = folder / "request.json"
    result_path = folder / "native" / "result.json"
    manifest_path = folder / "manifest.json"
    stdout_path = folder / "native" / "stdout.log"
    stderr_path = folder / "native" / "stderr.log"
    request = json.loads(request_path.read_bytes())
    result = json.loads(result_path.read_bytes())
    manifest = json.loads(manifest_path.read_bytes())
    stderr = stderr_path.read_text(errors="replace")
    actual_files = {path.relative_to(folder).as_posix(): digest(path)
                    for path in folder.rglob("*")
                    if path.is_file() and path.relative_to(folder).as_posix()
                    not in ("manifest.json", "report.json")}
    if (manifest.get("manifest_id") != identity(
            {key: value for key, value in manifest.items() if key != "manifest_id"})
            or actual_files != manifest.get("files_sha256")):
        raise ValueError("Pinned failed-attempt file hashes differ from its manifest")
    summary = result.get("mesh_summary", {})
    tool = result.get("tool", {})
    if (request.get("request_id", FAILED_REQUEST_ID) != FAILED_REQUEST_ID
            or request.get("parent_result_sha256") != parent_sha256
            or request.get("body_candidate_id") != CANDIDATE_ID
            or request.get("body_definition_id") != DEFINITION_ID
            or request.get("bundle_id") != BUNDLE_ID
            or request.get("mesh_m") != MESH_M
            or request.get("element_kind") != ELEMENT_KIND
            or request.get("load_case") != "normal"
            or request.get("load_mass_kg") != NORMAL_LOAD_KG
            or request.get("memory_mb") != OLD_MEMORY_MB
            or request.get("timeout_s") != OLD_TIMEOUT_S
            or request.get("omp_threads") != OMP_THREADS
            or request.get("solver_sha256") != CCX_SHA256
            or result.get("request_id") != FAILED_REQUEST_ID
            or result.get("evaluation_id") != FAILED_EVALUATION_ID
            or result.get("execution") != "tool_error"
            or result.get("returncode") != 255
            or result.get("candidate_id") != CANDIDATE_ID
            or result.get("definition_id") != DEFINITION_ID
            or result.get("parent_result_sha256") != parent_sha256
            or result.get("source_sha256") != request.get("source_sha256")
            or tool.get("requested_memory_mb") != OLD_MEMORY_MB
            or tool.get("timeout_s") != OLD_TIMEOUT_S
            or tool.get("OMP_threads") != OMP_THREADS
            or tool.get("RLIMIT_AS_bytes") != OLD_MEMORY_MB * 1024**2
            or tool.get("ccx_path") != CCX_PATH
            or tool.get("ccx_sha256") != CCX_SHA256
            or summary.get("mesh_m") != MESH_M
            or summary.get("element_kind") != ELEMENT_KIND
            or summary.get("solid_elements") != EXPECTED_CELLS
            or summary.get("node_count") != EXPECTED_NODES
            or summary.get("finite_face_components") != 1
            or summary.get("load_case") != "normal"
            or summary.get("load_mass_kg") != NORMAL_LOAD_KG
            or "allocate failure" not in stderr.lower()):
        raise ValueError("Pinned failed package does not match the specified returncode-255 allocation failure")
    package = dict(request_id=FAILED_REQUEST_ID,
                   evaluation_id=FAILED_EVALUATION_ID,
                   manifest_id=FAILED_MANIFEST_ID,
                   parent_result_sha256=parent_sha256,
                   returncode=255,
                   execution="tool_error",
                   failure_class=FAILURE_CLASS,
                   request_sha256=digest(request_path),
                   result_sha256=digest(result_path),
                   manifest_sha256=digest(manifest_path),
                   stdout_sha256=digest(stdout_path),
                   stderr_sha256=digest(stderr_path),
                   source_sha256=manifest.get("source_sha256"),
                   files_sha256=manifest.get("files_sha256"))
    package["package_id"] = identity(package)
    return package


def _context(root: Path, parent_result: Path, candidate_id: str):
    (root, parent_result, parent, body, bundle, frontier, prior,
     parent_sha256, prior_refinement, fine_sources) = railway_fine_refinement._context(
         root, parent_result, candidate_id)
    if (parent.get("campaign_id") != CAMPAIGN_ID
            or parent.get("contract_id") != CONTRACT_ID
            or body.get("candidate_id") != CANDIDATE_ID
            or body.get("definition_id") != DEFINITION_ID
            or bundle.get("candidate_id") != BUNDLE_ID):
        raise ValueError("Parent campaign/body/bundle differs from this resource-only evaluation")
    failed_package = _failed_attempt(root, parent_result, parent_sha256)
    sources = dict(fine_sources)
    sources[PRODUCER] = digest(root / PRODUCER)
    _checked_hashes(root, sources)
    if not Path(CCX_PATH).is_file() or digest(CCX_PATH) != CCX_SHA256:
        raise ValueError("Pinned CalculiX executable is missing or has changed")
    return (root, parent_result, parent, body, bundle, frontier, prior,
            parent_sha256, prior_refinement, failed_package, sources)


def _request(*, parent: dict, body: dict, bundle: dict, frontier: dict,
             prior: list, parent_sha256: str, prior_refinement: dict,
             failed_package: dict, source_sha256: dict, estimate: dict) -> dict:
    base_request = prior[1][3]
    return dict(schema="osr-railway-fine-refinement-resource-request/1",
                parent_campaign_id=parent["campaign_id"],
                parent_contract_id=parent["contract_id"],
                parent_result_sha256=parent_sha256,
                parent_run_id=parent["run_id"],
                parent_evaluation_ids=[item[1] for item in prior],
                parent_frontier_item=frontier,
                prior_refinement=prior_refinement,
                failed_attempt=failed_package,
                body_candidate_id=body["candidate_id"],
                body_definition_id=body["definition_id"],
                bundle_id=bundle["candidate_id"],
                bundle_definition_id=bundle["definition_id"],
                load_case="normal",
                load_mass_kg=base_request["load_mass_kg"],
                load_basis=base_request["load_basis"],
                mesh_m=MESH_M,
                element_kind=ELEMENT_KIND,
                computational_cell_estimate=estimate,
                computational_cell_budget=CELL_BUDGET,
                expected_solid_elements=EXPECTED_CELLS,
                expected_node_count=EXPECTED_NODES,
                resource_revision=dict(from_memory_mb=OLD_MEMORY_MB,
                                      from_timeout_s=OLD_TIMEOUT_S,
                                      memory_mb=MEMORY_MB,
                                      timeout_s=TIMEOUT_S,
                                      omp_threads=OMP_THREADS,
                                      solver_invocation_limit=1,
                                      retry_count=0),
                solver_path=CCX_PATH,
                solver_sha256=CCX_SHA256,
                source_sha256=source_sha256,
                purpose="resource-only continuation after a retained allocation failure; physical and numerical model fixed",
                **FLAGS)


def _execute_once(raw: str, definition: dict, output: Path) -> dict:
    """Run one pinned CalculiX invocation with the requested larger cap/time."""
    if (MEMORY_MB != 8_192 or TIMEOUT_S != 240 or OMP_THREADS != 1
            or Path(CCX_PATH).is_file() is False or digest(CCX_PATH) != CCX_SHA256):
        raise ValueError("This evaluator permits only its pinned 8 GiB/240 s/OMP=1 resource request")
    cap = _requested_address_space_cap()
    output.mkdir(parents=True)
    (output / "model.inp").write_text(raw)
    (output / "definition.json").write_bytes(encoded(definition))
    tool = dict(ccx_path=CCX_PATH, ccx_sha256=CCX_SHA256,
                requested_memory_mb=MEMORY_MB, RLIMIT_AS_bytes=cap,
                OMP_threads=OMP_THREADS, timeout_s=TIMEOUT_S)
    started = time.monotonic()

    def set_address_space_limit():
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))

    result = dict(execution="tool_error", numerical_validity="unknown",
                  engineering_screen="unknown")
    try:
        proc = subprocess.run([CCX_PATH, "model"], cwd=output,
                              capture_output=True, timeout=TIMEOUT_S,
                              preexec_fn=set_address_space_limit,
                              env={**os.environ, "OMP_NUM_THREADS": str(OMP_THREADS)})
        (output / "stdout.log").write_bytes(proc.stdout)
        (output / "stderr.log").write_bytes(proc.stderr)
        result["returncode"] = proc.returncode
        if proc.returncode == 0:
            result.update(grammar_shell.analyse(definition, output / "model.dat"))
    except subprocess.TimeoutExpired as error:
        (output / "stdout.log").write_bytes(error.stdout or b"")
        (output / "stderr.log").write_bytes(error.stderr or b"")
        result.update(execution="interrupted", reason="bounded native timeout")
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        result["reason"] = str(error)
    result["runtime_s"] = time.monotonic() - started
    result["tool"] = tool
    if digest(CCX_PATH) != CCX_SHA256:
        result.update(execution="tool_error", numerical_validity="unknown",
                      reason="Pinned CalculiX binary changed during execution",
                      ccx_sha256_after=digest(CCX_PATH))
    result["mesh_summary"] = {key: value for key, value in definition.items()
                              if key not in ("nodes", "loads_N", "supports")}
    return result


def _external_integrity(root: Path, parent_result: Path, parent_sha256: str,
                        source_sha256: dict, failed_package: dict) -> None:
    if digest(parent_result) != parent_sha256:
        raise ValueError("Parent campaign result changed during resource revision")
    _checked_hashes(root, source_sha256)
    current = _failed_attempt(root, parent_result, parent_sha256)
    if current != failed_package:
        raise ValueError("Pinned 5 GiB allocation-failure package changed during resource revision")
    if digest(CCX_PATH) != CCX_SHA256:
        raise ValueError("Pinned CalculiX binary changed during resource revision")


def _execution_status_valid(result: dict) -> bool:
    status = result.get("execution")
    returncode = result.get("returncode")
    if returncode is not None and (isinstance(returncode, bool) or not isinstance(returncode, int)):
        return False
    reason = result.get("reason")
    has_diagnostic = isinstance(reason, str) and bool(reason.strip())
    if status == "completed":
        return returncode == 0
    if status == "interrupted":
        return returncode is None and reason == "bounded native timeout"
    if status == "tool_error":
        return (returncode is not None and returncode != 0) or has_diagnostic
    return False


def _valid_existing(folder: Path, request: dict, root: Path,
                    parent_result: Path, parent_sha256: str,
                    failed_package: dict) -> tuple[dict, dict, dict]:
    manifest_path = folder / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError("An incomplete resource-revision package is retained here; it will not be overwritten")
    manifest = json.loads(manifest_path.read_bytes())
    if manifest.get("manifest_id") != identity({k: v for k, v in manifest.items() if k != "manifest_id"}):
        raise ValueError("Existing resource-revision manifest identity differs")
    actual_files = {p.relative_to(folder).as_posix(): digest(p)
                    for p in folder.rglob("*")
                    if p.is_file() and p.relative_to(folder).as_posix()
                    not in ("manifest.json", "report.json")}
    if actual_files != manifest.get("files_sha256"):
        raise ValueError("Existing resource-revision files differ from manifest")
    if json.loads((folder / "request.json").read_bytes()) != request:
        raise ValueError("Existing resource-revision request differs")
    if (manifest.get("schema") != "osr-railway-fine-refinement-resource-manifest/1"
            or manifest.get("source_sha256") != request.get("source_sha256")
            or manifest.get("failed_attempt") != failed_package
            or manifest.get("parent_campaign_id") != request.get("parent_campaign_id")
            or manifest.get("parent_contract_id") != request.get("parent_contract_id")
            or manifest.get("parent_run_id") != request.get("parent_run_id")
            or manifest.get("prior_refinement") != request.get("prior_refinement")
            or any(manifest.get(flag) is not False for flag in FLAGS)):
        raise ValueError("Existing resource-revision manifest context differs from request")
    _external_integrity(root, parent_result, parent_sha256,
                        request["source_sha256"], failed_package)
    result = json.loads((folder / "native" / "result.json").read_bytes())
    report = json.loads((folder / "report.json").read_bytes())
    request_id = identity(request)
    summary = result.get("mesh_summary", {})
    generated = report.get("generated_mesh", {})
    report_core = {k: v for k, v in report.items() if k not in ("report_id", "manifest_id")}
    tool = result.get("tool", {})
    if (result.get("evaluation_id") != identity({k: v for k, v in result.items() if k != "evaluation_id"})
            or manifest.get("request_id") != request_id
            or manifest.get("evaluation_id") != result.get("evaluation_id")
            or manifest.get("parent_campaign_id") != request.get("parent_campaign_id")
            or manifest.get("parent_contract_id") != request.get("parent_contract_id")
            or manifest.get("parent_run_id") != request.get("parent_run_id")
            or manifest.get("parent_result_sha256") != parent_sha256
            or manifest.get("failed_attempt") != failed_package
            or manifest.get("prior_refinement") != request.get("prior_refinement")
            or manifest.get("report_id") != report.get("report_id")
            or result.get("request_id") != request_id
            or result.get("parent_campaign_id") != request.get("parent_campaign_id")
            or result.get("parent_contract_id") != request.get("parent_contract_id")
            or result.get("parent_result_sha256") != parent_sha256
            or result.get("parent_run_id") != request.get("parent_run_id")
            or result.get("failed_attempt") != failed_package
            or result.get("prior_refinement") != request.get("prior_refinement")
            or result.get("candidate_id") != CANDIDATE_ID
            or result.get("definition_id") != DEFINITION_ID
            or result.get("source_sha256") != request.get("source_sha256")
            or tool.get("ccx_path") != CCX_PATH
            or tool.get("ccx_sha256") != CCX_SHA256
            or tool.get("requested_memory_mb") != MEMORY_MB
            or tool.get("timeout_s") != TIMEOUT_S
            or tool.get("OMP_threads") != OMP_THREADS
            or not isinstance(tool.get("RLIMIT_AS_bytes"), int)
            or tool.get("RLIMIT_AS_bytes", 0) <= 0
            or tool.get("RLIMIT_AS_bytes") != MEMORY_MB * 1024**2
            or report.get("request_id") != request_id
            or report.get("schema") != "osr-railway-fine-refinement-resource-report/1"
            or report.get("evaluation_id") != result.get("evaluation_id")
            or report.get("manifest_id") != manifest.get("manifest_id")
            or report.get("report_id") != identity(report_core)
            or report.get("parent_campaign_id") != request.get("parent_campaign_id")
            or report.get("parent_contract_id") != request.get("parent_contract_id")
            or report.get("parent_run_id") != request.get("parent_run_id")
            or report.get("parent_result_sha256") != parent_sha256
            or report.get("source_sha256") != request.get("source_sha256")
            or report.get("failed_attempt") != failed_package
            or report.get("prior_refinement") != request.get("prior_refinement")
            or report.get("resource_only_revision") is not True
            or report.get("physical_identity_changed") is not False
            or report.get("body_candidate_id") != CANDIDATE_ID
            or report.get("body_definition_id") != DEFINITION_ID
            or report.get("bundle_id") != BUNDLE_ID
            or report.get("stress") != result.get("stress_summary")
            or result.get("resource_only_revision") is not True
            or not _execution_status_valid(result)
            or any(report.get(flag) is not False for flag in FLAGS)
            or any(result.get(flag) is not False for flag in FLAGS)
            or generated.get("mesh_m") != MESH_M
            or generated.get("element_kind") != ELEMENT_KIND
            or generated.get("solid_elements") != EXPECTED_CELLS
            or generated.get("element_count") != EXPECTED_CELLS
            or generated.get("node_count") != EXPECTED_NODES
            or generated.get("finite_face_components") != 1
            or summary.get("mesh_m") != MESH_M
            or summary.get("element_kind") != ELEMENT_KIND
            or summary.get("solid_elements") != EXPECTED_CELLS
            or summary.get("node_count") != EXPECTED_NODES
            or summary.get("finite_face_components") != 1
            or summary.get("load_case") != "normal"
            or summary.get("load_mass_kg") != NORMAL_LOAD_KG
            or summary.get("load_basis") != request.get("load_basis")
            or summary.get("candidate_id") != CANDIDATE_ID
            or summary.get("definition_id") != DEFINITION_ID):
        raise ValueError("Existing resource-revision result/report/manifest differs from request")
    candidate = json.loads((folder / "native" / "candidate.json").read_bytes())
    if candidate.get("candidate_id") != CANDIDATE_ID or candidate.get("definition_id") != DEFINITION_ID:
        raise ValueError("Existing resource-revision candidate differs from request")
    return result, report, manifest


def run(root=ROOT, *, parent_result: Path, candidate_id: str) -> dict:
    """Run one 8 GiB/240 s resource revision after verifying the retained failure."""
    context = _context(Path(root).resolve(), Path(parent_result).resolve(), candidate_id)
    (root, parent_result, parent, body, bundle, frontier, prior,
     parent_sha256, prior_refinement, failed_package, source_sha256) = context
    estimate = railway_native.cell_estimate(body, MESH_M)
    if not estimate or estimate.get("solid_cells") != EXPECTED_CELLS:
        raise ValueError("Exact fine-mesh cell preflight differs from 128,382 occupied cells")
    if estimate["solid_cells"] > CELL_BUDGET:
        raise ValueError("Fine-mesh case exceeds its 140,000-cell computational ceiling")
    _requested_address_space_cap()
    request = _request(parent=parent, body=body, bundle=bundle, frontier=frontier,
                       prior=prior, parent_sha256=parent_sha256,
                       prior_refinement=prior_refinement,
                       failed_package=failed_package,
                       source_sha256=source_sha256, estimate=estimate)
    request_id = identity(request)
    folder = root / "build/coupled-railway/refinements" / CANDIDATE_ID / request_id
    if folder.exists():
        result, report, manifest = _valid_existing(
            folder, request, root, parent_result, parent_sha256, failed_package)
        return dict(request_id=request_id, evaluation_id=result["evaluation_id"],
                    manifest_id=manifest["manifest_id"], execution=result.get("execution"),
                    numerical_validity=result.get("numerical_validity"), output=str(folder),
                    reused=True, failure_lineage=report.get("allocation_failure_lineage"), **FLAGS)

    raw, definition, elements = railway_fine_refinement._fine_deck(
        body, bundle, mesh_m=MESH_M)
    if (definition.get("mesh_m") != MESH_M
            or definition.get("element_kind") != ELEMENT_KIND
            or definition.get("finite_face_components") != 1
            or definition.get("solid_elements") != EXPECTED_CELLS
            or definition.get("node_count") != EXPECTED_NODES
            or len(elements) != EXPECTED_CELLS
            or len(definition.get("nodes", {})) != EXPECTED_NODES
            or definition.get("load_case") != "normal"
            or definition.get("load_mass_kg") != NORMAL_LOAD_KG
            or definition.get("load_basis") != request.get("load_basis")):
        raise ValueError("Generated resource-revision mesh/load differs from the fixed preflight")
    generated_mesh = {k: definition[k] for k in (
        "mesh_m", "element_kind", "finite_face_components", "solid_elements", "node_count")}
    generated_mesh["element_count"] = len(elements)
    folder.mkdir(parents=True)
    (folder / "request.json").write_bytes(encoded(request))
    _external_integrity(root, parent_result, parent_sha256,
                        source_sha256, failed_package)
    native_dir = folder / "native"
    result = _execute_once(raw, definition, native_dir)
    _external_integrity(root, parent_result, parent_sha256,
                        source_sha256, failed_package)
    result.update(request_id=request_id,
                  parent_campaign_id=CAMPAIGN_ID,
                  parent_contract_id=CONTRACT_ID,
                  parent_result_sha256=parent_sha256,
                  parent_run_id=parent["run_id"],
                  prior_refinement=prior_refinement,
                  failed_attempt=failed_package,
                  candidate_id=CANDIDATE_ID,
                  definition_id=DEFINITION_ID,
                  source_sha256=source_sha256,
                  resource_only_revision=True,
                  engineering_screen="unknown",
                  missing_gates=grammar_shell.MISSING,
                  **FLAGS)
    if result.get("execution") == "completed":
        stress = railway_refinement._stress_summary(native_dir / "model.dat", elements)
    else:
        stress = dict(status="unavailable", reason="Native resource-revision execution did not complete",
                      metric="Cauchy von Mises stress", unit="Pa", physical_allowable=None)
    result["stress_summary"] = stress
    result["evaluation_id"] = identity(result)
    (native_dir / "candidate.json").write_bytes(encoded(body))
    (native_dir / "result.json").write_bytes(encoded(result))

    prior_refinement_folder = (root / "build/coupled-railway/refinements"
                               / CANDIDATE_ID / PREVIOUS_REQUEST_ID)
    prior_fine_result = json.loads((prior_refinement_folder / "native" / "result.json").read_bytes())
    if result.get("execution") == "completed":
        if prior_fine_result.get("execution") == "completed":
            displacement = railway_fine_refinement._matched_point_delta(
                prior_refinement_folder / "native", native_dir)
        else:
            displacement = dict(status="unavailable", matched_point_count=0,
                                reason="The preserved 5 GiB mesh run failed during factorization")
    else:
        displacement = dict(status="unavailable", matched_point_count=0,
                            reason="The 8 GiB resource revision did not complete")
    trend = []
    for mesh, evaluation_id, _raw, _request, previous in prior:
        trend.append(dict(mesh_m=mesh, evaluation_id=evaluation_id,
                          maximum_displacements=previous.get("maximum_displacements"),
                          external_work_J=previous.get("external_work_J"),
                          native_internal_energy_J=previous.get("native_internal_energy_J"),
                          energy_relative_residual=previous.get("energy_relative_residual"),
                          force_relative_residual=previous.get("force_relative_residual"),
                          moment_relative_residual=previous.get("moment_relative_residual")))
    trend.append(dict(mesh_m=railway_fine_refinement.PREVIOUS_MESH_M,
                      evaluation_id=prior_fine_result["evaluation_id"],
                      resource_attempt="5 GiB/150 s predecessor refinement",
                      execution=prior_fine_result.get("execution"),
                      maximum_displacements=prior_fine_result.get("maximum_displacements"),
                      external_work_J=prior_fine_result.get("external_work_J"),
                      native_internal_energy_J=prior_fine_result.get("native_internal_energy_J"),
                      energy_relative_residual=prior_fine_result.get("energy_relative_residual"),
                      force_relative_residual=prior_fine_result.get("force_relative_residual"),
                      moment_relative_residual=prior_fine_result.get("moment_relative_residual")))
    trend.append(dict(mesh_m=MESH_M, evaluation_id=FAILED_EVALUATION_ID,
                      resource_attempt="5 GiB/150 s", execution="tool_error",
                      returncode=255, failure_class=FAILURE_CLASS,
                      maximum_displacements=None, energy_relative_residual=None,
                      force_relative_residual=None, moment_relative_residual=None))
    trend.append(dict(mesh_m=MESH_M, evaluation_id=result["evaluation_id"],
                      resource_attempt="8 GiB/240 s", execution=result.get("execution"),
                      returncode=result.get("returncode"),
                      maximum_displacements=result.get("maximum_displacements"),
                      external_work_J=result.get("external_work_J"),
                      native_internal_energy_J=result.get("native_internal_energy_J"),
                      energy_relative_residual=result.get("energy_relative_residual"),
                      force_relative_residual=result.get("force_relative_residual"),
                      moment_relative_residual=result.get("moment_relative_residual")))
    report = dict(schema="osr-railway-fine-refinement-resource-report/1",
                  request_id=request_id,
                  evaluation_id=result["evaluation_id"],
                  parent_campaign_id=CAMPAIGN_ID,
                  parent_contract_id=CONTRACT_ID,
                  parent_run_id=parent["run_id"],
                  parent_result_sha256=parent_sha256,
                  source_sha256=source_sha256,
                  prior_refinement=prior_refinement,
                  failed_attempt=failed_package,
                  allocation_failure_lineage=dict(
                      prior_request_id=FAILED_REQUEST_ID,
                      prior_evaluation_id=FAILED_EVALUATION_ID,
                      prior_manifest_id=FAILED_MANIFEST_ID,
                      failure_class=FAILURE_CLASS,
                      returncode=255,
                      previous_memory_mb=OLD_MEMORY_MB,
                      revised_memory_mb=MEMORY_MB,
                      previous_timeout_s=OLD_TIMEOUT_S,
                      revised_timeout_s=TIMEOUT_S,
                      physical_or_numerical_model_changed=False),
                  body_candidate_id=CANDIDATE_ID,
                  body_definition_id=DEFINITION_ID,
                  bundle_id=BUNDLE_ID,
                  resource_only_revision=True,
                  physical_identity_changed=False,
                  generated_mesh=generated_mesh,
                  mesh_and_equilibrium_residual_trend=trend,
                  matched_point_displacement_comparison=dict(
                      from_mesh_m=railway_fine_refinement.PREVIOUS_MESH_M,
                      to_mesh_m=MESH_M, **displacement),
                  stress=stress,
                  stress_interpretation="Unqualified C3D8I ideal-joint Cauchy stress diagnostic only; no allowable or qualification meaning",
                  engineering_acceptance=False,
                  physical_acceptance=False,
                  interpretation="Resource-only evaluation of the same physical and numerical case; numerical completion does not establish engineering or physical acceptance.",
                  **FLAGS)
    report_id = identity(report)
    _external_integrity(root, parent_result, parent_sha256,
                        source_sha256, failed_package)
    files = {p.relative_to(folder).as_posix(): digest(p)
             for p in folder.rglob("*")
             if p.is_file() and p.relative_to(folder).as_posix()
             not in ("manifest.json", "report.json")}
    _external_integrity(root, parent_result, parent_sha256,
                        source_sha256, failed_package)
    manifest = dict(schema="osr-railway-fine-refinement-resource-manifest/1",
                    request_id=request_id,
                    evaluation_id=result["evaluation_id"],
                    parent_campaign_id=CAMPAIGN_ID,
                    parent_contract_id=CONTRACT_ID,
                    parent_run_id=parent["run_id"],
                    parent_result_sha256=parent_sha256,
                    prior_refinement=prior_refinement,
                    failed_attempt=failed_package,
                    source_sha256=source_sha256,
                    report_id=report_id,
                    files_sha256=files,
                    **FLAGS)
    manifest["manifest_id"] = identity(manifest)
    report["report_id"] = report_id
    report["manifest_id"] = manifest["manifest_id"]
    (folder / "report.json").write_bytes(encoded(report))
    _external_integrity(root, parent_result, parent_sha256,
                        source_sha256, failed_package)
    (folder / "manifest.json").write_bytes(encoded(manifest))
    return dict(request_id=request_id,
                evaluation_id=result["evaluation_id"],
                manifest_id=manifest["manifest_id"],
                failed_request_id=FAILED_REQUEST_ID,
                failed_evaluation_id=FAILED_EVALUATION_ID,
                execution=result.get("execution"),
                numerical_validity=result.get("numerical_validity"),
                output=str(folder), reused=False,
                allocation_failure_lineage=report["allocation_failure_lineage"],
                **FLAGS)


def verify(root=ROOT, *, parent_result: Path, candidate_id: str) -> dict:
    """Verify the immutable resource-revision package without executing a solver."""
    context = _context(Path(root).resolve(), Path(parent_result).resolve(), candidate_id)
    (root, parent_result, parent, body, bundle, frontier, prior,
     parent_sha256, prior_refinement, failed_package, source_sha256) = context
    estimate = railway_native.cell_estimate(body, MESH_M)
    if not estimate or estimate.get("solid_cells") != EXPECTED_CELLS:
        raise ValueError("Exact fine-mesh cell preflight differs from 128,382 occupied cells")
    request = _request(parent=parent, body=body, bundle=bundle, frontier=frontier,
                       prior=prior, parent_sha256=parent_sha256,
                       prior_refinement=prior_refinement,
                       failed_package=failed_package,
                       source_sha256=source_sha256, estimate=estimate)
    request_id = identity(request)
    folder = root / "build/coupled-railway/refinements" / CANDIDATE_ID / request_id
    result, report, manifest = _valid_existing(
        folder, request, root, parent_result, parent_sha256, failed_package)
    return dict(verified=True,
                request_id=request_id,
                evaluation_id=result["evaluation_id"],
                manifest_id=manifest["manifest_id"],
                failed_request_id=FAILED_REQUEST_ID,
                failed_evaluation_id=FAILED_EVALUATION_ID,
                failed_manifest_id=FAILED_MANIFEST_ID,
                execution=result.get("execution"),
                numerical_validity=result.get("numerical_validity"),
                allocation_failure_lineage=report.get("allocation_failure_lineage"),
                output=str(folder), **FLAGS)
