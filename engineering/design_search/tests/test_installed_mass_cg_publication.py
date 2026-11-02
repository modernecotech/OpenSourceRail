import shutil
import os
from pathlib import Path

import pytest

from engineering.design_search import installed_mass_cg_publication as publication


def test_pinned_current_publication_replays():
    result = publication.verify(expected_manifest_id='53f880cc6cd0a422aa5992b302899b70841b795671c133e4ebe9880e84541ebc')
    assert result['evaluation_id'] == publication.EPOCHS[-1][3]
    assert result['physical_accepted'] is False
    with pytest.raises(ValueError, match='identity'):
        publication.verify(expected_manifest_id='0'*64)


def test_worker_rejects_modified_evidence_and_symlink_root(tmp_path):
    source = publication.ROOT/publication.OUTPUT/'original/v3'
    target = tmp_path/'worker'
    shutil.copytree(source, target)
    (target/'outputs/python313-result.json').chmod(0o600)
    (target/'outputs/python313-result.json').write_text('{}')
    with pytest.raises(ValueError, match='package differs'):
        publication._worker(target, publication.EPOCHS[-1])
    link = tmp_path/'link'
    link.symlink_to(source, target_is_directory=True)
    with pytest.raises(ValueError, match='Symlink'):
        publication._worker(link, publication.EPOCHS[-1])


def test_atomic_handoff_preserves_existing_destination(tmp_path):
    source = tmp_path/'source'; source.mkdir()
    destination = tmp_path/'destination'; destination.mkdir()
    (destination/'user-data').write_text('preserve')
    with pytest.raises(OSError):
        publication._rename_noreplace(source, destination)
    assert (destination/'user-data').read_text() == 'preserve'
    assert source.is_dir()


def test_worker_rejects_special_files(tmp_path):
    source = publication.ROOT/publication.OUTPUT/'original/v3'
    target = tmp_path/'worker'; shutil.copytree(source, target)
    target.chmod(0o700)
    os.mkfifo(target/'unexpected-pipe')
    with pytest.raises(ValueError, match='regular files'):
        publication._worker(target, publication.EPOCHS[-1])


def test_source_map_rejects_different_executing_publisher(tmp_path):
    for name in [publication.PRODUCER, publication.CALCULATOR, *publication.calculation.INPUT_SHA256]:
        target = tmp_path/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(publication.ROOT/name, target)
    with (tmp_path/publication.PRODUCER).open('a') as file:
        file.write('\n# Different declared publisher\n')
    with pytest.raises(ValueError, match='Executing publisher'):
        publication._source_map(tmp_path)


def test_verify_detects_changes_after_a_worker_replay(tmp_path, monkeypatch):
    target = tmp_path/'publication'
    shutil.copytree(publication.ROOT/publication.OUTPUT, target)
    worker = publication._worker
    def mutate_after_last(folder, epoch):
        result = worker(folder, epoch)
        if epoch[0] == 'v3':
            path = target/'original/v1/logs/python313-tests.log'
            path.chmod(0o600); path.write_text('changed after replay')
        return result
    monkeypatch.setattr(publication, '_worker', mutate_after_last)
    with pytest.raises(ValueError, match='replay or source epoch'):
        publication.verify(target, expected_manifest_id='53f880cc6cd0a422aa5992b302899b70841b795671c133e4ebe9880e84541ebc')


def test_publish_rechecks_copied_worker_before_handoff(tmp_path, monkeypatch):
    state = tmp_path/'state'; state.mkdir()
    original = publication.ROOT/publication.OUTPUT/'original'
    for name in ('v1', 'v2', 'v3'):
        shutil.copytree(original/name, state/name)
    copy = publication.shutil.copytree
    def mutate_after_check(src, dst, *args, **kwargs):
        result = copy(src, dst, *args, **kwargs)
        if Path(src).name == 'v1':
            target = Path(dst)/'outputs/python313-result.json'
            target.chmod(0o600); target.write_text('{}')
        return result
    monkeypatch.setattr(publication.shutil, 'copytree', mutate_after_check)
    target = tmp_path/'new-publication'
    with pytest.raises(ValueError, match='package differs'):
        publication.publish(state, output=target)
    assert not target.exists()
    assert not list(tmp_path.glob('.mass-support-*'))
