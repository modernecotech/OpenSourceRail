"""Closed archival replay for three non-promoting flanged system-cost attempts.

Externally pinned topology and flanged-study manifest IDs anchor the two source
parents. Recorded worker files are preserved; verification actually recalculates
quantities, production scenarios and the cost ledger with current analytical
code, retaining original and replay runtime epochs separately. There is no
native solver admission, physical test, whole-life ranking or selection.
"""
import argparse
from copy import deepcopy
import gc
import gzip
from hashlib import sha256
import json
from math import isfinite
import os
from pathlib import Path
import shutil
import stat
import tempfile

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest,encoded,identity
from . import flanged_system_cost as cost

PRODUCER='engineering/design_search/flanged_system_cost_publication.py'
OUTPUT='docs/design-engine/flanged-system-cost-study'
NAMES=('baseline','thick-web','thick-flange')
FLAGS=dict(cost.FLAGS)
TOP='docs/design-engine/civil-topology'
FLANGED='docs/design-engine/flanged-span-study'
COMMON=('baseline-manifest.json','baseline.json.gz','producer.py','worker.py','prepare.py','prepare.log','dispatch.py','dispatch.log')
CASE_COMMON=('request.json','original-request.json','original-result.json','execution.json','stdout.log','stderr.log')
MAX_FILE=16*1024**2
MAX_EXPANDED=128*1024**2


def _file(path,limit=MAX_FILE):
    p=Path(path).absolute()
    for part in (p,*p.parents):
        if part.is_symlink():raise ValueError('Symlink input or ancestor rejected')
    before=p.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_size>limit:raise ValueError('Bounded ordinary file required: '+str(p))
    sig=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    fd=os.open(p,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
    with os.fdopen(fd,'rb') as stream:
        opened=os.fstat(stream.fileno())
        if sig(before)!=sig(opened):raise ValueError('Input changed before reading')
        data=stream.read(limit+1);after=os.fstat(stream.fileno())
    if len(data)>limit or sig(opened)!=sig(after) or sig(after)!=sig(p.lstat()):raise ValueError('Input changed while reading')
    return data


def _directory(path):
    p=Path(path).absolute()
    for part in (p,*p.parents):
        if part.is_symlink():raise ValueError('Symlink directory or ancestor rejected')
    if not p.is_dir():raise ValueError('Ordinary existing directory required: '+str(p))
    return p


def _pairs(rows):
    result={}
    for k,v in rows:
        if k in result:raise ValueError('Duplicate JSON key')
        result[k]=v
    return result


def _json(raw,*,canonical=True):
    try:value=json.loads(raw,object_pairs_hook=_pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))
    except (ValueError,UnicodeDecodeError) as error:raise ValueError('Malformed JSON') from error
    if not isinstance(value,dict) or (canonical and encoded(value)!=raw):raise ValueError('Canonical JSON object required')
    return value


def _gzip_json(raw):
    import io
    with gzip.GzipFile(fileobj=io.BytesIO(raw),mode='rb') as stream:data=stream.read(MAX_EXPANDED+1)
    if len(data)>MAX_EXPANDED:raise ValueError('Expanded JSON exceeds bounded budget')
    return _json(data)


def _sealed(value,key):
    if not isinstance(value,dict) or value.get(key)!=identity({k:v for k,v in value.items() if k!=key}):
        raise ValueError('Identity differs: '+key)


def _flags(value):
    if any(value.get(k) is not False for k in FLAGS):raise ValueError('Research record may not promote acceptance or selection')


def _producer_epoch(root):
    source=digest(Path(__file__))
    if source!=digest(Path(root)/PRODUCER):raise ValueError('Executing publication producer differs from root')
    return source


def _parent(root,folder,schema,expected):
    if not isinstance(expected,str) or len(expected)!=64 or any(c not in '0123456789abcdef' for c in expected):
        raise ValueError('Externally pinned parent manifest ID required')
    root=_directory(root);p=root/folder/'manifest.json';raw=_file(p,4*1024**2);value=_json(raw)
    _sealed(value,'manifest_id')
    if value.get('schema')!=schema or value['manifest_id']!=expected:raise ValueError('Pinned parent identity or schema differs: '+folder)
    for flag in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release'):
        if value.get(flag) is not False:raise ValueError('Parent cannot grant '+flag)
    cost.base._source_check(value['source_sha256'],root)
    return value,sha256(raw).hexdigest()


def _snapshot(state):
    state=_directory(state);files={}
    allowed_top=set(COMMON)|set(NAMES)
    if {p.name for p in state.iterdir()}!=allowed_top:raise ValueError('Exact attempt input inventory required')
    for name in COMMON:files[name]=_file(state/name)
    for name in NAMES:
        case=_directory(state/name);names={p.name for p in case.iterdir()}
        if not set(CASE_COMMON)<=names or names-set(CASE_COMMON)-{'result.json.gz'}:raise ValueError('Attempt inventory differs: '+name)
        for item in sorted(names):files[name+'/'+item]=_file(case/item)
    return files


def _parents(root,topology_id,flanged_id,raw):
    topology,top_sha=_parent(root,TOP,'osr-civil-topology-publication/1',topology_id)
    flange,flange_sha=_parent(root,FLANGED,'osr-flanged-span-stage1-manifest/1',flanged_id)
    if raw['baseline-manifest.json']!=_file(Path(root)/TOP/'manifest.json'):raise ValueError('Retained topology manifest differs from pinned parent')
    if sha256(raw['baseline.json.gz']).hexdigest()!=topology['files_sha256'].get('baseline.json.gz'):
        raise ValueError('Baseline archive differs from pinned parent')
    if raw['producer.py']!=_file(Path(root)/cost.PRODUCER):raise ValueError('Retained cost producer differs from current source')
    for name in NAMES:
        for key in ('request.json','result.json'):
            path='original/'+name+'/'+key
            if sha256(raw[name+'/original-'+key]).hexdigest()!=flange['files_sha256'].get(path):
                raise ValueError('Original flanged input differs from pinned parent: '+path)
    return dict(topology_manifest_id=topology_id,topology_manifest_sha256=top_sha,
        baseline_archive_sha256=sha256(raw['baseline.json.gz']).hexdigest(),
        flanged_manifest_id=flanged_id,flanged_manifest_sha256=flange_sha)


def _execution(raw,name):
    prefix=name+'/';request=_json(raw[prefix+'request.json']);execution=_json(raw[prefix+'execution.json'])
    _sealed(request,'request_id');_sealed(execution,'execution_id')
    disposition=('physical_accepted','engineering_accepted','manufacturing_release','operating_release')
    if any(request.get(k) is not False or execution.get(k) is not False for k in disposition):raise ValueError('Attempt release flag differs')
    limits=dict(address_space_bytes=1073741824,cpu_seconds=60,wall_seconds=60,blas_threads=1)
    if (request.get('schema')!='osr-flanged-system-cost-private-request/1' or request.get('gauge')!=name
            or request.get('limits')!=limits or execution.get('schema')!='osr-flanged-private-execution/1'
            or execution.get('request_id')!=request['request_id'] or execution.get('limits')!=limits
            or execution.get('execution') not in ('completed','failed','wall-timeout')):
        raise ValueError('Attempt identity, limits or execution disposition differs')
    wall=execution.get('wall_seconds')
    if type(wall) not in (int,float) or not isfinite(wall) or wall<0:
        raise ValueError('Finite observed execution duration required')
    required={'baseline-manifest.json','baseline.json.gz','producer.py','worker.py',prefix+'original-request.json',prefix+'original-result.json'}
    if set(request.get('input_sha256',{}))!=required or any(sha256(raw[k]).hexdigest()!=v for k,v in request['input_sha256'].items()):
        raise ValueError('Attempt source input bytes differ')
    files={k[len(prefix):]:sha256(v).hexdigest() for k,v in raw.items() if k.startswith(prefix) and k!=prefix+'execution.json'}
    if files!=execution.get('actual_files'):raise ValueError('Execution output/log bytes differ')
    present=prefix+'result.json.gz' in raw
    if ((execution['execution']=='completed' and not present)
            or execution['execution']=='completed' and execution.get('returncode')!=0
            or execution['execution']=='failed' and (type(execution.get('returncode')) is not int or execution['returncode']==0)
            or execution['execution']=='wall-timeout' and execution.get('returncode') is not None):
        raise ValueError('Result and worker terminal disposition differ')
    return request,execution


def _summary(record,name,request,execution):
    if record is None:
        return dict(gauge=name,execution=execution['execution'],candidate_id=request['original_candidate_id'],
            request_id=request['request_id'],execution_id=execution['execution_id'],evaluation_id=None,composition_candidate_id=None,
            unadmitted_partial_result_present='result.json.gz' in execution['actual_files'])
    return dict(gauge=name,execution='completed',candidate_id=request['original_candidate_id'],
        request_id=request['request_id'],execution_id=execution['execution_id'],evaluation_id=record['evaluation_id'],
        composition_candidate_id=record['candidate_id'],baseline_id=record['baseline_id'],
        load_context_id=record['load_context_id'],recorded_replay_context=deepcopy(record['replay_context']),
        base_mass_installed_iqd=record['cases']['base']['model_based_installed_CAPEX_iqd'],
        base_mass_whole_life_iqd=record['cases']['base']['model_based_whole_life_NPV_iqd'],
        whole_life_ranking_allowed=False,whole_life_comparison_ready=False,
        exact_original_scoped_cost_id=record['span_cost_evaluation_id'])


def _audit(raw,root,topology_id,flanged_id,*,replay):
    root=Path(root).resolve();binding=_parents(root,topology_id,flanged_id,raw)
    baseline=_gzip_json(raw['baseline.json.gz']);cost.base._check(baseline,'baseline_id')
    if baseline['baseline_id']!=cost._authenticated_baseline(baseline,root,topology_id)['baseline_id']:
        raise ValueError('Baseline does not match authenticated publication')
    source={**baseline['source_sha256'],**cost._sources(root)};rows=[];contexts=[]
    for name in NAMES:
        request,execution=_execution(raw,name)
        original=_json(raw[name+'/original-request.json']);detail=_json(raw[name+'/original-result.json'])
        cost.span._sealed(original['candidate'],'geometry_id');cost.span._sealed(detail,'result_id')
        if (request['original_candidate_id']!=original['candidate']['candidate_id']
                or request['original_geometry_id']!=original['candidate']['geometry_id']
                or request['original_scoped_evaluation_id']!=detail['cost']['evaluation_id']
                or request['expected_baseline_id']!=baseline['baseline_id']
                or request['expected_baseline_manifest_id']!=topology_id
                or request['load_context_id']!=original['context']['context_id']
                or request['producer_sha256']!=digest(root/cost.PRODUCER)
                or request['runtime']!=baseline['tool_context']):
            raise ValueError('Worker request mixes parent candidate, baseline, context, source or tool epoch')
        contexts.append(original['context']['context_id'])
        if execution['execution']!='completed':rows.append(_summary(None,name,request,execution));continue
        record=_gzip_json(raw[name+'/result.json.gz']);cost.base._check(record);_flags(record)
        tools=record['replay_context']
        if (record.get('schema')!='osr-flanged-system-cost/1' or record['candidate_id']!=request['expected_composition_candidate_id']
                or record['geometry_id']!=request['original_geometry_id'] or record['baseline_id']!=baseline['baseline_id']
                or record['span_cost_evaluation_id']!=request['original_scoped_evaluation_id']
                or record['load_context_id']!=request['load_context_id']
                or record['baseline_publication']['manifest_id']!=topology_id
                or tools['baseline_tools']!=baseline['tool_context'] or tools['ledger_replay_tools']!=request['runtime']
                or tools['current_tools_required'] is not True or tools['baseline_tool_reuse_check_enforced'] is not True
                or tools['native_evaluator_admission'] is not False or record['integrated_selection'] is not None
                or record['whole_life_comparison_ready'] is not False or record['whole_life_ranking_allowed'] is not False
                or set(record['cases'])!=set(cost.CASES)
                or any(set(c['scope_totals_iqd'])!=set(cost.model.SCOPES) for c in record['cases'].values())
                or any(c['whole_life_NPV_delta_iqd'] is not None or c['whole_life_rankable'] is not False for c in record['comparison_to_corrected_canonical_baseline'].values())):
            raise ValueError('Recorded ancestry, coverage, tool epoch or nonpromotion differs')
        cost.base._source_check(record['source_sha256'],root)
        for k,v in record['source_sha256'].items():
            if k in source and source[k]!=v:raise ValueError('Mixed source epochs')
            source[k]=v
        row=_summary(record,name,request,execution)
        # Recorded tool epoch is evidence, not a demand that the verifier use the
        # same executable. Exact analytical fields must reproduce byte-for-byte.
        semantic=identity({k:v for k,v in record.items() if k not in ('evaluation_id','replay_context')})
        del record;gc.collect()
        if replay:
            recalculated=cost.compare(original['candidate'],detail['quantities'],detail['cost'],baseline,original['context'],
                root=root,expected_baseline_manifest_id=topology_id,require_current_tools=False)
            if identity({k:v for k,v in recalculated.items() if k not in ('evaluation_id','replay_context')})!=semantic:
                raise ValueError('Current analytical cost, quantity or support replay differs: '+name)
            if recalculated['replay_context']['native_evaluator_admission'] is not False:
                raise ValueError('Analytical replay cannot admit native evaluator')
            del recalculated;gc.collect()
        rows.append(row)
    if len(set(contexts))!=1:raise ValueError('All three candidates must use the same selected load context')
    source[TOP+'/manifest.json']=binding['topology_manifest_sha256'];source[FLANGED+'/manifest.json']=binding['flanged_manifest_sha256']
    source[PRODUCER]=digest(root/PRODUCER)
    if source[PRODUCER]!=digest(Path(__file__)):raise ValueError('Executing publication producer differs from root')
    return rows,dict(sorted(source.items())),binding


def _readme(value):
    text=['# Flanged-span whole-railway Class C scenarios','',
        'Three 20 m steel-girder and concrete-deck research configurations retain the same selected six-car vehicle, provisional mass cases and synthetic 6 km two-track service. Each is bound to the pinned topology baseline and original flanged-span study. These are scenario estimates, not a qualified railway or site budget.','',
        '| Gauge | Worker execution | Composition | Base-mass installed cost low / base / high (IQD) | Base-mass whole-life NPV low / base / high (IQD) |',
        '|---|---|---|---|---|']
    for row in value['attempts']:
        if row['execution']=='completed':
            installed=' / '.join(f'{x:,.2f}' for x in row['base_mass_installed_iqd']);npv=' / '.join(f'{x:,.2f}' for x in row['base_mass_whole_life_iqd'])
            text.append(f"| {row['gauge']} | completed | `{row['composition_candidate_id']}` | {installed} | {npv} |")
        else:text.append(f"| {row['gauge']} | {row['execution']} | not available | — | — |")
    text += ['', 'Whole-life deltas and rankings against the canonical reference remain held: its separately modelled coating and bearing renewal events are not matched. Routine maintenance is assumed to exclude explicit capital renewals; actual overlap is unverified. Installed-cost differences retain an unchanged foundation/site price proxy and are conditional.','','Factory routes use bounded reserve fabrication, QA, waste and declared two-shift production and construction; operations use 16/18/24-hour cases. Productive crane hours are converted to paid shifts using the declared utilization. Site capacity, pier and footing self-weight, crane capacity at radius, transport permits, structural performance, joint behavior, magnetic gaps, manufacturing and independent approval remain open.','',
        'Original requests, responses, logs, failure dispositions, source and runtime epochs are retained. Verification replays current-source analytical quantities and costs with an explicitly reported verifier runtime; it does not rerun a native solver or establish physical acceptance.','']
    return '\n'.join(text)


def _payload(folder):
    folder=_directory(folder)
    if {p.name for p in folder.iterdir()}!={'README.md','result.json','manifest.json','original'}:
        raise ValueError('Exact closed publication inventory required')
    raw=_snapshot(folder/'original')
    data={'original/'+k:sha256(v).hexdigest() for k,v in raw.items()}
    for name in ('README.md','result.json'):data[name]=sha256(_file(folder/name,4*1024**2)).hexdigest()
    return dict(sorted(data.items()))


def _record(rows,source,binding,publication_environment):
    value=dict(schema='osr-flanged-system-cost-publication-result/1',attempts=rows,parent_publications=binding,
        source_sha256=source,load_context_id=next(r['load_context_id'] for r in rows if r['execution']=='completed') if any(r['execution']=='completed' for r in rows) else None,
        publication_environment=deepcopy(publication_environment),
        replay_scope='Current-source analytical quantity and Class C cost replay only; no native evaluator admission',
        original_worker_provenance='Supplied worker/log bytes and resource declarations; historical runtime and isolation are not independently attested',
        whole_life_comparison_ready=False,whole_life_ranking_allowed=False,integrated_selection=None,**FLAGS)
    value['publication_id']=identity(value)
    return value


def _check(folder,expected_manifest_id=None):
    folder=_directory(folder);manifest=_json(_file(folder/'manifest.json',4*1024**2));_sealed(manifest,'manifest_id')
    if (manifest.get('schema')!='osr-flanged-system-cost-publication/1'
            or expected_manifest_id is not None and manifest['manifest_id']!=expected_manifest_id
            or manifest.get('files_sha256')!=_payload(folder)):
        raise ValueError('Publication manifest, identity or payload differs')
    _flags(manifest)
    record=_json(_file(folder/'result.json',4*1024**2));_sealed(record,'publication_id');_flags(record)
    if (record.get('schema')!='osr-flanged-system-cost-publication-result/1'
            or record['publication_id']!=manifest.get('publication_id')
            or record.get('integrated_selection') is not None or record.get('whole_life_ranking_allowed') is not False
            or record.get('whole_life_comparison_ready') is not False
            or record.get('source_sha256')!=manifest.get('source_sha256')
            or record.get('parent_publications')!=manifest.get('parent_publications')
            or _file(folder/'README.md',4*1024**2)!=_readme(record).encode()):
        raise ValueError('Publication record, source or nonpromotion differs')
    return manifest,record


def publish(state,*,root=ROOT,output=None,expected_topology_manifest_id,expected_flanged_manifest_id):
    """Publish once, without replacing an earlier immutable packet."""
    root=_directory(root);producer_epoch=_producer_epoch(root);state=_directory(state);target=Path(output).absolute() if output is not None else root/OUTPUT
    if target.exists() or target.is_symlink():raise ValueError('New publication destination required')
    if target==state or target in state.parents or state in target.parents:raise ValueError('Original state and publication must be separate')
    parent=_directory(target.parent);raw=_snapshot(state)
    rows,source,binding=_audit(raw,root,expected_topology_manifest_id,expected_flanged_manifest_id,replay=True)
    record=_record(rows,source,binding,cost.base._tools())
    stage=Path(tempfile.mkdtemp(prefix='.flanged-system-stage-',dir=parent))
    try:
        for name,data in raw.items():
            p=stage/'original'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        (stage/'result.json').write_bytes(encoded(record));(stage/'README.md').write_text(_readme(record))
        # Create a placeholder first so the closed-inventory checker can hash the stage.
        (stage/'manifest.json').write_bytes(b'{}\n')
        manifest=dict(schema='osr-flanged-system-cost-publication/1',publication_id=record['publication_id'],
            parent_publications=binding,source_sha256=source,files_sha256=_payload(stage),**FLAGS)
        manifest['manifest_id']=identity(manifest);(stage/'manifest.json').write_bytes(encoded(manifest))
        _check(stage,manifest['manifest_id'])
        if (_snapshot(state)!=raw or _parents(root,expected_topology_manifest_id,expected_flanged_manifest_id,raw)!=binding
                or _producer_epoch(root)!=producer_epoch):
            raise ValueError('Original attempt files or parents changed during publication')
        cost.base._source_check(source,root)
        target.mkdir()
        try:os.rename(stage,target)
        except OSError:
            try:target.rmdir()
            except OSError:pass
            raise
    finally:
        if stage.exists():shutil.rmtree(stage)
    return manifest


def verify(output=None,*,root=ROOT,expected_topology_manifest_id,expected_flanged_manifest_id,expected_manifest_id):
    """Actually replay all completed accounting records under current tools."""
    root=_directory(root);producer_epoch=_producer_epoch(root);folder=Path(output) if output is not None else root/OUTPUT
    if not isinstance(expected_manifest_id,str) or len(expected_manifest_id)!=64:
        raise ValueError('Externally pinned publication manifest identity required')
    manifest,record=_check(folder,expected_manifest_id);raw=_snapshot(Path(folder)/'original')
    rows,source,binding=_audit(raw,root,expected_topology_manifest_id,expected_flanged_manifest_id,replay=True)
    expected=_record(rows,source,binding,record['publication_environment'])
    if record!=expected or manifest['source_sha256']!=source or manifest['parent_publications']!=binding:
        raise ValueError('Analytical replay, source epoch or parent identity differs')
    if (_snapshot(Path(folder)/'original')!=raw or _check(folder,expected_manifest_id)[0]!=manifest
            or _producer_epoch(root)!=producer_epoch):
        raise ValueError('Publication changed during verification')
    cost.base._source_check(source,root)
    return dict(verified=True,manifest_id=manifest['manifest_id'],publication_id=record['publication_id'],
        attempts=len(rows),completed=sum(r['execution']=='completed' for r in rows),
        analytical_cost_replay_executed=True,native_solver_executed=False,native_evaluator_admission=False,
        physical_measurements_verified=False,recorded_worker_environments=[r.get('recorded_replay_context') for r in rows],
        verifier_environment=cost.base._tools(),whole_life_ranking_allowed=False,integrated_selection=None,**FLAGS)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
    for name in ('publish','verify'):
        command=sub.add_parser(name);command.add_argument('--expected-topology-manifest-id',required=True);command.add_argument('--expected-flanged-manifest-id',required=True);command.add_argument('--output',type=Path)
        if name=='publish':command.add_argument('--state',type=Path,required=True)
        else:command.add_argument('--expected-manifest-id',required=True)
    parser.add_argument('--root',type=Path,default=ROOT);args=parser.parse_args(argv)
    try:
        common=dict(root=args.root,output=args.output,expected_topology_manifest_id=args.expected_topology_manifest_id,expected_flanged_manifest_id=args.expected_flanged_manifest_id)
        result=publish(args.state,**common) if args.action=='publish' else verify(expected_manifest_id=args.expected_manifest_id,**common)
    except (ValueError,OSError,KeyError,TypeError,EOFError) as error:parser.exit(2,str(error)+'\n')
    print(json.dumps(result,sort_keys=True,indent=2));return 0


if __name__=='__main__':raise SystemExit(main())
