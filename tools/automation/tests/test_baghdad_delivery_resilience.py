"""Opening, finite-resource and cash conservation for delivery disturbances."""
from collections import defaultdict
from copy import deepcopy
import csv
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tomllib

import pytest

ROOT = Path(__file__).resolve().parents[3]
CITY = ROOT / 'cities/catalogue/west-asia/Iraq/Baghdad'
sys.path.insert(0, str(ROOT / 'tools/automation'))
from delivery_rephasing import align_infrastructure_to_fleets
from baghdad_delivery_stress import next_slot, schedule, finance, city_funding_config


@pytest.fixture(scope='module')
def payload():
    return json.loads(gzip.decompress((CITY / 'operations/baghdad-operations.json.gz').read_bytes()))


def test_rephasing_preserves_scope_openings_lanes_dependencies_and_capital(payload):
    original = deepcopy(payload['manufacturing_tasks'])
    for row in original:
        row['planned_start_day'] = row['unphased_start_day']
        row['planned_finish_day'] = row['unphased_finish_day']
    before = deepcopy(original)
    report = align_infrastructure_to_fleets(original, 90)
    assert report['shifted_work_packages'] > 1000
    assert report['full_fleet_and_opening_dates_unchanged']
    first = report['line_completions'][0]
    assert first['original_idle_working_days'] == first['fleet_completion_day']-first['original_infrastructure_day']
    assert first['rephased_idle_working_days'] == 90
    by_uid = {r['manufacturing_uid']: r for r in original}
    for old, new in zip(before, original):
        for key in ('manufacturing_uid', 'asset_id', 'resource_lane', 'resource_capacity', 'duration_days', 'budget_usd'):
            assert old[key] == new[key]
        assert new['planned_start_day'] >= old['planned_start_day']
        assert new['planned_finish_day'] - new['planned_start_day'] + 1 == old['duration_days']
        if old['asset_type'] == 'rolling-stock':
            assert old['planned_finish_day'] == new['planned_finish_day']
        for uid in new['schedule_predecessor_uids'].split(';'):
            if uid.strip():
                assert by_uid[uid.strip()]['planned_finish_day'] < new['planned_start_day']
    expected = {r['manufacturing_uid']: r for r in payload['manufacturing_tasks']}
    assert all(r['planned_start_day'] == expected[r['manufacturing_uid']]['planned_start_day'] for r in original)
    assert sum(c['budget_usd'] for c in payload['project_twin']['budget_contracts']) == pytest.approx(json.loads((CITY/'engineering/finance/summary.json').read_text())['capex_usd']['reconciled_project_total'])
    for contract in payload['project_twin']['budget_contracts']:
        assert contract['planned_start_day'] == by_uid[contract['manufacturing_uid']]['planned_start_day']


@pytest.mark.parametrize('buffer', [-1, 1.5, True])
def test_invalid_rephasing_buffer_is_rejected(buffer):
    with pytest.raises(ValueError):
        align_infrastructure_to_fleets([], buffer)


def test_path_outage_intervals_are_exclusive_and_nonpreemptive():
    assert next_slot(5, 6, [(10, 20), (23, 30)]) == 30
    assert next_slot(4, 6, [(10, 20)]) == 4
    assert next_slot(20, 4, [(10, 20)]) == 20


def test_civil_productivity_identity_preserves_all_dates_paths_and_payments(payload):
    factory=json.loads((CITY/'engineering/factory/summary.json').read_text())
    baseline=schedule(payload['manufacturing_tasks'],factory,{})
    identity=schedule(payload['manufacturing_tasks'],factory,{'civil_cycle_factor':1.0})
    assert identity == baseline
    by_uid={r['manufacturing_uid']:r for r in identity['tasks']}
    for contract in payload['project_twin']['budget_contracts']:
        row=by_uid[contract['manufacturing_uid']]
        assert row['start_hour']//8 == contract['planned_start_day']
        assert (row['end_hour']+7)//8-1 == contract['planned_finish_day']
    faster=schedule(payload['manufacturing_tasks'],factory,{'civil_cycle_factor':.8})
    assert all(r['start_hour'] >= by_uid[r['manufacturing_uid']]['start_hour'] for r in faster['tasks'])
    earliest=schedule(payload['manufacturing_tasks'],factory,{'civil_timing':'earliest'})
    assert any(r['start_hour']<by_uid[r['manufacturing_uid']]['start_hour'] for r in earliest['tasks'])
    assert all(r['start_hour']<=by_uid[r['manufacturing_uid']]['start_hour'] for r in earliest['tasks'])
    assert earliest['phases'][0]['infrastructure_completion_day'] < baseline['phases'][0]['infrastructure_completion_day']
    assert earliest['phases'][0]['opening_month'] == baseline['phases'][0]['opening_month']


@pytest.mark.parametrize('value',[0,-.1,1.1,float('nan'),True])
def test_invalid_productivity_multiplier_rejected(payload,value):
    factory=json.loads((CITY/'engineering/factory/summary.json').read_text())
    with pytest.raises(ValueError,match='civil cycle multiplier'):
        schedule(payload['manufacturing_tasks'],factory,{'civil_cycle_factor':value})


def test_pure_start_delay_does_not_duplicate_baseline_staffed_months(payload):
    factory=json.loads((CITY/'engineering/factory/summary.json').read_text())
    programme=json.loads((CITY.parent/'finance/baghdad-programme.json').read_text())
    city=json.loads((CITY/'engineering/finance/summary.json').read_text())
    city['_contracts']=payload['project_twin']['budget_contracts']
    config=city_funding_config(tomllib.loads((ROOT/'lib/templates/iraq-funding.toml').read_text()),'baghdad')
    options=tomllib.loads((ROOT/'lib/templates/baghdad-finance-options.toml').read_text())
    risk=tomllib.loads((ROOT/'lib/templates/baghdad-delivery-risk.toml').read_text())
    settings=dict(factory_delay_days=130,delay_costs=True)
    delivered=schedule(payload['manufacturing_tasks'],factory,settings)
    result=finance(delivered,settings,(config,options,programme,city,factory,risk))
    # The six-month idle interval adds site carrying; production staffed span
    # remains the same length, so there is no duplicate direct wage extension.
    expected=factory['budgeted_plant_direct_usd']*.01/12*sum(1.05**(month//12) for month in range(19,25))
    assert result['metrics']['incremental_cost_totals_usd']['delay_extension_usd']==pytest.approx(expected)


def test_published_stresses_freeze_cells_and_reconcile_every_cash_principal_balance():
    risk = CITY / 'engineering/delivery-risk'
    report = json.loads((risk / 'summary.json').read_text())
    assert not report['financing_committed'] and not report['operational_release']
    for case in report['cases'].values():
        assert case['capacity'] == report['capacity']
        assert case['metrics']['government_capital_share'] == pytest.approx(.25)
        assert case['metrics']['maximum_cash_residual_usd'] < .02
        assert case['metrics']['maximum_principal_balance_residual_usd'] < .02
        assert sum(p['weight'] for p in case['phases']) == pytest.approx(1)
    for rel, sha in report['sources_sha256'].items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == sha, rel
    for rel, sha in report['outputs_sha256'].items():
        assert hashlib.sha256((risk / rel).read_bytes()).hexdigest() == sha, rel
    cases = report['cases']
    assert [p['opening_month'] for p in cases['calendar_baseline']['phases']] == report['canonical_opening_months']
    programme=json.loads((CITY.parent/'finance/baghdad-programme.json').read_text())
    canonical=programme['independent_recalculation']['early_repayment']['cases']['cost_priority']
    for key in ('peak_supplemental_balance_iqd','total_finance_interest_and_fees_usd','all_debt_cleared_month'):
        assert cases['calendar_baseline']['metrics'][key] == pytest.approx(canonical[key])
    fleet=len({r['asset_id'] for r in json.loads(gzip.decompress((CITY/'operations/baghdad-operations.json.gz').read_bytes()))['manufacturing_tasks'] if r['asset_type']=='rolling-stock'})
    rework=int(fleet*.1)
    assert cases['combined']['rework_trainsets'] == rework
    assert max(p['opening_month'] for p in cases['availability_65pct']['phases']) > max(p['opening_month'] for p in cases['calendar_baseline']['phases'])
    recovery = cases['combined_second_test_shift']
    factory=json.loads((CITY/'engineering/factory/summary.json').read_text())
    assumption=tomllib.loads((ROOT/'lib/templates/baghdad-delivery-risk.toml').read_text())
    recovery_capital=assumption['recovery']['test_shift_direct_usd_per_path']*factory['test_tracks']*(1+assumption['costs']['epc_fraction'])
    assert recovery['metrics']['incremental_recovery_capital_usd'] == recovery_capital
    assert recovery['metrics']['incremental_test_payroll_usd'] > 2000000
    assert recovery['metrics']['total_capital_usd'] == pytest.approx(programme['total_capex_usd']+rework*assumption['costs']['rework_local_usd_per_train']+recovery_capital)
    recovery_cash=list(csv.DictReader((risk/'combined_second_test_shift-monthly-finance.csv').open()))
    first_open=min(p['opening_month'] for p in recovery['phases'])
    assert any(float(r['opex_iqd'])>0 for r in recovery_cash if int(r['month'])<first_open)
    assert max(p['opening_month'] for p in recovery['phases']) <= max(p['opening_month'] for p in cases['combined']['phases'])
    assert max(p['infrastructure_completion_day'] for p in cases['civil_earliest_20pct_faster']['phases']) < max(p['infrastructure_completion_day'] for p in cases['calendar_baseline']['phases'])
    intervals = defaultdict(list)
    for row in csv.DictReader((risk / 'combined-schedule.csv').open()):
        intervals[row['resource_pool'], row['resource_lane']].append((int(row['start_hour']), int(row['end_hour'])))
        if row['test_path']:
            intervals['path', row['test_path']].append((int(row['test_start_hour']), int(row['test_end_hour'])))
            if row['test_path'] == '1':
                assert int(row['test_end_hour']) <= 900 * 8 or int(row['test_start_hour']) >= 1030 * 8
    for values in intervals.values():
        ordered = sorted(values)
        assert all(a[1] <= b[0] for a, b in zip(ordered, ordered[1:]))


def test_recovery_costs_extensions_and_downside_cash_are_reconciled(payload):
    risk=CITY/'engineering/delivery-risk'
    cases=json.loads((risk/'summary.json').read_text())['cases']
    assert [p['opening_month'] for p in cases['availability_75pct']['phases']] == [p['opening_month'] for p in cases['availability_75pct_second_test_shift']['phases']]
    coordinated=cases['availability_75pct_all_stage_shifts']
    assert coordinated['metrics']['incremental_recovery_capital_usd'] > 10e6
    assert coordinated['metrics']['incremental_cost_totals_usd']['production_shift_payroll_usd'] > 20e6
    assert max(p['opening_month'] for p in coordinated['phases']) < max(p['opening_month'] for p in cases['availability_75pct']['phases'])
    tmp=cases['temporary_first_article']
    assert min(p['opening_month'] for p in tmp['phases']) < 41
    assert tmp['metrics']['incremental_recovery_capital_usd'] == pytest.approx(35e6*1.07)
    rows=list(csv.DictReader((risk/'temporary_first_article-schedule.csv').open()))
    proto=next(r['asset_id'] for r in sorted(rows,key=lambda r:int(r['start_hour'])) if r['asset_type']=='rolling-stock')
    qualification=next(r for r in rows if r['asset_id']==proto and r['manufacturing_uid'].endswith('rs-50-dynamic-commissioning'))
    assert int(qualification['start_hour']) >= 390*8
    assert all(int(r['start_hour'])>=int(qualification['end_hour']) for r in rows if r['asset_type']=='rolling-stock' and r['asset_id']!=proto and r['manufacturing_uid'].endswith('rs-10-material-kit'))
    baseline_cash=list(csv.DictReader((risk/'combined-monthly-finance.csv').open()))
    extended_cash=list(csv.DictReader((risk/'combined_delay_costs-monthly-finance.csv').open()))
    costs=list(csv.DictReader((risk/'combined_delay_costs-incremental-costs.csv').open()))
    fx=1300.
    for old,new,cost in zip(baseline_cash,extended_cash,costs):
        assert (float(new['opex_iqd'])-float(old['opex_iqd']))/fx == pytest.approx(float(cost['delay_extension_usd']),abs=.0001)
    assert sum(float(r['delay_extension_usd']) for r in costs)==pytest.approx(cases['combined_delay_costs']['metrics']['incremental_cost_totals_usd']['delay_extension_usd'])
    downside=cases['joint_downside']['metrics']
    assert downside['capital_escalation_usd'] > 1e9
    assert downside['uncovered_support_iqd'] > 1e12
    assert downside['terminal_supplemental_balance_iqd'] > 1e12
    assert downside['debt_clearance_month_without_unfunded_support'] is None
    no_green=cases['combined_finance_downside']['metrics']
    assert no_green['green_bonds_iqd']==no_green['climate_grant_iqd']==no_green['net_rights_receipts_iqd']==0
    assert no_green['uncovered_support_iqd'] > 1e12
    assert no_green['debt_clearance_month_without_unfunded_support'] is None
    assert all(r['status']=='not-demonstrated' and r['operational_release']=='False' for r in csv.DictReader((risk/'qualification-register.csv').open()))


def test_narrative_facts_derive_from_current_sensitivity_and_respond_to_changes():
    spec = importlib.util.spec_from_file_location('proposal', ROOT / 'tools/automation/build-baghdad-proposal.py')
    builder = importlib.util.module_from_spec(spec); spec.loader.exec_module(builder)
    programme = json.loads((CITY.parent / 'finance/baghdad-programme.json').read_text())
    facts = builder.financial_narrative_facts(programme)
    assert facts['slow_income_full_opening_burden'] == pytest.approx(.1396, abs=.0001)
    assert facts['opex_stress_terminal_gap_iqd'] == 0
    calculation = programme['independent_recalculation']
    calculation['fare_pricing']['fare_5pct_opex_5pct_income_2pct']['full_opening']['forty_four_trips_income_share'] = .12345
    calculation['cases']['fare_5pct_opex_7pct']['terminal_supplemental_balance_iqd'] = 456e9
    calculation['cases']['fare_5pct_opex_7pct']['uncovered_support_iqd'] = 789e9
    facts = builder.financial_narrative_facts(programme)
    assert facts == dict(slow_income_full_opening_burden=.12345, opex_stress_terminal_gap_iqd=456e9, opex_stress_uncovered_support_iqd=789e9)
