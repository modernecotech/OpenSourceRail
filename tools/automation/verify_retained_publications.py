"""Explicit historical twin/motor rechecks; current readers remain strict.

Only four pinned publications are supported. Git/source/guard primitives are
shared with railway_closure.retained; its domain-specific verify is never used.
"""
from pathlib import Path
import argparse,hashlib,io,json,os,shutil,stat,subprocess,sys,tarfile,time
from engineering.railway_closure import retained as epoch

ROOT=Path(__file__).resolve().parents[2]
REVISION='946f1772540d07af85b57b0d13cac08a3293b140'
CATALOG={
    'twin':dict(folder='docs/design-engine/digital-twin',manifest='manifest.json',producer='engineering/railway_twin/pipeline.py',schema='osr-end-to-end-twin-publication/1'),
    'cell':dict(folder='docs/design-engine/reference-cell',manifest='manifest.json',producer='engineering/reference_cell/coordinator.py',schema='osr-reference-cell-publication/1'),
    'variants':dict(folder='docs/design-engine/engineering-closure',manifest='variant-design-manifest.json',producer='engineering/railway_completion/variant_design.py',schema='osr-coupled-wayside-variant-publication/1'),
    'motor':dict(folder='docs/design-engine/engineering-closure',manifest='motor-manifest.json',producer='engineering/railway_completion/experiments.py',schema='osr-current-motor-experiment-publication/1'),
}
FLAGS=tuple(dict.fromkeys((*epoch.AUTHORITY_FLAGS,'configuration_adopted','physical_journey_completed','native_evaluator_admission')))
MAX_TEMP=256*1024**2
MAX_FILE=32*1024**2
# Reuse the established isolated-import and process guards, not its closure checker.
_GUARD=epoch.CHILD.split('from engineering.railway_closure import publication\n')[0]
assert _GUARD.endswith('require_project_origins()\n')
CHILD=_GUARD.replace('resource.RLIMIT_FSIZE, (1024**2, 1024**2)',
    'resource.RLIMIT_FSIZE, (32*1024**2, 32*1024**2)')+r'''
if sys.argv[3]=='twin':
    from engineering.railway_twin import pipeline as original
    result=original.verify_publication(root=sys.argv[1],output=sys.argv[2])
elif sys.argv[3]=='cell':
    from engineering.reference_cell import coordinator as original
    result=original.verify_publication(root=sys.argv[1],output=sys.argv[2])
elif sys.argv[3]=='variants':
    from engineering.railway_completion import variant_design as original
    result=original.verify_publication(sys.argv[2],root=sys.argv[1])
elif sys.argv[3]=='motor':
    from engineering.railway_completion import experiments as original
    result=original.verify_publication(sys.argv[2],root=sys.argv[1])
else:
    raise ValueError('Known retained domain required')
require_project_origins()
print(json.dumps(dict(original_checker_result=result,project_module_origins=require_project_origins()),sort_keys=True))
'''


def _read_exact(path,expected):
    """Never allocate according to a mutable live-file size."""
    path=Path(path)
    if any(p.is_symlink() for p in path.parents):raise ValueError('Ordinary retained input required')
    with os.fdopen(os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK),'rb') as f:
        info=os.fstat(f.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size!=len(expected):raise ValueError('Original retained artifact size differs')
        if f.read(len(expected)+1)!=expected:raise ValueError('Original retained artifact bytes differ')


def selection(root,domain,*,sizes=True):
    if domain not in CATALOG:raise ValueError('Known retained domain required')
    root=Path(root);cfg=CATALOG[domain];entries=epoch.tree(root,REVISION,sizes=sizes)
    manifest_name=cfg['folder']+'/'+cfg['manifest']
    if not sizes:
        # Explicit prefetch stage first requests only the small pinned manifest.
        epoch.prefetch_selected(root,REVISION,[manifest_name])
        sized=epoch.tree(root,REVISION)
    else:sized=entries
    raw=dict(epoch.blobs(root,sized,[manifest_name]))[manifest_name]
    _read_exact(root/manifest_name,raw)
    manifest=json.loads(raw)
    if manifest.get('schema')!=cfg['schema']:raise ValueError('Historical publication schema differs')
    files=manifest.get('files_sha256') if domain in ('twin','cell','variants') else {manifest['archive']:manifest['archive_sha256']}
    if not isinstance(files,dict) or not files:raise ValueError('Declared historical payloads required')
    payload={cfg['folder']+'/'+epoch.safe_name(n):sha for n,sha in files.items()}
    sources=manifest['source_sha256']
    names=set(sources)|set(payload)|{manifest_name}
    names.update(n for n in entries if n.endswith('.py') and n.startswith(('engineering/','services/integration/')))
    if cfg['producer'] not in sources:raise ValueError('Original checker must be source bound')
    return cfg,entries,manifest,raw,payload,sources,names


def prefetch(root,domain):
    cfg,entries,manifest,raw,payload,sources,names=selection(root,domain,sizes=False)
    return epoch.prefetch_selected(root,REVISION,names)


def verify(root,domain,state,*,source_revision=REVISION,extended_cell_budget=False,diagnostics=False):
    if source_revision!=REVISION:raise ValueError('Exact pinned historical source revision required')
    if domain!='cell' and (extended_cell_budget or diagnostics):raise ValueError('Extended diagnostic budget is CELL-only')
    root=Path(root).resolve();state=Path(state).absolute()
    if state.exists() or state.is_symlink() or state==root or root in state.resolve().parents:
        raise ValueError('Fresh external retained verification state required')
    if any(p.is_symlink() for p in state.parents):raise ValueError('Ordinary external state required')
    probe=state.parent
    while not probe.exists():probe=probe.parent
    if shutil.disk_usage(probe).free-MAX_TEMP<epoch.MIN_FREE_BYTES:raise ValueError('Historical verification disk reserve unavailable')
    state.mkdir(parents=True,exist_ok=False);work=state/'epoch';scratch=state/'scratch';scratch.mkdir()
    child_code=CHILD
    cpu_seconds=(300 if extended_cell_budget else 150) if domain=='cell' else 120
    wall_seconds=360 if extended_cell_budget else 180
    if domain=='cell':child_code=child_code.replace('resource.RLIMIT_CPU, (120, 120)',f'resource.RLIMIT_CPU, ({cpu_seconds}, {cpu_seconds})')
    if diagnostics:
        child_code=child_code.replace("if sys.argv[3]=='twin':","import faulthandler\nfaulthandler.dump_traceback_later(30, repeat=True)\nif sys.argv[3]=='twin':")
    started=time.monotonic();receipt=dict(schema='osr-retained-twin-motor-check/1',domain=domain,
        source_revision=REVISION,current_source_valid=False,retained_verified=False,
        method_replay_completed=False,native_solver_executions=0,native_processes=0,
        resource_request=dict(cpu_seconds=cpu_seconds,wall_seconds=wall_seconds,address_space_bytes=3*1024**3,
            maximum_selected_input_bytes=epoch.MAX_SOURCE_BYTES,maximum_temporary_bytes=MAX_TEMP,
            per_file_limit_bytes=MAX_FILE,minimum_free_disk_bytes=epoch.MIN_FREE_BYTES),
        isolation='Isolated Python imports and cooperative process guard plus child rlimits; not an OS sandbox or aggregate filesystem quota',
        guard_sha256=hashlib.sha256(child_code.encode()).hexdigest(),diagnostic_stack_interval_seconds=30 if diagnostics else None,**{k:False for k in FLAGS})
    try:
        cfg,entries,manifest,raw,payload,sources,names=selection(root,domain)
        total=epoch.selected_size(entries,names)
        # Validate every selected source and artifact before running any old code.
        blobs=dict(epoch.blobs(root,entries,names));maximum_extraction=0
        for name,sha in sources.items():
            if hashlib.sha256(blobs[name]).hexdigest()!=sha:raise ValueError('Historical sources do not co-occur: '+name)
        for name,sha in payload.items():
            data=blobs[name]
            if hashlib.sha256(data).hexdigest()!=sha:raise ValueError('Pinned payload declaration differs')
            _read_exact(root/name,data)
            if not name.endswith('.tar.gz'):continue
            with tarfile.open(fileobj=io.BytesIO(data),mode='r:*') as archive:
                members=archive.getmembers();seen=set();raw_size=0
                for m in members:
                    epoch.safe_name(m.name)
                    if not m.isfile() or m.name in seen or m.size>MAX_FILE:raise ValueError('Bounded ordinary historical archive required')
                    seen.add(m.name);raw_size+=m.size
                if len(seen)>({'twin':100,'motor':128,'cell':32}[domain]):raise ValueError('Historical archive member budget exceeded')
                maximum_extraction=max(maximum_extraction,raw_size)
        if total+maximum_extraction+2*MAX_FILE>MAX_TEMP:raise ValueError('Historical temporary budget exceeded before staging')
        for name,data in blobs.items():
            dest=work/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        receipt.update(source_epoch_verified=True,source_bindings=len(sources),selected_files=len(names),
            selected_bytes=total,declared_payload_bytes=sum(len(blobs[n]) for n in payload),
            maximum_archive_extraction_bytes=maximum_extraction,manifest_sha256=hashlib.sha256(raw).hexdigest(),
            source_sha256=sources,payload_sha256=payload,
            input_scope='Pinned original manifest and exactly declared payloads; unindexed historical files unclaimed and untouched')
        env={k:v for k,v in os.environ.items() if k not in ('PYTHONPATH','PYTHONHOME')}
        env.update(PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(scratch),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
        with (state/'stdout.json').open('wb') as out,(state/'stderr.txt').open('wb') as err:
            run=subprocess.run([sys.executable,'-I','-B','-c',child_code,str(work),str(work/cfg['folder']),domain],
                cwd=work,env=env,stdout=out,stderr=err,timeout=wall_seconds)
        receipt['original_checker_exit_code']=run.returncode
        if run.returncode:raise ValueError('Original checker failed; original source/input copies and logs retained at '+str(state))
        with os.fdopen(os.open(state/'stdout.json',os.O_RDONLY|os.O_NOFOLLOW),'rb') as stream:
            info=os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size>MAX_FILE:raise ValueError('Bounded checker output required')
            stdout=stream.read(MAX_FILE+1)
        if len(stdout)>MAX_FILE:raise ValueError('Checker output budget exceeded')
        result=json.loads(stdout)
        original=result['original_checker_result']
        if original.get('verified') is not True or any(original.get(k,False) is not False for k in FLAGS):
            raise ValueError('Original checker result cannot grant current acceptance')
        receipt.update(retained_verified=True,method_replay_completed=True,original_checker_result=original,
            project_module_origins=result['project_module_origins'],verification_scope=(
                'Original twin analytical/materialisation/serialized-artifact recheck; no native generation/reopen' if domain=='twin' else
                'Original reference-cell analytical/materialisation and serialized-artifact recheck; no native execution' if domain=='cell' else
                'Original coupled variant stock/brake/motion/civil/delivery analytical replay; no native execution' if domain=='variants' else
                'Original motor recorded-tool/source/payload/trace verification; no field solve or exact numerical replay'))
        observed=sum(p.stat().st_size for p in state.rglob('*') if p.is_file())
        if observed>MAX_TEMP:raise ValueError('Observed historical temporary budget exceeded')
        receipt['observed_temporary_bytes']=observed
        shutil.rmtree(work);shutil.rmtree(scratch)
        receipt['staged_copy_disposition']='Verified redundant staging copies removed; original live payloads and pinned Git sources retained'
    except BaseException as exc:
        receipt['failure']=dict(type=type(exc).__name__,message=str(exc));raise
    finally:
        receipt['wall_seconds']=time.monotonic()-started
        (state/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    return receipt


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('prefetch','verify'))
    p.add_argument('domain',choices=tuple(CATALOG));p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--state',type=Path)
    p.add_argument('--cell-extended-budget',action='store_true',help='Explicit CELL-only300CPU/360wall verification request')
    p.add_argument('--diagnostics',action='store_true',help='CELL-only30-second faulthandler stack snapshots')
    a=p.parse_args()
    if a.action=='verify' and a.state is None:p.error('--state fresh external directory required')
    result=prefetch(a.root,a.domain) if a.action=='prefetch' else verify(a.root,a.domain,a.state,extended_cell_budget=a.cell_extended_budget,diagnostics=a.diagnostics)
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()
