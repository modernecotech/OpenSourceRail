"""Country publications must distinguish current, historical and unpriced scope."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/automation'))
import iraq_current_basis as basis


def test_country_basis_matches_its_inputs_and_retained_financial_case():
    current=basis.current_basis()
    published=json.loads((basis.COUNTRY/'CURRENT-PLANNING-BASIS.json').read_text())
    assert published==current
    for relative,digest in current['sources_sha256'].items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest
    financial=current['financial_case']
    assert financial['all_debt_cleared_month'] is None
    assert financial['terminal_debt_iqd']>0 and not financial['financing_committed']
    assert current['national_budget_usd'] is None
    assert current['accelerated_case']['capital_usd'] is None


def test_country_documents_lead_with_current_basis_and_preserve_historical_scope():
    for name in ('NATIONAL-BRIEF.md','IRAQ-FUNDING-PROGRAMME.md'):
        text=(basis.COUNTRY/name).read_text()
        assert basis.current_header() in text
        assert '**Foreign-capital advantage:**' not in text
        assert 'USD 8.312bn' in text
        assert 'purchase cash only' in text
        assert 'Iraq has existing precast facilities and expertise' in text
    funding=(basis.COUNTRY/'IRAQ-FUNDING-PROGRAMME.md').read_text()
    assert basis.funding_document(funding)==funding
    assert funding.count(basis.HISTORICAL_INTRO)==1
    assert 'Historical funding calculation — retained comparator' in funding


def test_regeneration_refreshes_iraq_even_when_skipping_portfolio():
    spec=importlib.util.spec_from_file_location('baghdad_regeneration',ROOT/'tools/automation/regenerate-baghdad-studies.py')
    regeneration=importlib.util.module_from_spec(spec);spec.loader.exec_module(regeneration)
    city_steps=regeneration.STEPS[:-2]
    assert ('tools/automation/generate-national-briefs.py','--country','IQ') in city_steps
    assert city_steps.index(('tools/automation/connected-build-study.py','--refresh-cad'))<city_steps.index(('tools/automation/generate-national-briefs.py','--country','IQ'))
