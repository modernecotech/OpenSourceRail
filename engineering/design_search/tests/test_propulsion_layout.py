"""Whole-trip, mass-feedback and non-promoting propulsion controls."""
from copy import deepcopy
from pathlib import Path
import gzip
import json

import pytest

from engineering.design_search import propulsion_layout as study
from engineering.development_baseline.selection import load
from engineering.station_rail import braking, common


def reference():
    value = load()
    value['_services'] = common.brief()['services']
    return value


def test_powered_cruise_counts_full_route_and_grade_work():
    service = study.specification()['service']
    m, rotor = 136031.989, 10622.322
    flat = study.trajectory_request(m, rotor, 20., .4, 0., 'sustain-to-brake', service)
    uphill = study.trajectory_request(m, rotor, 20., .4, .02, 'sustain-to-brake', service)
    assert flat['runtime_s'] == pytest.approx(141 + 2/3)
    assert flat['required_mechanical_energy_kWh'] == pytest.approx(11.530353, abs=1e-6)
    assert uphill['required_mechanical_energy_kWh'] == pytest.approx(23.882372, abs=1e-6)
    assert not flat['physical_journey_completed']
    assert uphill['required_mechanical_energy_kWh'] > 2 * flat['required_mechanical_energy_kWh']
    coast = study.trajectory_request(m, rotor, 20., .4, .02, 'launch-coast', service)
    assert coast['target_reachable'] is False


@pytest.mark.parametrize('count', [2, 4, 6, 8, 10, 12])
def test_bogie_indices_keep_identical_three_car_groups(count):
    indices = study.powered_bogie_indices(count)
    assert len(indices) == count and len(set(indices)) == count
    assert all(0 <= n < 12 for n in indices)
    assert [n + 6 for n in indices if n < 6] == [n for n in indices if n >= 6]


def test_seed_failure_is_preserved_before_storage_sizing():
    spec = study.specification()
    root = Path(study.ROOT)
    cap = json.loads((root / study.CAPACITOR).read_bytes())
    drive = json.loads((root / study.DRIVE).read_bytes())
    row = study.wheel_case(2, 20., .4, 0., 'sustain-to-brake', reference(), spec, cap, drive)
    assert row['calculation_status'] == 'fails-optimistic-adhesion-bound'
    assert row['sizing_trials'] == []
    assert row['actual_installed_mass_kg'] is None
    assert row['materialized_candidate_id'] is None


@pytest.fixture(scope='module')
def result():
    return study.compare()


def test_final_cap_count_and_mass_request_are_the_same_iteration(result):
    row = next(row for row in result['wheel_cases'] if 'inventory' in row)
    final = row['sizing_trials'][-1]
    previous = row['sizing_trials'][-2]
    assert final['storage']['module_count'] == previous['storage']['module_count']
    assert final['capacitor_bare_mass_used_kg'] == row['storage']['bare_module_mass_kg']
    assert final['comparison_mass_kg'] == row['inventory']['comparison_total_kg']
    assert row['inventory']['comparison_total_kg'] == pytest.approx(sum(
        row['inventory'][name] for name in ('inherited_account_kg', 'donor_motor_and_gear_catalogue_kg',
        'capacitor_bare_module_kg', 'unweighed_allowance_hypothesis_kg')))
    assert row['inventory']['actual_complete_installed_kg'] is None


def test_powered_rotor_is_not_miscounted_as_forward_adhesion_demand(result):
    row = next(row for row in result['wheel_cases'] if 'inventory' in row)
    inv, request = row['inventory'], row['request']
    f = 2 * request['powered_bogies'] / 24
    powered_rotor = inv['retained_rotating_equivalent_kg'] * f + inv['extra_powered_rotor_equivalent_hypothesis_kg']
    expected = row['target_profile']['required_peak_shaft_force_N'] - request['acceleration_m_s2'] * powered_rotor
    assert row['adhesion']['required_powered_contact_N'] == pytest.approx(expected)


def test_sparse_six_site_geometry_does_not_divide_train_force_by_six(result):
    three = next(r for r in result['sparse_cases'] if r['site_count'] == 3 and r['bank_length_m'] == 20)
    six = next(r for r in result['sparse_cases'] if r['site_count'] == 6 and r['bank_length_m'] == 20)
    assert three['geometry']['geometric_covered_m'] == 220.5
    assert six['geometry']['geometric_covered_m'] == 500
    assert six['geometry']['min_sum_overlap_m'] == 9
    assert six['necessary_force_at_least_one_final_site_N'] == pytest.approx(66616.7695, abs=.001)
    assert six['available_position_force_map'] is None


def test_all_concepts_keep_qualification_and_prices_open(result):
    assert len(result['wheel_cases']) == 144
    assert len(result['sparse_cases']) == 12
    for row in [result, *result['wheel_cases'], *result['sparse_cases']]:
        assert all(row[key] is False for key in study.FLAGS)
    assert result['requirement_policy']['integrated_suitability'] == 'unknown'
    assert result['actual_whole_life_cost_USD'] is None
    quoted = study.quote_scope(result)
    assert quoted['status'] == 'draft-not-submitted'
    assert quoted['monetary_totals'] is None and quoted['cheapest_railway'] is None
    assert quoted['live_business_records_created'] is False
    assert all(row['required_reviewed_prices'] is None and row['purchase_or_RFQ_submitted'] is False
               for row in quoted['wheel_options'] + quoted['sparse_options'])
    for row in result['wheel_cases']:
        if 'dependent_load_requests' in row:
            assert row['dependent_load_requests']['physical_option_id'] == row['physical_option_id']
            assert row['dependent_load_requests']['existing_body_brake_civil_results_reusable'] is False


def test_vehicle_cycle_is_not_station_headway(result):
    row = next(row for row in result['wheel_cases'] if 'service' in row)
    assert row['service']['conditional_vehicle_cycle_s'] == pytest.approx(row['target_profile']['runtime_s'] + 35)
    assert row['service']['conditional_vehicle_cycle_s'] != row['service']['headway_target_s']


def test_generated_geometry_plot_is_independent_of_prior_plot_style(result):
    import matplotlib
    expected = study.overlap_figure(result)
    with matplotlib.rc_context({'font.size': 19, 'axes.facecolor': '#eee'}):
        assert study.overlap_figure(result) == expected


def test_compressed_publication_rejects_self_consistent_forged_acceptance(tmp_path, result, monkeypatch):
    monkeypatch.setattr(study, 'compare', lambda root: deepcopy(result))
    monkeypatch.setattr(study, 'retain', lambda root, value: Path(root) / 'synthetic-retained-run')
    study.publish(tmp_path)
    assert study.verify(tmp_path)['verified']
    folder = tmp_path / study.OUTPUT
    wrong = deepcopy(result)
    wrong['physical_accepted'] = True
    (folder / 'comparison.json.gz').write_bytes(gzip.compress(study.encoded(wrong), mtime=0))
    manifest = json.loads((folder / 'manifest.json').read_bytes())
    manifest['files_sha256']['comparison.json.gz'] = study.digest(folder / 'comparison.json.gz')
    manifest['manifest_id'] = study.identity({k:v for k,v in manifest.items() if k != 'manifest_id'})
    (folder / 'manifest.json').write_bytes(study.encoded(manifest))
    with pytest.raises(ValueError, match='differs'):
        study.verify(tmp_path)


def test_configuration_cannot_drop_the_user_seeds(tmp_path):
    source = (study.ROOT / study.SPEC).read_text().replace('powered_bogies = [2, 4, 6, 8, 10, 12]', 'powered_bogies = [4, 6]')
    target = tmp_path / study.SPEC
    target.parent.mkdir(parents=True)
    target.write_text(source)
    with pytest.raises(ValueError, match='seeds'):
        study.specification(tmp_path)


def test_immutable_record_retains_source_bytes_and_rejects_later_edits(tmp_path):
    source = tmp_path / 'input.txt'
    source.write_bytes(b'bound source input\n')
    value = dict(source_sha256={'input.txt': study.digest(source)}, execution='interrupted-budget', **study.FLAGS)
    value['study_id'] = study.identity(value)
    target = study.retain(tmp_path, value)
    assert gzip.decompress((target / 'result.json.gz').read_bytes()) == study.encoded(value)
    assert study.retain(tmp_path, value) == target
    source.write_bytes(b'changed input\n')
    with pytest.raises(ValueError, match='changed'):
        study.retain(tmp_path, value)


def test_retained_identity_and_non_promoting_state_are_checked(tmp_path):
    value = dict(source_sha256={}, execution='interrupted-budget', **study.FLAGS)
    value['physical_accepted'] = True
    value['study_id'] = study.identity(value)
    with pytest.raises(ValueError, match='disposition'):
        study.retain(tmp_path, value)


def test_budget_interruption_preserves_pending_work_and_does_not_publish(tmp_path, monkeypatch):
    ticks = iter([0., 0., 121.])
    monkeypatch.setattr(study.time, 'monotonic', lambda: next(ticks))
    value = study.compare()
    assert value['execution'] == 'interrupted-budget'
    assert len(value['wheel_cases']) == 1
    assert len(value['pending_wheel_requests']) == 143
    assert len(value['pending_sparse_requests']) == 12
    monkeypatch.setattr(study, 'compare', lambda root: value)
    retained = []
    monkeypatch.setattr(study, 'retain', lambda root, value: retained.append(value) or Path(root) / 'retained')
    assert study.publish(tmp_path)['published'] is False
    assert retained == [value]
    assert not (tmp_path / study.OUTPUT).exists()
