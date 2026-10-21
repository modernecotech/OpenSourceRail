"""Independent quantity controls and conservative station structure evidence."""
from hashlib import sha256
import json
import math
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from engineering.ferrite_maglev import station_structure as structure
from engineering.ferrite_maglev import geometry


def test_reference_mass_panels_and_constituents_close_without_equipment_double_count():
    b = structure.body()
    upper, floor = b['panels']
    assert upper['net_area_m2'] == pytest.approx(112.83)
    assert floor['net_area_m2'] == pytest.approx(45.05)
    assert upper['calculated_mass_kg'] == pytest.approx(1297.545)
    assert floor['calculated_mass_kg'] == pytest.approx(700.5275)
    assert b['calculated_equipped_mass_kg'] == pytest.approx(5198.0725)
    assert b['tare_target_kg'] == 14200
    assert b['train_tare_target_kg'] == 85200
    assert b['train_aw3_target_kg'] == 157200
    assert b['passenger_doors_per_car'] == 4
    ledger = b['vehicle_mass_ledger']
    assert len({row['id'] for row in ledger}) == len(ledger)
    assert sum(row['mass_kg'] for row in ledger) == b['tare_target_kg']
    assert len({row['id'] for row in b['interface_ownership']}) == 4
    assert next(row for row in b['interface_ownership'] if row['id'] == 'magnetic-carrier')['excludes'] == 'body-side hardpoint'
    purchase = b['purchasing_quantities']
    assert purchase['illustrative_glass_kg'] + purchase['illustrative_resin_kg'] == pytest.approx(purchase['face_laminate_kg'])
    assert purchase['face_laminate_kg'] + purchase['core_kg'] + purchase['bonding_surface_kg'] == pytest.approx(sum(row['calculated_mass_kg'] for row in b['panels']))
    assert purchase['cutting_waste_fraction'] is None
    assert not b['complete_part_bom'] and not b['mass_measured']


def test_three_identified_targets_and_density_substitution_do_not_inherit_qualification():
    assert structure.body(case='stretch')['tare_target_kg'] == 13400
    assert structure.body(case='conservative')['tare_target_kg'] == 15300
    changes = {row['substitution_density_kg_m3']: row for row in structure.body()['core_density_substitutions']}
    assert changes[110]['added_mass_kg'] == pytest.approx(162.426)
    assert changes[180]['added_mass_kg'] == pytest.approx(667.56)
    assert not any(row['qualification_transferred'] for row in changes.values())
    with pytest.raises(ValueError, match='case'):
        structure.body(case='invented')
    assert structure.body({'vehicle': {'cars_per_train': 3}})['train_aw3_target_kg'] == 78600
    with pytest.raises(ValueError, match='finite positive'):
        structure.body({'vehicle': {'cars_per_train': True}})


@pytest.mark.parametrize('height,ratio', [(0., 1.0279724817414206), (.4, 1.1457516842056144), (.8, 1.489984114774859)])
def test_point_dipole_ring_reference_is_reproduced_without_rail_force_credit(height, ratio):
    benchmark = structure.ring_benchmark(heights=(height,))
    assert benchmark['cases'][0]['optimized_to_classical_field'] == pytest.approx(ratio)
    assert benchmark['railway_force_gain'] is None
    assert not benchmark['automatic_gain_credit']


def test_magnetic_sanity_checks_remain_required_fields_and_linear_candidates_are_inventory_only():
    m = structure.study()['magnetic_screens']
    assert m['equal_static_cartridge_force_n'] == pytest.approx(10709.25)
    assert m['required_ideal_gap_field_t'] == pytest.approx(.23201414138093046)
    assert m['required_ideal_gap_field_with_force_multiplier_t'] == pytest.approx(.2645368222780139)
    assert m['full_payload_force_swing_n'] == pytest.approx(117720)
    assert m['actual_effective_pole_area_m2'] is None
    assert not m['field_map_validated']
    candidates = m['linear_orientation_candidates']['candidates']
    assert len(candidates) == 4
    assert len({row['id'] for row in candidates}) == 4
    for row in candidates:
        assert row['ferrite_mass_kg'] == pytest.approx(125)
        assert row['total_car_allocation_if_repeated_kg'] == pytest.approx(3000)
        assert sum(math.prod(block['size_m']) for block in row['blocks']) == pytest.approx(.025)
        assert all(sum(x*x for x in block['magnetisation_unit_vector']) == pytest.approx(1) for block in row['blocks'])
        assert row['support_force_n'] is None and row['propulsion_force_n'] is None
        assert not row['rail_force_validated']
    assert candidates[0]['distinct_orientation_count'] <= 4
    assert candidates[-1]['needs_return_steel']
    assert candidates[-1]['return_steel_geometry'] is None


@pytest.mark.parametrize('parameters,area,inertia,mass', [
    ({'width': .8, 'depth': 1.6, 'web': .15, 'flange': .18}, .66, .193624, 49995.856),
    ({}, .54, .22005, 43055.856),
    ({'width': .65, 'depth': 1.9, 'web': .1, 'flange': .14}, .506, .21209686666666663, 40588.856),
])
def test_box_section_and_equal_end_infill_mass_controls(parameters, area, inertia, mass):
    c = structure.civil(**parameters)
    assert c['section']['area_m2'] == pytest.approx(area)
    assert c['section']['vertical_inertia_m4'] == pytest.approx(inertia)
    assert c['beam']['concrete_plus_iron_kg'] == pytest.approx(mass)
    assert c['beam']['complete_lift_mass_kg'] is None
    assert c['qualified_foundation_selection'] is None
    assert c['relative_magnetic_gap_error_m'] is None
    assert not c['construction_stage_strength_verified']


def test_civil_gross_stiffness_and_support_sensitivities_are_not_ground_approval():
    c = structure.civil()
    assert c['beam']['concrete_m3'] == pytest.approx(14.22)
    assert c['beam']['end_infill_total_m3'] == pytest.approx(.72)
    assert c['beam']['gross_udl_deflection_m'] == pytest.approx(.024121698932374157)
    assert c['supports']['hollow_column_m3'] == pytest.approx(6.489352325071419)
    assert c['supports']['continuous_supports_per_route_km'] == 40
    assert c['supports']['isolated_supports_for_that_count'] == 41
    assert len(c['foundation_families']) == 3
    assert c['footing_sensitivity']['maximum_pressure_kpa'] < 150
    assert not c['footing_sensitivity']['bearing_criterion_accepted']
    assert c['beam']['concrete_m3_continuous_dual_km'] == pytest.approx(1137.6)
    assert c['supports']['foundation_top_gravity_kn'] > c['supports']['superstructure_shared_gravity_kn']
    with pytest.raises(ValueError, match='void'):
        structure.civil(width=.15)
    with pytest.raises(ValueError, match='finite'):
        structure.civil(span=float('nan'))
    with pytest.raises(ValueError, match='end zones'):
        structure.civil(pier_height=.5)


def test_cost_comparison_matches_document_and_does_not_price_omissions_with_reserve():
    cost = structure.civil_costs()
    assert cost['baseline_listed_scope_usd'] == pytest.approx(4254976.96)
    assert cost['target_listed_scope_usd'] == pytest.approx(3313016.96)
    assert cost['saving_usd'] == pytest.approx(941960)
    assert cost['saving_fraction'] == pytest.approx(.22137840198751313)
    assert cost['support_rate_change_share_of_saving'] > .55
    assert cost['exact_concrete_m3'] < cost['rounded_budget_concrete_m3']
    assert cost['target_from_exact_end_infill_geometry_usd'] < cost['target_listed_scope_usd']
    assert cost['support_price_cases'][-1]['target_listed_scope_usd'] == pytest.approx(3833016.96)
    assert cost['conditional_rail_cases'][1]['target_listed_scope_usd'] == pytest.approx(3072829.568)
    assert not any(row['credited_to_primary'] for row in cost['conditional_rail_cases'])
    assert not any(row['supplier_quote'] for row in cost['rows'])
    assert cost['complete_installed_price_usd'] is None
    assert cost['exclusions'] and not cost['costs_are_supplier_quotes']


def test_production_balances_all_workstreams_and_retains_unexecuted_release_gates():
    p = structure.production()
    assert p['conditional_route_m_per_planned_workday'] == 56.25
    assert p['conditional_beams_per_planned_day'] == 4.5
    assert p['bottlenecks'] == ['erection']
    assert p['capacity_route_m_per_planned_workday']['factory'] == 75
    assert p['capacity_route_m_per_planned_workday']['foundations'] == 75
    assert p['beam_buffer_planned_workdays'] == pytest.approx(24/4.5)
    assert p['beam_buffer_full_available_erection_windows'] == 4
    assert p['elapsed_calendar_days_with_declared_lags'] == pytest.approx(259.9074074074074)
    assert p['accepted_output_demonstrated_m_per_day'] is None
    assert not p['production_release_allowed']
    assert all(not gate['accepted'] for gate in p['strength_and_handover_gates'])
    claimed = structure.production(measured_release_evidence={'qualified_transfer_and_demould_strength': 'passed'})
    assert not claimed['production_release_allowed']
    assert claimed['supplied_evidence_claims_authenticated'] is False


def test_factory_transport_and_zero_delivery_can_become_actual_capacity_bottleneck():
    p = structure.production(mould_positions=8)
    assert p['conditional_route_m_per_planned_workday'] == 37.5
    assert p['bottlenecks'] == ['factory']
    p = structure.production(mould_cycle_elapsed_hours=72)
    assert p['conditional_route_m_per_planned_workday'] == 50
    assert p['bottlenecks'] == ['factory']
    assert structure.production(mould_positions=24, mould_cycle_elapsed_hours=72)['conditional_route_m_per_planned_workday'] == 56.25
    p = structure.production(beam_deliveries_per_planned_day=0)
    assert p['conditional_route_m_per_planned_workday'] == 0
    assert p['steady_workdays'] is None and p['beam_buffer_planned_workdays'] is None
    assert p['bottlenecks'] == ['delivery']
    assert structure.production(availability=.5)['conditional_route_m_per_planned_workday'] == 37.5
    assert structure.production(accepted_beam_buffer=0)['beam_buffer_planned_workdays'] == 0
    with pytest.raises(ValueError, match='exceeds'):
        structure.production(availability=1.01)


def test_native_panel_stock_and_civil_solids_match_quantity_ledger_without_sized_hardpoint_claim():
    d = structure.definition()
    assert len({part['id'] for part in d['parts']}) == len(d['parts'])
    assert set(part['id'] for part in d['parts']) == set(part for stage in d['construction_stages'] for part in stage['parts'])
    densities = d['material_density_assumptions_kg_m3']
    panels = [part for part in d['parts'] if part['id'].startswith('body/')]
    mass = sum(geometry.volume(part)*densities[part['material']] for part in panels)
    assert mass == pytest.approx(sum(row['calculated_mass_kg'] for row in structure.body()['panels']))
    beam = [part for part in d['parts'] if part['id'].startswith('civil/beam-1/')]
    assert sum(geometry.volume(part)*densities[part['material']] for part in beam) == pytest.approx(structure.civil()['beam']['concrete_plus_iron_kg'])
    column = [part for part in d['parts'] if part['id'].startswith('civil/support-1/column')]
    assert sum(geometry.volume(part) for part in column) == pytest.approx(structure.civil()['supports']['hollow_column_m3'])
    cap = [part for part in d['parts'] if part['id'].startswith('civil/support-1/cap')]
    assert sum(geometry.volume(part) for part in cap) == pytest.approx(5.4)
    assert d['unmodelled_body_budget_kg'] == 3200
    assert not d['complete_body_mass_modelled']
    assert d['qualified_foundation_selection'] is None
    assert not any('hardpoint' in part['id'] for part in d['parts'])


def test_published_packet_recomputes_quantities_and_rejects_rehashed_fabricated_acceptance(tmp_path):
    packet = tmp_path/'structure'
    assert structure.publish(packet)['state'] == 'verified-study-records'
    result = json.loads((packet/'result.json').read_text())
    assert all(result[flag] is False for flag in structure.FLAGS)
    result['production']['production_release_allowed'] = True
    data = structure._encoded(result); (packet/'result.json').write_bytes(data)
    manifest = json.loads((packet/'manifest.json').read_text())
    manifest['files_sha256']['result.json'] = sha256(data).hexdigest()
    (packet/'manifest.json').write_bytes(structure._encoded(manifest))
    with pytest.raises(ValueError, match='reproducible'):
        structure.verify(packet)


def test_packet_rejects_stale_sources_unowned_files_and_symlinks(tmp_path):
    packet = tmp_path/'structure'; structure.publish(packet)
    manifest = json.loads((packet/'manifest.json').read_text()); manifest['source_epoch_sha256'] = '0'*64
    (packet/'manifest.json').write_bytes(structure._encoded(manifest))
    with pytest.raises(ValueError, match='stale'):
        structure.verify(packet)
    structure.publish(packet)
    (packet/'foreign').write_text('keep')
    with pytest.raises(ValueError, match='unexpected'):
        structure.publish(packet)
    (packet/'foreign').unlink(); (packet/'result.json').unlink()
    (packet/'result.json').symlink_to(tmp_path/'elsewhere')
    with pytest.raises(ValueError, match='ordinary'):
        structure.verify(packet)
