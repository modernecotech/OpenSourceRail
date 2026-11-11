"""Verify the line-30 budget packet against its recorded historical source epoch.

The packet differs from current sources only at the braking input. This checks
its original identities and financial ledger without replaying the calculation.
"""
from __future__ import annotations

import json
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity
from . import line_benchmark

PACKAGE = 'docs/design-engine/line30-benchmark'
SUPPORT = 'docs/archives/line30-benchmark-source-epochs/manifest.json'
PACKAGE_MANIFEST_ID = '0db5de45ccfaba484183d56f7719afe2c6144427b817f1adbbf915376a38ebf7'
EVALUATION_ID = '2b2b1033fda3b123b711383b25c687e6e3b5e9a3c9dacbedfd74df569304f2c0'
ARCHIVE_ID = '2a5bb02a9518ab30062cbdd3983581d87482ea1b79a13026945c5be4b6462dca'
SOURCE = 'engineering/station_rail/braking.py'
SOURCE_HASH = '905af0b5762a1acf987a831d588f5b8b26f0b400f3bf33be2dac2f940ce38510'
SOURCE_COMMIT = 'dbb62c6aeb48377cb57a00521075bba333f741d2'
SOURCE_BLOB = '74e12d096a4103877c1ba6a89ef33ea0e841da54'
SOURCE_ARTIFACT = (
    'docs/archives/coupled-railway-source-epochs/' + SOURCE_HASH
    + '/source/' + SOURCE
)
SCOPE = (
    'Exact historical source bytes for the unchanged line-30 analytical budget; '
    'no calculation replay or current-evaluator admission'
)
FLAGS = (
    'physical_accepted', 'engineering_accepted', 'manufacturing_release',
    'operating_release', 'selected_reference_changed', 'current_evaluator_admission',
    'numerical_reexecuted', 'physical_equivalence_proven',
)


def _file(root: Path, relative: str, *, maximum: int = 32 * 1024 * 1024) -> Path:
    path = Path(relative)
    if path.is_absolute() or not path.parts or '..' in path.parts:
        raise ValueError('Ordinary repository-relative line-30 evidence path required')
    target = root / path
    if any(node.is_symlink() for node in (target, *target.parents)
           if node == root or node.is_relative_to(root)):
        raise ValueError('Linked line-30 evidence path rejected')
    if not target.is_file() or target.stat().st_size > maximum:
        raise ValueError('Bounded line-30 evidence file required')
    return target


def verify(root=ROOT, output=None):
    root = Path(root).resolve()
    folder = root / PACKAGE if output is None else Path(output)
    if not folder.is_absolute():
        folder = root / folder
    if folder.resolve() != (root / PACKAGE).resolve():
        raise ValueError('Only the pinned line-30 benchmark can be verified')

    support_path = _file(root, SUPPORT, maximum=1024 * 1024)
    support = json.loads(support_path.read_bytes())
    if (support.get('archive_id') != ARCHIVE_ID
            or support.get('archive_id') != identity({k: v for k, v in support.items() if k != 'archive_id'})
            or support.get('schema') != 'osr-line30-benchmark-source-epoch/1'
            or support.get('benchmark_manifest_id') != PACKAGE_MANIFEST_ID
            or support.get('benchmark_evaluation_id') != EVALUATION_ID
            or support.get('source_commit') != SOURCE_COMMIT
            or support.get('source_git_blob') != SOURCE_BLOB
            or support.get('source_sha256') != {SOURCE: SOURCE_HASH}
            or support.get('source_artifacts') != {SOURCE: SOURCE_ARTIFACT}
            or support.get('files_sha256') != {SOURCE_ARTIFACT: SOURCE_HASH}
            or support.get('scope') != SCOPE
            or any(support.get(key) is not False for key in FLAGS)):
        raise ValueError('Line-30 historical source receipt differs')

    archive_source = _file(root, SOURCE_ARTIFACT, maximum=1024 * 1024)
    if digest(archive_source) != SOURCE_HASH:
        raise ValueError('Line-30 retained braking source differs')

    manifest_path = _file(root, PACKAGE + '/manifest.json', maximum=1024 * 1024)
    manifest = json.loads(manifest_path.read_bytes())
    if (manifest.get('schema') != 'osr-line-budget-publication/1'
            or manifest.get('manifest_id') != PACKAGE_MANIFEST_ID
            or manifest.get('manifest_id') != identity({k: v for k, v in manifest.items() if k != 'manifest_id'})
            or manifest.get('evaluation_id') != EVALUATION_ID
            or set(manifest.get('files', {})) != {'result.json', 'README.md'}):
        raise ValueError('Line-30 package identity differs')
    payload = {}
    for name, expected in manifest['files'].items():
        target = _file(root, PACKAGE + '/' + name)
        if digest(target) != expected:
            raise ValueError('Line-30 package payload differs: ' + name)
        payload[name] = target

    result = json.loads(payload['result.json'].read_bytes())
    if (result.get('evaluation_id') != EVALUATION_ID
            or manifest.get('source_sha256') != result.get('source_sha256')
            or result.get('native_solver_jobs', 0) != 0
            or result.get('engineering_validated') is not False
            or any(result.get(key) is not False for key in FLAGS if key in result)):
        raise ValueError('Line-30 result identity or disposition differs')
    line_benchmark.validate_result(result, root, verify_sources=False)

    historical_sources = []
    for name, expected in result['source_sha256'].items():
        current = _file(root, name)
        if digest(current) == expected:
            continue
        if name != SOURCE or expected != SOURCE_HASH or digest(archive_source) != expected:
            raise ValueError('Line-30 source epoch differs: ' + name)
        historical_sources.append(name)
    if historical_sources != [SOURCE]:
        raise ValueError('Line-30 historical source inventory differs')
    return dict(verified=True, manifest_id=PACKAGE_MANIFEST_ID,
        evaluation_id=EVALUATION_ID, source_epoch='historical',
        source_sha256=result['source_sha256'],
        historical_source_paths=historical_sources, analytical_replay=False,
        native_solver_jobs=0,
        **{key: False for key in FLAGS})
