"""Cached lexical inventories must recheck live paths and content on every request."""
from collections import Counter
from hashlib import sha256
import json
import os
from pathlib import Path

import pytest

from engineering.development_baseline import entrypoint as cli, FLAGS, OUTPUT


def encoded(value):
    return (json.dumps(value, sort_keys=True) + '\n').encode()


@pytest.fixture
def packet(tmp_path, monkeypatch):
    ids = dict(selection_id='e'*64, candidate_id='a'*64, body_candidate_id='b'*64,
               support_component_id='c'*64, propulsion_component_id='d'*64)
    baseline = dict(selection_id=ids['selection_id'], vehicle=ids)
    monkeypatch.setattr(cli, 'selected', lambda root: baseline)
    directory = tmp_path / OUTPUT
    directory.mkdir(parents=True)
    summary = dict(**ids, development_default=True, **FLAGS)
    (directory / 'summary.json').write_bytes(encoded(summary))
    source = tmp_path / 'inputs' / 'nested' / 'source.txt'
    source.parent.mkdir(parents=True)
    source.write_bytes(b'original')
    sibling = source.with_name('sibling.txt')
    sibling.write_bytes(b'sibling')
    manifest = dict(**summary, files_sha256={
        'summary.json': sha256((directory / 'summary.json').read_bytes()).hexdigest()},
        source_sha256={p.relative_to(tmp_path).as_posix(): sha256(p.read_bytes()).hexdigest()
                       for p in (source, sibling)})
    manifest_path = directory / 'manifest.json'
    manifest_path.write_bytes(encoded(manifest))
    cli._packet_paths.cache_clear()
    cli._digest.cache_clear()
    assert cli.read_packet(tmp_path) == (summary, manifest)
    return tmp_path, source, summary, manifest, manifest_path


def test_unchanged_packet_reuses_inventory_but_checks_each_unique_path(packet, monkeypatch):
    root, _, summary, manifest, manifest_path = packet
    inventory = cli._packet_paths(str(root), OUTPUT, manifest_path.read_bytes())
    calls = Counter()
    original = os.lstat

    def observed(path, *args, **kwargs):
        calls[str(path)] += 1
        return original(path, *args, **kwargs)

    monkeypatch.setattr(os, 'lstat', observed)
    cli._packet_stamps(inventory)
    assert set(calls) == set(inventory[0]) | set(inventory[1])
    assert all(count == 1 for count in calls.values())
    assert cli.read_packet(root) == (summary, manifest)
    assert cli._packet_paths.cache_info().hits >= 2


def test_changed_mtime_invalidates_content_digest(packet):
    root, source, *_ = packet
    before = source.stat()
    source.write_bytes(b'modified')
    os.utime(source, ns=(before.st_atime_ns, before.st_mtime_ns + 1_000_000_000))
    assert source.stat().st_mtime_ns != before.st_mtime_ns
    with pytest.raises(cli.CurrentUnavailable, match='Current source changed'):
        cli.read_packet(root)


def test_changed_ctime_rejects_same_size_content_with_restored_mtime(packet):
    root, source, *_ = packet
    before = source.stat()
    source.write_bytes(b'modified')
    os.utime(source, ns=(before.st_atime_ns, before.st_mtime_ns))
    after = source.stat()
    assert (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) == (
        before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    assert after.st_ctime_ns != before.st_ctime_ns
    with pytest.raises(cli.CurrentUnavailable, match='Current source changed'):
        cli.read_packet(root)


@pytest.mark.parametrize('target', ['ancestor', 'leaf'])
def test_cached_inventory_rejects_new_symlink_even_to_identical_bytes(packet, target):
    root, source, *_ = packet
    original = source.parent if target == 'ancestor' else source
    moved = original.with_name(original.name + '-original')
    original.rename(moved)
    original.symlink_to(moved, target_is_directory=target == 'ancestor')
    with pytest.raises(cli.CurrentUnavailable, match='Symlinks are not evidence paths'):
        cli.read_packet(root)


def test_exact_manifest_change_requires_new_inventory_and_checks_new_source(packet):
    root, source, _, manifest, manifest_path = packet
    addition = source.with_name('new.txt')
    addition.write_bytes(b'new input')
    manifest['source_sha256'][addition.relative_to(root).as_posix()] = sha256(addition.read_bytes()).hexdigest()
    manifest_path.write_bytes(encoded(manifest))
    assert cli.read_packet(root)[1] == manifest
    assert cli._packet_paths.cache_info().misses == 2
    addition.write_bytes(b'bad input')
    with pytest.raises(cli.CurrentUnavailable, match='Current source changed'):
        cli.read_packet(root)


@pytest.mark.parametrize('relative', ['../outside.txt', '/tmp/outside.txt', 'inputs/../../outside.txt'])
def test_cached_inventory_rejects_traversal_and_absolute_paths(packet, relative):
    root, _, _, manifest, manifest_path = packet
    manifest['source_sha256'][relative] = '0'*64
    manifest_path.write_bytes(encoded(manifest))
    with pytest.raises(cli.CurrentUnavailable, match='ordinary repository-relative'):
        cli.read_packet(root)


def test_cached_packet_cannot_reuse_other_candidate_identity(packet):
    root, _, _, manifest, manifest_path = packet
    manifest['candidate_id'] = 'f'*64
    manifest_path.write_bytes(encoded(manifest))
    with pytest.raises(cli.CurrentUnavailable, match='different candidate_id'):
        cli.read_packet(root)


def test_inventory_is_bounded_before_filesystem_checks(packet):
    root, _, _, manifest, _ = packet
    manifest['source_sha256'] = {str(i): '0'*64 for i in range(32769)}
    with pytest.raises(cli.CurrentUnavailable, match='bounded path inventory'):
        cli._packet_paths(str(root), OUTPUT, encoded(manifest))


def test_cached_leaf_must_remain_an_ordinary_file(packet):
    root, source, *_ = packet
    source.unlink()
    source.mkdir()
    with pytest.raises(cli.CurrentUnavailable, match='ordinary evidence file'):
        cli.read_packet(root)
