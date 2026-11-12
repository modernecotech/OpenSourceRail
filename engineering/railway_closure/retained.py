"""Authenticate a retained dossier and run its unchanged, single-epoch checker.

This is historical method replay, never current-design acceptance. No network,
compilation or native calculation is performed. The child has process/resource
limits and a cooperative subprocess guard; it is not an OS sandbox.
"""
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

MAX_SOURCE_BYTES = 512 * 1024**2
MIN_FREE_BYTES = 20 * 1024**3
AUTHORITY_FLAGS = ("physical_accepted", "engineering_accepted", "manufacturing_release",
    "operating_release", "movement_authority", "selected_reference_changed")
MAX_FILES = 10000
GIT_ENV = dict(os.environ, GIT_NO_LAZY_FETCH="1")


def safe_name(name):
    if (not isinstance(name, str) or not name or '\\' in name
            or any(ord(c) < 32 for c in name) or PurePosixPath(name).is_absolute()
            or any(p in ('', '.', '..') for p in name.split('/'))):
        raise ValueError('Unsafe retained source path')
    return name


def tree(repository, revision):
    if not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ValueError('An explicit full historical commit is required')
    resolved = subprocess.check_output(['git', '-C', str(repository), 'rev-parse',
        revision + '^{commit}'], timeout=15, env=GIT_ENV).decode().strip()
    if resolved != revision:
        raise ValueError('Historical commit differs')
    raw = subprocess.check_output(['git', '-C', str(repository), 'ls-tree', '-r',
        '-l', '-z', revision], timeout=30, env=GIT_ENV)
    result = {}
    for row in raw.split(b'\0'):
        if not row:
            continue
        meta, name = row.split(b'\t', 1)
        mode, kind, blob, size = meta.decode().split()
        name = safe_name(name.decode())
        result[name] = (mode, kind, blob, int(size) if size != '-' else -1)
    return result


def blobs(repository, entries, names):
    """Read bounded regular Git blobs, validating object identity, without fetch."""
    names = sorted(set(names))
    if len(names) > MAX_FILES:
        raise ValueError('Historical source file budget exceeded')
    total = 0
    for name in names:
        safe_name(name)
        mode, kind, _, size = entries[name]
        if mode not in ('100644', '100755') or kind != 'blob' or size < 0:
            raise ValueError('Ordinary historical blobs required')
        total += size
    if total > MAX_SOURCE_BYTES:
        raise ValueError('Historical source byte budget exceeded')
    raw = subprocess.check_output(['git', '-C', str(repository), 'cat-file', '--batch'],
        input=('\n'.join(entries[n][2] for n in names) + '\n').encode(), timeout=60, env=GIT_ENV)
    offset = 0
    for name in names:
        end = raw.index(b'\n', offset)
        oid, kind, length = raw[offset:end].decode().split()
        length = int(length)
        offset = end + 1
        data = raw[offset:offset + length]
        offset += length + 1
        if (oid != entries[name][2] or kind != 'blob' or length != entries[name][3]
                or len(data) != length or raw[offset - 1:offset] != b'\n'
                or hashlib.sha1(('blob ' + str(length) + '\0').encode() + data).hexdigest() != oid):
            raise ValueError('Historical Git blob differs')
        yield name, data
    if offset != len(raw):
        raise ValueError('Historical Git response differs')


CHILD = r'''
import json, os, resource, sys
resource.setrlimit(resource.RLIMIT_AS, (3*1024**3, 3*1024**3))
resource.setrlimit(resource.RLIMIT_CPU, (120, 120))
resource.setrlimit(resource.RLIMIT_FSIZE, (1024**2, 1024**2))
sys.path.insert(0, sys.argv[1])
def guard(event, args):
    if event in ('subprocess.Popen', 'os.system', 'os.posix_spawn', 'os.fork', 'os.exec'):
        raise RuntimeError('Retained verification cannot launch native processes')
sys.addaudithook(guard)
from engineering.railway_closure import publication
assert os.path.realpath(publication.__file__).startswith(os.path.realpath(sys.argv[1])+os.sep)
result = publication.verify(root=sys.argv[1], output=sys.argv[2])
print(json.dumps(result, sort_keys=True))
'''


def verify(*, root, output, source_revision, state=None):
    root = Path(root).resolve()
    out = Path(output).absolute()
    if any(p.is_symlink() for p in (out, *out.parents)) or not out.is_dir():
        raise ValueError('Ordinary retained publication required')
    manifest = json.loads((out / 'manifest.json').read_bytes())
    sources = dict(manifest['source_sha256'])
    delivery_manifest = out / 'delivery/manifest.json'
    if delivery_manifest.is_file():
        for name, digest in json.loads(delivery_manifest.read_bytes())['source_sha256'].items():
            if name in sources and sources[name] != digest:
                raise ValueError('Nested historical source epoch conflicts')
            sources[name] = digest
    # The caller's explicit Git pin is the trust input, never a live-file fallback.
    entries = tree(root, source_revision)
    try:
        prefix = out.relative_to(root).as_posix()
    except ValueError:
        raise ValueError('Retained publication must retain its repository path') from None
    expected_payload = {n[len(prefix)+1:] for n in entries if n.startswith(prefix + '/')}
    actual_payload = set()
    for path in out.rglob('*'):
        if path.is_symlink() or not (path.is_dir() or path.is_file()):
            raise ValueError('Ordinary retained payload required')
        if path.is_file():
            actual_payload.add(path.relative_to(out).as_posix())
    if actual_payload != expected_payload:
        raise ValueError('Original retained artifact inventory differs')
    for name, data in blobs(root, entries, [prefix + '/' + n for n in actual_payload]):
        if (out / name[len(prefix)+1:]).read_bytes() != data:
            raise ValueError('Original retained artifact bytes differ')
    # Recover import closure only from this same commit. Every declared source,
    # including data and Rust files, is independently checked against its SHA256.
    names = set(sources)
    names.update(n for n in entries if n.endswith('.py') and
        (n.startswith('engineering/') or n.startswith('services/integration/')))
    names.update(n for n in ('engineering/design_search/craft_backends/tools.json',) if n in entries)
    if any(n not in entries for n in names):
        raise ValueError('Historical source is missing')
    target_parent = None if state is None else Path(state)
    if target_parent is not None:
        target_parent.mkdir(parents=True, exist_ok=True)
    probe = Path(tempfile.gettempdir()) if target_parent is None else target_parent
    size = sum(entries[n][3] for n in names)
    if size > MAX_SOURCE_BYTES or shutil.disk_usage(probe).free - size < MIN_FREE_BYTES:
        raise ValueError('Historical replay disk reserve unavailable')
    with tempfile.TemporaryDirectory(prefix='osr-retained-epoch-', dir=target_parent) as folder:
        epoch = Path(folder)
        for name, data in blobs(root, entries, names):
            if name in sources and hashlib.sha256(data).hexdigest() != sources[name]:
                raise ValueError('Recorded sources do not co-occur at the pinned commit: ' + name)
            dest = epoch / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        if 'engineering/railway_closure/publication.py' not in sources:
            raise ValueError('Original verification method is not source-bound')
        env = {k: v for k, v in os.environ.items() if k not in ('PYTHONPATH', 'PYTHONHOME')}
        env.update(PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
        run = subprocess.run([sys.executable, '-I', '-B', '-c', CHILD, str(epoch), str(out)],
            cwd=epoch, env=env, capture_output=True, text=True, timeout=150, check=True)
        result = json.loads(run.stdout)
    if any(result.get(k, False) is not False for k in AUTHORITY_FLAGS):
        raise ValueError('Historical verification cannot grant acceptance or authority')
    if result.get('verified') is not True:
        raise ValueError('Original historical checker did not verify')
    return dict(retained_verified=True, source_epoch_verified=True,
        source_status='historical', current_source_valid=False, original_checker_result=result,
        **{k: False for k in AUTHORITY_FLAGS},
        source_revision=source_revision, source_files=len(sources),
        recovered_context_files=len(names), recovered_context_bytes=size,
        original_manifest_sha256=hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest(),
        verification_scope='original artifact bytes, whole source epoch and unchanged original checker; no new native execution',
        isolation='isolated Python imports, resource limits and cooperative process guard; not an OS sandbox')
