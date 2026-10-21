"""Retained actual Rust evidence must remain complete after receipt recomputation."""
import gzip
import json
from pathlib import Path
import shutil
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from engineering.ferrite_maglev import station_protocol as protocol


@pytest.fixture(scope='module')
def executed(tmp_path_factory):
    output=tmp_path_factory.mktemp('station-protocol')/'packet'
    protocol.publish(output)
    return output


def copied(executed,tmp_path):
    output=tmp_path/'packet';shutil.copytree(executed,output);return output


def reseal(output,*,replay=None,transcript=None):
    manifest=json.loads((output/'manifest.json').read_text())
    if replay is None:replay=json.loads((output/'replay.json').read_text())
    if transcript is None:transcript=json.loads(gzip.decompress((output/'executed-tests.txt.gz').read_bytes()))
    execution=protocol._execution(transcript)
    epoch=protocol.digest(protocol.encoded([manifest['source_sha256'],execution,manifest['binary_sha256']]))
    manifest.update(execution=execution,source_epoch=epoch)
    replay.update(execution=execution,source_epoch=epoch)
    (output/'replay.json').write_bytes(protocol.encoded(replay))
    (output/'executed-tests.txt.gz').write_bytes(gzip.compress(protocol.encoded(transcript),mtime=0))
    manifest['files_sha256']={name:protocol.digest((output/name).read_bytes()) for name in protocol.FILES}
    (output/'manifest.json').write_bytes(protocol.encoded(manifest))


def test_actual_rust_evidence_has_all_controls_tests_and_no_release(executed):
    manifest=protocol.verify(executed)
    replay=json.loads((executed/'replay.json').read_text())
    transcript=json.loads(gzip.decompress((executed/'executed-tests.txt.gz').read_bytes()))
    assert set(replay['controller_replay']['checks'])==protocol.CHECKS
    assert len(replay['required_executed_tests'])==13
    assert transcript['run']['returncode']==0
    assert manifest['release_authority'] is False
    assert 'crates/osr-interlocking/src/station.rs' in manifest['source_sha256']
    assert 'crates/osr-maglev-control/examples/station_replay.rs' in manifest['source_sha256']


def test_rehashed_omitted_control_is_not_accepted(executed,tmp_path):
    output=copied(executed,tmp_path)
    replay=json.loads((output/'replay.json').read_text())
    del replay['controller_replay']['checks']['replay_rejected']
    transcript=json.loads(gzip.decompress((output/'executed-tests.txt.gz').read_bytes()))
    transcript['run']['stdout']=protocol.encoded(replay['controller_replay']).decode()
    reseal(output,replay=replay,transcript=transcript)
    with pytest.raises(ValueError,match='mandatory offline controls'):protocol.verify(output)


def test_rehashed_omitted_named_test_cannot_be_replaced_by_a_pass_summary(executed,tmp_path):
    output=copied(executed,tmp_path)
    transcript=json.loads(gzip.decompress((output/'executed-tests.txt.gz').read_bytes()))
    name=sorted(protocol.REQUIRED_TESTS)[0]
    transcript['tests']['stdout']=transcript['tests']['stdout'].replace('test '+name+' ... ok\n','')
    reseal(output,transcript=transcript)
    with pytest.raises(ValueError,match='mandatory named executed tests'):protocol.verify(output)


def test_failed_or_unrelated_command_is_not_passing_evidence(executed,tmp_path):
    output=copied(executed,tmp_path)
    transcript=json.loads(gzip.decompress((output/'executed-tests.txt.gz').read_bytes()))
    transcript['tests']['command']=['echo','passed']
    reseal(output,transcript=transcript)
    with pytest.raises(ValueError,match='command differs'):protocol.verify(output)


def test_permission_to_actuate_cannot_be_added_to_rehashed_studies(executed,tmp_path):
    output=copied(executed,tmp_path)
    replay=json.loads((output/'replay.json').read_text());replay['physical_release']=True
    reseal(output,replay=replay)
    with pytest.raises(ValueError,match='no release authority'):protocol.verify(output)


def test_source_epoch_and_inventory_are_exact(executed,tmp_path):
    output=copied(executed,tmp_path)
    manifest=json.loads((output/'manifest.json').read_text());manifest['source_sha256'].pop('Cargo.lock')
    (output/'manifest.json').write_bytes(protocol.encoded(manifest))
    with pytest.raises(ValueError,match='source identity'):protocol.verify(output)
    shutil.rmtree(output);output=copied(executed,tmp_path)
    (output/'extra.json').write_text('{}')
    with pytest.raises(ValueError,match='inventory'):protocol.verify(output)


def test_tool_failure_holds_before_creating_a_publication(monkeypatch,tmp_path):
    def fail(command):raise RuntimeError('compiler unavailable')
    monkeypatch.setattr(protocol,'_run',fail)
    output=tmp_path/'held'
    with pytest.raises(RuntimeError,match='compiler unavailable'):protocol.publish(output)
    assert not output.exists()


def test_missing_manifest_receipt_is_not_a_partial_success(executed,tmp_path):
    output=copied(executed,tmp_path)
    manifest=json.loads((output/'manifest.json').read_text());manifest['files_sha256'].pop('executed-tests.txt.gz')
    (output/'manifest.json').write_bytes(protocol.encoded(manifest))
    with pytest.raises(ValueError,match='complete station protocol payload'):protocol.verify(output)
