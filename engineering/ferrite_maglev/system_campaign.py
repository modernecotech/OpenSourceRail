"""Integrated executable station/control campaign and independent recovery sizing.

The numerical plant supplies synthetic readiness/occupancy observations. Actual
Rust interlocking retains two consecutive launch bundles; physical I/O is absent.
Equivalent SI motor constants conserve air-gap power, without claiming a measured
three-phase map. Emergency brake and winch quantities are design hypotheses.
"""
from copy import deepcopy
from hashlib import sha256
import gzip
import json
import math
from pathlib import Path
import subprocess
import tomllib

from . import model,station,configuration,moving_train

INPUT=Path(__file__).with_name('system-campaign.toml')
OUTPUT=model.ROOT/'docs/design-engine/ferrite-maglev/system-campaign'
EXAMPLE=model.ROOT/'crates/osr-interlocking/examples/station_campaign.rs'
FILES={'result.json.gz','executed.json.gz','overview.svg','README.md'}
MAX_RAW=64*1024*1024
BASE=1_000_000_000
FAULTS=('receiver','sensor','drive','resistor','stale','phase','uncommitted')
BUILD=['cargo','build','--locked','-p','osr-interlocking','--example','station_campaign','--message-format=json']


def encoded(value):return (json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()


def load():
    a=tomllib.loads(INPUT.read_text())
    if a['schema']!='osr-system-campaign-input/1':raise ValueError('system campaign schema required')
    for key,low,high in [('distance_m',500,1500),('runtime_s',60,120),('step_s',.005,.05),('downstream_overlap_m',25,150),('acceleration_m_s2',.1,1.5),('scheduled_headway_s',120,600)]:
        v=a[key]
        if type(v) not in (int,float) or not math.isfinite(v) or not low<=v<=high:raise ValueError('bounded '+key+' required')
    for group in ('motor','brake','recovery'):
        for key,value in a[group].items():
            values=value if isinstance(value,list) else [value]
            if not values or any(type(v) not in (int,float) or not math.isfinite(v) or not 0<v<1e7 for v in values):
                raise ValueError('finite positive '+group+'/'+key+' required')
    primary=model.load()[1]
    if a['downstream_overlap_m']!=primary['power']['station_resource_downstream_overlap_m']:raise ValueError('campaign resource overlap differs from primary input')
    m=a['motor']
    if not 0<m['modulation_ceiling_fraction']<=1 or m['maximum_voltage_v']>m['dc_bus_v']*m['modulation_ceiling_fraction']/math.sqrt(3):raise ValueError('motor phase voltage exceeds assumed DC modulation bound')
    if m['dc_bus_v']!=model.load()[1]['power']['dc_bus_nominal_study_v']:raise ValueError('campaign DC bus differs from primary input')
    if type(a['brake']['units_per_car']) is not int or not 1<=a['brake']['units_per_car']<=8:raise ValueError('bounded integer brake units required')
    if any(v is not False for v in a['validation'].values()):raise ValueError('physical qualification remains open')
    return a


def emergency_brake(c=None,*,speed_kmh=None,grade=None,mu=.25,units=None,failed_units=0,car_mass_kg=None):
    """Controlled-friction capacity/energy screen, not a stopping demonstration.

    Clamp capacity is force on each pad face; two opposing faces per caliper.
    Pad force is modulated to the target net deceleration. A full spring force
    could give much higher deceleration; fail-safe modulation remains unqualified.
    """
    c=c or model.load()[1];b=load()['brake'];count=c['vehicle']['cars_per_train']
    speed_kmh=b['speed_kmh'] if speed_kmh is None else speed_kmh;grade=b['downgrade'] if grade is None else grade
    units=count*b['units_per_car'] if units is None else units
    if (type(units) is not int or type(failed_units) is not int or not 0<=failed_units<units<=100
            or any(type(x) not in (int,float) or not math.isfinite(x) for x in (speed_kmh,grade,mu))
            or not 0<=speed_kmh<=160 or not -.1<=grade<=.1 or not .01<=mu<=1):raise ValueError('bounded brake case required')
    baseline=model.mass(c,c['mass']['ferrite_base'],c['power']['services_battery_kwh_per_car'])['aw3_kg']
    if car_mass_kg is not None and (type(car_mass_kg) not in (int,float) or not math.isfinite(car_mass_kg) or not 0<car_mass_kg<=100000):
        raise ValueError('bounded positive per-car brake mass required')
    per_car=baseline if car_mass_kg is None else car_mass_kg
    mass=per_car*count
    gravity=9.81*grade/math.sqrt(1+grade*grade)
    v=speed_kmh/3.6;delay=b['response_s'];delay_speed=max(0.,v+gravity*delay)
    delay_distance=max(0.,v*delay+.5*gravity*delay**2)
    decel=b['net_deceleration_m_s2'];force=mass*(decel+gravity)
    stop=delay_speed**2/(2*decel);energy=force*stop
    effective=units-failed_units;capacity=effective*2*b['per_caliper_clamp_capacity_n']*mu
    required_normal=force/mu;per_face=required_normal/(2*effective)
    pressure=per_face/b['pad_area_m2']
    thermal=energy*b['thermal_mass_factor']/(b['heat_capacity_j_kg_k']*b['temperature_rise_k'])
    extra=thermal/count+b['hardware_allowance_kg_per_car'];reserve=c['mass']['growth_reserve']
    passed=capacity>=force and pressure<=b['pad_allowable_pressure_pa'] and extra<=reserve
    return dict(train_mass_kg=mass,car_mass_kg=per_car,
        mass_basis='retained configured battery benchmark' if car_mass_kg is None else 'explicit per-car gross-mass study input; no measured mass acceptance',
        speed_kmh=speed_kmh,downgrade=grade,friction_coefficient_assumption=mu,
        installed_units=units,failed_units=failed_units,available_units=effective,
        target_net_deceleration_m_s2=decel,response_s=delay,braking_force_n=force,
        available_friction_force_n=capacity,force_margin_n=capacity-force,
        required_effective_clamp_force_n=required_normal,
        installed_clamp_force_n=2*units*b['per_caliper_clamp_capacity_n'],
        brake_energy_j=energy,thermal_mass_kg=thermal,stopping_distance_m=delay_distance+stop,
        braking_distance_after_response_m=stop,holding_force_n=max(0.,mass*gravity),
        added_mass_kg_per_car=extra,consumed_growth_reserve_kg_per_car=extra,
        remaining_growth_reserve_kg_per_car=reserve-extra,
        reserve_is_not_additional_verified_mass=True,
        unmodulated_net_deceleration_m_s2=capacity/mass-gravity,modulation_required=True,
        screen_pass=passed,engineering_accepted=False,
        interface_loads=dict(longitudinal_force_n=force,normal_clamp_force_n=required_normal,
            per_unit_clamp_force_n=per_face,pad_area_m2=b['pad_area_m2'],pad_pressure_pa=pressure),
        limitations=['Friction/fade, actuation delay and controlled force are assumed, not tested',
            'Full spring application, empty-train deceleration and jerk require independent control/rig tests',
            'Existing reaction iron is not automatically a qualified brake face; local and global load paths required',
            'Thermal mass is energy capacity only, not a heat-transfer/fade/stress solution',
            'Hardware allowance is not a complete measured component BOM'],**model.FLAGS)


def recovery(c=None):
    c=c or model.load()[1];a=load();r=a['recovery'];brake=emergency_brake(c)
    mass=brake['train_mass_kg'];grade=a['brake']['downgrade'];g=9.81*grade/math.sqrt(1+grade*grade)
    resistance=c['vehicle']['cars_per_train']*station.load()['motion']['resistance_constant_n_per_car']
    pull=(mass*g+resistance)*r['working_pull_factor'];reach=a['distance_m']/2
    duration=reach/r['speed_m_s']+r['deployment_s'];energy=r['critical_services_kw_per_car']*duration/3600
    p=c['power'];usable=p['services_battery_kwh_per_car']*p['eol_capacity_fraction']*(p['normal_soc_high']-p['normal_soc_low'])
    incoming=p['hot_hotel_kw_per_car']*(a['runtime_s']+p['station_dwell_seconds']-p['charger_effective_seconds'])/3600
    return dict(working_line_pull_n=pull,cable_reach_m=reach,winch_input_kw=pull*r['speed_m_s']/r['efficiency']/1000,
        recovery_time_s=duration,essential_load_assumption_kw_per_car=r['critical_services_kw_per_car'],
        essential_services_kwh_per_car=energy,available_after_incoming_leg_kwh_per_car=usable-incoming,
        battery_energy_screen_pass=usable-incoming>=energy,anchor_design_force_n=pull,
        powered_onboard_main_traction=False,scheme='Station or independently powered recovery winch; secured train before cable attachment',
        route_access_accepted=False,curved_cable_path_accepted=False,critical_load_shedding_accepted=False,
        supplier_leads=[dict(name='ACE Winches / Ashtead Technology',
            url='https://www.ashtead-technology.com/lifting-pulling-and-deployment/support-services/',
            basis='OEM design/manufacture capability in Turriff; no selected railway winch or quote'),
            dict(name='Twiflex',url='https://www.twiflex.com/products/disc-braking-systems/spring-applied-calipers/vcs-series',
            basis='Spring-applied industrial brake precedent; catalogue disc caliper is not a selected linear train brake',
            uk_product_manufacture_confirmed=False)],**model.FLAGS)


def deployment(cfg,length,distance):
    """Six-resource same-controller study domain for two consecutive blocks."""
    d=round(distance*1000);ends=[0,d-125000,d+75000,d+150000,2*d-125000,2*d+75000,2*d+150000]
    resources=[dict(id=i,section=100+i,asset_id=f'resource-{i}',kind='platform' if i in (1,4) else 'track',
        controller=900,conflicts=[i],point_asset_id=None,clearance_basis='synthetic independent full-consist virtual detector') for i in range(6)]
    participants=[dict(entity=i,role='Voter',session=1,public_key=[i]*32,revoked=False,resources=[]) for i in (1,2,3)]
    participants.append(dict(entity=101,role='Train',session=1,public_key=[5]*32,revoked=False,resources=[]))
    return dict(schema='osr-tacs-railway/2',revision='two-leg-offline-study',approval_state='prototype-unapproved',
        runtime=dict(voters=[1,2,3],participants=participants,designed_revision='two-leg-offline-study',
            installed_state='not-installed',approved_operating_profile='prototype-unapproved',clock_error_ns=0),
        resources=resources,routes=[dict(id=1,asset_id='two-leg-route',direction='Forward',leader_required=False,
            operating_scope='One local controller, two protected station arrivals; no distributed city authority',
            segments=[dict(resource=i,start_mm=ends[i],end_mm=ends[i+1],speed_limit_mmps=22222,downhill_permille=0) for i in range(6)],
            stopping_locations=[dict(asset_id=f'berth-{i}',at_mm=(i+1)*d,platform=1+3*i,
                charger_asset_id=f'services-charger-{i}',minimum_departure_energy_wh=10000) for i in (0,1)])],
        trains=[dict(asset_id='train-101',config=dict(owner=dict(train=101,session=1),configuration=cfg,length_mm=length,
            minimum_deceleration_mmps2=800,reaction_time_ms=100,stop_margin_mm=1000,maximum_position_uncertainty_mm=10),
            integrity_arrangement='synthetic full-consist numerical position',braking_evidence='unqualified controlled-friction proposal',permitted_route=1)],
        controllers=[dict(id=900,asset_id='local-controller',startup_epoch=1,restart_reconciliation='retain locks and require positive clearance')],
        protected_work_resources=[],maintenance_procedure='controlled offline study')


def frames(a,c,*,fault=None,moving=None):
    import numpy as np
    from .moving_train import trajectory_at
    v=c['vehicle'];count=v['cars_per_train'];mass=model.mass(c,c['mass']['ferrite_base'],c['power']['services_battery_kwh_per_car'])['aw3_kg']
    t=station.trajectory(distance_m=a['distance_m'],runtime_s=a['runtime_s'],car_mass_kg=mass,cars=count,acceleration=a['acceleration_m_s2'])
    if not t['study_pass']:raise ValueError('campaign trajectory infeasible')
    cfg=configuration.selected(c);length=cfg.formation.assumed_overall_length_m
    indexing_um=0
    if moving is not None:
        validate_moving(moving,a,c,t)
        indexing_um=math.ceil(moving['maximum_cumulative_indexing_spread_m']*1e6)
    s=station.load();band=s['vehicle']['magnetic_band_m_per_car'];body=cfg.formation.body_length_m
    pitch=body+cfg.formation.coupling_gap_assumption_m;offset=(body-band)/2
    bands=np.array([[-offset-band-i*pitch,-offset-i*pitch] for i in range(count)])
    motor=a['motor'];pole=s['vehicle']['pole_pitch_m'];density=s['station']['equivalent_envelope_force_n_m']*length/(band*count)
    parameters=dict(zone_start_mm=round(s['station']['winding_start_m']*1000),zone_end_mm=round(s['station']['winding_end_m']*1000),
        train_envelope_mm=round(length*1000),pole_pitch_um=round(pole*1e6),force_density_n_m=density,
        force_constant_n_a=motor['force_constant_n_a'],resistance_ohm=motor['resistance_ohm'],inductance_h=motor['inductance_h'],
        flux_linkage_wb=motor['force_constant_n_a']*(2*pole)/math.tau,maximum_current_a=motor['maximum_current_a'],
        maximum_voltage_v=motor['maximum_voltage_v'],maximum_copper_loss_w=motor['maximum_copper_loss_w'],
        maximum_tick_ns=round(a['step_s']*1e9)+10)
    identity=sha256(encoded([a,cfg.record(),parameters])).digest();config=list(identity)
    dwell=c['power']['station_dwell_seconds'];launch_clearance=length+s['station']['winding_end_m']+a['downstream_overlap_m']
    values=[];was_clear=False
    for index,elapsed in enumerate(np.arange(0.,a['runtime_s']+dwell+40+a['step_s']/2,a['step_s'])):
        outgoing=bool(elapsed>=a['runtime_s']+dwell)
        if elapsed<a['runtime_s']:
            point=trajectory_at(t,float(elapsed));phase=point['phase'];zone=2 if phase=='braking' else 1
            position=point['position_m']-(a['distance_m'] if zone==2 else 0.)
            speed=point['speed_m_s'];force=point['motor_force_n'];mode={'launch':0,'coast':1,'braking':2}[phase]
            if phase=='braking' and force>0:
                if speed>.5 or abs(position)>2:raise ValueError('receiving positive force outside bounded berth')
                mode=4
        elif not outgoing:
            position=0.;speed=0.;force=0.;mode=3;zone=2
        else:
            point=trajectory_at(t,float(elapsed-a['runtime_s']-dwell));position=point['position_m'];speed=point['speed_m_s']
            force=point['motor_force_n'];mode={'launch':0,'coast':1,'braking':2}[point['phase']];zone=2
        # Observation is sampled at its actual timestamp, before current force demand.
        age=motor['observation_age_ns']/1e9
        local_time=max(0.,float(elapsed)-(a['runtime_s']+dwell if outgoing else 0.)-age)
        if elapsed<a['runtime_s'] or outgoing:
            historical=trajectory_at(t,local_time)
            observed_position=historical['position_m']-(a['distance_m'] if zone==2 and not outgoing else 0.)
            observed_speed=historical['speed_m_s']
        else:observed_position=0.;observed_speed=0.
        position_mm=round(observed_position*1000);observed_position=position_mm/1000
        overlap=float(station._overlap(np.array([observed_position]),bands,s['station']['winding_start_m'],s['station']['winding_end_m'])[0])
        clear=bool(outgoing and position-length>s['station']['winding_end_m']+a['downstream_overlap_m'])
        now=BASE+10_000+round(elapsed*1e9)
        frame=dict(now_ns=now,observed_ns=now-motor['observation_age_ns'],sequence=index+1,zone=zone,mode=mode,
            position_mm=position_mm,velocity_mmps=round(observed_speed*1000),overlap_mm=max(0,math.floor(overlap*1000)),force_n=force,
            position_uncertainty_um=motor['position_uncertainty_um']+indexing_um,timestamp_uncertainty_ns=motor['timestamp_uncertainty_ns'],
            receiver_healthy=True,sensors_healthy=True,drive_healthy=True,resistor_ready=True,outgoing=outgoing,full_tail_clear=clear and not was_clear)
        if fault=='uncommitted':frame['full_tail_clear']=False
        trigger=point['phase']=='braking' if elapsed<a['runtime_s'] else False
        if fault in FAULTS[:-1] and trigger:
            if fault=='stale':frame['observed_ns']=now-200_000
            elif fault=='phase':frame['position_uncertainty_um']=10000
            else:frame[{'receiver':'receiver_healthy','sensor':'sensors_healthy','drive':'drive_healthy','resistor':'resistor_ready'}[fault]]=False
        values.append(frame);was_clear=clear
        if fault=='uncommitted' or (fault in FAULTS[:-1] and trigger):break
        if clear:break
    return dict(model=deployment(config,parameters['train_envelope_mm'],a['distance_m']),configuration=config,motor=parameters,
        frames=values,initial_commit=fault!='uncommitted'),t,launch_clearance


def sources():
    paths={Path(__file__),INPUT,EXAMPLE,model.INPUT,station.INPUT,configuration.INPUT,
        model.ROOT/'Cargo.toml',model.ROOT/'Cargo.lock',model.ROOT/'engineering/analysis/tests/test_ferrite_maglev_system_campaign.py'}
    for package in ('osr-core','osr-interlocking','osr-maglev-control'):
        base=model.ROOT/'crates'/package;paths.add(base/'Cargo.toml');paths.update(base.rglob('*.rs'))
    for name in ('model.py','station.py','configuration.py','moving_train.py','moving-train.toml','coupled.py'):
        paths.add(Path(__file__).with_name(name))
    return {p.relative_to(model.ROOT).as_posix():digest(p) for p in sorted(paths) if p.is_file()}


def _run(command,input_text=None):
    r=subprocess.run(command,cwd=model.ROOT,input=input_text,capture_output=True,text=True,timeout=180)
    if r.returncode:raise ValueError('campaign execution failed: '+r.stderr[-2000:])
    return dict(command=command,returncode=r.returncode,stdin=input_text,stdout=r.stdout,stderr=r.stderr)


def validate_replay(value,request,case):
    if case not in ('nominal',*FAULTS):raise ValueError('declared campaign case required')
    required={'schema','observations','incoming_cleared','outgoing_committed','fault_held','configuration','physical_output_authorised','detector_evidence'}
    if (set(value)!=required or value.get('schema')!='osr-integrated-station-replay/1'
            or value.get('detector_evidence')!='synthetic full-consist numerical position, not authenticated physical observations'
            or value.get('fault_held') is not (case not in ('nominal','uncommitted'))
            or value.get('outgoing_committed') is not (case=='nominal')):
        raise ValueError('retained campaign metadata or fault outcome differs')
    records=value.get('observations',[])
    if len(records)!=len(request['frames']) or not records:raise ValueError('complete actual control frames required')
    if value.get('configuration')!=request['configuration'] or value.get('physical_output_authorised') is not False:raise ValueError('campaign identity or authority differs')
    previous={}
    for index,(observed,sent) in enumerate(zip(records,request['frames'])):
        if observed['sequence']!=sent['sequence'] or observed['now_ns']!=sent['now_ns']:raise ValueError('control frame identity differs')
        if observed.get('physical_output_authorised') is not False or observed.get('support_shutdown_requested') is not False:raise ValueError('offline support/authority invariant violated')
        if abs(observed['airgap_electrical_power_w']-observed['mechanical_power_w'])>max(1e-5,abs(observed['mechanical_power_w'])*1e-10):raise ValueError('air-gap power does not close')
        if sent['mode'] in (1,3) and observed['force_n']!=0:raise ValueError('coast or secured state supplies thrust')
        should_pass=case=='nominal' or index<len(records)-1
        if observed.get('feasible') is not should_pass or observed.get('mode')!=sent['mode']:raise ValueError('frame outcome/mode differs')
        expected_fault='None' if should_pass else 'Some('+{
            'receiver':'Receiver','sensor':'Sensors','drive':'Receiver','resistor':'Receiver',
            'stale':'StalePhase','phase':'StalePhase','uncommitted':'Authority'}[case]+')'
        if (observed.get('fault')!=expected_fault
                or observed.get('recovery_required') is not (not should_pass and case!='uncommitted')):
            raise ValueError('retained fault latch or recovery outcome differs')
        expected_force=sent['force_n'] if should_pass and sent['mode'] not in (1,3) else 0.
        motor=request['motor'];current=expected_force/motor['force_constant_n_a']
        old_now,old_current=previous.get(sent['zone'],(None,0.))
        dt=(motor['maximum_tick_ns'] if old_now is None else sent['now_ns']-old_now)*1e-9
        voltage=0. if not should_pass or sent['mode'] in (1,3) else abs(motor['resistance_ohm']*current)+motor['inductance_h']*abs((current-old_current)/dt)+abs(motor['flux_linkage_wb']*math.tau*(sent['velocity_mmps']/1000)/(2*motor['pole_pitch_um']*1e-6))
        calculated=dict(force_n=expected_force,current_a=current,voltage_bound_v=voltage,copper_loss_w=current*current*motor['resistance_ohm'],mechanical_power_w=expected_force*sent['velocity_mmps']/1000,airgap_electrical_power_w=expected_force*sent['velocity_mmps']/1000)
        if any(not math.isclose(observed[k],v,rel_tol=1e-10,abs_tol=1e-6) for k,v in calculated.items()):raise ValueError('retained controller electrical/force output differs from independent equations')
        if (observed.get('incoming_protected') is not (case!='uncommitted' and not sent['full_tail_clear'])
                or observed.get('outgoing_protected') is not sent['outgoing']
                or observed.get('incoming_cleared') is not sent['full_tail_clear']):raise ValueError('retained ownership outcome differs')
        previous[sent['zone']]=(sent['now_ns'],current)

    if case=='nominal':
        if not all(r['feasible'] for r in records) or not value['incoming_cleared'] or not value['outgoing_committed']:raise ValueError('two-leg nominal control failed')
        if not records[-1]['outgoing_protected'] or records[-1]['incoming_protected']:raise ValueError('consecutive block ownership differs')
        for r,f in zip(records,request['frames']):
            if not f['full_tail_clear'] and not r['incoming_protected']:raise ValueError('incoming bundle released before full tail')
    else:
        last=records[-1]
        if last['feasible'] or value['incoming_cleared']:raise ValueError('fault cannot launch or clear')
        if case!='uncommitted' and (not last['incoming_protected'] or not value['fault_held'] or not last['recovery_required']):raise ValueError('fault lost committed protection')
    return dict(case=case,frames=len(records),passed=True,peak_current_a=max(abs(r['current_a']) for r in records),
        peak_voltage_v=max(r['voltage_bound_v'] for r in records),incoming_cleared=value['incoming_cleared'],
        physical_output_authorised=False)


def validate_moving(moving,a,c,t):
    cfg=configuration.selected(c);cv=cfg.civil
    section=dict(width=cv.width_m,depth=cv.depth_m,web=cv.web_m,flange=cv.flange_m)
    if (moving.get('schema')!='osr-selected-moving-twin/1' or moving.get('study_pass') is not True or moving.get('configuration_revision')!=cfg.revision
            or moving.get('profile')!=t['inputs'] or moving.get('beam_section_m')!=section
            or moving.get('guideway_span_m')!=cv.span_m
            or moving.get('beam_modulus_pa')!=c['civil']['narrow_box_screen']['gross_uncracked_concrete_e_pa']
            or moving.get('coupler_stiffness_n_m')!=c['vehicle']['coupler_stiffness_assumption_n_m']
            or moving.get('formation',{}).get('cars')!=cfg.formation.cars):
        raise ValueError('moving evidence does not match exact campaign configuration/profile')
    spread=moving.get('maximum_cumulative_indexing_spread_m')
    if type(spread) not in (int,float) or not math.isfinite(spread) or not 0<=spread<.01:
        raise ValueError('bounded retained cumulative indexing uncertainty required')
    confirmations=moving.get('mandatory_confirmation_candidate_sha256',[])
    valid_hash=lambda v:isinstance(v,str) and len(v)==64 and all(x in '0123456789abcdef' for x in v)
    if len(confirmations)!=3 or len(set(confirmations))!=3 or not all(valid_hash(v) for v in [moving.get('candidate_sha256'),*confirmations]):raise ValueError('three exact mandatory moving confirmations required')
    if any(moving.get(k) is not False for k in model.FLAGS) or moving.get('shared_field_phase_registration_accepted') is not False:raise ValueError('moving evidence exceeds numerical authority')
    phase=spread*360/(2*station.load()['vehicle']['pole_pitch_m'])
    if not math.isclose(moving.get('maximum_magnetic_phase_spread_degrees',-1),phase,rel_tol=1e-8,abs_tol=1e-8):raise ValueError('moving indexing and magnetic phase budgets differ')
    return True


def _binary(build):
    if build.get('command')!=BUILD or build.get('returncode')!=0:raise ValueError('successful exact compiler command required')
    artifacts=[j['executable'] for line in build['stdout'].splitlines() for j in [json.loads(line)]
        if j.get('reason')=='compiler-artifact' and j.get('target',{}).get('name')=='station_campaign' and j.get('executable')]
    if len(artifacts)!=1:raise ValueError('actual campaign binary required')
    return Path(artifacts[0])


def _result(a,c,before,binary_hash,cases,t,clearance,executions,moving):
    brakes=[emergency_brake(c,mu=mu,failed_units=failed) for mu in a['brake']['friction_cases'] for failed in (0,1)]
    headway=dict(scheduled_s=a['scheduled_headway_s'],planning_minimum_s=(json.loads(executions['nominal']['stdout'])['observations'][-1]['now_ns']-BASE-10000)/1e9+station.load()['station']['release_allowance_s'],timer_is_clearance_proof=False)
    headway['screen_pass']=headway['scheduled_s']>=headway['planning_minimum_s']
    recovered=recovery(c);charging=station.evaluate(c)['charging']
    return dict(schema='osr-integrated-system-campaign/1',configuration_revision=configuration.selected(c).revision,
        source_sha256=before,binary_sha256=binary_hash,cases=cases,station_trajectory=t,
        selected_moving_evidence=moving,phase_position_uncertainty_um=a['motor']['position_uncertainty_um']+math.ceil(moving['maximum_cumulative_indexing_spread_m']*1e6),
        full_bundle_tail_clearance_front_distance_m=clearance,resource_headway=headway,
        emergency_brake_cases=brakes,recovery=recovered,charging=charging,
        numerical_study_pass=all(r['passed'] for r in cases) and all(r['screen_pass'] for r in brakes) and headway['screen_pass'] and recovered['battery_energy_screen_pass'] and charging['input_rating_screen_pass'],
        detector_basis='Virtual full-consist positions, supplied readiness and one local controller; no sensor/authentication qualification',
        measured_motor_map=False,cross_controller_handover_implemented=False,**model.FLAGS)


def study():
    before=sources();a=load();c=model.load()[1];moving=moving_train.read_selected();build=_run(BUILD)
    binary=_binary(build);executions={'build':build};cases=[]
    for case in ('nominal',*FAULTS):
        request,t,clearance=frames(a,c,fault=None if case=='nominal' else case,moving=moving)
        run=_run([str(binary)],encoded(request).decode());observed=json.loads(run['stdout'])
        cases.append(validate_replay(observed,request,case));executions[case]=run
    result=_result(a,c,before,digest(binary),cases,t,clearance,executions,moving)
    if sources()!=before:raise ValueError('campaign source changed during execution')
    return result,executions


def publish(output=OUTPUT):
    result,execution=study();output=Path(output);output.mkdir(parents=True,exist_ok=True)
    readme='\n'.join(['# Integrated station, interlocking and recovery study','',
        '[Results](result.json.gz) · [Actual command/input/output records](executed.json.gz) · [Receipts](manifest.json)','',
        'Actual Rust resource ownership is bound to station control over an incoming six-car run, dwell, and a committed next departure. Full-tail evidence releases the old bundle only after the complete virtual consist clears its downstream overlap. Receiver, sensor, drive, resistor, stale observation and uncommitted departure counterexamples retain their failure scope. No physical command is enabled.','',
        'Equivalent SI motor constants enforce air-gap power conservation. Current, voltage and copper-loss limits remain scalar hypotheses rather than measured three-phase performance. The brake proposal includes delay, downgrade, friction, one failed unit, heat-energy capacity, clamp loads and explicit growth-reserve consumption. The independent winch proposal exposes energy, pull, anchorage, cable reach and unresolved access.','',
        'Historical [FTA emergency-preparedness guidance](https://www.transit.dot.gov/regulations-and-guidance/safety/recommended-emergency-preparedness-guidelines-rail-transit-systems) motivates independent braking and recovery; it is not a current Iraqi approval basis. [Twiflex industrial spring-applied brakes](https://www.twiflex.com/products/disc-braking-systems/spring-applied-calipers/vcs-series) and [ACE/Ashtead OEM capability](https://www.ashtead-technology.com/lifting-pulling-and-deployment/support-services/) are leads, with no selected railway-rated product or quote.','',
        '**Open:** measured friction/fade/heat transfer, passive capture and restraint, safe force modulation across loads, guideway local/global reactions, essential power, winch access and anchors, distributed authority, authenticated sensors, MCU timing and full physical acceptance.',''])
    rows=''.join(f'<text x="30" y="{110+i*42}">{r["case"]}: {r["frames"]} actual Rust frames; expected outcome verified</text>' for i,r in enumerate(result['cases']))
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="460"><rect width="1000" height="460" fill="#f1f5f9"/><g font-family="sans-serif" fill="#17394c"><text x="30" y="42" font-size="23">Interlocking → station control → full-tail clearance</text><text x="30" y="72">Equivalent SI power balance, synthetic numerical plant; physical authority disabled</text>{rows}</g></svg>'
    payload={'result.json.gz':gzip.compress(encoded(result),mtime=0),'executed.json.gz':gzip.compress(encoded(execution),mtime=0),'overview.svg':svg.encode(),'README.md':readme.encode()}
    if {p.name for p in output.iterdir()}-FILES-{'manifest.json'}:raise ValueError('unexpected campaign output')
    for name,data in payload.items():(output/name).write_bytes(data)
    manifest=dict(schema='osr-system-campaign-publication/1',source_sha256=result['source_sha256'],
        files_sha256={name:sha256(data).hexdigest() for name,data in payload.items()},**model.FLAGS)
    (output/'manifest.json').write_bytes(encoded(manifest));return verify(output)


def _compressed(path):
    with gzip.open(path,'rb') as stream:raw=stream.read(MAX_RAW+1)
    if len(raw)>MAX_RAW:raise ValueError('campaign decompression bound exceeded')
    return json.loads(raw)


def verify(output=OUTPUT):
    output=Path(output)
    if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()}!=FILES|{'manifest.json'}:raise ValueError('exact campaign packet required')
    if (output/'manifest.json').is_symlink():raise ValueError('ordinary campaign manifest required')
    manifest=json.loads((output/'manifest.json').read_text())
    if manifest.get('schema')!='osr-system-campaign-publication/1':raise ValueError('campaign publication schema differs')
    if manifest.get('source_sha256')!=sources():raise ValueError('campaign sources changed')
    if set(manifest.get('files_sha256',{}))!=FILES:raise ValueError('campaign file receipts incomplete')
    for name,expected in manifest['files_sha256'].items():
        if (output/name).is_symlink() or (output/name).stat().st_size>8*1024*1024 or digest(output/name)!=expected:raise ValueError('campaign payload differs')
    result=_compressed(output/'result.json.gz');execution=_compressed(output/'executed.json.gz')
    if set(execution)!={'build','nominal',*FAULTS}:raise ValueError('actual campaign executions incomplete')
    binary=_binary(execution['build'])
    binary_hash=result.get('binary_sha256')
    if not isinstance(binary_hash,str) or len(binary_hash)!=64 or any(c not in '0123456789abcdef' for c in binary_hash):raise ValueError('binary identity required')
    # Portable receipts retain compiler identity and digest; installed binary may be absent.
    if binary.is_file() and digest(binary)!=binary_hash:raise ValueError('installed campaign binary differs')
    a=load();c=model.load()[1];moving=moving_train.read_selected();expected=[]
    for case in ('nominal',*FAULTS):
        request,t,clearance=frames(a,c,fault=None if case=='nominal' else case,moving=moving);run=execution[case]
        if run.get('returncode')!=0 or run.get('command')!=[str(binary)] or run.get('stdin')!=encoded(request).decode():raise ValueError('executed campaign plant inputs differ')
        expected.append(validate_replay(json.loads(run['stdout']),request,case))
    if encoded(result)!=encoded(_result(a,c,manifest['source_sha256'],binary_hash,expected,t,clearance,execution,moving)):raise ValueError('campaign result differs from retained execution and independent sizing')
    if any(row.get(k) is not False for row in (result,manifest) for k in model.FLAGS):raise ValueError('campaign has no physical release authority')
    return manifest


def read_summary(output=OUTPUT):
    verify(output);value=_compressed(Path(output)/'result.json.gz')
    return dict(packet_path=Path(output).relative_to(model.ROOT).as_posix(),manifest_sha256=digest(Path(output)/'manifest.json'),
        numerical_study_pass=value['numerical_study_pass'],cases=value['cases'],resource_headway=value['resource_headway'],
        emergency_brake_cases=value['emergency_brake_cases'],recovery=value['recovery'],charging=value['charging'],
        phase_position_uncertainty_um=value['phase_position_uncertainty_um'],cross_controller_handover_implemented=False,**model.FLAGS)
