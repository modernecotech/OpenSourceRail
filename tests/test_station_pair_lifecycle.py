"""Accounting invariants on synthetic cost fixtures; no motion evidence or native calls."""
from copy import deepcopy
import json
from math import fsum
from pathlib import Path

import pytest

from engineering.station_pair import FLAGS, lifecycle
from engineering.station_rail.common import identity


def seal(value, key='evaluation_id'):
    value.pop(key, None)
    value[key] = identity(value)
    return value


@pytest.fixture
def brief():
    return dict(operation_hours_day=18., operation_days_year=365., design_life_years=30,
        discount_rate=.05, hotel_W_per_car_hypothesis=35000.,
        hotel_charge_efficiency_hypothesis=.9,
        tariff_usd_kwh=dict(low=.07,base=.12,high=.2))


@pytest.fixture
def cost():
    accounts = []
    for index,owner in enumerate([*lifecycle.OWNER_SCOPES, 'rolling-stock-delivered']):
        accounts.append(dict(owner=owner,quantity=4 if owner=='rolling-stock-delivered' else 2,
            unit='synthetic accounting units',cost_usd={c:(index+1)*(i+1)*10000. for i,c in enumerate(lifecycle.CASES)},
            basis='Synthetic accounting fixture, not real quantities or prices'))
    direct = {c:fsum(r['cost_usd'][c] for r in accounts) for c in lifecycle.CASES}
    methods = []
    for name,setup in [('purchased-custom-outline',100000.),('local-assembly-factory',300000.)]:
        components = {}; cap = {}
        for i,c in enumerate(lifecycle.CASES):
            start = setup*(i+1); integration = (direct[c]+start)*.2
            contingency = (direct[c]+start+integration)*.25
            components[c] = dict(direct_accounts=direct[c],one_campaign_setup=start,
                integration_verification=integration,contingency=contingency)
            cap[c] = fsum(components[c].values())
        methods.append(dict(method=name,installed_capital_usd=cap,capital_components=components,
            capital_per_route_km_usd={c:cap[c]/1.5 for c in lifecycle.CASES},
            annual_operating={c:dict(energy_usd=100000.*(i+1),maintenance_usd=20000.*(i+1),
                staff_usd=150000.*(i+1)) for i,c in enumerate(lifecycle.CASES)}))
    return seal(dict(schema='osr-station-pair-cost/1',candidate_id='a'*64,body_candidate_id='b'*64,
        body_bundle_id='c'*64,mass_evaluation_id='d'*64,journey_evaluation_id='e'*64,
        service=dict(headway_s=200.,active_trainsets=3,spare_trainsets=1,total_trainsets=4),
        accounts=accounts,methods=methods,**FLAGS))


def extra(cost, **changes):
    row = dict(candidate_id=cost['candidate_id'],owner='station-store-and-linkage',
        scope='stations-power',quantity=2,unit='station modules',
        cost_usd=dict(low=100000.,base=200000.,high=400000.),
        basis='Explicit synthetic module allowance',renewal_class='station-storage')
    row.update(changes)
    return seal(row,'account_id')


def energy(cost, **changes):
    value = dict(schema='osr-station-pair-lifecycle-energy/1',candidate_id=cost['candidate_id'],
        input_cost_evaluation_id=cost['evaluation_id'],source_evaluation_id='f'*64,
        service_fulfilled=True,annual_energy_usd=dict(low=80000.,base=120000.,high=180000.),
        basis='Synthetic cycle accounting fixture; not observed energy or service')
    value.update(changes)
    return seal(value)


def test_fourteen_scopes_are_disjoint_and_capital_reconciles(cost,brief):
    before = deepcopy(cost)
    result = lifecycle.evaluate(cost,brief)
    assert cost == before
    assert result['candidate_id'] == cost['candidate_id']
    assert result['evaluation_id'] == identity({k:v for k,v in result.items() if k!='evaluation_id'})
    assert set(result['required_cost_scopes']) == set(lifecycle.SCOPES)
    for mode in result['methods']:
        original = next(x for x in cost['methods'] if x['method']==mode['method'])
        for c in lifecycle.CASES:
            rows = mode['capital_lines']+mode['lifecycle_lines']
            assert mode['installed_capital_usd'][c] == pytest.approx(fsum(x['costs_usd'][c] for x in mode['capital_lines']))
            assert mode['whole_life_NPV_usd'][c] == pytest.approx(fsum(x['costs_usd'][c] for x in rows))
            assert mode['whole_life_NPV_usd'][c] == pytest.approx(fsum(x[c] for x in mode['scope_totals_usd'].values()))
            assert all(x[c] > 0 for x in mode['scope_totals_usd'].values())
            retained = [x for x in mode['capital_lines'] if x['key'].startswith('original/')]
            assert fsum(x['costs_usd'][c] for x in retained) == pytest.approx(original['installed_capital_usd'][c])
            assert mode['additional_capital_usd'][c] > 0
            assert abs(mode['capital_conservation_residual_usd'][c]) < 1e-8
        assert len({x['key'] for x in mode['capital_lines']}) == len(mode['capital_lines'])
    assert all(result[k] is False for k in FLAGS)


def test_reserve_fleet_partitions_existing_trains_without_charging_again(cost,brief):
    result = lifecycle.evaluate(cost,brief)
    fleet = next(x for x in cost['accounts'] if x['owner']=='rolling-stock-delivered')
    for mode in result['methods']:
        rows = {x['key']:x for x in mode['capital_lines']}
        a = rows['original/rolling-stock-active']; b = rows['original/rolling-stock-reserve']
        assert a['quantity']['trainsets'] == 3 and b['quantity']['trainsets'] == 1
        for c in lifecycle.CASES:
            assert a['costs_usd'][c]+b['costs_usd'][c] == pytest.approx(fleet['cost_usd'][c])
            assert b['costs_usd'][c] == fleet['cost_usd'][c]/4


def test_unknown_electricity_does_not_become_zero_or_complete_npv(cost,brief):
    for m in cost['methods']: m['annual_operating']['base']['energy_usd'] = None
    seal(cost)
    result = lifecycle.evaluate(cost,brief)
    for m in result['methods']:
        assert m['whole_life_NPV_usd']['base'] is None
        assert m['scope_totals_usd']['energy']['base'] is None
        assert m['known_whole_life_subtotal_usd']['base'] > m['installed_capital_usd']['base']
        assert m['annual_operating']['base']['known_reserve_depot_energy_usd'] > 0
        assert m['known_scope_subtotals_usd']['energy']['base'] > 0
        assert fsum(z['base'] for z in m['known_scope_subtotals_usd'].values()) == pytest.approx(m['known_whole_life_subtotal_usd']['base'])
        assert m['incomplete_cases'] == ['base']
        assert m['accounting_scope_complete'] is False
        assert m['whole_life_NPV_usd']['low'] is not None


def test_vehicle_subcomponent_ages_reset_at_full_parent_renewal(cost,brief):
    result = lifecycle.evaluate(cost,brief)
    events = result['methods'][0]['renewal_events']
    battery = [e for e in events if e['owner']=='vehicle/service-batteries' and e['case']=='base']
    parent = [e for e in events if e['owner']=='delivered-whole-fleet' and e['case']=='base']
    assert [e['year'] for e in parent] == [20.]
    assert [e['year'] for e in battery] == [6.,12.,18.,26.]
    assert battery[-1]['component_age_origin_year'] == 20.
    assert all(e['year'] < 30 for e in events)
    assert all('premises' not in e['owner'] or 'excluding-premises' in e['owner'] for e in events)


def test_horizon_replacement_is_not_charged(cost,brief):
    brief['design_life_years'] = 20
    result = lifecycle.evaluate(cost,brief)
    for m in result['methods']:
        assert not any(e['owner']=='delivered-whole-fleet' and e['case']=='base' for e in m['renewal_events'])
        assert all(e['year'] < 20 for e in m['renewal_events'])


def test_new_station_hardware_is_charged_once_and_has_renewal_and_maintenance(cost,brief):
    a = lifecycle.evaluate(cost,brief)
    row = extra(cost)
    b = lifecycle.evaluate(cost,brief,extra_accounts=[row])
    for old,new in zip(a['methods'],b['methods']):
        rows = [x for x in new['capital_lines'] if x['key']=='extra/'+row['owner']]
        assert len(rows) == 1
        assert rows[0]['costs_usd'] == row['cost_usd']
        assert new['installed_capital_usd']['base']-old['installed_capital_usd']['base'] == pytest.approx(200000.*1.2*1.25)
        assert new['annual_operating']['base']['maintenance_usd']-old['annual_operating']['base']['maintenance_usd'] == pytest.approx(8000.)
        events = [e for e in new['renewal_events'] if e['owner']=='extra/'+row['owner'] and e['case']=='base']
        assert [e['year'] for e in events] == [12.,24.]


def test_energy_override_has_exact_context_and_does_not_remove_reserve_depot_demand(cost,brief):
    result = lifecycle.evaluate(cost,brief,energy_context=energy(cost))
    m = result['methods'][0]['annual_operating']['base']
    assert m['primary_pilot_energy_usd'] == 120000.
    assert m['energy_usd'] > 120000.
    assert m['energy_usd'] == m['primary_pilot_energy_usd']+m['known_reserve_depot_energy_usd']
    failed = energy(cost,service_fulfilled=False,annual_energy_usd=dict.fromkeys(lifecycle.CASES))
    result = lifecycle.evaluate(cost,brief,energy_context=failed)
    assert all(m['whole_life_NPV_usd']['base'] is None for m in result['methods'])
    with pytest.raises(ValueError,match='Unfulfilled service'):
        lifecycle.evaluate(cost,brief,energy_context=energy(cost,service_fulfilled=False))


@pytest.mark.parametrize('change',['candidate','cost','unsealed','source'])
def test_rejects_mixed_or_unsealed_energy(cost,brief,change):
    row = energy(cost)
    if change=='candidate': row['candidate_id']='0'*64
    if change=='cost': row['input_cost_evaluation_id']='0'*64
    if change=='source': row['source_evaluation_id']='not-an-evaluation'
    if change=='unsealed': row['annual_energy_usd']['base']+=1
    else: seal(row)
    with pytest.raises(ValueError): lifecycle.evaluate(cost,brief,energy_context=row)


@pytest.mark.parametrize('change',['candidate','owner','duplicate','negative','unsealed','class'])
def test_rejects_extra_account_doublecount_or_wrong_candidate(cost,brief,change):
    row = extra(cost)
    if change=='candidate': row=extra(cost,candidate_id='0'*64)
    if change=='owner': row=extra(cost,owner='wayside-propulsion')
    if change=='negative': row=extra(cost,cost_usd=dict(low=1,base=-1,high=3))
    if change=='class': row=extra(cost,renewal_class='unlimited-life')
    if change=='unsealed': row['quantity']+=1
    with pytest.raises(ValueError):
        lifecycle.evaluate(cost,brief,extra_accounts=[row,row] if change=='duplicate' else [row])


@pytest.mark.parametrize('change',['schema','tamper','duplicate','new-owner','capital','fleet','authority','route'])
def test_rejects_bad_existing_records(cost,brief,change):
    if change=='schema': cost['schema']='different-cost'
    if change=='tamper': cost['accounts'][0]['cost_usd']['base']+=1
    if change=='duplicate': cost['accounts'].append(deepcopy(cost['accounts'][0]))
    if change=='new-owner': cost['accounts'][0]['owner']='unassigned-new-owner'
    if change=='capital': cost['methods'][0]['capital_components']['base']['direct_accounts']+=10
    if change=='fleet': cost['service']['total_trainsets']+=1
    if change=='authority': cost['movement_authority']=True
    if change=='route': cost['methods'][0]['capital_per_route_km_usd']['base']*=2
    if change!='tamper': seal(cost)
    with pytest.raises(ValueError): lifecycle.evaluate(cost,brief)


@pytest.fixture
def policy_root(tmp_path):
    for n in (lifecycle.PRODUCER,lifecycle.POLICY,*lifecycle.DEPENDENCIES):
        dst=tmp_path/n; dst.parent.mkdir(parents=True,exist_ok=True)
        dst.write_bytes((lifecycle.ROOT/n).read_bytes())
    return tmp_path


@pytest.mark.parametrize('change',['negative','nan','short','fraction','partition'])
def test_rejects_invalid_rate_scenarios(cost,brief,policy_root,change):
    path = policy_root/lifecycle.POLICY
    p = json.loads(path.read_bytes())
    if change=='negative': p['land_access_usd_route_m'][1]=-1
    if change=='nan': p['utility_risk_usd_route_m'][1]=float('nan')
    if change=='short': p['rescue_standby_usd_year']=[1,2]
    if change=='fraction': p['disposal_fraction'][1]=1.1
    if change=='partition':
        for v in p['vehicle_components'].values(): v['fraction_of_delivered_fleet'][1]=.5
    path.write_text(json.dumps(p))
    with pytest.raises(ValueError): lifecycle.evaluate(cost,brief,root=policy_root)


def test_project_finance_layers_are_explicit_exclusions(cost,brief):
    result = lifecycle.evaluate(cost,brief)
    assert set(result['project_finance_layers']) == {'financing','taxes','customs','exchange_rate','nonfare_revenue'}
    assert all(isinstance(x,str) and x for x in result['project_finance_layers'].values())
    assert result['transactions_performed'] is False and result['procurement_ready'] is False


def test_policy_change_produces_new_evaluation_not_new_physical_candidate(cost,brief,policy_root):
    a = lifecycle.evaluate(cost,brief,root=policy_root)
    path=policy_root/lifecycle.POLICY; p=json.loads(path.read_bytes())
    p['utility_risk_usd_route_m'][1]*=2; path.write_text(json.dumps(p))
    b = lifecycle.evaluate(cost,brief,root=policy_root)
    assert a['candidate_id']==b['candidate_id']
    assert a['evaluation_id']!=b['evaluation_id']
    assert a['source_sha256'][lifecycle.POLICY]!=b['source_sha256'][lifecycle.POLICY]
    assert b['methods'][0]['installed_capital_usd']['base'] > a['methods'][0]['installed_capital_usd']['base']
