"""Loopback job control; workers calculate, one coordinator publishes artifacts."""
from hashlib import sha256
import json
import gzip
import io
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import threading
import time
from urllib.parse import unquote,urlsplit
from uuid import uuid4

from engineering.station_rail.common import encoded,digest,identity
from engineering.performance import disk_admission
from engineering.trip_dynamics.interactive import _loopback
from . import completion,city_workflow,publication_cache

MAX_REQUEST=2*1024**2
MAX_JOB_BYTES=64*1024**2
MAX_STORE_BYTES=512*1024**2
WALL_SECONDS=120
MINIMUM_FREE_GIB=4.0
FLAGS=city_workflow.FLAGS
STORE='build/city-studies'


def _json(raw):
    def pairs(rows):
        value={}
        for key,item in rows:
            if key in value:raise ValueError('Duplicate city study input key')
            value[key]=item
        return value
    return json.loads(raw,object_pairs_hook=pairs,
        parse_constant=lambda _:(_ for _ in ()).throw(ValueError('Finite city inputs required')))


class CityStudyService:
    def __init__(self,root,*,store=None):
        self.root=Path(root).resolve()
        requested_store=Path(store).expanduser() if store is not None else self.root/STORE
        if not requested_store.is_absolute():requested_store=self.root/requested_store
        completion._ordinary(requested_store)
        self.store=requested_store.resolve()
        if store is not None and self.store.is_relative_to(self.root):
            raise ValueError('Explicit city-study store must be outside the source checkout')
        self.lock=threading.RLock();self.jobs={};self.closed=False
        self.verified_runs={}
        self._lease=completion._locked(self.store);self._lease.__enter__()
        self.stop=threading.Event()
        self.watcher=threading.Thread(target=self._watch,name='osr-city-study-supervisor',daemon=True)
        self.watcher.start()

    def _watch(self):
        while not self.stop.wait(.5):
            with self.lock:
                for job_id,record in list(self.jobs.items()):
                    if not record.get('finished'):
                        try:
                            status=self._poll(job_id)
                            record['finished']=status['state']!='running'
                        except (ValueError,KeyError,TypeError,OSError) as exc:
                            self._failed_integrity(job_id,str(exc))

    def _job(self,job_id):
        if not re.fullmatch('[0-9a-f]{32}',job_id):raise ValueError('Known city study identifier required')
        return completion._ordinary(self.store/job_id)

    def _usage(self):
        total=0
        if self.store.exists():
            for p in self.store.rglob('*'):
                completion._ordinary(p)
                if p.is_file():total+=p.stat().st_size
        return total

    def _write(self,folder,status):
        completion._write(folder/'status.json',status)

    def _verify(self,folder):
        raw=completion._ordinary(folder/'manifest.json').read_bytes();manifest=json.loads(raw)
        stamp=(sha256(raw).hexdigest(),publication_cache._signature(self.root,folder,manifest))
        cached=self.verified_runs.get(str(folder))
        if cached and cached[0]==stamp:return cached[1]
        actual=city_workflow.verify(folder,root=self.root)
        after=(sha256((folder/'manifest.json').read_bytes()).hexdigest(),publication_cache._signature(self.root,folder,actual))
        if after!=stamp:raise ValueError('City study changed during verification')
        self.verified_runs[str(folder)]=(stamp,actual)
        return actual

    def _failed_integrity(self,job_id,error):
        folder=self._job(job_id);record=self.jobs.get(job_id)
        if record is not None:
            process=record['process']
            if process.poll() is None:
                try:os.killpg(process.pid,signal.SIGKILL)
                except ProcessLookupError:pass
            process.wait(timeout=5);record['log'].close();record['finished']=True
        old=completion._ordinary(folder/'status.json')
        if old.exists():old.replace(folder/('status.invalid-'+uuid4().hex+'.json'))
        status=dict(schema='osr-city-study-job/1',job_id=job_id,state='failed-integrity',
            error=error,request_and_logs_retained=True,**FLAGS)
        self._write(folder,status);return status

    def _poll(self,job_id):
        folder=self._job(job_id);record=self.jobs.get(job_id)
        path=completion._ordinary(folder/'status.json')
        try:
            status=json.loads(path.read_bytes())
            if (not isinstance(status,dict) or status.get('job_id')!=job_id
                    or status.get('state') not in ('running','completed','stale','interrupted',
                        'failed','failed-integrity','failed-output-budget','timed-out')):
                raise ValueError('Invalid retained city job status')
        except (ValueError,KeyError,TypeError) as exc:
            return self._failed_integrity(job_id,str(exc))
        if status['state']!='running':
            if status['state']=='completed':
                try:self._verify(folder/'artifacts')
                except (ValueError,KeyError,TypeError,OSError) as exc:
                    status.update(state='stale',error=str(exc));self._write(folder,status)
            return status
        if record is None:
            status.update(state='interrupted',error='Previous coordinator is unavailable; retained artifacts require explicit verification')
            self._write(folder,status);return status
        process=record['process']
        size=sum(p.stat().st_size for p in folder.rglob('*') if p.is_file())
        if process.poll() is None and size>MAX_JOB_BYTES:
            os.killpg(process.pid,signal.SIGKILL);process.wait(timeout=5)
            status.update(state='failed-output-budget',error='City calculation exceeded its output budget')
        elif process.poll() is None and time.monotonic()-record['started']>WALL_SECONDS:
            os.killpg(process.pid,signal.SIGKILL);process.wait(timeout=5)
            status.update(state='timed-out',error='City calculation exceeded its wall-clock budget')
        elif process.poll() is None:return status
        elif process.returncode!=0:
            status.update(state='failed',error='The bounded city worker failed; its request and log were preserved')
        else:
            try:
                if sum(p.stat().st_size for p in folder.rglob('*') if p.is_file())>MAX_JOB_BYTES:
                    raise ValueError('City calculation exceeded its output budget')
                m=self._verify(folder/'artifacts')
                result=json.loads((folder/'artifacts/summary.json').read_bytes())
                status.update(state='completed',manifest_id=m['manifest_id'],summary=result,
                    artifact_url='/api/city-studies/'+job_id+'/artifacts/')
            except (ValueError,KeyError,TypeError,OSError) as exc:
                status.update(state='failed-integrity',error=str(exc))
        record['log'].close();self._write(folder,status);return status

    def submit(self,request):
        request=city_workflow.normalize(request)
        with self.lock:
            if self.closed:raise ValueError('City calculation service is closed')
            completion._ordinary(self.store);self.store.mkdir(parents=True,exist_ok=True)
            detail=publication_cache.json_member('cities/'+request['city_slug']+'.json.gz',self.root)
            request.setdefault('expected_outline_evaluation_id',detail['evaluation_id'])
            key=identity(dict(request=request,seed_id=detail['planning_seed']['seed_id'],
                sources=city_workflow._sources(self.root)))
            for p in self.store.glob('*/status.json'):
                status=self._poll(p.parent.name)
                if status.get('request_key')==key and status['state']=='completed':
                    try:
                        self._verify(p.parent/'artifacts')
                        return dict(status,cache_hit=True)
                    except (ValueError,KeyError,TypeError,OSError):pass
                if status['state']=='running':return dict(status,busy=True)
            # The source checkout and the job store may be on different mounts.
            # Admit against the filesystem that will receive the generated data.
            admission=disk_admission(self.store,minimum_free_gib=MINIMUM_FREE_GIB)
            if not admission['admitted']:
                return dict(schema='osr-city-study-job/1',state='held',
                    error=admission['reason'],cache_hit=False,
                    resource_admission=admission,
                    resource_budget=dict(worker_processes=1,wall_seconds=WALL_SECONDS,
                        cpu_seconds=90,address_space_bytes=3*1024**3,
                        maximum_output_bytes=MAX_JOB_BYTES,
                        minimum_free_reserve_gib=MINIMUM_FREE_GIB,native_solver_jobs=0),
                    **FLAGS)
            if self._usage()+MAX_JOB_BYTES>MAX_STORE_BYTES:
                raise ValueError('City study storage budget reached; preserve/export finished runs before cleanup')
            job_id=uuid4().hex;folder=self._job(job_id);folder.mkdir()
            (folder/'request.json').write_bytes(encoded(request))
            log=(folder/'worker.log').open('wb')
            env=dict(os.environ)
            for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):env[name]='1'
            process=subprocess.Popen([sys.executable,'-m','engineering.outline.city_worker',
                '--request',str(folder/'request.json'),'--output',str(folder/'artifacts'),
                '--root',str(self.root)],cwd=self.root,env=env,stdout=log,stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,start_new_session=True)
            status=dict(schema='osr-city-study-job/1',job_id=job_id,state='running',request_key=key,
                cache_hit=False,resource_budget=dict(worker_processes=1,wall_seconds=WALL_SECONDS,
                    cpu_seconds=90,address_space_bytes=3*1024**3,maximum_output_bytes=MAX_JOB_BYTES,
                    minimum_free_reserve_gib=MINIMUM_FREE_GIB,native_solver_jobs=0),
                resource_admission=admission,**FLAGS)
            self.jobs[job_id]=dict(process=process,log=log,started=time.monotonic())
            self._write(folder,status);return status

    def status(self,job_id):
        with self.lock:return self._poll(job_id)

    def artifact(self,job_id,name):
        with self.lock:
            status=self._poll(job_id)
            if status['state']!='completed':raise ValueError('City study is not complete')
            folder=self._job(job_id)/'artifacts';manifest=self._verify(folder)
            if name=='manifest.json':return (folder/name).read_bytes()
            stored=manifest['artifact_paths'].get(name,name)
            if stored not in manifest['files_sha256']:raise ValueError('Known city study artifact required')
            raw=completion._ordinary(folder/stored).read_bytes()
            if sha256(raw).hexdigest()!=manifest['files_sha256'][stored]:raise ValueError('City study artifact differs')
            if stored!=name and stored.endswith('.gz'):
                with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:raw=stream.read(96*1024**2+1)
                if len(raw)>96*1024**2:raise ValueError('City study response exceeds read budget')
            return raw

    def close(self):
        with self.lock:
            if self.closed:return
            self.closed=True;self.stop.set()
        try:
            with self.lock:
                for job_id,record in self.jobs.items():
                    try:
                        if record['process'].poll() is None:
                            os.killpg(record['process'].pid,signal.SIGTERM)
                            try:record['process'].wait(timeout=3)
                            except subprocess.TimeoutExpired:
                                os.killpg(record['process'].pid,signal.SIGKILL);record['process'].wait(timeout=3)
                            try:
                                status=json.loads((self._job(job_id)/'status.json').read_bytes())
                                status.update(state='interrupted',error='City service closed; calculation artifacts retained')
                                self._write(self._job(job_id),status)
                            except (ValueError,KeyError,TypeError,OSError) as exc:
                                self._failed_integrity(job_id,str(exc))
                    finally:record['log'].close()
        finally:
            self.watcher.join(timeout=3)
            self._lease.__exit__(None,None,None)


def handle_api(handler):
    path=unquote(urlsplit(handler.path).path)
    if path!='/api/city-studies' and not path.startswith('/api/city-studies/'):return False
    post=handler.command=='POST'
    if handler.command not in ('GET','HEAD','POST'):
        handler.respond(405,{'error':'GET or POST required'});return True
    if not _loopback(handler,post=post):
        handler.respond(403,{'error':'Matching loopback Host and Origin required'});return True
    try:
        service=getattr(handler.server,'city_studies',None)
        if service is None:raise ValueError('Mapped-city job service is not configured')
        if post:
            if path!='/api/city-studies':raise ValueError('POST the mapped-city study endpoint')
            length=handler.headers.get('Content-Length','')
            if (handler.headers.get('Content-Type','').split(';')[0]!='application/json'
                    or not length.isdecimal() or not 0<int(length)<=MAX_REQUEST):
                raise ValueError('Bounded application/json city request required')
            status=service.submit(_json(handler.rfile.read(int(length))))
            handler.respond(429 if status.get('busy') else 200 if status['state']=='completed' else 202,status)
        elif path=='/api/city-studies':
            handler.respond(200,dict(schema='osr-city-study-options/1',selections=list(city_workflow.SELECTIONS),
                service_bounds=city_workflow.SERVICE_BOUNDS,alignment_bounds=city_workflow.ALIGNMENT_BOUNDS,
                maximum_request_bytes=MAX_REQUEST,**FLAGS))
        else:
            parts=path.removeprefix('/api/city-studies/').split('/')
            if len(parts)==1:handler.respond(200,service.status(parts[0]))
            elif len(parts)>=3 and parts[1]=='artifacts':
                handler.respond(200,service.artifact(parts[0],'/'.join(parts[2:])))
            else:raise ValueError('Known mapped-city study route required')
    except (ValueError,KeyError,TypeError,OSError) as exc:
        handler.respond(400,{'error':str(exc),**FLAGS})
    return True
