"""Remove owned Cargo intermediates after a research run has sealed its evidence.

This is deliberately limited to known per-run target names. Native inputs,
outputs, build logs, receipts and failed attempts are never cleanup candidates.
"""
import os
from pathlib import Path
import shutil
import stat
import fcntl
import json
import time

from engineering.station_rail.common import digest, identity

_TARGETS = frozenset({'native-target', 'native-product-target'})
_CARGO_TAG = b'Signature: 8a477f597d28d172789f06886806bc55\n# This file is a cache directory tag created by cargo.'


def cleanup_cargo_targets(state, targets, evidence, *, apply=True):
    """Delete only Cargo targets owned by *state* after evidence matches hashes.

    The coordinator must hold its run lock and call this before inventorying the
    final manifest. A missing target is harmless on a resumed run. A suspicious
    target or changed evidence fails closed, retaining the entire directory.
    """
    state = Path(state).absolute()
    if any(p.is_symlink() for p in (state,*state.parents)) or not state.is_dir():
        raise ValueError('Ordinary private run directory required for cache cleanup')
    if not isinstance(evidence, dict) or not evidence:
        raise ValueError('Sealed evidence hashes required before cache cleanup')
    for name, expected in evidence.items():
        if not isinstance(name, str) or Path(name).is_absolute() or '..' in Path(name).parts:
            raise ValueError('Relative evidence path required')
        path = state/name
        if (any(p.is_symlink() for p in (path,*[p for p in path.parents if p!=state and state in p.parents]))
                or not path.is_file() or digest(path) != expected):
            raise ValueError('Run evidence changed; compiler cache retained: '+name)
    if not isinstance(targets, (list, tuple)) or len(targets) != len(set(targets)):
        raise ValueError('Distinct owned Cargo targets required')
    candidates = []
    for name in targets:
        path = Path(name)
        if (path.is_absolute() or '..' in path.parts or not path.parts
                or path.name not in _TARGETS):
            raise ValueError('Unrecognised per-run Cargo target')
        target = state/path
        if not target.exists() and not target.is_symlink():
            continue
        if target.is_symlink() or not target.is_dir():
            raise ValueError('Ordinary Cargo target required: '+name)
        marker = target/'CACHEDIR.TAG'
        if marker.is_symlink() or not marker.is_file() or not marker.read_bytes().startswith(_CARGO_TAG):
            raise ValueError('Cargo cache marker required: '+name)
        device = target.stat().st_dev
        for directory, dirs, files in os.walk(target, followlinks=False):
            for entry in [Path(directory), *(Path(directory)/n for n in dirs+files)]:
                info = entry.lstat()
                if (stat.S_ISLNK(info.st_mode) or info.st_dev != device
                        or not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode))):
                    raise ValueError('Cargo target contains an external or special entry: '+str(entry))
        candidates.append(target)
    if apply:
        for target in candidates:
            shutil.rmtree(target)
    return [p.relative_to(state).as_posix() for p in candidates]


def sweep_terminal_runs(runs, *, apply=False, minimum_age_hours=24):
    """Review old terminal station runs and retire their unlisted Cargo caches.

    Never changes an old manifest. Failed or incomplete runs, active run locks,
    and manifests that inventory the target remain untouched.
    """
    runs=Path(runs).absolute()
    if any(p.is_symlink() for p in (runs,*runs.parents)) or not runs.is_dir():
        raise ValueError('Ordinary run-store root required')
    if minimum_age_hours < 0:raise ValueError('Nonnegative cache age required')
    report=[];seen=set();now=time.time()
    for marker in runs.rglob('CACHEDIR.TAG'):
        target=marker.parent
        if target.name not in _TARGETS:continue
        state=target.parent
        if state in seen:continue
        seen.add(state)
        manifest=state/'manifest.json';lock_path=state/'coordinator.lock'
        row={'run':str(state),'targets':[],'status':'held'}
        try:
            if not manifest.is_file() or manifest.is_symlink():
                raise ValueError('No terminal run manifest')
            if now-manifest.stat().st_mtime < minimum_age_hours*3600:
                raise ValueError('Run is younger than the cleanup age')
            m=json.loads(manifest.read_bytes())
            if (m.get('schema') not in ('osr-station-pair-run/1','osr-station-cycle-run/1')
                    or m.get('manifest_id')!=identity({k:v for k,v in m.items() if k!='manifest_id'})):
                raise ValueError('Unsupported or unsealed run manifest')
            if not isinstance(m.get('files_sha256'),dict) or not m['files_sha256']:
                raise ValueError('Run manifest has no evidence inventory')
            if any(Path(n).parts[0] in _TARGETS for n in m['files_sha256']):
                raise ValueError('Manifest inventories the compiler target')
            if not lock_path.is_file() or lock_path.is_symlink():
                raise ValueError('Ordinary coordinator lock required')
            names=[p.name for p in (state/'native-target',state/'native-product-target')
                   if p.exists() or p.is_symlink()]
            evidence=dict(m['files_sha256'])
            for n in ('native-build.json','native-build.log'):
                p=state/n
                if p.is_symlink() or not p.is_file():raise ValueError('Ordinary build evidence required')
                evidence[n]=digest(p)
            if 'native-product-target' in names:
                p=state/'cycle-build.json'
                if p.is_symlink() or not p.is_file():raise ValueError('Ordinary cycle build evidence required')
                evidence['cycle-build.json']=digest(p)
            with lock_path.open('rb') as lock:
                try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
                except BlockingIOError:raise ValueError('Run is active') from None
                row['targets']=cleanup_cargo_targets(state,names,evidence,apply=apply)
            row['status']='removed' if apply else 'eligible'
        except (OSError,ValueError,KeyError,TypeError) as exc:
            row['reason']=str(exc)
        report.append(row)
    return {'schema':'osr-terminal-run-cache-sweep/1','mode':'apply' if apply else 'preview',
            'eligible_or_removed':sum(r['status'] in ('eligible','removed') for r in report),
            'held':sum(r['status']=='held' for r in report),'runs':report}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description='Guarded cleanup of terminal run Cargo caches')
    parser.add_argument('--runs',type=Path,required=True)
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--minimum-age-hours',type=float,default=24)
    args=parser.parse_args()
    print(json.dumps(sweep_terminal_runs(args.runs,apply=args.apply,
        minimum_age_hours=args.minimum_age_hours),sort_keys=True,indent=2))
