"""Exact-request reuse for source-bound native result batches."""
from pathlib import Path
import gzip
import json
import shutil
import tempfile

from engineering.station_rail.common import digest, encoded, identity


def _sealed(value):
    return (isinstance(value, dict)
            and value.get('receipt_id') == identity(
                {key: item for key, item in value.items() if key != 'receipt_id'}))


def _same_solver_build(previous, current):
    if not _sealed(previous) or not _sealed(current):
        raise ValueError('Native cache build receipts must be sealed')
    fields = ('source_sha256', 'tools', 'product', 'protocol', 'binary_sha256')
    return all(previous.get(field) == current.get(field) for field in fields)


def _manifest_check(path, *, manifest_files, manifest_prefix, run_name):
    if manifest_files is None:
        return
    relative = f'{manifest_prefix}/{run_name}/{path.parent.name}/{path.name}'
    expected = manifest_files.get(relative)
    if expected is None or digest(path) != expected:
        raise ValueError('Native cache file differs from its source publication manifest: ' + relative)


def _ordinary(path):
    return path.is_file() and not path.is_symlink()


def seed_exact_batch(*, source_runs, target, request, raw_request,
                     previous_build, current_build, current_context,
                     input_hash_field, manifest_files=None,
                     manifest_prefix=None, run_name=None,
                     origin_manifest_id=None):
    """Create a new run receipt for a fully verified, exact prior batch.

    The native bridge hash and run-directory-derived build identity may differ.
    Solver source, compiler tools, product, protocol, binary bytes, canonical
    request, runtime limits and execution environment must match. Both bridge
    hashes are retained in the new receipt. The original receipt remains
    untouched in its source package and is named by the new receipt.
    """
    source_runs = Path(source_runs)
    target = Path(target)
    if not _same_solver_build(previous_build, current_build):
        return None
    previous_build_id = previous_build['receipt_id']
    if (source_runs.is_symlink() or not source_runs.is_dir()
            or target.exists() or target.is_symlink()):
        if target.exists() or target.is_symlink():
            raise ValueError('Native cache target already exists')
        return None

    current_context = dict(current_context)
    if (not isinstance(current_context.get('bridge_sha256'), str)
            or len(current_context['bridge_sha256']) != 64):
        raise ValueError('Current native bridge identity is required')

    for source in sorted(source_runs.iterdir()):
        if source.is_symlink():
            raise ValueError('Native cache source contains a symlink')
        if not source.is_dir():
            continue
        input_path = source / 'input.json.gz'
        if not _ordinary(input_path) or input_path.stat().st_size > 8 * 1024**2:
            continue
        input_bytes = input_path.read_bytes()
        try:
            if gzip.decompress(input_bytes) != raw_request:
                continue
        except (EOFError, OSError):
            continue

        receipt_path = source / 'receipt.json'
        output_path = source / 'output.json.gz'
        execution_path = source / 'execution.json'
        stderr_path = source / 'stderr.log'
        required = (receipt_path, output_path, execution_path, stderr_path)
        if any(not _ordinary(path) for path in required):
            raise ValueError('Exact native cache request lacks its sealed result files')
        receipt = json.loads(receipt_path.read_bytes())
        if not _sealed(receipt):
            raise ValueError('Exact native cache request has an invalid receipt seal')
        if receipt.get('build_receipt_id') != previous_build_id:
            continue
        prior_context = receipt.get('context')
        if not isinstance(prior_context, dict):
            raise ValueError('Exact native cache receipt lacks its execution context')
        if ({key: value for key, value in prior_context.items() if key != 'bridge_sha256'}
                != {key: value for key, value in current_context.items() if key != 'bridge_sha256'}):
            continue
        if ('resources' in receipt
                and receipt['resources'] != current_context.get('resources')):
            continue
        if (receipt.get(input_hash_field) != digest(input_path)
                or receipt.get('output_sha256') != digest(output_path)):
            raise ValueError('Exact native cache request has changed input or output bytes')
        if (receipt.get('request_sha256') is not None
                and receipt['request_sha256'] != identity(request)):
            raise ValueError('Exact native cache request identity differs')
        execution = json.loads(execution_path.read_bytes())
        if (any(execution.get(key) != receipt.get(key) for key in execution)
                or receipt.get('exit_code') != 0 or receipt.get('failure') is not None):
            continue
        if manifest_files is not None:
            for path in (receipt_path, input_path, output_path, execution_path, stderr_path):
                _manifest_check(path, manifest_files=manifest_files,
                    manifest_prefix=manifest_prefix, run_name=run_name)

        temporary = Path(tempfile.mkdtemp(prefix='.' + target.name + '.reuse-',
                                          dir=target.parent))
        try:
            shutil.copyfile(input_path, temporary / 'input.json.gz')
            shutil.copyfile(output_path, temporary / 'output.json.gz')
            shutil.copyfile(execution_path, temporary / 'execution.json')
            shutil.copyfile(stderr_path, temporary / 'stderr.log')
            rebound = dict(receipt)
            origin_receipt_id = rebound['receipt_id']
            rebound.pop('receipt_id')
            rebound['build_receipt_id'] = current_build['receipt_id']
            rebound['context'] = current_context
            rebound['cache_reuse'] = dict(
                schema='osr-exact-native-cache-reuse/1',
                origin_manifest_id=origin_manifest_id,
                origin_receipt_id=origin_receipt_id,
                origin_build_receipt_id=previous_build_id,
                origin_binary_sha256=previous_build['binary_sha256'],
                current_binary_sha256=current_build['binary_sha256'],
                origin_bridge_sha256=prior_context.get('bridge_sha256'),
                current_bridge_sha256=current_context['bridge_sha256'],
                request_sha256=identity(request),
            )
            rebound['receipt_id'] = identity(rebound)
            (temporary / 'receipt.json').write_bytes(encoded(rebound))
            temporary.replace(target)
        except Exception:
            shutil.rmtree(temporary, ignore_errors=True)
            raise
        return rebound
    return None
