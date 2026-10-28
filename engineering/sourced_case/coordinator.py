"""Sourced hardware revisions propagated through one reference-cell definition."""
from pathlib import Path
from copy import deepcopy
from math import ceil,fsum
import gzip,json,time,tarfile,io,tempfile,fcntl
from . import ROOT,FLAGS,identity,encoded,digest
from . import drive,equipment,commerce,operating
from . import layered_structure as structure,whole_refinement as whole_structure
from engineering.reference_cell import vehicles,bundle as vehicle_adapter
from engineering.railway_progress import civil,production,load_transfer
from engineering.railway_twin import pipeline

OUTPUT='docs/design-engine/sourced-case'


def sources(root=ROOT):
    from engineering.railway_progress.coordinator import sources as previous
    s=previous(root)
    for folder in ('engineering/sourced_case','engineering/sourced_redesign'):
        for p in sorted((Path(root)/folder).rglob('*')):
            if p.is_file() and p.suffix in ('.py','.json','.html') and 'tests' not in p.parts and '__pycache__' not in p.parts:s[p.relative_to(root).as_posix()]=digest(p)
    return dict(sorted(s.items()))


def revised(vehicle_id='V1',root=ROOT,parallel_strings=8):
    from . import power_revision
    from engineering.sourced_redesign import family_interfaces
    v=vehicles.evaluate(vehicle_id,root)
    v=family_interfaces.revision(v,root=root)
    v=whole_structure.revision(structure.revision(v,root=root),root=root)
    e=equipment.substitute(v,root=root,hvac_units_per_car=1,battery_parallel_strings=4)
    e=power_revision.revise(e,parallel_strings=parallel_strings,root=root)
    return e


def compose(e,distance_m=2000.,*,variant='parker400-dpw-h300',distributed=False,ambient_C=55.,root=ROOT):
    v=e['vehicle'];base=vehicle_adapter.materialize(v,distance_m,root=root)
    cfg=drive.configure(variant,ambient_C=ambient_C,root=root)
    params=dict(roller_pairs_per_bank=8)
    extra=[]
    if distributed:
        extra=[x for x in (600.,800.,1000.,1200.,1400.,1600.,1750.) if x<distance_m-220.]
        params['bank_starts_m']=[-12.,91.,194.,297.,400.]+extra
    a=drive.materialize(v,base,distance_m=distance_m,configuration=cfg,parameters=params,root=root)
    a['additional_power_windows_m']=[[x,x+116.5] for x in extra]
    a.pop('evaluation_id',None);a['evaluation_id']=identity(a)
    definition=civil.geometry_definition(v,distance_m,a,root=root)
    physical=dict(schema='osr-sourced-cell-physical/1',vehicle=v['candidate_id'],wayside_drive=a['candidate_id'],
        civil_geometry=definition['physical_geometry_id'],distance_m=distance_m,cars=6,car_length_m=17.,
        normal_places_per_car=46,auxiliary_infrastructure='Station600V shore connection and charger interfaces remain design tasks')
    cid=identity(physical)
    b={k:deepcopy(base[k]) for k in ('body_candidate_id','body_definition_id','support_component_id','cars','car_length_m','mass',
        'mass_interval_kg_per_car','rotating_equivalent_kg_per_car','rotor_definition_id','brake_definition','requirements','requirement_revision',
        'route_axle_offsets_from_leading_nose_m','source_sha256')}
    b.update(schema='osr-sourced-reference-cell-bundle/1',candidate_id=cid,bundle_id=cid,propulsion_component_id=a['candidate_id'],
        architecture_case=dict(physical_definition=dict(route=dict(station_spacing_m=distance_m),composition=physical)),
        progress_architecture=dict(alternative_candidate_id=a['candidate_id']),complete_installed_mass_kg=None,**FLAGS)
    constraints=equipment.constraints(e,ambient_C=ambient_C,disc_specific_heat_J_kgK=500.)
    if constraints.get('brake',{}).get('nominal_train_force_before_adhesion_N') is not None:
        b['sourced_brake']=dict(nominal_train_force_N=constraints['brake']['nominal_train_force_before_adhesion_N'],
            provenance='Source nominal caliper/clamp and pad coefficient; not a measured operating brake map',
            equipment_evaluation_id=e['evaluation_id'],pad_temperature_and_wet_map=None)
    b['brake_definition']['candidate_id']=cid;b['brake_definition']['propulsion_component_id']=a['candidate_id']
    b['brake_definition'].pop('brake_definition_id',None);b['brake_definition']['brake_definition_id']=identity(b['brake_definition'])
    b['definition_id']=identity(b)
    return b,a,civil.generate(cid,definition),constraints


def contexts(distance_m,ambient_C,aux_W):
    cases=[dict(name=load,load=load) for load in ('empty','normal','crowd-control')]
    cases.extend([dict(name='uphill',grade_fraction=.02),dict(name='downhill',grade_fraction=-.02),
        dict(name='low-adhesion',adhesion_coefficient=.025,condition='low-friction'),dict(name='one-bank-failed',failed_banks=[2]),
        dict(name='power-interruption',power_interrupt_at_s=15.),dict(name='emergency',emergency_at_m=800.)])
    return [dict(name=c.pop('name'),scenario=operating.scenario(distance_m=distance_m,ambient_C=ambient_C,auxiliary_W_per_car=aux_W,**c)) for c in cases]


def evaluate(e,distance_m=2000.,*,variant='parker400-dpw-h300',distributed=False,ambient_C=55.,root=ROOT):
    from . import charging as shore_charging
    b,a,c,limits=compose(e,distance_m,variant=variant,distributed=distributed,ambient_C=ambient_C,root=root)
    # Electrical source maximum includes600V compressor plus26V fans, with
    # explicitly added essential-load allowance. Actual cabin cooling is separate.
    aux=limits['HVAC']['per_car_peak_electrical_W']+1000.
    rows=[dict(name=x['name'],result=operating.evaluate(b,a,context=x['scenario'])) for x in contexts(distance_m,ambient_C,aux)]
    p=production.compile(e['vehicle'],c,a,b['candidate_id'])
    transfer=load_transfer.evaluate(b,c,a,rows)
    normal=next(x['result'] for x in rows if x['name']=='normal')
    charging=None;charging_proposal=None
    if normal.get('conditional_numerical_arrival',False) and 'journey_time_s' in normal:
        t=normal['journey_time_s'];fleet=ceil(2*(t+35)/120.)
        terminal_dwell=max(35.,fleet*120./2-t)
        charging=dict(fleet_trainsets=fleet,minimum_passenger_dwell_s=35.,two_terminal_cycle_dwell_s=terminal_dwell,
            fixed35s=commerce.charge_budget(e,aux,t,dwell_s=35.,bms_current_A=1000.),
            terminal_cycle=commerce.charge_budget(e,aux,t,dwell_s=terminal_dwell,bms_current_A=1000.),
            terminal_layover_is_not_general_city_station_dwell=True,protected_headway_qualified=False)
        charging_proposal=shore_charging.design(e,normal,terminal_dwell,station_ambient_C=ambient_C,root=root)
    prices=commerce.catalogue(root);sku_battery=next(x['SKU'] for x in prices['prices'] if 'BAT524120620'==x['SKU'])
    reg=e['vehicle']['registry'];part={x['physical_definition_id']:x for x in reg['parts']}
    ids=[o['occurrence_id'] for o in reg['occurrences'] if 'VICTRON-NG256-200' in part[o['part_definition_id']]['part_id']]
    cost=commerce.price_subtotal(b['candidate_id'],[dict(candidate_id=b['candidate_id'],SKU=sku_battery,occurrence_ids=ids)],root=root)
    result=dict(schema='osr-sourced-cell-evaluation/1',candidate_id=b['candidate_id'],body_candidate_id=e['vehicle']['candidate_id'],vehicle_id=e['vehicle']['vehicle_id'],
        distance_m=distance_m,variant=variant,distributed=distributed,ambient_C=ambient_C,bundle=b,drive=a,equipment_limits=limits,
        vehicle_summary=e['vehicle']['summary'],auxiliary_power_case=e.get('complete_source_power_case'),
        civil=c,manufacturing=p,journeys=rows,civil_load_transfer=transfer,charging=charging,charging_proposal=charging_proposal,partial_public_price=cost,
        conditional_arrivals=sum(x['result'].get('conditional_numerical_arrival',False) for x in rows),
        conditional_motion_screens=sum(x['result'].get('requested_service_screen_passed',False) for x in rows),
        qualified_journeys=0,operating_map_admitted=False,whole_life_cost=None,integrated_winner=None,
        next_tasks=['Actual installed joint/laminate/thermal/fatigue/fire and brake tests',
            'Rated motor/inverter/contact/gear repeated duty and wet contaminated grip tests',
            'Hot cabin cooling capacity and converter conditioned-enclosure proof',
            'Station shore charging, isolation, taper and fleet/terminal timetable validation',
            'Site/seismic/geotechnic/civil strength, actual full prices, HIL/independent/pilot acceptance'],
        source_sha256=sources(root),**FLAGS)
    result['evaluation_id']=identity(result);return result


def plan():
    return [dict(vehicle_id=v,distance_m=d,variant=variant,distributed=distributed,ambient_C=ambient)
        for v in vehicles.variants() for d in (1500.,2000.)
        for variant,ambient,distributed in (('parker400-dpw-h300',55.,False),('parker400-dpw-h300',55.,True),('emrax348-lv43-h300',25.,False))]


def write(path,v):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);raw=encoded(v);path.write_bytes(gzip.compress(raw,mtime=0) if path.suffix=='.gz' else raw)


def read(path):
    path=Path(path)
    if path.is_symlink() or path.stat().st_size>128*1024**2:raise ValueError('Ordinary bounded sourced packet required')
    if path.suffix=='.gz':
        with gzip.open(path,'rb') as f:raw=f.read(128*1024**2+1)
    else:raw=path.read_bytes()
    if len(raw)>128*1024**2:raise ValueError('Sourced packet exceeds decompression budget')
    return json.loads(raw)


def _run(state,root=ROOT,max_cases=30):
    if type(max_cases) is not int or not 0<=max_cases<=len(plan()):raise ValueError('Bounded sourced-case run required')
    folder=Path(state);folder.mkdir(parents=True,exist_ok=True);epoch=sources(root);cache={};cases=[];pending=[];new=0
    source=pipeline._input_archive(root,epoch)
    if (folder/'input-sources.tar.gz').exists() and (folder/'input-sources.tar.gz').read_bytes()!=source:raise ValueError('Use a new directory for changed sources')
    (folder/'input-sources.tar.gz').write_bytes(source)
    for req in plan():
        key=identity(dict(request=req,source=epoch));path=folder/'cases'/(key+'.json.gz')
        if path.exists():r=read(path)
        elif new>=max_cases:pending.append(req);continue
        else:
            v=req['vehicle_id']
            if v not in cache:cache[v]=revised(v,root);write(folder/'vehicles'/(v+'.json.gz'),cache[v])
            r=evaluate(cache[v],root=root,**{k:x for k,x in req.items() if k!='vehicle_id'});write(path,r);new+=1
        if r['evaluation_id']!=identity({k:v for k,v in r.items() if k!='evaluation_id'}) or r['source_sha256']!=epoch:raise ValueError('Cached sourced result differs')
        from engineering.railway_progress.coordinator import _unreleased
        _unreleased(r)
        if sources(root)!=epoch:raise ValueError('Sources changed; preserve completed runs without mixing epochs')
        cases.append(dict(request=req,path=path.relative_to(folder).as_posix(),evaluation_id=r['evaluation_id'],candidate_id=r['candidate_id'],arrivals=r['conditional_arrivals'],motion_screens=r['conditional_motion_screens']))
    value=dict(schema='osr-sourced-cell-run/1',source_sha256=epoch,cases=cases,pending=pending,**FLAGS)
    value['run_id']=identity(value);write(folder/'latest.json',value);return value


def run(state,root=ROOT,max_cases=30):
    folder=Path(state)
    if folder.is_symlink():raise ValueError('Ordinary private sourced run required')
    folder.mkdir(parents=True,exist_ok=True)
    with (folder/'.coordinator.lock').open('a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as err:raise ValueError('Sourced coordinator already running') from err
        return _run(state,root,max_cases)


def verify(state,root=ROOT,replay=True):
    folder=Path(state);value=read(folder/'latest.json');epoch=sources(root)
    if folder.is_symlink() or value['run_id']!=identity({k:v for k,v in value.items() if k!='run_id'}) or value['source_sha256']!=epoch:raise ValueError('Sourced run identity or source differs')
    if sorted(map(identity,[x['request'] for x in value['cases']]+value['pending']))!=sorted(map(identity,plan())):raise ValueError('Sourced request coverage differs')
    if (folder/'input-sources.tar.gz').read_bytes()!=pipeline._input_archive(root,epoch):raise ValueError('Sourced snapshot differs')
    from engineering.railway_progress.coordinator import _unreleased
    _unreleased(value)
    cache={};files={'input-sources.tar.gz','latest.json'}
    for row in value['cases']:
        req=row['request'];expected='cases/'+identity(dict(request=req,source=epoch))+'.json.gz'
        if row['path']!=expected:raise ValueError('Noncanonical case path')
        r=read(folder/row['path']);_unreleased(r)
        if r['source_sha256']!=epoch or row['candidate_id']!=r['candidate_id'] or row['arrivals']!=r['conditional_arrivals'] or row['motion_screens']!=r['conditional_motion_screens']:raise ValueError('Sourced candidate/source/summary differs')
        if r['evaluation_id']!=row['evaluation_id'] or r['evaluation_id']!=identity({k:v for k,v in r.items() if k!='evaluation_id'}):raise ValueError('Sourced case differs')
        v=req['vehicle_id']
        if v not in cache:
            cache[v]=revised(v,root)
            if encoded(cache[v])!=encoded(read(folder/'vehicles'/(v+'.json.gz'))):raise ValueError('Sourced registry revision differs')
        if replay and encoded(r)!=encoded(evaluate(cache[v],root=root,**{k:x for k,x in req.items() if k!='vehicle_id'})):raise ValueError('Sourced semantic replay differs')
        files.update((row['path'],'vehicles/'+v+'.json.gz'))
    if {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file() and p.name!='.coordinator.lock'}!=files or any(p.is_symlink() for p in folder.rglob('*')):raise ValueError('Unexpected sourced payload')
    return dict(verified=True,run_id=value['run_id'],cases=len(value['cases']),pending=len(value['pending']),semantic_replay_executed=replay,qualified_journeys=0,**FLAGS)


def publish(state,root=ROOT,output=None):
    check=verify(state,root);folder=Path(state);target=Path(output or Path(root)/OUTPUT);target.mkdir(parents=True,exist_ok=True)
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode='w') as archive:
        for p in sorted(folder.rglob('*')):
            if p.is_file() and p.name!='.coordinator.lock':
                data=p.read_bytes();info=tarfile.TarInfo(p.relative_to(folder).as_posix());info.size=len(data);info.mode=0o644;info.mtime=0;archive.addfile(info,io.BytesIO(data))
    (target/'sourced-cell.tar.gz').write_bytes(gzip.compress(stream.getvalue(),mtime=0))
    index=read(folder/'latest.json');summary=dict(schema='osr-sourced-cell-summary/1',run_id=index['run_id'],cases=index['cases'],pending=index['pending'],**FLAGS)
    write(target/'summary.json',summary)
    manifest=dict(schema='osr-sourced-cell-publication/1',source_sha256=sources(root),validation=check,
        files_sha256={n:digest(target/n) for n in ('sourced-cell.tar.gz','summary.json')},**FLAGS)
    manifest['publication_id']=identity(manifest);write(target/'manifest.json',manifest);return manifest


def verify_publication(root=ROOT,output=None):
    target=Path(output or Path(root)/OUTPUT);manifest=read(target/'manifest.json')
    from engineering.railway_progress.coordinator import _unreleased
    _unreleased(manifest)
    if manifest['publication_id']!=identity({k:v for k,v in manifest.items() if k!='publication_id'}) or manifest['source_sha256']!=sources(root):raise ValueError('Sourced publication source/identity differs')
    if set(manifest['files_sha256'])!={'sourced-cell.tar.gz','summary.json'} or any(digest(target/n)!=h for n,h in manifest['files_sha256'].items()):raise ValueError('Sourced publication inventory differs')
    with tempfile.TemporaryDirectory(prefix='osr-sourced-replay-') as temp:
        with tarfile.open(target/'sourced-cell.tar.gz','r:gz') as archive:
            entries=archive.getmembers();names=[m.name for m in entries]
            if len(names)!=len(set(names)) or len(names)>40 or sum(m.size for m in entries)>1024**3 or any(not m.isfile() or Path(m.name).is_absolute() or '..' in Path(m.name).parts for m in entries):raise ValueError('Bounded ordinary sourced archive required')
            archive.extractall(temp,filter='data')
        result=verify(temp,root)
        if result!=manifest['validation']:raise ValueError('Sourced archive replay differs')
        index=read(Path(temp)/'latest.json');summary=dict(schema='osr-sourced-cell-summary/1',run_id=index['run_id'],cases=index['cases'],pending=index['pending'],**FLAGS)
        if encoded(summary)!=encoded(read(target/'summary.json')):raise ValueError('Sourced published summary differs')
    return dict(result,publication_id=manifest['publication_id'])
