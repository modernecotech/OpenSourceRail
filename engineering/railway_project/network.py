"""Bind mapped adjacent legs to a causal no-storage research fleet request.

This module compiles explicit schedules; it does not invent journey times,
optimise a fleet, run a simulator or turn arrivals into protected service.
Physical route lengths remain station-centre distances even for rebased legs.
"""
from copy import deepcopy
from math import isfinite
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest,identity
from engineering.station_pair import native_bridge
from .civil import sealed,source_union
from .route import FLAGS

PRODUCER='engineering/railway_project/network.py'
TRAIN_FIELDS={'id','initial_station_id','initial_position_m','ready_at_s','role','initial_drive_temperature_c'}
DEPARTURE_FIELDS={'id','route_id','departure_time_s','requested_train_id','departure_authorized'}


def _number(x,lower,upper,name):
    if type(x) not in (int,float) or not isfinite(x) or not lower<=x<=upper:
        raise ValueError('Explicit bounded '+name+' required')
    return x


def _name(x):
    return isinstance(x,str) and 0<len(x)<=160 and not any(ord(c)<32 for c in x)


def compile_network(bundle,alignment,compiled_legs,trains,departures,*,turnaround_s,clearance_s,release_control,root=ROOT):
    """Return a canonical FleetCase and sealed provenance manifest, no execution.

    compiled_legs is [(Case, motion_manifest), ...] covering both directions of
    each adjacent leg. departures reference the returned deterministic route IDs
    (leg-N-forward/reverse). Trains retain their actual signed station offsets.
    All station energy stores/transfers/reset loads are explicitly inactive;
    storage-enabled alternatives require a different compiler and evaluator.
    """
    sealed(bundle);sealed(alignment)
    p=bundle.get('physical_definition',{})
    if (bundle.get('schema')!='osr-mapped-railway-project-bundle/1' or
        alignment.get('schema')!='osr-station-straight-alignment/1' or
        any(x['candidate_id']!=identity(x['physical_definition']) for x in (bundle,alignment)) or
        p.get('alignment_candidate_id')!=alignment['candidate_id'] or bundle.get('alignment_evaluation_id')!=alignment['evaluation_id']):
        raise ValueError('Exact mapped project/alignment required')
    stations=alignment['physical_definition']['stations'];ids=[s['id'] for s in stations]
    if not 2<=len(ids)<=8 or len(set(ids))!=len(ids) or not all(_name(x) for x in ids):
        raise ValueError('Two to eight uniquely named ordered stations required')
    if not isinstance(compiled_legs,list) or len(compiled_legs)!=2*(len(ids)-1):
        raise ValueError('Both explicit directions of every adjacent leg required')
    source=native_bridge.sources(root);routes={};exports={};packets=[bundle,alignment]
    for case,m in compiled_legs:
        sealed(m);packets.append(m)
        if (m.get('schema') not in ('osr-project-motion-input/1','osr-project-framed-motion-input/1') or
            case.get('id')!=identity({k:v for k,v in case.items() if k!='id'}) or
            m.get('case_id')!=case['id'] or m.get('native_input_id')!=identity(case) or
            case['candidate_id']!=bundle['candidate_id'] or m['candidate_id']!=bundle['candidate_id'] or
            m['bundle_evaluation_id']!=bundle['evaluation_id'] or
            m['alignment_evaluation_id']!=alignment['evaluation_id'] or
            m['body_evaluation_id']!=bundle['body_evaluation_id'] or m.get('native_method_sha256')!=source):
            raise ValueError('Canonical same-project leg and current native source required')
        i=m['leg_index'];d=m['direction']
        if type(i) is not int or not 0<=i<len(ids)-1 or type(d) is not int or d not in (-1,1):
            raise ValueError('Known directed adjacent leg required')
        leg=alignment['legs'][i];a,b=(ids[i],ids[i+1]) if d==1 else (ids[i+1],ids[i])
        if (m['from_stop']!=a or m['to_stop']!=b or leg['from_stop']!=ids[i] or leg['to_stop']!=ids[i+1]):
            raise ValueError('Leg station order differs from mapped geometry')
        name='leg-'+str(i)+'-'+('forward' if d==1 else 'reverse')
        if name in routes:raise ValueError('Duplicate directed leg; missing directions cannot be aliased')
        geometry_record=dict(alignment_candidate_id=alignment['candidate_id'],alignment_evaluation_id=alignment['evaluation_id'],
            leg_index=i,direction=d,from_stop=a,to_stop=b,distance_m=leg['distance_m'])
        r=dict(id=name,from_station_id=a,to_station_id=b,distance_m=leg['distance_m'],geometry_record_id=identity(geometry_record))
        if m['schema']=='osr-project-framed-motion-input/1':
            f=m['entry_frame'];binding=m['frame_binding'];g=f['geometry']
            if (f.get('context_id')!=identity({k:v for k,v in f.items() if k!='context_id'}) or
                f['physical_route_distance_m']!=leg['distance_m'] or f['physical_target_route_m']!=leg['distance_m'] or
                f['physical_authority_route_m']!=leg['distance_m'] or
                g['project_candidate_id']!=bundle['candidate_id'] or g['alignment_candidate_id']!=alignment['candidate_id'] or
                g['alignment_evaluation_id']!=alignment['evaluation_id'] or
                g['body_candidate_id']!=p['body_candidate_id'] or g['body_evaluation_id']!=bundle['body_evaluation_id'] or
                g['station_candidate_id']!=p['station_geometry_candidate_id'] or g['station_evaluation_id']!=bundle['station_evaluation_id'] or
                g['station_track_candidate_id']!=p.get('station_track_geometry_candidate_id') or g['station_track_evaluation_id']!=bundle.get('station_track_evaluation_id') or
                g['drive_duty_evaluation_id']!=m['drive_evaluation_id'] or binding['frame_context_id']!=f['context_id'] or
                binding['compiled_case_id']!=case['id'] or binding['compiled_policy_id']!=case['control']['policy_id'] or
                case['distance_m']!=leg['distance_m']-f['origin_route_m'] or
                case['control']['end_of_authority_m']!=case['distance_m'] or
                case['brake_start_m']!=binding['source_brake_start_route_m']-f['origin_route_m'] or
                case['fault']['emergency_at_m']!=(None if binding['source_emergency_route_m'] is None else binding['source_emergency_route_m']-f['origin_route_m']) or
                case.get('drive',{}).get('windows_m')!=[[0.,case['distance_m']]] or
                case['drive'].get('external_mass_kg')!=0 or case['drive'].get('external_resistance_n')!=0 or
                case['control'].get('research_v2',{}).get('berth_target_m',case['distance_m'])!=case['distance_m']):
                raise ValueError('Exact compiled frame, geometry and Case binding required')
            r['entry_frame']=deepcopy(f)
        elif (case['distance_m']!=leg['distance_m'] or case['control']['end_of_authority_m']!=case['distance_m'] or
              case['control'].get('research_v2',{}).get('berth_target_m',case['distance_m'])!=case['distance_m']):
            raise ValueError('Unframed journey distance/target/authority differs from physical leg')
        routes[name]=r;exports[name]=(case,m)
    if not isinstance(trains,list) or not 1<=len(trains)<=16:
        raise ValueError('One to sixteen explicit trains required')
    train_ids=set()
    for t in trains:
        if (not isinstance(t,dict) or set(t)!=TRAIN_FIELDS or not _name(t['id']) or t['id'] in train_ids or
            t['initial_station_id'] not in ids or t['role'] not in ('active','spare')):
            raise ValueError('Unique explicit trains, roles and actual initial stations required')
        train_ids.add(t['id'])
        _number(t['initial_position_m'],-1000.,1000.,'signed station offset')
        _number(t['ready_at_s'],0.,172800.,'train readiness')
        if t['initial_drive_temperature_c'] is not None:_number(t['initial_drive_temperature_c'],-100.,500.,'initial temperature')
    if not isinstance(departures,list) or not 1<=len(departures)<=64:
        raise ValueError('One to sixty-four explicit departures required')
    ds=[];seen=set()
    for d in departures:
        if (not isinstance(d,dict) or set(d)!=DEPARTURE_FIELDS or not _name(d['id']) or d['id'] in seen or
            d['route_id'] not in routes or type(d['departure_authorized']) is not bool or
            (d['requested_train_id'] is not None and d['requested_train_id'] not in train_ids)):
            raise ValueError('Unique explicit departure, known route/train and authorization hypothesis required')
        seen.add(d['id']);_number(d['departure_time_s'],0.,172800.,'departure time')
        r=routes[d['route_id']];case,m=exports[d['route_id']]
        row=dict(id=d['id'],journey=deepcopy(case),route_id=d['route_id'],departure_station_id=r['from_station_id'],
            arrival_station_id=r['to_station_id'],departure_time_s=d['departure_time_s'],
            departure_authorized=d['departure_authorized'],capture_failed=False,release_failed=False,reset_failed=False)
        if d['requested_train_id'] is not None:row['requested_train_id']=d['requested_train_id']
        if 'frame_binding' in m:row['frame_binding']=deepcopy(m['frame_binding'])
        ds.append(row)
    fields={'mode','force_slew_n_s','maximum_traction_share','reserve_factor'}
    if (not isinstance(release_control,dict) or set(release_control) not in (fields,fields|{'cutoff_audit'}) or
        release_control['mode'] not in ('grid-substitution-slew/1','grid-substitution-slew/2')):
        raise ValueError('Explicit native recorder release-policy contract required even when all transfers are inactive')
    _number(release_control['force_slew_n_s'],1e-12,1e12,'force slew')
    _number(release_control['maximum_traction_share'],1e-12,1.,'traction share')
    _number(release_control['reserve_factor'],1.,100.,'reserve factor')
    if 'cutoff_audit' in release_control and type(release_control['cutoff_audit']) is not bool:raise ValueError('Boolean cutoff audit required')
    _number(turnaround_s,0.,172800.,'turn/staging time hypothesis');_number(clearance_s,1e-12,172800.,'route-clearance time hypothesis')
    inactive=[]
    for s in ids:
        D=min(r['distance_m'] for r in routes.values() if s in (r['from_station_id'],r['to_station_id']))
        inactive.append(dict(id=s,initial_energy_j=0.,store=dict(capacity_j=0.,capture_efficiency=1.,release_efficiency=1.,leakage_per_s=0.),
            capture_stages=[],release=dict(start_m=0.,end_m=D,max_force_n=0.,max_power_w=0.),
            reset=dict(duration_s=0.,grid_energy_j=0.,grid_power_w=0.)))
    network=dict(schema='osr-no-storage-adjacent-network/1',position_reference='signed-station-order-offset/1',
        route_resource_model='dedicated-directed-double-track-blocks/1',station_order=ids,
        geometry_binding=dict(project_candidate_id=bundle['candidate_id'],alignment_candidate_id=alignment['candidate_id'],
            alignment_evaluation_id=alignment['evaluation_id'],route_manifest_id=alignment['corridor_evaluation_id']),
        routes=[routes[k] for k in sorted(routes)])
    request=dict(candidate_id=bundle['candidate_id'],stations=inactive,release_control=deepcopy(release_control),trains=deepcopy(trains),
        departures=ds,turnaround_s=turnaround_s,clearance_s=clearance_s,network=network)
    request['id']=identity(request)
    sources=source_union(*packets,root=root);sources[PRODUCER]=digest(Path(root)/PRODUCER)
    manifest=dict(schema='osr-project-network-input/1',candidate_id=bundle['candidate_id'],bundle_evaluation_id=bundle['evaluation_id'],
        alignment_candidate_id=alignment['candidate_id'],alignment_evaluation_id=alignment['evaluation_id'],
        body_evaluation_id=bundle['body_evaluation_id'],case_id=request['id'],native_input_id=identity(request),
        directed_leg_inputs={k:dict(case_id=q['id'],input_manifest_evaluation_id=m['evaluation_id'],native_input_id=identity(q)) for k,(q,m) in sorted(exports.items())},
        active_trainsets=sum(t['role']=='active' for t in trains),spare_trainsets=sum(t['role']=='spare' for t in trains),
        native_method_sha256=source,source_sha256=sources,route_m=alignment['route_m'],
        zero_energy_is_exact_inactive_equipment=True,service_evaluated=False,native_service_complete=False,
        holds=['Turn/staging, clearance and dedicated directed blocks are hypotheses, not finite-train station/turnout/interlocking proof.',
            'No shared supply, variable-grade, thermal calibration, braking hardware, capacity or operating acceptance follows from compilation.',
            'Unframed negative entries and unsupported source/control domains must remain held by the native evaluator.',
            'Arrival counts must be rescreened for stopping margin, terminal behaviour and every declared requirement before service completion.'],**FLAGS)
    manifest['evaluation_id']=identity(manifest)
    return request,manifest
