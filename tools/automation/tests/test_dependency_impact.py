import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('dependency_impact',ROOT/'tools/automation/dependency-impact.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)


def test_changed_shared_source_identifies_owner_without_modifying_evidence(tmp_path):
    source=tmp_path/'shared.py';source.write_text('old')
    artifact=next(iter(m.OWNERS));path=tmp_path/artifact;path.parent.mkdir(parents=True);record=dict(source_sha256={'shared.py':hashlib.sha256(source.read_bytes()).hexdigest()})
    path.write_text(json.dumps(record));before=path.read_bytes()
    assert m.impact([artifact],tmp_path)['invalidated']==[]
    source.write_text('new');result=m.impact([artifact],tmp_path)
    assert result['current_regeneration_required']==[artifact]
    assert result['invalidated'][0]['regenerate_command']
    assert path.read_bytes()==before and not result['source_hashes_rewritten']


def test_nested_maps_and_missing_dependencies_are_reported(tmp_path):
    p=tmp_path/'old.json';p.write_text(json.dumps(dict(review=dict(sources_sha256={'missing.py':'a'*64}))))
    result=m.impact(['old.json'],tmp_path)
    assert result['invalidated'][0]['state']=='scope-review-required'
    assert result['invalidated'][0]['changed_sources'][0]['current_sha256'] is None


def test_current_publication_detects_changed_output_locks_without_rewriting(tmp_path):
    artifact='cities/catalogue/west-asia/Iraq/Baghdad/publication-manifest.json'
    source=tmp_path/'coupled/manifest.json';source.parent.mkdir();source.write_text('old')
    path=tmp_path/artifact;path.parent.mkdir(parents=True)
    path.write_text(json.dumps(dict(sources_sha256={},
        outputs_sha256={'coupled/manifest.json':hashlib.sha256(source.read_bytes()).hexdigest()},
        # Context-free body hashes intentionally differ from full file bytes.
        reference_bodies_sha256={'coupled/manifest.json':'a'*64})))
    before=path.read_bytes()
    assert m.impact([artifact],tmp_path)['invalidated']==[]
    source.write_text('new')
    report=m.impact([artifact],tmp_path)
    assert report['current_regeneration_required']==[artifact]
    assert report['invalidated'][0]['changed_sources'][0]['source']=='coupled/manifest.json'
    assert report['invalidated'][0]['regenerate_command']==[
        'tools/automation/osr-python','tools/automation/publish-city-summary.py']
    assert path.read_bytes()==before


@pytest.mark.parametrize('defect',['changed','missing'])
def test_plural_operations_source_hashes_reopen_current_review_without_retagging(tmp_path,defect):
    artifact='engineering/operations/pilot-review.json'
    source=tmp_path/'tools/automation/workbench-server.py';source.parent.mkdir(parents=True)
    source.write_bytes(b'original workbench producer')
    relative=source.relative_to(tmp_path).as_posix()
    original_digest=hashlib.sha256(source.read_bytes()).hexdigest()
    path=tmp_path/artifact;path.parent.mkdir(parents=True)
    path.write_text(json.dumps(dict(source_sha256s={relative:original_digest},
                                   passed=True,movement_authority=False)))
    before=path.read_bytes()
    assert m.impact([artifact],tmp_path)['invalidated']==[]
    if defect=='changed':source.write_bytes(b'changed workbench producer')
    else:source.unlink()
    result=m.impact([artifact],tmp_path)
    assert result['current_regeneration_required']==[artifact]
    row=result['invalidated'][0]
    assert row['state']=='stale-current'
    assert row['regenerate_command']==[
        'tools/automation/osr-python','tools/automation/operations-pilot.py','--review']
    assert row['changed_sources']==[dict(source=relative,recorded_sha256=original_digest,
        current_sha256=hashlib.sha256(source.read_bytes()).hexdigest() if source.exists() else None)]
    assert path.read_bytes()==before
    assert not result['acceptance_changed'] and not result['source_hashes_rewritten']


def test_tracked_operations_pilot_review_is_current():
    completed=subprocess.run([sys.executable,str(ROOT/'tools/automation/operations-pilot.py'),'--check'],
                             cwd=ROOT,capture_output=True,text=True,check=False)
    assert completed.returncode==0,completed.stdout+completed.stderr
