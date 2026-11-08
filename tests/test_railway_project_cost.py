"""Cost ownership, mapped quantities, and unknown service electricity controls."""
from copy import deepcopy
from math import ceil
from pathlib import Path
import json

import pytest

from engineering.railway_project import bundle,cost
from engineering.station_rail.common import identity
from test_railway_project_bundle import inputs,civil_control
from test_railway_project_station_tracks import controls,generate
from test_railway_project_civil import seal


def context():
    # Deliberately synthetic binding and prices: no native model or hardware
    # performance is represented by this accounting control.
    b,_=inputs()
    b['parent_bundle_id']='a'*64
    b['policy']['evaluation']=dict(unlocated_installation_reserve_kg=dict(low=100.,base=200.,high=300.))
    b['parts']=[dict(id='compact-drive/'+name,quantity_per_train=q,
        direct_cost_each_usd=dict(low=v,base=2*v,high=4*v))
        for name,q,v in [('vendor-motor',24,1000.),('inverter',24,500.),('integration-reserve',6,2000.)]]
    b['direct_parts_process_usd']={c:sum(p['quantity_per_train']*p['direct_cost_each_usd'][c] for p in b['parts']) for c in cost.CASES}
    seal(b)
    a,_=controls()
    s=bundle.stations(b,a,platform_width_m=3.,track_centres_y_m=[-3.,3.],
        nominal_boarding_gap_m=.075,stopping_tolerance_m=2.,boarding_length_m=125.)
    tracks=generate(a,s);c=civil_control(b,a)
    c['physical_definition']['track_centres_y_m']=[-1.6,1.6]
    c['physical_definition']['station_centre_to_centre_route_m']=a['route_m']
    c['candidate_id']=identity(c['physical_definition'])
    c['quantities']=dict(nominal_span_track_m=2*ceil(a['route_m']/20)*20)
    c['cost']=dict(accounts=[dict(owner=k,cost_usd=dict(low=100.,base=200.,high=400.)) for group in cost.GROUPS.values() for k in group])
    seal(c)
    p=bundle.combine(b,a,c,s,station_tracks=tracks)
    service=seal(dict(schema='osr-project-network-service/1',candidate_id=p['candidate_id'],bundle_evaluation_id=p['evaluation_id'],
        route_m=a['route_m'],active_trainsets=4,spare_trainsets=1,total_trainsets=5,headway_s=200.,
        planning_capacity_pphpd=4000.,native_service_complete=False,source_sha256={},**cost.FLAGS))
    brief=json.loads(Path('engineering/station_pair/study.json').read_bytes())
    return p,b,c,s,tracks,service,brief


def evaluate(args,**changes):
    return cost.evaluate(*args,**dict(dict(turnout_units=4,station_peak_input_kw=3000.,
        paid_staff_cases=dict(low=20.,base=30.,high=50.)),**changes))


def test_all_fourteen_scopes_exist_and_unknown_energy_is_never_free():
    args=context();r=evaluate(args)
    assert len(r['full_scope']['required_cost_scopes'])==14
    for method in r['full_scope']['methods']:
        assert method['scope_totals_usd']['energy']['base'] is None
        assert method['whole_life_NPV_usd']['base'] is None
        assert method['known_whole_life_subtotal_usd']['base']>method['installed_capital_usd']['base']
        assert method['capital_conservation_residual_usd']['base']==pytest.approx(0.,abs=1e-7)
    assert r['additional_legacy_drive_charge_usd']==0.
    assert r['zero_is_exact_in_BOM_ownership']
    assert not r['station_widening_and_turnback_detailed']
    assert not r['physical_accepted']


def test_train_price_is_direct_BOM_reserve_final_and_delivery_exactly_once():
    args=context();r=evaluate(args);b=args[1]
    rates=json.loads(Path('engineering/station_pair/cost-policy.json').read_bytes())
    direct=b['direct_parts_process_usd']['base']+200.*25.
    final=2400.*10.+100000.
    assert r['delivered_train_unit_usd']['base']==pytest.approx((direct+final)*1.08)
    delivered=next(x for x in r['core']['accounts'] if x['owner']=='rolling-stock-delivered')
    assert delivered['cost_usd']['base']==pytest.approx(5*(direct+final)*1.08)
    assert r['additional_terminal_and_spread_track_m']==pytest.approx(args[4]['quantities']['total_track_m']-args[2]['quantities']['nominal_span_track_m'])
    assert r['full_scope']['route_km']==pytest.approx(args[5]['route_m']/1000)
    assert r['route_m']!=1500.
    assert rates['powered_axle_drive_unit_usd'][1]>0  # deliberately unused


def test_mixed_revisions_duplicate_owners_and_inconsistent_body_price_refuse():
    args=list(context());args[5]['bundle_evaluation_id']='f'*64;seal(args[5])
    with pytest.raises(ValueError,match='Exact mapped project'):
        evaluate(args)
    args=list(context());args[1]['parts'][0]['direct_cost_each_usd']['base']+=1.;seal(args[1])
    with pytest.raises(ValueError,match='Mixed mass'):
        evaluate(args)
    args=list(context());args[2]['cost']['accounts'].append(deepcopy(args[2]['cost']['accounts'][0]));seal(args[2])
    # An old project cannot inherit a re-sealed civil ledger.
    with pytest.raises(ValueError,match='Mixed mass'):
        evaluate(args)


def test_failed_service_cannot_annualize_a_positive_electricity_estimate():
    args=context()
    energy=seal(dict(schema='osr-project-service-energy/1',candidate_id=args[0]['candidate_id'],
        service_evaluation_id=args[5]['evaluation_id'],annual_grid_kwh=dict(low=1e5,base=2e5,high=3e5),
        scope='active-fleet-and-all-stations-excluding-reserve-and-depot',basis='Synthetic accounting control only',
        source_sha256={},**cost.FLAGS))
    with pytest.raises(ValueError,match='completed native service'):
        evaluate(args,energy=energy)


def test_bound_energy_closes_accounting_only_and_preserves_core_seal():
    args=list(context());args[5]['native_service_complete']=True
    args[5]['native_network_evaluation_id']='e'*64
    args[5]['energy_operating_context']=cost.energy_operating_context(args[6]);seal(args[5])
    energy=seal(dict(schema='osr-project-service-energy/1',candidate_id=args[0]['candidate_id'],
        service_evaluation_id=args[5]['evaluation_id'],native_network_evaluation_id='e'*64,
        annual_grid_kwh=dict(low=1e5,base=2e5,high=3e5),
        scope='active-fleet-and-all-stations-excluding-reserve-and-depot',basis='Synthetic accounting control only',
        energy_operating_context=cost.energy_operating_context(args[6]),
        source_sha256={},**cost.FLAGS))
    r=evaluate(args,energy=energy)
    assert r['core']['evaluation_id']==identity({k:v for k,v in r['core'].items() if k!='evaluation_id'})
    for m in r['full_scope']['methods']:
        assert m['whole_life_NPV_usd']['base']>m['installed_capital_usd']['base']
        assert m['annual_operating']['base']['known_reserve_depot_energy_usd']>0
    assert not r['physical_accepted']
    for key,value in (('operation_hours_day',2.),('operation_days_year',100.),
                      ('hotel_W_per_car_hypothesis',50000.),('hotel_charge_efficiency_hypothesis',.8)):
        changed=deepcopy(args);changed[6][key]=value
        with pytest.raises(ValueError,match='operating context'):
            evaluate(changed,energy=energy)
    changed=deepcopy(args);changed[6]['tariff_usd_kwh']['base']*=2
    repriced=evaluate(changed,energy=energy)
    assert repriced['full_scope']['methods'][0]['annual_operating']['base']['primary_pilot_energy_usd']==pytest.approx(
        2*r['full_scope']['methods'][0]['annual_operating']['base']['primary_pilot_energy_usd'])
