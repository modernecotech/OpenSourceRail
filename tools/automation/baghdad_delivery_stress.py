"""Deterministic delivery/finance stresses with selected production lanes frozen.

Preserves baseline lane order rather than claiming an optimal recovery schedule.
Separate exclusive running-path calendars expose queues inside acceptance bays.
All costs and disturbance magnitudes are engineering scenarios, not quotations.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
CITY = ROOT / 'cities/catalogue/west-asia/Iraq/Baghdad'
OUT = CITY / 'engineering/delivery-risk'
sys.path.insert(0, str(ROOT / 'design/city-generation/src'))
from osr_scenario.iraq_finance import city_funding_config, scheduled_requirements, run_case
from baghdad_funding_analysis import capital_projection, price_operating, simulate


def next_slot(start, duration, outages):
    """Non-preemptive reservations in half-open working-hour intervals."""
    for left, right in sorted(outages):
        if start < right and start + duration > left:
            start = right
    return start


def schedule(tasks, factory, settings):
    """Use frozen cells, resource-lane edges and full-fleet scope; never resize."""
    stages = {s['package']: s for s in factory['stages']}
    ready = factory['factory_ready_working_day'] + settings.get('factory_delay_days', 0)
    availability = settings.get('availability', .85)
    if not 0 < availability <= 1:
        raise ValueError('availability must lie in (0,1]')
    paths = [ready * 8] * 2
    results = {}
    stock = sorted({r['asset_id'] for r in tasks if r['asset_type'] == 'rolling-stock'})
    # Evenly distribute rework over delivery order, not an extra purchased train.
    delivery_order = sorted(stock, key=lambda a: min(r['planned_start_day'] for r in tasks if r['asset_id'] == a))
    rework_count = math.floor(len(stock) * settings.get('rework_fraction', 0))
    reworked = set(delivery_order[math.floor((i + .5) * len(stock) / rework_count)] for i in range(rework_count))
    for row in sorted(tasks, key=lambda r: (r['planned_start_day'], r['manufacturing_uid'])):
        uid = row['manufacturing_uid']
        pred = [p.strip() for p in row['schedule_predecessor_uids'].split(';') if p.strip()]
        start = max([row['planned_start_day'] * 8, *[results[p]['end_hour'] for p in pred]])
        duration = row['duration_days'] * 8
        is_stock = row['asset_type'] == 'rolling-stock'
        if is_stock:
            stage = stages[row['package_id']]
            duration = math.ceil(stage['cycle_working_days'] / availability) * 8
            duration += (row['duration_days'] - stage['planned_occupation_days']) * 8
            start = max(start, ready * 8)
            if row['resource_lane'] > stage['cells'] // 2:
                start = max(start, (ready + settings.get('hiring_ramp_days', 0)) * 8)
            if row['package_id'] == 'rs-10-material-kit' and settings.get('supplier_outage_days'):
                start = next_slot(start, duration, [(600 * 8, (600 + settings['supplier_outage_days']) * 8)])
            if row['asset_id'] in reworked and row['package_id'] in ('rs-40-fitout-static-test', 'rs-50-dynamic-commissioning'):
                duration += math.ceil(stage['planned_occupation_days'] * .5) * 8
        elif row.get('line') in ('line-8', 'line-9'):
            start = max(start, (row['planned_start_day'] + settings.get('civil_access_days', 0)) * 8)
        if not is_stock and row['asset_type'] != 'system' and settings.get('civil_cycle_factor'):
            # Separate unqualified acceleration study, with the same lane count.
            start = max([0, *[results[p]['end_hour'] for p in pred]])
            duration = max(8, math.ceil(row['duration_days'] * settings['civil_cycle_factor']) * 8)
        end = start + duration
        path_id = None
        path_start = path_end = None
        if is_stock and row['package_id'] == 'rs-50-dynamic-commissioning':
            shifts = settings.get('test_shifts', 1)
            # Hours map to an eight-hour primary production calendar; two test
            # shifts deliver twice the test hours per primary working day.
            duty = math.ceil(16 * (2 if row['asset_id'] in reworked else 1) / (availability * shifts))
            candidates = []
            for index, clock in enumerate(paths):
                outages = [(900 * 8, (900 + settings['path_outage_days']) * 8)] if index == 1 and settings.get('path_outage_days') else []
                slot = next_slot(max(start + 8, clock), duty, outages)
                candidates.append((slot, index))
            path_start, path_id = min(candidates)
            path_end = path_start + duty
            paths[path_id] = path_end
            end = max(end, path_end + 8)
        results[uid] = dict(manufacturing_uid=uid, asset_id=row['asset_id'], line=row['line'],
                            asset_type=row['asset_type'], resource_pool=row['resource_pool'],
                            resource_lane=row['resource_lane'], start_hour=start, end_hour=end,
                            test_path=path_id, test_start_hour=path_start, test_end_hour=path_end)
    lines = []
    shared = max(r['end_hour'] for r in results.values() if not r['line'] or r['asset_type'] in ('depot', 'depots-production'))
    for line in sorted({r['line'] for r in results.values() if r['line']}):
        members = [r for r in results.values() if r['line'] == line]
        fleet = max(r['end_hour'] for r in members if r['asset_type'] == 'rolling-stock')
        civil = max(r['end_hour'] for r in members if r['asset_type'] != 'rolling-stock')
        complete = math.ceil(max(fleet, civil, shared) / 8) - 1
        lines.append(dict(line=line, fleet_completion_day=math.ceil(fleet / 8) - 1,
                          infrastructure_completion_day=math.ceil(civil / 8) - 1,
                          opening_month=math.floor((complete + 30) * 12 / 260) + 1 + 3,
                          weight=len({r['asset_id'] for r in members if r['asset_type'] == 'rolling-stock'}) / len(stock)))
    return dict(tasks=list(results.values()), phases=lines, rework_trainsets=rework_count,
                factory_ready_day=ready, capacity=factory['resource_capacity'])


def finance(delivery, settings, context):
    config, options, programme, city_finance, factory = context
    tasks = {r['manufacturing_uid']: r for r in delivery['tasks']}
    # Context is deliberately a tuple of audited inputs; no global scenario state.
    contracts = deepcopy(city_finance['_contracts'])
    for contract in contracts:
        row = tasks[contract['manufacturing_uid']]
        contract.update(planned_start_day=row['start_hour'] // 8,
                        planned_finish_day=math.ceil(row['end_hour'] / 8) - 1)
    buckets = deepcopy(city_finance['capex_usd']['procurement_origin_buckets'])
    if delivery['rework_trainsets']:
        cost = delivery['rework_trainsets'] * 25000.
        buckets.append(dict(bucket='delivery_rework_local', total_usd=cost, imported_usd=0.))
        contracts.append(dict(bucket='delivery_rework_local', budget_usd=cost, imported_share=0.,
                              planned_start_day=delivery['factory_ready_day'],
                              planned_finish_day=max(p['fleet_completion_day'] for p in delivery['phases'])))
    factory_contracts = [dict(bucket=bucket, budget_usd=cost, imported_share=share, planned_start_day=0,
                              planned_finish_day=delivery['factory_ready_day'])
                         for bucket, cost, share in (('production_plant', factory['budgeted_plant_direct_usd'], .2),
                                                     ('epc_overhead', factory['budgeted_plant_epc_usd'], .15))]
    if settings.get('test_shifts', 1) > 1:
        factory_contracts += [dict(bucket=bucket, budget_usd=cost, imported_share=share,
                                   planned_start_day=max(0, delivery['factory_ready_day'] - 60),
                                   planned_finish_day=delivery['factory_ready_day'])
                              for bucket, cost, share in (('production_plant', 1500000., .2), ('epc_overhead', 105000., .15))]
    factory_buckets = []
    for bucket in ('production_plant', 'epc_overhead'):
        rows = [c for c in factory_contracts if c['bucket'] == bucket]
        factory_buckets.append(dict(bucket=bucket, total_usd=sum(r['budget_usd'] for r in rows),
                                    imported_usd=sum(r['budget_usd'] * r['imported_share'] for r in rows)))
    city_case = run_case(scheduled_requirements(contracts, buckets, config),
                         programme['operating_receipts']['total_annual_usd'],
                         city_finance['annual_opex_usd']['total'], config, operating_phases=delivery['phases'])
    plant_case = run_case(scheduled_requirements(factory_contracts, factory_buckets, config), 0, 0, config)
    operating = []
    receipts = programme['operating_receipts']
    for month in range(max(len(city_case['monthly']), len(plant_case['monthly']))):
        rows = [c['monthly'][month] for c in (city_case, plant_case) if month < len(c['monthly'])]
        plant = plant_case['monthly'][month] if month < len(plant_case['monthly']) else {}
        revenue = sum(r['revenue_usd'] for r in rows)
        operating.append(dict(month=month, revenue_usd=revenue, opex_usd=sum(r['opex_usd'] for r in rows),
                              fare_revenue_usd=revenue * receipts['farebox_annual_usd'] / receipts['total_annual_usd'],
                              nonfare_revenue_usd=revenue * receipts['existing_nonfare_annual_usd'] / receipts['total_annual_usd'],
                              factory_debt_service_usd=plant.get('debt_service_usd', 0.),
                              factory_reserve_usd=plant.get('closing_restricted_reserve_usd', 0.),
                              chinese_commitment_fee_usd=sum(r['chinese_export_credit_fees_usd'] - r['chinese_export_credit_draw_usd'] * config['chinese_export_credit']['arrangement_fee'] for r in rows)))
    operating[0]['phases'] = delivery['phases']
    fares = options['fares']
    operating, pricing = price_operating(operating, receipts, programme['comparison']['fare_iqd'],
                                        config['model']['iqd_per_usd'], options,
                                        annual_fare=fares['annual_increase'], annual_opex=fares['opex_inflation'],
                                        annual_income=fares['income_growth'], elasticity=fares['price_elasticity'],
                                        annual_price_inflation=fares['general_price_inflation'])
    payroll = 0.
    if settings.get('test_shifts', 1) > 1:
        # Existing train CAPEX contains baseline manufacturing labour. This is
        # incremental test crew only, including before passenger revenue starts.
        annual = programme['comparison']['operating_labour_annual_iqd'] / programme['comparison']['operating_fte'] * 52 / config['model']['iqd_per_usd']
        first = math.floor((delivery['factory_ready_day'] + 30) * 12 / 260)
        last = math.ceil((max(p['fleet_completion_day'] for p in delivery['phases']) + 31) * 12 / 260)
        for row in operating:
            if first <= row['month'] < last:
                extra = annual / 12 * (1 + fares['opex_inflation']) ** (row['month'] // 12)
                row['opex_usd'] += extra
                payroll += extra
    eligible = set(options['green']['candidate_buckets'])
    capital = capital_projection(contracts + factory_contracts, config, eligible)
    for month, row in capital_projection(factory_contracts, config, eligible).items():
        capital[month].update(factory_capex=row['capex'], factory_imports=row['imports'])
    liquidity = options['liquidity']
    result = simulate(capital, operating, config, options, green='blended', extras=True,
                      bridge_rate=liquidity['concessional_annual_rate'], bridge_fee=liquidity['concessional_draw_fee'],
                      repayment_policy='cost_priority')
    result['metrics'].update(incremental_test_payroll_usd=payroll,
                             total_capital_usd=sum(r['capex'] for r in capital.values()),
                             incremental_recovery_capital_usd=1605000. if settings.get('test_shifts', 1) > 1 else 0.)
    return result


def write_csv(path, rows):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        report = json.loads((OUT / 'summary.json').read_text())
        for rel, digest in report['sources_sha256'].items():
            if hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() != digest:
                raise ValueError('Stale delivery stress input: ' + rel)
        for rel, digest in report['outputs_sha256'].items():
            if hashlib.sha256((OUT / rel).read_bytes()).hexdigest() != digest:
                raise ValueError('Changed delivery stress output: ' + rel)
        print('Delivery resilience inputs and output hashes pass'); return
    paths = [Path(__file__), Path(__file__).with_name('baghdad_funding_analysis.py'),
             ROOT / 'design/city-generation/src/osr_scenario/iraq_finance.py',
             ROOT / 'lib/templates/baghdad-factory.toml', ROOT / 'lib/templates/iraq-funding.toml',
             ROOT / 'lib/templates/baghdad-finance-options.toml',
             CITY / 'operations/baghdad-operations.json.gz', CITY / 'engineering/factory/summary.json',
             CITY / 'engineering/finance/summary.json', CITY.parent / 'finance/baghdad-programme.json']
    programme = json.loads(paths[-1].read_text())
    city_finance = json.loads(paths[-2].read_text())
    factory = json.loads(paths[-3].read_text())
    payload = json.loads(gzip.decompress(paths[-4].read_bytes()))
    city_finance['_contracts'] = payload['project_twin']['budget_contracts']
    config = city_funding_config(tomllib.loads(paths[4].read_text()), 'baghdad')
    options = tomllib.loads(paths[5].read_text())
    combined = dict(factory_delay_days=130, supplier_outage_days=130, hiring_ramp_days=260,
                    rework_fraction=.1, path_outage_days=130, civil_access_days=130, availability=.75)
    cases = dict(calendar_baseline={}, factory_delay_6months=dict(factory_delay_days=130),
                 supplier_shortage_6months=dict(supplier_outage_days=130),
                 half_staff_late_12months=dict(hiring_ramp_days=260),
                 rework_10pct=dict(rework_fraction=.1), one_test_path_outage_6months=dict(path_outage_days=130),
                 civil_access_6months=dict(civil_access_days=130), availability_75pct=dict(availability=.75),
                 availability_65pct=dict(availability=.65), combined=combined,
                 combined_second_test_shift=dict(combined, test_shifts=2),
                 availability_75pct_second_test_shift=dict(availability=.75, test_shifts=2),
                 civil_cycles_20pct_faster=dict(civil_cycle_factor=.8))
    OUT.mkdir(parents=True, exist_ok=True)
    report = dict(schema='baghdad-frozen-delivery-stress-v1', status='unqualified-deterministic-planning-study',
                  financing_committed=False, operational_release=False, capacity=factory['resource_capacity'],
                  factory_cells={s['package']: s['cells'] for s in factory['stages']}, test_paths=2,
                  canonical_opening_months=[p['opening_month'] for p in city_finance['structured_financing']['phased_opening']['phases']],
                  sources_sha256={p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                  cases={})
    table = []
    for name, settings in cases.items():
        delivery = schedule(payload['manufacturing_tasks'], factory, settings)
        result = finance(delivery, settings, (config, options, programme, city_finance, factory))
        report['cases'][name] = dict(settings=settings, phases=delivery['phases'], metrics=result['metrics'],
                                    rework_trainsets=delivery['rework_trainsets'], capacity=delivery['capacity'])
        write_csv(OUT / (name + '-schedule.csv'), delivery['tasks'])
        write_csv(OUT / (name + '-six-month-finance.csv'), result['semiannual'])
        if name in ('calendar_baseline', 'combined', 'combined_second_test_shift'):
            write_csv(OUT / (name + '-monthly-finance.csv'), result['monthly'])
        metrics = result['metrics']
        table.append(dict(case=name, first_opening_month=min(p['opening_month'] for p in delivery['phases']),
                          full_opening_month=max(p['opening_month'] for p in delivery['phases']),
                          peak_gap_debt_iqd=metrics['peak_supplemental_balance_iqd'],
                          terminal_gap_debt_iqd=metrics['terminal_supplemental_balance_iqd'],
                          uncovered_cash_usd=metrics['uncovered_support_iqd'] / config['model']['iqd_per_usd'],
                          all_debt_cleared_month=metrics['all_debt_cleared_month'],
                          total_interest_fees_usd=metrics['total_finance_interest_and_fees_usd'],
                          incremental_test_payroll_usd=metrics['incremental_test_payroll_usd'],
                          incremental_recovery_capital_usd=metrics['incremental_recovery_capital_usd']))
        print(name, table[-1]['first_opening_month'], table[-1]['full_opening_month'], flush=True)
    write_csv(OUT / 'scenario-comparison.csv', table)
    lines = ['# Baghdad frozen-resource delivery and funding study', '',
             'These are deterministic disturbances, not P80/P90 dates or measured failure rates. All 831 planned six-car trains must pass acceptance before their line opens. Selected stage cells, civil crew lanes and dispatch order remain fixed in every stress. No stress calls the capacity-sizing search.', '',
             'The explicit two-path calendar books 16 exclusive running hours per train at the case availability, inside acceptance-bay occupation, with setup and clearance. This adds a conservative calendar audit to the published average-throughput check. Baseline lane order is preserved; a replanned optimal dispatch might recover some delay. Financial-close months include 30 pre-NTP working days and three commissioning months.', '',
             '| Case | First/full month | Peak IQD gap debt, tn | Interest/fees USD eq, bn | Debt cleared month |',
             '|---|---:|---:|---:|---:|']
    for row in table:
        lines.append(f"| {row['case']} | {row['first_opening_month']}/{row['full_opening_month']} | {row['peak_gap_debt_iqd']/1e12:.3f} | {row['total_interest_fees_usd']/1e9:.3f} | {row['all_debt_cleared_month']} |")
    lines += ['', 'Disturbances: factory readiness +130 working days; imported kit shortage days 600–730; half the stage lanes staffed 260 days after factory readiness; 83 trains with half-cycle additional fit-out/acceptance and double running-test duty; path 2 unavailable days 900–1030; line 8/9 civil access +130 days; and reduced productive availability. Combined applies these together at 75% availability.', '',
              'Recovery uses the same two segregated paths with a funded second eight-hour test shift. It adds 52 indicative test staff, USD 1.5m direct lighting/training allowance plus 7% EPC, and incremental payroll indexed 5% from financial close throughout train production, including before fares. Baseline factory labour remains in train CAPEX. The payroll rate uses the existing Iraqi operating labour proxy and needs a shift-pay quotation. Origin shares are unqualified 20% direct/15% EPC. Rework adds USD 25,000 local material/service allowance per affected train. Supplier expediting and unused plant carrying costs are not priced; stress costs are lower bounds, not risk contingencies.', '',
              'Every case rebuilds capital invoices, line revenue ramps, existing kiosk/advertising receipts, 5% fare/OPEX/income growth, USD import credit and IQD domestic/green/gap debt, reserves and surplus repayments. Government capital remains 25%, including USD cash for half of imports; Chinese USD credit funds the other half. Half-year files show actual native-currency draw/service requirements rather than treating a guarantee as cash. Green terms, grants, development rights, additional receipts and the 2% gap facility remain uncommitted, with an IQD 13tn illustrative gap limit. Capital budgets are not inflation-escalated.', '',
              'The civil acceleration case shortens every non-stock infrastructure occupation by 20%, retains crew counts and the baseline dependency/resource lane graph, and propagates the same lane dependencies. It is a diagnostic upper-bound productivity assumption, not a costed accelerated construction plan. Validate workfront access, casting-bed/mould output and curing, piling rigs and foundation tests, track-panel logistics and installation, station systems and energy handovers together. Seek measured cycles, geotechnical quantities, supplier rates and Iraqi contractor quotes before pricing extra workfronts or casting capacity. Full-fleet readiness remains an opening constraint; civil acceleration alone cannot bypass it.', '',
              'Before construction release, qualify six-car cycles and staffing through the first article; obtain tooling/battery/bogie delivery quotes, recruit and train shift crews, prove test-track safe segregation, and secure land/utility/access permits. Recovery funding and a revised accepted baseline require separate approval. All operational release gates remain unchanged.', '',
              '[Scenario comparison](scenario-comparison.csv) · [Machine-readable assumptions/results](summary.json) · [Baseline half-year funding](calendar_baseline-six-month-finance.csv) · [Combined stress half-year funding](combined-six-month-finance.csv) · [Funded recovery half-year funding](combined_second_test_shift-six-month-finance.csv)', '']
    (OUT / 'README.md').write_text('\n'.join(lines))
    report['outputs_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir()) if p.name != 'summary.json'}
    (OUT / 'summary.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
