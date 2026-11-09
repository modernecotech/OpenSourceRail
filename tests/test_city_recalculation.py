"""Exact package-07/Samawah adapter checks; no native service or cost solves."""
from copy import deepcopy
from math import ceil, fsum
from pathlib import Path
import gzip
import json

import pytest

from engineering.outline import city_inputs
from engineering.railway_project import city_recalculation as adapter
from engineering.station_rail.common import digest, identity


@pytest.fixture(scope='module')
def context():
    root = Path(adapter.ROOT)
    body = json.loads(gzip.decompress((root/adapter.BODY_FILE).read_bytes()))
    city = city_inputs.load('samawah', root=root)
    policy = json.loads((root/adapter.POLICY).read_bytes())
    return city, body, policy


def evaluate(context, *, city=None, body=None, policy=None):
    c, b, p = context
    city = c if city is None else city
    return adapter.evaluate(city, b if body is None else body, p if policy is None else policy,
        trusted_city_input_id=city['input_id'])


def reseal(v, key='evaluation_id'):
    v[key] = identity({k:x for k,x in v.items() if k != key})
    return v


def test_production_entry_binds_exact_body_and_five_lines_without_editing_evidence(context):
    root = Path(adapter.ROOT)
    paths = [root/adapter.BODY_FILE, root/'cities/catalogue/west-asia/Iraq/Samawah/README.md',
        root/'cities/catalogue/west-asia/Iraq/Samawah/engineering/outline/manifest.json']
    before = {str(p):digest(p) for p in paths}
    r = adapter.from_catalogue()
    assert {str(p):digest(p) for p in paths} == before
    assert adapter.verify(r)
    assert r['body_candidate_id'] == adapter.BODY
    assert r['body_evaluation_id'] == adapter.BODY_EVALUATION
    assert r['candidate_id'] != adapter.BODY
    assert r['candidate_id'] == identity(r['physical_definition'])
    assert [x['line_id'] for x in r['lines']] == context[2]['line_ids']
    assert all(x['body_candidate_id'] == adapter.BODY and x['body_evaluation_id'] == adapter.BODY_EVALUATION for x in r['lines'])
    assert r['historical_outline_reference_ids'] == context[0]['reference_candidate_ids']
    assert r['historical_outline_reference_ids']['body_candidate_id'] != adapter.BODY
    assert r['inherited_vehicle_service_cost_results'] is False


def test_stale_evaluation_or_resealed_different_body_revision_is_refused(context):
    body = dict(context[1]); body['evaluation_id'] = '0'*64
    with pytest.raises(ValueError, match='Evaluation seal'): evaluate(context, body=body)
    body = dict(context[1]); body['selection'] = 'another evaluation'
    reseal(body)
    with pytest.raises(ValueError, match='Exact package-07'): evaluate(context, body=body)
    body = dict(context[1]); body['physical_definition'] = dict(body['physical_definition'], invented_change=True)
    with pytest.raises(ValueError, match='Physical candidate seal'): evaluate(context, body=body)


@pytest.mark.parametrize('mode', ['missing', 'duplicate', 'other-city'])
def test_city_scope_cannot_silently_drop_duplicate_or_substitute_lines(context, mode):
    city = deepcopy(context[0])
    if mode == 'missing': city['lines'].pop()
    elif mode == 'duplicate': city['lines'][-1] = deepcopy(city['lines'][0])
    else: city['city']['slug'] = 'baghdad'
    reseal(city, 'input_id')
    with pytest.raises(ValueError, match='five lines|Samawah'): evaluate(context, city=city)


def test_quantities_recount_each_line_and_shared_city_facilities_once(context):
    r = evaluate(context); city = context[0]; p = context[2]
    expected = {x['line_id']:ceil(x['route_m']/p['reference_span_m']) for x in city['lines']}
    assert r['quantities']['standard_bays_by_line'] == expected
    assert sum(expected.values()) > ceil(fsum(x['route_m'] for x in city['lines'])/p['reference_span_m'])
    assert r['quantities']['standard_beams'] == 2*sum(expected.values())
    assert r['quantities']['standard_shared_bents'] == sum(v+1 for v in expected.values())
    assert r['quantities']['running_rail_m'] == pytest.approx(4*fsum(x['route_m'] for x in city['lines']))
    assert r['quantities']['shared_factory_campaigns'] == 1
    assert r['quantities']['shared_depot_provisions'] == 1
    assert r['quantities']['shared_city_protection_systems'] == 1
    assert r['scalar_pilot_cost_per_km_used'] is False


def test_historical_unit_prices_and_700_place_claim_do_not_feed_new_request(context):
    base = evaluate(context); city = deepcopy(context[0])
    city['retained_installed_usd_per_km'] = 10**15
    for line in city['lines']:
        line['retained_capacity_targets'] = {'normal_places':700}
        line['source_schedule'] = [{'headway_s':1}]
    reseal(city, 'input_id')
    changed = evaluate(context, city=city)
    assert changed['candidate_id'] == base['candidate_id']
    assert changed['scope_accounts'] == base['scope_accounts']
    assert changed['fleet_request_cases'] == base['fleet_request_cases']
    assert all(x['normal_places_per_train'] == 276 for x in changed['lines'])


def test_assumptions_change_evaluation_not_physical_candidate(context):
    base = evaluate(context); p = deepcopy(context[2])
    p['demand_pphpd_cases']['base'] = 3000
    changed = evaluate(context, policy=p)
    assert changed['candidate_id'] == base['candidate_id']
    assert changed['evaluation_id'] != base['evaluation_id']
    assert changed['policy_id'] != base['policy_id']
    assert changed['fleet_request_cases']['base']['total_trainsets'] < base['fleet_request_cases']['base']['total_trainsets']
    assert changed['body_evaluation_id'] == base['body_evaluation_id']


def test_all_fourteen_scopes_preserve_unknown_prices_and_counted_bom_subtotal(context):
    r = evaluate(context)
    assert len(r['scope_accounts']) == 14
    assert {x['scope'] for x in r['scope_accounts']} == set(adapter.SCOPES)
    assert all(x['cost_usd'] == dict.fromkeys(adapter.CASES) and not x['cost_complete'] for x in r['scope_accounts'])
    assert all(v == dict.fromkeys(adapter.CASES) for v in r['scope_totals_usd'].values())
    assert r['whole_life_NPV_usd'] == dict.fromkeys(adapter.CASES)
    energy = next(x for x in r['scope_accounts'] if x['scope'] == 'energy')['quantities']
    assert all(v > 0 for v in energy['conditional_vehicle_auxiliary_grid_kwh_cases'].values())
    assert energy['traction_grid_kwh'] is None
    assert energy['complete_actual_grid_kwh'] is None
    for c in adapter.CASES:
        subtotal = sum(x['known_counted_BOM_process_subtotal_usd'][c] for x in r['scope_accounts']
            if x['known_counted_BOM_process_subtotal_usd'] is not None)
        assert subtotal == pytest.approx(r['known_counted_BOM_process_subtotal_usd'][c])
        assert subtotal > 0
    assert not r['cost_complete'] and not r['service_complete'] and not r['simulation_complete']


def test_mass_unknowns_station_failures_and_shift_gap_are_preserved(context):
    r = evaluate(context)
    assert r['body_mass_uncertainty'] == context[1]['mass_uncertainty']
    assert r['installed_mass_complete'] is False
    assert r['unknown_inputs'] == dict.fromkeys(adapter.UNKNOWN_INPUTS)
    assert r['definition_failures']
    assert any(x['kind'] == 'overlapping-standard-platform-envelope' for x in r['definition_failures'])
    shifts = r['workforce_request']
    assert shifts['production_shifts_per_day'] == shifts['civil_shifts_per_day'] == 2
    assert shifts['minimum_operating_shifts_for_declared_calendar'] == 3
    assert shifts['initial_shift_coverage_complete'] is False
    assert shifts['extended_shift_coverage_possible'] is True
    assert shifts['staff_roster'] is None
    assert all(r[k] is False for k in adapter.FLAGS)


def test_resealed_mixed_scope_or_promoted_service_is_rejected(context):
    r = evaluate(context)
    bad = deepcopy(r); row = bad['scope_accounts'][0]
    row['body_evaluation_id'] = 'f'*64; reseal(row, 'account_id'); reseal(bad)
    with pytest.raises(ValueError, match='Mixed'): adapter.verify(bad)
    bad = deepcopy(r); bad['scope_accounts'].pop(); reseal(bad)
    with pytest.raises(ValueError, match='fourteen'): adapter.verify(bad)
    bad = deepcopy(r); bad['lines'][0]['native_service_complete'] = True; reseal(bad)
    with pytest.raises(ValueError, match='line service'): adapter.verify(bad)
    bad = deepcopy(r); bad['lines'][0]['route_m'] += 100; reseal(bad)
    with pytest.raises(ValueError, match='line quantities'): adapter.verify(bad)
    bad = deepcopy(r); bad['lines'].pop(); reseal(bad)
    with pytest.raises(ValueError, match='five distinct'): adapter.verify(bad)
    bad = deepcopy(r); bad['scope_totals_usd']['energy']['base'] = 0; reseal(bad)
    with pytest.raises(ValueError, match='remain unknown'): adapter.verify(bad)
    bad = deepcopy(r); bad['installed_mass_complete'] = True; reseal(bad)
    with pytest.raises(ValueError, match='Held body'): adapter.verify(bad)


@pytest.mark.parametrize('key,value', [('speed_cap_m_s',0), ('dwell_s',True), ('planning_occupancy',2),
    ('available_force_map',{'invented':'approved'}), ('operating_hours_per_day',25)])
def test_invalid_or_unadmitted_physical_inputs_are_not_defaulted(context, key, value):
    p = deepcopy(context[2]); p[key] = value
    with pytest.raises(ValueError): evaluate(context, policy=p)
