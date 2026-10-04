"""Finite supports, complete-train loading and honest installed-price boundaries."""
from copy import deepcopy
import importlib.util
import tomllib
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('viaduct_comparison',ROOT/'tools/automation/baghdad_viaduct_comparison.py')
comparison=importlib.util.module_from_spec(spec);spec.loader.exec_module(comparison)


def test_link_slab_does_not_reduce_bearings_and_finite_end_supports_are_counted():
    simple=comparison.support_layout(1000,25,'simple-span-link-slab')
    structural=comparison.support_layout(1000,25,'structural-continuity')
    assert simple['support_locations']==structural['support_locations']==41
    assert simple['bearings']==320 and structural['bearings']==200
    assert all(r['bearings']==8 for r in simple['supports'][1:-1])
    assert simple['deck_expansion_gaps']==structural['deck_expansion_gaps']==9
    assert simple['internal_connections']==structural['internal_connections']==30
    assert not structural['structural_continuity_accepted']
    assert comparison.support_layout(1000,20,'simple-span-link-slab')['bearings']==400
    with pytest.raises(ValueError,match='closure-span'):comparison.support_layout(999,25,'structural-continuity')
    with pytest.raises(ValueError):comparison.support_layout(float('nan'),25,'structural-continuity')


def test_complete_cost_scope_and_invoice_currencies_reconcile_without_hiding_unknowns():
    rows=[dict(id=key,quantity=1,rate=1300,currency='IQD') for key,_ in comparison.BUCKETS]
    rows += [dict(id=key,quantity=1,rate=2,currency='USD') for key in comparison.SEPARATE_COSTS]
    result=comparison.installed_estimate(rows,1000,1300)
    assert result['installed_total_usd']==len(comparison.BUCKETS)+2*len(comparison.SEPARATE_COSTS)
    assert result['installed_usd_per_completed_double_track_m']==result['installed_total_usd']/1000
    assert not result['construction_release']
    broken=deepcopy(rows);broken[0]['rate']=None
    assert comparison.installed_estimate(broken,1000,1300)['installed_total_usd'] is None
    assert 'land-and-rights' in comparison.installed_estimate(rows[:-6],1000,1300)['unpriced_items']
    with pytest.raises(ValueError,match='Duplicate'):comparison.installed_estimate(rows+[rows[0]],1000,1300)
    broken=deepcopy(rows);broken[0]['rate']=-1
    with pytest.raises(ValueError):comparison.installed_estimate(broken,1000,1300)
    with pytest.raises(ValueError):comparison.installed_estimate(rows,1000,0)


def test_complete_bay_rate_is_limited_by_acceptance_not_fast_beam_lifts():
    stages={s:dict(crews=2,productive_hours_per_crew_week=40,crew_hours_per_complete_bay=8) for s in comparison.STAGES}
    stages['survey-correction-and-acceptance']['crew_hours_per_complete_bay']=40
    result=comparison.production_capacity(stages)
    assert result['complete_double_track_bays_per_week']==2
    stages['foundation']['crew_hours_per_complete_bay']=None
    assert comparison.production_capacity(stages)['complete_double_track_bays_per_week'] is None
    assert not result['resource_loaded_programme_accepted']


def test_bearing_sensitivity_prices_standard_length_once_without_curvature_or_segmental_credit():
    design=dict(civil_segments=[dict(line='L1',**{'class':'elevated'},viaduct_product='OSR-Pi25',
        from_station_m=0,to_station_m=100,elevated_cost_multiplier=10),
        dict(line='L1',**{'class':'elevated'},viaduct_product='OSR-US',from_station_m=100,to_station_m=300)])
    costs={'classes':{'elevated':{'benchmark_usd_per_km':12000000,'drivers':[
        dict(quantity='bearings_per_km',cost_share=.1,current_quantity=200,benchmark_quantity=320)]}}}
    contracts=[dict(bucket='civil',manufacturing_uid=str(i),budget_usd=v,imported_share=.15,
        planned_start_day=i,planned_finish_day=i+10) for i,v in enumerate((2000000,8000000))]
    result=comparison.bearing_index_delta_contracts(contracts,{'0':'L1','1':'L1'},design,costs)
    assert sum(r['budget_usd'] for r in result)==45000
    assert [r['budget_usd'] for r in result]==[9000,36000]
    assert [r['planned_start_day'] for r in result]==[0,1]
    assert all(r['imported_share']==.15 and not r['actual_bearing_origin_and_dates_accepted'] for r in result)


def test_comparison_binds_all_special_segments_and_keeps_penalty_out_of_priced_design():
    result=comparison.build()
    assert result['complete_train']['axles']==24
    assert result['complete_train']['axle_positions_m']==[]
    design=tomllib.loads((comparison.CITY/'design.toml').read_text())
    count=sum(s.get('viaduct_product')=='REALIGN-OR-SPECIAL' for s in design['civil_segments'])
    assert result['special_segment_count']==count
    special=[r for r in result['alignment_segments'] if r['special_priority_rank']]
    assert sorted(r['special_priority_rank'] for r in special)==list(range(1,count+1))
    assert all(not r['radius_proxy_is_surveyed'] for r in special)
    assert any(r['pi20_chord_screen_passed'] is False for r in special)
    assert len(result['packages'])==5
    assert result['standard_rate_allowance_usd']+result['routing_penalty_usd']==pytest.approx(result['original_modelled_elevated_cost_usd'])
    assert not any(r['priced_structural_design'] or r['accepted'] for r in result['alignment_segments'])
    assert result['bearing_index_sensitivity']['delta_usd_per_km']==450000
    assert all(p['estimate']['installed_total_usd'] is None for p in result['packages'])
    assert all(s['actual_deep_element_length_m'] is None for p in result['packages'] for s in p['geometry']['supports'])
    segmental=result['packages'][-1]
    assert segmental['segment_lifts']==800 and segmental['match_cast_internal_joints']==720
    assert segmental['geometry']['bearings'] is None
    assert segmental['transport_width_m'] > 3 and not segmental['primary_shipping_target_met']
    assert segmental['complete_member_mass_kg'] is None
    assert not result['construction_release'] and result['finance_recalculated']
    assert not result['baseline_finance_replaced']
