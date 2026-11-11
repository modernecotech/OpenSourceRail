"""Verify the immutable compact-launch result under its recorded source epoch.

This checks identities, payload bytes, and the separately retained old braking
source. It deliberately does not replay the comparison under current sources.
"""
from __future__ import annotations

import json
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity

PACKAGE = 'docs/design-engine/compact-launch'
SUPPORT = 'docs/archives/compact-launch-source-epochs/manifest.json'
PACKAGE_ID = 'b14314b0f108372bb8eb4fc38ab43a78b541e01e9130566acb734e2b1b55a897'
ARCHIVE_ID = '2941204424afa28539a5dbca5618e35b3de1ef001be75237315c8ab5fc36065f'
SOURCE = 'engineering/station_rail/braking.py'
SOURCE_HASH = '905af0b5762a1acf987a831d588f5b8b26f0b400f3bf33be2dac2f940ce38510'
SOURCE_COMMIT = 'dbb62c6aeb48377cb57a00521075bba333f741d2'
SOURCE_BLOB = '74e12d096a4103877c1ba6a89ef33ea0e841da54'
SOURCE_ARTIFACT = (
    'docs/archives/coupled-railway-source-epochs/' + SOURCE_HASH
    + '/source/' + SOURCE
)
SCOPE = (
    'Exact historical source bytes for the unchanged compact-launch analytic packet; '
    'no calculation replay or current-evaluator admission'
)
FLAGS = (
    'physical_accepted', 'engineering_accepted', 'manufacturing_release',
    'operating_release', 'configuration_adopted', 'selected_reference_changed',
    'current_evaluator_admission', 'physical_equivalence_proven',
)


def _file(root: Path, relative: str, *, maximum: int = 32 * 1024 * 1024) -> Path:
    path = Path(relative)
    if path.is_absolute() or not path.parts or '..' in path.parts:
        raise ValueError('Ordinary repository-relative evidence path required')
    target = root / path
    if any(node.is_symlink() for node in (target, *target.parents)
           if node == root or node.is_relative_to(root)):
        raise ValueError('Linked compact-launch evidence path rejected')
    if not target.is_file() or target.stat().st_size > maximum:
        raise ValueError('Bounded compact-launch evidence file required')
    return target


def verify(root=ROOT, output=None):
    root = Path(root).resolve()
    folder = root / PACKAGE if output is None else Path(output)
    if not folder.is_absolute():
        folder = root / folder
    if folder.resolve() != (root / PACKAGE).resolve():
        raise ValueError('Only the pinned compact-launch publication can be verified')

    support_path = _file(root, SUPPORT, maximum=1024 * 1024)
    support = json.loads(support_path.read_bytes())
    if (support.get('archive_id') != ARCHIVE_ID
            or support.get('archive_id') != identity({k: v for k, v in support.items() if k != 'archive_id'})
            or support.get('schema') != 'osr-compact-launch-source-epoch/1'
            or support.get('compact_launch_package_id') != PACKAGE_ID
            or support.get('source_commit') != SOURCE_COMMIT
            or support.get('source_git_blob') != SOURCE_BLOB
            or support.get('source_sha256') != {SOURCE: SOURCE_HASH}
            or support.get('source_artifacts') != {SOURCE: SOURCE_ARTIFACT}
            or support.get('files_sha256') != {SOURCE_ARTIFACT: SOURCE_HASH}
            or support.get('scope') != SCOPE
            or any(support.get(key) is not False for key in FLAGS)):
        raise ValueError('Compact-launch historical source receipt differs')

    source_archive = _file(root, SOURCE_ARTIFACT, maximum=1024 * 1024)
    if digest(source_archive) != SOURCE_HASH:
        raise ValueError('Compact-launch retained braking source differs')

    manifest_path = _file(root, PACKAGE + '/manifest.json', maximum=1024 * 1024)
    manifest = json.loads(manifest_path.read_bytes())
    if (manifest.get('schema') != 'osr-compact-launch-package/1'
            or manifest.get('package_id') != PACKAGE_ID
            or manifest.get('package_id') != identity({k: v for k, v in manifest.items() if k != 'package_id'})
            or set(manifest.get('files', {})) != {'inputs.json', 'result.json', 'README.md'}):
        raise ValueError('Compact-launch package identity differs')
    payload = {}
    for name, expected in manifest['files'].items():
        target = _file(root, PACKAGE + '/' + name)
        actual = digest(target)
        if actual != expected:
            raise ValueError('Compact-launch package payload differs: ' + name)
        payload[name] = target
    result = json.loads(payload['result.json'].read_bytes())
    inputs = json.loads(payload['inputs.json'].read_bytes())
    if (result.get('schema') != 'osr-compact-launch-comparison/1'
            or result.get('comparison_id') != manifest.get('comparison_id')
            or result.get('comparison_id') != identity({k: v for k, v in result.items() if k != 'comparison_id'})
            or inputs != dict(configuration=result.get('configuration'),
                source_sha256=result.get('source_sha256'),
                reference_vehicle_candidate_id=result.get('reference_vehicle_candidate_id'))
            or result.get('execution') != 'completed-analytic-research'
            or result.get('native_solver_jobs') != 0
            or result.get('integrated_selection') is not None
            or any(result.get(key) is not False for key in (
                'physical_accepted', 'engineering_accepted', 'manufacturing_release',
                'operating_release', 'configuration_adopted', 'selected_reference_changed'))
            or any(key in result and result[key] is not False for key in (
                'current_evaluator_admission', 'physical_equivalence_proven'))
            or result.get('native_evaluator_admission') is not False
            or result.get('physical_journey_completed') is not False):
        raise ValueError('Compact-launch analytic evidence is mixed or improperly accepted')

    source_map = result.get('source_sha256')
    if not isinstance(source_map, dict) or not source_map:
        raise ValueError('Compact-launch source inventory is missing')
    historical_sources = []
    for name, expected in source_map.items():
        current = _file(root, name)
        if digest(current) == expected:
            continue
        if name != SOURCE or expected != SOURCE_HASH or digest(source_archive) != expected:
            raise ValueError('Compact-launch source epoch differs: ' + name)
        historical_sources.append(name)
    if historical_sources != [SOURCE]:
        raise ValueError('Compact-launch historical source inventory differs')
    return dict(verified=True, package_id=PACKAGE_ID, comparison_id=result['comparison_id'],
        source_epoch='historical', current_source_epoch=False,
        historical_source_paths=historical_sources, analytical_replay=False,
        numerical_reexecuted=False, native_solver_jobs=0,
        **{key: False for key in FLAGS})
