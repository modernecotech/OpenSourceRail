"""Candidate-bound propulsion evidence gaps; reuse existing equations and maps.

This compiler does not predict available installed thrust. A force-map sample,
including a valid nonlinear moving sample, is only one input to that question.
Run ``python -m engineering.station_rail.force_evidence --help`` for packets.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import subprocess
import sys

from . import ROOT, FLAGS
from .common import digest, encoded, identity
from . import braking, operations
from engineering.trip_dynamics.magnetic_maps import ForceMap, IDENTITY_KEYS

REFERENCE = '756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3'
BODY = '9489e4f2666fd3b3c73232c86df3f12adf42a5531eb27373834cf3fecb1a3117'
PRODUCER = 'engineering/station_rail/force_evidence.py'
DEPENDENCIES = ('engineering/station_rail/operations.py',
    'engineering/station_rail/braking.py', 'engineering/station_rail/common.py',
    'engineering/station_rail/__init__.py', 'engineering/trip_dynamics/magnetic_maps.py')
_LOADED_PATHS = {name: Path(sys.modules[name[:-3].replace('/', '.') if not name.endswith('/__init__.py')
    else name[:-12].replace('/', '.')].__file__).resolve() for name in DEPENDENCIES}
_LOADED_PATHS[PRODUCER] = Path(__file__).resolve()
_LOADED_SHA = {name: digest(path) for name, path in _LOADED_PATHS.items()}


def _verify_source_epoch(root):
    for name, path in _LOADED_PATHS.items():
        if digest(path) != _LOADED_SHA[name]:
            raise ValueError('Loaded source changed during this process: ' + name)
        if digest(root/name) != _LOADED_SHA[name]:
            raise ValueError('Requested root differs from loaded source: ' + name)
MISSING = {
    'installed_force_speed_current_envelope': [
        'Candidate-specific installed propulsion geometry, fixed groups, powered length, overlap and phase registration',
        'Source-bound force/flux/loss maps over moving speed, gap, alignment, current and temperature domains',
        'Winding resistance versus temperature, inductance/flux linkage and coupled current dynamics',
        'Converter/DC-link voltage and current limits, switching/control, faults and protection'],
    'receiving_braking_envelope': [
        'Receiving converter/brake force versus speed/current, limits and degraded modes',
        'Independent wheel brake pressure, pad friction/fade, latency, WSP and degraded-channel evidence'],
    'repeated_duty_temperature': [
        'Repeated copper/core/secondary/converter losses under actual current and receiving-brake duty',
        'Cooling geometry, contact conductance, ambient/initial state and measured temperature limits'],
    'complete_installed_mass_and_power': [
        'All installed primary groups, converters, feeders, switchgear, protection, wiring, cooling and supports',
        'Complete installed vehicle mass, inertia/CG and unresolved inventory overlap'],
}


def _finite(value, name, *, positive=False):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not isfinite(value):
        raise ValueError(name + ' must be a finite number')
    if value < 0 or (positive and value == 0):
        raise ValueError(name + ' must be ' + ('positive' if positive else 'nonnegative'))


def _vehicle(vehicle, root):
    v = deepcopy(vehicle)
    seal = v.pop('evaluation_id', None)
    if seal != identity(v):
        raise ValueError('Vehicle evaluation seal differs')
    candidate = identity(dict(physical_definition=v['physical_definition'],
        **{key: v[key] for key in operations.IDS[1:]}))
    if candidate != v['candidate_id'] or candidate != REFERENCE or v['body_candidate_id'] != BODY:
        raise ValueError('Explicit published passive-wheel reference candidate required')
    if any(v.get(key) is not flag for key, flag in FLAGS.items()):
        raise ValueError('Vehicle cannot grant acceptance')
    physical = v['physical_definition']['vehicle']
    for key in ('onboard_traction_motors', 'onboard_traction_battery_kWh', 'onboard_permanent_magnets'):
        if physical[key] != 0:
            raise ValueError('Onboard traction requires a separate research configuration')
    for name, sha in v['source_sha256'].items():
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or digest(root/path) != sha:
            raise ValueError('Vehicle source differs: ' + name)
    # The candidate binds geometry; the evaluation also binds its derived mass
    # account. A newly sealed, edited subtotal is not the published evaluation.
    from engineering.development_baseline.selection import load
    if vehicle['evaluation_id'] != load(root)['vehicle']['evaluation_id']:
        raise ValueError('Vehicle differs from the source-bound reference evaluation')


def controls():
    """Named retained controls, not selected service or mandatory brake limits."""
    return [dict(name=loading + '-2000m-retained-control', loading=loading,
        duty=dict(headway_s=120., dwell_s=35., ambient_C=50.),
        distance_m=2000., profile={}, stopping=dict(speed_m_s=20.,
            adhesion_coefficient=.05, downhill_grade_fraction=.02,
            reaction_s=1., target_deceleration_m_s2=.6))
        for loading in ('normal_46', 'crowd_160_control')]


def audit(vehicle, scenarios, *, root=ROOT, map_request=None):
    """Compile analytical requirements and declared-domain samples without solving.

    map_request must contain map, expected_identity (all four explicit IDs), and
    queries. No body/material identity is inferred from a component or vehicle.
    """
    root = Path(root).resolve()
    _verify_source_epoch(root)
    _vehicle(vehicle, root)
    if not scenarios:
        raise ValueError('At least one explicit named scenario required')
    samples = []
    metadata = None
    if map_request is not None:
        expected = map_request['expected_identity']
        if set(expected) != set(IDENTITY_KEYS) or expected['candidate_id'] != vehicle['candidate_id']:
            raise ValueError('All four exact map identities must bind the vehicle candidate')
        model = ForceMap(map_request['map'], expected_identity=expected)
        for name, sha in model.metadata['source_sha256'].items():
            if digest(root/name) != sha:
                raise ValueError('Force-map source differs: ' + name)
        metadata = model.metadata
        samples = [model.sample(query) for query in map_request['queries']]
        if not samples:
            raise ValueError('Explicit force-map queries required')
    rotor = braking.rotating_stock(vehicle)
    masses = dict(empty='accounted_tare_kg_per_car', normal_46='accounted_cap_loaded_kg_per_car',
        crowd_160_control='accounted_160_control_kg_per_car')
    rows = []
    names = set()
    for scenario in scenarios:
        name = scenario['name']
        if not isinstance(name, str) or not name or name in names:
            raise ValueError('Unique nonempty scenario name required')
        names.add(name)
        loading = scenario['loading']
        if loading not in masses:
            raise ValueError('Explicit empty, normal_46 or crowd_160_control loading required')
        _finite(scenario['distance_m'], 'distance_m', positive=True)
        kwargs = dict(scenario.get('profile', {}))
        if set(kwargs) - {'speed_cap_m_s', 'acceleration_m_s2', 'service_deceleration_m_s2',
                'rolling_coefficient', 'bearing_drag_N_per_car',
                'quadratic_drag_N_per_car_per_m_s_squared', 'grade_fraction', 'headwind_m_s'}:
            raise ValueError('Unsupported profile override; mass/formation remain candidate-bound')
        for key, value in kwargs.items():
            if isinstance(value, bool) or not isinstance(value, (float, int)) or not isfinite(value):
                raise ValueError('Finite profile control required: ' + key)
        stop = dict(scenario['stopping'])
        required = {'speed_m_s', 'adhesion_coefficient', 'downhill_grade_fraction',
            'reaction_s', 'target_deceleration_m_s2'}
        if set(stop) != required:
            raise ValueError('Explicit complete stopping hypotheses required')
        for key, value in stop.items():
            _finite(value, key, positive=key == 'target_deceleration_m_s2')
        duty = dict(scenario['duty'])
        if set(duty) != {'headway_s', 'dwell_s', 'ambient_C'}:
            raise ValueError('Explicit headway, dwell and ambient duty hypotheses required')
        for key in ('headway_s', 'dwell_s'):
            _finite(duty[key], key, positive=key == 'headway_s')
        if isinstance(duty['ambient_C'], bool) or not isinstance(duty['ambient_C'], (int, float)) or not isfinite(duty['ambient_C']):
            raise ValueError('Finite ambient temperature required')
        if duty['dwell_s'] >= duty['headway_s']:
            raise ValueError('Duty dwell must be below the named headway')
        requirement = operations.profile(scenario['distance_m'], vehicle['mass'][masses[loading]],
            cars=vehicle['physical_definition']['vehicle']['cars'], loading=loading,
            rotating_equivalent_mass_kg_per_car=rotor['equivalent_inertial_mass_kg_per_car'], **kwargs)
        rows.append(dict(name=name, loading=loading, passenger_mass_kg=75.,
            people_per_car={'empty': 0, 'normal_46': 46, 'crowd_160_control': 160}[loading],
            scope='Named analytical control; accounted mass, not complete installed mass',
            requested_data_domain=dict(speed_m_s=[0., kwargs.get('speed_cap_m_s', 20.)],
                signed_current_A=None, terminal_voltage_V=None, gap_alignment_and_phase=None,
                temperature_C=None, duty_hypotheses=duty,
                unknown_bounds='Current, voltage, alignment and temperature require installed drive/cooling definitions'),
            requirement=requirement, independent_stopping_requirement=operations.brake_bound(**stop),
            actual_installed_force_available_N=None, actual_terminal_voltage_V=None,
            actual_current_limit_A=None, repeated_duty_temperature_C=None,
            engineering_screen='held', missing_evidence=deepcopy(MISSING)))
    result = dict(schema='osr-candidate-force-evidence/1',
        **{key: vehicle[key] for key in operations.IDS}, vehicle_evaluation_id=vehicle['evaluation_id'],
        scope='Published passive-wheel reference; capstan/powered-axle research excluded',
        units=dict(force='N', speed='m/s', current='A', voltage='V', time='s', mass='kg', temperature='degC'),
        source_sha256={**vehicle['source_sha256'], **{p: digest(root/p) for p in DEPENDENCIES}},
        producer_sha256=_LOADED_SHA[PRODUCER], input_scenarios=deepcopy(scenarios),
        accounted_mass=deepcopy(vehicle['mass']), rotating_stock=rotor, scenarios=rows,
        force_map_metadata=metadata, model_force_samples=samples,
        model_samples_establish_installed_force=False, actual_installed_force_available_N=None,
        available_data_domain=None if metadata is None else metadata['axes'],
        execution_status='executed', numerical_validity='analytical-requirements-only',
        engineering_screen='held', physical_journey_completed=False,
        limitations=['No native solver run or new measured evidence',
            'Force-map samples alone do not close moving group overlap, phase, current/voltage or repeated thermal duty',
            'Friction-only stopping requirement credits neither regeneration nor resistance; assumptions are not approved limits'],
        **FLAGS)
    _verify_source_epoch(root)
    result['evaluation_id'] = identity(result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--scenarios', type=Path, help='JSON list; default two named retained controls')
    parser.add_argument('--map-request', type=Path, help='JSON map, all four expected_identity fields, and queries')
    parser.add_argument('--output', type=Path, required=True, help='New external directory; never overwritten')
    args = parser.parse_args(argv)
    root, output = args.root.resolve(), args.output.resolve()
    if output == root or root in output.parents:
        parser.error('Evidence output must be outside the source checkout')
    from engineering.development_baseline.selection import load
    inputs = {}
    for name, path in (('scenarios.json', args.scenarios), ('map-request.json', args.map_request)):
        if path is not None:
            with path.open('rb') as stream:
                raw = stream.read(32*1024**2 + 1)
            if len(raw) > 32*1024**2:
                parser.error('Input exceeds 32 MiB budget: ' + name)
            inputs[name] = raw
    scenarios = json.loads(inputs['scenarios.json']) if args.scenarios else controls()
    request = json.loads(inputs['map-request.json']) if args.map_request else None
    value = audit(load(root)['vehicle'], scenarios, root=root, map_request=request)
    value['runtime_source_commit'] = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    value['producer_source_commit'] = subprocess.check_output(['git', '-C', str(Path(__file__).parent), 'rev-parse', 'HEAD'], text=True).strip()
    value['command_arguments'] = dict(root=str(root), scenarios=str(args.scenarios), map_request=str(args.map_request), output=str(output))
    value['retained_inputs'] = {name: dict(bytes=len(raw), sha256=sha256(raw).hexdigest())
        for name, raw in inputs.items()}
    value.pop('evaluation_id')
    value['evaluation_id'] = identity(value)
    output.mkdir(parents=True, exist_ok=False)
    for name, raw in inputs.items():
        (output/name).write_bytes(raw)
    (output/'result.json').write_bytes(encoded(value))
    (output/'SHA256SUMS').write_text(''.join(digest(output/name) + '  ' + name + '\n'
        for name in ['result.json', *sorted(inputs)]))
    print(json.dumps(dict(evaluation_id=value['evaluation_id'], engineering_screen='held', output=str(output))))


if __name__ == '__main__':
    main()
