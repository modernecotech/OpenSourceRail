"""Same-candidate coupling and diagnostic ranking, without invented price/physics."""
from . import contracts as k
from engineering.station_rail import operations,braking,electrical


def evaluate(candidate,car,parameters,dependencies,request):
    rot=braking.rotating_stock(car)['equivalent_inertial_mass_kg_per_car'];profiles=[]
    for distance in (1500.,2000.,2999.9312214890124):
        for load,key in [('empty','accounted_tare_kg_per_car'),('normal','accounted_cap_loaded_kg_per_car'),('crowd','accounted_160_control_kg_per_car')]:
            profiles.append(operations.profile(distance,car['mass'][key],loading=load,rotating_equivalent_mass_kg_per_car=rot))
    required=next(p for p in profiles if p['inputs']['distance_m']==2000 and p['inputs']['loading']=='normal')
    zones=[operations.station_zone(required,L,train_length_m=104.5,dwell_s=35.,headway_s=120.) for L in (700.,800.,900.,1000.)]
    tasks=[];penalty=0.
    for name,result in dependencies.items():
        bad=result['numerical_status'] in ('invalid','nonconverged','unknown')
        if bad:
            # No force/deflection from an invalid numerical/material model is
            # used as a physical objective. This is an explicit diagnostic cost.
            penalty+=3.;kind='numerical-failure'
        elif result['screen_status']=='fail':penalty+=1.;kind='design-failure'
        else:penalty+=.25;kind='evidence-gap'
        if name=='wheel-definition':continue
        tasks.append(dict(candidate_id=candidate['candidate_id'],trigger_evaluation_id=result['evaluation_id'],
            failure_class=kind,domain=name,state='prepared-for-specialist',
            next_action={'wheel-body':'Revise counted load paths if stiffness fails; establish joint/laminate, local stress, buckling and modes before qualification.',
                'wheel-motor':'Revise tooth/backiron/winding geometry after field/force failure; validate nonlinear material, finite-height and entry/exit maps.',
                'wheel-brakes':'Size real actuator/thermal stock and qualify supplier/WSP curves; adhesion below downhill grade requires route/protection changes.',
                'wheel-civil':'Recalculate generated vehicle axle loads, torsion/fatigue and complete site/construction quantities.'}.get(name,'Resolve installed stock and evidence'),
            bounded_contract=dict(max_native_jobs=4,runtime_s=600,fixed_requirements=candidate['requirement_revision'])))
    motor=dependencies['wheel-motor'];native=motor['diagnostics'][0].get('native',{})
    force_map_supported=(motor['numerical_status']=='converged' and native.get('complete_installed_force_map') is True)
    # A centred full-overlap sample cannot be scaled through entry/exit. These
    # scenarios are coupled jobs with explicit unsupported-state stops, rather
    # than ideal acceleration relabelled as a simulated physical journey.
    journeys=[dict(candidate_id=candidate['candidate_id'],distance_m=p['inputs']['distance_m'],load=p['inputs']['loading'],
        analytical_requirement_profile_id=p['profile_id'],execution='held',failure_class='evidence-gap',
        stop_reason='Candidate-specific force(x,v,I,T,g) entry/exit map, qualified brake/contact plant and flexible modes unavailable',
        motor_evaluation_id=motor['evaluation_id'],body_evaluation_id=dependencies['wheel-body']['evaluation_id'],
        physical_journey_completed=False,position_m=None,elapsed_s=None) for p in profiles]
    tasks.append(dict(candidate_id=candidate['candidate_id'],trigger_evaluation_id=motor['evaluation_id'],failure_class='system-incompatibility',domain='coupled-journey',state='prepared-for-specialist',
        next_action='Generate finite motor-overlap/phase/current/temperature maps and connect wheel-contact/flexible-body/independent brakes. Do not use unsupported overlap scaling.',
        bounded_contract=dict(max_native_jobs=6,runtime_s=900,fixed_requirements=candidate['requirement_revision'])))
    from . import wheel_motor
    primary=wheel_motor.definition(parameters['motor'])['bare_primary_stock_kg_per_m']
    diagnostics=[dict(failure_class='evidence-gap',reason='Same-candidate required motion, rotor energy, station geometry, quantities and open cost coverage',
        candidate_id=candidate['candidate_id'],profiles=profiles,station_options=zones,journeys=journeys,next_tasks=tasks,
        actual_complete_force_map_available=force_map_supported,physical_journey_completed=False,
        installed_cost_USD=None,whole_life_cost_USD=None,cost_coverage=dict(vehicle=False,civil=False,station=False,energy=False,maintenance=False),
        price_unknown_is_zero=False,rank_scope='Diagnostic priority and counted stock only; no economic optimum or integrated feasibility claimed')]
    constraints=[dict(id='body-motor-brake-civil-identities',state='pass'),dict(id='position-dependent-full-journey-force-map',state='unknown'),
        dict(id='120s-safe-headway-and-real-dwell',state='unknown'),dict(id='complete-installed-stock-and-cost',state='unknown')]
    return dict(numerical_status='converged',screen_status='unknown',
        metrics=dict(research_penalty=penalty,accounted_vehicle_mass_kg=car['mass']['accounted_tare_kg_per_car'],bare_primary_mass_kg_per_m=primary),
        constraints=constraints,diagnostics=diagnostics)
