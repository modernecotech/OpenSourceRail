"""Bounded motor controls, practical excitation and physical return-path rewrite."""
from pathlib import Path
from copy import deepcopy
import json
import time
import fcntl
import gzip
import io
import tarfile
import tempfile
from math import sqrt

from engineering.station_rail import ROOT
from engineering.station_rail.common import identity,digest,encoded
from engineering.railway_twin import model
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
    return dict(motor.sources(root),**{PRODUCER:digest(Path(root)/PRODUCER)})


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


def verify_index(state,*,root=ROOT):
    folder=Path(state);value=json.loads((folder/'latest.json').read_bytes())
    if (value.get('schema')!='osr-configured-motor-experiment/1' or value.get('source_sha256')!=source_epoch(root)
        or value.get('experiment_id')!=identity({k:v for k,v in value.items() if k not in ('new_runs','experiment_id')})
        or any(value.get(k) is not False for k in FLAGS)):
        raise ValueError('Motor experiment source/index/disposition differs')
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
        path=folder/row['output']
        hold=definitions[name]['purpose']=='candidate-screen' and not electrical_bound(request)['passes_declared_sinusoidal_bound']
        if row['purpose']!=definitions[name]['purpose'] or row['electrical_bound']!=electrical_bound(request):
            raise ValueError('Experiment purpose/electrical screen differs')
        if hold:
            if set(p.name for p in path.iterdir())!={'input.json','result.json'}:
                raise ValueError('Necessary-bound hold cannot contain pretend native execution')
            if json.loads((path/'input.json').read_bytes())!=dict(request=request,source_sha256=value['source_sha256']):
                raise ValueError('Necessary-bound source/input differs')
        else:
            verified=motor.verify(path,root=root,require_current_tool=False)
            recorded=verified['recorded_tool_identity']
            if value['tool_identity']!={k:recorded[k] for k in motor.TOOL_IDENTITY_FIELDS}:
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
        files=[folder/'latest.json']+[p for row in value['rows'] for p in sorted((folder/row['output']).iterdir()) if p.is_file()]
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
