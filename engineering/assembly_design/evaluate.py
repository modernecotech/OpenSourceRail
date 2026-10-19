"""Independent scoped structural screens and executable cassette interface trials."""
import itertools
import math

from engineering.twin_workflow import core
from engineering.continuous_design import beam_confirmation,civil_kit
from engineering.integration_programme import joints
from . import baseline


def overhang_beam(length,supports,ei,uniform):
    """Integrated moment field, independent of the Hermite stiffness assembly."""
    a,b=supports
    if not all(math.isfinite(v) for v in (length,a,b,ei,uniform)) or not 0<=a<b<=length or ei<=0 or uniform<0:raise ValueError('finite stable beam hypothesis required')
    force=uniform*length;r2=force*(length/2-a)/(b-a);r1=force-r2
    def base(x):return uniform*x**4/(24*ei)-r1*max(x-a,0)**3/(6*ei)-r2*max(x-b,0)**3/(6*ei)
    slope=-(base(b)-base(a))/(b-a);offset=-base(a)-slope*a
    xs=[length*i/2000 for i in range(2001)]
    def moment(x):return uniform*x*x/2-r1*max(x-a,0)-r2*max(x-b,0)
    return dict(maximum_deflection_m=max(abs(base(x)+slope*x+offset) for x in xs),
        maximum_moment_nm=max(abs(moment(x)) for x in xs),reactions_n=[r1,r2],scope='Uniform equivalent beam; ideal point supports and composite rail sharing, not local joints or shells')


def control_source(variant):
    if variant not in {'branch','bitmask'}:raise ValueError('unknown software variant')
    healthy="all((i['locked'],i['earth_ok'],i['fresh'],i['supply_ok']))" if variant=='branch' else "sum(int(i[n])<<b for b,n in enumerate(('locked','earth_ok','fresh','supply_ok')))==15"
    return "def step(tripped, i):\n    healthy="+healthy+"\n    tripped=(not healthy) or (tripped and not (i['reset'] and i['stopped']))\n    return {'tripped':tripped,'enabled':bool(i['request'] and healthy and not tripped)}\n"


def control_trial(variant='branch',source=None):
    namespace={};exec(source or control_source(variant),namespace);step=namespace['step'];cases=[]
    names=('locked','earth_ok','fresh','supply_ok','reset','stopped','request')
    for old in (False,True):
        for values in itertools.product((False,True),repeat=len(names)):
            inputs=dict(zip(names,values))
            # Independent explicit transition oracle, not an imported generator.
            if not inputs['locked'] or not inputs['earth_ok'] or not inputs['fresh'] or not inputs['supply_ok']:fault=True
            elif old:
                if inputs['reset'] and inputs['stopped']:fault=False
                else:fault=True
            else:fault=False
            expected=dict(tripped=fault,enabled=bool(inputs['request'] and not fault))
            actual=step(old,inputs);cases.append(dict(before_tripped=old,input=inputs,expected=expected,actual=actual,passed=actual==expected))
    state=False;trace=[]
    for override in ({},{'locked':False},{},{'reset':True,'stopped':False},{'reset':True,'stopped':True},{}):
        inputs=dict(locked=True,earth_ok=True,fresh=True,supply_ok=True,reset=False,stopped=True,request=True);inputs.update(override)
        output=step(state,inputs);state=output['tripped'];trace.append(dict(input=inputs,output=output))
    expected=[True,False,False,False,True,True]
    return dict(variant=variant,cases=cases,trace=trace,checks=dict(exhaustive_transition_oracle=all(c['passed'] for c in cases),
        disconnect_latch_moving_reset_and_stopped_recovery=[r['output']['enabled'] for r in trace]==expected),
        scope='Offline cassette permission latch and interlock fault propagation; no target timing, physical wiring or railway safety qualification',**core.FLAGS)


def evaluate(policy,candidate):
    if candidate.get('kind')=='structural-bay':
        from . import structural_bay
        return structural_bay.evaluate(policy,candidate)
    from . import models
    if core.digest(candidate)!=core.digest(models.build(policy,candidate['kind'],candidate['variables'])):raise ValueError('candidate differs from its controlled generator revision')
    kind=candidate['kind'];p=policy['pilots'][kind];a=p['assumptions'];f=baseline.facts(policy);v=candidate['variables'];contract=candidate['contract']
    mass=sum(part['properties']['mass_kg'] for part in contract['parts']);checks={};measurements={};cases=[]
    checks['qa_revision_coverage']=all(t['unit_revision']==candidate['revision'] for t in candidate['qa_plan'])
    checks['positive_mass_and_unique_parts']=mass>0 and len({p['id'] for p in contract['parts']})==len(contract['parts'])
    checks['mount_clearance_tolerance']=v['bolt_diameter_m']*.1>2*a['dimensional_tolerance_m']
    if kind=='service-cassette':
        width,height,t=candidate['metadata']['rail_section_m'];I=(width*height**3-(width-2*t)*(height-2*t)**3)/12;EI=2*f['steel.elastic_modulus']*I
        L=a['length_m'];supports=[(L-a['mount_span_m'])/2,(L+a['mount_span_m'])/2]
        for payload in a['payload_kg']:
            force=(mass+payload)*a['gravity_m_s2']*a['vertical_factor'];q=force/L
            analytical=overhang_beam(L,supports,EI,q);native=beam_confirmation.solve(L,supports,EI,uniform=q,divisions=32)
            stress=analytical['maximum_moment_nm']*(height/2)/(2*I)
            checks['beam-refinement-'+str(payload)]=abs(native['maximum_nodal_deflection_m']/analytical['maximum_deflection_m']-1)<.01
            checks['beam-equilibrium-'+str(payload)]=native['force_balance_relative_error']<1e-7
            checks['rail-stress-'+str(payload)]=stress<=355e6*a['steel_stress_fraction']
            checks['rail-deflection-'+str(payload)]=analytical['maximum_deflection_m']<=a['deflection_limit_m']
            cases.append(dict(id='payload-'+str(payload),payload_kg=payload,force_n=force,stress_pa=stress,analytical=analytical,numerical=native))
        payload=max(a['payload_kg']);total=mass+payload
        force=[total*a['gravity_m_s2']*a['longitudinal_factor'],total*a['gravity_m_s2']*a['lateral_factor'],total*a['gravity_m_s2']*a['vertical_factor']]
        load=force+[0.,force[0]*a['height_m']/2,force[1]*a['height_m']/2]
        joint=joints.assess(joints.bolt_group(candidate['metadata']['mount_positions_m'],v['bolt_diameter_m'],.069,f['steel.elastic_modulus']),load)
        checks['duct-packaging']=.04+v['duct_area_m2']/.2+.002<=a['height_m']
        velocity=a['duct_flow_m3_s']/v['duct_area_m2'];checks['duct-velocity-hypothesis']=velocity<=a['duct_velocity_limit_m_s']
        checks['netlist-conductor-coverage']=sum(p['id'].endswith('-conductor') for p in contract['parts'])==sum(n!='spare' for n in candidate['metadata']['netlist']['pins'].values())
        checks['connector-headline-current-only']=a['branch_current_a']<=f['connector.current_max']
        checks['connector-operating-temperature-only']=max(a['temperature_sensitivity_c'])<=f['connector.temperature'][1]
        software=control_trial();checks.update({'software/'+k:value for k,value in software['checks'].items()})
        measurements.update(beam_cases=cases,duct_velocity_m_s=velocity,
            offline_airflow_trace_m3_s=[a['duct_flow_m3_s'] if r['output']['enabled'] else 0 for r in software['trace']],
            controller_scope=software['scope'],unresolved_physical_geometry=['qualified clamp lining/grip','mating connector and termination bends','bond conductor routing and crimp','duct seals and inspection covers'])
    else:
        from . import reactions
        kit=civil_kit.build(civil_kit.defaults());deck_mass=sum(u['mass_kg'] for u in kit['units'] if u['category']=='deck')
        train=reactions.revisioned(dict(architecture=policy['architecture'],mass_cases_kg=f['train.mass_cases'],cars=a['train_cars'],
            car_length_m=f['train.car_length'],tracks=a['tracks'],span_m=a['span_m'],gravity_m_s2=a['gravity_m_s2'],
            permanent_factor=a['vertical_factor'],variable_factor=a['vertical_factor']))
        seat=reactions.revisioned(dict(candidate_revision=candidate['revision'],mass_kg=mass))
        reaction_envelope=reactions.envelope(kit,train,seat,expected_kit_revision=core.digest(kit),expected_train_revision=train['revision'])
        checks.update({'reaction-envelope/'+name:value for name,value in reaction_envelope['checks'].items()})
        checks.update({'mandatory-action/'+name:None for name in reaction_envelope['mandatory_action_holds']})
        for train_mass in f['train.mass_cases']:
            # One controlled kit/train/seat envelope supplies downstream demands;
            # no parallel deck-only force calculation is allowed here.
            combination=next(c for c in reaction_envelope['combinations'] if c['id']=='research-factored-'+str(train_mass))
            selected=max(combination['bearing_reactions'],key=lambda r:r['force_n'][2]);force=selected['force_n'][2]
            area=math.prod(a['plate_plan_m']);pressure=force/area;overhang=max((x-y)/2 for x,y in zip(a['plate_plan_m'],a['bearing_plan_m']))
            moment=pressure*overhang**2/2;stress=6*moment/v['plate_thickness_m']**2
            fy=next(y for upper,y in f['steel.yield_by_thickness'] if v['plate_thickness_m']<=upper)
            checks['plate-strip-stress-'+str(train_mass)]=stress<=fy*a['steel_stress_fraction']
            checks['concrete-pressure-hypothesis-'+str(train_mass)]=pressure<=a['concrete_pressure_limit_pa']
            cases.append(dict(id='train-mass-'+str(train_mass),train_mass_kg=train_mass,deck_mass_kg=deck_mass,
                reaction_envelope_revision=reaction_envelope['revision'],combination_id=combination['id'],critical_bearing_id=selected['bearing_id'],
                normal_force_n=force,pressure_pa=pressure,stress_pa=stress,yield_reference_pa=fy,
                scope='Uniform plate-overhang strips and uniform concrete bedding; contact, prying, local concrete and reinforcement remain unverified'))
        force=max(c['normal_force_n'] for c in cases)
        load=[force*a['horizontal_fraction'],0.,force*a['uplift_fraction'],0.,force*a['horizontal_fraction']*a['restraint_height_m'],0.]
        joint=joints.assess(joints.bolt_group(candidate['metadata']['mount_positions_m'],v['bolt_diameter_m'],.2+v['plate_thickness_m'],f['steel.elastic_modulus']),load)
        movement=a['thermal_coefficient_per_k']*a['span_m']*a['temperature_range_k']
        checks['longitudinal-thermal-movement-hypothesis']=movement<=a['movement_allowance_m']
        # Supplier performance is a mandatory unresolved applicability check,
        # rather than treating an unspecified rating as a pass.
        checks['bearing-continuous-temperature-applicability']=max(policy['pilots']['service-cassette']['assumptions']['temperature_sensitivity_c'])<=f['bearing.reference_temperature'][1] if v['bearing_family']=='elastomeric-reference' else None
        measurements.update(seat_load_cases=cases,compiler_kit_sha256=core.digest(kit),reaction_envelope=reaction_envelope,thermal_movement_m=movement,
            horizontal_and_uplift_scope='Legacy fraction-of-gravity elastic sensitivity only; mandatory braking/thermal/wind/seismic/uplift actions remain held in the shared envelope',
            combined_bearing_ratings_verified=False,unresolved_physical_geometry=['offered bearing internals','pier-cap reinforcement and anchor development','qualified lifting provisions'])
    As=next(value for key,value in f['bolts.stress_areas'].items() if float(key)==v['bolt_diameter_m'])
    equivalent=max(math.sqrt(max(0.,z)**2+3*(x*x+y*y))/As for x,y,z in joint['bolt_forces_n'])
    checks['bolt-elastic-demand-hypothesis']=equivalent<=a['bolt_equivalent_stress_limit_pa']
    measurements.update(joint=joint,bolt_stress_area_m2=As,peak_bolt_equivalent_stress_pa=equivalent,mass_kg=mass,
        mass_scope='Represented parts and explicit purchased allowances only; unrepresented services/coatings remain open',owned_part_count=sum(p['geometric_role']=='manufactured-solid' and p['procurement'] is None for p in contract['parts']))
    failures=[k for k,value in checks.items() if value is False];held=[k for k,value in checks.items() if value is None]
    return dict(schema='osr-assembly-screening/1',candidate_revision=candidate['revision'],kind=kind,checks=checks,
        failed_checks=failures,held_checks=held,screen_pass=not failures and not held,implemented_checks_pass=not failures,
        state='failed' if failures else 'hold' if held else 'screened-with-open-design-requirements',
        measurements=measurements,open_requirements=candidate['open_requirements'],
        digital_specification_complete=False,connection_resistance_qualified=False,
        scope='Only listed geometry, elastic, thermal-expansion and offline interface screens; no full component/system acceptance',**core.FLAGS)
