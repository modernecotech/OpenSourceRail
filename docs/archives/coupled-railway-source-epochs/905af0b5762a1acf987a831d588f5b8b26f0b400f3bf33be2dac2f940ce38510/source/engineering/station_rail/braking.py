"""Wheel rotational inertia and independent disc-brake research model, SI.

The rolling constraint and ideal instantaneous adhesion-limiter are reduced-model
hypotheses, not WSP qualification. No supplier friction/fade curve is available.
Wayside LIM body force is independent of wheel adhesion; rolling contact force
and brake torque must be evaluated separately.
"""
from math import isfinite,pi,sqrt,exp
from pathlib import Path
import json,subprocess
from . import ROOT,FLAGS
from .common import encoded,identity,digest,source_map
G=9.80665
IDS=('candidate_id','body_candidate_id','support_component_id','propulsion_component_id')
PRODUCERS=('engineering/station_rail/braking.py','engineering/trip_dynamics/chrono_runner.py','engineering/trip_dynamics/formation.py')

def positive(value,name,zero=False):
    if type(value) not in (int,float) or not isfinite(value) or (value<0 if zero else value<=0):raise ValueError('Finite '+('nonnegative ' if zero else 'positive ')+name+' required')
    return float(value)

def rotating_stock(vehicle):
    rows=[]
    for p in vehicle['geometry_parts']:
        name=p['id']
        if name.startswith('bogie/') and any(t in name for t in ('/wheel/','/axle/','/brake/')) and p['kind'] in ('cylinder','annular-cylinder'):
            if p['axis']!=[0,1,0]:raise ValueError('Wheel rotor must use declared transverse axis')
            inertia=.5*p['mass_kg']*(p['radius_m']**2+p.get('inner_radius_m',0.)**2)
            rows.append(dict(part_id=name,mass_kg=p['mass_kg'],I_axial_kg_m2=inertia))
    if not rows:raise ValueError('Actual rotating stock required')
    radius=vehicle['physical_definition']['support']['wheel_new_diameter_m']/2
    I=sum(r['I_axial_kg_m2'] for r in rows)
    return dict(schema='osr-counted-wheel-inertia/1',radius_m=radius,parts=rows,I_kg_m2_per_car=I,
        equivalent_inertial_mass_kg_per_car=I/radius**2,
        counted_rotating_mass_kg_per_car=sum(r['mass_kg'] for r in rows),
        static_axle_load_uses_equivalent_inertial_mass=False,
        scope='Counted wheel, axle and disc material; bearings, seals and unlocated drive-free hardware rotation unresolved')

def definition(vehicle):
    rotor=rotating_stock(vehicle)
    discs=[p for p in vehicle['geometry_parts'] if '/brake/' in p['id'] and p['id'].endswith('/disc')]
    if len(discs)!=8:raise ValueError('Explicit eight counted discs required')
    r_out=.30;r_pad_inner=.15
    effective=2/3*(r_out**3-r_pad_inner**3)/(r_out**2-r_pad_inner**2)
    value=dict(schema='osr-wheel-brake-research-definition/1',**{k:vehicle[k] for k in IDS},
        rotors=rotor,discs_per_car=len(discs),counted_disc_stock_kg_per_car=sum(p['mass_kg'] for p in discs),
        pad_outer_radius_m=r_out,pad_inner_radius_m=r_pad_inner,effective_friction_radius_m=effective,
        opposed_pistons_per_caliper_hypothesis=2,piston_diameter_m_hypothesis=.10,
        maximum_pressure_Pa_hypothesis=.6e6,pad_friction_coefficient_hypothesis=.35,
        pressure_response_delay_s_hypothesis=1.,pressure_rise_time_s_hypothesis=.4,
        steel_specific_heat_J_kg_K_hypothesis=500.,ambient_C_hypothesis=50.,
        public_supplier_comparison=dict(url='https://rail.knorr-bremse.com/media/2000_products/2900d_product_broschures/p-1236_hydroact.pdf',
            reference='HydroAct reference actuator families; not the specified pneumatic actuator, brake-force definition and system compatibility require supplier confirmation',
            selected=False,supplier_friction_or_fade_curve=None),
        WSP='Ideal instantaneous rolling-adhesion torque limiter; real slip, valve cycling and latency not established',
        installed_hardware_qualified=False,brake_safety_floor_m_s2=None,**FLAGS)
    value['brake_definition_id']=identity(value);return value

def force_state(spec,mass_kg,speed_m_s,time_s,*,grade_down_fraction=0.,rail_adhesion=.05,
                pressure_Pa=None,pad_mu=None,available_discs=8,wayside_force_N=0.,ideal_WSP=True):
    m=positive(mass_kg,'mass');speed=positive(speed_m_s,'speed',True);positive(time_s,'time',True)
    if type(available_discs) is not int or not 0<=available_discs<=8:raise ValueError('Zero to eight functioning discs required')
    if not isfinite(grade_down_fraction) or abs(grade_down_fraction)>.1:raise ValueError('Grade outside reference domain')
    mu=positive(rail_adhesion,'adhesion',True);pad=positive(spec['pad_friction_coefficient_hypothesis'] if pad_mu is None else pad_mu,'pad friction',True)
    pressure=positive(spec['maximum_pressure_Pa_hypothesis'] if pressure_Pa is None else pressure_Pa,'pressure',True)
    if not isfinite(wayside_force_N):raise ValueError('Finite wayside force required')
    radius=spec['rotors']['radius_m'];rot=spec['rotors']['equivalent_inertial_mass_kg_per_car'];dynamic=m+rot
    rise=0. if time_s<=spec['pressure_response_delay_s_hypothesis'] else 1-exp(-(time_s-spec['pressure_response_delay_s_hypothesis'])/spec['pressure_rise_time_s_hypothesis'])
    pad_normal=spec['opposed_pistons_per_caliper_hypothesis']*pressure*pi*spec['piston_diameter_m_hypothesis']**2/4*rise
    torque=available_discs*pad*pad_normal*spec['effective_friction_radius_m']
    command=torque/radius
    grade_force=m*G*grade_down_fraction/sqrt(1+grade_down_fraction**2)
    a=(wayside_force_N+grade_force-command)/dynamic
    contact=-rot*a-command
    normal=m*G/sqrt(1+grade_down_fraction**2);limit=mu*normal
    outside=abs(contact)>limit+1e-8
    applied=command
    if outside and ideal_WSP:
        # Keep the axle rolling by reducing mechanical brake torque only. An
        # excessive LIM-induced contact requirement cannot be corrected by WSP.
        capped_contact=-limit if contact<0 else limit
        target_a=(wayside_force_N+grade_force+capped_contact)/m
        required_Q=-capped_contact-rot*target_a
        if not 0<=required_Q<=command+1e-8:
            return dict(valid=False,reason='rolling_contact_outside_domain_without_brake_only_remedy',wayside_force_N=wayside_force_N)
        applied=max(0.,required_Q);a=target_a;contact=capped_contact
    elif outside:
        return dict(valid=False,reason='wheel_slide_outside_pure_rolling_domain',wayside_force_N=wayside_force_N)
    return dict(valid=True,acceleration_m_s2=a,pressure_fraction=rise,
        commanded_brake_torque_Nm_per_car=torque,applied_brake_torque_Nm_per_car=applied*radius,
        torque_equivalent_brake_force_N_per_car=applied,rail_contact_force_N_per_car=contact,
        normal_load_N_per_car=normal,rail_contact_limit_N_per_car=limit,
        adhesion_limiter_active=outside,wayside_force_N=wayside_force_N,
        downhill_gravity_N_per_car=grade_force,disc_heat_rate_W_per_car=applied*speed,
        pure_rolling_constraint=True,actual_WSP_qualified=False)

def native_run(output,vehicle,*,dt_s=.01,root=ROOT):
    """Actual Chrono force-driven six-car braking, with analytically reduced rotors."""
    from engineering.trip_dynamics.chrono_runner import new_system,solver_info
    from engineering.trip_dynamics import formation
    output=Path(output);root=Path(root)
    if output.exists():raise ValueError('Fresh immutable braking run directory required')
    positive(dt_s,'timestep')
    if not .001<=dt_s<=.02:raise ValueError('Bounded timestep required')
    output.mkdir(parents=True);before=source_map(root,PRODUCERS);spec=definition(vehicle)
    (output/'inputs.json').write_bytes(encoded(dict(vehicle_mass=vehicle['mass'],spec=spec,dt_s=dt_s)))
    cases=[]
    for load in ('empty','normal','crowd_control'):
        key={'empty':'accounted_tare_kg_per_car','normal':'accounted_cap_loaded_kg_per_car','crowd_control':'accounted_160_control_kg_per_car'}[load]
        m=vehicle['mass'][key];rot=spec['rotors']['equivalent_inertial_mass_kg_per_car'];eff=m+rot
        for name,mu,grade,discs in [('dry',.15,0.,8),('wet-downhill',.05,.02,8),('one-channel-lost',.05,.02,4),('insufficient-adhesion',.03,.04,8)]:
            c,system=new_system();system.SetGravitationalAcceleration(c.ChVector3d(0,0,0))
            model=formation.build(system,c,[eff]*6);bodies=model['bodies'];starts=model['initial_positions_m']
            for body in bodies:body.SetPosDt(c.ChVector3d(20.,0,0))
            initial=6*.5*eff*20**2;heat=gravity_work=path_trapezoidal=0.;trace=[];next_sample=0.;peaktemp=50.;limited=0;state='running';reason=None
            while system.GetChTime()<400:
                t=system.GetChTime();speed=float(bodies[0].GetPosDt().x)
                f=force_state(spec,m,speed,t+dt_s/2,rail_adhesion=mu,grade_down_fraction=grade,available_discs=discs)
                if not f['valid']:state='outside-model-domain';reason=f['reason'];break
                # Every car is identically loaded; longitudinal couplers retain
                # physical links but do not create an invented braking floor.
                old=[float(b.GetPos().x) for b in bodies];old_speed=[float(b.GetPosDt().x) for b in bodies];h=dt_s
                if f['acceleration_m_s2']<0:h=min(h,speed/-f['acceleration_m_s2'])
                if h<1e-9:state='stopped';break
                for body,index in zip(bodies,model['accumulators']):
                    body.EmptyAccumulator(index);body.AccumulateForce(index,c.ChVector3d(f['downhill_gravity_N_per_car']-f['torque_equivalent_brake_force_N_per_car'],0,0),body.GetPos(),False)
                system.Update();system.DoStepDynamics(h)
                moved=sum(.5*(float(b.GetPosDt().x)+v)*h for b,v in zip(bodies,old_speed))
                path_trapezoidal+=moved/6
                heat+=f['torque_equivalent_brake_force_N_per_car']*moved
                gravity_work+=f['downhill_gravity_N_per_car']*moved
                delta=heat/6/(spec['counted_disc_stock_kg_per_car']*discs/8*spec['steel_specific_heat_J_kg_K_hypothesis'])
                peaktemp=max(peaktemp,50.+delta)
                limited+=f['adhesion_limiter_active']
                if t>=next_sample:
                    trace.append(dict(time_s=system.GetChTime(),force_evaluation_time_s=t+dt_s/2,front_translation_m=float(bodies[0].GetPos().x)-starts[0],speed_m_s=float(bodies[0].GetPosDt().x),
                        wheel_speed_rad_s=float(bodies[0].GetPosDt().x)/spec['rotors']['radius_m'],force=f,
                        total_disc_heat_J=heat,lumped_disc_temperature_C=50.+delta))
                    next_sample+=.25
                if float(bodies[0].GetPosDt().x)<=1e-7:state='stopped';break
                if t>5 and f['acceleration_m_s2']>=0:state='cannot-stop';reason='downhill_gravity_exceeds_adhesion_or_available_brake_torque';break
            if state=='running':state='interrupted';reason='400s simulation budget'
            kinetic=sum(.5*eff*float(b.GetPosDt().x)**2 for b in bodies)
            row=dict(case=name,load=load,state=state,failure_reason=reason,grade_down_fraction=grade,adhesion_hypothesis=mu,working_discs_per_car=discs,
                stop_distance_m=float(bodies[0].GetPos().x)-starts[0] if state=='stopped' else None,
                elapsed_s=system.GetChTime(),final_speed_m_s=float(bodies[0].GetPosDt().x),dt_s=dt_s,
                physical_translational_mass_kg_per_car=m,effective_inertial_mass_kg_per_car=eff,
                initial_translational_plus_rotational_energy_J=initial,total_disc_heat_J=heat,gravity_work_J=gravity_work,
                final_kinetic_energy_J=kinetic,energy_residual_J=initial+gravity_work-heat-kinetic,
                lumped_disc_temperature_C_hypothesis=peaktemp,active_disc_heat_capacity_J_K_per_car=spec['counted_disc_stock_kg_per_car']*discs/8*spec['steel_specific_heat_J_kg_K_hypothesis'],
                integrated_path_from_velocity_m=path_trapezoidal,native_position_minus_trapezoidal_path_m=float(bodies[0].GetPos().x)-starts[0]-path_trapezoidal,
                work_quadrature='Trapezoidal Chrono velocity work; Euler native position error recorded separately',
                adhesion_limited_steps=limited,trace=trace,
                station_propulsion_credited=False,qualified_braking_floor=False)
            cases.append(row)
    if before!=source_map(root,PRODUCERS):raise ValueError('Braking producer changed during execution')
    result=dict(schema='osr-native-wheel-braking/1',**{k:vehicle[k] for k in IDS},execution='completed',backend=solver_info(),specification=spec,
        cases=cases,scope='Force-driven Chrono reduced pure-rolling longitudinal six-car braking. Actual lateral/contact slip/WSP/flexible body not simulated; hardware parameters are hypotheses.',
        complete_station_to_station_journey=False,source_sha256=before,**FLAGS)
    (output/'result.json').write_bytes(encoded(result));m=dict(source_sha256=before,files_sha256={p.name:digest(p) for p in output.iterdir() if p.is_file()},**FLAGS);m['manifest_id']=identity(m)
    (output/'manifest.json').write_bytes(encoded(m));return result

def verify(output,vehicle,root=ROOT):
    p=Path(output);m=json.loads((p/'manifest.json').read_bytes());r=json.loads((p/'result.json').read_bytes())
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('Brake package identity differs')
    if m['source_sha256']!=source_map(root,PRODUCERS):raise ValueError('Brake source differs')
    if {x.name:digest(x) for x in p.iterdir() if x.is_file() and x.name!='manifest.json'}!=m['files_sha256']:raise ValueError('Brake payload differs')
    if any(r[k]!=vehicle[k] for k in IDS) or r['specification']!=definition(vehicle):raise ValueError('Brake candidate differs')
    if len(r['cases'])!=12 or any(r.get(k) is not v for k,v in FLAGS.items()):raise ValueError('Brake case inventory/disposition differs')
    def finite_tree(value):
        if isinstance(value,float) and not isfinite(value):raise ValueError('Nonfinite brake evidence')
        if isinstance(value,dict):
            for x in value.values():finite_tree(x)
        elif isinstance(value,list):
            for x in value:finite_tree(x)
    finite_tree(r)
    expected={(load,name) for load in ('empty','normal','crowd_control') for name in ('dry','wet-downhill','one-channel-lost','insufficient-adhesion')}
    if {(c['load'],c['case']) for c in r['cases']}!=expected:raise ValueError('Brake scenario inventory differs')
    for case in r['cases']:
        key={'empty':'accounted_tare_kg_per_car','normal':'accounted_cap_loaded_kg_per_car','crowd_control':'accounted_160_control_kg_per_car'}[case['load']]
        physical=vehicle['mass'][key];eff=physical+r['specification']['rotors']['equivalent_inertial_mass_kg_per_car']
        if case['physical_translational_mass_kg_per_car']!=physical or case['effective_inertial_mass_kg_per_car']!=eff:raise ValueError('Brake mass differs')
        initial=6*.5*eff*20**2
        if abs(case['initial_translational_plus_rotational_energy_J']-initial)>1e-6:raise ValueError('Brake initial energy differs')
        recomputed=initial+case['gravity_work_J']-case['total_disc_heat_J']-case['final_kinetic_energy_J']
        if abs(recomputed-case['energy_residual_J'])>1e-6:raise ValueError('Brake energy evidence differs')
        if case['state']=='stopped' and (abs(case['final_speed_m_s'])>1e-6 or not case['stop_distance_m']>0):raise ValueError('Brake stopped state inconsistent')
        heat_capacity=r['specification']['counted_disc_stock_kg_per_car']*case['working_discs_per_car']/8*r['specification']['steel_specific_heat_J_kg_K_hypothesis']
        if abs(case['lumped_disc_temperature_C_hypothesis']-(50+case['total_disc_heat_J']/6/heat_capacity))>1e-7:raise ValueError('Brake active-disc thermal capacity differs')
        for sample in case['trace']:
            actual=sample['force']
            check=force_state(r['specification'],case['physical_translational_mass_kg_per_car'],actual['disc_heat_rate_W_per_car']/actual['torque_equivalent_brake_force_N_per_car'] if actual['torque_equivalent_brake_force_N_per_car'] else 20.,sample['force_evaluation_time_s'],grade_down_fraction=case['grade_down_fraction'],rail_adhesion=case['adhesion_hypothesis'],available_discs=case['working_discs_per_car'])
            for key in ('applied_brake_torque_Nm_per_car','rail_contact_force_N_per_car','acceleration_m_s2'):
                if abs(check[key]-actual[key])>1e-7:raise ValueError('Brake force trace differs')
        if abs(case['energy_residual_J'])>1e-5*case['initial_translational_plus_rotational_energy_J']:raise ValueError('Brake energy balance invalid')
    return r
