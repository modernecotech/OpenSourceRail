"""Ordinary shares must reconcile to real cash, capital, debt and distributions."""
from copy import deepcopy
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import tomllib
import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/automation'))
from baghdad_equity import CORE, equity_irr, validate, consolidated_inputs, simulate_equity, report_text
from baghdad_financing_redesign import city_funding_config
OUT=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad/engineering/equity'

def read(name):return json.loads((OUT/(name+'.json')).read_text())

@pytest.fixture(scope='module')
def cases():
    return {name:read(name) for name in read('summary')['cases']}

@pytest.mark.parametrize('name,private',[('primary_500m',500e6),('primary_1000m',1e9),('primary_2000m',2e9)])
def test_paid_cap_table_and_fresh_cash(cases,name,private):
    c=cases[name];m=c['metrics'];programme=json.loads((OUT.parents[2]/'finance/baghdad-programme.json').read_text());government=programme['total_capex_usd']*.25
    assert m['government_capital_usd']==pytest.approx(government,abs=.02)
    assert m['government_ownership']==pytest.approx(government/(government+private))
    assert m['government_equity_reclassification_new_cash_usd']==0
    assert m['primary_gross_equity_usd']==pytest.approx(private,abs=.02)
    assert m['primary_net_equity_usd']==pytest.approx(private*.98,abs=.02)
    assert m['primary_issue_fees_usd']==pytest.approx(private*.02,abs=.02)
    assert sum(c['final_shares'].values())==pytest.approx((government+private)*1300)
    source=json.loads((OUT.parent/'financing-redesign/integrated.json').read_text())
    assert c['source_equity_replaced_iqd']==pytest.approx(sum(e['metrics']['private_equity_iqd'] for e in source['entities'].values()),abs=.1)
    assert m['total_capital_usd']==pytest.approx(programme['total_capex_usd']+2.4e9,abs=.02)
    assert m['chinese_credit_usd']==pytest.approx(programme['usd_denominated_capital_usd']/2,abs=.02)
    assert sum(r['government_usd_cash'] for r in c['monthly'])==pytest.approx(m['chinese_credit_usd'],abs=.02)


def test_reclassification_and_secondary_do_not_raise_company_money(cases):
    grant,equity,secondary=(cases[n] for n in ('government_grant_reference','government_equity_reference','secondary_500m'))
    for n in ('chinese_credit_usd','domestic_bond_face_iqd','bank_capital_iqd','peak_liquidity_debt_iqd'):
        assert grant['metrics'][n]==equity['metrics'][n]==secondary['metrics'][n]
    assert secondary['metrics']['secondary_seller_receipts_usd']==pytest.approx(500e6)
    assert secondary['metrics']['secondary_company_receipts_usd']==0
    assert secondary['metrics']['primary_gross_equity_usd']==0
    assert sum(secondary['final_shares'].values())==pytest.approx(sum(equity['final_shares'].values()),abs=.02)
    assert not any(grant['final_shares'].values())
    assert not any(r['government_equity_iqd'] for r in grant['monthly'])


def test_issue_premium_changes_dilution_without_creating_cash(cases):
    normal,premium=cases['primary_1000m'],cases['primary_1000m_premium']
    gov=normal['metrics']['government_capital_usd']
    assert premium['metrics']['government_ownership']==pytest.approx(gov/(gov+750e6+250e6/1.2))
    assert premium['monthly'][-1]['share_premium_iqd']==pytest.approx(250e6/1.2*.2*1300)
    for key in ('primary_gross_equity_usd','peak_liquidity_debt_iqd','total_dividends_iqd'):
        assert normal['metrics'][key]==premium['metrics'][key]


@pytest.mark.parametrize('name',['primary_500m','primary_1000m','primary_2000m','primary_1000m_premium'])
def test_paid_state_and_local_share_floors_hold_every_month(cases,name):
    rows=cases[name]['monthly']
    assert any(r['pending_subscription_cash_usd']>0 for r in rows)
    for r in rows:
        assert r['government_ownership']>=.25-1e-12
        assert r['iraqi_ownership']>=.51-1e-12
        assert r['paid_up_nominal_capital_iqd']==pytest.approx(sum(r[k] for k in ('government_shares','iraqi_private_shares','foreign_private_shares')))


@pytest.mark.parametrize('name',['undersubscribed_1000m','failed_later_primary','joint_downside_undersubscribed'])
def test_failed_subscriptions_stop_construction_without_capital_rescue(cases,name):
    c=cases[name];stop=c['funding_stop']
    assert c['status']=='funding-blocked-no-opening'
    assert c['opening_month'] is None and c['full_opening_month'] is None
    assert stop['month']==c['monthly'][-1]['month']+1
    assert sum(stop['refused_capital_credit_usd'].values())>.02
    assert stop['withheld_physical_capital_usd']>0
    assert stop['debt_not_forgiven'] and not stop['resolution_cashflows_modelled']
    assert c['metrics']['first_dividend_month'] is None
    assert not c['metrics']['all_debt_cleared_without_unfunded_support']
    assert c['shareholder_returns']['iraqi_private']['equity_irr'] is None
    assert c['metrics']['total_capital_usd']<cases['primary_1000m']['metrics']['total_capital_usd']


@pytest.mark.parametrize('name',['government_grant_reference','government_equity_reference','primary_500m','primary_1000m','primary_2000m',
    'primary_1000m_premium','secondary_500m','undersubscribed_1000m','failed_later_primary','delayed_1000m',
    'joint_downside_1000m','joint_downside_undersubscribed','aggregate_tax_proxy_1000m',
    'coverage_dividends_1000m','rental_small_1000m','rental_medium_1000m','rental_medium_downside_1000m','rental_medium_coverage_1000m'])
def test_independent_cash_principal_and_net_asset_reconciliation(cases,name):
    c=cases[name];previous_cash=previous_capital=previous_reserve=previous_buffer=previous_renewal=gap=deposit=0.
    balances={n:0. for n in CORE}
    for r in c['monthly']:
        capital=(r['government_usd_cash']+(r['government_iqd_cash']+r['private_equity_capital_use_iqd'])/1300+
            r['chinese_export_credit_draw_native']+(r['domestic_bonds_draw_native']+r['bank_credit_draw_native'])/1300)
        assert capital==pytest.approx(r['physical_capital_iqd']/1300,abs=.02)
        sources=(r['government_usd_cash']+r['government_iqd_cash']/1300+r['primary_net_subscription_iqd']/1300+
            sum(r[n+'_draw_native']/(1 if n=='chinese_export_credit' else 1300) for n in CORE)+
            (r['revenue_iqd']+r['liquidity_draw_iqd']+r['uncovered_support_required_iqd'])/1300)
        uses=((r['physical_capital_iqd']+r['opex_iqd']+r['tax_iqd']+r['liquidity_interest_iqd']+r['liquidity_fees_iqd']+
            r['liquidity_repayment_iqd']+r['early_premiums_iqd']+r['total_dividend_iqd'])/1300+
            sum(sum(r[n+'_'+k+'_native'] for k in ('interest','principal','fees','early_principal'))/(1 if n=='chinese_export_credit' else 1300) for n in CORE)+
            (r['closing_dsra_iqd']-previous_reserve+r['closing_operating_and_warranty_buffer_iqd']-previous_buffer+r['closing_renewal_reserve_iqd']-previous_renewal)/1300)
        assert previous_cash+previous_capital+sources-uses==pytest.approx((r['closing_cash_iqd']+r['closing_capital_cash_iqd'])/1300,abs=.02)
        for n in CORE:
            balances[n]+=r[n+'_draw_native']-r[n+'_principal_native']-r[n+'_early_principal_native']
            assert balances[n]==pytest.approx(r[n+'_closing_balance_native'],abs=.02)
        gap+=r['liquidity_draw_iqd']-r['liquidity_repayment_iqd']
        assert gap==pytest.approx(r['closing_liquidity_debt_iqd'],abs=.1)
        assets=sum(r[k] for k in ('closing_cash_iqd','closing_capital_cash_iqd','closing_dsra_iqd',
            'closing_operating_and_warranty_buffer_iqd','closing_ppe_iqd','closing_property_inventory_iqd','closing_renewal_reserve_iqd','rental_restricted_deposit_cash_iqd'))
        assert assets-r['liabilities_iqd']==pytest.approx(r['net_assets_iqd'],abs=.1)
        # Consolidated balances reach trillions of IQD; subtracting binary
        # floats must still reconcile within one dinar, not a tenth of one.
        assert r['net_assets_iqd']-r['shareholder_book_equity_iqd']==pytest.approx(r['assumed_unfunded_support_cumulative_iqd'],abs=1.)
        previous_cash,previous_capital=r['closing_cash_iqd']/1300,r['closing_capital_cash_iqd']/1300
        previous_reserve,previous_buffer=r['closing_dsra_iqd'],r['closing_operating_and_warranty_buffer_iqd']
        previous_renewal=r['closing_renewal_reserve_iqd']
        deposit+=r['rental_deposit_received_iqd']-r['rental_deposit_refunded_iqd']
        assert deposit==pytest.approx(r['rental_tenant_deposit_liability_iqd'],abs=.1)
        assert r['rental_restricted_deposit_cash_iqd']==r['rental_tenant_deposit_liability_iqd']
    for r in c['semiannual']:assert abs(r['capital_reconciliation_usd'])<.02


def test_resource_value_matches_prior_group_and_accounting_non_cash_charges(cases):
    old=json.loads((OUT.parent/'financing-redesign/integrated.json').read_text())
    for name in ('government_equity_reference','primary_500m','primary_1000m','primary_2000m','secondary_500m'):
        m=cases[name]['metrics']
        assert m['core_resource_npv_usd']==pytest.approx(old['appraisal']['consolidated_resource_npv_usd'],abs=.02)
        assert m['resource_npv_after_land_usd']==pytest.approx(old['appraisal']['consolidated_resource_npv_after_land_opportunity_usd'],abs=.02)
    with (OUT/'group-resource-monthly.csv').open() as f:resources=list(csv.DictReader(f))
    ppe_changes=[];inventory=0.
    for r,s in zip(cases['primary_1000m']['monthly'],resources):
        # Independent accumulation avoids losing sub-dinar precision when
        # hundreds of monthly changes are added to trillion-dinar balances.
        ppe_changes.extend(float(s[k+'_capital_usd'])*1300 for k in ('rail','train','solar','factory'))
        ppe_changes.extend((-r['depreciation_iqd'],-r['factory_impairment_iqd']))
        ppe=math.fsum(ppe_changes)
        inventory+=float(s['property_build_usd'])*1300-r['property_cost_of_sales_iqd']
        assert ppe==pytest.approx(r['closing_ppe_iqd'],abs=.1)
        assert inventory==pytest.approx(r['closing_property_inventory_iqd'],abs=.05)
        assert abs(float(s['consolidation_residual_usd']))<.02
    assert inventory==pytest.approx(0.,abs=.02)


def test_tax_accrual_payment_and_dividend_lock(cases):
    c=cases['primary_1000m'];prior_tax=0.
    for r in c['monthly']:
        assert r['tax_iqd']==pytest.approx(prior_tax,abs=.02)
        prior_tax=r['tax_accrual_iqd']
        if r['total_dividend_iqd']:
            assert r['retained_profit_iqd']>0
            assert r['closing_liquidity_debt_iqd']<.02
            assert all(r[n+'_closing_balance_native']<.02 for n in CORE)
            assert r['assumed_unfunded_support_cumulative_iqd']<.02
            assert r['closing_capital_cash_iqd']<.02
            assert sum(r[k+'_dividend_iqd'] for k in ('government','iraqi_private','foreign_private'))==pytest.approx(r['total_dividend_iqd'])
            assert r['government_dividend_iqd']==pytest.approx(r['total_dividend_iqd']*r['government_ownership'])
    assert c['monthly'][-1]['closing_tax_payable_iqd']==pytest.approx(0.,abs=.02)
    assert c['metrics']['corporate_cash_tax_iqd']>cases['aggregate_tax_proxy_1000m']['metrics']['corporate_cash_tax_iqd']
    assert cases['joint_downside_1000m']['metrics']['uncovered_support_iqd']>30e12
    assert cases['joint_downside_1000m']['metrics']['total_dividends_iqd']==0
    returns=c['shareholder_returns']['iraqi_private']
    if returns['equity_irr'] is None:
        assert returns['cash_return_usd']==0
    else:
        assert returns['equity_irr']<.05
    assert c['shareholder_returns']['iraqi_private']['equity_npv_at_hurdle_usd']<0


def test_irr_is_a_shareholder_cash_metric():
    assert equity_irr([(0,-100),(12,110)])==pytest.approx(.10)
    assert equity_irr([(0,-100),(24,121)])==pytest.approx(.10)
    assert equity_irr([(0,-100),(12,0)]) is None
    assert equity_irr([(0,-100),(12,150),(24,-20)]) is None


def test_report_preserves_undefined_returns_and_absent_dividends(cases):
    candidates=deepcopy(cases)
    for case in candidates.values():
        case['metrics']['first_dividend_month']=None
        case['shareholder_returns']['iraqi_private']['equity_irr']=None
        case['terminal_cash_sensitivity']['shareholder_returns']['iraqi_private']['equity_irr_with_terminal_cash']=None
    config=tomllib.loads((ROOT/'lib/templates/baghdad-equity.toml').read_text())
    text=report_text(candidates,config)
    assert 'undefined' in text
    assert 'not reached in the modelled horizon' in text
    assert 'month None' not in text
    assert 'roughly 3% nominal return' not in text


def test_domestic_vintages_wait_for_full_network_and_delay_keeps_scope(cases):
    c=cases['primary_1000m']
    for v in c['loan_vintages']:
        if v['instrument']!='chinese_export_credit':
            assert v['first_contractual_principal_month']>=c['full_opening_month']
            assert v['repayment_months']==(240 if v['instrument']=='bank_credit' else 216)
        else:assert v['first_contractual_principal_month']==v['month']+49
    delayed=cases['delayed_1000m']
    assert (delayed['opening_month'],delayed['full_opening_month'])==(c['opening_month']+6,c['full_opening_month']+6)
    assert all(r['physical_capital_iqd']==r['primary_gross_subscription_iqd']==0 for r in delayed['monthly'][:6])
    assert delayed['metrics']['total_capital_usd']==c['metrics']['total_capital_usd']


def test_legal_and_admission_are_pending_even_when_arithmetic_passes(cases):
    for c in cases.values():
        assert not c['company_incorporated'] and not c['listing_approved'] and not c['financing_committed']
    assert cases['primary_1000m']['metrics']['indicative_article28_threshold_failed_months']>0
    for name in ('primary_1000m','primary_2000m'):
        case=cases[name]
        breaches=[r['month'] for r in case['monthly'] if r['liabilities_iqd']>3*r['shareholder_book_equity_iqd']+.02]
        assert case['metrics']['indicative_article28_threshold_failed_months']==len(breaches)
        assert case['metrics']['first_indicative_article28_threshold_failed_month']==(breaches[0] if breaches else None)
    gates=read('listing-gates')
    assert gates['actual_shareholder_count'] is None and gates['accepted_audits']==0
    assert gates['open_source_design_exclusivity_valuation_iqd']==0
    assert gates['unvalued_land_paid_in_equity_iqd']==0
    packages=read('90-day-work-programme')['work_packages']
    assert len(packages)==6 and all(p['named_owner'] is None and p['evidence'] is None for p in packages)
    assert all(t['status']=='Open' for t in read('erpnext-tasks')['tasks'])


def test_invalid_equity_terms_rejected():
    config=tomllib.loads((ROOT/'lib/templates/baghdad-equity.toml').read_text())
    for section,key,value in [('model','subscription_price_iqd',.5),('model','private_iraqi_fraction',1.1),
        ('accounting','rail_asset_life_years',0),('accounting','terminal_asset_sale_usd',1000)]:
        invalid=deepcopy(config);invalid[section][key]=value
        with pytest.raises(ValueError):validate(invalid)


def test_generated_hashes_and_every_six_month_cash_total(cases):
    summary=read('summary')
    assert summary['included_cities']==['Baghdad']
    for base,key in ((ROOT,'sources_sha256'),(OUT,'outputs_sha256')):
        for rel,sha in summary[key].items():assert hashlib.sha256((base/rel).read_bytes()).hexdigest()==sha,rel
    c=cases['primary_1000m']
    for key in ('government_iqd_cash','primary_gross_subscription_iqd','tax_iqd','total_dividend_iqd',
        'chinese_export_credit_draw_native','domestic_bonds_draw_native','bank_credit_draw_native'):
        assert sum(r[key] for r in c['semiannual'])==pytest.approx(sum(r[key] for r in c['monthly']),abs=.02)
