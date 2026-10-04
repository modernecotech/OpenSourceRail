#!/usr/bin/env python3
"""Reproducible Baghdad financing alternatives, entity ledgers and consolidation.

All new commercial prices, land areas, finance and equity are explicit scenarios.
No assumed money is described as committed; internal transfers cancel exactly.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from copy import deepcopy
import csv
import gzip
import hashlib
import html
import json
import math
from pathlib import Path
import sys
import tomllib

from baghdad_delivery_stress import ROOT, CITY, schedule, finance
from baghdad_funding_analysis import CORE, capital_projection, simulate
sys.path.insert(0, str(ROOT / 'design/city-generation/src'))
from osr_scenario.iraq_finance import city_funding_config
from osr_scenario.network_readme import compute_stats, _energy_plan

OUT = CITY / 'engineering/financing-redesign'
NAMES = (*CORE, 'green_bonds')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_csv(path, rows):
    if not rows:
        return
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)

def npv(flows, rate):
    return sum(value / (1 + rate) ** (month / 12) for month, value in flows)

def indexed_projection(contracts, inputs, settings, risk):
    rows = capital_projection(contracts, inputs['config'], set(inputs['options']['green']['candidate_buckets']))
    if settings.get('capital_escalation'):
        for month, row in rows.items():
            factor = (1 + risk['downside']['capital_escalation_annual']) ** (max(0, month) / 12)
            for key in row:
                row[key] *= factor
    return rows

def opening_terms(capital, contracts, task_lines, phases, config, redesign, *, insured=False, factory=False):
    """Cohorts drawn in a month use the latest associated asset opening.

    This is conservative aggregation, not an assertion of per-line legal loans.
    Shared system/factory contracts use the latest network opening unless the
    factory's own production start is supplied as its one financed phase.
    """
    openings = {p['line']: p['opening_month'] for p in phases}
    fallback = max(openings.values())
    cohort = defaultdict(list)
    for contract in contracts:
        line = task_lines.get(contract.get('manufacturing_uid'), '')
        opening = openings.get(line, fallback)
        for month in capital_projection([contract], config, set()):
            cohort[month].append(opening)
    result = {}
    for month in capital:
        opening = max(cohort.get(month, [fallback]))
        grace = max(0, opening - month - 1)
        result[month] = {}
        for name, count in (('bank_credit', 84 if factory else redesign['model']['bank_amortisation_months']),
                            ('domestic_bonds', redesign['model']['bond_amortisation_months'])):
            result[month][name] = dict(grace_months_from_draw=grace, repayment_months=count)
        if insured:
            limit = redesign['insured_green']['maximum_total_tenor_months']
            if grace >= limit:
                raise ValueError('insured grace leaves no amortisation within coverage')
            result[month]['green_bonds'] = dict(grace_months_from_draw=grace, repayment_months=limit-grace)
    return result

def insured_options(options, redesign):
    result = deepcopy(options)
    terms = redesign['insured_green']
    result['green'].update(blended_rate=terms['illustrative_coupon'],
        annual_guarantee_fee=terms['illustrative_annual_insurance_fee']+terms['illustrative_annual_currency_conversion_cost'],
        arrangement_fee=terms['arrangement_fee'], blended_grace_months=0,
        blended_repayment_months=terms['maximum_total_tenor_months'])
    result['additional_sources']['climate_capital_grant_usd'] = terms['climate_grant_usd']
    return result

def commitment_fees(operating, capital, config):
    for op in operating:
        month = op['month']
        cohort = sorted(m for m, r in capital.items() if m // 12 == month // 12 and r.get('imports', 0) > 0)
        op['chinese_commitment_fee_usd'] = (sum(.5*capital[m]['imports'] for m in cohort if m > month)
            * config['chinese_export_credit']['undrawn_commitment_fee']/12 if cohort and month >= cohort[0] else 0.)

def pooled(inputs, phases, task_lines, redesign, *, linked=False, rights=False, insured=False):
    config, options = deepcopy(inputs['config']), deepcopy(inputs['options'])
    capital, operating = deepcopy(inputs['capital']), deepcopy(inputs['operating'])
    if rights:
        options['additional_sources']['net_development_rights_usd'] = redesign['development']['net_rights_usd']
    if insured:
        options = insured_options(options, redesign)
    terms = opening_terms(capital, inputs['contracts']+inputs['factory_contracts'], task_lines, phases,
                          config, redesign, insured=insured) if linked else None
    case = simulate(capital, operating, config, options, green='blended', extras=True,
        bridge_rate=options['liquidity']['concessional_annual_rate'],
        bridge_fee=options['liquidity']['concessional_draw_fee'], repayment_policy='cost_priority', draw_terms=terms)
    rate = (1+config['model']['discount_rate'])*(1+options['fares']['general_price_inflation'])-1
    core = npv([(r['month'], r['revenue_usd']-r['opex_usd']-capital.get(r['month'], {}).get('capex', 0)) for r in operating], rate)
    fx = config['model']['iqd_per_usd']
    case['appraisal'] = dict(core_unlevered_npv_usd=core, nominal_discount_rate=rate,
        rail_recipient_npv_with_targets_usd=core+npv([(r['month'], (r['net_rights_receipts_iqd']+r['incremental_net_receipts_iqd']+r['climate_capital_grant_iqd'])/fx) for r in case['monthly']], rate),
        consolidated_resource_npv_usd=None,
        consolidation_status='Developer resource costs/receipts not modelled in pooled rights-only sensitivity; not a consolidated property appraisal')
    return case

def entity_operating(inputs, phases):
    rows = [dict(month=r['month'], revenue_usd=0., opex_usd=0., fare_revenue_usd=0., nonfare_revenue_usd=0.,
                 factory_debt_service_usd=0., factory_reserve_usd=0., chinese_commitment_fee_usd=0.) for r in inputs['operating']]
    rows[0]['phases'] = deepcopy(phases)
    return rows

def empty_capital():
    return dict(capex=0., imports=0., candidate_capex=0., candidate_imports=0.)

def split_inputs(inputs, phases, task_lines, design, scenario, city_finance, redesign, risk, settings, *, downside=False, availability=False, ppa_tariff=None):
    """Four borrowers, same railway capital budgets; additional property separate.

    Train invoices fund rail CAPEX and are receipts to factory. Factory buys the
    same priced resources one month earlier. Ownership never deletes resources.
    """
    config, options = deepcopy(inputs['config']), insured_options(inputs['options'], redesign)
    config['capital_sources'] = dict(government_share=.25, chinese_import_share=.5,
        government_import_share=.5, residual_bond_share=.75)
    fx = config['model']['iqd_per_usd']
    capital = dict(rail=deepcopy(inputs['capital']))
    solar_contracts = [c for c in inputs['contracts'] if c['bucket']=='solar_plant']
    train_contracts = [c for c in inputs['contracts'] if c['bucket']=='rolling_stock']
    capital['energy'] = indexed_projection(solar_contracts, inputs, settings, risk)
    capital['factory'] = indexed_projection(inputs['factory_contracts'], inputs, settings, risk)
    train = indexed_projection(train_contracts, inputs, settings, risk)
    for month, row in capital['rail'].items():
        row.pop('factory_capex', None); row.pop('factory_imports', None)
        for entity in ('energy', 'factory'):
            for key, amount in capital[entity].get(month, {}).items():
                row[key] -= amount
        if min(row.values()) < -.05:
            raise ValueError('capital partition below zero')
    for entity in ('energy', 'factory'):
        fraction = redesign[entity]['private_equity_fraction']
        for row in capital[entity].values():
            row['private_equity'] = fraction*row['capex']
            row['candidate_private_equity'] = fraction*row['candidate_capex']
    programme_capital = sum(r['capex'] for rows in capital.values() for r in rows.values())
    source_capital = sum(r['capex'] for r in inputs['capital'].values())
    if abs(programme_capital-source_capital) > .02:
        raise ValueError('ownership partition changes original capital')
    op = {entity: entity_operating(inputs, phases) for entity in ('rail', 'energy', 'factory', 'development')}
    op['rail'] = deepcopy(inputs['operating'])
    # No old factory service/reserve remains embedded in the rail-company ledger.
    for row in op['rail']:
        row['factory_debt_service_usd'] = row['factory_reserve_usd'] = 0.
    energy_plan = _energy_plan(design, scenario, compute_stats(design, scenario, 0))
    annual_kwh = energy_plan.pre_plant_grid_import_kwh
    annual_solar_maintenance = city_finance['annual_opex_usd']['components']['solar_plant_maintenance']
    opex_growth = risk['downside']['opex_escalation_annual'] if settings.get('higher_opex') else options['fares']['opex_inflation']
    tariff = ppa_tariff if ppa_tariff is not None else redesign['energy']['ppa_reference_iqd_per_kwh']
    first_open, full_open = min(p['opening_month'] for p in phases), max(p['opening_month'] for p in phases)
    end_operation = full_open+config['model']['operating_years']*12
    first_train, last_train = min(train), max(train)
    factory_close = last_train+redesign['factory']['warranty_tail_months']
    factory_phase = [dict(line='factory', opening_month=first_train, weight=1.)]
    op['factory'][0]['phases'] = factory_phase
    d = redesign['development']
    delay = redesign['downside']['development_delay_months'] if downside else 0
    sale_first, sale_last = d['sale_first_month']+delay, d['sale_last_month']+delay
    op['development'][0]['phases'] = [dict(line='development', opening_month=sale_first, weight=1.)]
    capital['development'] = {}
    physical_property = d['station_candidates']*d['land_area_m2_per_site']*d['floor_area_ratio']*d['building_cost_usd_per_m2']
    rights_total = d['net_rights_usd']*(redesign['downside']['rights_receipts_multiplier'] if downside else 1.)
    rights_by_month = {d['rights_first_month']+delay+6*i: rights_total/d['rights_tranches'] for i in range(d['rights_tranches'])}
    # Build 36..71, sales 60..96 at reference. All payments in IQD at reference FX.
    build_start, build_end = 36+delay, 71+delay
    property_build = {}
    for month in range(build_start, build_end+1):
        amount = physical_property/(build_end-build_start+1)
        if downside:
            amount *= (1+risk['downside']['capital_escalation_annual'])**(month/12)
        property_build[month] = amount
    for month in set(property_build)|set(rights_by_month):
        amount = property_build.get(month, 0.)+rights_by_month.get(month, 0.)
        capital['development'][month] = {**empty_capital(), 'capex': amount, 'private_equity': d['private_equity_fraction']*amount}
    transfers, resource_rows = [], []
    cumulative_train_receipts = 0.
    sales_total = d['gross_sale_receipts_usd']*(redesign['downside']['development_receipts_multiplier'] if downside else 1.)
    for month, source in enumerate(inputs['operating']):
        active = first_open <= month < end_operation
        opened = sum(p['weight'] for p in phases if month >= p['opening_month']) if active else 0.
        index = (1+opex_growth)**(month//12)
        removed_maintenance = annual_solar_maintenance/12*(.25+.75*opened)*index if active else 0.
        energy_renewal = sum(r['capex'] for r in capital['energy'].values())*redesign['energy']['additional_annual_renewal_fraction']/12*opened*index
        energy_cost = removed_maintenance+energy_renewal
        ppa = annual_kwh/12*opened*tariff/fx*(1+redesign['energy']['ppa_indexation'])**(month//12)
        invoice = train.get(month, {}).get('capex', 0.)
        # Original train resource costs already include manufacturing wages,
        # QA, ordinary overhead and warranty. Additional fee funds plant return.
        fee = invoice*redesign['factory']['capacity_fee_usd_per_train']/1_680_000*(1+options['fares']['general_price_inflation'])**(month//12)
        manufacturing = train.get(month+redesign['factory']['manufacturing_cash_lead_months'], {}).get('capex', 0.)
        cumulative_train_receipts += invoice
        warranty_cash = cumulative_train_receipts*redesign['factory']['warranty_retained_cash_fraction'] if month <= factory_close else 0.
        custodian = 0.
        if last_train < month <= factory_close:
            custodian = (redesign['factory']['caretaker_fte']*inputs['labour_cost_per_fte_usd']+sum(r['capex'] for r in capital['factory'].values())*redesign['factory']['annual_carrying_fraction'])/12*index
        rights = rights_by_month.get(month, 0.)
        gross_sales = sales_total/(sale_last-sale_first+1) if sale_first <= month <= sale_last else 0.
        sales_cost = gross_sales*d['sale_transaction_fraction']
        public = (redesign['public_support']['annual_availability_payment_usd']/12*opened
                  *(1+redesign['public_support']['indexation'])**(month//12) if availability else 0.)
        op['rail'][month]['revenue_usd'] += rights+public
        op['rail'][month]['nonfare_revenue_usd'] += rights # Public payments separately disclosed below.
        op['rail'][month]['opex_usd'] += ppa+fee-removed_maintenance
        op['energy'][month].update(revenue_usd=ppa, nonfare_revenue_usd=ppa, opex_usd=energy_cost)
        op['factory'][month].update(revenue_usd=invoice+fee, nonfare_revenue_usd=invoice+fee,
            opex_usd=manufacturing+custodian, restricted_working_capital_usd=warranty_cash)
        op['development'][month].update(revenue_usd=gross_sales, nonfare_revenue_usd=gross_sales, opex_usd=sales_cost)
        consolidated = (source['revenue_usd']-source['opex_usd']-inputs['capital'].get(month, {}).get('capex', 0.)
            +invoice-manufacturing-energy_renewal-custodian+gross_sales-sales_cost-property_build.get(month, 0.))
        entity_resources = sum(op[name][month]['revenue_usd']-op[name][month]['opex_usd']-capital[name].get(month, {}).get('capex', 0.) for name in op)-public
        residual = entity_resources-consolidated
        if abs(residual) > .05:
            raise ValueError('internal transfers fail to cancel')
        transfers.append(dict(month=month, ppa_rail_payment_usd=ppa, ppa_energy_receipt_usd=ppa,
            train_rail_capital_invoice_usd=invoice, train_factory_receipt_usd=invoice,
            capacity_rail_payment_usd=fee, capacity_factory_receipt_usd=fee,
            rights_developer_capital_payment_usd=rights, rights_rail_receipt_usd=rights,
            government_availability_payment_usd_equivalent=public, government_payment_currency='IQD',
            factory_resource_purchase_usd=manufacturing, factory_warranty_locked_cash_usd=warranty_cash,
            energy_additional_renewal_spend_usd=energy_renewal,
            physical_property_build_usd=property_build.get(month, 0.), gross_property_sales_usd=gross_sales,
            property_transaction_cost_usd=sales_cost, internal_transfer_residual_usd=residual))
        resource_rows.append(dict(month=month, consolidated_unlevered_cash_usd=consolidated,
                                  consolidated_recipient_cash_with_public_support_usd=consolidated+public))
    entities = {}
    for name in op:
        entity_config, entity_options = deepcopy(config), deepcopy(options)
        entity_options['additional_sources'].update(climate_capital_grant_usd=0., net_development_rights_usd=0., incremental_net_local_receipts_annual_usd=0.)
        entity_options['liquidity']['illustrative_cap_iqd'] *= redesign['liquidity_allocation'][name+'_fraction']
        if name == 'development':
            entity_config['capital_sources'].update(government_share=0., chinese_import_share=0.,government_import_share=0., residual_bond_share=0.)
        if name == 'factory':
            entity_config['capital_sources']['residual_bond_share'] = 0.
        commitment_fees(op[name], capital[name], entity_config)
        contracts = (inputs['contracts'] if name == 'rail' else solar_contracts if name == 'energy' else inputs['factory_contracts'] if name == 'factory' else [])
        if name == 'rail':
            contracts = [c for c in contracts if c['bucket']!='solar_plant']
        entity_phases = op[name][0]['phases']
        terms = opening_terms(capital[name], contracts, task_lines, entity_phases, entity_config, redesign, insured=True, factory=name=='factory')
        entities[name] = simulate(capital[name], op[name], entity_config, entity_options,
            green=None if downside or name in ('factory', 'development') else 'blended', extras=False,
            bridge_rate=risk['downside']['gap_credit_rate'] if downside else entity_options['liquidity']['concessional_annual_rate'],
            bridge_fee=risk['downside']['gap_credit_draw_fee'] if downside else entity_options['liquidity']['concessional_draw_fee'],
            repayment_policy='cost_priority', draw_terms=terms)
        entities[name]['metrics']['sources_capital_include_internal_rights'] = name=='development'
    for name, ledger in entities.items():
        m = ledger['metrics']
        equity = m['private_equity_iqd']/fx
        m['terminal_private_equity_cash_return_usd'] = m['terminal_cash_iqd']/fx
        m['equity_cash_recovered_at_zero_hurdle'] = (m['terminal_cash_iqd']/fx >= equity
            and m['uncovered_support_iqd'] < .02*fx and m['terminal_supplemental_balance_iqd'] < .02*fx
            and all(v < .02 for v in m['core_final_balances_native'].values())) if equity else None
        if name in ('factory', 'development'):
            distribution_month = factory_close+1 if name=='factory' else sale_last+1
            closing = ledger['monthly'][distribution_month]
            unpaid = closing['closing_liquidity_debt_iqd']/fx+sum(closing[key+'_closing_balance_native']/(1 if key=='chinese_export_credit' else fx) for key in NAMES)
            distribution = max(0., closing['closing_project_cash_iqd']/fx-unpaid)
            equity_flows = [(r['month'], -r.get('private_equity_iqd', 0.)/fx) for r in ledger['monthly']]
            equity_flows.append((distribution_month, distribution))
            m['illustrative_equity_hurdle_rate'] = .15
            m['equity_npv_at_15pct_orderbook_or_sale_close_usd'] = npv(equity_flows, .15)
            m['equity_distribution_month_assumption'] = distribution_month
            m['equity_distribution_assumption_usd'] = distribution
            m['equity_distribution_status'] = 'Diagnostic of cash at final contract/warranty close net of unpaid debt; missing funding must be committed; no dividend authorised'
    rate = (1+config['model']['discount_rate'])*(1+options['fares']['general_price_inflation'])-1
    original_npv = npv([(r['month'], r['revenue_usd']-r['opex_usd']-inputs['capital'].get(r['month'], {}).get('capex', 0.)) for r in inputs['operating']], rate)
    land = d['station_candidates']*d['land_area_m2_per_site']*d['land_opportunity_usd_per_m2']
    land_pv = land/(1+rate)**((d['rights_first_month']+delay)/12)
    core_resource = npv([(r['month'], r['consolidated_unlevered_cash_usd']) for r in resource_rows], rate)
    public_cash_pv = npv([(r['month'], r['government_usd_cash']+r['government_iqd_cash']/fx) for e in entities.values() for r in e['monthly']], rate)
    public_support_pv = npv([(r['month'], r['government_availability_payment_usd_equivalent']) for r in transfers], rate)
    entity_npvs = {name: npv([(r['month'], r['revenue_usd']-r['opex_usd']-capital[name].get(r['month'], {}).get('capex', 0.)) for r in op[name]], rate) for name in op}
    metrics = dict(total_original_rail_energy_factory_capital_usd=source_capital,
        total_additional_property_build_usd=sum(property_build.values()),
        total_physical_programme_capital_usd=source_capital+sum(property_build.values()),
        total_private_equity_iqd=sum(e['metrics']['private_equity_iqd'] for e in entities.values()),
        government_capital_usd_equivalent=sum(e['metrics']['government_capital_usd_equivalent'] for e in entities.values()),
        government_cash_share_of_original_capital=sum(e['metrics']['government_capital_usd_equivalent'] for e in entities.values())/source_capital,
        government_usd_cash=sum(r['government_usd_cash'] for e in entities.values() for r in e['monthly']),
        chinese_usd_credit=sum(e['metrics']['china_capital_usd'] for e in entities.values()),
        total_bond_face_iqd=sum(e['metrics']['ordinary_bonds_iqd']+e['metrics']['green_bonds_iqd'] for e in entities.values()),
        total_bank_capital_iqd=sum(e['metrics']['bank_capital_iqd'] for e in entities.values()),
        allocated_liquidity_cap_iqd=sum(e['metrics']['illustrative_bridge_cap_iqd'] for e in entities.values()),
        peak_aggregate_liquidity_iqd=max(sum(e['monthly'][m]['closing_liquidity_debt_iqd'] for e in entities.values()) for m in range(len(resource_rows))),
        sum_independent_company_peak_liquidity_iqd=sum(e['metrics']['peak_supplemental_balance_iqd'] for e in entities.values()),
        uncovered_support_iqd=sum(e['metrics']['uncovered_support_iqd'] for e in entities.values()),
        terminal_supplemental_balance_iqd=sum(e['metrics']['terminal_supplemental_balance_iqd'] for e in entities.values()),
        total_finance_interest_and_fees_usd=sum(e['metrics']['total_finance_interest_and_fees_usd'] for e in entities.values()),
        net_rights_receipts_usd=rights_total, additional_rights_vs_original_usd=rights_total-300_000_000,
        additional_annual_receipts_targets_usd=0., climate_grant_usd=0., future_city_order_revenue_usd=0.,
        surplus_power_revenue_usd=0., maximum_internal_transfer_residual_usd=max(abs(r['internal_transfer_residual_usd']) for r in transfers))
    cleared = [e['metrics']['all_debt_cleared_month'] for e in entities.values()]
    metrics['all_company_debt_cleared_month_conditional_on_missing_funding'] = max(cleared) if all(m is not None for m in cleared) else None
    metrics['debt_clearance_month_without_unfunded_support'] = metrics['all_company_debt_cleared_month_conditional_on_missing_funding'] if metrics['uncovered_support_iqd'] < .02*fx else None
    appraisal = dict(core_unlevered_npv_usd=original_npv, nominal_discount_rate=rate,
        rail_entity_unlevered_npv_with_internal_payments_and_rights_usd=entity_npvs['rail'],
        entity_unlevered_npvs_usd=entity_npvs, consolidated_resource_npv_usd=core_resource,
        consolidated_resource_npv_after_land_opportunity_usd=core_resource-land_pv,
        public_capital_cash_pv_usd=public_cash_pv, public_land_opportunity_pv_usd=land_pv,
        additional_public_availability_payment_pv_usd=public_support_pv,
        public_contribution_pv_usd=public_cash_pv+land_pv+public_support_pv,
        consolidated_recipient_npv_with_public_capital_and_support_usd=core_resource+public_cash_pv+public_support_pv,
        # In a public+private resource appraisal, transfers from government cancel.
        consolidation_npv_residual_usd=sum(entity_npvs.values())-public_support_pv-core_resource,
        guarantee_exposure_usd=None, guarantee_status='Not quantified; no guarantee commitment/appropriation/insured eligibility established',
        tax_status='Pre-tax scenario; tax, duties, VAT relief, lease law and SPV distributions require Iraqi advice')
    return dict(status='illustrative-uncommitted-no-financial-close', financing_committed=False,
        metrics=metrics, appraisal=appraisal, entities=entities, intercompany_monthly=transfers,
        consolidated_monthly=resource_rows, ppa=dict(reference_iqd_per_kwh=tariff, annual_planning_purchased_kwh=annual_kwh,
            full_network_annual_payment_at_reference_prices_usd=annual_kwh*tariff/fx,
            time_resolved_generation_demonstrated=False, buyer_signed=False, surplus_sales_usd=0.),
        factory=dict(backlog_trainsets=831, baseline_price_usd_per_train=1_680_000,
            additional_capacity_fee_usd_per_train=redesign['factory']['capacity_fee_usd_per_train'],
            manufacturing_resource_cost_usd=sum(r['factory_resource_purchase_usd'] for r in transfers),
            train_invoice_total_usd=sum(r['train_rail_capital_invoice_usd'] for r in transfers),
            working_capital_lead_months=redesign['factory']['manufacturing_cash_lead_months'],
            warranty_restricted_cash_peak_usd=max(r['factory_warranty_locked_cash_usd'] for r in transfers),
            warranty_cash_release_month=factory_close+1,
            balances_at_orderbook_close_native={key:entities['factory']['monthly'][factory_close+1][key+'_closing_balance_native'] for key in NAMES},
            future_order_revenue_usd=0., residual_sale_usd=0.),
        development=dict(candidate_count=d['station_candidates'], land_area_m2=d['station_candidates']*d['land_area_m2_per_site'],
            floor_area_m2=d['station_candidates']*d['land_area_m2_per_site']*d['floor_area_ratio'],
            gross_sale_receipts_usd=sales_total, rights_total_usd=rights_total,
            opportunity_cost_usd=land, opportunity_cost_month=d['rights_first_month']+delay,
            title_verified=False, market_demand_verified=False, independent_valuation_usd=None, sales_contracts_signed=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    if args.check:
        summary = json.loads((OUT/'summary.json').read_text())
        for base, group in ((ROOT, 'sources_sha256'), (OUT, 'outputs_sha256')):
            for rel, sha in summary[group].items():
                if digest(base/rel) != sha:
                    raise ValueError('Stale financing redesign '+rel)
        print('Financing redesign source and output hashes pass'); return
    paths = [Path(__file__), ROOT/'tools/automation/baghdad_funding_analysis.py', ROOT/'tools/automation/baghdad_delivery_stress.py',
        ROOT/'lib/templates/baghdad-financing-redesign.toml', ROOT/'lib/templates/iraq-funding.toml', ROOT/'lib/templates/baghdad-finance-options.toml',
        ROOT/'lib/templates/baghdad-delivery-risk.toml', CITY/'engineering/finance/summary.json', CITY/'engineering/factory/summary.json',
        CITY/'engineering/delivery-risk/summary.json', CITY/'engineering/qualification/summary.json',
        CITY.parent/'finance/baghdad-programme.json', CITY/'operations/baghdad-operations.json.gz', CITY/'design.toml', CITY/'baghdad.toml',
        ROOT/'design/city-generation/src/osr_scenario/iraq_finance.py',ROOT/'design/city-generation/src/osr_scenario/network_readme.py',
        ROOT/'tools/automation/baghdad_viaduct_rentals.py',ROOT/'lib/templates/baghdad-viaduct-rentals.toml',
        CITY/'engineering/viaduct-rentals/summary.json']
    sources = {p.relative_to(ROOT).as_posix(): digest(p) for p in paths}
    def load(path): return json.loads(path.read_text())
    redesign = tomllib.loads(paths[3].read_text()); config = city_funding_config(tomllib.loads(paths[4].read_text()), 'baghdad')
    options, risk = tomllib.loads(paths[5].read_text()), tomllib.loads(paths[6].read_text())
    city_finance, factory, stress, programme = load(paths[7]), load(paths[8]), load(paths[9]), load(paths[11])
    payload = json.loads(gzip.decompress(paths[12].read_bytes())); city_finance['_contracts'] = payload['project_twin']['budget_contracts']
    design, scenario = tomllib.loads(paths[13].read_text()), tomllib.loads(paths[14].read_text())
    for name in ('energy', 'factory'):
        if not 0 <= redesign[name]['private_equity_fraction'] <= .25:
            raise ValueError('equity exceeds available domestic capital')
    if abs(sum(redesign['liquidity_allocation'].values())-1) > 1e-10:
        raise ValueError('liquidity allocation must total one')
    if redesign['insured_green']['maximum_total_tenor_months'] > 180:
        raise ValueError('insured tenor exceeds 15 years')
    task_lines = {r['manufacturing_uid']:r['line'] for r in payload['manufacturing_tasks']}
    context = config, options, programme, city_finance, factory, risk
    def model_input(name):
        settings = deepcopy(stress['cases'][name]['settings']); settings['export_model_inputs'] = True
        delivery = schedule(payload['manufacturing_tasks'], factory, settings)
        result = finance(delivery, settings, context)
        result['model_inputs']['labour_cost_per_fte_usd'] = programme['comparison']['operating_labour_annual_iqd']/programme['comparison']['operating_fte']/config['model']['iqd_per_usd']
        return result['model_inputs'], delivery['phases'], settings, result['metrics']
    inputs, phases, settings, baseline_metrics = model_input('calendar_baseline')
    if abs(baseline_metrics['peak_supplemental_balance_iqd']-stress['cases']['calendar_baseline']['metrics']['peak_supplemental_balance_iqd']) > .02:
        raise ValueError('baseline input reconstruction differs')
    cases = dict(reference=pooled(inputs, phases, task_lines, redesign),
        opening_linked_debt=pooled(inputs, phases, task_lines, redesign, linked=True),
        development_rights_1bn=pooled(inputs, phases, task_lines, redesign, linked=True, rights=True),
        insured_15year_debt=pooled(inputs, phases, task_lines, redesign, linked=True, insured=True))
    for name, kwargs in (('integrated', {}), ('integrated_low_ppa', {'ppa_tariff':redesign['energy']['ppa_low_iqd_per_kwh']}),
                         ('integrated_high_ppa', {'ppa_tariff':redesign['energy']['ppa_high_iqd_per_kwh']}),
                         ('integrated_public_availability', {'availability':True})):
        cases[name] = split_inputs(inputs, phases, task_lines, design, scenario, city_finance, redesign, risk, settings, **kwargs)
    weak_inputs, weak_phases, weak_settings, _ = model_input('joint_downside')
    cases['integrated_joint_downside'] = split_inputs(weak_inputs, weak_phases, task_lines, design, scenario, city_finance, redesign, risk, weak_settings, downside=True)
    rentals=tomllib.loads((ROOT/'lib/templates/baghdad-viaduct-rentals.toml').read_text())
    for name in ('small','medium','medium_downside'):
        portfolio=load(CITY/'engineering/viaduct-rentals'/f'{name}.json')
        cases['integrated_rental_'+name]=retained_entity(cases['integrated'],portfolio,config,options,rentals)
    OUT.mkdir(parents=True, exist_ok=True)
    output_paths = []
    def save(name, value):
        path = OUT/name; path.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n'); output_paths.append(path)
    def csvout(name, rows):
        if rows: write_csv(OUT/name, rows); output_paths.append(OUT/name)
    for name, case in cases.items():
        save(name+'.json', case)
        if 'entities' in case:
            for entity, ledger in case['entities'].items():
                csvout(name+'-'+entity+'-monthly.csv', ledger['monthly'])
                csvout(name+'-'+entity+'-six-months.csv', ledger['semiannual'])
                csvout(name+'-'+entity+'-loan-vintages.csv', ledger.get('loan_vintages', []))
            csvout(name+'-consolidated-monthly.csv', case['consolidated_monthly'])
            csvout(name+'-intercompany-monthly.csv', case['intercompany_monthly'])
        else:
            csvout(name+'-monthly.csv', case['monthly']); csvout(name+'-six-months.csv', case['semiannual'])
            csvout(name+'-loan-vintages.csv', case.get('loan_vintages', []))
    candidates = sorted(design['stations'], key=lambda s:(s.get('archetype') not in ('interchange', 'interchange-elevated'), s.get('archetype') not in ('major', 'terminal'), s['id']))[:redesign['development']['station_candidates']]
    land_register = [dict(station_id=s['id'], line=s['line'], latitude=s['lat'], longitude=s['lon'], selection_basis='Network archetype proxy only; commercial ranking pending',
        parcel_id=None, legal_owner=None, title_verified=False, encumbrance_search=None, surveyed_area_m2=None, independent_market_value_iqd=None,
        assumed_area_m2=redesign['development']['land_area_m2_per_site'], assumed_floor_area_ratio=redesign['development']['floor_area_ratio'],
        community_displacement_assessed=False, voluntary_land_pooling_agreement=None, developer_interest_evidence=None) for s in candidates]
    save('station-land-register.json', land_register); csvout('station-land-register.csv', land_register)
    workstreams = [
        ('DEBT','Sponsor treasury and Iraqi finance counsel','Indicative IQD lender/bond terms: opening-linked cohorts, separate construction/operation liquidity, contingency, DSRA, fees, prepayment rights and placement proof',15,60),
        ('LAND','Land/title lead and independent valuer','15 candidate areas: title and encumbrances, surveyed parcels, opportunity cost, safeguards, independent valuations, demand and competitive developer expressions',15,75),
        ('ENERGY','Energy procurement lead and lender engineer','Quoted IQD PPA and owner alternative; 8760-hour dispatch/grid imports, metering, replacement schedule, offtaker credit, termination compensation and guarantees',30,75),
        ('FACTORY','Industrial investment lead','831-train-only priced backlog, working capital/warranty, input quotes, labour/QA/overhead reconciliation, private equity terms, tax and post-order closure',30,75),
        ('PHASE','Owner engineer and safety assurance lead','Accept existing first-section package: independent depot, turnbacks, energy, fleet, safety, demand, contingent delivery and contingency costs',15,60),
        ('MODEL','Independent financial reviewer and public sponsor','Reconcile monthly/native ledgers and 6-month placements, entity cash and consolidation, debt tenor/covenants, joint downside, public affordability and funding gates',60,90)]
    revision = hashlib.sha256(json.dumps(sources, sort_keys=True).encode()).hexdigest()
    packages = [dict(id='BAG-EVID-FIN90-'+key, accountable_owner_role=role, named_owner=None, start_day=start, due_day=due,
        day_basis='Days from actual sponsor-approved redesign start; no calendar date assigned', output=output, evidence=None,
        status='not-demonstrated', source_revision=revision, acceptance_rule='Independent signed review of underlying quotes/legal/engineering/valuation evidence; model output alone cannot accept evidence') for key, role, output, start, due in workstreams]
    save('90-day-work-programme.json',dict(work_packages=packages, status='draft-no-evidence', external_contacts_made=False))
    tasks = [dict(subject=p['id']+' — '+p['accountable_owner_role'], status='Open', priority='High', description='<pre>'+html.escape(json.dumps(p,indent=2))+'</pre>') for p in packages]
    save('erpnext-tasks.json',dict(doctype='Task',status='draft-import-package-not-live-records',tasks=tasks))
    csvout('erpnext-task-import.csv',tasks)
    report = report_text(cases, phases, redesign)
    (OUT/'README.md').write_text(report); output_paths.append(OUT/'README.md')
    summary = dict(schema='baghdad-financing-redesign/1', as_of=redesign['model']['as_of'], status='illustrative-financeability-study-not-bankable',
        financing_committed=False, operational_release=False, included_cities=['Baghdad'], source_revision=revision,
        sources_sha256=sources, outputs_sha256={p.name:digest(p) for p in output_paths},
        cases={name:{key:case[key] for key in ('metrics','appraisal')} for name, case in cases.items()},
        evidence_status='All lender terms, equity, title, valuation, PPA, insurance/currency execution and subsidies pending')
    (OUT/'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True)+'\n')
    print('Generated twelve financing alternatives with retained rentals, company/monthly/six-month/vintage ledgers and six ERP drafts')


def retained_entity(baseline,portfolio,config,options,rentals):
    """A fifth ring-fenced borrower, without invented intercompany distributions.

    Security deposits are outside free project cash and matched by liabilities.
    The existing four gap caps stay fixed; this new entity has zero gap capacity.
    """
    if portfolio['status']!='conditional-unverified-retained-portfolio':raise ValueError('Unmapped rental area cannot enter financing')
    case=deepcopy(baseline);m=rentals['model'];cfg=deepcopy(config);opt=deepcopy(options)
    cfg['capital_sources']=dict(government_share=0.,chinese_import_share=0.,government_import_share=0.,residual_bond_share=0.)
    opt['liquidity']['illustrative_cap_iqd']=0.
    cap={r['month']:dict(capex=r['physical_fitout_capital_usd'],imports=0.,candidate_capex=0.,candidate_imports=0.,
        private_equity=r['physical_fitout_capital_usd']*m['private_partner_fitout_equity_fraction']) for r in portfolio['monthly'] if r['physical_fitout_capital_usd']}
    phases=[dict(line=p['line'],opening_month=p['handover_month'],weight=p['lettable_m2']/portfolio['metrics']['target_lettable_m2']) for p in portfolio['cohorts']]
    op=[dict(month=r['month'],revenue_usd=r['rent_collected_usd'],nonfare_revenue_usd=r['rent_collected_usd'],fare_revenue_usd=0.,
        opex_usd=r['landlord_opex_usd']+r['standalone_cash_tax_usd'],factory_debt_service_usd=0.,factory_reserve_usd=0.,chinese_commitment_fee_usd=0.) for r in portfolio['monthly']]
    op[0]['phases']=phases
    terms={month:{'bank_credit':dict(grace_months_from_draw=max(0,max(p['handover_month'] for p in portfolio['cohorts']
        if p['build_first_month']<=month<=p['build_last_month'])-month-1),repayment_months=240)} for month in cap}
    ledger=simulate(cap,op,cfg,opt,extras=False,bridge_rate=opt['liquidity']['concessional_annual_rate'],
        bridge_fee=opt['liquidity']['concessional_draw_fee'],repayment_policy='cost_priority',draw_terms=terms)
    if len(ledger['monthly'])!=len(case['consolidated_monthly']):raise ValueError('Rental/rail horizons do not match')
    for r,p in zip(ledger['monthly'],portfolio['monthly']):
        r.update(tenant_deposit_received_iqd=p['tenant_deposit_received_iqd'],tenant_deposit_refunded_iqd=p['tenant_deposit_refunded_iqd'],
            restricted_deposit_cash_iqd=p['restricted_deposit_cash_iqd'],tenant_deposit_liability_iqd=p['tenant_deposit_liability_iqd'],
            rental_tax_iqd=p['standalone_cash_tax_usd']*1300,rental_refurbishment_iqd=p['refurbishment_usd']*1300)
    ledger['status']='conditional-retained-property-after-rental-tax-no-gap-capacity'
    case['entities']['retained_rentals']=ledger;case['rental_portfolio']=portfolio['metrics']
    for r,p in zip(case['consolidated_monthly'],portfolio['monthly']):
        r['consolidated_unlevered_cash_usd']+=p['unlevered_cash_before_tax_usd']
        r['consolidated_recipient_cash_with_public_support_usd']+=p['unlevered_cash_before_tax_usd']
        r['consolidated_after_rental_cash_tax_usd']=r['consolidated_unlevered_cash_usd']-p['standalone_cash_tax_usd']
    for r in case['intercompany_monthly']:
        r['retained_rental_distribution_to_rail_usd']=0.;r['rail_receipt_from_retained_rentals_usd']=0.
    cm,lm=case['metrics'],ledger['metrics']
    cm['total_physical_programme_capital_usd']+=lm['total_capital_usd'];cm['retained_fitout_capital_usd']=lm['total_capital_usd']
    cm['total_private_equity_iqd']+=lm['private_equity_iqd'];cm['total_bank_capital_iqd']+=lm['bank_capital_iqd']
    cm['uncovered_support_iqd']+=lm['uncovered_support_iqd'];cm['terminal_supplemental_balance_iqd']+=lm['terminal_supplemental_balance_iqd']
    cm['total_finance_interest_and_fees_usd']+=lm['total_finance_interest_and_fees_usd']
    cm['peak_aggregate_liquidity_iqd']=max(sum(e['monthly'][i]['closing_liquidity_debt_iqd'] for e in case['entities'].values()) for i in range(len(op)))
    cm['new_rental_gap_capacity_iqd']=0.;cm['rental_security_deposits_are_income']=False
    a=case['appraisal'];increment=portfolio['metrics']['resource_npv_before_tax_usd']
    a['consolidated_resource_npv_usd']+=increment;a['consolidated_resource_npv_after_land_opportunity_usd']+=increment
    a['consolidated_recipient_npv_with_public_capital_and_support_usd']+=increment
    a['retained_rental_before_tax_incremental_npv_usd']=increment
    a['consolidated_resource_npv_after_rental_tax_usd']=baseline['appraisal']['consolidated_resource_npv_usd']+portfolio['metrics']['standalone_resource_npv_after_tax_usd']
    a['additional_rental_land_opportunity_cost_usd']=None
    a['tax_status']='Original four entities before tax; retained-rental cash includes a separate 15% tax stress; group statutory tax unestablished'
    expected=baseline['appraisal']['consolidated_resource_npv_usd']+increment
    a['consolidation_npv_residual_usd']=npv([(r['month'],r['consolidated_unlevered_cash_usd']) for r in case['consolidated_monthly']],.134)-expected
    return case


def report_text(cases, phases, redesign):
    baseline, integrated, weak = cases['reference'], cases['integrated'], cases['integrated_joint_downside']
    rows = []
    for name, case in cases.items():
        m, a = case['metrics'], case['appraisal']
        peak = m.get('peak_aggregate_liquidity_iqd',m.get('peak_supplemental_balance_iqd',0.))/1e12
        resource = a.get('consolidated_resource_npv_usd')
        rows.append(f"| {name} | {peak:.3f} | {m['uncovered_support_iqd']/1e12:.3f} | {m['terminal_supplemental_balance_iqd']/1e12:.3f} | {m['total_finance_interest_and_fees_usd']/1e9:.3f} | {'n/a' if resource is None else f'{resource/1e9:.3f}'} |")
    entities = '\n'.join(f"| {name} | {e['metrics']['total_capital_usd']/1e6:.3f} | {e['metrics']['private_equity_iqd']/1e9:.3f} | {e['metrics']['peak_supplemental_balance_iqd']/1e12:.3f} | {e['metrics']['uncovered_support_iqd']/1e12:.3f} | {e['metrics']['terminal_supplemental_balance_iqd']/1e12:.3f} |" for name,e in integrated['entities'].items())
    a,m = integrated['appraisal'], integrated['metrics']
    return f'''# Baghdad financing redesign — {redesign['model']['as_of']}

Twelve executable alternatives retain 9 lines, 516.5175 km, 182 stations and 831 six-car trains. Financial close, title, investor equity, insurance eligibility and physical acceptance remain unestablished. The [existing baseline](../../../finance/baghdad-programme.json) remains the planning reference. Conditional full-line openings are {', '.join(str(p['opening_month']) for p in phases)} months; the [independently operable first section](../qualification/README.md) is a separately costed sensitivity, not silently added to these full-network cases.

## Results and what they mean

| Case | Peak aggregate IQD liquidity tn | Cumulative missing IQD funding tn | Terminal IQD gap debt tn | Lifetime interest/fees USD bn eq | Consolidated resource NPV USD bn eq |
| --- | --- | --- | --- | --- | --- |
{chr(10).join(rows)}

**Next financing priority:** obtain opening-linked IQD terms and independently valued station proceeds, then compare quoted PPA prices against continued ownership. The integrated high-PPA structure shifts substantial cash to the energy company while rail remains short; private equity needs an acceptable return as well as debt repayment. The tested property margin improves resource NPV before land cost, but the assumed in-kind land cost more than offsets that improvement. None of these scenarios establishes financial feasibility.

[Summary with exact figures and appraisal definitions](summary.json); every case has a complete JSON model, monthly native-currency CSVs, six-month placements and contractual loan-vintage dates. **Missing funding must be filled before any reported conditional repayment date is credible.** Independently funded entities cannot use another company's cash without a separately approved agreement. Liquidity caps are allocated once: 65% rail, 10% energy, 5% factory and 20% development. The sum is IQD {m['allocated_liquidity_cap_iqd']/1e12:.1f}tn reference; the downside divides the existing IQD 4tn cap in the same proportions.

| Integrated borrower | Capital uses USD m eq | Private equity IQD bn | Peak gap IQD tn | Missing funding IQD tn | Terminal gap IQD tn |
| --- | --- | --- | --- | --- | --- |
{entities}

These are pre-tax sensitivities. Corporate tax, duties, VAT, sponsor equity hurdle rates, dividend restrictions, lender DSCR and termination liabilities need quoted/legal terms. Surplus is swept after monthly OPEX, scheduled debt service, reserve funding and the existing lock-ins/premiums. A positive cash balance or an annuity model does not establish bankability. The factory has no assumed national orders or residual asset sale.

## Opening-linked credit and insured green instruments

Bank amortisation becomes 240 months and ordinary bonds 216 months at the unchanged 9%/8% reference rates. Monthly draw cohorts use the latest opening of the assets included in that cohort; shared contracts use full opening. This conservative aggregation needs actual line-linked facility documents. Interest is **paid throughout grace**, funded by the separate IQD liquidity account if cash is insufficient; no interest is silently forgiven or capitalised. Arrangement/commitment charges, buffer and surplus rights remain priced. Chinese USD loan terms remain unchanged.

Loan-vintage and six-month CSVs show actual draw, first principal and final contractual principal dates. Cheaper/longer debt changes liquidity and finance cost, while core unlevered NPV stays **USD {baseline['appraisal']['core_unlevered_npv_usd']/1e9:.3f}bn**. Core excludes grant, development rights and new net receipt targets.

[ICIEC's official product](https://iciec.isdb.org/wp-content/uploads/2025/10/sukuk-book-2025.pdf) describes sovereign/sub-sovereign sukuk with coverage up to 15 years. The tested insured instrument has **grace plus amortisation capped at 180 months from each draw**, replacing the previous 48+240-month assumption in that sensitivity. A 6% coupon, 0.75% annual insurance and 1% annual IQD conversion/on-lending cost are assumptions, not insurer pricing or proof that an IQD issue is eligible. No climate grant is booked in insured/integrated cases. Obtain written eligibility, binding terms and a priced local-currency route before using an institution's name in funding commitments.

## Station-area partnership and public land

[15 station candidates](station-land-register.csv) are selected only by network archetypes, with actual station IDs/coordinates. Parcel title, legal ownership, survey area, encumbrances, independent values, displacement and developer interest are **null/unverified**. No selection is a claimed commercial valuation. First investigate 10–20 sites through independent market/title/safeguards work and competitive long leases or voluntary pooling.

USD 1bn **total** net development-rights replaces USD 300m; the increase is USD 700m. Six equal tranches begin month 24, every six months. Receipts are IQD using the model's 1,300 IQD/USD reference; they are not USD debt or dollar-indexed obligations. In the integrated sensitivity developers finance both rights and buildings. The hypothesis is 1.2m m² land, FAR 2.5, 3m m² buildings at USD 800/m², USD 4.2bn sales in months 60–96 and 5% sales costs. There is no rent revenue additionally booked against sold floor space. Public land's assumed USD 600m opportunity cost is an in-kind exposure, never spendable cash. All prices are unverified and require an Iraqi valuation/tax review. The downside halves rights, reduces sales 30%, delays both 24 months and escalates construction.

Rights payments are a developer use and a rail receipt. They cancel in consolidated appraisal; they cannot also be counted as programme profit. Developer equity is 25% of its rights/build uses, and its borrowing is IQD bank credit. Property debt/transaction costs and missing funding are included in its own ledger. [World Bank land-value guidance](https://www.worldbank.org/en/topic/urbandevelopment/publication/financing-transit-oriented-development-with-land-values) and [MTR's model](https://www.mtr.com.hk/sustainability/en/financial-sustainability.html) provide precedents, not Baghdad valuations.

## Energy and manufacturing contracts

Dedicated solar capital is transferred once, without inventing an additional EPC removal. Charging/microgrid equipment and its existing EPC remain rail assets. The railway pays a PPA of **IQD {integrated['ppa']['reference_iqd_per_kwh']:.0f}/kWh**, indexed 5% annually; the annual planning purchase is {integrated['ppa']['annual_planning_purchased_kwh']/1e9:.3f}bn kWh, USD {integrated['ppa']['full_network_annual_payment_at_reference_prices_usd']/1e6:.3f}m equivalent at reference prices. Dispatch/load follows open-line weights, not fare demand. Energy receives exactly what rail pays. Existing solar maintenance transfers once; a further 0.5% of solar capital/year is an explicit renewal-spending sensitivity. Timetable-derived annual generation is not 8760-hour dispatch proof: grid backup, curtailment, storage adequacy and metered purchases require qualification. Export sales are **zero**, with no signed buyer. Low/high PPA cases redistribute company cash and leave the consolidated resource NPV unchanged. [World Bank PPA guidance](https://ppp.worldbank.org/sector/energy/energy-power-agreements/power-purchase-agreements) explains the contractual financing route.

Energy and factory each test 20% private IQD equity. Government remains 25% of original physical rail/energy/factory capital. The factory receives Baghdad's existing train invoices and pays the same resource budgets one month earlier, exposing working capital. Original train prices already include manufacturing labour, QA, ordinary overhead and warranty; 1,044 production staff wages are not added again. An **additional USD 250,000-equivalent capacity fee per train**, annually indexed and paid in IQD, is a separately visible investor-return sensitivity. It cancels on consolidation but increases rail's operating obligations. Warranty cash is locked at 5% of cumulative train payments until 12 months after the final invoice, then released; it is cash restriction, not a duplicate warranty expense. Fifteen caretaker staff and 0.25% plant carrying cost are added during that tail. Plant costs, working-capital funding, interest and outstanding debt at backlog close remain visible in [integrated.json](integrated.json). New orders and salvage are zero until contractual.

At the illustrative capacity fee, factory cash remaining at contract/warranty close is **USD {integrated['entities']['factory']['metrics']['equity_distribution_assumption_usd']/1e6:.3f}m** against **USD {integrated['entities']['factory']['metrics']['private_equity_iqd']/1300/1e6:.3f}m** invested equity. The 15% equity-hurdle NPV is **USD {integrated['entities']['factory']['metrics']['equity_npv_at_15pct_orderbook_or_sale_close_usd']/1e6:.3f}m**. Debt repayment therefore does not establish an investable factory partnership. Developer equity-hurdle NPV is **USD {integrated['entities']['development']['metrics']['equity_npv_at_15pct_orderbook_or_sale_close_usd']/1e6:.3f}m**. These close-date distribution diagnostics deduct any remaining debt and disclose missing funding; no dividend or sponsor return is assumed to be committed. Competitive pricing, equity terms and a bankable capacity contract require further work.

## Appraisal and public exposure

Three retained under-viaduct rental variants add a **fifth independently financed entity** to the integrated case: small, medium and lower-rent/prolonged-vacancy medium. The [civil-linked register, pilot unit, costs, leases and hazards](../viaduct-rentals/README.md) have no accepted site/demand evidence. External rent adds revenue; actual collection follows fit-outs, physical line availability, initial rent-free periods, occupancy ramp, arrears/recovery, tenant turnover and lease-end refunds. Fit-out capital, occupied/vacant maintenance/insurance, 12-year refurbishment and a standalone 15% cash-tax proxy are included. No station sale parcel also earns rent; no existing kiosk income is duplicated. Tenant deposits are restricted cash and matching liabilities, never construction finance or revenue.

The rental partner supplies 25% fit-out capital as private IQD equity and the residual is IQD bank capital, with opening-linked principal and 240-month amortisation. It has **zero new operating-gap capacity**: missing construction interest, fees or reserves remains an explicit funding requirement. The original four borrowers keep their existing allocated caps; combined cap remains 13tn. Rental transfers to rail are zero until an approved agreement exists, so rail cannot silently use the new company's cash. Each borrower exports monthly native ledgers, six-month placements and loan vintages. These ring-fenced structures are alternative to the wholly owned holding rental cases, whose subscriptions replace rather than add partner equity.

Consolidated resource NPV adds collected rent less its OPEX and physical fit-out capital, before financing/tax, to the original resource case. A separately labelled after-rental-tax diagnostic deducts rental tax once; the original four businesses retain their existing before-tax basis. Additional rental-site rights/land opportunity cost is unknown, so the existing station-land subtraction is not a complete new-site appraisal. The 200,000 m² area illustration is blocked as unmapped and supplies no integrated cash.

Core rail/energy/factory unlevered NPV: **USD {a['core_unlevered_npv_usd']/1e9:.3f}bn**. Rail entity NPV including its PPA, capacity fees and internal rights: **USD {a['rail_entity_unlevered_npv_with_internal_payments_and_rights_usd']/1e9:.3f}bn**. Consolidated resource NPV including property sales/building costs and additional renewals/caretaking: **USD {a['consolidated_resource_npv_usd']/1e9:.3f}bn**; including land opportunity cost: **USD {a['consolidated_resource_npv_after_land_opportunity_usd']/1e9:.3f}bn**. Debt/equity/grants are financing transfers and excluded from resource NPV; intercompany transfers cancel to the cent. Nominal discount is {a['nominal_discount_rate']:.1%}, combining 8% real and 5% general inflation.

Government original-capital cash is **USD {m['government_capital_usd_equivalent']/1e9:.3f}bn equivalent ({m['government_cash_share_of_original_capital']:.0%})**. Its USD import cash is USD {m['government_usd_cash']/1e6:.3f}m and Chinese USD credit is USD {m['chinese_usd_credit']/1e6:.3f}m, splitting imports 50:50. All other debt, private equity, property payments, fares and subsidy payments are IQD. Original programme USD capital intensity therefore remains {(m['government_usd_cash']+m['chinese_usd_credit'])/m['total_original_rail_energy_factory_capital_usd']:.2%}; SPV transfers do not remove those USD import requirements. Property construction is assumed contracted in IQD; actual imported content/FX exposure needs quotes.

Public cash capital PV is USD {a['public_capital_cash_pv_usd']/1e9:.3f}bn; in-kind land PV USD {a['public_land_opportunity_pv_usd']/1e9:.3f}bn. The optional availability case pays USD 100m equivalent/year at full opening, indexed 5% and phased by available lines; its PV is USD {cases['integrated_public_availability']['appraisal']['additional_public_availability_payment_pv_usd']/1e9:.3f}bn. It sits **outside the 25% capital limit** and needs appropriation, service performance terms and affordability review. Recipient NPV adds public cash explicitly; the public-plus-private resource appraisal cancels that transfer. Contingent bond/guarantee/termination exposures remain unquantified rather than assumed zero. [World Bank public-support guidance](https://ppp.worldbank.org/government-support) describes these obligations.

Existing fares and kiosk/advertising receipts are retained with their original demand/price/OPEX indices. Integrated cases omit the old USD 25m grant and USD 25m/year new-net-income targets. Fibre, naming rights, parking and employer contracts require incremental **net** quotes; prepaid fares change timing of existing receipts and do not create revenue twice. At 13.4%, USD 50m/year for 20 end-of-year payments has PV USD {50e6*(1-(1+.134)**-20)/.134/1e6:.3f}m at the beginning of the payment period, lower when discounted back to close.

## Iraqi financing routes and 90-day evidence programme

The [World Bank's USD 930m national railway project](https://www.worldbank.org/en/news/press-release/2025/06/25/iraq-new-us-930-million-project-to-extend-and-modernize-railways-promote-regional-connectivity-and-boost-growth) is a separate Umm Qasr–Mosul programme through Baghdad, not metro money. [IFC's September 2025 Iraqi announcement](https://www.ifc.org/en/pressroom/2025/ifc-marks-20-years-of-partnerships-for-impact-in-iraq-announces-1bn-in-new-investm) combines investments and engagements across industrial/property/financial partnerships, not an available USD 1bn fund for this proposal. [ICIEC's 2025 impact report](https://iciec.isdb.org/ader/2025/development-impact-2025/) records reinsurance for Iraqi substations; it does not commit rail credit. Sources checked 3 October 2026. [GCF's published Iraq country programme](https://www.greenclimate.fund/document/iraq-country-programme) and [transport programme](https://www.greenclimate.fund/portfolio/areas-of-work/transport) establish potential application routes, not an award. Climate funding requires emissions baselines, eligibility, accredited-entity engagement and actual terms; no grant is presumed.

[Six workstreams](90-day-work-programme.json) cover lender terms, land/valuation, PPA, standalone factory, existing independently operable phase, and independent model/public-affordability review. Due days are relative to an actual approved start. Named people, legal opinions, quotes and accepted evidence remain pending. [ERPNext Task JSON](erpnext-tasks.json) is a draft native-import package with stable evidence subjects, not live IDs or accepted evidence. Local deployments record actual IDs privately and preserve assignments/status when refreshing descriptions. No external lender/developer contact, issuance or expenditure is authorised by these model files.

Later construction commitments require executable native-currency funding, separately accepted physical evidence and a conservative demand case. Integrated joint downside retains the existing 55/106-month physical stress and adds weaker property conditions: missing funding is **IQD {weak['metrics']['uncovered_support_iqd']/1e12:.3f}tn**, terminal gap debt **IQD {weak['metrics']['terminal_supplemental_balance_iqd']/1e12:.3f}tn**. The proposed structure is a market-test programme, not a claim that the financing gap is solved.

Regenerate with `.venv/bin/python tools/automation/baghdad_financing_redesign.py`; validate exact inputs/outputs with `--check`. No new financial commitments or physical release are implied.
'''

if __name__ == '__main__':
    main()
