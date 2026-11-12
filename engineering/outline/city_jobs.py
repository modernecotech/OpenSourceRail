"""Loopback job control; workers calculate, one coordinator publishes artifacts."""
from hashlib import sha256
import json
import gzip
import io
from math import isfinite
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
MAX_QUEUED_STATUS_BYTES=16*1024
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
    def __init__(self,root,*,store=None,max_workers=1,resource_ledger=None,minimum_free_gib=None):
        self.root=Path(root).resolve()
        requested_store=Path(store).expanduser() if store is not None else self.root/STORE
        if not requested_store.is_absolute():requested_store=self.root/requested_store
        completion._ordinary(requested_store)
        self.store=requested_store.resolve()
        if store is not None and self.store.is_relative_to(self.root):
            raise ValueError('Explicit city-study store must be outside the source checkout')
        if type(max_workers) is not int or max_workers not in (1,2):raise ValueError('One or two analytic workers required')
        self.max_workers=max_workers;self.pending=[]
        self.reservations=None;self.queuing=max_workers==2 or resource_ledger is not None
        self.minimum_free_gib=(20.0 if self.queuing else MINIMUM_FREE_GIB) if minimum_free_gib is None else minimum_free_gib
        if (type(self.minimum_free_gib) not in (int,float) or not isfinite(self.minimum_free_gib)
            or not 1<=self.minimum_free_gib<=1024 or self.queuing and self.minimum_free_gib<20):
            raise ValueError('Valid disk reserve required; queued workers retain at least20GiB')
        if self.queuing:
            from .city_resources import Reservations,DEFAULT_LEDGER
            ledger=Path(resource_ledger or DEFAULT_LEDGER).expanduser().resolve()
            if ledger.is_relative_to(self.root):raise ValueError('Worker reservation ledger must be outside source')
            self.reservations=Reservations(ledger)
        self.lock=threading.RLock();self.jobs={};self.closed=False;self.reservation_errors={}
        self.verified_runs={}
        self.completed_by_key={};self.indexed_key_by_job={}
        self._lease=completion._locked(self.store);self._lease.__enter__()
        self.stop=threading.Event()
        try:
            self._rebuild_completed_index()
            self.watcher=threading.Thread(target=self._watch,name='osr-city-study-supervisor',daemon=True)
            self.watcher.start()
        except BaseException:
            self._lease.__exit__(*sys.exc_info())
            raise

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
                if self.queuing:self._dispatch()

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

    def _set_index(self,job_id,status):
        previous=self.indexed_key_by_job.pop(job_id,None)
        if previous is not None:
            jobs=self.completed_by_key.get(previous,[])
            jobs=[value for value in jobs if value!=job_id]
            if jobs:self.completed_by_key[previous]=jobs
            else:self.completed_by_key.pop(previous,None)
        key=status.get('request_key')
        if (status.get('state')!='completed' or not isinstance(key,str)
                or not re.fullmatch('[0-9a-f]{64}',key)):
            return
        self.completed_by_key.setdefault(key,[]).append(job_id)
        self.indexed_key_by_job[job_id]=key

    def _rebuild_completed_index(self):
        if not self.store.exists():return
        for path in sorted(self.store.glob('*/status.json')):
            job_id=path.parent.name
            self._job(job_id)
            try:
                status=json.loads(completion._ordinary(path).read_bytes())
                if (not isinstance(status,dict) or status.get('job_id')!=job_id
                        or status.get('state') not in ('queued','running','completed','stale','interrupted',
                            'failed','failed-integrity','failed-output-budget','timed-out')):
                    raise ValueError('Invalid retained city job status')
            except (ValueError,KeyError,TypeError,OSError):
                # Use the normal integrity path so malformed records are retained
                # and surfaced exactly as they are during status polling.
                self._poll(job_id)
                continue
            if status['state']=='queued':
                self.pending.append(job_id)
            elif status['state']=='running':
                # A new coordinator has no process handle for an old worker.
                self._poll(job_id)
            else:
                # Completed records are only hints here. Their artifacts and
                # source bindings are verified again when a matching key is used.
                self._set_index(job_id,status)

        self.pending.sort(key=lambda job:json.loads((self._job(job)/'status.json').read_bytes()).get('queued_at_ns',0))

    def _write(self,folder,status):
        if status.get('state')=='queued' and len(encoded(status))>MAX_QUEUED_STATUS_BYTES:
            raise ValueError('Queued control record exceeds its reserved byte budget')
        completion._write(folder/'status.json',status)
        self._set_index(folder.name,status)

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

    def _release_reservation(self,job_id):
        try:self.reservations.release(job_id,self.store)
        except (ValueError,KeyError,TypeError,OSError) as exc:
            # Failed accounting must not prevent stopping other owned workers.
            # The ledger remains held for reconciliation, never silently cleared.
            self.reservation_errors[job_id]=str(exc)

    def _failed_integrity(self,job_id,error):
        folder=self._job(job_id);record=self.jobs.get(job_id)
        if record is not None:
            process=record['process']
            if process.poll() is None:
                try:os.killpg(process.pid,signal.SIGKILL)
                except ProcessLookupError:pass
            process.wait(timeout=5);record['log'].close();record['finished']=True
        if job_id in self.pending:self.pending.remove(job_id)
        if self.reservations:self._release_reservation(job_id)
        old=completion._ordinary(folder/'status.json')
        if old.exists():old.replace(folder/('status.invalid-'+uuid4().hex+'.json'))
        status=dict(schema='osr-city-study-job/1',job_id=job_id,state='failed-integrity',
            error=error,request_and_logs_retained=True,
            resource_release_warning=self.reservation_errors.get(job_id),**FLAGS)
        self._write(folder,status);return status

    def _poll(self,job_id):
        folder=self._job(job_id);record=self.jobs.get(job_id)
        path=completion._ordinary(folder/'status.json')
        try:
            status=json.loads(path.read_bytes())
            if (not isinstance(status,dict) or status.get('job_id')!=job_id
                    or status.get('state') not in ('queued','running','completed','stale','interrupted',
                        'failed','failed-integrity','failed-output-budget','timed-out')):
                raise ValueError('Invalid retained city job status')
        except (ValueError,KeyError,TypeError) as exc:
            return self._failed_integrity(job_id,str(exc))
        self._set_index(job_id,status)
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
        record['log'].close();record['finished']=True
        if self.reservations:self._release_reservation(job_id)
        if job_id in self.reservation_errors:status['resource_release_warning']=self.reservation_errors[job_id]
        self._write(folder,status);return status

    def submit(self,request):
        request=city_workflow.normalize(request)
        with self.lock:
            if self.closed:raise ValueError('City calculation service is closed')
            completion._ordinary(self.store);self.store.mkdir(parents=True,exist_ok=True)
            detail=publication_cache.json_member('cities/'+request['city_slug']+'.json.gz',self.root)
            request.setdefault('expected_outline_evaluation_id',detail['evaluation_id'])
            parent=None
            if 'base_study_id' in request:
                parent_id=request['base_study_id'];parent_status=self._poll(parent_id)
                if parent_status['state']!='completed':raise ValueError('Completed verified parent city study required')
                parent_folder=self._job(parent_id)/'artifacts'
                parent=city_workflow.parent_snapshot(parent_folder,parent_id,root=self.root,
                    verified_manifest=self._verify(parent_folder))
            key_fields=dict(request=request,seed_id=detail['planning_seed']['seed_id'],
                sources=city_workflow._sources(self.root))
            if parent is not None:key_fields['parent_snapshot_id']=parent['snapshot_id']
            key=identity(key_fields)
            for job_id in tuple(self.completed_by_key.get(key,())):
                status=self._poll(job_id)
                if status.get('request_key')==key and status['state']=='completed':
                    try:
                        artifacts=self._job(job_id)/'artifacts'
                        self._verify(artifacts)
                        retained_request=city_workflow.read_json(artifacts,'request.json')
                        if encoded(retained_request)!=encoded(request):
                            raise ValueError('Completed city study request does not match its indexed cache identity')
                        return dict(status,cache_hit=True)
                    except (ValueError,KeyError,TypeError,OSError) as exc:
                        self._failed_integrity(job_id,str(exc))
            if self.queuing:return self._submit_queued(request,key,parent)
            for job_id,record in self.jobs.items():
                if record.get('finished'):continue
                status=self._poll(job_id)
                record['finished']=status['state']!='running'
                if status['state']=='running':return dict(status,busy=True)
            # The source checkout and the job store may be on different mounts.
            # Admit against the filesystem that will receive the generated data.
            admission=disk_admission(self.store,minimum_free_gib=self.minimum_free_gib)
            if not admission['admitted']:
                return dict(schema='osr-city-study-job/1',state='held',
                    error=admission['reason'],cache_hit=False,
                    resource_admission=admission,
                    resource_budget=dict(worker_processes=1,wall_seconds=WALL_SECONDS,
                        cpu_seconds=90,address_space_bytes=3*1024**3,
                        maximum_output_bytes=MAX_JOB_BYTES,
                        minimum_free_reserve_gib=self.minimum_free_gib,native_solver_jobs=0),
                    **FLAGS)
            if self._usage()+MAX_JOB_BYTES>MAX_STORE_BYTES:
                raise ValueError('City study storage budget reached; preserve/export finished runs before cleanup')
            job_id=uuid4().hex;folder=self._job(job_id);folder.mkdir()
            (folder/'request.json').write_bytes(encoded(request))
            parent_args=[]
            if parent is not None:
                (folder/'parent-study.json').write_bytes(encoded(parent))
                parent_args=['--parent-snapshot',str(folder/'parent-study.json')]
            status=dict(schema='osr-city-study-job/1',job_id=job_id,state='running',request_key=key,
                cache_hit=False,resource_budget=self._budget(),resource_admission=admission,**FLAGS)
            return self._launch(folder,status)

    def _budget(self):
        return dict(worker_processes=1,wall_seconds=WALL_SECONDS,cpu_seconds=90,
            address_space_bytes=3*1024**3,maximum_output_bytes=MAX_JOB_BYTES,
            minimum_free_reserve_gib=self.minimum_free_gib,native_solver_jobs=0)

    def _launch(self,folder,status):
        job_id=folder.name
        parent_args=['--parent-snapshot',str(folder/'parent-study.json')] if (folder/'parent-study.json').exists() else []
        log=(folder/'worker.log').open('wb')
        env=dict(os.environ)
        for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):env[name]='1'
        try:
            process=subprocess.Popen([sys.executable,'-m','engineering.outline.city_worker',
                '--request',str(folder/'request.json'),'--output',str(folder/'artifacts'),
                '--root',str(self.root),*parent_args],cwd=self.root,env=env,stdout=log,stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,start_new_session=True)
        except BaseException:
            log.close()
            if self.reservations:self._release_reservation(job_id)
            raise
        self.jobs[job_id]=dict(process=process,log=log,started=time.monotonic())
        if self.reservations:self.reservations.attach(job_id,self.store,process.pid)
        status.update(state='running',resource_budget=self._budget())
        self._write(folder,status);return status

    def _submit_queued(self,request,key,parent):
        self._dispatch()
        for job_id in [*self.pending,*self.jobs]:
            status=self._poll(job_id)
            if status['state'] in ('queued','running') and status.get('request_key')==key:
                return status
        if len(self.pending)>=4:
            return dict(schema='osr-city-study-job/1',state='held',busy=True,
                error='Four pending city requests already retained',**FLAGS)
        # Encode before admission: ASCII escaping and parent snapshots can be
        # much larger than their character counts or on-disk compressed source.
        request_raw=encoded(request);parent_raw=encoded(parent) if parent is not None else None
        if len(request_raw)>MAX_REQUEST or parent_raw is not None and len(parent_raw)>city_workflow.MAX_PARENT_SNAPSHOT_BYTES:
            raise ValueError('Queued request or parent snapshot exceeds its byte budget')
        # Four filesystem blocks plus two maximum queued-status generations and
        # ledger bookkeeping supplement exact payload bytes. This is conservative
        # allocation admission; it is not an aggregate quota.
        growth=len(request_raw)+(len(parent_raw) if parent_raw is not None else 0)+4*4096+2*MAX_QUEUED_STATUS_BYTES
        active=sum(not r.get('finished') for r in self.jobs.values())
        if self._usage()+growth+active*MAX_JOB_BYTES>MAX_STORE_BYTES:
            return dict(schema='osr-city-study-job/1',state='held',cache_hit=False,request_accepted=False,
                error='Insufficient store reserve to retain queued request and control files',**FLAGS)
        job_id=uuid4().hex;folder=self._job(job_id)
        status=dict(schema='osr-city-study-job/1',job_id=job_id,state='queued',request_key=key,
            queued_at_ns=time.time_ns(),request_sha256=sha256(request_raw).hexdigest(),
            parent_snapshot_sha256=sha256(parent_raw).hexdigest() if parent_raw is not None else None,
            queued_sources=city_workflow._sources(self.root),cache_hit=False,resource_budget=self._budget(),
            queued_payload_bytes=dict(request=len(request_raw),parent_snapshot=len(parent_raw) if parent_raw is not None else 0),
            queued_control_reservation_bytes=growth,**FLAGS)
        try:
            with self.reservations.stage_metadata(self.store,self.minimum_free_gib,growth) as admission:
                if not admission['admitted']:
                    return dict(schema='osr-city-study-job/1',state='held',cache_hit=False,request_accepted=False,
                        error=admission['reason'],resource_admission=admission,**FLAGS)
                # Repeat the store check inside the shared admission transaction.
                if self._usage()+growth+active*MAX_JOB_BYTES>MAX_STORE_BYTES:
                    return dict(schema='osr-city-study-job/1',state='held',cache_hit=False,request_accepted=False,
                        error='Retained store changed before queue admission',**FLAGS)
                folder.mkdir();(folder/'request.json').write_bytes(request_raw)
                if parent_raw is not None:(folder/'parent-study.json').write_bytes(parent_raw)
                self.pending.append(job_id);self._write(folder,status)
        except (ValueError,KeyError,TypeError,OSError) as exc:
            if folder.exists():raise
            return dict(schema='osr-city-study-job/1',state='held',cache_hit=False,request_accepted=False,
                error='Shared metadata reservation unavailable: '+str(exc),**FLAGS)
        self._dispatch()
        return self._poll(job_id)

    def _dispatch(self):
        if self.closed:return
        for job_id,record in list(self.jobs.items()):
            if not record.get('finished'):self._poll(job_id)
        while self.pending and sum(not r.get('finished') for r in self.jobs.values())<self.max_workers:
            job_id=self.pending[0];folder=self._job(job_id)
            try:
                status=json.loads((folder/'status.json').read_bytes())
                if status['state']!='queued':self.pending.pop(0);continue
                if (digest(folder/'request.json')!=status['request_sha256']
                    or status['queued_sources']!=city_workflow._sources(self.root)
                    or ((digest(folder/'parent-study.json') if (folder/'parent-study.json').exists() else None)!=status['parent_snapshot_sha256'])):
                    raise ValueError('Queued request, parent snapshot or source changed')
                request=city_workflow.normalize(_json((folder/'request.json').read_bytes()))
                detail=publication_cache.json_member('cities/'+request['city_slug']+'.json.gz',self.root)
                if request.get('expected_outline_evaluation_id')!=detail['evaluation_id']:raise ValueError('Queued outline changed')
                fields=dict(request=request,seed_id=detail['planning_seed']['seed_id'],sources=city_workflow._sources(self.root))
                if status['parent_snapshot_sha256'] is not None:
                    parent=_json((folder/'parent-study.json').read_bytes());fields['parent_snapshot_id']=parent['snapshot_id']
                if identity(fields)!=status['request_key']:raise ValueError('Queued request identity changed')
            except (ValueError,KeyError,TypeError,OSError) as exc:
                self._failed_integrity(job_id,str(exc));continue
            if self._usage()+MAX_JOB_BYTES*(1+sum(not r.get('finished') for r in self.jobs.values()))>MAX_STORE_BYTES:
                status['resource_admission']=dict(admitted=False,reason='Retained store plus outstanding worker outputs exceeds store reserve')
                self._write(folder,status);break
            try:admission=self.reservations.claim(job_id,self.store,self.minimum_free_gib)
            except (ValueError,KeyError,TypeError,OSError) as exc:admission=dict(admitted=False,reason='Shared reservation ledger unavailable: '+str(exc))
            status['resource_admission']=admission
            if not admission['admitted']:self._write(folder,status);break
            self.pending.pop(0)
            try:self._launch(folder,status)
            except (ValueError,OSError,subprocess.SubprocessError) as exc:
                self._failed_integrity(job_id,'Worker launch/reservation failed: '+str(exc))

    def status(self,job_id):
        with self.lock:
            if self.queuing:self._dispatch()
            return self._poll(job_id)

    def corridor_proposal(self):
        from . import corridor_revision
        with self.lock:return corridor_revision.proposal(self.root)

    def corridor_comparison(self,before_id,after_id):
        from . import corridor_revision
        with self.lock:
            before_status=self._poll(before_id);after_status=self._poll(after_id)
            if before_status['state']!='completed' or after_status['state']!='completed':
                raise ValueError('Two completed, source-verified city studies are required')
            proposal=corridor_revision.proposal(self.root)
            load=lambda job,name:json.loads(self.artifact(job,name))
            # Retained status records are hints; bind reuse to the verified
            # artifact manifests, not a mutable status manifest_id field.
            before_manifest=load(before_id,'manifest.json');after_manifest=load(after_id,'manifest.json')
            key=identity(dict(proposal=proposal,before=before_manifest['manifest_id'],
                after=after_manifest['manifest_id'],jobs=[before_id,after_id]))
            cache=getattr(self,'corridor_comparisons',{})
            if key in cache:return dict(cache[key],cache_hit=True)
            report=corridor_revision.compare(proposal,
                load(before_id,'result.json'),load(after_id,'result.json'),
                before_manifest,after_manifest,
                performance=dict(before=load(before_id,'performance.json'),after=load(after_id,'performance.json')))
            value=dict(schema='osr-corridor-comparison-response/1',report=report,
                jobs=dict(before=dict(job_id=before_id,manifest_id=before_manifest['manifest_id']),
                          after=dict(job_id=after_id,manifest_id=after_manifest['manifest_id'])))
            if len(cache)>=4:cache.pop(next(iter(cache)))
            cache[key]=value;self.corridor_comparisons=cache
            return dict(value,cache_hit=False)

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
                    finally:
                        record['log'].close()
                        if self.reservations:self._release_reservation(job_id)
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
        project=re.fullmatch('/api/city-studies/projects/([0-9a-f]{32})/([0-9a-f]{32})',path)
        if project and not post:
            from engineering.v07_project import from_comparison
            comparison=service.corridor_comparison(*project.groups())
            handler.respond(200,from_comparison(comparison['report']))
            return True
        comparison=re.fullmatch('/api/city-studies/comparisons/([0-9a-f]{32})/([0-9a-f]{32})',path)
        if not post and path=='/api/city-studies/scenarios/samawah-station-merge':
            handler.respond(200,service.corridor_proposal())
        elif not post and comparison:
            handler.respond(200,service.corridor_comparison(*comparison.groups()))
        elif post:
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
                maximum_request_bytes=MAX_REQUEST,maximum_worker_processes=service.max_workers,
                maximum_pending_requests=4 if service.queuing else 0,**FLAGS))
        else:
            parts=path.removeprefix('/api/city-studies/').split('/')
            if len(parts)==1:handler.respond(200,service.status(parts[0]))
            elif len(parts)>=3 and parts[1]=='artifacts':
                handler.respond(200,service.artifact(parts[0],'/'.join(parts[2:])))
            else:raise ValueError('Known mapped-city study route required')
    except (ValueError,KeyError,TypeError,OSError) as exc:
        handler.respond(400,{'error':str(exc),**FLAGS})
    return True
