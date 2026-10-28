"""Continuing numerical cell development, separate from frozen regression cells."""
from pathlib import Path
from copy import deepcopy
import gzip,json,time,fcntl
from engineering.reference_cell import vehicles,bundle as vehicle_adapter,physics
from engineering.railway_twin import pipeline
from . import ROOT,FLAGS,identity,encoded,digest
from . import alternatives,journey,production,intake
import io,tarfile,tempfile

OUTPUT='docs/design-engine/continuing-cell'


def _unreleased(value):
    if isinstance(value,dict):
        if any(k in FLAGS and v is not False for k,v in value.items()):raise ValueError('Research output cannot issue nested acceptance or release')
        for v in value.values():_unreleased(v)
    elif isinstance(value,list):
        for v in value:_unreleased(v)


def sources(root=ROOT):
    from engineering.reference_cell import coordinator as frozen
    root=Path(root);s=frozen.sources(root)
    for p in sorted((root/'engineering/railway_progress').rglob('*')):
        if p.is_file() and p.suffix in ('.py','.json','.html','.js','.css') and not any(x in p.parts for x in ('tests','__pycache__')) and p.name!='propulsion.py':
            s[p.relative_to(root).as_posix()]=digest(p)
    for m in (vehicle_adapter,physics):s[m.PRODUCER if hasattr(m,'PRODUCER') else 'engineering/reference_cell/physics.py']=digest(m.__file__)
    return dict(sorted(s.items()))


def plan():
    return dict(schema='osr-continuing-cell-plan/1',requests=[dict(vehicle_id=v,distance_m=d,kind='station-pinch-rollers') for v in vehicles.variants() for d in (1500.,2000.)],
        alternative_kinds=list(alternatives.KINDS),scope='Conditional numerical engineering; all frozen six/ten-case regressions retained',
        release_conditions='Authenticated prototype results, supported models, independent engineering and operating approvals',**FLAGS)


def compose(vehicle,distance_m,alternative,*,root=ROOT):
    from . import civil
    base=vehicle_adapter.materialize(vehicle,distance_m,root=root)
    definition=civil.geometry_definition(vehicle,distance_m,alternative)
    physical=dict(schema='osr-continuing-cell-physical/1',vehicle_component_id=vehicle['candidate_id'],
        launch_component_id=alternative['candidate_id'],civil_component_id=definition['physical_geometry_id'],
        formation=dict(cars=6,car_length_m=17.,coupling_gap_m=.5,normal_places_per_car=46),
        route=dict(station_spacing_m=distance_m,stations=2,tracks=1),selected_reference_changed=False)
    cid=identity(physical)
    # Actual mass/brake/axle models are vehicle subcomponents. The previous LIM
    # architecture is not installed or silently relabelled as mechanical drive.
    b={k:deepcopy(base[k]) for k in ('body_candidate_id','body_definition_id','support_component_id','cars','car_length_m','mass',
        'mass_interval_kg_per_car','rotating_equivalent_kg_per_car','rotor_definition_id','brake_definition','requirements','requirement_revision',
        'route_axle_offsets_from_leading_nose_m','source_sha256')}
    b.update(schema='osr-continuing-reference-cell-bundle/1',candidate_id=cid,bundle_id=cid,
        propulsion_component_id=alternative['candidate_id'],family_id='station-mechanical-research' if alternative['conditional_force_model'] else 'station-LIM-research',
        architecture_case=dict(physical_definition=physical),progress_architecture=dict(alternative_candidate_id=alternative['candidate_id'],civil_geometry_id=definition['physical_geometry_id']),
        vehicle_adapter_evaluation_id=base['definition_id'],component_ancestry=dict(vehicle=vehicle['candidate_id'],launch=alternative['candidate_id'],civil=definition['physical_geometry_id']),
        complete_installed_mass_kg=None,**FLAGS)
    b['brake_definition']['candidate_id']=cid;b['brake_definition']['propulsion_component_id']=alternative['candidate_id']
    b['brake_definition'].pop('brake_definition_id',None);b['brake_definition']['brake_definition_id']=identity(b['brake_definition'])
    b['definition_id']=identity(b)
    return b,civil.generate(cid,definition)


def contexts(distance_m):
    cases=[]
    for load in ('empty','normal','crowd-control'):
        for bound in ('lower','upper'):cases.append(dict(name=load+'-'+bound,load=load,mass_bound=bound))
    cases.extend([dict(name='headwind-hot',wind_m_s=15.,ambient_C=55.),dict(name='uphill-2percent',grade_fraction=.02),
        dict(name='downhill-2percent',grade_fraction=-.02),dict(name='one-bank-failed',failed_banks=[2]),
        dict(name='power-interruption',power_interrupt_at_s=15.),dict(name='emergency-braking',emergency_at_m=800.),
        dict(name='low-adhesion',adhesion_coefficient=.025,condition='low-friction')])
    return [dict(name=c.pop('name'),scenario=journey.scenario(distance_m=distance_m,**c)) for c in cases]


def _journeys(b,a,distance_m):
    rows=[]
    for s in contexts(distance_m):
        scenario=dict(s['scenario']);banks=len(a['parameters'].get('bank_starts_m',[]))
        if scenario['failed_banks'] and banks<3:
            scenario['failed_banks']=[banks-1] if banks else []
        rows.append(dict(name=s['name'],result=journey.evaluate(b,a,context=scenario)))
    return rows


def evaluate(vehicle,distance_m,kind='station-pinch-rollers',*,root=ROOT,loaded_inputs=None,artifact_verifier=None,authenticator=None):
    base=vehicle_adapter.materialize(vehicle,distance_m,root=root)
    a=alternatives.evaluate(vehicle,base,kind=kind,distance_m=distance_m,root=root)
    b,c=compose(vehicle,distance_m,a,root=root)
    rows=_journeys(b,a,distance_m)
    p=production.compile(vehicle,c,a,b['candidate_id'])
    from . import load_transfer
    coupled_loads=load_transfer.evaluate(b,c,a,rows)
    exploration=None;alternative_comparison=None;alternate_journeys=None
    if vehicle['vehicle_id']=='V1' and distance_m==2000. and kind=='station-pinch-rollers':
        from . import search
        exploration=search.run(vehicle,base,root=root)
        variants=[alternatives.evaluate(vehicle,base,kind=k,distance_m=distance_m,root=root) for k in alternatives.KINDS]
        alternative_comparison=alternatives.compare(variants)
        cable=next(x for x in variants if x['kind']=='cable-launch-tug');cb,cc=compose(vehicle,distance_m,cable,root=root)
        alternate_journeys=dict(bundle=cb,alternative=cable,journeys=_journeys(cb,cable,distance_m),
            required_return_cycle_s=cable['mechanism']['launch_attach_reset_cycle_lower_s'],
            cycle_fits120s_hypothesis=cable['mechanism']['cycle_fits120s_hypothesis'])
    admitted=[]
    # Production LIM replay retains its own correctly typed P1 physical bundle.
    # Mechanical conditional capacities cannot enter that operating-map gate.
    if loaded_inputs is not None:
        if loaded_inputs['manifest']['binding']!=intake.evidence.binding(b):raise ValueError('Inputs bind another continuing cell')
        for row in rows:
            name=row['name'];model=intake.for_context(loaded_inputs,'coupled-models',name);fm=intake.for_context(loaded_inputs,'force-map',name)
            if fm is not None or model is not None:
                admitted.append(dict(name=name,execution='held-unsupported-physical-model-family',reason='Mechanical operating-map adapter requires measured contact/slip/spin-up and controlled brake models; no P1 LIM map is inherited'))
        e=intake.lifecycle(b,loaded_inputs,authenticator=authenticator)
    else:e=dict(execution='held-missing-service-fleet-cashflows',whole_life_cost_usd=None,**FLAGS)
    failures=[dict(name=r['name'],execution=r['result']['execution'],final_front_m=r['result'].get('final_front_m'),
        stopping_error_m=r['result'].get('stopping_error_m'),speed_cap_exceeded=r['result'].get('speed_cap_exceeded'),
        requested_service_screen_passed=r['result'].get('requested_service_screen_passed'))
        for r in rows if not r['result'].get('requested_service_screen_passed',False)]
    value=dict(schema='osr-continuing-cell-evaluation/1',candidate_id=b['candidate_id'],vehicle_id=vehicle['vehicle_id'],distance_m=distance_m,
        body_candidate_id=vehicle['candidate_id'],bundle=b,vehicle_summary=vehicle['summary'],alternative=a,civil=c,production=p,
        journeys=rows,operating_input_admission=admitted,economics=e,
        journey_to_civil_load_transfer=coupled_loads,
        physical_redesign_trials=exploration,architecture_comparison=alternative_comparison,
        alternate_journeys=alternate_journeys,
        conditional_numerical_arrivals=sum(r['result']['conditional_numerical_arrival'] for r in rows),
        conditional_service_screen_passes=sum(r['result'].get('requested_service_screen_passed',False) for r in rows),
        admitted_operating_maps=0,qualified_numerical_arrivals=0,
        failed_or_emergency_contexts=failures,integrated_winner=None,
        next_experiments=[dict(kind='physical-necessary-bound',context='uphill-2percent',action='Change actual power distribution or route/grade profile; body thinning does not remove specific-energy limit'),
            dict(kind='measurement',context='station-contact-drive',action='Measure wet/dry friction, clamp control, handoff, spin-up, strip attachment and repeated drive duty'),
            dict(kind='measurement',context='independent-braking',action='Measure pressure response, friction/fade, adhesion/WSP, thermal duty and stopping distribution'),
            dict(kind='definition',context='complete-installation',action='Resolve remaining equipment, geotechnics, station access, manufacture and whole-life prices')],
        source_sha256=sources(root),**FLAGS)
    value['evaluation_id']=identity(value);return value


def compact(r):
    return dict(candidate_id=r['candidate_id'],evaluation_id=r['evaluation_id'],vehicle_id=r['vehicle_id'],distance_m=r['distance_m'],
        alternative=r['alternative']['kind'],mass=r['vehicle_summary'],conditional_numerical_arrivals=r['conditional_numerical_arrivals'],
        conditional_service_screen_passes=r['conditional_service_screen_passes'],
        scenarios=len(r['journeys']),qualified_numerical_arrivals=r['qualified_numerical_arrivals'],admitted_operating_maps=r['admitted_operating_maps'],
        failures=r['failed_or_emergency_contexts'],known_vehicle_stock_process_cost_usd=r['production']['known_vehicle_stock_process_cost_usd'],
        complete_installed_cost_usd=None,whole_life_cost_usd=None,next_experiments=r['next_experiments'],**FLAGS)


def _write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);raw=encoded(value)
    path.write_bytes(gzip.compress(raw,mtime=0) if path.suffix=='.gz' else raw)


def _read(path):
    path=Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size>128*1024**2:raise ValueError('Bounded ordinary continuing packet required')
    if path.suffix=='.gz':
        with gzip.open(path,'rb') as f:raw=f.read(128*1024**2+1)
    else:raw=path.read_bytes()
    if len(raw)>128*1024**2:raise ValueError('Decompressed continuing packet exceeds budget')
    return json.loads(raw)


def run(state,*,root=ROOT,max_cases=10,maximum_seconds=1800.):
    if type(max_cases) is not int or not 0<=max_cases<=10 or not 0<maximum_seconds<=1800.:raise ValueError('Bounded persistent run required')
    folder=Path(state);folder.mkdir(parents=True,exist_ok=True)
    if folder.is_symlink():raise ValueError('Ordinary private run directory required')
    with (folder/'.coordinator.lock').open('a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as err:raise ValueError('Continuing coordinator already running') from err
        epoch=sources(root);started=time.monotonic();rows=[];pending=[];new=0;cache={}
        archive=pipeline._input_archive(root,epoch);source=folder/'input-sources.tar.gz'
        if source.exists() and source.read_bytes()!=archive:raise ValueError('Preserve old run; use new directory for a changed source epoch')
        if not source.exists():source.write_bytes(archive)
        for request in plan()['requests']:
            key=identity(dict(request=request,sources=epoch));path=folder/'cases'/(key+'.json.gz')
            if path.exists():report=_read(path)
            elif new>=max_cases or time.monotonic()-started>=maximum_seconds:pending.append(request);continue
            else:
                vid=request['vehicle_id']
                if vid not in cache:cache[vid]=vehicles.evaluate(vid,root)
                report=evaluate(cache[vid],request['distance_m'],request['kind'],root=root);_write(path,report);new+=1
            if report.get('source_sha256')!=epoch or any(report.get(k) is not False for k in FLAGS) or report['evaluation_id']!=identity({k:v for k,v in report.items() if k!='evaluation_id'}):raise ValueError('Cached continuing evaluation source, disposition or identity differs')
            _unreleased(report)
            if sources(root)!=epoch:raise ValueError('Source changed during run; completed cases preserved, publication held')
            rows.append(dict(request=request,path=path.relative_to(folder).as_posix(),summary=compact(report)))
        r=dict(schema='osr-continuing-cell-run/1',source_sha256=epoch,cases=rows,pending=pending,new_cases=new,integrated_winner=None,**FLAGS)
        r['run_id']=identity({k:v for k,v in r.items() if k!='new_cases'});_write(folder/'latest.json',r);return r


def verify(state,*,root=ROOT,replay=True):
    folder=Path(state)
    if folder.is_symlink():raise ValueError('Ordinary continuing state directory required')
    r=_read(folder/'latest.json');epoch=sources(root)
    if r.get('schema')!='osr-continuing-cell-run/1' or r['source_sha256']!=epoch or r['run_id']!=identity({k:v for k,v in r.items() if k not in ('run_id','new_cases')}):raise ValueError('Continuing run source/identity differs')
    if any(r.get(k) is not False for k in FLAGS):raise ValueError('Research packages cannot issue release')
    requests=[x['request'] for x in r['cases']]+r['pending']
    if sorted(map(identity,requests))!=sorted(map(identity,plan()['requests'])):raise ValueError('Executed/pending coverage differs')
    if (folder/'input-sources.tar.gz').read_bytes()!=pipeline._input_archive(root,epoch):raise ValueError('Continuing source snapshot differs')
    files={'latest.json','input-sources.tar.gz'};cache={}
    for row in r['cases']:
        req=row['request'];path='cases/'+identity(dict(request=req,sources=epoch))+'.json.gz'
        if row['path']!=path:raise ValueError('Exact continuing case path required')
        value=_read(folder/path)
        _unreleased(value)
        if value.get('source_sha256')!=epoch or any(value.get(k) is not False for k in FLAGS):raise ValueError('Continuing evaluation source or release disposition differs')
        if value['evaluation_id']!=identity({k:v for k,v in value.items() if k!='evaluation_id'}) or encoded(compact(value))!=encoded(row['summary']):raise ValueError('Continuing case/summary identity differs')
        if replay:
            vid=req['vehicle_id']
            if vid not in cache:cache[vid]=vehicles.evaluate(vid,root)
            expected=evaluate(cache[vid],req['distance_m'],req['kind'],root=root)
            if encoded(value)!=encoded(expected):raise ValueError('Independent semantic reconstruction differs')
        files.add(path)
    actual={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file() and p.name!='.coordinator.lock'}
    if actual!=files or any(p.is_symlink() for p in folder.rglob('*')):raise ValueError('Unexpected or linked continuing artifacts')
    return dict(verified=True,run_id=r['run_id'],cases=len(r['cases']),pending=len(r['pending']),semantic_replay_executed=replay,
        conditional_numerical_arrivals=sum(x['summary']['conditional_numerical_arrivals'] for x in r['cases']),qualified_numerical_arrivals=0,**FLAGS)


def publish(state,*,root=ROOT,output=None):
    validation=verify(state,root=root);folder=Path(state);target=Path(output or Path(root)/OUTPUT);target.mkdir(parents=True,exist_ok=True)
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode='w') as a:
        for path in sorted(folder.rglob('*')):
            if path.is_file() and path.name!='.coordinator.lock':
                raw=path.read_bytes();info=tarfile.TarInfo(path.relative_to(folder).as_posix());info.size=len(raw);info.mode=0o644;info.mtime=0
                a.addfile(info,io.BytesIO(raw))
    (target/'continuing-cell.tar.gz').write_bytes(gzip.compress(stream.getvalue(),mtime=0))
    index=_read(folder/'latest.json');summary=dict(schema='osr-continuing-cell-workbench/1',run_id=index['run_id'],cases=[x['summary'] for x in index['cases']],pending=index['pending'],**FLAGS)
    _write(target/'summary.json',summary)
    r=dict(schema='osr-continuing-cell-publication/1',source_sha256=sources(root),run_id=index['run_id'],validation=validation,
        files_sha256={n:digest(target/n) for n in ('continuing-cell.tar.gz','summary.json')},**FLAGS)
    r['publication_id']=identity(r);_write(target/'manifest.json',r);return r


def verify_publication(*,root=ROOT,output=None):
    target=Path(output or Path(root)/OUTPUT);r=_read(target/'manifest.json')
    if r.get('schema')!='osr-continuing-cell-publication/1' or r.get('publication_id')!=identity({k:v for k,v in r.items() if k!='publication_id'}) or r['source_sha256']!=sources(root) or any(r.get(k) is not False for k in FLAGS):raise ValueError('Continuing publication source/identity/disposition differs')
    if set(r['files_sha256'])!={'continuing-cell.tar.gz','summary.json'} or any(digest(target/n)!=h for n,h in r['files_sha256'].items()):raise ValueError('Continuing payload inventory differs')
    with tempfile.TemporaryDirectory(prefix='osr-progress-replay-') as temp:
        with tarfile.open(target/'continuing-cell.tar.gz','r:gz') as a:
            members=a.getmembers();names=[m.name for m in members]
            if len(names)!=len(set(names)) or len(names)>12 or sum(m.size for m in members)>512*1024**2 or any(not m.isfile() or Path(m.name).is_absolute() or '..' in Path(m.name).parts for m in members):raise ValueError('Bounded ordinary continuing archive required')
            a.extractall(temp,filter='data')
        result=verify(temp,root=root)
        if result!=r['validation']:raise ValueError('Continuing publication semantic replay differs')
        index=_read(Path(temp)/'latest.json');expected=dict(schema='osr-continuing-cell-workbench/1',run_id=index['run_id'],cases=[x['summary'] for x in index['cases']],pending=index['pending'],**FLAGS)
        if _read(target/'summary.json')!=expected:raise ValueError('Continuing workbench summary differs from evaluations')
    return dict(result,publication_id=r['publication_id'])
