"""Startup integrity checks do not claim numerical reproduction or acceptance."""
from hashlib import sha256
import json

import pytest

from engineering.trip_dynamics.interface_integrity import primary_integrity


def packet(root):
    source = root/'source.py'; source.write_text('retained implementation\n')
    folder = root/'docs/design-engine/ferrite-maglev/reference'
    folder.mkdir(parents=True)
    payload = folder/'result.json'; payload.write_text('{}\n')
    manifest = dict(schema='osr-primary-infrastructure-publication/1',
                    family='ferrite-pm-maglev-study',
                    design_complete=False, physical_validation=False,
                    manufacturing_release=False, physical_release=False,
                    source_sha256={'source.py':sha256(source.read_bytes()).hexdigest()},
                    files_sha256={'result.json':sha256(payload.read_bytes()).hexdigest()})
    receipt = folder/'manifest.json'; receipt.write_text(json.dumps(manifest))
    return source, payload, receipt, manifest


def test_current_envelope_has_no_numerical_or_acceptance_credit(tmp_path):
    packet(tmp_path)
    value = primary_integrity(tmp_path)
    assert value['state'] == 'current'
    assert value['source_files'] == value['payload_files'] == 1
    assert value['scope'] == 'source-and-payload-integrity-only'
    for key in ('numerical_verification_executed', 'engineering_accepted', 'physical_accepted'):
        assert value[key] is False


@pytest.mark.parametrize('kind', ['source', 'payload', 'extra-payload', 'new-source', 'release', 'traversal', 'symlink'])
def test_changed_or_invalid_envelope_is_held(tmp_path, kind):
    source, payload, receipt, manifest = packet(tmp_path)
    provider = None
    if kind == 'source': source.write_text('changed implementation\n')
    elif kind == 'payload': payload.write_text('{"changed":true}')
    elif kind == 'extra-payload': (payload.parent/'extra.json').write_text('{}')
    elif kind == 'new-source':
        provider = lambda: dict(manifest['source_sha256'], **{'new-source.py':'0'*64})
    elif kind == 'release': manifest['physical_release'] = True
    elif kind == 'traversal': manifest['source_sha256'] = {'../outside':'0'*64}
    elif kind == 'symlink':
        linked = tmp_path/'linked.py'; linked.write_text(source.read_text())
        source.unlink(); source.symlink_to(linked)
    receipt.write_text(json.dumps(manifest))
    value = primary_integrity(tmp_path, source_provider=provider)
    assert value['state'] == 'held' and value['issue_count'] > 0
    assert value['numerical_verification_executed'] is False


def test_missing_packet_remains_accessible_as_held(tmp_path):
    assert primary_integrity(tmp_path)['state'] == 'held'


@pytest.mark.parametrize('value', [None, [], ['source.py'], {'source.py':None}, {'source.py':'bad-digest'}])
def test_malformed_receipt_remains_accessible_as_held(tmp_path, value):
    _, _, receipt, manifest = packet(tmp_path)
    manifest['source_sha256'] = value
    receipt.write_text(json.dumps(manifest))
    assert primary_integrity(tmp_path)['state'] == 'held'
