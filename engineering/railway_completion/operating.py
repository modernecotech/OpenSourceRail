"""Authenticated, independently replayed operating-map inlet and duty checks.

Neither a supported string nor a signed assertion replaces numerical replay.
The numerical verifier is trusted application configuration, never executable
code selected by imported files. The retained point-train solver is used only
after this stronger gate; it is not a hardware or protected-service release.
"""
from copy import deepcopy
from math import exp, expm1, isfinite
from itertools import product
import re

from engineering.station_rail.common import identity
from engineering.design_search import system_motion
from . import FLAGS
from . import evidence

REQUIRED={'independent_benchmarks':'T05','mesh_time_convergence':'T05','finite_overlap':'T05',
          'zero_force_outside_windows':'T05','current_circuit_control':'T05',
          'thermal_duty':'T06','normal_force_interface':'T05'}


def interface(bundle):
    return dict(candidate_id=bundle['candidate_id'],motor_component_id=bundle['propulsion_component_id'],
        brake_definition_id=bundle['brake_definition']['brake_definition_id'],
        wayside=deepcopy(bundle['architecture_case']['physical_definition']['wayside']),
        formation=dict(cars=bundle['cars'],car_length_m=bundle['car_length_m'],coupling_gap_m=bundle['coupling_gap_m']),
        secondary=deepcopy(bundle['motor_parameters']['physical']))


def payload_id(force_map):
    """Dataset identity excludes review links, avoiding cyclic evidence hashes."""
    return identity({k:v for k,v in force_map.items() if k not in
        ('evaluation_id','supporting_record_ids','review_record_id','validation')})


def _number(value,label,positive=False):
    if type(value) not in (int,float) or not isfinite(value) or positive and value<=0:
        raise ValueError('Finite '+label+' required')
    return float(value)


def periodic_duty(data):
    """Exact affine RC cycles, including the limiting periodic temperature."""
    headway=_number(data['headway_s'],'headway',True)
    if headway!=120.:
        raise ValueError('This duty comparison retains120s target headway')
    nodes=data['nodes']
    if not isinstance(nodes,list) or not nodes or len(nodes)>128:
        raise ValueError('Bounded independently identified thermal nodes required')
    ids=[n['id'] for n in nodes]
    if len(ids)!=len(set(ids)):
        raise ValueError('Unique thermal nodes required')
    outputs=[]
    for node in nodes:
        C=_number(node['mass_kg'],'thermal mass',True)*_number(node['specific_heat_J_kg_K'],'specific heat',True)
        R=_number(node['resistance_K_W'],'thermal resistance',True)
        ambient=_number(node['ambient_C'],'ambient')
        maximum=_number(node['maximum_C'],'supported temperature')
        phases=node['phases']
        if not phases or abs(sum(_number(p['duration_s'],'duty duration',True) for p in phases)-headway)>1e-8:
            raise ValueError('Thermal phases must cover exactly one headway')
        B=0.;A=1.
        for phase in phases:
            dt=phase['duration_s'];power=_number(phase['loss_W'],'loss')
            if power<0:
                raise ValueError('Physical heat cannot be negative or stabilization work')
            a=exp(-dt/(R*C));b=-expm1(-dt/(R*C))*power*R
            B=a*B+b;A*=a
        initial=B/(-expm1(-headway/(R*C)))
        T=initial;peak=initial;trace=[]
        for phase in phases:
            a=exp(-phase['duration_s']/(R*C))
            T=a*T+(1-a)*phase['loss_W']*R
            peak=max(peak,T);trace.append(ambient+T)
        outputs.append(dict(id=node['id'],periodic_initial_C=ambient+initial,
            periodic_peak_C=ambient+peak,phase_end_temperatures_C=trace,
            cycle_residual_K=T-initial,temperature_margin_K=maximum-ambient-peak,
            passes=ambient+peak<=maximum))
    return dict(nodes=outputs,passes=all(n['passes'] for n in outputs),
        scope='Declared component RC model and phase losses; requires authenticated material/cooling/loss/circuit records',**FLAGS)


def admit(bundle,force_map,case,*,assessments=(),artifact_verifier=None,current_source_sha256=None):
    if force_map is None:
        return dict(admitted=False,reasons=['Missing available force map'],evidence_ready=False,**FLAGS)
    m=force_map;reasons=[]
    if m.get('schema')!='osr-station-available-force-map/1' or m.get('evaluation_id')!=identity({k:v for k,v in m.items() if k!='evaluation_id'}):
        raise ValueError('Exact operating-map schema/content identity required')
    if m.get('evidence_kind')!='verified-numerical-operating-map':
        raise ValueError('Synthetic/catalogue/linear method data cannot enter the operating inlet')
    axes=m.get('axes',{})
    for name in system_motion.AXES:
        values=axes.get(name)
        if not isinstance(values,list) or not values or any(type(v) not in (int,float) or not isfinite(v) for v in values) or any(b<=a for a,b in zip(values,values[1:])):
            raise ValueError('Finite ordered force-map axes required')
    expected=set(product(*(axes[n] for n in system_motion.AXES)))
    if len(expected)>16384:
        raise ValueError('Force map exceeds bounded interpolation domain')
    samples=m.get('samples',[])
    actual=[tuple(s[n] for n in system_motion.AXES) for s in samples]
    if len(actual)!=len(expected) or set(actual)!=expected:
        raise ValueError('Complete disjoint Cartesian force samples required')
    boundaries={value for pair in case['powered_windows'] for value in pair}
    if not boundaries<=set(axes['position_m']):
        raise ValueError('Every powered-window boundary must be an explicit map position')
    exits={b for a,b in case['powered_windows'] if b<case['distance_m']}
    limits=m['electrical_limits']
    voltage=_number(limits['maximum_voltage_V'],'voltage magnitude limit',True)
    current=_number(limits['maximum_current_A'],'path current limit',True)
    for sample in samples:
        for name in system_motion.FIELDS:
            _number(sample[name],name)
        if not 0<=sample['voltage_V']<=voltage or abs(sample['current_A'])>current:
            raise ValueError('Sample exceeds nonnegative voltage-magnitude or current envelope')
        if sample['loss_W_train']<0:
            raise ValueError('Physical loss cannot be negative')
        residual=sample['electrical_input_W_train']-sample['thrust_N_train']*sample['speed_m_s']-sample['loss_W_train']
        if abs(residual)>1e-3*max(1.,abs(sample['electrical_input_W_train'])):
            raise ValueError('Map electrical/mechanical/loss identity differs')
        active=any(a<=sample['position_m']<=b for a,b in case['powered_windows']) and sample['position_m'] not in exits
        if not active and (sample['thrust_N_train']!=0 or sample['electrical_input_W_train']!=0 or sample['loss_W_train']!=0):
            raise ValueError('Unsupported off-window force/input/loss; model isolation and flux decay explicitly')
        if sample['current_A']==0 and sample['thrust_N_train']!=0:
            raise ValueError('This zero-flux-envelope map cannot supply force at zero current')
    envelope=m.get('operating_envelope',{})
    if (envelope.get('interface_state')!=interface(bundle)
            or envelope.get('history_model')!='validated-zero-flux-start-and-isolation-envelope'
            or not envelope.get('frequency_control_law') or not envelope.get('phase_registration')
            or envelope.get('gap_each_side_m')!=bundle['motor_parameters']['physical']['gap_each_side_m']):
        reasons.append('Explicit exact installed interface/frequency/phase/gap/history envelope missing')
    registry={a['record_id']:a for a in assessments if a.get('authenticated') is True}
    refs=m.get('supporting_record_ids',{})
    dataset_id=payload_id(m)
    if m.get('interface_state_id')!=identity(interface(bundle)) or m.get('review_record_id') not in registry:
        reasons.append('Exact reviewed interface/map record identity missing')
    replayed=[]
    for scope,protocol in REQUIRED.items():
        assessment=registry.get(refs.get(scope))
        if assessment is None or assessment['protocol_id']!=protocol:
            reasons.append('Missing authenticated scoped record: '+scope);continue
        record=assessment['record'];data=record.get('data',{})
        if (record.get('schema')!='osr-wheel-operating-evidence/1'
                or any(record.get(k)!=value for k,value in evidence.binding(bundle).items())
                or record.get('record_id')!=identity({k:v for k,v in record.items() if k!='record_id'})
                or record.get('record_id')!=assessment['record_id'] or assessment.get('candidate_id')!=bundle['candidate_id']
                or data.get('scope')!=scope or data.get('map_payload_id')!=dataset_id
                or data.get('interface_state_id')!=identity(interface(bundle))
                or data.get('scenario_id')!=case['scenario_id']):
            reasons.append('Supporting numerical record uses another map/interface/scenario: '+scope);continue
        if artifact_verifier is None:
            reasons.append('Independent artifact replay backend missing: '+scope);continue
        request=data.get('artifact_request',{})
        current=current_source_sha256 or bundle['source_sha256']
        if (request.get('scope')!=scope or request.get('candidate_id')!=bundle['candidate_id']
                or request.get('motor_component_id')!=bundle['propulsion_component_id']
                or request.get('map_payload_id')!=dataset_id or request.get('scenario_id')!=case['scenario_id']
                or not request.get('source_sha256') or not request.get('tool_identity') or not request.get('numerical_request')
                or any(current.get(name)!=sha for name,sha in request.get('source_sha256',{}).items())
                or not re.fullmatch('[0-9a-f]{64}',str(data.get('output_evaluation_id')))):
            reasons.append('Numerical artifact request/source/tool context differs: '+scope);continue
        replay=artifact_verifier(deepcopy(record),deepcopy(bundle),deepcopy(case),deepcopy(m))
        if (not isinstance(replay,dict) or replay.get('verified') is not True
                or replay.get('record_id')!=record['record_id'] or replay.get('scope')!=scope
                or replay.get('map_payload_id')!=dataset_id
                or replay.get('source_sha256')!=request['source_sha256']
                or replay.get('tool_request_id')!=identity(request)
                or replay.get('tool_identity')!=request['tool_identity']
                or replay.get('output_evaluation_id')!=data['output_evaluation_id']):
            reasons.append('Numerical artifact replay did not confirm exact scope: '+scope);continue
        if scope=='thermal_duty':
            duty=periodic_duty(data['duty'])
            expected_nodes=set(data.get('required_node_ids',[]))
            actual_nodes={n['id'] for n in duty['nodes']}
            installed=interface(bundle)['wayside'].get('converter_and_feeder_definition')
            declared=set() if not isinstance(installed,dict) else set(installed.get('thermal_node_ids',[]))
            converters=set() if not isinstance(installed,dict) else set(installed.get('converter_node_ids',[]))
            prefixes=[f'bank/{i}' for i in range(5)]+[f'secondary/{i}' for i in range(6)]
            if (not expected_nodes or actual_nodes!=expected_nodes or actual_nodes!=declared or not duty['passes']
                    or not converters or not converters<=actual_nodes
                    or any(not any(name==prefix or name.startswith(prefix+'/') for name in actual_nodes) for prefix in prefixes)):
                reasons.append('Complete supported per-component periodic thermal duty missing')
        replayed.append(replay)
    if not reasons:
        legacy=system_motion.admit_map(bundle,m,case,current_source_sha256=current_source_sha256)
        reasons.extend(legacy['reasons'])
    result=dict(schema='osr-wheel-operating-admission/1',admitted=not reasons,reasons=reasons,evidence_ready=not reasons,
        candidate_id=bundle['candidate_id'],bundle_definition_id=bundle['definition_id'],
        motor_component_id=bundle['propulsion_component_id'],scenario_id=case['scenario_id'],
        map_evaluation_id=m['evaluation_id'],test_only=False,
        interface_state_id=identity(interface(bundle)),replayed_evidence=replayed,
        scope='Authenticated and independently replayed reduced numerical map; not physical or protected-service acceptance',**FLAGS)
    result['admission_id']=identity(result)
    return result


def evaluate(bundle,force_map=None,*,scenario_overrides=None,assessments=(),artifact_verifier=None,current_source_sha256=None):
    case=system_motion.scenario(bundle,scenario_overrides)
    gate=admit(bundle,force_map,case,assessments=assessments,artifact_verifier=artifact_verifier,current_source_sha256=current_source_sha256)
    if gate['admitted']:
        from . import motion
        forward=motion.forward(bundle,force_map,case,admission=gate,current_source_sha256=current_source_sha256)
    else:
        forward=dict(execution='not-run',admission=gate,available_motor_map_id=None,predicted_stop_within_berth=False,**FLAGS)
    return dict(candidate_id=bundle['candidate_id'],scenario=case,map_admission=gate,
        forward_motion=forward,braking=system_motion.brake_screens(bundle,case),
        numerical_arrival_predicted=bool(gate['admitted'] and forward.get('predicted_stop_within_berth')),
        protected_service_qualified=False,**FLAGS)
