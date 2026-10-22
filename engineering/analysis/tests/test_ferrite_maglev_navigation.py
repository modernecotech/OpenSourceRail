"""Current entrypoints preserve selection ownership and physical acceptance holds."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest

from engineering.ferrite_maglev import model, navigation

SPEC = importlib.util.spec_from_file_location('maglev_host_validator',model.ROOT/'tools/automation/validate-host-manifests.py')
HOSTS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HOSTS)


def command(*args,timeout=120):
    return subprocess.run([str(model.ROOT/'osr'),*args],cwd=model.ROOT,capture_output=True,text=True,timeout=timeout)


def test_selected_plan_resolves_only_current_city_compiler():
    primary = command('catalogue','plan','--city','baghdad','kisangani')
    assert primary.returncode==0, primary.stderr
    plan = json.loads(primary.stdout)
    assert plan['family']=='ferrite-pm-maglev-study'
    assert plan['commands']==[['./osr','city','baghdad'],['./osr','city','kisangani']]
    assert all(plan[k] is False for k in model.FLAGS)


def test_bad_complete_selection_is_rejected_before_any_write(tmp_path):
    output = tmp_path/'new'
    result = command('catalogue','run','--city','baghdad','nonexistent-city','--output',str(output))
    assert result.returncode!=0
    assert not output.exists()
    with pytest.raises(ValueError,match='distinct'):
        navigation.selected_plan(['baghdad','baghdad'])


def test_selected_generation_executes_maglev_without_touching_other_city_packets(tmp_path):
    report = navigation.run_selected(['baghdad'],output=tmp_path)
    assert report['family']=='ferrite-pm-maglev-study'
    assert [r['city'] for r in report['completed']]==['baghdad']
    assert sorted(p.name for p in tmp_path.iterdir())==['baghdad']
    city = json.loads((tmp_path/'baghdad/summary.json').read_text())
    assert city['architecture']=='ferrite-pm-maglev-study'
    assert all(city[k] is False for k in model.FLAGS)


def test_selected_generation_detects_new_files_in_unselected_packages(tmp_path,monkeypatch):
    from contextlib import nullcontext
    from engineering.ferrite_maglev import cities,workflow
    folders = {}
    for slug in ('one','two'):
        folder = tmp_path/'cities/catalogue/region/country'/slug
        (folder/'engineering/maglev').mkdir(parents=True)
        (folder/'city.json').write_text(json.dumps(dict(city=dict(slug=slug))))
        folders[slug] = folder
    monkeypatch.setattr(model,'ROOT',tmp_path)
    monkeypatch.setattr(cities,'find_city',lambda slug:folders[slug])
    monkeypatch.setattr(workflow,'locked',lambda:nullcontext())
    def incorrect_generation(*args,**kwargs):
        (folders['two']/'engineering/maglev/unrequested.json').write_text('{}')
        return dict(city='one')
    monkeypatch.setattr(cities,'generate',incorrect_generation)
    with pytest.raises(ValueError,match='unselected'):
        navigation.run_selected(['one'])


def test_capability_directory_uses_actual_primary_sources_and_detects_tampering(tmp_path):
    data = navigation.publish(tmp_path)
    from engineering.ferrite_maglev import transition
    assert data['inventory']['total_source_items']==len(transition.build()['items'])
    assert data['inventory']['primary_capabilities']==len(navigation.CAPABILITIES)
    assert data['accepted_item_count']==0
    assert all(r['engineering_accepted'] is False and (model.ROOT/r['source']).is_file() for r in data['capabilities'])
    navigation.publish(tmp_path,check=True)
    (tmp_path/'ledger.json').write_text('{}')
    with pytest.raises(ValueError,match='differs'):
        navigation.publish(tmp_path,check=True)


def test_default_city_artifact_index_is_current_and_cannot_assert_acceptance():
    data = navigation.city_index()
    assert data['family']=='ferrite-pm-maglev-study' and data['source_current']
    assert data['city_count']==266 and len(data['cities'])==266
    assert data['cities']['baghdad']['complete_city_programme_usd'] is None
    assert all(r['physical_release'] is False for r in data['cities'].values())


def test_readiness_is_current_and_keeps_all_requirements_open():
    # Readiness performs the same full cold verification as Workbench startup.
    result = command('readiness',timeout=600)
    assert result.returncode==0, result.stderr
    data = json.loads(result.stdout)
    assert data['family']=='ferrite-pm-maglev-study' and data['source_current']
    from engineering.ferrite_maglev import requirements
    assert data['accepted_physical_releases']==0
    assert data['open_requirements']==len(requirements.register()['requirements'])
    assert all(g['accepted'] is False for g in data['gates'])


def test_complete_workspace_inventory_includes_offline_maglev_core():
    assert HOSTS.validate()==[]
    profile = HOSTS.load_toml('deployment/maglev.toml')
    assert profile['services']==['osr-maglev-control']
    assert profile['io']['physical_outputs_enabled'] is False
    assert profile['runtime']['mode']=='offline-replay-only'


def test_readme_validation_follows_current_package_and_rejects_missing_or_released_evidence(tmp_path):
    from engineering.ferrite_maglev import cities
    spec = importlib.util.spec_from_file_location('primary_readme_check',model.ROOT/'tools/automation/check-readmes.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    root = tmp_path/'README.md'
    (tmp_path/'city.json').write_text(json.dumps(dict(city=dict(slug='example',name='Example'))))
    root.write_text('# Example\n\n[Current package](engineering/maglev/README.md)\n')
    body, errors = checker.primary_city_readme(root,root.read_text())
    assert body==root.read_text() and errors  # Missing primary package cannot pass.
    package = tmp_path/'engineering/maglev'
    package.mkdir(parents=True)
    (package/'README.md').write_text('# Primary city\n[Primary planning method](method.md)\n<!-- Generated by engineering.ferrite_maglev.cities; primary planning only. -->\n')
    summary = dict(architecture='ferrite-pm-maglev-study',**model.FLAGS)
    (package/'summary.json').write_text(json.dumps(summary))
    assert checker.primary_city_readme(root,root.read_text())==(body,[])
    summary['physical_release']=True
    (package/'summary.json').write_text(json.dumps(summary))
    assert checker.primary_city_readme(root,root.read_text())[1]
    assert checker.primary_city_readme(root,'<!-- osr-maglev-primary:start -->\n')[1]


def test_markdown_inventory_check_is_read_only_and_detects_drift(tmp_path,monkeypatch):
    import sys
    spec = importlib.util.spec_from_file_location('primary_doc_index',model.ROOT/'tools/automation/generate-doc-index.py')
    indexer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(indexer)
    path = tmp_path/'docs/INDEX.md'
    path.parent.mkdir()
    path.write_text('current\n')
    monkeypatch.setattr(indexer,'OUT',path)
    monkeypatch.setattr(indexer,'REPO_ROOT',tmp_path)
    monkeypatch.setattr(indexer,'generate',lambda:'current\n')
    monkeypatch.setattr(sys,'argv',['generate-doc-index.py','--check'])
    before = (path.stat().st_mtime_ns,path.read_bytes())
    assert indexer.main()==0 and (path.stat().st_mtime_ns,path.read_bytes())==before
    monkeypatch.setattr(indexer,'generate',lambda:'changed\n')
    assert indexer.main()==1 and (path.stat().st_mtime_ns,path.read_bytes())==before


@pytest.mark.parametrize('mutate',[
    lambda p:p['services'].append('unselected-service'),
    lambda p:p['release'].update(manufacturing_release=True),
    lambda p:p['release'].update(physical_release=0),
    lambda p:p['runtime'].update(target_timing_measured=True),
    lambda p:p['runtime'].update(examples=['sbc_replay','imaginary-hardware-driver']),
    lambda p:p['runtime'].update(examples=[[]]),
    lambda p:p['io'].update(physical_outputs_enabled=True),
    lambda p:p['io'].update(hardware_addresses=['/dev/ttyUSB0']),
    lambda p:p['io'].update(requirements=[]),
    lambda p:p.update(interface_qualification_required=[]),
    lambda p:p.update(runtime=[]),
])
def test_development_profile_rejects_physical_authority_and_invalid_interfaces(mutate):
    profile = deepcopy(HOSTS.load_toml('deployment/maglev.toml'))
    mutate(profile)
    assert HOSTS.validate_primary(profile)
