"""Bounded streaming bundles of exact committed research inputs and evidence."""
from hashlib import sha1, sha256
import gzip
import io
import json
import os
from pathlib import Path, PurePosixPath
import tarfile
import tempfile

FLAGS = dict(design_complete=False, physical_validation=False,
             manufacturing_release=False, physical_release=False)
MAX_MEMBER = 64 * 1024 * 1024
MAX_TOTAL = 8 * 1024 * 1024 * 1024
MAX_MEMBERS = 20000
MAX_METADATA = 16 * 1024 * 1024
DEFAULT_SHARD = 256 * 1024 * 1024
MAX_SHARD = 512 * 1024 * 1024
SCHEMA = 'osr-software-study-release/2'


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def safe(name):
    if (not isinstance(name, str) or not name or name == '.' or '\\' in name
            or PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts
            or PurePosixPath(name).as_posix() != name):
        raise ValueError('unsafe bundle member')
    return name


def member_path(root, name):
    path = root / safe(name)
    if root.is_symlink() or any(p.is_symlink() for p in (path, *path.parents) if p != root.parent):
        raise ValueError('symlink in bundle member')
    if not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError('ordinary in-root bundle member required')
    return path


def identity(stream, size):
    git = sha1(b'blob ' + str(size).encode() + b'\0')
    digest = sha256()
    count = 0
    while block := stream.read(1024 * 1024):
        count += len(block)
        if count > size:
            raise ValueError('bundle member grew while reading')
        git.update(block)
        digest.update(block)
    if count != size:
        raise ValueError('bundle member shrank while reading')
    return git.hexdigest(), digest.hexdigest()


def inventory(root, names, tracked):
    """Retain hashes/lengths, never the complete multi-gigabyte payload in RAM."""
    root = Path(root).absolute()
    names = sorted(set(names))
    if not names or len(names) > MAX_MEMBERS:
        raise ValueError('bounded nonempty bundle inventory required')
    members = {}
    total = 0
    for name in names:
        if name == 'PART-MANIFEST.json':
            raise ValueError('reserved bundle metadata name')
        path = member_path(root, name)
        before = path.stat()
        if before.st_size > MAX_MEMBER:
            raise ValueError('oversized member: ' + name)
        total += before.st_size
        if total > MAX_TOTAL:
            raise ValueError('bundle exceeds total raw bound')
        with path.open('rb') as stream:
            git, digest = identity(stream, before.st_size)
        after = path.stat()
        if (before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns):
            raise ValueError('bundle member changed during inventory')
        if tracked.get(name) != git:
            raise ValueError('release member differs from committed source: ' + name)
        members[name] = dict(bytes=before.st_size, sha256=digest, git_blob_sha1=git)
    return members


def partition(members, limit):
    if type(limit) is not int or not 0 < limit <= MAX_SHARD:
        raise ValueError('bounded positive shard size required')
    groups = []
    current = []
    size = 0
    for name, value in sorted(members.items()):
        if value['bytes'] > limit:
            raise ValueError('member exceeds shard payload bound: ' + name)
        if current and size + value['bytes'] > limit:
            groups.append(current)
            current, size = [], 0
        current.append(name)
        size += value['bytes']
    if current:
        groups.append(current)
    return groups


class CheckedReader:
    def __init__(self, stream):
        self.stream = stream
        self.digest = sha256()
        self.count = 0

    def read(self, length=-1):
        data = self.stream.read(length)
        self.digest.update(data)
        self.count += len(data)
        return data


def add_bytes(tar, name, data):
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mode = 0o644
    info.mtime = 0
    tar.addfile(info, io.BytesIO(data))


def part_bytes(names, members, manifest_digest):
    return encoded(dict(schema='osr-study-release-part/1', release_manifest_sha256=manifest_digest,
                        files_sha256={name: members[name]['sha256'] for name in names}, **FLAGS))


def write_archive(path, root, prefix, names, members, manifest_digest):
    part = part_bytes(names, members, manifest_digest)
    if len(part) > MAX_METADATA:
        raise ValueError('oversized part manifest')
    with path.open('wb') as target, gzip.GzipFile(filename='', mode='wb', fileobj=target, mtime=0) as zipped, tarfile.open(fileobj=zipped, mode='w|') as tar:
        add_bytes(tar, prefix + '/PART-MANIFEST.json', part)
        for name in names:
            source = member_path(root, name)
            info = tarfile.TarInfo(prefix + '/' + name)
            info.size = members[name]['bytes']
            info.mode = 0o755 if source.stat().st_mode & 0o111 else 0o644
            info.mtime = 0
            with source.open('rb') as stream:
                checked = CheckedReader(stream)
                tar.addfile(info, checked)
                if (checked.count != info.size or checked.digest.hexdigest() != members[name]['sha256']
                        or stream.read(1)):
                    raise ValueError('member changed during archive: ' + name)


def file_digest(path):
    with Path(path).open('rb') as stream:
        digest = sha256()
        while block := stream.read(1024 * 1024):
            digest.update(block)
        return digest.hexdigest()


def publish(root, output, names, tracked, *, version, commit, source_sha256, shard_limit=DEFAULT_SHARD):
    root, output = Path(root).absolute(), Path(output).absolute()
    if output.is_symlink() or (output.exists() and (not output.is_dir() or any(output.iterdir()))):
        raise ValueError('choose a new empty release output')
    if not isinstance(version, str) or not version or any(c not in '0123456789.-abcdefghijklmnopqrstuvwxyz' for c in version):
        raise ValueError('safe release version required')
    if not isinstance(commit, str) or len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
        raise ValueError('exact Git SHA-1 commit required')
    members = inventory(root, names, tracked)
    if not set(source_sha256) <= set(members) or any(members[name]['sha256'] != value for name, value in source_sha256.items()):
        raise ValueError('source receipt differs from bundle inventory')
    groups = partition(members, shard_limit)
    prefix = 'OpenSourceRail-v' + version
    shards = {prefix + f'-design-studies-part-{i:03d}.tar.gz': names for i, names in enumerate(groups, 1)}
    record = dict(schema=SCHEMA, version=version, commit=commit, archive_prefix=prefix,
                  scope='Source-bound digital studies; no manufacturing or operating release. All referenced inputs are retained across the numbered parts.',
                  source_sha256=source_sha256, files_sha256={n: v['sha256'] for n, v in members.items()},
                  members=members, shards=shards, shard_payload_limit_bytes=shard_limit,
                  uncompressed_payload_bytes=sum(v['bytes'] for v in members.values()),
                  maximum_total_payload_bytes=MAX_TOTAL, accepted_engineering_items=0, **FLAGS)
    manifest = encoded(record)
    if len(manifest) > MAX_METADATA:
        raise ValueError('oversized bundle manifest')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.osr-release-', dir=output.parent) as temporary:
        stage = Path(temporary) / 'bundle'
        stage.mkdir()
        (stage / 'RELEASE-MANIFEST.json').write_bytes(manifest)
        for name, group in shards.items():
            write_archive(stage / name, root, prefix, group, members, sha256(manifest).hexdigest())
        checks = {path.name: file_digest(path) for path in sorted(stage.iterdir())}
        (stage / 'SHA256SUMS').write_text(''.join(value + '  ' + name + '\n' for name, value in checks.items()))
        verify(stage, expected_manifest_sha256=sha256(manifest).hexdigest())
        os.replace(stage, output)
    return dict(version=version, commit=commit, members=len(members), parts=len(shards),
                uncompressed_bytes=record['uncompressed_payload_bytes'],
                archive_bytes=sum((output / name).stat().st_size for name in shards),
                output=str(output), physical_release=False)


class BoundedReader:
    def __init__(self, stream, maximum):
        self.stream, self.maximum, self.count = stream, maximum, 0

    def read(self, length=-1):
        if length < 0:
            length = self.maximum - self.count + 1
        data = self.stream.read(min(length, self.maximum - self.count + 1))
        self.count += len(data)
        if self.count > self.maximum:
            raise ValueError('archive exceeds decompressed bound')
        return data


def verify(output, *, expected_manifest_sha256=None):
    """Inspect all parts without extracting paths or trusting tar links."""
    output = Path(output)
    manifest_path = output / 'RELEASE-MANIFEST.json'
    if manifest_path.is_symlink() or not manifest_path.is_file() or manifest_path.stat().st_size > MAX_METADATA:
        raise ValueError('bounded ordinary bundle manifest required')
    manifest = manifest_path.read_bytes()
    if expected_manifest_sha256 is not None:
        if (not isinstance(expected_manifest_sha256,str) or len(expected_manifest_sha256)!=64
                or any(c not in '0123456789abcdef' for c in expected_manifest_sha256)
                or sha256(manifest).hexdigest()!=expected_manifest_sha256):
            raise ValueError('trusted manifest digest differs')
    record = json.loads(manifest)
    if record['schema'] != SCHEMA or any(record.get(k) is not False for k in FLAGS) or record['accepted_engineering_items'] != 0:
        raise ValueError('unsupported bundle scope/release flags')
    members, shards = record['members'], record['shards']
    if not 0 < len(members) <= MAX_MEMBERS or not 0 < len(shards) <= MAX_MEMBERS:
        raise ValueError('bounded bundle inventory required')
    for name, value in members.items():
        safe(name)
        if name == 'PART-MANIFEST.json' or type(value['bytes']) is not int or not 0 <= value['bytes'] <= MAX_MEMBER:
            raise ValueError('invalid member metadata')
        for key, length in [('sha256',64),('git_blob_sha1',40)]:
            digest = value[key]
            if not isinstance(digest,str) or len(digest)!=length or any(c not in '0123456789abcdef' for c in digest):
                raise ValueError('invalid member digest')
    if record['files_sha256'] != {n: v['sha256'] for n, v in members.items()}:
        raise ValueError('bundle file identities differ')
    if not set(record['source_sha256']) <= set(members) or any(members[n]['sha256'] != v for n, v in record['source_sha256'].items()):
        raise ValueError('bundle source identities differ')
    all_names = [name for names in shards.values() for name in names]
    if len(all_names) != len(set(all_names)) or set(all_names) != set(members):
        raise ValueError('missing or duplicate shard membership')
    total = sum(v['bytes'] for v in members.values())
    if total != record['uncompressed_payload_bytes'] or total > MAX_TOTAL or record['maximum_total_payload_bytes'] != MAX_TOTAL:
        raise ValueError('bundle raw total differs')
    limit = record['shard_payload_limit_bytes']
    if type(limit) is not int or not 0 < limit <= MAX_SHARD:
        raise ValueError('invalid shard bound')
    expected = {'RELEASE-MANIFEST.json', 'SHA256SUMS'} | set(shards)
    if {p.name for p in output.iterdir()} != expected or any(p.is_symlink() or not p.is_file() for p in output.iterdir()):
        raise ValueError('unexpected bundle output')
    prefix = record['archive_prefix']
    if prefix != 'OpenSourceRail-v' + record['version'] or '/' in prefix or '\\' in prefix:
        raise ValueError('unsafe archive prefix')
    raw_bounds = {}
    for archive, names in shards.items():
        safe(archive)
        if '/' in archive or not names or sum(members[n]['bytes'] for n in names) > limit:
            raise ValueError('unsafe or oversized shard')
        metadata = part_bytes(names, members, sha256(manifest).hexdigest())
        if len(metadata) > MAX_METADATA:
            raise ValueError('oversized part manifest')
        raw_bound = sum(members[n]['bytes'] for n in names) + len(metadata) + (len(names) + 1) * 4096 + 10240
        raw_bounds[archive] = raw_bound
        # Check before hashing or opening compressed input. The writer uses
        # ordinary gzip/deflate; 1% plus 64KiB exceeds its worst-case overhead.
        if (output / archive).stat().st_size > raw_bound + raw_bound // 100 + 65536:
            raise ValueError('archive exceeds compressed bound')
    checks = ''.join(file_digest(output / name) + '  ' + name + '\n' for name in sorted(expected - {'SHA256SUMS'}))
    if (output / 'SHA256SUMS').stat().st_size > MAX_METADATA or (output / 'SHA256SUMS').read_text() != checks:
        raise ValueError('bundle checksum differs')
    for archive, names in shards.items():
        expected_part = part_bytes(names, members, sha256(manifest).hexdigest())
        seen = set()
        with gzip.open(output / archive, 'rb') as zipped:
            bounded = BoundedReader(zipped, raw_bounds[archive])
            with tarfile.open(fileobj=bounded, mode='r|') as tar:
                for member in tar:
                    if not member.isfile() or not member.name.startswith(prefix + '/'):
                        raise ValueError('unsafe tar member')
                    name = safe(member.name[len(prefix) + 1:])
                    if name in seen:
                        raise ValueError('duplicate tar member')
                    seen.add(name)
                    stream = tar.extractfile(member)
                    if name == 'PART-MANIFEST.json':
                        if member.size != len(expected_part) or stream.read() != expected_part:
                            raise ValueError('part identity differs')
                    else:
                        if name not in names or type(member.size) is not int or not 0 <= member.size <= MAX_MEMBER or member.size != members[name]['bytes']:
                            raise ValueError('unexpected tar payload')
                        git, digest = identity(stream, member.size)
                        if digest != members[name]['sha256'] or git != members[name]['git_blob_sha1']:
                            raise ValueError('tar payload identity differs')
                # Inspect the tar stream's own prefetched buffer as well as
                # the underlying decompressor. Reading only `bounded` here
                # would miss a second archive already buffered after EOF.
                while tail := tar.fileobj.read(4096):
                    if any(tail):
                        raise ValueError('nonpadding bytes after tar terminator')
        if seen != set(names) | {'PART-MANIFEST.json'}:
            raise ValueError('incomplete tar inventory')
    return dict(parts=len(shards), members=len(members), source_bound=True,
                trusted_manifest_matched=expected_manifest_sha256 is not None,
                scope='Internal part/source digest consistency; authenticate the manifest digest or compare the exact commit in a trusted Git checkout separately',
                physical_release=False)
