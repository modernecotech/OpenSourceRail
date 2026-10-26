"""Readiness joins require the exact physical subject and scoped evidence."""
from copy import deepcopy
from hashlib import sha256
import json
import math
import re
from . import FLAGS

GATES={
 'mass':'Complete equipped geometry, installed BOM, load-case mass, CG and inertia',
 'suspension':'Converged three-dimensional support/guidance maps and operating reserve',
 'control':'Stable multiaxis operation, disturbance rejection and fault response',
 'electrical':'Current, voltage, energy and repeated thermal duty including 50°C HVAC',
 'structure':'Equipped stress, buckling, joints, fatigue, prestress and flexible modes',
 'civil':'Matching facing, anchors, beam deformation, piers and ground-specific loads',
 'operations':'Physical journey, protected headway, dwell and accessible transfers',
 'economics':'Same-configuration installed CAPEX, OPEX, renewal and financing at equal service'}
STATES={'pass','fail','unknown'}
MATURITIES={'definition','analytical-estimate','verified-simulation','correlated-measurement'}


def encoded(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def identity(value):return sha256(encoded(value)).hexdigest()


def digest(value,label):
    if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{64}',value):raise ValueError('explicit SHA256 '+label+' required')
    return value


def gate(name,state,reason,*,evidence=(),maturity='definition',values=None):
    if name not in GATES or state not in STATES or not isinstance(reason,str) or not reason.strip():
        raise ValueError('explained typed readiness gate required')
    if maturity not in MATURITIES:raise ValueError('declared evidence maturity required')
    if state=='pass' and maturity=='definition':raise ValueError('definition alone cannot pass an engineering gate')
    if state=='pass' and not evidence:raise ValueError('passing gate requires evidence')
    return dict(id=name,criterion=GATES[name],state=state,reason=reason,evidence=list(evidence),
                evidence_maturity=maturity,values=deepcopy(values or {}),physical_acceptance='unknown')


def require_subject(record,composition,scope):
    """A component result is not automatically a complete vehicle result."""
    keys={'composition':'candidate_id','body':'body_candidate_id','magnet':'magnet_component_id'}
    if scope not in keys:raise ValueError('declared physical evidence scope required')
    key=keys[scope];expected=digest(composition[key],key)
    if record.get(key)!=expected:raise ValueError(scope+' evidence belongs to a different physical configuration')
    return record


def candidate(composition,gates):
    for key in ('candidate_id','body_candidate_id','magnet_component_id'):digest(composition[key],key)
    if len(gates)!=len(GATES) or {g['id'] for g in gates}!=set(GATES):raise ValueError('one of every readiness gate required')
    for g in gates:
        expected=gate(g['id'],g['state'],g['reason'],evidence=g['evidence'],maturity=g['evidence_maturity'],values=g['values'])
        if expected!=g:raise ValueError('altered readiness criterion or disposition')
        for link in g['evidence']:
            scope=link.get('scope')
            if scope=='method':
                if g['state'] in {'pass','fail'}:raise ValueError('numerical method evidence cannot decide a candidate gate')
                continue
            require_subject(link,composition,scope)
            digest(link.get('evaluation_id'),'evidence evaluation')
        if g['state']=='pass' and (g['values'].get('criterion_complete') is not True or
                not any(e.get('scope')=='composition' for e in g['evidence'])):
            raise ValueError('passing full gate requires complete-criterion composition evidence')
    states=[g['state'] for g in gates]
    result=dict(schema='osr-candidate-readiness/1',**deepcopy(composition),gates=deepcopy(gates),
                engineering_readiness='fail' if 'fail' in states else 'unknown' if 'unknown' in states else 'pass',
                physical_acceptance='unknown',**FLAGS)
    result['readiness_id']=identity(result)
    return result


def preflights(record):
    """Cost and completed journey are outputs, not circular launch prerequisites."""
    from engineering.trip_dynamics.validation import preflight_result
    names={'mass','suspension','control','electrical','structure','civil'}
    gates=[dict(id=g['id'],state=g['state'],reason=g['reason'],values=g['values']) for g in record['gates'] if g['id'] in names]
    rows=[]
    cases=[('hover-empty',0,'empty',20,None),('hover-AW3',0,'AW3',20,None),
           ('2000-empty',2000,'empty',20,None),('2000-AW3',2000,'AW3',20,None),
           ('2000-asymmetric',2000,'asymmetric',20,None),('2000-hot-AW3',2000,'AW3',50,None),
           ('2000-receiving-loss',2000,'AW3',20,'receiving-power-loss'),
           ('2000-support-loss',2000,'AW3',20,'support-power-loss')]
    for name,distance,load,temp,fault in cases:
        scenario=dict(schema='osr-readiness-journey-request/1',case_id=name,candidate_id=record['candidate_id'],
            cars=6,car_length_m=17.,distance_m=distance,load_case=load,temperature_C=temp,
            fault=None if fault is None else dict(id=fault,at_s=80.),mode='evidence',
            speed_target_m_s=20.,station_zone_m=350.,physical_performance_established=False)
        scenario['scenario_id']=identity(scenario)
        result=preflight_result(scenario,record['candidate_id'],gates)
        result.update(scenario=scenario,readiness_id=record['readiness_id'],
            scope='Prerequisites for a numerical journey; no trajectory, hover or fault response is manufactured')
        rows.append(result)
    return rows
