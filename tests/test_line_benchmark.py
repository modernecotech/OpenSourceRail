"""Independent budget arithmetic and refusal controls; no native dispatch."""
from copy import deepcopy
from decimal import Decimal
import json
from math import ceil, fsum

import pytest

from engineering.design_search import line_benchmark as benchmark
from engineering.station_rail.common import digest, encoded, identity


@pytest.fixture(scope='module')
def budget():
    return benchmark.evaluate()


def baseline(value):
    return next(v for v in value['variants'] if v['mechanism'] == value['baseline_mechanism'])


def reseal(value, key='evaluation_id'):
    value.pop(key, None)
    value[key] = identity(value)


def test_route_track_fleet_and_launch_counts_are_independent(budget):
    r = budget['specification']['requirements']
    value = baseline(budget)
    s = value['service']
    assert s['active_trainsets'] == ceil(s['round_trip_s'] / r['headway_s'])
    assert s['spare_trainsets'] == ceil(s['active_trainsets'] * .15)
    assert s['total_trainsets'] == s['active_trainsets'] + s['spare_trainsets']
    assert s['totalcars'] == s['total_trainsets'] * 6
    assert s['departure_sites'] == 2 * (12-1) == 22
    assert s['boarding_edges'] == 24
    assert budget['civil']['quantities']['track_m'] == 60000
    assert budget['civil']['quantities']['span_count'] == 3000
    assert budget['civil']['quantities']['independent_supports'] == 3002
    assert s['capacity_pphpd'] == 276 * 3600 / 120 == 8280


def test_reference_vehicle_is_costed_once_for_the_purchased_fleet(budget):
    value = baseline(budget)
    row = next(v for v in value['capital_lines'] if v['key'] == 'delivered-and-assembled-fleet')
    trains = value['service']['total_trainsets']
    assert row['quantity']['trainsets'] == trains and row['quantity']['cars'] == trains * 6
    source = json.loads((benchmark.ROOT / benchmark.VEHICLE_COST).read_bytes())
    assert row['costs_iqd']['base'] == pytest.approx(trains * source['total_vehicle_factory_delivery_assembly_iqd_per_train']['base'], abs=.02)
    assert sum(v['key'] == 'delivered-and-assembled-fleet' for v in value['capital_lines']) == 1
    assert budget['selected_reference_vehicle_candidate_id'] == source['candidate_id']
    assert value['service']['added_vehicle_mass_reserve_kg_per_car'] == 250
    assert budget['civil']['quantities']['added_mass_kg_per_car'] == 250


def test_cost_sensitivity_keeps_the_same_account_mass_and_factory_hours(budget):
    value = baseline(budget)
    fleet = value['service']['total_trainsets']
    row = next(v for v in value['capital_lines'] if v['key'] == 'delivered-and-assembled-fleet')
    factory = next(v for v in value['capital_lines'] if v['scope'] == 'factory-tooling')
    source = json.loads((benchmark.ROOT / benchmark.VEHICLE_COST).read_bytes())
    for i, case in enumerate(benchmark.CASES):
        factor = source['mass_reserve_sensitivity']['case_factors'][case]
        expected = source['total_vehicle_factory_delivery_assembly_iqd_per_train'][case]
        expected += fsum(v['cost_iqd'][case] * (1/factor-1) for v in source['lines'] if v['line_key'].startswith('unlocated-account/'))
        assert row['quantity']['per_train_iqd'][case] == pytest.approx(expected, abs=.02)
        hours = 0.
        for unit in source['lines']:
            q = unit['quantity']
            if 'process_hours_per_train' in q:
                hours += q['process_hours_per_train'][i] / factor
            elif 'process_hours_per_car' in q:
                hours += q['process_hours_per_car'][i] * 6
            elif 'labour_hours_per_car' in q:
                hours += q['labour_hours_per_car'][i] * q['cars']
        assert factory['quantity']['fleet_process_hours'][i] == pytest.approx(hours * fleet, abs=1e-5)


@pytest.mark.parametrize('mechanism', benchmark.MODES)
def test_decimal_ledger_and_currency_closure(budget, mechanism):
    value = next(v for v in budget['variants'] if v['mechanism'] == mechanism)
    fx = Decimal(str(budget['specification']['currency']['iqd_per_usd']))
    route = Decimal('30')
    for case in benchmark.CASES:
        initial = sum(Decimal(str(v['costs_iqd'][case])) for v in value['capital_lines'])
        lifetime = initial + sum(Decimal(str(v['costs_iqd'][case])) for v in value['lifecycle_lines'])
        assert initial == Decimal(str(value['installed_capital_iqd'][case]))
        assert lifetime == Decimal(str(value['whole_life_npv_iqd'][case]))
        assert value['installed_capital_usd'][case] == pytest.approx(float(initial/fx), rel=1e-12)
        assert value['price_per_route_km_usd'][case] == pytest.approx(float(initial/fx/route), rel=1e-12)
        assert value['price_per_track_km_usd'][case] * 2 == pytest.approx(value['price_per_route_km_usd'][case])
        for scope, totals in value['scope_totals_iqd'].items():
            actual = sum(Decimal(str(v['costs_iqd'][case])) for v in [*value['capital_lines'], *value['lifecycle_lines']] if v['scope'] == scope)
            assert actual == Decimal(str(totals[case]))
    assert value['installed_capital_iqd']['low'] < value['installed_capital_iqd']['base'] < value['installed_capital_iqd']['high']


def test_common_converter_rates_apply_to_all_departure_sites(budget):
    spec = budget['specification']
    fx = spec['currency']['iqd_per_usd']
    for variant in budget['variants']:
        row = next(v for v in variant['capital_lines'] if v['key'] == 'launch-converters')
        for i, case in enumerate(benchmark.CASES):
            capacity = row['quantity']['capacities'][i]
            assert capacity['sites'] == 22
            expected = 22 * capacity['budget_kva_per_site'] * spec['rotary']['converter_usd_per_kva'][i] * fx
            assert row['costs_iqd'][case] == pytest.approx(expected, abs=.01)
        charger = next(v for v in variant['capital_lines'] if v['key'] == 'auxiliary-charging-and-grid-increment')
        assert charger['quantity']['platforms'] == 24
        assert charger['quantity']['required_kw'] == 24 * 6 * 200


def test_workplaces_are_not_complete_vehicle_factories(budget):
    value = baseline(budget)
    row = next(v for v in value['capital_lines'] if v['scope'] == 'factory-tooling')
    q = row['quantity']
    expected = [ceil(h/q['productive_hours_per_workplace']) for h in q['fleet_process_hours']]
    assert q['operator_workplaces_per_shift'] == expected
    assert q['productive_hours_per_workplace'] == 3 * 250 * 2 * 8 * .75 == 9000
    assert q['assembly_bays'][1] == 1
    assert q['precast_moulds'][1] == 20
    assert q['precast_crew_cells'][1] == 3


def test_financing_is_separate_from_installed_and_whole_life_ledgers(budget):
    value = baseline(budget)
    fractions = budget['specification']['capital']['financing_provision_fraction']
    assert not any('financ' in v['key'].lower() for v in value['capital_lines'])
    assert not any('financ' in v['key'].lower() for v in value['lifecycle_lines'])
    for i, case in enumerate(benchmark.CASES):
        assert value['funding_envelope_including_financing_usd'][case] == pytest.approx(value['installed_capital_usd'][case] * (1 + fractions[i]))


def test_services_renewal_age_resets_at_whole_vehicle_replacement(budget):
    value = baseline(budget)
    renewal = next(v for v in value['lifecycle_lines'] if v['scope'] == 'renewals')
    schedule = renewal['quantity']['service_account_age_reset_schedules'][1]
    assert schedule['component_life_years'] == 8
    assert schedule['parent_replacement_years'] == [20]
    assert [v['year'] for v in schedule['events'] if not v.get('covered_by_parent_replacement', False)] == [8, 16, 28]
    assert [v['year'] for v in schedule['age_resets']] == [20]
    assert all(v['year'] < 30 for v in renewal['quantity']['events'])


def test_same_budget_comparison_is_zero_and_never_selects_hardware(budget):
    result = benchmark.compare(budget, budget)
    assert result['base_usd_per_route_km_delta'] == 0
    assert result['physical_selection'] is None
    for key in benchmark.FLAGS:
        assert budget[key] is False
        assert all(v[key] is False for v in budget['variants'])


def test_transport_contract_does_not_make_reference_formation_universal(budget):
    spec = deepcopy(budget['specification'])
    changed = deepcopy(spec)
    changed['requirements'].update(cars_per_train=3, fixed_seats_per_car=88, wheelchair_places_per_car=4)
    changed['design']['acceleration_m_s2'] = 1.2
    assert benchmark.functional_requirements(changed) == benchmark.functional_requirements(spec)
    changed['requirements']['minimum_capacity_pphpd'] = 4000
    assert benchmark.functional_requirements(changed) != benchmark.functional_requirements(spec)


def test_comparison_rejects_an_unauthenticated_price(budget):
    changed = deepcopy(budget)
    baseline(changed)['price_per_route_km_usd']['base'] = 0
    with pytest.raises(ValueError):
        benchmark.compare(changed, budget)


def test_comparison_rejects_fully_resealed_inconsistent_totals(budget):
    changed = deepcopy(budget)
    variant = baseline(changed)
    variant['price_per_route_km_usd']['base'] = 0
    reseal(variant)
    changed['baseline_evaluation_id'] = variant['evaluation_id']
    reseal(changed)
    with pytest.raises(ValueError):
        benchmark.compare(changed, budget)


def test_comparison_derives_functional_requirements_instead_of_trusting_id(budget):
    changed = deepcopy(budget)
    changed['specification']['requirements']['headway_s'] = 600
    reseal(changed)
    with pytest.raises(ValueError):
        benchmark.compare(changed, budget)


def test_comparison_rejects_different_authenticated_requirements(budget):
    changed = deepcopy(budget)
    changed['requirements_id'] = 'f' * 64
    reseal(changed)
    with pytest.raises(ValueError):
        benchmark.compare(changed, budget)


def test_comparison_rejects_a_resealed_different_embedded_service(budget):
    changed = deepcopy(budget)
    # The outer configuration still advertises 120 seconds. All enclosing
    # identities are resealed, so only an actual service/configuration check
    # can reject the mismatch.
    for variant in changed['variants']:
        variant['service']['requirements']['headway_s'] = 600
        reseal(variant['service'])
        reseal(variant)
    changed['baseline_evaluation_id'] = baseline(changed)['evaluation_id']
    reseal(changed)
    with pytest.raises(ValueError):
        benchmark.compare(changed, budget)


def test_comparison_requires_declared_sources_and_selection_binding(budget):
    changed = deepcopy(budget)
    changed['source_sha256'] = {}
    reseal(changed)
    with pytest.raises(ValueError):
        benchmark.compare(changed, budget)
    changed = deepcopy(budget)
    changed['benchmark_selection_id'] = 'e' * 64
    reseal(changed)
    with pytest.raises(ValueError):
        benchmark.compare(changed, budget)


def test_fresh_package_tamper_and_fully_resealed_payload_are_rejected(tmp_path):
    folder = tmp_path / 'budget'
    result = benchmark.run(folder)
    assert benchmark.verify(folder)['evaluation_id'] == result['evaluation_id']
    with pytest.raises(ValueError, match='Fresh'):
        benchmark.run(folder)
    value = json.loads((folder/'result.json').read_bytes())
    value['baseline_price_per_route_km_usd']['base'] = 0
    reseal(value)
    (folder/'result.json').write_bytes(encoded(value))
    manifest = json.loads((folder/'manifest.json').read_bytes())
    manifest['evaluation_id'] = value['evaluation_id']
    manifest['files']['result.json'] = digest(folder/'result.json')
    reseal(manifest, 'manifest_id')
    (folder/'manifest.json').write_bytes(encoded(manifest))
    with pytest.raises(ValueError):
        benchmark.verify(folder)
