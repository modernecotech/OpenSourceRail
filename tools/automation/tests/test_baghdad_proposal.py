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


def verify_proposal_snapshot(root, proposal, manifest, *, retained_context_paths=()):
    """Verify original archive bytes; only separately checked contexts may evolve.

    Route, price, finance and publication-output drift still fails. The two
    evolving research/publication manifests are not adopted proposal inputs;
    their original declared bytes must remain intact in the retained archive.
    """
    from proposal_archives import part_inventory, read_members
    inventory=part_inventory(manifest)
    flattened=[name for names in inventory.values() for name in names]
    assert len(flattened)==len(set(flattened))
    assert set(flattened)==set(manifest['archive_members'])
    members=json.loads((proposal/'archive-manifest.json').read_text())['members']
    archive_manifest_path=(proposal/'archive-manifest.json').relative_to(root).as_posix()
    assert set(members)==set(flattened)-{archive_manifest_path}
    archived_receipts={}
    for part,names in inventory.items():
        with zipfile.ZipFile(proposal/part) as archive:assert archive.testzip() is None
        raw_members=read_members(root,proposal,manifest,names)
        for relative,raw in raw_members.items():
            archived_receipts[relative]=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
            if relative in members:
                assert len(raw)==members[relative]['bytes'],relative
                assert hashlib.sha256(raw).hexdigest()==members[relative]['sha256'],relative
    for group in ('inputs','outputs'):
        for relative,receipt in manifest[group].items():
            source=root/relative
            assert source.resolve().is_relative_to(root.resolve()),relative
            if relative in archived_receipts:
                assert archived_receipts[relative]==receipt,relative
            if group=='inputs':
                assert relative in members
                if relative in retained_context_paths:
                    continue
            assert source.stat().st_size==receipt['bytes'],relative
            assert hashlib.sha256(source.read_bytes()).hexdigest()==receipt['sha256'],relative
    for relative,receipt in manifest.get('companion_archives',{}).items():
        source=root/relative
        assert source.resolve().is_relative_to(root.resolve()),relative
        assert source.stat().st_size==receipt['bytes'],relative
        assert hashlib.sha256(source.read_bytes()).hexdigest()==receipt['sha256'],relative
        with zipfile.ZipFile(source) as archive:assert archive.testzip() is None
    assert (proposal/'Baghdad-Proposal.pdf').read_bytes().startswith(b'%PDF-')
    assert all(v['bytes'] <= 50*1024*1024 for v in manifest['outputs'].values())


def retained_research_context_paths(city=CITY, root=ROOT):
    """Require live non-adoption policy and current source-bound publication."""
    import importlib.util
    from iraq_current_basis import current_basis

    basis=json.loads((city.parent/'CURRENT-PLANNING-BASIS.json').read_text())
    assert basis==current_basis(), 'Current Iraq publication basis is stale'
    assert basis['financial_case']['status']=='unquoted-retained-financial-comparator'
    study=city/'engineering/coupled-programme'
    manifest=json.loads((study/'manifest.json').read_text())
    summary=json.loads((study/'summary.json').read_text())
    assert manifest['engineering_and_financial_adoption'] is False
    assert summary['financial_baseline_replaced'] is False
    for base,key in ((root,'sources_sha256'),(study,'outputs_sha256')):
        for name,digest in manifest[key].items():
            assert hashlib.sha256((base/name).read_bytes()).hexdigest()==digest,name
    spec=importlib.util.spec_from_file_location('proposal_current_publication',root/'tools/automation/publish-city-summary.py')
    publisher=importlib.util.module_from_spec(spec);spec.loader.exec_module(publisher)
    publisher.publish(city/'design.toml',city/'baghdad.toml',city/'README.md',check=True)
    return {(study/'manifest.json').relative_to(root).as_posix(),
            (city/'publication-manifest.json').relative_to(root).as_posix()}


def test_proposal_snapshot_and_current_nonadopted_contexts_are_verified():
    contexts=retained_research_context_paths()
    verify_proposal_snapshot(ROOT,PROPOSAL,data('manifest.json'),retained_context_paths=contexts)


@pytest.fixture
def retained_proposal(tmp_path):
    proposal=tmp_path/'proposal';proposal.mkdir()
    route=proposal/'route.json';route.write_bytes(b'{"length":1}')
    context=proposal/'context.json';context.write_bytes(b'{"revision":1}')
    pdf=proposal/'Baghdad-Proposal.pdf';pdf.write_bytes(b'%PDF-retained fixture')
    def receipt(path):
        return dict(bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    paths=[route,context,pdf]
    archive_manifest=proposal/'archive-manifest.json'
    archive_manifest.write_text(json.dumps(dict(members={p.relative_to(tmp_path).as_posix():receipt(p) for p in paths})))
    paths.append(archive_manifest)
    archive=proposal/'Baghdad-Proposal-Supporting-Data.zip'
    with zipfile.ZipFile(archive,'w') as stream:
        for p in paths:stream.writestr(p.relative_to(tmp_path).as_posix(),p.read_bytes())
    names=[p.relative_to(tmp_path).as_posix() for p in paths]
    manifest=dict(inputs={p.relative_to(tmp_path).as_posix():receipt(p) for p in (route,context)},
                  outputs={p.relative_to(tmp_path).as_posix():receipt(p) for p in (pdf,archive_manifest,archive)},
                  archive_members=names,supporting_archives={archive.name:names})
    return tmp_path,proposal,manifest,route,context,pdf,archive


def test_only_explicit_retained_context_can_differ_from_archived_inputs(retained_proposal):
    root,proposal,manifest,route,context,_,_=retained_proposal
    contexts={context.relative_to(root).as_posix()}
    context.write_bytes(b'{"revision":2}')
    verify_proposal_snapshot(root,proposal,manifest,retained_context_paths=contexts)
    with pytest.raises(AssertionError,match='context.json'):
        verify_proposal_snapshot(root,proposal,manifest)  # current/adopted comparison stays strict
    route.write_bytes(b'{"length":2}')
    with pytest.raises(AssertionError,match='route.json'):
        verify_proposal_snapshot(root,proposal,manifest,retained_context_paths=contexts)


@pytest.mark.parametrize('change',['archive','output','declared-input','declared-output'])
def test_retained_context_does_not_mask_archive_output_or_receipt_tampering(retained_proposal,change):
    root,proposal,manifest,_,context,pdf,archive=retained_proposal
    contexts={context.relative_to(root).as_posix()}
    if change=='archive':archive.write_bytes(b'corrupt archive')
    elif change in ('output','declared-output'):
        pdf.write_bytes(b'%PDF-altered fixture!')
        if change=='declared-output':
            manifest['outputs'][pdf.relative_to(root).as_posix()]=dict(bytes=pdf.stat().st_size,sha256=hashlib.sha256(pdf.read_bytes()).hexdigest())
    else:manifest['inputs'][context.relative_to(root).as_posix()]['sha256']='0'*64
    with pytest.raises((AssertionError,ValueError,zipfile.BadZipFile)):
        verify_proposal_snapshot(root,proposal,manifest,retained_context_paths=contexts)


def test_adopted_coupled_case_cannot_use_retained_proposal_exception(monkeypatch):
    original=json.loads
    def adopted(raw,*args,**kwargs):
        value=original(raw,*args,**kwargs)
        if isinstance(value,dict) and 'financial_baseline_replaced' in value:
            value['financial_baseline_replaced']=True
        return value
    monkeypatch.setattr(json,'loads',adopted)
    with pytest.raises(AssertionError):retained_research_context_paths()


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


def test_population_and_obstacle_evidence_are_published_without_physical_release():
    inputs = set(data('manifest.json')['inputs'])
    for relative in ('engineering/access/summary.json', 'engineering/access/population-pixels.npz.gz',
                     'engineering/clearance/summary.json', 'engineering/clearance/clearance-register.json.gz'):
        assert (CITY/relative).relative_to(ROOT).as_posix() in inputs
    access = data('engineering/access/summary.json')
    clearance = data('engineering/clearance/summary.json')
    narrative = (CITY/'BAGHDAD-PROPOSAL.md').read_text()
    for row in access['population']['catchments']:
        assert f"{row['covered_population_2020']:,.0f}" in narrative
        assert f"{row['fraction_of_raster_population']:.1%}" in narrative
    assert 'not verified walksheds' in narrative
    assert 'straight viaduct concept remains obstacle-unreleased' in narrative
    assert not clearance['physical_release']
    assert f"{clearance['beam_building_status']['beam-roof-collision']:,} provisional roof clashes" in narrative
    assert 'Current financial figures include no unpriced adopted obstacle solution.' in narrative


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
    assert manifest['facts']['programme_depot_count']==len(__import__('tomllib').loads((CITY/'design.toml').read_text())['lines'])
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


def test_current_energy_and_repayment_text_tracks_generated_scenario():
    import tomllib
    from osr_scenario.network_readme import _energy_plan, compute_stats
    design = tomllib.loads((CITY/'design.toml').read_text())
    scenario = tomllib.loads((CITY/'baghdad.toml').read_text())
    energy = _energy_plan(design, scenario, compute_stats(design, scenario, design['city']['population']))
    text = (CITY/'BAGHDAD-PROPOSAL.md').read_text()
    assert f'{energy.scheduled_daily_train_journeys:,.0f} one way journeys' in text
    assert f'{energy.scheduled_daily_train_km:,.0f} train km per day' in text
    assert f'{energy.annual_energy_kwh/1e6:,.1f} GWh annual traction demand' in text
    pv_mw = sum(site.get('pv_nameplate_kw', 0) for site in scenario['sites'])/1000
    storage_mwh = sum(site.get('storage_capacity_kwh', 0) for site in scenario['sites'])/1000
    charging_mw = sum(station.get('charging_power_kw', 0) for station in scenario['stations'])/1000
    assert f'{pv_mw:,.1f} MW station/depot PV' in text
    assert f'{storage_mwh:,.1f} MWh site storage' in text
    assert f'{charging_mw:,.1f} MW connected charging' in text
    metrics = json.loads((CITY/'engineering/programme-recalculation/summary.json').read_text())['finance_cases']['local_positive']
    if metrics['terminal_all_debt_iqd'] < 1 and metrics['unfunded_support_iqd'] < 1:
        assert 'repay debt within this scenario' in text
        assert 'Current indexed fares and additional-income assumptions do not repay this scope' not in text
    else:
        assert 'retains unsourced support or unpaid debt' in text
    assert '(engineering/design-system/index.html)' in text
    assert '(engineering/federation/index.html)' in text


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
