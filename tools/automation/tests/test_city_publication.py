"""Current public summaries cannot silently revert to earlier financial scope."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('city_publication',ROOT/'tools/automation/publish-city-summary.py')
publication=importlib.util.module_from_spec(spec);spec.loader.exec_module(publication)
CITY=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
STUDY=CITY/'engineering/programme-recalculation'


def test_baghdad_landing_page_matches_current_scope_and_cashflows():
    publication.publish(CITY/'design.toml',CITY/'baghdad.toml',CITY/'README.md',check=True)
    text=(CITY/'README.md').read_text();case=json.loads((STUDY/'local_positive.json').read_text())
    people=json.loads((STUDY/'workforce.json').read_text());depots=json.loads((STUDY/'depots.json').read_text())
    assert f"USD {case['metrics']['total_capital_usd']/1e9:.3f}bn" in text
    assert f"{people['reference_required_fte']:,} FTE" in text
    assert f"USD {depots['gross_reference_cost_usd']/1e6:.3f}m" in text
    assert f"{depots['number_of_depots']} depots" in text and f"{depots['full_fleet_storage_slots']} storage slots" in text
    assert 'Foreign-capital advantage' not in text
    assert '| Depots | $8.0 M |' not in text
    assert '50% government USD cash / 50% proposed Chinese USD credit' in text
    assert 'straight core radial tangents' in text and 'current reworked geometry' in text


def test_receipt_refresh_preserves_model_and_approval_values(tmp_path):
    doc=tmp_path/'old.md';doc.write_text('Earlier appraisal\n')
    a=tmp_path/'a.json';b=tmp_path/'b.json'
    a.write_bytes(publication.encoded(dict(total_capital_usd=17,approved=False,outputs_sha256={'old.md':publication.sha(doc.read_bytes())})))
    b.write_bytes(publication.encoded(dict(fares=[1,2,3],released=False,sources_sha256={'a.json':publication.sha(a.read_bytes())})))
    planned=publication.refresh_receipts(tmp_path,[a,b],{doc:b'Original reference; see current study\n'})
    result_a=json.loads(planned[a]);result_b=json.loads(planned[b])
    assert result_a['total_capital_usd']==17 and not result_a['approved']
    assert result_b['fares']==[1,2,3] and not result_b['released']
    assert result_a['outputs_sha256']['old.md']==publication.sha(planned[doc])
    assert result_b['sources_sha256']['a.json']==publication.sha(planned[a])
    assert doc.read_text()=='Earlier appraisal\n'  # planning is atomic before writes


def test_receipt_refresh_rejects_preexisting_drift(tmp_path):
    doc=tmp_path/'old.md';doc.write_text('Locally altered evidence\n')
    receipt=tmp_path/'summary.json'
    receipt.write_bytes(publication.encoded(dict(outputs_sha256={'old.md':'0'*64})))
    with pytest.raises(ValueError,match='receipt drift'):
        publication.refresh_receipts(tmp_path,[receipt],{doc:b'New context\n'})
    assert doc.read_text()=='Locally altered evidence\n'


def test_stale_study_stops_publication_without_overwriting_readme(tmp_path,monkeypatch):
    output=tmp_path/'README.md';output.write_text('Current summary\n')
    monkeypatch.setattr(publication,'render_readme',lambda *args,**kwargs:'Original catalogue summary')
    def reject(*args):raise ValueError('Current scope study is stale')
    monkeypatch.setattr(publication,'verify_study',reject)
    with pytest.raises(ValueError,match='study is stale'):
        publication.publish(CITY/'design.toml',CITY/'baghdad.toml',output)
    assert output.read_text()=='Current summary\n'


def test_other_city_keeps_its_own_catalogue_basis(tmp_path):
    city=CITY.parent/'Samawah';output=tmp_path/'README.md'
    publication.publish(city/'design.toml',city/'samawah.toml',output)
    assert output.read_text()==publication.current_catalogue_context(city/'design.toml',publication.render_readme(city/'design.toml',city/'samawah.toml'))
    assert 'line-local depots' in output.read_text()
    assert 'retained country income proxy' in output.read_text()
    assert 'local_positive' not in output.read_text()


def test_contexts_are_idempotent_and_retain_original_reference_bodies():
    config=publication.tomllib.loads(publication.CONFIG.read_text())['city'][0]
    paths=[CITY/p for p in config['references']]+[ROOT/p for p in config['portfolio_references']]
    for path in paths:
        assert publication.reference_context(path,STUDY)==path.read_bytes()
        assert path.read_text().count(publication.BEGIN)==1
        assert 'Original catalogue or earlier scope reference' in path.read_text()
    pipeline=(ROOT/'tools/automation/regenerate-city.sh').read_text()
    assert 'publish-city-summary.py' in pipeline
    assert '-m osr_scenario.network_readme' not in pipeline
    for name in ('generate-city-packages-fast.py','refresh-city-controls.py'):
        caller=(ROOT/'tools/automation'/name).read_text()
        assert 'publish-city-summary.py' in caller
        assert '"osr_scenario.network_readme"' not in caller
