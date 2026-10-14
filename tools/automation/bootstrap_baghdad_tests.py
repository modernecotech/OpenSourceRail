#!/usr/bin/env python3
"""Restore exact current test inputs, with legacy proposal-snapshot support."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile
from proposal_archives import read_members

ROOT = Path(__file__).resolve().parents[2]
CITY = ROOT / 'cities/catalogue/west-asia/Iraq/Baghdad'
CURRENT_INPUTS = Path('engineering/assurance/baghdad-test-inputs')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def current_inputs(root):
    directory=root/CURRENT_INPUTS
    path=directory/'manifest.json'
    if not path.exists():return None
    value=json.loads(path.read_text())
    if value.get('schema')!='osr-current-baghdad-test-inputs/1' or value.get('physical_release') is not False:
        raise ValueError('Invalid current test-input snapshot')
    for name,digest in value['source_sha256'].items():
        source=(root/name).resolve()
        if Path(name).is_absolute() or not source.is_relative_to(root.resolve()) or sha(source.read_bytes())!=digest:
            raise ValueError('Current test-input source receipt differs: '+name)
    return directory,value

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
    relative = target.relative_to(root).as_posix()
    snapshot=current_inputs(root)
    if snapshot:
        proposal,manifest=snapshot;member=manifest['members'][relative]
    else:
        proposal=city;manifest=json.loads((proposal/'manifest.json').read_text())
        member=json.loads((proposal/'archive-manifest.json').read_text())['members'][relative]
    if member != {'bytes': size, 'sha256': expected}:
        raise ValueError('Publication and operations receipts disagree')
    raw = read_members(root,proposal,manifest,[relative])[relative]
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
    print('Baghdad solver/GIS test inputs: '+restore_proposal_inputs(check=args.check))

def restore_proposal_inputs(root=ROOT, *, check=False):
    """Restore receipt-bound solver/GIS/alignment inputs, preserving local drift."""
    city=root/CITY.relative_to(ROOT)
    snapshot=current_inputs(root)
    if snapshot:
        proposal,manifest=snapshot;inputs=manifest['members']
    else:
        proposal=city;manifest=json.loads((proposal/'manifest.json').read_text());inputs=manifest['inputs']
    prefix=city.relative_to(root).as_posix()+'/engineering/'
    allowed=('energy/','gis/','sumo/')
    corridor=(city/'corridors.json').relative_to(root).as_posix()
    receipts={path:value for path,value in inputs.items()
        if path==corridor or path.startswith(prefix) and path[len(prefix):].startswith(allowed)}
    missing=[]
    for relative,receipt in receipts.items():
        path=root/relative
        if '..' in Path(relative).parts or Path(relative).is_absolute():raise ValueError('Unsafe proposal input path')
        path.resolve().relative_to(root.resolve())
        if path.is_file():
            if path.stat().st_size!=receipt['bytes'] or sha(path.read_bytes())!=receipt['sha256']:
                raise ValueError('Existing proposal solver/GIS input differs: '+relative)
        else:missing.append(relative)
    if not missing:return 'verified-existing'
    if check:raise ValueError('Proposal solver/GIS inputs missing; run bootstrap_baghdad_tests.py')
    # Validate every requested byte before creating any missing input.
    data=read_members(root,proposal,manifest,missing)
    for name,raw in data.items():
        if len(raw)!=receipts[name]['bytes'] or sha(raw)!=receipts[name]['sha256']:
            raise ValueError('Proposal solver/GIS archive content differs: '+name)
    for name,raw in data.items():
        target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=target.parent,delete=False) as handle:
            temporary=Path(handle.name);handle.write(raw)
        try:
            temporary.chmod(0o644);temporary.replace(target)
        finally:temporary.unlink(missing_ok=True)
    return 'restored-hash-bound-inputs'

if __name__ == '__main__':
    main()
