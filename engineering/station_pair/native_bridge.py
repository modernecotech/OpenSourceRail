"""Content-addressed bounded native runs, separate from report/cost revisions."""
from pathlib import Path
import fcntl,gzip,json,os,shutil,subprocess,time,platform
from engineering.station_rail.common import digest,encoded,identity
from . import ROOT

NATIVE='engineering/station_pair/native'


def sources(root=ROOT):
    root=Path(root)
    base=root/NATIVE
    paths=[base/'Cargo.toml',base/'Cargo.lock']
    for name in ('src','tests'):paths.extend(sorted((base/name).rglob('*.rs')))
    return {p.relative_to(root).as_posix():digest(p) for p in paths}


def build(state,root=ROOT):
    root=Path(root).resolve();state=Path(state).resolve();state.mkdir(parents=True,exist_ok=True)
    target=state/'native-target';pin=sources(root)
    tools={name:subprocess.check_output([name,'--version'],text=True).strip() for name in ('cargo','rustc')}
    receipt=state/'native-build.json';binary=target/'release/osr-journey'
    if receipt.exists() and binary.exists():
        r=json.loads(receipt.read_bytes())
        if (r.get('source_sha256')==pin and r.get('tools')==tools and r.get('binary_sha256')==digest(binary)
                and r.get('receipt_id')==identity({k:v for k,v in r.items() if k!='receipt_id'})):
            return binary,r
    command=['cargo','build','--manifest-path',str(root/NATIVE/'Cargo.toml'),'--release','--locked','--offline']
    with (state/'native-build.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        env=dict(os.environ,CARGO_TARGET_DIR=str(target),CARGO_BUILD_JOBS='2',
                 RUSTFLAGS='-C link-arg=-Wl,--threads=1')
        with (state/'native-build.log').open('wb') as log:
            p=subprocess.run(command,cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
        if p.returncode:raise ValueError('Native build failed; retained '+str(state/'native-build.log'))
        if sources(root)!=pin:raise ValueError('Native source changed during build')
        r=dict(schema='osr-journey-build/1',source_sha256=pin,tools=tools,command=command,
            build_jobs=2,link_threads=1,binary_sha256=digest(binary))
        r['receipt_id']=identity(r);receipt.write_bytes(encoded(r));return binary,r


def execute(cases,state,*,root=ROOT,kernel=None):
    if not cases:return []
    state=Path(state).resolve();binary,build_receipt=build(state,root) if kernel is None else kernel
    if digest(binary)!=build_receipt['binary_sha256'] or sources(root)!=build_receipt['source_sha256']:
        raise ValueError('Native kernel/source changed')
    limiter=shutil.which('prlimit')
    if limiter is None:raise ValueError('prlimit required for explicit native runtime budget')
    resources=dict(cpu_s=60,address_space_bytes=1073741824,wall_timeout_s=75)
    context=dict(bridge_sha256=digest(__file__),resources=resources,
        platform=platform.platform(),machine=platform.machine(),
        limiter_version=subprocess.check_output([limiter,'--version'],text=True).strip())
    results=[]
    for start in range(0,len(cases),96):
        request=dict(schema='osr-journey-request/1',cases=cases[start:start+96]);raw=encoded(request)
        if len(raw)>8*1024**2:raise ValueError('Native request byte budget exceeded')
        key=identity(dict(request=request,build_receipt_id=build_receipt['receipt_id'],context=context))
        folder=state/'native-runs'/key;folder.mkdir(parents=True,exist_ok=True)
        output=folder/'output.json.gz';receipt=folder/'receipt.json'
        if receipt.exists() and output.exists():
            r=json.loads(receipt.read_bytes())
            if (r.get('request_sha256')!=identity(request) or r.get('build_receipt_id')!=build_receipt['receipt_id']
                    or r.get('context')!=context
                    or r.get('output_sha256')!=digest(output)
                    or r.get('input_gzip_sha256')!=digest(folder/'input.json.gz')
                    or gzip.decompress((folder/'input.json.gz').read_bytes())!=raw
                    or r.get('receipt_id')!=identity({k:v for k,v in r.items() if k!='receipt_id'})):
                raise ValueError('Native cached result changed')
            value=json.loads(gzip.decompress(output.read_bytes()))
        else:
            (folder/'input.json.gz').write_bytes(gzip.compress(raw,mtime=0))
            t=time.monotonic()
            failure=None;p=None
            with (folder/'stderr.log').open('wb') as err:
                try:
                    p=subprocess.run([limiter,'--cpu=60','--as=1073741824','--',str(binary)],input=raw,
                        stdout=subprocess.PIPE,stderr=err,timeout=75,cwd=folder)
                except (OSError,subprocess.TimeoutExpired) as exc:failure=exc
            execution=dict(exit_code=None if p is None else p.returncode,wall_s=time.monotonic()-t,
                failure=None if failure is None else str(failure))
            (folder/'execution.json').write_bytes(encoded(execution))
            if failure or p.returncode:raise ValueError('Native run failed; preserved '+str(folder))
            if len(p.stdout)>128*1024**2:raise ValueError('Native output byte budget exceeded; execution retained')
            value=json.loads(p.stdout)
            output.write_bytes(gzip.compress(p.stdout,mtime=0))
            r=dict(schema='osr-journey-execution/1',request_sha256=identity(request),
                build_receipt_id=build_receipt['receipt_id'],output_sha256=digest(output),
                input_gzip_sha256=digest(folder/'input.json.gz'),
                resources=resources,context=context,**execution)
            r['receipt_id']=identity(r);receipt.write_bytes(encoded(r))
        if value.get('schema')!='osr-journey-result/1' or len(value['cases'])!=len(request['cases']):
            raise ValueError('Native batch shape differs')
        for row,case in zip(value['cases'],request['cases']):
            if row['candidate_id']!=case['candidate_id'] or row['id']!=case['id']:
                raise ValueError('Native mixed candidate/case')
            if any(row.get(k) is not False for k in ('physical_accepted','engineering_accepted','operating_release','admitted_operating_map')):
                raise ValueError('Conditional native calculation cannot grant release')
            row['native_receipt_id']=r['receipt_id'];row['native_input_id']=identity(case)
            row['evaluation_id']=identity(row);results.append(row)
    return results
