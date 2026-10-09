"""Append-only candidates/runs, bounded native workers and rebuildable reports."""
from __future__ import annotations

import csv
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from osr_mech.civil.exploration import geometry, section_svg
from .contracts import ROOT, HERE, dependencies, encoded, identity, load, sha, validate, validate_study


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.name == 'manifest.json' and (path.parent/'ledger.jsonl').exists():
        value['ledger_sha256'] = sha(path.parent/'ledger.jsonl')
    path.write_bytes(encoded(value))


def candidate(value, study, parents=None, reason=None):
    definition = {k: value[k] for k in ('deck', 'pier')}
    result = dict(schema='osr-civil-candidate/1', parents=list(value.get('parents', []) if parents is None else parents), definition=definition,
                  modification_reason=reason or value.get('modification_reason', 'registered control or research seed'),
                  material=study['material'], mass_allowances=study['mass_allowances'],
                  foundation=study['foundation'], geometry_sha256=identity(geometry(definition)))
    result['id'] = identity({k: v for k, v in result.items() if k not in ('parents', 'modification_reason')})
    validate(result, load(HERE/'schemas/candidate.json'))
    return result


def validate_candidate(value, *, current=True, schema=None):
    validate(value, schema or load(HERE/'schemas/candidate.json'))
    expected = identity({k: v for k, v in value.items() if k not in ('id', 'parents', 'modification_reason')})
    if value['id'] != expected or (current and value['geometry_sha256'] != identity(geometry(value['definition']))):
        raise ValueError('candidate identity/geometry mismatch')
    if value['id'] in value['parents'] or len(set(value['parents'])) != len(value['parents']):
        raise ValueError('invalid candidate lineage')


def environment():
    import openseespy.opensees as ops
    binaries = sorted({Path(m.__file__) for name, m in sys.modules.items()
                       if 'opensees' in name and str(getattr(m, '__file__', '')).endswith('.so')})
    if not binaries:
        raise RuntimeError('native OpenSees library fingerprint unavailable')
    ccx = shutil.which('ccx')
    return dict(python=sys.version.split()[0], openseespy=importlib.metadata.version('openseespy'),
                opensees=ops.version(), numpy=importlib.metadata.version('numpy'),
                native_libraries={p.name: sha(p) for p in binaries},
                calculix_binary_sha256=sha(Path(ccx)) if ccx else None)


def controlled(root, relative):
    path = (root/relative).resolve()
    if Path(relative).is_absolute() or '..' in Path(relative).parts or not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError('uncontrolled/missing artifact: '+relative)
    return path


def ledger(output, value):
    with (output/'ledger.jsonl').open('ab') as stream:
        stream.write(json.dumps(value, sort_keys=True, allow_nan=False).encode()+b'\n')


def prepare(config, output):
    study = load(config); validate_study(study)
    native_environment = environment()
    if output.exists():
        raise ValueError('study output already exists; use --resume or a new directory')
    if output.resolve().is_relative_to(ROOT) and not output.resolve().is_relative_to(ROOT/'build'):
        raise ValueError('scratch studies inside the repository belong under build/')
    cases = []
    ancestors = {c['id']: c for c in study.get('lineage_records', [])}
    if len(ancestors) != len(study.get('lineage_records', [])):
        raise ValueError('duplicate ancestor records')
    for c in ancestors.values():
        validate_candidate(c, current=False)
    def visit(identifier, active, visited):
        if identifier in active:
            raise ValueError('candidate lineage contains a cycle')
        if identifier not in ancestors:
            raise ValueError('candidate lineage parent record missing')
        if identifier in visited:
            return
        for parent in ancestors[identifier]['parents']:
            visit(parent, active | {identifier}, visited)
        visited.add(identifier)
    visited = set()
    for identifier in ancestors:
        visit(identifier, set(), visited)
    for value in study['candidates']:
        c = candidate(value, study)
        validate_candidate(c)
        for parent in c['parents']:
            visit(parent, {c['id']}, set())
        cases.append(dict(name=value['name'], candidate_id=c['id']))
    if len({r['candidate_id'] for r in cases}) != len(cases):
        raise ValueError('duplicate candidate definitions')
    if len(cases)*len(study['ground_scenarios']) > study['analysis']['max_evaluations']:
        raise ValueError('campaign exceeds registered evaluation budget')
    output.mkdir(parents=True)
    write(output/'study.json', study)
    source_hashes = dependencies()
    for relative in source_hashes:
        target = output/'sources'/relative
        target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes((ROOT/relative).read_bytes())
    for relative in study['sources_sha256']:
        target = output/'sources'/relative
        target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes((ROOT/relative).read_bytes())
    for value in study['candidates']:
        c = candidate(value, study)
        write(output/'candidates'/f'{c["id"]}.json', c)
        write(output/'geometry'/f'{c["id"]}.json', geometry(c['definition']))
        (output/'geometry'/f'{c["id"]}.svg').write_text(section_svg(c['definition']))
        ledger(output, dict(event='candidate-created', candidate_id=c['id'], parents=c['parents'], reason=c['modification_reason']))
    for identifier, c in ancestors.items():
        write(output/'lineage'/f'{identifier}.json', c)
    manifest = dict(schema='osr-civil-campaign/1', study_sha256=sha(output/'study.json'),
                    repository_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                    dependency_hashes=source_hashes, environment=native_environment, cases=cases,
                    input_hashes={p.relative_to(output).as_posix(): sha(p) for name in ('candidates', 'geometry', 'sources', 'lineage') for p in sorted((output/name).rglob('*')) if p.is_file()},
                    benchmark=None, evaluations=[], report_hashes={}, complete=False, physical_release=False)
    write(output/'manifest.json', manifest)
    return manifest


def verify(output, *, current=True):
    manifest = load(output/'manifest.json')
    if sha(output/'study.json') != manifest['study_sha256']:
        raise ValueError('study manifest hash mismatch')
    if sha(output/'ledger.jsonl') != manifest['ledger_sha256']:
        raise ValueError('candidate/evaluation ledger hash mismatch')
    for relative, digest in manifest['input_hashes'].items():
        if sha(controlled(output, relative)) != digest:
            raise ValueError('input hash mismatch: '+relative)
    for case in manifest['cases']:
        c = load(output/'candidates'/f'{case["candidate_id"]}.json')
        schema = load(output/'sources/engineering/civil_exploration/schemas/candidate.json')
        validate_candidate(c, current=current, schema=schema)
        if identity(load(output/'geometry'/f'{c["id"]}.json')) != c['geometry_sha256']:
            raise ValueError('retained geometry does not match candidate')
    if current:
        if dependencies() != manifest['dependency_hashes']:
            raise ValueError('stale model/schema dependencies; create a new campaign')
        validate_study(load(output/'study.json'))
        if environment() != manifest['environment']:
            raise ValueError('native environment changed; create a new campaign')
    for record in ([manifest['benchmark']] if manifest['benchmark'] else [])+manifest['evaluations']:
        if sha(controlled(output, record['path'])) != record['sha256']:
            raise ValueError('evaluation record hash mismatch: '+record['path'])
        value = load(output/record['path'])
        directory = (output/record['path']).parent
        if {p.name for p in directory.iterdir() if p.is_file()} != set(value['output_hashes']) | {'record.json'}:
            raise ValueError('missing or unexpected native evaluation files')
        for relative, digest in value['output_hashes'].items():
            if sha(controlled((output/record['path']).parent, relative)) != digest:
                raise ValueError('native artifact hash mismatch: '+relative)
        if not value['status'] in ('completed', 'failed', 'timeout'):
            raise ValueError('invalid evaluation execution status')
    for relative, digest in manifest['report_hashes'].items():
        if sha(controlled(output, relative)) != digest:
            raise ValueError('comparison report hash mismatch: '+relative)
    if manifest.get('complete'):
        study = load(output/'study.json')
        expected = {(c['candidate_id'], g['name']) for c in manifest['cases'] for g in study['ground_scenarios']}
        actual = {(r['candidate_id'], r['ground_scenario']) for item in manifest['evaluations'] for r in [load(output/item['path'])]}
        if actual != expected:
            raise ValueError('complete campaign evaluation coverage mismatch')
    return manifest


def execute(output, job, *, benchmark=False):
    evaluation_id = identity(job)
    parent = output/('benchmarks' if benchmark else 'evaluations')/evaluation_id
    parent.mkdir(parents=True, exist_ok=True)
    attempt = len(list(parent.glob('attempt-*')))+1
    directory = parent/f'attempt-{attempt:04d}'
    directory.mkdir(); write(directory/'job.json', job)
    start = time.monotonic()
    status, error = 'completed', None
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
    with (directory/'stdout.log').open('w') as stdout, (directory/'stderr.log').open('w') as stderr:
        try:
            execution = subprocess.run([sys.executable, str(ROOT/'tools/automation/civil-study.py'), '_worker',
                                        str(directory/'job.json'), str(directory)], cwd=ROOT, env=env,
                                       stdout=stdout, stderr=stderr, timeout=job['timeout_s'])
            if execution.returncode:
                status, error = 'failed', f'native worker exited {execution.returncode}; inspect stderr.log'
        except subprocess.TimeoutExpired:
            status, error = 'timeout', 'registered worker runtime budget exceeded'
    if status == 'completed' and not (directory/'result.json').exists():
        status, error = 'failed', 'worker produced no native result'
    record = dict(schema='osr-civil-execution/1', evaluation_id=evaluation_id, attempt=attempt,
                  candidate_id=job.get('candidate', {}).get('id'), ground_scenario=job.get('ground', {}).get('name'),
                  status=status, error=error, elapsed_s=time.monotonic()-start,
                  output_hashes={p.name: sha(p) for p in sorted(directory.iterdir()) if p.is_file()})
    write(directory/'record.json', record)
    ledger(output, dict(event='evaluation-finished', evaluation_id=evaluation_id, attempt=attempt, status=status))
    return dict(path=(directory/'record.json').relative_to(output).as_posix(), sha256=sha(directory/'record.json'))


def worker(job_path, output):
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (4*1024**3, 4*1024**3))
    job = load(job_path)
    if job['dependencies'] != dependencies() or job['environment'] != environment():
        raise ValueError('worker inputs do not match current code/native environment')
    if job.get('kind') == 'benchmark':
        from engineering.analysis.benchmarks.civil.exploration import run
        result = run()
        # Existing elastic beam/drainage replay is preserved, in addition to
        # the independent new shear/support/modal/moving-force fixtures.
        subprocess.run([sys.executable, str(ROOT/'tools/automation/civil_reference.py'), '--verify-native-replay'],
                       cwd=ROOT, check=True, timeout=60)
        result['existing_reference_replay_passed'] = True
    else:
        from .model import evaluate
        validate_study(job['study']); validate_candidate(job['candidate'])
        result = evaluate(job, output)
    write(output/'result.json', result)


def run_campaign(config, output, *, resume=False, retry_failed=False):
    manifest = verify(output) if resume else prepare(config, output)
    study = load(output/'study.json')
    if load(config) != study:
        raise ValueError('resume configuration differs from sealed study')
    common = dict(dependencies=manifest['dependency_hashes'], environment=manifest['environment'],
                  timeout_s=study['analysis']['worker_timeout_s'])
    if manifest['benchmark'] is None:
        manifest['benchmark'] = execute(output, dict(kind='benchmark', **common), benchmark=True)
        write(output/'manifest.json', manifest)
    benchmark_record = load(output/manifest['benchmark']['path'])
    benchmark_result = (output/manifest['benchmark']['path']).parent/'result.json'
    if benchmark_record['status'] != 'completed' or not load(benchmark_result)['passed']:
        raise ValueError('benchmark failed; candidate evaluation blocked; native evidence retained')
    for case in manifest['cases']:
        c = load(output/'candidates'/f'{case["candidate_id"]}.json')
        for ground in study['ground_scenarios']:
            job = dict(candidate=c, study=study, ground=ground, **common)
            previous = [r for r in manifest['evaluations'] if load(output/r['path'])['evaluation_id'] == identity(job)]
            if previous and (load(output/previous[-1]['path'])['status'] == 'completed' or not retry_failed):
                continue
            print(f"Evaluating {case['name']} / {ground['name']}", flush=True)
            manifest['evaluations'].append(execute(output, job))
            write(output/'manifest.json', manifest)
    manifest['complete'] = True
    write(output/'manifest.json', manifest)
    compare(output)
    return verify(output)


def derive(parent_path, definition_path, output, *, reason='user-specified geometry modification'):
    parent = load(parent_path); validate_candidate(parent)
    definition = load(definition_path)
    validate(definition, load(HERE/'schemas/candidate.json')['properties']['definition'])
    c = candidate(definition, parent, parents=[parent['id']], reason=reason)
    if c['id'] == parent['id']:
        raise ValueError('modification does not change the design')
    if output.exists():
        raise ValueError('derived candidate already exists')
    write(output, c)
    return c


def compare(output):
    manifest = verify(output)
    names = {case['candidate_id']: case['name'] for case in manifest['cases']}
    latest = {}
    for entry in manifest['evaluations']:
        record = load(output/entry['path'])
        latest[record['evaluation_id']] = (entry, record)
    rows = []
    for entry, record in latest.values():
        row = dict(candidate=names[record['candidate_id']], scenario=record['ground_scenario'],
                   execution=record['status'], numerical_screen='unresolved', engineering_feasibility='unresolved',
                   fabricated_beam_t=None, suspended_t=None, concrete_m3=None, installed_mass_t=None,
                   deck_displacement_mm=None, relative_static_deflection_mm=None, deck_acceleration_m_s2=None,
                   foundation_settlement_mm=None, braking_pier_drift_mm=None, gross_elastic_stress_mpa=None,
                   handling_moment_knm=None, lift_constraint='unresolved', installed_cost_usd=None,
                   evidence_gaps=record['error'] or '')
        if record['status'] == 'completed':
            result = load((output/entry['path']).parent/'result.json')
            q, peaks = result['quantities'], result['peak_responses']
            lift = next(l for l in result['research_limits'] if l['metric'] == 'suspended_mass_kg')
            row.update(numerical_screen='passed' if result['numerical_screen_passed'] else 'failed',
                       fabricated_beam_t=q['fabricated_beam_mass_kg']/1000, suspended_t=q['suspended_mass_kg']/1000,
                       concrete_m3=q['concrete_m3'], installed_mass_t=q['installed_study_mass_kg']/1000,
                       deck_displacement_mm=peaks['deck_displacement_m']*1000,
                       relative_static_deflection_mm=result['static'][-1]['envelope']['relative_deck_deflection_m']*1000,
                       deck_acceleration_m_s2=peaks['deck_acceleration_m_s2'],
                       foundation_settlement_mm=peaks['foundation_settlement_m']*1000,
                       braking_pier_drift_mm=result['braking']['pier_top_horizontal_m']*1000,
                       gross_elastic_stress_mpa=peaks['gross_elastic_fibre_stress_pa']/1e6,
                       handling_moment_knm=result['handling'][-1]['bending_moment_nm']/1000,
                       lift_constraint=lift['status'], evidence_gaps='; '.join(result['evidence_gaps']))
        rows.append(row)
    if not rows:
        raise ValueError('no completed or failed evaluations to compare')
    with (output/'comparison.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
    study = load(output/'study.json')
    text = ['# Complete civil system research comparison', '',
            f"Study: {study['name']}. Baseline commit: `{manifest['repository_commit']}`.", '',
            f"Equal {study['route_length_m']:g} m double-track scope. Concrete, steel, track and rigging masses are explicit study allowances.",
            f"Two synchronous `{study['train']['name']}` planning trains. {study['train']['basis']}", '',
            'Native 2D elastic Timoshenko analysis includes diaphragms, finite bearings, shared piers, ground springs, moving-force transients and overhanging handling stages.',
            'Geotechnical stiffness, damping, reinforcement and prestress are uncalibrated. Elastic stress is not a resistance or prestress check.',
            'Every engineering feasibility remains unresolved. Unknown supplier and whole-life costs stay blank. There is no qualified Pareto set or automatic release.', '',
            '| Candidate | Ground | Suspended t | Concrete m³ | Deck movement mm | Acceleration m/s² | Numerical screen | Lift study limit |',
            '|---|---|---:|---:|---:|---:|---|---|']
    def number(value):
        return '—' if value is None else f'{value:.3f}'
    for row in rows:
        text.append('| '+' | '.join([row['candidate'], row['scenario'], *[number(row[k]) for k in ('suspended_t', 'concrete_m3', 'deck_displacement_mm', 'deck_acceleration_m_s2')], row['numerical_screen'], row['lift_constraint']])+' |')
    text += ['', '## Evidence and failure history', '',
             'See `comparison.csv` for quantity/response fields and missing evidence, `manifest.json` for exact source/native identities, and `ledger.jsonl` for attempts.',
             'Each evaluation retains its sealed job, native histories, modal shapes, mesh/time-step checks, governing cases and worker logs.',
             'Native worker execution and convergence-screen outcomes are separate. Failed or timed-out attempts are retained.',
             'No supplier quotation, measured soil response, nonlinear capacity, fatigue, 3D torsion, seismic or physical-validation pass is inferred.', '']
    text += ['## Material sections', '']
    for case in manifest['cases']:
        text += [f"### {case['name']}", '', f"![Research material section](geometry/{case['candidate_id']}.svg)", '']
    (output/'comparison.md').write_text('\n'.join(text))
    write(output/'comparison.json', dict(schema='osr-civil-comparison/1', rows=rows,
                                        qualified_feasible_pareto_set=[], physical_release=False))
    manifest['report_hashes'] = {name: sha(output/name) for name in ('comparison.csv', 'comparison.md', 'comparison.json')}
    write(output/'manifest.json', manifest)
    return rows
