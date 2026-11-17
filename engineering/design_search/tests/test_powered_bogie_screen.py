import json
from pathlib import Path

from engineering.design_search import powered_bogie_screen as screen


def _case(value, load='normal', distance=2000, grade=.02):
    return next(row for row in value['rows'] if row['load_case']==load
                and row['spacing_m']==distance and row['grade_fraction_uphill']==grade)


def test_published_screen_matches_source_and_keeps_candidates_separate():
    config=json.loads((screen.ROOT/screen.INPUT).read_bytes())
    value=screen.evaluate(config)
    assert screen.encoded(value)==(screen.ROOT/'docs/design-engine/v07-powered-bogie/screen.json').read_bytes()
    assert len({c['research_physical_candidate_id'] for c in value['supply_research_configurations']})==3
    assert value['parent_selected_vehicle_candidate_id']==screen.SELECTED
    assert not value['physical_accepted'] and not value['manufacturing_release']


def test_station_store_and_brake_holds_are_visible():
    value=screen.evaluate(json.loads((screen.ROOT/screen.INPUT).read_bytes()))
    row=_case(value)
    assert row['electrical_motoring_plus_aux_kWh_train_hypothesis']>29
    assert row['battery_only']['station_charge_kW_per_train_hypothesis']>3000
    assert row['battery_only']['peak_discharge_C_per_hour_hypothesis']>20
    assert row['battery_supercapacitor']['supercapacitor_output_kWh_per_leg_hypothesis']>14
    assert row['traction_mu_floor_16_driven_axles_optimistic_uniform_load']>row['traction_mu_floor_24_driven_axles_optimistic_uniform_load']>.05
    assert value['independent_2pct_downhill_stop_necessary_bound']['additional_independent_non_wheel_contact_force_required_N_train']>40000
    assert row['rigid_overhead_dc']['separately_sized_rescue_store_kWh'] is None


def test_crowd_and_added_mass_raise_required_power_without_acceptance():
    value=screen.evaluate(json.loads((screen.ROOT/screen.INPUT).read_bytes()))
    assert _case(value,'160-person-crowd-control')['peak_mechanical_kW_train']>_case(value)['peak_mechanical_kW_train']
    assert value['added_equipment_mass_sensitivity'][1]['peak_mechanical_kW_train']>value['added_equipment_mass_sensitivity'][0]['peak_mechanical_kW_train']
    assert value['added_equipment_mass_sensitivity'][1]['added_traction_equipment_kg_per_car_hypothesis'] >= 2395
    assert all(row['complete_installed_mass_kg_per_car'] is None for row in value['rows'])
