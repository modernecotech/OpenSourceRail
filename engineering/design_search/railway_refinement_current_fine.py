"""Current-source continuation at the next mesh after the 0.2125 m run.

The physical body, P1 bundle, normal load, supports and C3D8I method remain
fixed. This separate evaluator records a larger compute request because the
128,382-cell mesh exceeds the previous 90,000-cell allowance.
"""
from __future__ import annotations

import json
from pathlib import Path

from engineering.station_rail import ROOT, FLAGS
from engineering.station_rail.common import digest, encoded, identity
from . import grammar_shell, railway_campaign, railway_fine_refinement, railway_native, railway_native_execution
from . import railway_refinement, railway_refinement_current as current
from . import railway_refinement_current_verifier as current_verifier

PRODUCER = "engineering/design_search/railway_refinement_current_fine.py"
CANDIDATE_ID = current.CANDIDATE_ID
MESH_M = 0.10625
CELL_BUDGET = 140_000
MEMORY_MB = 8_192
TIMEOUT_S = 240
ELEMENT_KIND = "C3D8I"


def _context(root=ROOT, *, parent_result: Path, candidate_id: str):
    root=Path(root).resolve();parent_result=Path(parent_result).resolve()
    base=current._context(root,parent_result=parent_result,candidate_id=candidate_id)
    request_02125=current._request(base[0],base[2],base[3],base[4],base[5],base[6],base[7])
    base_folder=current._package(root,request_02125)
    verified=current_verifier.verify(root,parent_result=parent_result,candidate_id=candidate_id)
    base_manifest=json.loads((base_folder/'manifest.json').read_bytes())
    base_result=json.loads((base_folder/'native/result.json').read_bytes())
    if verified.get('verified') is not True or base_result.get('execution')!='completed':
        raise ValueError("Exact current-source 0.2125 m package must verify and complete before finer refinement")
    if base_manifest.get('manifest_id')!=verified.get('manifest_id'):
        raise ValueError("Current 0.2125 m receipt differs from independent verification")
    return base,request_02125,base_folder,base_result,base_manifest


def _prior_0425(base):
    """Extract the 0.425 m row from the canonical current-context tuple."""
    prior=base[6][1]
    if prior[0]!=0.425 or not isinstance(prior[2],Path):
        raise ValueError("Current context does not contain its exact 0.425 m normal-load packet")
    return dict(evaluation_id=prior[1],raw=prior[2],request=prior[3],result=prior[4])


def _request(root,base,request_02125,base_result,base_manifest):
    _root,parent_path,parent,body,bundle,frontier,prior,parent_sha=base
    estimate=railway_native.cell_estimate(body,MESH_M)
    if not estimate or estimate.get('solid_cells')!=128_382:
        raise ValueError("Exact current 0.10625 m preflight differs from 128,382 solid cells")
    if estimate['solid_cells']>CELL_BUDGET:
        raise ValueError("Current fine mesh exceeds its explicit 140,000-cell compute budget")
    sources={
        PRODUCER:digest(root/PRODUCER),
        current.PRODUCER:digest(root/current.PRODUCER),
        current_verifier.PRODUCER:digest(root/current_verifier.PRODUCER),
        railway_fine_refinement.PRODUCER:digest(root/railway_fine_refinement.PRODUCER),
        railway_refinement.PRODUCER:digest(root/railway_refinement.PRODUCER),
        railway_campaign.PRODUCER:digest(root/railway_campaign.PRODUCER),
        railway_native.PRODUCER:digest(root/railway_native.PRODUCER),
        railway_native_execution.PRODUCER:digest(root/railway_native_execution.PRODUCER),
        grammar_shell.PRODUCER:digest(root/grammar_shell.PRODUCER),
        **body['sources'],
    }
    current._checked_hashes(root,sources)
    solver_path='/usr/bin/ccx'
    if not Path(solver_path).is_file():raise ValueError("Declared CalculiX executable is unavailable")
    return dict(schema='osr-current-source-fine-refinement-request/1',
        parent_campaign_id=parent['campaign_id'],parent_contract_id=parent['contract_id'],
        parent_run_id=parent['run_id'],parent_result_sha256=parent_sha,
        parent_frontier_item=frontier,parent_evaluation_ids=[x[1] for x in prior],
        preceding_refinement=dict(request_id=base_manifest['request_id'],evaluation_id=base_result['evaluation_id'],
            manifest_id=base_manifest['manifest_id'],mesh_m=request_02125['mesh_m']),
        body_candidate_id=body['candidate_id'],body_definition_id=body['definition_id'],
        bundle_id=bundle['candidate_id'],bundle_definition_id=bundle['definition_id'],
        previous_mesh_evaluation_ids=[prior[1][1],base_result['evaluation_id']],
        load_case='normal',load_mass_kg=request_02125['load_mass_kg'],load_basis=request_02125['load_basis'],
        mesh_m=MESH_M,element_kind=ELEMENT_KIND,computational_cell_estimate=estimate,
        computational_cell_budget=CELL_BUDGET,memory_mb=MEMORY_MB,timeout_s=TIMEOUT_S,
        solver=dict(path=solver_path,sha256=digest(solver_path)),source_sha256=sources,
        solver_invocation_limit=1,retry_count=0,
        purpose='Current-source numerical trend continuation only; no strength or physical acceptance',**FLAGS)


def _package(root,request):
    return Path(root)/'build/coupled-railway/refinements'/request['body_candidate_id']/identity(request)


def run(root=ROOT, *, parent_result: Path, candidate_id: str):
    base,request_02125,base_folder,base_result,base_manifest=_context(
        root,parent_result=parent_result,candidate_id=candidate_id)
    request=_request(Path(root).resolve(),base,request_02125,base_result,base_manifest)
    folder=_package(root,request)
    if folder.exists():
        result,report,manifest=_verify_package(root,parent_result=parent_result,candidate_id=candidate_id)
        return dict(request_id=manifest['request_id'],evaluation_id=result['evaluation_id'],
            execution=result.get('execution'),numerical_validity=result.get('numerical_validity'),
            output=str(folder),reused=True,manifest_id=manifest['manifest_id'],**FLAGS)
    body=base[3];bundle=base[4]
    raw,definition,elements=railway_fine_refinement._fine_deck(body,bundle,mesh_m=MESH_M)
    if (definition.get('solid_elements')!=request['computational_cell_estimate']['solid_cells']
            or definition.get('load_basis')!=request['load_basis']
            or definition.get('load_mass_kg')!=request['load_mass_kg']):
        raise ValueError("Generated fine mesh differs from exact current request")
    folder.mkdir(parents=True);(folder/'request.json').write_bytes(encoded(request))
    if digest(base[1])!=request['parent_result_sha256']:
        raise ValueError("Parent campaign changed before native solver execution")
    current._checked_hashes(root,request['source_sha256'])
    native=folder/'native'
    result=railway_native_execution.execute(raw,definition,native,memory_mb=MEMORY_MB,timeout_s=TIMEOUT_S)
    if digest(base[1])!=request['parent_result_sha256']:
        raise ValueError("Parent campaign changed during solver execution; raw files retained")
    current._checked_hashes(root,request['source_sha256'])
    if result.get('tool',{}).get('ccx_path')!=request['solver']['path'] or result.get('tool',{}).get('ccx_sha256')!=request['solver']['sha256']:
        raise ValueError("CalculiX executable changed during solver execution")
    result.update(candidate_id=body['candidate_id'],definition_id=body['definition_id'],
        source_sha256=request['source_sha256'],stress_request=definition.get('stress_request'),
        stress_qualification=False,engineering_accepted=False,manufacturing_release=False,
        operating_release=False,physical_accepted=False)
    stress=(railway_refinement._stress_summary(native/'model.dat',elements)
        if result.get('execution')=='completed' else dict(status='unavailable',reason='Native execution did not complete',
            metric='Cauchy von Mises stress',unit='Pa',physical_allowable=None))
    result['stress_summary']=stress;result['evaluation_id']=identity(result)
    (native/'candidate.json').write_bytes(encoded(body));(native/'result.json').write_bytes(encoded(result))
    prior_0425=_prior_0425(base)
    rows=[]
    for mesh,evaluation_id,raw_dir,prior_result in (
            (0.425,prior_0425['evaluation_id'],prior_0425['raw'],prior_0425['result']),
            (0.2125,base_result['evaluation_id'],base_folder/'native',base_result)):
        delta=(railway_refinement._matched_point_delta(raw_dir,native)
            if result.get('execution')=='completed' else dict(status='unavailable',reason='Finer solve did not complete'))
        rows.append(dict(from_mesh_m=mesh,to_mesh_m=MESH_M,from_evaluation_id=evaluation_id,**delta))
    trend=[]
    for mesh,evaluation_id,old_result in ((0.425,prior_0425['evaluation_id'],prior_0425['result']),
                                         (0.2125,base_result['evaluation_id'],base_result),
                                         (MESH_M,result['evaluation_id'],result)):
        trend.append(dict(mesh_m=mesh,evaluation_id=evaluation_id,
            maximum_displacements=old_result.get('maximum_displacements'),
            external_work_J=old_result.get('external_work_J'),
            native_internal_energy_J=old_result.get('native_internal_energy_J'),
            energy_relative_residual=old_result.get('energy_relative_residual'),
            force_relative_residual=old_result.get('force_relative_residual'),
            moment_relative_residual=old_result.get('moment_relative_residual')))
    report=dict(schema='osr-current-source-fine-refinement-report/1',request_id=identity(request),
        evaluation_id=result['evaluation_id'],parent_campaign_id=base[2]['campaign_id'],
        parent_contract_id=base[2]['contract_id'],body_candidate_id=body['candidate_id'],
        body_definition_id=body['definition_id'],bundle_id=bundle['candidate_id'],
        bundle_definition_id=bundle['definition_id'],preceding_refinement= request['preceding_refinement'],
        generated_mesh=dict(mesh_m=MESH_M,element_kind=ELEMENT_KIND,solid_elements=len(elements),
            element_count=len(elements),node_count=definition['node_count'],finite_face_components=definition['finite_face_components']),
        mesh_and_residual_trend=trend,matched_point_displacement_comparisons=rows,stress=stress,
        physical_and_engineering_acceptance=False,
        interpretation='Current-source numerical trend for the unchanged idealized metal frame and normal load. It does not establish material/joint strength, fatigue, buckling, clearance, physical correlation, or qualification.',**FLAGS)
    (folder/'report.json').write_bytes(encoded(report))
    files={p.relative_to(folder).as_posix():digest(p) for p in folder.rglob('*') if p.is_file() and p.name!='manifest.json'}
    manifest=dict(schema='osr-current-source-fine-refinement-manifest/1',request_id=identity(request),
        evaluation_id=result['evaluation_id'],parent_result_sha256=request['parent_result_sha256'],
        source_sha256=request['source_sha256'],files_sha256=files,**FLAGS)
    manifest['manifest_id']=identity(manifest);(folder/'manifest.json').write_bytes(encoded(manifest))
    return dict(request_id=manifest['request_id'],evaluation_id=result['evaluation_id'],
        execution=result.get('execution'),numerical_validity=result.get('numerical_validity'),
        output=str(folder),reused=False,manifest_id=manifest['manifest_id'],stress_status=stress.get('status'),**FLAGS)


def _verify_package(root=ROOT, *, parent_result: Path, candidate_id: str):
    base,request_02125,base_folder,base_result,base_manifest=_context(
        root,parent_result=parent_result,candidate_id=candidate_id)
    request=_request(Path(root).resolve(),base,request_02125,base_result,base_manifest)
    folder=_package(root,request)
    if not folder.is_dir():raise ValueError("Current-source fine refinement package is missing")
    manifest=json.loads((folder/'manifest.json').read_bytes());actual={p.relative_to(folder).as_posix():digest(p)
        for p in folder.rglob('*') if p.is_file() and p.name!='manifest.json'}
    if (manifest.get('manifest_id')!=identity({k:v for k,v in manifest.items() if k!='manifest_id'})
            or manifest.get('request_id')!=identity(request)
            or manifest.get('parent_result_sha256')!=request['parent_result_sha256']
            or manifest.get('source_sha256')!=request['source_sha256']
            or manifest.get('files_sha256')!=actual
            or json.loads((folder/'request.json').read_bytes())!=request):
        raise ValueError("Current fine-refinement manifest, request, or payload differs")
    result=json.loads((folder/'native/result.json').read_bytes());report=json.loads((folder/'report.json').read_bytes())
    definition=json.loads((folder/'native/definition.json').read_bytes())
    if (result.get('evaluation_id')!=identity({k:v for k,v in result.items() if k!='evaluation_id'})
            or result.get('evaluation_id')!=manifest.get('evaluation_id')
            or report.get('request_id')!=identity(request) or report.get('evaluation_id')!=result.get('evaluation_id')
            or result.get('candidate_id')!=request['body_candidate_id']
            or result.get('definition_id')!=request['body_definition_id']
            or result.get('source_sha256')!=request['source_sha256']
            or result.get('mesh_summary',{}).get('solid_elements')!=request['computational_cell_estimate']['solid_cells']
            or result.get('mesh_summary',{}).get('node_count')!=227_190
            or result.get('mesh_summary',{}).get('mesh_m')!=MESH_M
            or report.get('generated_mesh',{}).get('solid_elements')!=request['computational_cell_estimate']['solid_cells']
            or definition.get('solid_elements')!=request['computational_cell_estimate']['solid_cells']
            or result.get('tool',{}).get('ccx_path')!=request['solver']['path']
            or result.get('tool',{}).get('ccx_sha256')!=request['solver']['sha256']
            or result.get('tool',{}).get('requested_memory_mb')!=MEMORY_MB
            or result.get('tool',{}).get('timeout_s')!=TIMEOUT_S
            or result.get('tool',{}).get('OMP_threads')!=1
            or not isinstance(result.get('tool',{}).get('RLIMIT_AS_bytes'),int)
            or not 0<result.get('tool',{}).get('RLIMIT_AS_bytes',0)<=MEMORY_MB*1024**2):
        raise ValueError("Current fine-refinement result/mesh/resource context differs")
    current._checked_hashes(root,request['source_sha256'])
    raw,regenerated,elements=railway_fine_refinement._fine_deck(base[3],base[4],mesh_m=MESH_M)
    if ((folder/'native/model.inp').read_bytes()!=raw.encode()
            or definition!=json.loads(encoded(regenerated))
            or len(elements)!=request['computational_cell_estimate']['solid_cells']):
        raise ValueError("Current fine native deck does not regenerate from exact parent inputs")
    if report.get('physical_and_engineering_acceptance') is not False or any(result.get(k) is not False for k in
            ('physical_accepted','engineering_accepted','manufacturing_release','operating_release')):
        raise ValueError("Numerical refinement cannot grant physical acceptance or release")
    return result,report,manifest


def verify(root=ROOT, *, parent_result: Path, candidate_id: str):
    result,report,manifest=_verify_package(root,parent_result=parent_result,candidate_id=candidate_id)
    return dict(verified=True,request_id=manifest['request_id'],manifest_id=manifest['manifest_id'],
        evaluation_id=result['evaluation_id'],candidate_id=candidate_id,
        body_definition_id=result['definition_id'],mesh_m=report['generated_mesh']['mesh_m'],
        numerical_validity=result.get('numerical_validity'),execution=result.get('execution'),
        physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
        manufacturing_release=False,operating_release=False,physical_journey_completed=False)
