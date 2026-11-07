"""Same-candidate parts → mass → sourced envelopes → journey → full-scope budget."""
from copy import deepcopy
from math import ceil,pi,fsum,exp,sqrt
from pathlib import Path
import gzip,json,time
from engineering.station_rail.common import encoded,identity,digest
from . import ROOT,FLAGS,mass,profiles,economics,native_bridge,control_policy,history,lifecycle

BRIEF='engineering/station_pair/study.json'


def source_hashes(root=ROOT):
    root=Path(root)
    names=['engineering/station_pair/'+n for n in ('__init__.py','mass.py','mass-policy.json',
        'profiles.py','economics.py','cost-policy.json','coordinator.py','native_bridge.py','study.json',
        'control_policy.py','control-policy.json','history.py')]
    names += [profiles.ABB,profiles.TSA,economics.CIVIL,mass.INPUT,'engineering/station_rail/common.py']
    names += [history.OUTPUT+'/manifest.json',history.OUTPUT+'/packet-and-declared-sources.tar.gz']
    return {**{n:digest(root/n) for n in names},**native_bridge.sources(root),**lifecycle.sources(root)}


def inputs(root=ROOT):
    root=Path(root).resolve();brief=json.loads((root/BRIEF).read_bytes())
    bundle=json.loads(gzip.decompress((root/mass.INPUT).read_bytes()))
    reconciliation=mass.reconcile(bundle,unknown_mass_kg_per_train=brief['unlocated_installation_reserve_kg'],root=root)
    civil=json.loads((root/economics.CIVIL).read_bytes())
    beam=next(r for r in civil['rows'] if r['case_id']=='reference_box--reference')
    return brief,bundle,reconciliation,beam


def variants(root=ROOT):
    brief,bundle,reconciliation,beam=inputs(root);out=[]
    for distance in brief['station_spacings_m']:
        for v in profiles.build(bundle,distance,root=root):
            v['propulsion_candidate_id']=v['candidate_id']
            v['physical_definition']['civil_geometry_id']=beam['component_geometry_id']
            v['physical_definition']['civil_source_candidate_id']=beam['candidate_id']
            v['candidate_id']=identity(v['physical_definition']);out.append(v)
    return brief,bundle,reconciliation,out


def case_for(v,bundle,reconciliation,brief,*,speed_km_h,mass_case='base',force_case='base',fault=None,grade=0.,wind=0.,dt=None,temperature=None,hotel_W_per_car=None,
             control_mode='fixed',grade_observation=None,sensor_biases=None,drive_fault_observed=False,root=ROOT):
    m=next(r for r in reconciliation['mass_scenarios'] if r['case']==mass_case)
    if v['onboard_added_mass_kg'] is None:
        added=0.
    else:added=v['onboard_added_mass_kg'][mass_case]
    physical_mass=m['conditional_accounted_train_mass_kg']+brief['normal_people']*brief['passenger_mass_kg']+added
    rotation=physical_mass*brief['rotating_equivalent_fraction_hypothesis'][mass_case]
    adhesion=brief['degraded_adhesion_hypothesis'] if fault=='wet' else brief['normal_adhesion_hypothesis']
    wheel=next(p for p in bundle['parts'] if p['id']=='running/wheel')['stock']['size_m'][0]/2
    actuators=next(p for p in bundle['parts'] if p['id']=='running/service-actuator')['quantity_per_train']
    pads=2;force=actuators*brief['service_pressure_Pa_hypothesis']*pi*brief['service_piston_bore_m_hypothesis']**2/4
    force*=pads*brief['pad_friction_hypothesis']*brief['disc_effective_radius_m_hypothesis']/wheel
    force*=brief['caliper_mechanical_advantage_hypothesis']
    headway=max(h for h in brief['headway_options_s'] if h<=brief['maximum_wait_s']
        and brief['normal_people']*3600/h*brief['planning_occupancy']>=brief['peak_demand_pphpd'])
    distance=v['physical_definition']['station_spacing_m']
    c=dict(candidate_id=v['candidate_id'],mass_kg=physical_mass,rotating_equivalent_mass_kg=rotation,
        distance_m=distance,grade_fraction=grade,rolling_coefficient=brief['rolling_coefficient'],
        air_density_kg_m3=brief['air_density_kg_m3'],cd_a_m2=brief['CdA_m2'],headwind_m_s=wind,
        speed_cap_m_s=speed_km_h/3.6,acceleration_request_m_s2=brief['acceleration_request_m_s2'],
        comfort_jerk_m_s3=brief['comfort_jerk_target_m_s3'],brake_start_m=distance*.8,
        berth_tolerance_m=brief['berth_tolerance_m'],brake_force_cap_n=force,
        brake_adhesion_force_cap_n=physical_mass*9.80665*adhesion/sqrt(1+grade**2),
        brake_latency_s=brief['brake_latency_s_hypothesis'],brake_rise_s=brief['brake_rise_s_hypothesis'],
        dt_s=brief['nominal_dt_s'] if dt is None else dt,max_time_s=brief['maximum_time_s'],
        dwell_s=brief['dwell_s'],headway_s=headway,auxiliary_power_w=6*(brief['hotel_W_per_car_hypothesis'] if hotel_W_per_car is None else hotel_W_per_car),
        drive=profiles.force_profile(v,mass_kg=physical_mass,case=force_case,adhesion=adhesion,brief=brief,grade=grade),
        fault=dict(power_loss_at_s=10. if fault=='power-loss' else None,
            failed_drive_fraction=.5 if fault=='half-drive' else 0.,
            emergency_at_m=distance/2 if fault=='emergency-stop' else None),
        thermal=dict(capacity_j_k=max(1,v.get('geometry',{}).get('motors',v.get('geometry',{}).get('driven_axles',1)))*100000.,
            heat_rejection_w_k=2000.,ambient_c=brief['ambient_C'],initial_c=brief['ambient_C'] if temperature is None else temperature,maximum_c=120.))
    if c['drive'] is not None and v['family']=='cable':
        # Closed-loop rope gravity cancels; tug gradient is explicitly owned here.
        c['drive']['external_resistance_n']+=2500.*9.80665*grade
        if c['drive']['external_resistance_n']<0:raise ValueError('External assisting force requires its own signed model')
    if control_mode not in ('fixed','feedback'):raise ValueError('Explicit supported controller mode required')
    if control_mode=='feedback':
        c['control']=control_policy.prepare(v,reconciliation,brief,force,
            grade_observation=grade if grade_observation is None else grade_observation,
            biases=sensor_biases,drive_fault_observed=drive_fault_observed,root=root)
    c['id']=identity(c);return c


def followup_requests(variant,bundle,reconciliation,brief,nominal,*,root=ROOT):
    """Same experiments for both controllers; never fit a per-fault brake point."""
    speed=nominal['speed_cap_m_s']*3.6;mode='feedback' if nominal.get('control') is not None else 'fixed'
    p=json.loads((Path(root)/control_policy.POLICY).read_bytes())
    tasks=[('low-mass',dict(mass_case='low')),('high-mass',dict(mass_case='high')),
        ('wet',dict(fault='wet')),('power-loss',dict(fault='power-loss')),
        ('half-drive',dict(fault='half-drive',drive_fault_observed=True)),
        ('half-drive-unobserved',dict(fault='half-drive')),('emergency-stop',dict(fault='emergency-stop')),
        ('up-2pct',dict(grade=.02)),('down-2pct',dict(grade=-.02)),('headwind',dict(wind=15.)),
        ('high-mass-low-force',dict(mass_case='high',force_case='low')),
        ('hot-hotel',dict(hotel_W_per_car=brief['hot_hotel_control_W_per_car'])),
        ('compound-downhill-boundary',dict(mass_case='high',grade=-.02-p['grade_error_bound'],grade_observation=-.02,
             sensor_biases=dict(position_bias_m=-p['position_error_bound_m'],speed_bias_m_s=-p['speed_error_bound_m_s'],
                                acceleration_bias_m_s2=-p['acceleration_error_bound_m_s2']))),
        ('outside-brake-bound',{}),('outside-grade-bound',dict(grade=-.025,grade_observation=-.02)),
        ('tailwind-unsupported',dict(wind=-15.)),
        ('outside-position-bound',dict(sensor_biases=dict(position_bias_m=-2.))),
        ('outside-response-bound',{})]
    out=[]
    for name,kw in tasks:
        c=case_for(variant,bundle,reconciliation,brief,speed_km_h=speed,control_mode=mode,root=root,**kw)
        c['brake_start_m']=nominal['brake_start_m']
        if name=='compound-downhill-boundary':
            c['brake_force_cap_n']*=p['brake_force_lower_fraction']
            c['brake_latency_s']=p['reaction_time_bound_s'];c['brake_rise_s']=p['brake_rise_time_bound_s']
        if name=='outside-brake-bound':c['brake_force_cap_n']*=.7
        if name=='outside-response-bound':c['brake_latency_s']=2.;c['brake_rise_s']=2.
        c['id']=identity({k:v for k,v in c.items() if k!='id'})
        if nominal.get('control') is not None and not control_policy.same_policy(c['control'],nominal['control']):
            raise ValueError('A followup silently changed the controller policy')
        out.append((name,c))
    return out


def fit_brake(cases,state,*,root=ROOT,kernel=None,trials=16):
    """Bounded berth-fit evaluation; preserve every unsuccessful numerical trial."""
    bounds=[[0.,c['distance_m']] for c in cases];best=[None]*len(cases)
    held=[i for i,c in enumerate(cases) if c['drive'] is None]
    for i,r in zip(held,native_bridge.execute([cases[i] for i in held],state,root=root,kernel=kernel)):
        best[i]=(cases[i],r)
    active=[i for i in range(len(cases)) if i not in held]
    for _ in range(trials):
        trial=[]
        for i in active:
            c=cases[i];lo,hi=bounds[i]
            q=deepcopy(c);q['brake_start_m']=(lo+hi)/2;q['id']=identity({k:v for k,v in q.items() if k!='id'});trial.append(q)
        results=native_bridge.execute(trial,state,root=root,kernel=kernel)
        for i,(q,r) in zip(active,zip(trial,results)):
            if best[i] is None or abs(r['berth_error_m'])<abs(best[i][1]['berth_error_m']):best[i]=(q,r)
            if r['final_position_m']<q['distance_m']:bounds[i][0]=q['brake_start_m']
            else:bounds[i][1]=q['brake_start_m']
    return best


def _brief_result(v,c,r,cost,brief):
    scale=max(1.,abs(r['traction_work_j']),abs(r['grade_work_j']))
    criteria=dict(numerical_arrival=r['normal_numerical_arrival'],standstill_hold=r['standstill_holding'],
        energy_residual=abs(r['energy_residual_j'])<=1e-6*scale,
        declared_journey_time=r['elapsed_s']<=brief['maximum_pair_journey_s'],
        moving_jerk_target=r['maximum_absolute_jerk_m_s3']<=brief['comfort_jerk_target_m_s3']*1.01,
        demand=cost['service']['planning_capacity_pphpd']>=brief['peak_demand_pphpd'])
    control=r.get('control')
    if c.get('control') is not None:
        criteria['controller_bounds_supported']=control is not None and control['bounds_valid']
        criteria['model_route_boundary']=control is not None and not control['end_of_authority_violated']
    # The moving-jerk study target is screened; the terminal transition remains explicitly unresolved.
    complete=r['normal_numerical_arrival']
    reset=0.
    if v['family']=='cable':
        reset=(.5*v['external_mass_kg']*5.**2+v['external_resistance_N']*v['geometry']['powered_front_window_m'][1])/v['electrical_efficiency_hypothesis']
    return dict(candidate_id=v['candidate_id'],name=v['name'],family=v['family'],distance_m=c['distance_m'],
        speed_cap_km_h=c['speed_cap_m_s']*3.6,actual_peak_km_h=r['maximum_speed_m_s']*3.6 if c['drive'] is not None else None,
        mass_case='base',mass_kg=c['mass_kg'] if v['onboard_added_mass_kg'] is not None else None,
        accounted_mass_subtotal_kg=c['mass_kg'],installed_mass_kg=None,
        unquantified_architecture_additions=v['onboard_added_mass_kg'] is None,
        rotating_mass_hypothesis_kg=c['rotating_equivalent_mass_kg'],body_candidate_id=v['body_candidate_id'],
        journey_evaluation_id=r['evaluation_id'],cost_evaluation_id=cost['evaluation_id'],
        numerical_state=r['state'],numerical_arrival=r['normal_numerical_arrival'],criteria=criteria,
        outline_screen=all(criteria.values()),journey_s=r['elapsed_s'] if complete else None,partial_elapsed_s=r['elapsed_s'],berth_error_m=r['berth_error_m'],
        peak_acceleration_m_s2=r['maximum_acceleration_m_s2'] if c['drive'] is not None else None,maximum_actual_jerk_m_s3=r['maximum_absolute_jerk_m_s3'] if c['drive'] is not None else None,
        terminal_jerk_resolved=r['terminal_jerk_resolved'],terminal_acceleration_step_m_s2=r['terminal_acceleration_step_m_s2'],
        jerk_target_exceeded=r['maximum_absolute_jerk_m_s3']>brief['comfort_jerk_target_m_s3']*1.01,
        energy_residual_J=r['energy_residual_j'] if c['drive'] is not None else None,grid_propulsion_kwh=r['grid_energy_j']/3.6e6 if complete else None,
        hotel_grid_kwh=(r['auxiliary_energy_j']+c['auxiliary_power_w']*brief['terminal_turnaround_s'])/brief['hotel_charge_efficiency_hypothesis']/3.6e6 if complete else None,
        reset_grid_kwh=reset/3.6e6 if complete else None,
        full_grid_kwh=(r['grid_energy_j']+reset+(r['auxiliary_energy_j']+c['auxiliary_power_w']*brief['terminal_turnaround_s'])/brief['hotel_charge_efficiency_hypothesis'])/3.6e6 if complete else None,
        propulsion_peak_grid_MW=r['maximum_grid_power_w']/1e6 if c['drive'] is not None else None,
        base_installed_usd=min(x['installed_capital_usd']['base'] for x in cost['methods']),
        base_usd_route_km=min(x['capital_per_route_km_usd']['base'] for x in cost['methods']),
        headway_s=cost['service']['headway_s'],trainsets=cost['service']['total_trainsets'],
        control_mode='bounded-feedback' if c.get('control') is not None else 'fixed-brake-point' if c['drive'] is not None else 'not-evaluated',
        control_policy_id=None if control is None else control['policy_id'],
        control_bounds_supported=None if control is None else control['bounds_valid'],
        model_route_boundary_exceeded=None if control is None else control['end_of_authority_violated'],
        departure_held=False if control is None else control['departure_held'],
        operating_map_admitted=False,physical_journey_completed=False,**{k:v for k,v in FLAGS.items() if k!='physical_journey_completed'})


def repeated_proxy(variant,request,state,*,root=ROOT,kernel=None,brief=None,cycles=8):
    """Carry one aggregate thermal state; never call this a measured duty curve."""
    c=deepcopy(request);model=c['thermal'];ambient=model['ambient_c'];C=model['capacity_j_k'];K=model['heat_rejection_w_k']
    temperature=model['initial_c'];records=[]
    for i in range(cycles):
        c['thermal']['initial_c']=temperature;c['id']=identity({k:v for k,v in c.items() if k!='id'})
        r=native_bridge.execute([c],state,root=root,kernel=kernel)[0]
        if not r['normal_numerical_arrival']:
            return dict(state='held-journey-not-complete',cycles=records,failed_result=r,qualified=False)
        elapsed=r['journey_plus_dwell_s'];next_temperature=r['final_temperature_c']
        period=elapsed+brief['terminal_turnaround_s'] if variant['family']=='powered-wheel' else c['headway_s']
        last_drive=max((t['time_s'] for t in r['trace'] if t['traction_n']>0),default=0.)
        if period<last_drive:
            return dict(state='held-overlapping-drive-duty',cycles=records,qualified=False)
        next_temperature=ambient+(next_temperature-ambient)*exp(-K*(period-elapsed)/C)
        reset=None
        if variant['family']=='cable':
            L=variant['geometry']['powered_front_window_m'][1];speed=5.;acceleration=.5
            duration=L/speed+speed/acceleration
            exit_time=next((e['time_s'] for e in r['events'] if e['kind']=='drive-window-exit'),None)
            if exit_time is None or exit_time+duration+10.>period:
                return dict(state='held-reset-time-budget',cycles=records,qualified=False)
            force_required=variant['external_mass_kg']*acceleration+variant['external_resistance_N']
            available=min(c['drive']['points'][0]['force_n'],c['drive']['mechanical_power_w']/speed,c['drive']['contact_force_cap_n'])
            if force_required>available:
                return dict(state='held-reset-force-budget',cycles=records,qualified=False)
            mechanical=.5*variant['external_mass_kg']*speed**2+variant['external_resistance_N']*L
            grid=mechanical/variant['electrical_efficiency_hypothesis'];heat=grid-mechanical
            rise=heat/C if K==0 else (heat/duration/K)*(1-exp(-K*duration/C))*exp(-K*(period-exit_time-duration)/C)
            next_temperature+=rise
            reset=dict(return_speed_m_s=speed,acceleration_m_s2=acceleration,return_time_s=duration,
                launch_release_time_s=exit_time,attachment_allowance_s=10.,headway_margin_s=period-exit_time-duration-10.,
                force_required_N=force_required,conditional_force_cap_N=available,
                purchased_return_energy_J=grid,outgoing_detached_energy_for_disposal_J=r['detached_reset_kinetic_energy_j'],
                protected_return_path_verified=False)
        records.append(dict(cycle=i+1,start_temperature_C=temperature,next_temperature_C=next_temperature,
            reported_journey_peak_C=r['maximum_temperature_c'],period_s=period,reset=reset,
            native_receipt_id=r['native_receipt_id']))
        temperature=next_temperature
    return dict(state='calculated-uncalibrated-RC',cycles=records,qualified=False,
        last_cycle_change_C=records[-1]['next_temperature_C']-records[-1]['start_temperature_C'],
        steady_state_proven=False,idle_copper_and_standstill_losses_included=False,
        reset_heat_model='Uniform aggregate loss during assumed return stroke',
        source_motor_inverter_duty_curve_available=False)


def coast_bound(variant,request):
    if variant['family']!='cable':return None
    c=request;coast=c['distance_m']-variant['geometry']['powered_front_window_m'][1]
    kinetic=.5*(c['mass_kg']+c['rotating_equivalent_mass_kg'])*c['speed_cap_m_s']**2
    necessary=c['mass_kg']*9.80665*(c['rolling_coefficient']+c['grade_fraction'])*coast/sqrt(1+c['grade_fraction']**2)
    supported=c['headwind_m_s']>=0
    return dict(maximum_train_kinetic_at_speed_cap_J=kinetic,
        coast_gravity_and_rolling_J=necessary,aerodynamic_loss_omitted=True,
        nonnegative_headwind_domain=supported,
        fails_even_without_aerodynamic_loss=necessary>kinetic if supported else None,
        scope='Necessary energy bound at declared cap with no forward aerodynamic assistance; excludes detached tug kinetic energy')


def choose_experiments(fixed,feedback):
    """Keep the original control comparison and investigate new nominal fronts.

    Selection uses nominal outcomes only, before executing the fault suite.
    It is an experiment queue, never an integrated railway adoption.
    """
    chosen=[];keys=set()
    for group,purpose in ((fixed,'retained fixed-cohort comparison'),(feedback,'feedback-screened next experiment')):
        for family in ('cable','powered-wheel'):
            cohort=[c for c in group if c['summary']['outline_screen'] and c['variant']['family']==family
                    and c['request']['distance_m']==1500.]
            if not cohort:continue
            best=min(cohort,key=lambda c:(c['summary']['base_installed_usd'],c['summary']['journey_s']))
            key=(best['variant']['candidate_id'],best['summary']['speed_cap_km_h'])
            if key not in keys:chosen.append((best,purpose));keys.add(key)
    return chosen


def run(output,*,root=ROOT):
    root=Path(root).resolve();output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    with (output/'coordinator.lock').open('a+') as lock:
        import fcntl
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        return _run(output,root)


def _run(output,root):
    started=time.monotonic();before=source_hashes(root)
    brief,bundle,reconciliation,architectures=variants(root)
    kernel=native_bridge.build(output,root)
    normal=[];owners=[]
    for v in architectures:
        for speed in brief['speed_caps_km_h']:
            normal.append(case_for(v,bundle,reconciliation,brief,speed_km_h=speed,root=root));owners.append(v)
    fixed_fitted=fit_brake(normal,output,root=root,kernel=kernel,trials=brief['brake_search_trials'])
    requests=[case_for(v,bundle,reconciliation,brief,speed_km_h=c['speed_cap_m_s']*3.6,
                      control_mode='feedback',root=root) for v,c in zip(owners,normal)]
    fitted=list(zip(requests,native_bridge.execute(requests,output,root=root,kernel=kernel)))
    def collect(pairs):
        full=[]
        for v,(c,r) in zip(owners,pairs):
            cost=economics.evaluate(v,r,bundle,reconciliation,brief,root=root)
            row=_brief_result(v,c,r,cost,brief)
            full.append(dict(summary=row,variant=v,request=c,journey=r,cost=cost))
        return full
    full=collect(fitted);fixed_full=collect(fixed_fitted);rows=[c['summary'] for c in full]
    # Separate fronts per equal station spacing. Held/failed/unknown objectives never become zero.
    for row in rows:
        cohort=[x for x in rows if x['distance_m']==row['distance_m'] and x['outline_screen']]
        objectives=('base_installed_usd','journey_s','full_grid_kwh')
        row['pareto_for_next_experiment']=row['outline_screen'] and not any(
            all(x[k]<=row[k] for k in objectives) and any(x[k]<row[k] for k in objectives) for x in cohort)
    finalists=choose_experiments(fixed_full,full)
    followups=[]
    for selected,purpose in finalists:
        v=selected['variant'];speed=selected['summary']['speed_cap_km_h']
        old=next(c for c in fixed_full if c['variant']['candidate_id']==v['candidate_id']
                 and c['summary']['speed_cap_km_h']==speed)
        finalist=next(c for c in full if c['variant']['candidate_id']==v['candidate_id']
                      and c['summary']['speed_cap_km_h']==speed)
        tasks=followup_requests(v,bundle,reconciliation,brief,finalist['request'],root=root)
        fixed_tasks=followup_requests(v,bundle,reconciliation,brief,old['request'],root=root)
        results=native_bridge.execute([c for _,c in tasks+fixed_tasks],output,root=root,kernel=kernel)
        cases=list(zip(tasks,results[:len(tasks)]));fixed_cases=list(zip(fixed_tasks,results[len(tasks):]))
        refined=deepcopy(finalist['request']);refined['dt_s']=brief['refined_dt_s'];refined['id']=identity({k:v for k,v in refined.items() if k!='id'})
        fine=native_bridge.execute([refined],output,root=root,kernel=kernel)[0]
        refined_ok=abs(fine['final_position_m']-finalist['journey']['final_position_m'])<=brief['berth_tolerance_m']
        def detailed_cases(cases):
            return [dict(name=name,request=c,result=r,unpowered_route_energy_bound=coast_bound(v,c))
                    for (name,c),r in cases]
        followups.append(dict(candidate_id=v['candidate_id'],speed_cap_km_h=speed,
            experiment_purpose=purpose,
            cases=detailed_cases(cases),fixed_control_cases=detailed_cases(fixed_cases),
            controller_basis='One bounded position/speed/acceleration policy; no offline or per-fault brake-point fitting',
            refinement=dict(coarse_dt_s=finalist['request']['dt_s'],fine_dt_s=refined['dt_s'],result=fine,
                final_position_change_m=fine['final_position_m']-finalist['journey']['final_position_m'],
                berth_comparison_within_declared_tolerance=refined_ok,
                scope='Coupled plant timestep and controller-update-cadence sensitivity; not a pure fixed-sample integration convergence proof'),
            repeated_duty_proxy=repeated_proxy(v,finalist['request'],output,root=root,kernel=kernel,brief=brief),
            recovery_between_stations_protected=False,regeneration_credit_J=None,
            periodic_thermal_qualification=False))
    if source_hashes(root)!=before:raise ValueError('Station-pair source changed during execution')
    for c in full+fixed_full:c['lifecycle']=lifecycle.evaluate(c['cost'],brief,root=root)
    result=dict(schema='osr-station-pair-study/2',brief=brief,body_candidate_id=bundle['candidate_id'],
        body_bundle_id=bundle['bundle_id'],mass_evaluation_id=reconciliation['evaluation_id'],
        source_sha256=before,native_build_id=kernel[1]['receipt_id'],native_binary_sha256=kernel[1]['binary_sha256'],
        normal_case_count=len(rows),conditional_arrivals=sum(r['numerical_arrival'] for r in rows),
        outline_screens=sum(r['outline_screen'] for r in rows),rows=rows,cases=full,finalists=followups,
        fixed_control_cases=fixed_full,parent_fixed_control=history.verify(root),
        control_method='bounded-distance-feedback/1',feedback_brake_point_fits=0,
        fixed_nominal_brake_point_fit_trials=brief['brake_search_trials'],
        experiment_selection_basis='Retained fixed cohorts plus nominal feedback-screened representatives, selected before the common fault suite; no integrated adoption',
        mass_summary=dict(nominal_stock_kg=bundle['nominal_mass_kg'],
            conditional_mass_scenarios=reconciliation['mass_scenarios'],
            located_CG_complete=False,axle_loads_complete=False,rotating_inertia_measured=False),
        next_experiment_candidate_ids=[f['candidate_id'] for f in followups],integrated_selection=None,
        regeneration_saving_credited=False,available_operating_maps_added=0,priced_city_models_replaced=0,
        limitations=['Conditional rating envelopes do not establish attainable motor/inverter/transmission duty',
            'Installation reserve and centroid boxes are assumptions; full installed CAD, trim, CG and axle reactions remain open',
            'Pneumatic bore/pressure/pad friction and control response are assumptions, not tested brake curves',
            'Controller observations, mass/braking/response bounds and initial applied hold are hypotheses; no operating authority or authenticated protection evidence',
            'Jerk discontinuities are reported; validated passenger/protection limits and contact/multibody dynamics remain open',
            'No energy-recovery credit, station storage or rescue hardware performance is invented',
            'Civil geometry quantities are used for cost only; its earlier structural loads and crane admission do not transfer',
            'Grid energy excludes unmodeled standstill motor/copper losses; thermal model is an uncalibrated one-lump proxy'],
        execution_wall_s=time.monotonic()-started,**FLAGS)
    result['study_id']=identity(result)
    (output/'result.json.gz').write_bytes(gzip.compress(encoded(result),mtime=0))
    (output/'mass-reconciliation.json.gz').write_bytes(gzip.compress(encoded(reconciliation),mtime=0))
    receipt=dict(schema='osr-station-pair-run/1',study_id=result['study_id'],source_sha256=before,
        files_sha256={n:digest(output/n) for n in ('result.json.gz','mass-reconciliation.json.gz')},**FLAGS)
    receipt['manifest_id']=identity(receipt);(output/'manifest.json').write_bytes(encoded(receipt))
    return result
