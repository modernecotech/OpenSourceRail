"""Verify the line-30 budget packet against its recorded historical source epoch.

The original braking source and selected vehicle cost can differ from current
sources. Their exact retained bytes authenticate the unchanged financial ledger
without replaying the calculation or admitting it to the current evaluator.
"""
from __future__ import annotations

import argparse
import json
from hashlib import sha1, sha256
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
COST_SOURCE = line_benchmark.VEHICLE_COST
COST_HASH = 'c0bdf46c2d1eb8cf7c74474bfc9528b430a053b2a5529ed1702b2fd4339d4b0b'
COST_COMMIT = '946f1772540d07af85b57b0d13cac08a3293b140'
COST_BLOB = 'b9bce33439aa7242840af83680b2ab76b46304ea'
COST_ARTIFACT = 'docs/archives/line30-benchmark-source-epochs/selected-vehicle-cost-946f177254.json'
COST_RECEIPT = 'docs/archives/line30-benchmark-source-epochs/selected-vehicle-cost-manifest.json'
COST_RECEIPT_ID = '4341ff189c625859739253e686a23f4c3c5d69b318e9f5013e26ae0f6295cc73'
COST_ESTIMATE_ID = 'c213eae2c0c90c27d3d418d5aa28b820837385949ba865124dd2218fbc9535dd'
COST_VEHICLE_ID = '756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3'
COST_SELECTION_ID = 'e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803'
COST_SCOPE = (
    'Exact historical selected vehicle cost bytes for the retained line-30 '
    'analytical budget; no current-source evaluator admission'
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


def _retained_cost(root: Path, result: dict) -> None:
    receipt = json.loads(_file(root, COST_RECEIPT, maximum=1024 * 1024).read_bytes())
    if (receipt.get('schema') != 'osr-line30-benchmark-selected-cost-source-epoch/1'
            or receipt.get('receipt_id') != COST_RECEIPT_ID
            or receipt.get('receipt_id') != identity({k: v for k, v in receipt.items() if k != 'receipt_id'})
            or receipt.get('benchmark_manifest_id') != PACKAGE_MANIFEST_ID
            or receipt.get('benchmark_evaluation_id') != EVALUATION_ID
            or receipt.get('source_commit') != COST_COMMIT
            or receipt.get('source_git_blob') != COST_BLOB
            or receipt.get('source_path') != COST_SOURCE
            or receipt.get('source_sha256') != COST_HASH
            or receipt.get('source_artifact') != COST_ARTIFACT
            or receipt.get('files_sha256') != {COST_ARTIFACT: COST_HASH}
            or receipt.get('cost_estimate_id') != COST_ESTIMATE_ID
            or receipt.get('selected_reference_vehicle_candidate_id') != COST_VEHICLE_ID
            or receipt.get('selection_id') != COST_SELECTION_ID
            or receipt.get('scope') != COST_SCOPE
            or any(receipt.get(key) is not False for key in FLAGS)):
        raise ValueError('Line-30 retained selected-cost receipt differs')
    raw = _file(root, COST_ARTIFACT, maximum=1024 * 1024).read_bytes()
    blob = sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    if sha256(raw).hexdigest() != COST_HASH or blob != COST_BLOB:
        raise ValueError('Line-30 retained selected-cost source differs')
    cost = json.loads(raw)
    if (cost.get('cost_estimate_id') != identity({k: v for k, v in cost.items() if k != 'cost_estimate_id'})
            or cost.get('cost_estimate_id') != COST_ESTIMATE_ID
            or cost.get('candidate_id') != COST_VEHICLE_ID
            or cost.get('selection_id') != COST_SELECTION_ID
            or result['source_sha256'].get(COST_SOURCE) != COST_HASH
            or result.get('vehicle_cost_estimate_id') != COST_ESTIMATE_ID
            or result.get('selected_reference_vehicle_candidate_id') != COST_VEHICLE_ID
            or any(cost.get(key) is not False for key in ('physical_accepted', 'engineering_accepted',
                'manufacturing_release', 'operating_release'))):
        raise ValueError('Line-30 retained selected-cost identity differs')


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
    _retained_cost(root, result)

    historical_sources = []
    retained = {SOURCE: SOURCE_HASH, COST_SOURCE: COST_HASH}
    for name, expected in result['source_sha256'].items():
        current = _file(root, name)
        if digest(current) == expected:
            continue
        if retained.get(name) != expected:
            raise ValueError('Line-30 source epoch differs: ' + name)
        historical_sources.append(name)
    if SOURCE not in historical_sources or set(historical_sources) - set(retained):
        raise ValueError('Line-30 historical source inventory differs')
    return dict(verified=True, manifest_id=PACKAGE_MANIFEST_ID,
        evaluation_id=EVALUATION_ID,requirements_id=result['requirements_id'],
        source_epoch='historical',current_source_valid=False,
        source_sha256=result['source_sha256'],
        historical_source_paths=historical_sources,
        retained_cost_receipt_id=COST_RECEIPT_ID, analytical_replay=False,
        native_solver_jobs=0,
        **{key: False for key in FLAGS})


def historical_baseline(root=ROOT):
    """Return only the authenticated retained result for a historical comparison."""
    checked = verify(root)
    root = Path(root).resolve()
    manifest = json.loads(_file(root, PACKAGE + '/manifest.json').read_bytes())
    raw = _file(root, PACKAGE + '/result.json').read_bytes()
    if sha256(raw).hexdigest() != manifest['files']['result.json']:
        raise ValueError('Line-30 retained result changed after verification')
    result = json.loads(raw)
    if result['evaluation_id'] != checked['evaluation_id']:
        raise ValueError('Line-30 retained result identity changed')
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,help='Only the pinned line-30 publication directory is supported')
    args=parser.parse_args(argv)
    print(json.dumps(verify(output=args.output),sort_keys=True))


if __name__=='__main__':main()
