#!/usr/bin/env python3
"""Restore exact retired city maglev packets from the pinned Git revision."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engineering.performance import check_disk_reservation, disk_reservation

MANIFEST = ROOT / 'docs/archives/retired-city-maglev/manifest.json'


def run(*args: str) -> bytes:
    return subprocess.check_output(['git', *args], cwd=ROOT)


def source_inventory(manifest: dict, selected: list[dict]) -> dict[str, str]:
    commit = manifest['source_commit']
    if subprocess.run(['git', 'cat-file', '-e', commit + '^{tree}'], cwd=ROOT,
                      stderr=subprocess.DEVNULL).returncode:
        raise ValueError('Pinned city study commit is unavailable. Fetch it explicitly with '
                         f'git fetch --no-tags --depth=1 origin {commit}')
    expected = {}
    for entry in selected:
        path = entry['path']
        if run('rev-parse', f'{commit}:{path}').decode().strip() != entry['git_tree_oid']:
            raise ValueError('Pinned city study tree differs: ' + path)
        records = run('ls-tree', '-r', '-z', '--format=%(objectname)%x09%(path)',
                      commit, '--', path).split(b'\0')
        members = {}
        for record in records:
            if record:
                oid, name = record.split(b'\t', 1)
                members[name.decode()] = oid.decode()
        if len(members) != entry['file_count'] or set(Path(name).name for name in members) != {
                'manufacturing.json', 'network.svg', 'retained-records.json', 'summary.json'}:
            raise ValueError('Pinned city study file inventory differs: ' + path)
        expected.update(members)
    return expected


def hydrate(manifest: dict, selected: list[dict], destination: Path, expected: dict[str, str]) -> None:
    if destination.exists() or destination.is_symlink():
        raise ValueError('Historical output destination must not exist: ' + str(destination))
    parent = destination.parent.resolve(strict=True)
    destination = parent / destination.name
    projected = sum(entry['bytes'] for entry in selected) + 64 * 1024 * 1024
    with disk_reservation(ROOT, parent, 'hydrate-retired-city-maglev', projected) as lease:
        with tempfile.TemporaryDirectory(prefix='.retired-city-maglev-', dir=parent) as temporary:
            staging = Path(temporary)
            command = ['git', 'archive', '--format=tar', manifest['source_commit'],
                       '--', *(entry['path'] for entry in selected)]
            process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            seen = set()
            try:
                assert process.stdout is not None
                with tarfile.open(fileobj=process.stdout, mode='r|') as archive:
                    for member in archive:
                        if member.isdir():
                            continue
                        if not member.isfile() or member.name not in expected or member.name in seen:
                            raise ValueError('Unexpected Git archive member: ' + member.name)
                        target = staging / member.name
                        if not target.resolve().is_relative_to(staging):
                            raise ValueError('Archive member escapes destination: ' + member.name)
                        target.parent.mkdir(parents=True, exist_ok=True)
                        source = archive.extractfile(member)
                        assert source is not None
                        digest = hashlib.sha1()
                        digest.update(f'blob {member.size}\0'.encode())
                        with target.open('xb') as output:
                            while chunk := source.read(8 * 1024 * 1024):
                                output.write(chunk)
                                digest.update(chunk)
                                check_disk_reservation(lease)
                        if digest.hexdigest() != expected[member.name]:
                            raise ValueError('Restored file differs from pinned Git blob: ' + member.name)
                        seen.add(member.name)
                if seen != set(expected):
                    raise ValueError('Git archive omitted declared historical files')
                if process.wait() != 0:
                    raise ValueError('Git archive failed: ' + process.stderr.read().decode(errors='replace'))
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait()
            check_disk_reservation(lease)
            staging.rename(destination)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--city', help='City slug in the retired inventory')
    group.add_argument('--all', action='store_true', help='Restore all 265 packets')
    parser.add_argument('--output', type=Path, help='Empty destination for restored files')
    parser.add_argument('--check', action='store_true', help='Verify pinned Git trees without writing')
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    if manifest['schema'] != 'osr-retired-city-maglev-trees/1':
        raise ValueError('Unsupported city study inventory')
    selected = manifest['trees'] if args.all else [
        entry for entry in manifest['trees'] if entry['city_slug'] == args.city]
    if not selected:
        raise ValueError('City is not in the retired inventory: ' + args.city)
    expected = source_inventory(manifest, selected)
    if args.check:
        print(f'Pinned historical Git trees available: {len(selected)} cities, {len(expected)} files')
        return
    if args.output is None:
        parser.error('--output is required unless --check is used')
    hydrate(manifest, selected, args.output, expected)
    print(f'Restored and verified {len(selected)} cities, {len(expected)} files under {args.output}')


if __name__ == '__main__':
    main()
