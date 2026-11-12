"""Explicit opt-in Rust scheduler over the existing delivery task contract.

Never builds or falls back on schedule(). The default delivery evaluator remains
unchanged. Records bind source, toolchain and executable; they are not OS isolation.
"""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import time

SOURCES=('Cargo.toml','Cargo.lock','rust-toolchain.toml','crates/osr-design-search/Cargo.toml',
    'crates/osr-design-search/src/lib.rs','crates/osr-design-search/src/canonical.rs',
    'crates/osr-design-search/src/scheduling.rs','crates/osr-design-search/src/bin/osr-delivery-schedule.rs',
    'engineering/outline/native_schedule.py')
MAX_BYTES=16*1024**2


def _read(path, maximum=MAX_BYTES):
    path=Path(path)
    with os.fdopen(os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK),'rb') as f:
        st=os.fstat(f.fileno())
        if not stat.S_ISREG(st.st_mode) or st.st_size>maximum:raise ValueError('Bounded ordinary source/binary required')
        raw=f.read(maximum+1)
    if len(raw)>maximum:raise ValueError('Read budget exceeded')
    return raw


def _sources(root):return {p:hashlib.sha256(_read(Path(root)/p)).hexdigest() for p in SOURCES}
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
        self.verify()

    def verify(self):
        r=self.receipt
        if r.get('schema')!='osr-delivery-schedule-build/1' or r['source_sha256']!=_sources(self.root) or r['tools']!=_tools():
            raise ValueError('Scheduler source/tool receipt differs')
        if hashlib.sha256(_read(self.binary)).hexdigest()!=r['binary_sha256']:raise ValueError('Scheduler executable differs')

    def schedule(self,tasks,resources,case):
        raw=request(tasks,resources,case);self.verify()
        result=subprocess.run([str(self.binary)],input=raw,capture_output=True,timeout=60)
        self.verify()
        if result.returncode:raise ValueError(result.stderr.decode(errors='replace').strip())
        if len(result.stdout)>32*1024**2:raise ValueError('Scheduling response exceeds budget')
        value=json.loads(result.stdout)
        if value.get('engineering_release') is not False:raise ValueError('Conditional scheduling result required')
        return value
