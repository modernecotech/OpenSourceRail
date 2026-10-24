"""Crash/restart, immutable provenance and worker-resource controls; no train run."""
from copy import deepcopy
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import pytest

from engineering.design_search import campaign as c,contracts as k,verification as v
from engineering.design_search import resource_limits as limits
from engineering.design_search.storage import atomic_immutable,ImmutableConflict


def candidate(size=1.):
    mass=size*1000.
    return k.make_candidate(requirement_revision='fixture-r1',architecture=dict(cars=6),
        frames=[dict(id='world',parent_id=None,origin_m=[0.,0.,0.],rotation_matrix=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])],
        materials=[dict(id='steel',density_kg_m3=1000.,basis='unit fixture')],
        geometry=[dict(id='box',kind='box',frame_id='world',material_id='steel',at_m=[0.,0.,0.],size_m=[size,1.,1.])],interfaces=[],
        installed_inventory=[dict(id='box',geometry_id='box',frame_id='world',quantity=1,status='known',scope='vehicle-per-car',basis='fixture',
            unit_mass_kg=mass,cg_m=[size/2,.5,.5],inertia_kg_m2=[[mass/6,0.,0.],[0.,mass*(size**2+1)/12,0.],[0.,0.,mass*(size**2+1)/12]])])


def request_for(value,name='definition',**kw):
    return k.make_evaluation_request(value,evaluator_id=name,evaluator_sources={'engineering/design_search/verification.py':sha256(Path(v.__file__).read_bytes()).hexdigest()},**kw)


def primary(value=None,execution='executed',cost=1.):
    value=candidate() if value is None else value
    return k.make_result(request_for(value),execution_status=execution,numerical_status='converged' if execution=='executed' else 'unknown',
        screen_status='fail' if execution=='executed' else 'unknown',metrics=dict(cost=cost))


def resource_receipt(budget):
    return dict(memory_limit_bytes=budget['memory_mb']*1024**2,cpu_limit_s=math.ceil(budget['job_timeout_s'])+1,
        file_limit_bytes=64*1024**2,watchdog_process_group_cleanup=False,limits_before_domain_import=True)


def test_initial_family_and_requirements_cannot_be_erased_or_replaced():
    value=candidate();context=k.identity(value)
    definition=dict(candidate_context_ids=[context],specification=dict(requirement_revision='fixture-r1',budget=dict(max_candidates=2)))
    c._candidate_membership(definition,[value],[context])
    for values,contexts in [([],[]),([value,value],[context,context])]:
        with pytest.raises(ValueError,match='membership'):c._candidate_membership(definition,values,contexts)
    other=k.bind_context(value,requirement_revision='foreign')
    with pytest.raises(ValueError,match='membership'):c._candidate_membership(definition,[other],[context])


def prepare_attempt(value,request,attempt,budget,*,mode='evaluate',original=None,seal=True):
    attempt=Path(attempt);(attempt/'input').mkdir(parents=True);(attempt/'output').mkdir()
    c._exclusive(attempt/'input/job.json',dict(candidate=value,request=request,mode=mode,primary=original,
        worker_limits=dict(memory_mb=budget['memory_mb'],timeout_s=budget['job_timeout_s'])))
    c._exclusive(attempt/'launch.json',dict(pid=99999999,start_token=None,sandbox_requested=False))
    result=k.make_result(request,execution_status='executed',numerical_status='converged',screen_status='pass' if mode=='verify' else 'fail',metrics=dict(cost=1.))
    c._exclusive(attempt/'output/result.json',result);c._exclusive(attempt/'output/resource-limits.json',resource_receipt(budget))
    (attempt/'stdout.txt').write_text('fixture\n');(attempt/'stderr.txt').write_text('')
    record=c._seal(attempt,value,request,result,duration_s=.01,sandbox=False) if seal else None
    return result,record


@pytest.fixture
def setup_campaign(tmp_path,monkeypatch):
    values=[candidate(1.),candidate(1.2)]
    monkeypatch.setattr(c,'catalogue',lambda:dict(definition=dict(id='definition',dependencies=[])))
    monkeypatch.setattr(c,'source_epoch',lambda:dict(fixture='a'*64))
    monkeypatch.setattr(c.families,'initial_families',lambda **kw:deepcopy(values))
    monkeypatch.setattr(c.families,'propose_revision',lambda *a,**kw:None)
    monkeypatch.setattr(c,'sandbox_available',lambda:False)
    monkeypatch.setattr(c,'_write',lambda path,value:Path(path).write_text(json.dumps(value)))
    from engineering.design_search import evaluators
    monkeypatch.setattr(evaluators,'request_for',request_for)
    spec=tmp_path/'campaign.toml';spec.write_text('''schema="osr-design-campaign/1"
requirement_revision="fixture-r1"
requirement_ids=["R1"]
purpose="next-experiment"
evaluators=["definition"]
[budget]
max_candidates=2
max_generations=1
max_workers=1
job_timeout_s=3
total_runtime_s=30
memory_mb=256
[policy]
policy_id="fixture-policy"
[policy.objectives]
cost=1.0
''')
    state=tmp_path/'state';definition=c.create(spec,state=state);calls=[]
    def execute(value,request,attempt,budget,**kw):
        calls.append((value['candidate_id'],request['purpose']))
        return prepare_attempt(value,request,attempt,budget,mode=kw.get('mode','evaluate'),original=kw.get('primary'))
    monkeypatch.setattr(c,'execute',execute)
    return state,definition,calls,values


def test_interruption_resume_reuses_exact_completed_failures_and_journals_verifier(setup_campaign):
    state,definition,calls,_=setup_campaign;identity=definition['campaign_id']
    assert c.run(identity,state=state,max_jobs=1)['state']=='interrupted'
    assert c.run(identity,state=state,max_jobs=1)['state']=='interrupted'
    result=c.run(identity,state=state,max_jobs=1)
    assert result['state']=='completed' and len(calls)==3
    assert sum(job['role']=='verifier' for job in result['jobs'].values())==1
    assert result['completed_engineering_failures']==2
    assert c.run(identity,state=state)['state']=='completed' and len(calls)==3
    comparison=c.compare(identity,state=state)
    assert comparison['integrated_baseline']['selected_candidate_id'] is None
    assert comparison['next_experiment']['selected_candidate_id'] is not None


def test_comparison_recomputes_selection_even_after_rehash(setup_campaign):
    state,definition,_,_=setup_campaign;identity=definition['campaign_id'];c.run(identity,state=state)
    path=state/'campaigns'/identity/'comparison.json';value=json.loads(path.read_bytes())
    value['next_experiment']['selected_candidate_id']='f'*64
    value['comparison_sha256']=k.identity({key:item for key,item in value.items() if key!='comparison_sha256'})
    path.write_bytes(k.encoded(value))
    with pytest.raises(ValueError,match='selection'):c.compare(identity,state=state)


def test_comparison_cannot_promote_requirement_dispositions(setup_campaign):
    state,definition,_,_=setup_campaign;identity=definition['campaign_id'];c.run(identity,state=state)
    path=state/'campaigns'/identity/'comparison.json';value=json.loads(path.read_bytes())
    value['qualification']['physical_accepted']=True
    value['comparison_sha256']=k.identity({key:item for key,item in value.items() if key!='comparison_sha256'});path.write_bytes(k.encoded(value))
    with pytest.raises(ValueError,match='physical requirement'):c.compare(identity,state=state)


def test_cached_result_requires_unchanged_sealed_attempt_payload(setup_campaign):
    state,definition,_,_=setup_campaign;identity=definition['campaign_id'];c.run(identity,state=state,max_jobs=1)
    path=next((state/'campaigns'/identity/'attempts').glob('*/*/stdout.txt'));path.write_text('modified log')
    with pytest.raises(ValueError,match='payload bytes'):c.run(identity,state=state,max_jobs=1)


def test_finished_orphan_is_recovered_without_duplicate_evaluation(setup_campaign):
    state,definition,calls,values=setup_campaign;identity=definition['campaign_id'];folder=state/'campaigns'/identity
    value=values[0];request=request_for(value,purpose='diagnostic',hypothesis={},scenario={},settings=dict(coupling_context_id=k.identity(dict(candidate_id=value['candidate_id'],requirements='fixture-r1',scenario={}))))
    attempt=folder/'attempts'/request['evaluation_id']/'orphan'
    prepare_attempt(value,request,attempt,dict(memory_mb=256,job_timeout_s=3),seal=False)
    journal=dict(schema='osr-digital-execution-graph/1',campaign_id=identity,state='running',candidate_context_ids=definition['candidate_context_ids'],generations=[],
        jobs={request['evaluation_id']:dict(candidate_id=value['candidate_id'],evaluation_id=request['evaluation_id'],evaluator_id='definition',purpose='diagnostic',role='definition',state='running',attempts=[attempt.relative_to(folder).as_posix()])},
        runtime_used_s=0.,active_runtime_lease=dict(reserved_s=3.,id='orphan'),physical_requirement_dispositions_changed=False,physical_accepted=False)
    (folder/'journal.json').write_text(json.dumps(journal));result=c.run(identity,state=state,max_jobs=1)
    assert result['jobs'][request['evaluation_id']]['last_attempt']['recovered_after_coordinator_interruption']
    assert not any(candidate_id==value['candidate_id'] and purpose!='confirmation' for candidate_id,purpose in calls)
    assert result['runtime_used_s']>=3.


def test_runtime_budget_is_cumulative_and_charges_crashed_reservation(monkeypatch):
    clock=[0.];monkeypatch.setattr(c,'time',type('Clock',(),dict(monotonic=staticmethod(lambda:clock[0]),time=staticmethod(lambda:clock[0]))))
    journal={};budget=c._RuntimeBudget(journal,dict(total_runtime_s=3),lambda:None)
    assert budget.reserve(2)==2;clock[0]=1.25;budget.settle()
    resumed=c._RuntimeBudget(journal,dict(total_runtime_s=3),lambda:None)
    assert resumed.remaining()==pytest.approx(1.75)
    assert resumed.reserve(2)==1;clock[0]+=0.1
    crashed=c._RuntimeBudget(journal,dict(total_runtime_s=3),lambda:None)
    assert crashed.remaining()==pytest.approx(.75)
    assert crashed.reserve(2) is None
    assert journal['abandoned_runtime_leases'][0]['charged_s']==1


def test_confirmation_identity_binds_primary_result_payload():
    value=candidate();a=primary(value,cost=1.);b=primary(value,cost=2.)
    assert a['evaluation_id']==b['evaluation_id'] and a['result_sha256']!=b['result_sha256']
    assert v.request_for(value,a)['evaluation_id']!=v.request_for(value,b)['evaluation_id']


def test_atomic_immutable_install_does_not_publish_partial_bytes(tmp_path,monkeypatch):
    import engineering.design_search.storage as storage
    path=tmp_path/'record.json';actual=os.link
    def crash(*args,**kwargs):raise OSError('interrupted before atomic install')
    monkeypatch.setattr(storage.os,'link',crash)
    with pytest.raises(OSError):atomic_immutable(path,b'complete')
    assert not path.exists() and not list(tmp_path.glob('*.pending'))
    monkeypatch.setattr(storage.os,'link',actual);atomic_immutable(path,b'complete');atomic_immutable(path,b'complete')
    with pytest.raises(ImmutableConflict):atomic_immutable(path,b'other')


def test_nested_attempt_named_file_is_not_exempt_from_integrity(tmp_path):
    value=candidate();request=request_for(value);attempt=tmp_path/'attempt'
    prepare_attempt(value,request,attempt,dict(memory_mb=256,job_timeout_s=3))
    (attempt/'output/attempt.json').write_text('extra file')
    with pytest.raises(ValueError,match='payload bytes'):c._validate_attempt(attempt,request)


def test_worker_status_mapping_keeps_engineering_failures_completed():
    assert c._terminal('executed')==c._terminal('refused')=='completed'
    assert c._terminal('interrupted')=='interrupted'
    assert c._terminal('error')==c._terminal('running')=='tool-error'


def test_process_group_timeout_also_kills_sleeping_descendant(tmp_path,monkeypatch):
    value=candidate();request=request_for(value);attempt=tmp_path/'attempt'
    child=tmp_path/'child.py';pidfile=tmp_path/'child.pid'
    child.write_text('import subprocess,sys,time\np=subprocess.Popen([sys.executable,"-c","import time;time.sleep(60)"])\nopen(sys.argv[1],"w").write(str(p.pid))\ntime.sleep(60)\n')
    monkeypatch.setattr(c,'_worker_command',lambda *args:[sys.executable,str(child),str(pidfile)])
    result,record=c.execute(value,request,attempt,dict(memory_mb=256,job_timeout_s=.3))
    assert result['execution_status']=='interrupted' and record['state']=='interrupted'
    pid=int(pidfile.read_text());stat=Path(f'/proc/{pid}/stat')
    assert not stat.exists() or stat.read_text().split(')')[-1].strip().startswith('Z')
    assert not record['os_read_only_input_enforced'] and not record['network_isolated']


def test_limits_bootstrap_is_stdlib_and_worker_does_not_import_campaign():
    worker=Path(c.__file__).with_name('worker.py').read_text()
    assert 'from .campaign' not in worker
    assert worker.index('from .resource_limits import apply')<worker.index('from . import contracts')


@pytest.mark.parametrize('execution,expected',[('interrupted','interrupted'),('error','tool-error')])
def test_exit_zero_cannot_promote_typed_worker_interruption(tmp_path,monkeypatch,execution,expected):
    script=tmp_path/'terminal.py'
    script.write_text('''import json,sys,os
from pathlib import Path
from engineering.design_search.resource_limits import apply
limits=apply(256,3)
from engineering.design_search import contracts
from engineering.design_search.storage import atomic_immutable
job=json.loads(Path(sys.argv[1]).read_bytes());output=Path(sys.argv[2])
atomic_immutable(output.parent/'resource-limits.json',(json.dumps(limits)+'\\n').encode())
value=contracts.make_result(job['request'],execution_status=sys.argv[3],numerical_status='unknown',screen_status='unknown')
atomic_immutable(output,contracts.encoded(value))
''')
    monkeypatch.setattr(c,'_worker_command',lambda inputs,outputs,*args:[sys.executable,str(script),str(inputs/'job.json'),str(outputs/'result.json'),execution])
    value=candidate();result,record=c.execute(value,request_for(value),tmp_path/'attempt',dict(memory_mb=256,job_timeout_s=3))
    assert result['execution_status']==execution and record['state']==expected
    assert record['resource_limits']['limits_before_domain_import']
    assert record['resource_limits']['watchdog_process_group_cleanup']


def test_parent_death_watchdog_cleans_worker_and_descendant(tmp_path):
    pidfile=tmp_path/'worker-pids.json';worker=tmp_path/'watchdog-worker.py';coordinator=tmp_path/'coordinator.py'
    worker.write_text('''import json,os,subprocess,sys,time
from pathlib import Path
from engineering.design_search.resource_limits import apply
apply(256,5,parent_pid=int(sys.argv[1]),parent_start=sys.argv[2])
child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'])
Path(sys.argv[3]).write_text(json.dumps([os.getpid(),child.pid]))
time.sleep(60)
''')
    coordinator.write_text('''import os,subprocess,sys,time
from engineering.design_search.resource_limits import process_start
subprocess.Popen([sys.executable,sys.argv[1],str(os.getpid()),process_start(os.getpid()),sys.argv[2]],start_new_session=True)
time.sleep(60)
''')
    env=dict(os.environ,PYTHONPATH=str(c.ROOT),PYTHONDONTWRITEBYTECODE='1')
    process=subprocess.Popen([sys.executable,str(coordinator),str(worker),str(pidfile)],env=env,start_new_session=True)
    group=None
    try:
        deadline=time.monotonic()+5
        while not pidfile.is_file() and time.monotonic()<deadline:time.sleep(.02)
        assert pidfile.is_file()
        group,child=json.loads(pidfile.read_bytes());process.kill();process.wait(timeout=2)
        deadline=time.monotonic()+3
        while limits.group_members(group) and time.monotonic()<deadline:time.sleep(.02)
        assert not limits.group_members(group)
    finally:
        if process.poll() is None:process.kill();process.wait(timeout=2)
        if group is not None:limits.stop_group(group)


def test_bwrap_read_only_input_and_pid_namespace_when_available(tmp_path):
    if not c.sandbox_available():pytest.skip('OS cannot create nested bubblewrap PID/network namespaces; fallback remains explicitly unenforced')
    inputs=tmp_path/'input';outputs=tmp_path/'output';inputs.mkdir();outputs.mkdir();source=inputs/'immutable.txt';source.write_text('original')
    code='''from pathlib import Path
import sys
try:Path(sys.argv[1]).write_text('changed')
except OSError:Path(sys.argv[2]).write_text('read-only-enforced')
'''
    command=['bwrap','--ro-bind','/','/','--proc','/proc','--dev','/dev','--unshare-net','--unshare-pid','--die-with-parent',
        '--ro-bind',str(inputs),str(inputs),'--bind',str(outputs),str(outputs),'--',sys.executable,'-c',code,str(source),str(outputs/'result.txt')]
    result=subprocess.run(command,capture_output=True,timeout=5)
    assert result.returncode==0,result.stderr.decode()
    assert source.read_text()=='original' and (outputs/'result.txt').read_text()=='read-only-enforced'
