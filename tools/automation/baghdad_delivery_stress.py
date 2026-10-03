"""Deterministic delivery/finance stresses with selected production lanes frozen.

Preserves baseline lane order rather than claiming an optimal recovery schedule.
Separate exclusive running-path calendars expose queues inside acceptance bays.
All costs and disturbance magnitudes are engineering scenarios, not quotations.
"""
from __future__ import annotations

import argparse
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


def production_duration(stage, availability, staffed_hours_factor, fixed_hold_days):
    """Compress only staffed occupation; fixed holds occupy the bay unchanged.

    Holds are conservative working-calendar equivalents pending timed process
    routings, not a claim that curing stops at night. Unshifted totals preserve
    the reviewed availability schedule exactly, including its rounding.
    """
    if not math.isfinite(staffed_hours_factor) or staffed_hours_factor < 1:
        raise ValueError('staffed hours factor must be finite and at least one')
    total = math.ceil(stage['cycle_working_days'] / availability)
    if isinstance(fixed_hold_days, bool) or not isinstance(fixed_hold_days, int) or not 0 <= fixed_hold_days <= stage['cycle_working_days']:
        raise ValueError('fixed process hold must be an integer within the unshifted cycle')
    return fixed_hold_days + math.ceil((total - fixed_hold_days) / staffed_hours_factor)


def schedule(tasks, factory, settings):
    """Use frozen cells, resource-lane edges and full-fleet scope; never resize."""
    stages = {s['package']: s for s in factory['stages']}
    ready = factory['factory_ready_working_day'] + settings.get('factory_delay_days', 0)
    availability = settings.get('availability', .85)
    if not 0 < availability <= 1:
        raise ValueError('availability must lie in (0,1]')
    civil_factor = settings.get('civil_cycle_factor', 1.)
    if isinstance(civil_factor, bool) or not isinstance(civil_factor, (int, float)) or not math.isfinite(civil_factor) or not 0 < civil_factor <= 1:
        raise ValueError('civil cycle multiplier must lie in (0,1]')
    timing = settings.get('civil_timing', 'retained')
    if timing not in ('retained', 'earliest'):
        raise ValueError('unknown civil investment timing')
    prototype = min((r for r in tasks if r['asset_type'] == 'rolling-stock'), key=lambda r: r['planned_start_day'])['asset_id']
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
            extra_hours = settings.get('production_hours_factor', 1.) if row['package_id'] in settings.get('production_shift_stages', []) else 1.
            duration = production_duration(stage, availability, extra_hours,
                       settings.get('fixed_process_holds', {}).get(row['package_id'], 0)) * 8
            duration += (row['duration_days'] - stage['planned_occupation_days']) * 8
            release = ready
            if settings.get('temporary_first_article_ready_day'):
                # Only the already-in-scope first train uses the temporary line;
                # series awaits its acceptance and the permanent plant. Running
                # tests still wait for the permanent segregated paths/bays.
                if row['asset_id'] == prototype and row['package_id'] != 'rs-50-dynamic-commissioning':
                    release = settings['temporary_first_article_ready_day']
                start = max([release * 8, *[results[p]['end_hour'] for p in pred]])
            start = max(start, release * 8)
            if row['resource_lane'] > stage['cells'] // 2:
                start = max(start, (ready + settings.get('hiring_ramp_days', 0)) * 8)
            if row['package_id'] == 'rs-10-material-kit' and settings.get('supplier_outage_days'):
                start = next_slot(start, duration, [(600 * 8, (600 + settings['supplier_outage_days']) * 8)])
            if row['asset_id'] in reworked and row['package_id'] in ('rs-40-fitout-static-test', 'rs-50-dynamic-commissioning'):
                duration += math.ceil(stage['planned_occupation_days'] * .5) * 8
        elif row.get('line') in ('line-8', 'line-9'):
            start = max(start, (row['planned_start_day'] + settings.get('civil_access_days', 0)) * 8)
        if not is_stock and row['asset_type'] != 'system':
            # Productivity and investment timing are independent interventions.
            # A 1.0 factor with retained timing must be an exact identity.
            if timing == 'earliest' or row['asset_id'] in settings.get('early_civil_assets', []):
                start = max([0, *[results[p]['end_hour'] for p in pred]])
            duration = max(8, math.ceil(row['duration_days'] * civil_factor) * 8)
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
    # A conservative programme-wide funding stop: unfinished work and exclusive
    # path reservations resume after the same hold. No refused source is silently
    # replaced by liquidity credit; recovered cases require fresh placement.
    pause = settings.get('funding_pause_days', 0)
    pause_start = settings.get('funding_pause_start_day', 0)
    if pause:
        def shifted(hour, ending=False):
            affected = hour > pause_start * 8 if ending else hour >= pause_start * 8
            return hour + pause * 8 if affected else hour
        for row in results.values():
            for key in ('start_hour', 'end_hour', 'test_start_hour', 'test_end_hour'):
                if row[key] is not None:
                    row[key] = shifted(row[key], key in ('end_hour', 'test_end_hour'))
        if ready >= pause_start:
            ready += pause
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
    config, options, programme, city_finance, factory, risk_options = context
    config, options = deepcopy(config), deepcopy(options)
    recovery, costs, downside = (risk_options[k] for k in ('recovery', 'costs', 'downside'))
    less_finance = settings.get('less_favourable_finance', False)
    if less_finance:
        for key in ('chinese_export_credit', 'domestic_bonds', 'bank_credit'):
            config[key]['annual_rate'] += downside['core_rate_increment']
        options['liquidity']['illustrative_cap_iqd'] = downside['gap_credit_cap_iqd']
    tasks = {r['manufacturing_uid']: r for r in delivery['tasks']}
    # Context is deliberately a tuple of audited inputs; no global scenario state.
    contracts = deepcopy(city_finance['_contracts'])
    for contract in contracts:
        row = tasks[contract['manufacturing_uid']]
        contract.update(planned_start_day=row['start_hour'] // 8,
                        planned_finish_day=math.ceil(row['end_hour'] / 8) - 1)
    buckets = deepcopy(city_finance['capex_usd']['procurement_origin_buckets'])
    if delivery['rework_trainsets']:
        cost = delivery['rework_trainsets'] * costs['rework_local_usd_per_train']
        buckets.append(dict(bucket='delivery_rework_local', total_usd=cost, imported_usd=0.))
        contracts.append(dict(bucket='delivery_rework_local', budget_usd=cost, imported_share=0.,
                              planned_start_day=delivery['factory_ready_day'],
                              planned_finish_day=max(p['fleet_completion_day'] for p in delivery['phases'])))
    factory_contracts = [dict(bucket=bucket, budget_usd=cost, imported_share=share,
                              planned_start_day=settings.get('funding_pause_days', 0) if settings.get('funding_pause_start_day', 0) == 0 else 0,
                              planned_finish_day=delivery['factory_ready_day'])
                         for bucket, cost, share in (('production_plant', factory['budgeted_plant_direct_usd'], .2),
                                                     ('epc_overhead', factory['budgeted_plant_epc_usd'], .15))]
    added_direct = 0.
    shift_stages = [s for s in factory['stages'] if s['package'] in settings.get('production_shift_stages', [])]
    extra_production_fte = sum(s['direct_crew_fte'] for s in shift_stages) * (settings.get('production_hours_factor', 1.) - 1)
    if settings.get('test_shifts', 1) > 1:
        added_direct += recovery['test_shift_direct_usd']
    if shift_stages:
        added_direct += len(shift_stages) * recovery['production_shift_direct_usd_per_stage'] + extra_production_fte * recovery['recruitment_training_usd_per_fte']
    if settings.get('recruitment_recovery'):
        added_direct += math.ceil(factory['direct_production_crew_fte'] / 2) * recovery['recruitment_training_usd_per_fte']
    if settings.get('temporary_first_article_ready_day'):
        added_direct += recovery['temporary_first_article_direct_usd']
    if added_direct:
        factory_contracts += [dict(bucket=bucket, budget_usd=cost, imported_share=share,
                                   planned_start_day=0 if settings.get('temporary_first_article_ready_day') else max(0, delivery['factory_ready_day'] - 60),
                                   planned_finish_day=settings.get('temporary_first_article_ready_day', delivery['factory_ready_day']))
                              for bucket, cost, share in (('production_plant', added_direct, .2), ('epc_overhead', added_direct * costs['epc_fraction'], .15))]
    restart = settings.get('funding_restart_direct_usd', 0.)
    if restart:
        # Local remobilisation: separately priced, no additional train or
        # manufactured USD import share. Government remains 25% of capital.
        start = settings['funding_pause_start_day'] + settings['funding_pause_days']
        contracts.append(dict(bucket='funding_restart_local', budget_usd=restart * (1 + costs['epc_fraction']),
                              imported_share=0., planned_start_day=start, planned_finish_day=start + 30))
        buckets.append(dict(bucket='funding_restart_local', total_usd=restart * (1 + costs['epc_fraction']), imported_usd=0.))
    section = settings.get('first_section_direct_usd', 0.)
    if section:
        for bucket, amount, share in (('first_section_local', section * .8, 0.),
                                      ('first_section_imports', section * .2, 1.),
                                      ('first_section_epc', section * costs['epc_fraction'], .15)):
            contracts.append(dict(bucket=bucket, budget_usd=amount, imported_share=share,
                                  planned_start_day=120, planned_finish_day=settings['first_section_ready_day']))
            buckets.append(dict(bucket=bucket, total_usd=amount, imported_usd=amount * share))
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
        if section and settings['first_section_opening_month'] <= month < settings['first_section_support_until_month']:
            # A short independently operated section does not activate the
            # entire network's fixed OPEX. Its own staff/energy/maintenance
            # budget is used until the original full-line opening.
            operating[-1]['opex_usd'] = settings['first_section_annual_opex_usd'] / 12
    operating[0]['phases'] = delivery['phases']
    fares = options['fares']
    operating, pricing = price_operating(operating, receipts, programme['comparison']['fare_iqd'],
                                        config['model']['iqd_per_usd'], options,
                                        annual_fare=fares['annual_increase'], annual_opex=downside['opex_escalation_annual'] if settings.get('higher_opex') else fares['opex_inflation'],
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
    salary = programme['comparison']['operating_labour_annual_iqd'] / programme['comparison']['operating_fte'] / config['model']['iqd_per_usd']
    production_start = math.floor((delivery['factory_ready_day'] + 30) * 12 / 260)
    production_end = math.ceil((max(p['fleet_completion_day'] for p in delivery['phases']) + 31) * 12 / 260)
    baseline_production_end = math.ceil((factory['stock_finish_working_day'] + 31) * 12 / 260)
    baseline_production_start = math.floor((factory['factory_ready_working_day'] + 30) * 12 / 260)
    paid_extension_start = production_start + baseline_production_end - baseline_production_start
    baseline_civil_end = math.ceil((factory['infrastructure_target_working_day'] + 31) * 12 / 260)
    civil_end = math.ceil((max(p['infrastructure_completion_day'] for p in delivery['phases']) + 31) * 12 / 260)
    plant_ready_month = math.floor((factory['factory_ready_working_day'] + 30) * 12 / 260)
    incremental_costs = []
    for row in operating:
        month = row['month']; index = (1 + fares['opex_inflation']) ** (month // 12)
        extra_pay = extra_nonlabour = extension = temporary = expedite = section_support = 0.
        if section and math.floor((settings['first_section_ready_day'] + 30) * 12 / 260) <= month < settings['first_section_support_until_month']:
            section_support = settings['first_section_support_fte'] * salary / 12 * index
        if production_start <= month < production_end:
            extra_pay = extra_production_fte * salary / 12 * recovery['extra_shift_pay_factor'] * index
            extra_nonlabour = extra_pay * recovery['extra_shift_nonlabour_fraction_of_payroll']
        if settings.get('temporary_first_article_ready_day'):
            temporary_start = math.floor((settings['temporary_first_article_ready_day'] + 30) * 12 / 260)
            if temporary_start <= month < production_start:
                temporary = recovery['temporary_first_article_support_fte'] * salary / 12 * index
        if settings.get('delay_costs'):
            # Compare staffed span lengths, not absolute completion dates: a
            # pure start delay does not purchase the same crew-months twice.
            funding_hold = settings.get('funding_pause_days', 0)
            if funding_hold and settings['funding_pause_start_day'] > 0 and settings['funding_pause_first_month'] <= month < settings['funding_resume_month']:
                # Retained staff/site costs belong to the actual suspension,
                # not both the suspension and the later completion extension.
                extension += ((factory['direct_production_crew_fte'] + costs['factory_extended_support_fte'] + costs['civil_extended_supervision_fte']) * salary
                              + factory['budgeted_plant_direct_usd'] * costs['plant_nonlabour_carrying_annual_fraction']
                              + city_finance['capex_usd']['reconciled_project_total'] * costs['construction_nonlabour_prolongation_annual_fraction']) / 12 * index
            if not funding_hold and paid_extension_start <= month < production_end:
                extension += (factory['direct_production_crew_fte'] + costs['factory_extended_support_fte']) * salary / 12 * index
                extension += factory['budgeted_plant_direct_usd'] * costs['plant_nonlabour_carrying_annual_fraction'] / 12 * index
            if not funding_hold and plant_ready_month <= month < production_start:
                extension += factory['budgeted_plant_direct_usd'] * costs['plant_nonlabour_carrying_annual_fraction'] / 12 * index
            if not funding_hold and baseline_civil_end <= month < civil_end:
                extension += (costs['civil_extended_supervision_fte'] * salary + city_finance['capex_usd']['reconciled_project_total'] * costs['construction_nonlabour_prolongation_annual_fraction']) / 12 * index
        if settings.get('supplier_expedite') and month == math.floor((600 + 30) * 12 / 260):
            expedite = city_finance['capex_usd']['imported_external_capital'] * recovery['supplier_expedite_fraction_of_city_imports'] * index
        row['opex_usd'] += extra_pay + extra_nonlabour + extension + temporary + expedite + section_support
        if settings.get('lower_demand'):
            row['fare_revenue_usd'] *= downside['ridership_factor']
            row['nonfare_revenue_usd'] *= downside['nonfare_factor']
            row['revenue_usd'] = row['fare_revenue_usd'] + row['nonfare_revenue_usd']
        incremental_costs.append(dict(month=month, production_shift_payroll_usd=extra_pay,
                                      production_shift_nonlabour_usd=extra_nonlabour, delay_extension_usd=extension,
                                      temporary_facility_support_usd=temporary, supplier_expedite_usd=expedite,
                                      first_section_support_usd=section_support))
    eligible = set(options['green']['candidate_buckets'])
    capital = capital_projection(contracts + factory_contracts, config, eligible)
    for month, row in capital_projection(factory_contracts, config, eligible).items():
        capital[month].update(factory_capex=row['capex'], factory_imports=row['imports'])
    if settings.get('funding_pause_days'):
        first = settings['funding_pause_first_month']
        resume = settings['funding_resume_month']
        # A task spanning a stop must not create its 55% midpoint invoice in
        # the suspended period. Defer every due capital use until re-placement.
        for month in sorted(list(capital)):
            if first <= month < resume:
                deferred = capital.pop(month)
                target = capital.setdefault(resume, {})
                for key, value in deferred.items():
                    target[key] = target.get(key, 0.) + value
    escalation = 0.
    if settings.get('capital_escalation'):
        for month, row in capital.items():
            factor = (1 + downside['capital_escalation_annual']) ** (max(0, month) / 12)
            escalation += row['capex'] * (factor - 1)
            for key in row:
                row[key] *= factor
    if settings.get('capital_escalation') or settings.get('funding_pause_days'):
        # Rebuild undrawn Chinese commitment fees from actual invoice draws.
        for row in operating:
            month = row['month']; cohort = sorted(m for m, c in capital.items() if m // 12 == month // 12 and c['imports'] > 0)
            row['chinese_commitment_fee_usd'] = sum(.5 * capital[m]['imports'] for m in cohort if m > month) * config['chinese_export_credit']['undrawn_commitment_fee'] / 12 if cohort and month >= cohort[0] else 0.
    liquidity = options['liquidity']
    result = simulate(capital, operating, config, options, green=None if less_finance else 'blended', extras=not less_finance,
                      bridge_rate=downside['gap_credit_rate'] if less_finance else liquidity['concessional_annual_rate'],
                      bridge_fee=downside['gap_credit_draw_fee'] if less_finance else liquidity['concessional_draw_fee'],
                      repayment_policy='cost_priority')
    nominal_discount = (1 + config['model']['discount_rate']) * (1 + fares['general_price_inflation']) - 1
    unlevered_npv = sum((r['revenue_usd'] - r['opex_usd'] - capital.get(r['month'], {}).get('capex', 0.))
                       / (1 + nominal_discount) ** (r['month'] / 12) for r in operating)
    result['metrics'].update(incremental_test_payroll_usd=payroll,
                             unlevered_project_npv_usd=unlevered_npv, nominal_discount_rate=nominal_discount,
                             total_capital_usd=sum(r['capex'] for r in capital.values()),
                             incremental_recovery_capital_usd=added_direct * (1 + costs['epc_fraction']),
                             funding_restart_capital_usd=restart * (1 + costs['epc_fraction']),
                             first_section_incremental_capital_usd=section * (1 + costs['epc_fraction']),
                             extra_production_fte=extra_production_fte, capital_escalation_usd=escalation,
                             incremental_cost_totals_usd={key: sum(r[key] for r in incremental_costs) for key in incremental_costs[0] if key != 'month'})
    result['metrics']['debt_clearance_month_without_unfunded_support'] = result['metrics']['all_debt_cleared_month'] if result['metrics']['uncovered_support_iqd'] / config['model']['iqd_per_usd'] < .02 else None
    result['incremental_costs'] = incremental_costs
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
             CITY / 'engineering/finance/summary.json', CITY.parent / 'finance/baghdad-programme.json',
             ROOT / 'lib/templates/baghdad-delivery-risk.toml']
    programme = json.loads(paths[9].read_text())
    city_finance = json.loads(paths[8].read_text())
    factory = json.loads(paths[7].read_text())
    payload = json.loads(gzip.decompress(paths[6].read_bytes()))
    city_finance['_contracts'] = payload['project_twin']['budget_contracts']
    config = city_funding_config(tomllib.loads(paths[4].read_text()), 'baghdad')
    options = tomllib.loads(paths[5].read_text())
    risk_options = tomllib.loads(paths[10].read_text())
    recovery = risk_options['recovery']
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
                 civil_cycles_20pct_faster=dict(civil_cycle_factor=.8),
                 civil_earliest_unchanged_cycles=dict(civil_timing='earliest'),
                 civil_earliest_20pct_faster=dict(civil_timing='earliest', civil_cycle_factor=.8),
                 availability_75pct_costed=dict(availability=.75, delay_costs=True),
                 availability_75pct_test_shift_costed=dict(availability=.75, test_shifts=2, delay_costs=True),
                 hiring_ramp_costed=dict(hiring_ramp_days=260, delay_costs=True),
                 supplier_shortage_costed=dict(supplier_outage_days=130, delay_costs=True),
                 availability_75pct_structural_shift=dict(availability=.75, delay_costs=True, production_shift_stages=['rs-20-carbody-bogie'], production_hours_factor=recovery['extra_production_hours_factor']),
                 availability_75pct_electrical_shift=dict(availability=.75, delay_costs=True, production_shift_stages=['rs-30-traction-battery-control'], production_hours_factor=recovery['extra_production_hours_factor']),
                 availability_75pct_composite_shift=dict(availability=.75, delay_costs=True, production_shift_stages=['rs-23-moulded-body-modules'], production_hours_factor=recovery['extra_production_hours_factor']),
                 availability_75pct_all_stage_shifts=dict(availability=.75, delay_costs=True, production_shift_stages=[s['package'] for s in factory['stages']], production_hours_factor=recovery['extra_production_hours_factor'], test_shifts=2),
                 recruitment_training_recovery=dict(hiring_ramp_days=130, delay_costs=True, production_shift_stages=[], recruitment_recovery=True),
                 supplier_expedite_recovery=dict(supplier_outage_days=recovery['supplier_recovered_outage_days'], delay_costs=True, supplier_expedite=True),
                 temporary_first_article=dict(temporary_first_article_ready_day=recovery['temporary_first_article_ready_day']),
                 combined_delay_costs=dict(combined, delay_costs=True),
                 combined_lower_demand=dict(combined, delay_costs=True, lower_demand=True),
                 combined_escalation=dict(combined, delay_costs=True, capital_escalation=True),
                 combined_finance_downside=dict(combined, delay_costs=True, less_favourable_finance=True),
                 joint_downside=dict(combined, delay_costs=True, lower_demand=True, capital_escalation=True, less_favourable_finance=True, higher_opex=True))
    cases.update(domestic_placement_interrupted_recovered=dict(funding_pause_start_day=600, funding_pause_days=130,
                 funding_pause_first_month=29, funding_resume_month=35,
                 funding_restart_direct_usd=risk_options['funding_gates']['restart_direct_usd'], delay_costs=True),
                 export_credit_delayed_recovered=dict(funding_pause_start_day=0, funding_pause_days=130,
                 funding_pause_first_month=0, funding_resume_month=6,
                 funding_restart_direct_usd=risk_options['funding_gates']['restart_direct_usd'], delay_costs=True))
    for settings in cases.values():
        settings['fixed_process_holds'] = risk_options['fixed_process_holds']
    OUT.mkdir(parents=True, exist_ok=True)
    report = dict(schema='baghdad-frozen-delivery-stress-v2', status='unqualified-deterministic-planning-study',
                  financing_committed=False, operational_release=False, capacity=factory['resource_capacity'],
                  factory_cells={s['package']: s['cells'] for s in factory['stages']}, test_paths=2,
                  canonical_opening_months=[p['opening_month'] for p in city_finance['structured_financing']['phased_opening']['phases']],
                  sources_sha256={p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                  cases={})
    table = []
    for name, settings in cases.items():
        delivery = schedule(payload['manufacturing_tasks'], factory, settings)
        result = finance(delivery, settings, (config, options, programme, city_finance, factory, risk_options))
        report['cases'][name] = dict(settings=settings, phases=delivery['phases'], metrics=result['metrics'],
                                    rework_trainsets=delivery['rework_trainsets'], capacity=delivery['capacity'])
        write_csv(OUT / (name + '-schedule.csv'), delivery['tasks'])
        write_csv(OUT / (name + '-six-month-finance.csv'), result['semiannual'])
        write_csv(OUT / (name + '-incremental-costs.csv'), result['incremental_costs'])
        if name in ('calendar_baseline', 'combined', 'combined_second_test_shift', 'combined_delay_costs', 'joint_downside',
                    'domestic_placement_interrupted_recovered', 'export_credit_delayed_recovered'):
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
                          incremental_recovery_capital_usd=metrics['incremental_recovery_capital_usd'],
                          incremental_delay_costs_usd=metrics['incremental_cost_totals_usd']['delay_extension_usd'],
                          incremental_production_shift_payroll_usd=metrics['incremental_cost_totals_usd']['production_shift_payroll_usd'],
                          supplier_expedite_usd=metrics['incremental_cost_totals_usd']['supplier_expedite_usd'],
                          capital_escalation_usd=metrics['capital_escalation_usd']))
        print(name, table[-1]['first_opening_month'], table[-1]['full_opening_month'], flush=True)
    write_csv(OUT / 'scenario-comparison.csv', table)
    lines = ['# Baghdad frozen-resource delivery and funding study', '',
             'These are deterministic disturbances, not P80/P90 dates or measured failure rates. All 831 planned six-car trains must pass acceptance before their line opens. Selected stage cells, civil crew lanes and dispatch order remain fixed in every stress. No stress calls the capacity-sizing search.', '',
             'The explicit two-path calendar books 16 exclusive running hours per train at the case availability, inside acceptance-bay occupation, with setup and clearance. This adds a conservative calendar audit to the published average-throughput check. Baseline lane order is preserved; a replanned optimal dispatch might recover some delay. Financial-close months include 30 pre-NTP working days and three commissioning months.', '',
             '| Case | First/full month | Peak IQD gap debt, tn | Interest/fees USD eq, bn | Debt cleared month |',
             '|---|---:|---:|---:|---:|']
    for row in table:
        clearance = 'Unfunded' if row['uncovered_cash_usd'] > .02 else ('Unpaid' if row['all_debt_cleared_month'] is None else row['all_debt_cleared_month'])
        lines.append(f"| {row['case']} | {row['first_opening_month']}/{row['full_opening_month']} | {row['peak_gap_debt_iqd']/1e12:.3f} | {row['total_interest_fees_usd']/1e9:.3f} | {clearance} |")
    qualifications = [
        dict(assumption=label, required_evidence=evidence, accountable_role=owner,
             acceptance_rule=rule, status='not-demonstrated', quotation_received=False, operational_release=False)
        for label, evidence, owner, rule in (
            ('Six-car production cycles and tooling', 'Timed first-article travellers; mould duplication/cure tests; lifting and process layouts; vendor equipment quotes', 'Factory process engineer / independent inspector', 'Prove each stage cycle and 85% availability with traceable measurements; no series before first-article acceptance'),
            ('Imported bogies, batteries, doors and windows', 'Lot-level RFQs, origin certificates, qualified suppliers, delivery slots, warranty and lender eligibility', 'Procurement lead / lender technical adviser', 'Match 831 complete six-car kits, financed invoice origin and delivery calendar'),
            ('Staffing and extra shifts', 'Iraqi wage/shift quotes, recruitment cohorts, competency and fatigue roster, measured labour-hours', 'Factory operator / training lead', 'Demonstrate 1044 baseline cell positions plus option-specific incremental FTE without duplicate payroll'),
            ('Two segregated running paths', 'Land/geometry drawings, braking and electrical tests, safe access segregation, witnessed test duty and outage recovery', 'Test manager / independent assessor', 'Demonstrate 16 exclusive test-hours/train and coexistence with acceptance bay use; no shared route counted twice'),
            ('Civil quantities and access', 'Geotechnical survey, utility/land permits, precast curing/output tests, foundations and track installation records, Iraqi contractor RFQs', 'Civil lead / owner engineer', 'Validate access and crew-lane dependencies and quantity-based rates before adopting 20% cycle improvement'),
            ('Depot and temporary first-article facility', 'Site fit, utilities, quarantine/HV/fire layout, equipment transfer and readiness/price quotes', 'Industrial facilities lead', 'Temporary assembly ready day 260 and permanent paths day 390 are sensitivities until site acceptance'),
            ('Ridership, kiosks and advertising', 'OD survey, passenger demand calibration, signed concession heads, occupancy and management cost estimates', 'Transport economist / commercial lead', 'Test phase-specific paid trips and net receipts; planning population is not measured catchment'),
            ('Funding and risk allowance', 'MoF appropriation, IQD placement mandates, lender/green term sheets, capex price-date and delay cost quotes', 'Sponsor / finance lead', 'No uncovered cash placeholder may be called committed funding; hold government capital at 25% with import USD split 50:50'),
            ('Operating acceptance', 'Released hazards/interfaces, completed inspection/test plans, depot/charging/turnback fit and independently signed opening evidence', 'Operator / safety authority', 'Full allocated fleet and infrastructure acceptance precede each line opening; planning schedule cannot authorize service'))]
    for index, entry in enumerate(qualifications, 1):
        entry.update(work_package_id='BAG-EVID-%03d' % index,
                     erpnext_task_subject='BAG-EVID-%03d — ' % index + entry['assumption'],
                     accountable_owner_identity='pending-named-person',
                     executable_package='../qualification/evidence-work-packages.json', signed_result='pending')
    write_csv(OUT / 'qualification-register.csv', qualifications)
    slow = report['cases']['combined_lower_demand']['metrics']
    joint = report['cases']['joint_downside']['metrics']
    lines += ['', '## Separate productivity from investment timing', '',
              'The corrected civil_cycles_20pct_faster case retains every rephased start floor and changes only civil occupation durations. A 1.0 multiplier is tested as an exact schedule identity, including running-path reservations and line openings. Civil_earliest_unchanged_cycles removes the spending delays at original durations; civil_earliest_20pct_faster changes both. Their costs must not be attributed to productivity alone. Earlier completion may still advance completion/retention invoices even when mobilisation timing is retained. These are diagnostic cycle assumptions with no added crews or accepted acceleration price.', '',
              '## Recovery comparisons and priced assumptions', '',
              'Factory cells and dispatch lane order remain fixed. Fixed curing, bonding, inspection and test holds are listed in baghdad-delivery-risk.toml as unqualified working-calendar equivalents. Shift compression applies only to the remaining staffed occupation; the additional 60-day first-article qualification is unchanged. At one shift the original schedule is preserved exactly. Cure elapsed hours and batch/test evidence must replace these assumed splits before adoption. The test-only option uses the same two segregated paths with a second eight-hour test shift: 52 incremental staff, USD 1.5m direct lighting/training plus 7% EPC, and indexed payroll before and after fares. It does not repair upstream stage throughput. The single structural, electrical and composite options add four staffed hours/day to the named stage at unchanged bay count; the coordinated option applies this to all seven stages and funds the second test shift. Incremental production FTE is half each selected stage crew, paid at a 25% premium, with nonlabour shift costs equal to 25% of added payroll. Each stage adds a USD 1m installation/training allowance and USD 10,000 per added FTE plus EPC. These assumed shift efficiencies, relief and wage premiums need qualification.', '',
              'Use availability_75pct_costed, hiring_ramp_costed and supplier_shortage_costed as matching delay-cost baselines for their respective recovery options. Recruitment recovery funds USD 10,000 per delayed half of the 1044 production positions plus EPC and tests a six-month rather than twelve-month staffing ramp. Supplier recovery charges an assumed IQD local logistics fee of 2% of city imported invoice value, indexed to payment, and tests a shortage cut from 130 to 65 working days; this is a causal scenario assumption, not a guaranteed delivery improvement. Foreign-currency freight reimbursement and invoice eligibility need quotations. Neither purchases another train nor credits an unspecified subsidy.', '',
              'The temporary first-article option adds USD 35m direct facility/tooling and 7% EPC, ready at day 260 (12 planning months from NTP), plus 60 incremental support FTE until the permanent plant is ready. Only the already-planned prototype assembles there. Acceptance still waits for permanent bays and running paths at day 390, and series still waits for first-article qualification. All line fleets remain complete at opening. The temporary site and staff must have their own RFQs and acceptance; no shorter passenger section is folded into this option.', '',
              '## Delay costs and combined financial downside', '',
              'Original delivery-only cases remain lower-bound comparisons. Combined_delay_costs additionally prices extended direct production staffing plus 100 support FTE at the existing Iraqi labour proxy; it compares staffed span lengths so a pure start delay does not buy the same crew-months twice. Plant storage/insurance/utilities carrying uses 1% of direct plant capital per extra/idle year excluding wages. Civil prolongation adds 150 supervision FTE and nonlabour site overhead at 0.5% of city capital per year beyond baseline civil completion. All these incremental operating costs are charged monthly at 5% annual indexing; baseline train labour/materials already inside procurement are not repeated. Rework prices 83 affected trains at USD 25,000 each. Monthly incremental-cost files reconcile each allowance to the case OPEX ledger. Contingency, tax and contractor claims remain unquoted; these are not a funded risk reserve.', '',
              'The downside ladder isolates 30% fewer paid trips plus 25% lower existing retail/advertising receipts, 5% annual capital escalation applied to each invoice at actual payment month from financial close, and weaker financing. Weaker financing removes assumed green enhancement, climate grants, development rights and additional net income, increases core coupons two percentage points, and replaces the 2%/IQD 13tn gap sensitivity with 8% credit at a 1% draw fee and IQD 4tn maximum outstanding. Chinese credit and government import cash remain USD, all domestic credit/bonds/cash IQD; government remains 25% of escalated capital. Separately, domestic_placement_interrupted_recovered and export_credit_delayed_recovered stop procurement/construction/production for 130 working days and price local remobilisation plus prolongation; repayment is conditional on subsequently placing the refused debt. Permanent refusal has no opening or repayment date: see the [funding gates and evidence execution package](../qualification/README.md), including denied amounts, escrow requirements and six-month placement shortfalls. No gap facility is used to conceal a refused core source.', '',
              f"Lower demand with combined delays leaves IQD {slow['terminal_supplemental_balance_iqd']/1e12:.3f}tn terminal gap debt. Joint_downside applies all of those assumptions together and 7% rail OPEX inflation: IQD {joint['uncovered_support_iqd']/1e12:.3f}tn cumulative uncovered cash and IQD {joint['terminal_supplemental_balance_iqd']/1e12:.3f}tn terminal gap debt. Uncovered support is a balancing requirement, not an extra government appropriation, loan or cash source. Its presence blocks any unconditional repayment claim even if the simulated debt eventually amortizes. Interest totals in such cases also assume the missing cash is supplied; they do not establish an executable financed programme.", '',
              'Base fare and OPEX sensitivities remain 5% from financial close, with existing kiosks/advertising, separate receipts and each line revenue ramp included. No tickets are sold before opening. Capital escalation is absent from reference cases and explicit in the named escalation cases. Green/grant/rights and all financing availability remain uncommitted. No future national city cashflow supports Baghdad debt.', '',
              '## Evidence needed before adopting a recovery plan', '',
              'The [qualification register](qualification-register.csv) assigns owners, required measurements/RFQs and acceptance rules for production, suppliers, recruitment, civil quantities, depot/site fit, demand, funding and operation. Every row remains not demonstrated. No measurements or quotations were obtained by running this model. The baseline still has only 20 working days of fleet margin and 2.71% test-throughput margin. Shorter passenger sections require a separate route, turnback, charging, depot, fleet duty and safety/operating acceptance study; the present comparisons retain full fleets and existing operating scope.', '',
              'Regenerate after the city controls, factory plan and Baghdad funding programme are current with `.venv/bin/python tools/automation/baghdad_delivery_stress.py`, then regenerate the proposal. Verify source/output bindings with `--check`.', '',
              '[Scenario comparison](scenario-comparison.csv) · [Machine-readable assumptions/results](summary.json) · [Baseline half-year funding](calendar_baseline-six-month-finance.csv) · [Combined stress half-year funding](combined-six-month-finance.csv) · [Joint downside half-year funding](joint_downside-six-month-finance.csv)', '']
    (OUT / 'README.md').write_text('\n'.join(lines))
    report['outputs_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir()) if p.name != 'summary.json'}
    (OUT / 'summary.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
