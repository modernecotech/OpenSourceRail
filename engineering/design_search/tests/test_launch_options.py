"""Independent controls for launch bounds, configuration identities and holds."""
from copy import deepcopy
import json

import pytest

from engineering.design_search import launch_options as launch
from engineering.development_baseline import selection
from engineering.station_rail import operations


def test_zero_drag_energy_and_contact_inertia_distinction():
    row = launch.bounds(120000., 10000., 20., .4, rolling=0.,
                        bearing_per_car=0., aero_per_car=0.)
    assert row['launch_distance_m'] == 500
    assert row['launch_time_s'] == 50
    assert row['required_mechanical_work_kWh'] == pytest.approx(130000 * 200 / 3.6e6)
    assert row['required_body_drive_or_shaft_effort_N'] == 52000
    assert row['optimistic_wheel_contact_force_N'] == 48000
    assert row['lossless_mean_train_CG_drop_m'] == pytest.approx(130000 * 200 / (120000 * launch.G))


def test_independent_drag_work_integral_matches_existing_profile():
    row = launch.bounds(136000., 10600., 20., .4)
    profile = operations.profile(2000., 136000 / 6,
        rotating_equivalent_mass_kg_per_car=10600 / 6)
    assert row['required_mechanical_work_kWh'] == pytest.approx(profile['launch_mechanical_energy_J_per_car'] * 6 / 3.6e6)
    assert row['required_body_drive_or_shaft_effort_N'] == pytest.approx(profile['peak_launch_force_N_per_car'] * 6)


def test_ideal_cable_time_is_faster_than_coasting_but_still_misses_headway():
    t = launch.ideal_trip_time(2000., 20., .4, .6)
    assert t == pytest.approx(141 + 2 / 3)
    assert t + 35 > 120
    assert 2 * (t + 35) == pytest.approx(353 + 1 / 3)
    # Triangular case must not count a negative cruise interval.
    assert launch.ideal_trip_time(10., 20., .4, .4) == pytest.approx(10.)


@pytest.fixture(scope='module')
def result():
    return launch.compare()


def test_reference_numbers_match_independent_audit(result):
    r = result['normal_reference_bound']
    assert result['normal_accounted_mass_kg'] == pytest.approx(136031.989, abs=.001)
    assert result['retained_rotational_equivalent_kg'] == pytest.approx(10622.322, abs=.001)
    assert r['required_body_drive_or_shaft_effort_N'] == pytest.approx(66616.7695, abs=.001)
    assert r['optimistic_wheel_contact_force_N'] == pytest.approx(62367.8408, abs=.001)
    assert r['kinetic_energy_kWh'] == pytest.approx(8.147462, abs=1e-6)
    assert r['lossless_mean_train_CG_drop_m'] == pytest.approx(21.986855, abs=1e-6)
    assert len(result['options']) == 12 and len(result['cases']) == 144


def test_short_roller_bank_fails_even_optimistic_full_train_strip(result):
    row = next(row for row in result['cases'] if row['name'] == 'Wayside rollers, 100 m bank'
               and row['request']['speed_m_s'] == 20 and row['request']['acceleration_m_s2'] == .4
               and row['request']['grade_fraction'] == 0)
    assert row['necessary_bounds']['optimistic_any_contact_travel_m'] == 204.5
    assert row['necessary_bounds']['minimum_bank_under_any_contact_bound_m'] == 395.5
    assert row['necessary_bounds']['optimistic_reach_screen'] == 'fails-bound'
    assert row['engineering_screen'] == 'unknown'


def test_model_hypotheses_do_not_create_new_hardware():
    spec = launch.specification()
    reference = selection.load()
    changed = deepcopy(spec)
    changed['comparison']['traction_adhesion_hypotheses'] = [.2]
    changed['space']['speed_m_s'] = [10.]
    assert launch.options(spec, reference) == launch.options(changed, reference)
    changed['space']['fixed_drive_bank_m'] = [200., 500.]
    assert launch.options(spec, reference)[0]['physical_option_id'] != launch.options(changed, reference)[0]['physical_option_id']


def test_no_concept_or_arithmetic_promotes_missing_physics(result):
    for row in [result, *result['options'], *result['cases']]:
        assert all(row[key] is False for key in launch.FLAGS)
    for option in result['options']:
        assert option['materialized_candidate_id'] is None
        assert option['complete_installed_mass_kg'] is None
        assert option['available_force_map_id'] is None
    assert result['requirement_policy']['integrated_suitability'] == 'unknown'
    assert result['requirement_policy']['numerical_model_admitted'] is False


def test_store_energy_is_not_a_power_admission(result):
    for row in result['reference_conditional_storage']:
        assert row['energy_only_peak_power_to_energy_per_hour'] > 80
        assert row['dc_peak_power_kW'] > 1400
        assert row['actual_installed_store_energy_kWh'] is None
        assert row['hot_EOL_power_voltage_current_thermal_admission'] is False
        assert row['grid_recharge_plus_hotel_during_dwell_kW'] > row['launch_only_recharge_input_kW']


@pytest.mark.parametrize('mass,rotor,speed,acceleration', [
    (0, 1, 20, .4), (1, -1, 20, .4), (1, 1, float('nan'), .4), (1, 1, 20, 0)])
def test_invalid_bound_inputs_fail_closed(mass, rotor, speed, acceleration):
    with pytest.raises(ValueError):
        launch.bounds(mass, rotor, speed, acceleration)


def test_published_payload_cannot_be_rebound_to_claim_acceptance(tmp_path, result, monkeypatch):
    monkeypatch.setattr(launch, 'compare', lambda root: deepcopy(result))
    launch.publish(tmp_path)
    assert launch.verify(tmp_path)['verified'] is True
    folder = tmp_path / launch.OUTPUT
    value = json.loads((folder / 'comparison.json').read_bytes())
    value['physical_accepted'] = True
    (folder / 'comparison.json').write_bytes(launch.encoded(value))
    manifest = json.loads((folder / 'manifest.json').read_bytes())
    manifest['files_sha256']['comparison.json'] = launch.digest(folder / 'comparison.json')
    manifest['manifest_id'] = launch.identity({k:v for k,v in manifest.items() if k != 'manifest_id'})
    (folder / 'manifest.json').write_bytes(launch.encoded(manifest))
    with pytest.raises(ValueError, match='differs'):
        launch.verify(tmp_path)


@pytest.mark.parametrize('key,mutated', [
    ('wheel_store_types', ['battery', 'supercapacitor', 'hybrid', 'battery']),
    ('grade_fraction', [False, .02]),
    ('grade_fraction', [-.02, 0.]),
])
def test_out_of_study_or_duplicate_scenarios_are_rejected(tmp_path, key, mutated):
    source = (launch.ROOT / launch.SPEC).read_text()
    import re
    replacement = json.dumps(mutated)
    source = re.sub(r'^' + key + r' = .*$', key + ' = ' + replacement, source, flags=re.M)
    path = tmp_path / launch.SPEC
    path.parent.mkdir(parents=True)
    path.write_text(source)
    with pytest.raises(ValueError):
        launch.specification(tmp_path)


def test_wrong_manifest_schema_is_rejected_even_with_a_consistent_hash(tmp_path, result, monkeypatch):
    monkeypatch.setattr(launch, 'compare', lambda root: deepcopy(result))
    launch.publish(tmp_path)
    path = tmp_path / launch.OUTPUT / 'manifest.json'
    manifest = json.loads(path.read_bytes())
    manifest['schema'] = 'unrelated/99'
    manifest['manifest_id'] = launch.identity({k:v for k,v in manifest.items() if k != 'manifest_id'})
    path.write_bytes(launch.encoded(manifest))
    with pytest.raises(ValueError, match='differs'):
        launch.verify(tmp_path)
