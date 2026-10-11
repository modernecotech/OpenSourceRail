"""Original readers and verification experiments informed by OSRD open examples.

Schema 3.3 rolling-stock resistance is per mass; older raw force coefficients
are not silently interpreted as the same units. Open mock curves never replace
an OSR train's compiled geometry, mass or supplier slots.
"""
from pathlib import Path
import hashlib,json,math
import numpy as np
from engineering.industrialisation.common import finite,fingerprint

DATA=Path(__file__).parent/'data/osrd'


def retained_example():
    raw=(DATA/'commuter-train.json').read_bytes();meta=json.loads((DATA/'provenance.json').read_text())
    if hashlib.sha256(raw).hexdigest()!=meta['sha256']:raise ValueError('retained OSRD example changed')
    if hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=meta['git_blob_sha1']:raise ValueError('upstream OSRD blob identity differs')
    value=json.loads(raw)
    if value['railjson_version']!='3.3' or value['rolling_resistance']['type']!='davis':raise ValueError('unsupported OSRD units/schema')
    return value,meta


def effort(stock,speed_m_s,*,mode=None,comfort=None,electrical_profile=None,power_restriction=None):
    speed=finite(speed_m_s,'effort speed',0.);mode=mode or stock['effort_curves']['default_mode']
    if mode not in stock['effort_curves']['modes']:raise ValueError('unsupported traction power mode')
    selected=stock['effort_curves']['modes'][mode];matches=[]
    for row in selected['curves']:
        cond=row['cond']
        if cond.get('comfort')==comfort and cond.get('electrical_profile_level')==electrical_profile and cond.get('power_restriction_code')==power_restriction:matches.append(row['curve'])
    if len(matches)>1:raise ValueError('ambiguous conditional effort curve')
    # Explicit unmatched conditions cannot silently use another operating case.
    if not matches and any(v is not None for v in (comfort,electrical_profile,power_restriction)):raise ValueError('unsupported conditional effort curve')
    curve=matches[0] if matches else selected['default_curve'];v=np.asarray(curve['speeds'],float);F=np.asarray(curve['max_efforts'],float)
    if v.ndim!=1 or F.shape!=v.shape or len(v)<2 or not np.isfinite(v).all() or not np.isfinite(F).all() or np.any(np.diff(v)<=0) or np.any(F<0):raise ValueError('invalid effort curve')
    if speed>min(stock['max_speed'],v[-1]) or speed<v[0]:raise ValueError('effort request outside retained curve')
    return float(np.interp(speed,v,F))


def resistance(stock,speed_m_s):
    if stock['railjson_version']!='3.3':raise ValueError('explicit resistance-unit conversion required for another schema')
    speed=abs(finite(speed_m_s,'resistance speed'));p=stock['rolling_resistance']
    if p['type']!='davis':raise ValueError('unsupported resistance type')
    A,B,C=(finite(p[k],'Davis '+k,0.) for k in ('A','B','C'))
    return finite(stock['mass'],'example mass',1.)*(A+B*speed+C*speed*speed)


def tail_speed_limit(head_station_m,train_length_m,sections,*,rolling_stock_limit_m_s):
    head=finite(head_station_m,'head station');length=finite(train_length_m,'train length',1e-6);limit=finite(rolling_stock_limit_m_s,'stock speed',0.)
    for s in sections:
        begin=finite(s['begin_m'],'speed-section begin');end=finite(s['end_m'],'speed-section end');v=finite(s['speed_m_s'],'section speed',0.)
        if begin>=end:raise ValueError('ordered speed section required')
        # The restriction remains until the tail clears its downstream boundary.
        if head>=begin and head-length<end:limit=min(limit,v)
    return limit


def acceleration_experiment(stock,*,duration_s=60.,dt_s=.1,gradient_m_per_km=0.):
    dt=finite(dt_s,'longitudinal step',1e-4);duration=finite(duration_s,'duration',dt);gradient=finite(gradient_m_per_km,'gradient')
    if duration/dt>100000:raise ValueError('longitudinal experiment step budget exceeded')
    mass=finite(stock['mass'],'mass',1.);effective=mass*finite(stock['inertia_coefficient'],'inertial multiplier',1.)
    maximum=min(stock['max_speed'],max(stock['effort_curves']['modes'][stock['effort_curves']['default_mode']]['default_curve']['speeds']))
    state=np.array([0.,0.]);history=[];hill=mass*9.81*math.sin(math.atan(gradient/1000.))
    def rhs(y):
        v=float(y[1])
        if v<0 or v>maximum:raise ValueError('longitudinal trajectory exits retained effort domain')
        return np.array([v,(effort(stock,v)-resistance(stock,v)-hill)/effective])
    for i in range(math.ceil(duration/dt)):
        h=min(dt,duration-i*dt);k1=rhs(state);k2=rhs(state+h*k1/2);k3=rhs(state+h*k2/2);k4=rhs(state+h*k3)
        state=state+h*(k1+2*k2+2*k3+k4)/6;rhs(state)
        history.append(dict(time_s=min(duration,(i+1)*dt),position_m=float(state[0]),speed_m_s=float(state[1]),effort_n=effort(stock,float(state[1])),resistance_n=resistance(stock,float(state[1]))))
    return dict(schema='osr-osrd-example-verification/1',example_sha256=fingerprint(stock),history=history,gradient_m_per_km=gradient,
        source_scope='original RK4 acceleration experiment with retained fictional OSRD effort/resistance data; not an OSRD core execution or timetable envelope',
        full_spatial_force_feedback=False,physical_validation=False,engineering_released=False)
