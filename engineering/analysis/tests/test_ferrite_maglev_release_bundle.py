"""Multipart evidence survives round trips and rejects tampering/path tricks."""
from hashlib import sha1, sha256
import gzip
import io
import json
import os
from pathlib import Path
import tarfile

import pytest

from engineering.ferrite_maglev import release_bundle as bundle


def inputs(root):
    values = {'a.txt': b'abc' * 20, 'nested/b.rs': b'fn main() {}\n' * 4,
              'zero.txt': b'', 'nested/long-' + 'x' * 110 + '.json': b'{}\n'}
    tracked = {}
    for name, data in values.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        tracked[name] = sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    return values, tracked


def publish(root, output, values, tracked, **kwargs):
    return bundle.publish(root, output, values, tracked, version='0.5.2', commit='1' * 40,
                          source_sha256={n: sha256(d).hexdigest() for n, d in values.items()},
                          shard_limit=64, **kwargs)


def reseal(output):
    names = sorted(p.name for p in output.iterdir() if p.name != 'SHA256SUMS')
    (output / 'SHA256SUMS').write_text(''.join(bundle.file_digest(output/n) + '  ' + n + '\n' for n in names))


def test_roundtrip_is_deterministic_and_all_sources_present(tmp_path):
    root = tmp_path / 'repo'
    root.mkdir()
    values, tracked = inputs(root)
    first, second = tmp_path/'first', tmp_path/'second'
    result = publish(root, first, values, tracked)
    assert result['parts'] == 2
    assert bundle.verify(first)['source_bound']
    publish(root, second, values, tracked)
    assert {p.name: p.read_bytes() for p in first.iterdir()} == {p.name: p.read_bytes() for p in second.iterdir()}
    manifest = json.loads((first/'RELEASE-MANIFEST.json').read_text())
    assert set(manifest['files_sha256']) == set(values)
    assert all(manifest[k] is False for k in bundle.FLAGS)


def test_offline_verification_distinguishes_trusted_manifest_from_internal_consistency(tmp_path):
    root = tmp_path/'repo'
    root.mkdir()
    values, tracked = inputs(root)
    output = tmp_path/'out'
    publish(root, output, values, tracked)
    digest = bundle.file_digest(output/'RELEASE-MANIFEST.json')
    assert bundle.verify(output)['trusted_manifest_matched'] is False
    assert bundle.verify(output, expected_manifest_sha256=digest)['trusted_manifest_matched'] is True
    with pytest.raises(ValueError, match='trusted manifest'):
        bundle.verify(output, expected_manifest_sha256='0'*64)


@pytest.mark.parametrize('name', ['../outside', '/absolute', 'a/../b', 'a//b', './a', '.', 'a\\b'])
def test_unsafe_names_are_rejected_before_reading(tmp_path, name):
    with pytest.raises(ValueError, match='unsafe'):
        bundle.inventory(tmp_path, [name], {})


def test_committed_source_change_and_source_receipt_mismatch_rejected(tmp_path):
    values, tracked = inputs(tmp_path)
    (tmp_path/'a.txt').write_bytes(b'changed')
    with pytest.raises(ValueError, match='committed'):
        publish(tmp_path, tmp_path/'out', values, tracked)
    (tmp_path/'a.txt').write_bytes(values['a.txt'])
    bad = dict(values)
    bad['a.txt'] = b'wrong receipt'
    with pytest.raises(ValueError, match='source receipt'):
        publish(tmp_path, tmp_path/'out', bad, tracked)
    assert not (tmp_path/'out').exists()


def test_symlink_and_total_payload_bounds(tmp_path, monkeypatch):
    root = tmp_path/'repo'
    root.mkdir()
    values, tracked = inputs(root)
    (root/'alias').symlink_to(root/'a.txt')
    with pytest.raises(ValueError, match='symlink'):
        bundle.inventory(root, ['alias'], {})
    monkeypatch.setattr(bundle, 'MAX_TOTAL', 70)
    with pytest.raises(ValueError, match='total raw'):
        publish(root, tmp_path/'out', values, tracked)


def test_changed_source_during_archive_does_not_publish(tmp_path, monkeypatch):
    root = tmp_path/'repo'
    root.mkdir()
    values, tracked = inputs(root)
    original = bundle.write_archive

    def changed(*args):
        (root/'a.txt').write_bytes(b'Z' * len(values['a.txt']))
        return original(*args)

    monkeypatch.setattr(bundle, 'write_archive', changed)
    with pytest.raises(ValueError, match='changed during archive'):
        publish(root, tmp_path/'out', values, tracked)
    assert not (tmp_path/'out').exists()
    assert not list(tmp_path.glob('.osr-release-*'))


def test_corrupt_archive_rejected_even_with_updated_outer_checksum(tmp_path):
    root = tmp_path/'repo'
    root.mkdir()
    values, tracked = inputs(root)
    output = tmp_path/'out'
    publish(root, output, values, tracked)
    archive = sorted(output.glob('*.tar.gz'))[0]
    with tarfile.open(archive, 'r:gz') as source:
        retained = [(member, source.extractfile(member).read()) for member in source]
    with archive.open('wb') as target, gzip.GzipFile(fileobj=target, mode='wb', mtime=0) as zipped, tarfile.open(fileobj=zipped, mode='w|') as tar:
        for member, data in retained:
            if member.name.endswith('/a.txt'):
                data = b'Z' * len(data)
            tar.addfile(member, io.BytesIO(data))
    reseal(output)
    with pytest.raises(ValueError, match='payload identity'):
        bundle.verify(output)


def test_link_or_extra_tar_member_rejected(tmp_path):
    root = tmp_path/'repo'
    root.mkdir()
    values, tracked = inputs(root)
    output = tmp_path/'out'
    publish(root, output, values, tracked)
    archive = sorted(output.glob('*.tar.gz'))[0]
    with archive.open('wb') as target, gzip.GzipFile(fileobj=target, mode='wb', mtime=0) as zipped, tarfile.open(fileobj=zipped, mode='w|') as tar:
        info = tarfile.TarInfo('OpenSourceRail-v0.5.2/evil')
        info.type = tarfile.SYMTYPE
        info.linkname = '/etc/passwd'
        tar.addfile(info)
    reseal(output)
    with pytest.raises(ValueError, match='unsafe tar'):
        bundle.verify(output)


def test_nonempty_output_and_unexpected_files_are_not_overwritten(tmp_path):
    root = tmp_path/'repo'
    root.mkdir()
    values, tracked = inputs(root)
    output = tmp_path/'out'
    publish(root, output, values, tracked)
    before = (output/'RELEASE-MANIFEST.json').read_bytes()
    with pytest.raises(ValueError, match='new empty'):
        publish(root, output, values, tracked)
    assert (output/'RELEASE-MANIFEST.json').read_bytes() == before
    (output/'extra').write_text('unknown')
    with pytest.raises(ValueError, match='unexpected bundle'):
        bundle.verify(output)


def test_compressed_trailing_bomb_is_bounded(tmp_path):
    root = tmp_path/'repo'
    root.mkdir()
    values, tracked = inputs(root)
    output = tmp_path/'out'
    publish(root, output, values, tracked)
    archive = sorted(output.glob('*.tar.gz'))[0]
    with gzip.open(archive, 'rb') as stream:
        raw = stream.read()
    archive.write_bytes(gzip.compress(raw + b'\0' * (bundle.MAX_METADATA + 1024*1024), mtime=0))
    reseal(output)
    with pytest.raises(ValueError, match='decompressed bound'):
        bundle.verify(output)


def test_oversized_compressed_archive_rejected_before_hashing(tmp_path, monkeypatch):
    root = tmp_path/'repo'
    root.mkdir()
    values, tracked = inputs(root)
    output = tmp_path/'out'
    publish(root, output, values, tracked)
    archive = sorted(output.glob('*.tar.gz'))[0]
    with archive.open('r+b') as stream:
        stream.truncate(1024*1024)
    def forbidden_hash(path):
        raise AssertionError('no checksum I/O before compressed-byte bounds')
    monkeypatch.setattr(bundle, 'file_digest', forbidden_hash)
    with pytest.raises(ValueError, match='compressed bound'):
        bundle.verify(output)


def test_appended_second_tar_is_not_silently_ignored(tmp_path):
    root = tmp_path/'repo'
    root.mkdir()
    values, tracked = inputs(root)
    output = tmp_path/'out'
    publish(root, output, values, tracked)
    archive = sorted(output.glob('*.tar.gz'))[0]
    with gzip.open(archive, 'rb') as stream:
        raw = stream.read()
    extra = io.BytesIO()
    with tarfile.open(fileobj=extra, mode='w') as tar:
        info = tarfile.TarInfo('OpenSourceRail-v0.5.2/UNMANIFESTED')
        info.size = 1
        tar.addfile(info, io.BytesIO(b'X'))
    # Header, one padded data block and two EOF blocks make a complete small
    # TAR; omit tarfile's optional padding to a 10KiB record boundary.
    archive.write_bytes(gzip.compress(raw + extra.getvalue()[:2048], mtime=0))
    reseal(output)
    with pytest.raises(ValueError, match='nonpadding'):
        bundle.verify(output)


def test_fifo_manifest_rejected_without_opening(tmp_path):
    os.mkfifo(tmp_path/'RELEASE-MANIFEST.json')
    with pytest.raises(ValueError, match='ordinary bundle manifest'):
        bundle.verify(tmp_path)
