"""Retained baseline evidence must reproduce offline and detect tampering."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    'cost_reconciliation', ROOT / 'tools/automation/baghdad_cost_reconciliation.py')
MODEL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODEL)


def test_retained_snapshot_is_offline_and_source_bound(tmp_path, monkeypatch):
    city = tmp_path / 'city'
    archive = city / 'engineering/cost-reconciliation/baseline-sources.json.gz'
    archive.parent.mkdir(parents=True)
    raw = b'{"total": 7}\n'
    snapshot = dict(revision='reviewed', sources={
        'city/case.json': dict(text=raw.decode(), sha256=hashlib.sha256(raw).hexdigest())})
    archive.write_bytes(gzip.compress(json.dumps(snapshot).encode()))
    monkeypatch.setattr(MODEL, 'ROOT', tmp_path)
    monkeypatch.setattr(MODEL, 'CITY', city)
    def forbidden(*args, **kwargs):
        raise AssertionError('Retained evidence must not require Git history')
    monkeypatch.setattr(MODEL.subprocess, 'check_output', forbidden)
    assert MODEL.historical('reviewed', city/'case.json')[0] == raw
    with pytest.raises(ValueError, match='revision differs'):
        MODEL.historical('another', city/'case.json')
    snapshot['sources']['city/case.json']['text'] = '{"total": 8}\n'
    archive.write_bytes(gzip.compress(json.dumps(snapshot).encode()))
    with pytest.raises(ValueError, match='snapshot changed'):
        MODEL.historical('reviewed', city/'case.json')
