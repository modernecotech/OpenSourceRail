"""Bounded immutable fleet executions; source/tool/resource-exact reuse only."""
from pathlib import Path
from copy import deepcopy
import gzip,json,platform,shutil,subprocess,time
from engineering.station_pair import native_bridge as journey
from engineering.station_pair import native_products
from engineering.station_rail.common import encoded,identity,digest
from . import ROOT


def execute(cases,state,*,root=ROOT):
    if not cases:return []
    state=Path(state).resolve();state.mkdir(parents=True,exist_ok=True)
    binary,base=native_products.build(state,'osr-station-fleet',root=root)
    build=dict(base,protocol='osr-station-fleet-request/1',binary_sha256=digest(binary))
    build.pop('receipt_id');build['receipt_id']=identity(build)
    (state/'fleet-build.json').write_bytes(encoded(build))
    limiter=shutil.which('prlimit')
    if limiter is None:raise ValueError('Resource limiter required')
    resources=dict(cpu_s=60,address_space_bytes=1073741824,wall_s=75,
                   maximum_input_bytes=8*1024**2,maximum_output_bytes=128*1024**2,batch_cases=2)
    context=dict(resources=resources,bridge_sha256=digest(__file__),platform=platform.platform(),
                 limiter_version=subprocess.check_output([limiter,'--version'],text=True).strip())
    result=[]
    if len(cases)>64:raise ValueError('Explicit 64-case fleet invocation budget exceeded')
    for start in range(0,len(cases),resources['batch_cases']):
        request=dict(schema='osr-station-fleet-request/1',cases=cases[start:start+resources['batch_cases']])
        raw=encoded(request)
        if len(raw)>resources['maximum_input_bytes']:raise ValueError('Fleet input byte budget exceeded')
        key=identity(dict(request=request,build=build['receipt_id'],context=context))
        folder=state/'fleet-runs'/key;folder.mkdir(parents=True,exist_ok=True)
        receipt=folder/'receipt.json';output=folder/'output.json.gz';input_path=folder/'input.json.gz'
        if receipt.exists():
            r=json.loads(receipt.read_bytes())
            if (r['receipt_id']!=identity({k:v for k,v in r.items() if k!='receipt_id'})
                or r['build_receipt_id']!=build['receipt_id'] or r['context']!=context
                or r['input_sha256']!=digest(input_path) or r['output_sha256']!=digest(output)
                or gzip.decompress(input_path.read_bytes())!=raw):
                raise ValueError('Fleet cached evidence changed')
            value=json.loads(gzip.decompress(output.read_bytes()))
        else:
            if input_path.exists() or output.exists():
                raise ValueError('Interrupted fleet package retained; use a fresh run directory')
            input_path.write_bytes(gzip.compress(raw,mtime=0));t=time.monotonic();failure=None;p=None
            with (folder/'stderr.log').open('wb') as err:
                try:
                    p=subprocess.run([limiter,'--cpu=60','--as=1073741824','--',str(binary)],
                        input=raw,stdout=subprocess.PIPE,stderr=err,cwd=folder,timeout=75)
                except (OSError,subprocess.TimeoutExpired) as exc:failure=str(exc)
            execution=dict(exit_code=None if p is None else p.returncode,wall_s=time.monotonic()-t,failure=failure)
            (folder/'execution.json').write_bytes(encoded(execution))
            if p is not None:(folder/'stdout.json.gz').write_bytes(gzip.compress(p.stdout,mtime=0))
            if failure or p.returncode:raise ValueError('Fleet failure retained at '+str(folder))
            if len(p.stdout)>resources['maximum_output_bytes']:raise ValueError('Fleet output budget exceeded')
            value=json.loads(p.stdout);output.write_bytes(gzip.compress(p.stdout,mtime=0))
            r=dict(schema='osr-fleet-native-receipt/1',build_receipt_id=build['receipt_id'],context=context,
                   input_sha256=digest(input_path),output_sha256=digest(output),**execution)
            r['receipt_id']=identity(r);receipt.write_bytes(encoded(r))
        if journey.sources(root)!=base['source_sha256'] or digest(binary)!=build['binary_sha256']:
            raise ValueError('Native source/binary changed during fleet execution; evidence retained')
        if value.get('schema')!='osr-station-fleet-result/1' or len(value['cases'])!=len(request['cases']):
            raise ValueError('Fleet result shape differs')
        for row,q in zip(value['cases'],request['cases']):
            if row['candidate_id']!=q['candidate_id'] or row['id']!=q['id']:
                raise ValueError('Mixed fleet case or candidate identity')
            if any(row.get(k) is not False for k in ('physical_accepted','engineering_accepted','operating_release','admitted_operating_map')):
                raise ValueError('Fleet research cannot grant physical approval')
            row=deepcopy(row);row['native_receipt_id']=r['receipt_id'];row['native_input_id']=identity(q)
            row['evaluation_id']=identity(row);result.append(row)
    return result
