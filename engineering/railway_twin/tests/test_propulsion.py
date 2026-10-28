"""New short-bank hardware is counted without promoting operating evidence."""
from copy import deepcopy
from math import fsum

import pytest

from engineering.design_search import design_grammar, railway_bundle, sparse_launch
from engineering.station_rail.common import identity
from engineering.railway_twin import propulsion


@pytest.fixture(scope='module')
def context():
    plant = propulsion.materialize()
    geometry = sparse_launch.geometry(propulsion.BANK_STARTS_M, 20., initial_nose_m=104.5, launch_distance_m=500.)
    body = design_grammar.build(design_grammar.parameters())
    bundle = railway_bundle.materialize(body, motor_parameters=plant['parameters'])
    case = bundle['architecture_case']
    case['physical_definition']['wayside'].update(sparse_geometry_id=geometry['physical_geometry_id'],
        sparse_contact_evaluation_id=geometry['geometry_result_id'])
    bundle['candidate_id'] = bundle['bundle_id'] = case['candidate_id'] = identity(case['physical_definition'])
    case['case_id'] = identity({k:v for k,v in case.items() if k != 'case_id'})
    bundle['brake_definition']['candidate_id'] = bundle['candidate_id']
    bundle['brake_definition']['brake_definition_id'] = identity({k:v for k,v in bundle['brake_definition'].items() if k != 'brake_definition_id'})
    bundle['definition_id'] = identity({k:v for k,v in bundle.items() if k != 'definition_id'})
    railway_bundle.validate(bundle)
    return bundle, geometry


def test_materialized_twenty_metre_bank_has_balanced_eight_coil_paths():
    plant = propulsion.materialize()
    p, w = plant['parameters']['physical'], plant['winding']
    assert p['primary_length_m'] == 20 and p['periods'] == 40
    assert w['coil_count_both_faces'] == 240 and w['slot_occurrences_both_faces'] == 480
    assert w['branches'] == 30 and w['parallel_paths_per_phase'] == 10
    assert all(b['coils_in_series'] == 8 and b['coils_per_face'] == {'-1':4, '1':4} for b in w['branch_records'])
    assert len({c['coil_id'] for c in w['coils']}) == 240
    slots = [(c['face'], s['slot_index']) for c in w['coils'] for s in c['signed_slots']]
    assert len(set(slots)) == len(slots) == 480
    assert all(s['installation'] == 'wayside' and 'secondary' not in s['id'] for s in plant['wayside_stock'])
    assert not w['actual_connection_verified'] and w['end_turn_geometry'] is None


def test_wire_resistance_and_bare_stock_are_recomputed_from_counted_material():
    plant = propulsion.materialize()
    p, d, w = plant['parameters']['physical'], plant['motor_definition'], plant['winding']
    total_wire = fsum(b['wire_length_m_hypothesis'] for b in w['branch_records'])
    assert total_wire == pytest.approx(240 * 40 * (2 * (.16 + .25) + .05))
    copper = fsum(s['mass_kg'] for s in plant['wayside_stock'] if s['role'] == 'copper-stock')
    assert copper == pytest.approx(total_wire * p['conductor_area_m2'] * 8960)
    assert fsum(s['mass_kg'] for s in plant['wayside_stock']) == pytest.approx(20 * d['bare_primary_stock_kg_per_m'])
    for b in w['branch_records']:
        assert b['resistance_20C_ohm_hypothesis'] == pytest.approx(1.724e-8 * b['wire_length_m_hypothesis'] / 25e-6)
        assert b['leakage_inductance_H'] is None and b['actual_lead_and_terminal_resistance_ohm'] is None


def test_requirements_keep_candidate_stock_duty_and_available_force_separate(context):
    bundle, geometry = context
    result = propulsion.requirements(bundle, geometry)
    assert result['candidate_id'] == bundle['candidate_id'] and result['bundle_definition_id'] == bundle['definition_id']
    assert result['launch_bank_count'] == 5 and result['primary_faces'] == 10
    assert result['primary_bank_extent_m'] == 100 and result['primary_face_extent_m'] == 200
    assert result['coil_count_both_faces_all_banks'] == 1200 and result['branch_count_all_banks'] == 150
    assert result['bare_primary_stock_kg'] == pytest.approx(result['bare_copper_stock_kg'] + result['bare_steel_stock_kg'])
    assert len(result['launch_demands']) == 9
    assert all(site['potential_contact_time_s_required_motion'] > 0 for site in result['sites'])
    assert all(site['actual_current_trace_A'] is None and site['cooling_capacity_W'] is None and site['inverter_channel_count'] is None for site in result['sites'])
    assert result['operating_force_map_id'] is None and not result['force_map_admitted']
    assert not result['native_moving_evaluator_compatible'] and not result['repeated_thermal_duty_verified']
    assert all(result[key] is False for key in propulsion.FLAGS)
    assert result['full_installed_mass_kg'] is None and result['full_installed_cost_USD'] is None
    assert len(result['wayside_stock']) == 5 * len(result['materialization']['wayside_stock'])


def test_mutated_geometry_and_unbound_sparse_installation_are_rejected(context):
    bundle, geometry = context
    bad = deepcopy(geometry)
    bad['available_force_N'] = 100000.
    with pytest.raises(ValueError, match='Exact five-bank'):
        propulsion.requirements(bundle, bad)
    bad = deepcopy(bundle)
    case = bad['architecture_case']
    case['physical_definition']['wayside']['sparse_geometry_id'] = '0' * 64
    bad['candidate_id'] = bad['bundle_id'] = case['candidate_id'] = identity(case['physical_definition'])
    case['case_id'] = identity({k:v for k,v in case.items() if k != 'case_id'})
    bad['brake_definition']['candidate_id'] = bad['candidate_id']
    bad['definition_id'] = identity({k:v for k,v in bad.items() if k != 'definition_id'})
    with pytest.raises(ValueError, match='Installed sparse'):
        propulsion.requirements(bad, geometry)


def test_old_twelve_point_five_motor_cannot_inherit_short_bank_requirements(context):
    _, geometry = context
    body = design_grammar.build(design_grammar.parameters())
    old = railway_bundle.materialize(body)
    with pytest.raises(ValueError, match='Bundle motor differs'):
        propulsion.requirements(old, geometry)


def test_solo_final_bank_demand_is_not_divided_by_all_five_sites(context):
    bundle, geometry = context
    result = propulsion.requirements(bundle, geometry)
    full = next(row['result'] for row in result['launch_demands'] if row['load'] == 'normal' and row['grade_fraction'] == 0)
    last = next(row for row in result['sites'][-1]['required_force_envelopes'] if row['load'] == 'normal' and row['grade_fraction'] == 0)
    assert last['necessary_solo_peak_force_N'] == pytest.approx(full['required_body_drive_or_shaft_effort_N'])
    assert last['available_force_N'] is None
