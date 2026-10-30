"""One bounded follow-on C3D8I mesh refinement for the coupled railway body.

This evaluator holds the physical candidate, materials, interfaces, supports,
bundle, normal load and solver method fixed. Its outputs are numerical evidence
for the declared idealized model only; they cannot qualify or accept a body.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from engineering.station_rail import ROOT, FLAGS
from engineering.station_rail.common import digest, encoded, identity
from . import grammar_shell, railway_campaign, railway_native, railway_refinement

PRODUCER = "engineering/design_search/railway_fine_refinement.py"
CAMPAIGN_ID = "6ba19dff09e30606bb4d20ddd153deef033c86ab1d27adc8dab6ad842d68f99f"
CONTRACT_ID = "de9f89acc80e0ec2f3ebb8b6c8f60e2446de9df06c66317c5cedc5b8625f8921"
CANDIDATE_ID = "8db92b830fda54c81ec231c541f811b24f938f2471b559448d2ed2683754f78b"
DEFINITION_ID = "21efbaf935ba954a6788d2c54e841b12c891a01b70afef4f7a2edd581af5458f"
BUNDLE_ID = "1e8d1d7c394fc0bdbd47e34fb21d413ebc34a49576bad60b31b254bd635dfb68"
PREVIOUS_REQUEST_ID = "9130f2d637a8da4e7b687e6548508c4a8d1b05e42f6d0c5bf0cf350b814e47a1"
PREVIOUS_EVALUATION_ID = "da022c36ff3125f5cab90c2f709a2c29e85381e690dbfa082b03deef52f7ad05"
PREVIOUS_MANIFEST_ID = "69767b20a96bbd6b757f759d74911ea503898f3f9841784bbd60cf1509167e39"
PREVIOUS_MESH_M = 0.2125
NEXT_MESH_M = 0.10625
EXPECTED_CELLS = 128_382
CELL_BUDGET = 140_000
EXPECTED_NODES = 227_190
MEMORY_MB = 5_120
TIMEOUT_S = 150
OMP_THREADS = 1
ELEMENT_KIND = "C3D8I"
NORMAL_LOAD_KG = 10_818.661193648113
CCX_PATH = "/usr/bin/ccx"
CCX_SHA256 = "373f7ef4c118a1b5e1b53041fe4f7ef1f1f854051326e0d3f1eeb890ec34885b"
BODY_EVALUATIONS = {
    0.85: "4bea9935bb7e172a2364ac7fcf5218cabb5ea80d41f60db444bb7de199049cb1",
    0.425: "11a732b32205db4aa4511518ae3fd5aef8763278005dc513263bab203134c810",
}


def _checked_hashes(root: Path, sources: dict[str, str]) -> None:
    root = root.resolve()
    for name, expected in sources.items():
        path = (root / name).resolve()
        if root not in path.parents or not path.is_file() or digest(path) != expected:
            raise ValueError(f"Source identity mismatch: {name}")


def _prior_refinement_package(root: Path, parent_result: Path, parent_sha256: str) -> dict:
    """Verify the pinned 0.2125 m package and return its immutable identity."""
    checked = railway_refinement.verify(
        root, parent_result=parent_result, candidate_id=CANDIDATE_ID)
    if (checked.get("verified") is not True
            or checked.get("request_id") != PREVIOUS_REQUEST_ID
            or checked.get("evaluation_id") != PREVIOUS_EVALUATION_ID
            or checked.get("manifest_id") != PREVIOUS_MANIFEST_ID
            or checked.get("campaign_id") != CAMPAIGN_ID
            or checked.get("candidate_id") != CANDIDATE_ID
            or checked.get("execution") != "completed"):
        raise ValueError("Pinned 0.2125 m parent refinement does not verify as the required completed package")
    folder = (root / "build/coupled-railway/refinements" / CANDIDATE_ID / PREVIOUS_REQUEST_ID).resolve()
    expected_root = (root / "build/coupled-railway/refinements" / CANDIDATE_ID).resolve()
    if expected_root not in folder.parents:
        raise ValueError("Prior refinement package escapes the private refinement tree")
    request_path = folder / "request.json"
    result_path = folder / "native" / "result.json"
    manifest_path = folder / "manifest.json"
    request = json.loads(request_path.read_bytes())
    result = json.loads(result_path.read_bytes())
    manifest = json.loads(manifest_path.read_bytes())
    if (request.get("request_id", PREVIOUS_REQUEST_ID) != PREVIOUS_REQUEST_ID
            or request.get("parent_result_sha256") != parent_sha256
            or request.get("body_candidate_id") != CANDIDATE_ID
            or request.get("body_definition_id") != DEFINITION_ID
            or request.get("bundle_id") != BUNDLE_ID
            or request.get("mesh_m") != PREVIOUS_MESH_M
            or request.get("element_kind") != ELEMENT_KIND
            or request.get("load_case") != "normal"
            or request.get("load_mass_kg") != NORMAL_LOAD_KG
            or result.get("evaluation_id") != PREVIOUS_EVALUATION_ID
            or result.get("execution") != "completed"
            or result.get("candidate_id") != CANDIDATE_ID
            or result.get("definition_id") != DEFINITION_ID
            or manifest.get("manifest_id") != PREVIOUS_MANIFEST_ID):
        raise ValueError("Pinned 0.2125 m refinement request/result/manifest differs from its declared parent")
    files_sha256 = manifest.get("files_sha256")
    if not isinstance(files_sha256, dict):
        raise ValueError("Pinned prior refinement manifest lacks its sealed file hashes")
    package = dict(request_id=PREVIOUS_REQUEST_ID,
                   evaluation_id=PREVIOUS_EVALUATION_ID,
                   manifest_id=PREVIOUS_MANIFEST_ID,
                   request_sha256=digest(request_path),
                   result_sha256=digest(result_path),
                   manifest_sha256=digest(manifest_path),
                   files_sha256=files_sha256)
    package["package_id"] = identity(package)
    return package


def _context(root: Path, parent_result: Path, candidate_id: str):
    root = root.resolve()
    parent_result = parent_result.resolve()
    parent, body, bundle, frontier, prior, parent_sha256 = railway_refinement._verify_parent(
        root, parent_result, candidate_id)
    if (parent.get("campaign_id") != CAMPAIGN_ID
            or parent.get("contract_id") != CONTRACT_ID
            or body.get("candidate_id") != CANDIDATE_ID
            or body.get("definition_id") != DEFINITION_ID
            or bundle.get("candidate_id") != BUNDLE_ID):
        raise ValueError("Parent campaign, candidate, definition or P1 bundle differs from this evaluator")
    base_request = prior[1][3]
    if (base_request.get("load_case") != "normal"
            or base_request.get("element_kind") != ELEMENT_KIND
            or abs(float(base_request.get("load_mass_kg", 0.0)) - NORMAL_LOAD_KG) > 1e-6):
        raise ValueError("Campaign parent does not preserve the declared normal C3D8I load basis")
    prior_package = _prior_refinement_package(root, parent_result, parent_sha256)
    source_sha256 = {
        PRODUCER: digest(root / PRODUCER),
        railway_refinement.PRODUCER: digest(root / railway_refinement.PRODUCER),
        grammar_shell.PRODUCER: digest(root / grammar_shell.PRODUCER),
        railway_campaign.PRODUCER: digest(root / railway_campaign.PRODUCER),
        railway_native.PRODUCER: digest(root / railway_native.PRODUCER),
        "engineering/station_rail/__init__.py": digest(root / "engineering/station_rail/__init__.py"),
        "engineering/station_rail/common.py": digest(root / "engineering/station_rail/common.py"),
    }
    source_sha256.update(body.get("sources", {}))
    _checked_hashes(root, source_sha256)
    if not (Path(CCX_PATH).is_file() and digest(CCX_PATH) == CCX_SHA256):
        raise ValueError("CalculiX executable is missing or differs from the pinned binary")
    return (root, parent_result, parent, body, bundle, frontier, prior,
            parent_sha256, prior_package, source_sha256)


def _request(*, parent: dict, body: dict, bundle: dict, frontier: dict,
             prior: list, parent_sha256: str, prior_package: dict,
             source_sha256: dict, estimate: dict) -> dict:
    base_request = prior[1][3]
    return dict(schema="osr-railway-fine-refinement-request/1",
                parent_campaign_id=parent["campaign_id"],
                parent_contract_id=parent["contract_id"],
                parent_result_sha256=parent_sha256,
                parent_run_id=parent["run_id"],
                parent_evaluation_ids=[x[1] for x in prior],
                parent_frontier_item=frontier,
                prior_refinement=prior_package,
                body_candidate_id=body["candidate_id"],
                body_definition_id=body["definition_id"],
                bundle_id=bundle["candidate_id"],
                bundle_definition_id=bundle["definition_id"],
                load_case="normal",
                load_mass_kg=base_request["load_mass_kg"],
                load_basis=base_request["load_basis"],
                mesh_m=NEXT_MESH_M,
                parent_mesh_m=PREVIOUS_MESH_M,
                element_kind=ELEMENT_KIND,
                computational_cell_estimate=estimate,
                computational_cell_budget=CELL_BUDGET,
                expected_solid_elements=EXPECTED_CELLS,
                expected_node_count=EXPECTED_NODES,
                memory_mb=MEMORY_MB,
                timeout_s=TIMEOUT_S,
                omp_threads=OMP_THREADS,
                solver_path=CCX_PATH,
                solver_sha256=CCX_SHA256,
                solver_invocation_limit=1,
                retry_count=0,
                source_sha256=source_sha256,
                purpose="single bounded numerical refinement; no engineering acceptance or physical qualification",
                **FLAGS)


def _fine_deck(candidate: dict, bundle: dict, *, mesh_m: float):
    """Build the fixed normal-load C3D8I case at the declared finer mesh."""
    if mesh_m != NEXT_MESH_M:
        raise ValueError("This evaluator permits exactly the declared 0.10625 m mesh")
    plan = grammar_shell.plan(candidate)
    if not plan.get("admitted"):
        raise ValueError("Candidate failed the existing finite-face model admission")
    structural_ids = set(candidate["shell_model"]["structural_part_ids"])
    parts = [part for part in candidate["parts"] if part["id"] in structural_ids]
    nodes, elements, meta = grammar_shell._mesh(parts, mesh_m, ELEMENT_KIND)
    if meta.get("finite_face_components") != 1:
        raise ValueError("Fine mesh does not retain exactly one finite-face component")
    if (meta.get("solid_elements") != EXPECTED_CELLS
            or len(elements) != EXPECTED_CELLS
            or meta.get("node_count") != EXPECTED_NODES
            or len(nodes) != EXPECTED_NODES):
        raise ValueError("Generated fine mesh differs from the exact 128,382-element/227,190-node preflight")

    mass = float(bundle["normal_sprung_mass_hypothesis_kg"])
    if abs(mass - NORMAL_LOAD_KG) > 1e-6 or not math.isfinite(mass):
        raise ValueError("P1 normal sprung mass differs from the fixed same-load basis")
    load_basis = dict(bundle_id=bundle["candidate_id"],
                      bundle_definition_id=bundle["definition_id"],
                      scope=bundle["mass_scope"])
    stock_mass = sum(element["volume_m3"]
                     * candidate["materials"][element["material_id"]]["density_kg_m3"]
                     for element in elements)
    if mass < stock_mass:
        raise ValueError("Normal sprung mass is below counted structural stock mass")

    loads = {node_id: np.zeros(3) for node_id in nodes}
    gravity = 9.80665
    floor_area = 0.0
    for element in elements:
        weight = (element["volume_m3"]
                  * candidate["materials"][element["material_id"]]["density_kg_m3"]
                  * gravity)
        for node_id in element["nodes"]:
            loads[node_id][2] -= weight / 8.0
        if element["role"] == "floor" and abs(element["bounds"][5] - 1.0) < 1e-9:
            floor_area += ((element["bounds"][1] - element["bounds"][0])
                           * (element["bounds"][3] - element["bounds"][2]))
    if floor_area <= 0:
        raise ValueError("Counted passenger floor load surface missing")
    pressure = (mass - stock_mass) * gravity / floor_area
    for element in elements:
        if element["role"] == "floor" and abs(element["bounds"][5] - 1.0) < 1e-9:
            area = ((element["bounds"][1] - element["bounds"][0])
                    * (element["bounds"][3] - element["bounds"][2]))
            force = pressure * area
            for node_id in element["nodes"][4:8]:
                loads[node_id][2] -= force / 4.0

    model = candidate["shell_model"]
    supports = {}
    patches = []
    for x in model["support_x_m"]:
        for y in model["support_y_m"]:
            patch_nodes = [node_id for node_id, coordinate in nodes.items()
                           if abs(coordinate[2] - model["support_z_m"]) < 1e-9
                           and abs(coordinate[0] - x) <= 0.100001
                           and abs(coordinate[1] - y) <= 0.090001]
            if len(patch_nodes) < 8:
                raise ValueError("Declared finite bearing pad is unresolved at the fine mesh")
            for node_id in patch_nodes:
                supports[node_id] = {3}
            patches.append(dict(x_m=x, y_m=y, node_count=len(patch_nodes)))
    ordered = sorted(supports, key=lambda node_id: (nodes[node_id][0], nodes[node_id][1]))
    supports[ordered[0]].update((1, 2))
    supports[ordered[-1]].add(2)

    raw = grammar_shell._finish(
        grammar_shell._base(nodes, elements, candidate["materials"]),
        nodes, supports, loads)
    if raw.count("*END STEP") != 1:
        raise ValueError("Expected one terminal CalculiX step for the bounded stress request")
    # Integration-point Cauchy stress in .dat is retained as an exploratory,
    # unqualified numerical diagnostic only.
    raw = raw.replace("*END STEP", "*EL PRINT,ELSET=ALLSOLIDS\nS\n*END STEP")
    definition = dict(**meta,
                      candidate_id=candidate["candidate_id"],
                      definition_id=candidate["definition_id"],
                      load_case="normal",
                      load_mass_kg=mass,
                      load_basis=load_basis,
                      structural_selfweight_mass_kg=stock_mass,
                      floor_lumped_remaining_mass_kg=mass - stock_mass,
                      load_distribution="Consistent C3D8I selfweight plus uniform additional floor pressure; actual equipment/roof load locations held",
                      support_patches=patches,
                      support_assumption="Rigid flat finite bearing pads, one XY datum and one Y datum; bogie compliance held",
                      joint_assumption=model["joint_assumption"],
                      stress_request="Cauchy stress S at C3D8I integration points in model.dat; unqualified diagnostic",
                      nodes=nodes,
                      supports={str(node_id): sorted(dofs) for node_id, dofs in supports.items()},
                      loads_N={str(node_id): value.tolist() for node_id, value in loads.items()})
    return raw, definition, elements


def _comparison(prior_raw: Path, fine_raw: Path, execution: str) -> dict:
    if execution != "completed":
        return dict(status="unavailable", matched_point_count=0,
                    reason="Fine-mesh native execution did not complete; displacement output unavailable")
    return railway_refinement._matched_point_delta(prior_raw, fine_raw)


def _prior_trend(prior: list, prior_refinement_result: dict, result: dict) -> list[dict]:
    rows = []
    for mesh, evaluation_id, _raw_dir, _request, prior_result in prior:
        rows.append(dict(mesh_m=mesh, evaluation_id=evaluation_id,
                         maximum_displacements=prior_result.get("maximum_displacements"),
                         external_work_J=prior_result.get("external_work_J"),
                         native_internal_energy_J=prior_result.get("native_internal_energy_J"),
                         energy_relative_residual=prior_result.get("energy_relative_residual"),
                         force_relative_residual=prior_result.get("force_relative_residual"),
                         moment_relative_residual=prior_result.get("moment_relative_residual"),
                         stress_status="not-requested-in-campaign-evaluation"))
    rows.append(dict(mesh_m=PREVIOUS_MESH_M,
                     evaluation_id=prior_refinement_result["evaluation_id"],
                     maximum_displacements=prior_refinement_result.get("maximum_displacements"),
                     external_work_J=prior_refinement_result.get("external_work_J"),
                     native_internal_energy_J=prior_refinement_result.get("native_internal_energy_J"),
                     energy_relative_residual=prior_refinement_result.get("energy_relative_residual"),
                     force_relative_residual=prior_refinement_result.get("force_relative_residual"),
                     moment_relative_residual=prior_refinement_result.get("moment_relative_residual"),
                     stress_status=prior_refinement_result.get("stress_summary", {}).get("status")))
    rows.append(dict(mesh_m=NEXT_MESH_M, evaluation_id=result["evaluation_id"],
                     maximum_displacements=result.get("maximum_displacements"),
                     external_work_J=result.get("external_work_J"),
                     native_internal_energy_J=result.get("native_internal_energy_J"),
                     energy_relative_residual=result.get("energy_relative_residual"),
                     force_relative_residual=result.get("force_relative_residual"),
                     moment_relative_residual=result.get("moment_relative_residual"),
                     stress_status=result.get("stress_summary", {}).get("status")))
    return rows


def _external_integrity(root: Path, parent_result: Path, parent_sha256: str,
                        source_sha256: dict, prior_package: dict) -> None:
    if digest(parent_result) != parent_sha256:
        raise ValueError("Parent campaign result changed during fine refinement")
    _checked_hashes(root, source_sha256)
    current = _prior_refinement_package(root, parent_result, parent_sha256)
    if current != prior_package:
        raise ValueError("Pinned 0.2125 m parent package changed during fine refinement")
    if digest(CCX_PATH) != CCX_SHA256:
        raise ValueError("Pinned CalculiX executable changed during fine refinement")


def _valid_existing(folder: Path, request: dict, root: Path,
                    parent_result: Path, parent_sha256: str,
                    prior_package: dict) -> tuple[dict, dict, dict]:
    manifest_path = folder / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError("An incomplete earlier fine-refinement package is retained at this request path; it will not be overwritten")
    manifest = json.loads(manifest_path.read_bytes())
    if manifest.get("manifest_id") != identity({k: v for k, v in manifest.items() if k != "manifest_id"}):
        raise ValueError("Existing fine-refinement manifest identity differs")
    actual_files = {p.relative_to(folder).as_posix(): digest(p)
                    for p in folder.rglob("*")
                    if p.is_file() and p.relative_to(folder).as_posix()
                    not in ("manifest.json", "report.json")}
    if actual_files != manifest.get("files_sha256"):
        raise ValueError("Existing fine-refinement package files differ from manifest")
    if json.loads((folder / "request.json").read_bytes()) != request:
        raise ValueError("Existing fine-refinement path is occupied by a different request")
    if (manifest.get("source_sha256") != request.get("source_sha256")
            or manifest.get("schema") != "osr-railway-fine-refinement-manifest/1"):
        raise ValueError("Existing fine-refinement manifest source identity differs from the request")
    if any(manifest.get(flag) is not False for flag in FLAGS):
        raise ValueError("Existing fine-refinement manifest contains an acceptance or release flag")
    _external_integrity(root, parent_result, parent_sha256,
                        request["source_sha256"], prior_package)
    result = json.loads((folder / "native" / "result.json").read_bytes())
    report = json.loads((folder / "report.json").read_bytes())
    request_id = identity(request)
    summary = result.get("mesh_summary", {})
    generated = report.get("generated_mesh", {})
    report_core = {k: v for k, v in report.items() if k not in ("report_id", "manifest_id")}
    if (result.get("evaluation_id") != identity({k: v for k, v in result.items() if k != "evaluation_id"})
            or manifest.get("request_id") != request_id
            or manifest.get("evaluation_id") != result.get("evaluation_id")
            or manifest.get("parent_result_sha256") != parent_sha256
            or manifest.get("prior_refinement") != prior_package
            or result.get("request_id") != request_id
            or result.get("parent_campaign_id") != request.get("parent_campaign_id")
            or result.get("parent_contract_id") != request.get("parent_contract_id")
            or result.get("parent_result_sha256") != parent_sha256
            or result.get("parent_run_id") != request.get("parent_run_id")
            or result.get("prior_refinement") != prior_package
            or result.get("candidate_id") != CANDIDATE_ID
            or result.get("definition_id") != DEFINITION_ID
            or result.get("source_sha256") != request.get("source_sha256")
            or result.get("tool", {}).get("ccx_path") != CCX_PATH
            or result.get("tool", {}).get("ccx_sha256") != CCX_SHA256
            or result.get("tool", {}).get("requested_memory_mb") != MEMORY_MB
            or result.get("tool", {}).get("timeout_s") != TIMEOUT_S
            or result.get("tool", {}).get("OMP_threads") != OMP_THREADS
            or not isinstance(result.get("tool", {}).get("RLIMIT_AS_bytes"), int)
            or result.get("tool", {}).get("RLIMIT_AS_bytes", 0) <= 0
            or result.get("tool", {}).get("RLIMIT_AS_bytes", 0) > MEMORY_MB * 1024**2
            or report.get("request_id") != request_id
            or report.get("evaluation_id") != result.get("evaluation_id")
            or report.get("parent_campaign_id") != request.get("parent_campaign_id")
            or report.get("parent_contract_id") != request.get("parent_contract_id")
            or report.get("parent_result_sha256") != request.get("parent_result_sha256")
            or report.get("physical_identity_changed") is not False
            or report.get("report_id") != identity(report_core)
            or manifest.get("report_id") != report.get("report_id")
            or report.get("manifest_id") != manifest.get("manifest_id")
            or report.get("prior_refinement") != prior_package
            or report.get("body_candidate_id") != CANDIDATE_ID
            or report.get("body_definition_id") != DEFINITION_ID
            or report.get("bundle_id") != BUNDLE_ID
            or any(report.get(flag) is not False for flag in FLAGS)
            or generated.get("solid_elements") != EXPECTED_CELLS
            or generated.get("element_count") != EXPECTED_CELLS
            or generated.get("node_count") != EXPECTED_NODES
            or generated.get("finite_face_components") != 1
            or generated.get("element_kind") != ELEMENT_KIND
            or generated.get("mesh_m") != NEXT_MESH_M
            or summary.get("solid_elements") != EXPECTED_CELLS
            or summary.get("node_count") != EXPECTED_NODES
            or summary.get("finite_face_components") != 1
            or summary.get("element_kind") != ELEMENT_KIND
            or summary.get("mesh_m") != NEXT_MESH_M
            or summary.get("load_case") != "normal"
            or summary.get("load_mass_kg") != NORMAL_LOAD_KG
            or summary.get("load_basis") != request.get("load_basis")
            or summary.get("candidate_id") != CANDIDATE_ID
            or summary.get("definition_id") != DEFINITION_ID
            or result.get("stress_summary") != report.get("stress")
            or any(result.get(flag) is not False for flag in FLAGS)):
        raise ValueError("Existing fine-refinement result/report/manifest context differs from the request")
    native_candidate = json.loads((folder / "native" / "candidate.json").read_bytes())
    if (native_candidate.get("candidate_id") != CANDIDATE_ID
            or native_candidate.get("definition_id") != DEFINITION_ID):
        raise ValueError("Existing fine-refinement packet candidate differs from its request")
    return result, report, manifest


def run(root=ROOT, *, parent_result: Path, candidate_id: str) -> dict:
    """Execute at most one immutable 0.10625 m normal-load refinement."""
    context = _context(Path(root), Path(parent_result), candidate_id)
    (root, parent_result, parent, body, bundle, frontier, prior,
     parent_sha256, prior_package, source_sha256) = context
    estimate = railway_native.cell_estimate(body, NEXT_MESH_M)
    if not estimate or estimate.get("solid_cells") != EXPECTED_CELLS:
        raise ValueError("Exact 0.10625 m occupied-cell preflight differs from 128,382 solid cells")
    if estimate["solid_cells"] > CELL_BUDGET:
        raise ValueError("Fine refinement exceeds its one-off computational cell budget")
    request = _request(parent=parent, body=body, bundle=bundle, frontier=frontier,
                       prior=prior, parent_sha256=parent_sha256,
                       prior_package=prior_package, source_sha256=source_sha256,
                       estimate=estimate)
    request_id = identity(request)
    folder = root / "build/coupled-railway/refinements" / CANDIDATE_ID / request_id
    if folder.exists():
        result, report, manifest = _valid_existing(
            folder, request, root, parent_result, parent_sha256, prior_package)
        return dict(request_id=request_id, evaluation_id=result["evaluation_id"],
                    manifest_id=manifest["manifest_id"], execution=result.get("execution"),
                    numerical_validity=result.get("numerical_validity"), output=str(folder),
                    reused=True, stress_status=report.get("stress", {}).get("status"), **FLAGS)

    if digest(CCX_PATH) != CCX_SHA256:
        raise ValueError("CalculiX executable changed after preflight")
    raw, definition, elements = _fine_deck(body, bundle, mesh_m=NEXT_MESH_M)
    if (definition.get("load_mass_kg") != request["load_mass_kg"]
            or definition.get("load_basis") != request["load_basis"]
            or definition.get("mesh_m") != NEXT_MESH_M
            or definition.get("element_kind") != ELEMENT_KIND
            or definition.get("finite_face_components") != 1
            or definition.get("solid_elements") != EXPECTED_CELLS
            or definition.get("node_count") != EXPECTED_NODES
            or len(elements) != EXPECTED_CELLS
            or len(definition.get("nodes", {})) != EXPECTED_NODES):
        raise ValueError("Generated fine mesh/load differs from exact preflight request")
    generated_mesh = {k: definition[k] for k in (
        "mesh_m", "element_kind", "finite_face_components", "solid_elements", "node_count")}
    generated_mesh["element_count"] = len(elements)
    folder.mkdir(parents=True)
    (folder / "request.json").write_bytes(encoded(request))
    _external_integrity(root, parent_result, parent_sha256,
                        source_sha256, prior_package)
    native_dir = folder / "native"
    result = grammar_shell._execute(raw, definition, native_dir, MEMORY_MB, TIMEOUT_S)
    if result.get("tool", {}).get("ccx_sha256") != CCX_SHA256:
        raise ValueError("Native execution did not use the pinned CalculiX executable")
    _external_integrity(root, parent_result, parent_sha256,
                        source_sha256, prior_package)
    result.update(request_id=request_id,
                  parent_campaign_id=CAMPAIGN_ID,
                  parent_contract_id=CONTRACT_ID,
                  parent_result_sha256=parent_sha256,
                  parent_run_id=parent["run_id"],
                  prior_refinement=prior_package,
                  candidate_id=CANDIDATE_ID,
                  definition_id=DEFINITION_ID,
                  source_sha256=source_sha256,
                  stress_request=definition["stress_request"],
                  stress_qualification=False,
                  engineering_screen="unknown",
                  missing_gates=grammar_shell.MISSING,
                  **FLAGS)
    if result.get("execution") == "completed":
        stress = railway_refinement._stress_summary(native_dir / "model.dat", elements)
    else:
        stress = dict(status="unavailable", reason="Native execution did not complete",
                      metric="Cauchy von Mises stress", unit="Pa", physical_allowable=None)
    result["stress_summary"] = stress
    result["evaluation_id"] = identity(result)
    (native_dir / "candidate.json").write_bytes(encoded(body))
    (native_dir / "result.json").write_bytes(encoded(result))

    prior_refinement_folder = (root / "build/coupled-railway/refinements"
                               / CANDIDATE_ID / PREVIOUS_REQUEST_ID)
    previous_result = json.loads((prior_refinement_folder / "native" / "result.json").read_bytes())
    comparison = _comparison(prior_refinement_folder / "native", native_dir,
                             result.get("execution", "tool_error"))
    report = dict(schema="osr-railway-fine-refinement-report/1",
                  request_id=request_id,
                  evaluation_id=result["evaluation_id"],
                  parent_campaign_id=CAMPAIGN_ID,
                  parent_contract_id=CONTRACT_ID,
                  parent_result_sha256=parent_sha256,
                  prior_refinement=prior_package,
                  body_candidate_id=CANDIDATE_ID,
                  body_definition_id=DEFINITION_ID,
                  bundle_id=BUNDLE_ID,
                  generated_mesh=generated_mesh,
                  matched_point_displacement_comparison=dict(
                      from_mesh_m=PREVIOUS_MESH_M, to_mesh_m=NEXT_MESH_M, **comparison),
                  mesh_and_equilibrium_residual_trend=_prior_trend(prior, previous_result, result),
                  stress=stress,
                  stress_interpretation="Unqualified ideal-joint model Cauchy von Mises diagnostic only; no allowable or qualification meaning",
                  physical_identity_changed=False,
                  engineering_acceptance=False,
                  physical_acceptance=False,
                  interpretation="Numerical refinement only; complete installed mass, qualified joints, allowable stress, fatigue, buckling, clearance, physical correlation and independent qualification remain open.",
                  **FLAGS)
    report_id = identity(report)
    _external_integrity(root, parent_result, parent_sha256,
                        source_sha256, prior_package)
    # report.json carries manifest_id. Its payload is instead bound through
    # report_id in the manifest to avoid a self-referential hash cycle.
    files = {p.relative_to(folder).as_posix(): digest(p)
             for p in folder.rglob("*")
             if p.is_file() and p.relative_to(folder).as_posix()
             not in ("manifest.json", "report.json")}
    _external_integrity(root, parent_result, parent_sha256,
                        source_sha256, prior_package)
    manifest = dict(schema="osr-railway-fine-refinement-manifest/1",
                    request_id=request_id,
                    evaluation_id=result["evaluation_id"],
                    parent_result_sha256=parent_sha256,
                    prior_refinement=prior_package,
                    source_sha256=source_sha256,
                    report_id=report_id,
                    files_sha256=files,
                    **FLAGS)
    manifest["manifest_id"] = identity(manifest)
    report["report_id"] = report_id
    report["manifest_id"] = manifest["manifest_id"]
    (folder / "report.json").write_bytes(encoded(report))
    _external_integrity(root, parent_result, parent_sha256,
                        source_sha256, prior_package)
    (folder / "manifest.json").write_bytes(encoded(manifest))
    return dict(request_id=request_id,
                evaluation_id=result["evaluation_id"],
                manifest_id=manifest["manifest_id"],
                execution=result.get("execution"),
                numerical_validity=result.get("numerical_validity"),
                output=str(folder), reused=False,
                stress_status=stress.get("status"), **FLAGS)


def verify(root=ROOT, *, parent_result: Path, candidate_id: str) -> dict:
    """Reconstruct and validate a sealed fine-refinement package without solving."""
    context = _context(Path(root), Path(parent_result), candidate_id)
    (root, parent_result, parent, body, bundle, frontier, prior,
     parent_sha256, prior_package, source_sha256) = context
    estimate = railway_native.cell_estimate(body, NEXT_MESH_M)
    if not estimate or estimate.get("solid_cells") != EXPECTED_CELLS:
        raise ValueError("Exact 0.10625 m occupied-cell preflight differs from 128,382 solid cells")
    request = _request(parent=parent, body=body, bundle=bundle, frontier=frontier,
                       prior=prior, parent_sha256=parent_sha256,
                       prior_package=prior_package, source_sha256=source_sha256,
                       estimate=estimate)
    request_id = identity(request)
    folder = root / "build/coupled-railway/refinements" / CANDIDATE_ID / request_id
    result, report, manifest = _valid_existing(
        folder, request, root, parent_result, parent_sha256, prior_package)
    return dict(verified=True,
                request_id=request_id,
                evaluation_id=result["evaluation_id"],
                manifest_id=manifest["manifest_id"],
                prior_request_id=prior_package["request_id"],
                prior_evaluation_id=prior_package["evaluation_id"],
                prior_manifest_id=prior_package["manifest_id"],
                execution=result.get("execution"),
                numerical_validity=result.get("numerical_validity"),
                stress_status=report.get("stress", {}).get("status"),
                output=str(folder), **FLAGS)
