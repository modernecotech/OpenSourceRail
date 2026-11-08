#!/usr/bin/env python3
"""Sample and terminate one explicitly owned disposable Docker campaign.

No daemon changes, global prune, image removal or cgroup-isolation claim. This
wrapper must enclose the native runner; its success receipt is the final gate.
The runner must call require_binding(owner, private_dir) before resource writes.
"""
from dataclasses import asdict,dataclass
from hashlib import sha256
from pathlib import Path
import argparse
import json
import math
import os
import re
import select
import signal
import subprocess
import sys
import time

LABEL='osr.native.owner'
PROJECT='com.docker.compose.project'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
    operating_release=False,movement_authority=False,physical_evidence=False)


class Hold(RuntimeError):pass


def owner_id(value):
    if not isinstance(value,str) or re.fullmatch('osr-v06-[a-f0-9]{12}',value) is None:raise Hold('Exact fresh native owner required')
    return value


def encoded(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def write(path,value):
    path=Path(path);path.write_bytes(encoded(value));path.chmod(0o600)


def append(path,value):
    with Path(path).open('ab') as stream:stream.write(encoded(value))


@dataclass(frozen=True)
class Limits:
    cpu_seconds:float
    elapsed_seconds:float
    rss_bytes:int
    disk_bytes:int
    host_reserve_bytes:int
    interval_seconds:float=.5
    probe_seconds:float=10.
    shutdown_seconds:float=20.

    def __post_init__(self):
        if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<=0 for v in asdict(self).values()):raise Hold('Explicit positive finite budgets required')
        if not .1<=self.interval_seconds<=5 or not 1<=self.probe_seconds<=15 or not 1<=self.shutdown_seconds<=30:
            raise Hold('Bounded observation and shutdown intervals required')


def require_binding(owner,private_dir):
    """Runner handshake, before any Docker mutation; no caller-selected drift."""
    folder=Path(private_dir).absolute();owner_id(owner)
    if os.environ.get('OSR_NATIVE_OWNER')!=owner or os.environ.get('OSR_NATIVE_PRIVATE_DIR')!=str(folder):raise Hold('Supervisor owner/directory binding differs')
    request=json.loads((folder/'supervisor-binding.json').read_bytes())
    if request['owner']!=owner or request['private_dir']!=str(folder) or request['token']!=os.environ.get('OSR_NATIVE_BINDING'):
        raise Hold('Native runner did not receive the exact supervisor binding')
    write(folder/'runner-binding.json',dict(owner=owner,private_dir=str(folder),binding_sha256=sha256(encoded(request)).hexdigest()))
    return request


def owned(kind,row,owner):
    """All destructive operations recheck immutable native IDs and own labels."""
    labels=row.get('Labels') or {};name=str(row.get('Name','')).removeprefix('/')
    if labels.get(LABEL) not in (None,owner) or labels.get(PROJECT) not in (None,owner):raise Hold('Conflicting resource ownership')
    if kind=='network':
        # Compose's default network already has an exact project label. An
        # additional osr.native.owner label is accepted and recommended.
        ok=labels.get(PROJECT)==owner and name==owner+'_default'
    else:ok=labels.get(LABEL)==owner and name.startswith((owner+'_',owner+'-') if kind=='volume' else (owner+'-',))
    if not ok:raise Hold('Required exact resource owner/name binding missing')
    return row


def process_stat(pid,proc=Path('/proc')):
    """Linux counters, with birth tick preventing PID-reuse attribution."""
    raw=(proc/str(pid)/'stat').read_text();end=raw.rfind(')');fields=raw[end+2:].split()
    if end<0 or int(raw[:raw.index(' ')])!=pid or len(fields)<22:raise Hold('Unverifiable process stat')
    values=dict(pid=pid,ppid=int(fields[1]),ticks=sum(int(fields[i]) for i in (11,12,13,14)),
        start=int(fields[19]),rss_pages=int(fields[21]))
    if min(values['ticks'],values['start'],values['rss_pages'])<0:raise Hold('Invalid process counters')
    return values


def process_tree(root,proc=Path('/proc')):
    rows={}
    for entry in proc.iterdir():
        if not entry.name.isdigit():continue
        try:rows[int(entry.name)]=process_stat(int(entry.name),proc)
        except FileNotFoundError:continue
        except PermissionError:continue  # Required descendants are checked via native Docker top.
    if root not in rows:raise Hold('Supervisor process telemetry missing')
    selected={root};changed=True
    while changed:
        added={pid for pid,row in rows.items() if row['ppid'] in selected}-selected;changed=bool(added);selected|=added
    return {pid:rows[pid] for pid in selected}


def allocated(path,*,deadline=None):
    """Allocated blocks, no symlink traversal; inaccessible data is not zero."""
    seen=set();total=0;pending=[Path(path)]
    while pending:
        if deadline is not None and time.monotonic()>deadline:raise Hold('Filesystem observation deadline exceeded')
        item=pending.pop();st=item.lstat();key=(st.st_dev,st.st_ino)
        if key in seen:continue
        seen.add(key);total+=st.st_blocks*512
        if item.is_dir() and not item.is_symlink():pending.extend(item.iterdir())
    return total


class Docker:
    """Only fixed read probes and exact-ID owned teardown are exposed."""
    def __init__(self,owner,folder):
        self.owner=owner_id(owner);self.folder=Path(folder);self.deadline=None;self.helper_cpu_upper_s=0.;self.unaccounted_volumes=set();self.cleanup_deadline=None

    def call(self,args,*,timeout=5,cleanup=False):
        if self.cleanup_deadline is not None:
            timeout=min(timeout,self.cleanup_deadline-time.monotonic())
            if timeout<=0:raise Hold('Owned teardown deadline exceeded; manual audit required')
        if self.deadline is not None and not cleanup:
            timeout=min(timeout,self.deadline-time.monotonic())
            if timeout<=0:raise Hold('Resource observation deadline exceeded')
        started=time.monotonic()
        try:
            result=subprocess.run(['docker',*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
            append(self.folder/'docker-probes.jsonl',dict(argv=args,exit=result.returncode,elapsed_s=time.monotonic()-started,
                stdout=result.stdout.decode(errors='replace')[:1048576],stderr=result.stderr.decode(errors='replace')[:1048576]))
        except subprocess.TimeoutExpired as exc:
            append(self.folder/'docker-probes.jsonl',dict(argv=args,exit=None,interruption='timeout',elapsed_s=time.monotonic()-started,
                stdout=(exc.stdout or b'').decode(errors='replace')[:1048576],stderr=(exc.stderr or b'').decode(errors='replace')[:1048576]))
            raise Hold('Required Docker telemetry or cleanup timed out') from exc
        if result.returncode:raise Hold('Required Docker telemetry or cleanup failed')
        if len(result.stdout)>1048576:raise Hold('Unbounded Docker telemetry output')
        return result.stdout.decode()

    def inventory(self):
        result={}
        for kind,command in [('container',['ps','-aq']),('volume',['volume','ls','-q']),('network',['network','ls','-q'])]:
            values=set()
            for key in (LABEL,PROJECT):values.update(self.call([*command,'--filter','label='+key+'='+self.owner]).split())
            result[kind]=sorted(values)
        return result

    def inspect(self,kind,identifiers,*,size=False):
        if not identifiers:return []
        for name in identifiers:
            if not re.fullmatch('[A-Za-z0-9_.-]{1,150}',name):raise Hold('Invalid native resource ID')
        if kind=='container':
            # Deliberately omit Config.Env: credentials never enter probe logs.
            fields={'Id':'.Id','Name':'.Name','Labels':'.Config.Labels','State':'.State','Mounts':'.Mounts',
                'LogPath':'.LogPath','LogType':'.HostConfig.LogConfig.Type','Image':'.Image'}
            if size:fields['SizeRw']='.SizeRw'
            template='{'+','.join(json.dumps(k)+':{{json '+v+'}}' for k,v in fields.items())+'}'
            args=['inspect','--type','container',*(['--size'] if size else []),'--format',template,*identifiers]
        else:args=[kind,'inspect','--format','{{json .}}',*identifiers]
        rows=[owned(kind,json.loads(line),self.owner) for line in self.call(args).splitlines() if line.strip()]
        if len(rows)!=len(identifiers):raise Hold('Required native resource inspection is incomplete')
        return rows

    def images(self):
        names=sorted(set(self.call(['image','ls','-aq','--no-trunc']).split()))
        if not names:return {}
        rows=self.call(['image','inspect','--format','{"Id":{{json .Id}},"Size":{{json .Size}}}',*names])
        return {r['Id']:r['Size'] for r in map(json.loads,rows.splitlines())}

    def storage_roots(self):
        fields={'DockerRootDir':'.DockerRootDir','MemoryLimit':'.MemoryLimit','CpuCfsQuota':'.CPUCfsQuota',
            'CgroupVersion':'.CgroupVersion','NCPU':'.NCPU','ServerVersion':'.ServerVersion'}
        template='{'+','.join(json.dumps(k)+':{{json '+v+'}}' for k,v in fields.items())+'}'
        info=json.loads(self.call(['info','--format',template]));write(self.folder/'docker-capabilities.json',info)
        root=Path(info['DockerRootDir'])
        if not root.is_absolute() or not root.is_dir():raise Hold('Docker storage filesystem cannot be authenticated')
        return [root]

    def metrics(self,*,disk=True):
        inventory=self.inventory();containers=self.inspect('container',inventory['container'],size=disk)
        volumes=self.inspect('volume',inventory['volume']);self.inspect('network',inventory['network'])
        groups={};seen=set();mounts={};disk_bytes=0
        for row in containers:
            if row['State'].get('Running'):
                root=int(row['State']['Pid'])
                top=self.call(['top',row['Id'],'-eo','pid,ppid']).splitlines()
                if not top or top[0].split()!=['PID','PPID']:raise Hold('Native Docker process identity columns differ')
                pids=[int(line.split()[0]) for line in top[1:] if line.strip()]
                if root not in pids or len(pids)!=len(set(pids)) or seen.intersection(pids):raise Hold('Native container process identities cannot be authenticated')
                sampled_utc=time.time()
                try:stats=[process_stat(pid) for pid in pids]
                except (FileNotFoundError,PermissionError) as exc:raise Hold('Required container process telemetry disappeared or is inaccessible') from exc
                seen.update(pids)
                if not sum(p['rss_pages'] for p in stats):raise Hold('Required running-container RSS telemetry is zero and cannot be authenticated')
                key=row['Id']+':'+str(row['State']['StartedAt'])
                groups[key]=dict(ticks=sum(p['ticks'] for p in stats),rss_pages=sum(p['rss_pages'] for p in stats),
                    processes=stats,container_id=row['Id'],sampled_utc=sampled_utc)
            for m in row['Mounts']:
                if m.get('Type')=='volume':mounts.setdefault(m['Name'],[]).append((row,m['Destination']))
                elif m.get('Type')=='bind' and m.get('RW'):
                    if not Path(m['Source']).resolve().is_relative_to(self.folder.resolve()):raise Hold('Writable host bind lies outside the private resource budget')
            if disk:
                size=row.get('SizeRw')
                if type(size) is not int or size<0:raise Hold('Required writable-layer telemetry unavailable')
                disk_bytes+=size
                if row['LogType'] not in ('','json-file','none'):raise Hold('Unmeasurable container log driver')
                if row['State'].get('Running') and row['LogType']!='none' and not row['LogPath']:
                    raise Hold('Required running-container log allocation is unavailable')
                if row['LogPath']:
                    log=Path(row['LogPath'])
                    for path in log.parent.glob(log.name+'*'):disk_bytes+=allocated(path,deadline=self.deadline)
        unknown=set(mounts)-{r['Name'] for r in volumes}
        if unknown:
            self.unaccounted_volumes|=unknown
            raise Hold('Unlabelled or non-owned volume mount cannot become zero disk; declare an explicit owned volume')
        if disk:
            for row in volumes:
                try:disk_bytes+=allocated(row['Mountpoint'],deadline=self.deadline)
                except PermissionError:
                    choices=[(c,d) for c,d in mounts.get(row['Name'],[]) if c['State'].get('Running')]
                    if not choices:raise Hold('Owned volume cannot be measured without starting another container')
                    container,destination=choices[0];started=time.monotonic()
                    output=self.call(['exec','--user','0',container['Id'],'du','-sx','--block-size=1','--',destination])
                    # A read-only exec may finish between process samples. Charge
                    # its complete elapsed interval at all host CPUs, safely high.
                    self.helper_cpu_upper_s+=(time.monotonic()-started)*(os.cpu_count() or 1)
                    token=output.split()[0]
                    if not token.isdigit():raise Hold('Owned volume allocation probe differs')
                    disk_bytes+=int(token)
        return dict(inventory=inventory,containers=containers,groups=groups,owned_docker_disk_bytes=disk_bytes)

    def cleanup(self):
        """Never use global prune, rm by prefix, daemon settings or image delete."""
        self.deadline=None;self.cleanup_deadline=time.monotonic()+60;errors=[]
        # Fixed rounds catch a client finishing a concurrent create during stop.
        for _ in range(2):
            try:inventory=self.inventory()
            except Exception as exc:errors.append(type(exc).__name__+':'+str(exc));break
            for kind in ('container','volume','network'):
                for name in inventory[kind]:
                    try:
                        row=self.inspect(kind,[name])[0]  # Fresh exact labels, immediately before mutation.
                        if kind=='container':
                            volume_names={v['Name'] for v in row.get('Mounts',[]) if v.get('Type')=='volume'}
                            self.unaccounted_volumes|=volume_names-set(inventory['volume'])
                            try:self.call(['logs','--tail','2000',row['Id']],cleanup=True)
                            except Hold:pass
                            self.call(['rm','-f',row['Id']],timeout=15,cleanup=True)
                        else:self.call([kind,'rm',row.get('Name',name)],timeout=10,cleanup=True)
                    except Exception as exc:errors.append(kind+':'+name+':'+str(exc))
        try:remaining=self.inventory()
        except Exception as exc:remaining=None;errors.append('verification:'+str(exc))
        result=dict(owner=self.owner,remaining=remaining,errors=errors,deadline_seconds=60,unaccounted_volume_mounts=sorted(self.unaccounted_volumes),
            verified=remaining is not None and not any(remaining.values()) and not errors and not self.unaccounted_volumes)
        write(self.folder/'supervisor-cleanup.json',result);return result


class Accounting:
    def __init__(self,limits,*,hz=None,page=None):
        self.limits=limits;self.hz=hz or os.sysconf('SC_CLK_TCK');self.page=page or os.sysconf('SC_PAGE_SIZE')
        self.cpu={};self.peak_rss=0;self.peak_disk=0

    def sample(self,groups,*,elapsed,disk,free,extra_cpu=0):
        for key,row in groups.items():
            # Keep every authenticated PID birth through exit/restart. A Docker
            # exec process can be reaped by a shim outside the container's init;
            # a sum of only currently live processes would incorrectly decrease.
            counters=({f"pid:{p['pid']}:{p['start']}":p['ticks'] for p in row['processes']}
                if 'processes' in row else {key:row['ticks']})
            for identity,ticks in counters.items():
                previous=self.cpu.get(identity,0)
                if ticks<previous:raise Hold('Required cumulative process CPU telemetry decreased')
                self.cpu[identity]=ticks
        cpu=sum(self.cpu.values())/self.hz+extra_cpu;rss=sum(r['rss_pages'] for r in groups.values())*self.page
        self.peak_rss=max(self.peak_rss,rss);self.peak_disk=max(self.peak_disk,disk)
        result=dict(elapsed_s=elapsed,cpu_charged_s=cpu,rss_bytes=rss,disk_bytes=disk,host_free_bytes=free,
            peak_rss_bytes=self.peak_rss,peak_disk_bytes=self.peak_disk)
        violations=[name for name,value,limit in [('elapsed',elapsed,self.limits.elapsed_seconds),('cpu',cpu,self.limits.cpu_seconds),
            ('rss',rss,self.limits.rss_bytes),('disk',disk,self.limits.disk_bytes)] if value>limit]
        if free<self.limits.host_reserve_bytes:violations.append('host-disk-reserve')
        result['violations']=violations;return result


class Filesystems:
    def __init__(self,paths):
        self.roots={}
        for path in paths:
            path=Path(path);device=path.stat().st_dev;stat=os.statvfs(path)
            self.roots.setdefault(device,dict(path=str(path),initial_free=stat.f_bavail*stat.f_frsize))
    def sample(self):
        rows=[]
        for device,root in self.roots.items():
            path=Path(root['path'])
            if path.stat().st_dev!=device:raise Hold('Budget filesystem identity changed')
            stat=os.statvfs(path);free=stat.f_bavail*stat.f_frsize
            rows.append(dict(device=device,free_bytes=free,initial_free_bytes=root['initial_free'],growth_bytes=max(0,root['initial_free']-free)))
        return dict(roots=rows,minimum_free_bytes=min(r['free_bytes'] for r in rows),unattributed_growth_bytes=sum(r['growth_bytes'] for r in rows))


class Events:
    def __init__(self,owner):self.owner=owner;self.started={};self.execs={};self.cpu_upper_s=0.
    def accept(self,event,observed):
        if event.get('Type')!='container':return
        actor=event.get('Actor',{});attrs=actor.get('Attributes',{})
        if attrs.get(LABEL)!=self.owner:raise Hold('Unauthenticated Docker owner event')
        cid=actor['ID'];action=event.get('Action','').split(':',1)[0]
        stamp=event.get('timeNano',event.get('time',0)*10**9)/10**9
        if not 0<stamp<=time.time()+5:raise Hold('Unauthenticated Docker event clock')
        if action=='start':
            self.started[cid]=stamp
            if observed.get(cid,0)<stamp:observed.pop(cid,None)
        if action=='die':
            if cid not in self.started or cid not in observed:raise Hold('A required container exited without authenticated process/RSS telemetry')
            self.cpu_upper_s+=max(0,stamp-observed[cid])*(os.cpu_count() or 1)
        if action in ('exec_start','exec_die'):
            exec_id=attrs.get('execID')
            if not isinstance(exec_id,str) or not re.fullmatch('[a-zA-Z0-9]{1,128}',exec_id):raise Hold('Required exec process identity missing')
            key=(cid,exec_id)
            if action=='exec_start':self.execs[key]=stamp
            else:
                if key not in self.execs or self.execs[key]>stamp:raise Hold('Required exec lifecycle telemetry incomplete')
                # Includes short execs and their unsampled descendants. This is
                # an upper charge at all host CPUs, not an efficiency estimate.
                self.cpu_upper_s+=(stamp-self.execs.pop(key))*(os.cpu_count() or 1)


def _event_lines(process,buffer,*,deadline=None):
    if process.poll() is not None:raise Hold('Docker ownership event stream ended')
    while select.select([process.stdout],[],[],0)[0]:
        if deadline is not None and time.monotonic()>deadline:raise Hold('Docker event observation deadline exceeded')
        data=os.read(process.stdout.fileno(),65536)
        if not data:raise Hold('Docker ownership event stream EOF')
        buffer+=data
        if len(buffer)>1048576:raise Hold('Unbounded Docker event record')
    lines=buffer.split(b'\n');return [json.loads(line) for line in lines[:-1] if line],lines[-1]


def supervise(owner,private_dir,limits,command,*,backend=None):
    """Run once, retain failure evidence, publish success only after cleanup."""
    owner_id(owner);folder=Path(private_dir).absolute();source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()
    if folder.exists() or any(p.is_symlink() for p in folder.parents):raise Hold('Fresh ordinary private output directory required')
    if not command or not all(isinstance(v,str) and v for v in command):raise Hold('Explicit child argv required')
    folder.mkdir(parents=True,mode=0o700);folder.chmod(0o700)
    docker=backend or Docker(owner,folder);account=Accounting(limits);started=time.monotonic()
    binding=dict(owner=owner,private_dir=str(folder),limits=asdict(limits),token=os.urandom(24).hex(),**FLAGS)
    write(folder/'supervisor-binding.json',binding);write(folder/'command.json',dict(argv=command,**FLAGS))
    child=None;events=None;event_err=None;cleanup=None;failure=None;returncode=None;buffer=b'';observed={};last_disk=0;disk_at=-math.inf
    event_ledger=Events(owner);exit_seen=False
    cleanup_authority=False;last_native_sample=None
    old_handlers={};interruption=[];images={};filesystems=Filesystems([folder])
    def interrupted(signum,_):
        interruption.append(dict(signal=signum,at_elapsed_s=time.monotonic()-started));raise Hold('Supervisor interrupted by signal '+str(signum))
    for sig in (signal.SIGTERM,signal.SIGINT):old_handlers[sig]=signal.signal(sig,interrupted)
    try:
        docker.deadline=time.monotonic()+limits.probe_seconds
        if any(docker.inventory().values()):raise Hold('Owner namespace collision; no child was launched')
        cleanup_authority=True
        filesystems=Filesystems([folder,*docker.storage_roots()])
        images=docker.images();write(folder/'image-baseline.json',dict(images=images,reported_logical_bytes=sum(images.values()),
            note='Shared layers may overlap. Existing cache is never deleted; image inventory drift holds the run.'))
        for name in ('tmp','cache','config'):(folder/name).mkdir(mode=0o700)
        env=dict(os.environ,OSR_NATIVE_OWNER=owner,OSR_NATIVE_PRIVATE_DIR=str(folder),OSR_NATIVE_BINDING=binding['token'],
            TMPDIR=str(folder/'tmp'),TMP=str(folder/'tmp'),TEMP=str(folder/'tmp'),
            XDG_CACHE_HOME=str(folder/'cache'),XDG_CONFIG_HOME=str(folder/'config'))
        event_err=(folder/'docker-events.stderr').open('wb')
        events=subprocess.Popen(['docker','events','--since',str(int(time.time())),'--filter','label='+LABEL+'='+owner,'--format','{{json .}}'],
            stdout=subprocess.PIPE,stderr=event_err)
        child=subprocess.Popen(command,env=env,start_new_session=True,stdout=(folder/'child.stdout').open('wb'),stderr=(folder/'child.stderr').open('wb'))
        child_birth=process_stat(child.pid)['start'];write(folder/'child-process.json',dict(pid=child.pid,start=child_birth,process_group=child.pid))
        while True:
            docker.deadline=time.monotonic()+limits.probe_seconds
            lines,buffer=_event_lines(events,buffer,deadline=docker.deadline)
            for event in lines:
                append(folder/'docker-events.jsonl',event)
                event_ledger.accept(event,observed)
            measure_disk=time.monotonic()-disk_at>=5
            snapshot=docker.metrics(disk=measure_disk)
            if any(row['Image'] not in images for row in snapshot['containers']):raise Hold('Owned container uses an image absent from the frozen shared cache')
            for row in snapshot['groups'].values():observed[row['container_id']]=row['sampled_utc']
            if measure_disk:
                last_disk=snapshot['owned_docker_disk_bytes'];disk_at=time.monotonic()
                if docker.images()!=images:raise Hold('Shared image cache changed; impact is unattributed and no image will be deleted')
            rows=process_tree(os.getpid());host=dict(ticks=sum(r['ticks'] for r in rows.values()),rss_pages=sum(r['rss_pages'] for r in rows.values()),processes=list(rows.values()))
            if child.poll() is None and (child.pid not in rows or rows[child.pid]['start']!=child_birth):
                raise Hold('Required native child process telemetry cannot be authenticated')
            if {p['pid'] for g in snapshot['groups'].values() for p in g['processes']}.intersection(rows):raise Hold('Container and supervisor PID ownership overlap')
            groups=dict(snapshot['groups'],supervisor_and_child=host)
            storage=filesystems.sample();sample=account.sample(groups,elapsed=time.monotonic()-started,
                disk=max(last_disk+allocated(folder,deadline=docker.deadline),storage['unattributed_growth_bytes']),free=storage['minimum_free_bytes'],
                extra_cpu=event_ledger.cpu_upper_s+docker.helper_cpu_upper_s)
            append(folder/'metrics.jsonl',dict(sample,inventory=snapshot['inventory'],process_groups=groups,filesystems=storage))
            last_native_sample=time.monotonic()
            if sample['violations']:raise Hold('Aggregate resource budget exceeded: '+','.join(sample['violations']))
            returncode=child.poll()
            if returncode is not None:
                if returncode:raise Hold('Native child exited '+str(returncode))
                if not exit_seen:
                    exit_seen=True;time.sleep(limits.interval_seconds);continue  # Drain final exec/die events before the gate.
                if event_ledger.execs:raise Hold('Required exec lifecycle did not close before child completion')
                request=json.loads((folder/'runner-binding.json').read_bytes())
                if request!=dict(owner=owner,private_dir=str(folder),binding_sha256=sha256(encoded(binding)).hexdigest()):raise Hold('Runner binding acknowledgement differs')
                break
            time.sleep(limits.interval_seconds)
    except BaseException as exc:
        failure=dict(type=type(exc).__name__,reason=str(exc),elapsed_s=time.monotonic()-started)
        write(folder/'interruption.json',dict(failure=failure,signals=interruption,**FLAGS))
    finally:
        # Repeated termination signals are logged while teardown runs. They do
        # not interrupt label checks and leave a false cleanup-success record.
        for sig in old_handlers:signal.signal(sig,lambda number,_:interruption.append(dict(signal=number,during='cleanup')))
        # The child was started in its own session. PID birth/group are checked
        # before signalling; no unrelated PID or process group is targeted.
        if child is not None and child.poll() is None:
            try:
                current=process_stat(child.pid)
                if current['start']!=child_birth or os.getpgid(child.pid)!=child.pid:raise Hold('Child PID/group identity changed; refusing signal')
                os.killpg(child.pid,signal.SIGTERM)
                try:child.wait(timeout=limits.shutdown_seconds)
                except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait(timeout=5)
            except BaseException as exc:
                failure=failure or dict(type=type(exc).__name__,reason=str(exc));append(folder/'shutdown-errors.jsonl',failure)
        if child is not None:returncode=child.poll()
        if events is not None:
            events.terminate()
            try:events.wait(timeout=3)
            except subprocess.TimeoutExpired:events.kill();events.wait(timeout=3)
        if event_err is not None:event_err.close()
        try:
            if cleanup_authority:cleanup=docker.cleanup()
            else:
                cleanup=dict(owner=owner,remaining=None,errors=['No cleanup authority acquired; pre-existing namespace preserved'],verified=False)
                write(folder/'supervisor-cleanup.json',cleanup)
        except BaseException as exc:
            cleanup=dict(owner=owner,remaining=None,errors=['Cleanup failed:'+str(exc)],verified=False)
        finally:
            for sig,handler in old_handlers.items():signal.signal(sig,handler)
    if interruption:
        failure=failure or dict(type='Hold',reason='Supervisor interrupted during teardown')
        write(folder/'interruption.json',dict(failure=failure,signals=interruption,**FLAGS))
    # Include monitor, child and measurement/cleanup-client CPU and private
    # allocation through the end. Native activity after the last sample is
    # charged once at all host CPUs, conservatively high, never silently zero.
    try:
        docker.deadline=time.monotonic()+limits.probe_seconds
        final_images=docker.images()
        write(folder/'image-final.json',dict(images=final_images,added=sorted(set(final_images)-set(images)),removed=sorted(set(images)-set(final_images)),
            shared_cache_deleted_by_supervisor=False))
        if final_images!=images:failure=failure or dict(type='Hold',reason='Shared image cache changed; cache preserved')
        rows=process_tree(os.getpid());storage=filesystems.sample()
        extra=event_ledger.cpu_upper_s+docker.helper_cpu_upper_s+(max(0,time.monotonic()-last_native_sample)*(os.cpu_count() or 1) if last_native_sample else 0)
        final=account.sample(dict(supervisor_and_child=dict(ticks=sum(r['ticks'] for r in rows.values()),rss_pages=sum(r['rss_pages'] for r in rows.values()),processes=list(rows.values()))),
            elapsed=time.monotonic()-started,disk=max(allocated(folder,deadline=docker.deadline)+65536,storage['unattributed_growth_bytes']),
            free=storage['minimum_free_bytes'],extra_cpu=extra)
        append(folder/'metrics.jsonl',dict(final,phase='after-cleanup',filesystems=storage))
        if final['violations']:failure=failure or dict(type='Hold',reason='End-of-cleanup budget exceeded: '+','.join(final['violations']))
    except BaseException as exc:failure=failure or dict(type=type(exc).__name__,reason='Final accounting:'+str(exc))
    if sha256(Path(__file__).read_bytes()).hexdigest()!=source_sha256:
        failure=failure or dict(type='Hold',reason='Resource supervisor source changed during execution')
    result=dict(schema='osr-native-resource-supervision/1',owner=owner,execution='completed' if failure is None and cleanup['verified'] else 'held',
        supervisor_source_sha256=source_sha256,command_sha256=sha256(encoded(command)).hexdigest(),binding_sha256=sha256(encoded(binding)).hexdigest(),
        child_exit=returncode,failure=failure,limits=asdict(limits),elapsed_s=time.monotonic()-started,
        observed_peak_rss_bytes=account.peak_rss,observed_peak_disk_bytes=account.peak_disk,
        final_accounting=final if 'final' in locals() else None,
        cleanup=cleanup,image_baseline_sha256=sha256(encoded(images)).hexdigest(),
        mechanism='Sampled process/RSS/disk observation and exact-owner termination; no kernel aggregate quotas',
        limitations=['Detection delay includes interval plus probe deadline and shutdown latency; RSS/disk transient byte overshoot has no finite enforced bound',
            'Exited-container CPU gaps and volume-measurement exec intervals are conservatively charged at all host CPUs',
            'PID-birth counters retain parent reaped-child time and sampled child time; the charge can double-count CPU and is not a throughput benchmark',
            'Final CPU includes cleanup at a conservative all-host-CPU bound; private disk reserves another 64 KiB for final receipts',
            'Disk combines allocated private/volume/log blocks, logical writable-layer bytes and unattributed filesystem growth; there is no filesystem quota or write sandbox',
            'SIGKILL, supervisor crash, host outage or Docker daemon unavailability can prevent teardown; coordinator must audit leftovers',
            'Shared image cache is observed and never removed; cache drift holds the run'],**FLAGS)
    write(folder/'supervisor-result.json',result)
    if result['execution']!='completed':raise Hold('Native resource supervision held; inspect private result and cleanup')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--owner',required=True);p.add_argument('--private-dir',required=True,type=Path)
    p.add_argument('--cpu-seconds',required=True,type=float);p.add_argument('--elapsed-seconds',required=True,type=float)
    p.add_argument('--rss-bytes',required=True,type=int);p.add_argument('--disk-bytes',required=True,type=int);p.add_argument('--host-reserve-bytes',required=True,type=int)
    p.add_argument('--interval-seconds',type=float,default=.5);p.add_argument('--probe-seconds',type=float,default=10.)
    p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args();command=a.command[1:] if a.command[:1]==['--'] else a.command
    limits=Limits(a.cpu_seconds,a.elapsed_seconds,a.rss_bytes,a.disk_bytes,a.host_reserve_bytes,a.interval_seconds,a.probe_seconds)
    result=supervise(a.owner,a.private_dir,limits,command);print(json.dumps(dict(execution=result['execution'],owner=result['owner'],**FLAGS)))


if __name__=='__main__':main()
