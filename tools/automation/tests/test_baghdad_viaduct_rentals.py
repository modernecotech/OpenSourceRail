"""Retained premises require real geometry, incremental resources and locked deposits."""
from copy import deepcopy
import hashlib
import gzip
import json
from pathlib import Path
import sys
import tomllib
import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/automation'))
from baghdad_viaduct_rentals import validate,npv
from baghdad_equity import simulate_equity,terminal_cash_diagnostic,with_rental_portfolio,consolidated_inputs
from baghdad_financing_redesign import city_funding_config
OUT=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad/engineering/viaduct-rentals'

def read(name,base=OUT):return json.loads((base/(name+'.json')).read_text())

@pytest.fixture(scope='module')
def config():return tomllib.loads((ROOT/'lib/templates/baghdad-viaduct-rentals.toml').read_text())

def test_geometry_screen_is_civil_linked_and_never_accepted(config):
    rows=read('commercial-space-register');design=tomllib.loads((OUT.parent.parent/'design.toml').read_text())
    assert len(rows)==1143
    assert sum(r['length_m'] for r in rows)==pytest.approx(75810.5,abs=.01)
    assert sum(r['screening_net_area_m2'] for r in rows)==128070
    assert sum(r['confirmed_eligible_area_m2'] for r in rows)==0
    assert len({r['segment_id'] for r in rows})==len(rows)
    for r in rows:
        source=design['civil_segments'][r['design_segment_index']]
        assert source['class']=='elevated' and source['line']==r['line']
        assert (r['chainage_start_m'],r['chainage_end_m'])==(source['from_station_m'],source['to_station_m'])
        assert r['measured_clear_height_m'] is None and r['legal_owner'] is None
        assert not r['eligibility_accepted'] and not r['lease_signed']
        if r['length_m']<75:assert r['screening_bays']==0
    assert sum(not r['parent_track_asset_ids'] for r in rows)==14
    assert read('large')['status']=='unmapped-area-blocked'
    assert read('large')['unmapped_area_m2']==71930 and read('large')['monthly']==[]


def test_pilot_unit_parts_twin_hazards_and_native_drafts(config):
    units=read('pilot-digital-twin');segments={r['segment_id']:r for r in read('commercial-space-register')}
    assets={r['asset_id']:r for r in json.loads(gzip.decompress((OUT.parent.parent/'operations/baghdad-operations.json.gz').read_bytes()))['assets']}
    assert len(units)==30 and len({u['unit_id'] for u in units})==30
    assert len({u['planning_chainage_start_m'] for u in units})==30
    for u in units:
        segment=segments[u['segment_id']]
        assert segment['chainage_start_m']<u['planning_chainage_start_m']<u['planning_chainage_end_m']<segment['chainage_end_m']
        assert u['parent_track_asset_ids'] and u['internal_floor_m2']==30
        for asset_id in u['parent_track_asset_ids']:
            parent=assets[asset_id]
            assert parent['line']==u['line'] and parent['asset_type']=='track-section'
            assert float(parent['km_start'])*1000<u['planning_chainage_end_m']
            assert float(parent['km_end'])*1000>u['planning_chainage_start_m']
        assert u['erp_asset'] is None and u['native_lease_contract'] is None and u['approved_use'] is None
        assert not u['permit_accepted'] and len(u['hazard_ids'])==5
    assert sum(r['reference_allowance_usd'] for r in read('unit-parts'))==21000
    assert all(r['planning_quantity']>0 and r['quote'] is None for r in read('unit-parts'))
    assert len(read('hazards'))==5
    assert all(not h['software_redundancy_mitigation'] and not h['residual_risk_accepted'] for h in read('hazards'))
    packages=read('90-day-work-programme')['work_packages']
    assert len(packages)==6 and all(r['named_owner'] is None and r['evidence'] is None for r in packages)
    assert all(t['status']=='Open' for t in read('erpnext-tasks')['tasks'])


@pytest.mark.parametrize('name',['small','medium','medium_downside'])
def test_rent_arrears_deposits_assets_tax_and_refurbishment_reconcile(name,config):
    c=read(name);deposits=arrears=assets=previous_tax=0.
    for row in c['monthly']:
        deposits+=row['tenant_deposit_received_iqd']-row['tenant_deposit_refunded_iqd']
        assert deposits==pytest.approx(row['tenant_deposit_liability_iqd'],abs=.01)
        assert row['tenant_deposit_liability_iqd']==row['restricted_deposit_cash_iqd']
        assert row['deposit_revenue_iqd']==0
        arrears+=row['arrears_added_usd']-row['arrears_recovered_usd']-row['bad_debt_writeoff_usd']
        assert arrears==pytest.approx(row['closing_arrears_usd'],abs=.01)
        assert row['rent_collected_usd']==pytest.approx(row['contract_rent_billed_usd']-row['arrears_added_usd']+row['arrears_recovered_usd'],abs=.01)
        assets+=row['physical_fitout_capital_usd']-row['depreciation_usd']
        assert assets==pytest.approx(row['closing_ppe_usd'],abs=.01)
        assert row['landlord_opex_usd']==pytest.approx(row['occupied_landlord_opex_usd']+row['refurbishment_usd']+row['vacant_maintenance_and_insurance_usd'],abs=.01)
        terms=config['cases'][name]
        inflation=terms.get('opex_inflation',config['model']['opex_inflation'])
        assert row['occupied_landlord_opex_usd']==pytest.approx(row['occupied_m2']*terms['reference_monthly_rent_usd_per_m2']*.25*(1+inflation)**(row['month']//12),abs=.01)
        assert row['standalone_cash_tax_usd']==pytest.approx(previous_tax,abs=.01)
        previous_tax=row['standalone_tax_accrual_usd']
        for p in c['cohorts']:
            assert p['handover_month']>p['build_last_month']
            assert p['first_billing_month']==p['handover_month']+3
        if row['month']<c['metrics']['first_conditional_receipt_month']:assert row['rent_collected_usd']==0
    assert deposits==pytest.approx(0.,abs=.01) and arrears==pytest.approx(0.,abs=.01)
    assert previous_tax==0
    first_handover=min(p['handover_month'] for p in c['cohorts'])
    free_period=c['monthly'][first_handover]
    assert free_period['rent_collected_usd']==0 and free_period['occupied_landlord_opex_usd']>0
    assert c['metrics']['resource_npv_before_tax_usd']==pytest.approx(npv([(r['month'],r['rent_collected_usd']-r['landlord_opex_usd']-r['physical_fitout_capital_usd']) for r in c['monthly']],.134),abs=.01)
    assert c['additional_public_cash_usd']==c['additional_chinese_credit_usd']==c['terminal_asset_sale_usd']==0


def test_costed_rents_do_not_claim_receipts_only_value_or_double_count_inventory():
    small,medium,weak=(read(n)['metrics'] for n in ('small','medium','medium_downside'))
    assert medium['total_fitout_capital_usd']==pytest.approx(93532439.23250295,abs=.02)
    assert medium['resource_npv_before_tax_usd']==pytest.approx(17244285.200657256,abs=.02)
    assert medium['standalone_resource_npv_after_tax_usd']<medium['resource_npv_before_tax_usd']
    assert small['resource_npv_before_tax_usd']<0 and weak['resource_npv_before_tax_usd']<-30e6
    assert medium['confirmed_eligible_area_m2']==0 and medium['additional_land_opportunity_cost_usd'] is None
    old=read('integrated',OUT.parent/'financing-redesign')
    red=read('integrated_rental_medium',OUT.parent/'financing-redesign')
    assert red['metrics']['total_original_rail_energy_factory_capital_usd']==old['metrics']['total_original_rail_energy_factory_capital_usd']
    assert red['metrics']['allocated_liquidity_cap_iqd']==old['metrics']['allocated_liquidity_cap_iqd']==13e12
    assert red['entities']['retained_rentals']['metrics']['illustrative_bridge_cap_iqd']==0
    assert red['metrics']['government_capital_usd_equivalent']==old['metrics']['government_capital_usd_equivalent']
    assert red['metrics']['chinese_usd_credit']==old['metrics']['chinese_usd_credit']
    assert red['metrics']['total_physical_programme_capital_usd']-old['metrics']['total_physical_programme_capital_usd']==pytest.approx(medium['total_fitout_capital_usd'],abs=.02)
    assert red['appraisal']['consolidated_resource_npv_usd']-old['appraisal']['consolidated_resource_npv_usd']==pytest.approx(medium['resource_npv_before_tax_usd'],abs=.02)
    assert abs(red['appraisal']['consolidation_npv_residual_usd'])<.02
    assert all(r['retained_rental_distribution_to_rail_usd']==r['rail_receipt_from_retained_rentals_usd']==0 for r in red['intercompany_monthly'])
    for entity in old['entities']:assert red['entities'][entity]==old['entities'][entity]
    portfolio=read('medium')
    for v in red['entities']['retained_rentals']['loan_vintages']:
        if v['instrument']=='bank_credit':
            latest=max(p['handover_month'] for p in portfolio['cohorts'] if p['build_first_month']<=v['draw_month']<=p['build_last_month'])
            assert v['first_principal_month']>=latest


def test_holding_rental_costs_and_tax_are_counted_once():
    base=read('primary_1000m',OUT.parent/'equity');rental=read('rental_medium_1000m',OUT.parent/'equity');m=read('medium')['metrics']
    assert rental['metrics']['government_capital_usd']==base['metrics']['government_capital_usd']
    assert rental['metrics']['chinese_credit_usd']==base['metrics']['chinese_credit_usd']
    assert rental['metrics']['government_ownership']==base['metrics']['government_ownership']
    assert rental['metrics']['primary_gross_equity_usd']==base['metrics']['primary_gross_equity_usd']
    assert rental['metrics']['total_capital_usd']-base['metrics']['total_capital_usd']==pytest.approx(m['total_fitout_capital_usd'],abs=.02)
    assert rental['metrics']['resource_npv_after_land_usd']-base['metrics']['resource_npv_after_land_usd']==pytest.approx(m['resource_npv_before_tax_usd'],abs=.02)
    # Positive separate-business floor means the added business's standalone
    # cash tax equals the incremental group cash tax, without a second deduction.
    assert (rental['metrics']['corporate_cash_tax_iqd']-base['metrics']['corporate_cash_tax_iqd'])/1300==pytest.approx(m['standalone_cash_tax_usd'],abs=.02)
    for r in rental['monthly']:
        assert r['rental_restricted_deposit_cash_iqd']==r['rental_tenant_deposit_liability_iqd']
    for v in rental['loan_vintages']:
        if v['instrument']!='chinese_export_credit':assert v['first_contractual_principal_month']>=max(p['handover_month'] for p in read('medium')['cohorts'])


def test_terminal_cash_is_an_independent_unapproved_diagnostic():
    c=read('primary_1000m',OUT.parent/'equity');e=c['terminal_cash_sensitivity'];last=c['monthly'][-1]
    assert e['actual_company_distribution_iqd']==0 and e['asset_sale_usd']==0 and not e['guaranteed_redemption']
    assert e['cash_available_after_nonsecurity_liabilities_iqd']==pytest.approx(last['closing_cash_iqd'],abs=.02)
    private=e['shareholder_returns']['iraqi_private']
    assert private['equity_irr_with_terminal_cash']==pytest.approx(.04215653168778821)
    assert c['shareholder_returns']['iraqi_private']['equity_irr']==pytest.approx(.029965700682548113)
    assert sum(v['hypothetical_terminal_cash_iqd'] for v in e['shareholder_returns'].values())==pytest.approx(last['closing_cash_iqd'])
    failed=read('failed_later_primary',OUT.parent/'equity')['terminal_cash_sensitivity']
    assert failed['status']=='unavailable-incomplete-or-unfunded'
    assert failed['cash_available_after_nonsecurity_liabilities_iqd']==0


def test_coverage_policy_can_distribute_with_debt_without_breaking_reserves():
    config=tomllib.loads((ROOT/'lib/templates/baghdad-equity.toml').read_text())
    config['model'].update(founder_fraction=1.,founder_tranches=1)
    funding=city_funding_config(tomllib.loads((ROOT/'lib/templates/iraq-funding.toml').read_text()),'baghdad')
    options=tomllib.loads((ROOT/'lib/templates/baghdad-finance-options.toml').read_text())
    rows=[]
    for month in range(121):
        capital=1e9 if month==0 else 0.;income=20e6 if 1<=month<120 else 0.;opex=5e6 if income else 0.
        rows.append(dict(month=month,physical_capital_usd=capital,original_capital_usd=capital,imported_capital_usd=0.,
            government_capital_usd=.25*capital,government_usd_cash=0.,revenue_usd=income,opex_usd=opex,
            property_build_usd=0.,property_sales_usd=0.,property_transaction_cost_usd=0.,rail_capital_usd=capital,
            train_capital_usd=0.,solar_capital_usd=0.,factory_capital_usd=0.,factory_warranty_cash_usd=0.,internal_rights_tax_cost_usd=0.,
            tax_operating_bases_usd=dict(rail=income-opex,energy=0.,factory=0.,development=0.)))
    inputs=dict(rows=rows,phases=[dict(line='test',opening_month=1,weight=1.)],factory_ready_month=1,
        factory_close_month=30,land_opportunity_usd=0.,land_opportunity_month=0,replaced_subsidiary_equity_iqd=0.)
    base=simulate_equity(inputs,config,funding,options,100e6)
    cov=simulate_equity(inputs,config,funding,options,100e6,distribution_policy='coverage-and-reserves')
    paid_with_debt=[r for r in cov['monthly'] if r['total_dividend_iqd']>0 and sum(r[n+'_closing_balance_native'] for n in ('bank_credit','domestic_bonds'))>0]
    assert paid_with_debt and cov['metrics']['first_dividend_month']<base['metrics']['first_dividend_month']
    for r in paid_with_debt:
        assert r['coverage_dividend_gate'] and r['trailing_dscr']>=1.3 and r['forward_dscr']>=1.3
        assert r['retained_profit_iqd']>0 and r['closing_dsra_iqd']>0
        assert r['closing_cash_iqd']>=r['closing_tax_payable_iqd']-.02
        assert r['indicative_liabilities_to_book_equity']<=3.+1e-9
        assert r['trailing_dscr']==pytest.approx(r['trailing_cfads_iqd']/r['trailing_scheduled_service_iqd'])


def test_invalid_unit_access_and_uncommitted_money_rejected(config):
    c=deepcopy(config);c['geometry']['unit_internal_depth_m']=7
    with pytest.raises(ValueError):validate(c)
    c=deepcopy(config);c['model']['additional_government_cash_usd']=100
    with pytest.raises(ValueError):validate(c)


def test_sources_outputs_and_deposit_cash_hashes_are_complete():
    s=read('summary')
    for base,key in ((ROOT,'sources_sha256'),(OUT,'outputs_sha256')):
        for path,sha in s[key].items():assert hashlib.sha256((base/path).read_bytes()).hexdigest()==sha,path
    assert not s['operational_release'] and not s['commercial_eligibility_accepted']
