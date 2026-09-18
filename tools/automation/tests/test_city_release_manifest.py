import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('city_evidence', ROOT/'deployment/example-city/evidence.py')
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)


def fixture(folder):
    hashes = {}
    for name in evidence.REQUIRED:
        path = folder/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dict(passed=True, checks=[dict(passed=True)])))
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = dict(schema='osr-city-release-evidence/1', passed=True, clean_source=True,
                    commit='candidate', scenario_source=dict(commit='candidate', clean_source=True), reports=hashes)
    (folder/'city-evidence.json').write_text(json.dumps(manifest))
    return manifest


def test_complete_city_manifest_and_exact_commit(tmp_path):
    fixture(tmp_path)
    assert evidence.validate(tmp_path, 'candidate')['passed']
    with pytest.raises(ValueError, match='commit'):
        evidence.validate(tmp_path, 'different')


@pytest.mark.parametrize('change', ['dirty', 'old-start', 'dirty-start', 'missing', 'tamper', 'failed', 'empty', 'escape'])
def test_rejects_unbound_incomplete_or_tampered_evidence(tmp_path, change):
    manifest = fixture(tmp_path)
    if change == 'dirty': manifest['clean_source'] = False
    if change == 'old-start': manifest['scenario_source']['commit'] = 'old'
    if change == 'dirty-start': manifest['scenario_source']['clean_source'] = False
    if change == 'missing': manifest['reports'].pop('disposition-report.json')
    if change == 'escape': manifest['reports']['../escape.json'] = 'digest'
    if change in {'tamper', 'failed', 'empty'}:
        path = tmp_path/'business-report.json'
        path.write_text(json.dumps(dict(passed=change != 'failed', checks=[])))
        if change != 'tamper': manifest['reports']['business-report.json'] = hashlib.sha256(path.read_bytes()).hexdigest()
    (tmp_path/'city-evidence.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError): evidence.validate(tmp_path, 'candidate')


def test_failed_record_is_not_published_as_passed(tmp_path, monkeypatch):
    fixture(tmp_path)
    (tmp_path/'run-started.json').write_text(json.dumps(dict(commit='old', clean_source=True)))
    monkeypatch.setattr(evidence.subprocess, 'check_output', lambda args, **kw: '' if 'status' in args else 'candidate')
    h = SimpleNamespace(ROOT=tmp_path, OUTPUT=tmp_path, write=lambda path, data: path.write_text(json.dumps(data)))
    with pytest.raises(ValueError): evidence.record(h)
    assert json.loads((tmp_path/'city-evidence.json').read_text())['passed'] is False
