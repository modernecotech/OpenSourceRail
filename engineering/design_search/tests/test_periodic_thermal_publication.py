import os
import json
from pathlib import Path
import shutil

import pytest

from engineering.design_search import periodic_thermal_publication as publication

PINS=dict(expected_handoff_id='701824bd9fec83c2ae48725040804d3f7d42f94c3e742b638ac6e23437d6ef3d',
    expected_request_id='019fb919aaaef52d9e0af4ceda21648544bd35c1c15d9d31dc832f2bdcff6967',
    expected_evaluation_id='de6c95144aedca6ffde689fb4eb62dcef57adde633da9a46b013420d95dff48c')
MANIFEST='e2ac8e01ac36eaa19d8f5c59c0dcfc28de6acd7759065a0a7b122cd8d7c3d66d'


def test_externally_pinned_publication_replays():
    result=publication.verify(expected_manifest_id=MANIFEST,**PINS)
    assert result['evaluation_id']==PINS['expected_evaluation_id']
    assert result['physical_accepted'] is False
    with pytest.raises(ValueError,match='identity'):
        publication.verify(expected_manifest_id='0'*64,**PINS)


def test_worker_rejects_undeclared_root_manifest_and_special_file(tmp_path):
    target=tmp_path/'worker';shutil.copytree(publication.ROOT/publication.OUTPUT/'original',target)
    target.chmod(0o700);(target/'manifest.json').write_text('{}')
    with pytest.raises(ValueError,match='Unexpected root manifest'):
        publication._worker(target,**PINS)
    (target/'manifest.json').unlink();os.mkfifo(target/'unexpected-pipe')
    with pytest.raises(ValueError,match='regular files'):
        publication._worker(target,**PINS)
    (target/'unexpected-pipe').unlink();(target/'unexpected-empty-dir').mkdir()
    with pytest.raises(ValueError,match='empty directories'):
        publication._worker(target,**PINS)


def test_source_map_rejects_traversal_before_opening_inputs(tmp_path):
    path=tmp_path/publication.study.MANIFEST;path.parent.mkdir(parents=True)
    path.write_text(json.dumps({'source_sha256':{'../outside':'a'*64}}))
    with pytest.raises(ValueError,match='relative source path'):
        publication._sources(tmp_path)


def test_reader_reports_actual_headway_and_held_branch_dispositions():
    path=publication.ROOT/publication.OUTPUT/'original/short-headway-result-v10.json'
    text=publication._readme(json.loads(path.read_bytes()))
    assert '1 s departure period' in text
    assert 'Held: held-model-domain-exceeded' in text
    assert 'Held: no-steady-state-positive-heat' in text
    assert 'Held: controller-speed-limit' in text


def test_verify_rechecks_original_worker_after_replay(tmp_path,monkeypatch):
    target=tmp_path/'packet';shutil.copytree(publication.ROOT/publication.OUTPUT,target)
    evaluate=publication.study.evaluate
    def tamper_after_replay(*args,**kwargs):
        result=evaluate(*args,**kwargs)
        path=target/'original/run-v3-py312.log';path.chmod(0o600);path.write_text('modified')
        return result
    monkeypatch.setattr(publication.study,'evaluate',tamper_after_replay)
    with pytest.raises(ValueError,match='replay or source epoch'):
        publication.verify(target,expected_manifest_id=MANIFEST,**PINS)


def test_publish_rechecks_copied_worker_before_handoff(tmp_path,monkeypatch):
    source=publication.ROOT/publication.OUTPUT/'original';copy=publication.shutil.copytree
    def mutate_after_copy(src,dst,*args,**kwargs):
        result=copy(src,dst,*args,**kwargs)
        if Path(dst).name=='original':
            path=Path(dst)/'run-v3-py312.log';path.chmod(0o600);path.write_text('modified')
        return result
    monkeypatch.setattr(publication.shutil,'copytree',mutate_after_copy)
    target=tmp_path/'publication'
    with pytest.raises(ValueError,match='inventory'):
        publication.publish(source,output=target,**PINS)
    assert not target.exists()
    assert not list(tmp_path.glob('.thermal-study-*'))
