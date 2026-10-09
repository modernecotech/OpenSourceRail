"""Debt timing, standalone liabilities and programme consolidation must agree."""
from copy import deepcopy
import csv
import hashlib
import json
from pathlib import Path
import sys
import tomllib
import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools/automation'))
from baghdad_funding_analysis import add_draw, debt_month, simulate
from baghdad_financing_redesign import opening_terms, scoped_insured_terms, npv, insured_options
from osr_scenario.iraq_finance import city_funding_config
OUT = ROOT/'cities/catalogue/west-asia/Iraq/Baghdad/engineering/financing-redesign'

@pytest.fixture(scope='module')
def summary():
    return json.loads((OUT/'summary.json').read_text())

def test_per_vintage_grace_charges_interest_and_finishes_at_contractual_date():
    loans=[]
    terms=dict(annual_rate=.12, grace_months_from_draw=3, repayment_months=4)
    add_draw(loans,2,1000.,terms)
    principal=[]
    for month in range(2,10):
        interest, paid=debt_month(loans,month,dict(terms,grace_months_from_draw=0))
        principal.append(paid)
        if month <=5:
            assert interest==pytest.approx(5 if month==2 else 10)
            assert paid==0
    assert sum(principal)==pytest.approx(1000.)
    assert loans[0]['balance']==pytest.approx(0,abs=1e-9)


def test_opening_cohorts_wait_for_latest_actual_financed_line():
    cfg=city_funding_config(tomllib.loads((ROOT/'lib/templates/iraq-funding.toml').read_text()),'baghdad')
    redesign=tomllib.loads((ROOT/'lib/templates/baghdad-financing-redesign.toml').read_text())
    contracts=[dict(budget_usd=100.,imported_share=0.,planned_start_day=0,planned_finish_day=100,bucket='civil',manufacturing_uid=uid) for uid in ('A','B')]
    phases=[dict(line='early',opening_month=41),dict(line='late',opening_month=83)]
    result=opening_terms({0:{}},contracts,{'A':'early','B':'late'},phases,cfg,redesign,insured=True)
    assert result[0]['bank_credit']['grace_months_from_draw']+1==83
    assert sum(result[0]['green_bonds'].values())==180


def test_ineligible_insured_cohort_does_not_receive_an_extended_coverage_window():
    cfg=city_funding_config(tomllib.loads((ROOT/'lib/templates/iraq-funding.toml').read_text()),'baghdad')
    redesign=tomllib.loads((ROOT/'lib/templates/baghdad-financing-redesign.toml').read_text())
    phases=[dict(line='late',opening_month=200)]
    terms,eligible,excluded=scoped_insured_terms({0:{}},[],{},phases,cfg,redesign)
    assert excluded==[0] and eligible==set()
    assert 'green_bonds' not in terms[0]
    assert terms[0]['bank_credit']['grace_months_from_draw']==199
    with pytest.raises(ValueError,match='no amortisation'):
        opening_terms({0:{}},[],{},phases,cfg,redesign,insured=True)


def test_reference_matches_current_baseline_and_debt_changes_do_not_create_npv(summary):
    c=summary['cases']; risk=json.loads((OUT.parent/'delivery-risk/summary.json').read_text())['cases']['calendar_baseline']['metrics']
    for field in ('peak_supplemental_balance_iqd','total_finance_interest_and_fees_usd','government_capital_usd_equivalent'):
        assert c['reference']['metrics'][field]==pytest.approx(risk[field],abs=.02)
    for name in ('opening_linked_debt','development_rights_1bn','insured_15year_debt'):
        assert c[name]['appraisal']['core_unlevered_npv_usd']==c['reference']['appraisal']['core_unlevered_npv_usd']
    assert c['development_rights_1bn']['metrics']['net_rights_receipts_iqd']/1300==pytest.approx(1e9)
    assert c['reference']['metrics']['net_rights_receipts_iqd']/1300==pytest.approx(300e6)


def test_integrated_conserves_original_capital_and_usd_imports(summary):
    m=summary['cases']['integrated']['metrics']; reference=summary['cases']['reference']['metrics']
    assert m['total_original_rail_energy_factory_capital_usd']==pytest.approx(reference['total_capital_usd'],abs=.02)
    assert m['government_cash_share_of_original_capital']==pytest.approx(.25)
    assert m['government_usd_cash']==pytest.approx(m['chinese_usd_credit'],abs=.02)
    assert m['chinese_usd_credit']==pytest.approx(reference['china_capital_usd'],abs=.02)
    assert m['allocated_liquidity_cap_iqd']==13e12
    assert m['climate_grant_usd']==0 and m['future_city_order_revenue_usd']==0 and m['surplus_power_revenue_usd']==0
    assert m['additional_rights_vs_original_usd']==700e6


def test_ppa_price_and_public_payments_do_not_create_consolidated_resource_value(summary):
    c=summary['cases']; normal=c['integrated']['appraisal']
    for name in ('integrated_low_ppa','integrated_high_ppa','integrated_public_availability'):
        assert c[name]['appraisal']['consolidated_resource_npv_usd']==pytest.approx(normal['consolidated_resource_npv_usd'],abs=.02)
    assert c['integrated_high_ppa']['appraisal']['rail_entity_unlevered_npv_with_internal_payments_and_rights_usd'] < c['integrated_low_ppa']['appraisal']['rail_entity_unlevered_npv_with_internal_payments_and_rights_usd']
    support=c['integrated_public_availability']['appraisal']
    assert support['additional_public_availability_payment_pv_usd']>0
    assert support['consolidated_recipient_npv_with_public_capital_and_support_usd']-normal['consolidated_recipient_npv_with_public_capital_and_support_usd']==pytest.approx(support['additional_public_availability_payment_pv_usd'],abs=.02)
    assert normal['consolidated_resource_npv_after_land_opportunity_usd']==pytest.approx(normal['consolidated_resource_npv_usd']-normal['public_land_opportunity_pv_usd'])


def test_all_company_native_cash_principal_capital_and_insured_tenors_reconcile():
    for name in ('integrated','integrated_joint_downside'):
        case=json.loads((OUT/(name+'.json')).read_text())
        for entity,ledger in case['entities'].items():
            assert ledger['metrics']['maximum_cash_residual_usd'] < .02
            assert ledger['metrics']['maximum_principal_balance_residual_usd'] < .02
            assert max(abs(t['capital_reconciliation_usd']) for t in ledger['semiannual']) < .02
            for loan in ledger['loan_vintages']:
                if loan['instrument']=='green_bonds':
                    assert loan['contractual_last_principal_month']-loan['draw_month']<=180
                assert loan['currency']==('USD' if loan['instrument']=='chinese_export_credit' else 'IQD')
        assert case['metrics']['maximum_internal_transfer_residual_usd'] < .02
        assert abs(case['appraisal']['consolidation_npv_residual_usd']) < .02


def test_factory_receipts_are_matched_resources_not_extra_programme_income():
    case=json.loads((OUT/'integrated.json').read_text());f=case['factory']; rows=case['intercompany_monthly']
    assert f['train_invoice_total_usd']==pytest.approx(current_fleet()*1.68e6,abs=.02)
    assert f['manufacturing_resource_cost_usd']==pytest.approx(f['train_invoice_total_usd'],abs=.02)
    assert f['future_order_revenue_usd']==0 and f['residual_sale_usd']==0
    assert f['warranty_restricted_cash_peak_usd']==pytest.approx(.05*f['train_invoice_total_usd'])
    first_invoice=next(r['month'] for r in rows if r['train_rail_capital_invoice_usd']>0)
    first_resources=next(r['month'] for r in rows if r['factory_resource_purchase_usd']>0)
    assert first_resources==first_invoice-1
    assert rows[f['warranty_cash_release_month']]['factory_warranty_locked_cash_usd']==0
    assert all(r['ppa_rail_payment_usd']==r['ppa_energy_receipt_usd'] and r['rights_developer_capital_payment_usd']==r['rights_rail_receipt_usd'] for r in rows)


def test_joint_downside_preserves_stress_and_exposes_missing_money(summary):
    c=summary['cases']['integrated_joint_downside'];m=c['metrics']
    assert m['allocated_liquidity_cap_iqd']==4e12
    assert m['uncovered_support_iqd']>0
    assert m['debt_clearance_month_without_unfunded_support'] is None
    assert m['net_rights_receipts_usd']==500e6
    assert m['total_original_rail_energy_factory_capital_usd']>summary['cases']['reference']['metrics']['total_capital_usd']


def test_titles_quotes_and_named_people_are_not_fabricated():
    land=json.loads((OUT/'station-land-register.json').read_text())
    assert len(land)==15 and len({r['station_id'] for r in land})==15
    assert all(r['parcel_id'] is None and r['legal_owner'] is None and not r['title_verified'] and r['independent_market_value_iqd'] is None for r in land)
    work=json.loads((OUT/'90-day-work-programme.json').read_text())
    assert len(work['work_packages'])==6 and not work['external_contacts_made']
    assert all(r['due_day']<=90 and r['named_owner'] is None and r['evidence'] is None for r in work['work_packages'])


def test_source_and_output_hashes_cover_exact_model(summary):
    for base,group in ((ROOT,'sources_sha256'),(OUT,'outputs_sha256')):
        for name,expected in summary[group].items():
            assert hashlib.sha256((base/name).read_bytes()).hexdigest()==expected


def test_additional_income_example_discounts_from_start_of_payment_period():
    assert npv([(12*i,50e6) for i in range(1,21)],.134)==pytest.approx(342_962_327.2612521,abs=.01)


def test_factory_equity_return_is_distinct_from_cleared_debt(summary):
    case=json.loads((OUT/'integrated.json').read_text())
    factory=case['entities']['factory']['metrics']
    # Cash at order-book close is net of outstanding debt; clearance is not
    # assumed merely because the finite project horizon ended.
    rows=case['entities']['factory']['monthly']
    terminal=sum(rows[-1][n+'_closing_balance_native']/(1 if n=='chinese_export_credit' else 1300) for n in ('chinese_export_credit','domestic_bonds','bank_credit'))+rows[-1]['closing_liquidity_debt_iqd']/1300
    assert (factory['all_debt_cleared_month'] is None)==(terminal>.02)
    assert not factory['equity_cash_recovered_at_zero_hurdle']
    assert factory['equity_npv_at_15pct_orderbook_or_sale_close_usd'] < 0
    assert factory['equity_distribution_assumption_usd'] < factory['private_equity_iqd']/1300


def test_private_equity_and_working_capital_remain_balanced_when_equity_starts_late():
    cfg=city_funding_config(tomllib.loads((ROOT/'lib/templates/iraq-funding.toml').read_text()),'baghdad')
    cfg['model']['debt_service_reserve_months']=0
    options=tomllib.loads((ROOT/'lib/templates/baghdad-finance-options.toml').read_text())
    rows=[dict(month=i,revenue_usd=0.,opex_usd=0.,factory_debt_service_usd=0.,factory_reserve_usd=0.,chinese_commitment_fee_usd=0.,restricted_working_capital_usd=10. if i<2 else 0.) for i in range(3)]
    rows[0]['phases']=[dict(opening_month=0,weight=1.)]
    cap={1:dict(capex=100.,imports=0.,candidate_capex=0.,candidate_imports=0.,private_equity=20.)}
    result=simulate(cap,rows,cfg,options,bridge_rate=0.,repayment_policy='cost_priority')
    assert all('private_equity_iqd' in r for r in result['monthly'])
    assert result['metrics']['private_equity_iqd']==26000
    assert result['metrics']['maximum_cash_residual_usd']<1e-8
    assert abs(result['semiannual'][0]['capital_reconciliation_usd'])<1e-8
    assert result['monthly'][2]['operating_buffer_release_iqd']==13000
    rows[1]['restricted_working_capital_usd']=-1.
    with pytest.raises(ValueError,match='restricted'):
        simulate(cap,rows,cfg,options)


def current_design():
    import tomllib
    return tomllib.loads((ROOT/'cities/catalogue/west-asia/Iraq/Baghdad/design.toml').read_text())

def current_fleet():
    return sum(r['trainset_count'] for r in current_design()['fleets'])
