"""Explicit opt-in Rust scheduler over the existing delivery task contract.

Never builds or falls back on schedule(). The default delivery evaluator remains
unchanged. Records bind source, toolchain and executable; they are not OS isolation.
"""
import hashlib
import json
import os
from pathlib import Path
import stat
import shutil
import tempfile
import subprocess
import time

SOURCES=('Cargo.toml','Cargo.lock','rust-toolchain.toml','crates/osr-design-search/Cargo.toml',
    'crates/osr-design-search/src/lib.rs','crates/osr-design-search/src/canonical.rs',
    'crates/osr-design-search/src/scheduling.rs','crates/osr-design-search/src/bin/osr-delivery-schedule.rs',
    'engineering/outline/native_schedule.py','engineering/outline/delivery_plan.py',
    'engineering/outline/__main__.py')
MAX_BYTES=16*1024**2
HELPER_LIMITS=dict(cpu_seconds=30,wall_seconds=45,address_space_bytes=512*1024**2,
    maximum_output_file_bytes=32*1024**2,maximum_temporary_output_bytes=96*1024**2,
    disk_enforcement="Per-file RLIMIT_FSIZE plus post-process aggregate observation; not an aggregate quota",
    maximum_parallel_helpers=1,maximum_request_bytes=MAX_BYTES)
_LOADED_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def _read(path, maximum=MAX_BYTES):
    path=Path(path)
    with os.fdopen(os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK),'rb') as f:
        st=os.fstat(f.fileno())
        if not stat.S_ISREG(st.st_mode) or st.st_size>maximum:raise ValueError('Bounded ordinary source/binary required')
        raw=f.read(maximum+1)
    if len(raw)>maximum:raise ValueError('Read budget exceeded')
    return raw


def _sources(root):
    sources={p:hashlib.sha256(_read(Path(root)/p)).hexdigest() for p in SOURCES}
    if sources['engineering/outline/native_schedule.py']!=_LOADED_SHA:
        raise ValueError('Loaded scheduler bridge changed; restart its caller')
    return sources
def _tools():return {p:subprocess.check_output([p,'--version'],text=True,timeout=10).strip() for p in ('cargo','rustc')}
def _encoded(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def build(root,target):
    root,target=Path(root).resolve(),Path(target).resolve()
    if target==root or root in target.parents:raise ValueError('External Rust build target required')
    target.mkdir(parents=True,exist_ok=True)
    from engineering.performance import disk_admission
    if not disk_admission(target,minimum_free_gib=20.75)['admitted']:raise ValueError('Build reserve unavailable')
    before,tools=_sources(root),_tools();started=time.perf_counter()
    command=['cargo','build','--offline','--locked','--release','-p','osr-design-search','--bin','osr-delivery-schedule','-j','2']
    result=subprocess.run(command,cwd=root,env={**os.environ,'CARGO_TARGET_DIR':str(target)},capture_output=True,timeout=180)
    (target/'build.stdout').write_bytes(result.stdout);(target/'build.stderr').write_bytes(result.stderr)
    if result.returncode:raise ValueError('Rust scheduler build failed; build logs retained')
    if before!=_sources(root) or tools!=_tools():raise ValueError('Build source/tool changed')
    size=sum(p.stat().st_size for p in target.rglob('*') if p.is_file())
    if size>768*1024**2:raise ValueError('Observed Rust target exceeds 768 MiB; retained for review')
    binary=target/'release/osr-delivery-schedule'
    receipt=dict(schema='osr-delivery-schedule-build/1',source_sha256=before,tools=tools,
        binary_sha256=hashlib.sha256(_read(binary)).hexdigest(),command=command,
        wall_seconds=time.perf_counter()-started,target_logical_bytes=size,
        enforcement='Preflight plus post-build observation; no aggregate quota')
    binary.with_suffix('.receipt.json').write_bytes(_encoded(receipt));return receipt


def request(tasks,resources,case):
    if case not in ('low','base','high'):raise ValueError('Known case required')
    result=dict(schema='osr-delivery-schedule-request/1',max_work=100_000_000,tasks=[],resources=[])
    for r in resources:
        n=r['capacity_by_case'][case]
        if type(n) is not int:raise ValueError('Integer capacity required')
        result['resources'].append(dict(resource_id=r['resource_id'],capacity=n))
    for t in tasks:
        ordinal=t.get('ordinal',0)
        if type(ordinal) is not int:raise ValueError('Integer ordinal required')
        requests=[]
        for r in t['resource_requests']:
            n=r.get('units_by_case',{}).get(case,r.get('units',1))
            if type(n) is not int:raise ValueError('Integer resource units required')
            requests.append(dict(resource_id=r['resource_id'],units=n))
        duration=t['duration_workdays'][case]
        if type(duration) not in (int,float):raise ValueError('Numeric duration required')
        result['tasks'].append(dict(task_id=t['task_id'],ordinal=ordinal,duration=duration,
            predecessors=t['predecessors'],requests=requests))
    raw=_encoded(result)
    if len(raw)>MAX_BYTES:raise ValueError('Scheduling request exceeds byte budget')
    return raw


class NativeSchedule:
    def __init__(self,root,binary):
        self.root,self.binary=Path(root).resolve(),Path(binary).absolute()
        self.receipt=json.loads(_read(self.binary.with_suffix('.receipt.json')))
        self.completed_helper_jobs=0
        self.verify()

    def verify(self):
        r=self.receipt
        if r.get('schema')!='osr-delivery-schedule-build/1' or r['source_sha256']!=_sources(self.root) or r['tools']!=_tools():
            raise ValueError('Scheduler source/tool receipt differs')
        if hashlib.sha256(_read(self.binary)).hexdigest()!=r['binary_sha256']:raise ValueError('Scheduler executable differs')

    def evaluation_identity(self):
        """Stable evaluator provenance, separate from physical candidate identity."""
        self.verify()
        r=self.receipt
        return dict(backend='rust',schema='osr-delivery-scheduler/1',
            source_sha256=dict(r['source_sha256']),tools=dict(r['tools']),
            binary_sha256=r['binary_sha256'],resource_limits=dict(HELPER_LIMITS),
            native_solver_jobs=0,native_helper_jobs=3)

    def schedule(self,tasks,resources,case):
        raw=request(tasks,resources,case);self.verify()
        limiter=shutil.which('prlimit')
        if not limiter:raise ValueError('prlimit required for explicit bounded Rust scheduling')
        from engineering.performance import disk_admission
        base=Path(os.environ.get('XDG_STATE_HOME',str(Path.home()/'.local/state')))/'opensourcerail/delivery-schedule-attempts'
        if base==self.root or self.root in base.resolve().parents:raise ValueError('External scheduler scratch required')
        base.mkdir(parents=True,exist_ok=True)
        if any(p.is_symlink() for p in (base,*base.parents)):raise ValueError('Ordinary scheduler scratch required')
        if not disk_admission(base,minimum_free_gib=20.1)['admitted']:
            raise ValueError('Rust scheduling disk reserve unavailable')
        folder=Path(tempfile.mkdtemp(prefix='attempt-',dir=base))
        succeeded=False
        try:
            (folder/'request.json').write_bytes(raw)
            (folder/'attempt.json').write_bytes(_encoded(dict(case=case,
                request_sha256=hashlib.sha256(raw).hexdigest(),
                binary_sha256=self.receipt['binary_sha256'],resource_limits=HELPER_LIMITS)))
            command=[limiter,'--cpu='+str(HELPER_LIMITS['cpu_seconds']),
                '--as='+str(HELPER_LIMITS['address_space_bytes']),
                '--fsize='+str(HELPER_LIMITS['maximum_output_file_bytes']),'--',str(self.binary)]
            with (folder/'stdout.json').open('wb') as out,(folder/'stderr.txt').open('wb') as err:
                result=subprocess.run(command,input=raw,stdout=out,stderr=err,
                    timeout=HELPER_LIMITS['wall_seconds'])
            aggregate=sum(p.stat().st_size for p in folder.iterdir() if p.is_file())
            if aggregate>HELPER_LIMITS['maximum_temporary_output_bytes']:raise ValueError('Observed scheduler scratch exceeds declared aggregate budget')
            self.verify()
            stdout=_read(folder/'stdout.json',32*1024**2)
            stderr=_read(folder/'stderr.txt',1024**2)
            if result.returncode:raise ValueError(stderr.decode(errors='replace').strip() or 'Rust scheduler failed')
            value=json.loads(stdout)
            if value.get('engineering_release') is not False:raise ValueError('Conditional scheduling result required')
            self.completed_helper_jobs+=1
            succeeded=True
            return value
        except Exception as exc:
            raise ValueError('Rust scheduling failed; immutable attempt retained at '+str(folder)+': '+str(exc)) from exc
        finally:
            if succeeded:shutil.rmtree(folder)
