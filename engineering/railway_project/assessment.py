"""Keep numerical execution, journey screens and physical evidence separate."""
from math import fsum,isfinite
from pathlib import Path
from engineering.station_rail import ROOT
from engineering.station_rail.common import identity,digest
from .route import FLAGS

PRODUCER='engineering/railway_project/assessment.py'


def journey(case,manifest,result,*,speed_numerical_allowance_m_s,energy_relative_tolerance,
            stopping_margin_numerical_allowance_m,root=ROOT):
    for value in (manifest,result):
        if value.get('evaluation_id')!=identity({k:v for k,v in value.items() if k!='evaluation_id'}):
            raise ValueError('Sealed motion input/result required')
    if (case['id']!=identity({k:v for k,v in case.items() if k!='id'}) or
        manifest['case_id']!=case['id'] or manifest['native_input_id']!=identity(case) or
        result['id']!=case['id'] or result['native_input_id']!=identity(case) or
        result['candidate_id']!=case['candidate_id'] or manifest['candidate_id']!=case['candidate_id'] or
        result.get('control',{}).get('policy_id')!=case['control']['policy_id']):
        raise ValueError('Mixed native request, controller or physical candidate')
    if any(result.get(k) is not False for k in ('physical_accepted','engineering_accepted','operating_release','admitted_operating_map')):
        raise ValueError('Numerical output cannot confer hardware acceptance')
    for v in (speed_numerical_allowance_m_s,energy_relative_tolerance,stopping_margin_numerical_allowance_m):
        if type(v) not in (int,float) or not isfinite(v) or v<0:raise ValueError('Finite explicit numerical tolerances required')
    if energy_relative_tolerance>0.01:
        raise ValueError('An energy balance residual above1percent needs numerical investigation')
    fields=('energy_residual_j','grid_energy_j','brake_heat_j','grade_work_j','final_kinetic_energy_j',
        'maximum_speed_m_s','maximum_absolute_jerk_m_s3','maximum_mechanical_power_w','maximum_grid_power_w')
    if any(type(result.get(k)) not in (int,float) or not isfinite(result[k]) for k in fields):
        raise ValueError('Finite native energy/force/trajectory quantities required')
    scale=max(1.,fsum(abs(result[k]) for k in ('grid_energy_j','brake_heat_j','grade_work_j','final_kinetic_energy_j')))
    c=result['control'];margin=c.get('minimum_stopping_margin_m')
    margin_valid=type(margin) in (int,float) and isfinite(margin)
    checks=dict(energy_balance=abs(result['energy_residual_j'])<=energy_relative_tolerance*scale,
        nominal_arrival=result.get('normal_numerical_arrival') is True,
        no_rollback=result.get('rollback_detected') is False,
        declared_speed_envelope=result['maximum_speed_m_s']<=case['speed_cap_m_s']+speed_numerical_allowance_m_s,
        controller_input_domain=c.get('bounds_valid') is True,
        authority_not_violated=c.get('end_of_authority_violated') is False,
        stopping_bound_margin=margin_valid and margin>=-stopping_margin_numerical_allowance_m,
        drive_mechanical_power=result['maximum_mechanical_power_w']<=case['drive']['mechanical_power_w']*(1+1e-10),
        drive_grid_power=result['maximum_grid_power_w']<=case['drive']['grid_power_w']*(1+1e-10),
        total_supply=result['maximum_grid_power_w']+case['auxiliary_power_w']<=manifest['energy_partition']['total_supply_limit_w']*(1+1e-10))
    passed=all(checks.values())
    value=dict(schema='osr-project-journey-assessment/1',candidate_id=case['candidate_id'],case_id=case['id'],
        input_manifest_evaluation_id=manifest['evaluation_id'],native_result_evaluation_id=result['evaluation_id'],
        native_receipt_id=result['native_receipt_id'],execution='completed',checks=checks,
        failed_checks=[k for k,v in checks.items() if not v],model_journey_screen_passed=passed,
        advisory_jerk_target_met=result['maximum_absolute_jerk_m_s3']<=case['comfort_jerk_m_s3'],
        advisory_jerk_is_not_universal_hardware_rejection=True,
        numerical_tolerances=dict(speed_m_s=speed_numerical_allowance_m_s,energy_relative=energy_relative_tolerance,
            stopping_margin_m=stopping_margin_numerical_allowance_m),
        model_stopping_margin_m=margin,energy_relative_residual=abs(result['energy_residual_j'])/scale,
        thermal_evidence='not modelled' if case['thermal'] is None else 'declared aggregate hypothesis only',
        physical_evidence=False,protected_service_qualified=False,
        scope='Rescreen trusted native-runner output; this is not receipt authentication, a measured force map, an operating timetable or physical acceptance',
        source_sha256={PRODUCER:digest(Path(root)/PRODUCER)},**FLAGS)
    value['evaluation_id']=identity(value)
    return value
