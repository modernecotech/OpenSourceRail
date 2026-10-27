#!/usr/bin/env python3
"""Check an immutable research publication against its exact source checkout.

This guard neither rewrites evidence nor substitutes for the original verifier.
Run the publication's own verifier next, from the validated historical checkout.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

PACKETS = {
    'trip-dynamics': ('docs/design-engine/trip-dynamics', 'd7c8f40e13d9a5f4889921557311542b84bcbfb1'),
    'comfort-options': ('docs/design-engine/ferrite-maglev/comfort-options', 'f0946b699376699b408df6e9a1f04a657f74022b'),
    'comfort-design': ('docs/design-engine/ferrite-maglev/comfort-design', '578ee3950b872bf30fbf9e4207b2bda85951bdd7'),
    'vehicle-optimisation': ('docs/design-engine/vehicle-optimisation', 'afff13ebdb775a024b3b3f2f3331473297e853ef'),
    'passive-suspension': ('docs/design-engine/passive-suspension', 'aa31cec3307f82b0a5de65b76f8938081f7801a8'),
}


def ordinary(root, name):
    relative = PurePosixPath(name)
    if (relative.is_absolute() or '..' in relative.parts or relative.as_posix() != name
            or name in ('', '.') or '\\' in name):
        raise ValueError('Ordinary relative evidence path required: ' + name)
    path = Path(root)
    for part in relative.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError('Linked evidence path refused: ' + name)
    if not path.is_file():
        raise ValueError('Evidence file missing: ' + name)
    return path


def revision(repository):
    return subprocess.check_output(['git', '-C', str(repository), 'rev-parse', 'HEAD'], text=True).strip()


def committed_receipt(repository, revision, name):
    return subprocess.check_output(['git', '-C', str(repository), 'show', revision + ':' + name])


def verify(packet, repository, receipt_root):
    folder, expected_revision = PACKETS[packet]
    repository, receipt_root = Path(repository).resolve(), Path(receipt_root).resolve()
    if revision(repository) != expected_revision:
        raise ValueError('Historical publication requires its exact originating revision')
    manifest_name = folder + '/manifest.json'
    raw = ordinary(receipt_root, manifest_name).read_bytes()
    if (ordinary(repository, manifest_name).read_bytes() != raw
            or committed_receipt(repository, expected_revision, manifest_name) != raw):
        raise ValueError('Retained publication receipt differs from the immutable historical source')
    manifest = json.loads(raw)
    if packet == 'trip-dynamics':
        # This original schema authenticates its campaign input in its own verifier;
        # the receipt bytes above remain bound to the exact immutable Git blob.
        if manifest.get('schema') != 'osr-trip-publication/1' or not re.fullmatch('[0-9a-f]{64}', manifest.get('campaign_id', '')):
            raise ValueError('Original trip publication schema/campaign identity required')
    else:
        key = 'manifest_id' if packet in ('comfort-design', 'comfort-options') else 'publication_id'
        unsigned = {k: v for k, v in manifest.items() if k != key}
        encoded = (json.dumps(unsigned, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()
        if manifest[key] != sha256(encoded).hexdigest():
            raise ValueError('Research publication receipt identity differs')
    for flag in ('physical_accepted', 'engineering_accepted', 'configuration_adopted'):
        if manifest.get(flag) is not False:
            raise ValueError('Research publication cannot assert ' + flag)
    sources, payloads = manifest['source_sha256'], manifest['files_sha256']
    if not sources or not payloads:
        raise ValueError('Complete recorded source and payload inventories required')
    for name, expected in sources.items():
        if not re.fullmatch('[0-9a-f]{64}', expected) or sha256(ordinary(repository, name).read_bytes()).hexdigest() != expected:
            raise ValueError('Historical source bytes differ: ' + name)
    # Nested manifests are payloads too; exclude only this publication's receipt.
    actual = {p.relative_to(repository / folder).as_posix() for p in (repository / folder).rglob('*')
              if p.is_file() and p != repository / manifest_name}
    if actual != set(payloads):
        raise ValueError('Historical publication payload inventory differs')
    for name, expected in payloads.items():
        if not re.fullmatch('[0-9a-f]{64}', expected) or sha256(ordinary(repository / folder, name).read_bytes()).hexdigest() != expected:
            raise ValueError('Historical payload bytes differ: ' + name)
    report = dict(schema='osr-historical-publication-source-guard/1', packet=packet,
                  source_revision=expected_revision, receipt_sha256=sha256(raw).hexdigest(),
                  source_files=len(sources), payload_files=len(payloads),
                  source_and_payload_bytes_verified=True, original_semantic_verifier_required=True,
                  physical_accepted=False, engineering_accepted=False)
    report['guard_id'] = sha256((json.dumps(report, sort_keys=True, separators=(',', ':'))+'\n').encode()).hexdigest()
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet', choices=PACKETS, required=True)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--receipt-root', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        value = verify(args.packet, args.repository, args.receipt_root)
    except Exception as exc:
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(dict(schema='osr-historical-publication-source-guard/1',
                packet=args.packet, source_revision=PACKETS[args.packet][1], execution='held',
                error=type(exc).__name__ + ': ' + str(exc),
                source_and_payload_bytes_verified=False, physical_accepted=False, engineering_accepted=False),
                sort_keys=True, indent=2) + '\n')
        raise
    encoded = json.dumps(value, sort_keys=True, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
    print(encoded, end='')


if __name__ == '__main__':
    main()
