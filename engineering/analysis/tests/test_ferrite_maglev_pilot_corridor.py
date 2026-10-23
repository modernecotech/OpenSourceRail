"""Open-map estimates, complete event accounting and finance invariants."""
from copy import deepcopy
import gzip
import json
import math

import pytest
from engineering.ferrite_maglev import pilot_corridor as p


@pytest.fixture(scope='module')
def controlled():return p.controlled_line()


def test_direction_aligned_bodies_save_platform_but_expand_power_zone_union():
    v=p.compact_station();old=v['old_shared_front'];new=v['aligned_body_centres']
    assert old['platform_length_m']==219 and new['platform_length_m']==114.5
    assert old['common_straight_m']==400 and new['common_straight_m']==504.5
    assert new['direction_specific_front_stops_m']=={'1':52.25,'-1':-52.25}
    assert old['opposite_direction_door_pairs']==new['opposite_direction_door_pairs']==144
    assert new['maximum_walk_m']<old['maximum_walk_m']
    assert not v['approach_flare_and_multiline_common_core_fitted'] and not v['selected']


def test_current_policy_and_controlled_mass_are_bound(controlled):
    assert controlled['pilot_configuration']['controlled_aw3_kg']>28800
    assert controlled['launch_loss']['controlled_mass_matches']
    assert controlled['formation']['aw3_mass_kg']==6*controlled['pilot_configuration']['controlled_aw3_kg']
    assert controlled['launch_loss']['configuration_sha256']==controlled['pilot_configuration']['configuration_sha256']


def test_complete_terminal_cycles_keep_resources_battery_and_source_headway(controlled):
    r=p.service(line=controlled);assert r['fleet_active']==8 and r['fleet_total']==10
    assert not r['progressive_180s_adopted'] and not r['actual_rust_whole_line_protocol']
    assert {e['event'] for e in r['events']}==set(range(12))
    assert abs(r['event_energy_balance_kwh'])<1e-8
    for row in r['mainline_segment_departures']:
        assert row['segment'] in (0,1,2)
        assert min(b-a for a,b in zip(row['times_s'],row['times_s'][1:]))>=240-1e-9
    assert all(e['battery_after_kwh']>=e['normal_minimum_kwh'] for e in r['events'])


def test_receiver_charger_withdrawal_and_recovery_are_actual_event_cases(controlled):
    receiver=p.service('receiver-failure',line=controlled)
    charger=p.service('charger-failure',line=controlled)
    withdrawal=p.service('withdrawal',line=controlled)
    assert any(e['receiver_fault_wait'] and e['delay_s']>0 for e in receiver['events'])
    assert any(e['charger_failed'] and e['charge_delivered_kwh']==0 for e in charger['events'])
    assert withdrawal['withdrawals'] and any(e['train']==8 for e in withdrawal['events'])
    assert all(e['at_safe_berth'] for e in withdrawal['withdrawals'])


def test_held_source_berth_blocks_upstream_receiver_until_actual_dispatch(controlled):
    run=p.service('receiver-failure',line=controlled)
    assert run['berth_verification']['verified']
    assert any(r['source_still_occupied'] and r['occupant'] is not None for r in run['blocked_receiver_examples'])
    actions=[dict(action='stage-entry',time_s=0.,train=0,berth='origin'),dict(action='dispatch',time_s=0.,train=0,berth='origin',receiving_berth='middle',leg='approach'),dict(action='arrival',time_s=140.,train=0,berth='middle',leg='approach'),dict(action='stage-entry',time_s=240.,train=1,berth='origin')]
    assert p.verify_berth_replay(actions,1000.)['closing_occupied']==2
    # The first train completed its dwell at200s but is still held at middle.
    actions.append(dict(action='dispatch',time_s=240.,train=1,berth='origin',receiving_berth='middle',leg='approach'))
    with pytest.raises(ValueError,match='occupied receiving'):p.verify_berth_replay(actions,1000.)


def test_post_horizon_dispatch_is_excluded_and_pending_arrival_is_explicit(controlled):
    a=p.load();a['simulation_hours']=.03;v=p.service(line=controlled,a=a)
    assert v['events'] and all(r['start_s']<108 for r in v['events'])
    assert v['pending_arrivals_at_horizon']>0
    assert all(r['time_s']<108 for r in v['berth_events'])


def test_capacity_shortfall_is_unserved_not_free_capacity(controlled):
    r=p.service(line=controlled);od=dict(rows=[dict(origin=0,destination=3,daily_trips=1e7)])
    v=p.passenger_assignment(od,r)
    assert v['unserved_trips']>0
    assert all(s['carried']<=s['capacity']+1e-9 for s in v['segments'])
    assert v['served_trips']+v['unserved_trips']==pytest.approx(1e7*.12*sum(p.load()['peak_demand_factors']))


def test_lift_outage_preserves_queue_and_never_substitutes_stairs():
    od=dict(rows=[dict(origin=0,destination=1,daily_trips=1e5)]);v=p.lift_queues(od)
    rows={r['operating_lifts']:r for r in v['cases'] if r['station']==0 and r['lift_fraction']==1.}
    assert rows[0]['closing_unserved_queue']>rows[1]['closing_unserved_queue']>rows[2]['closing_unserved_queue']>0
    assert rows[0]['closing_unserved_queue']==pytest.approx(1e5*.12*sum(p.load()['peak_demand_factors']))
    for row in rows.values():
        for hour in row['hours']:assert hour['queue_before']+hour['demand']==pytest.approx(hour['served']+hour['queue_after'])
        assert not row['strict_accessible_route_available']


def test_finance_cash_dscr_revenue_and_nonzero_gap_are_arithmetic():
    a=p.load();v=p.finance(1e8,5e6,10000,[dict(month=1,capex_usd=4e7),dict(month=2,capex_usd=6e7)],a=a)
    assert v['debt_principal_usd']==6e7 and sum(r['equity_capex_usd'] for r in v['monthly_construction_cash'])==4e7
    first=v['annual_cases'][0]
    assert first['fare_revenue_usd']==pytest.approx(10000*360*.4*.25*.95)
    assert first['cfads_usd']==pytest.approx(first['fare_revenue_usd']*1.1-5e6-1e6+2e6)
    assert first['dscr']==pytest.approx(first['cfads_usd']/first['debt_service_usd'])
    assert first['annual_funding_gap_usd']>0 and not v['export_credit']['applied_or_approved']
    assert sum(r['principal_usd'] for r in v['annual_repayment'])==pytest.approx(6e7)
    assert v['annual_repayment'][-1]['closing_debt_usd']==pytest.approx(0.,abs=1e-6)
    assert first['fixed_local_fare_20pct_fx_loss_dscr']<first['dscr']
    with pytest.raises(ValueError):p.finance(1e8,5e6,10000,[dict(month=1,capex_usd=1.)])


def test_comparator_is_own_counted_bom_and_equal_passenger_service(controlled):
    value=p.comparison_bom(controlled,10,p.load());rows={r['id']:r for r in value['rows']}
    assert rows['rails']['quantity']==pytest.approx(controlled['operational_route_length_m']*4*60)
    assert rows['bogies']['quantity']==120 and rows['wheelsets']['quantity']==240 and rows['motors']['quantity']==240
    assert value['equal_service']['passengers_per_train']==720 and not value['primary_architecture_changed']


def test_comparison_excludes_only_maglev_terminal_chargers_and_counts_actual_lifts(controlled):
    rows=[dict(id='station-services',cost_usd=2e6),dict(id='terminal-service-cabinets',cost_usd=2e6),dict(id='land-utilities',cost_usd=3e6)]
    value=p.comparison_common_rows(rows)
    assert value['excluded_cost_usd']==2e6 and value['included_cost_usd']==5e6
    assert [r['id'] for r in value['excluded_maglev_only']]==['terminal-service-cabinets']
    q=p.delivery.topology_quantities(controlled);line=dict(controlled,operational_route_length_m=q['requested_route_m']);bom=p.comparison_bom(line,10,p.load(),topology=q)
    assert next(r['quantity'] for r in bom['rows'] if r['id']=='girder-lifts')==1092


def test_fixed_line_transfer_walk_and_new_line_wait_are_not_zero():
    value=p.network_transfers()
    assert value['transfer_links'] and all(r['assumed_floor_walk_m']>=60 and not r['accepted'] for r in value['transfer_links'])
    assert all(r['reachable_stops']>4 for r in value['journeys'])
    assert any(r['two_or_more_transfer_examples'] for r in value['journeys'])
    assert all(e['total_generalised_minutes']>4 and e['transfers']>=2 for r in value['journeys'] for e in r['two_or_more_transfer_examples'])


def test_comparison_energy_integrates_same_actual_service_without_regen(controlled):
    run=p.service(line=controlled);a=p.load();v=p.rail_energy_comparison(controlled,run,a,1.,1e8,65.)
    assert v['annual_grid_kwh']>v['mainline_leg_traction_input_kwh']>0
    assert abs(v['coarse_quadrature_kwh']-v['mainline_leg_traction_input_kwh'])<.01
    assert v['annual_opex_usd']==pytest.approx(65*15000+v['annual_grid_kwh']*.1+2e6)
    assert v['regeneration_credit_kwh']==0 and v['common_actual_departures_and_passengers']


def test_population_is_native_union_and_wheelchair_unknown_not_zero_claim():
    r=p.access()
    for v in r['population']:
        assert sum(v['station_exclusive_population'])==pytest.approx(v['walking_catchment_population'])
        assert v['both_lifts_station2_out_population']<=v['wheeling_sensitivity_population']
        assert v['verified_accessible_population'] is None
    assert r['graph']['verified_accessible_edges']==0 and r['measured_od'] is None
    assert r['destinations'] and all(not x['entrance_or_occupancy_verified'] for x in r['destinations'])


def test_rehashed_pilot_receipt_cannot_adopt_fake_access_or_price(tmp_path,monkeypatch):
    p.publish(tmp_path);v=p.study();e=v['economics'];f=e['finance'];original=p.study;calls=[]
    def counted():calls.append(True);return original()
    monkeypatch.setattr(p,'study',counted);summary=p.read_summary(tmp_path)
    assert len(calls)==1
    assert e['platform_budget']['reference_length_m']==219 and not e['platform_budget']['compact_alternative_selected']
    assert e['platform_budget']['compact_capital_sensitivity_usd']<e['capital_with_reserve_usd']
    assert e['comparison_shared_supports']['shared_scope_hypothesis_only'] and not e['comparison_shared_supports']['structural_equivalence_accepted']
    assert e['maglev_specific_civil']['supports']==302 and e['full_line_construction']['beam_units']==546
    assert e['full_line_construction']['tasks']==len(e['full_line_delivery_plan']['tasks'])
    assert sum(r['id'].endswith('/foundation') for r in e['full_line_delivery_plan']['tasks'])==302
    excluded=e['comparison_common_rows']['excluded_cost_usd'];assert excluded==2e6
    shared=e['shared_factory']['allocated_factory_usd']+e['shared_factory']['allocated_training_usd']+e['comparison_shared_supports']['allowance_usd']
    assert e['comparison_common_scope_usd']==pytest.approx(sum(r['cost_usd'] for r in e['capital_rows_common'])-excluded+shared)
    factory=e['factory_startup_funding'];assert factory['standalone_budget_usd']>factory['pooled_budget_usd'] and not factory['other_programme_factory_funding_committed']
    assert summary['finance']['drawn_debt_usd']==pytest.approx(summary['finance']['total_principal_repaid_usd'])
    assert len(summary['finance']['cases'])==6
    assert sum(r['capex_usd'] for r in f['monthly_construction_cash'])==pytest.approx(e['capital_with_reserve_usd'])
    idle=e['additional_idle_energy'];assert idle['additional_idle_kwh']==max(0,idle['full_year_station_group_idle_kwh']-idle['already_counted_trip_idle_kwh'])
    v['access']['population'][0]['verified_accessible_population']=1e9
    (tmp_path/'study.json.gz').write_bytes(gzip.compress(p.encoded(v),mtime=0));m=json.loads((tmp_path/'manifest.json').read_bytes());m['files_sha256']['study.json.gz']=p.digest(tmp_path/'study.json.gz');(tmp_path/'manifest.json').write_bytes(p.encoded(m))
    with pytest.raises(ValueError,match='recalculation'):p.verify(tmp_path)
