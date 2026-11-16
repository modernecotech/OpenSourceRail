"""Active native archives keep exact members while bounding write memory."""
import gzip
import io
import json
from pathlib import Path
import sys
import tarfile

import pytest

from engineering.design_search import generative_publication, railway_publication
from engineering.station_rail.common import digest, encoded


def _legacy_archive(folder, *, compact):
    """The former writer, kept only as a test oracle for packet bytes."""
    kept = {}
    omitted = {}
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode='w') as tar:
        for path in sorted(folder.rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts:
                continue
            name = path.relative_to(folder).as_posix()
            checksum = digest(path)
            excluded = path.suffix.lower() in ('.dat', '.frd', '.12d', '.step', '.fcstd', '.fcstd1')
            if compact:
                excluded = excluded or (path.name in ('candidate.json', 'definition.json', 'worker-result.json')
                                        and path.stat().st_size > 1_000_000)
            if excluded:
                omitted[name] = checksum
                continue
            raw = path.read_bytes()
            kept[name] = checksum
            member = tarfile.TarInfo(name)
            member.size = len(raw)
            member.mtime = 0
            member.mode = 0o644
            tar.addfile(member, io.BytesIO(raw))
        storage = ('Exact FEM decks/results/logs retained; large fields and duplicate node/body metadata remain local or regenerate from exact source/body/request. Full raw-payload hashes preserved.'
                   if compact else
                   'Large fields and native CAD remain in local immutable runs, or reproduce with exact sources and indexed inputs; no remote artifact storage is claimed')
        index = encoded(dict(retained_sha256=kept, omitted_sha256=omitted, storage=storage))
        member = tarfile.TarInfo('archive-index.json')
        member.size = len(index)
        member.mtime = 0
        member.mode = 0o644
        tar.addfile(member, io.BytesIO(index))
    return gzip.compress(output.getvalue(), mtime=0)


@pytest.mark.parametrize('compact', [False, True])
def test_archive_stream_matches_original_members_and_active_bytes(tmp_path, compact):
    source = tmp_path/'source'
    source.mkdir()
    (source/'manifest.json').write_bytes(b'{"case":"held"}\n')
    (source/'solver.log').write_bytes(b'iteration 1\n' * 5000)
    (source/'field.frd').write_bytes(b'omitted field\n' * 2000)
    (source/'candidate.json').write_bytes(b'x' * 1_000_001)
    (source/'nested').mkdir()
    (source/'nested'/'result.json').write_bytes(b'{"validity":null}\n')
    target = tmp_path/'archive.tar.gz'
    writer = railway_publication.compact_native_archive if compact else generative_publication.archive
    writer(source, target)
    actual = target.read_bytes()
    previous = _legacy_archive(source, compact=compact)
    assert gzip.decompress(actual) == gzip.decompress(previous)
    # gzip.compress acquired a stable OS=255 header in Python 3.13.
    if sys.version_info >= (3, 13):
        assert actual == previous
    with tarfile.open(target, mode='r:gz') as tar:
        names = tar.getnames()
        assert names[-1] == 'archive-index.json'
        index = json.load(tar.extractfile('archive-index.json'))
        assert set(index['retained_sha256']) == set(names)-{'archive-index.json'}
        assert index['omitted_sha256']['field.frd'] == digest(source/'field.frd')
        assert ('candidate.json' in index['omitted_sha256']) is compact


@pytest.mark.parametrize('compact', [False, True])
def test_archive_rejects_symlink_and_keeps_previous_target(tmp_path, compact):
    source = tmp_path/'source'
    source.mkdir()
    outside = tmp_path/'outside'
    outside.write_bytes(b'do not follow')
    (source/'link').symlink_to(outside)
    target = tmp_path/'archive.tar.gz'
    target.write_bytes(b'previous sealed archive')
    writer = railway_publication.compact_native_archive if compact else generative_publication.archive
    with pytest.raises(ValueError, match='Ordinary native evidence files required'):
        writer(source, target)
    assert target.read_bytes() == b'previous sealed archive'
    assert list(tmp_path.glob('.archive.tar.gz.*.pending'))
