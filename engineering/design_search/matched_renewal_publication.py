"""Closed, replayed publication of conditional matched-renewal research.

Caller-supplied trusted parent, request and evaluation IDs are mandatory. A
self-sealed file or a completed replay cannot grant engineering acceptance.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse
import json
import os
import shutil
import tempfile

from engineering.station_rail.common import digest, encoded, identity
from . import matched_renewal_research as research, flanged_system_cost_publication as prior

ROOT=Path(__file__).resolve().parents[2]
PRODUCER='engineering/design_search/matched_renewal_publication.py'
OUTPUT='docs/design-engine/matched-renewal-research'
SCHEMA='osr-matched-renewal-publication/1'
RESULT_SCHEMA='osr-matched-renewal-publication-result/1'
FLAGS=('physical_accepted','engineering_accepted','manufacturing_release','operating_release',
       'physical_journey_completed','service_qualified','selected_reference_changed')
EPOCHS={
    'epoch-v1':('worker.py','worker.log','reconstructed-producer.py'),
    'epoch-v2':('producer.py','worker.py','worker.log','result.json'),
    'epoch-v3':('producer.py','worker.py','request.json','worker.log','result.json'),
    'epoch-v4':('producer.py','worker.py','request.json','worker.log','result.json','check.py','check.log'),
    'epoch-v5':('producer.py','worker.py','request.json','worker.log','result.json','check.py','check.log','execution.json'),
}


def _identity(value,key):
    if not isinstance(value,dict) or value.get(key)!=identity({k:v for k,v in value.items() if k!=key}):
        raise ValueError('Identity differs: '+key)


def _hex(value):
    if not isinstance(value,str) or len(value)!=64 or any(c not in '0123456789abcdef' for c in value):
        raise ValueError('Externally trusted SHA256 identity required')
    return value


def _epoch(root):
    current=digest(Path(__file__))
    p=Path(root)/PRODUCER
    if not p.is_file() or digest(p)!=current:raise ValueError('Publication executing source differs from declared root')
    return current


def _snapshot(folder):
    folder=prior._directory(folder);data={}
    for epoch,names in EPOCHS.items():
        d=prior._directory(folder/epoch)
        if {p.name for p in d.iterdir()}!=set(names):raise ValueError('Worker epoch file inventory differs: '+epoch)
        for name in names:data[epoch+'/'+name]=prior._file(d/name)
    return data


def _validate(raw,root,parent_folder,expected_parent,expected_topology,expected_flanged,expected_request,expected_evaluation):
    for x in (expected_parent,expected_topology,expected_flanged,expected_request,expected_evaluation):_hex(x)
    prefix='epoch-v5/'
    request=prior._json(raw[prefix+'request.json'],canonical=False)
    expected=sha256(json.dumps({k:v for k,v in request.items() if k!='request_id'},sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if (request.get('schema')!='osr-private-matched-renewal-request/1' or request.get('request_id')!=expected
            or expected!=expected_request or request.get('publication_manifest_id')!=expected_parent
            or request.get('topology_manifest_id')!=expected_topology or request.get('flanged_manifest_id')!=expected_flanged
            or request.get('limits')!=dict(address_space_bytes=1073741824,cpu_seconds=60,wall_seconds=60,blas_threads=1)
            or request.get('numerical_native_solver') is not False):raise ValueError('Pinned worker request, parents or limits differ')
    if any(request.get(k) is not False for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release')):
        raise ValueError('Request cannot promote research')
    manifest,parent_record=prior._check(parent_folder,expected_parent)
    if (request['publication_manifest_sha256']!=digest(Path(parent_folder)/'manifest.json')
            or parent_record['parent_publications']['topology_manifest_id']!=expected_topology
            or parent_record['parent_publications']['flanged_manifest_id']!=expected_flanged):
        raise ValueError('Trusted parent publication ancestry differs')
    if (request['producer_sha256']!=sha256(raw[prefix+'producer.py']).hexdigest()
            or request['producer_sha256']!=digest(Path(root)/research.PRODUCER)
            or request['worker_sha256']!=sha256(raw[prefix+'worker.py']).hexdigest()):
        raise ValueError('Worker producer or runner bytes differ')
    execution=prior._json(raw[prefix+'execution.json'],canonical=False);_identity(execution,'execution_id')
    if (execution.get('schema')!='osr-matched-renewal-private-execution/1' or execution.get('request_id')!=expected_request
            or execution.get('evaluation_id')!=expected_evaluation or execution.get('execution')!='completed'
            or execution.get('returncode')!=0 or execution.get('limits')!=request['limits']
            or any(execution.get(k) is not False for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release'))):
        raise ValueError('Worker execution disposition differs')
    expected_files=('producer.py','worker.py','request.json','result.json','worker.log','check.py','check.log')
    if execution.get('artifact_sha256')!={n:sha256(raw[prefix+n]).hexdigest() for n in expected_files}:
        raise ValueError('Worker execution artifact bytes differ')
    record=prior._json(raw[prefix+'result.json'],canonical=False);_identity(record,'evaluation_id')
    if (record.get('schema')!='osr-matched-renewal-research/1' or record['evaluation_id']!=expected_evaluation
            or record.get('parent_publication_manifest_id')!=expected_parent or record.get('topology_manifest_id')!=expected_topology
            or record.get('flanged_span_manifest_id')!=expected_flanged or record.get('integrated_selection') is not None
            or record.get('whole_life_ranking_allowed') is not False or record.get('conditional_scenario_deltas_only') is not True
            or record.get('installed_mass_complete') is not False or any(record.get(k) is not False for k in FLAGS)):
        raise ValueError('Result source, identity or nonpromotion differs')
    if record.get('source_sha256',{}).get(research.PRODUCER)!=request['producer_sha256']:
        raise ValueError('Result producer epoch differs')
    research.cost.base._source_check(record['source_sha256'],root)
    if set(record['comparisons'])!=set(prior.NAMES) or set(record['reference_compositions'])!={'unsealed','outer_sealer'}:
        raise ValueError('Missing candidates or surface treatments')
    for treatment in record['reference_compositions'].values():
        if set(treatment['mass_cases'])!=set(research.CASES):raise ValueError('Missing reference mass cases')
        for case in treatment['mass_cases'].values():
            if set(case['scope_totals_iqd'])!=set(research.cost.model.SCOPES) or len(case['rows'])!=3:
                raise ValueError('Reference fourteen-scope accounting differs')
    for c in record['comparisons'].values():
        if set(c['mass_cases'])!=set(research.CASES):raise ValueError('Missing flanged mass cases')
        for mass,case in c['mass_cases'].items():
            if set(case['flanged']['scope_totals_iqd'])!=set(research.cost.model.SCOPES) or set(case['reference_deltas'])!={'unsealed','outer_sealer'}:
                raise ValueError('Candidate fourteen-scope accounting differs')
            for name,delta in case['reference_deltas'].items():
                ref=record['reference_compositions'][name]['mass_cases'][mass]
                if (delta['reference_candidate_id']!=ref['candidate_id'] or delta['reference_civil_physical_id']!=ref['evaluation_ancestry']['canonical_civil_physical_id']
                        or any(len(delta[k])!=3 for k in ('capex_delta_iqd','npv_delta_iqd','overlap_sensitivity_delta_iqd'))):
                    raise ValueError('Mixed reference identity or scenario count')
    if (b'Exit status: 1' not in raw['epoch-v1/worker.log'] or b'Candidate ancestry mismatch' not in raw['epoch-v1/worker.log']
            or b'Exit status: 0' not in raw[prefix+'worker.log'] or expected_evaluation.encode() not in raw[prefix+'worker.log']
            or b'Exit status: 0' not in raw[prefix+'check.log']):raise ValueError('Retained worker or checker log disposition differs')
    return record,execution


def _readme(value):
    return ('# Matched renewal research\n\n'
        'This closed record compares three flanged-span research compositions with distinct concrete reference compositions for each vehicle mass case. '
        'The concrete references use four hypothetical steel–elastomer bearing assemblies per span, either untreated outer concrete or a separately assumed outer sealer. '
        'Rates, QA, transport, erection-hour partition, access, renewals, maintenance-overlap sensitivity and 14 cost scopes are recorded in the original result.\n\n'
        'The costs are conditional Class C scenarios. The bearing design and site, soil, moving loads, torsion, prestress transfer, temporary stability, '
        'crane capacity and magnetic-gap deformation remain unverified. No whole-life ranking, reference change, physical acceptance, manufacturing release '
        'or movement authority follows. The successful worker and failed or superseded epochs are retained; v1 source is reconstructed and not independently attested.\n\n'
        'Current-source verification reruns the analytical 54-scenario calculation with externally pinned parent, request and evaluation identities. '
        'Recorded worker runtime was captured after execution and is not independent attestation.\n')


def _publication(record,execution,source,request_id):
    r=dict(schema=RESULT_SCHEMA,source_sha256=source,worker_request_id=request_id,worker_execution_id=execution['execution_id'],
        worker_evaluation_id=record['evaluation_id'],parent_publication_manifest_id=record['parent_publication_manifest_id'],
        topology_manifest_id=record['topology_manifest_id'],flanged_span_manifest_id=record['flanged_span_manifest_id'],
        worker_runtime_observed_after_execution=deepcopy(execution['runtime_observed_after_worker']),
        runtime_attestation='Recorded from the same executable after execution; no independent runtime or isolation attestation',
        attempts=['epoch-v1: failed identity mismatch; producer reconstructed','epoch-v2: superseded',
                  'epoch-v3: held, mixed reference civil identity','epoch-v4: held, initial coating QA omitted',
                  'epoch-v5: completed, conditional research only'],
        comparison_scenarios=54,whole_life_ranking_allowed=False,integrated_selection=None,installed_mass_complete=False,
        **{k:False for k in FLAGS})
    r['publication_id']=identity(r);return r


def _payload(folder):
    folder=prior._directory(folder);expected={'README.md','result.json'}|{'original/'+e+'/'+n for e,names in EPOCHS.items() for n in names}
    entries=list(folder.rglob('*'))
    if any(p.is_symlink() for p in entries):raise ValueError('Symlink in publication rejected')
    directories={str(p.relative_to(folder)) for p in entries if p.is_dir()}
    if directories!={'original'}|{'original/'+epoch for epoch in EPOCHS}:raise ValueError('Closed publication directory inventory differs')
    actual={str(p.relative_to(folder)) for p in entries if p.is_file()}
    if actual!=expected|{'manifest.json'}:raise ValueError('Closed publication file inventory differs')
    return {name:sha256(prior._file(folder/name)).hexdigest() for name in sorted(expected)}


def _check(folder,expected_manifest):
    _hex(expected_manifest);folder=prior._directory(folder);m=prior._json(prior._file(folder/'manifest.json'));_identity(m,'manifest_id')
    if m.get('schema')!=SCHEMA or m['manifest_id']!=expected_manifest or m.get('files_sha256')!=_payload(folder):
        raise ValueError('Publication identity or closed payload differs')
    r=prior._json(prior._file(folder/'result.json'));_identity(r,'publication_id')
    if (r.get('schema')!=RESULT_SCHEMA or r['publication_id']!=m.get('publication_id') or r.get('source_sha256')!=m.get('source_sha256')
            or any(m.get(k) is not False or r.get(k) is not False for k in FLAGS)
            or r.get('whole_life_ranking_allowed') is not False or r.get('integrated_selection') is not None
            or prior._file(folder/'README.md')!=_readme(r).encode()):raise ValueError('Publication record or nonpromotion differs')
    return m,r


def _replay(root,parent_folder,request_id,parent_id,topology_id,flanged_id,evaluation_id,raw):
    recorded,execution=_validate(raw,root,parent_folder,parent_id,topology_id,flanged_id,request_id,evaluation_id)
    current=research.compare(parent_folder,root=root,expected_publication_manifest_id=parent_id,
        expected_topology_manifest_id=topology_id,expected_flanged_manifest_id=flanged_id)
    if current!=recorded:
        raise ValueError('Current 54-scenario analytical replay differs from retained result')
    return recorded,execution


def publish(state,*,root=ROOT,output=None,parent_folder=None,expected_parent_manifest_id,
            expected_topology_manifest_id,expected_flanged_manifest_id,expected_request_id,expected_evaluation_id):
    root=prior._directory(root);source_epoch=_epoch(root);state=prior._directory(state)
    parent=prior._directory(parent_folder or root/prior.OUTPUT)
    target=Path(output).absolute() if output is not None else root/OUTPUT
    target.parent.mkdir(parents=True,exist_ok=True)
    for forbidden in (state,parent,root):
        if target==forbidden or target in forbidden.parents:raise ValueError('Output may not replace an input or source root')
    if target.exists() or target.is_symlink():raise FileExistsError('Immutable output already exists')
    raw=_snapshot(state)
    record,execution=_replay(root,parent,expected_request_id,expected_parent_manifest_id,
        expected_topology_manifest_id,expected_flanged_manifest_id,expected_evaluation_id,raw)
    source=dict(record['source_sha256']);source[PRODUCER]=source_epoch;source=dict(sorted(source.items()))
    value=_publication(record,execution,source,expected_request_id)
    if (_snapshot(state)!=raw or _epoch(root)!=source_epoch):raise ValueError('Source or retained worker epoch changed during replay')
    research.cost.base._source_check(source,root)
    prior._check(parent,expected_parent_manifest_id)
    stage=Path(tempfile.mkdtemp(prefix='.matched-renewal-',dir=target.parent));reserved=False
    try:
        for name,data in raw.items():
            dest=stage/'original'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        (stage/'README.md').write_text(_readme(value),encoding='utf-8')
        (stage/'result.json').write_bytes(encoded(value))
        paths=['README.md','result.json']+['original/'+name for name in raw]
        manifest=dict(schema=SCHEMA,source_sha256=source,publication_id=value['publication_id'],
            files_sha256={name:digest(stage/name) for name in sorted(paths)},**{k:False for k in FLAGS})
        manifest['manifest_id']=identity(manifest);(stage/'manifest.json').write_bytes(encoded(manifest))
        _check(stage,manifest['manifest_id'])
        # Recheck inputs immediately before the atomic handoff.
        if _snapshot(state)!=raw or _epoch(root)!=source_epoch:raise ValueError('Inputs changed before publication')
        research.cost.base._source_check(source,root);prior._check(parent,expected_parent_manifest_id)
        os.mkdir(target);reserved=True;os.rename(stage,target);reserved=False
        return manifest
    finally:
        if stage.exists():shutil.rmtree(stage)
        if reserved and target.is_dir():target.rmdir()


def verify(output=None,*,root=ROOT,parent_folder=None,expected_manifest_id,expected_parent_manifest_id,
           expected_topology_manifest_id,expected_flanged_manifest_id,expected_request_id,expected_evaluation_id):
    root=prior._directory(root);source_epoch=_epoch(root);folder=prior._directory(output or root/OUTPUT)
    parent=prior._directory(parent_folder or root/prior.OUTPUT)
    manifest,value=_check(folder,expected_manifest_id);raw=_snapshot(folder/'original')
    record,execution=_replay(root,parent,expected_request_id,expected_parent_manifest_id,
        expected_topology_manifest_id,expected_flanged_manifest_id,expected_evaluation_id,raw)
    expected_source=dict(record['source_sha256']);expected_source[PRODUCER]=source_epoch;expected_source=dict(sorted(expected_source.items()))
    if value!=_publication(record,execution,expected_source,expected_request_id):raise ValueError('Publication and replayed worker differ')
    if _snapshot(folder/'original')!=raw or _epoch(root)!=source_epoch:raise ValueError('Sources changed during verification')
    research.cost.base._source_check(expected_source,root);_check(folder,expected_manifest_id);prior._check(parent,expected_parent_manifest_id)
    return dict(verified=True,manifest_id=manifest['manifest_id'],publication_id=value['publication_id'],
        worker_evaluation_id=record['evaluation_id'],recorded_worker_runtime=execution['runtime_observed_after_worker'],
        verifier_runtime=research.cost.base._tools(),native_evaluator_admission=False,
        whole_life_ranking_allowed=False,**{k:False for k in FLAGS})


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('publish','verify'))
    parser.add_argument('--root',default=str(ROOT));parser.add_argument('--output');parser.add_argument('--parent-folder')
    parser.add_argument('--state');parser.add_argument('--expected-manifest-id')
    for name in ('parent-manifest-id','topology-manifest-id','flanged-manifest-id','request-id','evaluation-id'):
        parser.add_argument('--expected-'+name,required=True)
    args=parser.parse_args(argv);common=dict(root=args.root,output=args.output,parent_folder=args.parent_folder,
        expected_parent_manifest_id=args.expected_parent_manifest_id,expected_topology_manifest_id=args.expected_topology_manifest_id,
        expected_flanged_manifest_id=args.expected_flanged_manifest_id,expected_request_id=args.expected_request_id,
        expected_evaluation_id=args.expected_evaluation_id)
    if args.action=='publish':
        if not args.state:parser.error('--state is required to publish')
        result=publish(args.state,**common)
    else:
        if not args.expected_manifest_id:parser.error('--expected-manifest-id is required to verify')
        result=verify(expected_manifest_id=args.expected_manifest_id,**common)
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':main()
