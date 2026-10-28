#!/usr/bin/env python3
"""Parallel execution/replay of the unchanged sourced-case coordinator.

Private workers never write canonical state. Source/receipt checks and cooperative
locks are enforced here; filesystem/network read-only access is not OS enforced.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from contextlib import contextmanager
import argparse,fcntl,gzip,hashlib,importlib,io,json,os,resource,shutil,subprocess,sys,tarfile,tempfile,traceback
ROOT=Path(__file__).resolve().parents[2]
MEMORY=2*1024**3
RSS_TARGET=700*1024**2
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False,selected_reference_changed=False)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()


def ident(value):return hashlib.sha256(encoded(value)).hexdigest()


def load(path):
    p=Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size>256*1024**2:raise ValueError('Ordinary bounded orchestration payload required')
    if p.suffix=='.gz':
        with gzip.open(p,'rb') as f:raw=f.read(256*1024**2+1)
    else:raw=p.read_bytes()
    if len(raw)>256*1024**2:raise ValueError('Orchestration decompression budget exceeded')
    return json.loads(raw)


def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);raw=encoded(value)
    if path.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
    path.write_bytes(raw)


def modules(root):
    root=Path(root).resolve();sys.path.insert(0,str(root))
    c=importlib.import_module('engineering.sourced_case.coordinator')
    if Path(c.__file__).resolve()!=root/'engineering/sourced_case/coordinator.py':raise ValueError('Imported coordinator differs from explicit source root')
    return c


def unreleased(value):
    if isinstance(value,dict):
        for k,v in value.items():
            if k in FLAGS and v is not False:raise ValueError('Research record cannot grant acceptance or release')
            unreleased(v)
    elif isinstance(value,list):
        for v in value:unreleased(v)


def sealed(c,value,key='evaluation_id'):
    if value.get(key)!=c.identity({k:v for k,v in value.items() if k!=key}):raise ValueError('Modified recorded evaluation')
    unreleased(value)


def vehicle(c,e):
    sealed(c,e);v=e['vehicle'];sealed(c,v)
    from engineering.component_registry import validate_registry
    validate_registry(v['registry'])
    if e['candidate_id']!=v['candidate_id'] or v['candidate_id']!=v['registry']['candidate_id']:raise ValueError('Mixed canonical vehicle')
    return v


def case(c,r,req,e,epoch):
    sealed(c,r);v=vehicle(c,e)
    if r['source_sha256']!=epoch or any(r.get(k)!=val for k,val in req.items()):raise ValueError('Case source epoch or exact request differs')
    if r['body_candidate_id']!=v['candidate_id']:raise ValueError('Case uses another vehicle')
    b=r['bundle'];sealed(c,b,'definition_id');sealed(c,r['drive'])
    cid=r['candidate_id']
    if b['candidate_id']!=cid or b['body_candidate_id']!=v['candidate_id'] or r['drive']['body_candidate_id']!=v['candidate_id']:raise ValueError('Mixed component identities')
    if b['propulsion_component_id']!=r['drive']['candidate_id'] or b['brake_definition']['candidate_id']!=cid:raise ValueError('Mixed drive/brake context')
    if c.identity(b['architecture_case']['physical_definition']['composition'])!=cid:raise ValueError('Physical composition differs')
    if any(r[name]['candidate_id']!=cid for name in ('civil','manufacturing','partial_public_price')):raise ValueError('Mixed downstream cell')
    if r['qualified_journeys']!=0 or r['operating_map_admitted'] is not False:raise ValueError('Unsupported operating acceptance')
    for row in r['journeys']:
        q=row['result'];sealed(c,q)
        if q['candidate_id']!=cid or q['bundle_definition_id']!=b['definition_id'] or q['alternative_candidate_id']!=r['drive']['candidate_id']:raise ValueError('Mixed trajectory inputs')
    return r


@contextmanager
def lock(state):
    state=Path(state)
    if state.is_symlink() or state.exists() and any(p.is_symlink() for p in state.rglob('*')):raise ValueError('Ordinary unlinked canonical state required')
    state.mkdir(parents=True,exist_ok=True)
    with (state/'.coordinator.lock').open('a') as f:
        try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as err:raise ValueError('Canonical coordinator already running') from err
        yield


def outside(path,state):
    p=Path(path).resolve();s=Path(state).resolve()
    if p==s or s in p.parents:raise ValueError('Audit/publication must remain outside closed canonical state')
    return p


def fresh(audit,operation):
    audit=Path(audit);audit.mkdir(parents=True,exist_ok=True)
    for index in range(10000):
        p=audit/(operation+'-'+str(index).zfill(4))
        try:p.mkdir();return p
        except FileExistsError:continue
    raise ValueError('Audit attempt budget exceeded')


def install(source,target):
    source=Path(source);target=Path(target);target.parent.mkdir(parents=True,exist_ok=True)
    if target.is_symlink():raise ValueError('Canonical destination is linked')
    if target.exists():
        if target.read_bytes()!=source.read_bytes():raise ValueError('Canonical artifact conflict; preserve both versions')
        return
    temporary=target.with_name(target.name+'.pending');shutil.copyfile(source,temporary);temporary.replace(target)


def job_input(folder,c,root,epoch,requests,operation,state,archive,timeout_s):
    folder.mkdir();vid=requests[0]['vehicle_id'];cached=Path(state)/'vehicles'/(vid+'.json.gz')
    files={};missing=[]
    if cached.exists():
        vehicle(c,load(cached));shutil.copyfile(cached,folder/'cached-vehicle.json.gz');files['cached-vehicle.json.gz']=sha(folder/'cached-vehicle.json.gz')
    for req in requests:
        key=c.identity(dict(request=req,source=epoch));p=Path(state)/'cases'/(key+'.json.gz')
        if p.exists():
            if not cached.exists():raise ValueError('Completed case has no canonical vehicle')
            case(c,load(p),req,load(cached),epoch)
            if operation=='replay':
                name='expected-'+key+'.json.gz';shutil.copyfile(p,folder/name);files[name]=sha(folder/name)
        else:missing.append(key)
    if operation=='replay' and missing:raise ValueError('Incomplete campaign cannot publish')
    r=dict(schema='osr-sourced-worker-request/1',operation=operation,root=str(Path(root).resolve()),requests=requests,missing_request_keys=missing,
        source_sha256=epoch,executor_sha256=sha(__file__),input_files_sha256=files,source_archive_sha256=sha(archive),source_archive=str(archive),
        memory_bytes=MEMORY,maximum_seconds=timeout_s,**FLAGS)
    r['request_id']=ident(r);write(folder/'input.json',r);return r


def worker(folder):
    folder=Path(folder);r=load(folder/'input.json');completed=[];outputs={};failure=None;c=None
    try:
        if r['request_id']!=ident({k:v for k,v in r.items() if k!='request_id'}) or r['executor_sha256']!=sha(__file__):raise ValueError('Worker request/helper identity differs')
        c=modules(r['root']);epoch=r['source_sha256']
        expected=[x for x in c.plan() if x['vehicle_id']==r['requests'][0]['vehicle_id']]
        if r['requests']!=expected or c.sources(r['root'])!=epoch or sha(r['source_archive'])!=r['source_archive_sha256']:raise ValueError('Worker physical plan/source snapshot differs')
        for name,digest in r['input_files_sha256'].items():
            if Path(name).name!=name or sha(folder/name)!=digest:raise ValueError('Worker owned input differs')
        cached=folder/'cached-vehicle.json.gz'
        e=load(cached) if cached.exists() else c.revised(expected[0]['vehicle_id'],Path(r['root']))
        vehicle(c,e);c.write(folder/'vehicle.json.gz',e);outputs['vehicle.json.gz']=sha(folder/'vehicle.json.gz')
        for req in expected:
            key=c.identity(dict(request=req,source=epoch))
            if r['operation']=='gen' and key not in r['missing_request_keys']:continue
            value=c.evaluate(e,root=Path(r['root']),**{k:v for k,v in req.items() if k!='vehicle_id'})
            case(c,value,req,e,epoch)
            if c.sources(r['root'])!=epoch:raise ValueError('Physics source changed during execution')
            if r['operation']=='replay':
                old=load(folder/('expected-'+key+'.json.gz'))
                if c.encoded(value)!=c.encoded(old):raise ValueError('Actual semantic replay differs: '+key)
            name='case-'+key+'.json.gz';c.write(folder/name,value);outputs[name]=sha(folder/name)
            completed.append(dict(request=req,request_key=key,evaluation_id=value['evaluation_id'],candidate_id=value['candidate_id'],file=name))
    except BaseException as error:
        failure=dict(type=type(error).__name__,reason=str(error),classification='definition-or-contract' if isinstance(error,ValueError) else 'execution-or-resource')
        traceback.print_exc()
    result=dict(schema='osr-sourced-worker-execution/1',request_id=r.get('request_id'),operation=r.get('operation'),source_sha256=r.get('source_sha256'),
        executor_sha256=sha(__file__),actual_address_space_limit_bytes=list(resource.getrlimit(resource.RLIMIT_AS)),
        peak_resident_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024),
        resident_target_bytes=RSS_TARGET,resident_target_is_hard_limit=False,python_executable=sys.executable,python_version=sys.version,completed=completed,output_files_sha256=outputs,
        execution='failed' if failure else 'completed',failure=failure,
        isolation='Ordinary subprocess with address-space/wall-clock limits; filesystem/network access is not sandboxed',**FLAGS)
    result['execution_id']=ident(result);write(folder/'worker-result.json',result)
    return 2 if failure else 0


def launch(folder,request,root):
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','NUMEXPR_NUM_THREADS':'1'}
    try:
        p=subprocess.run([sys.executable,str(Path(__file__).resolve()),'_worker',str(folder)],cwd=root,env=env,capture_output=True,
            timeout=request['maximum_seconds'])
        (folder/'stdout.log').write_bytes(p.stdout);(folder/'stderr.log').write_bytes(p.stderr)
        return dict(returncode=p.returncode,interrupted=False)
    except subprocess.TimeoutExpired as error:
        (folder/'stdout.log').write_bytes(error.stdout or b'');(folder/'stderr.log').write_bytes(error.stderr or b'')
        return dict(returncode=None,interrupted=True,reason='Explicit worker wall-clock budget exceeded; partial outputs retained')


def validate_outputs(c,folder,request,epoch):
    if request['executor_sha256']!=sha(__file__) or request['source_sha256']!=epoch:raise ValueError('Executor or requested source changed')
    for name,digest in request['input_files_sha256'].items():
        if Path(name).name!=name or sha(folder/name)!=digest:raise ValueError('Worker modified an owned input')
    outputs=[];report=None;path=folder/'worker-result.json'
    if path.exists():
        report=load(path)
        if report['execution_id']!=ident({k:v for k,v in report.items() if k!='execution_id'}) or report['request_id']!=request['request_id'] or report['source_sha256']!=epoch or report['executor_sha256']!=sha(__file__):raise ValueError('Worker receipt source/request differs')
        unreleased(report)
        for name,digest in report['output_files_sha256'].items():
            if Path(name).name!=name or sha(folder/name)!=digest:raise ValueError('Worker output bytes differ')
    vpath=folder/'vehicle.json.gz'
    if not vpath.exists():return [],report
    e=load(vpath);vehicle(c,e)
    # Fully sealed cases survive a later definition failure or interrupted worker.
    for req in request['requests']:
        key=c.identity(dict(request=req,source=epoch));path=folder/('case-'+key+'.json.gz')
        if not path.exists():continue
        try:value=case(c,load(path),req,e,epoch)
        except (ValueError,OSError,EOFError,json.JSONDecodeError):
            if report is not None and path.name in report['output_files_sha256']:raise
            continue
        outputs.append((req,path,value))
    return outputs,report


def canonical_inventory(state):
    """Pin every canonical byte, including vehicle registries and frontier."""
    state=Path(state)
    if state.is_symlink() or any(p.is_symlink() for p in state.rglob('*')):raise ValueError('Ordinary canonical snapshot required')
    return {p.relative_to(state).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p))
        for p in sorted(state.rglob('*')) if p.is_file() and p.relative_to(state).as_posix()!='.coordinator.lock'}


def bind_verified_snapshot(c,state,replay,root):
    """Reuse the actual first verification only while its whole input is exact."""
    check=replay['initial_verification'];snapshot=replay['canonical_input_inventory']
    unreleased(check)
    if check.get('verified') is not True or check.get('pending')!=0 or check.get('semantic_replay_executed') is not False:raise ValueError('Actual complete first verification required')
    if replay['canonical_input_inventory_id']!=ident(snapshot) or canonical_inventory(state)!=snapshot or c.sources(root)!=replay['source_sha256']:
        raise ValueError('Canonical inventory or source changed after first verification')
    return dict(check)


def execute(operation,state,*,audit,workers=3,root=ROOT,timeout_s=1800.):
    if operation not in ('gen','replay') or type(workers) is not int or not 1<=workers<=3 or not 0<timeout_s<=7200:raise ValueError('Explicit bounded operation,1–3workers andtimeout required')
    c=modules(root);state=Path(state);audit=outside(audit,state);attempt=fresh(audit,operation);jobs=[];receipts=[];failures=[];integrated=0;verified=None;pinned=None
    with lock(state):
        epoch=c.sources(root);archive=attempt/'input-sources.tar.gz'
        from engineering.railway_twin import pipeline
        raw=pipeline._input_archive(root,epoch);archive.write_bytes(raw);shutil.copyfile(__file__,attempt/'executor-source.py')
        canonical=state/'input-sources.tar.gz'
        if canonical.exists() and canonical.read_bytes()!=raw:raise ValueError('Existing campaign uses another source epoch')
        if operation=='gen' and not canonical.exists():canonical.write_bytes(raw)
        if operation=='replay':
            verified=c.verify(state,root,replay=False)
            if verified['pending']:raise ValueError('Incomplete campaign cannot publish')
            pinned=canonical_inventory(state)
        groups={}
        for req in c.plan():groups.setdefault(req['vehicle_id'],[]).append(req)
        for vid,reqs in groups.items():
            folder=attempt/vid;r=job_input(folder,c,root,epoch,reqs,operation,state,archive,timeout_s)
            if operation=='gen' and not r['missing_request_keys'] and (folder/'cached-vehicle.json.gz').exists():continue
            jobs.append((folder,r))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures={pool.submit(launch,p,r,root):(p,r) for p,r in jobs}
            for future in as_completed(futures):
                folder,r=futures[future]
                try:
                    execution=future.result();done,report=validate_outputs(c,folder,r,epoch)
                except Exception as error:
                    failures.append(dict(body=folder.name,classification='worker-contract-or-execution',reason=type(error).__name__+': '+str(error)))
                    receipts.append(dict(folder=folder.name,request_id=r['request_id'],execution='contract-or-execution-failure',audit_files_sha256={p.name:sha(p) for p in folder.iterdir() if p.is_file()}))
                    if c.sources(root)!=epoch:raise ValueError('Source epoch changed; private outputs retained') from error
                    continue
                if c.sources(root)!=epoch:raise ValueError('Source epoch changed; private outputs retained without integration')
                receipts.append(dict(folder=folder.name,request_id=r['request_id'],execution=execution,worker_receipt_id=None if report is None else report['execution_id'],validated_cases=len(done),audit_files_sha256={p.name:sha(p) for p in folder.iterdir() if p.is_file()}))
                expected=len(r['requests']) if operation=='replay' else len(r['missing_request_keys'])
                if execution.get('returncode')!=0 or report is None or report['execution']!='completed' or len(done)!=expected:failures.append(dict(body=folder.name,execution=execution,failure=None if report is None else report['failure']))
                if operation=='gen' and done:
                    install(folder/'vehicle.json.gz',state/'vehicles'/(r['requests'][0]['vehicle_id']+'.json.gz'))
                    for req,path,value in done:
                        key=c.identity(dict(request=req,source=epoch));install(path,state/'cases'/(key+'.json.gz'));integrated+=1
        if c.sources(root)!=epoch:raise ValueError('Source changed before canonical frontier sealing')
    frontier=c.run(state,root,max_cases=0) if operation=='gen' else None
    r=dict(schema='osr-sourced-parallel-orchestration/1',operation=operation,source_sha256=epoch,executor_sha256=sha(__file__),
        initial_verification=verified,canonical_input_inventory=pinned,canonical_input_inventory_id=None if pinned is None else ident(pinned),
        source_archive_sha256=sha(archive),executor_snapshot_sha256=sha(attempt/'executor-source.py'),worker_limit=workers,address_space_limit_per_worker_bytes=MEMORY,maximum_seconds_per_worker=timeout_s,workers=receipts,failures=failures,
        integrated_cases=integrated,completed_cases=None if frontier is None else len(frontier['cases']),pending_cases=None if frontier is None else len(frontier['pending']),
        semantic_replay_executed=operation=='replay' and not failures,
        independent_engineering_or_physical_validation=False,**FLAGS)
    r['orchestration_id']=ident(r);write(attempt/'orchestration.json',r)
    return r,attempt


def bind_replayed_canonical(c,state,folder,request,epoch):
    """Bind unchanged original compressed bytes, not a host's regenerated gzip.

    Workers already compare canonical JSON encodings of recomputed physics.
    Different valid gzip implementations may serialize those equal JSON bytes
    differently. The retained expected input pins the pre-replay canonical file.
    """
    for req in request['requests']:
        key=c.identity(dict(request=req,source=epoch));name='expected-'+key+'.json.gz'
        expected=request['input_files_sha256'].get(name)
        canonical=Path(state)/'cases'/(key+'.json.gz')
        if expected is None or sha(Path(folder)/name)!=expected or sha(canonical)!=expected:
            raise ValueError('Canonical case or retained expected input changed after actual replay')


def publish(state,*,output,audit,workers=3,root=ROOT,timeout_s=1800.):
    c=modules(root);output=outside(output,state)
    replay,attempt=execute('replay',state,audit=audit,workers=workers,root=root,timeout_s=timeout_s)
    if replay['failures'] or not replay['semantic_replay_executed']:raise ValueError('Publication held: actual worker replay failed; audit retained at '+str(attempt))
    with lock(state):
        check=bind_verified_snapshot(c,state,replay,root)
        # Bind unchanged canonical bytes across the second lock acquisition.
        epoch=replay['source_sha256']
        for folder in attempt.iterdir():
            if folder.is_dir():
                request=load(folder/'input.json')
                bind_replayed_canonical(c,state,folder,request,epoch)
        check['semantic_replay_executed']=True
        output.mkdir(parents=True,exist_ok=True);stream=io.BytesIO()
        with tarfile.open(fileobj=stream,mode='w') as archive:
            for path in sorted(Path(state).rglob('*')):
                if path.is_file() and path.name!='.coordinator.lock':
                    raw=path.read_bytes();info=tarfile.TarInfo(path.relative_to(state).as_posix());info.size=len(raw);info.mode=0o644;info.mtime=0;archive.addfile(info,io.BytesIO(raw))
        (output/'sourced-cell.tar.gz').write_bytes(gzip.compress(stream.getvalue(),mtime=0))
        index=c.read(Path(state)/'latest.json');summary=dict(schema='osr-sourced-cell-summary/1',run_id=index['run_id'],cases=index['cases'],pending=index['pending'],**FLAGS);c.write(output/'summary.json',summary)
        manifest=dict(schema='osr-sourced-cell-publication/1',source_sha256=c.sources(root),validation=check,
            files_sha256={n:sha(output/n) for n in ('sourced-cell.tar.gz','summary.json')},**FLAGS)
        manifest['publication_id']=c.identity(manifest);c.write(output/'manifest.json',manifest)
    write(attempt/'published.json',dict(publication_id=manifest['publication_id'],orchestration_id=replay['orchestration_id'],**FLAGS));return manifest


def main(argv=None):
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='operation',required=True)
    for name in ('gen','publish'):
        q=sub.add_parser(name);q.add_argument('state',type=Path);q.add_argument('--audit',required=True,type=Path);q.add_argument('--workers',type=int,default=3);q.add_argument('--timeout-s',type=float,default=1800.);q.add_argument('--root',type=Path,default=ROOT)
        if name=='publish':q.add_argument('--output',required=True,type=Path)
    q=sub.add_parser('_worker');q.add_argument('folder',type=Path);a=p.parse_args(argv)
    if a.operation=='_worker':
        resource.setrlimit(resource.RLIMIT_AS,(MEMORY,MEMORY))
        return worker(a.folder)
    if a.operation=='gen':
        result,where=execute('gen',a.state,audit=a.audit,workers=a.workers,root=a.root,timeout_s=a.timeout_s);print(json.dumps(dict(result,audit=str(where)),sort_keys=True));return 2 if result['failures'] or result['pending_cases'] else 0
    result=publish(a.state,output=a.output,audit=a.audit,workers=a.workers,root=a.root,timeout_s=a.timeout_s);print(json.dumps(result,sort_keys=True));return 0


if __name__=='__main__':raise SystemExit(main())
