"""Executable quality-record checks, never automatic product/ISO acceptance."""
from __future__ import annotations
from copy import deepcopy
import math
import statistics
from .common import finite,timestamp,artifact,fingerprint,ROOT


def measurement_decision(value,uncertainty,lower,upper):
    """OSR interval-containment decision; uncertainty is supplied expanded U."""
    value=finite(value,'measurement');u=finite(uncertainty,'expanded uncertainty',0.)
    for bound in (lower,upper):
        if bound is not None:finite(bound,'measurement bound')
    if lower is None and upper is None:return dict(status='open-limits',within_nominal_limits=None,guarded_conformity=None)
    if lower is not None and upper is not None and lower>upper:raise ValueError('ordered measurement bounds required')
    nominal=(lower is None or value>=lower) and (upper is None or value<=upper)
    contained=(lower is None or value-u>=lower) and (upper is None or value+u<=upper)
    outside=(lower is not None and value+u<lower) or (upper is not None and value-u>upper)
    return dict(status='within-guarded-limits' if contained else 'outside-limits' if outside else 'uncertainty-overlaps-limit',
        within_nominal_limits=nominal,guarded_conformity=contained,interval=[value-u,value+u],
        decision_rule='OSR expanded-uncertainty interval containment; project applicability required')


def calibration(record,performed_at,unit,root=ROOT):
    if set(record)!={'tool_id','unit','valid_from','valid_until','minimum','maximum','artifact'} or not record['tool_id'] or record['unit']!=unit:
        raise ValueError('calibrated tool identity/unit mismatch')
    start,end,when=map(timestamp,(record['valid_from'],record['valid_until'],performed_at))
    if start>end or not start<=when<=end:raise ValueError('tool calibration expired or not valid at execution time')
    lo,hi=(finite(record[k],'calibrated range') for k in ('minimum','maximum'))
    if lo>=hi:raise ValueError('ordered calibrated tool range required')
    artifact(record['artifact'],root,kind='calibration')
    return lo,hi


def assess_measurement(characteristic,record,root=ROOT):
    fields={'characteristic_id','configuration_sha256','instance_id','part_revision','serial','batch','unit','value',
            'expanded_uncertainty','performed_at','operator','inspector','calibration','environment','evidence'}
    if set(record)!=fields:raise ValueError('measurement record fields missing or unknown')
    for k in ('characteristic_id','configuration_sha256','instance_id','part_revision','serial','batch','unit'):
        if record[k]!=characteristic[k]:raise ValueError('measurement identity/revision/serial/batch/unit mismatch: '+k)
    if not(record['serial'] or record['batch']) or not record['operator'] or not record['inspector'] or record['operator']==record['inspector']:
        raise ValueError('physical identity and independent quality inspector required')
    artifact(record['evidence'],root,kind='measurement');artifact(characteristic['procedure'],root,kind='procedure')
    lo,hi=calibration(record['calibration'],record['performed_at'],record['unit'],root)
    value=finite(record['value'],'measurement')
    if not lo<=value<=hi:raise ValueError('measurement outside calibrated tool range')
    environment=record['environment'];limits=characteristic['environment_limits']
    if set(environment)!=set(limits):raise ValueError('required measurement environment missing')
    for key,(minimum,maximum) in limits.items():
        finite(minimum,'environment minimum');finite(maximum,'environment maximum')
        if minimum>maximum:raise ValueError('ordered environment limits required')
        reading=finite(environment[key],'environment '+key)
        if not minimum<=reading<=maximum:raise ValueError('measurement environment outside released window')
    decision=measurement_decision(value,record['expanded_uncertainty'],characteristic['minimum'],characteristic['maximum'])
    return dict(schema='osr-factory-measurement-assessment/1',characteristic_id=record['characteristic_id'],
        record_sha256=fingerprint(record),**decision,ready_for_independent_quality_review=decision['guarded_conformity'] is True,
        production_released=False,physical_validation=False)


def torque_trace(trace,limits,*,root=ROOT):
    fields={'joint_id','fastener_id','configuration_sha256','part_revision','tool','performed_at','operator','inspector',
            'attempt','rework_authority','samples','expanded_uncertainty','evidence'}
    if set(trace)!=fields or not trace['fastener_id'] or not trace['operator'] or not trace['inspector'] or trace['operator']==trace['inspector']:
        raise ValueError('complete joint/fastener trace and independent review identity required')
    for key in ('joint_id','configuration_sha256','part_revision'):
        if trace[key]!=limits[key]:raise ValueError('torque trace configuration/joint revision mismatch')
    if type(trace['attempt']) is not int or trace['attempt']<1:raise ValueError('positive tightening attempt required')
    if trace['attempt']>1:artifact(trace['rework_authority'],root,kind='procedure')
    elif trace['rework_authority'] is not None:artifact(trace['rework_authority'],root,kind='procedure')
    artifact(limits['procedure'],root,kind='procedure');artifact(trace['evidence'],root,kind='measurement')
    tool_lo,tool_hi=calibration(trace['tool'],trace['performed_at'],'N m',root)
    rows=trace['samples']
    if len(rows)<3:raise ValueError('at least three timestamped torque/angle samples required')
    previous_t=-math.inf;previous_angle=-math.inf
    for row in rows:
        if len(row)!=3:raise ValueError('time/torque/angle sample required')
        t,torque,angle=(finite(v,'torque trace sample') for v in row)
        if t<0 or t<=previous_t or angle<previous_angle or not tool_lo<=torque<=tool_hi:
            raise ValueError('unordered trace, reversed angle or torque outside calibrated range')
        previous_t=t;previous_angle=angle
    decision=measurement_decision(rows[-1][1],trace['expanded_uncertainty'],limits['minimum_nm'],limits['maximum_nm'])
    angle_bounds=limits['final_angle_deg'];angle_ok=None if angle_bounds is None else angle_bounds[0]<=rows[-1][2]<=angle_bounds[1]
    return dict(schema='osr-torque-trace-assessment/1',joint_id=trace['joint_id'],fastener_id=trace['fastener_id'],
        trace_sha256=fingerprint(trace),torque_decision=decision,angle_within_released_limits=angle_ok,
        ready_for_independent_quality_review=decision['guarded_conformity'] is True and (angle_ok is not False),
        preload_verified=False,production_released=False,physical_validation=False)


def process_statistics(values,lower,upper,*,stability_evidence=None,normality_evidence=None,measurement_system_evidence=None,root=ROOT):
    xs=[finite(v,'process sample') for v in values]
    lo,hi=finite(lower,'lower specification'),finite(upper,'upper specification')
    if len(xs)<2 or lo>=hi:raise ValueError('two samples and ordered specification limits required')
    mean=statistics.mean(xs);sd=statistics.stdev(xs)
    qualified=len(xs)>=50 and all(r is not None for r in (stability_evidence,normality_evidence,measurement_system_evidence))
    for ref in (stability_evidence,normality_evidence,measurement_system_evidence):
        if ref is not None:artifact(ref,root,kind='record')
    pp=None if sd==0 else (hi-lo)/(6*sd);ppk=None if sd==0 else min(hi-mean,mean-lo)/(3*sd)
    return dict(sample_count=len(xs),mean=mean,sample_standard_deviation=sd,diagnostic_pp=pp,diagnostic_ppk=ppk,
        conditional_cp=pp if qualified else None,conditional_cpk=ppk if qualified else None,
        assumptions_evidence_present=qualified,capability_accepted=False,
        limits=['independent suitable samples and stable approximately normal process required',
                '50 samples is a screening policy; project evidence/confidence requirements remain controlling',
                'overall-spread diagnostics cannot waive individual inspections or approve a process'])


def material_lot(passport,lot,performed_at,root=ROOT):
    if set(lot)!={'lot_id','material_id','grade','expiry','certificate','supplier','quantity','unit'} or not lot['lot_id'] or not lot['supplier']:
        raise ValueError('complete material genealogy required')
    if lot['material_id']!=passport['material_id'] or lot['unit']!=passport['unit']:raise ValueError('material family or unit mismatch')
    finite(lot['quantity'],'material lot quantity',1e-12);artifact(lot['certificate'],root,kind='material')
    if lot['expiry'] is not None and timestamp(performed_at)>timestamp(lot['expiry']):raise ValueError('material shelf life expired')
    grade=passport['released_grade']
    if not isinstance(lot['grade'],str) or not lot['grade'] or (grade is not None and (not isinstance(grade,str) or not grade)):
        raise ValueError('material grades must be declared identifiers')
    return dict(material_identity_matches=grade is not None and grade==lot['grade'],status='open-grade' if grade is None else 'grade-mismatch' if grade!=lot['grade'] else 'ready-for-quality-review',
        lot_sha256=fingerprint(lot),production_released=False)
