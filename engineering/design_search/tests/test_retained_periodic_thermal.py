"""Pinned thermal archive controls: retained evidence never grants admission.

All adversarial modifications operate on private pytest copies, not source or
published packets. These are cooperative checks, not an operating-system sandbox.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import stat

import pytest

from engineering.design_search import retained_periodic_thermal as periodic
from engineering.design_search import retained_service_energy_materialize as materialize
from engineering.design_search import retained_service_energy_epoch as epoch
from engineering.design_search import retained_source_epoch as retained
from engineering.station_rail import ROOT

MANIFEST_ID = 'e2ac8e01ac36eaa19d8f5c59c0dcfc28de6acd7759065a0a7b122cd8d7c3d66d'
ARCHIVE_ID = 'd2f4511f180592083945bb993658353218b9efcf91d0dd3f21d02e58399967b9'
PINS_ID = '91d8be8f7893aea692e90683c214bbda0d35c4dbe1a652c7cb8908e3d3a4f050'


def payload(root, name):
    return Path(root) / Path(name)


@pytest.fixture
def private_root(tmp_path):
    root = tmp_path / 'isolated-root'; root.mkdir()
    for name in (periodic.PACKET, periodic.ARCHIVE):
        dest = payload(root, name); dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(payload(ROOT, name), dest)
        for directory in (dest, *(p for p in dest.rglob('*') if p.is_dir())):
            directory.chmod(directory.stat().st_mode | stat.S_IWUSR | stat.S_IXUSR)
    pin = payload(root, periodic.PINS); pin.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(payload(ROOT, periodic.PINS), pin)
    for name in periodic.HELPERS:
        dest = payload(root, name); dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(payload(ROOT, name), dest)
    return root


def writable(path):
    path = Path(path); path.chmod(path.stat().st_mode | stat.S_IWUSR)
    return path


def test_actual_externally_pinned_archive_has_442_sources_and_thermal_subset():
    pins = json.loads(payload(ROOT, periodic.PINS).read_bytes())
    meta, _, _, _ = materialize._preflight(payload(ROOT, periodic.ARCHIVE), pins, PINS_ID, ARCHIVE_ID)
    manifest_path = payload(ROOT, periodic.PACKET) / 'manifest.json'
    manifest = json.loads(manifest_path.read_bytes())
    assert manifest['manifest_id'] == MANIFEST_ID
    assert len(meta['original_source_sha256']) == 442 and len(manifest['source_sha256']) == 55
    assert all(meta['original_source_sha256'].get(k) == v for k, v in manifest['source_sha256'].items())
    assert meta['records']['periodic-thermal-research/manifest.json']['manifest_id'] == MANIFEST_ID
    assert meta['records']['periodic-thermal-research/manifest.json']['manifest_sha256'] == epoch._file_data(manifest_path)[0]
    inventory = epoch._inventory(payload(ROOT, periodic.PACKET))
    assert inventory == meta['folders'][str(periodic.PACKET)] and inventory['file_count'] == 128
    assert all(manifest[key] is False for key in epoch.FLAGS)


def test_real_pinned_packet_verifies_without_current_evaluator_or_physical_promotion():
    result = periodic.verify()
    assert result['verified'] is True
    assert result['current_evaluator_admission'] is False
    assert all(result[key] is False for key in epoch.FLAGS)


@pytest.mark.parametrize('kind', ['pins', 'archive-manifest', 'archive-tar', 'packet-manifest',
                                  'packet-result', 'producer', 'extra-file', 'empty-directory',
                                  'symlink', 'hardlink', 'fifo'])
def test_private_tampered_or_undeclared_pinned_input_is_rejected(private_root, kind):
    archive = payload(private_root, periodic.ARCHIVE)
    packet = payload(private_root, periodic.PACKET)
    if kind == 'pins':
        path = writable(payload(private_root, periodic.PINS)); value = json.loads(path.read_bytes())
        value['manifest_ids']['periodic-thermal-research/manifest.json'] = '0' * 64
        value['pins_id'] = retained._id({k: v for k, v in value.items() if k != 'pins_id'})
        path.write_bytes(retained._encoded(value))
    elif kind == 'archive-manifest':
        path = writable(archive / 'manifest.json'); value = json.loads(path.read_bytes())
        value['physical_accepted'] = True
        value['archive_id'] = retained._id({k: v for k, v in value.items() if k != 'archive_id'})
        path.write_bytes(retained._encoded(value))
    elif kind == 'archive-tar':
        path = writable(archive / 'sources.tar.gz')
        with path.open('r+b') as stream:
            stream.seek(-1, os.SEEK_END); old = stream.read(1); stream.seek(-1, os.SEEK_END)
            stream.write(bytes([old[0] ^ 1]))
    elif kind == 'packet-manifest':
        path = writable(packet / 'manifest.json'); value = json.loads(path.read_bytes())
        value['engineering_accepted'] = True
        value['manifest_id'] = retained._id({k: v for k, v in value.items() if k != 'manifest_id'})
        path.write_bytes(retained._encoded(value))
    elif kind == 'packet-result':
        writable(packet / 'result.json').write_text('{}')
    elif kind == 'producer':
        writable(packet / 'original' / 'producer-v10.py').write_text('# modified producer\n')
    elif kind == 'extra-file':
        (packet / 'undeclared.txt').write_text('unexpected')
    elif kind == 'empty-directory':
        (packet / 'undeclared-empty').mkdir()
    elif kind == 'symlink':
        (packet / 'undeclared-link').symlink_to(packet / 'result.json')
    elif kind == 'hardlink':
        os.link(packet / 'result.json', packet / 'undeclared-hardlink')
    else:
        os.mkfifo(packet / 'undeclared-fifo')
    with pytest.raises((ValueError, OSError)):
        periodic.verify(root=private_root)


def test_unrelated_changed_current_source_does_not_reclassify_historical_packet(private_root):
    source = private_root / 'engineering/design_search/interface_graph.py'
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text('# deliberately different current nonphysical source\n')
    first = periodic.verify(root=private_root)
    source.write_text('# another current nonphysical source revision\n')
    second = periodic.verify(root=private_root)
    assert first == second
    assert first['current_evaluator_admission'] is False and first['physical_accepted'] is False


def test_symlinked_source_root_is_rejected(private_root, tmp_path):
    link = tmp_path / 'root-link'; link.symlink_to(private_root, target_is_directory=True)
    with pytest.raises((ValueError, OSError)):
        periodic.verify(root=link)


@pytest.mark.parametrize('name', list(periodic.HELPERS))
def test_executing_helper_must_match_verifier_root_bytes(private_root, name):
    writable(payload(private_root, name)).write_text('# changed verifier\n')
    with pytest.raises((ValueError, OSError)):
        periodic.verify(root=private_root)


@pytest.mark.parametrize('change', ['packet-file', 'packet-extra', 'packet-empty-directory', 'archive-extra'])
def test_verification_rechecks_inputs_and_inventory_before_return(private_root, monkeypatch, change):
    original = periodic._inspect
    injected = False
    def changed_after_initial_inspection(root):
        nonlocal injected
        result = original(root)
        if not injected:
            injected = True
            packet = payload(private_root, periodic.PACKET)
            if change == 'packet-file': writable(packet / 'result.json').write_text('{}')
            elif change == 'packet-extra': (packet / 'injected.txt').write_text('unexpected')
            elif change == 'packet-empty-directory': (packet / 'injected-empty').mkdir()
            else: (payload(private_root, periodic.ARCHIVE) / 'injected.txt').write_text('unexpected')
        return result
    monkeypatch.setattr(periodic, '_inspect', changed_after_initial_inspection)
    with pytest.raises((ValueError, OSError)):
        periodic.verify(root=private_root)
    assert injected


@pytest.mark.parametrize('changed_name', list(periodic.TESTS))
def test_current_original_test_contract_cannot_be_silently_replaced(private_root, monkeypatch, changed_name):
    test_bytes = {name: payload(ROOT, name).read_bytes() for name in periodic.TESTS}
    for name, raw in test_bytes.items():
        target = payload(private_root, name); target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    monkeypatch.setattr(periodic.extra, '_git_bytes', lambda root, name: test_bytes[name])
    periodic._test_inputs(private_root)
    payload(private_root, changed_name).write_text('# revised test would be silently lost\n')
    with pytest.raises(ValueError, match='test contract'):
        periodic._test_inputs(private_root)


@pytest.mark.skipif(os.environ.get('OSR_TEST_RETAINED_PERIODIC') != '1',
                    reason='Explicit archived-source replay integration only')
def test_exact_original_sources_and_old_publication_are_replayed_without_current_admission(tmp_path):
    output = tmp_path / 'replay'
    result = periodic.replay(output)
    assert result['verified'] is True and result['original_epoch_numerical_reexecuted'] is True
    assert result['current_evaluator_numerical_reexecuted'] is False
    assert result['original_manifest_id'] == MANIFEST_ID
    assert result['current_evaluator_admission'] is False
    assert all(result[key] is False for key in epoch.FLAGS)
    assert 'no OS sandbox' in result['isolation']
    context = json.loads((output / 'context.json').read_bytes())
    assert context['archive_id'] == ARCHIVE_ID and context['pins_id'] == PINS_ID
    assert len(context['source_sha256']) >= 442 and set(context['test_source_sha256']) == set(periodic.TESTS)
    assert json.loads((output / 'child-result.json').read_bytes())['tests_passed'] is True
    assert (output / 'logs/stdout.log').is_file() and (output / 'logs/stderr.log').is_file()


@pytest.mark.skipif(os.environ.get('OSR_TEST_RETAINED_PERIODIC') != '1',
                    reason='Explicit archived-source context integration only')
@pytest.mark.parametrize('change', ['producer-resealed', 'empty-directory', 'unlisted-file'])
def test_sealed_private_source_context_cannot_be_modified(tmp_path, change):
    output = tmp_path / 'context'
    context = periodic.prepare_context(output)
    source_root = output / 'root'
    if change == 'producer-resealed':
        name = 'engineering/design_search/periodic_thermal_research.py'
        path = source_root / name; path.write_text('# forged archived producer\n')
        context['source_sha256'][name] = retained._file_data(path)[0]
        context['context_id'] = retained._id({k: v for k, v in context.items() if k != 'context_id'})
        (output / 'context.json').write_bytes(retained._encoded(context))
    elif change == 'empty-directory':
        (source_root / 'injected-empty').mkdir()
    else:
        (source_root / 'injected.txt').write_text('unexpected')
    with pytest.raises((ValueError, OSError)):
        periodic._context(output, ROOT)
