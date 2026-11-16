"""Bounded-memory, deterministic native evidence archives."""
from __future__ import annotations

from hashlib import sha256
import io
import os
from pathlib import Path
import stat
import struct
import tarfile
import tempfile
import zlib

from engineering.station_rail.common import encoded, digest


class _GzipSink:
    """Write the mtime-zero gzip format used by the active Python toolchain."""

    def __init__(self, output):
        self.output = output
        self.compressor = zlib.compressobj(level=9, wbits=-15)
        self.crc = 0
        self.size = 0
        self._write_all(b'\x1f\x8b\x08\x00' + b'\x00' * 4 + b'\x02\xff')

    def _write_all(self, data):
        remaining = memoryview(data)
        while remaining:
            count = self.output.write(remaining)
            if type(count) is not int or not 0 < count <= len(remaining):
                raise OSError('Native archive write made no progress')
            remaining = remaining[count:]

    def write(self, data):
        self.crc = zlib.crc32(data, self.crc)
        self.size = (self.size + len(data)) & 0xffffffff
        self._write_all(self.compressor.compress(data))
        return len(data)

    def finish(self):
        self._write_all(self.compressor.flush())
        self._write_all(struct.pack('<II', self.crc, self.size))


class _HashingReader:
    def __init__(self, stream):
        self.stream = stream
        self.digest = sha256()
        self.size = 0

    def read(self, count):
        data = self.stream.read(count)
        self.digest.update(data)
        self.size += len(data)
        return data


def _add_file(tar, path, name):
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(descriptor, 'rb') as source:
        before = os.fstat(source.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise ValueError('Ordinary native evidence files required')
        member = tarfile.TarInfo(name)
        member.size = before.st_size
        member.mtime = 0
        member.mode = 0o644
        reader = _HashingReader(source)
        tar.addfile(member, reader)
        after = os.fstat(source.fileno())
        current = os.stat(path, follow_symlinks=False)
        fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
        if (reader.size != before.st_size
                or any(getattr(before, field) != getattr(after, field)
                       or getattr(after, field) != getattr(current, field)
                       for field in fields)):
            raise ValueError('Native evidence changed while archiving: ' + name)
        return reader.digest.hexdigest()


def write_archive(folder, target, *, omit, storage):
    """Atomically write a native archive without holding members or tar in RAM.

    Incomplete `.pending` output remains visible after a failed write; an
    existing completed target is never replaced until the stream is sealed.
    """
    folder = Path(folder)
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, pending_name = tempfile.mkstemp(
        prefix='.' + target.name + '.', suffix='.pending', dir=target.parent)
    pending = Path(pending_name)
    kept = {}
    omitted = {}
    with os.fdopen(descriptor, 'wb', buffering=0) as output:
        sink = _GzipSink(output)
        with tarfile.open(fileobj=sink, mode='w|') as tar:
            for path in sorted(folder.rglob('*')):
                if path.is_symlink():
                    raise ValueError('Ordinary native evidence files required')
                if not path.is_file() or '__pycache__' in path.parts:
                    continue
                name = path.relative_to(folder).as_posix()
                if omit(path):
                    omitted[name] = digest(path)
                    continue
                kept[name] = _add_file(tar, path, name)
            index = encoded(dict(retained_sha256=kept,
                                 omitted_sha256=omitted, storage=storage))
            member = tarfile.TarInfo('archive-index.json')
            member.size = len(index)
            member.mtime = 0
            member.mode = 0o644
            tar.addfile(member, io.BytesIO(index))
        sink.finish()
        output.flush()
        os.fsync(output.fileno())
    os.replace(pending, target)
