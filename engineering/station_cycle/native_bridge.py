"""Content-addressed bounded native runs, separate from report/cost revisions."""
from pathlib import Path
from copy import deepcopy
import fcntl,gzip,json,os,shutil,subprocess,time,platform
from engineering.station_rail.common import digest,encoded,identity
from . import ROOT
from engineering.station_pair import native_bridge as journey_bridge

NATIVE='engineering/station_pair/native'


def sources(root=ROOT):
    root=Path(root)
    base=root/NATIVE
    paths=[base/'Cargo.toml',base/'Cargo.lock']
    for name in ('src','tests'):paths.extend(sorted((base/name).rglob('*.rs')))
    return {p.relative_to(root).as_posix():digest(p) for p in paths}


def build(state,root=ROOT):
    binary,base=journey_bridge.build(state,root)
    cycle=binary.parent/'osr-station-cycle'
    if not cycle.is_file():raise ValueError('Cycle binary missing from native package build')
    own=Path(state)/'cycle-build.json'
    if own.exists():
        previous=json.loads(own.read_bytes())
        if (previous.get('source_sha256')==base['source_sha256'] and previous.get('tools')==base['tools']
            and (previous.get('receipt_id')!=identity({k:v for k,v in previous.items() if k!='receipt_id'})
                 or previous.get('binary_sha256')!=digest(cycle))):
            raise ValueError('Cycle binary or build receipt changed')
    r=dict(base,journey_binary_sha256=base['binary_sha256'],binary_sha256=digest(cycle),protocol='osr-station-cycle-request/1')
    r.pop('receipt_id',None);r['receipt_id']=identity(r)
    (Path(state)/'cycle-build.json').write_bytes(encoded(r))
    return cycle,r


def execute(cases,state,*,root=ROOT,kernel=None):
    if not cases:return []
    # Different experiment labels may intentionally share exactly the same
    # request (e.g. an unobserved fault under a controller with no such input).
    # Evaluate it once, retaining one immutable evidence record for each alias.
    unique={};ids={};order=[]
    for c in cases:
        key=identity(c)
        if c['id'] in ids and ids[c['id']]!=key:raise ValueError('Conflicting requests share one case ID')
        ids[c['id']]=key;unique.setdefault(key,c);order.append(key)
    if len(unique)<len(cases):
        values=execute(list(unique.values()),state,root=root,kernel=kernel)
        bykey=dict(zip(unique,values))
        return [deepcopy(bykey[key]) for key in order]
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
    for start in range(0,len(cases),16):
        request=dict(schema='osr-station-cycle-request/1',cases=cases[start:start+16]);raw=encoded(request)
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
        if value.get('schema')!='osr-station-cycle-result/1' or len(value['cases'])!=len(request['cases']):
            raise ValueError('Native batch shape differs')
        for row,case in zip(value['cases'],request['cases']):
            if row['candidate_id']!=case['candidate_id'] or row['id']!=case['id']:
                raise ValueError('Native mixed candidate/case')
            if any(row.get(k) is not False for k in ('physical_accepted','engineering_accepted','operating_release','admitted_operating_map')):
                raise ValueError('Conditional native calculation cannot grant release')
            row['native_receipt_id']=r['receipt_id'];row['native_input_id']=identity(case)
            row['evaluation_id']=identity(row);results.append(row)
    return results
