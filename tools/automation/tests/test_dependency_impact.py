import hashlib
import importlib.util
import json
from pathlib import Path
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
