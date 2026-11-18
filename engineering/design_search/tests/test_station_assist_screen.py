import json
from pathlib import Path

from engineering.design_search import station_assist_screen as screen


def test_station_assist_is_source_bound_and_not_selected(monkeypatch):
    value = screen.evaluate()
    packet = screen.ROOT / screen.BASE / 'station-assist.json'
    assert screen.encoded(value) == packet.read_bytes()
    assert value['parent_selected_vehicle_candidate_id'] == screen.SELECTED
    assert value['station_primary_minimum_m'] == 596.5
    assert value['comparison_booster_primary_minimum_m'] == 943
    assert value['selected_reference_changed'] is False
    assert value['baghdad_selected_changed'] is False
    assert value['physical_accepted'] is False
    assert {r['grade_up_fraction'] for r in value['assist_rows']} == {0, .02}
    adverse = next(r for r in value['assist_rows'] if r['grade_up_fraction'] == .02)
    assert adverse['wheel_required_mechanical_kWh_train'] > 11
    assert adverse['wheel_peak_mechanical_kW_train'] > 690
    assert adverse['station_recharge_kW_35s_hypothesis'] > 1600
    assert adverse['hybrid_cap_nominal_two_leg_kWh_hypothesis'] > 22
    assert adverse['optimistic_minimum_driven_axles_if_inherited_mu_applied_to_traction'] == 13
    assert value['added_equipment_mass_sensitivity'][1]['wheel_mechanical_kWh_train'] > value['added_equipment_mass_sensitivity'][0]['wheel_mechanical_kWh_train']
    assert adverse['installed_vehicle_mass_kg'] is None
    ids = [option['research_configuration_id'] for option in adverse['driven_axle_options']]
    assert len(set(ids)) == 4
    assert all(option['selected'] is False for option in adverse['driven_axle_options'])
    assert adverse['driven_axle_options'][0]['optimistic_uniform_load_mu_floor'] > adverse['driven_axle_options'][-1]['optimistic_uniform_load_mu_floor']
    original = Path.read_bytes
    source = screen.ROOT / 'engineering/design_search/station_assist_screen.py'

    def changed_source(path):
        raw = original(path)
        return raw + b'\n' if path == source else raw

    monkeypatch.setattr(Path, 'read_bytes', changed_source)
    revised = screen.evaluate()
    assert revised['source_id'] != value['source_id']
    assert revised['evaluation_id'] != value['evaluation_id']


def test_source_identity_mismatch_is_rejected(monkeypatch):
    original = Path.read_bytes
    source = screen.ROOT / screen.BASE / 'comparison.json'

    def changed_comparison(path):
        raw = original(path)
        if path == source:
            altered = json.loads(raw)
            altered['evaluation_id'] = 'different'
            return screen.encoded(altered)
        return raw

    monkeypatch.setattr(Path, 'read_bytes', changed_comparison)
    try:
        screen.evaluate()
    except ValueError as error:
        assert 'stale or has a different parent' in str(error)
    else:
        raise AssertionError('Stale comparison accepted')
