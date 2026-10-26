"""Bounded propulsion-family proposals, not a change to the development default.

This layer prepares explicit geometry/material/service alternatives and cheap
necessary checks. It does not dispatch a solver or turn active area into a
thrust estimate. New topologies require their own verified native adapters.
"""
from copy import deepcopy
from math import isfinite,sqrt
from pathlib import Path
import json
from engineering.station_rail.common import identity,digest
from . import wheel_motor
PRODUCER='engineering/design_search/propulsion_families.py'
FLAGS=dict(configuration_adopted=False,engineering_accepted=False,physical_accepted=False,
    manufacturing_release=False,operating_release=False,complete_installed_twin=False)
BOUNDS=dict(fin_count=[1,3],fin_length_m=[7.,12.],active_height_m=[.12,.18],secondary_thickness_m=[.010,.020],
    physical_gap_m=[.015,.020],pole_pitch_m=[.20,.50],slots_per_period=[6,12],slot_fill_max=.60,
    wire_density_RMS_A_mm2_max=4.,linear_model_peak_field_limit_T=1.3,
    reserved_transverse_half_corridor_m=.62,primary_top_TOR_m_max=.20,
    speed_m_s=[12.,20.],acceleration_m_s2=[.25,.40],powered_station_length_m=[600.,1200.])


def material_options():
    """Supplier checkpoints/printed curves remain distinct from a solver law.

    Supplier tables report polarization J(H), not an accepted B(H) curve.
    B=J+mu0*H; three guaranteed checkpoints do not define a nonlinear model.
    Cold-work, assembly stress, hot losses and the delivered lot remain unknown.
    """
    return {
      'linear-1000-hypothesis':dict(kind='core',density_kg_m3=7850.,data_maturity='declared-linear-research-hypothesis',
          relative_mu=1000.,research_peak_field_limit_T=1.3,source_url=None,solver_BH_curve=None,qualified=False),
      'sij-M330-50A':dict(kind='core',supplier='SIJ Acroni',grade='M330-50A',density_kg_m3=7610.,lamination_thickness_m=.0005,
          source_url='https://cms.sij.si/storage/336/SIWATT-M330-50A.pdf',
          source_sha256='ad32a111ccea78b301b606b921387ab37437ee771ab784dbd8c98f611c467773',source_pages=[1,2],
          published_data_kind='50Hz magnetic polarization J(H), typical plotted magnetization/loss curves and specified checkpoints',
          H_A_m=[2500.,5000.,10000.],minimum_polarization_J_T=[1.49,1.60,1.70],typical_polarization_J_T=[1.53,1.62,1.74],
          maximum_specific_loss_W_kg_at_50Hz_1_5T=3.30,data_maturity='primary-supplier-published-data-not-correlated',
          solver_BH_curve=None,curve_digitization_verified=False,hot_and_stressed_data=None,qualified=False),
      'powercore-M270-35A':dict(kind='core',supplier='thyssenkrupp Steel',grade='M270-35A',density_kg_m3=7650.,lamination_thickness_m=.00035,
          source_url='https://www.thyssenkrupp-steel.com/media/content_1/publikationen/lieferprogramme/thyssenkrupp_product-range_no-electrical-steel_powercore_steel_en.pdf',
          source_sha256=None,source_pages=[17],retrieval_note='Primary PDF read through web source; direct binary request returned403; no byte hash invented',
          published_data_kind='Specified minimum polarization checkpoints; not a complete B-H law',H_A_m=[2500.,5000.,10000.],
          minimum_polarization_J_T=[1.49,1.60,1.70],maximum_specific_loss_W_kg_at_50Hz_1_5T=2.70,
          data_maturity='primary-supplier-published-checkpoints',solver_BH_curve=None,hot_and_stressed_data=None,qualified=False),
      'isovac-simulation-catalogue':dict(kind='material-data-source',supplier='voestalpine',
          source_url='https://www.voestalpine.com/isovac/Downloads/Datenblaetter',
          published_data_kind='Supplier lists grade-specific simulation spreadsheets including330-50A',
          data_maturity='catalogue-discovered-file-not-ingested',source_sha256=None,solver_BH_curve=None,qualified=False),
      'copper-hypothesis':dict(kind='conductor',density_kg_m3=8960.,resistivity_20C_ohm_m=1.724e-8,
          data_maturity='declared-stock-hypothesis-no-lot-or-insulation-specification',qualified=False),
      'aluminium-hypothesis':dict(kind='conductor',density_kg_m3=2710.,resistivity_20C_ohm_m=2.826e-8,
          data_maturity='declared-stock-hypothesis-no-lot-or-insulation-specification',qualified=False)}


def _physical_identity(physical):
    return identity({n:v for n,v in physical.items() if n not in ('name','label')})


def _base(parent):
    defaults=wheel_motor.default_parameters()
    p=deepcopy(parent.get('architecture',{}).get('wheel_parameters',{}).get('motor',defaults['physical']))
    p.pop('name',None);p.update(topology='double-sided-LIM',fin_centres_y_m=[0.],
        core_material='linear-1000-hypothesis',conductor_material='copper-hypothesis',secondary_material='aluminium-hypothesis',
        cooling=dict(method='conductive-heat-spreader',installed_hardware_mass_kg=None,heat_rejection_W=None),
        single_sided_secondary_backiron_m=0.,rack_tooth_depth_m=0.,rack_pitch_m=None,rack_tooth_duty=None)
    return p,deepcopy(defaults['evaluation'])


def _option(parent,physical,evaluation,service,label,rationale):
    if not parent.get('candidate_id') or not parent.get('requirement_revision'):raise ValueError('Explicit parent candidate and requirements required')
    base_service=dict(speed_m_s=20.,acceleration_m_s2=.4,service_deceleration_m_s2=.6,
        powered_station_length_m=900.,headway_s=120.,dwell_s=35.,cars=6,people_per_car=46,train_length_m=104.5)
    base_service.update(service)
    changed=any(base_service[n]!=v for n,v in dict(speed_m_s=20.,acceleration_m_s2=.4,powered_station_length_m=900.,headway_s=120.,cars=6,people_per_car=46).items())
    revision=identity(dict(parent_requirement_revision=parent['requirement_revision'],service_alternative=base_service)) if changed else parent['requirement_revision']
    option=dict(schema='osr-expanded-propulsion-proposal/1',parent_candidate_id=parent['candidate_id'],
        parent_requirement_revision=parent['requirement_revision'],requirement_revision=revision,label=label,rationale=rationale,
        parent_counted_passive_fin_mass_kg=sum(g['native_part']['mass_kg'] for g in parent.get('geometry',[]) if g.get('native_part',{}).get('id')=='station-secondary/active-fin') if any(g.get('native_part',{}).get('id')=='station-secondary/active-fin' for g in parent.get('geometry',[])) else None,
        physical=deepcopy(physical),physical_design_id=_physical_identity(physical),evaluation_hypotheses=deepcopy(evaluation),
        service=base_service,service_is_requirement_alternative=changed,changes_development_default=False,
        candidate_bundle_patch=dict(architecture=dict(wheel_parameters=dict(motor=deepcopy(physical)))),
        bundle_materialization='Required before CAD/BOM/civil/dynamics; new fin/mount/normal-force interfaces may need adapter development',
        available_installed_force_N=None,whole_life_cost_USD=None,**FLAGS)
    option['proposal_id']=identity(option);return option


def _check(option):
    p=option['physical'];s=option['service'];e=option['evaluation_hypotheses']
    if option['physical_design_id']!=_physical_identity(p):raise ValueError('Physical proposal identity differs')
    if p['topology'] not in ('double-sided-LIM','single-sided-LIM','passive-linear-reluctance'):raise ValueError('Named supported proposal topology required')
    for n in ('primary_length_m','pole_pitch_m','slot_width_m','slot_depth_m','backiron_m','conductor_area_m2','active_height_m','secondary_length_m','secondary_thickness_m','gap_each_side_m'):
        if not isinstance(p[n],(int,float)) or not isfinite(p[n]) or p[n]<=0:raise ValueError('Positive finite physical '+n+' required')
    if p['slots_per_period'] not in (6,12) or type(p['periods']) is not int or type(p['turns_per_coil']) is not int or type(p['parallel_paths_per_phase']) is not int:raise ValueError('Integer winding topology required')
    if len(p['fin_centres_y_m']) not in (1,2,3) or len(set(p['fin_centres_y_m']))!=len(p['fin_centres_y_m']):raise ValueError('One to three uniquely located fins required')
    if any(not isinstance(y,(int,float)) or not isfinite(y) for y in p['fin_centres_y_m']):raise ValueError('Finite lateral fin coordinates required')
    if abs(p['primary_length_m']-2*p['pole_pitch_m']*p['periods'])>1e-8:raise ValueError('Integer magnetic periods must match the finite primary')
    if p['core_material'] not in material_options() or material_options()[p['core_material']].get('kind')!='core' or p['conductor_material'] not in ('copper-hypothesis','aluminium-hypothesis'):raise ValueError('Named core and conductor data required')
    if p['secondary_material'] not in ('aluminium-hypothesis','copper-hypothesis','sij-M330-50A'):raise ValueError('Named passive secondary material required')
    if p['topology']=='passive-linear-reluctance' and (p['secondary_material']!='sij-M330-50A' or p['rack_pitch_m'] is None or not 0<p['rack_tooth_depth_m']<p['secondary_thickness_m'] or not 0<p['rack_tooth_duty']<1):raise ValueError('Explicit passive toothed steel rack required')
    if p['slot_width_m']>=2*p['pole_pitch_m']/p['slots_per_period'] or p['turns_per_coil']<1 or p['periods']<1 or p['parallel_paths_per_phase']<1:raise ValueError('Positive manufacturable teeth/turns/periods/paths required')
    if e['current_peak_A']<0 or not isfinite(e['current_peak_A']):raise ValueError('Finite nonnegative source current required')
    for n in ('speed_m_s','acceleration_m_s2','service_deceleration_m_s2','powered_station_length_m','headway_s'):
        if not isfinite(s[n]) or s[n]<=0:raise ValueError('Positive finite service alternative required')
    if any(option.get(n) is not v for n,v in FLAGS.items()) or option['changes_development_default'] is not False:raise ValueError('Proposal cannot select or release a design')


def necessary_screens(option,context=None):
    """Cheap definitions, counted material and ideal necessary service bounds.

    Additional supports, insulation, cooling, converters, winding current
    sharing and actual launch force remain unknown. Material weights are
    counted-stock lower bounds, not complete installed system mass.
    """
    _check(option);context={} if context is None else context;p=option['physical'];s=option['service'];e=option['evaluation_hypotheses'];data=material_options()
    count=len(p['fin_centres_y_m']);sides=1 if p['topology']=='single-sided-LIM' else 2;L=p['primary_length_m'];h=p['active_height_m'];pitch=2*p['pole_pitch_m']/p['slots_per_period']
    fill=p['turns_per_coil']*p['conductor_area_m2']/(p['slot_width_m']*p['slot_depth_m']);J=e['current_peak_A']/sqrt(2)/(p['conductor_area_m2']*1e6)
    tooth=pitch-p['slot_width_m'];outer=p['secondary_thickness_m']/2+p['gap_each_side_m']+p['slot_depth_m']+p['backiron_m']
    centre=sorted(p['fin_centres_y_m']);overlap=any(b-a<2*outer for a,b in zip(centre,centre[1:]));inside=max(abs(y)+outer for y in centre)<=BOUNDS['reserved_transverse_half_corridor_m']
    coils_per_phase=int(p['periods']*p['slots_per_period']*sides/6)
    parallel_ok=1<=p['parallel_paths_per_phase']<=coils_per_phase and coils_per_phase%p['parallel_paths_per_phase']==0
    secondary_volume=count*p['secondary_length_m']*p['secondary_thickness_m']*h
    if p['topology']=='passive-linear-reluctance':secondary_volume-=count*p['secondary_length_m']*p['rack_tooth_depth_m']*(1-p['rack_tooth_duty'])*h
    secondary_mass=secondary_volume*data[p['secondary_material']]['density_kg_m3']
    backing_mass=count*p['secondary_length_m']*p['single_sided_secondary_backiron_m']*h*data[p['core_material']]['density_kg_m3']
    iron_per_m=count*sides*(p['backiron_m']+p['slot_depth_m']*(1-p['slot_width_m']/pitch))*h*data[p['core_material']]['density_kg_m3']
    coil_length=p['turns_per_coil']*(2*(h+p['pole_pitch_m'])+.05)
    copper_per_m=count*sides*p['slots_per_period']/2/(2*p['pole_pitch_m'])*coil_length*p['conductor_area_m2']*data[p['conductor_material']]['density_kg_m3']
    v=s['speed_m_s'];a=s['acceleration_m_s2'];b=s['service_deceleration_m_s2'];xa=v*v/(2*a);xb=v*v/(2*b);setback=(17.-p['secondary_length_m'])/2
    cap_braking_zone=xa+xb+s['train_length_m']-2*setback
    # Coasting lowers arrival speed. Full-cap braking distance is a declared
    # zero-resistance scenario, not a necessary lower bound for every journey.
    necessary_zone=xa+s['train_length_m']-2*setback
    failures=[]
    screens=dict(slot_fill='pass' if fill<=.60 else 'fail',wire_density='pass' if J<=4. else 'fail',positive_teeth='pass' if tooth>0 else 'fail',
        passive_fin_bounds='pass' if 7.<=p['secondary_length_m']<=12. and .12<=h<=.18 and .010<=p['secondary_thickness_m']<=.020 else 'fail',
        service_bounds='pass' if 12.<=v<=20. and .25<=a<=.40 and 600.<=s['powered_station_length_m']<=1200. else 'fail',
        pole_pitch_bounds='pass' if .20<=p['pole_pitch_m']<=.50 else 'fail',
        gap_bound='pass' if .015<=p['gap_each_side_m']<=.020 else 'fail',
        fin_top_TOR='pass' if p['secondary_bottom_TOR_m']+h<=.2+1e-10 else 'fail',
        primary_cross_sections='pass' if not overlap and inside else 'fail',equal_parallel_group_count='pass' if parallel_ok else 'fail',
        ideal_powered_length='pass' if s['powered_station_length_m']>=necessary_zone else 'fail')
    failures=[n for n,value in screens.items() if value=='fail']
    ideal_times={}
    for distance in (1500.,2000.):
        peak=min(v,sqrt(2*distance/(1/a+1/b)));launch=peak*peak/(2*a);brake=peak*peak/(2*b)
        ideal_times[str(int(distance))]=peak/a+peak/b+(distance-launch-brake)/peak
    known_lower_mass=context.get('accounted_mass_kg_per_car');required=None
    if known_lower_mass is not None:
        if not isfinite(known_lower_mass) or known_lower_mass<=0:raise ValueError('Positive accounted mass required')
        old_fin=context.get('parent_passive_fin_mass_kg',option['parent_counted_passive_fin_mass_kg'])
        if old_fin is None:known_lower_mass=None
        elif not isfinite(old_fin) or old_fin<0:raise ValueError('Finite nonnegative parent counted fin mass required')
        else:known_lower_mass+=secondary_mass+backing_mass-old_fin
        rot=context.get('rotating_equivalent_mass_kg_per_car')
        if rot is not None and known_lower_mass is not None:
            if not isfinite(rot) or rot<0:raise ValueError('Nonnegative rotating-equivalent mass required')
            required=(known_lower_mass+rot)*a+.0025*known_lower_mass*9.80665+50+1.8*v*v
    stock=dict(passive_secondary_kg_per_car=secondary_mass,passive_secondary_backing_kg_per_car=backing_mass,
        bare_primary_steel_kg_per_m=iron_per_m,bare_primary_conductor_kg_per_m=copper_per_m,
        bare_primary_kg_per_addressed_module=(iron_per_m+copper_per_m)*L,
        bare_primary_kg_per_station_direction=(iron_per_m+copper_per_m)*s['powered_station_length_m'])
    unknown=['Fin/primary mounts and clearance interfaces','Lamination insulation and assembly','Cooling hardware and heat rejection',
        'Converter branches, current sharing, switching and cables','Civil reactions and normal forces','Complete equipped vehicle mass',
        'Prices, fabrication labour and whole-life renewals','Actual headway, fleet and journey performance']
    return dict(schema='osr-propulsion-necessary-screen/1',proposal_id=option['proposal_id'],physical_design_id=option['physical_design_id'],
        necessary_screens=screens,necessary_screen='fail' if failures else 'pass',failed_necessary_screens=failures,
        installed_engineering_screen='unknown',slot_fill_fraction=fill,wire_density_RMS_A_mm2=J,tooth_width_m=tooth,
        fin_active_faces_m2=count*sides*p['secondary_length_m']*h,coils_per_phase_per_fin=coils_per_phase,
        converter_phase_current_RMS_A=e['current_peak_A']/sqrt(2)*p['parallel_paths_per_phase']*count,
        stock=stock,accounted_translation_mass_lower_bound_kg_per_car=known_lower_mass,required_launch_force_N_lower_bound=required,
        ideal_station_powered_length_necessary_m=necessary_zone,ideal_zero_resistance_cap_braking_envelope_m=cap_braking_zone,
        zero_resistance_cap_braking_layout_screen='pass' if s['powered_station_length_m']>=cap_braking_zone else 'fail',
        kinematic_bound_scope='Necessary launch plus train engagement only; separately shown full-cap braking assumes zero coast resistance and is not a universal necessary condition',
        ideal_no_resistance_journey_time_s=ideal_times,
        nominal_arithmetic_passengers_per_hour_direction=s['cars']*s['people_per_car']*3600/s['headway_s'],
        retained_capacity_comparison_passengers_per_hour_direction=14400,actual_protected_headway_s=None,
        counted_material_cost_USD=None,complete_installed_cost_USD=None,whole_life_cost_USD=None,
        available_installed_force_N=None,unknown_inventory_and_evidence=unknown,
        stock_scope='Bare geometry-derived stock only; multiplicity is not a thrust-scaling model',**FLAGS)


def _triggers(diagnostics):
    text=json.dumps(diagnostics,sort_keys=True).lower();tags=[]
    if any(x in text for x in ('linear_steel','outside_linear','satur','field_domain','2.24')):tags.append('field-domain')
    if any(x in text for x in ('insufficient','thrust','force_screen','force reserve')):tags.append('thrust')
    if any(x in text for x in ('cost','price','econom')):tags.append('economics')
    if any(x in text for x in ('nonconverg','invalid','tool_error','force_balance')):tags.append('numerical')
    return tags or ['unresolved-engineering']


def next_experiments(option,diagnostics):
    _check(option);tags=_triggers(diagnostics);p=option['physical'];tasks=[]
    def add(kind,question,allowed,native_cases=0):
        value=dict(kind=kind,parent_candidate_id=option['parent_candidate_id'],physical_design_id=option['physical_design_id'],requirement_revision=option['requirement_revision'],
            question=question,allowed_variables=allowed,maximum_native_cases=native_cases,maximum_runtime_s=240 if native_cases else 120,
            required_output='Immutable source/input/output/log identities with numerical, model-domain and engineering states separated',
            physical_acceptance=False,default_change_authorized=False)
        value['task_id']=identity(value);tasks.append(value)
    if 'numerical' in tags:add('repair-and-confirm-method','Resolve invalid discretization or solver execution before using its physical outputs',['mesh','quadrature','solver settings'],2)
    if 'field-domain' in tags or p['core_material']!='linear-1000-hypothesis':
        add('nonlinear-material-validation','Import full supplier J(H)/loss data with units and B=J+mu0H conversion, validate interpolation and hot/stressed coupons; retain old1.3T linear bound',['core grade','digitized curve','coupon conditions','tooth/return sections'],2)
    if 'thrust' in tags or p['topology']!='double-sided-LIM' or len(p['fin_centres_y_m'])>1:
        add('finite-topology-force-map','Evaluate actual finite primary, every fin and current return; measure normal forces and saturation. Do not multiply a single-fin force result',['active area','fin geometry','pole/slot layout','slip3–15Hz','coil stock'],3)
    if p['topology']=='single-sided-LIM':add('normal-force-interface','Recalculate wheel loads, reaction-plate bending, rail adhesion and mounting gaps under single-sided attraction',['steel backing','mount stiffness','primary arrangement'],2)
    if p['topology']=='passive-linear-reluctance':add('reluctance-adapter-benchmark','Develop position-dependent nonlinear reluctance/commutation model with passive toothed secondary; confirm force ripple and normal loads',['tooth profile','phase overlap','position sensing'],3)
    add('electrothermal-circuit','Calculate real per-branch flux/voltage, current sharing, cooling and120s duty with counted equipment',['branch grouping','conductor','insulation','cooling'],2)
    if 'economics' in tags or option['service_is_requirement_alternative']:
        add('equal-service-system-comparison','Compare station-only induction and passive reluctance, complete primary/vehicle/civil/fleet stock and same-service costs; unknown prices stay unknown',['topology','speed','acceleration','powered length','fleet'],0)
    return tasks


def wheel_motor_parameters(option):
    """A strict bridge for already-supported single-fin linear-Cu double LIMs.

    Rejection is intentional: new physical families must not be silently mapped
    into the old two-dimensional geometry or a multiplied force estimate.
    """
    _check(option);p=option['physical']
    if p['topology']!='double-sided-LIM' or p['fin_centres_y_m']!=[0.] or p['slots_per_period']!=6 or p['core_material']!='linear-1000-hypothesis' or p['conductor_material']!='copper-hypothesis' or p['secondary_material']!='aluminium-hypothesis' or p['single_sided_secondary_backiron_m']!=0:raise ValueError('New native topology/material adapter required')
    base=wheel_motor.default_parameters();base['physical']={n:deepcopy(p[n]) for n in base['physical'] if n!='name'};base['physical']['name']=option['label']
    for n in ('current_peak_A','slip_frequency_Hz'):base['evaluation'][n]=option['evaluation_hypotheses'][n]
    wheel_motor.definition(base);return base


def expanded_plan(parent,diagnostics,*,candidate_budget=12,native_case_budget=12,confirmation_case_budget=4,context=None):
    """Prepare twelve proposals, screening first; execute no native workers."""
    if candidate_budget!=12 or not 0<=native_case_budget<=12 or not 0<=confirmation_case_budget<=4:raise ValueError('First expansion is bounded to12 proposals,12 primary and4 confirmation cases')
    p,e=_base(parent);options=[]
    def add(label,changes=None,eval_changes=None,service=None,why='Failure-driven alternative'):
        physical=deepcopy(p);physical.update(changes or {});evaluation=deepcopy(e);evaluation.update(eval_changes or {})
        options.append(_option(parent,physical,evaluation,service or {},label,why))
    add('deeper-return-and-teeth',dict(backiron_m=.09,slot_width_m=.035,slot_depth_m=.08),why='Increase return and tooth area under the retained1.3T linear-domain limit')
    add('two-parallel-passive-fins',dict(fin_centres_y_m=[-.28,.28],active_height_m=.16),why='Increase actual active area; include coupled fins and doubled interfaces in new spatial model')
    add('three-passive-fins',dict(fin_centres_y_m=[-.43,0.,.43],active_height_m=.16),why='Test greater area against track envelope, wayside stock and maintenance')
    add('longer-passive-fin',dict(secondary_length_m=12.),why='Test finite overlap/end effects with a regenerated car interface')
    add('longer-pole-pitch',dict(periods=15,pole_pitch_m=12.5/30),why='Change magnetic wavelength/tooth width and actual slip frequency, preserving exact finite module length')
    add('distributed-twelve-slot-period',dict(slots_per_period=12,slot_width_m=.022,turns_per_coil=24,conductor_area_m2=25e-6),dict(current_peak_A=140.),why='Explore two slots per phase belt with explicit coil-side grouping and new winding factors')
    add('twenty-parallel-circuit-paths',dict(parallel_paths_per_phase=20),why='Count increased converter current and branch equipment; validate unequal finite-overlap fluxes')
    add('aluminium-primary-winding',dict(conductor_material='aluminium-hypothesis',turns_per_coil=36,conductor_area_m2=50e-6,slot_width_m=.055,slot_depth_m=.075,
        cooling=dict(method='wayside-liquid-loop',installed_hardware_mass_kg=None,heat_rejection_W=None)),why='Compare lower conductor-stock density with resistive heating, joining and cooling burden')
    add('single-sided-induction',dict(topology='single-sided-LIM',single_sided_secondary_backiron_m=.025),why='Compare reduced primary stock against train-borne backiron and unwanted normal attraction')
    add('passive-toothed-reluctance',dict(topology='passive-linear-reluctance',secondary_material='sij-M330-50A',secondary_thickness_m=.02,
        rack_tooth_depth_m=.006,rack_pitch_m=.08,rack_tooth_duty=.5,core_material='sij-M330-50A'),why='Compare a passive toothed steel secondary; requires a new position-dependent commutated model')
    add('supplier-steel-57_6kmh',dict(core_material='sij-M330-50A'),service=dict(speed_m_s=16.,acceleration_m_s2=.3,powered_station_length_m=800.),why='Combine supplier nonlinear-data study with an explicit lower-speed, shorter-powered-zone requirement alternative')
    add('thin-lamination-43_2kmh',dict(core_material='powercore-M270-35A',secondary_thickness_m=.012),service=dict(speed_m_s=12.,acceleration_m_s2=.25,powered_station_length_m=600.),why='Compare thinner core laminations and passive-fin stock at a separate lower-speed service requirement')
    rows=[];remaining=native_case_budget
    for option in options:
        screen=necessary_screens(option,context);tasks=next_experiments(option,diagnostics)
        try:wheel_motor_parameters(option);ready=True
        except ValueError:ready=False
        allocation=min(2,remaining) if ready and screen['necessary_screen']=='pass' else 0;remaining-=allocation
        rows.append(dict(proposal=option,screen=screen,next_experiments=tasks,current_native_adapter_ready=ready,
            reserved_primary_cases=allocation,dispatch='not-started',adapter_extension_required=not ready))
    result=dict(schema='osr-expanded-propulsion-plan/1',parent_candidate_id=parent['candidate_id'],parent_requirement_revision=parent['requirement_revision'],
        diagnostic_triggers=_triggers(diagnostics),candidate_proposal_count=len(rows),distinct_physical_designs=len({r['proposal']['physical_design_id'] for r in rows}),
        source_sha256={PRODUCER:digest(Path(__file__).resolve()),wheel_motor.PRODUCER:digest(Path(wheel_motor.__file__).resolve())},
        bounds=deepcopy(BOUNDS),proposals=rows,budget=dict(candidate_proposals=12,maximum_primary_native_cases=native_case_budget,
            reserved_primary_native_cases=native_case_budget-remaining,unallocated_primary_native_cases=remaining,maximum_confirmation_cases=confirmation_case_budget,
            aggregate_runtime_s=1200,worker_RAM_bytes=3*1024**3,threads_per_worker=1),
        automatic_native_dispatch=False,changes_development_default=False,whole_system_selection='held pending materialization, valid native maps and equal-service economics',**FLAGS)
    result['plan_id']=identity(result);return result
