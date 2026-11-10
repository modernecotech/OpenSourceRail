import json

import pytest

from engineering.railway_closure.coordinator import _prune_unreferenced_native_reuse
from engineering.station_rail.common import identity


def sealed(value, key='receipt_id'):
    value[key] = identity(value)
    return value


def test_native_reuse_keeps_only_receipts_used_by_the_new_study(tmp_path):
    output = tmp_path / 'run'
    serial = output / 'serial'
    runs = serial / 'native-runs'
    runs.mkdir(parents=True)
    build = sealed({'schema': 'osr-cycle-build-test/1'})
    (serial / 'cycle-build.json').write_text(json.dumps(build))

    source = tmp_path / 'old-publication'
    copied_stale = runs / 'old-build'
    copied_stale.mkdir()
    stale = sealed({'schema': 'osr-native-test/1', 'build_receipt_id': 'old-build'})
    (copied_stale / 'receipt.json').write_text(json.dumps(stale))
    (copied_stale / 'output.json.gz').write_bytes(b'old cached output')
    original_stale = source / 'native-runs' / 'old-build'
    original_stale.mkdir(parents=True)
    (original_stale / 'receipt.json').write_text(json.dumps(stale))

    copied_incomplete = runs / 'interrupted-build'
    copied_incomplete.mkdir()
    (copied_incomplete / 'execution.json').write_text('{"exit_code":null}')

    copied_used = runs / 'used-build'
    copied_used.mkdir()
    used = sealed({'schema': 'osr-native-test/1', 'build_receipt_id': build['receipt_id']})
    (copied_used / 'receipt.json').write_text(json.dumps(used))

    new_uncopied = runs / 'new-build'
    new_uncopied.mkdir()
    (new_uncopied / 'receipt.json').write_text('{}')

    discarded = _prune_unreferenced_native_reuse(
        output,
        {'serial': {copied_stale, copied_incomplete, copied_used}, 'fleet': set()},
        {'serial': {used['receipt_id']}, 'fleet': set()},
    )

    assert discarded['batches'] == 2
    assert discarded['allocated_bytes'] >= len(b'old cached output')
    assert not copied_stale.exists()
    assert not copied_incomplete.exists()
    assert copied_used.is_dir()
    assert new_uncopied.is_dir()
    assert (original_stale / 'receipt.json').read_text() == json.dumps(stale)


def test_native_reuse_fails_closed_if_a_referenced_receipt_uses_another_build(tmp_path):
    output = tmp_path / 'run'
    serial = output / 'serial'
    runs = serial / 'native-runs'
    runs.mkdir(parents=True)
    build = sealed({'schema': 'osr-cycle-build-test/1'})
    (serial / 'cycle-build.json').write_text(json.dumps(build))
    copied = runs / 'mismatch'
    copied.mkdir()
    receipt = sealed({'schema': 'osr-native-test/1', 'build_receipt_id': 'other-build'})
    (copied / 'receipt.json').write_text(json.dumps(receipt))

    with pytest.raises(ValueError, match='different build'):
        _prune_unreferenced_native_reuse(
            output, {'serial': {copied}, 'fleet': set()},
            {'serial': {receipt['receipt_id']}, 'fleet': set()},
        )
