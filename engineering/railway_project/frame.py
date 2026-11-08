"""Compile signed station entry without moving a train or its authority.

The motion kernel uses nonnegative coordinates. A fixed affine frame can cover
an actual short stop on the preceding leg, provided the track, swept envelope
and continuous feed have explicitly declared coverage there. These declarations
are research inputs, not evidence of a built station or available power map.
This compiler executes no motion, changes no physical candidate and extends no
authority. Native dispatch must preserve the exported Case bytes and identity.
"""
from copy import deepcopy
from math import isfinite
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity
from engineering.station_pair import control_policy, native_bridge
from . import motion
from .civil import sealed, source_union
from .route import FLAGS

PRODUCER='engineering/railway_project/frame.py'
COVERAGE_SCHEMA='osr-project-continuous-reference-coverage/1'


def _interval(value, name):
    if (not isinstance(value,list) or len(value)!=2 or
        any(type(x) not in (int,float) or not isfinite(x) for x in value) or value[0]>value[1]):
        raise ValueError('Finite ordered reference interval required: '+name)
    return value


def _hash(value):
    return isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value)


def compile_frame(case,manifest,bundle,body,alignment,station,tracks,duty,envelope,feed,*,
                  origin_route_m,allowed_initial_route_interval_m,controller_v2=None,root=ROOT):
    """Return (Case, input manifest, native EntryFrame, FrameCaseBinding).

    envelope/feed are separately sealed coverage declarations with exact project,
    body, alignment, station, track, drive and directed-leg bindings. Their
    reference_interval_m describes where the *formation reference point* is
    supported, after any train-end/equipment reach is accounted for. A raw rail
    extent or platform length is not a swept-envelope declaration.
    """
    packets=(manifest,bundle,body,alignment,station,tracks,duty,envelope,feed)
    for packet in packets:sealed(packet)
    if (manifest.get('schema')!='osr-project-motion-input/1' or
        case.get('id')!=identity({k:v for k,v in case.items() if k!='id'}) or
        manifest.get('case_id')!=case['id'] or manifest.get('native_input_id')!=identity(case)):
        raise ValueError('Exact canonical unframed motion request required')
    if manifest.get('native_method_sha256')!=native_bridge.sources(root):
        raise ValueError('Motion source epoch changed; regenerate the motion input')
    p=bundle['physical_definition']
    components=(('body',body),('alignment',alignment),('station',station),('station_track',tracks))
    physical_keys={'body':'body_candidate_id','alignment':'alignment_candidate_id',
                   'station':'station_geometry_candidate_id','station_track':'station_track_geometry_candidate_id'}
    if (bundle.get('schema')!='osr-mapped-railway-project-bundle/1' or
        any(v['candidate_id']!=identity(v['physical_definition']) for v in (bundle,body,alignment,station,tracks)) or
        any(p.get(physical_keys[k])!=v['candidate_id'] or bundle.get(k+'_evaluation_id')!=v['evaluation_id'] for k,v in components) or
        case['candidate_id']!=bundle['candidate_id'] or manifest['candidate_id']!=bundle['candidate_id'] or
        manifest.get('bundle_evaluation_id')!=bundle['evaluation_id'] or
        manifest.get('body_evaluation_id')!=body['evaluation_id'] or
        manifest.get('alignment_evaluation_id')!=alignment['evaluation_id'] or
        manifest.get('drive_evaluation_id')!=duty['evaluation_id'] or
        duty['candidate_id']!=body['candidate_id'] or duty['body_evaluation_id']!=body['evaluation_id']):
        raise ValueError('Exact same-project geometry, mass and drive revision required')
    # Check inner ancestry as well as the outer bundle's links.
    if (station.get('schema')!='osr-project-station-interfaces/1' or
        tracks.get('schema')!='osr-station-track-spread-evaluation/1' or
        station['alignment_candidate_id']!=alignment['candidate_id'] or
        station['physical_definition']['alignment_candidate_id']!=alignment['candidate_id'] or
        station['alignment_evaluation_id']!=alignment['evaluation_id'] or
        station['body_candidate_id']!=body['candidate_id'] or station['body_evaluation_id']!=body['evaluation_id'] or
        tracks['alignment_candidate_id']!=alignment['candidate_id'] or
        tracks['station_candidate_id']!=station['candidate_id'] or
        tracks['physical_definition']['alignment_candidate_id']!=alignment['candidate_id'] or
        tracks['physical_definition']['station_geometry_candidate_id']!=station['candidate_id'] or
        tracks['alignment_evaluation_id']!=alignment['evaluation_id'] or tracks['station_evaluation_id']!=station['evaluation_id']):
        raise ValueError('Contradictory station-track ancestry')
    leg_index=manifest['leg_index'];direction=manifest['direction']
    if type(leg_index) is not int or not 0<=leg_index<len(alignment['legs']) or type(direction) is not int or direction not in (-1,1):
        raise ValueError('Known directed leg required')
    # A digest proves content integrity, not that the producer supplied these
    # bounds. Recompile the cheap definition from the exact declared scenario,
    # body, drive and policy before assigning transformed inputs a new identity.
    # This invokes no trajectory or native evaluator.
    expected_case,expected_manifest=motion.compile_case(bundle,body,alignment,duty,
        leg_index,manifest['scenario'],direction=direction,root=root)
    if case!=expected_case or manifest!=expected_manifest:
        raise ValueError('Unframed producer contract differs; source bounds and redundant identities cannot be resealed into admission')
    leg=alignment['legs'][leg_index];D=leg['distance_m']
    a,b=(leg['from_stop'],leg['to_stop']) if direction==1 else (leg['to_stop'],leg['from_stop'])
    if (manifest['from_stop']!=a or manifest['to_stop']!=b or case['distance_m']!=D or
        case.get('control',{}).get('end_of_authority_m')!=D or case.get('drive',{}).get('windows_m')!=[[0.,D]] or
        case['drive'].get('external_mass_kg')!=0 or case['drive'].get('external_resistance_n')!=0):
        raise ValueError('Unchanged physical leg, authority and continuous in-BOM drive required')
    if type(origin_route_m) not in (int,float) or not isfinite(origin_route_m) or origin_route_m>0:
        raise ValueError('Fixed finite nonpositive origin required')
    lo,hi=_interval(allowed_initial_route_interval_m,'initial entry')
    error=case['control']['position_error_bound_m'];bias=case['control']['position_bias_m']
    if (lo < -case['berth_tolerance_m'] or hi>case['berth_tolerance_m'] or abs(bias)>error or
        lo-origin_route_m-2*error<0 or hi-origin_route_m+2*error>=D-origin_route_m):
        raise ValueError('Full allowed entry and biased observation interval must remain within declared coverage; berth tolerance is unchanged')
    geometry=dict(project_candidate_id=bundle['candidate_id'],body_candidate_id=body['candidate_id'],
        body_evaluation_id=body['evaluation_id'],alignment_candidate_id=alignment['candidate_id'],
        alignment_evaluation_id=alignment['evaluation_id'],station_candidate_id=station['candidate_id'],
        station_evaluation_id=station['evaluation_id'],station_track_candidate_id=tracks['candidate_id'],
        station_track_evaluation_id=tracks['evaluation_id'],drive_duty_evaluation_id=duty['evaluation_id'])
    domains={}
    for kind,packet in (('operating-envelope',envelope),('continuous-feed',feed)):
        if (packet.get('schema')!=COVERAGE_SCHEMA or packet.get('kind')!=kind or
            packet.get('geometry_binding')!=geometry or packet.get('leg_index')!=leg_index or packet.get('direction')!=direction or
            packet.get('train_reference')!='formation-geometric-centre' or
            packet.get('physical_route_distance_m')!=D or
            packet.get('coverage_maturity') not in ('declared-research-domain','independently-checked-calculated-domain') or
            not isinstance(packet.get('basis'),str) or not packet['basis'].strip() or
            not isinstance(packet.get('limitations'),list) or not packet['limitations']):
            raise ValueError('Exact separately declared formation-reference '+kind+' coverage required')
        domain=_interval(packet.get('reference_interval_m'),kind)
        if domain[0]>origin_route_m or domain[1]<D:
            raise ValueError('Coverage omits the physical entry or target: '+kind)
        domains[kind]=domain
    # The rail model has an actual finite longitudinal extent. This check only
    # establishes reference-coordinate coverage; the separate envelope record
    # must account for finite train length, curves, sway and other interfaces.
    stations=alignment['physical_definition']['stations']
    origin_chainage=stations[leg_index if direction==1 else leg_index+1]['chainage_m']
    rail=_interval(tracks['physical_definition']['modeled_chainage_domain_m'],'counted rail')
    rail_domain=([rail[0]-origin_chainage,rail[1]-origin_chainage] if direction==1 else
                 [origin_chainage-rail[1],origin_chainage-rail[0]])
    if rail_domain[0]>origin_route_m or rail_domain[1]<D:
        raise ValueError('Counted station track does not reach the physical entry/target')
    geometry.update(operating_envelope_evaluation_id=envelope['evaluation_id'],feed_coverage_evaluation_id=feed['evaluation_id'])
    frame=dict(schema='osr-fixed-route-origin-entry/1',train_reference='formation-geometric-centre',
        origin_route_m=origin_route_m,physical_route_distance_m=D,physical_target_route_m=D,physical_authority_route_m=D,
        allowed_initial_route_interval_m=deepcopy(allowed_initial_route_interval_m),
        station_track_reference_domain_m=rail_domain,
        operating_envelope_reference_domain_m=deepcopy(domains['operating-envelope']),
        continuous_feed_reference_domain_m=deepcopy(domains['continuous-feed']),geometry=geometry)
    frame=motion.native_numbers(frame)
    frame['context_id']=identity(frame)
    q=deepcopy(case);control=q['control'];old_policy=control['policy_id']
    q['distance_m']=D-origin_route_m;q['brake_start_m']=case['brake_start_m']-origin_route_m
    source_emergency=case['fault']['emergency_at_m']
    q['fault']['emergency_at_m']=None if source_emergency is None else source_emergency-origin_route_m
    q['drive']['windows_m']=[[0.,D-origin_route_m]]
    control['end_of_authority_m']=D-origin_route_m
    if controller_v2 is not None:
        if (not isinstance(controller_v2,dict) or set(controller_v2)!={'strategy','brake_floor_n','creep_speed_m_s'} or
            controller_v2['strategy']!='held-docking-speed-governor/2' or
            any(type(controller_v2[k]) not in (int,float) or not isfinite(controller_v2[k]) for k in ('brake_floor_n','creep_speed_m_s')) or
            controller_v2['brake_floor_n']<0 or not 0<controller_v2['creep_speed_m_s']<=.25 or
            controller_v2['brake_floor_n']>control['brake_force_lower_bound_n']):
            raise ValueError('Explicit bounded research controller floor/creep required')
        control['research_v2']=dict(controller_v2,berth_target_m=D-origin_route_m)
    elif 'research_v2' in control:
        if control['research_v2']['berth_target_m']!=D:
            raise ValueError('Source controller target differs from physical route end')
        control['research_v2']['berth_target_m']=D-origin_route_m
    control=motion.native_numbers(control);q['control']=control
    sources=source_union(*packets,root=root)
    sources[PRODUCER]=digest(Path(root)/PRODUCER)
    policy_parameters={k:v for k,v in control.items() if k not in control_policy.OBSERVATIONS and k!='policy_id'}
    control['policy_id']=identity(dict(candidate_id=bundle['candidate_id'],source_policy_id=old_policy,
        frame_context_id=frame['context_id'],parameters=policy_parameters,producer_sha256=sources[PRODUCER],
        native_method_sha256=native_bridge.sources(root)))
    q.pop('id');q['id']=identity(q)
    binding=dict(frame_context_id=frame['context_id'],source_case_id=case['id'],source_policy_id=old_policy,
        compiled_case_id=q['id'],compiled_policy_id=control['policy_id'],
        source_brake_start_route_m=case['brake_start_m'],source_emergency_route_m=source_emergency)
    if not all(_hash(v) for k,v in binding.items() if k not in ('source_brake_start_route_m','source_emergency_route_m')):
        raise ValueError('Canonical source/compiled frame identities required')
    out=deepcopy(manifest);out.pop('evaluation_id')
    out.update(schema='osr-project-framed-motion-input/1',source_input_evaluation_id=manifest['evaluation_id'],
        source_case_id=case['id'],case_id=q['id'],native_input_id=identity(q),entry_frame=deepcopy(frame),frame_binding=deepcopy(binding),
        physical_route_distance_m=D,native_coordinate_distance_m=q['distance_m'],
        source_sha256=sources,train_reference='Fixed formation geometric centre; native x equals physical directed route coordinate minus fixed origin',
        authority_extended=False,physical_candidate_changed=False,coverage_geometry_verified=False,
        holds=manifest['holds']+['Coverage declarations and coordinate binding do not establish swept geometry, installed feed capability or service acceptance.'])
    out['evaluation_id']=identity(out)
    return q,out,frame,binding
