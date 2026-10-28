"""Passive-priority, aligned-bank and installed/fault identity controls."""
from copy import deepcopy
from pathlib import Path
import gzip
import json

import pytest

from engineering.design_search import station_accelerators as study


def test_current_priority_requires_passive_vehicles_and_keeps_services():
    spec = study.specification()
    a = spec['architecture']
    assert a['passive_bogies_only'] is True
    assert a['onboard_powered_axles'] == a['onboard_traction_motors'] == 0
    assert a['onboard_traction_store_allowed'] is False
    assert a['auxiliary_and_essential_power_retained'] is True
    assert a['independent_service_emergency_parking_brakes_retained'] is True
    assert spec['priority']['onboard_drive_studies'] == 'retained-secondary-research-comparisons'


@pytest.mark.parametrize('old,new', [
    ('onboard_powered_axles = 0', 'onboard_powered_axles = 4'),
    ('onboard_traction_store_allowed = false', 'onboard_traction_store_allowed = true'),
    ('independent_service_emergency_parking_brakes_retained = true', 'independent_service_emergency_parking_brakes_retained = false'),
])
def test_priority_rejects_hidden_traction_or_lost_independent_brakes(tmp_path, old, new):
    source = (study.ROOT / study.SPEC).read_text()
    path = tmp_path / study.SPEC
    path.parent.mkdir(parents=True)
    path.write_text(source.replace(old, new))
    with pytest.raises(ValueError):
        study.specification(tmp_path)


@pytest.mark.parametrize('field,value', [('cars', 3), ('body_length_m', 18), ('onboard_traction_motors', 2)])
def test_changed_reference_cannot_inherit_fixed_six_car_geometry(field, value):
    vehicle = deepcopy(study.selection.load()['vehicle'])
    vehicle['physical_definition']['vehicle'][field] = value
    with pytest.raises(ValueError, match='Reference interfaces differ'):
        study._reference_interfaces(vehicle)


def test_changed_motion_cannot_inherit_fixed_reference_reports(tmp_path):
    source = (study.ROOT / study.SPEC).read_text()
    path = tmp_path / study.SPEC
    path.parent.mkdir(parents=True)
    path.write_text(source.replace('speed_m_s = 20.0', 'speed_m_s = 16.0')
                   .replace('launch_command_m = 500.0', 'launch_command_m = 320.0'))
    with pytest.raises(ValueError, match='Fixed reference-motion experiment differs'):
        study.specification(tmp_path)


@pytest.fixture(scope='module')
def result():
    return study.compare()


def lead(result):
    return next(row for row in result['layouts'] if row['name'] == result['lead_research_layout_name'])


def test_aligned_five_preserves_margin_with_one_less_site(result):
    five = lead(result)
    six = next(row for row in result['layouts'] if row['name'] == 'previous-six-20')
    assert five['geometry']['site_count'] == 5
    assert five['geometry']['summed_bank_length_m'] == 100
    assert five['geometry']['geometric_covered_m'] == 500
    assert five['geometry']['min_sum_overlap_m'] == six['geometry']['min_sum_overlap_m'] == 9
    assert five['geometry']['longest_single_fin_min_m'] == six['geometry']['longest_single_fin_min_m'] == 5.75
    assert five['necessary_force_at_one_final_active_site_N'] == pytest.approx(66616.7695, abs=.001)
    assert five['available_force_map_id'] is None


def test_active_layout_has_no_onboard_traction_equipment(result):
    for row in result['layouts']:
        physical = row['physical_definition']
        assert physical['passive_bogies'] == 12
        assert physical['powered_bogies'] == physical['onboard_traction_motors'] == physical['onboard_traction_supercapacitors'] == 0
        assert physical['onboard_traction_battery_kWh'] == 0
        assert row['materialized_candidate_id'] is None
        assert all(row[k] is False for k in study.FLAGS)


def test_failed_site_is_not_removed_from_installed_hardware(result):
    row = lead(result)
    assert len(row['fault_evaluations']) == 5
    for fault in row['fault_evaluations']:
        assert fault['installed_physical_option_id'] == row['physical_option_id']
        assert fault['installed_primary_geometry_id'] == row['geometry']['physical_geometry_id']
        assert fault['installed_primary_extent_m'] == 100
        assert fault['active_contact_diagnostic']['summed_bank_length_m'] == 80
        assert fault['active_subset_is_installed_geometry'] is False
    first = row['fault_evaluations'][0]
    assert first['departure_readiness'] == 'hold'
    assert not first['active_contact_diagnostic']['initial_geometric_overlap']
    middle = row['fault_evaluations'][2]
    assert middle['active_contact_diagnostic']['geometric_uncovered_m'] == 84.25


def test_full_request_grid_is_demand_only(result):
    for row in result['layouts']:
        assert len(row['target_demands']) == (18 if row['name'] == result['lead_research_layout_name'] else 0)
        assert all(demand['result']['available_force'] is None and not demand['result']['physical_journey_completed']
                   for demand in row['target_demands'])
    assert result['physical_selection_id'] is None and result['integrated_selection'] is None
    assert result['requirement_policy']['integrated_suitability'] == 'unknown'


def test_forged_physical_acceptance_cannot_be_rebound(tmp_path, result, monkeypatch):
    monkeypatch.setattr(study, 'compare', lambda root: deepcopy(result))
    monkeypatch.setattr(study.propulsion_layout, 'retain', lambda root, value: Path(root) / 'synthetic-run')
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


def test_interruption_retains_pending_work_without_replacing_publication(tmp_path, result, monkeypatch):
    folder = tmp_path / study.OUTPUT
    folder.mkdir(parents=True)
    published = folder / 'manifest.json'
    published.write_bytes(b'previous complete publication')
    interrupted = deepcopy(result)
    interrupted['execution'] = 'interrupted-budget'
    interrupted['pending_layouts'] = interrupted['specification']['layouts'][3:]
    interrupted['layouts'] = interrupted['layouts'][:3]
    interrupted['study_id'] = study.identity({k:v for k,v in interrupted.items() if k != 'study_id'})
    retained = []
    monkeypatch.setattr(study, 'compare', lambda root: interrupted)
    def retain(root, value):
        retained.append(deepcopy(value))
        return Path(root) / 'synthetic-run'
    monkeypatch.setattr(study.propulsion_layout, 'retain', retain)
    outcome = study.publish(tmp_path)
    assert outcome['published'] is False and outcome['pending_layouts'] == 2
    assert retained[0]['pending_layouts'] == interrupted['pending_layouts']
    assert published.read_bytes() == b'previous complete publication'
    with pytest.raises(ValueError, match='interrupted'):
        study.verify(tmp_path)
    assert len(retained) == 2
