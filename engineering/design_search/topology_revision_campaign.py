"""Separate immutable binary-revision experiments; original SIMP is never rerun.

Plan verifies the complete existing parent campaign. Each bounded child worker
rechecks its own parent package, exact source/tool epoch and copied baseline.
Read-only access is cooperative; no filesystem/network sandbox is claimed.
"""
import argparse
from collections import Counter
from copy import deepcopy
import fcntl
import gzip
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

import numpy as np

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest,encoded,identity
from . import civil_topology as parent, topology_revisions as revisions
from . import topology_geometry as geometry, topology_cost, topology_system_cost, portable_gzip

PRODUCER='engineering/design_search/topology_revision_campaign.py'
PARENT_STATE='build/runtime-civil-topology-v1'
STATE='build/runtime-civil-topology-revisions-v1'
FLAGS=dict(parent.FLAGS,current_evaluator_admission=False)
RESOURCES=dict(maximum_address_space_bytes=1024**3,maximum_cpu_seconds=140,
    maximum_trial_wall_seconds=150,workers=1,requested_blas_threads=1,native_jobs=0,
    maximum_rhs=128,replay_rhs=81)
PROPOSAL_POLICY=dict(maximum_elements=1920,maximum_operations=1_000_000,time_budget_s=2.)
MAX_JSON=64*1024**2


def _seal(value,key):value[key]=identity(value);return value
def _json(value):return parent._json(value)


def _ordinary(path):
    p=Path(path).absolute()
    if '..' in p.parts or any(x.is_symlink() for x in (p,*p.parents)):
        raise ValueError('Ordinary unlinked revision evidence path required')
    return p


def _read(path,compressed=False):
    p=_ordinary(path)
    if not p.is_file() or p.stat().st_size>MAX_JSON:raise ValueError('Bounded ordinary revision record required')
    if compressed:
        with gzip.open(p,'rb') as stream:raw=stream.read(MAX_JSON+1)
    else:raw=p.read_bytes()
    if len(raw)>MAX_JSON:raise ValueError('Revision record decompression exceeds budget')
    return json.loads(raw)


def _write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    raw=encoded(_json(value))
    if path.name.endswith('.gz'):raw=portable_gzip.compress(raw)
    temporary=path.with_name(path.name+'.tmp');temporary.write_bytes(raw);temporary.replace(path)


def _source_epoch(root,parent_plan):
    epoch=parent.sources(root,parent_plan['load_context'])
    if epoch!=parent_plan['source_sha256']:raise ValueError('Frozen parent producer epoch differs')
    for name,module in ((PRODUCER,sys.modules[__name__]),(revisions.PRODUCER,revisions)):
        path=Path(root)/name
        if not path.is_file() or digest(path)!=digest(module.__file__):
            raise ValueError('Executing revision producer differs from explicit root')
        epoch[name]=digest(path)
    return dict(sorted(epoch.items()))


def _passive(mask,spec):
    nz,nx=mask.shape;g=spec['geometry']
    if (nx,nz)!=(spec['search']['nx'],spec['search']['nz']):raise ValueError('Parent array grid differs from request')
    centres=np.array([(g['span_m']*(i+.5)/nx,g['web_height_m']*(j+.5)/nz)
        for j in range(nz) for i in range(nx)])
    return parent._passive(dict(element_centres=centres),spec).reshape(mask.shape)


def _parent_data(folder,row,configured,baseline_ref):
    result=parent._read_attempt(folder,row,configured,baseline_ref)
    if (result is None or result.get('execution')!='completed' or result.get('optimization') is None
            or result['trial']['kind']!='optimized-density'):
        raise ValueError('Exact completed original SIMP result required')
    if (result['coarse_replay']['execution']=='completed' and result['fine_replay']['execution']=='completed'):
        raise ValueError('Revision matrix is restricted to failed original binary parents')
    output=Path(folder)/'trials'/row['trial_id'];array_path=_ordinary(output/'arrays.npz')
    if array_path.stat().st_size>MAX_JSON:raise ValueError('Parent arrays package exceeds budget')
    with np.load(array_path,allow_pickle=False) as arrays:
        mask=arrays['binary_occupancy'].copy();rho=arrays['density_field'].copy()
    if (mask.dtype.kind!='b' or mask.ndim!=2 or mask.size>1920 or rho.shape!=mask.shape
            or not np.array_equal(rho.ravel(),np.asarray(result['optimization']['densities']))):
        raise ValueError('Original density/occupancy does not match successful SIMP state')
    passive=_passive(mask,configured['specification'])
    binding=revisions.make_parent_input(result['physical_geometry'],mask,rho,passive,
        parent_evaluation_id=result['evaluation_id'],parent_request_id=row['request_id'],
        arrays_package_sha256=digest(array_path),required_passive_cell_ids=np.flatnonzero(passive).tolist())
    files={name:digest(_ordinary(output/name)) for name in ('request.json','attempt.json','worker.json','result.json.gz','arrays.npz')}
    return result,mask,rho,passive,dict(parent_trial_id=row['trial_id'],parent_attempt_id=row['attempt_id'],
        parent_request_id=row['request_id'],parent_evaluation_id=result['evaluation_id'],
        parent_candidate_id=result['physical_geometry']['candidate_id'],parent_input=binding,
        parent_files_sha256=files)


def _verified_parents(folder,root):
    folder=_ordinary(folder)
    if not all((folder/p).exists() for p in ('state.json','baseline.json.gz','trials')):
        raise ValueError('Existing complete parent state required; no parent generation is permitted')
    state=parent._state(folder,root)
    if state['pending_trial_ids'] or len(state['completed'])!=7:
        raise ValueError('All seven original attempts must be terminal before child planning')
    records=[]
    by_id={t['trial_id']:t for t in state['plan']['trials']}
    for row in state['completed']:
        if by_id[row['trial_id']]['kind']=='full-solid-reference':continue
        records.append(_parent_data(folder,row,state['plan'],state['baseline'])[-1])
    if len(records)!=6:raise ValueError('Exactly six failed original SIMP parents required')
    return state,records


def plan(root=ROOT,*,parent_state=None):
    """Read and verify parents; creates no state, baseline or numerical execution."""
    root=Path(root).resolve();folder=_ordinary(parent_state or root/PARENT_STATE)
    state,records=_verified_parents(folder,root)
    if state['plan']['tool_context']!=parent.tool_context():raise ValueError('Parent numerical tools differ')
    children=[]
    for record in sorted(records,key=lambda r:r['parent_trial_id']):
        for strategy in revisions.STRATEGIES:
            child=dict(record,strategy=strategy);_seal(child,'trial_id');children.append(child)
    value=dict(schema='osr-topology-revision-plan/1',parent_state_path=str(folder),
        parent_state_sha256=digest(folder/'state.json'),parent_plan=deepcopy(state['plan']),
        parent_campaign_id=state['plan']['campaign_id'],baseline=deepcopy(state['baseline']),
        source_sha256=_source_epoch(root,state['plan']),tool_context=deepcopy(state['plan']['tool_context']),
        resources=dict(RESOURCES),proposal_policy=dict(PROPOSAL_POLICY),children=children,
        parent_count=6,maximum_children=12,SIMP_reexecuted=False,selection_purpose='next-experiment',**FLAGS)
    return _seal(value,'campaign_id')


def _check_plan(configured,root):
    parent._sealed(configured,'campaign_id');parent._sealed(configured['parent_plan'],'campaign_id')
    if (configured.get('schema')!='osr-topology-revision-plan/1' or configured['resources']!=RESOURCES
            or configured['proposal_policy']!=PROPOSAL_POLICY or len(configured['children'])!=12
            or configured['parent_count']!=6 or configured['maximum_children']!=12
            or configured['SIMP_reexecuted'] is not False or any(configured.get(k) is not False for k in FLAGS)):
        raise ValueError('Bounded non-promoting revision plan differs')
    pairs=[];seen=set()
    for child in configured['children']:
        parent._sealed(child,'trial_id');parent._sealed(child['parent_input'],'parent_input_id')
        if child['trial_id'] in seen or child['strategy'] not in revisions.STRATEGIES:raise ValueError('Duplicate/unknown child trial')
        seen.add(child['trial_id']);pairs.append((child['parent_trial_id'],child['strategy']))
    counts=Counter(p for p,_ in pairs)
    if (len(counts)!=6 or any(n!=2 for n in counts.values())
            or set(pairs)!={(p,s) for p in counts for s in revisions.STRATEGIES}):
        raise ValueError('Exactly two strategies per original parent required')
    if (configured['source_sha256']!=_source_epoch(root,configured['parent_plan'])
            or configured['tool_context']!=parent.tool_context()):
        raise ValueError('Revision source or numerical tool epoch changed')
    folder=_ordinary(configured['parent_state_path'])
    if digest(folder/'state.json')!=configured['parent_state_sha256']:
        raise ValueError('Immutable original parent state bytes differ')
    if digest(folder/'baseline.json.gz')!=configured['baseline']['file_sha256']:
        raise ValueError('Original baseline bytes differ')
    return configured


def _request(configured,child):
    return _seal(dict(schema='osr-topology-revision-request/1',campaign_id=configured['campaign_id'],
        child=deepcopy(child),source_sha256=deepcopy(configured['source_sha256']),
        tool_context=deepcopy(configured['tool_context']),baseline=deepcopy(configured['baseline']),
        resources=dict(configured['resources']),**FLAGS),'request_id')


def _own_parent(configured,child):
    folder=_ordinary(configured['parent_state_path']);state=_read(folder/'state.json')
    if state['plan']!=configured['parent_plan'] or state['baseline']!=configured['baseline']:
        raise ValueError('Original parent plan/baseline differs')
    row=next((r for r in state['completed'] if r['trial_id']==child['parent_trial_id']),None)
    if row is None:raise ValueError('Original parent trial absent')
    result,mask,rho,passive,record=_parent_data(folder,row,state['plan'],state['baseline'])
    expected=dict(record,strategy=child['strategy']);_seal(expected,'trial_id')
    if child!=expected:raise ValueError('Child binding differs from exact own-parent artifacts')
    # Parent integrity and ancestry were checked above. Retain only the fields
    # needed by the child so its independent cost ledger fits the worker budget.
    original = {key: result[key] for key in ('physical_geometry', 'representative_poses')}
    return original,mask,rho,passive


def _labels(cases):
    names=('load_case','vehicle_mass_case','span_mass_case','pose')
    values=[tuple(row[k] for k in names) for row in cases]
    if len(values)!=81 or len(set(values))!=81:raise ValueError('Complete disjoint 81-case binary replay required')
    return values


def _evaluate(request,configured,original,mask,rho,passive,baseline,*,root=ROOT,checkpoint=None):
    """Internal worker calculation; callers must first verify its immutable inputs."""
    child=request['child'];spec=configured['parent_plan']['specification'];g=spec['geometry']
    def save(phase,data,arrays=None):
        if checkpoint:checkpoint(phase,data,{} if arrays is None else arrays)
    proposal=revisions.propose(child['parent_input'],original['physical_geometry'],mask,rho,passive,
        strategy=child['strategy'],**configured['proposal_policy'])
    realized=np.asarray(proposal['occupancy'],dtype=bool)
    save('proposal',proposal,dict(binary_occupancy=realized,original_density_field=rho))
    result=dict(schema='osr-topology-revision-result/1',request_id=request['request_id'],trial_id=child['trial_id'],
        parent_campaign_id=configured['parent_campaign_id'],parent_trial_id=child['parent_trial_id'],
        parent_request_id=child['parent_request_id'],parent_evaluation_id=child['parent_evaluation_id'],
        parent_candidate_id=child['parent_candidate_id'],parent_input_id=child['parent_input']['parent_input_id'],
        original_arrays_package_sha256=child['parent_input']['original_arrays_package_sha256'],
        proposal=proposal,revision_id=proposal['revision_id'],proposal_evaluation_id=proposal['evaluation_id'],
        SIMP_reexecuted=False,density_field_used_as_FE_material=False,void_stiffness_credited=False,
        baseline_id=baseline['baseline_id'],load_context_id=baseline['load_context_id'],
        integrated_selection=None,installed_mass_complete=False,**FLAGS)
    raw=dict(binary_occupancy=realized,original_density_field=rho)
    if proposal['execution']!='proposal-generated':
        result.update(execution='proposal-rejected',numerical_evaluation_execution='not-run',
            failure_reason=proposal['failure_reason'],physical_geometry=None,system_cost=None)
        return _json(_seal(result,'evaluation_id')),raw
    candidate=proposal['proposed_geometry'];geometry.validate(candidate)
    if candidate!=geometry.realize(realized,**g) or candidate['candidate_id']==original['physical_geometry']['candidate_id']:
        raise ValueError('Explicit child physical geometry differs or is unchanged')
    cost_spec=configured['parent_plan']['cost_specification'];e=spec['elastic_hypotheses']
    quantity=geometry.quantities(candidate,dict(steel=e['steel_density_kg_m3'],concrete=e['concrete_density_kg_m3']),
        reserves_kg=cost_spec['reserve_mass_kg'],module_length_m=cost_spec['module_length_m'])
    cost=topology_cost.estimate(candidate,quantity,cost_spec,baseline['assumptions'])
    save('quantities-and-cost',dict(physical_geometry=candidate,quantities=quantity,span_cost=cost))
    poses=deepcopy(original['representative_poses'])
    coarse_raw,coarse=parent.replay(parent.mesh(spec),realized,spec,baseline['load_context'],quantity,poses)
    save('coarse',coarse,dict(displacements=coarse_raw.get('displacements')))
    finer=np.repeat(np.repeat(realized,2,axis=0),2,axis=1)
    if geometry.realize(finer,**g)['candidate_id']!=candidate['candidate_id']:
        raise ValueError('Refinement changed child physical candidate')
    fine_raw,fine=parent.replay(parent.mesh(spec,2),finer,spec,baseline['load_context'],quantity,poses)
    save('fine',fine,dict(displacements=fine_raw.get('displacements')))
    changes=None
    for analysis in (coarse,fine):
        if analysis['execution']=='completed':_labels(analysis['cases'])
    if coarse['execution']==fine['execution']=='completed':
        if _labels(coarse['cases'])!=_labels(fine['cases']):raise ValueError('Coarse/fine load-case order differs')
        if coarse['declared_residual_request_met'] and fine['declared_residual_request_met']:
            changes=[abs(a['compliance_J']-b['compliance_J'])/max(abs(b['compliance_J']),1e-20)
                for a,b in zip(coarse['cases'],fine['cases'])]
    supports=parent.support_demands(candidate,quantity,baseline,spec)
    system=topology_system_cost.compare(candidate,quantity,cost,baseline,supports,root=root)
    if (set(system['cases'])!={'low','base','high'} or any(len(row['scope_totals_iqd'])!=14
            or any(len(values)!=3 for values in row['scope_totals_iqd'].values()) for row in system['cases'].values())):
        raise ValueError('Complete three-mass/fourteen-scope system cost required')
    save('whole-system-cost',dict(support_demands=supports,system_cost=system))
    result.update(execution='completed',numerical_evaluation_execution='binary-replay-attempted',
        physical_geometry=candidate,candidate_id=candidate['candidate_id'],composition_candidate_id=system['candidate_id'],
        quantities=quantity,span_cost=cost,support_demands=supports,system_cost=system,
        representative_poses=poses,coarse_replay=coarse,fine_replay=fine,
        same_physical_geometry_refined=True,compliance_relative_changes=changes,
        numerical_refinement_status='mesh-unresolved' if changes is None or max(changes)>spec['replay']['two_mesh_compliance_change_target'] else 'two-mesh-comparison-within-declared-target',
        material_strength_or_buckling_qualified=False,physical_geometry_repaired_silently=False)
    raw.update(coarse_displacements=coarse_raw.get('displacements'),fine_displacements=fine_raw.get('displacements'))
    return _json(_seal(result,'evaluation_id')),raw


def _read_attempt(folder,row,configured):
    parent._sealed(row,'attempt_id');output=_ordinary(Path(folder)/'trials'/row['trial_id'])
    if _read(output/'attempt.json')!=row:raise ValueError('Revision state/attempt differs')
    actual={p.name:digest(p) for p in output.iterdir() if p.name!='attempt.json' and p.is_file()}
    if any(p.is_symlink() or not p.is_file() for p in output.iterdir()) or actual!=row['files_sha256']:
        raise ValueError('Revision immutable attempt payload differs')
    child=next((c for c in configured['children'] if c['trial_id']==row['trial_id']),None)
    if child is None or _read(output/'request.json')!=_request(configured,child):raise ValueError('Revision request differs')
    request=_request(configured,child)
    if row['request_id']!=request['request_id']:raise ValueError('Revision attempt request ID differs')
    for path in output.glob('checkpoint-*.json.gz'):
        check=_read(path,True);parent._sealed(check,'checkpoint_id')
        if check['request_id']!=request['request_id']:raise ValueError('Foreign revision checkpoint')
    if row['execution']!='worker-completed' or row['returncode']!=0:return None
    receipt=_read(output/'worker.json');parent._sealed(receipt,'receipt_id')
    if (receipt['request_id']!=request['request_id'] or row['worker_receipt_id']!=receipt['receipt_id']
            or receipt['trial_id']!=child['trial_id'] or receipt['campaign_id']!=configured['campaign_id']
            or receipt['source_sha256']!=configured['source_sha256'] or receipt['tool_context']!=configured['tool_context']
            or receipt['observed_worker_environment']!=configured['tool_context']['worker_environment']
            or receipt['native_jobs_dispatched']!=0 or receipt['SIMP_reexecuted'] is not False
            or receipt['limits']!={'RLIMIT_AS_bytes':[RESOURCES['maximum_address_space_bytes']]*2,
                'RLIMIT_CPU_seconds':[RESOURCES['maximum_cpu_seconds']]*2}
            or any(receipt.get(k) is not False for k in FLAGS)):
        raise ValueError('Revision worker source/tool/disposition differs')
    if set(receipt['files_sha256'])!={'arrays.npz','result.json.gz'}:raise ValueError('Complete revision output hash coverage required')
    for name,wanted in receipt['files_sha256'].items():
        if actual.get(name)!=wanted:raise ValueError('Revision worker payload digest differs')
    result=_read(output/'result.json.gz',True);parent._sealed(result,'evaluation_id')
    bindings=dict(request_id=request['request_id'],trial_id=child['trial_id'],parent_campaign_id=configured['parent_campaign_id'],
        parent_trial_id=child['parent_trial_id'],parent_request_id=child['parent_request_id'],parent_candidate_id=child['parent_candidate_id'],
        parent_evaluation_id=child['parent_evaluation_id'],parent_input_id=child['parent_input']['parent_input_id'],
        original_arrays_package_sha256=child['parent_input']['original_arrays_package_sha256'],baseline_id=configured['baseline']['baseline_id'])
    if (any(result.get(k)!=v for k,v in bindings.items()) or any(result.get(k) is not False for k in FLAGS)
            or result['SIMP_reexecuted'] is not False or result['density_field_used_as_FE_material'] is not False
            or result['void_stiffness_credited'] is not False):
        raise ValueError('Revision result ancestry or disposition differs')
    proposal=result['proposal'];parent._sealed(proposal,'evaluation_id')
    if (proposal['parent_input_id']!=child['parent_input']['parent_input_id'] or proposal['strategy']!=child['strategy']
            or result['revision_id']!=proposal['revision_id'] or result['proposal_evaluation_id']!=proposal['evaluation_id']
            or any(proposal.get(k) is not False for k in revisions.FLAGS)):
        raise ValueError('Revision proposal ancestry or disposition differs')
    with np.load(output/'arrays.npz',allow_pickle=False) as arrays:
        if not np.array_equal(arrays['binary_occupancy'],np.asarray(result['proposal']['occupancy'],dtype=bool)):
            raise ValueError('Revision result and binary arrays differ')
        if revisions._fingerprint(arrays['original_density_field'])!=child['parent_input']['original_density_sha256']:
            raise ValueError('Revision original density binding differs')
        if result['execution']=='completed':
            physical=geometry.realize(arrays['binary_occupancy'])
            if (physical!=result['physical_geometry'] or physical!=proposal['proposed_geometry']
                    or result['candidate_id']!=physical['candidate_id'] or result['candidate_id']==child['parent_candidate_id']):
                raise ValueError('Revision saved physical geometry differs')
    return result


def _state(folder,root=ROOT,*,parent_state=None,create=False):
    folder=_ordinary(folder)
    if not (folder/'state.json').exists():
        if not create:raise ValueError('Existing revision state required')
        configured=plan(root,parent_state=parent_state);ancestor=Path(configured['parent_state_path'])
        if folder==ancestor or folder in ancestor.parents or ancestor in folder.parents:
            raise ValueError('Child and original parent states must be disjoint')
        if (folder/'baseline.json.gz').exists():raise ValueError('Unindexed revision baseline must be preserved')
        folder.mkdir(parents=True,exist_ok=True)
        (folder/'baseline.json.gz').write_bytes((ancestor/'baseline.json.gz').read_bytes())
        _write(folder/'state.json',dict(schema='osr-topology-revision-state/1',plan=configured,
            baseline=deepcopy(configured['baseline']),pending_trial_ids=[c['trial_id'] for c in configured['children']],completed=[]))
    state=_read(folder/'state.json');configured=_check_plan(state['plan'],root)
    ancestor=_ordinary(configured['parent_state_path'])
    if folder==ancestor or folder in ancestor.parents or ancestor in folder.parents:
        raise ValueError('Child and original parent states must be disjoint')
    if parent_state is not None and _ordinary(parent_state)!=ancestor:raise ValueError('Revision parent state path differs')
    if state.get('schema')!='osr-topology-revision-state/1' or state['baseline']!=configured['baseline']:
        raise ValueError('Revision state schema/baseline differs')
    if digest(folder/'baseline.json.gz')!=configured['baseline']['file_sha256']:raise ValueError('Copied baseline bytes differ')
    done=[r['trial_id'] for r in state['completed']];pending=state['pending_trial_ids'];expected={c['trial_id'] for c in configured['children']}
    if len(done)!=len(set(done)) or len(pending)!=len(set(pending)) or set(done)&set(pending) or set(done)|set(pending)!=expected:
        raise ValueError('Revision terminal/pending coverage differs')
    for row in state['completed']:_read_attempt(folder,row,configured)
    return state


def _worker(request_path,output):
    request_path=_ordinary(request_path);output=_ordinary(output);request=_read(request_path)
    parent._sealed(request,'request_id')
    if request.get('resources')!=RESOURCES:raise ValueError('Exact child process resource request required')
    resource.setrlimit(resource.RLIMIT_AS,(RESOURCES['maximum_address_space_bytes'],)*2)
    resource.setrlimit(resource.RLIMIT_CPU,(RESOURCES['maximum_cpu_seconds'],)*2)
    folder=output.parent.parent;state=_read(folder/'state.json');configured=_check_plan(state['plan'],ROOT)
    child=next((c for c in configured['children'] if c['trial_id']==output.name),None)
    if child is None or request_path!=output/'request.json' or request!=_request(configured,child):
        raise ValueError('Child worker request/private output differs')
    expected_env=configured['tool_context']['worker_environment']
    if {k:os.environ.get(k) for k in expected_env}!=expected_env:raise ValueError('Child worker environment differs')
    original,mask,rho,passive=_own_parent(configured,child)
    baseline=parent._baseline(folder,configured['baseline'],ROOT)
    if baseline['load_context']!=configured['parent_plan']['load_context']:raise ValueError('Child baseline/load context differs')
    started=time.monotonic()
    def checkpoint(phase,data,arrays):
        path=output/('checkpoint-'+phase+'.json.gz')
        if path.exists():raise ValueError('Prior revision checkpoint must not be overwritten')
        record=_seal(dict(schema='osr-topology-revision-checkpoint/1',request_id=request['request_id'],phase=phase,data=_json(data),**FLAGS),'checkpoint_id')
        _write(path,record);values={k:v for k,v in arrays.items() if v is not None}
        if values:np.savez_compressed(output/('checkpoint-'+phase+'.npz'),**values)
    result,raw=_evaluate(request,configured,original,mask,rho,passive,baseline,root=ROOT,checkpoint=checkpoint)
    _check_plan(configured,ROOT)
    np.savez_compressed(output/'arrays.npz',**{k:v for k,v in raw.items() if v is not None})
    _write(output/'result.json.gz',result)
    receipt=dict(schema='osr-topology-revision-worker/1',request_id=request['request_id'],trial_id=child['trial_id'],
        campaign_id=configured['campaign_id'],source_sha256=configured['source_sha256'],tool_context=configured['tool_context'],
        observed_worker_environment={k:os.environ.get(k) for k in expected_env},
        observed_threads_after_trial=len(list(Path('/proc/self/task').iterdir())),
        elapsed_seconds=time.monotonic()-started,max_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        limits=dict(RLIMIT_AS_bytes=resource.getrlimit(resource.RLIMIT_AS),RLIMIT_CPU_seconds=resource.getrlimit(resource.RLIMIT_CPU)),
        native_jobs_dispatched=0,SIMP_reexecuted=False,operating_system_filesystem_or_network_isolation=False,
        files_sha256={p.name:digest(p) for p in output.iterdir() if p.is_file() and p.name in ('arrays.npz','result.json.gz')},**FLAGS)
    _seal(receipt,'receipt_id');_write(output/'worker.json',receipt)
    return dict(completed=True,receipt_id=receipt['receipt_id'],execution=result['execution'],**FLAGS)


def run(folder,*,root=ROOT,max_trials=1,parent_state=None):
    root=Path(root).resolve();folder=_ordinary(folder)
    if type(max_trials) is not int or not 0<=max_trials<=12:raise ValueError('Zero to twelve child attempts per invocation required')
    recorded=_read(folder/'state.json')['plan']['parent_state_path'] if (folder/'state.json').exists() else None
    ancestor=_ordinary(parent_state or recorded or root/PARENT_STATE)
    if folder==ancestor or folder in ancestor.parents or ancestor in folder.parents:
        raise ValueError('Child and parent states must be disjoint')
    folder.mkdir(parents=True,exist_ok=True)
    with (folder/'run.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        state=_state(folder,root,parent_state=parent_state,create=True);configured=state['plan']
        by_id={c['trial_id']:c for c in configured['children']}
        for trial_id in list(state['pending_trial_ids'])[:max_trials]:
            child=by_id[trial_id];output=folder/'trials'/trial_id
            if output.exists():raise ValueError('Unfinished child directory exists; inspect and preserve before any retry')
            output.mkdir(parents=True);request=_request(configured,child);_write(output/'request.json',request)
            environment=dict(os.environ,**configured['tool_context']['worker_environment'],PYTHONPATH=str(root))
            started=time.monotonic();returncode=-999;execution='spawn-failed';interruption=None;process=None
            with (output/'stdout.log').open('wb') as stdout,(output/'stderr.log').open('wb') as stderr:
                try:
                    command=[sys.executable,'-m','engineering.design_search.topology_revision_campaign',
                        '_worker',str(output/'request.json'),str(output)]
                    process=subprocess.Popen(command,cwd=root,env=environment,
                        stdout=stdout,stderr=stderr,start_new_session=True)
                    _write(output/'process.json',dict(pid=process.pid,request_id=request['request_id'],command=command,
                        working_directory=str(root),requested_worker_environment=configured['tool_context']['worker_environment'],started_at=time.time()))
                    try:returncode=process.wait(timeout=RESOURCES['maximum_trial_wall_seconds']);execution='worker-completed' if returncode==0 else 'worker-failed'
                    except subprocess.TimeoutExpired:
                        try:os.killpg(process.pid,signal.SIGKILL)
                        except ProcessLookupError:pass
                        returncode=process.wait();execution='wall-timeout'
                except BaseException as exc:
                    if process is not None and process.poll() is None:
                        try:os.killpg(process.pid,signal.SIGKILL)
                        except ProcessLookupError:pass
                        returncode=process.wait()
                    stderr.write((type(exc).__name__+': '+str(exc)+'\n').encode())
                    if not isinstance(exc,Exception):interruption=exc;execution='coordinator-interrupted'
            row=dict(trial_id=trial_id,request_id=request['request_id'],returncode=returncode,execution=execution,
                runtime_seconds=time.monotonic()-started,physical_failure_inferred=False)
            if execution=='worker-completed':
                try:
                    receipt=_read(output/'worker.json');parent._sealed(receipt,'receipt_id')
                    if receipt['request_id']!=request['request_id']:raise ValueError('Foreign worker receipt')
                    row['worker_receipt_id']=receipt['receipt_id']
                except (OSError,ValueError,KeyError) as exc:
                    row['execution']='worker-protocol-failed';_write(output/'coordinator-error.json',dict(error=str(exc)))
            row['files_sha256']={p.name:digest(p) for p in output.iterdir() if p.is_file()};_seal(row,'attempt_id')
            _write(output/'attempt.json',row)
            if row['execution']=='worker-completed':
                try:_read_attempt(folder,row,configured)
                except (OSError,ValueError,KeyError,TypeError) as exc:
                    _write(output/'coordinator-error.json',dict(error=str(exc)))
                    row.pop('attempt_id');row['execution']='worker-protocol-failed'
                    row['files_sha256']={p.name:digest(p) for p in output.iterdir() if p.is_file() and p.name!='attempt.json'}
                    _seal(row,'attempt_id');_write(output/'attempt.json',row)
            state['completed'].append(row);state['pending_trial_ids'].remove(trial_id);_write(folder/'state.json',state)
            if interruption is not None:raise interruption
        return dict(campaign_id=configured['campaign_id'],completed=len(state['completed']),pending=len(state['pending_trial_ids']),
            failed=sum(r['execution']!='worker-completed' for r in state['completed']),SIMP_reexecuted=False,**FLAGS)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('plan','run','_worker'))
    parser.add_argument('arguments',nargs='*');parser.add_argument('--state',type=Path,default=ROOT/STATE)
    parser.add_argument('--parent-state',type=Path,default=ROOT/PARENT_STATE);parser.add_argument('--max-trials',type=int,default=1)
    args=parser.parse_args(argv)
    if args.action=='plan':value=plan(parent_state=args.parent_state)
    elif args.action=='run':value=run(args.state,parent_state=args.parent_state,max_trials=args.max_trials)
    else:
        if len(args.arguments)!=2:raise ValueError('Internal worker requires exact request and output paths')
        value=_worker(*args.arguments)
    print(json.dumps(value,sort_keys=True,allow_nan=False));return 0


if __name__=='__main__':raise SystemExit(main())
