"""Service-case planning, actual passage coverage and rigid-CG ride diagnostics.

Plans do not qualify a train. Coverage comes from recorded wheel stations, and
unweighted RMS/VDV are deliberately separate from ISO comfort evaluation.
"""
from __future__ import annotations
from copy import deepcopy
import math
from numbers import Real
import numpy as np
from osr_mech.engineering_definition import fingerprint, validate
from engineering.civil_exploration.spatial_vehicle import SpatialVehicle, loaded_model


def finite(value, name, minimum=None):
    if isinstance(value,bool) or not isinstance(value,Real) or not math.isfinite(value) or (minimum is not None and value < minimum):
        raise ValueError('invalid service input: '+name)
    return float(value)


def passage_configuration(model, cfg, *, speed_m_s, acceleration_m_s2=0., clearance_m=1., arrival_offsets=None):
    """Place every represented wheel before the approach; compute the clearance time.

    Each train retains its own speed, load and identity. Positive acceleration is
    bounded by the supplied family speed limit; braking that stops before the
    clearance point is retained as a stopping test, not a completed passage.
    """
    result=deepcopy(cfg);speed=finite(speed_m_s,'speed',.001);a=finite(acceleration_m_s2,'acceleration')
    margin=finite(clearance_m,'clearance',.001);definition=validate(model)
    maximum=definition['profile']['max_speed_mps']
    if speed>maximum:raise ValueError('service speed exceeds the frozen family planning limit')
    length=model['bridge']['candidate']['definition']['deck']['span_m']*model['bridge']['span_count']
    approach=5.;plans=[]
    for index,entry in enumerate(result['traffic']):
        vehicle=SpatialVehicle(loaded_model(model,entry['load_case']),result['joint_laws'])
        wheels=[g for g in vehicle.groups.values() if g['wheel']]
        offsets=[float(g['cg'][0]) for g in wheels]
        if not offsets:raise ValueError('service plan needs represented wheelsets')
        first=-approach-margin-max(offsets);last=length+approach+margin-min(offsets);distance=last-first
        v0=speed if index==0 else finite(entry['speed_m_s'],'other train speed',.001)
        if v0>maximum:raise ValueError('other train speed exceeds the frozen family planning limit')
        arrival=entry['arrival_time_s'] if arrival_offsets is None else arrival_offsets[index]
        finite(arrival,'arrival offset',0.)
        stopped=a<0 and v0*v0/(-2*a)<distance
        if stopped:
            travel_time=-v0/a;end_time=arrival+travel_time+1.;end_speed=0.
        elif a==0:
            travel_time=distance/v0;end_time=arrival+travel_time;end_speed=v0
        else:
            end_speed=math.sqrt(v0*v0+2*a*distance)
            travel_time=2*distance/(v0+end_speed);end_time=arrival+travel_time
        if end_speed>maximum:raise ValueError('accelerating passage exceeds the frozen family planning limit')
        entry.update(initial_advance_m=first,arrival_time_s=arrival,speed_m_s=v0,acceleration_m_s2=a)
        plans.append(dict(train=entry['id'],track=entry['track'],wheelsets=[g['id'] for g in wheels],
            starting_advance_m=first,required_clearance_advance_m=last,
            estimated_end_time_s=end_time,end_speed_m_s=end_speed,
            expected_complete_passage=not stopped,stopping_test=stopped))
    duration=max(p['estimated_end_time_s'] for p in plans)
    return result,dict(schema='osr-service-passage-plan/1',hardware_definition_sha256=fingerprint(model),
        configuration_sha256=fingerprint(result),duration_s=duration,bridge_length_m=length,
        approach_length_m=approach,clearance_m=margin,trains=plans,
        represented_car_count=len({r['body'] for r in model['instances'] if r['body']}),
        family_car_count=definition['car_count'],full_family_represented=len({r['body'] for r in model['instances'] if r['body']})==definition['car_count'],
        physical_validation=False,engineering_released=False)


def case_matrix(model, base, speeds=(10.,15.,20.), resonance_band=None):
    """An explicit case matrix; all generated cases must be executed for coverage."""
    if not speeds or len(set(speeds))!=len(speeds):raise ValueError('unique operating speeds required')
    records=[]
    def add(identifier,kind,configuration,speed,acceleration=0.):
        cfg,plan=passage_configuration(model,configuration,speed_m_s=speed,acceleration_m_s2=acceleration)
        records.append(dict(id=identifier,kind=kind,configuration=cfg,passage_plan=plan))
    for load in ('empty','nominal','crush','uneven'):
        for speed in speeds:
            cfg=deepcopy(base)
            for train in cfg['traffic']:train['load_case']['id']=load
            add(f'{load}-{speed:g}mps','normal-service',cfg,speed)
    service_speed=float(speeds[len(speeds)//2]);nominal=deepcopy(base)
    for train in nominal['traffic']:train['load_case']['id']='nominal'
    add('service-braking','braking',deepcopy(nominal),service_speed,-.5)
    add('emergency-braking','braking',deepcopy(nominal),service_speed,-1.)
    add('acceleration','traction',deepcopy(nominal),min(service_speed,10.),.2)
    add('rescue-tow','rescue',deepcopy(nominal),min(service_speed,5.))
    maintenance=deepcopy(base)
    for train in maintenance['traffic']:train['load_case']['id']='empty'
    add('maintenance','maintenance',maintenance,min(service_speed,5.))
    curve=deepcopy(nominal);curve['route'].update(radius_m=800.,cant_rad=.04,vertical_radius_m=5000.)
    add('curve-cant-vertical-curve','alignment',curve,service_speed)
    defect=deepcopy(nominal);defect['irregularity']['amplitude_m']=.0005;defect['wheel_defect']['depth_m']=.0001
    add('irregularity-wheel-defect','distress',defect,service_speed)
    degraded=deepcopy(nominal)
    for law in degraded['joint_laws'].values():law['stiffness_si']=(np.asarray(law['stiffness_si'])*.8).tolist()
    degraded['infrastructure_condition']=dict(foundation_stiffness_factor=.5,bearing_stiffness_factor=.8)
    add('degraded-suspension-ground-bearings','degraded',degraded,service_speed)
    wear=deepcopy(nominal)
    for profile in wear['contact']['wheel_profiles'].values():
        for point in profile:point[1]+=.001*(point[0]/.06)**2
    wear['contact']['basis']+='; synthetic worn-tread perturbation, not a measured wear profile'
    add('worn-tread','wear',wear,service_speed)
    dual=deepcopy(nominal)
    if len(dual['traffic'])==1:
        other=deepcopy(dual['traffic'][0]);other.update(id='train-B',track=1,speed_m_s=service_speed*.8,arrival_time_s=.5)
        dual['traffic'].append(other)
    add('two-track-offset-arrival','traffic',dual,service_speed)
    if resonance_band is not None:
        low,high,step=resonance_band
        for number,name in ((low,'resonance low'),(high,'resonance high'),(step,'resonance step')):finite(number,name,.001)
        if high<low or (high-low)/step>80:raise ValueError('resonance band outside registered sweep budget')
        for speed in np.arange(low,high+step*.01,step):
            add(f'resonance-{speed:g}mps','resonance',deepcopy(nominal),float(speed))
    return dict(schema='osr-service-case-matrix/1',hardware_definition_sha256=fingerprint(model),cases=records,
        operating_speeds_m_s=list(speeds),resonance_band_m_s=list(resonance_band) if resonance_band else None,
        numerical_budget=dict(maximum_duration_per_case_s=30.,maximum_steps_per_case=200000),
        unexecuted_case_ids=[r['id'] for r in records],physical_validation=False,engineering_released=False,
        basis='synthetic research matrix; rescue payload, braking distributions, route/wear and ground cases require project records')


def coverage(result, plan):
    """Use every recorded wheel on both sides, rather than duration alone."""
    if result['hardware_definition_sha256']!=plan['hardware_definition_sha256'] or result['configuration_sha256']!=plan['configuration_sha256']:
        raise ValueError('passage result and frozen plan identity differ')
    expected={(p['train'],wheel,side) for p in plan['trains'] for wheel in p['wheelsets'] for side in (-1,1)}
    observed={key:[] for key in expected};complete_samples=True;unknown=set()
    for h in result['history']:
        keys=set()
        for c in h['contacts']:
            key=(c['train'],c['wheelset'],c['side']);keys.add(key)
            if key not in expected:unknown.add(key);continue
            s=finite(c['station_m'],'recorded wheel station');observed[key].append(s)
        if keys!=expected or len(keys)!=len(h['contacts']):complete_samples=False
    boundary=-plan['approach_length_m'];end=plan['bridge_length_m']+plan['approach_length_m']
    rows=[]
    for key,stations in sorted(observed.items()):
        entered=any(0<=s<=plan['bridge_length_m'] for s in stations)
        finished=bool(stations) and stations[-1]>=end
        rows.append(dict(train=key[0],wheelset=key[1],side=key[2],
            first_station_m=stations[0] if stations else None,last_station_m=stations[-1] if stations else None,
            began_before_approach=bool(stations) and stations[0]<=boundary,entered_structure=entered,cleared_approach=finished))
    crossing_required={p['train'] for p in plan['trains'] if p['expected_complete_passage']}
    passed=complete_samples and bool(rows) and not unknown and all(r['began_before_approach'] and r['entered_structure'] and r['cleared_approach'] for r in rows if r['train'] in crossing_required)
    return dict(schema='osr-service-passage-coverage/1',wheel_contacts=rows,all_expected_contacts_recorded=complete_samples,
        coverage_basis='recorded nominal interpolation stations of the linearised contact adapter; finite contact motion is not qualified',
        unexpected_contact_count=len(unknown),complete_passage=bool(crossing_required) and passed,
        stopping_test=not crossing_required,full_family_represented=plan['full_family_represented'],
        within_adapter_domain=result['within_adapter_domain'],physical_validation=False,engineering_released=False)


def ride_diagnostics(result, *, discard_before_s=0.):
    """Time-integrated unweighted RMS, crest factor and fourth-power VDV at the CG."""
    discard=finite(discard_before_s,'discard time',0.);groups={};samples={};expected=None
    for h in result['history']:
        if h['time_s']<discard:continue
        keys=set()
        for row in h.get('bodies',[]):
            key=(row['train'],row['body']);keys.add(key)
            groups.setdefault(key,[]).append(row);samples.setdefault(key,[]).append(h['time_s'])
        if not keys:raise ValueError('individual body acceleration histories are required for ride diagnostics')
        if expected is None:expected=keys
        if keys!=expected or len(keys)!=len(h.get('bodies',[])):raise ValueError('every body requires one sample at every retained timestamp')
    output=[]
    for key,rows in sorted(groups.items()):
        time=np.asarray(samples[key],dtype=float);a=np.asarray([r['acceleration_body_m_s2'] for r in rows],dtype=float)
        if len(time)<3 or a.shape!=(len(time),3) or not np.isfinite(a).all() or not np.isfinite(time).all() or np.any(np.diff(time)<=0):
            raise ValueError('ordered finite body histories with three acceleration axes required')
        duration=time[-1]-time[0];rms=np.sqrt(np.trapezoid(a*a,time,axis=0)/duration);peak=np.max(np.abs(a),axis=0)
        vdv=np.trapezoid(a**4,time,axis=0)**.25
        crest=[float(p/r) if r else None for p,r in zip(peak,rms)]
        output.append(dict(train=key[0],body=key[1],sample_count=len(time),analysed_duration_s=float(duration),
            rms_xyz_m_s2=rms.tolist(),peak_xyz_m_s2=peak.tolist(),crest_factor_xyz=crest,vdv_xyz_m_s175=vdv.tolist(),
            reference_point=rows[0]['reference_point']))
    if not output:raise ValueError('no usable body samples in the selected time window')
    return dict(schema='osr-unweighted-rigid-cg-ride/1',body_results=output,discard_before_s=discard,
        basis='unweighted kinematic acceleration in nominal body axes; no ISO frequency weighting, seat transfer or comfort acceptance',
        iso_comfort_evaluated=False,physical_validation=False,engineering_released=False)
