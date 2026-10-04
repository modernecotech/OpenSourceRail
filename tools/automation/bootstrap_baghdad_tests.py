#!/usr/bin/env python3
"""Restore the exact ignored operations input from the tracked proposal archive."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
CITY = ROOT / 'cities/catalogue/west-asia/Iraq/Baghdad'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def restore(root=ROOT, *, check=False):
    city = root / CITY.relative_to(ROOT)
    metadata = json.loads((city/'operations/baghdad-operations-manifest.json').read_text())
    if metadata['file'] != 'baghdad-operations.json.gz':
        raise ValueError('Unexpected operations input name')
    target = city/'operations'/metadata['file']
    expected = metadata['compressed_sha256']
    size = metadata['compressed_bytes']
    if target.exists():
        if target.stat().st_size != size or sha(target.read_bytes()) != expected:
            raise ValueError('Existing operations input differs; preserve it and reconcile explicitly')
        return 'verified-existing'
    if check:
        raise ValueError('Operations input missing; run bootstrap_baghdad_tests.py')
    proposal = city/'proposal'
    manifest = json.loads((proposal/'manifest.json').read_text())
    archive_path = proposal/'Baghdad-Proposal-Supporting-Data.zip'
    receipt = manifest['outputs'][archive_path.relative_to(root).as_posix()]
    if archive_path.stat().st_size != receipt['bytes'] or sha(archive_path.read_bytes()) != receipt['sha256']:
        raise ValueError('Proposal archive differs from its publication receipt')
    relative = target.relative_to(root).as_posix()
    member = json.loads((proposal/'archive-manifest.json').read_text())['members'][relative]
    if member != {'bytes': size, 'sha256': expected}:
        raise ValueError('Publication and operations receipts disagree')
    with zipfile.ZipFile(archive_path) as archive:
        if len(archive.namelist()) != len(set(archive.namelist())):
            raise ValueError('Duplicate archive members')
        if archive.getinfo(relative).file_size != size:
            raise ValueError('Operations archive size differs')
        raw = archive.read(relative)
    if len(raw) != size or sha(raw) != expected:
        raise ValueError('Operations archive content differs')
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(raw)
    try:
        temporary.chmod(0o644)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    return 'restored-hash-bound-input'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    print('Baghdad test input: '+restore(check=args.check))

if __name__ == '__main__':
    main()
