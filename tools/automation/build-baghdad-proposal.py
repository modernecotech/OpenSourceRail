#!/usr/bin/env python3
"""Publish the complete Baghdad proposal and a separate future Iraqi programme."""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tomllib
from urllib.parse import quote
import zipfile

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, Spacer
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[2]
CITY = ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
COUNTRY = CITY.parent
OUT = CITY
PUBLICATION_FILES = ('BAGHDAD-PROPOSAL.md','Baghdad-Proposal.pdf','DETAILED-SCHEDULES.md',
    'Baghdad-Proposal-Supporting-Data.zip','manifest.json','archive-manifest.json',
    'appendix-sources.json','national-context.json','source-inventory.csv')

def publication_output(path):
    return path.parent == CITY and path.name in PUBLICATION_FILES or CITY/'registers' in path.parents

MAX_BYTES = 50*1024*1024
SHARED = [
    'docs/rfcs/0033-tacs-runtime-and-resource-control.md',
    'docs/certification/distributed-onboard-control-profile.md',
    'docs/rolling-stock/design-system.md',
    'docs/rfcs/0011-civil-infrastructure-design-standard.md',
    'docs/rfcs/0014-depot-design-standard.md',
    'docs/rfcs/0013-operations-rulebook.md',
    'docs/operating/city-platform.md',
    'docs/deployment-planning-reference.md',
    'docs/civil/slab-trackforms.md',
    'docs/civil/viaduct-design-basis.md',
    'docs/civil/viaduct-bearing-and-movement-schedule.md',
    'docs/civil/viaduct-transport-and-erection-envelope.md',
    'docs/civil/viaduct-first-article-test-plan.md',
    'docs/civil/viaduct-obstacle-clearance.md',
    'docs/repository-artifact-policy.md',
    'docs/baghdad-delivery-review-2026-10-04.md',
    'docs/baghdad-continuation-review-2026-10-04.md',
    'docs/baghdad-ci-controls-review-2026-10-04.md',
    'docs/baghdad-manufactured-viaduct-review-2026-10-04.md',
    'docs/baghdad-scope-and-industrial-review-2026-10-04.md',
]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


book = module('baghdad_proposal_book', ROOT/'tools/automation/build-doc-book.py')
national = module('baghdad_proposal_national', ROOT/'tools/automation/generate-national-briefs.py')


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024*1024), b''):
            value.update(block)
    return value.hexdigest()


def receipt(path):
    return {'bytes': path.stat().st_size, 'sha256': digest(path)}


def read_json(path):
    return json.loads(path.read_text())


def table(headers, rows):
    def cell(value):
        return str(value).replace('|', '/').replace('\n', ' ')
    return '\n'.join(['| '+' | '.join(headers)+' |', '| '+' | '.join(['---']*len(headers))+' |',
                       *['| '+' | '.join(cell(v) for v in row)+' |' for row in rows]])


def usd_m(value):
    return f'{value/1e6:,.3f}'


def financial_narrative_facts(programme):
    calculation=programme['independent_recalculation']
    return dict(slow_income_full_opening_burden=calculation['fare_pricing']['fare_5pct_opex_5pct_income_2pct']['full_opening']['forty_four_trips_income_share'],
                opex_stress_terminal_gap_iqd=calculation['cases']['fare_5pct_opex_7pct']['terminal_supplemental_balance_iqd'],
                opex_stress_uncovered_support_iqd=calculation['cases']['fare_5pct_opex_7pct']['uncovered_support_iqd'])


def check_baseline(programme, package):
    subprocess.run([sys.executable,str(ROOT/'tools/automation/publish-city-summary.py'),'--check'],cwd=ROOT,check=True)
    revised=read_json(CITY/'engineering/programme-recalculation/summary.json')
    for base,group in ((ROOT,'sources_sha256'),(CITY/'engineering/programme-recalculation','outputs_sha256')):
        for relative,sha in revised[group].items():
            if digest(base/relative)!=sha:raise ValueError('Stale programme recalculation: '+relative)
    viaduct=read_json(CITY/'engineering/viaduct-comparison/summary.json')
    for base,group in ((ROOT,'sources_sha256'),(CITY/'engineering/viaduct-comparison','outputs_sha256')):
        for relative,sha in viaduct[group].items():
            if digest(base/relative)!=sha:raise ValueError('Stale viaduct comparison: '+relative)
    closure=read_json(CITY/'engineering/delivery-closure/summary.json')
    for base,group in ((ROOT,'sources_sha256'),(CITY/'engineering/delivery-closure','outputs_sha256')):
        for relative,sha in closure[group].items():
            if digest(base/relative)!=sha:raise ValueError('Stale delivery continuation: '+relative)
    delivery=read_json(CITY/'engineering/delivery-baseline/summary.json')
    for base,group in ((ROOT,'sources_sha256'),(CITY/'engineering/delivery-baseline','outputs_sha256'),(ROOT,'external_outputs_sha256')):
        for relative,sha in delivery[group].items():
            if digest(base/relative)!=sha:raise ValueError('Stale delivery reconciliation: '+relative)
    rentals=read_json(CITY/'engineering/viaduct-rentals/summary.json')
    for base,group in ((ROOT,'sources_sha256'),(CITY/'engineering/viaduct-rentals','outputs_sha256')):
        for relative,sha in rentals[group].items():
            if digest(base/relative)!=sha:raise ValueError('Stale viaduct rentals: '+relative)
    equity=read_json(CITY/'engineering/equity/summary.json')
    for base,group in ((ROOT,'sources_sha256'),(CITY/'engineering/equity','outputs_sha256')):
        for relative,sha in equity[group].items():
            if digest(base/relative)!=sha:raise ValueError('Stale Baghdad equity: '+relative)
    redesign=read_json(CITY/'engineering/financing-redesign/summary.json')
    for base,group in ((ROOT,'sources_sha256'),(CITY/'engineering/financing-redesign','outputs_sha256')):
        for relative,sha in redesign[group].items():
            if digest(base/relative) != sha: raise ValueError('Stale financing redesign: '+relative)
    qualification=read_json(CITY/'engineering/qualification/summary.json')
    for relative,sha in qualification['sources_sha256'].items():
        if digest(ROOT/relative) != sha: raise ValueError('Stale qualification source: '+relative)
    for relative,sha in qualification['outputs_sha256'].items():
        if digest(CITY/'engineering/qualification'/relative) != sha: raise ValueError('Changed qualification output: '+relative)
    risk=read_json(CITY/'engineering/delivery-risk/summary.json')
    for relative,sha in risk['sources_sha256'].items():
        if digest(ROOT/relative) != sha: raise ValueError('Stale delivery stress input: '+relative)
    for relative,sha in risk['outputs_sha256'].items():
        if digest(CITY/'engineering/delivery-risk'/relative) != sha: raise ValueError('Changed delivery stress output: '+relative)
    detail=read_json(CITY/'engineering/detail/register.json')
    for relative,sha in detail['sources_sha256'].items():
        if digest(ROOT/relative) != sha:
            raise ValueError('Stale Baghdad engineering source: '+relative)
    if detail['engineering_release'] or detail['family'] != 'metro-6car':
        raise ValueError('Unexpected engineering family/release boundary')
    factory=read_json(CITY/'engineering/factory/summary.json')
    for relative,sha in factory['sources_sha256'].items():
        if digest(ROOT/relative)!=sha:
            raise ValueError('Stale Baghdad factory source: '+relative)
    if factory['readiness_months_from_ntp']!=18 or factory['stock_finish_working_day']>factory['infrastructure_target_working_day']:
        raise ValueError('Factory must support the 18-month facility and civil-aligned fleet programme')
    for relative, sha in programme['sources_sha256'].items():
        if digest(ROOT/relative) != sha:
            raise ValueError('Stale Baghdad financing source: '+relative)
    if programme['included_cities'] != ['Baghdad'] or programme['factory']['anchor_city'] != 'Baghdad':
        raise ValueError('Baghdad finance cannot include future national cities')
    if abs(sum(v['usd_equivalent'] for v in programme['capital_sources_native'].values())-programme['total_capex_usd']) > .02:
        raise ValueError('Capital sources and uses disagree')
    if not package['planning_example_complete'] or package['operational_release']:
        raise ValueError('Unexpected Baghdad planning/release status')
    ops = read_json(CITY/'operations/baghdad-operations-manifest.json')
    payload = CITY/'operations'/ops['file']
    if not payload.is_file() or digest(payload) != ops['compressed_sha256']:
        raise ValueError('Materialise the current Baghdad operations payload with ./osr city baghdad')


def national_context(programme):
    cities = [national.load_city(path)[1] for path in sorted(COUNTRY.glob('*/design.toml'))]
    factory = national.factory_budget('IQ',cities)
    aggregate = national.aggregate_breakdowns([c.breakdown for c in cities], national_factory_usd=factory)
    factory_epc = factory*float(tomllib.loads((ROOT/'lib/templates/capex-costs.toml').read_text())['overhead']['epc_fraction'])
    baghdad_factory = programme['factory']['cost_usd']
    baghdad_factory_epc = programme['factory']['epc_usd']
    if factory < baghdad_factory-.02 or factory_epc < baghdad_factory_epc-.02:
        raise ValueError('National shared factory cannot omit the Baghdad plant allowance')
    factory_increment = factory-baghdad_factory
    factory_epc_increment = factory_epc-baghdad_factory_epc
    rows = []
    for c in sorted(cities, key=lambda c: (-c.population, c.name)):
        path = COUNTRY/c.name/'design.toml'
        d = tomllib.loads(path.read_text())
        rows.append({'city': c.name, 'population': c.population, 'lines': len(d['lines']),
                     'stations': len(d['stations']), 'route_km': sum(l['length_m'] for l in d['lines'])/1000,
                     'family': d['lines'][0]['rolling_stock'], 'trainsets': c.fleet_trainsets,
                     'vehicle_modules': c.vehicle_modules, 'city_capex_usd': c.breakdown.total_usd})
    city_total = sum(c.breakdown.total_usd for c in cities)
    if abs(city_total+factory+factory_epc-aggregate.total_usd) > .02:
        raise ValueError('National capital reconciliation failed')
    return {'status': 'future-catalogue-planning-not-funded', 'cities': rows, 'city_count': len(rows),
            'represented_population': sum(c.population for c in cities),
            'trainsets': sum(c.fleet_trainsets for c in cities), 'vehicle_modules': sum(c.vehicle_modules for c in cities),
            'city_capital_usd': city_total, 'shared_factory_usd': factory, 'shared_factory_epc_usd': factory_epc,
            'baghdad_factory_reference_usd': baghdad_factory,
            'baghdad_factory_epc_reference_usd': baghdad_factory_epc,
            'future_shared_factory_increment_usd': factory_increment,
            'future_shared_factory_epc_increment_usd': factory_epc_increment,
            'total_national_capital_usd': aggregate.total_usd,
            'future_incremental_city_capital_after_baghdad_usd': aggregate.total_usd-programme['total_capex_usd'],
            'imported_procurement_usd': aggregate.imported_usd, 'local_procurement_usd': aggregate.local_usd,
            'factory_count': 1, 'baghdad_financing_includes_national_expansion': False,
            'limitations': ['Catalogue budgets, un-escalated and unquoted; no national debt or appropriations agreed.',
                            'One shared factory is counted once. Future scope adds other cities and only the difference above the Baghdad plant/EPC reference; it does not add a second full factory.',
                            'The larger national factory allowance is an unquoted city-order envelope, not a priced expansion or proof of concurrent throughput. Renewal, intercity links and national governance costs remain unpriced.',
                            'Represented population is a sum of planning city populations, not measured rail catchment or unique national beneficiaries.']}


def build_narrative(d, s, p, f, n, ops, deployment):
    from baghdad_equity import return_label, dividend_date
    revised=read_json(CITY/'engineering/programme-recalculation/summary.json')
    scope_buy=revised['finance_cases']['revised_scope_buy']
    local=revised['finance_cases']['local_positive']
    mezz=revised['finance_cases']['local_positive_mezzanine']
    depot_revised=read_json(CITY/'engineering/programme-recalculation/depots.json')
    staff_revised=read_json(CITY/'engineering/programme-recalculation/workforce.json')
    industry_revised=read_json(CITY/'engineering/programme-recalculation/industry.json')
    component_quantities={row['id']:row['network_quantity'] for row in industry_revised['products']}
    process_labels={'bogie':'bogie fabrication','motor-inverter-set':'motor assembly','battery-225kwh-pack':'battery-pack assembly','door-cassette':'door manufacture','window-cassette':'window manufacture'}
    selected_factories=read_json(CITY/'engineering/programme-recalculation/local_positive.json')['selected_component_factories']
    selected_process_names=', '.join(process_labels[key] for key in selected_factories)
    bought_process_names=', '.join(process_labels[row['id']] for row in industry_revised['products'] if row['id'] not in selected_factories)
    alignment_revised=read_json(CITY/'engineering/programme-recalculation/alignment.json')
    revised_rows=[[name,f"{m['total_capital_usd']/1e9:.3f}",f"{m['usd_capital_intensity']:.2%}",
        f"{m['unfunded_support_iqd']/1e12:.3f}",f"{m['terminal_all_debt_iqd']/1e12:.3f}",m['junior_defaulted_vintages']]
        for name,m in revised['finance_cases'].items()]
    revised_cash=read_json(CITY/'engineering/programme-recalculation/local_positive.json')['monthly']
    revised_sources=[[label,currency,f"{sum(r[key] for r in revised_cash):,.0f}",
        usd_m(sum(r[key] for r in revised_cash)/(1 if currency=='USD' else 1300))]
        for label,currency,key in (
            ('Government import cash','USD','government_usd_cash'),('Government local cash','IQD','government_iqd_cash'),
            ('Chinese capital credit','USD','chinese_export_credit_draw_native'),('Ordinary capital bonds','IQD','domestic_bonds_draw_native'),
            ('Green capital bonds','IQD','green_bonds_draw_native'),('Senior bank capital credit','IQD','bank_credit_draw_native'),
            ('Conditional climate capital grant','IQD','climate_grant_iqd'))]
    comp = p['comparison']; rec = p['independent_recalculation']; indexed = rec['cases']['fare_5pct_opex_5pct']
    prices = rec['fare_pricing']['fare_5pct_opex_5pct']; early = rec['early_repayment']['cases']; fx = 1300.
    narrative_facts=financial_narrative_facts(p)
    resilience=read_json(CITY/'engineering/delivery-risk/summary.json')
    factory_plan=read_json(CITY/'engineering/factory/summary.json')
    civil_one=next(x for x in factory_plan['civil_rephasing']['line_completions'] if x['line']=='line-1')
    resilience_rows=[]
    risk_labels={'calendar_baseline':'Baseline', 'civil_cycles_20pct_faster':'Faster civil; retained starts',
                 'civil_earliest_unchanged_cycles':'Earliest civil; original cycles', 'civil_earliest_20pct_faster':'Earliest civil; faster cycles',
                 'availability_75pct_costed':'75% availability, costed', 'availability_75pct_test_shift_costed':'75% availability + test shift',
                 'availability_75pct_all_stage_shifts':'75% availability + all stages', 'temporary_first_article':'Temporary first-article facility',
                 'combined_delay_costs':'Combined delays, costed', 'joint_downside':'Joint downside'}
    for name in ('calendar_baseline','civil_cycles_20pct_faster','civil_earliest_unchanged_cycles','civil_earliest_20pct_faster',
                 'availability_75pct_costed','availability_75pct_test_shift_costed','availability_75pct_all_stage_shifts',
                 'temporary_first_article','combined_delay_costs','joint_downside'):
        case=resilience['cases'][name];m=case['metrics']
        clearance='Unfunded' if m['uncovered_support_iqd']/1300. > .02 else ('Unpaid' if m['all_debt_cleared_month'] is None else m['all_debt_cleared_month'])
        resilience_rows.append([risk_labels[name],f"{min(x['opening_month'] for x in case['phases'])}/{max(x['opening_month'] for x in case['phases'])}",f"{m['peak_supplemental_balance_iqd']/1e12:.3f}",f"{m['total_finance_interest_and_fees_usd']/1e9:.3f}",clearance])
    joint=resilience['cases']['joint_downside']['metrics']
    temporary=resilience['cases']['temporary_first_article']
    section=read_json(CITY/'engineering/qualification/first-section.json')
    redesign=read_json(CITY/'engineering/financing-redesign/summary.json')['cases']
    equity=read_json(CITY/'engineering/equity/summary.json')['cases']
    rentals=read_json(CITY/'engineering/viaduct-rentals/summary.json')
    delivery=read_json(CITY/'engineering/delivery-baseline/summary.json')
    hourly=read_json(CITY/'engineering/delivery-baseline/chronological-energy.json')['cases']['synthetic_reference:owned_solar']
    closure=read_json(CITY/'engineering/delivery-closure/finance-reconciled_full_fleet.json')
    closure_metrics=closure['metrics']
    core_alignment=read_json(CITY/'engineering/alignment/core-realignment.json')
    access=read_json(CITY/'engineering/access/summary.json')
    clearance=read_json(CITY/'engineering/clearance/summary.json')
    access_rows=[[row['radius_m'],f"{row['covered_population_2020']:,.0f}",f"{row['fraction_of_raster_population']:.1%}"] for row in access['population']['catchments']]
    manufactured_viaduct=read_json(CITY/'engineering/viaduct-comparison/comparison.json')
    local_energy=read_json(CITY/'engineering/delivery-closure/site-energy.json')['cases']['reference']
    fare_trials=read_json(CITY/'engineering/delivery-closure/fare-sensitivities.json')
    rental_eq=equity['rental_medium_1000m'];coveq=equity['coverage_dividends_1000m']
    eq=equity['primary_1000m'];eqbase=equity['government_equity_reference']
    redesigned=redesign['integrated']; redweak=redesign['integrated_joint_downside']
    energy = national._energy_plan(d, s, national.compute_stats(d, s, d['city']['population']))
    profile = tomllib.loads((ROOT/'lib/templates/rolling-stock.toml').read_text())['profiles']['metro-6car']
    terms = tomllib.loads((ROOT/'lib/templates/iraq-funding.toml').read_text())
    fareopts = tomllib.loads((ROOT/'lib/templates/baghdad-finance-options.toml').read_text())
    line_rows = []
    for line in d['lines']:
        fleet = next(row for row in d['fleets'] if row['line'] == line['name'])
        line_rows.append([line['name'], line['shape'], f"{line['length_m']/1000:.3f}",
                          sum(st['line']==line['name'] for st in d['stations']), fleet['peak_count'],
                          fleet['trainset_count'], next(x['opening_month'] for x in p['phased_opening']['phases'] if x['line']==line['name'])])
    civil = {}
    for segment in d['civil_segments']:
        civil[segment['class']] = civil.get(segment['class'],0.)+segment['to_station_m']-segment['from_station_m']
    cap_rows = [[row['bucket'].replace('_',' '), usd_m(row['total_usd']), usd_m(row['imported_usd']), usd_m(row['local_usd'])]
                for row in f['capex_usd']['procurement_origin_buckets']]
    cap_rows += [['Baghdad plant', usd_m(p['factory']['cost_usd']), usd_m(p['factory']['cost_usd']*national.IMPORTED_SHARE['production_plant']), usd_m(p['factory']['cost_usd']*(1-national.IMPORTED_SHARE['production_plant']))],
                 ['Plant EPC', usd_m(p['factory']['epc_usd']), usd_m(p['factory']['epc_usd']*national.IMPORTED_SHARE['epc_overhead']), usd_m(p['factory']['epc_usd']*(1-national.IMPORTED_SHARE['epc_overhead']))],
                 ['Total Baghdad capital', usd_m(p['total_capex_usd']), usd_m(comp['osr_imported_purchases_usd']), usd_m(comp['osr_local_purchases_usd'])]]
    source_rows = [[name.replace('_',' '), value['currency'], f"{value['amount']:,.0f}", usd_m(value['usd_equivalent'])]
                   for name,value in p['capital_sources_native'].items()]
    selected_capital = early['cost_priority']
    candidate_rows = [[name.replace('_',' '), value['currency'], f"{value['amount']:,.0f}", usd_m(value['usd_equivalent'])]
                      for name,value in p['capital_sources_native'].items() if name.startswith('government_')]
    for label, currency, value in [('Chinese export credit','USD',selected_capital['china_capital_usd']),
                                    ('Ordinary IQD bonds','IQD',selected_capital['ordinary_bonds_iqd']),
                                    ('Green IQD bonds','IQD',selected_capital['green_bonds_iqd']),
                                    ('Bank capital credit','IQD',selected_capital['bank_capital_iqd']),
                                    ('Conditional climate capital grant','IQD',selected_capital['climate_grant_iqd'])]:
        candidate_rows.append([label,currency,f'{value:,.0f}',usd_m(value if currency=='USD' else value/fx)])
    receipts = p['operating_receipts']
    cases = [[name.replace('_',' '), f"{m['peak_supplemental_balance_iqd']/1e12:.3f}",
              f"{m['uncovered_support_iqd']/1e12:.3f}",f"{m['terminal_supplemental_balance_iqd']/1e12:.3f}"]
             for name,m in rec['cases'].items()]
    early_rows = [[name.replace('_',' '), m['all_debt_cleared_month'],
                   usd_m(m['net_finance_cost_saving_vs_buffered_gap_only_usd']), usd_m(m['early_premiums_usd_equivalent'])]
                  for name,m in early.items()]
    national_rows = [[c['city'],f"{c['population']:,}",c['family'],f"{c['route_km']:.1f}",c['trainsets'],usd_m(c['city_capex_usd'])]
                     for c in n['cities']]
    intro = f'''# Baghdad Proposal

OpenSourceRail proposes an owner led feasibility and front end engineering programme for Baghdad, with Iraqi train manufacture and local infrastructure delivery. This proposal brings the Baghdad network, railway systems, operating organisation, delivery evidence and financing together, and sets out a separate path for future national development. It is addressed to the prospective Iraqi public sponsor, Baghdad authorities, operating organisation and financing partners; no appointment or financing commitment is asserted.

The latest [programme recalculation](engineering/programme-recalculation/README.md) sizes **{revised['operating_fte']:,} permanent operating FTE** and **{revised['depot_count']} line-local depots** for all {revised['depot_storage_slots']} six-car trainsets. With completed components bought, revised capital is **USD {scope_buy['total_capital_usd']/1e9:.3f}bn**. The unquoted positive-margin local-production option gives **USD {local['total_capital_usd']/1e9:.3f}bn**, imported invoice exposure of **USD {local['imported_invoices_usd']/1e9:.3f}bn** and **{local['usd_capital_intensity']:.2%} USD capital intensity**. It records **IQD {local['unfunded_support_iqd']/1e12:.3f}tn residual unsourced support** after assumed facilities and retains **IQD {local['terminal_all_debt_iqd']/1e12:.3f}tn total debt** at the horizon. Current indexed fares and additional-income assumptions do not repay this scope. Mezzanine defers cash pressure but leaves unpaid balloons; it is a sensitivity, not a recommended solution.

The earlier [delivery-cost continuation](engineering/delivery-closure/README.md) remains a comparator: **USD {closure_metrics['total_capital_usd']/1e9:.3f}bn capital**, before still-unpriced scope, and **IQD {closure_metrics['terminal_supplemental_balance_iqd']/1e12:.3f}tn unpaid gap debt**. The original financial schedules below likewise remain controlled reference cases. Debt clearance in an older reference is not the current feasibility conclusion; higher fares and conditional additional funding are tested separately, with no adopted tariff or lender commitment.

The current planning network is **{comp['osr_lines']} lines, {comp['osr_route_km']:.1f} km of double track route, {comp['osr_stations']} stations and {sum(x['trainset_count'] for x in d['fleets']):,} six car trainsets**. Original reference capital, including one final-assembly plant and its EPC, was **USD {p['total_capex_usd']/1e9:.3f} billion equivalent**; it does not include the latest scope replacement. The direct government capital contribution remains **25%** of each revised case. Imports are financed 50% government USD cash and 50% proposed Chinese USD credit; all remaining capital cash, bonds and bank debt are IQD.

The immediate decision proposed is to establish a sponsor, commission survey and demand work, develop the first operable line and plant packages, qualify suppliers and obtain executable financing terms. Construction and operating release require the recorded physical and approval gates. The current resource constrained plan reaches first line revenue in month {prices['first_opening']['month']} and full operation in month {prices['full_opening']['month']} after financial close. That long schedule is a material design and delivery problem to resolve; this proposal does not substitute a five year promise.

## How to read the proposal

The first part states the integrated proposal and the decisions it needs. The next part prints the detailed network registers and six month financing schedules. The technical appendices reproduce every current Baghdad Markdown report, the national brief and selected shared standards. The supporting ZIP preserves the full controlled Baghdad files, every Baghdad financing spreadsheet, the operations payload, national city design inputs and the cited shared references. The source inventory and manifest identify exact file bytes.

Baghdad is the only financed city. National expansion is a future strategic option with its own budgets and approvals. The national totals and generic city pages retain original catalogue assumptions; the latest Baghdad study does not silently reprice or finance other cities. Procurement origin, loan currency and reporting currency are different measures. USD equivalents use the historical model anchor of IQD {fx:,.0f}/USD; this is not a current execution quote. All prices, demand, debt terms and rights proceeds remain planning assumptions. Older generic foreign turnkey examples reproduced in source appendices are separate from the historical 148 km comparison and the scheduled Baghdad financing cases.

## Latest scope, local production and matched funding cases

The {len(d['stations'])} stations have two concurrent staff during two normal eight-hour shifts, giving {staff_revised['station_cover']['normal_daily_shift_assignments']} daily shift assignments. The retained 20.5-hour railway also funds 4.5 hours of late cover. Weekly/leave/training/sickness cover gives {staff_revised['station_cover']['station_cover_fte']} station FTE, included in the {revised['operating_fte']} permanent railway FTE. Loaded annual payroll is IQD {revised['annual_payroll_iqd']/1e9:.3f}bn before subsequent OPEX inflation. The general pay floor is IQD {staff_revised['wage_basis']['general_monthly_floor_iqd']:,.0f}/month: 1.5 times the 2021 employee median indexed to 2026 at an assumed 5% a year. Technical/supervisor/senior/director grades use 2.25/3/4/5 times the same proxy. This is not a newly observed national median and does not change the fare-income denominator.

Each line has one depot; all spare/reserve trains are included. Storage uses the actual 111 m train plus 10 m clearance; workshop bays follow bay-hour workload separately. The nine sites total USD {depot_revised['gross_reference_cost_usd']/1e6:.3f}m and replace the old USD 8m allowance once. Itemised storage/workshop/access tracks, points, civil shells, process equipment, services, wash plants, wheel lathes, stores, rescue/isolation and retained energy stock are costed. Land/title, utilities, actual foundations and installed charging/grid upgrades remain open; launch/throat conflicts need an operating replay.

The order requires {component_quantities['bogie']:,} bogies, {component_quantities['motor-inverter-set']:,} motor/inverter sets, {component_quantities['battery-225kwh-pack']:,} battery packs ({industry_revised['battery_gross_network_kwh']/1e6:.3f} GWh gross), {component_quantities['door-cassette']:,} door cassettes and {component_quantities['window-cassette']:,} window cassettes. Final assembly employs {industry_revised['main_factory_production_fte']} production and {industry_revised['main_factory_support_fte']} support FTE for {industry_revised['production_months']} scheduled paid months. Upstream facilities are sized to the train factory rate and price imported process machinery, local buildings/materials, residual imported inputs, qualification and their full paid establishment. Selected processes ({selected_process_names}) have positive whole-order margins under the unquoted assumptions. The remaining processes ({bought_process_names}) stay bought in this case; their Baghdad-only whole-order margins are shown in the make/buy register. Imported cells/BMS, inverters, wheels/axles/bearings and other safety parts remain; no cell gigafactory or future national sales credit is assumed.

The main design uses the reworked central elevated routes and {alignment_revised['current_elevated_fraction']:.2%} elevated track across Baghdad. Further outer civil alternatives permit up to {alignment_revised['policy']['maximum_elevated_fraction']:.0%} elevated and screen {alignment_revised['candidate_extra_elevated_m']/1000:.3f} km of additional at-grade conversion around exceptional curves, reaching {alignment_revised['candidate_elevated_fraction']:.2%} elevated. These outer candidate intervals are not adopted or surveyed. Elevation alone removes no horizontal bend. Added viaduct and hypothetical 0/25/50% routing-penalty removal are priced separately; no hypothetical penalty removal is adopted as a saving.

{table(['Matched case','CAPEX USD bn','USD intensity','Unsourced support IQD tn','Terminal all debt IQD tn','Defaulted junior vintages'],revised_rows)}

All twelve cases have invoice-level capital registers, monthly native-currency cash/principal ledgers and six-month bond/loan placement schedules in the [latest study](engineering/programme-recalculation/README.md) and supporting archive. Government is 25% of total capital, with USD machinery/input downpayments on actual invoice dates and the balance allocated as local IQD appropriation. Only Chinese credit is USD debt; bonds, senior bank/gap debt and mezzanine are IQD. Six months of senior service are reserved from the first draw, with three months of OPEX and industrial working capital. This reserve policy differs from the older reference; matched cases are the valid comparison.

The following capital-only source table is for the latest positive-margin local-production senior case. Fees, interest, reserve funding and gap facilities are separate cashflows; this table reconciles to capital uses only. Ordinary and green bonds are separate placements within the same total funding requirement.

{table(['Latest capital source','Currency','Native amount','USD equivalent m'],revised_sources)}

The proposed IQD mezzanine replaces 10% of residual domestic capital borrowing, with 6% cash coupon, 4% PIK, 2% fee and a 15-year balloon. Cash coupons require senior DSCR of 1.20, funded reserves and genuine residual cash. Deferred coupons and PIK are debt. Unpaid balloons become overdue balances with separately disclosed simple-interest sensitivity, without automatic refinancing, conversion or interest-on-arrears. The case leaves IQD {mezz['terminal_all_debt_iqd']/1e12:.3f}tn total debt and {mezz['junior_defaulted_vintages']} defaulted draw vintages. It does not improve the unlevered company NPV of USD {local['company_npv_before_finance_usd']/1e9:.3f}bn at the assumed discount rate. Grants, net development-rights receipts, green terms and concessional gap funding are uncommitted; an 8% gap-rate case exposes this dependency. Fares, fare/OPEX inflation, advertising, kiosk/rental receipts and inherited additional income are already included.

## Baghdad network and population access

The design retains a planning population of {comp['planning_population']:,}. The former {comp['anchor_weighted_coverage']:.1%} routing-demand cell fraction is not population coverage and its resident multiplication is retired. Native WorldPop 2020 pixels give a bbox population of **{access['population']['bbox_population_2020']:,.0f}**, with residents counted once in the union of station circles:

{table(['Radius (m)','Covered residents (2020)','Share of raster bbox population'],access_rows)}

These are potential radial catchments, not verified walksheds or unique passengers. The 1,500–2,000 m cases require actual walking/feeder provision. Population dates and boundaries differ from the catalogue; no rebasing or extra fare demand is assumed. River crossings, entrances, barriers and topography require validation. **Reachable line pairs are {access['transfers']['reachable_line_pair_fraction']:.1%}** through intermediate lines; direct transfers cover {access['transfers']['direct_transfer_fraction']:.1%}. [Source counts, sensitivities and transfer paths](engineering/access/README.md).

**The straight viaduct concept remains obstacle-unreleased.** The [beam/support/terrain register](engineering/clearance/README.md) retains {clearance['mapped_footprints']:,} nearby mapped footprints, including {clearance['known_height_footprints']:,} with source height tags. It flags {clearance['beam_building_status'].get('beam-roof-collision',0):,} provisional roof clashes and {clearance['beam_building_status'].get('height-unresolved',0):,} unresolved-height checks. Low-roof overflight never clears the pier/foundation below; supports, tall-building clearance, terrain/grades, utilities, property/air rights and construction access require survey and redesign. Raising the deck needs grade-compliant approaches and revised capital; moving piers must use verified spans or an independently checked special crossing. Current financial figures include no unpriced adopted obstacle solution.

{table(['Line','Shape','Route km','Stations','Peak fleet','Total fleet','Opening month'],line_rows)}

![Baghdad network](baghdad-network-map.png)

Line names are controlled design identifiers. Public station names, route brands and final termini require owner approval. Chainages, coordinates, interchange platforms and fleet roles are printed in the network registers and regenerated from the adopted core corridor concept.

The service concept operates 05:30 to 02:00 with a three minute protected peak headway. The current scheduled journeys and fleet sizing are capacity led; accepted junction/authority capacity, ridership, a timetable, station crowding and degraded recovery need operating review. The {sum(x['trainset_count'] for x in d['fleets'])} trainsets comprise peak, spare and cold reserve roles documented in the annex.

## City-centre alignment rework

Within the controlled core rectangle ({core_alignment['core']['south']}–{core_alignment['core']['north']}°N, {core_alignment['core']['west']}–{core_alignment['core']['east']}°E), radial corridors use straight tangents and ring connections use broad circular planning fillets where the water constraints permit. Detoured sections require a new curve and structural review. Core land sections are elevated; water crossings retain bridge classification. The final water-constrained core routes change from {core_alignment['core_original_length_m']/1000:.3f} to {core_alignment['core_final_route_length_m']/1000:.3f} km. This is the main design used by the updated station, fleet, civil, energy, depot, staffing, delivery and financing calculations. The earlier extra-viaduct cost-only case did not change geometry.

![Before and after core routing](engineering/alignment/core-alignment-comparison.png)

These corridors reserve no property or air rights. Obstacles, heritage/security constraints, surveyed clearances, pier access, utilities, transition curves, cant, vertical geometry and foundations require engineering and owner review. Outer approaches retain bends and exceptional elevated products. The coverage proxy must be measured before selecting the faster/straighter layout as an access solution; no old coverage score is carried forward.

## Trains and imported component strategy

The Baghdad profile is metro 6car: {profile['cars']} cars, {profile['length_m']} m body length, {profile['passenger_capacity']} passengers at nominal planning load including {profile['seat_count']} seats, and {profile['crush_capacity']} at short duration crush load. Each train has {profile['onboard_battery_nameplate_kwh']:,.0f} kWh nameplate / {profile['onboard_battery_kwh']:,.0f} kWh usable LFP battery capacity, {profile['traction_controller_count']} traction controllers, {profile['traction_peak_kw']:,.0f} kW peak traction and a {profile['hvac_design_ambient_c']} C design ambient. These are reference profiles requiring supplier and physical qualification, not delivered fleet performance.

The original industrial scope is train assembly, body modules, fit out, wiring, coatings, inspection, testing and maintenance, with completed bogies, batteries, windows and doors bought. The latest positive-margin local-production option replaces selected completed imports with Chinese process machinery and residual inputs for Iraqi fabrication/assembly. Solar equipment, glazing and critical component inputs retain imports. Chinese supplier origin and export lender eligibility need evidence for every financed item; the entire imported basket is currently an unqualified scenario. Candidate CRRC equipment remains subject to competitive supplier selection, interface and safety qualification. There is no established CRRC partnership, quotation or endorsement.

Shared LM3 fabrication and first article documentation is reference process evidence for a three car platform. It does not qualify Baghdad's six car consist. The national programme should qualify the shared modules and then validate each consist and its interfaces, rather than treating a shared drawing as an accepted Baghdad train.

## Civil infrastructure and stations

The civil screen contains {len(d['civil_segments']):,} segments: '''
    intro += ', '.join(f'{length/1000:.1f} km {name}' for name,length in civil.items())+'. '
    intro += f'''Route kilometres describe double track corridors; they are not track kilometres or a measurement of all sidings. Station products, {len(d['interchanges'])} interchange complexes and {len(d['junctions'])} junction records are bound to the generated layout.

The proposed civil programme starts with survey control, utilities, property and access, geotechnical investigation, flood/drainage levels, alignment and station fit. Desktop soil inputs contain 7,287 sample locations and 65 missing profiles; they do not supply foundation bearing capacity, groundwater or deep stratigraphy. Structural calculations, spans, erection, movements and independent checking must follow route specific evidence. Generated alignment exports have unfitted curves, placeholder vertical profiles and undesigned cant.

Stations require accessible approaches, platforms, passenger information, fire and evacuation design, fare equipment, retail and advertising layouts, security, sanitation and maintenance access. Platform and station access standards must be checked against the final six car envelope and passenger demand. Equipment and architecture references do not establish installed compliance.

The original USD 8m depot allowance is replaced by the nine full-fleet line depots in the latest recalculation above. Surveyed land, foundation/electrical interfaces, fire/security release and supplier quotations remain open. Workshop bays cannot be counted as overnight train parking. The earlier reference policy proposed two revenue trains at selected powered stations and line-local storage for remaining fleet; the latest study gives no capacity credit to station parking. Usable tracks, charging, protected morning release, evening repositioning and repeated-day replay still require acceptance. The depot and stabling appendices retain these failures explicitly.

## Manufactured viaduct alternatives and installed cost

The [manufactured-viaduct comparison](engineering/viaduct-comparison/README.md) covers Pi20 and Pi25 with two bearing/connection schemes, plus an OSR-US constrained-access option. Baghdad's infrastructure load seed now explicitly requires the complete 24-axle, 111 m six-car train, with supplier axle positions and loaded distribution still unresolved. A link slab retains independent girder-end bearings; shared bearings require a checked structural continuity connection and staged load path.

Every one of the {len(manufactured_viaduct['alignment_segments'])} elevated segments, including {manufactured_viaduct['special_segment_count']} exceptional segments, has a comparison record. The original elevated model separates USD {manufactured_viaduct['standard_rate_allowance_usd']/1e9:.3f}bn standard-rate allowance from USD {manufactured_viaduct['routing_penalty_usd']/1e9:.3f}bn routing penalties. Penalties discourage difficult routing; they are not supplier-priced structures or savings available merely by deletion. Realignment, station movements, ground/utility investigations and installed whole-life alternatives remain unaccepted.

Retaining simple-span bearings changes the existing periodic cost index from USD {manufactured_viaduct['bearing_index_sensitivity']['current_conditional_rate_usd_per_km']/1e6:.3f}m/km to USD {manufactured_viaduct['bearing_index_sensitivity']['simple_span_link_slab_rate_usd_per_km']/1e6:.3f}m/km. The USD {manufactured_viaduct['bearing_index_sensitivity']['direct_network_delta_usd']/1e6:.3f}m uniform whole-elevated-network difference is an unadopted rate illustration; Pi bearing quantities are not transferred to OSR-US/special designs. The lower existing rate remains conditional on an unaccepted structural scheme.

The separate financed sensitivity applies only to {manufactured_viaduct['bearing_index_sensitivity']['financed_pi25_only_length_m']/1000:.3f} km of standard Pi25, adding USD {manufactured_viaduct['bearing_index_sensitivity']['financed_pi25_only_direct_delta_usd']/1e6:.3f}m direct and incremental EPC once. It gives USD {manufactured_viaduct['bearing_sensitivity_finance_metrics']['total_capital_usd']/1e9:.3f}bn capital and IQD {manufactured_viaduct['bearing_sensitivity_finance_metrics']['terminal_supplemental_balance_iqd']/1e12:.3f}tn terminal gap debt, with monthly/six-month financing recalculated under the same 25% government and USD/IQD rules. Existing civil invoice dates and origin proportions are inherited assumptions. Connection, finite end effects, foundations, actual import eligibility and other consequential costs remain unpriced; the original full-fleet case is preserved as a comparator.

Finite supports, unknown foundation lengths, complete member/hook mass gates, configured erection bids, per-item invoice currencies and eight production fronts are included in the supporting data. Installed-price totals remain unknown while scope is unpriced. Accepted complete double-track bays/week, first beam/pier/connection trials and independent design release must precede programme and budget selection. No literature savings or 30 m product is assumed.

## Energy and desert operation

The current duty model schedules 3,952 one way journeys and about 217,090 train km per day, with 2,053.8 GWh annual traction demand. It assigns 52.1 MW station/depot PV, 354.0 MWh site storage, 316.0 MW connected charging and {energy.solar_plant_kw/1000:.1f} MW dedicated solar. The design's zero annual residual grid/PPA import is an energy accounting result; it does not establish uninterrupted operation or installed grid independence.

Storage endurance, adverse weather, PV land, heat/dust derating, losses, supplier fire separation, actual charging duty, protection and backup import need a time resolved operating appraisal. Snapshot solver passes and grid only diagnostics do not close these gates. Battery protection and cabin/battery thermal separation must be qualified at the declared ambient and duty. No claimed unlimited battery autonomy or accepted solar islanding is used to close financing.

![Engineering map](engineering/screenshots/baghdad-qgis-engineering-map.png)

## Train control and operational safety

The current architecture reference is RFC 0033, TACS runtime and committed resource control. RFC 0032's separate authority/protection prototype is superseded. The design retains committed resource ownership in the interlocking, ordered consensus decisions, onboard movement authority, automatic train protection, station departure gates and final brake requests. OCC supplies service intentions and observations; ERP and supervision cannot bypass railway authority or clear protection latches.

The reference uses three static consensus voters and two logical protection channels. Hardware placement, independent power/network domains, sensing, brake outputs and common cause analysis need assessment. Two software channels do not establish independent safety hardware. Lost required permissions, stale/invalid evidence and missing physical proving retain restrictive protection. The runtime is a synthetic process reference and not a deployed Baghdad control system or safety certificate. Existing Baghdad timetable simulations do not constitute RFC 0033 physical acceptance.

## Iraqi manufacture and local economic benefit

The Baghdad plant is sized from {p['factory']['vehicle_modules']:,} vehicle modules. Its base allowance is USD {usd_m(p['factory']['cost_usd'])}m plus USD {usd_m(p['factory']['epc_usd'])}m EPC, counted once outside city CAPEX. The current plant construction assumption is {p['factory']['planning_build_working_days']} working days before train production. Factory siting, freight access, utilities, tooling, staff, production rate, quality capacity and six car qualification require their own approved business and delivery plan.

The original procurement allocation assigns USD {comp['osr_local_purchases_usd']/1e9:.3f}bn equivalent locally. This is potential local expenditure, not payroll, GDP added or a guaranteed Iraqi content ratio. Local train and infrastructure work can retain skills, supplier income, repair capacity and spares knowledge. The latest process appraisal above includes whole-order labour, factory support/maintenance and make/buy margins; manufacturing sales to other customers still need a separate business case. No multiplier, tax recovery or future national plant profit is booked as project cash without evidence. Imported machinery and residual inputs retain foreign exchange and supply-chain exposure.

## Operating organisation and digital management

The latest operating establishment is {revised['operating_fte']:,} FTE with IQD {revised['annual_payroll_iqd']/1e9:.3f}bn annual loaded payroll, replacing the original {comp['operating_fte']:,} FTE / IQD {comp['operating_labour_annual_iqd']/1e9:.3f}bn allowance. It includes OCC/remote assistance, fleet maintenance, infrastructure/energy, stations, passenger service, administration and training. It remains a planning workload/roster model; legal duties, appointments and competence require acceptance. Construction and factory populations are priced separately as explained above, with measured work hours, crew mixes and throughput still required.

{table(['Operating role','Required FTE','Wage grade'],[[r['role_id'],r['required_fte'],r['grade']] for r in staff_revised['roles']])}

The Baghdad operating package contains {ops['assets']:,} assets, {ops['manufacturing_tasks']:,} manufacturing/verification tasks, {ops['manufacturing_materials']:,} material/procurement rows, {ops['maintenance_tasks']:,} maintenance tasks and {ops['qa_actions']:,} QA actions. These are generated planning records. Actual purchase orders, execution, measurements and accountable release evidence remain distinct. The project twin, ERPNext/Frappe integration, supervision, QR identities, maintenance and advisory AI support business work; they do not issue movement or safety release authority.

![Baghdad operations dashboard](engineering/screenshots/baghdad-operations-dashboard.png)

## Delivery and commissioning sequence

First obtain survey and demand inputs, freeze a viable first line and plant scope, and reconcile depot and energy duties. Qualify long lead components and the first six car train, then deliver infrastructure, energy, station systems and trained operating staff in accepted phases. Each line needs its own operating and safety acceptance before fare revenue is realised.

The city-sized plant becomes available after **18 months from NTP**, followed by first-article qualification and finite six-car production cells. All {sum(x['trainset_count'] for x in d['fleets'])} trains remain in scope. The calculated full fleet finishes alongside the overall infrastructure programme. Civil work and invoice milestones are rephased within the existing crew lanes and dependency graph. Line 1's infrastructure moves from day {civil_one['original_infrastructure_day']} to {civil_one['rephased_infrastructure_day']}, reducing its fleet wait from {civil_one['original_idle_working_days']} to {civil_one['rephased_idle_working_days']} working days. Resources, durations and opening dates are preserved. Survey, land, utility, permit and contract approval remain necessary before deferring work. See the [physical factory sizing, crews, test paths and capital reconciliation](engineering/factory/README.md).

Current capital milestones span {f['structured_financing']['base']['metrics']['construction_cash_months']} months, based on 260 working days/year and 30 pre NTP working days. Conditional first/full network opening is month **{prices['first_opening']['month']}/{prices['full_opening']['month']}**, including the separate three-month line commissioning allowance. Opening-weighted demand and the 25% fixed / 75% variable OPEX proxy require a surveyed phase-specific plan. Factory sizing and its explicit capital increase are included in the new monthly and six-month financing schedules; rates, physical qualification and delivery risk remain open.

The factory's final fleet margin is only {factory_plan['infrastructure_target_working_day']-factory_plan['stock_finish_working_day']} working days; test-path throughput margin is {factory_plan['exclusive_test_path_capacity_trainsets_per_year']/factory_plan['minimum_steady_output_trainsets_per_year']-1:.2%}. The [frozen-resource delivery and financing study](engineering/delivery-risk/README.md) separates civil productivity from investment timing: a 1.0 cycle multiplier preserves the complete baseline schedule, faster cycles retain the rephased start floors, and earliest construction is a separate comparison. Removing spending delays at unchanged productivity must not be called a productivity financing penalty.

Recovery options price extra structural/electrical/composite or coordinated production shifts, hiring/training, supplier expediting and testing, with unchanged cell counts and indexed incremental payroll/nonlabour costs. Testing alone does not improve the 75% availability opening dates; upstream production still limits them. A separate temporary first-article facility sensitivity adds USD {temporary['metrics']['incremental_recovery_capital_usd']/1e6:.3f}m capital plus support staffing and tests first opening in month {min(x['opening_month'] for x in temporary['phases'])}; permanent acceptance paths, first-article qualification and full line fleets remain required. These options are unquoted deterministic comparisons, not adopted delivery commitments.

Shift compression now excludes fixed curing/bonding/inspection holds and the additional 60-day first-article qualification. The [industrial qualification and funding-gate package](engineering/qualification/README.md) adds a metric temporary-site layout, cell tooling/transfer interfaces, quantity-based RFQs reconciled inside the existing USD 35m direct allowance, and ten ERPNext evidence tasks with source-bound measurement templates and authenticated independent result verification. Named owners, measurements, quotations and signatures remain pending.

Funding interruptions halt procurement/construction/production and defer invoices, adding local remobilisation and carrying/prolongation costs. Recovered domestic placement and delayed export credit are conditional on re-placement; permanent refusal has **no opening or debt-clearance date**, and is never filled by an automatic government or gap-loan replacement. The separate first-section study uses {section['route_km']:.3f} km and five actual line-1 stations, {section['total_trainsets']} already-planned six-car trains at six-minute headways, independent turnbacks/charging/maintenance and USD {section['extra_capital_with_epc_usd']/1e6:.2f}m extra capital. Conditional section service is month {section['conditional_opening_month']}, with surveyed demand and physical acceptance still required; the full {sum(x['trainset_count'] for x in d['fleets'])}-train baseline remains unchanged. Earlier small-section fares alone do not establish better finance: the study includes advanced invoices, additional support costs, phase demand deducted from later full-line receipts, and native-currency reserves/debt.

Combined delay-cost cases add extended staffing, supervision, carrying, storage/insurance and construction prolongation allowances without buying baseline crew-months twice. The financial downside ladder tests 30% fewer paid trips, 25% lower retail/advertising receipts, 5% annual invoice escalation, 7% rail OPEX growth, no assumed green/grant/rights enhancements, core rates two percentage points higher and an 8% IQD gap facility limited to IQD 4tn. The joint case leaves **IQD {joint['uncovered_support_iqd']/1e12:.3f}tn cumulative uncovered cash** and **IQD {joint['terminal_supplemental_balance_iqd']/1e12:.3f}tn terminal gap debt**. Uncovered cash is a missing funding requirement; it is not an additional government contribution or secured credit. Reported repayment in such a case is conditional on filling that gap. The [physical qualification register](engineering/delivery-risk/qualification-register.csv) remains entirely not demonstrated; no model run supplies measured production/civil evidence or lender commitments.

{table(['Scenario','First/full month','Peak IQD gap tn','Interest/fees USD eq bn','Debt cleared month'],resilience_rows)}

![Baghdad project twin](engineering/screenshots/baghdad-project-twin.png)

## Original reference capital and procurement origin

{table(['Capital scope','USD eq m','Imported USD m','Local USD eq m'],cap_rows)}

The city and plant total includes the plant EPC once. Budgets are unquoted planning estimates; land, utilities, taxes/duties, escalation, contingency and accepted depot/site scope require closure. Loan principal repaid later is a financing cashflow, not additional construction CAPEX. Origin shares do not establish citizenship of vendors, employment or lender eligibility.

## Original reference financing in USD and Iraqi dinars

{table(['Capital source','Currency','Native amount','USD equivalent m'],source_rows)}

Government cash totals USD {sum(p['capital_sources_native'][k]['usd_equivalent'] for k in ('government_import_cash','government_local_cash'))/1e9:.3f}bn equivalent, exactly 25% of capital. Its USD {p['government_capital_usd_cash']/1e6:.3f}m import cash is inside that limit. The same amount of Chinese USD debt covers the other half of imports. Remaining capital sources are IQD. Combined USD capital funding is USD {p['usd_denominated_capital_usd']/1e9:.3f}bn ({p['usd_denominated_capital_share']:.2%}); IQD is {p['iqd_denominated_capital_share']:.2%}. Only Chinese credit is USD debt, while government also needs USD cash for downpayments.

{table(['Facility','Currency','Rate assumption','Grace months per draw','Amortisation months','Arrangement fee'],[[name.replace('_',' '),terms[name]['currency'],f"{terms[name]['annual_rate']:.0%}",terms[name]['grace_months_from_draw'],terms[name]['repayment_months'],f"{terms[name]['arrangement_fee']:.1%}"] for name in ('chinese_export_credit','domestic_bonds','bank_credit')])}

Bond and bank capital split the residual after government and Chinese credit 75:25. Interest, fees and reserve deposits are funded separately in the cash forecast. A direct 25% capital contribution does not cap sovereign bond liabilities, guarantees or all lifetime public risk. Ministry of Finance issuance powers, sponsor structure, investor mandates, IQD placement capacity, draw availability and creditor consent for city/plant pooling need confirmation. Chinese supplier and lender qualification remains pending. Terms are sensitivities, not loan offers or an approved appropriation.

The capital source table above is the reference allocation. The conditional blended/early repayment case below replaces part of those ordinary bonds with green bonds and adds a climate grant that reduces domestic borrowing. It is a separate capital mix with the same total uses, government cash and Chinese credit; the two tables must not be added together.

{table(['Conditional blended capital source','Currency','Native amount','USD equivalent m'],candidate_rows)}

The conditional capital grant replaces USD 25m equivalent of domestic borrowing. Additional development rights and new local operating receipts enter later project cash and are not counted as construction capital a second time. Supplemental gap draws pay financing/OPEX/reserve cash needs and are separate from both capital tables.

## Delivery estimate, physical scope and operating establishment

The published original **USD {delivery['base_programme_usd']/1e9:.6f}bn equivalent** remains a planning base with **{delivery['unpriced_scope_count']} explicit unpriced scope categories**, not the amount proved sufficient to deliver service. The [delivery reconciliation](engineering/delivery-baseline/README.md) records quantity/rate/source/currency/price-date/inclusions/exclusions/estimator/uncertainty, depot/storage alternatives, six-car BOM/mass/axle/interfaces/labour/qualification, hourly energy, demand-led fleet requirements and workload/competence. Quotations, price dates and actual accountable appointments remain pending. Existing EPC, factory contingency, training/qualification and train QA/labour are not added twice. Uncalibrated correlated cost/delay quantiles remain separate sensitivities, not approved risk budgets.

The original USD 8m depot allowance does not fund the full current fleet, line-local storage and maintenance requirements. Quantity-based alternatives price storage tracks, points, drainage/access, workshop shells/equipment, line-local inspection/rescue/isolation/quarantine and full depot PV/storage. Gross reference budgets are **USD {delivery['depot_reference_alternatives']['workload_bays']['depot_gross_reference_usd']/1e6:.3f}m** for workload bays and **USD {delivery['depot_reference_alternatives']['retained_declared_bays']['depot_gross_reference_usd']/1e6:.3f}m** retaining declared bays; land, foundations, utility diversion, installation and overlap with charging/EPC remain open. Their replacement illustrations remove the old allowance once, and neither is adopted into loans or original government funding. The existing failed morning-direction/stabling and conflict-aware access gates remain open.

Annual energy netting supplies no firm hourly charging guarantee. The synthetic hourly owned-solar reference requires **{hourly['grid_import_kwh']/1e6:.1f} GWh purchases / USD {hourly['electricity_purchase_usd']/1e6:.3f}m per year**, before separately priced wheeling, balancing and connection. It also exposes **{hourly['unserved_kwh']/1e6:.3f} GWh unmet charging**, so the assumed service is not fully delivered even with aggregate pooling. Weather, charger queues, feeder rights/outages, storage ageing and actual tariffs require measured per-site replay; these are sensitivity values, not a forecast or silently updated finance allowance. Owned, contracted and hybrid options use the same duty and no export income.

Reference workload cover totals **{delivery['reference_operating_fte']:,} operating FTE / USD {delivery['reference_loaded_payroll_usd']/1e6:.3f}m loaded annual pay equivalent**, against the original catalogue payroll allowance. Local pay, employer/rest terms and measured task hours remain unaccepted. Recruitment cohorts work backwards through joining, practical assessment/repeats and supervised authorisation; factory production payroll and temporary commissioning are separate. The real pilot roster has zero appointed workers and blocks every slot. Native HR/training/maintenance/manufacturing mappings and the read-only task eligibility preview preserve human work-release authority. Six additional 90-day evidence Tasks carry accountable functions, unquoted closure work budgets and independent exit criteria.

Opening fleet comparisons reduce service supply and require calibrated OD/access/fares and usable corridor/dependency evidence. They do not retain unchanged fares or announce an earlier opening from fewer trains alone. The continuation now reconciles these assumptions into explicit unquoted monthly cash sensitivities. [Current review](../../../../../docs/baghdad-delivery-review-2026-10-04.md) supersedes the historical 347-month figures; [clean-checkout test bootstrap](../../../../../tools/automation/bootstrap_baghdad_tests.py) restores the exact archived operations input.

## Latest per-site energy, funding and fare reconciliation

The [new monthly and six-month funding ledgers](engineering/delivery-closure/FINANCE-RECONCILIATION.md) replace allowances once and preserve the original financing reconstruction exactly. The full-fleet sensitivity has peak supplemental debt **IQD {closure_metrics['peak_supplemental_balance_iqd']/1e12:.3f}tn**, company cash NPV before finance **USD {closure['company_cash_npv_before_finance_usd']/1e9:.3f}bn**, and no debt-clear month. Government is 25% of scenario capital; a separate case fixes its original absolute contribution. Imports retain 50% government USD / 50% Chinese USD loan, with bonds, bank/gap credit and receipts in IQD. Conditional grants, rights receipts, local income and cheap gap lending remain uncommitted; removing the additional income exposes unfunded cash.

Per-site reference energy requires **{local_energy['grid_import_kwh']/1e6:.1f} GWh imports**, exposes **{local_energy['unserved_kwh']/1e6:.1f} GWh unserved charging**, and prices firm energy services/owned-plant maintenance at **USD {local_energy['annual_firm_energy_cost_usd']/1e6:.3f}m/year**. Physical grid and charger upgrades remain unpriced. Buying shortage energy in the financial sensitivity does not provide a physical connection or an accepted timetable. Depot layouts label individual tracks/slots; Iraqi yard-slab mould capacity meets cumulative installation dates at assumed cycles, while plant cost and actual curing/qualification remain open. The 23 child part RFQs sit inside the eight parent allocations; all 26 maintenance intervals, practical lesson cards and rest-limited anonymous slots retain their actual evidence gates.

Battery reserve contributions are already in rolling maintenance. Separate monthly restricted-cash ledgers add only inflation shortfalls at replacement, including in the reduced-fleet opening case, and prohibit spending reserve cash on early bond/loan repayment. Reduced fleet procurement also reduces service receipts; contracted solar moves plant capital to a provider whose resource costs remain visible.

[Installed-site shortage diagnostics](engineering/delivery-closure/SITE-ENERGY.md) separate local PV from wheeled generation and trace every constrained hour. The installed energy/charger throughput case reduces fare and commercial receipts; it is an upper bound until actual charging events and timetable feasibility are accepted. [Development and training mobilisation](engineering/delivery-closure/DEVELOPMENT-TRAINING.md) funds interim authorities from NTP, schedules external teachers, assessors and mentors before opening, and retains absent real appointments and equipment as explicit gates. The reduced-fleet factory replay removes deferred orders and rebuilds finite production queues, preserving expansion-capable plant/depot capital. Opening dates use the later of civil readiness and replayed fleet acceptance, with later dates propagated into all operating cashflows. No earlier receipts or cheaper factory are invented. All integrated sensitivities retain zero dividends; terminal project cash is not audited distributable profit.

{table(['Initial base fare IQD','Paid-demand multiplier','44-trip income share','Debt-clear month','Terminal gap IQD tn','Before-finance cash NPV USD bn'],[(str(r['base_fare_iqd']),f"{r['paid_demand_multiplier']:.3f}",f"{r['monthly_44_trip_income_share']:.1%}",str(r['debt_clearance_without_unfunded_support_month']),f"{r['terminal_gap_debt_iqd']/1e12:.3f}",f"{r['company_cash_npv_before_finance_usd']/1e9:.3f}") for r in fare_trials])}

These fare sensitivities retain annual 5% fare/OPEX/income increases and variable pricing, with the existing uncalibrated price elasticity. Debt clearance is conditional on funding placement; a negative company cash NPV persists across these trials. The affordability share uses the historical income proxy, not disposable-income surveys. No higher fare, commercial first-corridor rank, operational release or accepted lease/loan is created by the calculation.

## Early deficits and additional financing

The independent flat price reconstruction requires USD {rec['reconciliation']['gross_additional_liquidity_usd']/1e9:.3f}bn gross early additional cash and retains USD {rec['reconciliation']['later_retained_cash_usd']/1e9:.3f}bn later. Their difference is USD {rec['reconciliation']['net_lifetime_liquidity_gap_usd']/1e6:.3f}m net nominal deficit before pricing gap finance. These figures cannot be added to construction capital as though they were new infrastructure. Later revenue cannot fund an earlier payment without a priced and available facility.

The candidate replaces eligible ordinary capital bonds with IQD green debt at 4% plus arrangement and 0.5% annual guarantee charges; it also tests an uncommitted USD 25m equivalent climate grant, USD 300m equivalent net development rights and USD 25m equivalent annual additional net local receipts. A green label alone changes no coupon. Grants replace eligible domestic capital borrowing; guarantees enhance credit rather than provide cash. Supplemental IQD credit at 2% and a 0.5% draw fee is capped at IQD 13tn outstanding, not treated as proven market capacity. All these conditional sources require legal, donor, investor and valuation evidence.

Additional routes to qualify include climate/renewable energy grants or concessional finance, guaranteed IQD on lending, phased green bonds/sukuk, development rights and station land leases, telecom/fibre leases, naming rights, sponsorship, employer travel contracts and carefully priced concessions. Carbon receipts remain unbooked contingent upside. Upfront lease receipts cannot be added while the same future rents remain in revenue. Keep net proceeds after costs and any transferred liabilities; foreign development finance needs confirmed IQD on lending or a priced hedge to preserve the currency structure.

{table(['Financing and pricing sensitivity','Peak gap IQD tn','Uncovered IQD tn','Terminal gap IQD tn'],cases)}

## Rail, property, energy and industrial financing redesign

The [twelve-case financing redesign](engineering/financing-redesign/README.md) tests opening-linked principal, longer civil amortisation, a 15-year total insured green tenor and USD 1bn-equivalent **total** station rights replacing USD 300m, plus three retained viaduct-rental variants. Separate rail, solar, factory and developer monthly/native-currency accounts cancel PPA payments, train invoices, plant capacity fees and rights transfers on consolidation. The rental variants add a fifth borrower with zero extra operating-gap cap and no unapproved transfers to rail. Six-month placement envelopes and loan-vintage dates accompany every borrower. Fares/kiosks/advertising remain included; no future national order, surplus-power sale or unawarded climate grant services the integrated case.

The integrated sensitivity leaves peak aggregate IQD liquidity of **IQD {redesigned['metrics']['peak_aggregate_liquidity_iqd']/1e12:.3f}tn**, cumulative missing funding **IQD {redesigned['metrics']['uncovered_support_iqd']/1e12:.3f}tn**, and resource NPV **USD {redesigned['appraisal']['consolidated_resource_npv_usd']/1e9:.3f}bn**, or **USD {redesigned['appraisal']['consolidated_resource_npv_after_land_opportunity_usd']/1e9:.3f}bn** after unverified public-land opportunity cost. Company cash balances and an assumed credit cap cannot establish bankability. Longer grace still pays interest, and changing finance terms leaves the core unlevered NPV unchanged.

Government remains 25% of the original rail/energy/factory capital. Import cash/Chinese credit still split 50:50 in USD; other credit, equity, fares, rights and payments are IQD. Private property construction is an additional explicitly priced scope, with its own IQD debt and equity. Optional indexed availability payments add public obligations **outside** the 25% capital limit; resource NPV cancels those government transfers. The combined downside retains delayed openings, weaker fare/nonfare demand, inflation and restricted financing, and adds weaker property sales/rights: **IQD {redweak['metrics']['uncovered_support_iqd']/1e12:.3f}tn** remains missing. Fifteen station candidates and six 90-day evidence workstreams have no invented title, valuation, investor term or named owner.

## Iraqi mixed joint-stock holding and staged ordinary equity

The [eighteen-case ordinary-equity study](engineering/equity/README.md) proposes a holding company with 100%-owned rail, energy, factory and station-development businesses, including retained viaduct premises. It replaces the prior subsidiary private equity rather than adding it twice. Government's original USD 1.970bn-equivalent cash remains 25% of original capital; converting it into shares creates **zero new money**. Same-price private subscriptions of USD 500m/1bn/2bn equivalent leave government ownership of {equity['primary_500m']['metrics']['government_ownership']:.1%}/{eq['metrics']['government_ownership']:.1%}/{equity['primary_2000m']['metrics']['government_ownership']:.1%}. IQD subscriptions, paid share registers, premium/dilution and fees are explicit. A secondary government share sale gives cash to the seller and zero to the company.

The $1bn primary sensitivity requests six founder calls and a conditional later issue at month 60, with 2% fees. Monthly paid state capital constrains actual settlement; listing at that date is unproven. Against a matched tax-stressed holding reference, peak IQD liquidity falls from **{eqbase['metrics']['peak_liquidity_debt_iqd']/1e12:.3f}tn to {eq['metrics']['peak_liquidity_debt_iqd']/1e12:.3f}tn**. Domestic principal waits for full-network opening. Subscription failure cannot silently expand agreed six-month capital-credit placements or draw operating rescue for construction: the next unfunded invoice is withheld and no opening is reported. Whole-programme subscription delay and joint downside have separate cash/debt ledgers. Government's USD cash and Chinese USD credit remain the import split; other money remains IQD.

The $1bn case's illustrative private equity return is **{return_label(eq['shareholder_returns']['iraqi_private']['equity_irr'])} nominal IRR**, compared with an assumed 15% hurdle, with first dividend **{dividend_date(eq['metrics']['first_dividend_month'])}**. Dividends require profit, cleared debt, intact reserves and no missing cash; shares have no guaranteed redemption. Tax, depreciation, property inventory, factory impairment, retained earnings and internal-charge eliminations reconcile in pro-forma accounts. The base tax sensitivity avoids assumed group loss relief; a separate aggregate-profit proxy is explicitly unqualified. Resource NPV after land remains **USD {eq['metrics']['resource_npv_after_land_usd']/1e9:.3f}bn**; changing financing does not create additional resources or financial feasibility.

Current Iraqi corporate/admission rules require an accepted mandate, legal/capital approvals, eligible audited business/accounts and actual investors. The 2019 liabilities restriction also needs entity-level assessment: the consolidated screening proxy flags **{eq['metrics']['indicative_article28_threshold_failed_months']} months** in the $1bn sensitivity. The structure therefore needs capitalisation/legal resolution before execution. Incorporated status, listing approval, public-land equity valuation and independent audit are all absent. Six additional source-bound ERP evidence packages cover legal/tax, mandate, subscriptions, accounts, governance and admission. Open licences are retained; no exclusive design valuation, national train order or uncontracted export income is assumed.

## Retained premises beneath suitable viaducts

The [commercial-space register, open unit plan, pilot and rental model](engineering/viaduct-rentals/README.md) links **{rentals['elevated_segment_count']:,} elevated segments / {rentals['elevated_length_m']/1000:.4f} km** to civil chainage, planning coordinates and existing track assets. A preliminary 25 m bay screen reserves approaches, support inspection zones and independent access, suggesting **{rentals['screening_area_m2']:,.0f} m²**. Confirmed eligible area remains **zero**: surveyed height/footprint, ownership, street/utility access, fire/flood/impact protection and station-sale overlap are unaccepted. The 200,000 m² illustration has {rentals['cases']['large']['unmapped_area_m2']:,.0f} m² unmapped and supplies no integrated lease cash. A 30-unit draft pilot and reusable independent 30 m² enclosure have no invented tenant, permit or live contract.

The medium 100,000 m² scenario adds **USD {rentals['cases']['medium']['metrics']['total_fitout_capital_usd']/1e6:.3f}m equivalent** of indexed fit-out capital. Leasing follows civil/rail readiness, rent-free periods, occupancy ramp, tenant turnover and arrears. Occupied/vacant maintenance, insurance, 12-year refurbishment, depreciation and tax are visible. Security deposits are liabilities backed by restricted cash; they supply no revenue, capital or dividends. Existing kiosks are unchanged and station buildings assumed sold cannot also generate rent. Additional under-viaduct land/rights cost is unverified; no free land value is asserted.

Before-tax incremental rental resource NPV is **USD {rentals['cases']['medium']['metrics']['resource_npv_before_tax_usd']/1e6:.3f}m**, with the lower-rent/prolonged-vacancy case **USD {rentals['cases']['medium_downside']['metrics']['resource_npv_before_tax_usd']/1e6:.3f}m**. In the wholly owned $1bn holding case, medium rents give private nominal IRR **{return_label(rental_eq['shareholder_returns']['iraqi_private']['equity_irr'])}**, first dividend **{dividend_date(rental_eq['metrics']['first_dividend_month'])}** and peak IQD liquidity **{rental_eq['metrics']['peak_liquidity_debt_iqd']/1e12:.3f}tn**. Recurring rent adds value only after its resources/costs; it does not close the multibillion-dollar financial deficit.

The independent lender-policy comparison allows annual dividends with at least 1.30 historical/projected debt coverage, positive profit, completed capital, intact operating/tax/forward-service/renewal reserves and conservative leverage. These terms are unapproved and do not produce earlier distributions under the current tested assumptions: the non-rental first dividend is **{dividend_date(coveq['metrics']['first_dividend_month'])}**. A separately labelled final-cash diagnostic leaves actual accounts unchanged: the original $1bn private IRR from ordinary dividends is {return_label(eq['shareholder_returns']['iraqi_private']['equity_irr'])}; the terminal-cash sensitivity reports **{return_label(eq['terminal_cash_sensitivity']['shareholder_returns']['iraqi_private']['equity_irr_with_terminal_cash'])}**, with no guaranteed redemption, unvalued asset sale or quoted share-exit price. An undefined IRR establishes no positive investor return; missing funding prevents a completed-horizon cash exit.

Each pilot unit carries lease/meter/inspection/use fields, civil-parent links and five common physical hazard paths. Tenant fire, flooding, impact, blocked bearing/inspection access and utility faults can affect piers, spans and railway operation; controller redundancy provides no mitigation for these hazards. Six additional native ERP evidence drafts require actual site, civil/fire, market, quote, maintenance/lease and finance evidence before occupancy or construction release.

## Passenger fares and other operating income

Base model average paid trip yield is IQD {comp['fare_iqd']:,.0f}. At full steady operation, existing fares contribute IQD {receipts['farebox_annual_usd']*fx/1e9:.3f}bn/year, shops/kiosks IQD {receipts['station_retail_annual_usd']*fx/1e9:.3f}bn and advertising IQD {receipts['station_advertising_annual_usd']*fx/1e9:.3f}bn. These already reduce the funding gap. Rental occupancy is 88%, advertising 85%; prices, collection and customer demand are not verified Baghdad lease quotations. Commercial figures are gross receipts, with dedicated concession costs requiring appraisal.

Low capacity use assumes {comp['annual_low_case_paid_trips']/365:,.0f} paid trips/day, not unique travellers or a demand survey. The proposed fare design should evaluate concession funding, student and low income access, commuter caps, transfer integration, peak/off peak tiers and collection costs before adopting a tariff. Neither a fare increase nor future kiosk rent places the early financing by itself.

The base full network operating allowance totals USD {usd_m(f['annual_opex_usd']['total'])}m/year equivalent, before the separate inflation sensitivities. Existing maintenance includes a battery renewal reserve on a 12 year reference cycle and fixed asset renewal allowances; it is not an accepted lifecycle replacement plan. Do not add the same battery reserve as new CAPEX. Condition based renewal quantities, inflation, dedicated concession costs, tax and supplier maintenance terms need qualification.

{table(['Base steady annual OPEX','USD equivalent m'],[[k.replace('_',' '),usd_m(v)] for k,v in f['annual_opex_usd']['components'].items()])}

## Annual ticket increases and OPEX inflation

The requested paired sensitivity indexes fares, OPEX and income 5% annually from financial close. No tickets are sold before opening. Nominal average fares are IQD {prices['first_opening']['average_paid_fare_iqd']:,.0f} at first opening and IQD {prices['full_opening']['average_paid_fare_iqd']:,.0f} at full opening. With 5% income growth, 44 trips remain {prices['full_opening']['forty_four_trips_income_share']:.1%} of the income proxy. With only 2% income growth that burden reaches **{narrative_facts['slow_income_full_opening_burden']:.2%}** at full opening and the assumed real price elasticity reduces paid trips.

Variable pricing tests 40% of baseline trips at 1.25 times the standard fare and 60% at 0.90 times it, with separate demand response and the same capacity limit. If OPEX grows 7% while fares/income grow 5%, the model leaves **IQD {narrative_facts['opex_stress_uncovered_support_iqd']/1e12:.3f}tn uncovered cash** and **IQD {narrative_facts['opex_stress_terminal_gap_iqd']/1e12:.3f}tn terminal unpaid gap debt**. This sensitivity still needs additional financing before later surpluses; repayment remains conditional on that funding being available. Existing rent is flat unless the rental indexation sensitivity is chosen; new net rights/receipt targets are held nominal.

The paired case's unlevered NPV is USD {indexed['pricing_project_npv_usd_equivalent']/1e9:.3f}bn at {indexed['pricing_nominal_discount_rate']:.1%} nominal discount, excluding new grant/rights/net income targets and with un-escalated capital. Paying debt under a nominal model is not evidence of positive discounted project value. CAPEX escalation, renewal inflation, future FX, floating rates and surveyed demand remain material appraisal work.

![Fare and OPEX sensitivities](../finance/baghdad-fare-inflation-sensitivities.png)

## Surplus cash and early debt retirement

Surplus first pays OPEX, scheduled principal, interest and fees, then debt service reserves and three months of current OPEX. Voluntary payments cannot be funded by a new gap draw or uncovered cash in the same month. All comparisons below use the same buffers and 5% fare/OPEX/income inputs. Scheduled and voluntary principal are deducted once from native balances.

{table(['Repayment policy','All debt cleared month','Net saving vs buffered gap only USD eq m','Premium USD eq m'],early_rows)}

Cost priority retires bank credit, ordinary bonds, Chinese credit, green bonds, then cheaper gap credit. Under assumed contractual rights it saves USD {usd_m(early['cost_priority']['net_finance_cost_saving_vs_buffered_gap_only_usd'])}m equivalent after premiums and clears debt in month {early['cost_priority']['all_debt_cleared_month']} versus {early['gap_only_buffered']['all_debt_cleared_month']} for buffered gap only. Loans first saves USD {usd_m(early['loans_then_bonds']['net_finance_cost_saving_vs_buffered_gap_only_usd'])}m. All retain IQD {early['cost_priority']['terminal_operating_buffer_iqd']/1e12:.3f}tn operating buffer at the horizon.

Premiums assume 1% bank/Chinese/green and 2% ordinary bonds, with minimum draw ages 6/12/24 months respectively. Eligible vintages are oldest first, retaining instalments and shortening maturity. Calls, notice, compensation, tax and market buyback prices need actual terms. The noncallable case makes no early bond payments; cost ordering is a heuristic rather than a globally best solution. Savings are nominal finance costs, not principal savings or present value wealth. Month numbers run from financial close, with no calendar commencement date assumed.

![Early debt retirement](../finance/baghdad-early-repayment.png)

## Historical Baghdad metro comparison

{table(['Measure','Latest positive-margin local-production Baghdad study','Historical proposal or requested comparator'],[
 ['Route km',f"{comp['osr_route_km']:.1f}",'148'],['Lines / stations',f"{comp['osr_lines']} / {comp['osr_stations']}",'7 / 64'],
 ['Capital USD equivalent bn',f"{local['total_capital_usd']/1e9:.3f}",'18.000 reported'],
 ['Capital USD equivalent m / route km',f"{local['total_capital_usd']/comp['osr_route_km']/1e6:.2f}",f"{18e9/148/1e6:.2f}"],
 ['USD capital funding bn',f"{local['imported_invoices_usd']/1e9:.3f}",'18.000 requested all USD scenario'],
 ['Chinese USD debt bn',f"{local['chinese_usd_draw']/1e9:.3f}",'Final debt and government split unverified']])}

The July 2024 reported estimate is a historical 148 km, USD 18bn scope. An entirely USD foreign loan/government cash basis is the requested comparator, not a verified financing contract. Under that assumption the latest study's USD capital requirement is {1-local['imported_invoices_usd']/18e9:.1%} lower. Distinct scope, price date, tunnelling/structures, land, utilities, qualification and schedule prevent a like for like bid saving claim. Third party fares, actual financing and comparable population access are not established. Its Iraqi labour share cannot be assumed zero. The following retained figure illustrates the original reference allocation; the table above uses the revised study.

![USD capital comparison](../finance/baghdad-financing-comparison.png)

## Future national development

Baghdad can establish manufacturing, maintenance, training, procurement and digital delivery capacity that later Iraqi cities can reuse. The existing catalogue contains {n['city_count']} cities representing {n['represented_population']:,} planning residents, {n['trainsets']:,} trainsets and {n['vehicle_modules']:,} vehicle modules across several standard families. These are proposed urban networks; national intercity rail and freight connections are a future feasibility topic, without routes, budgets, revenues or approvals in these totals.

{table(['Future catalogue city','Planning population','Fleet family','Route km','Trainsets','City CAPEX USD eq m'],national_rows)}

Current catalogue city capital totals sum to USD {n['city_capital_usd']/1e9:.3f}bn. Adding one shared factory at USD {usd_m(n['shared_factory_usd'])}m and its EPC at USD {usd_m(n['shared_factory_epc_usd'])}m produces **USD {n['total_national_capital_usd']/1e9:.3f}bn equivalent** nationally on the catalogue basis. The Baghdad funding reference already contains USD {usd_m(n['baghdad_factory_reference_usd'])}m of plant and USD {usd_m(n['baghdad_factory_epc_reference_usd'])}m of plant EPC. The national allowance uses the larger city-order envelope or module allowance. Future scope beyond that Baghdad reference totals **USD {n['future_incremental_city_capital_after_baghdad_usd']/1e9:.3f}bn**, including only USD {usd_m(n['future_shared_factory_increment_usd']+n['future_shared_factory_epc_increment_usd'])}m of additional shared-plant/EPC allowance, with no second full plant added. Other cities now use current depot and staffing calculations; Baghdad's optional upstream plants remain separate sensitivities. Imported/local procurement in the generic national origin model is USD {n['imported_procurement_usd']/1e9:.3f}bn / USD {n['local_procurement_usd']/1e9:.3f}bn; this is procurement composition, not a national loan programme.

The additional national plant allowance is an unquoted planning envelope; the actual expansion, renewal and concurrent production programme remain unpriced. Intercity connections, research/training institutions, shared governance and capital acceleration also require separate budgets. Independent city-order factory plans do not prove simultaneous national throughput. The 18 city aggregate is not a five year delivery commitment. Future orders require a throughput/renewal study, scheduled allocation and separate appropriations; no national revenue or profit services Baghdad debt in this proposal.

### National industrial and institutional programme

Create common interface standards and supplier quality processes; qualify body, interior and infrastructure suppliers in Iraq; develop local module assembly, battery service, tools, spares and repair capability. A shared apprenticeship and technician programme should cover fabrication, concrete/precast, rail installation, power electronics, charging, software, accessibility and accountable inspection. Set competency outcomes and measured hours before assigning job numbers or training budgets.

Establish a national asset and evidence framework with separate city ownership, budgets, installed configuration and operating approval. Shared procurement and maintenance standards may reduce duplicated development, but each city still needs its own survey, demand, fiscal powers, financial close and safety acceptance. National development should coordinate with existing railways, freight access and universities where feasible; institutional appointments and agreements remain proposed.

### Conditional national sequence

{table(['Stage','Proposed work','Decision before investment'],[
 ['Baghdad foundation','Sponsor, surveyed first line, plant and six car qualification','Accepted scope, executable finance and physical evidence'],
 ['Demonstration and repeatability','Prove operating and industrial outcomes; maintain Mosul and Samawah as planning examples','Evidence of safe service, actual cost, production and affordable demand'],
 ['Next city feasibility','Evaluate regional demand, access, land, energy and local implementation capacity','City specific business case and legal/financial approval'],
 ['Broader urban rollout','Allocate shared factory output by accepted opening dates; qualify family differences','Priced capacity expansion, renewal and approved city finance'],
 ['Intercity and national services','Study railway interfaces, freight/logistics, training and shared standards','New scope, environmental approvals and independently funded appraisal']])}

Mosul and Samawah are useful reference packages; their inclusion here is not a selected construction order. Basra, Erbil, Sulaymaniyah and the other cities require transparent prioritisation from actual need and readiness. Future national borrowing shares and USD/IQD exposure must be recalculated from each qualified import basket. Baghdad's 25% contribution and 50:50 import split are not silently imposed on future city budgets.

## Ownership and decisions requested

The proposed public sponsor should establish the legal project vehicle and accountable budget authority. The city/operator should own demand, fares, service and operating competence. Manufacturing management should own supplier interfaces, tooling, work hours and first article evidence. Independent survey, civil, energy and safety assessors should control their acceptance evidence. Lenders and placement advisers should validate rights, currency, timing, fees and investor capacity. These are proposed functions, not appointments.

Commission a phased Baghdad feasibility package that closes the route, station, depot and energy scope, independently verifies demand and affordable fares, prices capital and lifecycle obligations, and obtains term sheets for the USD import and IQD domestic funding. Review the long production schedule and fund any acceleration explicitly. Present the accepted first phase to the sponsor and competent authorities before construction. Maintain the national chapter as a separately approved development framework.

## Current Baghdad deployment gates

{table(['Gate','Status','Responsible function','Closure action'],[[g['id'],g['status'],g['owner_role'],g['closure_action']] for g in deployment['gates']])}

{deployment['closed_gate_count']} checks are closed and {deployment['open_gate_count']} deployment gates remain open. Manufacturing, system certification and donor/lender decisions have additional distinct gates. The Baghdad package is complete as a planning example and has operational release false. Synthetic simulation, generated registers and documentary completeness are not physical acceptance.

## Detailed schedules and source appendices

The [detailed engineering plan](DETAILED-ENGINEERING.md) and [component register](engineering/detail/README.md) expand Baghdad's six-car mechanical interfaces, civil works, Iraqi slab manufacture, missing parts, onboard power/wiring, software host allocation and ERP handover. The register carries 69 reference part rows and all 60 Rust software allocations, with unknown prices and supplier identities left open. It corrects the ST6 seat layout and electronics interface errors; it does not release shop drawings or add unpriced components to the accepted finance totals. Local ERP recovery and planning-contract checks are recorded separately from production readiness.

The following proposal annex prints every station, interchange, fleet role, energy site and the complete cost priority six month draw/repayment schedule. Civil segment chainages and junction details are in the attached registers and design. Full monthly and alternative case ledgers remain in the supporting archive and repository. Technical annexes reproduce the city survey, ground, alignment, depot, stabling, delivery, deployment, finance and acceptance reports, followed by the current shared architecture and engineering references.

[Source inventory](source-inventory.csv) and [publication manifest](manifest.json) identify exact inputs and outputs. [Supporting data archive](Baghdad-Proposal-Supporting-Data.zip) includes the controlled files and complete operations payload. The editable proposal, PDF and appendix source list can be regenerated with the repository's proposal builder.

External instrument and historical sources are retained from the financing baseline. Source retrieval attempts on 3 October 2026 for China Exim, the GCF Iraq page and the NIC notice returned a timeout or access denial; this proposal does not claim a new source verification or a new lending commitment. Detailed financing reports retain the original source URLs and their stated evidence limits.
'''
    return intro


def write_csv(path, rows):
    with path.open('w',newline='') as handle:
        fields = list(dict.fromkeys(key for row in rows for key in row))
        writer = csv.DictWriter(handle,fieldnames=fields,lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)


def write_registers(d, s, early):
    directory=OUT/'registers'; directory.mkdir(exist_ok=True)
    station_rows=[{k: st.get(k,'') for k in ('id','line','s_m','lat','lon','archetype','platform_length_m','anchor_kind','anchor_name')} for st in d['stations']]
    write_csv(directory/'stations.csv',station_rows)
    write_csv(directory/'civil-segments.csv',d['civil_segments'])
    write_csv(directory/'fleets.csv',d['fleets'])
    write_csv(directory/'energy-sites.csv',s['sites'])
    write_csv(directory/'junctions.csv',d['junctions'])
    write_csv(directory/'interchanges.csv',[{**row,'lines':'; '.join(row['lines']),'platforms':'; '.join(row['platforms'])} for row in d['interchanges']])
    parts=['# Baghdad detailed schedules','', '## Station register','',
           'Coordinates and chainages are planning inputs. IDs are controlled; anchor names remain in the UTF-8 CSV rather than being adopted as public station names. Latitude/longitude are WGS84 degrees.','',
           table(['Station ID','Line','Chainage km','Latitude','Longitude','Platform m'],[[r['id'],r['line'],f"{r['s_m']/1000:.3f}",f"{r['lat']:.6f}",f"{r['lon']:.6f}",r['platform_length_m']] for r in station_rows]),'',
           '## Interchange register','',table(['Interchange','Lines','Latitude','Longitude'],[[r['id'],', '.join(r['lines']),f"{r['lat']:.6f}",f"{r['lon']:.6f}"] for r in d['interchanges']]),'',
           '## Fleet roles','',table(['Line','Peak','Rotation','Spare','Cold reserve','Total'],[[r['line'],r['peak_count'],r['service_rotation_count'],r['spare_count'],r['cold_reserve_count'],r['trainset_count']] for r in d['fleets']]),'',
           '## Energy site register','',table(['Site station','Tier','PV kW','Storage kWh','Grid import kW','Charger kW'],[[r['station'],r['tier'],r['pv_nameplate_kw'],r['storage_capacity_kwh'],r['grid_import_kw'],r['charger_max_kw']] for r in s['sites']]),'',
           '## Six month capital and supplemental draw requirements','',
           'Cost priority with identical three month operating buffers. Settlement is monthly; six month rows are envelopes, not advance placements. Unrounded CSV values reconcile; displayed amounts are rounded. Tranches continue through the entire model horizon.','',
           table(['Months','Gov USD m','Gov IQD bn','China USD m','Ordinary bond IQD bn','Green IQD bn','Bank IQD bn','Gap IQD bn'],
                 [[f"{r['start_month']} to {r['end_month']}",f"{r['government_usd_cash']/1e6:.2f}",f"{r['government_iqd_cash']/1e9:.2f}",f"{r['chinese_export_credit_draw_native']/1e6:.2f}",f"{r['domestic_bonds_draw_native']/1e9:.2f}",f"{r['green_bonds_draw_native']/1e9:.2f}",f"{r['bank_credit_draw_native']/1e9:.2f}",f"{r['liquidity_draw_iqd']/1e9:.2f}"] for r in early['semiannual']]),'',
           '## Six month early repayments and closing balances','',
           'Early principal is additional to the scheduled principal separately retained in the full ledger. Outstanding debt uses the final month of each period. USD equivalent aggregates convert Chinese native debt at the historical IQD 1,300 anchor. Premiums and operating buffers are distinct from principal.','',
           table(['Months','Core early principal USD eq m','Premium USD eq m','Gap principal IQD bn','All debt closing IQD tn eq','Cash closing IQD tn','OPEX buffer IQD bn'],
                 [[f"{r['start_month']} to {r['end_month']}",f"{r['early_core_principal_usd_equivalent']/1e6:.2f}",f"{r['early_premiums_usd_equivalent']/1e6:.2f}",f"{r['liquidity_repayment_iqd']/1e9:.2f}",f"{(r['chinese_export_credit_closing_balance_native']*1300+sum(r[n+'_closing_balance_native'] for n in ('bank_credit','domestic_bonds','green_bonds'))+r['closing_liquidity_debt_iqd'])/1e12:.3f}",f"{r['closing_project_cash_iqd']/1e12:.3f}",f"{r['closing_operating_buffer_iqd']/1e9:.3f}"] for r in early['semiannual']]),'',
           '[Complete civil chainages](registers/civil-segments.csv) · [station names and attributes](registers/stations.csv) · [junction records](registers/junctions.csv) · [complete repayment ledger](../finance/baghdad-early-cost_priority-six-month-tranches.csv)','']
    (OUT/'DETAILED-SCHEDULES.md').write_text('\n'.join(parts))


class ProposalDoc(book.BookDocTemplate):
    def afterFlowable(self, flowable):
        super().afterFlowable(flowable)
        if getattr(flowable,'book_bookmark',None) is not None:
            self.notify('TOCEntry',(flowable.book_level,flowable.book_title,self.page,flowable.book_bookmark))


def build_pdf(sources, as_of):
    book.IMAGE_ERRORS.clear(); book._register_fonts(); styles=book._styles()
    width,height=A4; content_width=width-2.9*cm-12; content_height=height-3.1*cm-12
    styles['title'].alignment=0; styles['title'].textColor=colors.HexColor('#102936')
    story=[Spacer(1,3*cm),Paragraph('Baghdad Proposal',styles['title']),
           Paragraph('Urban railway and Iraqi manufacturing<br/>Future national development',styles['subtitle']),
           Spacer(1,.8*cm),Paragraph(f'OpenSourceRail · Planning baseline {as_of}',styles['subtitle']),
           Paragraph('Complete proposal, detailed schedules and technical evidence annexes',styles['subtitle']),
           Paragraph('Prepared for the prospective Iraqi sponsor, Baghdad authorities, operating organisation and financing partners.',styles['body']),
           Paragraph('Baghdad finance only. National expansion is a separate future development programme. Construction and operating approval remain pending.',styles['body']),Spacer(1,.5*cm)]
    story.extend(book._image_flowables({'attrs':{'url':'baghdad-network-map.png'},'children':[{'type':'text','raw':'Baghdad planning network'}]},OUT/'BAGHDAD-PROPOSAL.md',styles,max_width=content_width,max_height=9.5*cm,max_px=1600,quality=85))
    story.extend([PageBreak(),Paragraph('Contents',styles['h1'])])
    toc=TableOfContents(); toc.levelStyles=[ParagraphStyle('TOC',fontName=styles['body'].fontName,fontSize=9,leading=13,leftIndent=0,firstLineIndent=0,spaceBefore=4)]
    story += [toc,PageBreak()]
    for index,path in enumerate(sources):
        if index: story.append(PageBreak())
        title=book._markdown_title(path)
        story.append(book._outline_heading(title,styles['h1'],f'chapter-{index}',0))
        relative=path.relative_to(ROOT).as_posix()
        source_url=book.REPOSITORY_BLOB_URL+'/'+quote(relative,safe='/')
        story.append(Paragraph('Source: <link href="'+html.escape(source_url,quote=True)+'" color="#2563eb">'+html.escape(relative)+'</link>',styles['source']))
        story.extend(book._render_markdown(path,styles,content_width,content_height,1600,85,True))
    if book.IMAGE_ERRORS: raise ValueError('Missing proposal images: '+str(book.IMAGE_ERRORS))
    def footer(canv,doc):
        canv.saveState();canv.setFont(styles['small'].fontName,7)
        canv.setFillColor(colors.HexColor('#52616A'));canv.drawString(1.45*cm,.75*cm,'OpenSourceRail Baghdad Proposal · '+as_of+' · planning only')
        canv.drawRightString(width-1.45*cm,.75*cm,str(doc.page));canv.restoreState()
    doc=ProposalDoc(str(OUT/'Baghdad-Proposal.pdf'),pagesize=A4,leftMargin=1.45*cm,rightMargin=1.45*cm,topMargin=1.55*cm,bottomMargin=1.55*cm,
                    title='Baghdad Proposal',author='OpenSourceRail',invariant=1)
    doc.multiBuild(story,onFirstPage=footer,onLaterPages=footer)


def source_inputs():
    tracked=subprocess.check_output(['git','ls-files',str(CITY.relative_to(ROOT)),str((COUNTRY/'finance').relative_to(ROOT))],cwd=ROOT,text=True).splitlines()
    paths={ROOT/p for p in tracked if not publication_output(ROOT/p) and (ROOT/p).is_file()}
    paths.update(COUNTRY.glob('*/design.toml')); paths.update(p.parent/(tomllib.loads(p.read_text())['city']['slug']+'.toml') for p in COUNTRY.glob('*/design.toml'))
    paths.update(COUNTRY.glob('*/README.md'))
    paths.update(ROOT/p for p in SHARED)
    for name in ('access','clearance'):
        report=read_json(CITY/f'engineering/{name}/summary.json')
        paths.update(ROOT/relative for relative in report['sources_sha256'])
    paths.add(ROOT/'tools/automation/fetch-clearance-terrain.py')
    paths.update([COUNTRY/'NATIONAL-BRIEF.md',COUNTRY/'IRAQ-FUNDING-PROGRAMME.md',ROOT/'tools/automation/build-baghdad-proposal.py',
                  ROOT/'tools/automation/build-doc-book.py',ROOT/'tools/automation/generate-national-briefs.py',ROOT/'tools/automation/baghdad_funding_analysis.py',
                  ROOT/'tools/automation/generate-iraq-funding-programme.py',ROOT/'design/city-generation/src/osr_scenario/capital.py',
                  ROOT/'design/city-generation/src/osr_scenario/network_readme.py',ROOT/'lib/templates/capex-costs.toml',
                  ROOT/'lib/templates/rolling-stock.toml',ROOT/'lib/templates/iraq-funding.toml',ROOT/'lib/templates/baghdad-finance-options.toml'])
    paths.update(ROOT/relative for relative in read_json(COUNTRY/'finance/baghdad-programme.json')['sources_sha256'])
    paths.update((ROOT/'lib/templates').glob('*.toml'))
    paths.add(CITY/'corridors.json')
    paths.update([CITY/'publication-manifest.json',ROOT/'tools/automation/publish-city-summary.py',
        ROOT/'tools/automation/rework-baghdad-alignment.py',ROOT/'tools/automation/render-baghdad-alignment-review.py',
        ROOT/'tools/automation/regenerate-baghdad-studies.py',ROOT/'tools/automation/regenerate-city.sh'])
    paths.update((ROOT/'crates/osr-design/src').glob('*.rs'))
    paths.update((ROOT/'design/city-generation/src/osr_scenario').glob('*.py'))
    paths.add(ROOT/'design/city-generation/pyproject.toml')
    # Public hardware/ERP design inputs; never private site data.
    detail=read_json(CITY/'engineering/detail/register.json')
    paths.update(ROOT/relative for relative in detail['sources_sha256'])
    paths.update(CITY.glob('DETAILED-ENGINEERING.md'))
    paths.update(p for p in (CITY/'engineering/detail').glob('*') if p.is_file())
    resilience=read_json(CITY/'engineering/delivery-risk/summary.json')
    paths.update(ROOT/relative for relative in resilience['sources_sha256'])
    paths.update(p for p in (CITY/'engineering/delivery-risk').glob('*') if p.is_file())
    qualification=read_json(CITY/'engineering/qualification/summary.json')
    paths.update(ROOT/relative for relative in qualification['sources_sha256'])
    paths.update(p for p in (CITY/'engineering/qualification').glob('*') if p.is_file())
    redesign=read_json(CITY/'engineering/financing-redesign/summary.json')
    paths.update(ROOT/relative for relative in redesign['sources_sha256'])
    paths.update(p for p in (CITY/'engineering/financing-redesign').glob('*') if p.is_file())
    equity=read_json(CITY/'engineering/equity/summary.json')
    paths.update(ROOT/relative for relative in equity['sources_sha256'])
    paths.update(p for p in (CITY/'engineering/equity').glob('*') if p.is_file())
    rentals=read_json(CITY/'engineering/viaduct-rentals/summary.json')
    paths.update(ROOT/relative for relative in rentals['sources_sha256'])
    paths.update(p for p in (CITY/'engineering/viaduct-rentals').glob('*') if p.is_file())
    delivery=read_json(CITY/'engineering/delivery-baseline/summary.json')
    paths.update(ROOT/relative for relative in delivery['sources_sha256'])
    paths.update(ROOT/relative for relative in delivery['external_outputs_sha256'])
    paths.update(p for p in (CITY/'engineering/delivery-baseline').glob('*') if p.is_file())
    closure=read_json(CITY/'engineering/delivery-closure/summary.json')
    paths.update(ROOT/relative for relative in closure['sources_sha256'])
    paths.update(p for p in (CITY/'engineering/delivery-closure').glob('*') if p.is_file())
    viaduct=read_json(CITY/'engineering/viaduct-comparison/summary.json')
    paths.update(ROOT/relative for relative in viaduct['sources_sha256'])
    paths.update(p for p in (CITY/'engineering/viaduct-comparison').glob('*') if p.is_file())
    revised=read_json(CITY/'engineering/programme-recalculation/summary.json')
    paths.update(ROOT/relative for relative in revised['sources_sha256'])
    paths.update(p for p in (CITY/'engineering/programme-recalculation').glob('*') if p.is_file())
    factory=read_json(CITY/'engineering/factory/summary.json')
    paths.update(ROOT/relative for relative in factory['sources_sha256'])
    paths.update(p for p in (CITY/'engineering/factory').glob('*') if p.is_file())
    # Exact full task payload is deliberately excluded from Git outside this archive.
    ops=read_json(CITY/'operations/baghdad-operations-manifest.json');paths.add(CITY/'operations'/ops['file'])
    # Retained solver/geospatial outputs complete the evidence where materialised.
    for subpath in ('engineering/gis','engineering/sumo','engineering/energy'):
        paths.update(path for path in (CITY/subpath).glob('*') if path.is_file() and path.suffix in ('.gpkg','.xml','.json'))
    return sorted(paths)


def verify():
    manifest=read_json(OUT/'manifest.json')
    for group in ('inputs','outputs'):
        for relative,value in manifest[group].items():
            if receipt(ROOT/relative) != value: raise ValueError('Proposal '+group+' changed: '+relative)
    with zipfile.ZipFile(OUT/'Baghdad-Proposal-Supporting-Data.zip') as archive:
        if archive.testzip() is not None: raise ValueError('Corrupt proposal archive')
        if set(archive.namelist()) != set(manifest['archive_members']): raise ValueError('Archive inventory mismatch')
        members=read_json(OUT/'archive-manifest.json')['members']
        for relative,value in members.items():
            raw=archive.read(relative)
            if len(raw)!=value['bytes'] or hashlib.sha256(raw).hexdigest()!=value['sha256']:
                raise ValueError('Archive member checksum mismatch: '+relative)
    print('Baghdad proposal: source/output hashes and archive CRCs pass')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.check: verify();return 0
    OUT.mkdir(parents=True,exist_ok=True)
    d=tomllib.loads((CITY/'design.toml').read_text());s=tomllib.loads((CITY/'baghdad.toml').read_text())
    p=read_json(COUNTRY/'finance/baghdad-programme.json');f=read_json(CITY/'engineering/finance/summary.json')
    check_baseline(p,read_json(CITY/'package-manifest.json'))
    n=national_context(p);ops=read_json(CITY/'operations/baghdad-operations-manifest.json')['totals']
    continuation=read_json(CITY/'engineering/delivery-closure/finance-reconciled_full_fleet.json')
    revised=read_json(CITY/'engineering/programme-recalculation/summary.json')
    deployment=read_json(CITY/'engineering/deployment/summary.json')
    (OUT/'BAGHDAD-PROPOSAL.md').write_text(build_narrative(d,s,p,f,n,ops,deployment))
    (OUT/'national-context.json').write_text(json.dumps(n,indent=2,sort_keys=True)+'\n')
    early=read_json(COUNTRY/'finance/baghdad-early-repayment.json')['cases']['cost_priority']
    write_registers(d,s,early)
    city_docs=sorted(path for path in CITY.rglob('*.md') if not publication_output(path))
    sources=[OUT/'BAGHDAD-PROPOSAL.md',OUT/'DETAILED-SCHEDULES.md',*city_docs,COUNTRY/'IRAQ-FUNDING-PROGRAMME.md',COUNTRY/'NATIONAL-BRIEF.md',*[ROOT/p for p in SHARED]]
    (OUT/'appendix-sources.json').write_text(json.dumps([p.relative_to(ROOT).as_posix() for p in sources],indent=2)+'\n')
    as_of=max(tomllib.loads((ROOT/'lib/templates/iraq-funding.toml').read_text())['model']['as_of'],
        read_json(CITY/'engineering/delivery-closure/summary.json')['as_of'],
        read_json(CITY/'engineering/equity/summary.json')['as_of'],read_json(CITY/'engineering/viaduct-rentals/summary.json')['as_of'])
    build_pdf(sources,as_of)
    inputs=source_inputs()
    inventory=[{'path':path.relative_to(ROOT).as_posix(),**receipt(path)} for path in inputs]
    write_csv(OUT/'source-inventory.csv',inventory)
    generated=[OUT/name for name in PUBLICATION_FILES if name not in ('Baghdad-Proposal-Supporting-Data.zip','manifest.json','archive-manifest.json')]
    generated.extend(sorted((OUT/'registers').glob('*.csv')))
    archive_members={path.relative_to(ROOT).as_posix():path for path in inputs+generated}
    archive_receipts={relative:receipt(path) for relative,path in sorted(archive_members.items())}
    (OUT/'archive-manifest.json').write_text(json.dumps({'schema_version':'1.0','members':archive_receipts,'self_hash_excluded':True},indent=2,sort_keys=True)+'\n')
    archive_members[(OUT/'archive-manifest.json').relative_to(ROOT).as_posix()]=OUT/'archive-manifest.json'
    if OUT/'archive-manifest.json' not in generated: generated.append(OUT/'archive-manifest.json')
    archive_path=OUT/'Baghdad-Proposal-Supporting-Data.zip'
    with zipfile.ZipFile(archive_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for relative,path in sorted(archive_members.items()):
            entry=zipfile.ZipInfo(relative,date_time=tuple(int(v) for v in as_of.split('-'))+(0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED;entry.external_attr=0o100644<<16
            archive.writestr(entry,path.read_bytes(),compresslevel=9)
    outputs=generated+[archive_path]
    for path in outputs:
        if path.stat().st_size>MAX_BYTES: raise ValueError('Proposal artifact exceeds repository 50 MiB limit: '+str(path))
    manifest={'schema_version':'1.0','title':'Baghdad Proposal','as_of':as_of,'document_status':'planning-proposal-not-construction-or-operating-release',
              'baghdad_financing_scope':['Baghdad'],'national_development_status':'future-separate-not-funded','factory_count':1,
              'baseline_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'inputs':{path.relative_to(ROOT).as_posix():receipt(path) for path in inputs},
              'outputs':{path.relative_to(ROOT).as_posix():receipt(path) for path in outputs},
              'archive_members':sorted(archive_members),'appendix_document_count':len(sources),
              'facts':{'baghdad_total_capex_usd':p['total_capex_usd'],'baghdad_route_km':p['comparison']['osr_route_km'],
                       'delivery_continuation_capital_usd':continuation['metrics']['total_capital_usd'],
                       'delivery_continuation_terminal_gap_iqd':continuation['metrics']['terminal_supplemental_balance_iqd'],
                       'delivery_continuation_budget_complete':False,
                       'programme_recalculation':revised['finance_cases'],
                       'programme_operating_fte':revised['operating_fte'],
                       'programme_depot_count':revised['depot_count'],
                       'programme_depot_slots':revised['depot_storage_slots'],
                       'programme_budget_complete':False,
                       **financial_narrative_facts(p),
                       'baghdad_station_count':len(d['stations']),'baghdad_government_share':p['government_share_of_total_capital'],
                       'national_total_capital_usd':n['total_national_capital_usd'],'national_incremental_after_baghdad_usd':n['future_incremental_city_capital_after_baghdad_usd']}}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    verify(); print(f'Published proposal with {len(sources)} document chapters and {len(inputs)} source files')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
