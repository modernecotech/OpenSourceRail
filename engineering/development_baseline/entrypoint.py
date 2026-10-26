"""Repository front doors for the explicitly selected development design.

Historical calculations are available through the separate ``legacy`` namespace.
No command substitutes their mass, operating assumptions or qualification state.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
from hashlib import sha256
import importlib
import json
from pathlib import Path
import subprocess
import sys

from . import FLAGS, INPUT, OUTPUT, ROOT
from . import selection

IDS = ('candidate_id', 'body_candidate_id', 'support_component_id', 'propulsion_component_id')


class CurrentUnavailable(ValueError):
    """Missing, stale or incompatible evidence must remain an explicit hold."""


def checked_path(root, relative):
    root = Path(root).resolve()
    path = Path(relative)
    if path.is_absolute() or not path.parts or any(p in ('..', '') for p in path.parts):
        raise CurrentUnavailable('Expected an ordinary repository-relative path')
    target = root / path
    for part in (target, *target.parents):
        if part == root:
            break
        if part.is_symlink():
            raise CurrentUnavailable('Symlinks are not evidence paths: ' + str(relative))
    if not target.resolve().is_relative_to(root):
        raise CurrentUnavailable('Evidence path escapes repository')
    return target


def stamp(path):
    st = path.stat()
    return st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns


@lru_cache(maxsize=8192)
def _digest(path, signature):
    h = sha256()
    with Path(path).open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            h.update(chunk)
    if stamp(Path(path)) != signature:
        raise CurrentUnavailable('Evidence changed while reading: ' + path)
    return h.hexdigest()


def digest(path):
    path = Path(path)
    return _digest(str(path), stamp(path))


@lru_cache(maxsize=8)
def _selected(root, signatures):
    value = selection.load(Path(root))
    # load() already checks publication bytes and identities; the stamps keep
    # repeated read-only requests cheap while invalidating edits immediately.
    if _selection_stamps(Path(root)) != signatures:
        raise CurrentUnavailable('Selection changed while reading')
    return value


def _selection_stamps(root):
    import tomllib
    selector = checked_path(root, INPUT)
    config = tomllib.loads(selector.read_text())
    if config.get('family') != 'wheel_rail_station_lim':
        raise CurrentUnavailable('The current front door requires the explicit v0.6 wheel-supported selector')
    # Physical definitions are generated from the selected source. A running
    # Workbench must invalidate its cached selection when those producers change,
    # including a rebuild that leaves the selector TOML unchanged.
    paths = [INPUT, config['source_brief']]
    paths += [p.relative_to(root).as_posix() for p in
              sorted((root / 'engineering/station_rail').glob('*.py'))]
    return tuple((p, stamp(checked_path(root, p))) for p in sorted(set(paths)))


def selected(root=ROOT):
    root = Path(root).resolve()
    return _selected(str(root), _selection_stamps(root))


def check_identity(value, baseline):
    expected = baseline['vehicle']
    if value.get('selection_id') != baseline['selection_id']:
        raise CurrentUnavailable('Current packet uses a different selection')
    for key in IDS:
        if value.get(key) != expected[key]:
            raise CurrentUnavailable('Current packet uses a different ' + key)
    if value.get('development_default') is not True:
        raise CurrentUnavailable('Current packet is not the selected development default')
    # Every current packet carries all dispositions explicitly. Execution and
    # adoption never confer engineering/manufacturing/operating acceptance.
    for key, expected_value in FLAGS.items():
        if value.get(key) is not expected_value:
            raise CurrentUnavailable('Unsupported acceptance disposition: ' + key)


def read_packet(root=ROOT, output=OUTPUT):
    root = Path(root).resolve()
    baseline = selected(root)
    directory = checked_path(root, output)
    manifest_path = checked_path(root, str(Path(output) / 'manifest.json'))
    if not manifest_path.is_file():
        raise CurrentUnavailable('Current publication is missing; run ./osr build')
    manifest = json.loads(manifest_path.read_text())
    check_identity(manifest, baseline)
    bindings = manifest.get('files_sha256', {})
    if 'summary.json' not in bindings:
        raise CurrentUnavailable('Current summary has no publication binding')
    for relative, expected in bindings.items():
        path = checked_path(root, str(Path(output) / relative))
        if not path.is_file() or digest(path) != expected:
            raise CurrentUnavailable('Current output is missing or modified: ' + relative)
    sources = manifest.get('source_sha256')
    if not isinstance(sources, dict) or not sources:
        raise CurrentUnavailable('Current publication has no source bindings')
    for relative, expected in sources.items():
        path = checked_path(root, relative)
        if not path.is_file() or digest(path) != expected:
            raise CurrentUnavailable('Current source changed: ' + relative)
    summary_bytes = (directory / 'summary.json').read_bytes()
    if sha256(summary_bytes).hexdigest() != bindings['summary.json']:
        raise CurrentUnavailable('Current summary changed while reading')
    result = json.loads(summary_bytes)
    check_identity(result, baseline)
    return result, manifest


def status(root=ROOT):
    baseline = selected(root)
    config = baseline['selection']
    vehicle = baseline['vehicle']
    result = dict(schema='osr-default-entrypoint/1', selection_id=baseline['selection_id'],
                  development_default=True, selection_revision=config['revision'],
                  family=config['family'], vehicle=config['vehicle'],
                  service=config['service'], mass=vehicle['mass'],
                  network_proposal_id=config['network_proposal_id'],
                  publication_path=OUTPUT, **{key: vehicle[key] for key in IDS}, **FLAGS)
    try:
        result['publication'], _ = read_packet(root)
        result['publication_state'] = 'current'
    except (OSError, ValueError, KeyError) as exc:
        result['publication_state'] = 'hold'
        result['hold_reason'] = str(exc)
    return result


def emit(value):
    print(json.dumps(value, indent=2, sort_keys=True, allow_nan=False))


def hold(root, action, reason):
    value = status(root)
    value.update(execution='held', requested_action=action, reason=reason)
    emit(value)
    return 3


def _module(name):
    return importlib.import_module('engineering.development_baseline.' + name)


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(root), help=argparse.SUPPRESS)
    parser.add_argument('command', nargs='?', default='status')
    parser.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    command, rest = args.command, args.arguments
    # design/infrastructure are aliases, including their own status default.
    if command in ('design', 'infrastructure'):
        command, rest = (rest[0], rest[1:]) if rest else ('status', [])
    try:
        if command == 'legacy':
            return _module('legacy').main(rest, root=root)
        if command in ('status', 'readiness'):
            if rest and rest != ['--json']:
                return hold(root, command, 'Unsupported current status options')
            emit(status(root))
            return 0
        if command in ('build', 'run', 'cycle', 'publish', 'verify', 'check'):
            allowed = {'--force'} if command in ('build', 'run', 'cycle') else set()
            if set(rest) - allowed:
                return hold(root, command, 'Unsupported current command options')
            module = _module('publication')
            if command in ('build', 'run', 'cycle'):
                result = module.build(root=root, force='--force' in rest)
            elif command == 'publish':
                result = module.publish(root=root, output=root / OUTPUT)
            else:
                result = module.verify(root=root, output=root / OUTPUT)
            emit(result)
            return 0
        if command == 'release-check':
            return hold(root, command, 'Development adoption is not a manufacturing or operating release; physical qualification remains open')
        if command == 'book':
            if rest not in ([], ['--check']):
                return hold(root, command, 'Use ./osr book [--check] for the selected reader')
            emit(_module('book').build(root=root, output=root / 'OpenSourceRail-Book.pdf', check=bool(rest)))
            return 0
        if command in ('catalogue', 'capabilities'):
            if rest and rest not in (['status'], ['--json']):
                return hold(root, command, 'Current catalogue supports read-only status; use ./osr build to regenerate selected city packages')
            emit(_module('cities').read_catalogue(root=root))
            return 0
        if command in ('city', 'sim'):
            slug = rest[0] if rest else 'baghdad'
            if len(rest) > 1:
                return hold(root, command, 'Only a selected city slug is supported')
            module = _module('cities')
            # Both are the same explicitly analytical selected-city evaluator.
            # Neither command is a native dynamic or operational qualification.
            result = module.publish_city(slug, root=root) if command == 'city' else module.evaluate_city(slug, root=root)
            emit(result)
            return 3 if result.get('execution') == 'held' else 0
        if command == 'twin' and rest and rest[0] in ('compile', 'export'):
            baseline = selected(root)
            if len(rest) > 2 or (len(rest) == 2 and rest[1] != baseline['vehicle']['candidate_id']):
                return hold(root, 'twin ' + ' '.join(rest),
                            'Current twin exports require the exact selected physical candidate. Run ./osr build to regenerate them.')
            verification = _module('publication').verify(root=root, output=root / OUTPUT)
            read_packet(root)
            directory = checked_path(root, OUTPUT + '/exports')
            manifest = json.loads((directory / 'manifest.json').read_bytes())
            for key in IDS:
                if manifest.get(key) != baseline['vehicle'][key]:
                    raise CurrentUnavailable('Current twin uses a different ' + key)
            if manifest.get('selection_id') != baseline['selection_id']:
                raise CurrentUnavailable('Current twin uses a different selection')
            for key, value in FLAGS.items():
                if manifest.get(key) is not value:
                    raise CurrentUnavailable('Unsupported twin qualification disposition: ' + key)
            artifacts = []
            for name, expected in manifest['files_sha256'].items():
                path = checked_path(root, OUTPUT + '/exports/' + name)
                if digest(path) != expected:
                    raise CurrentUnavailable('Current twin artifact changed: ' + name)
                artifacts.append(str(path.relative_to(root)))
            emit(dict(schema='osr-current-twin-entrypoint/1', execution='verified-published-export',
                      action='read-only; ./osr build regenerates the selected exports',
                      selection_id=baseline['selection_id'],
                      **{key: baseline['vehicle'][key] for key in IDS},
                      development_default=True, manifest=manifest,
                      artifacts=artifacts, verification=verification, **FLAGS))
            return 0
        if command in ('trip', 'twin', 'plan', 'planning'):
            action = rest[0] if rest else 'status'
            if action in ('status', 'cases', 'catalogue', 'list'):
                emit(status(root))
                return 0
            if command in ('plan', 'planning') and action in ('serve', 'open'):
                return _module('server').main(rest[1:], root=root)
            return hold(root, command + ' ' + ' '.join(rest),
                        'This current-design action has no verified candidate-bound adapter. See ./osr status for actual gates; historical methods use ./osr legacy')
        if command == 'workbench':
            return _module('server').main(rest, root=root)
        if command == 'test':
            if rest:
                return hold(root, command, 'Current tests take no extra arguments')
            subprocess.run([sys.executable, '-m', 'pytest', '-q', '--import-mode=importlib',
                            str(Path(__file__).parent / 'tests'),
                            str(root / 'engineering/station_rail/tests')], cwd=root, check=True)
            emit(_module('publication').verify(root=root, output=root / OUTPUT))
            subprocess.run(['node', str(root / 'tools/automation/tests/verify-development-baseline.mjs')], cwd=root, check=True)
            return 0
        return hold(root, command, 'Unsupported current-design command; use ./osr --help or ./osr legacy for retained methods')
    except (OSError, ValueError, KeyError, ImportError, subprocess.CalledProcessError) as exc:
        emit(dict(schema='osr-default-entrypoint-error/1', execution='held',
                  requested_action=command, reason=str(exc), development_default=True, **FLAGS))
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
