"""Cheap electrical bounds and experiment receipts; no native solve or acceptance."""
from copy import deepcopy
from math import sqrt
import fcntl
import json
from pathlib import Path

import pytest

from engineering.railway_completion import experiments as e
from engineering.station_rail.common import encoded, identity


def read(path):
    return json.loads(Path(path).read_bytes())


def write(path, value):
    Path(path).write_bytes(encoded(value))


def reseal(folder, value):
    value['experiment_id'] = identity({k: v for k, v in value.items()
                                       if k not in ('new_runs', 'experiment_id')})
    write(folder / 'latest.json', value)


@pytest.fixture(scope='module')
def matrix():
    return {row['name']: row for row in e.cases()}


def test_real_reference_and_rewound_geometry_have_independently_reproduced_power_bounds(matrix):
    base = matrix['launch-reference-rated']['request']
    rewound = matrix['rewound-running']['request']
    for request, expected in ((base, False), (rewound, True)):
        result = e.electrical_bound(request)
        p = request['physical_geometry']
        definition = request['motor_definition']
        rho = definition['copper_resistivity_20C_ohm_m_hypothesis'] * (
            1 + definition['copper_temperature_coefficient_K_inv_hypothesis'] *
            (request['temperature_C'] - 20))
        resistance = request['wiring']['coils_per_path'] * rho * definition['wire_length_m_per_coil'] / p['conductor_area_m2']
        voltage = 375 / sqrt(2)
        limit = min(request['current_limit_A'] / sqrt(2),
                    4 * p['conductor_area_m2'] * 1e6)
        current = min(limit, voltage / (2 * resistance))
        branches = request['wiring']['branches']
        apparent = branches * voltage * current
        copper = branches * resistance * current ** 2
        assert result['branch_RMS_current_A'] == pytest.approx(limit)
        assert result['sinusoidal_apparent_power_ceiling_VA'] == pytest.approx(apparent)
        assert result['optimistic_copper_loss_W'] == pytest.approx(copper)
        assert result['optimistic_mechanical_power_ceiling_W'] == pytest.approx(apparent - copper)
        assert result['passes_declared_sinusoidal_bound'] is expected
        assert result['required_mechanical_peak_W'] == pytest.approx(1043465.1683394368)
        assert all(result[key] is False for key in e.FLAGS)
        assert 'Conditional quasi-steady sinusoidal' in result['scope']
    assert base['bundle_id'] != rewound['bundle_id']
    assert base['physical_geometry']['conductor_area_m2'] < rewound['physical_geometry']['conductor_area_m2']
    assert base['current_density_limit_RMS_A_mm2'] == rewound['current_density_limit_RMS_A_mm2'] == 4
    assert e.electrical_bound(base)['optimistic_mechanical_power_ceiling_W'] == pytest.approx(717747.1422750719)
    assert e.electrical_bound(rewound)['optimistic_mechanical_power_ceiling_W'] == pytest.approx(1189160.2558489598)


def test_zero_voltage_bound_cannot_supply_launch_power(matrix):
    result = e.electrical_bound(matrix['zero']['request'])
    assert result['sinusoidal_apparent_power_ceiling_VA'] == 0
    assert result['optimistic_copper_loss_W'] == 0
    assert result['optimistic_mechanical_power_ceiling_W'] == 0
    assert result['passes_declared_sinusoidal_bound'] is False


def test_eight_case_matrix_keeps_controls_separate_from_candidate_screens(matrix):
    assert len(matrix) == 8
    assert sum(row['purpose'] == 'method-control' for row in matrix.values()) == 4
    assert sum(row['purpose'] == 'candidate-screen' for row in matrix.values()) == 4
    assert len({row['request']['request_id'] for row in matrix.values()}) == 8
    assert matrix['inside-forward']['request']['phase_direction'] == 1
    assert matrix['inside-reverse']['request']['phase_direction'] == -1
    assert matrix['inside-forward']['request']['motor_component_id'] == matrix['inside-reverse']['request']['motor_component_id']
    for row in matrix.values():
        e.motor.validate(row['request'])


@pytest.fixture
def pending(tmp_path):
    folder = tmp_path / 'pending'
    result = e.run(folder, maximum_new_runs=0)
    assert result['new_runs'] == 0 and len(result['pending']) == 8 and result['rows'] == []
    return folder


def test_zero_budget_retains_complete_exact_pending_matrix_without_execution(pending):
    result = e.verify_index(pending)
    assert len(result['pending']) == 8
    assert not (pending / 'runs').exists()
    assert not (pending / 'latest.json.tmp').exists()
    assert all(result[key] is False for key in e.FLAGS)


@pytest.mark.parametrize('mutation', [
    lambda value: value.update(tool_identity={}),
    lambda value: value['tool_identity'].pop('numpy'),
    lambda value: value['tool_identity'].update(unrequested='extra-tool'),
    lambda value: value['tool_identity'].update(python_sha256='A' * 64),
    lambda value: value['tool_identity'].update(superlu_sha256='not-a-digest'),
    lambda value: value['tool_identity'].update(scipy=''),
    lambda value: value['pending'][0].update(output='../outside'),
    lambda value: value['pending'][0]['request'].update(speed_m_s=13.),
    lambda value: value['pending'].pop(),
    lambda value: value['pending'].append(deepcopy(value['pending'][0])),
    lambda value: value['source_sha256'].update({'fictional.py': 'a' * 64}),
])
def test_pending_matrix_reseals_cannot_change_tool_source_request_or_path(pending, mutation):
    value = read(pending / 'latest.json')
    mutation(value)
    reseal(pending, value)
    with pytest.raises(ValueError):
        e.verify_index(pending)


@pytest.fixture
def method_state(tmp_path, monkeypatch):
    """Test-only backend wiring fixture; never a numerical result or force map."""
    calls = []
    recorded = {k: v for k, v in e.motor._tool(e.cases()[0]['request']).items()
                if k in e.motor.TOOL_IDENTITY_FIELDS}
    def fake_run(request, output, **options):
        calls.append(request['request_id'])
        output = Path(output); output.mkdir(parents=True)
        result = dict(bundle_id=request['bundle_id'], motor_component_id=request['motor_component_id'],
                      request_id=request['request_id'], execution='completed', state='UNIT-TEST-ONLY-NO-SOLVER',
                      test_fixture_only=True, trace=[], **e.FLAGS)
        result['evaluation_id'] = identity(result)
        write(output / 'result.json', result)
        write(output / 'input.json', dict(request=request))
        return result
    def fake_verify(path, **options):
        return dict(verified=True, recorded_tool_identity=recorded)
    monkeypatch.setattr(e.motor, 'run', fake_run)
    monkeypatch.setattr(e.motor, 'verify', fake_verify)
    folder = tmp_path / 'test-only-state'
    value = e.run(folder)
    return folder, value, calls


def test_necessary_bound_holds_skip_backend_while_low_voltage_method_controls_execute(method_state):
    folder, value, calls = method_state
    assert len(value['rows']) == 8 and not value['pending'] and len(calls) == 6
    held = [row for row in value['rows'] if row['summary']['execution'] == 'held-necessary-bound']
    assert {row['summary']['name'] for row in held} == {'launch-reference-rated', 'launch-wide-return-rated'}
    assert all(row['request']['request_id'] not in calls for row in held)
    assert all(row['summary']['available_operating_map'] is False for row in value['rows'])
    for row in held:
        assert {p.name for p in (folder / row['output']).iterdir()} == {'input.json', 'result.json'}
        assert row['summary']['steps'] == 0 and row['summary']['final_thrust_N'] is None
    assert e.verify_index(folder)['experiment_id'] == value['experiment_id']


@pytest.mark.parametrize('mutation', ['native-file', 'execution', 'source', 'bound', 'purpose'])
def test_resealed_necessary_bound_cannot_masquerade_as_native_evidence(method_state, mutation):
    folder, value, _ = method_state
    row = next(r for r in value['rows'] if r['summary']['execution'] == 'held-necessary-bound')
    path = folder / row['output']
    if mutation == 'native-file':
        (path / 'worker-result.json').write_text('{"pretend_native":true}')
    elif mutation == 'execution':
        result = read(path / 'result.json'); result['execution'] = 'completed'
        result['evaluation_id'] = identity({k: v for k, v in result.items() if k != 'evaluation_id'})
        write(path / 'result.json', result)
        row['summary'] = e._summary(row['summary']['name'], result)
    elif mutation == 'source':
        inputs = read(path / 'input.json'); inputs['source_sha256'] = {}
        write(path / 'input.json', inputs)
    elif mutation == 'bound':
        row['electrical_bound']['passes_declared_sinusoidal_bound'] = True
    else:
        row['purpose'] = 'method-control'
    reseal(folder, value)
    with pytest.raises(ValueError):
        e.verify_index(folder)


def test_tool_reseal_and_all_path_renames_cannot_relabel_recorded_backend(method_state):
    folder, value, _ = method_state
    value['tool_identity']['python'] = 'UNIT-TEST-FORGED-RECORDED-TOOL'
    for row in value['rows']:
        key = identity(dict(request_id=row['request']['request_id'], source_sha256=value['source_sha256'],
                            tool_identity=value['tool_identity']))
        old = folder / row['output']; row['output'] = 'runs/' + key
        old.rename(folder / row['output'])
    reseal(folder, value)
    with pytest.raises(ValueError, match='actual recorded package'):
        e.verify_index(folder)


def test_disposable_test_backend_publication_retains_holds_and_no_acceptance(method_state, tmp_path):
    folder, _, _ = method_state
    output = tmp_path / 'publication'
    e.publish(folder, output)
    result = e.verify_publication(output)
    assert result['verified'] and result['runs'] == 8 and result['pending'] == 0
    assert all(result[key] is False for key in e.FLAGS)


def test_concurrent_coordinator_is_refused_without_dispatch(tmp_path, monkeypatch):
    with (tmp_path / '.coordinator.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        def forbidden(*args, **kwargs):
            raise AssertionError('Locked coordinator cannot dispatch or rewrite state')
        monkeypatch.setattr(e, '_run', forbidden)
        with pytest.raises(ValueError, match='already running'):
            e.run(tmp_path)
    assert not (tmp_path / 'latest.json').exists()
