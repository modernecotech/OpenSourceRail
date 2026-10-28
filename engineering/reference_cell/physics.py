"""Same-candidate reduced electrothermal/vehicle/brake/auxiliary co-simulation.

Production input goes through the existing authenticated operating-map inlet and
additional exact model/fault replay. Test fixtures use a separate entry point.
No installed force map, protected headway or physical release is manufactured.
"""
from copy import deepcopy
from math import exp, isfinite, sqrt
from pathlib import Path
import re
from engineering.station_rail import ROOT, braking
from engineering.station_rail.common import identity,digest
from engineering.design_search import system_motion as retained
from engineering.railway_completion import operating, motion, evidence, FLAGS

PRODUCER='engineering/reference_cell/physics.py'
MODEL_SCOPES={'brake-thermal-fade':'T06','auxiliary-energy':'T01','wheel-load-transfer':'T07','protection-and-fault-control':'T07'}


def sources(root=ROOT):
    return {name:digest(Path(root)/name) for name in (PRODUCER,operating.__name__.replace('.','/')+'.py',
        motion.PRODUCER,retained.PRODUCER,'engineering/station_rail/braking.py')}


def scenarios(bundle):
    """One physical route/formation, three loadings and explicit environment/fault cases."""
    result=[]
    for loading in ('empty','normal','crowd'):
        definitions=[('nominal',{},dict(kind='none',at_s=None)),
            ('grade-wind',dict(grade_up_fraction=.02,headwind_m_s=10.),dict(kind='none',at_s=None)),
            ('hot',dict(ambient_C=45.),dict(kind='none',at_s=None)),
            ('cold',dict(ambient_C=5.),dict(kind='none',at_s=None)),
            ('bank-failure',{},dict(kind='bank-failure',at_s=20.,bank_index=1)),
            ('power-interruption',{},dict(kind='power-interruption',at_s=20.)),
            ('emergency-braking',{},dict(kind='emergency-braking',at_s=30.)),
            ('low-adhesion',dict(rail_adhesion=.025),dict(kind='none',at_s=None)),
            ('disabled-rescue',{},dict(kind='disabled-rescue',at_s=30.))]
        for name,changes,fault in definitions:
            case=retained.scenario(bundle,dict(load=loading,**changes,fault=fault))
            result.append(dict(name=loading+'/'+name,candidate_id=bundle['candidate_id'],scenario=case))
    return result


def _num(v,name,minimum=None):
    if type(v) not in (int,float) or not isfinite(v) or minimum is not None and v<minimum:
        raise ValueError('Finite bounded '+name+' required')
    return float(v)


def _thermal(node):
    if set(node)!={'capacity_J_K','heat_rejection_W_K','initial_C','ambient_C','maximum_C'}:
        raise ValueError('Exact coupled RC thermal schema required')
    for key in node:_num(node[key],key,0. if key in ('capacity_J_K','heat_rejection_W_K') else None)
    if node['capacity_J_K']<=0 or node['maximum_C']<node['initial_C']:
        raise ValueError('Positive heat capacity and initial thermal margin required')


def model_payload_id(models):
    return identity({k:v for k,v in models.items() if k not in ('model_id','supporting_record_ids')})

def validate_models(bundle,models):
    fields={'schema','candidate_id','bundle_definition_id','brake_definition_id','brake_thermal','pad_fade',
        'auxiliary','reactions','protection','launch_hold','supporting_record_ids','model_id'}
    if not isinstance(models,dict) or set(models)!=fields or models['schema']!='osr-reference-cell-coupling-models/1':
        raise ValueError('Exact candidate-bound coupled models required')
    if models['model_id']!=model_payload_id(models):
        raise ValueError('Coupled model content identity differs')
    bindings=dict(candidate_id=bundle['candidate_id'],bundle_definition_id=bundle.get('definition_id'),
        brake_definition_id=bundle.get('brake_definition',{}).get('brake_definition_id'))
    if any(models[k]!=v for k,v in bindings.items()):raise ValueError('Coupled models use another candidate/installed brake definition')
    refs=models['supporting_record_ids']
    if not isinstance(refs,dict) or set(refs)-set(MODEL_SCOPES) or any(re.fullmatch('[0-9a-f]{64}',str(v)) is None for v in refs.values()):
        raise ValueError('Explicit scoped coupled-model evidence identities required')
    _thermal(models['brake_thermal']);aux=models['auxiliary']
    if set(aux)!={'service_load_W','HVAC_W','usable_energy_J','initial_energy_J','minimum_essential_energy_J','heat_fraction','thermal'}:
        raise ValueError('Explicit auxiliary loads, usable service energy and battery heat required')
    for k in set(aux)-{'thermal'}:_num(aux[k],k,0.)
    if not 0<=aux['minimum_essential_energy_J']<=aux['initial_energy_J']<=aux['usable_energy_J'] or aux['heat_fraction']>=1:
        raise ValueError('Auxiliary energy bounds differ; no traction energy is introduced')
    _thermal(aux['thermal']);fade=models['pad_fade']
    if not isinstance(fade,list) or len(fade)<2 or any(set(r)!={'temperature_C','pad_mu'} for r in fade):
        raise ValueError('Explicit temperature-dependent brake friction curve required')
    for row in fade:_num(row['temperature_C'],'fade temperature');_num(row['pad_mu'],'pad friction',0.)
    if any(b['temperature_C']<=a['temperature_C'] for a,b in zip(fade,fade[1:])):
        raise ValueError('Ordered fade curve required')
    bt=models['brake_thermal']
    if fade[0]['temperature_C']>bt['initial_C'] or fade[-1]['temperature_C']<bt['maximum_C']:
        raise ValueError('Fade curve must cover the whole brake thermal envelope')
    reaction=models['reactions']
    if set(reaction)!={'bogie_centres_from_rear_m','CG_from_rear_m','CG_height_m','axles_per_bogie'}:
        raise ValueError('Explicit support/CG load-transfer model required')
    centres=reaction['bogie_centres_from_rear_m']
    if not isinstance(centres,list) or len(centres)!=2 or not 0<=centres[0]<reaction['CG_from_rear_m']<centres[1]<=bundle['car_length_m'] or reaction['axles_per_bogie']!=2:
        raise ValueError('Two passive two-axle bogies must bracket the declared CG')
    for k in ('CG_from_rear_m','CG_height_m'):_num(reaction[k],k,0.)
    protection=models['protection']
    if set(protection)!={'response_s','guaranteed_deceleration_m_s2','position_uncertainty_m','blocks_m','minimum_separation_m'}:
        raise ValueError('Explicit protection limits/blocks required')
    for k in set(protection)-{'blocks_m'}:_num(protection[k],k,0.)
    if protection['guaranteed_deceleration_m_s2']<=0:raise ValueError('A supported braking floor is necessary for a protection envelope')
    blocks=protection['blocks_m']
    if not isinstance(blocks,list) or any(not isinstance(b,list) or len(b)!=2 or not 0<=b[0]<b[1] for b in blocks):
        raise ValueError('Ordered bounded physical block intervals required')
    if any(b[0]<a[1] for a,b in zip(blocks,blocks[1:])):raise ValueError('Disjoint ordered protected blocks required')
    if set(models['launch_hold'])!={'declared','maximum_s','maximum_restraint_N_train'} or type(models['launch_hold']['declared']) is not bool:
        raise ValueError('Initial brake-hold controller must be an explicit model')
    _num(models['launch_hold']['maximum_s'],'maximum launch hold',0.)
    _num(models['launch_hold']['maximum_restraint_N_train'],'maximum hold restraint',0.)
    if models['launch_hold']['maximum_s']>30:raise ValueError('Bounded launch-hold model required')
    return deepcopy(models)


def _fault(case):
    fault=case.get('fault',dict(kind='none',at_s=None))
    kind=fault.get('kind')
    if kind not in ('none','bank-failure','power-interruption','emergency-braking','disabled-rescue'):
        raise ValueError('Explicit supported fault family required')
    if kind!='none':_num(fault.get('at_s'),'fault time',0.)
    if kind=='bank-failure' and (type(fault.get('bank_index')) is not int or not 0<=fault['bank_index']<5):
        raise ValueError('Explicit bank identity required; failed-bank force cannot be divided from a nominal map')
    return fault


def _model_admission(bundle,models,case,force_map,assessments,artifact_verifier,current):
    if models is None:return ['Missing coupled brake/fade, auxiliary, reaction and protection models']
    validate_models(bundle,models);registry={a['record_id']:a for a in assessments if a.get('authenticated') is True}
    reasons=[]
    for scope,protocol in MODEL_SCOPES.items():
        record_id=models['supporting_record_ids'].get(scope);a=registry.get(record_id)
        if a is None or a.get('protocol_id')!=protocol:
            reasons.append('Missing authenticated coupled model record: '+scope);continue
        r=a['record'];d=r.get('data',{});request=d.get('artifact_request',{})
        if (r.get('schema')!='osr-wheel-operating-evidence/1' or a.get('candidate_id')!=bundle['candidate_id']
            or any(r.get(k)!=v for k,v in evidence.binding(bundle).items())
            or r.get('record_id')!=identity({k:v for k,v in r.items() if k!='record_id'})
            or r.get('record_id')!=record_id or d.get('scope')!=scope or d.get('model_id')!=models['model_id']
            or d.get('scenario_id')!=case['scenario_id'] or not request.get('source_sha256')
            or any(current.get(k)!=v for k,v in request.get('source_sha256',{}).items())
            or request.get('candidate_id')!=bundle['candidate_id'] or request.get('scope')!=scope
            or request.get('model_id')!=models['model_id'] or request.get('scenario_id')!=case['scenario_id']
            or re.fullmatch('[0-9a-f]{64}',str(d.get('output_evaluation_id'))) is None
            or not request.get('tool_identity') or not request.get('numerical_request')):
            reasons.append('Coupled model record/source/request differs: '+scope);continue
        if artifact_verifier is None:
            reasons.append('Independent coupled-model replay backend missing: '+scope);continue
        replay=artifact_verifier(deepcopy(r),deepcopy(bundle),deepcopy(case),deepcopy(force_map))
        expected=dict(verified=True,record_id=record_id,scope=scope,tool_request_id=identity(request),
            source_sha256=request['source_sha256'],tool_identity=request['tool_identity'],output_evaluation_id=d.get('output_evaluation_id'))
        if not isinstance(replay,dict) or any(replay.get(k)!=v for k,v in expected.items()):
            reasons.append('Independent coupled-model replay differs: '+scope)
    return reasons


def _rc(T,power,dt,node):
    C=node['capacity_J_K'];H=node['heat_rejection_W_K']
    return T+power*dt/C if H==0 else node['ambient_C']+(T-node['ambient_C'])*exp(-H*dt/C)+power/H*(1-exp(-H*dt/C))


def _pad_mu(T,curve):
    if not curve[0]['temperature_C']<=T<=curve[-1]['temperature_C']:raise ValueError('Brake temperature outside supported fade curve')
    for a,b in zip(curve,curve[1:]):
        if a['temperature_C']<=T<=b['temperature_C']:
            w=(T-a['temperature_C'])/(b['temperature_C']-a['temperature_C']);return (1-w)*a['pad_mu']+w*b['pad_mu']
    return curve[-1]['pad_mu']


def _run(bundle,force_maps,case,models,gate):
    """Explicit midpoint force/current coupling with event bounds and RC energy."""
    retained._bundle(bundle);models=validate_models(bundle,models);fault=_fault(case)
    m=force_maps['nominal'];motion._gate(bundle,m,case,gate)
    if 'ambient_C' in case and any(node['ambient_C']!=case['ambient_C'] for node in (models['brake_thermal'],models['auxiliary']['thermal'],m['thermal_model'])):
        raise ValueError('Coupled models do not cover the explicit ambient environment')
    mass=retained._mass(bundle,case['load']);cars=bundle['cars'];effective=cars*(mass+bundle['rotating_equivalent_kg_per_car'])
    spec=retained._brake_definition(bundle)
    if spec is None:raise ValueError('Independent candidate-bound brake plant required')
    x=v=t=I=0.;I=case['initial_current_A'];T=m['thermal_model']['initial_C'];TB=models['brake_thermal']['initial_C']
    aux=models['auxiliary'];TA=aux['thermal']['initial_C'];E=aux['initial_energy_J'];length=cars*bundle['car_length_m']+(cars-1)*bundle['coupling_gap_m']
    electrical=loss=mechanical=drag=gravity_work=brake_heat=aux_used=aux_delivered=aux_heat=motor_rejected=brake_rejected=aux_rejected=0.;trace=[];brake_since=None;state='time-budget';reason=None;peak_axle=0.
    blocks=[dict(interval_m=b,front_entry_s=None,rear_clear_s=None) for b in models['protection']['blocks_m']]
    for step in range(12000):
        failed=fault['kind']!='none' and t>=fault['at_s']-1e-10
        name=fault['kind'] if failed and fault['kind'] in ('bank-failure','power-interruption') else 'nominal'
        active_map=force_maps[name];limits=active_map['electrical_limits'];thermal=active_map['thermal_model']
        emergency=failed and fault['kind'] in ('emergency-braking','disabled-rescue') or E<=aux['minimum_essential_energy_J']
        braking_now=emergency or case['brake_start_m'] is not None and x>=case['brake_start_m']-1e-8
        if braking_now and brake_since is None:brake_since=t
        active=any(a-1e-9<=x<b-1e-9 for a,b in case['powered_windows'])
        command=case['current_command_A'] if active and not braking_now and v<case['speed_cap_m_s'] else 0.
        h=min(case['dt_s'],case['maximum_time_s']-t)
        events=[e for pair in case['powered_windows'] for e in pair if e>x+1e-8]+[case['distance_m']]
        if case['brake_start_m'] is not None and case['brake_start_m']>x+1e-8:events.append(case['brake_start_m'])
        edge=min(events)
        if fault['kind']!='none' and not failed and t<fault['at_s']:h=min(h,fault['at_s']-t)
        if h<=1e-10:break
        upper=max(0.,max(r['thrust_N_train'] for r in active_map['samples']))/effective+max(0.,-cars*mass*braking.G*case['grade_up_fraction'])/effective
        if v or upper:
            denominator=v+sqrt(max(0.,v*v+2*upper*max(0.,edge-x)))
            if denominator:h=min(h,2*max(0.,edge-x)/denominator)
        if h<=1e-10:state='event-resolution-limit';reason='Cannot resolve route/window event';break
        acceleration=0.;sample=None;held=False
        try:
            for event_iteration in range(20):
                newI=I+max(-limits['current_slew_A_s']*h,min(limits['current_slew_A_s']*h,command-I))
                if abs(newI)>limits['maximum_current_A']+1e-8:raise ValueError('Admitted current envelope exceeded')
                for iteration in range(12):
                    mv=max(0.,v+acceleration*h/2);mx=max(x,x+v*h/2+acceleration*h*h/8)
                    sample=retained.sample_map(active_map,position_m=mx,speed_m_s=mv,current_A=(I+newI)/2,temperature_C=T) if active else {f:0. for f in retained.FIELDS}
                    resistance=cars*(mass*braking.G*case['rolling_coefficient']+case['bearing_N_per_car']+case['aero_N_s2_m2_per_car']*(mv+case['headwind_m_s'])**2)
                    gravity=-cars*mass*braking.G*case['grade_up_fraction']/sqrt(1+case['grade_up_fraction']**2)
                    bf=braking.force_state(spec,mass,mv,(t-brake_since+h/2) if braking_now else 0.,
                        pressure_Pa=None if braking_now else 0.,pad_mu=_pad_mu(TB,models['pad_fade']),
                        grade_down_fraction=-case['grade_up_fraction'],rail_adhesion=case['rail_adhesion'],available_discs=case['available_discs'],wayside_force_N=(sample['thrust_N_train']-resistance)/cars)
                    if not bf['valid']:raise ValueError(bf['reason'])
                    Q=cars*bf['torque_equivalent_brake_force_N_per_car'];a=(sample['thrust_N_train']-resistance+gravity-Q)/effective
                    held=v==0 and a<=0 and not braking_now and models['launch_hold']['declared'] and t<models['launch_hold']['maximum_s']
                    if held:
                        restraint=abs(sample['thrust_N_train']-resistance+gravity)
                        if restraint>min(models['launch_hold']['maximum_restraint_N_train'],cars*mass*braking.G*case['rail_adhesion']):raise ValueError('Declared launch hold exceeds its force/adhesion capacity')
                        a=0.
                    if abs(a-acceleration)<1e-10:break
                    acceleration=a
                else:raise ValueError('Coupled force/current midpoint failed to converge')
                newv=v+a*h
                if v==0 and a<=0 and not held:state='stalled';reason='Insufficient available force with no remaining supported hold';break
                if newv<0 and a<0:
                    shorter=v/-a
                    if shorter<h-1e-10:h=shorter;continue
                dx=(v+max(0.,newv))*h/2
                if x+dx>edge+1e-8 and dx>0:
                    target=edge-x;denom=v+sqrt(max(0.,v*v+2*a*target));shorter=2*target/denom if denom>0 else h
                    if shorter<h-1e-10:h=shorter;continue
                break
            else:raise ValueError('Coupled route/stop event failed to converge')
            if state=='stalled':break
            newv=max(0.,v+a*h);dx=(v+newv)*h/2
            if abs(x+dx-edge)<1e-8:dx=edge-x
            if newv>case['speed_cap_m_s']+1e-7:raise ValueError('Declared current controller cannot enforce the speed cap')
            if not 0<=sample['voltage_V']<=limits['maximum_voltage_V']+1e-9:raise ValueError('Admitted converter voltage magnitude exceeded')
            power_residual=sample['electrical_input_W_train']-sample['thrust_N_train']*(v+newv)/2-sample['loss_W_train']
            if abs(power_residual)>1e-3*max(1.,abs(sample['electrical_input_W_train'])):raise ValueError('Interpolated electrical/force/heat balance differs')
            motor_node=dict(capacity_J_K=thermal['capacity_J_K'],heat_rejection_W_K=thermal['heat_rejection_W_K'],ambient_C=thermal['ambient_C'])
            newT=_rc(T,sample['loss_W_train'],h,motor_node);newTB=_rc(TB,Q*(v+newv)/2,h,models['brake_thermal'])
            Pload=aux['service_load_W']+aux['HVAC_W'];Paux=Pload/(1-aux['heat_fraction']);Pheat=Paux-Pload;newE=E-Paux*h;newTA=_rc(TA,Pheat,h,aux['thermal'])
            if newE<0:raise ValueError('Usable essential-service battery energy exhausted')
            if newT>thermal['maximum_C'] or newTB>models['brake_thermal']['maximum_C'] or newTA>aux['thermal']['maximum_C']:
                raise ValueError('Coupled thermal envelope exceeded')
            support=models['reactions'];rear,front=support['bogie_centres_from_rear_m'];N=mass*braking.G/sqrt(1+case['grade_up_fraction']**2)
            frontN=N*(support['CG_from_rear_m']-rear)/(front-rear)-mass*a*support['CG_height_m']/(front-rear);rearN=N-frontN
            if min(frontN,rearN)<0:raise ValueError('Declared longitudinal support model predicts wheel unloading')
            axle=[rearN/2,rearN/2,frontN/2,frontN/2]*cars;peak_axle=max(peak_axle,max(axle))
            motor_rejected+=sample['loss_W_train']*h-thermal['capacity_J_K']*(newT-T);brake_rejected+=Q*dx-models['brake_thermal']['capacity_J_K']*(newTB-TB);aux_rejected+=Pheat*h-aux['thermal']['capacity_J_K']*(newTA-TA);aux_delivered+=Pload*h;aux_heat+=Pheat*h
            electrical+=sample['electrical_input_W_train']*h;loss+=sample['loss_W_train']*h;mechanical+=sample['thrust_N_train']*dx;drag+=resistance*dx;gravity_work+=gravity*dx;brake_heat+=Q*dx;aux_used+=Paux*h
            x+=dx;t+=h;v=newv;I=newI;T=newT;TB=newTB;TA=newTA;E=newE
            p=models['protection'];stop=v*p['response_s']+v*v/(2*p['guaranteed_deceleration_m_s2'])+p['position_uncertainty_m']
            for b in blocks:
                if b['front_entry_s'] is None and x>=b['interval_m'][0]:b['front_entry_s']=t
                if b['rear_clear_s'] is None and x-length>=b['interval_m'][1]:b['rear_clear_s']=t
            trace.append(dict(time_s=t,position_m=x,speed_m_s=v,acceleration_m_s2=a,current_A=I,motor_temperature_C=T,
                brake_temperature_C=TB,auxiliary_temperature_C=TA,auxiliary_energy_J=E,thrust_N_train=sample['thrust_N_train'],
                electrical_input_W_train=sample['electrical_input_W_train'],loss_W_train=sample['loss_W_train'],brake_force_N_train=Q,
                axle_normal_reactions_N=axle,protection_stopping_envelope_m=stop,launch_hold_active=held,launch_hold_restraint_N_train=(resistance-gravity-sample['thrust_N_train']) if held else 0.,fault_active=failed))
            if x>=case['distance_m']-1e-8:state='destination-boundary';break
            if v<=1e-8 and brake_since is not None:state='stopped';break
        except ValueError as error:state='outside-model-domain';reason=str(error);break
    test=gate['test_only'];arrival=abs(x-case['distance_m'])<=case['berth_tolerance_m'] and v<=1e-7
    result=dict(schema='osr-reference-cell-coupled-journey/1',candidate_id=bundle['candidate_id'],scenario=case,model_id=models['model_id'],
        execution='completed-method-test' if test else 'completed-reduced-coupled-model',state=state,reason=reason,test_only=test,model_definition=deepcopy(models),
        final_position_m=x,final_speed_m_s=v,elapsed_s=t,trace=trace,
        numerical_arrival_predicted=bool(arrival and not test),method_only_arrival=bool(arrival and test),available_operating_map_id=None if test else m['evaluation_id'],
        electrical_energy_J=electrical,motor_heat_J=loss,mechanical_propulsion_work_J=mechanical,friction_brake_heat_J=brake_heat,
        auxiliary_energy_used_J=aux_used,auxiliary_load_energy_J=aux_delivered,auxiliary_internal_heat_J=aux_heat,auxiliary_energy_residual_J=aux['initial_energy_J']-E-aux_used,
        auxiliary_delivery_residual_J=aux_used-aux_delivered-aux_heat,motor_heat_rejected_J=motor_rejected,brake_heat_rejected_J=brake_rejected,auxiliary_heat_rejected_J=aux_rejected,
        final_motor_temperature_C=T,final_brake_temperature_C=TB,final_auxiliary_temperature_C=TA,
        mechanical_energy_residual_J=mechanical+gravity_work-drag-brake_heat-.5*effective*v*v,
        electrical_work_residual_J=electrical-loss-mechanical,
        peak_axle_normal_reaction_N=peak_axle,normal_reaction_scope='Declared equal-car two-bogie longitudinal CG/pitch model; lateral/wheel contact/flexible-body response unqualified',
        block_occupancy=blocks,protected_service_qualified=False,qualified_headway_s=None,
        rescue_required=bool(fault['kind']=='disabled-rescue' and state=='stopped'),rescue_execution='not-run-no-tow-model' if fault['kind']=='disabled-rescue' else 'not-requested',
        source_sha256=sources(),scope='Coupled sampled-force/current, motor RC, fade-sensitive brake, service battery, support reactions and explicit faults; no physical/HIL/GoA4 release',**FLAGS)
    result['evaluation_id']=identity(result);return result


def evaluate(bundle,force_map=None,*,models=None,scenario_overrides=None,fault_maps=None,assessments=(),artifact_verifier=None,current_source_sha256=None):
    retained._bundle(bundle)
    case=retained.scenario(bundle,scenario_overrides);fault=_fault(case)
    current=current_source_sha256 or dict(bundle.get('source_sha256',{}),**sources())
    gate=operating.admit(bundle,force_map,case,assessments=assessments,artifact_verifier=artifact_verifier,current_source_sha256=current)
    reasons=list(gate['reasons'])+_model_admission(bundle,models,case,force_map,assessments,artifact_verifier,current)
    maps={'nominal':force_map}
    if fault['kind'] in ('bank-failure','power-interruption'):
        failed=(fault_maps or {}).get(fault['kind'])
        if failed is None:reasons.append('Missing separately validated fault-state map; nominal train force is never scaled')
        else:
            fg=operating.admit(bundle,failed,case,assessments=assessments,artifact_verifier=artifact_verifier,current_source_sha256=current)
            if failed.get('fault_state')!=fault:reasons.append('Fault map must bind the exact failed bank/time/interface')
            if force_map is not None and failed.get('thermal_model')!=force_map.get('thermal_model'):reasons.append('Fault map changes the installed thermal inventory/state model')
            reasons+=fg['reasons'];maps[fault['kind']]=failed
    if reasons:
        value=dict(schema='osr-reference-cell-coupled-journey/1',candidate_id=bundle['candidate_id'],scenario=case,
            execution='not-run',map_admission=gate,reasons=reasons,numerical_arrival_predicted=False,
            available_operating_map_id=None,qualified_headway_s=None,protected_service_qualified=False,**FLAGS)
        value['evaluation_id']=identity(value);return value
    return _run(bundle,maps,case,models,gate)


def method_test(bundle,force_map,models,*,scenario_overrides=None,fault_maps=None):
    """Explicit synthetic numerical control; never entered by production evaluate."""
    case=retained.scenario(bundle,scenario_overrides);fault=_fault(case)
    if force_map.get('evidence_kind')!='synthetic-method-test':raise ValueError('Method entry point requires synthetic fixture labelling')
    gate0=retained.admit_map(bundle,force_map,case,allow_synthetic=True)
    if not gate0['admitted']:raise ValueError('Synthetic map domain differs: '+str(gate0['reasons']))
    maps={'nominal':force_map}
    if fault['kind'] in ('bank-failure','power-interruption'):
        failed=(fault_maps or {}).get(fault['kind'])
        if failed is None or failed.get('evidence_kind')!='synthetic-method-test' or failed.get('fault_state')!=fault:
            raise ValueError('Separate exact synthetic fault-state map required; no nominal-force scaling')
        if not retained.admit_map(bundle,failed,case,allow_synthetic=True)['admitted']:raise ValueError('Fault map domain differs')
        if failed['thermal_model']!=force_map['thermal_model']:raise ValueError('Fault map changes installed thermal inventory')
        maps[fault['kind']]=failed
    gate=dict(schema='osr-wheel-operating-admission/1',admitted=True,evidence_ready=True,test_only=True,
        candidate_id=bundle['candidate_id'],bundle_definition_id=bundle.get('definition_id'),motor_component_id=bundle['propulsion_component_id'],
        scenario_id=case['scenario_id'],map_evaluation_id=force_map['evaluation_id'],reasons=[],**FLAGS)
    gate['admission_id']=identity(gate)
    return _run(bundle,maps,case,models,gate)


FMI_PORTS={'vehicle.position':('Real','m','output'),'vehicle.speed':('Real','m/s','output'),
    'motor.thrust':('Real','N','output'),'motor.current':('Real','A','input'),'motor.temperature':('Real','K','output'),
    'brake.force':('Real','N','output'),'brake.command':('Real','1','input')}


def fmi_manifest(bundle,manifest):
    """Check exchange identity/units without executing untrusted native FMU code."""
    if manifest.get('schema')!='osr-reference-cell-FMI-exchange/1' or manifest.get('candidate_id')!=bundle['candidate_id']:
        raise ValueError('Exact candidate-bound FMI manifest required')
    if manifest.get('manifest_id')!=identity({k:v for k,v in manifest.items() if k!='manifest_id'}):raise ValueError('FMI manifest content differs')
    ports=manifest.get('ports',[]);actual={r['name']:(r['type'],r['unit'],r['causality']) for r in ports}
    if len(actual)!=len(ports) or actual!=FMI_PORTS:raise ValueError('Typed FMI port/quantity/causality contract differs')
    models=manifest.get('models',[])
    if not models or any(not isinstance(r.get('sha256'),str) or len(r['sha256'])!=64 or any(c not in '0123456789abcdef' for c in r['sha256']) or not r.get('source_identity') or not r.get('model_identifier') for r in models):
        raise ValueError('Content/source-bound actual model artifacts required')
    return dict(interface_valid=True,execution='not-run',reason='Actual authenticated FMU bytes, supported co-simulation backend and independent correlation are required',
        candidate_id=bundle['candidate_id'],manifest_id=manifest['manifest_id'],models_verified=False,physical_co_simulation_complete=False,**FLAGS)
