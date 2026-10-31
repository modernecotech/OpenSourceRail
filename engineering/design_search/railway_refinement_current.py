"""Current-source continuation of the coupled frame mesh refinement.

The earlier one-off refinement evaluator remains pinned to its historical
campaign. This wrapper binds the same numerical deck builder to the exact
current parent result, body definition, bundle, and two preceding mesh cases.
It records only numerical evidence and cannot change engineering acceptance.
"""
from __future__ import annotations

import json
from pathlib import Path

from engineering.station_rail import ROOT, FLAGS
from engineering.station_rail.common import digest, encoded, identity
from . import railway_campaign, railway_native, railway_refinement

PRODUCER = "engineering/design_search/railway_refinement_current.py"
CANDIDATE_ID = "8db92b830fda54c81ec231c541f811b24f938f2471b559448d2ed2683754f78b"
P1_BUNDLE_ID = "1e8d1d7c394fc0bdbd47e34fb21d413ebc34a49576bad60b31b254bd635dfb68"
PRIOR_MESHES = (0.85, 0.425)
NEXT_MESH_M = 0.2125
CELL_BUDGET = 90_000
MEMORY_MB = 5_120
TIMEOUT_S = 150
ELEMENT_KIND = "C3D8I"


def _checked_hashes(root: Path, sources: dict[str, str]) -> None:
    railway_refinement._checked_hashes(root, sources)


def _context(root=ROOT, *, parent_result: Path, candidate_id: str):
    root = Path(root).resolve()
    parent_result = Path(parent_result).resolve()
    if not parent_result.is_file():
        raise ValueError("Exact current parent result.json is required")
    parent_sha = digest(parent_result)
    parent_dir = parent_result.parent
    parent = json.loads(parent_result.read_bytes())
    if digest(parent_result) != parent_sha:
        raise ValueError("Parent result changed while it was read")

    specification = railway_campaign.specification(root)
    source_epoch = railway_campaign.source_epoch(root)
    contract_id = identity(dict(specification=specification, source_sha256=source_epoch))
    if (parent.get("contract_id") != contract_id
            or parent.get("source_sha256") != source_epoch
            or parent.get("specification") != specification
            or parent.get("campaign_id") != railway_campaign.semantic_id(parent)
            or parent.get("run_id") != identity({k: v for k, v in parent.items() if k != "run_id"})):
        raise ValueError("Parent result is not the exact current source-bound campaign")
    if candidate_id != CANDIDATE_ID:
        raise ValueError("This bounded continuation accepts only its declared physical candidate")

    body = next((b for b in parent.get("bodies", []) if b.get("candidate_id") == candidate_id), None)
    if body is None:
        raise ValueError("Candidate body is absent from the current parent result")
    _checked_hashes(root, body.get("sources", {}))
    frontier = next((x for x in parent.get("frontier", [])
                     if x.get("kind") == "unresolved-numerical-refinement"
                     and x.get("body_candidate_id") == candidate_id), None)
    if not frontier or frontier.get("proposed_next_mesh_m") != NEXT_MESH_M:
        raise ValueError("Current parent frontier does not request this mesh continuation")

    bundle = next((b for b in parent.get("bundles", [])
                   if b.get("candidate_id") == P1_BUNDLE_ID
                   and b.get("body_candidate_id") == candidate_id
                   and b.get("family_id") == "P1"), None)
    if bundle is None:
        raise ValueError("Exact same-candidate P1 bundle is absent")
    prior = []
    for mesh, case in zip(PRIOR_MESHES, ("normal-fine", "normal-refined")):
        row = next((r for r in parent.get("native", {}).get("body_results", [])
                    if r.get("body_candidate_id") == candidate_id
                    and r.get("bundle_id") == bundle["candidate_id"]
                    and r.get("case") == case and r.get("mesh_m") == mesh), None)
        if row is None:
            raise ValueError(f"Current parent lacks its exact {mesh:g} m normal-load row")
        raw, request, result = railway_refinement._native_parent_package(
            parent_dir, parent, row["evaluation_id"])
        if (result.get("execution") != "completed"
                or result.get("numerical_validity") != "equilibrium_energy_confirmed_only"
                or result.get("candidate_id") != candidate_id
                or result.get("definition_id") != body.get("definition_id")
                or request.get("bundle_id") != bundle["candidate_id"]
                or request.get("definition_id") != body.get("definition_id")
                or request.get("load_case") != "normal"
                or request.get("mesh_m") != mesh
                or request.get("element_kind") != ELEMENT_KIND
                or result.get("mesh_summary", {}).get("mesh_m") != mesh
                or result.get("mesh_summary", {}).get("load_basis") != request.get("load_basis")):
            raise ValueError(f"Prior mesh case {row['evaluation_id']} does not match the current candidate and interfaces")
        prior.append((mesh, row["evaluation_id"], raw, request, result))
    first, second = prior[0][3], prior[1][3]
    same_inputs = ("bundle_id", "definition_id", "load_case", "load_mass_kg", "load_basis",
                   "element_kind", "memory_mb", "timeout_s")
    if any(first.get(k) != second.get(k) for k in same_inputs):
        raise ValueError("Prior mesh cases do not share the exact candidate, load, method and resource basis")
    if first.get("load_basis", {}).get("bundle_definition_id") != bundle.get("definition_id"):
        raise ValueError("Prior load basis differs from the current P1 bundle definition")
    if abs(float(first.get("load_mass_kg", 0.0)) - float(bundle["normal_sprung_mass_hypothesis_kg"])) > 1e-6:
        raise ValueError("Prior normal load differs from the current bundle")
    return root, parent_result, parent, body, bundle, frontier, prior, parent_sha


def _request(root, parent, body, bundle, frontier, prior, parent_sha):
    estimate = railway_native.cell_estimate(body, NEXT_MESH_M)
    if not estimate or estimate.get("solid_cells") != 82_372:
        raise ValueError("Exact current-candidate mesh preflight differs from 82,372 cells")
    if estimate["solid_cells"] > CELL_BUDGET:
        raise ValueError("Current refinement exceeds its explicitly declared 90,000-cell budget")
    sources = {
        PRODUCER: digest(root / PRODUCER),
        railway_refinement.PRODUCER: digest(root / railway_refinement.PRODUCER),
        railway_campaign.PRODUCER: digest(root / railway_campaign.PRODUCER),
        railway_native.PRODUCER: digest(root / railway_native.PRODUCER),
        railway_refinement.grammar_shell.PRODUCER: digest(root / railway_refinement.grammar_shell.PRODUCER),
        **body["sources"],
    }
    _checked_hashes(root, sources)
    solver_path = "/usr/bin/ccx"
    if not Path(solver_path).is_file():
        raise ValueError("Declared CalculiX executable is unavailable")
    base_request = prior[0][3]
    return dict(
        schema="osr-current-source-railway-refinement-request/1",
        parent_campaign_id=parent["campaign_id"], parent_contract_id=parent["contract_id"],
        parent_result_sha256=parent_sha, parent_run_id=parent["run_id"],
        parent_frontier_item=frontier, parent_evaluation_ids=[x[1] for x in prior],
        body_candidate_id=body["candidate_id"], body_definition_id=body["definition_id"],
        bundle_id=bundle["candidate_id"], bundle_definition_id=bundle["definition_id"],
        load_case="normal", load_mass_kg=base_request["load_mass_kg"],
        load_basis=base_request["load_basis"], mesh_m=NEXT_MESH_M,
        element_kind=ELEMENT_KIND, computational_cell_estimate=estimate,
        computational_cell_budget=CELL_BUDGET, memory_mb=MEMORY_MB, timeout_s=TIMEOUT_S,
        solver=dict(path=solver_path, sha256=digest(solver_path)),
        source_sha256=sources,
        purpose="Current-source numerical refinement only; no engineering acceptance or physical qualification",
        **FLAGS)


def _package(root, request):
    return Path(root) / "build/coupled-railway/refinements" / request["body_candidate_id"] / identity(request)


def run(root=ROOT, *, parent_result: Path, candidate_id: str):
    context = _context(root, parent_result=parent_result, candidate_id=candidate_id)
    root, parent_result, parent, body, bundle, frontier, prior, parent_sha = context
    request = _request(root, parent, body, bundle, frontier, prior, parent_sha)
    request_id = identity(request)
    folder = _package(root, request)
    if folder.exists():
        result, report, manifest = railway_refinement._valid_existing(folder, request, root)
        tool = result.get("tool", {})
        if tool.get("ccx_path") != request["solver"]["path"] or tool.get("ccx_sha256") != request["solver"]["sha256"]:
            raise ValueError("Existing package CalculiX identity differs from the requested solver")
        return dict(request_id=request_id, evaluation_id=result["evaluation_id"],
                    execution=result.get("execution"), numerical_validity=result.get("numerical_validity"),
                    output=str(folder), reused=True, manifest_id=manifest["manifest_id"],
                    stress_status=report.get("stress", {}).get("status"), **FLAGS)

    raw, definition, elements = railway_refinement._refinement_deck(body, bundle, mesh_m=NEXT_MESH_M)
    if (definition.get("load_basis") != request["load_basis"]
            or definition.get("load_mass_kg") != request["load_mass_kg"]
            or definition.get("solid_elements") != request["computational_cell_estimate"]["solid_cells"]):
        raise ValueError("Generated refinement deck does not match the exact current request")
    folder.mkdir(parents=True)
    (folder / "request.json").write_bytes(encoded(request))
    if digest(parent_result) != parent_sha:
        raise ValueError("Parent result changed before execution; incomplete request retained")
    _checked_hashes(root, request["source_sha256"])
    native_dir = folder / "native"
    result = railway_refinement.grammar_shell._execute(raw, definition, native_dir, MEMORY_MB, TIMEOUT_S)
    if digest(parent_result) != parent_sha:
        raise ValueError("Parent result changed during execution; raw files retained unsealed")
    _checked_hashes(root, request["source_sha256"])
    tool = result.get("tool", {})
    if tool.get("ccx_path") != request["solver"]["path"] or tool.get("ccx_sha256") != request["solver"]["sha256"]:
        raise ValueError("CalculiX executable changed during refinement")
    result.update(candidate_id=body["candidate_id"], definition_id=body["definition_id"],
                  source_sha256=request["source_sha256"], stress_request=definition["stress_request"],
                  missing_gates=railway_refinement.grammar_shell.MISSING,
                  stress_qualification=False, engineering_accepted=False,
                  manufacturing_release=False, operating_release=False, physical_accepted=False)
    stress = (railway_refinement._stress_summary(native_dir / "model.dat", elements)
              if result.get("execution") == "completed"
              else dict(status="unavailable", reason="Native execution did not complete",
                        metric="Cauchy von Mises stress", unit="Pa", physical_allowable=None))
    result["stress_summary"] = stress
    result["evaluation_id"] = identity(result)
    (native_dir / "candidate.json").write_bytes(encoded(body))
    (native_dir / "result.json").write_bytes(encoded(result))

    trend = [dict(mesh_m=mesh, evaluation_id=evaluation_id,
                  maximum_displacements=prior_result.get("maximum_displacements"),
                  external_work_J=prior_result.get("external_work_J"),
                  native_internal_energy_J=prior_result.get("native_internal_energy_J"),
                  energy_relative_residual=prior_result.get("energy_relative_residual"),
                  force_relative_residual=prior_result.get("force_relative_residual"),
                  moment_relative_residual=prior_result.get("moment_relative_residual"),
                  stress_status="unavailable-in-parent-evaluation")
             for mesh, evaluation_id, _raw, _request, prior_result in prior]
    trend.append(dict(mesh_m=NEXT_MESH_M, evaluation_id=result["evaluation_id"],
                      maximum_displacements=result.get("maximum_displacements"),
                      external_work_J=result.get("external_work_J"),
                      native_internal_energy_J=result.get("native_internal_energy_J"),
                      energy_relative_residual=result.get("energy_relative_residual"),
                      force_relative_residual=result.get("force_relative_residual"),
                      moment_relative_residual=result.get("moment_relative_residual"),
                      stress_status=stress.get("status")))
    comparisons = []
    for mesh, evaluation_id, prior_raw, _prior_request, _prior_result in prior:
        if result.get("execution") == "completed":
            comparisons.append(dict(from_mesh_m=mesh, to_mesh_m=NEXT_MESH_M,
                                    **railway_refinement._matched_point_delta(prior_raw, native_dir)))
        else:
            comparisons.append(dict(from_mesh_m=mesh, to_mesh_m=NEXT_MESH_M,
                                    status="unavailable", reason="Native refinement did not complete"))
    report = dict(
        schema="osr-current-source-railway-refinement-report/1", request_id=request_id,
        evaluation_id=result["evaluation_id"], parent_campaign_id=parent["campaign_id"],
        parent_contract_id=parent["contract_id"], body_candidate_id=body["candidate_id"],
        body_definition_id=body["definition_id"], bundle_id=bundle["candidate_id"],
        bundle_definition_id=bundle["definition_id"], physical_identity_changed=False,
        generated_mesh=dict(mesh_m=definition["mesh_m"], element_kind=definition["element_kind"],
                            solid_elements=definition["solid_elements"], node_count=definition["node_count"]),
        mesh_and_residual_trend=trend, matched_point_displacement_comparisons=comparisons,
        stress=stress,
        physical_and_engineering_acceptance=False,
        interpretation="Current-source numerical evidence for the declared idealized frame model only; complete installed mass, qualified joints, material allowables, fatigue, buckling, clearance, physical correlation, and release remain open.",
        **FLAGS)
    (folder / "report.json").write_bytes(encoded(report))
    if digest(parent_result) != parent_sha:
        raise ValueError("Parent changed before manifest sealing; raw package retained")
    _checked_hashes(root, request["source_sha256"])
    files = {p.relative_to(folder).as_posix(): digest(p) for p in folder.rglob("*")
             if p.is_file() and p.name != "manifest.json"}
    manifest = dict(schema="osr-current-source-railway-refinement-manifest/1",
                    request_id=request_id, evaluation_id=result["evaluation_id"],
                    parent_result_sha256=parent_sha, source_sha256=request["source_sha256"],
                    files_sha256=files, **FLAGS)
    manifest["manifest_id"] = identity(manifest)
    (folder / "manifest.json").write_bytes(encoded(manifest))
    return dict(request_id=request_id, evaluation_id=result["evaluation_id"],
                execution=result.get("execution"), numerical_validity=result.get("numerical_validity"),
                output=str(folder), reused=False, manifest_id=manifest["manifest_id"],
                stress_status=stress.get("status"), **FLAGS)


def verify(root=ROOT, *, parent_result: Path, candidate_id: str):
    context = _context(root, parent_result=parent_result, candidate_id=candidate_id)
    root, parent_result, parent, body, bundle, frontier, prior, parent_sha = context
    request = _request(root, parent, body, bundle, frontier, prior, parent_sha)
    folder = _package(root, request)
    result, report, manifest = railway_refinement._valid_existing(folder, request, root)
    tool = result.get("tool", {})
    if tool.get("ccx_path") != request["solver"]["path"] or tool.get("ccx_sha256") != request["solver"]["sha256"]:
        raise ValueError("Current refinement CalculiX identity differs")
    raw, definition, _elements = railway_refinement._refinement_deck(body, bundle, mesh_m=NEXT_MESH_M)
    if ((folder / "native/model.inp").read_bytes() != raw.encode()
            or json.loads((folder / "native/definition.json").read_bytes()) != definition):
        raise ValueError("Current refinement native deck does not regenerate from the exact parent")
    if report.get("physical_and_engineering_acceptance") is not False or any(
            result.get(k) is not False for k in ("physical_accepted", "engineering_accepted",
                                                  "manufacturing_release", "operating_release")):
        raise ValueError("Numerical refinement cannot grant physical acceptance or release")
    return dict(verified=True, request_id=identity(request), manifest_id=manifest["manifest_id"],
                evaluation_id=result["evaluation_id"], parent_contract_id=parent["contract_id"],
                candidate_id=body["candidate_id"], body_definition_id=body["definition_id"],
                bundle_definition_id=bundle["definition_id"], numerical_validity=result.get("numerical_validity"),
                execution=result.get("execution"), stress_status=report.get("stress", {}).get("status"),
                **FLAGS)
