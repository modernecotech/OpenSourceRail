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


@pytest.fixture
def pending_network(tmp_path,monkeypatch):
    monkeypatch.setattr(publication,'ROOT',tmp_path)
    city=tmp_path/'city';out=city/'engineering/alignment';out.mkdir(parents=True)
    design=city/'design.toml';design.write_text('[city]\nslug="fixture"\nname="Fixture"\n[[lines]]\nname="line-1"\nlength_m=1200.0\n[[stations]]\nline="line-1"\n[[fleets]]\ntrainset_count=2\n')
    (city/'package-manifest.json').write_bytes(publication.encoded(dict(passed=False,planning_example_complete=False,package_status='incomplete',stale_analysis_sources=[{'artifact':'energy'}])))
    routes={'lines':[{'name':'line-1','cells':[[0,0],[1,1]]}]};(city/'corridors.json').write_bytes(publication.encoded(routes))
    (city/'fixture.corridor.geojson').write_bytes(b'current native corridor')
    (city/'fixture-network-map.png').write_bytes(b'unit fixture preview')
    dependency=tmp_path/'seed';dependency.write_bytes(b'retained input')
    (out/'water-source-receipt.json').write_bytes(b'retained water receipt')
    audit_generator=tmp_path/'tools/automation/audit-city-geography.py';audit_generator.parent.mkdir(parents=True);audit_generator.write_bytes(b'audit generator')
    proof=dict(schema='osr-city-network-correction/1',candidate_sha256=publication.sha(publication.encoded(routes)),engineering_release=False,physical_release=False,source_sha256={'seed':publication.sha(dependency.read_bytes())})
    (out/'network-correction.json').write_bytes(publication.encoded(proof))
    audit=dict(passed=True,operating_release=False,physical_release=False,generator_sha256=publication.sha(audit_generator.read_bytes()),cities=[dict(city='fixture',passed=True,connected_network=True,design_sha256=publication.sha(design.read_bytes()),corridor_sha256=publication.sha((city/'fixture.corridor.geojson').read_bytes()),water_source_receipt_sha256=publication.sha((out/'water-source-receipt.json').read_bytes()))])
    (out/'network-topology.json').write_bytes(publication.encoded(audit))
    old=city/'engineering/simulation/validation-summary.json';old.parent.mkdir();old.write_text('{"nominal_completion":99.9}')
    return design


def test_pending_network_publishes_geometry_without_reusing_old_numerical_passes(pending_network):
    text=publication.provisional_network_summary(pending_network).decode()
    assert 'Engineering revalidation pending' in text and '1.2 km' in text
    assert '2 trainsets' in text and '99.9' not in text
    assert len(text.splitlines())<=120
    assert json.loads((pending_network.parent/'package-manifest.json').read_text())['passed'] is False


@pytest.mark.parametrize('change',['dependency','audit-failure','candidate-revision','missing-map'])
def test_pending_network_publication_holds_failed_or_stale_geometry(pending_network,change):
    out=pending_network.parent/'engineering/alignment'
    if change=='dependency':(publication.ROOT/'seed').write_bytes(b'changed source')
    elif change=='missing-map':(pending_network.parent/'fixture-network-map.png').unlink()
    else:
        path=out/'network-topology.json';audit=json.loads(path.read_text())
        if change=='audit-failure':audit['passed']=False
        else:audit['cities'][0]['design_sha256']='0'*64
        path.write_bytes(publication.encoded(audit))
    with pytest.raises(ValueError):publication.provisional_network_summary(pending_network)


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
    receipt = json.loads((CITY/'publication-manifest.json').read_text())
    assert not any('/engineering/design-system/' in name or '/engineering/federation/' in name
                   for name in receipt['outputs_sha256'])
    assert '(engineering/design-system/index.html)' in text


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
    assert output.read_text()==publication.compact_local_summary(publication.design_system_context(publication.current_catalogue_context(city/'design.toml',publication.residential_context(city/'design.toml',publication.access_context(city/'design.toml',publication.render_readme(city/'design.toml',city/'samawah.toml'))))))
    assert '| Estimated station catchment |' not in output.read_text()
    assert 'Direct transfers / reachable line pairs' in output.read_text()
    assert 'Residents within 800 m radial station catchments' in output.read_text()
    assert 'line-local depots' in output.read_text()
    assert 'retained country income proxy' in output.read_text()
    assert 'local_positive' not in output.read_text()


def test_contexts_are_idempotent_and_retain_original_reference_bodies():
    config=publication.tomllib.loads(publication.CONFIG.read_text())['city'][0]
    paths=[CITY/p for p in config['references']]+[ROOT/p for p in config['portfolio_references']]
    for path in paths:
        assert publication.reference_context(path,STUDY)==path.read_bytes()
        if path.name in ('NATIONAL-BRIEF.md','IRAQ-FUNDING-PROGRAMME.md'):
            assert path.read_text().count('<!-- OSR CURRENT IRAQ BASIS -->')==1
            from iraq_current_basis import current_basis
            financial=current_basis()['financial_case']
            debt_text='no month in which all debt is cleared' if financial['all_debt_cleared_month'] is None else f"All debt clears at model month {financial['all_debt_cleared_month']}"
            assert debt_text in path.read_text()
        else:
            assert path.read_text().count(publication.BEGIN)==1
            assert 'Original catalogue or earlier scope reference' in path.read_text()
    pipeline=(ROOT/'tools/automation/regenerate-city.sh').read_text()
    assert 'publish-city-summary.py' in pipeline
    assert '-m osr_scenario.network_readme' not in pipeline
    for name in ('generate-city-packages-fast.py','refresh-city-controls.py'):
        caller=(ROOT/'tools/automation'/name).read_text()
        assert 'publish-city-summary.py' in caller
        assert '"osr_scenario.network_readme"' not in caller
