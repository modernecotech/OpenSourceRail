"""Check the delivered Baghdad scenario's scope, native sources and cap gap."""
import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]


def programme():
    return json.loads((ROOT / 'cities/catalogue/west-asia/Iraq/finance/baghdad-programme.json').read_text())


def test_capital_sources_fund_imports_without_double_counting_government():
    p = programme()
    total = p['total_capex_usd']
    imports = p['comparison']['osr_imported_purchases_usd']
    sources = p['capital_sources_native']
    assert p['included_cities'] == ['Baghdad']
    assert p['factory']['anchor_city'] == 'Baghdad'
    assert sources['chinese_export_credit']['currency'] == 'USD'
    assert sources['government_import_cash']['currency'] == 'USD'
    assert sources['chinese_export_credit']['amount'] == pytest.approx(imports*.5)
    assert sources['government_import_cash']['amount'] == pytest.approx(imports*.5)
    for name in ('government_local_cash', 'domestic_bonds', 'bank_credit'):
        assert sources[name]['currency'] == 'IQD'
        assert sources[name]['amount']/1300 == pytest.approx(sources[name]['usd_equivalent'])
    government = sources['government_import_cash']['usd_equivalent'] + sources['government_local_cash']['usd_equivalent']
    assert government == pytest.approx(total*.25)
    assert sum(v['usd_equivalent'] for v in sources.values()) == pytest.approx(total)
    assert p['usd_denominated_debt_principal_usd'] < p['usd_denominated_capital_usd']


def test_capital_cap_leaves_support_unfunded_and_annuals_match_months():
    p = programme()
    monthly = p['monthly']
    capital = sum(r['government_cash_with_25_percent_cap_usd'] for r in monthly)
    gap = sum(r['additional_funding_required_with_25_percent_cap_usd'] for r in monthly)
    assert capital == pytest.approx(p['total_capex_usd']*.25)
    assert gap > 0
    assert gap == pytest.approx(p['additional_funding_required_with_25_percent_cap_usd'])
    assert sum(p['additional_funding_breakdown_usd'].values()) == pytest.approx(gap)
    assert capital+gap == pytest.approx(p['conditional_total_public_cash_required_usd'])
    cumulative = 0
    for annual in p['annual']:
        rows = [r for r in monthly if r['year'] == annual['year']]
        for key in ('government_capital_usd_cash', 'government_capital_iqd', 'chinese_export_credit_draw_usd', 'domestic_debt_service_iqd', 'additional_funding_required_with_25_percent_cap_usd'):
            assert annual[key] == pytest.approx(sum(r[key] for r in rows))
        cumulative += annual['additional_funding_required_with_25_percent_cap_usd']
        assert annual['cumulative_additional_funding_required_usd'] == pytest.approx(cumulative)


def test_comparator_and_employment_remain_evidence_limited():
    p = programme()
    c = p['comparison']
    assert c['third_party']['reported_scope']['route_km'] == 148
    assert 'not verified' in c['third_party']['currency_basis']
    assert 'not measured' in c['third_party']['coverage_basis']
    assert c['construction_job_count'] is None
    assert c['operating_fte'] == 2350
    assert 0 < c['anchor_weighted_coverage'] < 1
    assert c['first_operating_year_neutral_fare_iqd_including_debt_and_fees'] > c['operating_only_neutral_fare_iqd_at_low_trips']
    assert not p['funding_committed']


def test_programme_provenance_is_current_and_excludes_other_cities():
    p = programme()
    assert not any('/Samawah/' in relative or '/Mosul/' in relative for relative in p['sources_sha256'])
    for relative, digest in p['sources_sha256'].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest, relative


def test_phased_programme_uses_same_capital_and_reports_complete_line_cashflows():
    p = programme()
    phases = p['phased_opening']['phases']
    assert len(phases) == 9
    assert sum(row['weight'] for row in phases) == pytest.approx(1)
    for name, case in p['phased_opening']['cases'].items():
        monthly = case['monthly']
        metrics = case['metrics']
        assert sum(row['capex_usd'] for row in monthly) == pytest.approx(p['total_capex_usd'])
        assert sum(row['government_capital_received_usd'] for row in monthly) == pytest.approx(p['total_capex_usd']*.25)
        assert case['additional_funding_required_usd'] == pytest.approx(sum(row['government_operations_and_debt_support_usd'] for row in monthly))
        assert metrics['max_cash_balance_residual_usd'] < .01
        assert max(metrics['final_debt_balances_native'].values()) < .01
        assert sum(row['revenue_usd'] for row in case['annual']) == pytest.approx(sum(row['revenue_usd'] for row in monthly))
    low = p['phased_opening']['cases']['low_demand']
    assert low['metrics']['operations_start_month'] > 24  # new plant precedes production and line release
    assert low['metrics']['operations_start_month'] < low['metrics']['full_network_operations_start_month']
    assert low['additional_funding_required_usd'] < p['additional_funding_required_with_25_percent_cap_usd']
    assert p['phased_opening']['cases']['demand_minus_40_percent']['additional_funding_required_usd'] > low['additional_funding_required_usd']
