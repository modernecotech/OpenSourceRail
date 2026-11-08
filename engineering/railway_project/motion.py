"""Compile exact mapped-corridor legs for the retained Rust point-train method.

All equipment, brake and environmental sizing values are explicit research
assumptions. This compiler executes no solver and grants no available-map or
operating admission. The old pilot vehicle/force profile is never consulted.
"""
from copy import deepcopy
from math import isfinite,sqrt
from pathlib import Path
import json

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest,identity
from engineering.station_pair import control_policy,native_bridge
from . import drive
from .civil import sealed,source_union
from .route import FLAGS

PRODUCER='engineering/railway_project/motion.py'
FIELDS={'load_state','mass_case','grade_fraction','grade_observation_fraction','headwind_m_s',
    'speed_cap_m_s','rolling_coefficient','air_density_kg_m3','cd_a_m2','acceleration_request_m_s2',
    'comfort_jerk_m_s3','non_motor_rotating_mass_fraction','brake_force_cap_n',
    'brake_lower_fraction','adhesion_fraction','adhesion_lower_fraction',
    'brake_latency_s','brake_rise_s','berth_tolerance_m','dt_s','max_time_s','dwell_s','headway_s',
    'hotel_power_w_per_car','train_total_supply_limit_w','assumption_reference',
    'brake_independence_hypothesis','power_loss_at_s','failed_drive_fraction','emergency_at_m'}


def compile_case(bundle,body,alignment,duty,leg_index,scenario,*,direction=1,root=ROOT):
    for v in (bundle,body,alignment,duty):sealed(v)
    if (bundle.get('schema')!='osr-mapped-railway-project-bundle/1' or
        body.get('schema')!='osr-vehicle-installation/1' or
        alignment.get('schema')!='osr-station-straight-alignment/1'):
        raise ValueError('Mapped project, counted body and designed alignment required')
    if any(v['candidate_id']!=identity(v['physical_definition']) for v in (bundle,body,alignment)):
        raise ValueError('Physical project/body/alignment identity differs')
    physical=bundle['physical_definition']
    if (physical['body_candidate_id']!=body['candidate_id'] or bundle['body_evaluation_id']!=body['evaluation_id'] or
        physical['alignment_candidate_id']!=alignment['candidate_id'] or bundle['alignment_evaluation_id']!=alignment['evaluation_id'] or
        duty['candidate_id']!=body['candidate_id'] or duty['body_evaluation_id']!=body['evaluation_id']):
        raise ValueError('Mixed project/body/mass/alignment/drive revision')
    if not isinstance(scenario,dict) or set(scenario)!=FIELDS:
        raise ValueError('Complete explicit motion scenario required')
    s=deepcopy(scenario)
    if s['mass_case'] not in ('low','base','high') or s['load_state'] not in ('normal','crowd-control'):
        raise ValueError('Explicit normal or structural crowd load bound required')
    if type(direction) is not int or direction not in (-1,1) or type(leg_index) is not int or not 0<=leg_index<len(alignment['legs']):
        raise ValueError('Explicit known leg and travel direction required')
    strings={'load_state','mass_case','assumption_reference','brake_independence_hypothesis'}
    nullable={'power_loss_at_s','emergency_at_m'}
    signed={'grade_fraction','grade_observation_fraction'}
    nonnegative={'headwind_m_s','brake_latency_s','failed_drive_fraction',*nullable}
    for name,x in s.items():
        if name in strings:
            if not isinstance(x,str) or not x.strip() or len(x)>1000:raise ValueError('Named motion assumption required: '+name)
        elif name in nullable and x is None:continue
        elif type(x) not in (int,float) or not isfinite(x) or (name not in signed and (x<0 if name in nonnegative else x<=0)):
            raise ValueError('Finite explicit physical input required: '+name)
    if s['brake_independence_hypothesis']!='independent-stored-brake-energy-hypothesis':
        raise ValueError('Independent braking must remain an explicit unverified hardware hypothesis')
    if any(not 0<s[n]<=1 for n in ('brake_lower_fraction','adhesion_fraction','adhesion_lower_fraction','non_motor_rotating_mass_fraction')):
        raise ValueError('Physical fraction outside range')
    if not 0<=s['failed_drive_fraction']<=1 or max(abs(s[n]) for n in signed)>.1 or not .001<=s['dt_s']<=.2 or s['max_time_s']>3600:
        raise ValueError('Fault/grade/time outside declared native research domain')
    if s['adhesion_lower_fraction']>s['adhesion_fraction']:
        raise ValueError('Controller adhesion lower bound exceeds the plant scenario')
    leg=alignment['legs'][leg_index];D=leg['distance_m']
    if s['emergency_at_m'] is not None and not 0<=s['emergency_at_m']<=D:
        raise ValueError('Emergency event outside this leg')
    rows={r['case']:r for r in body['mass_scenarios'] if r['name'].startswith(s['load_state']+'-')}
    if set(rows)!={'low','base','high'}:
        raise ValueError('All three source mass bounds required')
    low,high,actual=rows['low']['train_mass_kg'],rows['high']['train_mass_kg'],rows[s['mass_case']]['train_mass_kg']
    if not low<=actual<=high:raise ValueError('Unordered source mass bounds')
    native_drive=drive.native_drive(duty,D,acknowledge_domain=drive.CONDITIONAL_DOMAIN,root=root)
    fixed=drive.mandatory_auxiliary_power_w(duty,root=root)
    hotel=body['policy']['layout']['cars']*s['hotel_power_w_per_car']
    if s['train_total_supply_limit_w']<duty['declared']['grid_input_power_limit_w']+hotel:
        raise ValueError('Total supply must include declared drive grid limit plus base hotel; cooling/copper already partitioned once')
    rotor=duty['model']['rotor_reflected_equivalent_mass_kg']
    grade=direction*s['grade_fraction'];observed=direction*s['grade_observation_fraction']
    mu=s['adhesion_fraction'];normal=actual*9.80665/sqrt(1+grade**2)
    native_drive['contact_force_cap_n']=min(native_drive['contact_force_cap_n'],normal*mu)
    p=json.loads((Path(root)/control_policy.POLICY).read_bytes())
    adhesion_lower=low*9.80665*s['adhesion_lower_fraction']/sqrt(1+p['numerical_grade_magnitude_limit']**2)
    brake_lower=min(s['brake_force_cap_n'],adhesion_lower)*s['brake_lower_fraction']
    control=dict(mass_lower_kg=low,mass_upper_kg=high,rotating_mass_upper_kg=high*s['non_motor_rotating_mass_fraction']+rotor,
        external_mass_upper_kg=0.,brake_force_lower_bound_n=brake_lower,grade_estimate_fraction=observed,
        grade_error_bound=p['grade_error_bound'],position_error_bound_m=p['position_error_bound_m'],
        speed_error_bound_m_s=p['speed_error_bound_m_s'],acceleration_error_bound_m_s2=p['acceleration_error_bound_m_s2'],
        position_bias_m=0.,speed_bias_m_s=0.,acceleration_bias_m_s2=0.,
        reaction_time_bound_s=p['reaction_time_bound_s'],brake_rise_time_bound_s=max(p['brake_rise_time_bound_s'],s['brake_rise_s']),
        stopping_margin_m=p['stopping_margin_m'],end_of_authority_m=D,initial_hold_applied=p['initial_hold_applied'],
        start_traction_lower_bound_n=min(native_drive['points'][0]['force_n']*p['start_traction_lower_fraction_of_nominal'],adhesion_lower),
        rolling_resistance_upper_n=high*9.80665*max(p['rolling_coefficient_upper_hypothesis'],s['rolling_coefficient']),
        external_resistance_upper_n=0.,positive_acceleration_bound_m_s2=p['positive_acceleration_bound_m_s2'],
        drive_fault_observed=False)
    if s['brake_latency_s']>control['reaction_time_bound_s']:
        raise ValueError('Plant brake latency exceeds the declared controller bound')
    static={k:v for k,v in control.items() if k not in control_policy.OBSERVATIONS}
    control['policy_id']=identity(dict(candidate_id=bundle['candidate_id'],parameters=static,
        policy_sha256=digest(Path(root)/control_policy.POLICY),producer_sha256=digest(Path(root)/PRODUCER),
        body_evaluation_id=body['evaluation_id'],drive_evaluation_id=duty['evaluation_id']))
    vmax=min(s['speed_cap_m_s'],alignment['requirements']['requested_speed_m_s'],native_drive['maximum_speed_m_s'])
    case=dict(candidate_id=bundle['candidate_id'],mass_kg=actual,
        rotating_equivalent_mass_kg=actual*s['non_motor_rotating_mass_fraction']+rotor,distance_m=D,
        grade_fraction=grade,rolling_coefficient=s['rolling_coefficient'],air_density_kg_m3=s['air_density_kg_m3'],
        cd_a_m2=s['cd_a_m2'],headwind_m_s=s['headwind_m_s'],speed_cap_m_s=vmax,
        acceleration_request_m_s2=s['acceleration_request_m_s2'],comfort_jerk_m_s3=s['comfort_jerk_m_s3'],
        brake_start_m=D,berth_tolerance_m=s['berth_tolerance_m'],brake_force_cap_n=s['brake_force_cap_n'],
        brake_adhesion_force_cap_n=normal*mu,brake_latency_s=s['brake_latency_s'],brake_rise_s=s['brake_rise_s'],
        dt_s=s['dt_s'],max_time_s=s['max_time_s'],dwell_s=s['dwell_s'],headway_s=s['headway_s'],
        auxiliary_power_w=hotel+fixed,drive=native_drive,
        fault={k:s[k] for k in ('power_loss_at_s','failed_drive_fraction','emergency_at_m')},thermal=None,control=control)
    case['id']=identity(case)
    sources=source_union(bundle,body,alignment,duty,root=root)
    sources.update({PRODUCER:digest(Path(root)/PRODUCER),control_policy.POLICY:digest(Path(root)/control_policy.POLICY)})
    manifest=dict(schema='osr-project-motion-input/1',candidate_id=bundle['candidate_id'],bundle_evaluation_id=bundle['evaluation_id'],
        body_candidate_id=body['candidate_id'],body_evaluation_id=body['evaluation_id'],alignment_evaluation_id=alignment['evaluation_id'],
        drive_evaluation_id=duty['evaluation_id'],leg_index=leg_index,direction=direction,
        from_stop=leg['from_stop'] if direction==1 else leg['to_stop'],
        to_stop=leg['to_stop'] if direction==1 else leg['from_stop'],
        train_reference='Fixed formation geometric centre; this point-method authority is not the full train clearance envelope',
        scenario=s,case_id=case['id'],native_input_id=identity(case),native_method_sha256=native_bridge.sources(root),
        energy_partition=dict(base_hotel_power_w=hotel,conservative_copper_cooling_addition_w=fixed,
            drive_grid_limit_w=native_drive['grid_power_w'],total_supply_limit_w=s['train_total_supply_limit_w']),
        source_sha256=sources,old_pilot_force_mass_or_distance_imported=False,
        holds=['Constant-grade sensitivity is not a surveyed vertical profile or variable-grade simulation.',
            'Brake force, adhesion, sensor bounds and stored braking energy are uncalibrated hardware assumptions.',
            'Thermal RC is unknown and absent; motor/cooling/current/brake repeated-duty acceptance is held.',
            'Each leg starts at rest; fleet interactions, station occupation, turnbacks and whole-route supply remain separate.'],**FLAGS)
    manifest['evaluation_id']=identity(manifest)
    return case,manifest
