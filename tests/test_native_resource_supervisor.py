"""No Docker mutations: pure counters, scripted daemon and tiny child processes."""
from dataclasses import replace
from importlib.util import spec_from_file_location,module_from_spec
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import time
import textwrap
import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=spec_from_file_location('native_resource_supervisor_test',ROOT/'tools/automation/native-v06/resource_supervisor.py')
m=module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
OWNER='osr-v06-a123456789ab'


def limits():return m.Limits(1000,15,1024**3,2*1024**2,1,interval_seconds=.1,probe_seconds=1,shutdown_seconds=1)


@pytest.mark.parametrize('field',['cpu_seconds','elapsed_seconds','rss_bytes','disk_bytes','host_reserve_bytes'])
def test_limits_must_be_explicit_positive_and_finite(field):
    for value in (0,-1,True,float('nan'),float('inf')):
        with pytest.raises(m.Hold):replace(limits(),**{field:value})


def test_aggregate_counters_preserve_exited_generations_and_include_supervisor():
    a=m.Accounting(limits(),hz=100,page=4096)
    first=a.sample({'a':dict(ticks=100,rss_pages=100),'supervisor':dict(ticks=50,rss_pages=50)},elapsed=1,disk=123,free=999)
    second=a.sample({'b':dict(ticks=200,rss_pages=200),'supervisor':dict(ticks=75,rss_pages=50)},elapsed=2,disk=200,free=999,extra_cpu=.5)
    assert first['cpu_charged_s']==1.5 and second['cpu_charged_s']==4.25
    assert second['rss_bytes']==250*4096 and second['peak_disk_bytes']==200
    with pytest.raises(m.Hold):a.sample({'b':dict(ticks=199,rss_pages=1)},elapsed=3,disk=1,free=99)


def test_docker_exec_exit_does_not_drop_lifetime_cpu_or_confuse_pid_reuse():
    a=m.Accounting(limits(),hz=100,page=4096)
    def row(pid,start,ticks):return dict(pid=pid,start=start,ticks=ticks)
    a.sample({'container':dict(ticks=200,rss_pages=2,processes=[row(1,100,100),row(2,200,100)])},elapsed=1,disk=0,free=100)
    result=a.sample({'container':dict(ticks=100,rss_pages=1,processes=[row(1,100,100)])},elapsed=2,disk=0,free=100)
    assert result['cpu_charged_s']==2 and result['rss_bytes']==4096
    result=a.sample({'container':dict(ticks=150,rss_pages=2,processes=[row(1,100,100),row(2,300,50)])},elapsed=3,disk=0,free=100)
    assert result['cpu_charged_s']==2.5


def test_event_ledger_authenticates_generation_and_charges_short_exec_cpu(monkeypatch):
    monkeypatch.setattr(m.os,'cpu_count',lambda:4);ledger=m.Events(OWNER);now=time.time()-2;observed={}
    def event(action,stamp,**attrs):return dict(Type='container',Action=action,timeNano=int(stamp*10**9),Actor=dict(ID='cid',Attributes={m.LABEL:OWNER,**attrs}))
    ledger.accept(event('start',now),observed);observed['cid']=now+.5
    ledger.accept(event('exec_start: python',now+.6,execID='abc'),observed)
    ledger.accept(event('exec_die',now+.8,execID='abc'),observed)
    ledger.accept(event('die',now+1),observed)
    assert ledger.cpu_upper_s==pytest.approx(2.8) and not ledger.execs
    with pytest.raises(m.Hold):ledger.accept(event('exec_die',now+1.1,execID='unknown'),observed)
    ledger.accept(event('start',now+1.2),observed)
    with pytest.raises(m.Hold,match='without authenticated'):ledger.accept(event('die',now+1.3),observed)


@pytest.mark.parametrize('change,expected',[(dict(elapsed=16),'elapsed'),(dict(disk=3*1024**2),'disk'),(dict(free=0),'host-disk-reserve')])
def test_every_aggregate_limit_holds(change,expected):
    a=m.Accounting(limits());kwargs=dict(elapsed=1,disk=0,free=100);kwargs.update(change)
    assert expected in a.sample({},**kwargs)['violations']
    assert 'cpu' in a.sample({'x':dict(ticks=1001*a.hz,rss_pages=0)},elapsed=1,disk=0,free=100)['violations']
    assert 'rss' in a.sample({'x':dict(ticks=1001*a.hz,rss_pages=1024**3//a.page+1)},elapsed=1,disk=0,free=100)['violations']


def test_resource_ownership_requires_exact_labels_and_names():
    rows=[('container',dict(Name=OWNER+'-backend-1',Labels={m.LABEL:OWNER,m.PROJECT:OWNER})),
        ('volume',dict(Name=OWNER+'_sites',Labels={m.LABEL:OWNER,m.PROJECT:OWNER})),
        ('volume',dict(Name=OWNER+'-integration',Labels={m.LABEL:OWNER})),
        ('network',dict(Name=OWNER+'_default',Labels={m.PROJECT:OWNER}))]
    for kind,row in rows:
        assert m.owned(kind,row,OWNER)==row
        with pytest.raises(m.Hold):m.owned(kind,dict(row,Labels={m.LABEL:'another-project',m.PROJECT:OWNER}),OWNER)
        with pytest.raises(m.Hold):m.owned(kind,dict(row,Name='unrelated-resource'),OWNER)
    for invalid in ('osr-v06-other','../global','osr-v06-A123456789ab'):
        with pytest.raises(m.Hold):m.owner_id(invalid)


def test_allocated_disk_does_not_follow_symlinks_or_double_count_hardlinks(tmp_path):
    data=tmp_path/'data';data.mkdir();file=data/'file';file.write_bytes(b'x'*8192)
    os.link(file,data/'hardlink');outside=tmp_path/'outside';outside.write_bytes(b'x'*200000)
    (data/'link').symlink_to(outside)
    expected=sum(p.lstat().st_blocks*512 for p in (data,file,data/'link'))
    assert m.allocated(data)==expected
    with pytest.raises(m.Hold):m.allocated(data,deadline=time.monotonic()-1)


def test_real_proc_birth_cpu_and_rss_are_read_without_claiming_cgroups():
    row=m.process_stat(os.getpid());tree=m.process_tree(os.getpid())
    assert row['pid']==os.getpid() and row['rss_pages']>0 and row['start']>0
    assert tree[os.getpid()]['start']==row['start']


def test_storage_capability_probe_uses_native_go_template_field_spelling(tmp_path):
    d=m.Docker(OWNER,tmp_path);commands=[]
    def call(args,**kwargs):
        commands.append(args)
        return json.dumps(dict(DockerRootDir=str(tmp_path),MemoryLimit=False,CpuCfsQuota=False,CgroupVersion='2',NCPU=12,ServerVersion='29.8.0'))
    d.call=call
    assert d.storage_roots()==[tmp_path]
    assert '.CPUCfsQuota' in commands[0][-1] and '.CpuCfsQuota' not in commands[0][-1]
    assert not json.loads((tmp_path/'docker-capabilities.json').read_bytes())['MemoryLimit']


class ScriptedCleanup(m.Docker):
    def __init__(self,folder):
        super().__init__(OWNER,folder);self.commands=[];self.removed=[]
    def inventory(self):return dict(container=[v for v in ('good','conflicting') if v not in self.removed],volume=[],network=[])
    def call(self,args,**kwargs):
        self.commands.append(args)
        if args[0]=='inspect':
            name=args[-1];return json.dumps(dict(Id=name,Name=OWNER+'-'+name,Labels={m.LABEL:OWNER if name=='good' else 'unrelated-owner'}))+'\n'
        if args[:2]==['rm','-f']:self.removed.append(args[-1])
        return ''


def test_cleanup_rechecks_labels_and_never_mutates_conflicting_or_shared_resources(tmp_path):
    d=ScriptedCleanup(tmp_path);result=d.cleanup()
    assert d.removed==['good'] and not result['verified']
    assert all('prune' not in c and not(c[0]=='image' and 'rm' in c) for c in d.commands)
    assert not any(c[:2]==['rm','-f'] and c[-1]=='conflicting' for c in d.commands)


class MetricsDocker(m.Docker):
    def __init__(self,folder,*,top_ok=True,with_volume=False,size=True):
        super().__init__(OWNER,folder);self.top_ok=top_ok;self.with_volume=with_volume;self.commands=[];self.size=size
    def inventory(self):return dict(container=['cid'],volume=[OWNER+'_sites'] if self.with_volume else [],network=[])
    def call(self,args,**kwargs):
        self.commands.append(args)
        if args[0]=='inspect':
            row=dict(Id='cid',Name=OWNER+'-backend-1',Labels={m.LABEL:OWNER},State=dict(Running=True,Pid=os.getpid(),StartedAt='START'),
                Mounts=[dict(Type='volume',Name=OWNER+'_sites',Destination='/sites')] if self.with_volume else [],LogType='none',LogPath='',Image='cached')
            if self.size:row['SizeRw']=10
            return json.dumps(row)+'\n'
        if args[:2]==['volume','inspect']:return json.dumps(dict(Name=OWNER+'_sites',Labels={m.LABEL:OWNER},Mountpoint='/inaccessible'))+'\n'
        if args[0]=='top':return 'PID PPID\n'+str(os.getpid() if self.top_ok else 1)+' 0\n'
        if args[0]=='exec':return '4096\t/sites\n'
        raise AssertionError(args)


@pytest.mark.parametrize('failure',['pid-set','missing-process','zero-rss','missing-layer'])
def test_required_container_telemetry_never_silently_becomes_zero(tmp_path,monkeypatch,failure):
    d=MetricsDocker(tmp_path,top_ok=failure!='pid-set',size=failure!='missing-layer')
    if failure=='missing-process':monkeypatch.setattr(m,'process_stat',lambda pid:(_ for _ in ()).throw(PermissionError('hidden')))
    if failure=='zero-rss':monkeypatch.setattr(m,'process_stat',lambda pid:dict(pid=pid,ppid=0,start=1,ticks=1,rss_pages=0))
    with pytest.raises(m.Hold):d.metrics()
    assert not any(c[0] in ('run','rm','kill') for c in d.commands)


def test_volume_fallback_reads_only_verified_existing_container_and_charges_helper_cpu(tmp_path,monkeypatch):
    d=MetricsDocker(tmp_path,with_volume=True)
    monkeypatch.setattr(m,'allocated',lambda path,**kw:(_ for _ in ()).throw(PermissionError('mapped uid')))
    result=d.metrics()
    assert result['owned_docker_disk_bytes']==4106 and d.helper_cpu_upper_s>0
    assert ['exec','--user','0','cid','du','-sx','--block-size=1','--','/sites'] in d.commands
    assert not any(c[0]=='run' for c in d.commands)


def test_anonymous_volume_is_neither_free_disk_nor_successful_cleanup(tmp_path):
    d=MetricsDocker(tmp_path,with_volume=True)
    d.inventory=lambda:dict(container=['cid'],volume=[],network=[])
    with pytest.raises(m.Hold,match='Unlabelled'):d.metrics()
    assert d.unaccounted_volumes=={OWNER+'_sites'}


def test_writable_host_bind_outside_private_budget_is_refused(tmp_path):
    d=MetricsDocker(tmp_path);original=d.call
    def call(args,**kwargs):
        raw=original(args,**kwargs)
        if args[0]=='inspect':
            row=json.loads(raw);row['Mounts']=[dict(Type='bind',RW=True,Source='/unrelated/shared/data')];return json.dumps(row)+'\n'
        return raw
    d.call=call
    with pytest.raises(m.Hold,match='Writable host bind'):d.metrics()


class FakeEvents:
    def __init__(self):self.read,self.write=os.pipe();self.stdout=os.fdopen(self.read,'rb',buffering=0);self.returncode=None
    def poll(self):return self.returncode
    def terminate(self):self.returncode=0;os.close(self.write)
    def kill(self):self.terminate()
    def wait(self,**kwargs):return self.returncode


class FakeDocker:
    helper_cpu_upper_s=0.
    def __init__(self,folder,*,collision=False,cleanup_ok=True,interrupt=None):
        self.folder=folder;self.collision=collision;self.cleanup_ok=cleanup_ok;self.cleaned=False;self.interrupt=interrupt
    def inventory(self):return dict(container=['pre-existing'] if self.collision else [],volume=[],network=[])
    def images(self):return {'sha256:cached-image':123}
    def storage_roots(self):return []
    def metrics(self,**kwargs):
        if self.interrupt:self.interrupt()
        return dict(inventory=self.inventory(),containers=[],groups={},owned_docker_disk_bytes=0)
    def cleanup(self):
        self.cleaned=True;result=dict(owner=OWNER,remaining=dict(container=[],volume=[],network=[]),errors=[],verified=self.cleanup_ok)
        m.write(self.folder/'supervisor-cleanup.json',result);return result


def popen_factory(monkeypatch):
    real=subprocess.Popen
    monkeypatch.setattr(m.subprocess,'Popen',lambda argv,**kw:FakeEvents() if argv[:2]==['docker','events'] else real(argv,**kw))


def child(*,status=0,sleep=0):
    code="import os,sys,time;sys.path.insert(0,"+repr(str(ROOT/'tools/automation/native-v06'))+");from resource_supervisor import require_binding;require_binding(os.environ['OSR_NATIVE_OWNER'],os.environ['OSR_NATIVE_PRIVATE_DIR']);print('fixture stdout',flush=True);print('fixture stderr',file=sys.stderr,flush=True);time.sleep("+str(sleep)+");sys.exit("+str(status)+")"
    return [sys.executable,'-c',code]


def test_wrapper_records_stdout_exit_own_metrics_and_requires_verified_cleanup(tmp_path,monkeypatch):
    popen_factory(monkeypatch);folder=tmp_path/'success';backend=FakeDocker(folder)
    result=m.supervise(OWNER,folder,limits(),child(),backend=backend)
    assert result['execution']=='completed' and result['child_exit']==0 and backend.cleaned
    assert (folder/'child.stdout').read_text()=='fixture stdout\n' and (folder/'child.stderr').read_text()=='fixture stderr\n'
    assert result['final_accounting']['rss_bytes']>0 and result['final_accounting']['disk_bytes']>=65536
    assert all(result[k] is False for k in m.FLAGS)


@pytest.mark.parametrize('separate_session',[False,True])
def test_native_leader_exit_does_not_leave_observed_host_grandchildren(tmp_path,monkeypatch,separate_session):
    popen_factory(monkeypatch);folder=tmp_path/'orphan';backend=FakeDocker(folder)
    code="import os,sys,time,subprocess;sys.path.insert(0,"+repr(str(ROOT/'tools/automation/native-v06'))+");from resource_supervisor import require_binding;require_binding(os.environ['OSR_NATIVE_OWNER'],os.environ['OSR_NATIVE_PRIVATE_DIR']);p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(20)'],start_new_session="+str(separate_session)+");print(p.pid,flush=True);time.sleep(.35)"
    result=m.supervise(OWNER,folder,limits(),[sys.executable,'-c',code],backend=backend)
    assert result['host_process_cleanup']['verified'] and result['host_process_cleanup']['descendants']['verified']
    pid=int((folder/'child.stdout').read_text())
    reaped=next(row for row in result['host_process_cleanup']['adoption']['adopted_reaped'] if row['pid']==pid)
    try:row=m.process_stat(pid)
    except FileNotFoundError:return
    assert row['start']!=reaped['start']


def test_reused_or_unrelated_pid_birth_is_never_signalled(monkeypatch):
    current=m.process_stat(os.getpid())
    monkeypatch.setattr(m.signal,'pidfd_send_signal',lambda *a:(_ for _ in ()).throw(AssertionError('Unrelated PID signalled')))
    with pytest.raises(m.Hold,match='birth/adoption'):
        m._signal_child(dict(current,start=current['start']+1),signal.SIGTERM)


@pytest.mark.parametrize('new_session,double_fork',[(False,False),(True,False),(True,True)])
def test_native_exit_before_first_sample_adopts_kills_and_reaps_every_orphan(tmp_path,monkeypatch,new_session,double_fork):
    popen_factory(monkeypatch);folder=tmp_path/'early-orphan';backend=FakeDocker(folder)
    original=backend.metrics;calls=[]
    def delayed(**kwargs):
        if not calls:
            deadline=time.monotonic()+2
            while time.monotonic()<deadline:
                report=folder/'child-reaper.json'
                try:
                    if json.loads(report.read_bytes()).get('native_reaped'):break
                except (FileNotFoundError,json.JSONDecodeError):pass
                time.sleep(.01)
            assert report.is_file() and json.loads(report.read_bytes())['native_reaped']
        calls.append(True);return original(**kwargs)
    backend.metrics=delayed
    code=textwrap.dedent('''
        import json,os,sys,time
        sys.path.insert(0,MODPATH)
        from resource_supervisor import require_binding,process_stat
        require_binding(os.environ['OSR_NATIVE_OWNER'],os.environ['OSR_NATIVE_PRIVATE_DIR'])
        read,write=os.pipe()
        first=os.fork()
        if first==0:
            os.close(read)
            if NEWSESSION:os.setsid()
            if DOUBLEFORK:
                second=os.fork()
                if second:os._exit(0)
            row=process_stat(os.getpid())
            os.write(write,(json.dumps({'pid':row['pid'],'start':row['start']})+'\\n').encode())
            os.close(write)
            time.sleep(20)
            os._exit(0)
        os.close(write)
        result=b''
        while not result.endswith(b'\\n'):result+=os.read(read,1024)
        os.close(read)
        print(result.decode().strip(),flush=True)
        os._exit(0)
    ''').replace('MODPATH',repr(str(ROOT/'tools/automation/native-v06'))).replace('NEWSESSION',str(new_session)).replace('DOUBLEFORK',str(double_fork))
    result=m.supervise(OWNER,folder,limits(),[sys.executable,'-c',code],backend=backend)
    orphan=json.loads((folder/'child.stdout').read_text());adoption=result['host_process_cleanup']['adoption']
    assert result['execution']=='completed' and result['child_exit']==0
    assert adoption['capabilities']['verified_before_launch'] and adoption['native_reaped']
    assert result['host_process_cleanup']['worker_reaped']
    assert not adoption['remaining_direct_children']
    reaped=next(row for row in adoption['adopted_reaped'] if row['pid']==orphan['pid'] and row['start']==orphan['start'])
    assert os.WIFSIGNALED(reaped['wait_status'])
    try:remaining=m.process_stat(orphan['pid'])
    except FileNotFoundError:return
    assert remaining['start']!=orphan['start']  # Reaped, never merely a zombie.


def test_dedicated_reaper_cannot_consume_unrelated_or_probe_popen_wait_status(tmp_path,monkeypatch):
    popen_factory(monkeypatch);folder=tmp_path/'unrelated';backend=FakeDocker(folder);original=backend.metrics;probes=[]
    def metrics(**kwargs):
        probes.append(subprocess.run([sys.executable,'-c','raise SystemExit(23)']).returncode)
        return original(**kwargs)
    backend.metrics=metrics
    unrelated=subprocess.Popen([sys.executable,'-c','import time;time.sleep(.1);raise SystemExit(17)'])
    try:
        result=m.supervise(OWNER,folder,limits(),child(sleep=.25),backend=backend)
        assert result['execution']=='completed' and unrelated.wait(timeout=2)==17
        assert probes and all(code==23 for code in probes)
    finally:
        if unrelated.poll() is None:unrelated.terminate();unrelated.wait(timeout=2)


def test_subreaper_capability_failure_is_closed_before_launch(monkeypatch):
    monkeypatch.setattr(m,'waitability',lambda **kwargs:dict(verified=True))
    monkeypatch.setattr(m.sys,'platform','unsupported')
    with pytest.raises(m.Hold,match='Verified Linux'):m._reaper_capabilities(os.getpid(),m.process_stat(os.getpid())['start'])
    monkeypatch.setattr(m.sys,'platform','linux');calls=[]
    monkeypatch.setattr(m,'_prctl',lambda *a:calls.append(a))  # GET deliberately leaves flags unset.
    with pytest.raises(m.Hold,match='could not be verified'):m._reaper_capabilities(os.getpid(),m.process_stat(os.getpid())['start'])
    assert calls


def test_worker_capability_refusal_launches_no_native_command(tmp_path,monkeypatch):
    m.write(tmp_path/'reaper-config.json',dict(owner=OWNER,parent_pid=os.getpid(),parent_birth=m.process_stat(os.getpid())['start'],
        source_sha256='a'*64,command=['must-not-run'],shutdown_seconds=1))
    monkeypatch.setattr(m,'_direct_children',lambda:[])
    monkeypatch.setattr(m,'_reaper_capabilities',lambda *a:(_ for _ in ()).throw(m.Hold('Unsupported adoption')))
    monkeypatch.setattr(m.signal,'signal',lambda *a:None)
    monkeypatch.setattr(m.subprocess,'Popen',lambda *a,**kw:(_ for _ in ()).throw(AssertionError('Native launch occurred')))
    assert m.child_reaper(tmp_path)==125
    report=json.loads((tmp_path/'child-reaper.json').read_bytes())
    assert report['native_pid'] is None and not report['verified'] and report['capabilities'] is None


@pytest.fixture(scope='module')
def sigchld_library(tmp_path_factory):
    compiler=shutil.which('cc')
    if sys.platform!='linux' or not compiler:pytest.skip('Linux C headers/compiler required for actual SA_NOCLDWAIT control')
    folder=tmp_path_factory.mktemp('sigchld-control');library=folder/'sigchld.so'
    source='''#include <signal.h>
#include <string.h>
int set_autoreap(void) { struct sigaction a; memset(&a,0,sizeof(a));
  a.sa_handler=SIG_DFL; a.sa_flags=SA_NOCLDWAIT; sigemptyset(&a.sa_mask);
  return sigaction(SIGCHLD,&a,0); }
int is_autoreap(void) { struct sigaction a; if(sigaction(SIGCHLD,0,&a)) return -1;
  return (a.sa_flags & SA_NOCLDWAIT)!=0; }
'''
    result=subprocess.run([compiler,'-shared','-fPIC','-x','c','-o',str(library),'-'],input=source,text=True,capture_output=True)
    assert result.returncode==0,result.stderr
    return library


def signal_setup(disposition,library):
    code="import ctypes,signal\nlib=ctypes.CDLL("+repr(str(library))+")\n"
    if disposition=='ignored':code+='signal.signal(signal.SIGCHLD,signal.SIG_IGN)\n'
    elif disposition=='custom':code+='signal.signal(signal.SIGCHLD,lambda *args:None)\n'
    elif disposition=='autoreap':code+='assert lib.set_autoreap()==0\nassert signal.getsignal(signal.SIGCHLD)==signal.SIG_DFL and lib.is_autoreap()==1\n'
    return code


@pytest.mark.parametrize('disposition',['ignored','custom','autoreap'])
def test_outer_refuses_nonwaitable_policy_without_popen_resources_or_handler_changes(tmp_path,sigchld_library,disposition):
    folder=tmp_path/'must-not-exist'
    code="import sys,json\nsys.path.insert(0,"+repr(str(ROOT/'tools/automation/native-v06'))+")\nimport resource_supervisor as m\n"
    code+=signal_setup(disposition,sigchld_library)
    code+='before=signal.getsignal(signal.SIGCHLD);before_auto=lib.is_autoreap();calls=[]\n'
    code+="m.subprocess.Popen=lambda *a,**kw:calls.append('forbidden-popen')\n"
    code+='held=None\ntry:\n m.supervise('+repr(OWNER)+','+repr(str(folder))+',m.Limits(100,10,100000000,1000000,1),["must-not-run"],backend=object())\nexcept m.Hold as exc:\n held=str(exc)\n'
    code+='assert held and not calls\nassert signal.getsignal(signal.SIGCHLD) is before and lib.is_autoreap()==before_auto\nassert not m.Path('+repr(str(folder))+').exists()\nprint(json.dumps(dict(held=held,handler_preserved=True,autoreap=before_auto,popen_calls=len(calls))))\n'
    result=subprocess.run([sys.executable,'-c',code],text=True,capture_output=True,timeout=5)
    assert result.returncode==0,result.stderr
    proof=json.loads(result.stdout);assert proof['handler_preserved'] and proof['popen_calls']==0
    if disposition=='autoreap':assert proof['autoreap']==1 and 'auto-reaped' in proof['held']


@pytest.mark.parametrize('disposition',['default','ignored','custom','autoreap'])
def test_dedicated_worker_resets_waitability_and_preserves_actual_exit_seven(tmp_path,sigchld_library,disposition):
    folder=tmp_path/'worker';folder.mkdir()
    code="import sys,json,os\nsys.path.insert(0,"+repr(str(ROOT/'tools/automation/native-v06'))+")\nimport resource_supervisor as m\n"
    code+=signal_setup(disposition,sigchld_library)
    code+='folder=m.Path('+repr(str(folder))+')\n'
    code+="m.write(folder/'reaper-config.json',dict(owner="+repr(OWNER)+",parent_pid=os.getppid(),parent_birth=m.process_stat(os.getppid())['start'],source_sha256=m.sha256(m.Path(m.__file__).read_bytes()).hexdigest(),command=[sys.executable,'-c','raise SystemExit(7)'],shutdown_seconds=1))\n"
    code+="actual=m.child_reaper(folder)\nrecord=json.loads((folder/'child-reaper.json').read_bytes())\nassert actual==7 and record['native_exit']==7 and record['native_wait_status']==7<<8\nassert record['verified'] and record['native_reaped']\nassert record['capabilities']['waitability']['probe_exit']==73\nassert signal.getsignal(signal.SIGCHLD)==signal.SIG_DFL and lib.is_autoreap()==0\nprint(json.dumps(record))\n"
    result=subprocess.run([sys.executable,'-c',code],text=True,capture_output=True,timeout=5)
    assert result.returncode==0,result.stderr
    assert json.loads(result.stdout)['native_exit']==7


def test_lost_exact_child_wait_status_never_becomes_popen_zero(monkeypatch):
    class Child:pid=123;returncode=None
    monkeypatch.setattr(m.os,'waitpid',lambda *a:(_ for _ in ()).throw(ChildProcessError('ECHILD')))
    child=Child()
    with pytest.raises(m.Hold,match='ECHILD fallback'):m.exact_poll(child)
    assert child.returncode is None
    child.returncode=0
    with pytest.raises(m.Hold,match='lacks an authenticated'):m.exact_poll(child)


@pytest.mark.parametrize('mode',['child-failure','budget','cleanup'])
def test_failure_budget_or_cleanup_cannot_publish_success(tmp_path,monkeypatch,mode):
    popen_factory(monkeypatch);folder=tmp_path/mode;backend=FakeDocker(folder,cleanup_ok=mode!='cleanup')
    budget=replace(limits(),cpu_seconds=.00001) if mode=='budget' else limits()
    with pytest.raises(m.Hold):m.supervise(OWNER,folder,budget,child(status=7 if mode=='child-failure' else 0,sleep=2 if mode=='budget' else 0),backend=backend)
    result=json.loads((folder/'supervisor-result.json').read_bytes())
    assert result['execution']=='held' and backend.cleaned
    if mode=='child-failure':assert result['child_exit']==7
    if mode=='budget':assert (folder/'interruption.json').is_file() and 'cpu' in result['failure']['reason']


def test_namespace_collision_never_grants_cleanup_authority(tmp_path,monkeypatch):
    popen_factory(monkeypatch);folder=tmp_path/'collision';backend=FakeDocker(folder,collision=True)
    with pytest.raises(m.Hold):m.supervise(OWNER,folder,limits(),child(),backend=backend)
    result=json.loads((folder/'supervisor-result.json').read_bytes())
    assert not backend.cleaned and result['child_exit'] is None and not result['cleanup']['verified']


def test_unbound_runner_and_shared_image_cache_drift_are_held(tmp_path,monkeypatch):
    popen_factory(monkeypatch)
    for name in ('unbound','cache-drift'):
        folder=tmp_path/name;backend=FakeDocker(folder)
        if name=='cache-drift':
            calls=[]
            def images():calls.append(True);return {'sha256:cached-image':123} if len(calls)==1 else {'sha256:changed-shared-cache':456}
            backend.images=images
        command=[sys.executable,'-c','print("no binding")'] if name=='unbound' else child(sleep=1)
        with pytest.raises(m.Hold):m.supervise(OWNER,folder,limits(),command,backend=backend)
        assert backend.cleaned and json.loads((folder/'supervisor-result.json').read_bytes())['execution']=='held'


def test_event_telemetry_failure_does_not_allow_success(tmp_path,monkeypatch):
    real=subprocess.Popen
    def spawn(argv,**kwargs):
        if argv[:2]!=['docker','events']:return real(argv,**kwargs)
        events=FakeEvents();events.returncode=1;return events
    monkeypatch.setattr(m.subprocess,'Popen',spawn);folder=tmp_path/'event-failure';backend=FakeDocker(folder)
    with pytest.raises(m.Hold):m.supervise(OWNER,folder,limits(),child(sleep=1),backend=backend)
    result=json.loads((folder/'supervisor-result.json').read_bytes())
    assert 'event stream' in result['failure']['reason'] and backend.cleaned


def test_signal_interruption_is_logged_and_owned_child_teardown_runs(tmp_path,monkeypatch):
    popen_factory(monkeypatch);handlers={}
    def register(sig,callback):previous=handlers.get(sig,signal.SIG_DFL);handlers[sig]=callback;return previous
    monkeypatch.setattr(m.signal,'signal',register)
    folder=tmp_path/'interruption';backend=FakeDocker(folder,interrupt=lambda:handlers[signal.SIGTERM](signal.SIGTERM,None))
    with pytest.raises(m.Hold):m.supervise(OWNER,folder,limits(),child(sleep=2),backend=backend)
    report=json.loads((folder/'interruption.json').read_bytes())
    assert report['signals'][0]['signal']==signal.SIGTERM and backend.cleaned
    assert json.loads((folder/'supervisor-result.json').read_bytes())['execution']=='held'
