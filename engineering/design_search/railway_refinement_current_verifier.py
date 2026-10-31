"""Independent verifier for current-source mesh continuation packets.

The shared historical verifier requires an ``element_count`` report alias
that the current-source producer did not emit. This verifier checks the
original immutable packet against its request, definition, native result and
regenerated deck without editing or resealing that packet.
"""
from __future__ import annotations

import json
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from . import railway_refinement_current as current

PRODUCER = "engineering/design_search/railway_refinement_current_verifier.py"


def verify(root=ROOT, *, parent_result: Path, candidate_id: str):
    context = current._context(root, parent_result=parent_result, candidate_id=candidate_id)
    root, parent_path, parent, body, bundle, _frontier, _prior, parent_sha = context
    request = current._request(root, parent, body, bundle, _frontier, _prior, parent_sha)
    folder = current._package(root, request)
    if not folder.is_dir():
        raise ValueError("Current-source refinement package is missing")
    manifest = json.loads((folder / "manifest.json").read_bytes())
    actual_files = {p.relative_to(folder).as_posix(): digest(p) for p in folder.rglob("*")
                    if p.is_file() and p.name != "manifest.json"}
    if (manifest.get("manifest_id") != identity({k: v for k, v in manifest.items() if k != "manifest_id"})
            or manifest.get("files_sha256") != actual_files
            or manifest.get("request_id") != identity(request)
            or manifest.get("parent_result_sha256") != parent_sha
            or manifest.get("source_sha256") != request.get("source_sha256")):
        raise ValueError("Current refinement receipt or immutable files differ")
    if json.loads((folder / "request.json").read_bytes()) != request:
        raise ValueError("Current refinement request differs from the exact parent context")
    result = json.loads((folder / "native/result.json").read_bytes())
    report = json.loads((folder / "report.json").read_bytes())
    definition = json.loads((folder / "native/definition.json").read_bytes())
    native_candidate = json.loads((folder / "native/candidate.json").read_bytes())
    if (result.get("evaluation_id") != identity({k: v for k, v in result.items() if k != "evaluation_id"})
            or manifest.get("evaluation_id") != result.get("evaluation_id")
            or report.get("request_id") != identity(request)
            or report.get("evaluation_id") != result.get("evaluation_id")
            or result.get("candidate_id") != body.get("candidate_id")
            or result.get("definition_id") != body.get("definition_id")
            or native_candidate.get("candidate_id") != body.get("candidate_id")
            or native_candidate.get("definition_id") != body.get("definition_id")
            or result.get("source_sha256") != request.get("source_sha256")
            or result.get("execution") != "completed"
            or result.get("numerical_validity") != "equilibrium_energy_confirmed_only"):
        raise ValueError("Current refinement result identity or execution state differs")
    current._checked_hashes(root, request["source_sha256"])
    expected_tool = request["solver"]
    tool = result.get("tool", {})
    if (tool.get("ccx_path") != expected_tool["path"]
            or tool.get("ccx_sha256") != expected_tool["sha256"]
            or tool.get("requested_memory_mb") != request["memory_mb"]
            or tool.get("timeout_s") != request["timeout_s"]):
        raise ValueError("Current refinement solver or resource request differs")

    generated = report.get("generated_mesh", {})
    estimate = request["computational_cell_estimate"]
    mesh = result.get("mesh_summary", {})
    if (generated.get("solid_elements") != estimate.get("solid_cells")
            or generated.get("element_kind") != request.get("element_kind")
            or generated.get("mesh_m") != request.get("mesh_m")
            or not isinstance(generated.get("node_count"), int)
            or generated.get("node_count") <= 0
            or definition.get("solid_elements") != estimate.get("solid_cells")
            or definition.get("node_count") != generated.get("node_count")
            or definition.get("element_kind") != request.get("element_kind")
            or definition.get("mesh_m") != request.get("mesh_m")
            or mesh.get("solid_elements") != estimate.get("solid_cells")
            or mesh.get("element_kind") != request.get("element_kind")
            or mesh.get("mesh_m") != request.get("mesh_m")
            or mesh.get("load_mass_kg") != request.get("load_mass_kg")
            or mesh.get("load_basis") != request.get("load_basis")):
        raise ValueError("Generated mesh count, load, or definition differs from preflight")

    raw, regenerated_definition, elements = current.railway_refinement._refinement_deck(
        body, bundle, mesh_m=request["mesh_m"])
    if ((folder / "native/model.inp").read_bytes() != raw.encode()
            or definition != json.loads(encoded(regenerated_definition))
            or len(elements) != estimate["solid_cells"]):
        raise ValueError("Native input deck does not regenerate from the exact current parent")
    if (report.get("physical_and_engineering_acceptance") is not False
            or any(result.get(k) is not False for k in (
                "physical_accepted", "engineering_accepted", "manufacturing_release", "operating_release"))):
        raise ValueError("Numerical refinement cannot grant physical acceptance or release")
    return dict(verified=True, request_id=identity(request), manifest_id=manifest["manifest_id"],
                evaluation_id=result["evaluation_id"], parent_contract_id=parent["contract_id"],
                candidate_id=body["candidate_id"], body_definition_id=body["definition_id"],
                bundle_definition_id=bundle["definition_id"], numerical_validity=result["numerical_validity"],
                execution=result["execution"], stress_status=report.get("stress", {}).get("status"),
                verification_note="The archived report omits a redundant element_count alias. Exact count is confirmed by the regenerated deck, definition, native result and preflight.",
                physical_accepted=False, engineering_accepted=False, configuration_adopted=False,
                manufacturing_release=False, operating_release=False, physical_journey_completed=False)
