"""Live numerical-plant composition with the actual Rust station resource log.

Local synthetic readiness/pose assertions are not field detectors. The produced
decisions gate the plant; a second independent replay can verify the transcript.
"""
from hashlib import sha256
from pathlib import Path
import gzip
import json
import math
import subprocess
import uuid
from . import model, delivery_platform as platform

ROOT=model.ROOT
EXAMPLE=ROOT/'crates/osr-interlocking/examples/candidate_authority_bridge.rs'
BUILD=['cargo','build','--locked','-p','osr-interlocking','--example','candidate_authority_bridge','--message-format=json']
BASE=1_000_000_000

def sources():
    paths={Path(__file__),Path(model.__file__),Path(platform.__file__),EXAMPLE,ROOT/'Cargo.toml',ROOT/'Cargo.lock',ROOT/'rust-toolchain.toml',
        ROOT/'engineering/analysis/tests/test_ferrite_maglev_candidate_authority.py'}
    for name in ('osr-core','osr-interlocking'):
        base=ROOT/'crates'/name;paths.add(base/'Cargo.toml');paths.update(base.rglob('*.rs'))
    return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}

def build():
    r=subprocess.run(BUILD,cwd=ROOT,capture_output=True,text=True,timeout=300)
    if r.returncode:raise RuntimeError('Rust authority compiler failed: '+r.stderr[-2000:])
    artifacts=[Path(v['executable']) for line in r.stdout.splitlines() if line.startswith('{') and
        (v:=json.loads(line)).get('reason')=='compiler-artifact' and v.get('target',{}).get('name')=='candidate_authority_bridge' and v.get('executable')]
    if len(artifacts)!=1:raise ValueError('one actual authority binary required')
    return artifacts[0],dict(command=BUILD,exit_code=0,binary_sha256=sha256(artifacts[0].read_bytes()).hexdigest(),stderr=r.stderr)

def deployment(configuration_sha256,stops_m):
    if not isinstance(configuration_sha256,str) or len(configuration_sha256)!=64:raise ValueError('controlled candidate digest required')
    try:cfg=list(bytes.fromhex(configuration_sha256))
    except ValueError as e:raise ValueError('candidate hexadecimal identity required') from e
    if len(cfg)!=32 or not 2<=len(stops_m)<=10 or any(type(s) not in (int,float) or not math.isfinite(s) for s in stops_m) or any(b-a<400 for a,b in zip(stops_m,stops_m[1:])):raise ValueError('bounded ordered fixed-line station geometry required')
    # The departure station is a separate secured numerical domain. The
    # requested outgoing corridor starts beyond it, so its clear proof does not
    # falsely declare the departing train's occupied origin berth empty.
    bounds=[stops_m[0]+200.]
    for stop in stops_m[1:]:bounds.extend([stop-150.,stop+125.,stop+200.])
    resources=[dict(id=i,section=100+i,asset_id=f'candidate-leg-resource-{i}',kind='platform' if i%3==1 else 'track',controller=900,conflicts=[i],point_asset_id=None,
        clearance_basis='Live simulated full-consist position and length; synthetic numerical evidence, no physical detector acceptance') for i in range(len(bounds)-1)]
    participants=[dict(entity=i,role='Voter',session=1,public_key=[i]*32,revoked=False,resources=[]) for i in (1,2,3)]
    participants.append(dict(entity=101,role='Train',session=1,public_key=[5]*32,revoked=False,resources=[]))
    value=dict(schema='osr-tacs-railway/2',revision='candidate-live-numerical-line-1',approval_state='prototype-unapproved',
        runtime=dict(voters=[1,2,3],participants=participants,designed_revision='candidate-live-numerical-line-1',installed_state='not-installed',approved_operating_profile='prototype-unapproved',clock_error_ns=0),resources=resources,
        routes=[dict(id=1,asset_id='candidate-fixed-line',direction='Forward',leader_required=False,operating_scope='One six-car numerical train; no distributed/physical authority or fleet capacity claim',
            segments=[dict(resource=i,start_mm=round((start-bounds[0])*1000),end_mm=round((end-bounds[0])*1000),speed_limit_mmps=30000,downhill_permille=0) for i,(start,end) in enumerate(zip(bounds,bounds[1:]))],
            stopping_locations=[dict(asset_id=f'station-{j+1}',at_mm=round((stop-bounds[0])*1000),platform=j*3+1,charger_asset_id=f'services-{j+1}',minimum_departure_energy_wh=10000) for j,stop in enumerate(stops_m[1:])])],
        trains=[dict(asset_id='candidate-train-101',config=dict(owner=dict(train=101,session=1),configuration=cfg,length_mm=104500,minimum_deceleration_mmps2=600,reaction_time_ms=200,stop_margin_mm=20000,maximum_position_uncertainty_mm=500),
            integrity_arrangement='Six actual integrated rigid-car poses and104.5m consist; synthetic assertions; origin station separately secured in this one-train study',braking_evidence='Candidate clamp/capture calculation, physical acceptance open',permitted_route=1)],
        controllers=[dict(id=900,asset_id='candidate-local-controller',startup_epoch=1,restart_reconciliation='Retain committed arrival locks; only actual positive full-tail evidence clears')],protected_work_resources=[],maintenance_procedure='Offline source-bound simulation only')
    return dict(model=value,configuration=cfg,stops_m=list(stops_m))

class AuthorityClient:
    def __init__(self,configuration_sha256,route_stops_m,directory=None):
        self.configuration=configuration_sha256;self.stops=list(route_stops_m);self.before=sources();self.binary,self.compiler=build()
        self.directory=Path(directory) if directory is not None else ROOT/'build/candidate-authority'/uuid.uuid4().hex
        self.directory.mkdir(parents=True,exist_ok=False)
        self.initial=deployment(configuration_sha256,self.stops);(self.directory/'init.json').write_bytes(platform.encoded(self.initial))
        producer=dict(schema='osr-live-authority-producer/1',configuration_sha256=configuration_sha256,source_sha256=self.before,compiler=self.compiler,
            initial_sha256=sha256((self.directory/'init.json').read_bytes()).hexdigest(),**platform.FLAGS)
        (self.directory/'producer.json').write_bytes(platform.encoded(producer));self.producer_receipt_sha256=sha256((self.directory/'producer.json').read_bytes()).hexdigest()
        self.process=subprocess.Popen([str(self.binary)],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
        self.process.stdin.write(json.dumps(self.initial)+'\n');self.process.stdin.flush();line=self.process.stdout.readline()
        if not line:
            self.process.wait(timeout=10)
            raise RuntimeError('actual Rust authority failed to initialise: '+self.process.stderr.read()[-1500:])
        ready=json.loads(line)
        if ready!={'ready':True,'physical_output_authorised':False}:raise RuntimeError('actual Rust authority failed to initialise')
        self.stream=(self.directory/'decisions.jsonl.gz').open('wb');self.journal=gzip.GzipFile(fileobj=self.stream,mode='wb',mtime=0)
        self.sequence=0;self.records=0;self.closed=False;self.last_s=-1.;self.current_leg=None
    def _call(self,command,now_s):
        if self.closed:raise ValueError('closed authority client')
        platform.finite(now_s,minimum=0,maximum=3600)
        if now_s<self.last_s:raise ValueError('nonmonotone actual plant clock')
        self.last_s=now_s;command=dict(command,now_ns=BASE+round(now_s*1e9))
        self.process.stdin.write(json.dumps(command,allow_nan=False)+'\n');self.process.stdin.flush();line=self.process.stdout.readline()
        if not line:raise RuntimeError('Rust authority process ended: '+self.process.stderr.read()[-1500:])
        raw=json.loads(line);self.sequence+=1
        if raw.get('sequence')!=self.sequence or raw.get('physical_output_authorised') is not False or raw.get('configuration')!=self.initial['configuration']:raise ValueError('authority sequence/configuration/output mismatch')
        ok=raw.get('ok') is True
        event=dict(schema='osr-full-dynamics-authority/1',configuration_sha256=self.configuration,sequence=self.sequence,issued_s=now_s,expires_s=now_s+.1,
            protected=ok and raw['protected'],committed=ok and raw['committed'],receiver_ready=ok and raw['receiver_ready'],resistor_ready=ok and raw['resistor_ready'],
            actual_rust_protocol=True,physical_output_authorised=False,source_receipt_sha256=self.producer_receipt_sha256,
            leg=raw['leg'],raw_decision_sha256=platform.digest(raw))
        self.journal.write(platform.encoded(dict(command=command,response=raw,event=event)).replace(b'\n',b'')+b'\n');self.records+=1
        if self.records>500000:raise ValueError('bounded live authority history required')
        return event
    def prepare(self,leg,now_s,readiness=None,**kwargs):
        r=dict(readiness or {},**kwargs)
        values={name:r.get(name,False) for name in ('receiver_ready','resistor_ready','reserve_ready','doors_closed','train_healthy')}
        if any(type(v) is not bool for v in values.values()) or type(leg) is not int:raise ValueError('actual boolean readiness and integer leg required')
        self.current_leg=leg;return self._call(dict(kind='prepare',leg=leg,**values),now_s)
    def step(self,now_s,front_m,tail_m,speed_m_s,receiver_failed=False,resistor_ready=True):
        for v in (front_m,tail_m,speed_m_s):platform.finite(v,minimum=-1e6,maximum=1e6)
        if type(receiver_failed) is not bool or type(resistor_ready) is not bool:raise ValueError('actual health flags required')
        return self._call(dict(kind='sample',front_m=front_m,tail_m=tail_m,speed_m_s=speed_m_s,receiver_failed=receiver_failed,resistor_ready=resistor_ready),now_s)
    def close(self):
        if self.closed:return
        self.journal.close();self.stream.close();self.process.stdin.close()
        try:self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:self.process.kill();self.process.wait()
        self.closed=True
        if self.process.returncode:raise RuntimeError('authority bridge terminated abnormally: '+self.process.stderr.read()[-1500:])
        if sources()!=self.before:raise ValueError('authority sources changed during actual execution')
        files={n:sha256((self.directory/n).read_bytes()).hexdigest() for n in ('init.json','producer.json','decisions.jsonl.gz')}
        self.result=dict(schema='osr-live-authority-execution/1',configuration_sha256=self.configuration,source_sha256=self.before,source_unchanged=True,
            files_sha256=files,records=self.records,producer_receipt_sha256=self.producer_receipt_sha256,compiler=self.compiler,process_exit_code=0,**platform.FLAGS)
        (self.directory/'receipt.json').write_bytes(platform.encoded(self.result))
    def receipt(self):
        self.close();return dict(self.result,folder=str(self.directory.relative_to(ROOT)) if self.directory.is_relative_to(ROOT) else str(self.directory))
    def __enter__(self):return self
    def __exit__(self,*exc):self.close()

def verify_receipt(folder,*,configuration_sha256=None,replay=False):
    folder=Path(folder);names={'receipt.json','init.json','producer.json','decisions.jsonl.gz'}
    if folder.is_symlink() or {p.name for p in folder.iterdir()}!=names or any(p.is_symlink() or not p.is_file() for p in folder.iterdir()):raise ValueError('exact ordinary authority inventory required')
    if any((folder/n).stat().st_size>8*1024*1024 for n in names-{'decisions.jsonl.gz'}) or (folder/'decisions.jsonl.gz').stat().st_size>64*1024*1024:raise ValueError('authority evidence exceeds compressed bound')
    receipt=json.loads((folder/'receipt.json').read_bytes());producer=json.loads((folder/'producer.json').read_bytes())
    if receipt.get('schema')!='osr-live-authority-execution/1' or producer.get('schema')!='osr-live-authority-producer/1' or set(receipt.get('files_sha256',{}))!=names-{'receipt.json'}:raise ValueError('authority receipt coverage differs')
    if receipt.get('source_sha256')!=sources() or receipt.get('source_unchanged') is not True or producer['source_sha256']!=receipt['source_sha256']:raise ValueError('live authority source receipt stale')
    if configuration_sha256 is not None and receipt['configuration_sha256']!=configuration_sha256:raise ValueError('authority candidate mismatch')
    if any(v.get(k) is not False for v in (receipt,producer) for k in platform.FLAGS):raise ValueError('authority receipt asserted physical release')
    for name,d in receipt['files_sha256'].items():
        p=folder/name
        if p.parent!=folder or p.is_symlink() or sha256(p.read_bytes()).hexdigest()!=d:raise ValueError('authority raw bytes changed')
    if sha256((folder/'producer.json').read_bytes()).hexdigest()!=receipt['producer_receipt_sha256']:raise ValueError('authority producer identity differs')
    with gzip.open(folder/'decisions.jsonl.gz','rb') as stream:raw=stream.read(256*1024*1024+1)
    if len(raw)>256*1024*1024:raise ValueError('authority history exceeds raw bound')
    records=[json.loads(line) for line in raw.splitlines()];initial=json.loads((folder/'init.json').read_bytes())
    if len(records)!=receipt['records'] or len(records)>500000 or initial!=deployment(receipt['configuration_sha256'],initial['stops_m']) or producer['configuration_sha256']!=receipt['configuration_sha256'] or producer['initial_sha256']!=sha256((folder/'init.json').read_bytes()).hexdigest() or producer['compiler']!=receipt['compiler']:raise ValueError('authority decision history/configuration incomplete')
    last_s=-1.
    for i,r in enumerate(records,1):
        e=r['event'];d=r['response'];ok=d['ok'] is True
        if e['sequence']!=i or d['sequence']!=i or d['configuration']!=initial['configuration'] or e['configuration_sha256']!=receipt['configuration_sha256'] or e['source_receipt_sha256']!=receipt['producer_receipt_sha256'] or e['raw_decision_sha256']!=platform.digest(d):raise ValueError('authority decision identity differs')
        now=e['issued_s'];platform.finite(now,minimum=0,maximum=3600)
        if now<last_s or e['expires_s']!=now+.1 or r['command']['now_ns']!=BASE+round(now*1e9) or e.get('actual_rust_protocol') is not True:raise ValueError('authority decision age/provenance differs')
        last_s=now
        for key in ('protected','committed','receiver_ready','resistor_ready'):
            if e[key] is not (ok and d[key]):raise ValueError('authority decision does not match actual Rust result')
        if e['physical_output_authorised'] is not False or d['physical_output_authorised'] is not False:raise ValueError('physical output asserted')
    if replay:
        binary,compiler=build()
        if compiler['binary_sha256']!=receipt['compiler']['binary_sha256']:raise ValueError('authority executable differs')
        data=json.dumps(initial)+'\n'+''.join(json.dumps(r['command'])+'\n' for r in records)
        result=subprocess.run([str(binary)],input=data,text=True,capture_output=True,cwd=ROOT,timeout=300)
        outputs=[json.loads(line) for line in result.stdout.splitlines()]
        if result.returncode or outputs[1:]!=[r['response'] for r in records]:raise ValueError('independent Rust authority transcript replay differs')
    return dict(verified=True,replayed=replay,records=len(records),configuration_sha256=receipt['configuration_sha256'],**platform.FLAGS)
