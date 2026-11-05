"""Independent mechanics controls and immutable Rust bridge contracts."""
from copy import deepcopy
import json
import math
import os

import pytest

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from engineering.station_energy import examples, runner


@pytest.fixture
def kernel():
    binary = ROOT/runner.TARGET/'release/osr-station-energy'
    if not binary.exists():
        if os.environ.get('OSR_TEST_STATION_ENERGY') == '1':
            pytest.fail('Explicit station-energy Rust build required')
        pytest.skip('Run python -m engineering.station_energy build first')
    return binary


def evaluate(case):
    return runner.calculate(dict(schema=examples.SCHEMA, cases=[case]))[0]['cases'][0]


def test_synthetic_examples_explore_speed_without_selecting_a_solution():
    request = examples.request()
    assert len(request['cases']) == 123
    assert len({c['id'] for c in request['cases']}) == 123
    assert {round(c['target_speed_m_s']*3.6) for c in request['cases']} == {40, 50, 60, 72}
    assert sum(c['capture_speed_m_s'] == 0 for c in request['cases']) == 12
    assert {c['booster_length_m'] for c in request['cases']} == {100, 200, 300}


def test_proposal_has_no_hidden_physical_adoption():
    from engineering.outline import approaches
    catalogue = approaches.catalogue()
    row = next(r for r in catalogue['policy']['approaches']
        if r['id'] == 'station-regenerative-mechanical-launch')
    assert row['outline_adapter'] == 'requires-approach-specific-adapter'
    assert 'engineering.station_energy' in row['screening_adapter']
    assert catalogue['capability_declarations_grant_dispatch'] is False


def test_illustration_independently_reproduced(kernel):
    result = evaluate(examples.reference_case())
    assert result['capture']['kinetic_energy_j'] == pytest.approx(2000000.0)
    assert result['capture']['required_stroke_m'] == pytest.approx(15.625)
    assert result['storage']['delivered_j'] == pytest.approx(1400000.0)
    assert result['storage']['delivered_from_initial_j'] == 0.0
    assert result['motion']['ideal_launch_speed_m_s'] == pytest.approx(math.sqrt(17.5))
    assert result['booster']['net_acceleration_m_s2'] == pytest.approx(0.95625)
    assert result['booster']['required_force_n'] == pytest.approx(153000.0)
    assert result['booster']['peak_mechanical_power_w'] == pytest.approx(3060000.0)
    assert result['booster']['peak_source_power_w'] == pytest.approx(3400000.0)
    assert result['booster']['time_s'] == pytest.approx(16.54033973054078)
    assert abs(result['energy_residual_j']) < 1e-7
    assert result['unknowns']
    assert all(result[k] is False for k in runner.FLAGS)


def test_all_ordinary_sweeps_match_independent_closed_form(kernel):
    request = examples.request()
    request['cases'] = request['cases'][:120]
    result, _ = runner.calculate(request)
    for case, row in zip(request['cases'], result['cases'], strict=True):
        mass = case['effective_mass_kg']
        expected_energy = 0.5*mass*case['capture_speed_m_s']**2*case['efficiency_capture']
        launch = math.sqrt(2*expected_energy/mass)
        target = case['target_speed_m_s']
        acceleration = (target**2-launch**2)/(2*case['booster_length_m'])
        assert row['storage']['delivered_j'] == pytest.approx(expected_energy)
        assert row['motion']['ideal_launch_speed_m_s'] == pytest.approx(launch)
        assert row['booster']['required_force_n'] == pytest.approx(mass*acceleration)
        assert row['booster']['peak_mechanical_power_w'] == pytest.approx(mass*acceleration*target)
        assert row['booster']['time_s'] == pytest.approx(2*case['booster_length_m']/(target+launch))
        assert abs(row['energy_residual_j']) < 1e-6


def test_two_percent_uphill_offset_does_not_become_powered_length(kernel):
    case = examples.reference_case()
    case.update(grade_fraction=0.02, booster_offset_m=200.0)
    row = evaluate(case)
    assert row['motion']['booster_reached'] is False
    assert row['necessary_bounds'] == 'fail'
    assert row['booster']['required_force_n'] is None
    gravity_force = case['physical_mass_kg']*9.80665*math.sin(math.atan(0.02))
    assert row['motion']['coast_distance_travelled_m'] == pytest.approx(
        row['storage']['delivered_j']/gravity_force)


def test_capacity_overflow_and_two_departures_cannot_duplicate_energy(kernel):
    case = examples.reference_case()
    case.update(store_capacity_j=1000000.0, store_initial_j=500000.0)
    first = evaluate(case)
    assert first['storage']['overflow_j'] > 0
    assert first['storage']['delivered_j'] <= 1000000.0
    second_case = deepcopy(case)
    second_case.update(capture_speed_m_s=0.0, store_initial_j=first['storage']['end_j'])
    second = evaluate(second_case)
    assert second['storage']['delivered_j'] == 0.0
    assert abs(first['energy_residual_j']) < 1e-6
    assert abs(second['energy_residual_j']) < 1e-6


def test_independent_loss_reserve_and_energy_origin_fixture(kernel):
    case = examples.reference_case()
    case.update(store_initial_j=200000.0, store_capacity_j=800000.0,
        efficiency_capture=0.8, efficiency_store=0.9, efficiency_release=0.7,
        standing_loss_w=100.0, dwell_s=30.0, store_reserve_j=50000.0)
    row = evaluate(case)
    assert row['storage']['accepted_j'] == pytest.approx(600000.0)
    assert row['storage']['overflow_j'] == pytest.approx(840000.0)
    assert row['storage']['standing_loss_j'] == pytest.approx(3000.0)
    assert row['storage']['delivered_j'] == pytest.approx(522900.0)
    assert row['storage']['delivered_from_initial_j'] == pytest.approx(137900.0)
    assert row['storage']['delivered_from_new_capture_j'] == pytest.approx(385000.0)
    assert row['storage']['end_j'] == pytest.approx(50000.0)
    assert abs(row['energy_residual_j']) < 1e-6


def test_rotating_inertia_does_not_inflate_gravitational_mass(kernel):
    case = examples.reference_case()
    case.update(effective_mass_kg=170000.0, physical_mass_kg=160000.0,
        grade_fraction=0.02, resistance_n=3000.0)
    row = evaluate(case)
    assert row['capture']['opposing_work_j'] == pytest.approx(537109.4629101468)
    assert row['capture']['available_braking_work_j'] == pytest.approx(1587890.537089853)


def test_spring_direction_and_resource_conflict_are_preserved(kernel):
    cases = examples.request()['cases'][-3:]
    result, _ = runner.calculate(dict(schema=examples.SCHEMA, cases=cases))
    assert all(r['necessary_bounds'] == 'fail' for r in result['cases'])
    assert result['cases'][0]['storage']['delivered_j'] == 0.0
    assert result['cases'][2]['resource']['headway_margin_s'] < 0


@pytest.mark.parametrize('patch', (
    {'efficiency_capture': 1.1}, {'store_initial_j': -1.0},
    {'physical_mass_kg': 0.0}, {'target_speed_m_s': True},
    {'booster_length_m': -1.0}, {'pretend_physical_accepted': True},
))
def test_malformed_physics_input_rejected(kernel, patch):
    case = examples.reference_case()
    case.update(patch)
    with pytest.raises((ValueError, RuntimeError)):
        evaluate(case)


def test_unknown_propulsion_capacity_never_passes_as_available_force(kernel):
    row = evaluate(examples.reference_case())
    assert row['necessary_bounds'] == 'unknown'
    assert row['braking']['physical_capability_verified'] is False
    case = examples.reference_case()
    case['source_power_limit_w'] = 100000.0
    limited = evaluate(case)
    assert limited['necessary_bounds'] == 'fail'


def test_immutable_package_replays_and_rejects_resealed_false_data(kernel, tmp_path):
    output = tmp_path/'study'
    request = dict(schema=examples.SCHEMA, cases=[examples.reference_case()])
    manifest = runner.run(output, request)
    assert runner.verify(output) == manifest
    with pytest.raises(ValueError, match='fresh immutable'):
        runner.run(output, request)
    value = json.loads((output/'result.json').read_bytes())
    value['result']['cases'][0]['booster']['required_force_n'] = 1.0
    value['evaluation_id'] = identity({k:v for k,v in value.items() if k != 'evaluation_id'})
    (output/'result.json').write_bytes(encoded(value))
    manifest['evaluation_id'] = value['evaluation_id']
    manifest['files_sha256']['result.json'] = digest(output/'result.json')
    manifest['manifest_id'] = identity({k:v for k,v in manifest.items() if k != 'manifest_id'})
    (output/'manifest.json').write_bytes(encoded(manifest))
    with pytest.raises(ValueError, match='replay differs'):
        runner.verify(output)


def test_duplicate_case_ids_rejected_before_kernel():
    case = examples.reference_case()
    with pytest.raises(ValueError, match='Unique'):
        runner.calculate(dict(schema=examples.SCHEMA, cases=[case, case]))
