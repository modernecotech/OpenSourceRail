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

import pytest

ROOT = Path(__file__).resolve().parents[3]
CITY = ROOT / 'cities/catalogue/west-asia/Iraq/Baghdad'
sys.path.insert(0, str(ROOT / 'tools/automation'))
from delivery_rephasing import align_infrastructure_to_fleets
from baghdad_delivery_stress import next_slot, schedule


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
    assert first['original_idle_working_days'] == 553
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
    assert sum(c['budget_usd'] for c in payload['project_twin']['budget_contracts']) == pytest.approx(7555743753.488)
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
    assert cases['combined']['rework_trainsets'] == 83
    assert max(p['opening_month'] for p in cases['availability_65pct']['phases']) > max(p['opening_month'] for p in cases['calendar_baseline']['phases'])
    recovery = cases['combined_second_test_shift']
    assert recovery['metrics']['incremental_recovery_capital_usd'] == 1605000
    assert recovery['metrics']['incremental_test_payroll_usd'] > 2000000
    assert recovery['metrics']['total_capital_usd'] == pytest.approx(programme['total_capex_usd']+83*25000+1605000)
    recovery_cash=list(csv.DictReader((risk/'combined_second_test_shift-monthly-finance.csv').open()))
    first_open=min(p['opening_month'] for p in recovery['phases'])
    assert any(float(r['opex_iqd'])>0 for r in recovery_cash if int(r['month'])<first_open)
    assert max(p['opening_month'] for p in recovery['phases']) < max(p['opening_month'] for p in cases['combined']['phases'])
    assert max(p['infrastructure_completion_day'] for p in cases['civil_cycles_20pct_faster']['phases']) < max(p['infrastructure_completion_day'] for p in cases['calendar_baseline']['phases'])
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
