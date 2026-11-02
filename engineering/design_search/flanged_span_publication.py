"""Immutable archival and analytical replay for the flanged-span stage-1 study.

This verifies recorded inputs against current source, selection and mass context,
then re-evaluates the declared beam arithmetic and per-span cost. It does not
execute a native solver, independently measure a bridge, select an alternative,
or qualify the linear model, materials, foundation or manufacturing process.
"""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from math import fsum
import os
from pathlib import Path
import platform
import shutil
import stat
import tempfile

from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded, identity
from . import flanged_span as span

PRODUCER = 'engineering/design_search/flanged_span_publication.py'
OUTPUT = 'docs/design-engine/flanged-span-study'
NAMES = ('baseline', 'thick-web', 'thick-flange')
FLAGS = dict(span.FLAGS)
MAX_JSON = 4 * 1024 * 1024
MAX_TEXT = 1024 * 1024
DISPOSITION = 'Research calculation; no approval or selected reference change'
REPLAY_SCOPE = 'Current-source analytical beam, quantity and per-span cost; not a physical test'
PROVENANCE_SCOPE = 'Supplied original bytes; independent worker/tool attestation not available'


def _pairs(rows):
    result = {}
    for k, v in rows:
        if k in result:
            raise ValueError('Duplicate JSON key')
        result[k] = v
    return result


def _file(path, limit):
    path = Path(path)
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise ValueError('Symlink input or ancestor refused')
    before = path.stat()
    if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
        raise ValueError('Bounded ordinary file required: ' + str(path))
    with path.open('rb') as f:
        opened = os.fstat(f.fileno())
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns):
            raise ValueError('Input changed during opening')
        data = f.read(limit + 1)
        after = os.fstat(f.fileno())
    current = path.stat()
    if len(data) > limit or (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns) or (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns) != (current.st_dev, current.st_ino, current.st_size, current.st_mtime_ns, current.st_ctime_ns):
        raise ValueError('Input changed during read')
    return data


def _json(data):
    try:
        value = json.loads(data, object_pairs_hook=_pairs, parse_constant=lambda v: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError('Malformed JSON') from error
    if not isinstance(value, dict) or encoded(value) != data:
        raise ValueError('Canonical JSON object required')
    return value


def _seal(value, key):
    value[key] = identity(value)
    return value


def _sealed(value, key):
    if value.get(key) != identity({k: v for k, v in value.items() if k != key}):
        raise ValueError('Invalid identity: ' + key)


def _snapshot(state):
    """Read exactly three attempt slots without fabricating missing executions."""
    state = Path(state).absolute()
    if not state.is_dir() or state.is_symlink():
        raise ValueError('Existing unlinked attempt directory required')
    values = {}
    for name in ('run.py', 'execution.log'):
        values[name] = _file(state / name, MAX_TEXT)
    for name in NAMES:
        folder = state / name
        if folder.is_symlink():
            raise ValueError('Unlinked attempt folder required')
        if not folder.exists():
            continue
        if not folder.is_dir() or folder.is_symlink():
            raise ValueError('Unlinked attempt folder required')
        allowed = {'request.json', 'result.json', 'failure.txt'}
        if {p.name for p in folder.iterdir()} - allowed:
            raise ValueError('Unexpected attempt file')
        for item in allowed:
            path = folder / item
            if path.exists() or path.is_symlink():
                values[name + '/' + item] = _file(path, MAX_JSON if item.endswith('.json') else MAX_TEXT)
    return values


def _audit(raw, root, *, replay=True):
    root = Path(root).resolve()
    contexts, summaries, sources = [], [], {}
    for name in NAMES:
        prefix = name + '/'
        request_raw = raw.get(prefix + 'request.json')
        result_raw = raw.get(prefix + 'result.json')
        failure = raw.get(prefix + 'failure.txt')
        if request_raw is None:
            if result_raw is not None or failure is not None:
                raise ValueError('Attempt output without recorded request')
            summaries.append(dict(gauge=name, execution='not-attempted', candidate_id=None, request_id=None, result_id=None))
            continue
        request = _json(request_raw)
        _sealed(request, 'request_id')
        if (set(request) != {'schema', 'candidate', 'context', 'assumptions', 'runtime_budget', 'disposition', 'request_id'}
                or request['schema'] != 'osr-flanged-span-stage1-request/1' or request['disposition'] != DISPOSITION
                or request['runtime_budget'] != dict(address_space_bytes=1073741824, cpu_seconds=240, wall_seconds=300, workers=1)):
            raise ValueError('Request schema, disposition or execution-budget record differs')
        candidate, context, assumptions = request['candidate'], request['context'], request['assumptions']
        if candidate['gauge'] != name:
            raise ValueError('Attempt label and physical candidate differ')
        span._candidate(candidate)
        span._context(context, root)
        if span._spec(assumptions) != assumptions:
            raise ValueError('Invalid declared assumptions')
        contexts.append(context)
        for key, value in context['source_sha256'].items():
            if key in sources and sources[key] != value:
                raise ValueError('Mixed producer/source epochs')
            sources[key] = value
        if result_raw is not None and failure is not None:
            raise ValueError('Attempt cannot be both failed and completed')
        if result_raw is None:
            summaries.append(dict(gauge=name, execution='recorded-failure' if failure is not None else 'interrupted-or-unrecorded',
                candidate_id=candidate['candidate_id'], request_id=request['request_id'], result_id=None))
            continue
        result = _json(result_raw)
        _sealed(result, 'result_id')
        if (set(result) != {'schema','request_id','candidate_id','quantities','analysis','cost','execution','result_id'}
                or result['schema'] != 'osr-flanged-span-stage1-result/1' or result['execution'] != 'completed'
                or result['request_id'] != request['request_id'] or result['candidate_id'] != candidate['candidate_id']):
            raise ValueError('Result source request or candidate identity differs')
        for key in ('quantities','analysis','cost'):
            span._sealed(result[key], 'evaluation_id')
            if result[key]['candidate_id'] != candidate['candidate_id']:
                raise ValueError('Mixed candidate in evaluated record')
            if any(result[key].get(flag) is not False for flag in FLAGS):
                raise ValueError('Research evidence cannot grant promotion or acceptance')
        if (result['analysis']['load_context_id'] != context['context_id']
                or result['analysis']['quantity_evaluation_id'] != result['quantities']['evaluation_id']
                or result['cost']['quantity_evaluation_id'] != result['quantities']['evaluation_id']
                or len(result['analysis']['responses']) != 81 or len(result['analysis']['all_position_model_bounds']) != 27
                or result['analysis']['engineering_screen'] != 'unresolved'
                or result['analysis']['integrated_selection'] is not None
                or result['cost']['whole_system_ranking_allowed'] is not False
                or result['quantities']['complete_installed_mass_kg'] is not None
                or result['cost']['complete_installed_cost_iqd'] is not None
                or result['cost']['lifecycle_cost_iqd'] is not None):
            raise ValueError('Evaluation scope, coverage or nonqualification differs')
        if replay:
            quantities = span.quantities(candidate, assumptions)
            if result['quantities'] != quantities or result['cost'] != span.estimate(candidate, quantities, assumptions):
                raise ValueError('Analytical quantity or scoped production cost replay differs')
            if result['analysis'] != span.evaluate(candidate, context, assumptions, root=root):
                raise ValueError('Declared beam response and load replay differs')
        a, q, cost = result['analysis'], result['quantities'], result['cost']
        summaries.append(dict(gauge=name, execution='completed', candidate_id=candidate['candidate_id'],
            request_id=request['request_id'], result_id=result['result_id'], geometry_id=candidate['geometry_id'],
            quantity_evaluation_id=q['evaluation_id'], analysis_evaluation_id=a['evaluation_id'], cost_evaluation_id=cost['evaluation_id'],
            EI_Nm2=a['EI_Nm2'], accounted_mass_kg_cases=deepcopy(q['accounted_mass_kg_cases']),
            scoped_installed_iqd={k:v['scoped_installed_iqd'] for k,v in cost['cases'].items()},
            factory_person_hours={k:fsum(v['factory_labour_hours'].values()) for k,v in cost['cases'].items()},
            maximum_representative_model_deflection_m=max(max(r['response']['deflection_at_observation_m']) for r in a['responses']),
            maximum_all_position_model_bound_m=max(r['all_position_model_deflection_upper_m'] for r in a['all_position_model_bounds']),
            numerical_validity=a['numerical_validity'], engineering_screen='unresolved', holds=deepcopy(a['holds'])))
    if not contexts:
        raise ValueError('At least one original candidate request required')
    if any(c != contexts[0] for c in contexts):
        raise ValueError('All compared candidates require the same exact selected load context')
    if replay and span.load_context(root) != contexts[0]:
        raise ValueError('Selected vehicle or mass ledger has changed')
    source_file = root / PRODUCER
    source = _file(source_file, MAX_TEXT)
    if sha256(source).hexdigest() != sha256(_file(Path(__file__), MAX_TEXT)).hexdigest():
        raise ValueError('Executing publication source differs from declared root')
    sources[PRODUCER] = sha256(source).hexdigest()
    return summaries, dict(sorted(sources.items())), contexts[0]['context_id']


def _readme(record):
    lines = ['# Flanged-girder 20 m span: analytical research study', '',
        'Three distinct physical steel-girder gauges share the selected vehicle, load and mass scenarios. The declared simply-supported, steel-only beam model assumes symmetric load sharing and continuous full-moment splices; it does not establish their physical behaviour.', '',
        '| Gauge | Execution | Candidate | Maximum representative model deflection (m) | Base scoped installed cost (IQD) | Base factory person-hours |',
        '|---|---|---|---:|---:|---:|']
    for r in record['attempts']:
        if r['execution'] == 'completed':
            lines.append(f"| {r['gauge']} | completed | `{r['candidate_id']}` | {r['maximum_representative_model_deflection_m']:.6g} | {r['scoped_installed_iqd']['base']:.6g} | {r['factory_person_hours']['base']:.6g} |")
        else:
            lines.append(f"| {r['gauge']} | {r['execution']} | {r['candidate_id'] or 'not available'} | — | — | — |")
    lines += ['', 'Results cover per-span Class C estimates only; site, foundations, dedicated plant and lifecycle costs are not completed. The all-position bounds apply only within the stated gross beam model. The research contains no material, buckling, fatigue, connection, transverse distribution or physical acceptance. No whole-system ranking or reference change is made.', '',
        'The request, result, supplied coordinator script and execution log are preserved byte-for-byte. The script and log are supplied provenance, not proof of an independently sandboxed execution or a measured physical structure. The verifier replays the declared analytical calculation from the current selected source inputs; it does not run a native solver.', '']
    return '\n'.join(lines)


def _payload(folder):
    folder = Path(folder)
    files = {}
    for path in sorted(folder.rglob('*')):
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            raise ValueError('Ordinary publication tree required')
        if path.is_file() and path.relative_to(folder).as_posix() != 'manifest.json':
            files[path.relative_to(folder).as_posix()] = sha256(_file(path, MAX_JSON if path.suffix == '.json' else MAX_TEXT)).hexdigest()
    return files


def publish(state, *, root=ROOT, output=None):
    """Create a new immutable destination; never replace a previous packet."""
    root = Path(root).resolve()
    target = Path(output) if output is not None else root / OUTPUT
    target = target.absolute()
    state_path = Path(state).resolve()
    resolved_target = target.resolve()
    if resolved_target == state_path or state_path in resolved_target.parents or resolved_target in state_path.parents:
        raise ValueError('Publication must be separate from original attempt files')
    if target.exists() or target.is_symlink():
        raise ValueError('New publication directory required; preserve existing packet')
    raw = _snapshot(state)
    rows, sources, context_id = _audit(raw, root)
    record = _seal(dict(schema='osr-flanged-span-stage1-publication/1', attempts=rows,
        load_context_id=context_id, source_sha256=sources, integrated_selection=None,
        whole_system_ranking_allowed=False, physical_model_qualified=False,
        replay_scope=REPLAY_SCOPE,
        worker_script_and_log_provenance=PROVENANCE_SCOPE,
        publication_environment=dict(python=platform.python_version(), system=os.uname().sysname,
            release=os.uname().release, machine=os.uname().machine), **FLAGS), 'publication_id')
    target.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.flanged-stage-', dir=target.parent))
    try:
        for name, data in raw.items():
            p = stage / 'original' / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        (stage / 'result.json').write_bytes(encoded(record))
        (stage / 'README.md').write_text(_readme(record))
        manifest = _seal(dict(schema='osr-flanged-span-stage1-manifest/1', publication_id=record['publication_id'],
            source_sha256=sources, files_sha256=_payload(stage), **FLAGS), 'manifest_id')
        (stage / 'manifest.json').write_bytes(encoded(manifest))
        verify(stage, root=root)
        if _snapshot(state) != raw:
            raise ValueError('Original attempt bytes changed during publication')
        target.mkdir()  # Exclusive creation prevents replacing an existing packet.
        try:
            os.rename(stage, target)
        except OSError:
            try: target.rmdir()
            except OSError: pass
            raise
    finally:
        if stage.exists(): shutil.rmtree(stage)
    return manifest


def verify(output=None, *, root=ROOT):
    """Independently replay the published source-bound analytical records."""
    root = Path(root).resolve()
    output = Path(output) if output is not None else root / OUTPUT
    if not output.is_dir() or output.is_symlink():
        raise ValueError('Existing ordinary publication directory required')
    manifest = _json(_file(output / 'manifest.json', MAX_JSON))
    _sealed(manifest, 'manifest_id')
    if (set(manifest) != {'schema','publication_id','source_sha256','files_sha256','manifest_id',*FLAGS}
            or manifest.get('schema') != 'osr-flanged-span-stage1-manifest/1'
            or any(manifest.get(flag) is not False for flag in FLAGS)
            or manifest.get('files_sha256') != _payload(output)):
        raise ValueError('Publication manifest, disposition or payload differs')
    record = _json(_file(output / 'result.json', MAX_JSON))
    _sealed(record, 'publication_id')
    if (set(record) != {'schema','attempts','load_context_id','source_sha256','integrated_selection',
            'whole_system_ranking_allowed','physical_model_qualified','replay_scope',
            'worker_script_and_log_provenance','publication_environment','publication_id',*FLAGS}
            or record.get('schema') != 'osr-flanged-span-stage1-publication/1'
            or record['publication_id'] != manifest['publication_id']
            or any(record.get(flag) is not False for flag in FLAGS)
            or record['integrated_selection'] is not None or record['whole_system_ranking_allowed'] is not False
            or record['physical_model_qualified'] is not False or record['replay_scope'] != REPLAY_SCOPE
            or record['worker_script_and_log_provenance'] != PROVENANCE_SCOPE):
        raise ValueError('Research result identity or nonpromotion differs')
    raw = _snapshot(output / 'original')
    rows, sources, context_id = _audit(raw, root)
    if (record['attempts'] != rows or record['source_sha256'] != sources or manifest['source_sha256'] != sources
            or record['load_context_id'] != context_id or _file(output / 'README.md', MAX_TEXT) != _readme(record).encode()):
        raise ValueError('Replay, producer, context or interpretation differs')
    return dict(verified=True, publication_id=record['publication_id'], manifest_id=manifest['manifest_id'],
        attempts=len(rows), completed=sum(r['execution']=='completed' for r in rows),
        analytical_replay_executed=True, native_solver_executed=False, physical_measurements_verified=False,
        integrated_selection=None, **FLAGS)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    p = commands.add_parser('publish');p.add_argument('--state', type=Path, required=True);p.add_argument('--output', type=Path)
    p = commands.add_parser('verify');p.add_argument('--output', type=Path)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        value = publish(args.state, root=args.root, output=args.output) if args.action == 'publish' else verify(args.output, root=args.root)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(2, str(error) + '\n')
    print(json.dumps(value, sort_keys=True, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
