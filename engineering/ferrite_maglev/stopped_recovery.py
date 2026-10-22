"""Executed single-domain stopped recovery; fresh runs verify every retained replay.

The old snapshot grants never resume. This does not implement moving recovery,
multi-controller handover, authenticated installed persistence or physical I/O.
"""
from hashlib import sha256
from pathlib import Path
import gzip
import json
import re
import subprocess

from . import line_capacity, model

ROOT=model.ROOT
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/stopped-recovery'
EXAMPLE=ROOT/'crates/osr-interlocking/examples/stopped_recovery_replay.rs'
TEST=ROOT/'engineering/analysis/tests/test_ferrite_maglev_stopped_recovery.py'
SCHEMA='osr-stopped-recovery-study/1'
PROTOCOL='osr-progressive-stopped-recovery/1'
BUILD=['cargo','build','--locked','-p','osr-interlocking','--example','stopped_recovery_replay','--message-format=json']
API=['cargo','test','--locked','-p','osr-interlocking','--lib','progressive::recovery::tests','--','--test-threads=1']
CASES=('nominal','prepared','two-train','missing-train','duplicate-train','moving','wrong-berth',
       'old-epoch','stale-readiness','stale-proof','wrong-owner','unexplained-occupant',
       'unsafe-clearance','cleared-owner','quarantine','wrong-model','missing-proof',
       'blocked','proof-sequence','second-crash','replayed-reconcile','old-commit')
PASS={'nominal','prepared','two-train','replayed-reconcile','old-commit'}
FILES={'study.json.gz','execution.json.gz','overview.svg','README.md'}
MAX_FILE=8*1024*1024
MAX_RAW=32*1024*1024
SCOPE='Executed stopped reconciliation within one local domain.250m assumed stopping margin explicitly retains forward locks; no capacity or physical acceptance.'
API_NAMES={'adversarial_reconciliation_is_atomic_and_never_releases_a_retained_owner',
    'every_crash_loses_the_transient_restart_and_reconciliation_witness',
    'pinned_model_and_policy_must_match_restored_controller',
    'prepared_and_committed_snapshots_need_new_epoch_and_fresh_contract',
    'restart_of_a_live_domain_also_requires_reconciliation',
    'snapshot_cannot_inject_a_live_or_restart_witness',
    'two_owners_need_complete_evidence_and_observation_order_does_not_matter'}
HOLDS=[
    'One bounded controller domain, stationary full consists at declared berths; moving restart and controller-to-controller handover remain unimplemented.',
    'Synthetic identified occupancy, integrity, brake readiness and100ms observation bounds require physical detector and timing qualification.',
    'The caller pins the expected configuration/model/policy and must authenticate and durably commit the event history before acting. This transcript and its SHA256 do not supply installed authentication, consensus, fsync or anti-rollback storage.',
    'Every crash loses the transient fence/reconciliation witness; a new monotonically fenced epoch and lease/skew quarantine are required. Reconciliation retires old contracts; new prepare/commit is mandatory.',
    'Off-berth stranded trains, evacuation, rescue authority, degraded protection, station motor/receiver composition and full-line capacity acceptance remain open.',
]


def encoded(v):return (json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def digest(v):return sha256(v).hexdigest()
def sources():
    paths={Path(__file__),TEST,EXAMPLE,*line_capacity.source_paths()}
    return {p.relative_to(ROOT).as_posix():digest(p.read_bytes()) for p in sorted(paths)}


def request(mode,case):
    if mode not in {'urban','suburban'} or case not in CASES:raise ValueError('declared recovery mode/case required')
    a=line_capacity.load();a[mode+'_legs']=2;a['stop_margin_m']=250.
    railway,cfg,_,_=line_capacity.deployment(a,mode,block_length_m=1000.)
    count=2 if case=='two-train' else 1
    positions=[dict(configuration=cfg,owner=t['config']['owner'],epoch=1,sequence=1,observed_ns=1_000_000_000,
        front_mm=railway['routes'][0]['stopping_locations'][i]['at_mm'],velocity_mmps=0,
        independent_brake_ready=True,integrity_proved=True,support_healthy=True,minimum_gap_um=6000,maximum_gap_um=8000)
        for i,t in enumerate(railway['trains'][:count])]
    return dict(model=railway,configuration=cfg,case=case,positions=positions,
        policy=dict(maximum_acceleration_mmps2=round(a['maximum_acceleration_m_s2']*1000),
            maximum_sample_ns=100_000_000,velocity_error_mmps=a['velocity_error_mmps'],minimum_gap_um=3000,maximum_gap_um=13000))


def command(args,stdin=None):
    result=subprocess.run(args,cwd=ROOT,input=stdin,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
    if len(result.stdout)>MAX_RAW or len(result.stderr)>MAX_FILE:raise ValueError('bounded recovery tool output required')
    entry=dict(command=list(map(str,args)),returncode=result.returncode,stdout=result.stdout.decode(),stderr=result.stderr.decode())
    if stdin is not None:entry['stdin_sha256']=digest(stdin)
    if result.returncode:raise ValueError('recovery execution failed: '+result.stderr.decode()[-3000:])
    return entry


def compile_replay():
    entry=command(BUILD);binary=None
    for line in entry['stdout'].splitlines():
        v=json.loads(line)
        if v.get('reason')=='compiler-artifact' and v.get('target',{}).get('name')=='stopped_recovery_replay' and v.get('executable'):
            binary=Path(v['executable'])
    if binary is None or not binary.is_file() or binary.is_symlink():raise ValueError('actual recovery executable required')
    return binary,entry


def api_controls(entry):
    names=set(re.findall(r'^test progressive::recovery::tests::([a-z_]+) \.\.\. ok$',entry.get('stdout',''),re.M))
    if entry.get('command')!=API or entry.get('returncode')!=0 or names!=API_NAMES or '7 passed; 0 failed; 0 ignored;' not in entry['stdout']:
        raise ValueError('complete executed recovery API regression group required')


def check_replay(value,input):
    expected=input['case'] in PASS;count=len(input['positions'])
    if (value.get('schema')!='osr-stopped-recovery-replay/1' or value.get('protocol')!=PROTOCOL
        or value.get('case')!=input['case'] or value.get('configuration')!=input['configuration']
        or value.get('participants')!=count or value.get('reconciliation_passed') is not expected
        or value.get('new_authorities')!=(count if expected else 0)
        or value.get('snapshot_fenced') is not True or value.get('old_contracts_fenced') is not True
        or value.get('exact_event_replay_equal') is not True
        or any(value.get(k) is not False for k in ('physical_output_authorised','multi_controller_handover_implemented','authenticated_persistence_implemented'))):
        raise ValueError('recovery result, identity or scope differs')
    if not expected and (value.get('rejection_atomic') is not True or not value.get('reconciliation_error')):
        raise ValueError('recovery rejection must retain every resource record')
    if input['case']=='replayed-reconcile' and value.get('duplicate_rejected') is not True:raise ValueError('repeated reconciliation accepted')
    if input['case']=='old-commit' and value.get('old_commit_rejected') is not True:raise ValueError('old contract resumed')
    snapshots=[a['Restore']['snapshot'] for a in value['transcript'] if 'Restore' in a]
    if len(snapshots)!=(2 if input['case']=='second-crash' else 1):raise ValueError('exact checkpoint inventory differs')
    if snapshots[0]['ledger']['model']!=input['model'] or snapshots[0]['ledger']['configuration']!=input['configuration']:
        raise ValueError('checkpoint model differs')
    if len(value['retained_records'])!=len(input['model']['resources']):raise ValueError('resource inventory differs')


def replay(binary,mode,case):
    value=request(mode,case);raw=encoded(value);entry=command([str(binary)],raw)
    result=json.loads(entry['stdout']);check_replay(result,value)
    return dict(mode=mode,case=case,request=value,result=result),entry


def study():
    before=sources();binary,build=compile_replay();api=command(API);api_controls(api)
    binary_sha=digest(binary.read_bytes())
    runs=[];execution=[]
    for mode in ('urban','suburban'):
        for case in CASES:
            run,entry=replay(binary,mode,case);runs.append(run);execution.append(dict(mode=mode,case=case,**entry))
    if sources()!=before or digest(binary.read_bytes())!=binary_sha:raise ValueError('recovery sources or executable changed during execution')
    return dict(schema=SCHEMA,source_sha256=before,protocol=PROTOCOL,runs=runs,
        all_controls_pass=True,study_pass=True,multi_controller_handover_implemented=False,
        authenticated_persistence_implemented=False,old_contract_resumption=False,city_default_changed=False,
        scope=SCOPE,open_gates=HOLDS,**model.FLAGS),dict(build=build,api=api,binary_sha256=binary_sha,runs=execution)


def overview(value):
    rows=''.join(f'<text x="24" y="{92+28*i}">{r["mode"]} / {r["case"]}: '+('reconciled; fresh contract only' if r['result']['reconciliation_passed'] else 'rejected atomically; locks retained')+'</text>' for i,r in enumerate(value['runs']))
    h=150+28*len(value['runs'])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{h}" viewBox="0 0 1000 {h}"><rect width="1000" height="{h}" fill="#f4f8fb"/><g font-family="sans-serif" font-size="16" fill="#17384b"><text x="24" y="38" font-size="25">Stopped recovery — one offline conflict domain</text><text x="24" y="64">Fresh epoch + quarantine + full stopped evidence + atomic reconciliation + new prepare/commit</text>{rows}<text x="24" y="{h-24}">No moving recovery, distributed handover, installed authentication or physical release.</text></g></svg>\n').encode()


def readme(value):
    return ('# Stopped progressive-controller recovery\n\n'+value['scope']+'\n\n'
        f'`{PROTOCOL}` executes {len(value["runs"])} actual Rust replays. '
        'Prepared/committed snapshots, two trains, omitted/duplicated trains, stale/wrong-epoch proofs, unsafe clearance, moving/off-berth reports, blocked resources, a second crash, repeated reconciliation and old commits are separate controls. '
        'Rejected reconciliation changes no resource record. Positive cases require fresh prepare/commit; the old contracts remain retired.\n\n'
        '[Full inputs, snapshots, event transcripts and outputs](study.json.gz) · [Actual compiler, API-test and replay output](execution.json.gz) · [Source receipt](manifest.json) · [Overview](overview.svg).\n\n'
        'Verification recompiles the pinned source and repeats every replay, comparing complete decoded output; altered, rehashed histories do not pass.\n\n'
        +'\n'.join('- '+v for v in HOLDS)+'\n\nAll engineering/physical release flags remain false. No city headway or design is promoted.\n').encode()


def publish(output=OUTPUT):
    output=Path(output).absolute()
    if output.resolve()!=output:raise ValueError('ordinary recovery output path required')
    value,execution=study()
    payload={'study.json.gz':gzip.compress(encoded(value),mtime=0),'execution.json.gz':gzip.compress(encoded(execution),mtime=0),'overview.svg':overview(value),'README.md':readme(value)}
    output.mkdir(parents=True,exist_ok=True)
    if output.is_symlink() or (output/'manifest.json').is_symlink() or set(p.name for p in output.iterdir())-FILES-{'manifest.json'}:raise ValueError('owned recovery packet required')
    for n,data in payload.items():
        if (output/n).is_symlink():raise ValueError('ordinary recovery payload required')
        (output/n).write_bytes(data)
    manifest=dict(schema=SCHEMA,source_sha256=value['source_sha256'],files_sha256={n:digest(data) for n,data in payload.items()},**model.FLAGS)
    (output/'manifest.json').write_bytes(encoded(manifest));return verify(output)


def _read(path,compressed=False):
    if path.is_symlink() or not path.is_file() or path.stat().st_size>MAX_FILE:raise ValueError('bounded ordinary recovery file required')
    raw=path.read_bytes()
    if compressed:
        import io
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as f:raw=f.read(MAX_RAW+1)
        if len(raw)>MAX_RAW:raise ValueError('recovery inflate limit exceeded')
    return json.loads(raw)


def verify(output=OUTPUT):
    output=Path(output).absolute()
    if output.resolve()!=output or output.is_symlink() or set(p.name for p in output.iterdir())!=FILES|{'manifest.json'}:raise ValueError('exact ordinary recovery packet inventory required')
    m=_read(output/'manifest.json');before=sources()
    if m.get('schema')!=SCHEMA or m.get('source_sha256')!=before or set(m.get('files_sha256',{}))!=FILES or any(m.get(k) is not False for k in model.FLAGS):raise ValueError('recovery source or release scope differs')
    for n,h in m['files_sha256'].items():
        p=output/n
        if p.is_symlink() or not p.is_file() or p.stat().st_size>MAX_FILE or digest(p.read_bytes())!=h:raise ValueError('recovery payload differs')
    value=_read(output/'study.json.gz',True);execution=_read(output/'execution.json.gz',True)
    if (value.get('source_sha256')!=before or value.get('schema')!=SCHEMA or value.get('protocol')!=PROTOCOL
        or value.get('scope')!=SCOPE or value.get('open_gates')!=HOLDS or value.get('all_controls_pass') is not True or value.get('study_pass') is not True
        or any(value.get(k) is not False for k in (*model.FLAGS,'old_contract_resumption','city_default_changed','multi_controller_handover_implemented','authenticated_persistence_implemented'))):raise ValueError('recovery study scope differs')
    binary,_=compile_replay()
    original_hash=execution.get('binary_sha256')
    if (not isinstance(original_hash,str) or re.fullmatch('[0-9a-f]{64}',original_hash) is None
        or execution.get('build',{}).get('command')!=BUILD or execution['build'].get('returncode')!=0):raise ValueError('recovery executable receipt differs')
    api_controls(execution.get('api',{}));api_controls(command(API))
    binary_sha=digest(binary.read_bytes())
    if len(value['runs'])!=2*len(CASES) or len(execution['runs'])!=len(value['runs']):raise ValueError('complete recovery replay matrix required')
    for retained,entry,(mode,case) in zip(value['runs'],execution['runs'],((mode,case) for mode in ('urban','suburban') for case in CASES)):
        if retained['mode']!=mode or retained['case']!=case or retained['request']!=request(mode,case):raise ValueError('recovery input differs')
        fresh,_=replay(binary,mode,case)
        if (entry.get('mode')!=mode or entry.get('case')!=case or len(entry.get('command',[]))!=1
            or Path(entry['command'][0]).name!='stopped_recovery_replay'
            or retained!=fresh or json.loads(entry['stdout'])!=retained['result'] or entry.get('returncode')!=0
            or entry.get('stdin_sha256')!=digest(encoded(retained['request']))):raise ValueError('recovery history does not reproduce')
    if sources()!=before or digest(binary.read_bytes())!=binary_sha or (output/'overview.svg').read_bytes()!=overview(value) or (output/'README.md').read_bytes()!=readme(value):raise ValueError('recovery sources, executable or presentation differs')
    return m


def read_summary():
    verify();v=_read(OUTPUT/'study.json.gz',True)
    return dict(schema=SCHEMA,protocol=PROTOCOL,runs=len(v['runs']),successful_reconciliations=sum(r['result']['reconciliation_passed'] for r in v['runs']),
        adverse_cases_rejected=sum(not r['result']['reconciliation_passed'] for r in v['runs']),new_contract_required=True,
        multi_controller_handover_implemented=False,authenticated_persistence_implemented=False,city_default_changed=False,**model.FLAGS)
