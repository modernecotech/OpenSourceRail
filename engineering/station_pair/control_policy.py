"""Separate fixed controller assumptions from the plant being investigated."""
from pathlib import Path
from math import sqrt
import json
from engineering.station_rail.common import identity,digest
from . import ROOT,native_bridge

POLICY='engineering/station_pair/control-policy.json'
OBSERVATIONS={'grade_estimate_fraction','position_bias_m','speed_bias_m_s','acceleration_bias_m_s2','drive_fault_observed'}


def prepare(variant,reconciliation,brief,brake_force_n,*,grade_observation=0.,biases=None,drive_fault_observed=False,root=ROOT):
    if variant['onboard_added_mass_kg'] is None:return None
    if type(drive_fault_observed) is not bool:raise ValueError('Explicit boolean drive-fault observation required')
    root=Path(root);p=json.loads((root/POLICY).read_bytes())
    rows={r['case']:r for r in reconciliation['mass_scenarios']}
    payload=brief['normal_people']*brief['passenger_mass_kg']
    masses={c:rows[c]['conditional_accounted_train_mass_kg']+payload+variant['onboard_added_mass_kg'][c] for c in ('low','base','high')}
    start_force=variant['rated_force_ceiling_N']*brief['force_rating_fraction_hypothesis']['base']
    contact=variant['contact_force_hypothesis_N']
    if variant['family']=='powered-wheel':
        contact=(brief['degraded_adhesion_hypothesis']*masses['low']*9.80665*variant['geometry']['driven_axles']/24
                 /sqrt(1+p['numerical_grade_magnitude_limit']**2))
    # A drive failure reduces motor force. It does not also halve the separately
    # bounded contact capability; apply the two bounds before taking their min.
    start_force=min(start_force*p['start_traction_lower_fraction_of_nominal'],contact)
    value=dict(mass_lower_kg=masses['low'],mass_upper_kg=masses['high'],
        rotating_mass_upper_kg=masses['high']*brief['rotating_equivalent_fraction_hypothesis']['high'],
        external_mass_upper_kg=variant['external_mass_kg'],
        brake_force_lower_bound_n=brake_force_n*p['brake_force_lower_fraction'],
        grade_estimate_fraction=grade_observation,grade_error_bound=p['grade_error_bound'],
        position_error_bound_m=p['position_error_bound_m'],speed_error_bound_m_s=p['speed_error_bound_m_s'],
        acceleration_error_bound_m_s2=p['acceleration_error_bound_m_s2'],
        position_bias_m=0.,speed_bias_m_s=0.,acceleration_bias_m_s2=0.,
        drive_fault_observed=bool(drive_fault_observed),
        reaction_time_bound_s=p['reaction_time_bound_s'],brake_rise_time_bound_s=p['brake_rise_time_bound_s'],
        stopping_margin_m=p['stopping_margin_m'],initial_hold_applied=p['initial_hold_applied'],
        end_of_authority_m=variant['physical_definition']['station_spacing_m'],
        start_traction_lower_bound_n=start_force,
        rolling_resistance_upper_n=masses['high']*9.80665*p['rolling_coefficient_upper_hypothesis'],
        external_resistance_upper_n=p['cable_external_resistance_upper_n'] if variant['family']=='cable' else 0.,
        positive_acceleration_bound_m_s2=p['positive_acceleration_bound_m_s2'])
    static={k:v for k,v in value.items() if k not in OBSERVATIONS}
    value['policy_id']=identity(dict(candidate_id=variant['candidate_id'],parameters=static,
        policy_sha256=digest(root/POLICY),native_method_sha256=native_bridge.sources(root)))
    if biases is not None:
        if set(biases)-{'position_bias_m','speed_bias_m_s','acceleration_bias_m_s2'}:raise ValueError('Unknown simulated observation bias')
        value.update(biases)
    return value


def same_policy(a,b):
    """Bias/grade observations may change; every declared policy bound must match."""
    if a is None or b is None:return a is b
    return {k:v for k,v in a.items() if k not in OBSERVATIONS}=={k:v for k,v in b.items() if k not in OBSERVATIONS}
