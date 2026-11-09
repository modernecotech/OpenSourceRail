"""Acceleration assumptions are separate evaluations, never installed capability."""
from copy import deepcopy
from pathlib import Path

import pytest

from engineering.railway_project import city_acceleration_sensitivity as study
from engineering.station_rail.common import digest, identity


@pytest.fixture(scope='module')
def result():
    root = Path(study.ROOT)
    names = [study.outline.PRODUCER,study.outline.POLICY,study.outline.BODY_FILE,
        'cities/catalogue/west-asia/Iraq/Samawah/engineering/outline/manifest.json']
    before = {name:digest(root/name) for name in names}
    value = study.build()
    assert {name:digest(root/name) for name in names} == before
    return value


def reseal(value):
    value['evaluation_id'] = identity({k:v for k,v in value.items() if k != 'evaluation_id'})
    return value


def test_original_control_reproduces_and_physical_candidate_stays_fixed(result):
    assert study.verify(result)
    assert result['cases'][0]['source_outline_evaluation_id'] == study.REFERENCE_EVALUATION
    assert result['acceleration_hypotheses_m_s2'] == [0.4,0.6,0.8]
    assert len({r['source_outline_evaluation_id'] for r in result['cases']}) == 3
    assert {r['candidate_id'] for r in result['cases']} == {result['candidate_id']}
    assert all(r['body_candidate_id'] == study.outline.BODY and
        r['body_evaluation_id'] == study.outline.BODY_EVALUATION for r in result['cases'])
    assert result['retained_control_reference']['original_packet_modified'] is False


def test_all_nine_inertia_components_follow_ma_and_mav_without_extra_loads(result):
    baseline = {r['mass_scenario']:r for r in result['cases'][0]['inertia_only_lower_bound_components']}
    assert len(baseline) == 9
    for case in result['cases']:
        acceleration = case['acceleration_hypothesis_m_s2']
        for row in case['inertia_only_lower_bound_components']:
            force = row['declared_train_mass_kg']*acceleration
            assert row['translational_inertia_force_N'] == pytest.approx(force)
            assert row['mechanical_power_at_declared_speed_cap_W'] == pytest.approx(force*20)
            assert row['translational_inertia_force_N'] == pytest.approx(
                baseline[row['mass_scenario']]['translational_inertia_force_N']*acceleration/0.4)
            assert row['installed_mass_verified'] is False
    assert result['inertia_component_basis']['excluded_effects'] == list(study.EXCLUDED)


def test_higher_hypotheses_only_change_conditional_runtime_and_fleet_requests(result):
    for previous,current in zip(result['cases'],result['cases'][1:]):
        before = {r['line_id']:r for r in previous['kinematic_lines']}
        for row in current['kinematic_lines']:
            assert row['assumed_cycle_s'] < before[row['line_id']]['assumed_cycle_s']
            for c in study.outline.CASES:
                assert row['scenarios'][c]['total_trainsets'] <= before[row['line_id']]['scenarios'][c]['total_trainsets']
                assert row['scenarios'][c]['headway_s'] == before[row['line_id']]['scenarios'][c]['headway_s']
                assert row['scenarios'][c]['available_force_N'] is None
                assert row['scenarios'][c]['braking_distance_m'] is None
        assert current['definition_failures'] == previous['definition_failures']
    assert all(result[k] is False for k in study.FLAGS)
    assert all(case[k] is False for case in result['cases'] for k in study.FLAGS)


def test_resealed_missing_mass_mixed_identity_false_power_or_promotion_refuses(result):
    mutations = [
        lambda r:r['cases'][1]['inertia_only_lower_bound_components'].pop(),
        lambda r:r['cases'][1].update(body_evaluation_id='f'*64),
        lambda r:r['cases'][1]['inertia_only_lower_bound_components'][0].update(translational_inertia_force_N=0),
        lambda r:r['cases'][1].update(achieved_acceleration=True),
        lambda r:r['cases'][1]['inertia_only_lower_bound_components'][0].update(speed_at_power_evaluation_m_s=30),
    ]
    for edit in mutations:
        bad = deepcopy(result);edit(bad)
        for case in bad['cases']:reseal(case)
        reseal(bad)
        with pytest.raises(ValueError):study.verify(bad)
    bad = deepcopy(result);bad['retained_control_reference']['outline_evaluation_id'] = 'f'*64;reseal(bad)
    with pytest.raises(ValueError,match='Original control'):study.verify(bad)
