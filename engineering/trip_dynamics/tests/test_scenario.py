import math
import pytest

from engineering.trip_dynamics.scenario import bind_vehicle, campaign_cases, kinematic_target, scenario, validate
from engineering.trip_dynamics.validation import energy_balance, gate, preflight_result


def test_independent_two_km_target():
    s = scenario('example', 2000, 'AW3', mode='benchmark')
    r = kinematic_target(s, [37618.6666666667]*6)
    assert r['journey_time_s'] == 125.
    assert r['acceleration_distance_m'] == 250.
    assert r['propulsive_force_N'] == pytest.approx(180569.6)
    assert r['arrival_kinetic_energy_kWh'] == pytest.approx(12.5395555556)
    assert r['full_formation_powered_overlap_proved'] is False


def test_case_set_and_identity_refusal():
    cases = campaign_cases()
    assert len(cases) == 9
    assert kinematic_target(cases[2], [25000.]*6)['journey_time_s'] == 100.
    value = cases[0].copy(); value['distance_m'] = 2000
    with pytest.raises(ValueError, match='identity'): validate(value)


def test_physical_and_scenario_identities_are_distinct():
    raw = scenario('route', 2000, 'AW3')
    bound = bind_vehicle(raw, '1'*64)
    assert bound['candidate_id'] == '1'*64
    assert bound['scenario_id'] != bound['candidate_id']
    assert bound['scenario_id'] != raw['scenario_id']
    with pytest.raises(ValueError, match='different physical'):
        bind_vehicle(bound, '2'*64)


@pytest.mark.parametrize('distance', [math.nan, math.inf, -1, 2001])
def test_bad_domain_refused(distance):
    with pytest.raises(ValueError): scenario('bad', distance, 'AW3')


def test_unknown_preflight_does_not_create_trajectory():
    r = preflight_result(campaign_cases()[0], 'candidate', [gate('mass', 'unknown', 'unweighed equipment')])
    assert r['dynamic_execution'] == 'not-run'
    assert r['trajectory'] is None and not r['launch_authorised']
    assert r['engineering_screen'] == 'unknown'


def test_cooling_not_counted_twice_in_energy():
    r = energy_balance(dc_J=10., copper_J=4., emf_J=3., field_change_J=3., cooling_J=1., heat_change_J=3.)
    assert r['electrical_residual_J'] == r['thermal_residual_J'] == 0.
