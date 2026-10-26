"""Umbrella research campaign: change railway arrangements, never release them.

Physical definitions, requirements, calculation contexts and selection records
have separate identities. Analytical trajectories describe demanded forces at
an inherited comparison mass; unavailable motors and unknown added equipment
never become available thrust or a complete vehicle weight.
"""
from copy import deepcopy
from pathlib import Path
from math import ceil,isfinite
import gzip,json,itertools,time,tomllib
from engineering.station_rail import ROOT,vehicle,braking,civil
from engineering.station_rail.common import encoded,identity,digest
from . import capabilities

PRODUCER='engineering/design_search/railway_architecture.py'
SPEC='campaigns/whole-railway-architecture-search.toml'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
           manufacturing_release=False,operating_release=False)
G=9.80665


def load_spec(root=ROOT):
    s=tomllib.loads((Path(root)/SPEC).read_text())
    if s['schema']!='osr-railway-architecture-campaign/1' or s['purpose']!='next-experiment' or s['reference_changes_allowed'] is not False or s['native_dispatch'] is not False:raise ValueError('Explicit non-promoting research campaign required')
    if not 1<=s['maximum_cases']<=600 or not 1<=s['maximum_generations']<=2 or not 1<=s['maximum_runtime_s']<=900:raise ValueError('Bounded campaign required')
    if set(s['families'])!=set(capabilities.catalogue()['families']):raise ValueError('All registered architecture controls required')
    return s


def union(intervals,lower=0.,upper=None):
    """Exact geometric union, used for quantities only, never force scaling."""
    rows=[]
    for a,b in sorted(intervals):
        if not all(isfinite(x) for x in (a,b)) or b<a:raise ValueError('Finite ordered track interval required')
        a=max(lower,a);b=b if upper is None else min(upper,b)
        if b<=a:continue
        if rows and a<=rows[-1][1]+1e-10:rows[-1][1]=max(rows[-1][1],b)
        else:rows.append([a,b])
    return rows


def periodic_installed_windows(commands,spacing,train_length,fin_length,car_length=17.):
    """Expand nose-command windows so every fin is wholly inside motor stock.

    A finite train entering/exiting these intervals still needs the native
    position-dependent force model. No overlap fraction supplies a force.
    """
    offset=(car_length-fin_length)/2
    if spacing<=0 or train_length<=0 or offset<0:raise ValueError('Positive route/train and fitting fin required')
    raw=[[a-train_length+offset,b-offset] for a,b in commands]
    repeated=[[a+k*spacing,b+k*spacing] for a,b in raw for k in (-1,0,1)]
    return union(repeated,0.,spacing)


def _configuration(family,cars,distance,speed,knobs,spec,reference):
    sc=spec['scenario'];rq=spec['requirements'];train_length=cars*sc['car_length_m']+(cars-1)*sc['coupling_gap_m']
    launch=knobs.get('launch_m',0.);commands=[]
    if family in ('P1','P2','P3','P4','P7'):commands=[[0.,launch]]
    if family=='P3':commands.append([distance*.5,distance*.5+knobs['booster_m']])
    if family=='P5':commands=[[i*distance/3,i*distance/3+distance*knobs['fraction']/3] for i in range(3)]
    if family=='P6':commands=[[0.,distance]]
    if family!='P6':installed=periodic_installed_windows(commands+[[distance-sc['receiving_command_m'],distance]],distance,train_length,sc['passive_fin_length_m'])
    else:installed=[]
    powered_axles=knobs.get('powered_axles',0)
    if family=='P6':powered_axles=cars*knobs['powered_axles_per_car']
    drive='wheel-traction' if family=='P6' else 'creep-only' if family=='P4' else 'none'
    physical=dict(schema='osr-railway-architecture-physical/1',
        retained_body_definition_id=reference['body_candidate_id'],retained_support_reference_id=reference['support_component_id'],
        formation=dict(cars=cars,car_length_m=sc['car_length_m'],coupling_gap_m=sc['coupling_gap_m'],train_length_m=train_length,
            seats_per_car=rq['fixed_seats_per_car'],wheelchair_places_per_car=rq['wheelchair_places_per_car']),
        route=dict(directional_ring_length_m=sc['directional_ring_length_m'],station_spacing_m=distance,stations=int(sc['directional_ring_length_m']/distance),
            geometry_scope='Synthetic periodic comparison corridor; no city geography or access equivalence implied'),
        guideway=dict(family='box-beam',span_m=20.,section=civil.section('box-beam'),rail_profile='60E1-reference',site_substructure_defined=False),
        wayside=dict(motor_family='new-passive-secondary-topology' if family=='P7' else 'single-fin-double-sided-LIM' if family!='P6' else 'none',
            reference_motor_definition_id=reference['propulsion_component_id'] if family not in ('P6','P7') else None,
            installed_linear_track_intervals_per_leg_m=installed,
            conductor_supply_track_m=sc['directional_ring_length_m'] if knobs.get('supply')=='conductor-supply' else 0.),
        onboard=dict(drive=drive,driven_axle_count=powered_axles,supply=knobs.get('supply','separate-recovery-store' if family=='P4' else 'auxiliary-only'),
            propulsion_equipment_geometry_id=None if drive!='none' else 'not-applicable',additional_drive_mass_kg=None if drive!='none' else 'not-applicable',
            traction_store_geometry_id=None if knobs.get('supply')=='battery' or family=='P4' else 'not-applicable'),
        component_interface_changes=['new powered bogie and drive mounting' if drive!='none' else 'passive bogie reference retained',
            'new passive secondary and material model' if family=='P7' else 'reference passive secondary retained' if family!='P6' else 'linear secondary omitted; wheel traction interface required'],
        complete_installed_geometry=False)
    candidate_id=identity(physical)
    requirements=dict(base_revision=spec['revision'],mandatory=deepcopy(rq['mandatory']),capacity_pphpd=rq['capacity_pphpd'],
        passengers_per_car=rq['passengers_per_car'],crowd_control_per_car=rq['crowd_control_per_car'],speed_cap_m_s=speed,
        acceleration_m_s2={12.:.25,16.:.3,20.:.4}[speed],service_deceleration_m_s2=rq['independent_service_deceleration_m_s2'],
        dwell_s=rq['dwell_s'],target_headway_s=cars*rq['passengers_per_car']*3600/rq['capacity_pphpd'])
    revision=identity(requirements)
    composition=capabilities.composition(family,candidate_id,revision)
    case=dict(schema='osr-railway-architecture-case/1',candidate_id=candidate_id,physical_definition=physical,
        family_id=family,requirement_revision=revision,requirements=requirements,capability_composition=composition,
        commanded_power_windows_m=commands,knobs=deepcopy(knobs),generation=0,parent_case_ids=[],
        reference_candidate_id=reference['candidate_id'],complete_mass_kg=None,complete_CG_m=None,complete_inertia_kg_m2=None,**FLAGS)
    case['case_id']=identity({n:v for n,v in case.items() if n!='case_id'});return case


def generate(spec,reference):
    rows=[];space=spec['space']
    for family in spec['families']:
        speeds=[20.] if family=='P1' else [12.,16.] if family=='P2' else space['speed_caps_m_s']
        if family in ('P1','P2','P7'):knobs=[dict(launch_m=l) for l in space['station_launch_command_m']]
        elif family=='P3':knobs=[dict(launch_m=l,booster_m=b) for l,b in itertools.product(space['booster_launch_command_m'],space['booster_command_m'])]
        elif family=='P4':knobs=[dict(launch_m=l,powered_axles=a) for l,a in itertools.product(space['station_launch_command_m'],space['recovery_driven_axles_per_train'])]
        elif family=='P5':knobs=[dict(fraction=f) for f in space['distributed_command_fraction']]
        else:knobs=[dict(supply=p,powered_axles_per_car=a) for p,a in itertools.product(space['wheel_traction_supply'],space['wheel_traction_driven_axles_per_car'])]
        for cars,distance,speed,k in itertools.product(space['cars'],space['station_spacing_m'],speeds,knobs):
            rows.append(_configuration(family,cars,distance,speed,k,spec,reference))
    if len(rows)>spec['maximum_cases'] or len({r['case_id'] for r in rows})!=len(rows):raise ValueError('Bounded distinct evaluation cases required')
    return rows


def recovery(case,comparison_mass_per_car,spec,rotating_mass_per_car=0.):
    sc=spec['scenario'];n=case['physical_definition']['formation']['cars'];m=comparison_mass_per_car*n
    F=m*G*(sc['adverse_grade_fraction']+.0025)+(m+rotating_mass_per_car*n)*sc['recovery_acceleration_m_s2']+50*n+1.8*n*sc['recovery_speed_m_s']**2
    axles=case['physical_definition']['onboard']['driven_axle_count'];available=sc['traction_adhesion_hypothesis']*m*G*axles/(4*n)
    self_drive=case['family_id'] in ('P4','P6');energy=F*sc['recovery_distance_m']/sc['drive_efficiency_hypothesis']/3.6e6
    return dict(required_force_N_at_comparison_mass=F,required_mechanical_power_W=F*sc['recovery_speed_m_s'],
        driven_axles=axles,total_axles=4*n,uniform_axle_load_adhesion_bound_N=available if self_drive else None,
        self_recovery_necessary_screen=('pass' if available>=F else 'fail') if self_drive else 'external-recovery-required',
        required_drive_energy_kWh=energy if self_drive else None,
        energy_basis='Conservative constant-peak-force work allowance over the recovery distance; includes acceleration throughout, not a necessary minimum or a sized battery',
        installed_drive_mass_kg=None if self_drive else 'not-applicable',
        actual_recovery_demonstrated=False,
        external_recovery=dict(method='protected rail rescue/tow unit' if not self_drive else 'independent rescue after drive/power fault',
            dispatch_time_s=None,coupling_and_force_capacity_N=None,operator_access_qualified=False,availability_impact=None),
        unknowns=['Measured traction/adhesion and wheel loads','Off-zone braking/holding','Drive and store sizing/installation' if self_drive else 'Rescue equipment, access, response and protected towing','Degraded headway and evacuation'],**FLAGS)


def screen(case,comparison_mass,rotating_mass,spec,*,dt=None):
    from .architecture_demand import demand
    rq=case['requirements'];sc=spec['scenario'];p=case['physical_definition'];n=p['formation']['cars'];D=p['route']['station_spacing_m']
    trajectory=demand(D,comparison_mass,rotating_mass,cars=n,speed_cap_m_s=rq['speed_cap_m_s'],acceleration_m_s2=rq['acceleration_m_s2'],
        deceleration_m_s2=rq['service_deceleration_m_s2'],powered_windows=case['commanded_power_windows_m'],dt=sc['time_step_s'] if dt is None else dt)
    installed=sum(b-a for a,b in p['wayside']['installed_linear_track_intervals_per_leg_m']);stops=p['route']['stations'];headway=rq['target_headway_s']
    clear=(2*p['formation']['train_length_m']/rq['acceleration_m_s2'])**.5
    # Use actual final-brake duration from this demand trajectory. A full-cap
    # estimate could wrongly reject a slower coasting arrival.
    berth=(trajectory['phase_time_s'].get('final-braking',0.)+rq['dwell_s']+clear) if trajectory['reachable'] else None
    cycle=None if not trajectory['reachable'] else stops*(trajectory['runtime_s']+rq['dwell_s'])
    trains=None if cycle is None else ceil(cycle/headway);spares=None if trains is None else ceil(trains*sc['spare_fleet_fraction_hypothesis'])
    normal_demand=trajectory.get('peak_required_force_N_per_car');axles=p['onboard']['driven_axle_count']
    traction_bound=sc['traction_adhesion_hypothesis']*comparison_mass*G*axles/n/4 if case['family_id']=='P6' else None
    rec=recovery(case,comparison_mass,spec,rotating_mass)
    valid=trajectory['execution']=='completed' and trajectory['numerical_validity']=='valid'
    screens=dict(analytical_reach=('pass' if trajectory['reachable'] else 'fail') if valid else 'unknown',
        serial_berth_target='unknown' if berth is None or not valid else 'pass' if berth<=headway else 'fail',
        normal_wheel_traction='unknown' if not valid or traction_bound is None or normal_demand is None else 'pass' if traction_bound>=normal_demand else 'fail',
        self_recovery=rec['self_recovery_necessary_screen'],independent_brakes='unknown',structure='unknown',accessibility='unknown',
        motor_force_map='unknown',installed_equipment='unknown',physical_journey='unknown',whole_life_cost='unknown')
    failures=[name for name,state in screens.items() if state=='fail']
    cycles_per_hour=3600/headway
    # These are required quantities at a reference mass, never complete priced
    # CAPEX or an energy/availability comparison between validated railways.
    coefficients=dict(directional_route_m=sc['directional_ring_length_m'],stations=stops,
        linear_motor_track_m=installed*stops,conductor_track_m=p['wayside']['conductor_supply_track_m'],
        normal_service_trainsets=trains,spare_trainsets=spares,
        purchased_cars=None if trains is None else (trains+spares)*n,
        onboard_drive_units=None if trains is None else (trains+spares)*axles,
        offered_people_per_hour_direction=n*rq['passengers_per_car']*cycles_per_hour,
        platform_train_length_m=p['formation']['train_length_m']+sc['platform_length_margin_m_hypothesis'])
    result=dict(schema='osr-railway-architecture-screen/1',case_id=case['case_id'],candidate_id=case['candidate_id'],requirement_revision=case['requirement_revision'],
        execution='completed',fidelity='analytical-demand-and-necessary-bounds',screens=screens,design_failure_reasons=failures,trajectory=trajectory,
        comparison_mass_kg_per_car=comparison_mass,rotating_reference_mass_kg_per_car=rotating_mass,
        mass_basis='Inherited v0.6 accounted material/reference allocations; new equipment is unweighed. Equal-accounted-mass sensitivity, not complete installed mass or certified lower bound.',
        additional_equipment_mass_kg=None,complete_mass_kg=None,
        actual_protected_headway_s=None,serial_berth_interval_bound_s=berth,required_cycle_s=cycle,
        recovery=rec,quantity_coefficients=coefficients,complete_CAPEX_USD=None,whole_life_cost_USD=None,
        price_coverage='No supplier-installed architecture prices; no unknown-as-zero ranking',
        economic_expression='Shared civil + stations + powered_track_m*installed_motor_rate + conductor_m*installed_supply_rate + purchased_cars*car_rate + onboard_drive_units*drive_rate + stores + construction + energy + maintenance + recovery disruption',
        passenger_access_equivalence='Not established: changing station count changes access and transfer service',
        capability_admission=capabilities.admission_check(case['capability_composition']),
        native_dispatch_eligible=False,physical_journey_completed=False,**FLAGS)
    result['evaluation_id']=identity(result);return result


def next_tasks(case,result):
    reasons=result['design_failure_reasons'];tasks=[]
    if result['trajectory']['execution']!='completed' or result['trajectory']['numerical_validity']!='valid':tasks.append(('numerical-resource-or-model','Resolve the simulation horizon/resource or energy-validity hold before physical ranking or redesign'))
    if 'analytical_reach' in reasons:tasks.append(('architecture-redesign','Change launch/booster positions, speed, spacing or propulsion distribution; retain the failed case'))
    if 'serial_berth_target' in reasons:tasks.append(('station-service-redesign','Compare formation/headway/dwell and berth/route arrangements at equal offered capacity'))
    if 'normal_wheel_traction' in reasons or result['screens']['self_recovery']=='fail':tasks.append(('runninggear-redesign','Increase independently supported driven-axle distribution or revise grade/acceleration; extra torque alone cannot defeat adhesion'))
    tasks.extend([('evaluator-gap','Resolve joint rotational transfer and all-axis body validation'),('evaluator-gap','Establish selected-grade nonlinear moving force/overlap and repeated duty'),
        ('installed-assembly','Count, place, fit and maintain all newly required equipment with complete mass/CG/inertia'),
        ('measurement','Execute M1 component/joint/brake correlation before M2 carriage and M3 protected pilot'),
        ('economics','Obtain common installed price, labour, supply, energy, renewal and recovery availability evidence')])
    return [dict(candidate_id=case['candidate_id'],trigger_evaluation_id=result['evaluation_id'],requirement_revision=case['requirement_revision'],
        failure_class=kind,question=question,maximum_native_jobs=4,runtime_s=600,status='prepared',**FLAGS) for kind,question in tasks]


def source_epoch(reference,root=ROOT):
    root=Path(root);names=[PRODUCER,SPEC,'engineering/design_search/capabilities.py','engineering/design_search/architecture_demand.py',
        'engineering/station_rail/common.py','engineering/station_rail/operations.py','engineering/station_rail/braking.py','engineering/station_rail/civil.py']
    return dict(sorted({**reference['source_sha256'],**{n:digest(root/n) for n in names}}.items()))


def compact_result(result):
    """Preserve raw evaluation identity while indexing the bulky time history."""
    value=deepcopy(result);trace=value['trajectory'].pop('trace')
    value['schema']='osr-railway-architecture-screen-index/1'
    value['raw_evaluation_id']=value.pop('evaluation_id')
    value['trajectory']['schema']='osr-architecture-demand-index/1'
    value['trajectory']['raw_demand_id']=value['trajectory'].pop('demand_id')
    value['trajectory']['trace_archive']=dict(rows=len(trace),sha256=identity(trace),scope='Complete trace retained in the source-bound private case package; regenerate with this exact request')
    value['trajectory']['indexed_demand_id']=identity(value['trajectory']);value['evaluation_id']=identity(value)
    return value


def evaluate_campaign(root=ROOT,*,max_new_cases=None,state=None):
    root=Path(root);spec=load_spec(root);reference=vehicle.build(root);rot=braking.rotating_stock(reference)['equivalent_inertial_mass_kg_per_car']
    mass=reference['mass']['accounted_cap_loaded_kg_per_car'];started=time.monotonic();cases=generate(spec,reference);results=[]
    epoch=source_epoch(reference,root);contract=identity(dict(specification=spec,reference_candidate_id=reference['candidate_id'],sources=epoch))
    folder=Path(state) if state is not None else root/'build/v06-architecture/campaigns'/contract
    folder.mkdir(parents=True,exist_ok=True);journal=dict(schema='osr-architecture-execution-journal/1',contract_id=contract,
        source_sha256=epoch,state='running',completed_case_ids=[],cache_hits=0,new_cases=0,native_jobs_dispatched=0,**FLAGS)
    limit=None if max_new_cases is None else int(max_new_cases)
    if limit is not None and not 1<=limit<=spec['maximum_cases']:raise ValueError('Positive bounded interruption limit required')
    def save():
        journal['journal_id']=identity({n:v for n,v in journal.items() if n!='journal_id'});temporary=folder/'journal.json.tmp';temporary.write_bytes(encoded(journal));temporary.replace(folder/'journal.json')
    def execute(case):
        if source_epoch(reference,root)!=epoch:raise ValueError('Architecture source changed during execution')
        path=folder/(case['case_id']+'.json.gz')
        request=dict(case_id=case['case_id'],candidate_id=case['candidate_id'],requirement_revision=case['requirement_revision'],
            source_sha256=epoch,comparison_mass_kg_per_car=mass,rotating_reference_mass_kg_per_car=rot)
        key=identity(request)
        if path.is_file():
            package=json.loads(gzip.decompress(path.read_bytes()))
            if package['request']!=request or package['cache_key']!=key or package['result']['evaluation_id']!=identity({n:v for n,v in package['result'].items() if n!='evaluation_id'}):raise ValueError('Architecture cache identity differs')
            journal['cache_hits']+=1;result=package['result']
        else:
            if limit is not None and journal['new_cases']>=limit:return None
            result=screen(case,mass,rot,spec);package=dict(request=request,cache_key=key,result=result)
            if source_epoch(reference,root)!=epoch:raise ValueError('Architecture source changed before result sealing')
            temporary=path.with_suffix('.tmp');temporary.write_bytes(gzip.compress(encoded(package),mtime=0));temporary.replace(path);journal['new_cases']+=1
        journal['completed_case_ids'].append(case['case_id']);save();return result
    for case in cases:
        if time.monotonic()-started>spec['maximum_runtime_s']:raise TimeoutError('Architecture campaign time budget; completed source-bound work must be retained')
        result=execute(case)
        if result is None:journal['state']='interrupted';journal['reason']='invocation-case-limit';save();return journal
        results.append(compact_result(result))
    # Failure-driven revisions are separate physical/requirement records. Only
    # failures in valid cheap screens trigger them; unavailable physics creates
    # explicit evaluator/measurement tasks instead of invented passing numbers.
    revisions=[]
    for case,result in zip(cases,results):
        if result['screens']['analytical_reach']=='fail' and case['family_id'] in ('P1','P2') and len(revisions)<12:
            knobs=dict(launch_m=150.,booster_m=200.)
            child=_configuration('P3',case['physical_definition']['formation']['cars'],case['physical_definition']['route']['station_spacing_m'],case['requirements']['speed_cap_m_s'],knobs,spec,reference)
            child['generation']=1;child['parent_case_ids']=[case['case_id']];child['revision_reason']='Add an explicit intermediate powered section after off-zone stall in the demand model'
            child['case_id']=identity({n:v for n,v in child.items() if n!='case_id'});revisions.append(child)
    for child in revisions:
        result=execute(child)
        if result is None:journal['state']='interrupted';journal['reason']='invocation-case-limit';save();return journal
        results.append(compact_result(result));cases.append(child)
    # Challenge the box-beam hypothesis without changing route, train, target
    # service or normal-load comparison. Complete foundation/site costs stay held.
    for family in spec['families']:
        controls=[c for c in cases if c['family_id']==family and c['generation']==0 and c['physical_definition']['formation']['cars']==6 and c['physical_definition']['route']['station_spacing_m']==2000.]
        if not controls:continue
        parent=max(controls,key=lambda c:(c['requirements']['speed_cap_m_s'],c['knobs'].get('launch_m',0.),c['knobs'].get('booster_m',0.)))
        for beam,cap in [('twin-beam','guideway.rail-twin'),('u-beam','guideway.rail-u')]:
            child=deepcopy(parent);child['physical_definition']['guideway'].update(family=beam,section=civil.section(beam));child['candidate_id']=identity(child['physical_definition'])
            child['capability_composition']=capabilities.composition(family,child['candidate_id'],child['requirement_revision'],capabilities={'guideway':cap})
            child.update(generation=1,parent_case_ids=[parent['case_id']],revision_reason='Compare a different complete track-section family under the same service and train context')
            child['case_id']=identity({n:v for n,v in child.items() if n!='case_id'})
            result=execute(child)
            if result is None:journal['state']='interrupted';journal['reason']='invocation-case-limit';save();return journal
            results.append(compact_result(result));cases.append(child)
    if len(cases)>spec['maximum_cases']:raise ValueError('Revision budget exhausted before publication')
    tasks=[t for c,r in zip(cases,results) for t in next_tasks(c,r)]
    journal['state']='completed';save()
    value=dict(schema='osr-whole-railway-architecture-campaign/1',contract_id=contract,source_sha256=epoch,specification=spec,
        reference=dict(candidate_id=reference['candidate_id'],selector_sha256=digest(root/spec['reference_selector']),mass=reference['mass']),
        capability_registry=capabilities.catalogue(),cases=cases,results=results,next_tasks=tasks,
        distinct_physical_candidates=len({c['candidate_id'] for c in cases}),distinct_requirement_contexts=len({c['requirement_revision'] for c in cases}),
        generations=max(c['generation'] for c in cases)+1,executed_native_journeys=0,integrated_selection=dict(status='no-qualified-architecture',selected_candidate_id=None),
        actual_installed_cost_comparison=False,selected_development_default_changed=False,city_performance_packages_written=0,**FLAGS)
    value['campaign_id']=identity(value);return value
