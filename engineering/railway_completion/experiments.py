"""Bounded motor controls, practical excitation and physical return-path rewrite."""
from pathlib import Path,PurePosixPath
from copy import deepcopy
import json
import time
import fcntl
import gzip
import io
import tarfile
import tempfile
import shutil
from math import sqrt

from engineering.station_rail import ROOT
from engineering.station_rail.common import identity,digest,encoded
from engineering.railway_twin import model
from engineering.railway_twin import pipeline as twin_pipeline
from . import motor,FLAGS
from engineering.design_search.launch_options import bounds

PRODUCER='engineering/railway_completion/experiments.py'


def cases(root=ROOT):
    base=model.materialize(root=root)['bundle']
    wide=motor.variant(base,backiron_m=.1)
    rewound=motor.rewound_variant(base)
    rows=[('zero',base,dict(voltage_peak_V=0.,steps=4)),
        ('inside-forward',base,dict(voltage_peak_V=2.,steps=16)),
        ('inside-reverse',base,dict(voltage_peak_V=2.,steps=16,phase_direction=-1)),
        ('moving-entry',base,dict(voltage_peak_V=2.,steps=16,start_m=-8.95,speed_m_s=.5)),
        ('launch-reference-rated',base,dict(voltage_peak_V=375.,frequency_Hz=30.,steps=64,start_m=0.)),
        ('launch-wide-return-rated',wide,dict(voltage_peak_V=375.,frequency_Hz=30.,steps=64,start_m=0.)),
        ('rewound-running',rewound,dict(voltage_peak_V=375.,frequency_Hz=50.,steps=64,start_m=5.5,speed_m_s=20.,transport_method='supg-coth')),
        ('rewound-running-fine-time',rewound,dict(voltage_peak_V=375.,frequency_Hz=50.,steps=128,dt_s=.001,start_m=5.5,speed_m_s=20.,transport_method='supg-coth'))]
    return [dict(name=name,request=motor.request(bundle,**variables),purpose='method-control' if i<4 else 'candidate-screen') for i,(name,bundle,variables) in enumerate(rows)]


def electrical_bound(request):
    b=request['bundle_definition'];p=request['physical_geometry'];e=b['motor_parameters']['evaluation']
    demand=bounds(6*b['mass']['accounted_cap_loaded_kg_per_car'],6*b['rotating_equivalent_kg_per_car'],20.,.4)
    voltage=request['voltage_peak_V']/sqrt(2)
    rms=min(request['current_limit_A']/sqrt(2),e['wire_density_limit_RMS_A_mm2']*p['conductor_area_m2']*1e6)
    resistance=motor.path_resistance(request)
    # Optimistic unity power factor, with copper as the sole counted loss.
    currents=[min(rms,voltage/(2*float(R))) for R in resistance]
    apparent=sum(voltage*I for I in currents)
    copper=sum(float(R)*I*I for R,I in zip(resistance,currents))
    return dict(candidate_id=b['candidate_id'],accounted_normal_mass_kg=6*b['mass']['accounted_cap_loaded_kg_per_car'],
        required_mechanical_peak_W=demand['required_mechanical_power_W'],phase_voltage_peak_V=request['voltage_peak_V'],
        branch_current_peak_limit_A=request['current_limit_A'],branch_RMS_current_A=rms,
        sinusoidal_apparent_power_ceiling_VA=apparent,optimistic_copper_loss_W=copper,
        optimistic_mechanical_power_ceiling_W=apparent-copper,
        passes_declared_sinusoidal_bound=apparent-copper>=demand['required_mechanical_power_W'],
        scope='Conditional quasi-steady sinusoidal necessary screen at accounted mass, declared wire RMS/current envelope and one active bank. Transient magnetic storage, other waveforms, installed mass and all other losses need separate evidence.',**FLAGS)


def _held(request):
    value=dict(execution='held-necessary-bound',bundle_id=request['bundle_id'],motor_component_id=request['motor_component_id'],
        request_id=request['request_id'],state='insufficient-declared-electrical-envelope',trace=[],
        reason='Optimistic sinusoidal electrical power less copper is below required high-speed mechanical power',
        electrical_bound=electrical_bound(request),**FLAGS)
    value['evaluation_id']=identity(value);return value


def source_epoch(root=ROOT):
    # Motor requests are materialized from the complete twin candidate. Bind
    # that source graph as well as the narrower solver-method sources so a
    # changed body/bundle definition cannot retain an old request identity.
    return dict(twin_pipeline.sources(root),**motor.sources(root),
        **{PRODUCER:digest(Path(root)/PRODUCER)})


def _summary(name,result):
    trace=result.get('trace',[])
    return dict(name=name,candidate_id=result['bundle_id'],motor_component_id=result['motor_component_id'],
        evaluation_id=result['evaluation_id'],request_id=result['request_id'],execution=result['execution'],state=result.get('state'),
        reason=result.get('reason'),steps=len(trace),final_time_s=None if not trace else trace[-1]['time_s'],
        final_thrust_N=None if not trace else trace[-1]['thrust_N'],
        maximum_path_current_A=None if not trace else max(abs(i) for row in trace for i in row['path_currents_A']),
        peak_steel_B_T=None if not trace else max(row['peak_steel_B_T'] for row in trace),
        maximum_discrete_power_residual_W=None if not trace else max(abs(row['discrete_power_residual_W']) for row in trace),
        available_operating_map=False,**FLAGS)


def _run(state,*,root=ROOT,maximum_new_runs=8,maximum_seconds=1800.):
    if type(maximum_new_runs) is not int or not 0<=maximum_new_runs<=8 or not 0<maximum_seconds<=1800:
        raise ValueError('Zero to eight new motor runs and at most1800s invocation budget required')
    folder=Path(state);folder.mkdir(parents=True,exist_ok=True)
    if (folder/'latest.json').is_file() and 'reindex_provenance' in json.loads((folder/'latest.json').read_bytes()):
        raise ValueError('Reindexed terminal state is immutable; verify or publish it instead of rewriting its provenance')
    epoch=source_epoch(root);requests=cases(root);rows=[];pending=[];new=0;started=time.monotonic()
    tool={k:v for k,v in motor._tool(requests[0]['request']).items() if k in ('python','python_sha256','numpy','scipy','superlu_sha256')}
    for row in requests:
        request=row['request'];key=identity(dict(request_id=request['request_id'],source_sha256=epoch,tool_identity=tool))
        output=folder/'runs'/key
        hold=row['purpose']=='candidate-screen' and not electrical_bound(request)['passes_declared_sinusoidal_bound']
        if output.exists():
            if hold:
                data=json.loads((output/'result.json').read_bytes())
                if data!=_held(request) or json.loads((output/'input.json').read_bytes())!=dict(request=request,source_sha256=epoch):
                    raise ValueError('Necessary-bound record differs')
            else: motor.verify(output,root=root)
            result=json.loads((output/'result.json').read_bytes())
        elif new>=maximum_new_runs or time.monotonic()-started+request['maximum_seconds']+5>maximum_seconds:
            pending.append(dict(name=row['name'],request=request,output='runs/'+key));continue
        else:
            if source_epoch(root)!=epoch:
                raise ValueError('Experiment source changed before execution')
            if hold:
                output.mkdir(parents=True);result=_held(request)
                (output/'input.json').write_bytes(encoded(dict(request=request,source_sha256=epoch)))
                (output/'result.json').write_bytes(encoded(result))
            else:result=motor.run(request,output,root=root)
            new+=1
        if source_epoch(root)!=epoch:
            raise ValueError('Experiment source changed; retain numerical packages without publishing a mixed index')
        rows.append(dict(output='runs/'+key,request=request,purpose=row['purpose'],electrical_bound=electrical_bound(request),summary=_summary(row['name'],result)))
    value=dict(schema='osr-configured-motor-experiment/1',source_sha256=epoch,tool_identity=tool,
        rows=rows,pending=pending,new_runs=new,integrated_selection=None,**FLAGS)
    value['experiment_id']=identity({k:v for k,v in value.items() if k!='new_runs'})
    temporary=folder/'latest.json.tmp';temporary.write_bytes(encoded(value));temporary.replace(folder/'latest.json')
    return value


def run(state,*,root=ROOT,maximum_new_runs=8,maximum_seconds=1800.):
    folder=Path(state);folder.mkdir(parents=True,exist_ok=True)
    with (folder/'.coordinator.lock').open('a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as error:raise ValueError('Motor experiment coordinator already running') from error
        return _run(folder,root=root,maximum_new_runs=maximum_new_runs,maximum_seconds=maximum_seconds)


def _ordinary(folder):
    folder=Path(folder)
    if any(p.is_symlink() for p in (folder,*folder.parents)) or not folder.is_dir() or any(p.is_symlink() or not(p.is_file() or p.is_dir()) for p in folder.rglob('*')):
        raise ValueError('Ordinary unlinked motor state/package required')


def _epoch_paths(epoch):
    if not isinstance(epoch,dict) or not epoch:raise ValueError('Explicit source epoch required')
    for name,sha in epoch.items():
        path=PurePosixPath(name)
        if (not isinstance(name,str) or not path.parts or path.is_absolute() or '..' in path.parts or '\\' in name or path.as_posix()!=name or not isinstance(sha,str) or len(sha)!=64 or any(c not in '0123456789abcdef' for c in sha)):
            raise ValueError('Ordinary source epoch paths/digests required')


def _inventory(folder):
    _ordinary(folder)
    return {p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=digest(p)) for p in sorted(Path(folder).rglob('*')) if p.is_file()}


def _index_seal(value):
    return value.get('experiment_id')==identity({k:v for k,v in value.items() if k not in ('new_runs','experiment_id')})


def _verify_reindex(folder,value,root):
    provenance=value['reindex_provenance'];origin_path=Path(folder)/'origin-index.json'
    if (provenance.get('schema')!='osr-exact-raw-motor-reindex/1' or provenance.get('origin_index')!='origin-index.json'
            or digest(origin_path)!=provenance['origin_index_sha256'] or value['new_runs']!=0):raise ValueError('Reindex origin index/hash differs')
    origin=json.loads(origin_path.read_bytes());_epoch_paths(origin.get('source_sha256'))
    if (origin.get('schema')!='osr-configured-motor-experiment/1' or origin.get('integrated_selection') is not None or not _index_seal(origin) or origin.get('reindex_provenance') is not None or origin.get('pending') or len(origin.get('rows',[]))!=8
            or provenance['origin_experiment_id']!=origin['experiment_id'] or provenance['origin_source_sha256']!=origin['source_sha256']
            or origin['tool_identity']!=value['tool_identity'] or any(origin.get(k) is not False for k in FLAGS)):
        raise ValueError('Original execution index seal/epoch/tool/disposition differs')
    old={r['summary']['name']:r for r in origin['rows']};new={r['summary']['name']:r for r in value['rows']};entries={r['name']:r for r in provenance['entries']}
    if len(old)!=8 or len(entries)!=8 or len(provenance['entries'])!=8 or set(old)!=set(new) or set(entries)!=set(new):raise ValueError('Reindex origin matrix differs')
    definitions={r['name']:r for r in cases(root)}
    for name,row in new.items():
        previous=old[name];entry=entries[name];request=row['request']
        expected_old='runs/'+identity(dict(request_id=request['request_id'],source_sha256=origin['source_sha256'],tool_identity=origin['tool_identity']))
        if (previous['request']!=request or previous['output']!=expected_old or previous['purpose']!=row['purpose']
                or entry['origin_output']!=expected_old or entry['output']!=row['output']
                or entry['origin_evaluation_id']!=previous['summary']['evaluation_id']):raise ValueError('Reindex original request/path/evaluation differs')
        path=Path(folder)/row['output']
        hold=definitions[name]['purpose']=='candidate-screen' and not electrical_bound(request)['passes_declared_sinusoidal_bound']
        if hold:
            retained=Path(folder)/'origin-holds'/expected_old.split('/')[1]
            if entry['disposition']!='necessary-bound-recomputed' or entry['origin_hold_output']!='origin-holds/'+expected_old.split('/')[1] or _inventory(retained)!=entry['origin_files']:
                raise ValueError('Retained original necessary-bound payload differs')
            original_input=json.loads((retained/'input.json').read_bytes());actual=json.loads((retained/'result.json').read_bytes())
            if (set(entry['origin_files'])!={'input.json','result.json'} or original_input!=dict(request=request,source_sha256=origin['source_sha256'])
                    or actual!=_held(request) or previous['summary']!=_summary(name,actual) or previous['electrical_bound']!=electrical_bound(request)):
                raise ValueError('Original necessary-bound provenance differs')
        else:
            if entry['disposition']!='exact-raw-package-preserved' or _inventory(path)!=entry['origin_files'] or previous['summary']!=row['summary'] or previous['electrical_bound']!=row['electrical_bound']:
                raise ValueError('Reused raw package/evaluation differs from origin')
            proof=entry['creation_verification']
            if (proof['recorded_tool_identity']!=origin['tool_identity'] or proof['current_tool_identity']!=origin['tool_identity']
                    or proof['require_current_tool'] is not True or proof['independent_execution_attempted'] is not False
                    or proof['request_id']!=request['request_id'] or proof['evaluation_id']!=previous['summary']['evaluation_id']):
                raise ValueError('Exact source/tool/resource reuse verification differs')
    return provenance


def verify_index(state,*,root=ROOT):
    folder=Path(state);_ordinary(folder)
    if (folder/'reindex-failure.txt').exists():raise ValueError('Failed partial reindex cannot be published; preserve it and use a fresh output')
    value=json.loads((folder/'latest.json').read_bytes())
    _verify_contents(folder,value,root,source_epoch(root))
    if 'reindex_provenance' in value:_verify_reindex(folder,value,root)
    return value


def reindex(source_state,new_state,root=ROOT):
    """Preserve exact raw executions across a broad-only source-epoch change.

    The source must be the original complete execution index. Necessary bounds
    are rerun algebraically; no numerical motor execution or replay is allowed.
    Interrupted packages retain their original evaluation and disposition.
    """
    source=Path(source_state);target=Path(new_state);root=Path(root)
    _ordinary(source)
    if target.exists() or target.is_symlink() or any(p.is_symlink() for p in target.parents):raise ValueError('Fresh unlinked reindex output required')
    if source.resolve()==target.resolve() or source.resolve() in target.resolve().parents:raise ValueError('Reindex output cannot mutate source state')
    snapshot=_inventory(source);raw=(source/'latest.json').read_bytes();origin=json.loads(raw)
    if origin.get('reindex_provenance') is not None or origin.get('pending') or len(origin.get('rows',[]))!=8:raise ValueError('Original complete8-case execution index required')
    epoch=source_epoch(root);_epoch_paths(epoch)
    _verify_contents(source,origin,root,origin.get('source_sha256'),require_current_tool=True)
    tool={k:v for k,v in motor._tool(cases(root)[0]['request']).items() if k in motor.TOOL_IDENTITY_FIELDS}
    if origin['tool_identity']!=tool:raise ValueError('Current tool differs from original execution tool')
    target.mkdir(parents=True);(target/'origin-index.json').write_bytes(raw);rows=[];entries=[]
    try:
        for old in origin['rows']:
            request=old['request'];name=old['summary']['name'];key=identity(dict(request_id=request['request_id'],source_sha256=epoch,tool_identity=tool));output=target/'runs'/key;oldpath=source/old['output']
            hold=old['purpose']=='candidate-screen' and not electrical_bound(request)['passes_declared_sinusoidal_bound'];files=_inventory(oldpath)
            entry=dict(name=name,origin_output=old['output'],output='runs/'+key,origin_evaluation_id=old['summary']['evaluation_id'],origin_files=files)
            if hold:
                retained=target/'origin-holds'/old['output'].split('/')[1];shutil.copytree(oldpath,retained)
                output.mkdir(parents=True);result=_held(request);(output/'input.json').write_bytes(encoded(dict(request=request,source_sha256=epoch)));(output/'result.json').write_bytes(encoded(result))
                entry.update(disposition='necessary-bound-recomputed',origin_hold_output=retained.relative_to(target).as_posix())
            else:
                proof=motor.verify(oldpath,root=root,require_current_tool=True,replay=False)
                shutil.copytree(oldpath,output)
                if _inventory(output)!=files:raise ValueError('Raw package bytes changed during copy')
                result=json.loads((output/'result.json').read_bytes());entry.update(disposition='exact-raw-package-preserved',creation_verification=proof)
            rows.append(dict(output='runs/'+key,request=request,purpose=old['purpose'],electrical_bound=electrical_bound(request),summary=_summary(name,result)));entries.append(entry)
        provenance=dict(schema='osr-exact-raw-motor-reindex/1',origin_index='origin-index.json',origin_index_sha256=digest(target/'origin-index.json'),origin_experiment_id=origin['experiment_id'],origin_source_sha256=origin['source_sha256'],entries=entries,numerical_solver_executed=False)
        value=dict(schema='osr-configured-motor-experiment/1',source_sha256=epoch,tool_identity=tool,rows=rows,pending=[],new_runs=0,reindex_provenance=provenance,integrated_selection=None,**FLAGS)
        value['experiment_id']=identity({k:v for k,v in value.items() if k!='new_runs'})
        (target/'latest.json').write_bytes(encoded(value))
        if source_epoch(root)!=epoch or _inventory(source)!=snapshot:raise ValueError('Source epoch/original package changed during reindex')
        verify_index(target,root=root)
    except BaseException:
        (target/'reindex-failure.txt').write_text('Reindex interrupted or verification failed; preserve partial output and original inputs.\n');raise
    return value


def _verify_contents(folder,value,root,epoch,*,require_current_tool=False):
    if (value.get('schema')!='osr-configured-motor-experiment/1' or value.get('source_sha256')!=epoch
        or value.get('integrated_selection') is not None or type(value.get('new_runs')) is not int or not 0<=value['new_runs']<=8
        or value.get('experiment_id')!=identity({k:v for k,v in value.items() if k not in ('new_runs','experiment_id')})
        or any(value.get(k) is not False for k in FLAGS)):
        raise ValueError('Motor experiment source/index/disposition differs')
    _ordinary(folder);_epoch_paths(value.get('source_sha256'))
    tool=value.get('tool_identity')
    if not isinstance(tool,dict) or set(tool)!=set(motor.TOOL_IDENTITY_FIELDS) or any(not isinstance(v,str) or not v.strip() for v in tool.values()):
        raise ValueError('Exact recorded experiment tool identity required')
    if any(len(tool[k])!=64 or any(c not in '0123456789abcdef' for c in tool[k]) for k in ('python_sha256','superlu_sha256')):
        raise ValueError('Experiment tool digests differ')
    definitions={r['name']:r for r in cases(root)}
    expected={name:r['request'] for name,r in definitions.items()}
    names=[r['summary']['name'] for r in value['rows']]+[r['name'] for r in value['pending']]
    if len(names)!=len(set(names)) or set(names)!=set(expected):
        raise ValueError('Motor executed/pending matrix differs')
    for row in value['rows']:
        name=row['summary']['name'];request=row['request']
        if request!=expected[name]:raise ValueError('Motor experiment request differs')
        key=identity(dict(request_id=request['request_id'],source_sha256=value['source_sha256'],tool_identity=value['tool_identity']))
        if row['output']!='runs/'+key:raise ValueError('Exact ordinary motor output path required')
        path=folder/row['output'];_ordinary(path)
        if any(not p.is_file() for p in path.iterdir()):raise ValueError('Flat ordinary motor package required')
        hold=definitions[name]['purpose']=='candidate-screen' and not electrical_bound(request)['passes_declared_sinusoidal_bound']
        if row['purpose']!=definitions[name]['purpose'] or row['electrical_bound']!=electrical_bound(request):
            raise ValueError('Experiment purpose/electrical screen differs')
        if hold:
            if set(p.name for p in path.iterdir())!={'input.json','result.json'}:
                raise ValueError('Necessary-bound hold cannot contain pretend native execution')
            if json.loads((path/'input.json').read_bytes())!=dict(request=request,source_sha256=value['source_sha256']):
                raise ValueError('Necessary-bound source/input differs')
        else:
            verified=motor.verify(path,root=root,require_current_tool=require_current_tool,replay=False)
            if json.loads((path/'input.json').read_bytes())['request']!=request:raise ValueError('Indexed/native motor request differs')
            recorded=verified['recorded_tool_identity']
            if recorded is None or value['tool_identity']!={k:recorded[k] for k in motor.TOOL_IDENTITY_FIELDS}:
                raise ValueError('Experiment tool identity differs from actual recorded package')
        actual=json.loads((path/'result.json').read_bytes())
        if hold and actual!=_held(request):raise ValueError('Necessary-bound screen differs')
        if row['summary']!=_summary(name,actual):raise ValueError('Motor experiment semantic summary differs')
    for row in value['pending']:
        if row['request']!=expected[row['name']]:raise ValueError('Pending motor experiment request differs')
        key=identity(dict(request_id=row['request']['request_id'],source_sha256=value['source_sha256'],tool_identity=value['tool_identity']))
        if row['output']!='runs/'+key:raise ValueError('Pending motor experiment path differs')
    return value


def publish(state,output,*,root=ROOT):
    value=verify_index(state,root=root);folder=Path(state);target=Path(output);target.mkdir(parents=True,exist_ok=True)
    data=io.BytesIO()
    with tarfile.open(fileobj=data,mode='w') as archive:
        provenance_files=([folder/'origin-index.json']+list((folder/'origin-holds').rglob('*'))) if 'reindex_provenance' in value else []
        files=[folder/'latest.json']+[p for p in provenance_files if p.is_file()]+[p for row in value['rows'] for p in sorted((folder/row['output']).iterdir()) if p.is_file()]
        for p in files:
            raw=p.read_bytes();item=tarfile.TarInfo(p.relative_to(folder).as_posix());item.size=len(raw);item.mtime=0;item.mode=0o644
            archive.addfile(item,io.BytesIO(raw))
    path=target/'motor-experiments.tar.gz';path.write_bytes(gzip.compress(data.getvalue(),mtime=0))
    m=dict(schema='osr-current-motor-experiment-publication/1',archive=path.name,archive_sha256=digest(path),
        experiment_id=value['experiment_id'],source_sha256=source_epoch(root),summaries=[r['summary'] for r in value['rows']],pending=value['pending'],**FLAGS)
    m['publication_id']=identity(m);(target/'motor-manifest.json').write_bytes(encoded(m));return m


def verify_publication(output,*,root=ROOT):
    folder=Path(output);m=json.loads((folder/'motor-manifest.json').read_bytes())
    if (m['publication_id']!=identity({k:v for k,v in m.items() if k!='publication_id'}) or m['source_sha256']!=source_epoch(root)
        or m['archive']!='motor-experiments.tar.gz' or digest(folder/m['archive'])!=m['archive_sha256'] or any(m.get(k) is not False for k in FLAGS)):
        raise ValueError('Motor publication identity/source/payload differs')
    with tempfile.TemporaryDirectory(prefix='osr-motor-archive-') as temporary:
        with tarfile.open(folder/m['archive'],'r:gz') as archive:
            members=archive.getmembers();names=[p.name for p in members]
            if len(names)!=len(set(names)) or len(names)>128 or sum(p.size for p in members)>128*1024**2 or any(not p.isfile() or Path(p.name).is_absolute() or '..' in Path(p.name).parts for p in members):
                raise ValueError('Bounded ordinary motor archive required')
            archive.extractall(temporary,filter='data')
        value=verify_index(temporary,root=root)
        if m['experiment_id']!=value['experiment_id'] or m['summaries']!=[r['summary'] for r in value['rows']] or m['pending']!=value['pending']:
            raise ValueError('Motor publication semantic summary differs')
    return dict(verified=True,experiment_id=value['experiment_id'],runs=len(value['rows']),pending=len(value['pending']),**FLAGS)
