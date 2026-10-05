"""Independent physical quantities, reserve cash, scenario funding and evidence."""
from copy import deepcopy
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import tomllib
import pytest

ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools/automation'))
import baghdad_delivery_closure as closure
OUT=closure.OUT
def read(name):return json.loads((OUT/(name+'.json')).read_text())

def test_tracks_slots_and_rectangular_layouts_reconcile_without_land_credit():
    data=read('depot-layouts');assert len(data['slots'])==data['total_storage_positions']==sum(row['stabling_positions'] for row in data['sites'])
    assert len({r['id'] for r in data['tracks']})==len(data['tracks'])
    assert sum(r['usable_length_m'] for r in data['tracks'])==data['total_storage_positions']*121
    for track in data['tracks']:
        slots=[r for r in data['slots'] if r['track']==track['id']]
        assert len(slots)==track['slots']<=3
        assert max(r['end_chainage_m'] for r in slots)==track['usable_length_m']
        assert track['rail_m']==2*track['usable_length_m']
        assert track['concrete_reference_m3']==pytest.approx(track['usable_length_m']*(2.9*.25+2*.38*.16))
        assert all(r['actual_asset_assignment'] is None and r['charger_circuit'] is None for r in slots)
    for site in data['sites']:
        assert site['planning_yard_rectangle_m2']>=site['yard_area_m2']
        assert site['workshop_rectangle_m2']>=site['workshop_shell_m2']
        assert not site['layout_accepted'] and site['land_title'] is None
        text=(OUT/('depot-'+site['line']+'.svg')).read_text();assert 'NOT a surveyed' in text
    plant=data['slab_factory'];assert plant['capital_allowance_usd'] is None
    assert all(r['cumulative_capacity_margin_panels']>=0 for r in plant['programme'])

def test_sixcar_child_counts_are_inside_parent_cost_and_unknowns_not_zero():
    data=read('six-car-procurement');rows={r['id']:r for r in data['parts']}
    assert rows['M6-C-wheelset']['quantity_per_train']==24 and rows['M6-C-wheel']['quantity_per_train']==48
    assert rows['M6-C-door-cassette']['quantity_per_train']==24 and rows['M6-C-window-cassette']['quantity_per_train']==36
    assert sum(r['cost_allocation_per_consist_usd'] for r in data['parent_allocations'])==1680000
    assert rows['M6-C-hv-isolation']['quantity_per_train'] is None
    assert all(r['unit_price_usd'] is None and not r['qualification_accepted'] for r in rows.values())

def test_site_allocations_and_line_hourly_balances_preserve_annual_duty():
    d=read('site-energy');finance=json.loads((OUT.parent/'finance/summary.json').read_text())
    scenario=tomllib.loads((OUT.parent.parent/'baghdad.toml').read_text())
    expected=finance['operations_basis']['annual_train_km_including_non_revenue']*scenario['consist']['car_count']*finance['operations_basis']['energy_kwh_per_car_km_hot_climate_planning']
    for case in d['cases'].values():
        assert sum(r['allocated_traction_kwh'] for r in case['sites'])==pytest.approx(expected)
        assert sum(r['grid_import_kwh'] for r in case['sites'])==pytest.approx(case['grid_import_kwh'])
        assert all(r['hourly_maximum_energy_residual_kwh']<1e-6 for r in case['sites'])
        assert case['unserved_kwh']==case['firm_purchase_topup_kwh']>0
        assert case['actual_upgrade_capex_usd'] is None
    reference=d['cases']['reference'];total=0
    for path in OUT.glob('energy-line-*-hourly.csv'):
        with path.open() as f:rows=list(csv.DictReader(f))
        assert len(rows)==8760
        total+=sum(float(r['demand_kwh']) for r in rows)
    assert total==pytest.approx(reference['charging_bus_demand_kwh'])

def test_restricted_asset_cash_does_not_double_count_replacements_or_repay_debt():
    with (OUT/'battery-reserve-monthly.csv').open() as f:rows=list(csv.DictReader(f))
    total=0
    for row in rows:
        cash=float(row['opening_restricted_cash_usd'])+float(row['contribution_inside_existing_maintenance_usd'])+float(row['inflation_topup_required_usd'])-float(row['replacement_usd'])
        assert cash==pytest.approx(float(row['closing_restricted_cash_usd'])) and cash>=-.001
        assert row['available_for_early_debt_repayment']=='False'
        total+=float(row['inflation_topup_required_usd'])
    assert total==pytest.approx(read('battery-reserve')['total_topups_usd']) and total>0
    assert not read('maintenance')['additional_payroll_or_reserve_adopted']
    opening=read('opening-battery-reserve')
    assert 0<opening['total_topups_usd']<read('battery-reserve')['total_topups_usd']
    financial=read('finance-opening_fleet_supply_scaled')
    assert sum(r['asset_reserve_topup_usd'] for r in financial['opex_components'])==pytest.approx(opening['total_topups_usd'])

def test_all_maintenance_intervals_and_startup_deficit_keep_evidence_open():
    intervals=read('maintenance-interval-register')
    source=tomllib.loads((ROOT/'lib/templates/maintenance-schedule.toml').read_text())['maintenance_interval']
    assert {r['id'] for r in intervals}=={r['id'] for r in source}
    assert all(r['measured_task_duration_hours'] is None and r['native_asset'] is None and not r['accepted'] for r in intervals)
    station=next(r for r in intervals if r['id']=='station-daily')
    assert station['programme_asset_family_quantity_reference']==len(current_design()['stations'])
    startup=read('startup-policy-alternatives');row=next(r for r in startup['cases'] if r['line']=='line-9')
    assert row['frozen_baseline_dispatch_direction_count']==len(row['frozen_dispatch_points'])
    assert row['revenue_position_deficit']==max(0,row['frozen_baseline_dispatch_direction_count']-row['baseline_revenue_trains'])
    assert row['additional_10_percent_spares']>=math.ceil(row['minimum_additional_revenue_trains']*.1)
    assert row['additional_train_reference_capital_usd']==(row['minimum_additional_revenue_trains']+row['additional_10_percent_spares'])*1680000
    assert row['selected_start_station_ids'] is None and not row['operational_release']

def test_simple_span_bearing_cash_adds_pi25_delta_and_epc_once():
    case=read('finance-simple_span_bearing_index');full=read('finance-reconciled_full_fleet')
    direct=sum(r['budget_usd'] for r in case['bearing_index_delta_contracts'])
    comparison=json.loads((OUT.parent/'viaduct-comparison/comparison.json').read_text())
    assert direct==pytest.approx(comparison['bearing_index_sensitivity']['financed_pi25_only_direct_delta_usd'])
    assert case['metrics']['total_capital_usd']-full['metrics']['total_capital_usd']==pytest.approx(direct*1.07)
    # The gap facility can be capped: additional cash then appears as
    # explicitly uncovered support instead of invented extra credit.
    assert sum(case['metrics'][k] for k in ('terminal_supplemental_balance_iqd','uncovered_support_iqd'))>sum(full['metrics'][k] for k in ('terminal_supplemental_balance_iqd','uncovered_support_iqd'))
    assert all(not r['actual_bearing_origin_and_dates_accepted'] for r in case['bearing_index_delta_contracts'])
    assert case['metrics']['government_capital_share']==pytest.approx(.25)


@pytest.mark.parametrize('name',['reference','reconciled_full_fleet','reconciled_fixed_original_government','reconciled_without_uncommitted_income','opening_fleet_supply_scaled','contracted_solar','installed_energy_supply_bound','simple_span_bearing_index'])
def test_finance_cases_reconcile_native_capital_principal_cash_and_tranches(name):
    case=read('finance-'+name);rows=case['monthly'];totals=defaultdict_float()
    previous={k:0 for k in ('chinese_export_credit','domestic_bonds','bank_credit','green_bonds')}
    for row in rows:
        sources=row['government_usd_cash']+row['chinese_export_credit_draw_native']+(row['government_iqd_cash']+row['domestic_bonds_draw_native']+row['green_bonds_draw_native']+row['bank_credit_draw_native']+row['climate_capital_grant_iqd'])/1300
        assert sources==pytest.approx(row['capex_usd'],abs=.02)
        assert row['government_usd_cash']==pytest.approx(row['chinese_export_credit_draw_native'])
        assert abs(row['cash_balance_residual_usd'])<.01
        for key in previous:
            expected=previous[key]+row[key+'_draw_native']-row[key+'_principal_native']-row[key+'_early_principal_native']
            assert row[key+'_closing_balance_native']==pytest.approx(expected,abs=.01)
            previous[key]=row[key+'_closing_balance_native']
        totals['capex']+=row['capex_usd']
    assert totals['capex']==pytest.approx(case['metrics']['total_capital_usd'])
    for tranche in case['semiannual']:
        assert tranche['end_month']-tranche['start_month']<=5
        assert abs(tranche['capital_reconciliation_usd'])<.01
        assert tranche['indicative_rounded_bond_face_iqd']>=tranche['bond_face_iqd']-.01
    if name!='reconciled_fixed_original_government':assert case['metrics']['government_capital_share']==pytest.approx(.25)
    else:assert case['metrics']['government_capital_usd_equivalent']==pytest.approx(read('finance-reference')['metrics']['government_capital_usd_equivalent'])
    assert not case['operational_release'] and case['physical_energy_upgrade_capex_usd'] is None

def defaultdict_float():
    from collections import defaultdict
    return defaultdict(float)

def test_budget_replacements_preserve_factory_and_original_reference():
    original=json.loads((OUT.parent/'financing-redesign/reference.json').read_text())
    ref=read('finance-reference')
    for key in ('total_capital_usd','terminal_cash_iqd','peak_supplemental_balance_iqd'):
        assert ref['metrics'][key]==pytest.approx(original['metrics'][key],abs=.02)
    scenario=read('finance-reconciled_full_fleet');depots=closure.read(OUT.parent/'delivery-baseline/depot-package.json')
    direct=depots['alternatives']['workload_bays']['gross_reference_cost_usd']-8000000
    assert scenario['metrics']['total_capital_usd']-ref['metrics']['total_capital_usd']==pytest.approx(direct*1.07,abs=.02)
    opening=read('finance-opening_fleet_supply_scaled')
    assert scenario['metrics']['total_capital_usd']-opening['metrics']['total_capital_usd']==pytest.approx((sum(row['trainset_count'] for row in current_design()['fleets'])-read('opening-factory-replay')['selected_trainsets'])*1680000,abs=.02)
    assert opening['deferred_expansion_fleet_funding_usd'] is None
    assert any(r['supply_income_multiplier']<1 for r in opening['opex_components'])

def test_hourly_site_diagnostics_identify_bus_and_charger_limits_without_netting():
    with (OUT/'energy-site-shortage-hours.csv').open() as f:rows=list(csv.DictReader(f))
    sites={r['station']:r for r in read('site-energy')['cases']['reference']['sites']}
    assert rows and all(float(r['unserved_bus_kwh'])>0 or float(r['charger_delivery_shortfall_kwh'])>0 for r in rows)
    for station,site in sites.items():
        assert sum(float(r['unserved_bus_kwh']) for r in rows if r['station']==station)==pytest.approx(site['unserved_kwh'])
        assert site['generation_kwh']==pytest.approx(site['local_generation_kwh']+site['gross_utility_generation_kwh']*.95)
        assert 0<site['installed_service_energy_fraction']<=1+1e-9
    with (OUT/'aggregate-reference-shortage-hours.csv').open() as f:aggregate=list(csv.DictReader(f))
    with (OUT.parent/'delivery-baseline/energy-synthetic_reference-owned_solar-hourly.csv').open() as f:
        expected=[row for row in csv.DictReader(f) if float(row['unserved_kwh'])>1e-7]
    assert len(aggregate)==len(expected)
    bound=read('finance-installed_energy_supply_bound');firm=read('finance-reconciled_full_fleet')
    assert sum(r['fare_receipts_iqd'] for r in bound['monthly'])<sum(r['fare_receipts_iqd'] for r in firm['monthly'])
    assert sum(r['incremental_net_receipts_iqd'] for r in bound['monthly'])<sum(r['incremental_net_receipts_iqd'] for r in firm['monthly'])
    assert not bound['operational_release'] and not bound['shareholder_distributions']['dividend_permission']

def test_development_training_capacity_precedes_operating_cohorts_and_reconciles_cash():
    mobilisation=read('development-training-mobilisation')
    people=json.loads((OUT.parent/'delivery-baseline/workforce.json').read_text())
    first_join=min(r['join_month'] for r in people['recruitment_cohorts'])
    leadership=next(r for r in mobilisation['development_posts'] if r['role_id']=='city-director')
    assert leadership['start_month']==0 and leadership['handover_month']==min(r['authorised_available_month'] for r in people['recruitment_cohorts'])
    assert mobilisation['training_rigs_required_month']<first_join
    assert all(r['qualified_internal_capacity_credited']==0 for r in mobilisation['monthly'])
    assert sum(r['existing_trainer_assessor_cash_iqd'] for r in mobilisation['monthly'])==pytest.approx(people['training_recruitment_cash_iqd']-sum(r['paid_preopening_training_iqd'] for r in people['recruitment_cohorts']))
    assert sum(r['additional_mentor_cash_iqd']+r['additional_development_cash_iqd'] for r in mobilisation['monthly'])==pytest.approx(mobilisation['additional_preopening_cash_iqd'])
    assert {r['role_id'] for r in mobilisation['role_coverage']}=={r['role_id'] for r in people['roles']}
    assert any(r['minimum_external_assessor_posts']>0 for r in mobilisation['monthly'])
    assert any(r['minimum_external_mentor_posts']>0 for r in mobilisation['monthly'])
    assert not mobilisation['named_handover_accepted']

def test_opening_factory_orders_match_fleet_without_earlier_income_or_factory_saving():
    factory=read('opening-factory-replay');tasks=factory['delivery']['tasks']
    stock={r['asset_id'] for r in tasks if r['asset_type']=='rolling-stock'}
    first_phase=json.loads((OUT.parent/'delivery-baseline/first-phase.json').read_text())
    assert len(stock)==factory['selected_trainsets']==first_phase['opening_fleet']
    assert len({r['asset_id'] for r in tasks if 'OPENING-EXTRA' in r['asset_id']})==1
    baseline=json.loads((OUT.parent/'delivery-risk/summary.json').read_text())['cases']['calendar_baseline']['phases']
    deadlines={r['line']:r['opening_month'] for r in baseline}
    assert all(r['opening_month']>=deadlines[r['line']] for r in factory['delivery']['phases'])
    cash=read('finance-opening_fleet_supply_scaled')
    assert cash['operating_phases']==factory['delivery']['phases']
    first=min(r['opening_month'] for r in cash['operating_phases'])
    last=max(r['opening_month'] for r in cash['operating_phases'])
    assert all(r['fare_receipts_iqd']==0 for r in cash['monthly'] if r['month']<first)
    assert max(r['month'] for r in cash['monthly'])==last+30*12-1
    assert factory['factory_ready_month']==18 and not factory['factory_repriced'] and not factory['accepted']
    occupied={}
    for row in sorted(tasks,key=lambda r:r['start_hour']):
        if row['asset_type']!='rolling-stock':continue
        lane=(row['resource_pool'],row['resource_lane'])
        assert row['start_hour']>=occupied.get(lane,0),row['manufacturing_uid']
        occupied[lane]=row['end_hour']

def test_corridor_break_even_has_no_fabricated_od_or_rank():
    c=read('corridor-comparison');assert len(c['cases'])==9 and not c['first_corridor_selected']
    for row in c['cases']:
        cash=max(0,row['reference_annual_opex_usd']-row['allocated_existing_nonfare_usd'])
        assert row['operating_break_even_paid_trips']*row['base_yield_iqd']/1300==pytest.approx(cash)
        assert row['commercial_rank'] is None and row['actual_od_demand'] is None
        assert row['allocated_borrower_debt_service_usd'] is None

def test_higher_fares_reduce_demand_and_distinguish_cash_npv_from_clearance():
    rows=read('fare-sensitivities');assert len(rows)==5
    assert all(r['paid_demand_multiplier']<1 and not r['adopted'] for r in rows)
    assert [r['paid_demand_multiplier'] for r in rows]==sorted([r['paid_demand_multiplier'] for r in rows],reverse=True)
    assert [r['company_cash_npv_before_finance_usd'] for r in rows]==sorted(r['company_cash_npv_before_finance_usd'] for r in rows)
    assert all(r['monthly_44_trip_income_share']>.10 for r in rows)

def test_pilot_roster_covers_service_with_rest_and_hours_but_no_real_worker():
    roster=read('pilot-roster');assert roster['required_weekly_cover_hours']==143.5
    for row in roster['slots']:
        assert row['end_hour_from_week']-row['start_hour_from_week']<=8
        assert row['prior_rest_hours'] is None or row['prior_rest_hours']>=11
        assert row['hours_rolling_7_days']<=40
        assert row['native_employee'] is None and not row['eligible']
    assert not roster['roster_released']

def test_field_and_training_packets_are_prepared_not_accepted():
    packet=read('closure-packets');assert len(packet['scope_inclusion_forms'])==12
    assert all(r['repository_artifacts_prepared'] and not r['field_work_completed'] and r['named_owner'] is None for r in packet['work_packages'])
    assert packet['actual_quotes']==packet['named_appointments']==0
    cards=read('lesson-cards');assert len(cards)==7
    assert all(r['arabic_native_review'] is None and r['practical_assessment_result'] is None and not r['attendance_is_competence'] for r in cards)

def test_source_and_output_hashes_current():
    summary=read('summary')
    for base,key in ((ROOT,'sources_sha256'),(OUT,'outputs_sha256')):
        for relative,sha in summary[key].items():assert hashlib.sha256((base/relative).read_bytes()).hexdigest()==sha,relative
    assert not summary['complete_delivery_budget'] and summary['field_work_packages_accepted']==0

@pytest.mark.parametrize('section,key',[('slab_factory','utilisation'),('maintenance','wheel_interval_km'),('mobilisation','maximum_shift_hours')])
def test_invalid_capacity_and_intervals_rejected(section,key):
    c=tomllib.loads(closure.CONFIG.read_text());c[section][key]=0
    with pytest.raises(ValueError):closure.validate(c)


def current_design():
    import tomllib
    return tomllib.loads((ROOT/'cities/catalogue/west-asia/Iraq/Baghdad/design.toml').read_text())

def current_fleet():
    return sum(r['trainset_count'] for r in current_design()['fleets'])
