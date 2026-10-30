"""One-off, source-bound sub-0.4 m refinement for the coupled railway body.

This evaluator holds the physical candidate and bundle fixed. Its lower mesh
domain and stress request are owned by this module so the historical
``grammar_shell`` campaign method and its source identity remain unchanged.
The result is a numerical experiment only; it cannot qualify or accept a body.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from engineering.station_rail import ROOT, FLAGS
from engineering.station_rail.common import digest, encoded, identity
from . import grammar_shell, railway_campaign, railway_native

PRODUCER = "engineering/design_search/railway_refinement.py"
CAMPAIGN_ID = "6ba19dff09e30606bb4d20ddd153deef033c86ab1d27adc8dab6ad842d68f99f"
CONTRACT_ID = "de9f89acc80e0ec2f3ebb8b6c8f60e2446de9df06c66317c5cedc5b8625f8921"
CANDIDATE_ID = "8db92b830fda54c81ec231c541f811b24f938f2471b559448d2ed2683754f78b"
DEFINITION_ID = "21efbaf935ba954a6788d2c54e841b12c891a01b70afef4f7a2edd581af5458f"
BODY_EVALUATIONS = {
    0.85: "4bea9935bb7e172a2364ac7fcf5218cabb5ea80d41f60db444bb7de199049cb1",
    0.425: "11a732b32205db4aa4511518ae3fd5aef8763278005dc513263bab203134c810",
}
NEXT_MESH_M = 0.2125
CELL_BUDGET = 90_000
MEMORY_MB = 5_120
TIMEOUT_S = 150
ELEMENT_KIND = "C3D8I"
NORMAL_LOAD_KG = 10_818.661193648113


def _checked_hashes(root: Path, sources: dict[str, str]) -> None:
    for name, expected in sources.items():
        path = (root / name).resolve()
        if root.resolve() not in path.parents or not path.is_file() or digest(path) != expected:
            raise ValueError(f"Source identity mismatch: {name}")


def _native_parent_package(parent_dir: Path, parent: dict, evaluation_id: str):
    packet = next((x for x in parent.get("native", {}).get("packet_index", [])
                   if x.get("evaluation_id") == evaluation_id), None)
    if packet is None:
        raise ValueError(f"Parent campaign lacks native packet {evaluation_id}")
    raw = (parent_dir / "native" / packet["raw_path"]).resolve()
    if parent_dir.resolve() not in raw.parents or not raw.is_dir():
        raise ValueError("Parent native packet path escapes its campaign or is missing")
    result = railway_native._packet(raw)
    if result.get("evaluation_id") != evaluation_id:
        raise ValueError("Parent native packet identity differs")
    request_path = raw.parent / "request.json"
    request = json.loads(request_path.read_bytes())
    return raw, request, result


def _verify_parent(root: Path, parent_result: Path, candidate_id: str):
    parent_result = parent_result.resolve()
    if not parent_result.is_file():
        raise ValueError("Explicit parent result.json is required")
    parent_result_sha256 = digest(parent_result)
    parent_dir = parent_result.parent
    parent = json.loads(parent_result.read_bytes())
    if digest(parent_result) != parent_result_sha256:
        raise ValueError("Parent result changed while it was being read")
    expected_run_id = identity({k: v for k, v in parent.items() if k != "run_id"})
    if (parent.get("campaign_id") != CAMPAIGN_ID
            or parent.get("campaign_id") != railway_campaign.semantic_id(parent)
            or parent.get("run_id") != expected_run_id
            or parent.get("contract_id") != CONTRACT_ID):
        raise ValueError("Parent campaign/contract differs from this refinement definition")
    if candidate_id != CANDIDATE_ID:
        raise ValueError("This bounded refinement accepts only its declared physical candidate")
    body = next((x for x in parent.get("bodies", []) if x.get("candidate_id") == candidate_id), None)
    if not body or body.get("definition_id") != DEFINITION_ID:
        raise ValueError("Parent physical body definition differs")
    _checked_hashes(root, body.get("sources", {}))
    frontier = next((x for x in parent.get("frontier", [])
                     if x.get("kind") == "unresolved-numerical-refinement"
                     and x.get("body_candidate_id") == candidate_id), None)
    if not frontier or frontier.get("proposed_next_mesh_m") != NEXT_MESH_M:
        raise ValueError("Parent frontier does not request this exact mesh refinement")

    prior = []
    for mesh, evaluation_id in BODY_EVALUATIONS.items():
        raw, request, result = _native_parent_package(parent_dir, parent, evaluation_id)
        native_candidate = json.loads((raw / "candidate.json").read_bytes())
        if (native_candidate.get("candidate_id") != body["candidate_id"]
                or native_candidate.get("definition_id") != body["definition_id"]):
            raise ValueError(f"Prior packet candidate differs from parent body: {evaluation_id}")
        summary = result.get("mesh_summary", {})
        if (result.get("candidate_id") != candidate_id
                or result.get("definition_id") != DEFINITION_ID
                or summary.get("mesh_m") != mesh
                or summary.get("load_case") != "normal"
                or summary.get("element_kind") != ELEMENT_KIND
                or request.get("body_candidate_id") != candidate_id
                or request.get("definition_id") != DEFINITION_ID
                or request.get("load_case") != "normal"
                or request.get("mesh_m") != mesh
                or request.get("element_kind") != ELEMENT_KIND):
            raise ValueError(f"Prior evaluation {evaluation_id} is not the required same-candidate case")
        prior.append((mesh, evaluation_id, raw, request, result))
    first_request, second_request = prior[0][3], prior[1][3]
    identity_keys = ("bundle_id", "load_case", "load_mass_kg", "load_basis", "element_kind",
                     "memory_mb", "timeout_s")
    if any(first_request.get(k) != second_request.get(k) for k in identity_keys):
        raise ValueError("Prior normal cases do not share one exact bundle/load/method/resource basis")
    if first_request.get("bundle_id") != "1e8d1d7c394fc0bdbd47e34fb21d413ebc34a49576bad60b31b254bd635dfb68":
        raise ValueError("Prior body evaluations are not attached to the declared P1 bundle")
    if abs(first_request.get("load_mass_kg", 0.0) - NORMAL_LOAD_KG) > 1e-6:
        raise ValueError("Prior normal load differs from the required source-bound mass")
    bundle = next((x for x in parent.get("bundles", [])
                   if x.get("candidate_id") == first_request["bundle_id"]), None)
    if not bundle or bundle.get("body_candidate_id") != candidate_id or bundle.get("family_id") != "P1":
        raise ValueError("Parent P1 bundle is missing or has a different physical body")
    bundle_definition_id = bundle.get("definition_id")
    if first_request["load_basis"].get("bundle_definition_id") != bundle_definition_id:
        raise ValueError("Source-bound load basis does not match the retained bundle definition")
    return parent, body, bundle, frontier, prior, parent_result_sha256


def _refinement_deck(candidate: dict, bundle: dict, *, mesh_m: float):
    """Build the same C3D8I body deck while allowing the declared 0.2125 m study."""
    if not 0.2 <= mesh_m < 0.4:
        raise ValueError("This evaluator is restricted to the declared 0.2..0.4 m refinement interval")
    plan = grammar_shell.plan(candidate)
    if not plan["admitted"]:
        raise ValueError("Candidate failed the existing finite-face model admission")
    ids = set(candidate["shell_model"]["structural_part_ids"])
    parts = [p for p in candidate["parts"] if p["id"] in ids]
    nodes, elements, meta = grammar_shell._mesh(parts, mesh_m, ELEMENT_KIND)
    if meta["finite_face_components"] != 1:
        raise ValueError("Refinement mesh has a disconnected physical load path")

    load_case = "normal"
    mass = bundle["normal_sprung_mass_hypothesis_kg"]
    load_basis = dict(bundle_id=bundle["candidate_id"], bundle_definition_id=bundle["definition_id"],
                      scope=bundle["mass_scope"])
    stock_mass = sum(e["volume_m3"] * candidate["materials"][e["material_id"]]["density_kg_m3"]
                     for e in elements)
    if mass < stock_mass or not math.isfinite(mass):
        raise ValueError("Source-bound passenger load omits counted body stock")

    loads = {n: np.zeros(3) for n in nodes}
    gravity = 9.80665
    floor_area = 0.0
    for element in elements:
        weight = (element["volume_m3"] * candidate["materials"][element["material_id"]]["density_kg_m3"]
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
            force = pressure * ((element["bounds"][1] - element["bounds"][0])
                                * (element["bounds"][3] - element["bounds"][2]))
            for node_id in element["nodes"][4:8]:
                loads[node_id][2] -= force / 4.0

    model = candidate["shell_model"]
    supports = {}
    patches = []
    for x in model["support_x_m"]:
        for y in model["support_y_m"]:
            support_nodes = [n for n, q in nodes.items()
                             if abs(q[2] - model["support_z_m"]) < 1e-9
                             and abs(q[0] - x) <= 0.100001
                             and abs(q[1] - y) <= 0.090001]
            if len(support_nodes) < 8:
                raise ValueError("Declared finite bearing pad is unresolved at this mesh")
            for n in support_nodes:
                supports[n] = {3}
            patches.append(dict(x_m=x, y_m=y, node_count=len(support_nodes)))
    ordered = sorted(supports, key=lambda n: (nodes[n][0], nodes[n][1]))
    supports[ordered[0]].update((1, 2))
    supports[ordered[-1]].add(2)

    raw = grammar_shell._finish(grammar_shell._base(nodes, elements, candidate["materials"]),
                                nodes, supports, loads)
    # CalculiX *EL PRINT S writes integration-point Cauchy stress to model.dat.
    # NOE is valid on *EL FILE, not *EL PRINT; this numerical diagnostic has no
    # material allowable or qualification meaning.
    raw = raw.replace("*END STEP", "*EL PRINT,ELSET=ALLSOLIDS\nS\n*END STEP")
    definition = dict(**meta, candidate_id=candidate["candidate_id"],
                      definition_id=candidate["definition_id"], load_case=load_case,
                      load_mass_kg=mass, load_basis=load_basis,
                      structural_selfweight_mass_kg=stock_mass,
                      floor_lumped_remaining_mass_kg=mass-stock_mass,
                      load_distribution="Consistent C3D8I selfweight + uniform additional floor pressure; actual equipment/roof load locations held",
                      support_patches=patches,
                      support_assumption="Rigid flat finite bearing pads, one XY datum and one Y datum; bogie compliance held",
                      joint_assumption=model["joint_assumption"],
                      stress_request="Cauchy stress S at C3D8I integration points in model.dat; exploratory and unqualified",
                      nodes=nodes, supports={str(n): sorted(ds) for n, ds in supports.items()},
                      loads_N={str(n): v.tolist() for n, v in loads.items()})
    return raw, definition, elements


def _stress_summary(path: Path, elements: list[dict]) -> dict:
    """Extract element integration-point stresses if CalculiX wrote the section."""
    rows = []
    active = False
    for line in path.read_text(errors="replace").splitlines():
        lower = line.lower()
        if "stresses" in lower and ("elem" in lower or "integ" in lower or "integration" in lower):
            active = True
            continue
        if any(k in lower for k in ("displacements", "forces", "total internal energy", "strains (")):
            active = False
        if not active:
            continue
        fields = line.replace(",", " ").split()
        if len(fields) < 8:
            continue
        try:
            element_id = int(fields[0])
            integration_point = int(fields[1])
            values = [float(x.replace("D", "E").replace("d", "e")) for x in fields[2:8]]
        except (ValueError, OverflowError):
            continue
        if not all(math.isfinite(x) for x in values):
            continue
        sxx, syy, szz, sxy, sxz, syz = values
        von_mises = math.sqrt(max(0.0, 0.5 * ((sxx-syy)**2 + (syy-szz)**2 + (szz-sxx)**2)
                                      + 3.0 * (sxy*sxy + sxz*sxz + syz*syz)))
        rows.append((element_id, integration_point, von_mises))
    if not rows:
        return dict(status="unavailable", reason="No parseable CalculiX integration-point stress rows",
                    metric="Cauchy von Mises stress", unit="Pa", physical_allowable=None)
    material_by_id = {e["id"]: e for e in elements}
    values = np.asarray([r[2] for r in rows], dtype=float)
    peak = max(rows, key=lambda r: r[2])
    element = material_by_id.get(peak[0], {})
    return dict(status="reported-numerical-diagnostic", metric="Cauchy von Mises stress at C3D8I integration points",
                unit="Pa", integration_point_rows=len(rows), maximum_Pa=float(peak[2]),
                percentile_95_Pa=float(np.percentile(values, 95)), percentile_99_Pa=float(np.percentile(values, 99)),
                maximum_element_id=peak[0], maximum_integration_point=peak[1],
                maximum_element_part_id=element.get("part_id"), maximum_element_role=element.get("role"),
                physical_allowable=None,
                interpretation="Unqualified ideal-joint model stress; maxima may be mesh/junction singularity sensitive.")


def _point_displacement_map(raw: Path):
    definition = json.loads((raw / "definition.json").read_bytes())
    displacement, _, _ = grammar_shell._read(raw / "model.dat")
    points = {}
    for node_id, coordinate in definition["nodes"].items():
        value = displacement.get(int(node_id))
        if value is None:
            continue
        key = tuple(round(float(v), 9) for v in coordinate)
        points[key] = value
    return points


def _matched_point_delta(coarse_raw: Path, fine_raw: Path) -> dict:
    coarse = _point_displacement_map(coarse_raw)
    fine = _point_displacement_map(fine_raw)
    common = sorted(set(coarse).intersection(fine))
    if not common:
        return dict(status="unavailable", matched_point_count=0,
                    reason="No exactly matched physical mesh-node coordinates")
    differences = np.asarray([[abs(coarse[p][d] - fine[p][d]) for d in range(3)] for p in common])
    magnitudes = np.asarray([[abs(fine[p][d]) for d in range(3)] for p in common])
    names = ("longitudinal_m", "lateral_m", "vertical_m")
    summary = {}
    for axis, name in enumerate(names):
        maximum = float(np.max(differences[:, axis]))
        reference = float(np.max(magnitudes[:, axis]))
        summary[name] = dict(maximum_absolute_difference_m=maximum,
                             rms_absolute_difference_m=float(np.sqrt(np.mean(differences[:, axis]**2))),
                             maximum_relative_to_fine_component=maximum / max(reference, 1e-12))
    return dict(status="compared", matched_point_count=len(common), components=summary,
                normalization="maximum absolute fine-grid displacement component over matched nodes")


def _valid_existing(folder: Path, request: dict, root: Path):
    manifest_path = folder / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError("An incomplete earlier refinement attempt is retained at this request path; it will not be overwritten")
    manifest = json.loads(manifest_path.read_bytes())
    if manifest.get("manifest_id") != identity({k: v for k, v in manifest.items() if k != "manifest_id"}):
        raise ValueError("Existing refinement manifest identity differs")
    actual = {p.relative_to(folder).as_posix(): digest(p) for p in folder.rglob("*")
              if p.is_file() and p.name != "manifest.json"}
    if actual != manifest.get("files_sha256"):
        raise ValueError("Existing refinement package files differ from manifest")
    if json.loads((folder / "request.json").read_bytes()) != request:
        raise ValueError("Existing refinement path is occupied by a different request")
    if manifest.get("source_sha256") != request.get("source_sha256"):
        raise ValueError("Existing refinement manifest source identity differs from the request")
    _checked_hashes(root, manifest.get("source_sha256", {}))
    result = json.loads((folder / "native" / "result.json").read_bytes())
    report = json.loads((folder / "report.json").read_bytes())
    expected_request_id = identity(request)
    if (result.get("evaluation_id") != identity({k: v for k, v in result.items() if k != "evaluation_id"})
            or manifest.get("request_id") != expected_request_id
            or manifest.get("evaluation_id") != result.get("evaluation_id")
            or manifest.get("parent_result_sha256") != request.get("parent_result_sha256")
            or result.get("candidate_id") != request.get("body_candidate_id")
            or result.get("definition_id") != request.get("body_definition_id")
            or result.get("source_sha256") != request.get("source_sha256")
            or result.get("tool", {}).get("requested_memory_mb") != request.get("memory_mb")
            or result.get("tool", {}).get("timeout_s") != request.get("timeout_s")
            or report.get("request_id") != expected_request_id
            or report.get("evaluation_id") != result.get("evaluation_id")):
        raise ValueError("Existing refinement result/manifest/report context differs from the request")
    generated_mesh = report.get("generated_mesh", {})
    estimate = request.get("computational_cell_estimate", {})
    if (generated_mesh.get("solid_elements") != estimate.get("solid_cells")
            or generated_mesh.get("element_count") != generated_mesh.get("solid_elements")
            or generated_mesh.get("element_kind") != request.get("element_kind")
            or generated_mesh.get("mesh_m") != request.get("mesh_m")
            or not isinstance(generated_mesh.get("node_count"), int)
            or generated_mesh.get("node_count", 0) <= 0
            or result.get("mesh_summary", {}).get("solid_elements") != estimate.get("solid_cells")
            or result.get("mesh_summary", {}).get("element_kind") != request.get("element_kind")
            or result.get("mesh_summary", {}).get("mesh_m") != request.get("mesh_m")
            or result.get("mesh_summary", {}).get("load_mass_kg") != request.get("load_mass_kg")
            or result.get("mesh_summary", {}).get("load_basis") != request.get("load_basis")):
        raise ValueError("Existing generated mesh counts differ from the preflight request")
    native_candidate = json.loads((folder / "native" / "candidate.json").read_bytes())
    if (native_candidate.get("candidate_id") != request.get("body_candidate_id")
            or native_candidate.get("definition_id") != request.get("body_definition_id")):
        raise ValueError("Existing refinement packet candidate differs from its request")
    return result, report, manifest


def run(root=ROOT, *, parent_result: Path, candidate_id: str):
    root = Path(root).resolve()
    parent_result = Path(parent_result).resolve()
    parent, body, bundle, frontier, prior, parent_result_sha256 = _verify_parent(root, parent_result, candidate_id)
    estimate = railway_native.cell_estimate(body, NEXT_MESH_M)
    if not estimate or estimate["solid_cells"] != 82_372:
        raise ValueError("Exact refinement cell preflight differs from the declared 82,372-cell case")
    if estimate["solid_cells"] > CELL_BUDGET:
        raise ValueError("Refinement exceeds its one-off computational cell budget")

    request_sources = {PRODUCER: digest(root / PRODUCER),
                       grammar_shell.PRODUCER: digest(root / grammar_shell.PRODUCER),
                       railway_campaign.PRODUCER: digest(root / railway_campaign.PRODUCER),
                       railway_native.PRODUCER: digest(root / railway_native.PRODUCER),
                       **body.get("sources", {})}
    _checked_hashes(root, request_sources)
    base_request = prior[1][3]
    request = dict(schema="osr-railway-numerical-refinement-request/1",
                   parent_campaign_id=parent["campaign_id"], parent_contract_id=parent["contract_id"],
                   parent_result_sha256=parent_result_sha256, parent_run_id=parent["run_id"],
                   parent_frontier_item=frontier,
                   parent_evaluation_ids=[x[1] for x in prior],
                   body_candidate_id=body["candidate_id"], body_definition_id=body["definition_id"],
                   bundle_id=bundle["candidate_id"], bundle_definition_id=bundle["definition_id"],
                   load_case="normal", load_mass_kg=base_request["load_mass_kg"],
                   load_basis=base_request["load_basis"], mesh_m=NEXT_MESH_M,
                   element_kind=ELEMENT_KIND, computational_cell_estimate=estimate,
                   computational_cell_budget=CELL_BUDGET, memory_mb=MEMORY_MB, timeout_s=TIMEOUT_S,
                   source_sha256=request_sources,
                   purpose="next numerical experiment; no engineering acceptance or physical qualification",
                   **FLAGS)
    request_id = identity(request)
    folder = root / "build/coupled-railway/refinements" / candidate_id / request_id
    if folder.exists():
        result, report, manifest = _valid_existing(folder, request, root)
        return dict(request_id=request_id, evaluation_id=result["evaluation_id"],
                    execution=result.get("execution"), numerical_validity=result.get("numerical_validity"),
                    output=str(folder), reused=True, manifest_id=manifest["manifest_id"],
                    stress_status=report.get("stress", {}).get("status"), **FLAGS)

    raw, definition, elements = _refinement_deck(body, bundle, mesh_m=NEXT_MESH_M)
    if definition["load_basis"] != request["load_basis"] or definition["load_mass_kg"] != request["load_mass_kg"]:
        raise ValueError("Generated refinement deck changed the retained load basis")
    generated_mesh = dict(mesh_m=definition["mesh_m"], element_kind=definition["element_kind"],
                          solid_elements=definition["solid_elements"], element_count=len(elements),
                          node_count=definition["node_count"])
    if generated_mesh["solid_elements"] != estimate["solid_cells"]:
        raise ValueError("Generated mesh element count differs from exact occupied-cell preflight")
    if generated_mesh["element_count"] != generated_mesh["solid_elements"]:
        raise ValueError("Generated element total differs from the reported solid element count")

    folder.mkdir(parents=True)
    (folder / "request.json").write_bytes(encoded(request))
    if digest(parent_result) != parent_result_sha256:
        raise ValueError("Parent result changed before native refinement; request retained without solver execution")
    _checked_hashes(root, request_sources)
    native_dir = folder / "native"
    result = grammar_shell._execute(raw, definition, native_dir, MEMORY_MB, TIMEOUT_S)
    if digest(parent_result) != parent_result_sha256:
        raise ValueError("Parent result changed during native refinement; raw execution files retained unsealed")
    _checked_hashes(root, request_sources)
    result.update(candidate_id=body["candidate_id"], definition_id=body["definition_id"],
                  source_sha256=request_sources, stress_request=definition["stress_request"],
                  missing_gates=grammar_shell.MISSING,
                  stress_qualification=False, engineering_accepted=False,
                  manufacturing_release=False, operating_release=False, physical_accepted=False)
    stress = _stress_summary(native_dir / "model.dat", elements) if result.get("execution") == "completed" else dict(
        status="unavailable", reason="Native execution did not complete", metric="Cauchy von Mises stress", unit="Pa")
    result["stress_summary"] = stress
    result["evaluation_id"] = identity(result)
    (native_dir / "candidate.json").write_bytes(encoded(body))
    (native_dir / "result.json").write_bytes(encoded(result))

    previous_rows = {x[0]: x for x in prior}
    by_mesh = {x["mesh_m"]: x for x in parent["native"]["body_results"]
               if x.get("body_candidate_id") == candidate_id
               and x.get("bundle_id") == bundle["candidate_id"]
               and x.get("case") in ("normal-fine", "normal-refined")}
    prior_results = [by_mesh.get(0.85), by_mesh.get(0.425)]
    displacement_comparisons = []
    for i, mesh in enumerate((0.85, 0.425)):
        if prior_results[i] is None:
            displacement_comparisons.append(dict(from_mesh_m=mesh, to_mesh_m=NEXT_MESH_M,
                                                  status="unavailable", reason="Prior body row missing"))
            continue
        if result.get("execution") != "completed":
            displacement_comparisons.append(dict(from_mesh_m=mesh, to_mesh_m=NEXT_MESH_M,
                                                  status="unavailable",
                                                  reason="Native refinement did not complete; displacement output unavailable"))
            continue
        old_raw = previous_rows[mesh][2]
        displacement_comparisons.append(dict(from_mesh_m=mesh, to_mesh_m=NEXT_MESH_M,
                                              **_matched_point_delta(old_raw, native_dir)))
    trend = []
    for mesh, evaluation_id, raw_dir, prior_request, prior_result in prior:
        trend.append(dict(mesh_m=mesh, evaluation_id=evaluation_id,
                          maximum_displacements=prior_result.get("maximum_displacements"),
                          external_work_J=prior_result.get("external_work_J"),
                          native_internal_energy_J=prior_result.get("native_internal_energy_J"),
                          energy_relative_residual=prior_result.get("energy_relative_residual"),
                          force_relative_residual=prior_result.get("force_relative_residual"),
                          moment_relative_residual=prior_result.get("moment_relative_residual"),
                          stress_status="unavailable-in-parent-evaluation"))
    trend.append(dict(mesh_m=NEXT_MESH_M, evaluation_id=result["evaluation_id"],
                      maximum_displacements=result.get("maximum_displacements"),
                      external_work_J=result.get("external_work_J"),
                      native_internal_energy_J=result.get("native_internal_energy_J"),
                      energy_relative_residual=result.get("energy_relative_residual"),
                      force_relative_residual=result.get("force_relative_residual"),
                      moment_relative_residual=result.get("moment_relative_residual"),
                      stress_status=stress.get("status")))
    report = dict(schema="osr-railway-numerical-refinement-report/1",
                  request_id=request_id, evaluation_id=result["evaluation_id"],
                  parent_campaign_id=parent["campaign_id"], parent_contract_id=parent["contract_id"],
                  body_candidate_id=body["candidate_id"], body_definition_id=body["definition_id"],
                  bundle_id=bundle["candidate_id"], physical_identity_changed=False,
                  generated_mesh=generated_mesh,
                  mesh_and_residual_trend=trend,
                  matched_point_displacement_comparisons=displacement_comparisons,
                  stress=stress,
                  stress_trend_status="incomplete: the two parent evaluations did not request stress output",
                  physical_and_engineering_acceptance=False,
                  interpretation="Numerical evidence for the declared idealized frame model only; no complete installed mass, qualified joints, material allowables, fatigue, buckling, clearance, physical correlation, or release.",
                  **FLAGS)
    (folder / "report.json").write_bytes(encoded(report))
    if digest(parent_result) != parent_result_sha256:
        raise ValueError("Parent result changed before refinement manifest sealing")
    _checked_hashes(root, request_sources)
    files = {p.relative_to(folder).as_posix(): digest(p) for p in folder.rglob("*")
             if p.is_file() and p.name != "manifest.json"}
    if digest(parent_result) != parent_result_sha256:
        raise ValueError("Parent result changed before refinement manifest sealing")
    _checked_hashes(root, request_sources)
    manifest = dict(schema="osr-railway-numerical-refinement-manifest/1",
                    request_id=request_id, evaluation_id=result["evaluation_id"],
                    parent_result_sha256=parent_result_sha256, source_sha256=request_sources,
                    files_sha256=files, **FLAGS)
    manifest["manifest_id"] = identity(manifest)
    (folder / "manifest.json").write_bytes(encoded(manifest))
    return dict(request_id=request_id, evaluation_id=result["evaluation_id"],
                execution=result.get("execution"), numerical_validity=result.get("numerical_validity"),
                output=str(folder), reused=False, manifest_id=manifest["manifest_id"],
                stress_status=stress.get("status"), **FLAGS)


def verify(root=ROOT, *, parent_result: Path, candidate_id: str):
    """Verify the immutable follow-on package without executing a solver."""
    root = Path(root).resolve()
    parent_result = Path(parent_result).resolve()
    parent, body, bundle, _, prior, parent_result_sha256 = _verify_parent(root, parent_result, candidate_id)
    estimate = railway_native.cell_estimate(body, NEXT_MESH_M)
    request_sources = {PRODUCER: digest(root / PRODUCER),
                       grammar_shell.PRODUCER: digest(root / grammar_shell.PRODUCER),
                       railway_campaign.PRODUCER: digest(root / railway_campaign.PRODUCER),
                       railway_native.PRODUCER: digest(root / railway_native.PRODUCER),
                       **body.get("sources", {})}
    base_request = prior[1][3]
    request = dict(schema="osr-railway-numerical-refinement-request/1",
                   parent_campaign_id=parent["campaign_id"], parent_contract_id=parent["contract_id"],
                   parent_result_sha256=parent_result_sha256, parent_run_id=parent["run_id"],
                   parent_frontier_item=next(x for x in parent["frontier"]
                                             if x.get("kind") == "unresolved-numerical-refinement"
                                             and x.get("body_candidate_id") == candidate_id),
                   parent_evaluation_ids=[x[1] for x in prior], body_candidate_id=body["candidate_id"],
                   body_definition_id=body["definition_id"], bundle_id=bundle["candidate_id"],
                   bundle_definition_id=bundle["definition_id"], load_case="normal",
                   load_mass_kg=base_request["load_mass_kg"], load_basis=base_request["load_basis"],
                   mesh_m=NEXT_MESH_M, element_kind=ELEMENT_KIND,
                   computational_cell_estimate=estimate, computational_cell_budget=CELL_BUDGET,
                   memory_mb=MEMORY_MB, timeout_s=TIMEOUT_S, source_sha256=request_sources,
                   purpose="next numerical experiment; no engineering acceptance or physical qualification",
                   **FLAGS)
    request_id = identity(request)
    folder = root / "build/coupled-railway/refinements" / candidate_id / request_id
    result, report, manifest = _valid_existing(folder, request, root)
    return dict(verified=True, request_id=request_id, manifest_id=manifest["manifest_id"],
                evaluation_id=result["evaluation_id"], campaign_id=parent["campaign_id"],
                candidate_id=body["candidate_id"], numerical_validity=result.get("numerical_validity"),
                execution=result.get("execution"), stress_status=report.get("stress", {}).get("status"),
                **FLAGS)
