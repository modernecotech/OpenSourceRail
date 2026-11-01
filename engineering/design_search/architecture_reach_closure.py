"""Necessary coast-reach bounds for interrupted architecture demand studies.

This supplemental evaluator preserves the original time/step budget and trace.
It can prove an off-power target unreachable using a conservative resistance
floor, without claiming a completed trajectory or available propulsion/brakes.
"""
import argparse
import gzip
import json
from math import isfinite
from pathlib import Path
import shutil
import tempfile

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from . import architecture_demand, architecture_publication

PRODUCER='engineering/design_search/architecture_reach_closure.py'
INPUT='docs/design-engine/v06-architecture'
OUTPUT='docs/design-engine/architecture-reach-closure'
TOLERANCE_M=1e-7
FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
    manufacturing_release=False,operating_release=False,physical_journey_completed=False,
    selected_reference_changed=False)


def _finite(value,name,*,positive=False,nonnegative=False):
    if (type(value) not in (int,float) or not isfinite(value)
            or positive and value<=0 or nonnegative and value<0):
        raise ValueError('Finite admissible '+name+' required')
    return float(value)


def coast_bound(inputs,position_m,speed_m_s):
    """Upper bounds on further travel/time when no traction acts before a target.

    F(v)=m*g*(rolling+grade)+constant+k*(v+headwind)^2 >= F_floor
    for v>=0, k>=0 and headwind>=0. Work/energy and momentum then give
    s_stop <= (m+mr)*v^2/(2*F_floor), t_stop <= (m+mr)*v/F_floor.
    A reachable intermediate power window prevents an infeasibility proof.
    """
    distance=_finite(inputs.get('distance_m'),'distance',positive=True)
    mass=_finite(inputs.get('mass_kg_per_car'),'translation mass',positive=True)
    rotating=_finite(inputs.get('rotating_mass_kg_per_car'),'rotating equivalent mass',nonnegative=True)
    rolling=_finite(inputs.get('rolling_coefficient'),'rolling coefficient',nonnegative=True)
    constant=_finite(inputs.get('constant_resistance_N_per_car'),'constant resistance',nonnegative=True)
    aero=_finite(inputs.get('aero_coefficient_N_s2_m2'),'aerodynamic coefficient',nonnegative=True)
    wind=_finite(inputs.get('headwind_m_s'),'headwind',nonnegative=True)
    grade=_finite(inputs.get('grade_fraction_uphill'),'grade')
    x=_finite(position_m,'position',nonnegative=True);v=_finite(speed_m_s,'speed',nonnegative=True)
    if x>distance:raise ValueError('Tail state must lie within the declared route')
    windows=architecture_demand._windows(inputs.get('powered_windows'),distance)
    active=any(lo-TOLERANCE_M<=x<=hi+TOLERANCE_M for lo,hi in windows)
    next_power=min((lo for lo,hi in windows if lo>x+TOLERANCE_M),default=None)
    target=distance if next_power is None else min(distance,next_power)
    floor=mass*architecture_demand.G*(rolling+grade)+constant+aero*wind**2
    effective=mass+rotating;kinetic=.5*effective*v*v
    values=dict(position_m=x,speed_m_s=v,effective_inertial_mass_kg_per_car=effective,
        translation_mass_kg_per_car=mass,rotating_equivalent_mass_kg_per_car=rotating,
        signed_grade_fraction_uphill=grade,resistance_floor_N_per_car=floor,
        remaining_kinetic_energy_J_per_car=kinetic,next_commanded_power_start_m=next_power,
        next_target_m=target,destination_m=distance,numerical_distance_tolerance_m=TOLERANCE_M,
        additional_coast_distance_upper_m=None,additional_coast_time_upper_s=None,
        stop_position_upper_m=None,shortfall_to_next_target_lower_m=None,
        comparison_stop_position_m=None,comparison_shortfall_to_next_target_m=None,
        target_infeasibility_proven=False,applicable=False)
    if active:reason='Tail state is inside or within tolerance of a commanded powered window'
    elif x>=distance-TOLERANCE_M:reason='Tail state is already at the destination'
    elif floor<=0:reason='A positive resistance floor is unavailable; finite stopping is not established'
    else:
        extra=kinetic/floor;time=effective*v/floor;stop=x+extra;shortfall=target-stop
        if not all(isfinite(z) for z in (extra,time,stop,shortfall)):
            raise ValueError('Finite derived coast bound required')
        proven=stop+TOLERANCE_M<target
        values.update(applicable=True,additional_coast_distance_upper_m=extra,
            additional_coast_time_upper_s=time,stop_position_upper_m=stop,
            shortfall_to_next_target_lower_m=shortfall,comparison_stop_position_m=stop+TOLERANCE_M,
            comparison_shortfall_to_next_target_m=shortfall-TOLERANCE_M,target_infeasibility_proven=proven)
        reason=('Stops before the next commanded power window or destination under the declared demand model'
                if proven else 'This conservative bound does not exclude reaching the next power window or destination')
    values.update(reason=reason,scope='Necessary bound under the declared constant-grade resistance and no-off-zone-traction model; not physical railway acceptance',**FLAGS)
    values['bound_id']=identity(values)
    return values


def sources(root=ROOT):
    root=Path(root)
    paths=(PRODUCER,architecture_demand.PRODUCER,'engineering/design_search/architecture_publication.py','engineering/station_rail/common.py',
        INPUT+'/manifest.json',INPUT+'/campaign.json.gz')
    return {name:digest(root/name) for name in paths}


def _calculate(root=ROOT):
    root=Path(root);architecture_publication.verify(root,replay=False)
    epoch=sources(root);m=json.loads((root/INPUT/'manifest.json').read_bytes())
    campaign=json.loads(gzip.decompress((root/INPUT/'campaign.json.gz').read_bytes()))
    cases={row['case_id']:row for row in campaign['cases']};rows=[];seen=set()
    for result in campaign['results']:
        case_id=result['case_id']
        if case_id in seen or case_id not in cases:raise ValueError('Unique architecture case/result binding required')
        seen.add(case_id);case=cases[case_id]
        if (case['case_id']!=identity({k:v for k,v in case.items() if k!='case_id'})
                or case['candidate_id']!=result['candidate_id'] or case['requirement_revision']!=result['requirement_revision']
                or case['candidate_id']!=identity(case['physical_definition'])
                or result['evaluation_id']!=identity({k:v for k,v in result.items() if k!='evaluation_id'})):
            raise ValueError('Mixed architecture candidate, requirement or evaluation identity')
        if result['screens']['analytical_reach']!='unknown':continue
        t=result['trajectory'];inputs=t['inputs']
        if (inputs['powered_windows']!=case['commanded_power_windows_m']
                or inputs['distance_m']!=case['physical_definition']['route']['station_spacing_m']
                or inputs['cars']!=case['physical_definition']['formation']['cars']
                or inputs['mass_kg_per_car']!=result['comparison_mass_kg_per_car']
                or inputs['rotating_mass_kg_per_car']!=result['rotating_reference_mass_kg_per_car']):
            raise ValueError('Motion inputs differ from the source case and mass hypothesis')
        supported=(t.get('execution')=='interrupted' and t.get('reason')=='bounded_runtime_or_step_budget_exhausted'
            and t.get('numerical_validity')=='valid' and type(t.get('relative_energy_residual')) in (int,float)
            and 0<=t['relative_energy_residual']<=1e-6 and t.get('available_force') is None and t.get('reachable') is False)
        bound=coast_bound(inputs,t['final_position_m'],t['final_speed_m_s']) if supported else None
        proven=bool(bound and bound['target_infeasibility_proven'])
        row=dict(case_id=case_id,candidate_id=case['candidate_id'],requirement_revision=case['requirement_revision'],
            parent_evaluation_id=result['evaluation_id'],parent_raw_evaluation_id=result['raw_evaluation_id'],
            parent_raw_demand_id=t['raw_demand_id'],parent_indexed_demand_id=t['indexed_demand_id'],
            family_id=case['family_id'],cars=case['physical_definition']['formation']['cars'],
            distance_m=inputs['distance_m'],inputs=inputs,
            source_execution=t['execution'],source_reason=t['reason'],source_runtime_s=t['runtime_s'],
            source_maximum_runtime_s=inputs['maximum_runtime_s'],source_numerical_validity=t['numerical_validity'],
            source_trace_archive=t['trace_archive'],bound=bound,
            state_error_enclosure_available=False,
            state_basis='Conditional on the recorded numerical terminal state. Energy consistency is not a rigorous position/speed error enclosure.',
            reachability_disposition='infeasible-under-declared-demand-model' if proven else 'unresolved-by-this-bound',
            analytical_infeasibility_proven=proven,original_trace_completion_claimed=False,
            next_action=('Revise the declared launch/booster distribution, speed or station spacing under a new evaluation/configuration'
                if proven else 'Retain the numerical/model task; this bound supplies no reachability decision'),**FLAGS)
        row['evaluation_id']=identity(row);rows.append(row)
    if seen!=set(cases):raise ValueError('Architecture result coverage differs')
    value=dict(schema='osr-architecture-coast-reach-closure/1',source_sha256=epoch,
        parent_campaign_id=campaign['campaign_id'],parent_manifest_id=m['manifest_id'],
        parent_evaluation_case_count=len(cases),resource_hold_count=len(rows),rows=rows,
        analytically_infeasible_cases=sum(row['analytical_infeasibility_proven'] for row in rows),
        unresolved_reachability_cases=sum(not row['analytical_infeasibility_proven'] for row in rows),
        interpretation='Supplemental necessary-bound evaluations conditional on recorded numerical terminal states and unchanged model inputs, without a rigorous state-error enclosure. Original 600-second interrupted traces and their resource statuses are preserved. No propulsion, braking, installed mass or passenger-operation qualification is granted.',
        integrated_selection=None,**FLAGS)
    if sources(root)!=epoch:raise ValueError('Reach-bound sources changed during evaluation')
    value['closure_id']=identity(value)
    return value


def _readme(value):
    lines=['# Interrupted architecture reachability closure','',
        f"The current architecture campaign has {value['resource_hold_count']} interrupted reachability questions among {value['parent_evaluation_case_count']} evaluations. A conservative off-power stopping bound proves {value['analytically_infeasible_cases']} of these scenarios cannot reach the next commanded power window or destination. {value['unresolved_reachability_cases']} remain unresolved by this bound.",'',
        'The original time histories remain interrupted at their declared runtime/step limit. No limit or stored trajectory was changed. This supplement records separate evaluation identities linked to the exact candidate, requirement, case, source evaluation and trace index. The inference is conditional on the recorded terminal state; energy balance does not provide a rigorous position/speed error enclosure. An outward comparison margin prevents equality or near-boundary rounding from establishing infeasibility.','',
        '## Necessary bound','',
        'For forward speed, nonnegative headwind and quadratic drag, the opposing force is at least `F_floor = m*g*(rolling + uphill_grade) + constant_drag + k*headwind²`. When that floor is positive, work/energy gives `s_stop ≤ (m + rotating_equivalent_mass)*v²/(2*F_floor)` and momentum gives `t_stop ≤ (m + rotating_equivalent_mass)*v/F_floor`. Rotating mass contributes to inertia; gravity and rolling load use translation mass only.','',
        'The bound is applied only outside commanded powered windows. It checks the nearest future powered-window start as well as the destination, so an accessible booster cannot be ignored. A nonpositive floor, a powered tail or an energy-invalid source remains unresolved.','',
        '| Cars | Source runtime | Tail position | Tail speed | Latest stop position | Minimum shortfall to next target | Disposition |',
        '|---:|---:|---:|---:|---:|---:|---|']
    for row in value['rows']:
        b=row['bound'];stop=None if b is None else b['stop_position_upper_m'];gap=None if b is None else b['shortfall_to_next_target_lower_m']
        fmt=lambda x:'unknown' if x is None else f'{x:.3f}'
        lines.append(f"| {row['cars']} | {row['source_runtime_s']:.1f} s | {fmt(None if b is None else b['position_m'])} m | {fmt(None if b is None else b['speed_m_s'])} m/s | {fmt(stop)} m | {fmt(gap)} m | {row['reachability_disposition']} |")
    lines+=['','The three P3 rows differ in formation but share the same declared per-car mass and motion state. Their result is conditional on the campaign\'s command windows and accounted-mass hypothesis. Changing the power commands, speed, route or hardware creates another evaluation/configuration. No available motor force, installed equipment, actual stopping performance, engineering acceptance or operating approval is established.','',
        'Reproduce with `python3 -m engineering.design_search.architecture_reach_closure build` and `python3 -m engineering.design_search.architecture_reach_closure verify`.','',
        '[Exact evaluations](result.json) · [Source and payload receipt](manifest.json) · [Parent architecture study](../v06-architecture/README.md)','']
    return '\n'.join(lines)


def _check_packet(out):
    m=json.loads((out/'manifest.json').read_bytes())
    if m.get('manifest_id')!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('Reach-closure manifest identity differs')
    actual={p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!='manifest.json'}
    if any(p.is_symlink() or p.is_dir() for p in out.iterdir()) or actual!=m.get('files_sha256'):
        raise ValueError('Reach-closure payload differs')
    return m


def build(root=ROOT,output=None):
    root=Path(root);out=root/OUTPUT if output is None else Path(output);value=_calculate(root)
    out.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='.reach-closure-',dir=out.parent))
    try:
        (stage/'result.json').write_bytes(encoded(value));(stage/'README.md').write_text(_readme(value))
        m=dict(schema='osr-architecture-coast-reach-publication/1',source_sha256=value['source_sha256'],
            files_sha256={p.name:digest(p) for p in stage.iterdir()},closure_id=value['closure_id'],**FLAGS)
        m['manifest_id']=identity(m);(stage/'manifest.json').write_bytes(encoded(m))
        verify(root,output=stage)
        if out.exists():
            old=_check_packet(out)
            if old==m:return verify(root,output=out)
            backup=root/'build/architecture-reach-closure/replaced-publications'/old['manifest_id']
            backup.parent.mkdir(parents=True,exist_ok=True)
            if backup.exists():raise ValueError('Prior reach publication is already retained; inspect before replacement')
            shutil.move(out,backup)
        stage.rename(out)
    finally:
        if stage.exists():shutil.rmtree(stage)
    return verify(root,output=out)


def verify(root=ROOT,output=None):
    root=Path(root);out=root/OUTPUT if output is None else Path(output);m=_check_packet(out)
    if m.get('schema')!='osr-architecture-coast-reach-publication/1' or m.get('source_sha256')!=sources(root):
        raise ValueError('Reach-closure source epoch differs')
    expected=_calculate(root);actual=json.loads((out/'result.json').read_bytes())
    if actual!=expected or m.get('closure_id')!=expected['closure_id'] or (out/'README.md').read_text()!=_readme(expected):
        raise ValueError('Reach bound does not reproduce from the current parent study')
    if any(m.get(k) is not v for k,v in FLAGS.items()):raise ValueError('Reach bound cannot grant physical acceptance or selection')
    return dict(verified=True,manifest_id=m['manifest_id'],closure_id=expected['closure_id'],
        resource_hold_count=expected['resource_hold_count'],analytically_infeasible_cases=expected['analytically_infeasible_cases'],
        unresolved_reachability_cases=expected['unresolved_reachability_cases'],original_traces_completed=False,**FLAGS)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('build','verify'))
    a=p.parse_args();print(json.dumps((build if a.action=='build' else verify)(),indent=2))
