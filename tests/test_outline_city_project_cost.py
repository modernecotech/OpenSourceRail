from copy import deepcopy
from math import fsum
import pytest
from engineering.outline import coordinator, city_project_cost, city_civil
from engineering.design_search import line_benchmark_service
from engineering.station_rail.common import identity


@pytest.fixture(scope='module')
def context():return coordinator.prepare()


def inputs(context,shape='radial',fallback=False):
    c=dict(input_id='synthetic-city-input',city=dict(slug='fixture',country='XX'),
        lines=[dict(line_id='A',shape=shape,route_m=6000.,stops=[dict(id='a',chainage_m=0.),dict(id='b',chainage_m=3000.),dict(id='c',chainage_m=6000.)])],
        civil_segments=[dict(line_id='A',**{'class':'elevated'},from_m=0.,to_m=6000.)],interchanges=[],source_sha256={})
    r=deepcopy(context['spec']['requirements']);d=deepcopy(context['spec']['design']);r.update(route_km=6.,stations=3,headway_s=200.)
    s=line_benchmark_service.evaluate(r,d,context['vehicle'])
    if shape=='ring':s.update(minimum_turnback_positions_per_end=0,departure_sites=6)
    h=dict(kind='powered-axle-continuous-research',traction_rated_kw_per_car=150.,added_traction_mass_kg_per_car=1000.) if fallback else dict(kind='station-launch-reference')
    return c,[dict(line_id='A',shape=shape,requirements=r,design=d,service=s,propulsion_hypothesis=h)]


def cost(city,rows,context):
    # Explicit independent sealed fixtures; production calls must supply their
    # genuine city/service/configuration receipts without this test helper.
    city['input_id']=identity({k:v for k,v in city.items() if k!='input_id'})
    mapped={z['line_id']:z for z in city['lines']}
    for row in rows:
        cfg=row['propulsion_hypothesis'];cfg.update(city_input_id=city['input_id'],line_id=row['line_id'],reference_vehicle_candidate_id=context['vehicle']['candidate_id'])
        cfg['research_configuration_id']=identity({k:v for k,v in cfg.items() if k!='research_configuration_id'})
        service=row['service'];req=row['requirements'];req['stations']=len(row.get('operational_stops',mapped[row['line_id']]['stops']));req['route_km']=mapped[row['line_id']]['route_m']/1000
        service.update(requirements=deepcopy(req),design=deepcopy(row['design']),reference_vehicle_candidate_id=context['vehicle']['candidate_id'],reference_vehicle_evaluation_id=context['vehicle']['evaluation_id'])
        service['evaluation_id']=identity({k:v for k,v in service.items() if k!='evaluation_id'})
        row['evaluation_id']=identity({k:v for k,v in row.items() if k!='evaluation_id'})
    return city_project_cost.evaluate_city_cost(city,rows,context)


def test_complete_city_all_fourteen_scopes_and_accounting_identity(context):
    c,s=inputs(context);cost(c,s,context);original=deepcopy((c,s));v=city_project_cost.evaluate_city_cost(c,s,context)
    assert (c,s)==original
    assert len(v['scope_totals_usd'])==14
    assert all(z['base']>0 for z in v['scope_totals_usd'].values())
    for case in ('low','base','high'):
        assert v['installed_capital_usd'][case]==pytest.approx(fsum(z['costs_usd'][case] for z in v['capital_lines']))
        assert v['whole_life_npv_usd'][case]==pytest.approx(fsum(z['costs_usd'][case] for z in v['capital_lines']+v['lifecycle_lines']))
        assert v['price_per_route_km_usd'][case]==pytest.approx(v['installed_capital_usd'][case]/6.)
    assert v['evaluation_id']==identity({k:z for k,z in v.items() if k!='evaluation_id'})
    assert all(v[k] is False for k in city_project_cost.FLAGS)
    assert v['assumptions']['local_rates_verified'] is False


def test_reserve_auxiliary_electricity_and_supply_ledger_reconcile(context):
    c,s=inputs(context);v=cost(c,s,context)
    service=s[0]['service'];req=s[0]['requirements'];design=s[0]['design']
    expected=service['spare_trainsets']*6*design['aux_kw_per_car']*context['spec']['lifecycle']['reserve_aux_fraction']*req['operating_hours_per_day']*req['operating_days_per_year']/design['charge_efficiency']
    assert expected>0
    line=next(r for r in v['lifecycle_lines'] if r['key']=='network-electricity')
    for case in ('low','base','high'):
        row=v['energy_ledger']['cases'][case]
        assert row['reserve_vehicle_aux_grid_kwh']==pytest.approx(expected)
        assert row['total_grid_kwh']==pytest.approx(sum(row[k] for k in ('traction_grid_kwh','active_vehicle_aux_grid_kwh','reserve_vehicle_aux_grid_kwh','station_and_depot_kwh')))
        assert row['annual_cost_usd']==pytest.approx(row['total_grid_kwh']*row['electricity_usd_per_kwh'])
        assert line['quantity']['annual_energy'][case]==row
    assert v['energy_ledger']['physical_grid_demand_verified'] is False


def test_city_horizon_discount_and_final_removal_follow_declared_policy(context):
    c,s=inputs(context);cost(c,s,context)
    v=city_project_cost.evaluate_city_cost(c,s,context,policy=dict(accounting_horizon_years=12,real_discount_rate=0.))
    assert v['resources']['accounting_years']==12 and v['resources']['real_discount_rate']==0
    energy=next(r for r in v['lifecycle_lines'] if r['key']=='network-electricity')
    assert energy['quantity']['annuity']==12
    end=next(r for r in v['lifecycle_lines'] if r['key']=='final-removal-disposal')
    assert end['quantity']['year']==12
    assert end['costs_usd']['base']==pytest.approx(v['installed_capital_usd']['base']*context['spec']['lifecycle']['decommission_fraction'][1])
    renewal=next(r for r in v['lifecycle_lines'] if r['scope']=='renewals')
    assert all(r['year']<12 for r in renewal['quantity']['events'])


def test_local_operating_overrides_do_not_discount_imported_capital(context):
    c,s=inputs(context);base=cost(c,s,context)
    profile=dict(basis='Declared local tariff/wage test estimates; not supplier evidence',
        electricity_usd_per_kwh=[.1,.2,.3],operations_loaded_paid_wage_usd_h=[1.,2.,3.])
    v=city_project_cost.evaluate_city_cost(c,s,context,policy=dict(local_costs=profile))
    assert v['capital_lines']==base['capital_lines']
    assert v['local_cost_inputs']['status']=='scoped-operating-estimates'
    assert v['local_cost_inputs']['local_rates_verified'] is False
    assert v['energy_ledger']['cases']['base']['annual_cost_usd']==pytest.approx(v['energy_ledger']['cases']['base']['total_grid_kwh']*.2)
    assert v['source_sha256']['engineering/outline/city-cost-inputs.toml']


@pytest.mark.parametrize('policy',[dict(accounting_horizon_years=0),dict(accounting_horizon_years=True),dict(real_discount_rate=-.1),dict(real_discount_rate=float('nan'))])
def test_invalid_accounting_inputs_are_not_silently_replaced(context,policy):
    c,s=inputs(context);cost(c,s,context)
    with pytest.raises(ValueError,match='accounting horizon'):city_project_cost.evaluate_city_cost(c,s,context,policy=policy)


def test_ring_terminal_quantities_not_copied_from_radial_default(context):
    c,s=inputs(context,'ring');v=cost(c,s,context)
    row=next(z for z in v['capital_lines'] if z['key']=='A/terminal-and-line-controls')
    assert row['quantity']['terminals']==0
    assert v['resources']['ring_lines']==1 and v['resources']['radial_lines']==0


def test_powered_axle_fallback_has_vehicle_mass_drive_and_route_power_budget(context):
    c,s=inputs(context,fallback=True);v=cost(c,s,context)
    a=next(z for z in v['capital_lines'] if z['key']=='A/powered-axle-traction-collector-protection')
    b=next(z for z in v['capital_lines'] if z['key']=='A/continuous-feed-and-substations')
    assert a['quantity']['added_mass_kg_per_car']==1000 and a['costs_usd']['base']>0
    assert b['quantity']['substations']==2 and b['costs_usd']['base']>0
    assert v['assumptions']['powered_axle_research_lines']==['A']
    assert not any(z['key']=='A/launch-converters' for z in v['capital_lines'])


def test_network_factory_once_at_total_committed_fleet_and_shared_station_access(context):
    c,s=inputs(context);line=deepcopy(c['lines'][0]);line['line_id']='B'
    for x in line['stops']:x['id']='B'+x['id']
    c['lines'].append(line);c['civil_segments'].append(dict(line_id='B',**{'class':'elevated'},from_m=0.,to_m=6000.))
    b=deepcopy(s[0]);b['line_id']='B';s.append(b)
    c['interchanges']=[dict(id='X',platforms=['a','Ba'])]
    v=cost(c,s,context)
    assert v['resources']['line_stop_records']==6 and v['resources']['access_sites']==5
    assert sum(z['scope']=='factory-tooling' for z in v['capital_lines'])==1
    row=next(z for z in v['capital_lines'] if z['scope']=='factory-tooling')
    assert row['quantity']['committed_cars']==sum(z['service']['totalcars'] for z in s)
    assert v['resources']['total_trainsets']==2*s[0]['service']['total_trainsets']


def test_mixed_civil_costs_are_positive_without_charging_elevated_deck_at_grade(context):
    c,s=inputs(context);c['civil_segments']=[dict(line_id='A',**{'class':k},from_m=a,to_m=b) for k,a,b in [('at-grade',0,2000),('bridge',2000,4000),('tunnel',4000,6000)]]
    v=cost(c,s,context);rows={z['key']:z for z in v['capital_lines']}
    assert rows['repeat-box-beams']['quantity']['spans']==200
    for key in ('surface-formation-drainage-crossings','bridge-special-foundations-deck-temporary','tunnels-portals-lining-ventilation-egress'):
        assert rows[key]['costs_usd']['base']>0


def test_all_surface_city_has_no_free_required_factory_or_empty_cost_scope(context):
    c,s=inputs(context);c['civil_segments'][0]['class']='at-grade'
    v=cost(c,s,context)
    assert v['civil']['quantities']['span_count']==0
    assert v['civil']['owned_factory_capital_usd']['base']==0
    assert all(z['base']>0 for z in v['scope_totals_usd'].values())


def test_missing_or_mixed_line_service_cannot_inherit_other_city_result(context):
    c,s=inputs(context)
    with pytest.raises(ValueError):city_project_cost.evaluate_city_cost(c,[],context)
    s[0]['city_input_id']='different'
    with pytest.raises(ValueError):cost(c,s,context)


def test_shared_interchange_unknown_platform_rejected(context):
    c,s=inputs(context);c['interchanges']=[dict(id='X',platforms=['a','missing'])]
    with pytest.raises(ValueError):cost(c,s,context)


def test_parallel_berths_and_terminal_positions_add_track_civil_and_drive_quantities(context):
    c,s=inputs(context);s[0]['service'].update(minimum_parallel_berth_resources=2,terminal_additional_positions=6,minimum_turnback_positions_per_end=5)
    v=cost(c,s,context)
    assert v['resources']['additional_berth_edges']==12
    assert v['resources']['boarding_edges']==18
    assert v['civil']['quantities']['additional_station_track_m']==12*220
    assert v['civil']['quantities']['span_count']==600+132
    assert v['civil']['quantities']['rail_m']==24000+2*2640
    power=next(z for z in v['capital_lines'] if z['key']=='A/launch-converters')
    assert power['quantity']['capacities'][1]['sites']==2*s[0]['service']['departure_sites']


def test_operational_stop_repair_prices_one_complex_and_extra_access_and_platform(context):
    c,s=inputs(context);s[0]['operational_stops']=[c['lines'][0]['stops'][0],c['lines'][0]['stops'][2]]
    s[0]['station_repair']=dict(additional_access_walkway_m=100.,additional_shared_platform_length_m=200.,complexes=[dict(operational_stop_id='a',original_stop_ids=['a','b'])])
    c['interchanges']=[dict(id='X',platforms=['b','c'])]
    v=cost(c,s,context)
    assert v['resources']['original_map_stop_records']==3
    assert v['resources']['line_stop_records']==2
    assert v['resources']['access_sites']==1
    assert v['resources']['access_repair_walkway_m']==100
    platforms=next(z for z in v['capital_lines'] if z['key']=='line-platform-structures')
    assert platforms['quantity']['area_m2']==(4*120+200)*4
    repair=next(z for z in v['capital_lines'] if z['key']=='stop-complex-access-repair-and-berth-junctions')
    assert repair['costs_usd']['base']>0


def test_conflicting_service_source_hash_cannot_overwrite_existing_epoch(context):
    c,s=inputs(context);name=next(iter(context['sources']));s[0]['source_sha256']={name:'not-the-source-hash'}
    with pytest.raises(ValueError,match='Mixed city pricing source epochs'):
        cost(c,s,context)


def test_fallback_added_mass_propagates_to_civil_pricing_hypothesis(context):
    c,s=inputs(context,fallback=True);v=cost(c,s,context)
    assert v['assumptions']['civil_added_mass_kg_per_car_hypothesis']==context['spec']['design']['added_vehicle_mass_kg_per_car']+1000.
    assert v['assumptions']['civil_uses_maximum_declared_traction_mass_across_lines'] is True


def test_factory_floor_uses_disjoint_cells_bays_and_throughput_receiving(context):
    c,s=inputs(context);v=cost(c,s,context)
    row=next(z for z in v['capital_lines'] if z['scope']=='factory-tooling');q=row['quantity']
    assert q['disjoint_owned_cell_and_assembly_and_receiving_floor'] is True
    assert q['operator_positions_include_final_assembly'] is True
    supply=v['production_supply'];a=context['spec']['capital']
    for i in range(3):
        expected=(supply['cell_floor_m2'][i]+q['assembly_bays'][i]*a['assembly_bay_area_m2']+q['receiving_staging_m2'][i])*a['factory_storage_area_factor']
        assert q['vehicle_floor_m2'][i]==pytest.approx(expected)
        # Floor is not increased again by all production operator positions.
        duplicated=expected+q['vehicle_operator_positions_per_shift'][i]*a['workspace_area_m2']*a['factory_storage_area_factor']
        assert q['vehicle_floor_m2'][i]<duplicated
    assert q['receiving_buffer_car_kits']>=1


def test_stale_same_line_alignment_or_wrong_reference_vehicle_is_rejected(context):
    c,s=inputs(context);cost(c,s,context)
    other=deepcopy(c);other['alignment_hypothesis']={'kind':'new-path'}
    other['input_id']=identity({k:v for k,v in other.items() if k!='input_id'})
    with pytest.raises(ValueError,match='binding'):
        city_project_cost.evaluate_city_cost(other,s,context)
    bad=deepcopy(s);cfg=bad[0]['propulsion_hypothesis'];cfg['reference_vehicle_candidate_id']='other-vehicle'
    cfg['research_configuration_id']=identity({k:v for k,v in cfg.items() if k!='research_configuration_id'})
    bad[0]['evaluation_id']=identity({k:v for k,v in bad[0].items() if k!='evaluation_id'})
    with pytest.raises(ValueError,match='binding'):
        city_project_cost.evaluate_city_cost(c,bad,context)


@pytest.mark.parametrize('target',['row','service','config'])
def test_each_production_receipt_is_verified(context,target):
    c,s=inputs(context);cost(c,s,context)
    record=s[0] if target=='row' else s[0]['service'] if target=='service' else s[0]['propulsion_hypothesis']
    record['unsealed_change']='must not inherit previous evidence'
    with pytest.raises(ValueError,match='identity'):
        city_project_cost.evaluate_city_cost(c,s,context)


def test_sealed_wrong_station_route_requirements_cannot_reuse_city_prices(context):
    c,s=inputs(context);cost(c,s,context)
    s[0]['requirements']['route_km']=7.;s[0]['service']['requirements']=deepcopy(s[0]['requirements'])
    s[0]['service']['evaluation_id']=identity({k:v for k,v in s[0]['service'].items() if k!='evaluation_id'})
    s[0]['evaluation_id']=identity({k:v for k,v in s[0].items() if k!='evaluation_id'})
    with pytest.raises(ValueError,match='route/station'):
        city_project_cost.evaluate_city_cost(c,s,context)


def test_fleet_renewal_retools_without_rebuying_retained_factory_premises(context):
    c,s=inputs(context);v=cost(c,s,context)
    fleet=next(z for z in v['capital_lines'] if z['key']=='network-delivered-assembled-fleet')
    renew=next(z for z in v['lifecycle_lines'] if z['scope']=='renewals')
    events=[e for e in renew['quantity']['events'] if e.get('line_id')==fleet['line_id'] and e['case']=='base']
    assert events
    setup=v['resources']['vehicle_setup_equipment_tools_usd']['base']*.75
    premises=v['resources']['vehicle_factory_premises_usd']['base'];assert premises>0
    discount=context['spec']['requirements']['real_discount_rate']
    for e in events:
        assert e['production_setup_usd']==pytest.approx(setup)
        assert e['production_premises_usd']==0
        assert e['present_value_usd']==pytest.approx((fleet['costs_usd']['base']+setup)/(1+discount)**e['year'])
        assert e['present_value_usd']<(fleet['costs_usd']['base']+setup+premises)/(1+discount)**e['year']
    assert v['assumptions']['factory_premises_rebuilt_at_fleet_renewal'] is False


@pytest.mark.parametrize('years',[1,5])
def test_short_horizon_keeps_explicit_zero_scheduled_renewals(context,years):
    from engineering.outline.completion import _check_costs
    c,rows=inputs(context);cost(c,rows,context)
    v=city_project_cost.evaluate_city_cost(c,rows,context,policy=dict(accounting_horizon_years=years))
    renewal=next(r for r in v['lifecycle_lines'] if r['scope']=='renewals')
    assert renewal['quantity']['events']==[]
    assert renewal['quantity']['zero_basis']
    assert v['scope_totals_usd']['renewals']['base']==0
    _check_costs(v)


def test_explicit_local_wage_bounds_are_not_transferred_again(context):
    c,rows=inputs(context);cost(c,rows,context)
    profile=dict(basis='Local paid-hour scenario',operations_loaded_paid_wage_usd_h=[1.,1.,1.])
    v=city_project_cost.evaluate_city_cost(c,rows,context,policy=dict(local_costs=profile))
    stat=context['assumptions']['assumptions'];req=rows[0]['requirements']
    sites=v['resources']['access_sites']
    expected=[(stat['controllers_per_shift'][i]+sites*stat['station_staff_per_station_per_shift'][i])*req['operating_hours_per_day']*req['operating_days_per_year']*stat['operations_reliever_multiplier'][i] for i in range(3)]
    assert [v['resources']['annual_operations_usd'][case] for case in ('low','base','high')]==pytest.approx(expected)
