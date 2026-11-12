"""Cooperative cross-store reservations for at most two analytic workers.

Admission only: no cgroup, aggregate quota or claim about unrelated host jobs.
"""
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import stat
from uuid import uuid4
from engineering.performance import disk_admission

MEMORY_BYTES=3*1024**3
HOST_MEMORY_RESERVE=2*1024**3
DISK_BYTES=67*1024**2
DEFAULT_LEDGER=Path.home()/'.local/state/opensourcerail/analytic-worker-reservations.json'


def process_token(pid):
    try:
        text=Path(f'/proc/{pid}/stat').read_text();fields=text[text.rfind(')')+2:].split()
        return None if fields[0]=='Z' else fields[19]
    except (OSError,IndexError):return None


def available_memory():
    try:
        for line in Path('/proc/meminfo').read_text().splitlines():
            if line.startswith('MemAvailable:'):return int(line.split()[1])*1024
    except (OSError,ValueError):pass
    return None


def cpu_slots():
    return len(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else os.cpu_count() or 1


class Reservations:
    def __init__(self,path):
        self.path=Path(path).expanduser().absolute()
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.owner=process_token(os.getpid())
        if self.owner is None:raise ValueError('Process identity unavailable for shared worker admission')
        from .completion import _ordinary
        _ordinary(self.path);_ordinary(self.path.with_suffix('.lock'))

    @contextmanager
    def transaction(self,*,write_back=True):
        lock=os.open(self.path.with_suffix('.lock'),os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600)
        with os.fdopen(lock,'a+b') as handle:
            fcntl.flock(handle,fcntl.LOCK_EX)
            rows={}
            if self.path.exists():
                descriptor=os.open(self.path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
                with os.fdopen(descriptor,'rb') as stream:
                    if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):raise ValueError('Ordinary reservation ledger required')
                    raw=stream.read(256*1024+1)
                if len(raw)>256*1024:raise ValueError('Reservation ledger exceeds budget')
                value=json.loads(raw)
                if value.get('schema')!='osr-analytic-worker-reservations/1':raise ValueError('Unknown reservation ledger')
                rows=value['reservations']
                if not isinstance(rows,dict) or len(rows)>32:raise ValueError('Bounded reservation map required')
                for r in rows.values():
                    if (not isinstance(r,dict) or type(r.get('owner_pid')) is not int or r['owner_pid']<=0
                        or not isinstance(r.get('owner_token'),str) or not r['owner_token'].isdigit()
                        or (r.get('worker_pid') is not None and (type(r['worker_pid']) is not int or r['worker_pid']<=0))
                        or (r.get('worker_token') is not None and (not isinstance(r['worker_token'],str) or not r['worker_token'].isdigit()))
                        or type(r.get('device')) is not int or r['device']<0 or r.get('disk_bytes')!=DISK_BYTES):
                        raise ValueError('Malformed analytic reservation record')
            # A coordinator may die between spawning and attaching its worker.
            # Keep unassigned reservations until explicit reconciliation rather
            # than assuming its child never started and oversubscribing RAM.
            rows={k:r for k,r in rows.items() if r.get('worker_pid') is None
                  or process_token(r['worker_pid'])==r.get('worker_token')}
            yield rows
            if not write_back:return
            raw=json.dumps(dict(schema='osr-analytic-worker-reservations/1',reservations=rows),sort_keys=True).encode()
            temporary=self.path.with_name(self.path.name+f'.{uuid4().hex}.pending')
            fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
            try:
                with os.fdopen(fd,'wb') as stream:stream.write(raw)
                temporary.replace(self.path)
            finally:temporary.unlink(missing_ok=True)

    @contextmanager
    def stage_metadata(self,store,minimum_free_gib,growth_bytes):
        # Serialize admission plus small immutable queue writes across stores.
        # Existing worker reservations protect their still-unwritten outputs.
        with self.transaction(write_back=False) as rows:
            device=Path(store).stat().st_dev
            reserved=sum(r['disk_bytes'] for r in rows.values() if r['device']==device)
            disk=disk_admission(store,minimum_free_gib=minimum_free_gib+(reserved+growth_bytes)/1024**3)
            yield dict(admitted=disk['admitted'],reason=None if disk['admitted'] else 'Insufficient disk to retain queued request/control files',
                disk=disk,queued_control_reservation_bytes=growth_bytes,
                outstanding_worker_reservation_bytes=reserved,
                enforcement='Serialized cooperative admission, not an aggregate filesystem quota')

    def claim(self,job_id,store,minimum_free_gib):
        key=str(Path(store).resolve())+'/'+job_id
        with self.transaction() as rows:
            memory=available_memory();cpu=cpu_slots();device=Path(store).stat().st_dev
            reserved=sum(r['disk_bytes'] for r in rows.values() if r['device']==device)
            disk=disk_admission(store,minimum_free_gib=minimum_free_gib+(reserved+DISK_BYTES)/1024**3)
            reason=None
            orphan_launches=[k for k,r in rows.items() if r.get('worker_pid') is None and process_token(r['owner_pid'])!=r['owner_token']]
            if orphan_launches:reason='Unreconciled interrupted worker-launch reservation; inspect retained job before release'
            elif len(rows)>=min(2,cpu):reason='Shared analytic CPU/worker slots reserved'
            elif memory is None or memory<HOST_MEMORY_RESERVE+(len(rows)+1)*MEMORY_BYTES:reason='Shared memory reserve unavailable'
            elif not disk['admitted']:reason='Shared disk reservation unavailable'
            admission=dict(admitted=reason is None,reason=reason,available_memory_bytes=memory,
                host_memory_reserve_bytes=HOST_MEMORY_RESERVE,reserved_workers=len(rows),cpu_slots=cpu,
                disk=disk,unreconciled_launches=orphan_launches,enforcement='Cooperative fcntl reservations and host admission; no aggregate quota or cgroup')
            if reason is None:
                rows[key]=dict(owner_pid=os.getpid(),owner_token=self.owner,worker_pid=None,worker_token=None,
                    device=device,disk_bytes=DISK_BYTES)
            return admission

    def attach(self,job_id,store,pid):
        key=str(Path(store).resolve())+'/'+job_id
        with self.transaction() as rows:
            if key not in rows:raise ValueError('Analytic worker reservation disappeared')
            rows[key].update(worker_pid=pid,worker_token=process_token(pid))

    def release(self,job_id,store):
        with self.transaction() as rows:rows.pop(str(Path(store).resolve())+'/'+job_id,None)
