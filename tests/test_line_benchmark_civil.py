from copy import deepcopy

import pytest

from engineering.development_baseline import selection
from engineering.design_search import line_benchmark_civil as civil
from engineering.station_rail.common import identity


@pytest.fixture(scope='module')
def vehicle():
    return selection.load()['vehicle']


def inputs():
    return dict(route_km=30., trackways=2, stations=12), dict(span_m=20., pier_height_m=8.,
        platform_length_m=120., platform_width_m=4., soil_cases_kpa=[300., 200., 100.])


def test_zero_added_mass_matches_independent_civil_cost_review(vehicle):
    r, d = inputs(); result = civil.evaluate(r, d, vehicle)
    assert result['quantities']['span_count'] == 3000
    assert result['quantities']['independent_supports'] == 3002
    assert result['quantities']['fastener_sets'] == 210000
    assert result['quantities']['fastener_hardware_kg'] == 1680000.
    assert result['unit_rates']['base']['rail_factory_iqd_kg'] == pytest.approx(3097.)
    assert result['unit_rates']['base']['complete_8kg_fastener_factory_iqd_set'] == pytest.approx(49217.916666666664)
    assert result['unit_rates']['base']['beam_factory_iqd_span'] == pytest.approx(24136808.322826665)
    assert sum(x['costs_iqd']['base'] for x in result['capital_lines']) == pytest.approx(105261935.4741815*1510)
    assert result['evaluation_id'] == identity({k:v for k,v in result.items() if k != 'evaluation_id'})


def test_added_equipment_changes_loads_without_mutating_reference_or_qualifying_it(vehicle):
    original = deepcopy(vehicle); r, d = inputs()
    before = civil.evaluate(r, d, vehicle)
    d['added_vehicle_mass_kg_per_car'] = 250.
    after = civil.evaluate(r, d, vehicle)
    assert vehicle == original
    assert after['beam']['maximum_live_moment_Nm'] > before['beam']['maximum_live_moment_Nm']
    assert after['evaluation_vehicle_mass_hypothesis']['accounted_160_control_kg_per_car'] == vehicle['mass']['accounted_160_control_kg_per_car']+250.
    assert after['soil_gravity_necessary_bounds'][1]['gravity_closed_area_m2'] > before['soil_gravity_necessary_bounds'][1]['gravity_closed_area_m2']
    assert all(after[k] is False for k in civil.FLAGS)
    assert after['native_solver_jobs'] == 0


def test_track_installation_is_not_charged_once_per_rail_and_complete_sets_include_material(vehicle):
    r, d = inputs(); result = civil.evaluate(r, d, vehicle)
    assert result['quantities']['track_m'] == 60000.
    assert result['quantities']['rail_m'] == 120000.
    line = next(x for x in result['capital_lines'] if x['key'] == 'field_two_rail_track_install')
    assert line['costs_iqd']['base'] == pytest.approx(60000*result['unit_rates']['base']['rail_field_install_iqd_track_m'])
    assert 'not a second beam uplift' in next(x for x in result['capital_lines'] if x['key'] == 'beam_factory')['basis']


def test_walkway_weight_and_reserve_remain_explicit_unqualified_hypotheses(vehicle):
    r, d = inputs(); before = civil.evaluate(r, d, vehicle)
    d.update(include_walkway_gravity=True, load_detail_reserve_fraction=.05, platform_continuity_cost_assumption=False)
    after = civil.evaluate(r, d, vehicle)
    assert after['quantities']['protected_walkway_m'] == 60000.
    assert after['soil_gravity_necessary_bounds'][1]['gravity_closed_area_m2'] > before['soil_gravity_necessary_bounds'][1]['gravity_closed_area_m2']
    assert after['structural_evidence']['walkway_uniform_beam_response_and_eccentric_torsion_qualified'] is False
    reserve = next(x for x in after['capital_lines'] if x['key'] == 'civil_load_detail_reserve')
    beam = next(x for x in after['capital_lines'] if x['key'] == 'beam_factory')
    assert reserve['costs_iqd']['base'] == pytest.approx(.05*beam['costs_iqd']['base'])


@pytest.mark.parametrize('group,key,value', [
    ('requirements','route_km',float('nan')), ('requirements','trackways',1),
    ('requirements','trackways',True), ('requirements','stations',1),
    ('design','span_m',25.), ('design','shared_crossheads',True),
    ('design','added_vehicle_mass_kg_per_car',-1.), ('design','soil_cases_kpa',[200.,200.,200.]),
    ('design','footing_thickness_m',5.), ('design','load_detail_reserve_fraction',2.)])
def test_invalid_or_unmodeled_configuration_is_rejected(vehicle, group, key, value):
    r, d = inputs(); (r if group == 'requirements' else d)[key] = value
    with pytest.raises(ValueError): civil.evaluate(r, d, vehicle)
