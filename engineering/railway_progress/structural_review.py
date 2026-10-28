"""Saved-state structural review with JSON-portable numerical scalar semantics.

The original producer and both native packages remain untouched. Its legacy
verifier rejects equal JSON floats/numpy.float64 values. This separate verifier
normalizes numerical representation, retains its numerical tolerances and
reconstructs model, mass loads and matrix responses without another solve.
"""
from pathlib import Path
import json
import re
import numpy as np

from engineering.station_rail import ROOT
from engineering.station_rail.common import identity,digest,encoded
from . import FLAGS
from . import structures as frozen

PRODUCER='engineering/railway_progress/structural_review.py'
UPSTREAM='engineering/railway_progress/structures.py'
UPSTREAM_SHA256='8f2263c54d6e3648cd536434a017a848fb6e1928588008140e03cd0eb61ec09b'
FILES={'input.json','input-sources.tar.gz','stdout.log','stderr.log','worker-result.json','result.json','manifest.json'}


def _parse(raw):
    def pairs(rows):
        value={}
        for key,item in rows:
            if key in value:raise ValueError('Duplicate structural JSON key')
            value[key]=item
        return value
    def invalid(value):raise ValueError('Finite structural JSON required')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=invalid)


def normalize(value):
    """Convert native numpy scalar/container representation through strict JSON."""
    return _parse(encoded(value))


def _same(actual,expected):
    # The frozen tolerance is unchanged. Only equivalent JSON numeric/container
    # types are canonicalized; shape, keys, values and physical bindings remain.
    return frozen._close(normalize(actual),normalize(expected))


def sources(root=ROOT):
    if digest(Path(root)/UPSTREAM)!=UPSTREAM_SHA256 or digest(frozen.__file__)!=UPSTREAM_SHA256:
        raise ValueError('Frozen structural producer changed; a new review is required')
    if digest(Path(root)/PRODUCER)!=digest(__file__):raise ValueError('Executing structural reviewer differs')
    return {UPSTREAM:UPSTREAM_SHA256,PRODUCER:digest(__file__)}


def review_responses(request,worker):
    if len(worker['results'])!=len(request['mesh_sizes_m']):raise ValueError('Structural refinement inventory differs')
    diagnostics=[]
    for sample,mesh in zip(worker['results'],request['mesh_sizes_m']):
        model,car=frozen.build_model(request['vehicle'],mesh,request['joint_translation_N_m'],request['joint_rotation_Nm_rad'],request['material_scale'],request['contact_gap_hypothesis_m'])
        cases,loads=frozen.load_cases(request['vehicle'],model,car)
        if sample['mesh_m']!=mesh or not _same(sample['model'],model) or not _same(sample['loads'],loads):
            raise ValueError('Actual structural geometry, mass loading, interfaces or mesh differs')
        response=sample['response'];checks=[]
        if response['execution']=='completed':
            if len(response['cases'])!=len(cases):raise ValueError('Structural load cases missing')
            K=frozen.assemble(model)
            for saved,(name,F,prescribed) in zip(response['cases'],cases):
                u=np.asarray(saved['displacements_m_rad'],dtype=float).ravel()
                if u.shape!=(6*len(model['nodes']),) or not np.isfinite(u).all():raise ValueError('Full finite saved structural state required')
                for dof in model['supports']:
                    if abs(u[int(dof)]-prescribed.get(int(dof),0.))>1e-10:raise ValueError('Saved structural support displacement differs')
                actual=frozen._response(model,K,F,u,name)
                if not _same(saved,actual):raise ValueError('Saved structural force/reaction/stress/energy arithmetic differs')
                checks.append(dict(name=name,maximum_translation_m=actual['maximum_translation_m'],
                    maximum_rotation_rad=actual['maximum_rotation_rad'],free_relative_residual=actual['free_relative_residual'],
                    relative_energy_residual=actual['relative_energy_residual'],small_displacement_domain_suspect=actual['small_displacement_domain_suspect'],
                    approved_strength_margin=None,approved_deflection_limit_m=None))
        diagnostics.append(dict(mesh_m=mesh,response_execution=response['execution'],nodes=len(model['nodes']),
            elements=len(model['elements']),connections=len(model['connections']),cases=checks))
    return diagnostics


def verify(output,*,root=ROOT,require_current_tool=False):
    if type(require_current_tool) is not bool:raise ValueError('Explicit numerical tool policy required')
    reviewer=sources(root);folder=Path(output)
    if folder.is_symlink() or {p.name for p in folder.iterdir()}!=FILES or any(not p.is_file() or p.is_symlink() for p in folder.iterdir()):
        raise ValueError('Exact ordinary original structural package required')
    if any(p.stat().st_size>256*1024**2 for p in folder.iterdir()):raise ValueError('Bounded structural inputs/results required')
    manifest=_parse((folder/'manifest.json').read_bytes());request=_parse((folder/'input.json').read_bytes())
    frozen._validate_request(request,root)
    result=_parse((folder/'result.json').read_bytes());worker=_parse((folder/'worker-result.json').read_bytes())
    if (manifest.get('schema')!='osr-located-structure-package/1'
        or manifest.get('manifest_id')!=identity({k:v for k,v in manifest.items() if k!='manifest_id'})
        or manifest.get('files_sha256')!={p.name:digest(p) for p in folder.iterdir() if p.name!='manifest.json'}
        or manifest.get('source_sha256')!=request['source_sha256']
        or manifest.get('candidate_id')!=request['candidate_id'] or manifest.get('request_id')!=request['request_id']
        or result.get('run_evaluation_id')!=identity({k:v for k,v in result.items() if k!='run_evaluation_id'})
        or manifest.get('evaluation_id')!=result['run_evaluation_id'] or result.get('candidate_id')!=request['candidate_id']
        or worker.get('evaluation_id')!=identity({k:v for k,v in worker.items() if k!='evaluation_id'})
        or any(manifest.get(k) is not False or result.get(k) is not False or worker.get(k) is not False for k in FLAGS)):
        raise ValueError('Original structural source/payload/candidate/evaluation/disposition differs')
    expected={**worker,'candidate_id':request['candidate_id'],'request_id':request['request_id'],'source_sha256':request['source_sha256']}
    if {k:v for k,v in result.items() if k!='run_evaluation_id'}!=expected:raise ValueError('Original structural worker/result binding differs')
    frozen._verify_retained_sources(folder,request['source_sha256'],root)
    if worker.get('actual_address_space_limit_bytes')!=request['memory_bytes'] or worker.get('OPENBLAS_NUM_THREADS')!='1' or worker.get('OMP_NUM_THREADS')!='1':
        raise ValueError('Actual structural worker resources differ')
    tool=worker.get('tool',{})
    if set(tool)!={'python','python_sha256','numpy','scipy','superlu_sha256'} or any(not isinstance(v,str) or not v for v in tool.values()):
        raise ValueError('Complete recorded numerical tool identity required')
    if any(re.fullmatch('[0-9a-f]{64}',tool[k]) is None for k in ('python_sha256','superlu_sha256')):raise ValueError('Recorded numerical tool digest differs')
    if require_current_tool and tool!=frozen._tool():raise ValueError('Current numerical tool differs from the recorded execution')
    diagnostics=review_responses(request,worker)
    completed=all(d['response_execution']=='completed' for d in diagnostics)
    if worker.get('conditional_calculation_completed') is not completed or worker.get('execution')!=('completed' if completed else 'model-or-numerical-hold'):
        raise ValueError('Structural execution/numerical response state differs')
    refinement=None
    if completed:
        if len(diagnostics)!=2:raise ValueError('Exactly two refinement records required')
        refinement=[dict(case=a['name'],coarse_max_translation_m=a['maximum_translation_m'],fine_max_translation_m=b['maximum_translation_m'],
            relative_change=None if b['maximum_translation_m']==0 else abs(a['maximum_translation_m']-b['maximum_translation_m'])/abs(b['maximum_translation_m']))
            for a,b in zip(diagnostics[0]['cases'],diagnostics[1]['cases'])]
    if not _same(worker.get('refinement'),refinement):raise ValueError('Structural refinement diagnostics differ')
    if any(worker.get(k) is not None for k in ('approved_strength_allowables','approved_joint_allowables','approved_deflection_or_functional_clearance_limits','hot_wet_retention','fatigue_law','actual_laminate_schedule')) or worker.get('whole_body_qualification') is not False:
        raise ValueError('Unapproved constitutive/interface information cannot become structural qualification')
    if not _same(worker['material_models'],frozen.MATERIALS) or worker['primary_references']!=frozen.PRIMARY_SOURCES:
        raise ValueError('Declared structural material hypotheses/source references differ')
    value=dict(verified=True,candidate_id=request['candidate_id'],evaluation_id=result['run_evaluation_id'],execution=result['execution'],
        producer_source_sha256=request['source_sha256'],verifier_source_sha256=reviewer,diagnostics=diagnostics,
        recorded_tool_identity=tool,current_tool_identity_asserted=require_current_tool,native_reuse_eligible=False,
        numerical_replayed=False,factorization_reexecuted=False,matrix_response_arithmetic_recomputed=True,
        verification_scope='Original input/source/payload integrity and independently reconstructed model/mass/matrix response; JSON scalar normalization only',
        legacy_verification_issue='Equal JSON float versus numpy.float64 rejected by frozen Python-type comparison',
        physical_qualification=False,**FLAGS)
    value['review_id']=identity(value);return value
