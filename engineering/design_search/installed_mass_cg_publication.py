"""Publish and replay the selected-car conditional support sensitivity.

The three worker epochs are retained independently; their recorded runtime is
not independently attested. This publication does not qualify a vehicle.
"""
from __future__ import annotations

import argparse
import ctypes
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile

from engineering.station_rail.common import digest, encoded, identity
from . import installed_mass_cg as calculation

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path('docs/design-engine/installed-mass-support')
PRODUCER = 'engineering/design_search/installed_mass_cg_publication.py'
CALCULATOR = 'engineering/design_search/installed_mass_cg.py'
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False)
EPOCHS = (
    ('v1', 'bdbd9bd017fa5a3854403939b704d19eff338096fbb80b33516245bc1617e6d5',
     'af9c5f6c39da8892615e409ef6dc79c960a52f6e',
     '96142644c1df209fa6b523b6ec4bd8b2687c85cf9fd02bcaf78d89f1703c0978',
     'superseded: account-level reconciliation and source provenance required'),
    ('v2', '68bc5681113cc307bc622b4bb03508238bd7bc93f4013ef68e05d314af2422b6',
     '0b22f400f64d426531322ab04e328a16ac1d924e',
     '23a2c242357fe6e1c849e6b0fb1e6813c515ce70709347cb6406d1e2aa9377b0',
     'superseded: provenance wording corrected'),
    ('v3', '1e47ab04411d93e86a4cc404b2e33a278f6ac0e79249fb6c7d85b06bf8c3dfe7',
     '0886c73c89c8578d3ad220183f8bd9d6717b0efb',
     'a7f173254aff59ae70f1698eaedfb64cac42d9231b626757c96f30985ca0af7f',
     'completed analytical sensitivity; physical requirements open'),
)


def _ordinary(path, *, directory=True):
    path = Path(os.path.abspath(path))
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise ValueError('Symlink path or ancestor is not permitted')
    if directory and not path.is_dir():
        raise ValueError('An existing ordinary directory is required')
    return path


def _rename_noreplace(source, destination):
    """Linux atomic directory handoff that cannot replace an existing path."""
    libc = ctypes.CDLL(None, use_errno=True)
    try:
        rename = libc.renameat2
    except AttributeError as exc:
        raise OSError('Atomic no-replace publication is unavailable') from exc
    rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    rename.restype = ctypes.c_int
    if rename(-100, os.fsencode(source), -100, os.fsencode(destination), 1) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), str(destination))


def _file(path):
    path = _ordinary(path, directory=False)
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError('An ordinary regular file is required')
    return path


def _remove_staging(path):
    # Worker evidence is deliberately read-only; only make our failed staging
    # directories writable before deleting them, never the source packages.
    for p in path.rglob('*'):
        if not p.is_symlink() and p.is_dir():
            p.chmod(p.stat().st_mode | stat.S_IWUSR)
    shutil.rmtree(path)


def _files(folder):
    folder = _ordinary(folder)
    out = {}
    for p in folder.rglob('*'):
        mode = p.lstat().st_mode
        if not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
            raise ValueError('Only regular files and directories are permitted in retained packets')
        if stat.S_ISREG(mode) and p.relative_to(folder).as_posix() != 'run-manifest.json':
            out[p.relative_to(folder).as_posix()] = digest(p)
    return out


def _worker(folder, epoch):
    name, package_id, commit, evaluation_id, disposition = epoch
    folder = _ordinary(folder)
    manifest_path = _file(folder/'run-manifest.json')
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    if (manifest.get('schema') != 'osr-selected-mass-support-worker-package/1'
            or manifest.get('package_id') != package_id
            or identity({k:v for k,v in manifest.items() if k != 'package_id'}) != package_id
            or manifest.get('source_commit') != commit
            or manifest.get('evaluation_id') != evaluation_id
            or _files(folder) != manifest.get('files_sha256')):
        raise ValueError('Worker package differs from pinned '+name+' epoch')
    original = (folder/'outputs/python313-result.json').read_bytes()
    if original != (folder/'outputs/python312-result.json').read_bytes():
        raise ValueError('Recorded Python outputs differ in '+name)
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
    replay = subprocess.run([sys.executable, '-B', str(folder/'inputs'/CALCULATOR)],
        cwd=folder/'inputs', env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=60, check=True).stdout
    if replay != original or json.loads(original).get('evaluation_id') != evaluation_id:
        raise ValueError('Worker source replay differs in '+name)
    if _file(manifest_path).read_bytes() != manifest_bytes or _files(folder) != manifest['files_sha256']:
        raise ValueError('Worker package changed during replay in '+name)
    return dict(epoch=name, package_id=package_id, source_commit=commit,
                evaluation_id=evaluation_id, disposition=disposition)


def _source_map(root):
    root = Path(root)
    names = [PRODUCER, CALCULATOR, *calculation.INPUT_SHA256]
    sources = {name:digest(_file(root/name)) for name in sorted(names)}
    if digest(_file(__file__)) != sources[PRODUCER]:
        raise ValueError('Executing publisher differs from declared source tree')
    return sources


def _publication_payload(folder):
    entries = sorted(folder.rglob('*'))
    if any(not (stat.S_ISREG(p.lstat().st_mode) or stat.S_ISDIR(p.lstat().st_mode)) for p in entries):
        raise ValueError('Only regular files and directories are permitted in publication payload')
    return {p.relative_to(folder).as_posix():digest(p) for p in entries
        if stat.S_ISREG(p.lstat().st_mode) and p.relative_to(folder).as_posix() != 'manifest.json'}


def _readme(result):
    rows = []
    for c in result['cases']:
        lo, hi = c['x_cg_interval_m']
        rlo, rhi = c['left_bogie_force_interval_N']
        rows.append(f"| {c['case']} | {c['scenario_accounted_mass_kg']:.2f} | "
                    f"{lo:.3f} to {hi:.3f} | {rlo/1000:.2f} to {rhi/1000:.2f} |")
    return ('# Conditional vehicle mass and support sensitivity\n\n'
        'This selected-car calculation uses pinned located geometry and replaces each named residual account once. '
        'Every residual centroid is independently assumed to lie within the 17 m car body; these synthetic inputs '
        'are not verified installation envelopes or guaranteed physical bounds.\n\n'
        '| Mass case | Accounted mass per car (kg) | Assumed longitudinal CG interval (m) | Left bogie reaction interval (kN) |\n'
        '|---|---:|---:|---:|\n'+'\n'.join(rows)+'\n\n'
        'The calculation assumes two vertical point supports and rigid static equilibrium. '
        'Account overlap, actual installed mass and CG, load sharing among axles, suspension behaviour and '
        'physical qualification remain unknown. Negative reactions are reported, not clipped. '
        'These conditional results do not change the selected railway or authorize manufacture or operation.\n\n'
        'Original worker packages and independent replay preserve v1 and v2 as superseded, and v3 as '
        'the current analytical sensitivity. Recorded worker resource limits and runtimes are not independently '
        'attested; no filesystem or network sandbox was enforced. In v2 and v3, the '
        '`source-base-revision.txt` files identify the preparation predecessor; the recorded source commits '
        'were instead based on `dad8c4bedb2361d3e621e9def312273167279027`, as stated in their manifests.\n')


def publish(state, output=OUTPUT, *, root=ROOT):
    root = _ordinary(root); state = _ordinary(state); output = _ordinary(root/output, directory=False)
    if output.exists():
        raise ValueError('Publish to a fresh output directory')
    sources = _source_map(root)
    workers = [_worker(state/name, epoch) for epoch in EPOCHS for name in [epoch[0]]]
    result = calculation.evaluate(root=root)
    original = json.loads((state/'v3/outputs/python313-result.json').read_bytes())
    if result != original or result['evaluation_id'] != EPOCHS[-1][3]:
        raise ValueError('Current replay differs from pinned final worker')
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix='.mass-support-', dir=output.parent))
    try:
        for epoch in EPOCHS:
            shutil.copytree(state/epoch[0], temporary/'original'/epoch[0])
        (temporary/'result.json').write_bytes(encoded(result))
        (temporary/'README.md').write_text(_readme(result))
        payload = {p.relative_to(temporary).as_posix():digest(p)
            for p in sorted(temporary.rglob('*')) if p.is_file()}
        manifest = dict(schema='osr-installed-mass-support-publication/1',
            candidate_id=calculation.CANDIDATE_ID, selection_id=calculation.SELECTION_ID,
            source_sha256=sources, files_sha256=payload, worker_epochs=workers,
            evaluation_id=result['evaluation_id'], configuration_adopted=False, **FLAGS)
        manifest['manifest_id'] = identity(manifest)
        (temporary/'manifest.json').write_bytes(encoded(manifest))
        verify(temporary, root=root, expected_manifest_id=manifest['manifest_id'])
        if (_source_map(root) != sources
                or [_worker(state/epoch[0], epoch) for epoch in EPOCHS] != workers
                or _publication_payload(temporary) != payload
                or _file(temporary/'manifest.json').read_bytes() != encoded(manifest)):
            raise ValueError('Publication sources or original workers changed during replay')
        _rename_noreplace(temporary, output)
    finally:
        if temporary.exists(): _remove_staging(temporary)
    return manifest['manifest_id']


def verify(folder=OUTPUT, *, root=ROOT, expected_manifest_id):
    root = _ordinary(root); folder = _ordinary(root/folder)
    manifest_path = _file(folder/'manifest.json')
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    if (manifest.get('schema') != 'osr-installed-mass-support-publication/1'
            or manifest.get('manifest_id') != expected_manifest_id
            or identity({k:v for k,v in manifest.items() if k != 'manifest_id'}) != expected_manifest_id
            or any(manifest.get(k) is not v for k,v in FLAGS.items())
            or manifest.get('configuration_adopted') is not False
            or manifest.get('candidate_id') != calculation.CANDIDATE_ID
            or manifest.get('selection_id') != calculation.SELECTION_ID
            or manifest.get('source_sha256') != _source_map(root)):
        raise ValueError('Pinned publication identity, sources or disposition differs')
    payload = _publication_payload(folder)
    if payload != manifest.get('files_sha256'):
        raise ValueError('Publication payload differs')
    workers = [_worker(folder/'original'/epoch[0], epoch) for epoch in EPOCHS]
    result = calculation.evaluate(root=root)
    if (workers != manifest.get('worker_epochs') or result['evaluation_id'] != EPOCHS[-1][3]
            or result != json.loads((folder/'result.json').read_bytes())
            or _readme(result) != (folder/'README.md').read_text()
            or _source_map(root) != manifest['source_sha256']
            or _file(manifest_path).read_bytes() != manifest_bytes
            or _publication_payload(folder) != payload):
        raise ValueError('Publication replay or source epoch differs')
    return dict(verified=True, manifest_id=expected_manifest_id,
                evaluation_id=result['evaluation_id'], **FLAGS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    create = sub.add_parser('publish'); create.add_argument('--state', required=True, type=Path)
    check = sub.add_parser('verify'); check.add_argument('--expected-manifest-id', required=True)
    args = parser.parse_args()
    result = publish(args.state) if args.action == 'publish' else verify(expected_manifest_id=args.expected_manifest_id)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__': main()
