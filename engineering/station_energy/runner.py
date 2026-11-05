"""Source-bound, bounded batch execution of the Rust station-energy screen.

The receipt checks cooperative source/tool/binary consistency. It is not an
authenticated measurement, signed provenance or OS-enforced isolation.
"""
from collections import Counter
import fcntl
import json
import os
from pathlib import Path
import tempfile
import time

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from engineering.design_search import native_search as bridge

CRATE = 'crates/osr-station-energy'
TARGET = 'build/station-energy-target'
PRODUCER = 'engineering/station_energy/runner.py'
REQUEST_SCHEMA = 'osr-station-energy-request/1'
RESULT_SCHEMA = 'osr-station-energy-result/1'
BUILD_COMMAND = ['cargo', 'build', '--locked', '--release', '-p', 'osr-station-energy']
MAX_REQUEST_BYTES = 8 * 1024**2
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    operating_release=False, selected_reference_changed=False)


def sources(root=ROOT):
    root = Path(root)
    names = ['Cargo.toml', 'Cargo.lock', PRODUCER,
        'engineering/station_energy/examples.py',
        'engineering/station_energy/__main__.py',
        bridge.PRODUCER, 'engineering/station_rail/common.py']
    names.extend(n for n in ('rust-toolchain.toml', 'rust-toolchain',
        '.cargo/config', '.cargo/config.toml') if (root/n).exists())
    crate = root/CRATE
    if crate.is_symlink() or not crate.is_dir():
        raise ValueError('Regular station-energy crate required')
    for directory, directories, files in os.walk(crate, followlinks=False):
        if any((Path(directory)/n).is_symlink() for n in directories):
            raise ValueError('Ordinary Rust source directories required')
        names.extend((Path(directory)/n).relative_to(root).as_posix()
            for n in files if Path(n).suffix in ('.rs', '.toml'))
    return {n: digest(bridge._regular(root/n)) for n in sorted(set(names))}


def _write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.energy-', delete=False) as file:
        temporary = Path(file.name)
        file.write(encoded(value))
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def build(root=ROOT):
    root = Path(root).resolve()
    target = root/TARGET
    if target.is_symlink():
        raise ValueError('Ordinary Rust build directory required')
    target.mkdir(parents=True, exist_ok=True)
    lock_path = target/'build.lock'
    if lock_path.exists():
        bridge._regular(lock_path)
    with lock_path.open('a+b') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        before, tools = sources(root), bridge._tools()
        environment = dict(os.environ, CARGO_TARGET_DIR=str(target), CARGO_BUILD_JOBS='2')
        bridge._run(BUILD_COMMAND, cwd=root, env=environment, timeout=180)
        if sources(root) != before or bridge._tools() != tools:
            raise ValueError('Station-energy sources or toolchain changed during build')
        binary = bridge._regular(target/'release/osr-station-energy')
        receipt = dict(schema='osr-station-energy-build/1', source_sha256=before,
            tool_versions=tools, build_command=BUILD_COMMAND, binary_sha256=digest(binary))
        receipt['receipt_id'] = identity(receipt)
        _write(binary.with_suffix('.receipt.json'), receipt)
        return receipt


def _kernel(root):
    binary = Path(root)/TARGET/'release/osr-station-energy'
    receipt = bridge._parse(bridge._read(binary.with_suffix('.receipt.json')))
    if (receipt.get('schema') != 'osr-station-energy-build/1'
        or receipt.get('receipt_id') != identity({k:v for k,v in receipt.items() if k != 'receipt_id'})
        or receipt.get('source_sha256') != sources(root)
        or receipt.get('tool_versions') != bridge._tools()
        or receipt.get('build_command') != BUILD_COMMAND
        or receipt.get('binary_sha256') != digest(bridge._regular(binary))):
        raise ValueError('Station-energy build differs; explicitly rebuild the kernel')
    return binary, receipt


def calculate(request, root=ROOT):
    root = Path(root).resolve()
    raw = encoded(request)
    if len(raw) > MAX_REQUEST_BYTES:
        raise ValueError('Station-energy request exceeds 8 MiB budget')
    if (not isinstance(request, dict) or set(request) != {'schema', 'cases'}
        or request['schema'] != REQUEST_SCHEMA or not isinstance(request['cases'], list)
        or not 1 <= len(request['cases']) <= 10000):
        raise ValueError('Explicit bounded station-energy request required')
    ids = [r.get('id') for r in request['cases'] if isinstance(r, dict)]
    if (len(ids) != len(request['cases']) or any(not isinstance(i,str) or not i.strip() for i in ids)
        or len(ids) != len(set(ids))):
        raise ValueError('Unique nonempty case identities required')
    binary, receipt = _kernel(root)
    result = bridge._parse(bridge._run([str(binary)], raw, cwd=root, timeout=30))
    if (result.get('schema') != RESULT_SCHEMA
        or [r.get('id') for r in result.get('cases', [])] != ids
        or any(r.get(k) is not False for r in result['cases'] for k in FLAGS)
        or any(r.get('execution') != 'complete' for r in result['cases'])):
        raise ValueError('Rust station-energy result inventory or disposition differs')
    if _kernel(root)[1] != receipt:
        raise ValueError('Station-energy execution sources or binary changed')
    return result, receipt


def summary(request, result):
    counts = Counter(r['necessary_bounds'] for r in result['cases'])
    rows = []
    for inputs, value in zip(request['cases'], result['cases'], strict=True):
        rows.append(dict(id=value['id'], target_speed_kmh=inputs['target_speed_m_s']*3.6,
            capture_speed_m_s=inputs['capture_speed_m_s'],
            booster_offset_m=inputs['booster_offset_m'],
            booster_active_distance_m=inputs['booster_length_m'],
            ideal_launch_speed_m_s=value['motion']['ideal_launch_speed_m_s'],
            delivered_recovery_j=value['storage']['delivered_from_new_capture_j'],
            required_peak_mechanical_power_w=value['booster']['peak_mechanical_power_w'],
            necessary_bounds=value['necessary_bounds'], failures=value['failures'],
            unknowns=value['unknowns']))
    return dict(schema='osr-station-energy-summary/1', cases=len(rows),
        necessary_bound_counts=dict(sorted(counts.items())),
        physical_candidate_id=None, preferred_architecture=None, preferred_speed_kmh=None,
        speed_is_design_variable=True, outline_complete=False,
        cost=None, cost_status='Requires mechanism-specific quantity and lifecycle model',
        model_scope='Ideal constant-acceleration envelopes, not contact dynamics or a complete journey',
        installed_powered_length_proven=False, results=rows, **FLAGS)


def run(output, request, root=ROOT):
    output = Path(output)
    if output.exists():
        raise ValueError('A fresh immutable station-energy execution directory is required')
    started = time.monotonic()
    result, receipt = calculate(request, root)
    value = dict(schema='osr-station-energy-evaluation/1', request_id=identity(request),
        build_receipt_id=receipt['receipt_id'], source_sha256=sources(root),
        result=result, summary=summary(request, result), **FLAGS)
    value['evaluation_id'] = identity(value)
    output.mkdir(parents=True)
    for name, record in (('request.json', request), ('result.json', value),
                         ('summary.json', value['summary']), ('build-receipt.json', receipt)):
        _write(output/name, record)
    manifest = dict(schema='osr-station-energy-manifest/1',
        evaluation_id=value['evaluation_id'], source_sha256=value['source_sha256'],
        files_sha256={n:digest(output/n) for n in ('request.json', 'result.json',
            'summary.json', 'build-receipt.json')}, **FLAGS)
    manifest['manifest_id'] = identity(manifest)
    _write(output/'manifest.json', manifest)
    _write(output/'performance.json', dict(wall_seconds=time.monotonic()-started,
        cases=len(result['cases']), rust_invocations=1,
        scope='Whole bounded invocation, includes source/tool/binary checks'))
    return manifest


def verify(output, root=ROOT):
    """Read-only payload/source checks and fresh deterministic kernel replay."""
    output = Path(output)
    manifest = bridge._parse(bridge._read(output/'manifest.json'))
    if (manifest.get('schema') != 'osr-station-energy-manifest/1'
        or manifest.get('manifest_id') != identity({k:v for k,v in manifest.items() if k != 'manifest_id'})
        or manifest.get('source_sha256') != sources(root)
        or any(manifest.get(k) is not False for k in FLAGS)):
        raise ValueError('Station-energy manifest source or disposition differs')
    expected = {'request.json', 'result.json', 'summary.json', 'build-receipt.json'}
    if set(manifest.get('files_sha256', {})) != expected:
        raise ValueError('Station-energy payload inventory differs')
    for name, sha in manifest['files_sha256'].items():
        if digest(bridge._regular(output/name)) != sha:
            raise ValueError('Station-energy artifact differs: '+name)
    request = bridge._parse(bridge._read(output/'request.json'))
    value = bridge._parse(bridge._read(output/'result.json'))
    result, receipt = calculate(request, root)
    expected_value = dict(schema='osr-station-energy-evaluation/1', request_id=identity(request),
        build_receipt_id=receipt['receipt_id'], source_sha256=sources(root),
        result=result, summary=summary(request, result), **FLAGS)
    expected_value['evaluation_id'] = identity(expected_value)
    if (value != expected_value or manifest['evaluation_id'] != value['evaluation_id']
        or bridge._parse(bridge._read(output/'summary.json')) != value['summary']
        or bridge._parse(bridge._read(output/'build-receipt.json')) != receipt):
        raise ValueError('Station-energy replay differs')
    return manifest
