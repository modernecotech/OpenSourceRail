"""Executed development profiles, separate from source trace and acceptance.

Heavy checks run only through ``run``. Readers check pinned sources and raw
outputs; opening a report cannot start Docker, Kani or a test campaign.
"""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

from . import model

ROOT = model.ROOT
OUTPUT = ROOT/'docs/design-engine/ferrite-maglev/assurance-profiles'
RAW = ROOT/'engineering/assurance/v052-pilot-profiles'
CASE = Path(__file__).parent/'data/pilot-assurance-case.toml'
SCHEMA = 'osr-pilot-assurance/1'
PROOFS = (
    ('osr-interlocking', 'kani_p5_time_bounded_arithmetic', 'retained validity-window saturating arithmetic'),
    ('osr-atp', 'kani_a2_expired_ma_trips', 'retained expired authority emergency response'),
    ('osr-maglev-control', 'kani_maglev_stale_support_requests_fallback', 'stale support sample refusal'),
    ('osr-maglev-control', 'kani_maglev_unprotected_launch_has_no_force', 'uncommitted or unprotected launch refusal'),
    ('osr-maglev-control', 'kani_maglev_replayed_drive_frame_has_no_duties', 'replayed current-loop sequence refusal'),
)
PROFILES = ('engineering', 'delivery-lifecycle', 'control-formal')
COLD_CYCLE_TEST = 'engineering/analysis/tests/test_ferrite_maglev.py::test_scheduled_cycle_idles_without_rewriting_unchanged_results'
COLD_CYCLE_TIMEOUT_SECONDS = 7200


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n').encode()


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def commands(profile):
    python = ['tools/automation/osr-python']
    if profile == 'control-formal':
        return [['cargo', 'kani', '-p', package, '--harness', harness] for package, harness, _ in PROOFS]
    if profile == 'engineering':
        tests = sorted((ROOT/'engineering/analysis/tests').glob('test_ferrite_maglev*.py'))
        observer='engineering/ferrite_maglev/observer-prototype/Cargo.toml'
        slow=('engineering/analysis/tests/test_ferrite_maglev.py::test_primary_publication_tamper_stale_and_source_binding',
              COLD_CYCLE_TEST)
        pytest=python+['-m','pytest','-q']
        # Guard failures should precede full publication/refresh campaigns.
        # The two exact functions remain required as separate executions.
        return [pytest+[*(p.relative_to(ROOT).as_posix() for p in tests),
                        *('--deselect='+node for node in slow)],
                *(pytest+[node] for node in slow),
                ['cargo','fmt','--manifest-path',observer,'--','--check'],
                ['cargo','clippy','--locked','--manifest-path',observer,'--all-targets','--','-D','warnings'],
                ['cargo','test','--locked','--manifest-path',observer,'--all-targets'],
                python+['engineering/ferrite_maglev/observer-prototype/tests/differential.py'],
                ['cargo','fmt','--manifest-path','engineering/ferrite_maglev/full-dynamics-kernel/Cargo.toml','--','--check'],
                ['cargo','clippy','--locked','--manifest-path','engineering/ferrite_maglev/full-dynamics-kernel/Cargo.toml','--all-targets','--','-D','warnings'],
                ['cargo','test','--locked','--manifest-path','engineering/ferrite_maglev/full-dynamics-kernel/Cargo.toml','--all-targets'],
        ['node','tools/automation/tests/verify-planning-workspace.mjs','build/planning-browser'],
        ['cargo','fmt','--all','--','--check'],
        ['cargo','clippy','--locked','--workspace','--all-targets','--','-D','warnings'],
        ['cargo','test','--locked','--workspace','--all-targets'],
        ['cargo','check','--locked','-p','osr-maglev-control','--no-default-features']]
    if profile == 'delivery-lifecycle':
        return [python+['tools/automation/pilot-lifecycle-native.py', 'verify'],
                python+['tools/automation/pilot-lifecycle-native.py','verify','--candidate'],
                python+['-m', 'pytest', '-q', 'engineering/analysis/tests/test_ferrite_maglev_pilot_lifecycle.py','engineering/analysis/tests/test_ferrite_maglev_candidate_lifecycle.py']]
    raise ValueError('unknown development profile')


def source_paths():
    return [Path(__file__), CASE, ROOT/'engineering/analysis/tests/test_ferrite_maglev_pilot_assurance.py']


def command_timeout(command):
    # This one test runs two complete cold cycles, including a report mirror
    # and reader-book verification. The outer runner must cover both inner
    # deadlines; unrelated commands retain their existing bounded allowance.
    scheduled = ['tools/automation/osr-python','-m','pytest','-q',COLD_CYCLE_TEST]
    return 2*COLD_CYCLE_TIMEOUT_SECONDS+3600 if command == scheduled else 7200


def sources(profile=None):
    paths = set(source_paths())
    if profile != 'control-formal':
        paths.update(ROOT/name for name in model.sources(include_generated=False))
        paths.add(ROOT/'tools/automation/osr-python')
        observer_lock=ROOT/'engineering/ferrite_maglev/observer-prototype/Cargo.lock'
        if observer_lock.is_file():
            paths.add(observer_lock)
        paths.add(ROOT/'engineering/ferrite_maglev/full-dynamics-kernel/Cargo.lock')
    # Scope dependencies conservatively; no generated packet or receipt is an
    # implementation input. A changed dependency invalidates retained execution.
    folders = ['crates'] if profile == 'control-formal' else ['crates', 'engineering/ferrite_maglev', 'engineering/analysis/tests']
    if profile != 'control-formal':
        folders += ['deployment/erpnext/apps', 'services/integration', 'deployment/supervision']
    for folder in folders:
        paths.update(p for p in (ROOT/folder).rglob('*') if p.is_file()
                     and p.suffix in {'.py', '.rs', '.toml', '.json', '.sh', '.js', '.mjs', '.h', '.c'}
                     and not any(x in p.parts for x in ('__pycache__', 'node_modules', 'target'))
                     and not p.name.startswith('city-index.'))
    for name in ('Cargo.toml', 'Cargo.lock', 'rust-toolchain.toml'):
        if (ROOT/name).exists():
            paths.add(ROOT/name)
    if profile == 'delivery-lifecycle':
        paths.add(ROOT/'tools/automation/pilot-lifecycle-native.py')
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(paths)}


def refresh_development_views():
    """Publish the new pending hold before readiness tests inspect the UI.

    A repeat engineering run invalidates its former pass immediately. Updating
    only these dependent views prevents that intentional hold from making the
    run fail its own source/currentness test. Other design packets must already
    be current; this never reruns physics, native business work or proofs.
    """
    from . import capability_migration, pilot_release, delivery, workflow
    with workflow.locked():
        for name, publisher in (('assurance-profiles',publish),
                                ('capability-migration',capability_migration.publish),
                                ('pilot-delivery',pilot_release.publish)):
            workflow.fresh_packet(name,publisher)
        delivery.publish()


def run(profile, raw=RAW):
    """Retain immutable command outputs and fail if their source changes."""
    expected = commands(profile)
    before = sources(profile)
    directory = Path(raw)/profile/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    directory.mkdir(parents=True, exist_ok=False)
    rows = []
    receipt = dict(schema=SCHEMA, profile=profile, state='running', passed=False,
                   executions=rows, source_sha256=before, tool_version='unavailable',
                   source_unchanged=True, independent_acceptance=False, **model.FLAGS)
    def write_receipt():
        temporary=directory/'receipt.pending'
        temporary.write_bytes(encoded(receipt))
        os.replace(temporary,directory/'receipt.json')
    # Durable intent precedes command execution. SIGKILL, a missing executable
    # or a failed version query must invalidate any older same-source pass.
    write_receipt()
    if profile=='engineering' and Path(raw).resolve()==RAW.resolve():
        try:
            refresh_development_views()
            receipt['presentation_preflight']='pending hold published before readiness tests'
        except Exception as exc:
            receipt.update(state='failed',passed=False,presentation_preflight_error=str(exc),
                           source_unchanged=before==sources(profile))
            write_receipt()
            raise ValueError('engineering views could not publish the pending hold; build current design packets first') from exc
    for i, command in enumerate(expected):
        log = directory/f'{i:02d}.txt'
        started = datetime.now(timezone.utc).isoformat()
        with log.open('wb') as stream:
            try:
                result = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, timeout=command_timeout(command))
                code = result.returncode
            except (OSError, subprocess.TimeoutExpired) as exc:
                stream.write(str(exc).encode()); code = 125
        text = log.read_text(errors='replace')
        verified = code == 0 and (profile != 'control-formal' or
            '1 successfully verified harnesses, 0 failures, 1 total' in text)
        rows.append(dict(command=command, started_utc=started, finished_utc=datetime.now(timezone.utc).isoformat(),
                         exit_code=code, passed=verified, report=log.name, report_sha256=digest(log)))
        if not verified:
            break
    tool_command = ['cargo', 'kani', '--version'] if profile == 'control-formal' else [str(ROOT/'tools/automation/osr-python'), '--version']
    try:
        receipt['tool_version']=subprocess.check_output(tool_command,cwd=ROOT,text=True,stderr=subprocess.STDOUT,timeout=30).strip()
        version_ok=bool(receipt['tool_version'])
    except (OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as exc:
        receipt['tool_version_error']=str(exc); version_ok=False
    receipt.update(executions=rows,source_unchanged=before==sources(profile))
    receipt['passed'] = version_ok and len(rows) == len(expected) and all(r['passed'] for r in rows) and receipt['source_unchanged']
    receipt['state']='passed' if receipt['passed'] else 'failed'
    write_receipt()
    if not receipt['passed']:
        raise ValueError('development profile failed or source changed: '+str(directory))
    return directory/'receipt.json'


def read_execution_receipt(path):
    path = Path(path)
    if (path.name!='receipt.json' or any(p.is_symlink() for p in (path,*path.parents))
            or not path.is_file() or path.stat().st_size>8*1024*1024):
        raise ValueError('ordinary bounded execution receipt and ancestors required')
    value=json.loads(path.read_bytes())
    if not isinstance(value,dict):
        raise ValueError('execution receipt must be a mapping')
    return value


def verify_run(path, profile):
    path=Path(path)
    r=read_execution_receipt(path)
    if (r.get('schema') != SCHEMA or r.get('profile') != profile or r.get('passed') is not True
            or r.get('state')!='passed' or not isinstance(r.get('tool_version'),str)
            or r.get('tool_version') in {'','unavailable'}
            or r.get('source_unchanged') is not True or r.get('source_sha256') != sources(profile)
            or r.get('independent_acceptance') is not False or any(r.get(k) is not False for k in model.FLAGS)):
        raise ValueError('missing, stale or unqualified execution receipt')
    if [row['command'] for row in r['executions']] != commands(profile):
        raise ValueError('profile command coverage differs')
    names={f'{i:02d}.txt' for i in range(len(r['executions']))}
    if set(p.name for p in path.parent.iterdir())!=names|{'receipt.json'}:
        raise ValueError('execution inventory differs')
    for i,row in enumerate(r['executions']):
        name = row['report']
        if not isinstance(name,str):
            raise ValueError('unsafe execution log')
        log=path.parent/name
        if (name!=f'{i:02d}.txt' or log.is_symlink()
                or not log.is_file() or log.stat().st_size>64*1024*1024):
            raise ValueError('unsafe execution log')
        if digest(path.parent/name) != row['report_sha256'] or row['exit_code'] != 0 or row['passed'] is not True:
            raise ValueError('failed or altered execution log')
        if profile == 'control-formal' and '1 successfully verified harnesses, 0 failures, 1 total' not in (path.parent/name).read_text():
            raise ValueError('formal harness did not execute')
    return r


def latest(profile, raw=RAW):
    folder=Path(raw)/profile
    directories=sorted(folder.iterdir(),reverse=True) if folder.exists() else []
    if not directories:
        return None, None
    current=sources(profile)
    for directory in directories:
        path=directory/'receipt.json'
        try:
            if directory.is_symlink() or not directory.is_dir() or not path.is_file():
                return None,None
            value=read_execution_receipt(path)
            if value.get('profile')!=profile or value.get('source_sha256')!=current:
                continue
            # A known newer failure for this exact source scope invalidates the
            # former pass. Do not select an older success around that failure.
            return path, verify_run(path, profile)
        except (ValueError, KeyError, TypeError, OSError):
            return None, None
    return None, None


def study(raw=RAW):
    values = []
    for profile in PROFILES:
        path, receipt = latest(profile, raw)
        values.append(dict(id=profile, digital_state='executed-current' if receipt else 'hold',
                           receipt=path.relative_to(ROOT).as_posix() if path and path.is_relative_to(ROOT) else None,
                           receipt_sha256=digest(path) if path else None,
                           executions=len(receipt['executions']) if receipt else 0, independent_acceptance=False))
    return dict(schema=SCHEMA, profiles=values, source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in source_paths()},
                formal_properties=[dict(crate=p, harness=h, scope=s) for p,h,s in PROOFS],
                all_profiles_executed=all(r['digital_state']=='executed-current' for r in values),
                scope='Exact development execution; engineering, delivery and formal profiles are separate. No SIL, hardware, site or operational acceptance.',
                external_gates=['measured magnetic maps', 'target timing and EMI', 'site/ground and utilities',
                                'fire and evacuation', 'supplier qualifications', 'independent engineering and authority acceptance'], **model.FLAGS)


def evidence_results(raw=RAW):
    """Export execution records for the existing Rust GSN result assessor.

    No acceptance section is emitted. The physical protocol plan intentionally
    has no execution record, even when all three development profiles pass.
    """
    formal_ids=('E-TIME','E-EXPIRED','E-STALE-SUPPORT','E-UNPROTECTED-LAUNCH','E-REPLAY-DRIVE')
    rows=[]
    for profile in PROFILES:
        path,receipt=latest(profile,raw)
        if receipt is None:
            continue
        if profile=='control-formal':
            mappings=[(identity,'kani',f'crates/{package}/src/kani_proofs.rs',harness,i)
                      for i,(identity,(package,harness,_)) in enumerate(zip(formal_ids,PROOFS))]
        elif profile=='engineering':
            mappings=[(identity,'pytest',f'engineering/analysis/tests/test_ferrite_maglev_{name}.py',None,0)
                      for identity,name in [('E-PRODUCT','pilot_product'),('E-ACTUATOR','pilot_actuators'),
                                             ('E-DELIVERY-SCHEDULE','delivery_schedule'),('E-CORRIDOR','pilot_corridor')]]
        else:
            mappings=[('E-LIFECYCLE','sim-run','tools/automation/pilot-lifecycle-native.py',None,0)]
        for identity,kind,source,anchor,index in mappings:
            execution=receipt['executions'][index]
            report=path.parent/execution['report']
            row=dict(solution=identity,kind=kind,path=source,tool='cargo-kani' if kind=='kani' else 'controlled-profile-runner',
                     tool_version=receipt['tool_version'],bounds='Exact declared command and source scope; Kani source harness assumptions and unwind40 for new refusal properties; no physical or timing qualification',
                     executed_by='local-development-runner',status='passed',exit_code=0,
                     report=report.relative_to(ROOT).as_posix(),report_sha256=digest(report),inputs=receipt['source_sha256'])
            if anchor:
                row['anchor']=anchor
            rows.append(row)
    text=['schema = "osr-evidence-results/1"','']
    for row in rows:
        text += ['[[result]]']
        for key,value in row.items():
            if key=='inputs':
                continue
            text.append(key+' = '+json.dumps(value))
        text += ['[result.inputs]']
        text += [json.dumps(k)+' = '+json.dumps(v) for k,v in sorted(row['inputs'].items())]
        text.append('')
    return '\n'.join(text)


def readme(result):
    rows = ['# Pilot development assurance profiles', '', result['scope'], '',
            '| Profile | Digital execution | Commands |', '|---|---|---:|']
    rows += [f"| {r['id']} | {r['digital_state']} | {r['executions']} |" for r in result['profiles']]
    rows += ['', 'Run an explicit profile with `./osr assurance run <profile>`.',
             'Opening/verifying this packet only checks retained evidence. Failed or stale runs cannot become a current pass. Build current design packets before an engineering profile; its pending hold is published before readiness tests. Run `./osr build` after successful profiles to refresh their completed presentation.', '',
             'The project assurance graph traces current engineering, delivery and control claims to source. Source traceability, executed verification and independent acceptance are separate gates.', '',
             'Physical gates: '+', '.join(result['external_gates'])+'.', '',
             'Compile the whole pilot evidence graph with `cargo run --locked -p osr-safety-case -- engineering/ferrite_maglev/data --evidence-root . --results docs/design-engine/ferrite-maglev/assurance-profiles/results.toml`. The physical-protocol branch remains unverified and every independent acceptance remains open.', '',
             '[Kani usage and harness selection](https://model-checking.github.io/kani/usage.html) · [Loop bounds and unwinding assertions](https://model-checking.github.io/kani/tutorial-loop-unwinding.html).', '']
    return '\n'.join(rows)


def publish(output=OUTPUT):
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    result = study()
    files = {'study.json':encoded(result), 'README.md':readme(result).encode(), 'results.toml':evidence_results().encode()}
    for name, data in files.items():
        (output/name).write_bytes(data)
    manifest = dict(schema=SCHEMA, source_sha256=result['source_sha256'], files_sha256={n:sha256(b).hexdigest() for n,b in files.items()}, **model.FLAGS)
    (output/'manifest.json').write_bytes(encoded(manifest))
    return manifest


def verify(output=OUTPUT, *, require_executed=False):
    output = Path(output); m = json.loads((output/'manifest.json').read_bytes())
    if output.is_symlink() or m['schema'] != SCHEMA or any(m.get(k) is not False for k in model.FLAGS):
        raise ValueError('assurance packet schema or release differs')
    if set(p.name for p in output.iterdir()) != {'study.json','README.md','results.toml','manifest.json'} or any(p.is_symlink() for p in output.iterdir()):
        raise ValueError('unexpected assurance payload')
    if m['files_sha256'] != {n:digest(output/n) for n in ('study.json','README.md','results.toml')}:
        raise ValueError('assurance payload changed')
    current=study()
    if (m.get('source_sha256')!=current['source_sha256'] or json.loads((output/'study.json').read_bytes())!=current
            or (output/'results.toml').read_text()!=evidence_results()
            or (output/'README.md').read_text()!=readme(current)):
        raise ValueError('assurance execution changed; refresh profiles packet')
    if require_executed and current.get('all_profiles_executed') is not True:
        raise ValueError('all three current development execution profiles are required')
    return m


def read_summary(output=OUTPUT):
    verify(output)
    return json.loads((Path(output)/'study.json').read_bytes())


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('run','publish','verify'))
    parser.add_argument('profile', nargs='?', choices=PROFILES)
    parser.add_argument('--require-executed', action='store_true', help='Reject a valid presentation whose current development profiles remain held')
    args = parser.parse_args()
    if args.action == 'run':
        if args.profile is None:
            parser.error('run requires a development profile')
        print(run(args.profile))
    elif args.action=='verify':
        print(json.dumps(verify(require_executed=args.require_executed), indent=2))
    else:
        if args.require_executed:
            parser.error('--require-executed applies to verify')
        print(json.dumps(publish(), indent=2))


if __name__ == '__main__':
    main()
