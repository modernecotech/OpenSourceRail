"""Fixed-line urban/suburban longitudinal plants and finite powered zones.

Passenger transfers do not route a train between fixed guideways. The 1km/88s
moving and station campaigns remain benchmarks; this module separately executes
longer profiles. Equivalent circuits and synthetic detectors are unqualified.
"""
from copy import deepcopy
from collections import OrderedDict
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from hashlib import sha256
import gzip
import json
import math
from pathlib import Path
import subprocess
import tempfile
import tomllib

import numpy as np
from scipy.integrate import quad
from scipy.optimize import least_squares

from . import configuration,model,station

ROOT=model.ROOT
INPUT=Path(__file__).with_suffix('.toml')
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/corridor'
FLAGS=model.FLAGS
EXAMPLE=ROOT/'crates/osr-interlocking/examples/corridor_replay.rs'
BUILD=['cargo','build','--locked','-p','osr-interlocking','--example','corridor_replay','--message-format=json']
FAULTS=('legacy-voltage','booster-loss','grid-loss','resistor-loss','handover-delay','stale-observation','uncommitted')
FILES={'result.json.gz','overview.svg','README.md',*(f'{mode}-{name}' for mode in ('urban','suburban') for name in ('overview.png','motion.mp4','visual-receipt.json'))}
MAX_RAW=128*1024*1024
_REQUEST_IDENTITIES=OrderedDict()


def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def digest(value):return sha256(value).hexdigest()


def load():
    a=tomllib.loads(INPUT.read_text())
    if a.get('schema')!='osr-fixed-powered-corridor-input/1':raise ValueError('fixed powered corridor schema required')
    for key,value in a.items():
        if key in {'schema','revision','ratings','validation'}:continue
        if type(value) not in (int,float) or not math.isfinite(value) or not 0<value<100000:raise ValueError('bounded corridor input: '+key)
    if any(value is not False for value in a['validation'].values()):raise ValueError('corridor cannot claim hardware acceptance')
    for rating in a['ratings'].values():
        if any(type(v) not in (int,float) or not math.isfinite(v) or not 0<v<1e7 for v in rating.values()):raise ValueError('bounded equivalent motor rating required')
        if rating['maximum_phase_voltage_v']>rating['dc_bus_v']*.9/math.sqrt(3):raise ValueError('phase rating exceeds assumed modulation bound')
    return a


def sources():
    from . import moving_train
    paths={Path(__file__),INPUT,ROOT/'engineering/analysis/tests/test_ferrite_maglev_corridor.py',
        ROOT/'crates/osr-interlocking/examples/corridor_replay.rs',*configuration.source_paths()}
    for package in ('osr-core','osr-interlocking','osr-maglev-control'):
        base=ROOT/'crates'/package;paths.add(base/'Cargo.toml');paths.update(base.rglob('*.rs'))
    paths.update(ROOT/name for name in station.sources())
    paths.update(ROOT/name for name in moving_train.sources())
    paths.update({ROOT/'Cargo.toml',ROOT/'Cargo.lock',ROOT/'engineering/ferrite_maglev/moving_train.py',ROOT/'engineering/ferrite_maglev/moving-train.toml'})
    paths.update({ROOT/'engineering/ferrite_maglev/system_campaign.py',ROOT/'engineering/ferrite_maglev/system-campaign.toml'})
    return {p.relative_to(ROOT).as_posix():digest(p.read_bytes()) for p in sorted(paths) if p.is_file()}


def _topup(v0,v1,mass,acceleration,jerk,constant,quadratic):
    a0=-(constant+quadratic*v0*v0)/mass;a1=-(constant+quadratic*v1*v1)/mass
    peak=min(acceleration,math.sqrt(max(0.,jerk*(v1-v0)+(a0*a0+a1*a1)/2)))
    if peak<=max(0.,a0,a1):raise ValueError('positive finite booster transition required')
    first=(peak-a0)/jerk;last=(peak-a1)/jerk
    ramp_delta=(2*peak*peak-a0*a0-a1*a1)/(2*jerk)
    hold=(v1-v0-ramp_delta)/peak
    if hold< -1e-7:raise ValueError('booster transition has no forward solution')
    return station._segments(v0,a0,[(jerk,first),(0.,max(0.,hold)),(-jerk,last)])


def profile(*,distance_m,runtime_s,cars,car_mass_kg,mode='urban',grade=0.):
    """Exact constant-jerk powered phases and analytic resistance-only coast."""
    a=load();s=station.load();m=s['motion'];mass=cars*car_mass_kg
    constant=m['resistance_constant_n_per_car']*cars+mass*station.G*grade
    quadratic=m['resistance_quadratic_n_per_car']*cars
    inputs=dict(distance_m=distance_m,runtime_s=runtime_s,cars=cars,car_mass_kg=car_mass_kg,train_mass_kg=mass,
        acceleration_m_s2=a['acceleration_m_s2'],deceleration_m_s2=a['deceleration_m_s2'],jerk_m_s3=a['jerk_m_s3'],grade=grade,speed_limit_kmh=a['speed_limit_kmh'])
    if not 100<=distance_m<=10000 or not 40<=runtime_s<=900 or mode not in {'urban','suburban'}:raise ValueError('bounded corridor motion inputs required')
    if mode=='urban':
        t=station.trajectory(distance_m=distance_m,runtime_s=runtime_s,cars=cars,car_mass_kg=car_mass_kg,acceleration=a['acceleration_m_s2'],
            deceleration=a['deceleration_m_s2'],jerk=a['jerk_m_s3'],grade=grade,speed_limit_kmh=a['speed_limit_kmh'],record_trace=False)
        if not t['study_pass']:return dict(study_pass=False,inputs=inputs,reason=t.get('reason'),phases=[],**FLAGS)
        sequences=[('launch','departure',t['segments']['launch'])]
        coast_time=t['phases']['coast']['duration_s'];launch=t['phases']['launch'];v=t['launch_speed_kmh']/3.6
        coast=dict(kind='coast',phase='coast',zone_id=None,start_time_s=launch['duration_s'],start_position_m=launch['distance_m'],start_speed_m_s=v,
            start_acceleration_m_s2=-(constant+quadratic*v*v)/mass,duration_s=coast_time)
        brake_time=launch['duration_s']+coast_time;brake_x=launch['distance_m']+t['phases']['coast']['distance_m']
        phases=[dict(seg,kind='jerk',phase='launch',zone_id='departure') for seg in sequences[0][2]]+[coast]
        phases.extend(dict(seg,kind='jerk',phase='braking',zone_id='arrival',start_time_s=seg['start_time_s']+brake_time,start_position_m=seg['start_position_m']+brake_x) for seg in t['segments']['braking'])
    else:
        length=cars*s['vehicle']['body_length_m']+(cars-1)*s['vehicle']['coupling_gap_m']
        def parts(values):
            speed,t1,t2=values
            launch=station._segments(0.,0.,station._launch(speed,mass,a['acceleration_m_s2'],a['jerk_m_s3'],constant,quadratic))
            u,x1,stopped1=station._coast(speed,t1,mass,constant,quadratic)
            boost=_topup(u,speed,mass,a['acceleration_m_s2'],a['jerk_m_s3'],constant,quadratic)
            v,x2,stopped2=station._coast(speed,t2,mass,constant,quadratic)
            brake=station._segments(v,-(constant+quadratic*v*v)/mass,station._brake(v,mass,a['deceleration_m_s2'],a['jerk_m_s3'],constant,quadratic))
            return launch,u,x1,boost,v,x2,brake,stopped1+stopped2
        def residual(values):
            try:
                l,u,x1,b,v,x2,br,stopped=parts(values)
                return [(l[1]+values[1]+b[1]+values[2]+br[1]-runtime_s+stopped)/runtime_s,
                    (l[2]+x1+b[2]+x2+br[2]-distance_m)/distance_m,
                    (l[2]+x1+b[2]/2-length/2-distance_m/2)/(distance_m/2)]
            except ValueError:return [100.,100.,100.]
        fit=least_squares(residual,[min(21.5,a['speed_limit_kmh']/3.6*.99),runtime_s*.4,runtime_s*.4],
            bounds=([3.,.1,.1],[a['speed_limit_kmh']/3.6,850.,850.]),xtol=1e-11,ftol=1e-11,gtol=1e-11,max_nfev=400)
        if max(abs(v) for v in fit.fun)>1e-6:return dict(study_pass=False,inputs=inputs,reason='No midpoint-top-up profile meets distance/runtime/speed constraints',residual=fit.fun.tolist(),phases=[],**FLAGS)
        l,u,x1,b,v,x2,br,stopped=parts(fit.x);phases=[];time=position=0.
        for label,zone,part in [('launch','departure',l),('coast',None,fit.x[1]),('booster','booster',b),('coast',None,fit.x[2]),('braking','arrival',br)]:
            if label=='coast':
                speed=fit.x[0];phases.append(dict(kind='coast',phase=label,zone_id=None,start_time_s=time,start_position_m=position,start_speed_m_s=speed,
                    start_acceleration_m_s2=-(constant+quadratic*speed*speed)/mass,duration_s=float(part)))
                _,dx,_=station._coast(speed,part,mass,constant,quadratic);time+=part;position+=dx
            else:
                for seg in part[0]:phases.append(dict(seg,kind='jerk',phase=label,zone_id=zone,start_time_s=time+seg['start_time_s'],start_position_m=position+seg['start_position_m']))
                time+=part[1];position+=part[2]
    return dict(schema='osr-fixed-corridor-profile/1',study_pass=True,inputs=inputs,mode=mode,phases=phases,
        resistance=dict(constant_n_per_car=m['resistance_constant_n_per_car'],quadratic_n_per_car_per_m_s_squared=m['resistance_quadratic_n_per_car']),**FLAGS)


def trajectory_at(t,time_s):
    if not t['study_pass'] or not math.isfinite(time_s) or not 0<=time_s<=t['inputs']['runtime_s']+1e-7:raise ValueError('feasible bounded corridor profile required')
    seg=next((s for s in t['phases'] if time_s<=s['start_time_s']+s['duration_s']+1e-10),t['phases'][-1])
    tau=min(seg['duration_s'],max(0.,time_s-seg['start_time_s']));i=t['inputs'];r=t['resistance'];mass=i['train_mass_kg']
    constant=r['constant_n_per_car']*i['cars']+mass*station.G*i['grade'];quadratic=r['quadratic_n_per_car_per_m_s_squared']*i['cars']
    if seg['kind']=='coast':
        speed,dx,_=station._coast(seg['start_speed_m_s'],tau,mass,constant,quadratic);acc=-(constant+quadratic*speed*speed)/mass;force=0.
    else:
        speed,acc,dx=station._step(seg['start_speed_m_s'],seg['start_acceleration_m_s2'],seg['jerk_m_s3'],tau)
        force=mass*acc+constant+quadratic*speed*speed
    return dict(time_s=time_s,position_m=seg['start_position_m']+dx,speed_m_s=max(0.,speed),acceleration_m_s2=acc,
        phase=seg['phase'],zone_id=seg['zone_id'],motor_force_n=force)


def _zones(t,a):
    distance=t['inputs']['distance_m'];suburban=t['mode']=='suburban';left=-150.;right=200.
    zones=[dict(id='departure',kind='station',passenger=True,start_m=left,end_m=right),dict(id='arrival',kind='station',passenger=True,start_m=distance+left,end_m=distance+right)]
    if suburban:
        segs=[s for s in t['phases'] if s['phase']=='booster'];begin=segs[0]['start_position_m'];last=segs[-1]
        _,_,dx=station._step(last['start_speed_m_s'],last['start_acceleration_m_s2'],last['jerk_m_s3'],last['duration_s']);end=last['start_position_m']+dx
        length=t['inputs']['cars']*17+(t['inputs']['cars']-1)*.5
        # Full magnetic-band coverage and five metres geometric margin; finite
        # installed zones are rounded outwards to electrical section boundaries.
        start=math.floor((begin-(length-2.5)-5)/a['electrical_section_m'])*a['electrical_section_m']
        stop=math.ceil((end-2.5+5)/a['electrical_section_m'])*a['electrical_section_m']
        zones.insert(1,dict(id='booster',kind='top-up',passenger=False,start_m=start,end_m=stop))
    for zone in zones:
        zone.update(length_m=zone['end_m']-zone['start_m'],electrical_sections=math.ceil((zone['end_m']-zone['start_m'])/a['electrical_section_m']),
            electrical_section_m=a['electrical_section_m'],protected_by='exclusive-corridor-and-arrival-bundle')
    return zones


def evaluate(c=None,*,distance_m,cars,car_mass_kg=None,load_case='AW3',mode='urban',runtime_s=None,battery_kwh=None,charger_kw=400.,dwell_s=60.,motor_option='higher-voltage',record_trace=False):
    if c is None:_,c,_=model.load()
    a=load();p=c['power'];battery=p['services_battery_kwh_per_car'] if battery_kwh is None else battery_kwh
    if type(cars) is not int or not 1<=cars<=12 or load_case not in {'AW0','AW2','AW3'} or motor_option not in a['ratings']:raise ValueError('bounded declared formation/load/rating required')
    if car_mass_kg is None:car_mass_kg=model.mass(c,c['mass']['ferrite_base'],battery)[{'AW0':'tare_kg','AW2':'aw2_kg','AW3':'aw3_kg'}[load_case]]
    if runtime_s is None:
        masses=model.mass(c,c['mass']['ferrite_base'],battery)
        runtime_s=_common_runtime(distance_m,cars,mode,tuple(masses[key] for key in ('tare_kg','aw2_kg','aw3_kg')))
    for value,lo,hi in [(car_mass_kg,5000,100000),(battery,5,100),(charger_kw,100,1000),(dwell_s,30,300),(distance_m,100,10000),(runtime_s,40,900)]:
        if type(value) not in (int,float) or not math.isfinite(value) or not lo<=value<=hi:raise ValueError('finite bounded corridor inputs required')
    key=encoded(dict(c=c,a=a,distance_m=distance_m,cars=cars,car_mass_kg=car_mass_kg,load_case=load_case,mode=mode,runtime_s=runtime_s,
        battery_kwh=battery,charger_kw=charger_kw,dwell_s=dwell_s,motor_option=motor_option,record_trace=record_trace)).decode()
    return deepcopy(_evaluate(key))


@lru_cache(maxsize=2048)
def _common_runtime(distance,cars,mode,masses):
    base=max(60.,140.+.03*(distance-2000.)) if mode=='urban' else 60.+.048*distance
    # One exact runtime for every load case, chosen from bounded explicit duty
    # alternatives. A lighter empty vehicle has greater assumed drag per tonne.
    for extra in range(0,101,5):
        if all(profile(distance_m=distance,runtime_s=base+extra,cars=cars,car_mass_kg=mass,mode=mode)['study_pass'] for mass in masses):return base+extra
    return base+100.


@lru_cache(maxsize=512)
def _motion_samples(profile_key):
    """Immutable exact-distance plant cache, independent of converter or dwell."""
    t=json.loads(profile_key);runtime=t['inputs']['runtime_s'];interval=.05
    times=np.unique(np.concatenate((np.linspace(0.,runtime,math.ceil(runtime/interval)+1),
        np.array([s['start_time_s'] for s in t['phases']]),np.array([s['start_time_s']+s['duration_s'] for s in t['phases']]))))
    position=np.zeros(len(times));speed=position.copy();acc=position.copy();force=position.copy();zone=np.empty(len(times),dtype=object)
    i=t['inputs'];r=t['resistance'];mass=i['train_mass_kg'];constant=r['constant_n_per_car']*i['cars']+mass*station.G*i['grade'];quadratic=r['quadratic_n_per_car_per_m_s_squared']*i['cars']
    for seg in t['phases']:
        mask=(times>=seg['start_time_s']-1e-10)&(times<=seg['start_time_s']+seg['duration_s']+1e-10)
        tau=np.clip(times[mask]-seg['start_time_s'],0.,seg['duration_s']);v0=seg['start_speed_m_s']
        if seg['kind']=='coast':
            if constant<=0:raise ValueError('vectorised corridor coast currently requires positive resistance; adverse gradients remain held')
            k=constant/mass;q=quadratic/mass;theta=math.atan(v0*math.sqrt(q/k));final=theta-math.sqrt(k*q)*tau
            vv=math.sqrt(k/q)*np.tan(final);dx=(np.log(np.cos(final))-math.log(math.cos(theta)))/q;aa=-(constant+quadratic*vv*vv)/mass;ff=np.zeros(len(tau))
        else:
            jerk=seg['jerk_m_s3'];a0=seg['start_acceleration_m_s2'];vv=v0+a0*tau+.5*jerk*tau*tau
            dx=v0*tau+.5*a0*tau*tau+jerk*tau*tau*tau/6;aa=a0+jerk*tau;ff=mass*aa+constant+quadratic*vv*vv
        position[mask]=seg['start_position_m']+dx;speed[mask]=np.maximum(0.,vv);acc[mask]=aa;force[mask]=ff;zone[mask]=seg['zone_id']
    energy=[]
    for sign in (1,-1):
        work=0.
        for seg in t['phases']:
            if seg['kind']=='coast':continue
            def power(time):
                point=trajectory_at(t,time);return max(0.,sign*point['motor_force_n'])*point['speed_m_s']
            work+=quad(power,seg['start_time_s'],seg['start_time_s']+seg['duration_s'],epsabs=.01)[0]
        energy.append(work)
    for array in (times,position,speed,acc,force,zone):array.setflags(write=False)
    return dict(times=times,position=position,speed=speed,acc=acc,force=force,zone=zone,energy=energy)


@lru_cache(maxsize=1024)
def _motion_screen(profile_key,rating_key,record_trace):
    t=json.loads(profile_key);rating=json.loads(rating_key);sample=_motion_samples(profile_key);i=t['inputs'];cars=i['cars'];v=station.load()['vehicle']
    length=cars*v['body_length_m']+(cars-1)*v['coupling_gap_m'];band=v['magnetic_band_m_per_car'];pitch=v['body_length_m']+v['coupling_gap_m']
    bands=np.array([[-(v['body_length_m']-band)/2-band-j*pitch,-(v['body_length_m']-band)/2-j*pitch] for j in range(cars)])
    density=station.load()['station']['equivalent_envelope_force_n_m']*length/(band*cars)
    overlap=np.zeros(len(sample['times']));active=np.zeros(len(overlap),dtype=bool)
    for z in t['powered_zones']:
        mask=sample['zone']==z['id'];active|=mask
        overlap[mask]=station._overlap(sample['position'][mask],bands,z['start_m'],z['end_m'])
    demand=sample['force'];moving=np.abs(demand)>1e-3;current=demand/rating['force_constant_n_a']
    derivative=np.zeros(len(current));delta=np.diff(sample['times']);derivative[1:]=np.divide(np.abs(np.diff(current)),delta,out=np.zeros(len(delta)),where=delta>1e-9)
    voltage=np.where(active&moving,rating['force_constant_n_a']*sample['speed']+np.abs(rating['resistance_ohm']*current)+rating['inductance_h']*derivative,0.)
    loss=rating['resistance_ohm']*current*current
    trace=[]
    if record_trace:
        for index in range(0,len(current),2):
            point=trajectory_at(t,float(sample['times'][index]));trace.append(dict(point,overlap_m=float(overlap[index]),current_a=float(current[index]),voltage_bound_v=float(voltage[index]),copper_loss_w=float(loss[index])))
    return dict(minimum_force_reserve_fraction=float(np.min(density*overlap[moving]/np.abs(demand[moving])-1)),peak_current_a=float(np.max(np.abs(current))),
        peak_voltage_bound_v=float(voltage.max()),peak_copper_loss_w=float(loss.max()),peak_force_n=float(np.max(np.abs(demand))),peak_speed_m_s=float(sample['speed'].max()),
        copper_heat_j=float(np.trapezoid(loss,sample['times'])),trace=trace,mechanical_input_j=sample['energy'][0],mechanical_recovered_j=sample['energy'][1])


@lru_cache(maxsize=4096)
def _evaluate(key):
    k=json.loads(key);c=k['c'];a=k['a'];p=c['power'];cars=k['cars'];mass=k['car_mass_kg']*cars
    t=profile(distance_m=k['distance_m'],runtime_s=k['runtime_s'],cars=cars,car_mass_kg=k['car_mass_kg'],mode=k['mode'])
    result=dict(schema='osr-fixed-corridor-screen/1',distance_m=k['distance_m'],runtime_s=k['runtime_s'],cars=cars,car_mass_kg=k['car_mass_kg'],load_case=k['load_case'],mode=k['mode'],
        motion_screen_pass=False,rating_screen_pass=False,service_energy_screen_pass=False,protection_screen_pass=False,capacity_screen_pass=False,study_pass=False,
        peak_speed_kmh=None,propulsion_input_kwh=None,recovered_energy_kwh=None,installed_zones=[],longitudinal_profile=t,headway_lower_bound_s=None,holds=[],
        physical_output_authorised=False,operational_geometry_confirmed=False,**FLAGS)
    if not t['study_pass']:result['holds']=[t['reason']];return result
    zones=_zones(t,a)
    if k['mode']=='suburban':
        # One installed booster serves all load cases at this common duty;
        # quantity/cost may not use only the shorter AW3 boost interval.
        masses=model.mass(c,c['mass']['ferrite_base'],k['battery_kwh']);starts=[];ends=[]
        for key in ('tare_kg','aw2_kg','aw3_kg'):
            alternative=profile(distance_m=k['distance_m'],runtime_s=k['runtime_s'],cars=cars,car_mass_kg=masses[key],mode=k['mode'])
            if alternative['study_pass']:
                zone=next(z for z in _zones(alternative,a) if z['id']=='booster');starts.append(zone['start_m']);ends.append(zone['end_m'])
        booster=next(z for z in zones if z['id']=='booster');booster.update(start_m=min(starts),end_m=max(ends))
        booster.update(length_m=booster['end_m']-booster['start_m'],electrical_sections=math.ceil((booster['end_m']-booster['start_m'])/a['electrical_section_m']))
    t['powered_zones']=zones
    rating=deepcopy(a['ratings'][k['motor_option']]);ratio=cars/6
    # Parallel equivalent banks: common back-EMF constant, current capacity and
    # loss capacity scale with banks, parallel R/L inversely. Not a winding map.
    rating.update(maximum_current_a=rating['maximum_current_a']*ratio,resistance_ohm=rating['resistance_ohm']/ratio,
        inductance_h=rating['inductance_h']/ratio,maximum_copper_loss_w=rating['maximum_copper_loss_w']*ratio)
    kf=rating['force_constant_n_a'];v=station.load()['vehicle'];length=cars*v['body_length_m']+(cars-1)*v['coupling_gap_m'];band=v['magnetic_band_m_per_car']
    offsets=np.array([[-(v['body_length_m']-band)/2-band-i*(v['body_length_m']+v['coupling_gap_m']),-(v['body_length_m']-band)/2-i*(v['body_length_m']+v['coupling_gap_m'])] for i in range(cars)])
    density=station.load()['station']['equivalent_envelope_force_n_m']*length/(band*cars)
    quantities=_motion_screen(encoded(t).decode(),encoded(rating).decode(),k['record_trace'])
    minimum_force_reserve=quantities['minimum_force_reserve_fraction'];peakcurrent=quantities['peak_current_a']
    peakvoltage=quantities['peak_voltage_bound_v'];peakloss=quantities['peak_copper_loss_w'];peakforce=quantities['peak_force_n'];peakv=quantities['peak_speed_m_s']
    copper_j=quantities['copper_heat_j'];trace=quantities['trace']
    propulsion=quantities['mechanical_input_j']/station.load()['motion']['motoring_efficiency']/3.6e6
    recovered=quantities['mechanical_recovered_j']*station.load()['motion']['generating_efficiency']/3.6e6
    travel_services=a['hot_services_kw_per_car']*(k['runtime_s']+k['dwell_s']*(1-a['connected_fraction']))/3600
    reserve=a['hot_services_kw_per_car']*a['protected_services_reserve_minutes']/60
    usable=k['battery_kwh']*p['eol_capacity_fraction']*(p['normal_soc_high']-p['normal_soc_low'])
    connected=k['dwell_s']*a['connected_fraction'];charge=(k['charger_kw']*a['charger_efficiency']-a['hot_services_kw_per_car'])*connected/3600
    service_pass=usable>=travel_services+reserve and charge>=travel_services
    # Release is a position/integrity event on the following departure. This
    # value is only a timing lower bound; the Rust replay retains actual locks.
    release_front=length+zones[-1]['end_m']-k['distance_m']+a['downstream_overlap_m']
    lo=0.;hi=min(k['runtime_s'],120.)
    if trajectory_at(t,hi)['position_m']<release_front:clear_time=None
    else:
        for _ in range(60):
            mid=(lo+hi)/2
            if trajectory_at(t,mid)['position_m']<release_front:lo=mid
            else:hi=mid
        clear_time=hi
    headway=None if clear_time is None else k['runtime_s']+k['dwell_s']+clear_time+a['release_allowance_s']
    motion=minimum_force_reserve>=0
    rated=peakcurrent<=rating['maximum_current_a'] and peakvoltage<=rating['maximum_phase_voltage_v'] and peakloss<=rating['maximum_copper_loss_w']
    capacity=headway is not None and headway<=a['requested_headway_s']
    for z in zones:z['converter_rating']=deepcopy(rating)
    holds=[]
    if not motion:holds.append('Finite installed powered-zone overlap cannot deliver demanded force')
    if not rated:holds.append('Equivalent motor current/voltage/copper bounds exceeded')
    if not service_pass:holds.append('Hotel services, protected reserve or charge replenishment fails')
    if not capacity:holds.append('Exclusive whole-leg arrival protection cannot sustain requested180s headway')
    holds.extend(['Operational moving geometry requires exact-profile numerical confirmation','Measured magnetic force/loss maps remain unqualified','Converter/winding, handover and independent recovery hardware remain unqualified'])
    result.update(motion_screen_pass=bool(motion),rating_screen_pass=bool(rated),service_energy_screen_pass=bool(service_pass),capacity_screen_pass=bool(capacity),
        peak_speed_kmh=peakv*3.6,propulsion_input_kwh=propulsion,recovered_energy_kwh=recovered,installed_zones=zones,longitudinal_profile=t,trace=trace,
        headway_lower_bound_s=headway,full_tail_clearance_time_after_next_departure_s=clear_time,holds=holds,motor_option=k['motor_option'],equivalent_motor=rating,
        minimum_force_reserve_fraction=minimum_force_reserve,peak_current_a=peakcurrent,peak_voltage_bound_v=peakvoltage,peak_copper_loss_w=peakloss,peak_force_n=peakforce,copper_heat_j=copper_j,
        service_energy=dict(battery_kwh_per_car=k['battery_kwh'],charger_kw_per_car=k['charger_kw'],dwell_s=k['dwell_s'],connected_s=connected,
            usable_kwh_per_car=usable,trip_hotel_kwh_per_car=travel_services,protected_reserve_kwh_per_car=reserve,replenished_kwh_per_car=charge,screen_pass=bool(service_pass)),
        powered_length_m_per_direction=sum(z['length_m'] for z in zones),stator_allowance_usd_two_directions=2*sum(z['length_m'] for z in zones)*a['stator_allowance_usd_per_direction_m'],
        costs_are_quotes=False,capacity_basis='Exclusive corridor+arrival berth+overlap retained until synthetic full-consist clearance; no section pipeline or distributed guarantee')
    return result


def request(screen,*,fault=None,indexing_spread_m=0.):
    """Finite sections and one protected whole-leg arrival, then full tail clear.

    The booster lies inside the exclusively reserved corridor resource. Two
    successive three-resource bundles share one local controller; this does not
    establish a distributed or pipelined whole-line control system.
    """
    from . import system_campaign
    a=load();t=screen['longitudinal_profile'];i=t['inputs'];zones=screen['installed_zones'];rating=screen['equivalent_motor']
    if not t['study_pass'] or not 0<=indexing_spread_m<=.05:raise ValueError('feasible corridor profile and bounded indexing envelope required')
    v=station.load()['vehicle'];cars=i['cars'];length=cars*v['body_length_m']+(cars-1)*v['coupling_gap_m'];distance=i['distance_m'];step=a['step_s']
    density=station.load()['station']['equivalent_envelope_force_n_m']*length/(cars*v['magnetic_band_m_per_car'])
    motors=[dict(id=index+1,start_mm=round(z['start_m']*1000),end_mm=round(z['end_m']*1000),
        origin_mm=round((0. if z['id']=='departure' else distance if z['id']=='arrival' else distance/2)*1000),
        force_density_n_m=density,force_constant_n_a=rating['force_constant_n_a'],resistance_ohm=rating['resistance_ohm'],inductance_h=rating['inductance_h'],
        maximum_current_a=rating['maximum_current_a'],maximum_voltage_v=900. if fault=='legacy-voltage' else rating['maximum_phase_voltage_v'],maximum_copper_loss_w=rating['maximum_copper_loss_w']) for index,z in enumerate(zones)]
    cfg=list(sha256(encoded([screen['longitudinal_profile'],motors,screen['service_energy']])).digest())
    deployment=system_campaign.deployment(cfg,round(length*1000),distance)
    left=zones[-1]['start_m']-distance;right=zones[-1]['end_m']-distance;overlap=a['downstream_overlap_m']
    ends=[0,distance+left,distance+right,distance+right+overlap,2*distance+left,2*distance+right,2*distance+right+overlap]
    for segment,start,end in zip(deployment['routes'][0]['segments'],ends,ends[1:]):segment.update(start_mm=round(start*1000),end_mm=round(end*1000))
    deployment['revision']='fixed-line-two-arrival-corridor';deployment['routes'][0]['operating_scope']='Fixed independent line; one local controller, exclusively protected corridor and two arrivals. Midpoint booster is a physical asset inside the corridor, not a passenger stop or junction switch.'
    dwell=screen['service_energy']['dwell_s'];arming=a['initial_arming_s'];release=distance+right+overlap+length
    frames=[];was_clear=False
    for index in range(math.ceil((arming+i['runtime_s']+dwell+100)/step)+1):
        elapsed=index*step-arming;outgoing=elapsed>=i['runtime_s']+dwell
        if elapsed<0:point=dict(position_m=0.,speed_m_s=0.,motor_force_n=0.,phase='secured',zone_id='departure');mode=3
        elif elapsed<i['runtime_s']:
            point=trajectory_at(t,elapsed);mode={'launch':0,'coast':1,'booster':0,'braking':2}[point['phase']]
        elif not outgoing:point=dict(position_m=distance,speed_m_s=0.,motor_force_n=0.,phase='secured',zone_id='arrival');mode=3
        else:
            point=trajectory_at(t,min(i['runtime_s'],elapsed-i['runtime_s']-dwell));point=dict(point,position_m=point['position_m']+distance,zone_id='arrival' if point['phase']=='launch' else None)
            mode={'launch':0,'coast':1,'booster':0,'braking':2}[point['phase']]
        zone=next((index+1 for index,z in enumerate(zones) if z['id']==point['zone_id']),0)
        if mode==2 and point['motor_force_n']>0:
            if point['speed_m_s']>.5 or abs(point['position_m']-distance)>2:raise ValueError('receiving positive force exceeds bounded berth')
            mode=4
        observed=point
        if 0<=elapsed<i['runtime_s']:
            observed=trajectory_at(t,max(0.,elapsed-50e-6))
        elif outgoing:
            local=max(0.,elapsed-i['runtime_s']-dwell-50e-6)
            observed=trajectory_at(t,min(i['runtime_s'],local));observed=dict(observed,position_m=observed['position_m']+distance)
        now=system_campaign.BASE+1_000_000+round(index*step*1e9)
        clear=bool(outgoing and observed['position_m']>release)
        frame=dict(now_ns=now,observed_ns=now-50_000,sequence=index+1,active_zone=zone,mode=mode,
            position_mm=round(observed['position_m']*1000),velocity_mmps=round(observed['speed_m_s']*1000),force_n=point['motor_force_n'],
            position_uncertainty_um=600+math.ceil(indexing_spread_m*1e6),timestamp_uncertainty_ns=1000,
            receiver_healthy=True,sensors_healthy=True,resistor_ready=True,failed_zone=0,extra_warmup_ns=0,outgoing=outgoing,full_tail_clear=clear and not was_clear)
        trigger=point['phase']=='booster' if fault in {'booster-loss','grid-loss','handover-delay'} else point['phase']=='braking'
        if trigger:
            if fault in {'booster-loss','grid-loss'}:frame['failed_zone']=zone
            elif fault=='handover-delay':frame['extra_warmup_ns']=10_000_000_000
            elif fault=='resistor-loss':frame['resistor_ready']=False
            elif fault=='stale-observation':frame['observed_ns']=now-200_000
        frames.append(frame);was_clear=clear
        if clear:break
    if len(frames)>100000 or len(encoded(frames))>60*1024*1024:raise ValueError('bounded corridor frame budget required')
    return dict(model=deployment,configuration=cfg,motors=motors,geometry=dict(cars=cars,body_mm=round(v['body_length_m']*1000),gap_mm=round(v['coupling_gap_m']*1000),
        band_mm=round(v['magnetic_band_m_per_car']*1000),section_mm=round(a['electrical_section_m']*1000),warmup_ns=round(a['section_warmup_s']*1e9),lookahead_ns=round(a['section_lookahead_s']*1e9),
        maximum_tick_ns=round(step*1e9)+10,downstream_overlap_mm=round(overlap*1000)),frames=frames,initial_commit=fault!='uncommitted')


def build_replay():
    process=subprocess.run(BUILD,cwd=ROOT,check=True,capture_output=True,text=True,timeout=180)
    artifacts=[json.loads(line) for line in process.stdout.splitlines()]
    paths=[Path(v['executable']) for v in artifacts if v.get('reason')=='compiler-artifact' and v.get('target',{}).get('name')=='corridor_replay' and v.get('executable')]
    if len(paths)!=1 or not paths[0].is_file():raise ValueError('actual corridor Rust compiler artifact required')
    return paths[0],dict(command=BUILD,exit_status=process.returncode,binary_sha256=digest(paths[0].read_bytes()),
        rustc=subprocess.run(['rustc','--version'],check=True,capture_output=True,text=True,timeout=30).stdout.strip())


def replay(binary,screen,*,fault=None,indexing_spread_m=0.):
    packet=request(screen,fault=fault,indexing_spread_m=indexing_spread_m)
    _remember_request(screen,fault,indexing_spread_m,packet)
    process=subprocess.run([str(binary)],input=encoded(packet),capture_output=True,check=True,timeout=120)
    value=json.loads(process.stdout)
    if (value.get('schema')!='osr-fixed-corridor-rust-replay/1' or value.get('configuration')!=packet['configuration']
            or value.get('physical_output_authorised') is not False or not 0<value['executed_frames']<=len(packet['frames'])):raise ValueError('actual bounded Rust corridor replay identity differs')
    success=value['first_fault'] is None and value['incoming_cleared'] and value['outgoing_committed'] and value['executed_frames']==len(packet['frames']) and value['power_conservation_max_residual_w']<1e-6
    expected=bool(success) if fault is None else bool(value['fault_held'] and value['first_fault'] is not None and not value['incoming_cleared'] and (value['incoming_protected'] or fault=='uncommitted'))
    return dict(fault=fault,expected_behavior_pass=expected,executed=bool(process.returncode==0),exit_status=process.returncode,
        request_sha256=digest(encoded(packet)),indexing_spread_m=indexing_spread_m,frames_requested=len(packet['frames']),request_geometry=packet['geometry'],request_motors=packet['motors'],
        raw_replay=value,physical_output_authorised=False,**FLAGS)


def _request_key(screen,fault,spread):
    return digest(encoded([screen['longitudinal_profile'],screen['equivalent_motor'],screen['installed_zones'],screen['service_energy'],fault,spread]))


def _remember_request(screen,fault,spread,packet):
    key=_request_key(screen,fault,spread)
    value=dict(sha256=digest(encoded(packet)),configuration=packet['configuration'],frames=len(packet['frames']))
    _REQUEST_IDENTITIES[key]=value;_REQUEST_IDENTITIES.move_to_end(key)
    while len(_REQUEST_IDENTITIES)>128:_REQUEST_IDENTITIES.popitem(last=False)
    return value


def check_replay_identity(record,screen,fault,spread):
    key=_request_key(screen,fault,spread)
    identity=_REQUEST_IDENTITIES.get(key)
    if identity is None:identity=_remember_request(screen,fault,spread,request(screen,fault=fault,indexing_spread_m=spread))
    raw=record['raw_replay']
    if (record.get('fault')!=fault or record.get('indexing_spread_m')!=spread or record.get('request_sha256')!=identity['sha256']
            or raw.get('configuration')!=identity['configuration'] or record.get('frames_requested')!=identity['frames']):raise ValueError('exact corridor replay request/fault/configuration differs')
    success=bool(raw['first_fault'] is None and raw['incoming_cleared'] and raw['outgoing_committed'] and raw['executed_frames']==identity['frames'] and raw['power_conservation_max_residual_w']<1e-6)
    expected=success if fault is None else bool(raw['first_fault'] is not None and raw['fault_held'] and not raw['incoming_cleared'] and (raw['incoming_protected'] or fault=='uncommitted'))
    if not expected or record.get('expected_behavior_pass') is not True or (fault=='uncommitted' and (raw['first_fault']['sequence']!=1 or raw['outgoing_committed'])):raise ValueError('actual corridor replay fault/clearance behavior differs')


def check_moving_identity(role,run,profile):
    from . import moving_train
    expected=deepcopy(moving_train.load())
    if role.endswith('nominal'):factor,bias=1.,0.
    else:factor,bias=.85,-.0005 if role.endswith('negative-bias') else .0005
    expected.update(beam_modulus_pa=expected['beam_modulus_pa']*factor,sensor_bias_m=bias,
        runtime_s=profile['inputs']['runtime_s'],car_mass_kg=profile['inputs']['car_mass_kg'],operational_profile_sha256=digest(encoded(profile)))
    if role.endswith(('rejected-2.2m','lighter-2.4m-comparison')):
        depth=2.2 if role.endswith('rejected-2.2m') else 2.4;section=dict(expected['beam_section_m'],depth=depth)
        expected.update(beam_section_m=section,beam_vertical_inertia_m4=model.section(section['width'],depth,section['web'],section['flange'])['vertical_i_m4'],
            guideway_line_mass_kg_m=moving_train.geometry.guideway_quantities(25.,**section)['total_line_mass_kg_m'])
    if run.get('assumptions')!=expected or run.get('candidate_sha256')!=digest(encoded(expected)):raise ValueError('exact mandatory moving role assumptions/revision differ')


def _moving_case(job):
    from . import moving_train
    executable,a,profile,role=job
    run=moving_train.simulate(Path(executable),assumptions=a,profile=profile)
    return dict(role=role,profile_sha256=digest(encoded(profile)),run=run)


def study():
    from . import moving_train
    a=load();_,c,_=model.load();binary,execution=build_replay();bridge,bridge_execution=moving_train.build_bridge()
    operations={mode:evaluate(c,distance_m=distance,cars=6,mode=mode,runtime_s=runtime,battery_kwh=50.,charger_kw=charger,dwell_s=dwell,record_trace=True)
        for mode,distance,runtime,charger,dwell in [('urban',2000.,140.,400.,60.),('suburban',5000.,375.,600.,96.)]}
    faster=evaluate(c,distance_m=5000.,cars=6,mode='suburban',runtime_s=300.,battery_kwh=50.,charger_kw=600.,record_trace=True)
    faster_holds={case:evaluate(c,distance_m=5000.,cars=6,mode='suburban',runtime_s=300.,battery_kwh=50.,charger_kw=600.,load_case=case) for case in ('AW0','AW2')}
    energy=[];ratings=[]
    for mode,distance,runtime in [('urban',2000.,140.),('suburban',5000.,375.)]:
        for pack in (30.,50.,60.):
            for charger,dwell in ((240.,240.),(400.,120.),(600.,96.)):
                energy.append(evaluate(c,distance_m=distance,cars=6,mode=mode,runtime_s=runtime,battery_kwh=pack,charger_kw=charger,dwell_s=dwell))
        for load_case in ('AW0','AW2','AW3'):
            for option in ('legacy','lower-force-constant','higher-voltage'):
                ratings.append(evaluate(c,distance_m=distance,cars=6,mode=mode,runtime_s=runtime,battery_kwh=50.,charger_kw=400. if mode=='urban' else 600.,dwell_s=60. if mode=='urban' else 96.,load_case=load_case,motor_option=option))
    jobs=[]
    for mode,screen in operations.items():
        for role,bias,factor in [('nominal',0.,1.),('reduced-E-positive-bias',.0005,.85),('reduced-E-negative-bias',-.0005,.85)]:
            assumption=deepcopy(moving_train.load());assumption.update(sensor_bias_m=bias,beam_modulus_pa=assumption['beam_modulus_pa']*factor)
            jobs.append((str(bridge),assumption,screen['longitudinal_profile'],mode+'/'+role))
    # Retain the failed previous geometry and the lighter passing alternative;
    # neither can erase mandatory confirmation failures of the selected design.
    for depth,role in ((2.2,'suburban/rejected-2.2m'),(2.4,'suburban/lighter-2.4m-comparison')):
        assumption=deepcopy(moving_train.load());section=dict(assumption['beam_section_m'],depth=depth)
        assumption.update(beam_section_m=section,beam_modulus_pa=assumption['beam_modulus_pa']*.85,sensor_bias_m=.0005,
            beam_vertical_inertia_m4=model.section(section['width'],depth,section['web'],section['flange'])['vertical_i_m4'],
            guideway_line_mass_kg_m=moving_train.geometry.guideway_quantities(25.,**section)['total_line_mass_kg_m'])
        jobs.append((str(bridge),assumption,faster['longitudinal_profile'],role))
    with ProcessPoolExecutor(max_workers=4) as pool:moving={value['role']:value for value in pool.map(_moving_case,jobs)}
    replays={}
    for mode,screen in operations.items():
        spread=max(moving[mode+'/'+role]['run']['maximum_longitudinal_relative_spread_m'] for role in ('nominal','reduced-E-positive-bias','reduced-E-negative-bias'))
        for load_case in ('AW0','AW2','AW3'):
            case=evaluate(c,distance_m=screen['distance_m'],cars=6,mode=mode,runtime_s=screen['runtime_s'],battery_kwh=50.,charger_kw=400. if mode=='urban' else 600.,dwell_s=60. if mode=='urban' else 96.,load_case=load_case)
            replays[mode+'/'+load_case]=replay(binary,case,indexing_spread_m=spread)
        for fault in (FAULTS if mode=='suburban' else ('legacy-voltage',)):
            replays[mode+'/'+fault]=replay(binary,screen,fault=fault,indexing_spread_m=spread)
    numeric=all(value['expected_behavior_pass'] for value in replays.values())
    for mode,screen in operations.items():
        selected=[moving[mode+'/'+role]['run'] for role in ('nominal','reduced-E-positive-bias','reduced-E-negative-bias')]
        confirmed=all(moving_train.confirmation_eligible(run) and run['completed_moving_steps']==run['planned_moving_steps'] for run in selected)
        numeric &= confirmed
        screen.update(operational_geometry_confirmed=bool(confirmed),protection_screen_pass=bool(replays[mode+'/AW3']['expected_behavior_pass']),
            moving_candidate_sha256=selected[0]['candidate_sha256'],mandatory_moving_candidate_sha256=[run['candidate_sha256'] for run in selected[1:]],
            maximum_indexing_spread_m=max(run['maximum_longitudinal_relative_spread_m'] for run in selected))
        if confirmed:screen['holds']=[hold for hold in screen['holds'] if hold!='Operational moving geometry requires exact-profile numerical confirmation']
    return dict(schema='osr-fixed-corridor-study/1',assumptions=a,configuration_revision=configuration.selected().revision,operations=operations,
        energy_alternatives=energy,rating_alternatives=ratings,moving=moving,replays=replays,execution=execution,moving_execution=bridge_execution,
        faster_suburban_benchmark=faster,faster_load_holds=faster_holds,
        executed_numerical_study_pass=bool(numeric),study_pass=False,
        inertia_scope='Independent unqualified rigid-body hypotheses: roll20000kg m2 and pitch600000kg m2 retained across pack masses. No measured mass distribution, pack CG or actual body inertia is claimed.',
        capacity_accepted=False,physical_output_authorised=False,**FLAGS,
        scope='Executed longer-profile numerical plants with actual Rust finite-section and local resource controls.180s whole-leg headway and engineering/physical release remain held.',
        research=[dict(url='https://dgjsxb.ces-transaction.com/EN/10.19595/j.cnki.1000-6753.tces.201570',
            basis='Zhao et al.2022 segmented long-stator PMLSM changeover/feeder-voltage control precedent; no force, cost or hardware validation credit')])


def _overview(result):
    rows=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="580" viewBox="0 0 1200 580"><rect width="1200" height="580" fill="#f4f8fc"/>',
        '<text x="40" y="36" font-size="22">Fixed-line urban and suburban powered zones — provisional numerical study</text>']
    for number,(mode,screen) in enumerate(result['operations'].items()):
        y=100+number*220;distance=screen['distance_m'];scale=1050/(distance+500)
        rows.append(f'<text x="40" y="{y}" font-size="18">{mode}: {distance:g}m / {screen["runtime_s"]:g}s — exclusive-block headway ≥{screen["headway_lower_bound_s"]:.1f}s</text>')
        rows.append(f'<path d="M50 {y+65} H1150" stroke="#61778b" stroke-width="5"/>')
        for zone in screen['installed_zones']:
            x=50+(zone['start_m']+200)*scale;width=zone['length_m']*scale;colour='#df8f35' if zone['kind']=='top-up' else '#139582'
            rows.append(f'<rect x="{x:.2f}" y="{y+45}" width="{width:.2f}" height="40" fill="{colour}"/><text x="{x:.2f}" y="{y+115}" font-size="14">{zone["id"]} {zone["length_m"]:g}m</text>')
    rows.append('<text x="40" y="545" font-size="15">Passenger transfers remain between independent fixed lines. No train-routing switch; no180s capacity or physical acceptance claim.</text></svg>')
    return '\n'.join(rows)


def publish(output=OUTPUT):
    from . import moving_train
    before=sources();result=study();result['source_sha256']=before
    if sources()!=before:raise ValueError('corridor sources changed during executed study')
    output=Path(output)
    if output.is_symlink():raise ValueError('ordinary corridor output required')
    output.mkdir(parents=True,exist_ok=True)
    if any(p.is_symlink() for p in output.iterdir()) or {p.name for p in output.iterdir()}-FILES-{'manifest.json'}:raise ValueError('unexpected corridor output')
    (output/'result.json.gz').write_bytes(gzip.compress(encoded(result),mtime=0));(output/'overview.svg').write_text(_overview(result))
    for mode in ('urban','suburban'):
        with tempfile.TemporaryDirectory(prefix='osr-corridor-media-') as temporary:
            folder=Path(temporary);moving_train.render(dict(moving_run=result['moving'][mode+'/nominal']['run']),folder)
            for old,new in [('overview.png','overview.png'),('moving-train.mp4','motion.mp4'),('visual-receipt.json','visual-receipt.json')]:
                (output/f'{mode}-{new}').write_bytes((folder/old).read_bytes())
    (output/'README.md').write_text('\n'.join(['# Fixed-line urban and suburban operational studies','',
        '![Exact installed zones](overview.svg)','',
        '[Urban moving geometry](urban-motion.mp4) · [Suburban moving geometry](suburban-motion.mp4) · [Raw executed evidence](result.json.gz) · [Receipt](manifest.json)','',
        'Two separate exact profiles are executed:2km/140s urban and5km/375s suburban with a finite midpoint LSM booster and96s suburban dwell. Both use350m station windings; booster extent covers all three load cases. The faster300s AW3 suburban benchmark retains its AW0/AW2 speed-limit failures. The booster is an installed nonpassenger asset; passenger transfers occur between independent fixed lines. The1km/88s packets remain explicit benchmarks.','',
        'Three rigid-body moving confirmations per profile retain nominal stiffness and reduced-E/signed sensor bias. The previous2.2m failure and lighter2.4m comparison remain visible. Actual Rust controls evaluate finite electrical sections, warm-up, phase/current/voltage/copper bounds and resource holds.900V, booster/grid/resistor, delayed handover, stale sensing and uncommitted cases are executed.50/60kWh packs and240/400/600kW charging alternatives retain60kW/car hotel load and ten-minute reserve.','',
        'Rigid-body inertias remain independent unqualified hypotheses (roll20,000kg·m² and pitch600,000kg·m²), even when the exact battery mass changes. No measured pack position, CG or complete mass distribution is claimed.','',
        '**Held:**180s capacity under exclusive whole-leg arrival reservations. Geometry confirmation is a bounded linear/ideal-force numerical result; measured magnet/winding maps, new converter ratings, flexible bodies, lateral/torsion, soil/joints/fatigue, rescue hardware, alignment and physical acceptance remain open. No manufacturing or physical release is claimed.','']))
    if sources()!=before:raise ValueError('corridor sources changed during presentation')
    manifest=dict(schema='osr-fixed-corridor-publication/1',source_sha256=before,
        files_sha256={name:digest((output/name).read_bytes()) for name in sorted(FILES)},physical_output_authorised=False,**FLAGS)
    (output/'manifest.json').write_bytes(encoded(manifest));return verify(output)


def verify(output=OUTPUT):
    from . import moving_train
    output=Path(output)
    if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()}!=FILES|{'manifest.json'}:raise ValueError('exact corridor inventory required')
    if any(p.is_symlink() or p.stat().st_size>64*1024*1024 for p in output.iterdir()):raise ValueError('bounded ordinary corridor payload required')
    manifest=json.loads((output/'manifest.json').read_bytes())
    if manifest.get('schema')!='osr-fixed-corridor-publication/1' or manifest.get('source_sha256')!=sources() or set(manifest.get('files_sha256',{}))!=FILES:raise ValueError('corridor source or payload inventory differs')
    if any(digest((output/name).read_bytes())!=sha for name,sha in manifest['files_sha256'].items()):raise ValueError('corridor payload changed')
    with gzip.open(output/'result.json.gz','rb') as stream:raw=stream.read(MAX_RAW+1)
    if len(raw)>MAX_RAW:raise ValueError('bounded corridor decompression required')
    result=json.loads(raw)
    if result.get('schema')!='osr-fixed-corridor-study/1' or result.get('source_sha256')!=manifest['source_sha256'] or result.get('assumptions')!=load():raise ValueError('corridor execution inputs differ')
    if result['execution'].get('command')!=BUILD or result['execution'].get('exit_status')!=0 or len(result['execution'].get('binary_sha256',''))!=64:raise ValueError('actual Rust compilation receipt required')
    expected_moving={mode+'/'+role for mode in ('urban','suburban') for role in ('nominal','reduced-E-positive-bias','reduced-E-negative-bias')}|{'suburban/rejected-2.2m','suburban/lighter-2.4m-comparison'}
    expected_replay={mode+'/'+load for mode in ('urban','suburban') for load in ('AW0','AW2','AW3')}|{'urban/legacy-voltage'}|{'suburban/'+fault for fault in FAULTS}
    if set(result.get('moving',{}))!=expected_moving or set(result.get('replays',{}))!=expected_replay or set(result.get('operations',{}))!={'urban','suburban'}:raise ValueError('mandatory corridor confirmations/counterexamples omitted')
    records=[manifest,result,*result['operations'].values(),*result['energy_alternatives'],*result['rating_alternatives'],*result['replays'].values(),
        result['faster_suburban_benchmark'],*result['faster_load_holds'].values()]
    nominal=moving_train.load()
    for role,evidence in result['moving'].items():
        run=evidence['run'];records.append(run);mode=role.split('/')[0];screen=result['faster_suburban_benchmark'] if role.endswith(('rejected-2.2m','lighter-2.4m-comparison')) else result['operations'][mode]
        if (evidence['profile_sha256']!=digest(encoded(screen['longitudinal_profile'])) or run['trajectory']!=screen['longitudinal_profile']
                or run['formation']['car_mass_kg']!=screen['car_mass_kg'] or run['formation']['cars']!=6):raise ValueError('operational moving profile/formation differs')
        check_moving_identity(role,run,screen['longitudinal_profile'])
        if role.endswith(('nominal','positive-bias','negative-bias')):
            if run['assumptions']['beam_section_m']!=nominal['beam_section_m'] or run['assumptions']['guideway_span_m']!=nominal['guideway_span_m']:raise ValueError('operational moving geometry differs from selected common design')
            if (not moving_train.confirmation_eligible(run) or run['completed_moving_steps']!=run['planned_moving_steps'] or not run['trace']
                    or abs(run['trace'][-1]['time_s']-screen['runtime_s'])>1e-8
                    or not nominal['gap_minimum_m']<=run['minimum_gap_m']<=run['maximum_gap_m']<=nominal['gap_maximum_m']):raise ValueError('mandatory operational moving confirmation failed or incomplete')
        if run['candidate_sha256']!=digest(encoded(run['assumptions'])):raise ValueError('operational moving revision differs')
    for record in records:
        if any(record.get(flag) is not False for flag in FLAGS):raise ValueError('corridor cannot authorize release')
        if 'physical_output_authorised' in record and record['physical_output_authorised'] is not False:raise ValueError('corridor cannot authorize physical outputs')
    for key,replay_record in result['replays'].items():
        if replay_record.get('exit_status')!=0 or replay_record.get('executed') is not True or replay_record.get('expected_behavior_pass') is not True or replay_record['raw_replay'].get('physical_output_authorised') is not False:raise ValueError('actual corridor replay evidence failed')
        mode,label=key.split('/');fault=None if label in {'AW0','AW2','AW3'} else label
        if fault is None:
            candidates=[screen for screen in result['rating_alternatives'] if screen['mode']==mode and screen['load_case']==label and screen.get('motor_option')=='higher-voltage']
            if len(candidates)!=1:raise ValueError('exact load/rating case missing')
            screen=candidates[0]
        else:screen=result['operations'][mode]
        check_replay_identity(replay_record,screen,fault,result['operations'][mode]['maximum_indexing_spread_m'])
    if result.get('executed_numerical_study_pass') is not True or result.get('study_pass') is not False or result.get('capacity_accepted') is not False:raise ValueError('corridor capacity/release scope differs')
    for mode in ('urban','suburban'):
        screen=result['operations'][mode];run=result['moving'][mode+'/nominal']['run'];visual=json.loads((output/f'{mode}-visual-receipt.json').read_bytes())
        if (visual.get('retained_trace_sha256')!=digest(encoded(run['trace'])) or visual.get('candidate_sha256')!=run['candidate_sha256']
                or visual.get('renderer_sha256')!=manifest['source_sha256']['engineering/ferrite_maglev/moving_train.py']
                or visual.get('files_sha256')!={'overview.png':manifest['files_sha256'][f'{mode}-overview.png'],'moving-train.mp4':manifest['files_sha256'][f'{mode}-motion.mp4']}):raise ValueError('operational moving visual provenance differs')
        if any(visual.get(flag) is not False for flag in FLAGS):raise ValueError('operational visual cannot authorize release')
        if (not screen['protection_screen_pass'] or not screen['operational_geometry_confirmed'] or screen['capacity_screen_pass']
                or screen['headway_lower_bound_s']<=load()['requested_headway_s']):raise ValueError('corridor protection/capacity scope differs')
    return manifest


def read_summary(output=OUTPUT):
    receipt=verify(output)
    with gzip.open(Path(output)/'result.json.gz','rt') as stream:value=json.load(stream)
    operations={}
    for mode,screen in value['operations'].items():
        operations[mode]={key:deepcopy(screen[key]) for key in ('distance_m','runtime_s','cars','car_mass_kg','load_case','peak_speed_kmh','installed_zones',
            'motion_screen_pass','rating_screen_pass','service_energy_screen_pass','protection_screen_pass','capacity_screen_pass','operational_geometry_confirmed',
            'headway_lower_bound_s','propulsion_input_kwh','recovered_energy_kwh','service_energy','holds','moving_candidate_sha256','mandatory_moving_candidate_sha256','maximum_indexing_spread_m')}
    return dict(schema='osr-fixed-corridor-summary/1',operations=operations,executed_numerical_study_pass=value['executed_numerical_study_pass'],
        inertia_scope=value['inertia_scope'],
        study_pass=False,capacity_accepted=False,configuration_revision=value['configuration_revision'],source_sha256=receipt['source_sha256'],
        manifest_sha256=digest((Path(output)/'manifest.json').read_bytes()),physical_output_authorised=False,**FLAGS)
