from copy import deepcopy
import ast
import gzip
import json
from math import pi
from pathlib import Path

import pytest

from engineering.city_reports import analysis
from engineering.station_rail.common import identity


def seal(value, key):
    value.pop(key, None)
    value[key] = identity(value)
    return value


@pytest.fixture
def inputs():
    amount=dict(low=10.,base=20.,high=30.)
    capital=[dict(line_id=s,key=s,scope=s,costs_usd=amount,quantity={}) for s in analysis.SCOPES]
    life=[dict(line_id='annual-'+s,key='annual-'+s,scope=s,costs_usd={c:v*2 for c,v in amount.items()},
        quantity=dict(annual_usd=[1.,2.,3.],annuity=20.)) for s in ('energy','operations','maintenance','reliability','recovery')]
    scopes={s:{c:amount[c]+sum(r['costs_usd'][c] for r in life if r['scope']==s) for c in amount} for s in analysis.SCOPES}
    costs=dict(capital_lines=capital,lifecycle_lines=life,scope_totals_usd=scopes,
        installed_capital_usd={c:v*14 for c,v in amount.items()},
        whole_life_npv_usd={c:v*24 for c,v in amount.items()})
    city=dict(slug='fixture',name='Fixture',population_retained_unaccepted=10000)
    ids=dict(city_input_id='city',cost_evaluation_id='cost',outline_evaluation_id='outline',
        service_evaluation_id='service',research_configuration_id='configuration',selected_alignment_id='alignment',
        selection_id='selection',reference_candidate_ids=dict(candidate_id='candidate'),source_result_sha256='result')
    seed=seal(dict(selected_city_input_id='city',source_cost_evaluation_id='cost',source_outline_evaluation_id='outline',
        selected_service_evaluation_id='service',research_configuration_id='configuration',selected_alignment_id='alignment',
        reference_candidate_ids=ids['reference_candidate_ids'],source_result_sha256='result'),'seed_id')
    ids['seed_id']=seed['seed_id']
    req=dict(operating_hours_per_day=10.,operating_days_per_year=100,headway_s=200.,peak_demand_pphpd=100.)
    stops=[dict(id='a',chainage_m=0.),dict(id='b',chainage_m=1000.)]
    line=dict(line_id='line-1',shape='radial',route_m=1000.,requirements=req,original_stops=stops,operational_stops=stops,
        service=dict(active_trainsets=2,spare_trainsets=1,total_trainsets=3,one_way_s=600.,round_trip_s=1400.,boarding_edges=4),
        design=dict(platform_length_m=120.),propulsion_hypothesis=dict(kind='station-launch-reference'),service_evaluation_id='line-service',
        station_complexes=[dict(operational_stop_id=r['id'],coordinates=[0.,0.],chainage_m=r['chainage_m'],
            original_stop_ids=[r['id']],boarding_platform_length_m=120.,maximum_added_walk_m=0.) for r in stops],
        metrics=dict(normal_places_per_train=276,capacity_pphpd=4968.,planning_usable_capacity_pphpd=4180.,
            one_way_s=600.,round_trip_s=1400.,train_km_per_day=360.,annual_train_km=36000.,
            mechanical_traction_kwh_per_day=50.,auxiliary_load_kwh_per_day=20.,auxiliary_grid_kwh_per_day=25.))
    staffing=analysis.DEFAULT_POLICY['staffing']
    sources={staffing[k]:staffing[k+'_sha256'] for k in ('cost_source','city_cost_source')}
    packet=seal(dict(schema='osr-city-atlas/1',city=city,identity=ids,lines=[line],interchanges=[],costs=costs,
        resources=dict(access_sites=2,production_positions_per_shift=[1,2,3]),civil=dict(quantities=dict(independent_supports=0,span_count=0)),
        sources=dict(calculation_sha256=sources),summary=dict(lines=1,route_km=1.),
        assumptions=dict(policy=dict(accounting_horizon_years=2,real_discount_rate=0.)),evidence={},missing_evidence=[],**analysis.FLAGS),'packet_id')
    detail=dict(city=city,input_id='city',city_cost_evaluation_id='cost',evaluation_id='outline',research_configuration_id='configuration',
        selected_alignment_id='alignment',reference_candidate_ids=ids['reference_candidate_ids'],planning_seed=seed,**costs,**analysis.FLAGS)
    return packet,detail


def test_hand_controls_identity_costs_energy_fte_and_no_mutation(inputs):
    original=deepcopy(inputs)
    result=analysis.build(*inputs)
    assert inputs==original
    assert result['analysis_id']==identity({k:v for k,v in result.items() if k!='analysis_id'})
    assert result['costs']['installed_capital_usd']==dict(low=140.,base=280.,high=420.)
    assert result['costs']['whole_life_npv_usd']==dict(low=240.,base=480.,high=720.)
    assert result['costs']['annual_opex_usd']==dict(low=5.,base=10.,high=15.)
    assert result['costs']['reconciliation']['all_fourteen_scopes_reconciled']
    assert result['energy']['mechanical_traction_kwh_per_year']==5000.
    assert result['energy']['physical_total_grid_kwh_per_day'] is None
    ops=next(r for r in result['workforce'] if r['domain']=='operations' and r['case']=='base')
    # Four controls + two staff at each of two access sites, 1000 service hours,
    # and the same 1.25 relief already included in the current operations ledger.
    assert ops['positions_per_shift']==8
    assert ops['paid_person_hours']==10000.
    assert ops['paid_fte_equivalent']==5.
    production=next(r for r in result['workforce'] if r['domain']=='vehicle-production' and r['case']=='base')
    assert production['distinct_two_shift_people']==4
    assert production['productive_capacity_person_hours']==18000
    assert production['productive_person_hours'] is None
    assert result['lines'][0]['scheduled_direction_journeys_per_day']==360.
    assert result['access']['scenarios'][0]['station_circle_area_sum_km2']==pytest.approx(2*pi*.4**2)
    assert result['access']['population_coverage'] is None
    assert all(result[k] is False for k in analysis.FLAGS)
    for records in result['tables'].values():
        assert all(not isinstance(v,(dict,list)) for r in records for v in r.values())


def test_hand_finance_is_explicit_profile_not_capacity_and_does_not_reprice(inputs):
    p=deepcopy(analysis.DEFAULT_POLICY)
    p['finance'].update(time_profile=[dict(fraction_of_service_hours=1.,peak_flow_fraction=.5)],
        reverse_direction_peak_fraction=.5,mean_section_to_peak_section_load_ratio=.5,
        average_trip_fraction_of_line_length=.25,boardings_per_linked_trip=1.5,collection_fraction=.8,
        demand_multipliers=[1.],fares_usd_per_paid_trip=[.25])
    r=analysis.build(*inputs,policy=p)
    # 100 pphpd * 1.5 directions * 10h * .5 time * .5 mean load / .25 trip
    # length *100 days /1.5 transfers *.8 collection =80,000 paid trips/year.
    assert r['finance']['assumed_trips'][0]['assumed_annual_paid_linked_trips']==80000
    row=next(z for z in r['finance']['scenario_rows'] if z['cost_case']=='base')
    assert row['annual_revenue_usd']==20000
    assert row['operating_cost_covering_fare_usd']==10/80000
    assert row['full_life_cost_covering_fare_usd']==480/160000
    assert row['unfinanced_revenue_less_whole_life_cost_npv_usd']==40000-480
    assert r['finance']['not_a_demand_forecast']
    assert r['costs']['installed_capital_usd']==inputs[0]['costs']['installed_capital_usd']
    p['finance']['enabled']=False
    assert analysis.build(*inputs,policy=p)['finance']['scenario_rows']==[]


def test_connectivity_uses_declared_platform_links_and_natural_line_order(inputs):
    packet,detail=deepcopy(inputs)
    line=deepcopy(packet['lines'][0]);line['line_id']='line-10'
    for stop in line['original_stops']:stop['id']='z'+stop['id']
    packet['lines']=[line,*packet['lines']]
    seal(packet,'packet_id')
    assert analysis.build(packet,detail)['network']['connected_line_components']==[['line-1'],['line-10']]
    packet['interchanges']=[dict(id='transfer',lines=['line-1','line-10'],platforms=['a','za'])]
    seal(packet,'packet_id');r=analysis.build(packet,detail)
    assert [l['line_id'] for l in r['lines']]==['line-1','line-10']
    assert r['network']['all_lines_reachable_by_declared_transfers']
    assert r['network']['transfer_access_qualified'] is False
    packet['interchanges'][0]['platforms']=['missing','za'];seal(packet,'packet_id')
    with pytest.raises(ValueError,match='transfer'):
        analysis.build(packet,detail)


@pytest.mark.parametrize('key', ['city_input_id','cost_evaluation_id','outline_evaluation_id','research_configuration_id','selected_alignment_id','reference_candidate_ids','selection_id'])
def test_resealed_cross_candidate_inputs_and_changed_selection_rejected(inputs,key):
    packet,detail=deepcopy(inputs)
    if key=='selection_id':detail[key]='other'
    else:packet['identity'][key]='other'
    seal(packet,'packet_id')
    with pytest.raises(ValueError,match='Mixed'):
        analysis.build(packet,detail)


def test_tampering_cost_release_staffing_and_business_records_rejected(inputs):
    packet,detail=deepcopy(inputs);packet['city']['name']='tampered'
    with pytest.raises(ValueError,match='identity'):analysis.build(packet,detail)
    packet,detail=deepcopy(inputs);packet['physical_accepted']=True;seal(packet,'packet_id')
    with pytest.raises(ValueError,match='false release'):analysis.build(packet,detail)
    packet,detail=deepcopy(inputs);packet['costs']['capital_lines'][0]['costs_usd']['base']=200;seal(packet,'packet_id')
    detail['capital_lines']=deepcopy(packet['costs']['capital_lines'])
    with pytest.raises(ValueError,match='reconcile'):analysis.build(packet,detail)
    packet,detail=deepcopy(inputs);packet['sources']['calculation_sha256'].clear();seal(packet,'packet_id')
    with pytest.raises(ValueError,match='source binding'):analysis.build(packet,detail)


def test_literal_assumptions_match_pinned_producers():
    root=Path(__file__).resolve().parents[1];p=analysis.DEFAULT_POLICY
    from hashlib import sha256
    for section,key in [('staffing','cost_source'),('staffing','city_cost_source'),('delivery','source')]:
        source=root/p[section][key]
        assert sha256(source.read_bytes()).hexdigest()==p[section][key+'_sha256']
    tree=ast.parse((root/p['staffing']['cost_source']).read_text())
    for key in ('controllers_per_shift','station_staff_per_station_per_shift','operations_reliever_multiplier'):
        found=[n.value for n in ast.walk(tree) if isinstance(n,ast.keyword) and n.arg==key]
        assert len(found)==1
        assert ast.literal_eval(found[0])==p['staffing'][key]


def test_current_samawah_authenticated_fixture_sample():
    # Integration runs against the actual publication when available; never copies
    # large city artefacts into test/source worktrees. Manifest authentication is
    # performed by the publication owner, outside the pure analysis function.
    root=Path('/home/hayder/Documents/OpenSourceRail')
    atlas=root/'docs/design-engine/city-atlas/cities/samawah.json.gz'
    detail=root/'docs/design-engine/outline-completion/cities/samawah.json.gz'
    if not atlas.exists() or not detail.exists():pytest.skip('Current source publication not available')
    a=json.loads(gzip.decompress(atlas.read_bytes()));d=json.loads(gzip.decompress(detail.read_bytes()))
    r=analysis.build(a,d)
    assert len(r['lines'])==5
    assert r['network']['all_lines_reachable_by_declared_transfers']
    assert r['costs']['annual_opex_usd']['base']==pytest.approx(48685436.23685808)
    op=next(z for z in r['workforce'] if z['case']=='base' and z['domain']=='operations')
    assert op['paid_fte_equivalent']==pytest.approx((4+17*2)*18*365*1.25/2000)
    assert r['source_ids']['atlas_packet_id']==a['packet_id']


def test_debt_overlay_has_capitalised_grace_level_payment_and_separate_dscr(inputs):
    p=deepcopy(analysis.DEFAULT_POLICY)
    p['finance']['debt']=dict(financed_share=.5,real_interest_rate=.1,term_years=4,grace_years=1,
        grace_convention='Interest capitalised, no payments',debt_draw_timing='Year zero')
    r=analysis.build(*inputs,policy=p)
    row=next(z for z in r['finance']['scenario_rows'] if z['cost_case']=='base')
    assert row['illustrative_financed_principal_usd']==140.
    assert row['illustrative_balance_after_capitalised_grace_usd']==pytest.approx(154.)
    service=154*.1/(1-1.1**-3)
    assert row['illustrative_annual_debt_service_after_grace_usd']==pytest.approx(service)
    assert row['illustrative_post_grace_DSCR']==pytest.approx((row['annual_revenue_usd']-10)/service)
    assert row['unfinanced_revenue_less_whole_life_cost_npv_usd']==pytest.approx(row['annual_revenue_usd']*2-480)
    assert r['finance']['financing']['grace_period_debt_service_usd']==0
    assert r['costs']['whole_life_npv_usd']['base']==480
    p['finance']['debt']['grace_years']=4
    with pytest.raises(ValueError,match='loan share'):analysis.build(*inputs,policy=p)


def test_per_line_energy_propulsion_and_force_requirements_are_csv_ready(inputs):
    packet,detail=deepcopy(inputs)
    source=packet['lines'][0]
    source['metrics'].update(peak_train_force_N=120000.,peak_train_mechanical_power_W=2400000.)
    source['propulsion_hypothesis'].update(research_configuration_id='line-configuration',
        actual_available_force_map=None,collector_protection_and_rescue_required=True,
        independent_friction_braking_required=True)
    source['service'].update(jerk_launch_distance_m=220.,jerk_full_train_fin_launch_envelope_m=316.5,
        independent_braking_qualified=False)
    source['known_reference_failures']=[dict(status='reference-coast-infeasible')]
    seal(packet,'packet_id')
    result=analysis.build(packet,detail);line=result['lines'][0]
    assert result['tables']['lines'][0]==line
    assert line['mechanical_traction_kwh_per_day']==50
    assert line['mechanical_traction_kwh_per_year']==5000
    assert line['auxiliary_load_kwh_per_year']==2000
    assert line['auxiliary_grid_kwh_per_year']==2500
    assert line['electrical_traction_kwh_per_day'] is None
    assert line['physical_total_grid_kwh_per_day'] is None
    assert line['propulsion_research_configuration_id']=='line-configuration'
    assert line['actual_available_force_map_available'] is False
    assert line['required_peak_train_force_N']==120000
    assert line['required_peak_train_mechanical_power_W']==2400000
    assert line['jerk_full_train_fin_launch_envelope_m']==316.5
    assert line['recovery_required'] is True
    assert line['recovery_qualified'] is None
    assert line['independent_braking_qualified'] is False
    assert line['reference_failure_statuses']=='reference-coast-infeasible'
    assert all(not isinstance(v,(dict,list)) for v in line.values())
