"""Cross-scope staffing, imported machinery, junior maturity and cash tests."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import tomllib

import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/automation'))
import baghdad_programme_recalculation as programme
import baghdad_recalculation_finance as finance

OUT=programme.OUT
def read(name):return json.loads((OUT/(name+'.json')).read_text())


def synthetic(horizon=6):
    c=tomllib.loads(programme.CONFIG.read_text())
    c['financing'].update(debt_service_reserve_months=0,operating_buffer_months=0,gap_draw_fee=0)
    c['mezzanine'].update(cash_coupon=.12,pik_coupon=.12,overdue_interest_annual_rate=.24,arrangement_fee=0,maturity_months_from_draw=2)
    terms=dict(annual_rate=0,grace_months_from_draw=9999,repayment_months=12,arrangement_fee=0,undrawn_commitment_fee=0)
    funding={'model':{'operating_years':30},'chinese_export_credit':dict(terms,currency='USD'),
        'domestic_bonds':dict(terms,currency='IQD'),'bank_credit':dict(terms,currency='IQD')}
    options=tomllib.loads((ROOT/'lib/templates/baghdad-finance-options.toml').read_text())
    options['green']['blended_rate']=0
    options['prepayments']['minimum_age_months']={n:0 for n in options['prepayments']['minimum_age_months']}
    phases=[dict(line='L1',opening_month=0,weight=1)]
    op=[dict(month=m,revenue_usd=0,opex_usd=0,phases=phases) for m in range(horizon)]
    return c,funding,options,op


def test_machinery_downpayments_follow_invoices_but_total_government_stays_25pct():
    c,f,o,op=synthetic()
    capital={0:dict(capex=100,imports=80),1:dict(capex=100,imports=0)}
    r=finance.simulate(capital,op,f,o,c,extras=False)
    assert r['metrics']['government_share']==pytest.approx(.25)
    assert r['monthly'][0]['government_usd_cash']==40
    assert r['monthly'][0]['government_usd_cash']+r['monthly'][0]['government_iqd_cash']/1300>25
    assert r['metrics']['chinese_usd_draw']==40
    assert max(abs(row['capital_residual_usd']) for row in r['monthly'])<1e-7


def test_junior_deferral_is_debt_and_unpaid_balloon_is_not_refinanced_or_compounded():
    c,f,o,op=synthetic()
    op[1]['opex_usd']=10
    r=finance.simulate({0:dict(capex=200,imports=0)},op,f,o,c,mezzanine=True,extras=False)
    rows=r['monthly']
    assert rows[1]['gap_draw_iqd']>0 and rows[1]['mezzanine_interest_cash_iqd']==0
    assert rows[1]['mezzanine_pik_iqd']>0 and rows[1]['mezzanine_deferred_coupon_iqd']>0
    assert rows[2]['mezzanine_unpaid_balloon_at_maturity_iqd']>0
    assert rows[3]['mezzanine_pik_iqd']==rows[3]['mezzanine_deferred_coupon_iqd']==0
    assert rows[3]['closing_mezzanine_principal_iqd']==rows[2]['closing_mezzanine_principal_iqd']
    assert rows[3]['mezzanine_overdue_interest_accrued_iqd']==pytest.approx(rows[4]['mezzanine_overdue_interest_accrued_iqd'])
    assert r['metrics']['junior_defaulted_vintages']==1
    assert r['metrics']['all_debt_cleared_month'] is None
    assert not r['automatic_refinancing']


def test_payments_with_actual_surplus_reduce_junior_principal_once():
    c,f,o,op=synthetic()
    op[2]['revenue_usd']=300
    r=finance.simulate({0:dict(capex=200,imports=0)},op,f,o,c,mezzanine=True,extras=False)
    assert r['monthly'][2]['mezzanine_principal_iqd']>0
    assert r['monthly'][2]['closing_mezzanine_iqd']==0
    assert r['metrics']['junior_defaulted_vintages']==0
    assert r['metrics']['maximum_cash_residual_usd']<1e-7


def test_station_rosters_wages_and_depot_slots_bind_full_baghdad_scope():
    people=read('workforce');depots=read('depots')
    assert people['station_cover']['normal_daily_shift_assignments']==4*len(current_design()['stations'])
    assert people['station_cover']['simultaneous_posts']==2*len(current_design()['stations'])
    assert people['station_cover']['additional_late_hours_per_station']==4.5
    assert people['station_cover']['station_cover_fte']>=len(current_design()['stations'])*20.5*365*2/people['productive_hours_per_fte']
    median=people['wage_basis']['indexed_planning_median_iqd']
    assert all(r['monthly_base_iqd']>=1.5*median-.01 for r in people['roles'])
    assert sum(r['required_fte'] for r in people['roles'])==people['reference_required_fte']
    assert sum(r['annual_loaded_payroll_iqd'] for r in people['roles'])==pytest.approx(people['reference_annual_loaded_payroll_iqd'])
    assert depots['number_of_depots']==9 and depots['full_fleet_storage_slots']==current_fleet()
    assert len({r['line'] for r in depots['sites']})==9
    for depot in depots['sites']:
        assert sum(t['slots'] for t in depot['tracks'])==depot['trainsets']
        assert depot['workshop_bay_hours_capacity']>=depot['workshop_bay_hours_demand']
        assert all(t['usable_length_m']==t['slots']*121 for t in depot['tracks'])


def test_factory_establishment_is_paid_through_the_scheduled_order():
    industry=read('industry')
    people=read('workforce')
    cfg=tomllib.loads(programme.CONFIG.read_text())
    wage=people['wage_basis']['indexed_planning_median_iqd']*cfg['wages']['technical_multiplier']
    annual=wage*12*(1+cfg['wages']['employer_cost_fraction']+cfg['wages']['overtime_allowance_fraction'])/cfg['model']['iqd_per_usd']
    years=industry['paid_production_years']
    assert industry['production_months']==industry['production_end_month']-cfg['industry']['ready_month']+1
    assert industry['main_assembly_variable_payroll_usd']+industry['main_factory_capacity_payroll_topup_usd']==pytest.approx(industry['main_factory_production_fte']*annual*years)
    for product in industry['products']:
        assert product['annual_production_payroll_in_unit_prices_usd']+product['annual_capacity_payroll_topup_usd']==pytest.approx(product['production_fte']*annual)
        assert product['annual_fixed_factory_cost_usd']==pytest.approx(product['support_fte']*annual+product['annual_capacity_payroll_topup_usd']+product['incremental_capital_usd']*cfg['industry']['fixed_plant_maintenance_fraction'])


def test_fabrication_counts_capacity_parent_budgets_and_residual_imports():
    industry=read('industry');products={r['id']:r for r in industry['products']}
    assert products['bogie']['network_quantity']==products['motor-inverter-set']['network_quantity']==current_fleet()*12
    assert products['battery-225kwh-pack']['network_quantity']==current_fleet()*6
    assert products['door-cassette']['network_quantity']==current_fleet()*24
    assert products['window-cassette']['network_quantity']==current_fleet()*36
    assert industry['battery_gross_network_kwh']==current_fleet()*6*225
    assert industry['no_cell_manufacturing_plant_assumed']
    assert all(r['annual_cell_output_capacity']>=r['annual_required_output'] for r in products.values())
    assert all(r['imported_input_usd_per_unit']>0 and not r['first_article_accepted'] for r in products.values())
    assert 'window-cassette' not in read('local_positive')['selected_component_factories']
    assert read('local_positive')['metrics']['imported_invoices_usd']<read('revised_scope_buy')['metrics']['imported_invoices_usd']


@pytest.mark.parametrize('name',['revised_scope_buy','local_all','local_positive','local_positive_mezzanine',
    'local_positive_commercial_gap','local_positive_mezzanine_stress','additional_elevation_base_allowance','local_positive_raw_price_stress',
    'local_positive_supplier_delay','construction_wage_content_stress','integrated_fare_1_25_boardings','integrated_fare_1_5_boardings','integrated_fare_2_boardings'])
def test_every_cashflow_and_native_principal_and_six_month_tranche_reconciles(name):
    data=read(name);metrics=data['metrics'];rows=data['monthly']
    assert metrics['government_share']==pytest.approx(.25)
    assert metrics['dividends_iqd']==0 and not metrics['financing_committed']
    assert metrics['maximum_cash_residual_usd']<.02
    assert metrics['maximum_mezzanine_balance_residual_usd']<.02
    assert metrics['maximum_senior_balance_residual_usd']<.02
    assert metrics['maximum_capital_residual_usd']<.02
    total_capital=sum(r['capex_usd'] for r in rows)
    assert metrics['total_capital_usd']==pytest.approx(total_capital)
    for tranche in data['semiannual']:
        part=rows[tranche['start_month']:tranche['end_month']+1]
        assert len(part)<=6
        assert tranche['bond_face_iqd']==pytest.approx(sum(r['domestic_bonds_draw_native']+r['green_bonds_draw_native'] for r in part))
        assert tranche['closing_mezzanine_iqd']==part[-1]['closing_mezzanine_iqd']
        assert tranche['bond_units']*1000000>=tranche['bond_face_iqd']
    if data['mezzanine_terms']:
        for row in rows:
            if row['gap_draw_iqd']>.01 or row['unfunded_support_iqd']>.01:
                assert row['mezzanine_interest_cash_iqd']==row['mezzanine_principal_iqd']==0


def test_delay_and_raw_input_and_construction_stress_do_not_invent_savings():
    base=read('local_positive');delay=read('local_positive_supplier_delay')
    assert min(p['opening_month'] for p in delay['opening_phases'])==min(p['opening_month'] for p in base['opening_phases'])+6
    assert max(p['opening_month'] for p in delay['opening_phases'])==max(p['opening_month'] for p in base['opening_phases'])+6
    assert len(delay['monthly'])==len(base['monthly'])+6
    assert all(r['revenue_iqd']==0 for r in delay['monthly'] if r['month']<min(p['opening_month'] for p in delay['opening_phases']))
    assert read('local_positive_raw_price_stress')['metrics']['total_capital_usd']>base['metrics']['total_capital_usd']
    assert read('construction_wage_content_stress')['metrics']['total_capital_usd']>base['metrics']['total_capital_usd']
    alignment=read('alignment')
    assert alignment['elevation_alone_removes_no_horizontal_bend']
    assert alignment['candidate_elevated_fraction']<=alignment['policy']['maximum_elevated_fraction']
    assert not any(r['achieved_saving'] for r in alignment['alternatives'])


def current_design():
    import tomllib
    return tomllib.loads((ROOT/'cities/catalogue/west-asia/Iraq/Baghdad/design.toml').read_text())

def current_fleet():
    return sum(r['trainset_count'] for r in current_design()['fleets'])


def test_integrated_transfers_reduce_fares_without_reducing_commercial_income_or_costs():
    original=[dict(month=0,revenue_usd=120,fare_revenue_usd=100,nonfare_revenue_usd=20,opex_usd=80)]
    corrected=programme.integrated_journey_projection(original,2)
    assert corrected[0]['fare_revenue_usd']==50
    assert corrected[0]['nonfare_revenue_usd']==20
    assert corrected[0]['revenue_usd']==70 and corrected[0]['opex_usd']==80
    assert original[0]['revenue_usd']==120
    with pytest.raises(ValueError):programme.integrated_journey_projection(original,float('nan'))
    with pytest.raises(ValueError):programme.integrated_journey_projection(original,.5)
