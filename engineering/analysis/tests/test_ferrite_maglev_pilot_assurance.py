"""Execution and source trace must not substitute for independent acceptance."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import pytest

from engineering.ferrite_maglev import pilot_assurance as p


def test_formal_profile_executes_exact_retained_and_maglev_harnesses():
    commands = p.commands('control-formal')
    assert len(commands) == 5
    assert [r[-1] for r in commands] == [h for _,h,_ in p.PROOFS]
    assert all(r[:2] == ['cargo','kani'] for r in commands)


def test_missing_execution_is_hold_not_acceptance(tmp_path):
    value = p.study(tmp_path)
    assert all(r['digital_state'] == 'hold' for r in value['profiles'])
    assert not value['all_profiles_executed']
    assert all(value[k] is False for k in p.model.FLAGS)


def test_forged_execution_does_not_pass_current_profile(tmp_path):
    receipt = tmp_path/'receipt.json'
    receipt.write_text(json.dumps(dict(schema=p.SCHEMA, profile='control-formal',passed=True,
        source_unchanged=True, source_sha256={}, independent_acceptance=False,**p.model.FLAGS)))
    with pytest.raises(ValueError,match='stale'):
        p.verify_run(receipt,'control-formal')


def test_log_tampering_and_zero_commands_rejected(tmp_path,monkeypatch):
    monkeypatch.setattr(p,'sources',lambda profile:{'test':'a'*64})
    command=p.commands('control-formal')[0]
    monkeypatch.setattr(p,'commands',lambda profile:[command])
    log=tmp_path/'00.txt';log.write_text('1 successfully verified harnesses, 0 failures, 1 total')
    receipt=tmp_path/'receipt.json'
    data=dict(schema=p.SCHEMA,profile='control-formal',passed=True,state='passed',tool_version='fixture',source_unchanged=True,
              source_sha256=p.sources(None),independent_acceptance=False,**p.model.FLAGS,
              executions=[dict(command=command,report=log.name,report_sha256=p.digest(log),exit_code=0,passed=True)])
    receipt.write_bytes(p.encoded(data));p.verify_run(receipt,'control-formal')
    log.write_text('VERIFICATION:- SUCCESSFUL')
    with pytest.raises(ValueError,match='altered'):
        p.verify_run(receipt,'control-formal')
    data['executions']=[];receipt.write_bytes(p.encoded(data))
    with pytest.raises(ValueError,match='coverage'):
        p.verify_run(receipt,'control-formal')


def test_newer_current_failure_invalidates_older_pass(tmp_path,monkeypatch):
    monkeypatch.setattr(p,'sources',lambda profile:{'test':'a'*64})
    command=p.commands('control-formal')[0]
    monkeypatch.setattr(p,'commands',lambda profile:[command])
    passed=tmp_path/'control-formal/001';passed.mkdir(parents=True)
    log=passed/'00.txt';log.write_text('1 successfully verified harnesses, 0 failures, 1 total')
    receipt=dict(schema=p.SCHEMA,profile='control-formal',passed=True,state='passed',tool_version='fixture',source_unchanged=True,
                 source_sha256=p.sources(None),independent_acceptance=False,**p.model.FLAGS,
                 executions=[dict(command=command,report=log.name,report_sha256=p.digest(log),exit_code=0,passed=True)])
    (passed/'receipt.json').write_bytes(p.encoded(receipt))
    assert p.latest('control-formal',tmp_path)[0] is not None
    failed=tmp_path/'control-formal/002';failed.mkdir()
    (failed/'receipt.json').write_bytes(p.encoded(dict(receipt,passed=False)))
    assert p.latest('control-formal',tmp_path)==(None,None)


def test_killed_run_durably_holds_before_its_result(tmp_path,monkeypatch):
    command=[sys.executable,'-c',"print('running',flush=True); import time; time.sleep(120)"]
    monkeypatch.setattr(p,'sources',lambda profile:{'test':'a'*64})
    monkeypatch.setattr(p,'commands',lambda profile:[command])
    code="\n".join(['from engineering.ferrite_maglev import pilot_assurance as p',
        "p.sources=lambda profile:{'test':'a'*64}",
        'p.commands=lambda profile:'+repr([command]),
        'p.run("engineering",'+repr(str(tmp_path))+')'])
    worker=subprocess.Popen([sys.executable,'-c',code],cwd=p.ROOT,start_new_session=True,
                            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        deadline=time.monotonic()+10
        while time.monotonic()<deadline:
            receipts=list((tmp_path/'engineering').glob('*/receipt.json'))
            if receipts and receipts[0].with_name('00.txt').exists():
                break
            time.sleep(.05)
        assert receipts
        receipt=receipts[0]
        assert json.loads(receipt.read_bytes())['state']=='running'
        os.killpg(worker.pid,signal.SIGKILL);worker.wait(timeout=5)
        assert p.latest('engineering',tmp_path)==(None,None)
        assert json.loads(receipt.read_bytes())['passed'] is False
    finally:
        if worker.poll() is None:
            os.killpg(worker.pid,signal.SIGKILL);worker.wait(timeout=5)


def test_version_tool_unavailable_records_failure_instead_of_resurrecting_pass(tmp_path,monkeypatch):
    monkeypatch.setattr(p,'sources',lambda profile:{'test':'a'*64})
    monkeypatch.setattr(p,'commands',lambda profile:[[sys.executable,'-c',"print('executed')"]])
    def missing(*args,**kwargs):raise FileNotFoundError('version tool unavailable')
    monkeypatch.setattr(p.subprocess,'check_output',missing)
    with pytest.raises(ValueError,match='profile failed'):
        p.run('engineering',tmp_path)
    receipt=next((tmp_path/'engineering').glob('*/receipt.json'))
    result=json.loads(receipt.read_bytes())
    assert result['state']=='failed' and 'tool_version_error' in result
    assert p.latest('engineering',tmp_path)==(None,None)


def test_linked_run_and_extra_unreceipted_payload_rejected(tmp_path,monkeypatch):
    monkeypatch.setattr(p,'sources',lambda profile:{'test':'a'*64})
    command=p.commands('control-formal')[0]
    monkeypatch.setattr(p,'commands',lambda profile:[command])
    actual=tmp_path/'actual';actual.mkdir();log=actual/'00.txt'
    log.write_text('1 successfully verified harnesses, 0 failures, 1 total')
    receipt=dict(schema=p.SCHEMA,profile='control-formal',passed=True,state='passed',tool_version='fixture',source_unchanged=True,
                 source_sha256=p.sources(None),independent_acceptance=False,**p.model.FLAGS,
                 executions=[dict(command=command,report=log.name,report_sha256=p.digest(log),exit_code=0,passed=True)])
    (actual/'receipt.json').write_bytes(p.encoded(receipt));p.verify_run(actual/'receipt.json','control-formal')
    profile=tmp_path/'profiles/control-formal';profile.mkdir(parents=True)
    (profile/'002').symlink_to(actual,target_is_directory=True)
    assert p.latest('control-formal',tmp_path/'profiles')==(None,None)
    with pytest.raises(ValueError,match='ordinary'):
        p.verify_run(profile/'002/receipt.json','control-formal')
    (actual/'unreceipted.txt').write_text('outside declared inventory')
    with pytest.raises(ValueError,match='inventory'):
        p.verify_run(actual/'receipt.json','control-formal')


def test_profile_manifest_cannot_change_only_its_source_claim(tmp_path):
    p.publish(tmp_path);p.verify(tmp_path)
    m=json.loads((tmp_path/'manifest.json').read_bytes());m['source_sha256']={'forged':'a'*64}
    (tmp_path/'manifest.json').write_bytes(p.encoded(m))
    with pytest.raises(ValueError,match='execution changed'):
        p.verify(tmp_path)


def test_repeated_engineering_run_publishes_its_pending_hold_first(tmp_path,monkeypatch):
    monkeypatch.setattr(p,'RAW',tmp_path)
    monkeypatch.setattr(p,'sources',lambda profile:{'test':'a'*64})
    monkeypatch.setattr(p,'commands',lambda profile:[[sys.executable,'-c',"print('executed')"]])
    observed=[]
    def refresh():
        receipt=next((tmp_path/'engineering').glob('*/receipt.json'))
        observed.append(json.loads(receipt.read_bytes())['state'])
        assert p.latest('engineering',tmp_path)==(None,None)
    monkeypatch.setattr(p,'refresh_development_views',refresh)
    receipt=p.run('engineering',tmp_path)
    assert observed==['running']
    assert json.loads(receipt.read_bytes())['passed'] is True


def test_failed_pending_view_refresh_cannot_execute_or_resurrect_a_pass(tmp_path,monkeypatch):
    monkeypatch.setattr(p,'RAW',tmp_path)
    monkeypatch.setattr(p,'sources',lambda profile:{'test':'a'*64})
    monkeypatch.setattr(p,'commands',lambda profile:[[sys.executable,'-c',"raise AssertionError('must not run')"]])
    def stale():raise ValueError('other exact design packets stale')
    monkeypatch.setattr(p,'refresh_development_views',stale)
    with pytest.raises(ValueError,match='pending hold'):
        p.run('engineering',tmp_path)
    receipt=next((tmp_path/'engineering').glob('*/receipt.json'))
    value=json.loads(receipt.read_bytes())
    assert value['state']=='failed' and not value['executions']
    assert 'other exact design packets stale' in value['presentation_preflight_error']
    assert p.latest('engineering',tmp_path)==(None,None)


def test_rehashed_false_acceptance_readme_is_rejected(tmp_path):
    from hashlib import sha256
    p.publish(tmp_path);p.verify(tmp_path)
    (tmp_path/'README.md').write_text('All hardware accepted and released for passengers.')
    receipt=json.loads((tmp_path/'manifest.json').read_bytes())
    receipt['files_sha256']['README.md']=sha256((tmp_path/'README.md').read_bytes()).hexdigest()
    (tmp_path/'manifest.json').write_bytes(p.encoded(receipt))
    with pytest.raises(ValueError,match='execution changed'):
        p.verify(tmp_path)


def test_execution_gate_rejects_valid_but_unexecuted_presentation(tmp_path,monkeypatch):
    original=p.study()
    original['all_profiles_executed']=False
    monkeypatch.setattr(p,'study',lambda:original)
    p.publish(tmp_path);p.verify(tmp_path)
    with pytest.raises(ValueError,match='all three current'):
        p.verify(tmp_path,require_executed=True)
    original['all_profiles_executed']=True
    p.publish(tmp_path)
    p.verify(tmp_path,require_executed=True)


def test_engineering_profile_binds_launcher_lock_and_compiled_abi_inputs():
    sources=p.sources('engineering')
    assert all(name in sources for name in (
        'tools/automation/osr-python',
        'engineering/ferrite_maglev/observer-prototype/Cargo.lock',
        'engineering/ferrite_maglev/observer-prototype/include/osr_normal_wrench_observer.h',
        'engineering/ferrite_maglev/observer-prototype/tests/header-layout.c',
        'engineering/ferrite_maglev/observer-prototype/tests/differential.py'))


@pytest.mark.parametrize('kind',['oversized','symlink','ancestor'])
def test_latest_rejects_unsafe_receipt_before_opening_it(tmp_path,monkeypatch,kind):
    monkeypatch.setattr(p,'sources',lambda profile:{})
    actual=tmp_path/'actual'
    receipt=actual/'control-formal/001/receipt.json'
    receipt.parent.mkdir(parents=True)
    if kind=='oversized':
        with receipt.open('wb') as stream:stream.truncate(8*1024*1024+1)
    elif kind=='symlink':
        target=tmp_path/'external.json';target.write_text('{}')
        receipt.symlink_to(target)
    else:
        receipt.write_text('{}')
        linked=tmp_path/'linked';linked.symlink_to(actual,target_is_directory=True)
        actual=linked
        receipt=linked/'control-formal/001/receipt.json'
    original=Path.read_bytes
    def guarded(path):
        assert path!=receipt,'unsafe receipt must not be opened'
        return original(path)
    monkeypatch.setattr(Path,'read_bytes',guarded)
    assert p.latest('control-formal',actual)==(None,None)


def test_engineering_profile_runs_guards_then_both_exact_e2e_tests():
    commands=p.commands('engineering')
    prefix=['tools/automation/osr-python','-m','pytest','-q']
    tests=[path.relative_to(p.ROOT).as_posix() for path in sorted(
        (p.ROOT/'engineering/analysis/tests').glob('test_ferrite_maglev*.py'))]
    slow=('engineering/analysis/tests/test_ferrite_maglev.py::test_primary_publication_tamper_stale_and_source_binding',
          'engineering/analysis/tests/test_ferrite_maglev.py::test_scheduled_cycle_idles_without_rewriting_unchanged_results')
    assert commands[0]==prefix+tests+['--deselect='+node for node in slow]
    assert commands[1:3]==[prefix+[node] for node in slow]
    assert p.command_timeout(commands[2]) > 2*p.COLD_CYCLE_TIMEOUT_SECONDS
    assert all(p.command_timeout(command)==7200 for i,command in enumerate(commands) if i!=2)
    observer='engineering/ferrite_maglev/observer-prototype/Cargo.toml'
    assert commands[3:]==[
        ['cargo','fmt','--manifest-path',observer,'--','--check'],
        ['cargo','clippy','--locked','--manifest-path',observer,'--all-targets','--','-D','warnings'],
        ['cargo','test','--locked','--manifest-path',observer,'--all-targets'],
        ['tools/automation/osr-python','engineering/ferrite_maglev/observer-prototype/tests/differential.py'],
        ['cargo','fmt','--manifest-path','engineering/ferrite_maglev/full-dynamics-kernel/Cargo.toml','--','--check'],
        ['cargo','clippy','--locked','--manifest-path','engineering/ferrite_maglev/full-dynamics-kernel/Cargo.toml','--all-targets','--','-D','warnings'],
        ['cargo','test','--locked','--manifest-path','engineering/ferrite_maglev/full-dynamics-kernel/Cargo.toml','--all-targets'],
        ['node','tools/automation/tests/verify-planning-workspace.mjs','build/planning-browser'],
        ['cargo','fmt','--all','--','--check'],
        ['cargo','clippy','--locked','--workspace','--all-targets','--','-D','warnings'],
        ['cargo','test','--locked','--workspace','--all-targets'],
        ['cargo','check','--locked','-p','osr-maglev-control','--no-default-features']]
    # These four GSN solutions still cite the complete guard-suite command0.
    import tomllib
    case=tomllib.loads(p.CASE.read_text())
    evidence={row['id']:row['evidence']['path'] for row in case['solution']}
    for identity in ('E-PRODUCT','E-ACTUATOR','E-DELIVERY-SCHEDULE','E-CORRIDOR'):
        assert evidence[identity] in tests
        assert not any(node.startswith(evidence[identity]+'::') for node in slow)
