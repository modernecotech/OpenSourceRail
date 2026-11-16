"""Reuse a Rust case codec only when its local build receipt still matches.

This is a build-cache admission check, not a campaign source epoch or an OS
sandbox. Campaigns separately bind the exact executable bytes they use.
"""

from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile

SCHEMA = 'osr-case-codec-build-receipt/1'
BIN = Path('target/debug/osr-campaign-case-nodes')
DEPFILE = Path('target/debug/osr-campaign-case-nodes.d')
RECEIPT = Path('target/debug/osr-campaign-case-nodes.build-receipt.json')
BUILD_COMMAND = ('cargo', 'build', '--quiet', '--locked', '-p', 'osr-design-search',
                 '--features', 'columnar', '--bin', 'osr-campaign-case-nodes')
REQUIRED_DEPENDENCIES = frozenset({
    'crates/osr-design-search/src/bin/osr-campaign-case-nodes.rs',
    'crates/osr-design-search/src/case_nodes.rs',
    'crates/osr-design-search/src/canonical.rs',
    'crates/osr-design-search/src/columnar.rs',
    'crates/osr-design-search/src/lib.rs',
    'crates/osr-design-search/src/scheduling.rs',
})
BUILD_INPUTS = (
    'Cargo.toml', 'crates/osr-design-search/Cargo.toml', 'Cargo.lock',
    'rust-toolchain.toml', 'osr', 'tools/automation/case_codec_build_receipt.py',
)
MAX_RECEIPT_BYTES = 1024 * 1024
MAX_DEPFILE_BYTES = 1024 * 1024


def _digest(path: Path) -> str:
    value = sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def _ordinary(path: Path, maximum: int | None = None) -> None:
    if path.is_symlink():
        raise ValueError(f'Unsafe symlink: {path}')
    info = path.stat(follow_symlinks=False)
    if not stat.S_ISREG(info.st_mode) or (maximum is not None and info.st_size > maximum):
        raise ValueError(f'Unsafe or oversized ordinary file: {path}')


def _inside(root: Path, value: str) -> tuple[str, Path]:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    path = Path(os.path.abspath(path))
    if not path.is_relative_to(root):
        raise ValueError('Codec dependency escaped the repository')
    if any(p.is_symlink() for p in (path, *path.parents) if p == root or p.is_relative_to(root)):
        raise ValueError('Codec dependency path contains a symlink')
    _ordinary(path)
    return path.relative_to(root).as_posix(), path


def _dependencies(root: Path) -> tuple[str, dict[str, str]]:
    depfile = root / DEPFILE
    _ordinary(depfile, MAX_DEPFILE_BYTES)
    raw = depfile.read_text(encoding='utf-8')
    if ':' not in raw or '\n' in raw.rstrip('\n'):
        raise ValueError('Unexpected Rust codec depfile format')
    target, source_names = raw.strip().split(':', 1)
    if Path(os.path.abspath(target)) != root / BIN:
        raise ValueError('Rust depfile points to another executable')
    names = shlex.split(source_names)
    if not names or len(names) != len(set(names)):
        raise ValueError('Rust depfile has missing or duplicate inputs')
    result = dict(_inside(root, name) for name in names)
    if not REQUIRED_DEPENDENCIES.issubset(result):
        raise ValueError('Rust depfile omitted a required compiled source')
    return _digest(depfile), {name: _digest(path) for name, path in result.items()}


def _build_environment() -> dict[str, str]:
    prefixes = ('CARGO_', 'RUST', 'CC', 'CXX', 'AR', 'CFLAGS', 'CXXFLAGS',
                'LDFLAGS', 'PKG_CONFIG', 'SOURCE_DATE_EPOCH')
    return {key: value for key, value in sorted(os.environ.items())
            if key.startswith(prefixes)}


def _tool(name: str) -> dict[str, str]:
    selected = os.environ.get('RUSTC', name) if name == 'rustc' else name
    path = shutil.which(selected)
    if path is None:
        raise ValueError(f'{selected} unavailable')
    binary = Path(os.path.abspath(path))
    # rustup launchers can be symlinks; their resolved bytes and reported active
    # toolchain both participate in the cache identity.
    resolved = binary.resolve(strict=True)
    _ordinary(resolved)
    version = subprocess.run((str(binary), '-vV' if name == 'rustc' else '--version'),
                             capture_output=True, text=True, check=True, timeout=15).stdout.strip()
    return dict(path=str(binary), resolved_path=str(resolved), executable_sha256=_digest(resolved),
                version=version)


def _explicit_tool_hashes() -> dict[str, dict[str, str]]:
    result = {}
    for key, value in sorted(os.environ.items()):
        if key not in {'RUSTC_WRAPPER', 'RUSTC_WORKSPACE_WRAPPER', 'CC', 'CXX', 'AR', 'RANLIB'} and not key.endswith('_LINKER'):
            continue
        if not value:
            continue
        command = shlex.split(value)
        if not command:
            raise ValueError(f'Empty build tool override: {key}')
        path = shutil.which(command[0])
        if path is None:
            raise ValueError(f'Build tool override unavailable: {key}')
        resolved = Path(path).resolve(strict=True)
        _ordinary(resolved)
        result[key] = dict(path=str(resolved), executable_sha256=_digest(resolved))
    return result


def _snapshot(root: Path) -> dict:
    root = root.resolve(strict=True)
    for folder in (root / 'target', root / 'target/debug'):
        if folder.is_symlink() or not folder.is_dir():
            raise ValueError('Rust build target must be an ordinary directory')
    binary = root / BIN
    _ordinary(binary)
    depfile_hash, dependencies = _dependencies(root)
    inputs = {name: _digest(_inside(root, name)[1]) for name in BUILD_INPUTS}
    for name in ('.cargo/config', '.cargo/config.toml'):
        optional = root / name
        if optional.exists() or optional.is_symlink():
            inputs[name] = _digest(_inside(root, name)[1])
    cargo_home = Path(os.environ.get('CARGO_HOME', str(Path.home() / '.cargo'))).expanduser()
    global_config = {}
    for name in ('config', 'config.toml'):
        path = cargo_home / name
        if path.exists() or path.is_symlink():
            _ordinary(path)
            global_config[name] = _digest(path)
    return dict(schema=SCHEMA, build_command=list(BUILD_COMMAND),features=['columnar'],
                profile='dev', build_environment=_build_environment(),
                cargo_home=str(cargo_home),cargo_home_config_sha256=global_config,
                rustc=_tool('rustc'), cargo=_tool('cargo'),explicit_tool_sha256=_explicit_tool_hashes(),
                source_sha256={**dependencies, **inputs}, depfile_sha256=depfile_hash,
                executable_sha256=_digest(binary))


def _encoded(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n').encode()


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate build receipt key')
        result[key] = value
    return result


def check(root: Path) -> bool:
    receipt = root / RECEIPT
    try:
        _ordinary(receipt, MAX_RECEIPT_BYTES)
        raw = receipt.read_bytes()
        value = json.loads(raw, object_pairs_hook=_unique)
        if not isinstance(value, dict) or value.get('receipt_id') != sha256(
                _encoded({key: item for key, item in value.items() if key != 'receipt_id'})).hexdigest():
            return False
        if raw != _encoded(value):
            return False
        return value == dict(_snapshot(root), receipt_id=value['receipt_id'])
    except (OSError, ValueError, UnicodeError, subprocess.SubprocessError):
        return False


def seal(root: Path) -> None:
    value = _snapshot(root)
    value['receipt_id'] = sha256(_encoded(value)).hexdigest()
    target = root / RECEIPT
    data = _encoded(value)
    if len(data) > MAX_RECEIPT_BYTES:
        raise ValueError('Rust codec build receipt exceeds bound')
    descriptor, name = tempfile.mkstemp(prefix='.case-codec-receipt.', dir=target.parent)
    try:
        with os.fdopen(descriptor, 'wb') as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        os.replace(name, target)
        directory = os.open(target.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    if not check(root):
        raise ValueError('Rust codec build receipt readback differs')


def build(root: Path) -> None:
    for name in (BIN, DEPFILE):
        path = root / name
        if path.is_symlink():
            raise ValueError('Unsafe Rust codec build artifact symlink')
        if path.exists():
            _ordinary(path)
            path.unlink()
    subprocess.run(BUILD_COMMAND, cwd=root, check=True)
    seal(root)


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] not in ('check', 'build'):
        print('usage: case_codec_build_receipt.py check|build ROOT', file=sys.stderr)
        return 2
    root = Path(sys.argv[2]).resolve(strict=True)
    if sys.argv[1] == 'check':
        return 0 if check(root) else 1
    build(root)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f'Rust case codec build receipt: {error}', file=sys.stderr)
        raise SystemExit(3) from error
