"""Seal and verify artifacts for the already-completed 0.10625 m resource run.

This module only reconciles saved solver outputs. It never dispatches or retries
CalculiX and preserves the fixed candidate and resource-revision identities.
"""
from __future__ import annotations

import json
import math
import os
import tempfile
from pathlib import Path

from engineering.station_rail import ROOT, FLAGS
from engineering.station_rail.common import digest, encoded, identity
from . import railway_fine_refinement_resource as resource
from . import grammar_shell, railway_native, railway_refinement

PRODUCER = "engineering/design_search/railway_fine_refinement_recovery.py"
EXPECTED_REQUEST_ID = "e8a5a9c6d836cb5f20425a46f04ecac21f107952bec25559e5650e69a865cd7e"
EXPECTED_EVALUATION_ID = "bd0566331853171bac52b8107e075cd4c997526735af7ede9bbcc3fc3ebca9ea"
EXPECTED_PARENT_RESULT_SHA256 = "6ca007290089bda577bac8c2dd75802c231c4eb4bc9ec4d07153f15dc737c3e9"
EXPECTED_RUNTIME_S = 89.4248315119994


def _postprocessing_source_sha256(root: Path) -> dict[str, str]:
    local_path = Path(__file__).resolve()
    source_hash = digest(local_path)
    integrated_copy = (root / PRODUCER).resolve()
    if integrated_copy.is_file() and digest(integrated_copy) != source_hash:
        raise ValueError("Recovery postprocessor source differs from the integrated source copy")
    return {PRODUCER: source_hash}


def _reconstruct(root: Path, parent_result: Path, candidate_id: str):
    root = root.resolve()
    parent_result = parent_result.resolve()
    context = resource._context(root, parent_result, candidate_id)
    (root, parent_result, parent, body, bundle, frontier, prior,
     parent_sha256, prior_refinement, failed_package, source_sha256) = context
    estimate = railway_native.cell_estimate(body, resource.MESH_M)
    if not estimate or estimate.get("solid_cells") != resource.EXPECTED_CELLS:
        raise ValueError("Reconstructed request has a different exact fine-mesh cell estimate")
    request = resource._request(
        parent=parent, body=body, bundle=bundle, frontier=frontier, prior=prior,
        parent_sha256=parent_sha256, prior_refinement=prior_refinement,
        failed_package=failed_package, source_sha256=source_sha256, estimate=estimate)
    request_id = identity(request)
    if (request_id != EXPECTED_REQUEST_ID
            or parent_sha256 != EXPECTED_PARENT_RESULT_SHA256
            or parent.get("campaign_id") != resource.CAMPAIGN_ID
            or parent.get("contract_id") != resource.CONTRACT_ID
            or body.get("candidate_id") != resource.CANDIDATE_ID
            or body.get("definition_id") != resource.DEFINITION_ID
            or bundle.get("candidate_id") != resource.BUNDLE_ID):
        raise ValueError("Reconstructed request, parent, candidate or bundle differs from the sealed solver run")
    folder = root / "build/coupled-railway/refinements" / resource.CANDIDATE_ID / request_id
    return (root, parent_result, parent, body, bundle, prior, parent_sha256,
            prior_refinement, failed_package, source_sha256, estimate,
            request, request_id, folder)


def _verify_frd_mesh(path: Path, definition: dict, elements: list) -> None:
    """Cross-check FRD node coordinates and brick connectivity against inputs."""
    expected_nodes = {int(node_id): tuple(float(x) for x in xyz)
                      for node_id, xyz in definition["nodes"].items()}
    expected_elements = {int(element["id"]): tuple(int(n) for n in element["nodes"])
                         for element in elements}
    state = "scan"
    node_header_count = element_header_count = None
    seen_nodes = set()
    seen_elements = set()
    pending_element = None
    for line_number, line in enumerate(path.open(errors="replace"), 1):
        stripped = line.lstrip()
        fields = stripped.split()
        if not fields:
            continue
        tag = fields[0]
        if state == "scan":
            if tag == "2C":
                if len(fields) < 2:
                    raise ValueError("FRD node header lacks a declared count")
                node_header_count = int(fields[1])
                state = "nodes"
        elif state == "nodes":
            if tag == "-3":
                if node_header_count != resource.EXPECTED_NODES or len(seen_nodes) != node_header_count:
                    raise ValueError("FRD node record count differs from the regenerated mesh")
                state = "seek-elements"
            elif tag == "-1":
                if len(line.rstrip("\r\n")) < 49:
                    raise ValueError(f"Malformed FRD node record at line {line_number}")
                node_id = int(line[3:13])
                if node_id in seen_nodes or node_id not in expected_nodes:
                    raise ValueError(f"Unexpected or duplicate FRD node id {node_id}")
                coordinate_fields = (line[13:25], line[25:37], line[37:49])
                saved = tuple(float(value.replace("D", "E").replace("d", "e"))
                              for value in coordinate_fields)
                expected = expected_nodes[node_id]
                for actual, target, token in zip(saved, expected, coordinate_fields):
                    exponent_text = token.strip().replace("D", "E").replace("d", "e").split("e")[-1]
                    precision = len(token.strip().lower().split("e")[0].split(".")[-1])
                    rounding_tolerance = 0.5 * (10.0 ** (int(exponent_text) - precision))
                    if not math.isfinite(actual) or abs(actual - target) > max(rounding_tolerance, 1e-12):
                        raise ValueError(f"FRD coordinate for node {node_id} differs from the regenerated mesh")
                seen_nodes.add(node_id)
        elif state == "seek-elements":
            if tag == "3C":
                if len(fields) < 2:
                    raise ValueError("FRD element header lacks a declared count")
                element_header_count = int(fields[1])
                state = "elements"
        elif state == "elements":
            if tag == "-3":
                if (pending_element is not None
                        or element_header_count != resource.EXPECTED_CELLS
                        or len(seen_elements) != element_header_count
                        or seen_elements != set(expected_elements)):
                    raise ValueError("FRD element records differ from the regenerated mesh")
                return
            if tag == "-1":
                if len(line.rstrip("\r\n")) < 13 or pending_element is not None:
                    raise ValueError(f"Malformed FRD element header at line {line_number}")
                pending_element = int(line[3:13])
                if pending_element in seen_elements or pending_element not in expected_elements:
                    raise ValueError(f"Unexpected or duplicate FRD element id {pending_element}")
            elif tag == "-2":
                if pending_element is None:
                    raise ValueError(f"FRD connectivity without element header at line {line_number}")
                if len(line.rstrip("\r\n")) < 83:
                    raise ValueError(f"Incomplete FRD brick connectivity at line {line_number}")
                connectivity = tuple(int(line[start:start + 10]) for start in range(3, 83, 10))
                if connectivity != expected_elements[pending_element]:
                    raise ValueError(f"FRD connectivity for element {pending_element} differs from the generated mesh")
                seen_elements.add(pending_element)
                pending_element = None
    raise ValueError("FRD mesh section ended before all node and element records were validated")


def _solver_packet(folder: Path, request: dict, body: dict, bundle: dict) -> tuple[dict, dict, list]:
    request_path = folder / "request.json"
    native = folder / "native"
    result_path = native / "result.json"
    for path in (request_path, result_path, native / "model.inp", native / "definition.json",
                 native / "candidate.json", native / "model.dat", native / "model.frd", native / "model.sta",
                 native / "stdout.log", native / "stderr.log"):
        if not path.is_file():
            raise ValueError(f"Completed solver package is missing {path.relative_to(folder)}")
    saved_request = json.loads(request_path.read_bytes())
    result = json.loads(result_path.read_bytes())
    if saved_request != request:
        raise ValueError("Saved request differs from the reconstructed immutable request")
    result_id = result.get("evaluation_id")
    if (result_id != EXPECTED_EVALUATION_ID
            or result_id != identity({k: v for k, v in result.items() if k != "evaluation_id"})
            or result.get("execution") != "completed"
            or type(result.get("returncode")) is not int
            or result.get("returncode") != 0
            or result.get("numerical_validity") != "equilibrium_energy_confirmed_only"
            or result.get("request_id") != EXPECTED_REQUEST_ID
            or result.get("parent_campaign_id") != resource.CAMPAIGN_ID
            or result.get("parent_contract_id") != resource.CONTRACT_ID
            or result.get("parent_result_sha256") != request.get("parent_result_sha256")
            or result.get("parent_run_id") != request.get("parent_run_id")
            or result.get("prior_refinement") != request.get("prior_refinement")
            or result.get("failed_attempt") != request.get("failed_attempt")
            or result.get("candidate_id") != resource.CANDIDATE_ID
            or result.get("definition_id") != resource.DEFINITION_ID
            or result.get("source_sha256") != request.get("source_sha256")
            or result.get("resource_only_revision") is not True
            or any(result.get(flag) is not False for flag in FLAGS)):
        raise ValueError("Saved result identity/status/candidate context differs from the completed solver run")
    runtime = result.get("runtime_s")
    if not isinstance(runtime, (int, float)) or abs(runtime - EXPECTED_RUNTIME_S) > 1e-6:
        raise ValueError("Saved solver runtime differs from the identified completed run")
    tool = result.get("tool", {})
    expected_tool = dict(ccx_path=resource.CCX_PATH,
                         ccx_sha256=resource.CCX_SHA256,
                         requested_memory_mb=resource.MEMORY_MB,
                         RLIMIT_AS_bytes=resource.MEMORY_MB * 1024**2,
                         OMP_threads=resource.OMP_THREADS,
                         timeout_s=resource.TIMEOUT_S)
    if tool != expected_tool:
        raise ValueError("Saved solver tool/resource identity differs from the request")
    if digest(resource.CCX_PATH) != resource.CCX_SHA256:
        raise ValueError("Pinned CalculiX binary differs from the completed run")

    summary = result.get("mesh_summary", {})
    expected_summary = dict(mesh_m=resource.MESH_M,
                            element_kind="C3D8I",
                            solid_elements=resource.EXPECTED_CELLS,
                            node_count=resource.EXPECTED_NODES,
                            finite_face_components=1,
                            load_case="normal",
                            load_mass_kg=resource.NORMAL_LOAD_KG,
                            load_basis=request.get("load_basis"),
                            candidate_id=resource.CANDIDATE_ID,
                            definition_id=resource.DEFINITION_ID)
    for key, value in expected_summary.items():
        if summary.get(key) != value:
            raise ValueError(f"Saved mesh/load summary differs for {key}")
    if not isinstance(result.get("stress_summary"), dict):
        raise ValueError("Saved stress summary is missing")

    candidate = json.loads((native / "candidate.json").read_bytes())
    if (candidate.get("candidate_id") != resource.CANDIDATE_ID
            or candidate.get("definition_id") != resource.DEFINITION_ID
            or candidate != body):
        raise ValueError("Saved candidate packet differs from the source-bound body definition")
    # Regenerate only the deterministic input deck; this does not invoke a solver.
    raw, definition, elements = resource.railway_fine_refinement._fine_deck(
        body, bundle, mesh_m=resource.MESH_M)
    saved_definition = json.loads((native / "definition.json").read_bytes())
    if ((native / "model.inp").read_text() != raw
            or saved_definition != json.loads(encoded(definition))
            or len(elements) != resource.EXPECTED_CELLS
            or len(definition.get("nodes", {})) != resource.EXPECTED_NODES
            or definition.get("finite_face_components") != 1):
        raise ValueError("Saved solver input/definition differs from the deterministic source-bound mesh")
    _verify_frd_mesh(native / "model.frd", definition, elements)
    model_dat = native / "model.dat"
    recomputed = grammar_shell.analyse(definition, model_dat)
    for key, value in recomputed.items():
        if result.get(key) != value:
            raise ValueError(f"Saved solver result differs from model.dat analysis for {key}")
    recomputed_stress = railway_refinement._stress_summary(model_dat, elements)
    if result.get("stress_summary") != recomputed_stress:
        raise ValueError("Saved stress summary differs from the model.dat integration-point records")
    return result, definition, elements


def _report(context: tuple, result: dict, definition: dict, elements: list,
            request: dict, request_id: str, recovery_sha256: dict) -> dict:
    (root, parent_result, parent, body, bundle, prior, parent_sha256,
     prior_refinement, failed_package, source_sha256, _estimate, _request,
     _request_id, folder) = context
    prior_folder = (root / "build/coupled-railway/refinements" / resource.CANDIDATE_ID
                    / resource.PREVIOUS_REQUEST_ID)
    prior_result = json.loads((prior_folder / "native" / "result.json").read_bytes())
    if (prior_result.get("evaluation_id") != resource.PREVIOUS_EVALUATION_ID
            or prior_result.get("execution") != "completed"):
        raise ValueError("Verified 0.2125 m predecessor result is not complete")
    displacement = railway_refinement._matched_point_delta(prior_folder / "native", folder / "native")
    if displacement.get("status") != "compared":
        raise ValueError("Matched-point displacement comparison from 0.2125 m is unavailable")
    stress = result.get("stress_summary")
    trend = []
    for mesh, evaluation_id, _raw, _prior_request, previous in prior:
        trend.append(dict(mesh_m=mesh, evaluation_id=evaluation_id,
                          maximum_displacements=previous.get("maximum_displacements"),
                          external_work_J=previous.get("external_work_J"),
                          native_internal_energy_J=previous.get("native_internal_energy_J"),
                          energy_relative_residual=previous.get("energy_relative_residual"),
                          force_relative_residual=previous.get("force_relative_residual"),
                          moment_relative_residual=previous.get("moment_relative_residual")))
    trend.append(dict(mesh_m=resource.railway_fine_refinement.PREVIOUS_MESH_M,
                      evaluation_id=prior_result["evaluation_id"],
                      maximum_displacements=prior_result.get("maximum_displacements"),
                      external_work_J=prior_result.get("external_work_J"),
                      native_internal_energy_J=prior_result.get("native_internal_energy_J"),
                      energy_relative_residual=prior_result.get("energy_relative_residual"),
                      force_relative_residual=prior_result.get("force_relative_residual"),
                      moment_relative_residual=prior_result.get("moment_relative_residual"),
                      stress_status=prior_result.get("stress_summary", {}).get("status")))
    trend.append(dict(mesh_m=resource.MESH_M, evaluation_id=resource.FAILED_EVALUATION_ID,
                      resource_attempt="5 GiB/150 s", execution="tool_error", returncode=255,
                      failure_class=resource.FAILURE_CLASS,
                      maximum_displacements=None, energy_relative_residual=None,
                      force_relative_residual=None, moment_relative_residual=None))
    trend.append(dict(mesh_m=resource.MESH_M, evaluation_id=result["evaluation_id"],
                      resource_attempt="8 GiB/240 s", execution=result["execution"],
                      returncode=result["returncode"],
                      maximum_displacements=result.get("maximum_displacements"),
                      external_work_J=result.get("external_work_J"),
                      native_internal_energy_J=result.get("native_internal_energy_J"),
                      energy_relative_residual=result.get("energy_relative_residual"),
                      force_relative_residual=result.get("force_relative_residual"),
                      moment_relative_residual=result.get("moment_relative_residual"),
                      stress_status=stress.get("status") if isinstance(stress, dict) else "unavailable"))
    return dict(schema="osr-railway-fine-refinement-resource-report/1",
                request_id=request_id,
                evaluation_id=result["evaluation_id"],
                parent_campaign_id=resource.CAMPAIGN_ID,
                parent_contract_id=resource.CONTRACT_ID,
                parent_run_id=parent["run_id"],
                parent_result_sha256=parent_sha256,
                source_sha256=source_sha256,
                postprocessing_source_sha256=recovery_sha256,
                prior_refinement=prior_refinement,
                failed_attempt=failed_package,
                allocation_failure_lineage=dict(
                    prior_request_id=resource.FAILED_REQUEST_ID,
                    prior_evaluation_id=resource.FAILED_EVALUATION_ID,
                    prior_manifest_id=resource.FAILED_MANIFEST_ID,
                    failure_class=resource.FAILURE_CLASS,
                    returncode=255,
                    previous_memory_mb=resource.OLD_MEMORY_MB,
                    revised_memory_mb=resource.MEMORY_MB,
                    previous_timeout_s=resource.OLD_TIMEOUT_S,
                    revised_timeout_s=resource.TIMEOUT_S,
                    physical_or_numerical_model_changed=False),
                body_candidate_id=resource.CANDIDATE_ID,
                body_definition_id=resource.DEFINITION_ID,
                bundle_id=resource.BUNDLE_ID,
                resource_only_revision=True,
                physical_identity_changed=False,
                generated_mesh=dict(mesh_m=definition["mesh_m"],
                                    element_kind=definition["element_kind"],
                                    finite_face_components=definition["finite_face_components"],
                                    solid_elements=definition["solid_elements"],
                                    element_count=len(elements),
                                    node_count=definition["node_count"]),
                mesh_and_equilibrium_residual_trend=trend,
                matched_point_displacement_comparison=dict(
                    from_mesh_m=resource.railway_fine_refinement.PREVIOUS_MESH_M,
                    to_mesh_m=resource.MESH_M, **displacement),
                matched_point_displacement_source="model.dat nodal displacement records parsed by grammar_shell._read; model.frd is checked for mesh records only",
                stress=stress,
                stress_interpretation="Unqualified C3D8I ideal-joint Cauchy stress diagnostic only; no allowable or qualification meaning",
                engineering_acceptance=False,
                physical_acceptance=False,
                interpretation="Resource-only evaluation of the same physical and numerical case; numerical completion does not establish engineering or physical acceptance.",
                **FLAGS)


def _seal_manifest(folder: Path, request: dict, result: dict, report: dict,
                   parent: dict, failed_package: dict, recovery_sha256: dict) -> dict:
    report_id = identity(report)
    files = {path.relative_to(folder).as_posix(): digest(path)
             for path in folder.rglob("*")
             if path.is_file() and path.relative_to(folder).as_posix()
             not in ("manifest.json", "report.json")}
    manifest = dict(schema="osr-railway-fine-refinement-resource-manifest/1",
                    request_id=identity(request),
                    evaluation_id=result["evaluation_id"],
                    parent_campaign_id=parent["campaign_id"],
                    parent_contract_id=parent["contract_id"],
                    parent_run_id=parent["run_id"],
                    parent_result_sha256=request["parent_result_sha256"],
                    prior_refinement=request["prior_refinement"],
                    failed_attempt=failed_package,
                    source_sha256=request["source_sha256"],
                    postprocessing_source_sha256=recovery_sha256,
                    report_id=report_id,
                    files_sha256=files,
                    **FLAGS)
    manifest["manifest_id"] = identity(manifest)
    report["report_id"] = report_id
    report["manifest_id"] = manifest["manifest_id"]
    return manifest


def _expected_seal(context: tuple, result: dict, definition: dict, elements: list,
                   request: dict, request_id: str, recovery_sha256: dict) -> tuple[dict, dict]:
    _root, _parent_result, parent, _body, _bundle, _prior, _parent_sha256, _prior_refinement, failed_package, _source_sha256, _estimate, _request, _request_id, folder = context
    report = _report(context, result, definition, elements,
                     request, request_id, recovery_sha256)
    manifest = _seal_manifest(folder, request, result, report,
                              parent, failed_package, recovery_sha256)
    return report, manifest


def _source_mapping(value) -> bool:
    return (isinstance(value, dict) and set(value) == {PRODUCER}
            and isinstance(value[PRODUCER], str) and len(value[PRODUCER]) == 64
            and all(ch in "0123456789abcdef" for ch in value[PRODUCER]))


def _write_seal_pair(folder: Path, report: dict, manifest: dict) -> None:
    """Atomically stage each replacement outside the sealed request folder."""
    staged = []
    try:
        for name, value in (("report.json", report), ("manifest.json", manifest)):
            fd, temp_name = tempfile.mkstemp(prefix=".recovery-", suffix=".tmp", dir=folder.parent)
            staged.append((Path(temp_name), folder / name))
            with os.fdopen(fd, "wb") as stream:
                stream.write(encoded(value))
                stream.flush()
                os.fsync(stream.fileno())
        for temporary, destination in staged:
            os.replace(temporary, destination)
    finally:
        for temporary, _destination in staged:
            temporary.unlink(missing_ok=True)


def reconcile(root=ROOT, *, parent_result: Path, candidate_id: str) -> dict:
    """Recover the missing report and manifest for the saved completed run."""
    context = _reconstruct(Path(root), Path(parent_result), candidate_id)
    (root, parent_result, parent, body, bundle, prior, parent_sha256,
     prior_refinement, failed_package, source_sha256, estimate, request,
     request_id, folder) = context
    if request_id != EXPECTED_REQUEST_ID:
        raise ValueError("Recovery is limited to the known completed resource request")
    recovery_sha256 = _postprocessing_source_sha256(root)
    report_path, manifest_path = folder / "report.json", folder / "manifest.json"
    if report_path.exists() and manifest_path.exists():
        # First establish that the old seal and all raw solver files are intact.
        old_verified = resource.verify(root, parent_result=parent_result,
                                       candidate_id=candidate_id)
        if (old_verified.get("verified") is not True
                or old_verified.get("request_id") != EXPECTED_REQUEST_ID
                or old_verified.get("evaluation_id") != EXPECTED_EVALUATION_ID):
            raise ValueError("Existing recovery seal does not pass the resource verifier")
        old_report = json.loads(report_path.read_bytes())
        old_manifest = json.loads(manifest_path.read_bytes())
        old_report_source = old_report.get("postprocessing_source_sha256")
        old_manifest_source = old_manifest.get("postprocessing_source_sha256")
        if (not _source_mapping(old_report_source)
                or old_report_source != old_manifest_source):
            raise ValueError("Existing seal is partial, malformed or belongs to another postprocessor")
        if old_report_source == recovery_sha256:
            verified = verify(root, parent_result=parent_result, candidate_id=candidate_id)
            return {**verified, "reused": True}
        # Stale-source reseal is allowed only after the old resource seal and
        # raw hashes validate, and both old maps identify this same producer.
        result, definition, elements = _solver_packet(folder, request, body, bundle)
        resource._external_integrity(root, parent_result, parent_sha256,
                                     source_sha256, failed_package)
        if recovery_sha256 != _postprocessing_source_sha256(root):
            raise ValueError("Recovery source changed while preparing a replacement seal")
        report, manifest = _expected_seal(
            context, result, definition, elements, request, request_id, recovery_sha256)
        _write_seal_pair(folder, report, manifest)
        return verify(root, parent_result=parent_result, candidate_id=candidate_id)
    if report_path.exists() != manifest_path.exists():
        raise ValueError("Partial report/manifest seal exists; recovery will not overwrite it")
    if not folder.is_dir():
        raise ValueError("Expected completed solver output folder is missing")
    result, definition, elements = _solver_packet(folder, request, body, bundle)
    # The request is source-bound to the original 8 GiB evaluator. Confirm its
    # inputs and parent artifacts again before creating any seal files.
    resource._external_integrity(root, parent_result, parent_sha256,
                                 source_sha256, failed_package)
    if recovery_sha256 != _postprocessing_source_sha256(root):
        raise ValueError("Recovery source changed while reconciling the solver packet")
    report, manifest = _expected_seal(
        context, result, definition, elements, request, request_id, recovery_sha256)
    if report_path.exists() or manifest_path.exists():
        raise ValueError("A report or manifest appeared during recovery; no files were overwritten")
    _write_seal_pair(folder, report, manifest)
    return verify(root, parent_result=parent_result, candidate_id=candidate_id)


def verify(root=ROOT, *, parent_result: Path, candidate_id: str) -> dict:
    """Verify the sealed package with the original resource evaluator."""
    context = _reconstruct(Path(root), Path(parent_result), candidate_id)
    (root, parent_result, parent, body, bundle, _prior, parent_sha256,
     _prior_refinement, failed_package, source_sha256, _estimate,
     request, request_id, folder) = context
    if request_id != EXPECTED_REQUEST_ID:
        raise ValueError("Recovery verifier reconstructed an unexpected request")
    report_path, manifest_path = folder / "report.json", folder / "manifest.json"
    if not report_path.is_file() or not manifest_path.is_file():
        raise ValueError("Recovery report and manifest must both be sealed")
    recovery_sha256 = _postprocessing_source_sha256(root)
    report = json.loads(report_path.read_bytes())
    manifest = json.loads(manifest_path.read_bytes())
    verified = resource.verify(root, parent_result=parent_result, candidate_id=candidate_id)
    if (verified.get("verified") is not True
            or verified.get("request_id") != EXPECTED_REQUEST_ID
            or verified.get("evaluation_id") != EXPECTED_EVALUATION_ID):
        raise ValueError("Original resource evaluator did not verify the recovered package")
    if (report.get("postprocessing_source_sha256") != recovery_sha256
            or manifest.get("postprocessing_source_sha256") != recovery_sha256
            or report.get("request_id") != EXPECTED_REQUEST_ID
            or report.get("evaluation_id") != EXPECTED_EVALUATION_ID
            or report.get("manifest_id") != manifest.get("manifest_id")):
        raise ValueError("Postprocessing source or recovery identity differs from the sealed package")
    result, definition, elements = _solver_packet(folder, request, body, bundle)
    expected_report, expected_manifest = _expected_seal(
        context, result, definition, elements, request, request_id, recovery_sha256)
    if report != expected_report or manifest != expected_manifest:
        raise ValueError("Sealed report or manifest differs from recomputed solver evidence")
    resource._external_integrity(root, parent_result, parent_sha256,
                                 source_sha256, failed_package)
    if recovery_sha256 != _postprocessing_source_sha256(root):
        raise ValueError("Recovery source changed during verification")
    return dict(**verified, postprocessing_source_sha256=recovery_sha256,
                report_id=report.get("report_id"))
