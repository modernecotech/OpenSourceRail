"""A complete Baghdad publication must preserve scope, evidence and cash totals."""
import csv
import hashlib
import json
import sys
from pathlib import Path
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/automation'))
from baghdad_equity import return_label, dividend_date
CITY = ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
PROPOSAL = CITY


def data(name):
    return json.loads((PROPOSAL/name).read_text())


def test_proposal_sources_outputs_and_complete_archive_are_current():
    manifest = data('manifest.json')
    with zipfile.ZipFile(PROPOSAL/'Baghdad-Proposal-Supporting-Data.zip') as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == set(manifest['archive_members'])
        archive_manifest_path = (PROPOSAL/'archive-manifest.json').relative_to(ROOT).as_posix()
        members = json.loads(archive.read(archive_manifest_path))['members']
        assert set(members) == set(archive.namelist())-{archive_manifest_path}
        for relative, value in members.items():
            raw = archive.read(relative)
            assert len(raw) == value['bytes'], relative
            assert hashlib.sha256(raw).hexdigest() == value['sha256'], relative
        for group in ('inputs', 'outputs'):
            for relative, receipt in manifest[group].items():
                source = ROOT/relative
                assert source.stat().st_size == receipt['bytes'], relative
                assert hashlib.sha256(source.read_bytes()).hexdigest() == receipt['sha256'], relative
                if group == 'inputs':
                    assert hashlib.sha256(archive.read(relative)).hexdigest() == receipt['sha256'], relative
    assert (PROPOSAL/'Baghdad-Proposal.pdf').read_bytes().startswith(b'%PDF-')
    assert all(v['bytes'] <= 50*1024*1024 for v in manifest['outputs'].values())


def test_every_baghdad_document_and_financial_case_is_included():
    manifest = data('manifest.json')
    chapters = set(data('appendix-sources.json'))
    docs = {p.relative_to(ROOT).as_posix() for p in CITY.rglob('*.md') if p.name not in ('BAGHDAD-PROPOSAL.md','DETAILED-SCHEDULES.md')}
    assert docs <= chapters
    inputs = set(manifest['inputs'])
    financial = {p.relative_to(ROOT).as_posix() for p in (CITY.parent/'finance').glob('baghdad-*') if p.is_file()}
    assert financial <= inputs
    assert len(chapters) == manifest['appendix_document_count']
    ops = json.loads((CITY/'operations/baghdad-operations-manifest.json').read_text())
    payload = (CITY/'operations'/ops['file']).relative_to(ROOT).as_posix()
    assert manifest['inputs'][payload]['sha256'] == ops['compressed_sha256']
    assert (CITY/'DETAILED-ENGINEERING.md').relative_to(ROOT).as_posix() in chapters
    assert (CITY/'engineering/detail/register.json').relative_to(ROOT).as_posix() in inputs
    assert 'control-electronics/reference-integration.json' in inputs
    assert 'deployment/erpnext/compose.yaml' in inputs
    assert 'docs/rfcs/0033-tacs-runtime-and-resource-control.md' in chapters
    assert 'docs/rfcs/0032-train-centred-control.md' not in chapters


def test_delivery_reconciliation_and_current_review_are_published():
    manifest=data('manifest.json');inputs=set(manifest['inputs'])
    for suffix in ('summary.json','chronological-energy.json','scope-register.json','six-car.json','workforce.json','rental-delivery-options.json','erpnext-tasks.json'):
        assert (CITY/'engineering/delivery-baseline'/suffix).relative_to(ROOT).as_posix() in inputs
    assert 'docs/baghdad-delivery-review-2026-10-04.md' in data('appendix-sources.json')
    for name in ('workforce.py','workforce_rules.py'):
        assert 'deployment/erpnext/apps/osr_erpnext/osr_erpnext/'+name in inputs
    assert 'tools/automation/bootstrap_baghdad_tests.py' in inputs

def test_delivery_continuation_headlines_and_all_ledgers_are_published():
    manifest=data('manifest.json');inputs=set(manifest['inputs'])
    for name in ('finance-reconciled_full_fleet.json','finance-reconciled_full_fleet-monthly.csv','fare-sensitivities.json','depot-line-6.svg','opening-battery-reserve-monthly.csv','maintenance-interval-register.json','erpnext-tasks.json'):
        assert (CITY/'engineering/delivery-closure'/name).relative_to(ROOT).as_posix() in inputs
    for name in ('tools/automation/verify_baghdad_erp_restore.py','deployment/erpnext/apps/osr_erpnext/osr_erpnext/delivery_admin.py'):
        assert name in inputs
    case=json.loads((CITY/'engineering/delivery-closure/finance-reconciled_full_fleet.json').read_text())
    narrative=(PROPOSAL/'BAGHDAD-PROPOSAL.md').read_text()
    assert f"USD {case['metrics']['total_capital_usd']/1e9:.3f}bn capital" in narrative
    assert f"IQD {case['metrics']['terminal_supplemental_balance_iqd']/1e12:.3f}tn unpaid gap debt" in narrative
    assert manifest['facts']['delivery_continuation_capital_usd']==case['metrics']['total_capital_usd']
    assert not manifest['facts']['delivery_continuation_budget_complete']


def test_manufactured_viaduct_review_and_bearing_cashflow_are_published_together():
    inputs=set(data('manifest.json')['inputs'])
    chapters=set(data('appendix-sources.json'))
    assert 'docs/baghdad-manufactured-viaduct-review-2026-10-04.md' in chapters
    assert (CITY/'engineering/viaduct-comparison/README.md').relative_to(ROOT).as_posix() in chapters
    for suffix in ('.json','-monthly.csv','-semiannual.csv'):
        path=CITY/('engineering/delivery-closure/finance-simple_span_bearing_index'+suffix)
        assert path.relative_to(ROOT).as_posix() in inputs
    case=json.loads((CITY/'engineering/delivery-closure/finance-simple_span_bearing_index.json').read_text())
    narrative=(PROPOSAL/'BAGHDAD-PROPOSAL.md').read_text()
    assert f"USD {case['metrics']['total_capital_usd']/1e9:.3f}bn capital" in narrative
    assert f"IQD {case['metrics']['terminal_supplemental_balance_iqd']/1e12:.3f}tn terminal gap debt" in narrative
    assert 'complete 24-axle' in narrative


def test_latest_scope_and_every_native_cashflow_are_published():
    summary=json.loads((CITY/'engineering/programme-recalculation/summary.json').read_text())
    manifest=data('manifest.json')
    inputs=set(manifest['inputs'])
    assert manifest['facts']['programme_recalculation']==summary['finance_cases']
    assert manifest['facts']['programme_operating_fte']==summary['operating_fte']
    assert manifest['facts']['programme_depot_count']==9
    assert manifest['facts']['programme_depot_slots']==current_fleet()
    assert not manifest['facts']['programme_budget_complete']
    for case in summary['finance_cases']:
        for suffix in ('.json','-monthly.csv','-semiannual.csv','-contracts.csv'):
            assert (CITY/('engineering/programme-recalculation/'+case+suffix)).relative_to(ROOT).as_posix() in inputs
    assert 'docs/baghdad-scope-and-industrial-review-2026-10-04.md' in data('appendix-sources.json')
    narrative=(PROPOSAL/'BAGHDAD-PROPOSAL.md').read_text()
    current=summary['finance_cases']['local_positive']
    assert f"IQD {current['terminal_all_debt_iqd']/1e12:.3f}tn total debt" in narrative
    assert f"{current['usd_capital_intensity']:.2%} USD capital intensity" in narrative
    assert f"{summary['finance_cases']['local_positive_mezzanine']['junior_defaulted_vintages']} defaulted draw vintages" in narrative


def test_national_capital_counts_the_existing_factory_once_and_keeps_baghdad_scope():
    n = data('national-context.json')
    p = json.loads((CITY.parent/'finance/baghdad-programme.json').read_text())
    m = data('manifest.json')
    assert n['factory_count'] == m['factory_count'] == 1
    assert m['baghdad_financing_scope'] == p['included_cities'] == ['Baghdad']
    assert not n['baghdad_financing_includes_national_expansion']
    assert n['city_count'] == len(list(CITY.parent.glob('*/design.toml'))) == 18
    assert n['shared_factory_usd'] >= p['factory']['cost_usd']
    assert n['shared_factory_epc_usd'] >= p['factory']['epc_usd']
    assert n['baghdad_factory_reference_usd'] == p['factory']['cost_usd']
    assert n['baghdad_factory_epc_reference_usd'] == p['factory']['epc_usd']
    plant_increment = n['future_shared_factory_increment_usd']+n['future_shared_factory_epc_increment_usd']
    assert plant_increment == pytest.approx(n['shared_factory_usd']+n['shared_factory_epc_usd']-p['factory']['cost_usd']-p['factory']['epc_usd'])
    assert sum(c['city_capex_usd'] for c in n['cities'])+n['shared_factory_usd']+n['shared_factory_epc_usd'] == pytest.approx(n['total_national_capital_usd'])
    others = sum(c['city_capex_usd'] for c in n['cities'] if c['city'] != 'Baghdad')
    assert n['future_incremental_city_capital_after_baghdad_usd'] == pytest.approx(others+plant_increment)
    assert n['total_national_capital_usd'] == pytest.approx(p['total_capex_usd']+others+plant_increment)
    assert m['facts']['baghdad_total_capex_usd'] == p['total_capex_usd']
    assert m['facts']['baghdad_government_share'] == .25


def test_network_registers_preserve_complete_counts_and_optional_civil_fields():
    def rows(name):
        with (PROPOSAL/'registers'/name).open() as handle:
            return list(csv.DictReader(handle))
    import tomllib
    design = tomllib.loads((CITY/'design.toml').read_text())
    assert len(rows('stations.csv')) == len(design['stations'])
    assert {r['id'] for r in rows('stations.csv')} == {r['id'] for r in design['stations']}
    assert len(rows('civil-segments.csv')) == len(design['civil_segments'])
    assert any(r['viaduct_product'] for r in rows('civil-segments.csv'))
    assert sum(int(r['trainset_count']) for r in rows('fleets.csv')) == current_fleet()
    assert len(rows('interchanges.csv')) == len(design['interchanges'])
    assert len(rows('junctions.csv')) == len(design['junctions'])
    narrative = (PROPOSAL/'BAGHDAD-PROPOSAL.md').read_text()
    assert 'RFC 0033' in narrative and 'superseded' in narrative
    analysis=json.loads((CITY.parent/'finance/baghdad-early-repayment.json').read_text())
    for name in ('cost_priority','loans_then_bonds'):
        assert name in analysis['cases']
    assert '18 months from NTP' in narrative
    assert '(engineering/factory/README.md)' in narrative
    assert '14 deployment gates remain open' in narrative
    assert 'future national' in narrative.lower()


def test_financial_narrative_matches_sensitivity_results_and_manifest():
    programme=json.loads((CITY.parent/'finance/baghdad-programme.json').read_text())
    calculation=programme['independent_recalculation']
    expected=dict(slow_income_full_opening_burden=calculation['fare_pricing']['fare_5pct_opex_5pct_income_2pct']['full_opening']['forty_four_trips_income_share'],
                  opex_stress_terminal_gap_iqd=calculation['cases']['fare_5pct_opex_7pct']['terminal_supplemental_balance_iqd'],
                  opex_stress_uncovered_support_iqd=calculation['cases']['fare_5pct_opex_7pct']['uncovered_support_iqd'])
    narrative=(PROPOSAL/'BAGHDAD-PROPOSAL.md').read_text()
    for name,value in expected.items():
        assert data('manifest.json')['facts'][name] == value
    assert f"**{expected['slow_income_full_opening_burden']:.2%}** at full opening" in narrative
    assert f"**IQD {expected['opex_stress_terminal_gap_iqd']/1e12:.3f}tn terminal unpaid gap debt**" in narrative
    assert f"**IQD {expected['opex_stress_uncovered_support_iqd']/1e12:.3f}tn uncovered cash**" in narrative
    assert '26.4%' not in narrative and 'IQD 13tn remains unpaid' not in narrative
    assert (CITY/'engineering/delivery-risk/summary.json').relative_to(ROOT).as_posix() in data('manifest.json')['inputs']


def test_financing_redesign_is_published_with_exact_integrated_results():
    root=CITY/'engineering/financing-redesign'
    report=json.loads((root/'summary.json').read_text())
    inputs=set(data('manifest.json')['inputs'])
    assert {p.relative_to(ROOT).as_posix() for p in root.glob('*') if p.is_file()} <= inputs
    narrative=(PROPOSAL/'BAGHDAD-PROPOSAL.md').read_text()
    case=report['cases']['integrated']
    assert f"IQD {case['metrics']['peak_aggregate_liquidity_iqd']/1e12:.3f}tn" in narrative
    assert f"USD {case['appraisal']['consolidated_resource_npv_usd']/1e9:.3f}bn" in narrative
    assert '25% capital limit' in narrative and '15-year total insured green tenor' in narrative
    assert (root/'README.md').relative_to(ROOT).as_posix() in data('appendix-sources.json')


def test_equity_study_is_published_without_promising_admission_or_return():
    root=CITY/'engineering/equity'
    c=json.loads((root/'summary.json').read_text())['cases']['primary_1000m']
    assert {p.relative_to(ROOT).as_posix() for p in root.glob('*') if p.is_file()}<=set(data('manifest.json')['inputs'])
    text=(PROPOSAL/'BAGHDAD-PROPOSAL.md').read_text()
    assert f"{return_label(c['shareholder_returns']['iraqi_private']['equity_irr'])} nominal IRR" in text
    assert f"**{dividend_date(c['metrics']['first_dividend_month'])}**" in text
    assert 'zero new money' in text and 'listing at that date is unproven' in text
    assert (root/'README.md').relative_to(ROOT).as_posix() in data('appendix-sources.json')


def test_retained_rental_evidence_and_exact_dividend_exit_comparisons_are_published():
    root=CITY/'engineering/viaduct-rentals'
    assert {p.relative_to(ROOT).as_posix() for p in root.glob('*') if p.is_file()}<=set(data('manifest.json')['inputs'])
    c=json.loads((CITY/'engineering/equity/summary.json').read_text())['cases']['rental_medium_1000m']
    narrative=(PROPOSAL/'BAGHDAD-PROPOSAL.md').read_text()
    assert 'Confirmed eligible area remains **zero**' in narrative
    assert return_label(c['shareholder_returns']['iraqi_private']['equity_irr']) in narrative
    exit_case=json.loads((CITY/'engineering/equity/primary_1000m.json').read_text())
    expected=exit_case['terminal_cash_sensitivity']['shareholder_returns']['iraqi_private']['equity_irr_with_terminal_cash']
    assert return_label(expected) in narrative and 'Tenant fire' in narrative
    assert (root/'README.md').relative_to(ROOT).as_posix() in data('appendix-sources.json')


def current_design():
    import tomllib
    return tomllib.loads((ROOT/'cities/catalogue/west-asia/Iraq/Baghdad/design.toml').read_text())

def current_fleet():
    return sum(r['trainset_count'] for r in current_design()['fleets'])
