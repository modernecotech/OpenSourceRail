#!/usr/bin/env python3
"""Retain one exact historical output before its unmodified generator refreshes it.

The v0.5 lifecycle publisher can drop two native UI images when the separate
ERP/FUXA receipt becomes stale. Its staging installer correctly rejects the old
extra files. Move only that complete, Git-authenticated packet aside; preserve
every byte and the original source/receipt guards. No evaluator is substituted.
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess

PIN = '92e1385e03dcd5c6f76a5b0a9dd5ba348f50d164'
PACKET = 'docs/design-engine/ferrite-maglev/pilot-lifecycle'
FILES = {
    'README.md', 'dimension-schedules.json', 'fuxa-project.json',
    'lifecycle-package.json', 'manifest.json', 'native-fuxa.png',
    'native-workbench.png', 'planning-bundle.json', 'qa-travellers.json',
    'serial-history.json', 'study.json.gz', 'supervisory-package.json',
    'unit-procedures.json',
}
FLAGS = ('automatic_handback', 'design_complete', 'engineering_accepted',
         'manufacturing_release', 'movement_authority', 'physical_release',
         'physical_validation')


def git(repository, *arguments):
    return subprocess.check_output(['git', '-C', str(repository), *arguments])


def ordinary(root, relative):
    path = root
    for part in Path(relative).parts:
        path = path / part
        if path.is_symlink():
            raise ValueError('Linked historical path refused: ' + str(relative))
    if not path.is_file():
        raise ValueError('Ordinary historical file required: ' + str(relative))
    return path


def committed_files(repository):
    rows = git(repository, 'ls-tree', '-r', '-z', PIN, '--', PACKET).split(b'\0')
    values = {}
    for row in filter(None, rows):
        metadata, path = row.split(b'\t', 1)
        mode, kind, _ = metadata.split()
        name = path.decode().removeprefix(PACKET + '/')
        if mode != b'100644' or kind != b'blob' or name not in FILES:
            raise ValueError('Unexpected committed lifecycle inventory')
        raw = git(repository, 'show', PIN + ':' + PACKET + '/' + name)
        if len(raw) > 16 * 1024 * 1024:
            raise ValueError('Historical lifecycle file exceeds bounded size')
        values[name] = raw
    if set(values) != FILES:
        raise ValueError('Exact historical thirteen-file lifecycle inventory required')
    return values


def prepare(repository, archive_contract, output):
    repository, output = Path(repository), Path(output)
    if repository.is_symlink() or not repository.is_dir():
        raise ValueError('Explicit ordinary historical repository required')
    repository = repository.resolve()
    if git(repository, 'rev-parse', 'HEAD').decode().strip() != PIN:
        raise ValueError('Exact v0.5 historical revision required')
    if ordinary(repository, 'VERSION').read_bytes() != git(repository, 'show', PIN + ':VERSION'):
        raise ValueError('Historical VERSION differs from its exact source')
    if ordinary(repository, 'VERSION').read_text().strip() != '0.5':
        raise ValueError('Historical v0.5 VERSION required')
    contract = json.loads(Path(archive_contract).read_bytes())
    unsigned = {k: v for k, v in contract.items() if k != 'archive_id'}
    encoded = (json.dumps(unsigned, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()
    if (contract.get('schema') != 'osr-v05-git-archive/1'
            or contract.get('revision') != PIN or contract.get('physical_accepted') is not False
            or contract.get('archive_id') != sha256(encoded).hexdigest()):
        raise ValueError('Current immutable v0.5 archive contract differs')
    # Refuse existing destinations and links before creating or moving anything.
    if output.is_symlink() or output.exists():
        raise ValueError('Fresh retained-output destination required')
    output = output.absolute()
    for parent in (output, *output.parents):
        if parent == repository:
            break
        if parent.is_symlink():
            raise ValueError('Linked retained-output destination refused')
    output = output.resolve()
    if not output.is_relative_to(repository / 'build'):
        raise ValueError('Retained output must be inside the historical build directory')
    packet = repository
    for part in Path(PACKET).parts:
        packet = packet / part
        if packet.is_symlink() or not packet.is_dir():
            raise ValueError('Ordinary complete historical lifecycle packet required')
    expected = committed_files(repository)
    actual = set()
    for path in packet.rglob('*'):
        if path.is_symlink() or not path.is_file():
            raise ValueError('Unexpected linked or nested historical lifecycle output')
        actual.add(path.relative_to(packet).as_posix())
    if actual != FILES:
        raise ValueError('Unowned or missing historical lifecycle files; nothing moved')
    hashes = {}
    for name, raw in expected.items():
        if ordinary(packet, name).read_bytes() != raw:
            raise ValueError('Historical lifecycle bytes differ: ' + name)
        hashes[name] = sha256(raw).hexdigest()
    manifest = json.loads(expected['manifest.json'])
    if (manifest.get('schema') != 'osr-maglev-pilot-lifecycle/1'
            or any(manifest.get(flag) is not False for flag in FLAGS)
            or manifest.get('files_sha256') != {n: h for n, h in hashes.items() if n != 'manifest.json'}):
        raise ValueError('Historical lifecycle receipt inventory/authority differs')
    output.mkdir(parents=True)
    retained = output / 'pilot-lifecycle'
    os.replace(packet, retained)
    for name, raw in expected.items():
        if ordinary(retained, name).read_bytes() != raw:
            raise ValueError('Retained historical lifecycle bytes differ: ' + name)
    report = dict(
        schema='osr-historical-replay-retention/1', execution='retained-for-refresh',
        source_revision=PIN, archive_id=contract['archive_id'], original_packet=PACKET,
        retained_packet=retained.relative_to(repository).as_posix(), files_sha256=hashes,
        retained_files=len(hashes), original_semantic_verifier_required=True,
        original_staging_install_guard_unchanged=True, native_receipts_modified=False,
        scope='Retained historical output only; unmodified publisher must regenerate and verify current bytes',
        native_images='Historical ERP/FUXA screenshots retained, never copied into a refreshed hold packet',
        physical_accepted=False, engineering_accepted=False,
    )
    (output / 'retention.json').write_text(json.dumps(report, sort_keys=True, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--archive-contract', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    try:
        report = prepare(args.repository, args.archive_contract, args.output)
    except Exception as exc:
        report = dict(schema='osr-historical-replay-retention/1', execution='held',
                      error=type(exc).__name__ + ': ' + str(exc), source_revision=PIN,
                      physical_accepted=False, engineering_accepted=False)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, sort_keys=True, indent=2) + '\n')
        raise
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, sort_keys=True, indent=2) + '\n')
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
