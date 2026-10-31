"""Seal a separate reconciliation receipt for a completed raw fine-mesh run.

The original solver package is never modified. This adapter reconstructs its
report after a post-processing exception and binds the receipt to the exact raw
files, original producer source bytes, current parent, and prior meshes.
"""
from __future__ import annotations

import json
from pathlib import Path

from engineering.station_rail import ROOT, FLAGS
from engineering.station_rail.common import digest, encoded, identity
from . import grammar_shell, railway_campaign, railway_fine_refinement, railway_native
from . import railway_refinement, railway_refinement_current as current
from . import railway_refinement_current_verifier as current_verifier
from .generative_publication import archive

PRODUCER = "engineering/design_search/railway_refinement_current_fine_reconcile.py"
FINE_PRODUCER = "engineering/design_search/railway_refinement_current_fine.py"
CANDIDATE_ID = current.CANDIDATE_ID
MESH_M = 0.10625


def _raw_folder(root, candidate_id, request_id):
    return Path(root)/'build/coupled-railway/refinements'/candidate_id/request_id


def _reconciliation_folder(root, candidate_id, request_id):
    return Path(root)/'build/coupled-railway/reconciliations'/candidate_id/request_id


def _context(root, *, parent_result: Path, candidate_id: str, request_id: str):
    root=Path(root).resolve();parent_path=Path(parent_result).resolve()
    parent_sha=digest(parent_path);parent=json.loads(parent_path.read_bytes())
    base=current._context(root,parent_result=parent_path,candidate_id=candidate_id)
    target=_reconciliation_folder(root,candidate_id,request_id)
    request_path=_raw_folder(root,candidate_id,request_id)/'request.json'
    raw=_raw_folder(root,candidate_id,request_id)
    if not request_path.is_file():raise ValueError("Preserved raw fine-refinement request is missing")
    request=json.loads(request_path.read_bytes())
    if (identity(request)!=request_id or request.get('parent_result_sha256')!=parent_sha
            or request.get('parent_contract_id')!=parent.get('contract_id')
            or request.get('parent_campaign_id')!=parent.get('campaign_id')
            or request.get('parent_run_id')!=parent.get('run_id')
            or candidate_id!=CANDIDATE_ID or request.get('body_candidate_id')!=candidate_id
            or request.get('body_definition_id')!=base[3].get('definition_id')
            or request.get('bundle_id')!=base[4].get('candidate_id')
            or request.get('bundle_definition_id')!=base[4].get('definition_id')
            or request.get('mesh_m')!=MESH_M or request.get('element_kind')!='C3D8I'
            or request.get('load_case')!='normal' or request.get('computational_cell_estimate',{}).get('solid_cells')!=128382
            or request.get('computational_cell_budget')!=140000 or request.get('memory_mb')!=8192
            or request.get('timeout_s')!=240 or request.get('solver_invocation_limit')!=1
            or request.get('retry_count')!=0):
        raise ValueError("Raw fine-refinement request differs from its exact current parent and bounded contract")
    fine_source=Path(root)/FINE_PRODUCER
    snapshot=target/'fine-producer-source.py'
    original_source=snapshot.read_bytes() if snapshot.is_file() else fine_source.read_bytes()
    if digest_bytes(original_source)!=request.get('source_sha256',{}).get(FINE_PRODUCER):
        raise ValueError("Original fine-refinement producer bytes differ from the preserved request")
    for name,h in request.get('source_sha256',{}).items():
        if name==FINE_PRODUCER:continue
        path=Path(root)/name
        if not path.is_file() or digest(path)!=h:raise ValueError(f"Raw run source epoch differs: {name}")
    current_verifier.verify(root,parent_result=parent_path,candidate_id=candidate_id)
    base_request=current._request(base[0],base[2],base[3],base[4],base[5],base[6],base[7])
    base_manifest=json.loads((current._package(root,base_request)/'manifest.json').read_bytes())
    if request.get('preceding_refinement',{}).get('manifest_id')!=base_manifest.get('manifest_id'):
        raise ValueError("Fine-refinement request does not follow the exact verified 0.2125 m packet")
    return root,parent_path,parent,base,request,raw,original_source,parent_sha


def digest_bytes(value):
    from hashlib import sha256
    return sha256(value).hexdigest()


def _derive(context):
    root,parent_path,parent,base,request,raw,original_source,parent_sha=context
    raw_payload={p.relative_to(raw).as_posix():digest(p) for p in raw.rglob('*') if p.is_file()}
    result_path=raw/'native/result.json'
    if not result_path.is_file():raise ValueError("Completed raw native result is missing")
    result=json.loads(result_path.read_bytes())
    if (result.get('evaluation_id')!=identity({k:v for k,v in result.items() if k!='evaluation_id'})
            or result.get('execution')!='completed'
            or result.get('numerical_validity')!='equilibrium_energy_confirmed_only'
            or result.get('candidate_id')!=request.get('body_candidate_id')
            or result.get('definition_id')!=request.get('body_definition_id')
            or result.get('source_sha256')!=request.get('source_sha256')):
        raise ValueError("Preserved native result is not the requested completed numerical evaluation")
    estimate=railway_native.cell_estimate(base[3],MESH_M)
    if estimate.get('solid_cells')!=request['computational_cell_estimate']['solid_cells']:
        raise ValueError("Current source preflight differs from the original fine request")
    raw_deck,definition,elements=railway_fine_refinement._fine_deck(base[3],base[4],mesh_m=MESH_M)
    saved_definition=json.loads((raw/'native/definition.json').read_bytes())
    if ((raw/'native/model.inp').read_bytes()!=raw_deck.encode()
            or saved_definition!=json.loads(encoded(definition))
            or len(elements)!=estimate['solid_cells']):
        raise ValueError("Preserved solver deck does not regenerate from the exact current candidate")
    tool=result.get('tool',{})
    if (tool.get('ccx_path')!=request['solver']['path']
            or tool.get('ccx_sha256')!=request['solver']['sha256']
            or tool.get('requested_memory_mb')!=request['memory_mb']
            or tool.get('timeout_s')!=request['timeout_s']
            or tool.get('OMP_threads')!=1
            or not isinstance(tool.get('RLIMIT_AS_bytes'),int)
            or not 0<tool.get('RLIMIT_AS_bytes',0)<=request['memory_mb']*1024**2):
        raise ValueError("Preserved native result differs from its solver/resource request")
    stress=railway_refinement._stress_summary(raw/'native/model.dat',elements)
    if result.get('stress_summary')!=stress:raise ValueError("Preserved stress summary differs from the native field")

    prior_0425=base[6][1]
    old_0425=prior_0425[2]
    base_folder=current._package(root,current._request(base[0],base[2],base[3],base[4],base[5],base[6],base[7]))
    rows=[]
    for mesh,evaluation_id,raw_dir in (
            (0.425,prior_0425[1],old_0425),
            (0.2125,request['preceding_refinement']['evaluation_id'],base_folder/'native')):
        delta=railway_refinement._matched_point_delta(raw_dir,raw/'native')
        rows.append(dict(from_mesh_m=mesh,to_mesh_m=MESH_M,from_evaluation_id=evaluation_id,**delta))
    trend=[]
    for mesh,evaluation_id,old_result in (
            (0.425,prior_0425[1],prior_0425[4]),
            (0.2125,request['preceding_refinement']['evaluation_id'],json.loads((base_folder/'native/result.json').read_bytes())),
            (MESH_M,result['evaluation_id'],result)):
        trend.append(dict(mesh_m=mesh,evaluation_id=evaluation_id,
            maximum_displacements=old_result.get('maximum_displacements'),
            external_work_J=old_result.get('external_work_J'),
            native_internal_energy_J=old_result.get('native_internal_energy_J'),
            energy_relative_residual=old_result.get('energy_relative_residual'),
            force_relative_residual=old_result.get('force_relative_residual'),
            moment_relative_residual=old_result.get('moment_relative_residual')))
    report=dict(schema='osr-current-source-fine-refinement-reconciled-report/1',
        request_id=identity(request),evaluation_id=result['evaluation_id'],
        parent_campaign_id=parent['campaign_id'],parent_contract_id=parent['contract_id'],
        parent_result_sha256=parent_sha,body_candidate_id=request['body_candidate_id'],
        body_definition_id=request['body_definition_id'],bundle_id=request['bundle_id'],
        bundle_definition_id=request['bundle_definition_id'],preceding_refinement=request['preceding_refinement'],
        generated_mesh=dict(mesh_m=MESH_M,element_kind='C3D8I',solid_elements=len(elements),
            element_count=len(elements),node_count=definition['node_count'],finite_face_components=definition['finite_face_components']),
        mesh_and_residual_trend=trend,matched_point_displacement_comparisons=rows,
        stress=stress,raw_package_files_sha256=raw_payload,
        postprocess_reconciliation=dict(state='reconciled-from-immutable-native-result',
            original_exception="TypeError: 'PosixPath' object is not subscriptable in the trend assembly; native solve and raw outputs completed before this error",
            correction='Read the 0.425 m prior packet from the context prior-list; no solver re-execution and no edits to the original raw package',
            original_producer_sha256=request['source_sha256'][FINE_PRODUCER]),
        physical_and_engineering_acceptance=False,
        interpretation='Current-source numerical trend for the unchanged idealized metal frame and normal load. The reconciliation closes result reporting only; it does not establish material/joint strength, fatigue, buckling, clearance, physical correlation, or qualification.',**FLAGS)
    return result,report,raw_payload,original_source


def reconcile(root=ROOT, *, parent_result: Path, candidate_id: str, request_id: str):
    context=_context(root,parent_result=parent_result,candidate_id=candidate_id,request_id=request_id)
    root,parent_path,parent,base,request,raw,original_source,parent_sha=context
    target=_reconciliation_folder(root,candidate_id,request_id)
    if target.exists():return verify(root,parent_result=parent_path,candidate_id=candidate_id,request_id=request_id)
    result,report,raw_payload,source_snapshot=_derive(context)
    target.mkdir(parents=True)
    (target/'request.json').write_bytes(encoded(request))
    (target/'result.json').write_bytes(encoded(result))
    (target/'report.json').write_bytes(encoded(report))
    (target/'raw-payload.json').write_bytes(encoded(raw_payload))
    (target/'fine-producer-source.py').write_bytes(source_snapshot)
    (target/'raw-run.tar.gz').write_bytes(archive(raw))
    files={p.relative_to(target).as_posix():digest(p) for p in target.rglob('*') if p.is_file() and p.name!='manifest.json'}
    manifest=dict(schema='osr-current-source-fine-refinement-reconciliation-manifest/1',
        request_id=request_id,evaluation_id=result['evaluation_id'],parent_result_sha256=parent_sha,
        original_producer_sha256=request['source_sha256'][FINE_PRODUCER],
        reconciliation_source_sha256=digest(Path(root)/PRODUCER),raw_payload_sha256=raw_payload,
        files_sha256=files,**FLAGS)
    manifest['manifest_id']=identity(manifest);(target/'manifest.json').write_bytes(encoded(manifest))
    return verify(root,parent_result=parent_path,candidate_id=candidate_id,request_id=request_id)


def verify(root=ROOT, *, parent_result: Path, candidate_id: str, request_id: str):
    context=_context(root,parent_result=parent_result,candidate_id=candidate_id,request_id=request_id)
    root,parent_path,parent,base,request,raw,_source_snapshot,parent_sha=context
    target=_reconciliation_folder(root,candidate_id,request_id)
    manifest=json.loads((target/'manifest.json').read_bytes())
    actual={p.relative_to(target).as_posix():digest(p) for p in target.rglob('*') if p.is_file() and p.name!='manifest.json'}
    if (manifest.get('manifest_id')!=identity({k:v for k,v in manifest.items() if k!='manifest_id'})
            or manifest.get('files_sha256')!=actual
            or manifest.get('request_id')!=request_id
            or manifest.get('parent_result_sha256')!=parent_sha
            or manifest.get('reconciliation_source_sha256')!=digest(Path(root)/PRODUCER)):
        raise ValueError("Reconciliation receipt or payload changed")
    result,expected_report,raw_payload,source_snapshot=_derive(context)
    if ((target/'request.json').read_bytes()!=encoded(request)
            or (target/'result.json').read_bytes()!=encoded(result)
            or (target/'report.json').read_bytes()!=encoded(expected_report)
            or json.loads((target/'raw-payload.json').read_bytes())!=raw_payload
            or (target/'fine-producer-source.py').read_bytes()!=source_snapshot
            or manifest.get('raw_payload_sha256')!=raw_payload
            or manifest.get('original_producer_sha256')!=request['source_sha256'][FINE_PRODUCER]):
        raise ValueError("Reconciled report differs from the preserved native result or exact raw files")
    return dict(verified=True,request_id=request_id,manifest_id=manifest['manifest_id'],
        evaluation_id=result['evaluation_id'],candidate_id=candidate_id,
        mesh_m=MESH_M,solid_elements=request['computational_cell_estimate']['solid_cells'],
        runtime_s=result.get('runtime_s'),numerical_validity=result.get('numerical_validity'),
        physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
        manufacturing_release=False,operating_release=False,physical_journey_completed=False)
