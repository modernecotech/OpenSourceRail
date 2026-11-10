"""Separate package-07/Samawah acceleration hypotheses, without drive selection.

The retained 0.4 m/s² outline evaluation must reproduce exactly. The 0.6 and 0.8
cases change evaluation assumptions only. F=m*a and P=F*v are translational
inertia components, not available motor force, complete traction requirements,
measured acceleration or a signed-gradient bound on actual traction.
"""
from copy import deepcopy
from math import isclose, isfinite
from pathlib import Path
import argparse
import gzip
import json

from engineering.outline import city_inputs
from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from . import city_recalculation as outline

PRODUCER = 'engineering/railway_project/city_acceleration_sensitivity.py'
ACCELERATIONS = (0.4, 0.6, 0.8)
REFERENCE_EVALUATION = '0b1715bb59c73645335865a35f317ab51bb24254f1ec2f7711521ef9c32d333c'
REFERENCE_PACKET = '9527062dffe31c9c0f706abda76d9ecf9b772d1d97872be4697db817eeba4f29'
REFERENCE_MANIFEST_SHA256 = '892dcf2ca82bd2e758275f3bf64153b15ccdbde1bd18aac195218a73cd6121cc'
EXCLUDED = ('grade', 'rolling resistance', 'rotational inertia', 'jerk',
            'drivetrain/electrical losses', 'aerodynamic drag', 'thermal limits', 'adhesion limits')
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    manufacturing_release=False, operating_release=False,
    selected_reference_changed=False, movement_authority=False,
    service_complete=False, cost_complete=False, simulation_complete=False,
    achieved_acceleration=False, drive_selected=False)


def _seal(value):
    value['evaluation_id'] = identity(value)
    return value


def _is_sha256(value):
    return (isinstance(value, str) and len(value) == 64
            and all(char in '0123456789abcdef' for char in value))


def build(*, root=ROOT, body_path=None):
    """Recompute three bounded kinematic requests from exactly the same inputs.

    The original packet is an immutable identity reference, not a file modified
    or authenticated by this producer. Fresh control reproduction is checked
    before comparison. Any changed source epoch requires a separate study.
    """
    root = Path(root)
    path = root/outline.BODY_FILE if body_path is None else Path(body_path)
    raw = path.read_bytes()
    body = json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)
    city = city_inputs.load('samawah', root=root)
    policy = json.loads((root/outline.POLICY).read_bytes())
    if policy.get('acceleration_m_s2') != ACCELERATIONS[0]:
        raise ValueError('Retained 0.4 m/s² control policy must remain unchanged')
    cases = []; source = None; control = None
    for acceleration in ACCELERATIONS:
        p = deepcopy(policy); p['acceleration_m_s2'] = acceleration
        result = outline.evaluate(city, body, p, trusted_city_input_id=city['input_id'], root=root)
        if control is None:
            control = result
            if control['evaluation_id'] != REFERENCE_EVALUATION:
                raise ValueError('Original 0.4 m/s² source-bound control did not reproduce; retain it and use a separate source epoch')
            source = deepcopy(result['source_sha256'])
        if (result['candidate_id'] != control['candidate_id'] or result['source_sha256'] != source or
            result['source_city_input_id'] != control['source_city_input_id']):
            raise ValueError('Mixed physical city or source epoch in acceleration comparison')
        inertia = []
        for name, mass in sorted(result['body_mass_scenarios_kg'].items()):
            force = mass*acceleration
            inertia.append(dict(mass_scenario=name,declared_train_mass_kg=mass,
                translational_inertia_force_N=force,
                mechanical_power_at_declared_speed_cap_W=force*p['speed_cap_m_s'],
                speed_at_power_evaluation_m_s=p['speed_cap_m_s'],
                includes_six_car_train=True,installed_mass_verified=False))
        cases.append(_seal(dict(schema='osr-city-acceleration-case/1',
            candidate_id=result['candidate_id'],body_candidate_id=outline.BODY,
            body_evaluation_id=outline.BODY_EVALUATION,
            acceleration_hypothesis_m_s2=acceleration,
            role='retained reference control' if acceleration == 0.4 else 'unselected research hypothesis',
            source_outline_evaluation_id=result['evaluation_id'],policy_id=result['policy_id'],
            policy=deepcopy(result['policy']),
            source_city_input_id=result['source_city_input_id'],
            kinematic_lines=deepcopy(result['lines']),fleet_request_cases=deepcopy(result['fleet_request_cases']),
            inertia_only_lower_bound_components=inertia,
            definition_failures=deepcopy(result['definition_failures']),
            unknown_inputs=deepcopy(result['unknown_inputs']),**FLAGS)))
    source[PRODUCER] = digest(root/PRODUCER)
    value = dict(schema='osr-city-acceleration-sensitivity/1',candidate_id=control['candidate_id'],
        physical_definition=deepcopy(control['physical_definition']),
        body_candidate_id=outline.BODY,body_evaluation_id=outline.BODY_EVALUATION,
        source_city_input_id=city['input_id'],source_planning_revision_id=city['planning_revision_sha256'],
        retained_control_reference=dict(packet_id=REFERENCE_PACKET,manifest_sha256=REFERENCE_MANIFEST_SHA256,
            outline_evaluation_id=REFERENCE_EVALUATION,control_reproduced=True,
            original_packet_modified=False,original_packet_payload_authenticated_by_this_producer=False),
        acceleration_hypotheses_m_s2=list(ACCELERATIONS),cases=cases,
        inertia_component_basis=dict(force='F_translation=m_declared*a_requested',
            power='P_translation=F_translation*v_declared_speed_cap',
            excluded_effects=list(EXCLUDED),
            interpretation='Translation alone supplies a necessary inertial component. This is not a complete drive requirement or a universal lower bound on actual motor traction under signed grade/other forces. The speed cap is an evaluation point, not an achieved speed on every leg.'),
        declared_mass_scenarios_kg=deepcopy(control['body_mass_scenarios_kg']),
        body_mass_uncertainty=deepcopy(body['mass_uncertainty']),installed_mass_complete=False,
        holds=['Declared acceleration and braking are kinematic assumptions without an available drive/brake map.',
            'Mass cases retain the exact body uncertainty; they are not verified installed train masses.',
            'Force and power omit the listed effects; no inverter, motor, gearbox, adhesion, thermal or supply selection follows.',
            'Every source station conflict, workforce/calendar gap and service/cost hold from the outline remains open.'],
        source_sha256=dict(sorted(source.items())),**FLAGS)
    _seal(value); verify(value)
    return value


def verify(value):
    """Verify identities, comparison coverage and the narrow inertia algebra."""
    if (value.get('schema') != 'osr-city-acceleration-sensitivity/1' or value.get('evaluation_id') !=
        identity({k:v for k,v in value.items() if k != 'evaluation_id'})):
        raise ValueError('Sealed acceleration sensitivity required')
    candidate = value.get('candidate_id')
    physical_definition = value.get('physical_definition')
    body_candidate_id = value.get('body_candidate_id')
    body_evaluation_id = value.get('body_evaluation_id')
    if (not isinstance(physical_definition, dict)
        or candidate != identity(physical_definition)
        or physical_definition.get('body_candidate_id') != body_candidate_id
        or not _is_sha256(body_candidate_id) or not _is_sha256(body_evaluation_id)):
        raise ValueError('Sealed physical definition and body identities required')
    if any(value.get(k) is not False for k in FLAGS) or value.get('installed_mass_complete') is not False:
        raise ValueError('Sensitivity cannot grant achieved acceleration, selection, completion or acceptance')
    reference = value.get('retained_control_reference', {})
    if (reference.get('packet_id') != REFERENCE_PACKET or reference.get('manifest_sha256') != REFERENCE_MANIFEST_SHA256 or
        reference.get('outline_evaluation_id') != REFERENCE_EVALUATION or reference.get('control_reproduced') is not True or
        reference.get('original_packet_modified') is not False or reference.get('original_packet_payload_authenticated_by_this_producer') is not False):
        raise ValueError('Original control identity and evidence boundary must remain unchanged')
    cases = value.get('cases', [])
    if (value.get('acceleration_hypotheses_m_s2') != list(ACCELERATIONS) or len(cases) != 3 or
        tuple(r['acceleration_hypothesis_m_s2'] for r in cases) != ACCELERATIONS):
        raise ValueError('Exactly 0.4, 0.6, 0.8 m/s² hypotheses required')
    if cases[0]['source_outline_evaluation_id'] != REFERENCE_EVALUATION:
        raise ValueError('Retained control must reproduce exactly')
    if len({r['source_outline_evaluation_id'] for r in cases}) != 3:
        raise ValueError('Distinct hypothesis evaluations required')
    expected_masses = {load+'-'+c for load in ('tare','normal','crowd-control') for c in outline.CASES}
    baseline_policy = {k:v for k,v in cases[0]['policy'].items() if k != 'acceleration_m_s2'}
    baseline_lines = {r['line_id']:r for r in cases[0]['kinematic_lines']}
    if set(value.get('declared_mass_scenarios_kg', {})) != expected_masses:
        raise ValueError('Exact declared mass scenario coverage required')
    for case in cases:
        if case.get('evaluation_id') != identity({k:v for k,v in case.items() if k != 'evaluation_id'}):
            raise ValueError('Case evaluation identity differs')
        if (case.get('candidate_id') != candidate or case.get('body_candidate_id') != body_candidate_id or
            case.get('body_evaluation_id') != body_evaluation_id or
            case.get('source_city_input_id') != value['source_city_input_id'] or
            any(case.get(k) is not False for k in FLAGS)):
            raise ValueError('Mixed candidate/source or promoted sensitivity case')
        p = outline._policy(case['policy'])
        if (identity(p) != case['policy_id'] or p['acceleration_m_s2'] != case['acceleration_hypothesis_m_s2'] or
            {k:v for k,v in p.items() if k != 'acceleration_m_s2'} != baseline_policy):
            raise ValueError('Only acceleration may change between the declared policies')
        rows = case.get('inertia_only_lower_bound_components', [])
        if len(rows) != 9 or {r['mass_scenario'] for r in rows} != expected_masses:
            raise ValueError('All nine declared mass scenarios required')
        masses = {r['mass_scenario']:r['declared_train_mass_kg'] for r in rows}
        if masses != value['declared_mass_scenarios_kg']:
            raise ValueError('Mass hypotheses must remain identical across acceleration cases')
        for row in rows:
            mass = row['declared_train_mass_kg']; speed = row['speed_at_power_evaluation_m_s']
            if (type(mass) not in (int,float) or not isfinite(mass) or mass <= 0 or
                type(speed) not in (int,float) or not isfinite(speed) or speed <= 0 or
                speed != p['speed_cap_m_s'] or
                row.get('installed_mass_verified') is not False or row.get('includes_six_car_train') is not True or
                not isclose(row['translational_inertia_force_N'],mass*case['acceleration_hypothesis_m_s2'],rel_tol=1e-12) or
                not isclose(row['mechanical_power_at_declared_speed_cap_W'],row['translational_inertia_force_N']*speed,rel_tol=1e-12)):
                raise ValueError('Inertia-only force/power algebra or evidence boundary differs')
        lines = case.get('kinematic_lines', [])
        if (len(lines) != 5 or {r['line_id'] for r in lines} != {'line-'+str(i) for i in range(1,6)} or
            any(r.get('city_candidate_id') != candidate or r.get('body_candidate_id') != body_candidate_id or
                r.get('body_evaluation_id') != body_evaluation_id or r.get('service_evaluation_id') is not None or
                r.get('native_service_complete') is not False for r in lines)):
            raise ValueError('Exact five-line held kinematic coverage required')
        for row in lines:
            base = baseline_lines[row['line_id']]
            if any(row[k] != base[k] for k in ('route_m','station_markers','leg_count','train_length_m',
                    'normal_places_per_train','required_platform_length_m')):
                raise ValueError('Mapped geometry and formation cannot change between acceleration cases')
            if any(row['scenarios'][c]['headway_s'] != base['scenarios'][c]['headway_s'] for c in outline.CASES):
                raise ValueError('Demand/headway controls cannot change between acceleration cases')
    if value['inertia_component_basis'].get('excluded_effects') != list(EXCLUDED):
        raise ValueError('All omitted effects must remain explicit')
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--body',type=Path);parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args(); value = build(body_path=args.body)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('xb') as stream:stream.write(encoded(value))
    print(json.dumps(dict(candidate_id=value['candidate_id'],evaluation_id=value['evaluation_id'],
        cases=len(value['cases']),reference_control_reproduced=True,achieved_acceleration=False,drive_selected=False)))


if __name__ == '__main__':main()
