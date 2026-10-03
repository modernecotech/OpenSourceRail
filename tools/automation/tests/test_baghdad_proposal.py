"""A complete Baghdad publication must preserve scope, evidence and cash totals."""
import csv
import hashlib
import json
from pathlib import Path
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[3]
CITY = ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
PROPOSAL = CITY/'proposal'


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
    docs = {p.relative_to(ROOT).as_posix() for p in CITY.rglob('*.md') if PROPOSAL not in p.parents}
    assert docs <= chapters
    inputs = set(manifest['inputs'])
    financial = {p.relative_to(ROOT).as_posix() for p in (CITY.parent/'finance').glob('baghdad-*') if p.is_file()}
    assert financial <= inputs
    assert len(chapters) == manifest['appendix_document_count']
    ops = json.loads((CITY/'operations/baghdad-operations-manifest.json').read_text())
    payload = (CITY/'operations'/ops['file']).relative_to(ROOT).as_posix()
    assert manifest['inputs'][payload]['sha256'] == ops['compressed_sha256']
    assert 'docs/rfcs/0033-tacs-runtime-and-resource-control.md' in chapters
    assert 'docs/rfcs/0032-train-centred-control.md' not in chapters


def test_national_capital_counts_the_existing_factory_once_and_keeps_baghdad_scope():
    n = data('national-context.json')
    p = json.loads((CITY.parent/'finance/baghdad-programme.json').read_text())
    m = data('manifest.json')
    assert n['factory_count'] == m['factory_count'] == 1
    assert m['baghdad_financing_scope'] == p['included_cities'] == ['Baghdad']
    assert not n['baghdad_financing_includes_national_expansion']
    assert n['city_count'] == len(list(CITY.parent.glob('*/design.toml'))) == 18
    assert n['shared_factory_usd'] == p['factory']['cost_usd']
    assert n['shared_factory_epc_usd'] == p['factory']['epc_usd']
    assert sum(c['city_capex_usd'] for c in n['cities'])+n['shared_factory_usd']+n['shared_factory_epc_usd'] == pytest.approx(n['total_national_capital_usd'])
    others = sum(c['city_capex_usd'] for c in n['cities'] if c['city'] != 'Baghdad')
    assert n['future_incremental_city_capital_after_baghdad_usd'] == pytest.approx(others)
    assert n['total_national_capital_usd'] == pytest.approx(p['total_capex_usd']+others)
    assert m['facts']['baghdad_total_capex_usd'] == p['total_capex_usd']
    assert m['facts']['baghdad_government_share'] == .25


def test_network_registers_preserve_complete_counts_and_optional_civil_fields():
    def rows(name):
        with (PROPOSAL/'registers'/name).open() as handle:
            return list(csv.DictReader(handle))
    import tomllib
    design = tomllib.loads((CITY/'design.toml').read_text())
    assert len(rows('stations.csv')) == len(design['stations']) == 182
    assert {r['id'] for r in rows('stations.csv')} == {r['id'] for r in design['stations']}
    assert len(rows('civil-segments.csv')) == len(design['civil_segments']) == 2312
    assert any(r['viaduct_product'] for r in rows('civil-segments.csv'))
    assert sum(int(r['trainset_count']) for r in rows('fleets.csv')) == 831
    assert len(rows('interchanges.csv')) == len(design['interchanges'])
    assert len(rows('junctions.csv')) == len(design['junctions'])
    narrative = (PROPOSAL/'BAGHDAD-PROPOSAL.md').read_text()
    assert 'RFC 0033' in narrative and 'superseded' in narrative
    assert '293.309' in narrative and '189.758' in narrative
    assert '14 deployment gates remain open' in narrative
    assert 'future national' in narrative.lower()
