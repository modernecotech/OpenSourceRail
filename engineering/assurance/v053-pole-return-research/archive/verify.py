"""Bounded offline portable receipt verification and isolated exact numeric replay."""
from pathlib import Path, PurePosixPath
from hashlib import sha256
import argparse
import gzip
import json
import math
import os
import shutil
import stat
import subprocess
import sys
import tempfile

SCHEMA = 'osr-portable-pole-return-research/1'
ROOT = Path(os.path.abspath(__file__)).parent
MAX_MEMBERS = 128
MAX_DIRECTORIES = 64
MAX_DEPTH = 16
MAX_MEMBER_BYTES = 32 * 1024**2
MAX_TOTAL_BYTES = 128 * 1024**2
MAX_MANIFEST_BYTES = 1024**2
MAX_RAW_BYTES = 128 * 1024**2
MAX_TOTAL_RAW_BYTES = 256 * 1024**2
RECORDS = ('results.json', 'topology-results.json', 'controls-results.json', 'guidance-results.json')
DRIVERS = ('run.py', 'run_topology.py', 'run_controls.py', 'run_guidance.py')
FLAGS = {'design_complete', 'physical_validation', 'manufacturing_release', 'physical_release',
         'physical_output_authorised', 'engineering_accepted', 'configuration_adopted',
         'complete_system_feasible', 'canonical_outputs_edited', 'canonical_sources_edited'}


def safe(name):
    if not isinstance(name, str) or not name or len(name) > 512:
        raise ValueError('unsafe archive path')
    path = PurePosixPath(name)
    if (not path.parts or path.is_absolute() or path.as_posix() != name or '\\' in name
            or any(part in {'.', '..'} for part in path.parts) or len(path.parts) > MAX_DEPTH
            or any(ord(char) < 32 or ord(char) == 127 for char in name)):
        raise ValueError('unsafe archive path: ' + repr(name))
    return path


def ordinary(path, directory=False):
    """Check lexical ancestors before opening; do not resolve away symbolic links."""
    path = Path(os.path.abspath(path))
    for parent in reversed(path.parents):
        if not stat.S_ISDIR(parent.lstat().st_mode):
            raise ValueError('nonordinary or symlink ancestor: ' + str(parent))
    mode = path.lstat().st_mode
    if not (stat.S_ISDIR(mode) if directory else stat.S_ISREG(mode)):
        raise ValueError('nonordinary or symlink archive member: ' + str(path))
    return path


def data(path, maximum):
    path = ordinary(path)
    if path.lstat().st_size > maximum:
        raise ValueError('archive file exceeds byte limit: ' + str(path))
    # O_NOFOLLOW also rejects replacement of the final member with a symlink.
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(descriptor, 'rb') as source:
        if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
            raise ValueError('nonordinary opened member')
        value = source.read(maximum + 1)
    if len(value) > maximum:
        raise ValueError('archive file exceeds byte limit: ' + str(path))
    return value


def digest(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def bounded_integer(value, maximum):
    return type(value) is int and 0 <= value <= maximum


def pairs(values):
    result = {}
    for key, value in values:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def load(value):
    def invalid(value):
        raise ValueError('nonfinite JSON number: ' + value)
    return json.loads(value, object_pairs_hook=pairs, parse_constant=invalid)


def flags(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in FLAGS and item is not False:
                raise ValueError('research cannot assert release/adoption: ' + key)
            flags(item)
    elif isinstance(value, list):
        for item in value:
            flags(item)
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValueError('nonfinite JSON number')


def inventory(root):
    ordinary(root, directory=True)
    files = {}
    directories = 0
    total = 0
    pending = [(root, 0)]
    while pending:
        directory, depth = pending.pop()
        ordinary(directory, directory=True)
        with os.scandir(directory) as entries:
            for entry in entries:
                path = Path(entry.path)
                name = path.relative_to(root).as_posix()
                safe(name)
                mode = entry.stat(follow_symlinks=False).st_mode
                if stat.S_ISDIR(mode):
                    directories += 1
                    if directories > MAX_DIRECTORIES or depth + 1 >= MAX_DEPTH:
                        raise ValueError('archive directory/depth limit exceeded')
                    pending.append((path, depth + 1))
                elif stat.S_ISREG(mode):
                    size = entry.stat(follow_symlinks=False).st_size
                    if not bounded_integer(size, MAX_MEMBER_BYTES):
                        raise ValueError('archive member byte limit exceeded')
                    files[name] = size
                    total += size
                    if len(files) > MAX_MEMBERS or total > MAX_TOTAL_BYTES:
                        raise ValueError('archive count/total byte limit exceeded')
                else:
                    raise ValueError('nonordinary or symlink member: ' + name)
    if 'manifest.json' not in files:
        raise ValueError('missing root manifest')
    del files['manifest.json']  # Nested manifests remain ordinary hashed inventory members.
    return files


def strip_elapsed(value):
    if isinstance(value, dict):
        return {key: strip_elapsed(item) for key, item in value.items() if key != 'elapsed_s'}
    if isinstance(value, list):
        return [strip_elapsed(item) for item in value]
    return value


def verify_archive(root):
    root = Path(os.path.abspath(root))
    members = inventory(root)
    manifest = load(data(root / 'manifest.json', MAX_MANIFEST_BYTES))
    if not isinstance(manifest, dict) or manifest.get('schema') != SCHEMA:
        raise ValueError('unexpected archive schema')
    flags(manifest)
    hashes = manifest.get('files_sha256')
    if not isinstance(hashes, dict) or len(hashes) > MAX_MEMBERS or set(hashes) != set(members):
        raise ValueError('unexpected/missing evidence member')
    for name, expected in hashes.items():
        safe(name)
        if name == 'manifest.json' or not digest(expected):
            raise ValueError('invalid member hash or root self-inventory')
        if sha256(data(root / name, MAX_MEMBER_BYTES)).hexdigest() != expected:
            raise ValueError('archive bytes differ: ' + name)
    raw = manifest.get('raw_records')
    if not isinstance(raw, dict) or set(raw) != set(RECORDS):
        raise ValueError('unexpected raw receipt inventory')
    total_raw = 0
    for name, entry in raw.items():
        if not isinstance(entry, dict):
            raise ValueError('invalid raw receipt')
        safe(entry.get('path'))
        if entry['path'] not in hashes or not digest(entry.get('raw_sha256')):
            raise ValueError('unbound raw receipt')
        if not bounded_integer(entry.get('raw_bytes'), MAX_RAW_BYTES) or not entry['raw_bytes']:
            raise ValueError('raw receipt byte limit exceeded')
        total_raw += entry['raw_bytes']
    if total_raw > MAX_TOTAL_RAW_BYTES:
        raise ValueError('total raw receipt byte limit exceeded')

    def record(name):
        entry = raw[name]
        # Compressed bytes were bounded, inventoried and hashed above.
        import io
        with gzip.GzipFile(fileobj=io.BytesIO(data(root / entry['path'], MAX_MEMBER_BYTES))) as source:
            value = source.read(entry['raw_bytes'] + 1)
        if len(value) != entry['raw_bytes'] or sha256(value).hexdigest() != entry['raw_sha256']:
            raise ValueError('raw receipt differs: ' + name)
        result = load(value)
        flags(result)
        return result

    for name in RECORDS:
        value = record(name)
        sources = value.get('source_sha256')
        if not isinstance(sources, dict) or not 1 <= len(sources) <= MAX_MEMBERS:
            raise ValueError('invalid source binding inventory')
        for source, expected in sources.items():
            safe(source)
            target = ('evidence/' + source.removeprefix('build/pole-return-research/')
                      if source.startswith('build/pole-return-research/') else 'inputs/' + source)
            safe(target)
            if not digest(expected) or hashes.get(target) != expected:
                raise ValueError('source binding differs: ' + source)
    summary = load(data(root / 'summary.json', MAX_MEMBER_BYTES))
    flags(summary)
    if summary.get('baseline_failure_invariant') is not True or summary.get('guidance_combined_screen_passes') != 0:
        raise ValueError('summary changes recorded failure scope')
    return members, record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--replay', action='store_true')
    args = parser.parse_args()
    members, record = verify_archive(ROOT)
    print(json.dumps(dict(state='hash-consistent-research-evidence', files=len(members),
                          baseline_failure_invariant=True, all_release_adoption_flags_false=True)), flush=True)
    if args.replay:
        with tempfile.TemporaryDirectory(prefix='osr-pole-return-replay-') as temporary:
            tree = Path(temporary)
            for name in members:
                if name.startswith('inputs/'):
                    target = tree / name.removeprefix('inputs/')
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data(ROOT / name, MAX_MEMBER_BYTES))
            out = tree / 'build/pole-return-research'
            out.mkdir(parents=True)
            for name in DRIVERS:
                (out / name).write_bytes(data(ROOT / 'evidence' / name, MAX_MEMBER_BYTES))
            env = {**os.environ, 'PYTHONPATH': str(tree), 'PYTHONDONTWRITEBYTECODE': '1',
                   'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1'}
            for driver, name in zip(DRIVERS, RECORDS):
                process = subprocess.run([sys.executable, str(out / driver)], cwd=tree, env=env,
                                         capture_output=True, text=True, timeout=300)
                if process.returncode:
                    raise ValueError('replay driver failed: ' + driver + '\n' + process.stdout[-2000:] + process.stderr[-2000:])
                actual = load(data(out / name, MAX_RAW_BYTES))
                flags(actual)
                expected = record(name)
                if strip_elapsed(actual) != strip_elapsed(expected):
                    raise ValueError('replayed numeric evidence differs: ' + name)
                print(json.dumps(dict(driver=driver, state='exact-replay-apart-from-elapsed',
                                      cases=actual.get('executed_cases', len(actual['cases'])))), flush=True)


if __name__ == '__main__':
    main()
