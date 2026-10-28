"""Versioned component master -> same-candidate reference-cell packages and holds."""
from pathlib import Path
from copy import deepcopy
from collections import Counter
import gzip,io,json,tarfile,tempfile,time,fcntl
from engineering.railway_twin import pipeline as regression
from engineering.design_search import test_readiness
from engineering.component_registry import validate_registry
from . import ROOT,FLAGS,identity,encoded,digest
from . import vehicles,architecture,civil,manufacturing,physics,bundle,economics,qualification

OUTPUT='docs/design-engine/reference-cell'
SPEC='campaigns/sourced-reference-cell.toml'


def sources(root=ROOT):
    root=Path(root);value=regression.sources(root)
    independent_methods={'geometry.py','motor_refinement.py','native_evidence.py','native_cad.py'}
    for folder in ('engineering/component_registry','engineering/reference_cell'):
        for p in sorted((root/folder).rglob('*')):
            if p.is_file() and p.suffix in ('.py','.json','.html','.js','.css') and 'tests' not in p.parts and '__pycache__' not in p.parts and not (folder.endswith('reference_cell') and p.name in independent_methods):
                value[p.relative_to(root).as_posix()]=digest(p)
    for name in (SPEC,'osr-cell','services/integration/osr_integration/reference_cell.py'):
        value[name]=digest(root/name)
    if value['engineering/reference_cell/coordinator.py']!=digest(__file__):raise ValueError('Executing cell coordinator differs from declared source root')
    return dict(sorted(value.items()))


def plan(root=ROOT):
    import tomllib
    s=tomllib.loads((Path(root)/SPEC).read_text())
    if (s.get('schema')!='osr-sourced-reference-cell/1' or s.get('reference_changes_allowed') is not False
        or s.get('vehicle_ids')!=vehicles.variants() or s.get('distances_m')!=[1500.,2000.] or s.get('maximum_cases')!=10):
        raise ValueError('Explicit independent five-vehicle/two-distance research contract required')
    return dict(specification=s,requests=[dict(vehicle_id=v,distance_m=d) for v in vehicles.variants() for d in s['distances_m']],
        selected_reference_changed=False,physical_qualification_required=True)


def structural_loads(vehicle,b):
    """Actual placed part mass bounds -> body support reactions; not body strength."""
    r=vehicle['registry'];parts={p['physical_definition_id']:p for p in r['parts']}
    car=[o for o in r['occurrences'] if o['occurrence_id'].startswith('car-1/')]
    load=[]
    for o in car:
        p=parts[o['part_definition_id']];m=p['mass']['upper_bound_kg']
        if m is None:continue
        load.append((o['transform'][0][3],m*9.80665))
    a,c=vehicle['interfaces']['bogie_centres_per_car_m'];rows=[]
    for name,people in (('empty',0),('normal',46),('crowd-control',160)):
        passengers=people*75.*9.80665
        forces=load+[(8.5,passengers)]
        total=sum(F for x,F in forces);right=sum(F*(x-a) for x,F in forces)/(c-a);left=total-right
        rows.append(dict(name=name,passengers=people,known_upper_account_weight_N=total,
            left_bogie_reaction_N=left,right_bogie_reaction_N=right,force_residual_N=left+right-total,
            moment_residual_Nm=right*(c-a)-sum(F*(x-a) for x,F in forces),
            passengers_centroid_hypothesis_m=8.5,part_mass_at_declared_centroid_is_hypothesis=True))
    return dict(candidate_id=b['candidate_id'],body_candidate_id=r['candidate_id'],load_cases=rows,
        executed_FEA=False,body_strength_supported=False,
        missing=['Qualified directional laminate stacks and joint laws','Correlated attachment/support load paths',
                 'Buckling/fatigue/crash/fire/torsion and full shell/frame refinement'],**FLAGS)


def evaluate(vehicle_id='V1',distance_m=2000.,*,root=ROOT,propulsion='five-20m',guideway='box',vehicle=None):
    v=vehicles.evaluate(vehicle_id,root) if vehicle is None else vehicle
    validate_registry(v['registry']);b=bundle.materialize(v,distance_m,propulsion,guideway,root)
    cid=b['candidate_id'];body=v['candidate_id'];upper=v['summary']['mass_upper_bound_kg']
    wayside=b['architecture_case']['physical_definition']['wayside']
    starts=wayside.get('bank_starts_from_initial_nose_m',wayside.get('bank_starts_m',[]))
    length=wayside.get('bank_length_m',20.)
    part_lookup={p['physical_definition_id']:p for p in v['registry']['parts']}
    floor_top=max(o['transform'][2][3]+part_lookup[o['part_definition_id']]['geometry']['dimensions_m'][2]/2 for o in v['registry']['occurrences'] if o['occurrence_id'].startswith('car-1/') and 'FLOOR-FACE' in part_lookup[o['part_definition_id']]['part_id'])
    door_side=-1 if v['interfaces']['door_side_y_m']<0 else 1
    c=civil.generate(cid,distance_m=distance_m,section=guideway,bank_starts_m=starts,bank_length_m=length,
        car_mass_upper_kg=None if upper is None else [upper/6+12000.]*6,
        axle_positions_m=v['interfaces']['axle_longitudinal_positions_m'],primary_stock=b.get('wayside_primary_stock'),
        platform_height_above_rail_m=floor_top,door_side=door_side)
    # Seal actual generated civil/station geometry into the integrated physical ID.
    # Evaluator/residual/cost changes are excluded; changed steel/concrete/poses are not.
    geometry_rows=[{k:p[k] for k in ('id','assembly','kind','at_m','size_m','net_volume_m3','material','manufacturing_method')} for p in c['stock']]
    physical=b['architecture_case']['physical_definition'];physical['civil_geometry_definition_id']=identity(geometry_rows)
    final_id=identity(physical)
    b['candidate_id']=b['bundle_id']=final_id;b['architecture_case']['candidate_id']=final_id
    from engineering.design_search import capabilities,railway_bundle
    b['architecture_case']['capability_composition']=capabilities.composition('P1',final_id,b['requirement_revision'])
    b['architecture_case'].pop('case_id',None);b['architecture_case']['case_id']=identity(b['architecture_case'])
    b['brake_definition']['candidate_id']=final_id;b['brake_definition'].pop('brake_definition_id',None)
    b['brake_definition']['brake_definition_id']=identity(b['brake_definition'])
    b['source_sha256']['engineering/reference_cell/civil.py']=digest(Path(root)/'engineering/reference_cell/civil.py')
    b['source_sha256']['engineering/reference_cell/coordinator.py']=digest(__file__)
    b.pop('definition_id',None);b['definition_id']=identity(b);railway_bundle.validate(b)
    cid=final_id
    # Geometry is unchanged; all candidate-bound physical occurrences and loads
    # are rematerialized under the final composition rather than relabelled.
    c=civil.generate(cid,distance_m=distance_m,section=guideway,bank_starts_m=starts,bank_length_m=length,
        car_mass_upper_kg=None if upper is None else [upper/6+12000.]*6,
        axle_positions_m=v['interfaces']['axle_longitudinal_positions_m'],primary_stock=b.get('wayside_primary_stock'),
        platform_height_above_rail_m=floor_top,door_side=door_side)
    m=manufacturing.compile(v,c,bundle=b)
    cases=[]
    for request in physics.scenarios(b):
        result=physics.evaluate(b,scenario_overrides=request['scenario'])
        cases.append(dict(name=request['name'],candidate_id=cid,scenario_id=result['scenario']['scenario_id'],
            execution=result['execution'],numerical_arrival_predicted=result['numerical_arrival_predicted'],
            reasons=result.get('reasons',[]),evaluation_id=result['evaluation_id']))
    service=dict(cars=6,normal_places_per_car=46,headway_s=120.,capacity_pphpd=8280.,station_spacing_m=distance_m,
                 protected_service_qualified=False,fleet_size=None)
    e=dict(candidate_id=cid,state='missing-qualified-service-and-cashflows',service_context=service,
        required_scopes=list(economics.SCOPES),fleet_trainsets=None,conditional_NPV_usd=None,whole_life_cost_usd=None,
        owning_adapter='engineering.reference_cell.economics.evaluate',economic_winner=None,**FLAGS)
    readiness=qualification.build(b,root=root)
    closures=[dict(domain='vehicle',state='physical-and-supplier-evidence-open',items=v['unresolved']),
        dict(domain='structure',state='load-requests-only',items=['Strength, buckling, fatigue, joints, fire and actual material allowables']),
        dict(domain='propulsion',state='no-admitted-operating-map',items=['Segmented-secondary model, convergence, force/current/control/thermal/handoff and physical correlation']),
        dict(domain='journey',state='not-run-without-supported-inputs',items=[f'{len(cases)} required contexts; zero completed production arrivals']),
        dict(domain='civil',state='generated-unqualified-assemblies',items=c['open_items']),
        dict(domain='economics',state='conditional-C-known-stock-only',items=['Actual quotes, qualified processes, full installed scope and whole-life service costs']),
        dict(domain='GoA4-and-HIL',state='physical-hardware-tests-open',items=['Actual braking/sensing/timing/HIL, independent safety review']),
        dict(domain='commissioning-and-pilot',state='external-physical-work-required',items=['Authenticated prototype tests, operating pilot and city/site approval'])]
    value=dict(schema='osr-sourced-reference-cell-evaluation/1',candidate_id=cid,body_candidate_id=body,
        vehicle_id=vehicle_id,distance_m=distance_m,propulsion=propulsion,guideway=guideway,
        bundle=b,vehicle_summary=v['summary'],functional_requirements=v['functional_requirements'],
        structural_loads=structural_loads(v,b),civil=c,manufacturing=m,economics=e,scenarios=cases,
        physical_test_programme=readiness,closures=closures,
        dependency_edges=architecture.EDGES,
        next_experiment=architecture.revision(cid,'missing-evidence',[dict(domain=x['domain'],state=x['state']) for x in closures]),
        available_operating_maps=0,completed_production_journeys=0,engineering_complete=False,
        source_sha256=sources(root),**FLAGS)
    value['evaluation_id']=identity(value);return value


def compact(report):
    return dict(vehicle_id=report['vehicle_id'],distance_m=report['distance_m'],candidate_id=report['candidate_id'],
        body_candidate_id=report['body_candidate_id'],evaluation_id=report['evaluation_id'],
        mass=report['vehicle_summary'],known_C_vehicle_budget_usd=report['manufacturing']['known_vehicle_scope_conditional_usd'],
        actual_quote_occurrence_coverage=report['manufacturing']['actual_quote_occurrence_coverage'],
        span_count=report['civil']['span_count'],station_count=2,scenario_count=len(report['scenarios']),
        completed_production_journeys=0,available_operating_maps=0,closures=report['closures'],**FLAGS)


def _write(path,value):
    raw=encoded(value);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(gzip.compress(raw,mtime=0) if path.name.endswith('.gz') else raw)


def _read(path):
    if path.is_symlink() or path.stat().st_size>128*1024**2:raise ValueError('Bounded ordinary cell payload required')
    if path.name.endswith('.gz'):
        with gzip.open(path,'rb') as stream:data=stream.read(128*1024**2+1)
    else:data=path.read_bytes()
    if len(data)>128*1024**2:raise ValueError('Decompressed cell payload exceeds budget')
    return json.loads(data)


def run(state,*,root=ROOT,max_cases=10,maximum_seconds=1800.):
    if type(max_cases) is not int or not 0<=max_cases<=10 or not 0<maximum_seconds<=1800:raise ValueError('Bounded persistent reference-cell run required')
    folder=Path(state);folder.mkdir(parents=True,exist_ok=True)
    with (folder/'.coordinator.lock').open('a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as error:raise ValueError('Reference-cell coordinator already running') from error
        epoch=sources(root);contract=plan(root)
        source_path=folder/'input-sources.tar.gz'
        expected_sources=regression._input_archive(root,epoch)
        if source_path.exists() and gzip.decompress(source_path.read_bytes())!=gzip.decompress(expected_sources):raise ValueError('Retained input sources differ')
        if not source_path.exists():source_path.write_bytes(expected_sources)
        started=time.monotonic();rows=[];pending=[];done=0;cache={}
        for request in contract['requests']:
            key=identity(dict(request=request,source_sha256=epoch));path=folder/'cases'/(key+'.json.gz')
            if path.exists():
                vid=request['vehicle_id']
                if vid not in cache:cache[vid]=vehicles.evaluate(vid,root)
                report=_read(path)
                if encoded(_read(folder/'vehicles'/(vid+'.json.gz')))!=encoded(cache[vid]) or encoded(report)!=encoded(evaluate(root=root,vehicle=cache[vid],**request)):raise ValueError('Cached cell semantic replay differs')
                if report['source_sha256']!=epoch or report['evaluation_id']!=identity({k:v for k,v in report.items() if k!='evaluation_id'}):
                    raise ValueError('Cached cell source or evaluation differs')
            elif done>=max_cases or time.monotonic()-started>maximum_seconds:
                pending.append(request);continue
            else:
                vid=request['vehicle_id']
                if vid not in cache:cache[vid]=vehicles.evaluate(vid,root)
                report=evaluate(root=root,vehicle=cache[vid],**request);_write(path,report);done+=1
                _write(folder/'vehicles'/(vid+'.json.gz'),cache[vid])
            if sources(root)!=epoch:raise ValueError('Source changed; preserve completed cases without mixed publication')
            rows.append(dict(request=request,path='cases/'+path.name,summary=compact(report)))
        value=dict(schema='osr-sourced-reference-cell-run/1',source_sha256=epoch,contract=contract,
            cases=rows,pending=pending,failed=[],new_cases=done,integrated_winner=None,**FLAGS)
        value['run_id']=identity({k:v for k,v in value.items() if k!='new_cases'})
        _write(folder/'latest.pending.json',value);(folder/'latest.pending.json').replace(folder/'latest.json');return value


def verify(state,*,root=ROOT,strict=False):
    folder=Path(state)
    if folder.is_symlink():raise ValueError('Ordinary cell state directory required')
    value=_read(folder/'latest.json');epoch=sources(root)
    if value.get('schema')!='osr-sourced-reference-cell-run/1' or value['source_sha256']!=epoch or value['contract']!=plan(root) or value['run_id']!=identity({k:v for k,v in value.items() if k not in ('new_cases','run_id')}):raise ValueError('Reference-cell run source/identity differs')
    if any(value.get(k) is not False for k in FLAGS):raise ValueError('Research cannot issue release')
    all_requests=[row['request'] for row in value['cases']]+value['pending']
    if sorted(map(identity,all_requests))!=sorted(map(identity,plan(root)['requests'])):raise ValueError('Executed/pending request coverage differs')
    cache={};files={'latest.json','input-sources.tar.gz'}
    if gzip.decompress((folder/'input-sources.tar.gz').read_bytes())!=gzip.decompress(regression._input_archive(root,epoch)):raise ValueError('Cell source snapshot differs')
    for row in value['cases']:
        request=row['request'];vid=request['vehicle_id'];expected_path='cases/'+identity(dict(request=request,source_sha256=epoch))+'.json.gz'
        if row['path']!=expected_path:raise ValueError('Exact ordinary cell path required')
        if vid not in cache:
            cache[vid]=vehicles.evaluate(vid,root)
            if encoded(_read(folder/'vehicles'/(vid+'.json.gz')))!=encoded(cache[vid]):raise ValueError('Vehicle master semantic replay differs')
        expected=evaluate(root=root,vehicle=cache[vid],**request);actual=_read(folder/row['path'])
        if encoded(actual)!=encoded(expected) or encoded(row['summary'])!=encoded(compact(expected)):raise ValueError('Cell semantic replay differs')
        files.update((row['path'],'vehicles/'+vid+'.json.gz'))
    actual={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file() and p!=folder/'.coordinator.lock'}
    if any(p.is_symlink() for p in folder.rglob('*')) or actual!=files:raise ValueError('Unexpected or linked reference-cell artifacts')
    if strict:raise regression.IncompleteDesign([dict(id=x['domain'],**x) for x in value['cases'][0]['summary']['closures']] if value['cases'] else [dict(id='pending-designs')])
    return dict(verified=True,run_id=value['run_id'],cases=len(value['cases']),pending=len(value['pending']),
                available_operating_maps=0,completed_production_journeys=0,engineering_complete=False,**FLAGS)


def publish(state,*,root=ROOT,output=None):
    result=verify(state,root=root);folder=Path(state);target=Path(output) if output else Path(root)/OUTPUT;target.mkdir(parents=True,exist_ok=True)
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode='w') as archive:
        for path in sorted(folder.rglob('*')):
            if path.is_file() and path.name!='.coordinator.lock':
                raw=path.read_bytes();item=tarfile.TarInfo(path.relative_to(folder).as_posix());item.size=len(raw);item.mtime=0;item.mode=0o644;archive.addfile(item,io.BytesIO(raw))
    path=target/'reference-cell.tar.gz';path.write_bytes(gzip.compress(stream.getvalue(),mtime=0));index=_read(folder/'latest.json')
    summary=dict(schema='osr-reference-cell-workbench/1',cases=[r['summary'] for r in index['cases']],pending=index['pending'],
        architecture_records=list(architecture.defaults().records.values()),**FLAGS)
    _write(target/'summary.json',summary)
    value=dict(schema='osr-reference-cell-publication/1',source_sha256=sources(root),run_id=index['run_id'],
        files_sha256={name:digest(target/name) for name in ('reference-cell.tar.gz','summary.json')},validation=result,**FLAGS)
    value['publication_id']=identity(value);_write(target/'manifest.json',value);return value


def verify_publication(root=ROOT,output=None):
    folder=Path(output) if output else Path(root)/OUTPUT;v=_read(folder/'manifest.json')
    if v.get('schema')!='osr-reference-cell-publication/1' or any(v.get(k) is not False for k in FLAGS):raise ValueError('Cell publication schema or release disposition differs')
    if v['publication_id']!=identity({k:x for k,x in v.items() if k!='publication_id'}) or v['source_sha256']!=sources(root):raise ValueError('Cell publication source/identity differs')
    if set(v['files_sha256'])!={'reference-cell.tar.gz','summary.json'} or any(digest(folder/k)!=h for k,h in v['files_sha256'].items()):raise ValueError('Cell publication payload inventory differs')
    with tempfile.TemporaryDirectory(prefix='osr-cell-replay-') as temp:
        with tarfile.open(folder/'reference-cell.tar.gz','r:gz') as archive:
            members=archive.getmembers();names=[m.name for m in members]
            if len(names)!=len(set(names)) or len(names)>32 or sum(m.size for m in members)>512*1024**2 or any(not m.isfile() or Path(m.name).is_absolute() or '..' in Path(m.name).parts for m in members):raise ValueError('Bounded ordinary cell archive required')
            archive.extractall(temp,filter='data')
        actual=verify(temp,root=root)
        if actual!=v['validation']:raise ValueError('Cell publication semantics differ')
        index=_read(Path(temp)/'latest.json');expected=dict(schema='osr-reference-cell-workbench/1',cases=[r['summary'] for r in index['cases']],pending=index['pending'],architecture_records=list(architecture.defaults().records.values()),**FLAGS)
        if _read(folder/'summary.json')!=expected:raise ValueError('Workbench summary differs from actual cell evaluations')
    return dict(actual,publication_id=v['publication_id'])
