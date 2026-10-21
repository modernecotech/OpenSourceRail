"""Portable receipts for executed Rust station-control and launch-protocol studies.

This publication checks retained executable evidence and its source identity.
It is not an authenticated detector record, a motor model or release authority.
"""
from hashlib import sha256
import gzip
import json
import os
from pathlib import Path
import re
import subprocess

from . import model

ROOT=model.ROOT
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/station-protocol'
FILES={'replay.json','executed-tests.txt.gz','README.md'}
MAX_FILE=8*1024*1024
MAX_TRANSCRIPT=16*1024*1024
BUILD=['cargo','build','--locked','-p','osr-maglev-control','--example','station_replay','--message-format=json']
TEST=['cargo','test','--locked','-p','osr-interlocking','--test','station_launch','--','--nocapture','--test-threads=1']
RUSTC=['rustc','--version']
CHECKS={
    'launch','replay_rejected','stale_phase_rejected','zero_thrust_coast','resistor_braking',
    'receiver_fault_requires_independent_recovery','uncommitted_launch_rejected',
    'insufficient_overlap_rejected','physical_outputs_disabled_and_support_preserved',
}
REQUIRED_TESTS={
    'preparation_is_atomic_and_an_unavailable_receiver_does_not_allocate',
    'expiry_before_commit_prevents_departure_without_releasing_ownership',
    'commit_survives_expired_permissions_and_duplicate_events_are_idempotent',
    'receiver_fault_after_commit_holds_the_entire_arrival_path',
    'missing_tail_integrity_and_partial_or_replayed_proofs_cannot_clear',
    'serialized_restart_retains_bundle_and_requires_new_epoch_complete_clearance',
    'wrong_consist_or_configuration_or_duplicate_bundle_is_rejected',
    'committed_log_replay_and_incremental_fold_preserve_the_same_launch',
    'conflicting_detector_or_lost_integrity_holds_without_releasing',
    'this_prototype_rejects_cross_controller_atomic_launch_domains',
    'delayed_prelaunch_clearance_cannot_release_committed_arrival',
    'newer_occupancy_or_conflicting_proofs_disqualify_delayed_clearance',
    'changed_point_route_is_held_and_cannot_commit_station_launch',
}


def encoded(value):
    return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def digest(data):
    return sha256(data).hexdigest()


def sources():
    paths={Path(__file__),ROOT/'Cargo.toml',ROOT/'Cargo.lock',ROOT/'rust-toolchain.toml',
        Path(model.__file__),ROOT/'engineering/analysis/tests/test_ferrite_maglev_station_protocol.py'}
    for name in ('osr-core','osr-interlocking','osr-maglev-control'):
        base=ROOT/'crates'/name
        paths.add(base/'Cargo.toml')
        paths.update(p for p in base.rglob('*') if p.is_file() and p.suffix in {'.rs','.proto'})
    config=ROOT/'.cargo/config.toml'
    if config.is_file():paths.add(config)
    return {p.relative_to(ROOT).as_posix():digest(p.read_bytes()) for p in sorted(paths) if p.is_file()}


def _run(command):
    completed=subprocess.run(command,cwd=ROOT,env=dict(os.environ,CARGO_TERM_COLOR='never'),
        capture_output=True,text=True,timeout=240,check=False)
    record=dict(command=[str(v) for v in command],returncode=completed.returncode,
        stdout=completed.stdout,stderr=completed.stderr)
    if len(encoded(record))>MAX_TRANSCRIPT//4:raise ValueError('station command output exceeds publication bound')
    if completed.returncode!=0:
        raise RuntimeError('station evidence command failed: '+' '.join(record['command'])+'\n'+completed.stderr[-3000:])
    return record


def _execution(transcript):
    return {name:dict(command=entry['command'],returncode=entry['returncode'],
        stdout_sha256=digest(entry['stdout'].encode()),stderr_sha256=digest(entry['stderr'].encode()))
        for name,entry in transcript.items()}


def _controller(value):
    if (value.get('schema')!='osr-station-control-replay/1' or set(value.get('checks',{}))!=CHECKS
            or any(value['checks'][name] is not True for name in CHECKS) or value.get('all_passed') is not True
            or value.get('physical_output_authorised') is not False or value.get('measured_motor_map') is not False):
        raise ValueError('station replay lacks mandatory offline controls or exceeds evidence authority')
    for name in ('launch_current_a','launch_phase_mdeg','voltage_bound_v','copper_loss_w'):
        v=value.get(name)
        if type(v) not in (int,float) or not 0<=v<=1e9:raise ValueError('bounded station replay observation required')


def _tests(stdout):
    passed=set(re.findall(r'^test ([A-Za-z0-9_]+) \.\.\. ok$',stdout,re.M))
    summaries=re.findall(r'^test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',stdout,re.M)
    if passed!=REQUIRED_TESTS or summaries!=[(str(len(REQUIRED_TESTS)),'0','0','0','0')]:
        raise ValueError('station protocol lacks mandatory named executed tests')


def _artifact(stdout):
    artifacts=[]
    for line in stdout.splitlines():
        value=json.loads(line)
        if (value.get('reason')=='compiler-artifact' and value.get('target',{}).get('name')=='station_replay'
                and value.get('executable')):
            artifacts.append(value['executable'])
    if len(artifacts)!=1:raise ValueError('station replay compiler artifact identity missing')
    return artifacts[0]


def _transcript(value):
    if set(value)!={'compiler','build','run','tests'}:raise ValueError('station execution transcript is incomplete')
    for name,entry in value.items():
        if (set(entry)!={'command','returncode','stdout','stderr'} or type(entry['returncode']) is not int
                or entry['returncode']!=0 or not isinstance(entry['stdout'],str) or not isinstance(entry['stderr'],str)):
            raise ValueError('successful actual station execution record required')
        expected={'compiler':RUSTC,'build':BUILD,'tests':TEST}.get(name)
        if expected is not None and entry['command']!=expected:raise ValueError('station execution command differs')
    if (value['run']['command']!=[_artifact(value['build']['stdout'])]
            or not value['compiler']['stdout'].startswith('rustc ')):
        raise ValueError('station compiler/run identity differs')
    _tests(value['tests']['stdout'])


def publish(output=OUTPUT):
    before=sources()
    compiler=_run(RUSTC)
    build=_run(BUILD)
    binary=Path(_artifact(build['stdout']))
    if binary.is_symlink() or not binary.is_file():raise ValueError('ordinary compiled station replay executable required')
    binary_sha=digest(binary.read_bytes())
    run=_run([str(binary)])
    controller=json.loads(run['stdout']);_controller(controller)
    tests=_run(TEST)
    transcript=dict(compiler=compiler,build=build,run=run,tests=tests);_transcript(transcript)
    execution=_execution(transcript)
    epoch=digest(encoded([before,execution,binary_sha]))
    replay=dict(schema='osr-station-protocol-evidence/1',source_sha256=before,source_epoch=epoch,
        execution=execution,binary_sha256=binary_sha,controller_replay=controller,
        required_executed_tests=sorted(REQUIRED_TESTS),release_authority=False,
        protocol_scope='One persistent local controller domain with at most 32 resources; no distributed city authority',
        evidence_scope='Actual Rust executable and durable-fold fault tests with synthetic detector/readiness assertions; no physical qualification',
        **model.FLAGS)
    readme='\n'.join([
        '# Station launch and controller executable evidence','',
        '[Actual offline replay](replay.json) · [Compressed JSON execution transcript](executed-tests.txt.gz) · [Source/payload receipt](manifest.json)','',
        f'{len(CHECKS)} controller counterexamples and {len(REQUIRED_TESTS)} named Rust protocol tests executed successfully. The transcript retains exact commands, return codes, stdout and stderr, including the compiler artifact and binary identity.','',
        'The existing resource log now folds atomic corridor/receiving-berth/overlap preparation, a distinct launch commit, held arrivals and complete-consist bundle clearance. Permission expiry cannot free a committed arrival. Individual-clear bypass, failed partial reservation, duplicate/replayed events, persisted restart and missing/replayed tail evidence are exercised.','',
        'The controller replay exercises timestamped position/phase prediction, declared overlap and scalar force/current/voltage/loss hypotheses, zero-thrust coast and resistor-braking readiness. Physical outputs stay disabled; a fault never requests removal of onboard support.','',
        '**Limits:** one local controller and at most 32 resources, external synthetic readiness/integrity/clearance assertions, no automatic restart resumption, measured motor map, cross-car magnetic phase proof, qualified emergency brake, MCU deadline or physical I/O. Retained ownership cannot make a failed receiver work. Checksums establish record consistency, not authenticated independent acceptance. No engineering, manufacturing or physical release is claimed.',''])
    payload={'replay.json':encoded(replay),'executed-tests.txt.gz':gzip.compress(encoded(transcript),mtime=0),'README.md':readme.encode()}
    if sources()!=before or digest(binary.read_bytes())!=binary_sha:raise ValueError('station protocol sources or executable changed during execution')
    output=Path(output)
    if output.is_symlink():raise ValueError('ordinary station packet output required')
    output.mkdir(parents=True,exist_ok=True)
    if any(p.is_symlink() for p in output.iterdir()) or {p.name for p in output.iterdir()}-FILES-{'manifest.json'}:
        raise ValueError('unexpected station protocol packet inventory')
    for name,data in payload.items():
        if len(data)>MAX_FILE:raise ValueError('station packet exceeds bound')
        path=output/name;pending=path.with_suffix(path.suffix+'.pending');pending.write_bytes(data);pending.replace(path)
    manifest=dict(schema='osr-station-protocol-publication/1',source_sha256=before,source_epoch=epoch,
        execution=execution,binary_sha256=binary_sha,files_sha256={name:digest(data) for name,data in payload.items()},
        release_authority=False,**model.FLAGS)
    path=output/'manifest.json';pending=path.with_suffix('.pending');pending.write_bytes(encoded(manifest));pending.replace(path)
    return verify(output)


def _read(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size>MAX_FILE:raise ValueError('bounded ordinary station packet file required')
    return path.read_bytes()


def verify(output=OUTPUT):
    output=Path(output)
    if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()}!=FILES|{'manifest.json'}:
        raise ValueError('exact station protocol packet inventory required')
    manifest=json.loads(_read(output/'manifest.json'))
    if manifest.get('schema')!='osr-station-protocol-publication/1' or manifest.get('source_sha256')!=sources():
        raise ValueError('station protocol source identity differs')
    if set(manifest.get('files_sha256',{}))!=FILES:raise ValueError('complete station protocol payload receipts required')
    for name,expected in manifest['files_sha256'].items():
        if digest(_read(output/name))!=expected:raise ValueError('station protocol payload differs: '+name)
    replay=json.loads(_read(output/'replay.json'))
    with gzip.open(output/'executed-tests.txt.gz','rb') as stream:raw=stream.read(MAX_TRANSCRIPT+1)
    if len(raw)>MAX_TRANSCRIPT:raise ValueError('station transcript exceeds decompression bound')
    transcript=json.loads(raw);_transcript(transcript)
    _controller(replay.get('controller_replay',{}))
    execution=_execution(transcript)
    binary_sha=manifest.get('binary_sha256','')
    if not isinstance(binary_sha,str) or not re.fullmatch(r'[0-9a-f]{64}',binary_sha):raise ValueError('station binary checksum required')
    epoch=digest(encoded([manifest['source_sha256'],execution,binary_sha]))
    if (replay.get('schema')!='osr-station-protocol-evidence/1' or replay.get('source_sha256')!=manifest['source_sha256']
            or replay.get('execution')!=execution or manifest.get('execution')!=execution
            or replay.get('binary_sha256')!=binary_sha or manifest.get('source_epoch')!=epoch or replay.get('source_epoch')!=epoch
            or replay.get('required_executed_tests')!=sorted(REQUIRED_TESTS)
            or json.loads(transcript['run']['stdout'])!=replay['controller_replay']):
        raise ValueError('station evidence identity or executed transcript differs')
    if any(row.get(k) is not False for row in (manifest,replay) for k in (*model.FLAGS,'release_authority')):
        raise ValueError('station executable evidence has no release authority')
    return manifest
