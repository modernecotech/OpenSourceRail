"""Verify the retired station-LIM reference without admitting it as an active design.

The exact published 3bf38a5 Git tree is the archive. Sources and old packets are
read from pinned Git blobs. A packet that has since advanced is checked by its
own current publisher, while the original bytes remain retrievable by commit.
No lazy fetch, solver replay, current-evaluator admission or physical approval.
Shared-filesystem integrity checks are not an OS security sandbox.
"""
from collections import OrderedDict
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
from threading import RLock
import tomllib

ROOT=Path(__file__).resolve().parents[2]
PRODUCER='engineering/station_rail/retired_station_reference.py'
OUTPUT='docs/archives/retired-station-reference'
COMMIT='3bf38a501d09fa3a3c2dd6f4731be11828d04f55'
COUPLED_SOURCE_EPOCH='docs/archives/coupled-railway-source-epochs/905af0b5762a1acf987a831d588f5b8b26f0b400f3bf33be2dac2f940ce38510'
COUPLED_PACKET_MANIFEST_ID='4363503c0647f6e0aff2253b4c714e4f00d47827722d8fe3e0f6c1fe18c6f91f'
COUPLED_SOURCE_EPOCH_ID='938edc9b1f3f579bb783cf9b8bf520a3f79253f7d67b28c5c302ac1208e16000'
COUPLED_SOURCE_COMMIT='dbb62c6aeb48377cb57a00521075bba333f741d2'
COUPLED_SOURCE_BLOB='74e12d096a4103877c1ba6a89ef33ea0e841da54'
_LOADED_SHA=sha256(Path(__file__).read_bytes()).hexdigest()
EXPECTED_RECEIPT_ID='2c24b33b347acb9bae40301aad5387b908209ff4d75958cc0e04f9a03498de72'
# source-map key, payload-map key, manifest identity key, optional disposition.
PACKETS={
 'v06-design-space':('source_sha256','files_sha256','manifest_id',None),
 'v06-architecture':('source_sha256','files_sha256','manifest_id',None),
 'civil-shape-mechanics':('source_sha256','files_sha256','manifest_id',None),
 'civil-topology':('source_sha256','files_sha256','manifest_id',('result.json','portfolio_id')),
 'civil-topology-revisions':('source_sha256','files_sha256','manifest_id',('result.json','portfolio_id')),
 'flanged-span-study':('source_sha256','files_sha256','manifest_id',('result.json','publication_id')),
 'flanged-system-cost-study':('source_sha256','files_sha256','manifest_id',('result.json','publication_id')),
 'matched-renewal-research':('source_sha256','files_sha256','manifest_id',('result.json','publication_id')),
 'installed-mass-support':('source_sha256','files_sha256','manifest_id',('result.json','evaluation_id')),
 'v06-adaptive-design':('source_sha256','files_sha256','manifest_id',None),
 'generative-structure':('source_sha256','files_sha256','manifest_id',None),
 'coupled-railway':('source_sha256','files_sha256','manifest_id',None),
 'railway-closure':('sources','files','publication_id',None),
 'practical-launch':('source_sha256','files_sha256','manifest_id',None),
 'propulsion-layout':('source_sha256','files_sha256','manifest_id',None),
 'station-accelerators':('sources_sha256','files_sha256','manifest_id',None),
 'breadth-first-shape-portfolio':('source_sha256','files_sha256','manifest_id',('result.json','portfolio_id')),
}
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
    operating_release=False,current_evaluator_admission=False,numerical_reexecuted=False,
    physical_equivalence_proven=False,configuration_adopted=False,selected_reference_changed=False)
MAX_FILES=20000
MAX_TREE_BYTES=8*1024**2
MAX_FILE_BYTES=512*1024**2
MAX_TOTAL_BYTES=4*1024**3
_cache=OrderedDict()
_COUPLED_VERIFY_LOCK=RLock()


class RetiredReferenceHold(ValueError):pass


def encoded(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def identity(v):return sha256(encoded(v)).hexdigest()
def _stamp(p):
    s=p.lstat();return (s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns)


def _hash(p):
    before=_stamp(p);h=sha256();fd=os.open(p,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
    with os.fdopen(fd,'rb') as f:
        for b in iter(lambda:f.read(1024**2),b''):h.update(b)
    if _stamp(p)!=before:raise RetiredReferenceHold('Retired evidence changed during hashing')
    return h.hexdigest()


def _path(root,name):
    p=Path(name)
    if not name or p.is_absolute() or '..' in p.parts or '\\' in name:
        raise RetiredReferenceHold('Ordinary repository-relative retired evidence required')
    out=Path(root)/p
    if any(x.is_symlink() for x in (out,*out.parents)):
        raise RetiredReferenceHold('Linked retired evidence is not allowed')
    return out


def _env():
    e=dict(os.environ)
    for k in tuple(e):
        if k.startswith('GIT_CONFIG_') or k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE',
            'GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES','GIT_REPLACE_REF_BASE','GIT_SHALLOW_FILE'):
            e.pop(k,None)
    e.update(GIT_NO_REPLACE_OBJECTS='1',GIT_NO_LAZY_FETCH='1',GIT_TERMINAL_PROMPT='0',
        GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,GIT_OPTIONAL_LOCKS='0')
    return e


def _command():
    return ['git','--no-replace-objects','-c','core.packedGitWindowSize=16m',
        '-c','core.packedGitLimit=64m','-c','core.deltaBaseCacheLimit=32m']


def _git(root,args):
    try:
        r=subprocess.run([*_command(),*args],cwd=root,env=_env(),
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60,check=True)
        return r.stdout
    except (subprocess.SubprocessError,OSError) as exc:
        raise RetiredReferenceHold('Retired reference history is unavailable; fetch exact commit '+COMMIT+' before verification') from exc


def _tree(root):
    actual=_git(root,['rev-parse','--verify',COMMIT+'^{commit}']).decode().strip()
    if actual!=COMMIT:raise RetiredReferenceHold('Exact retired reference commit differs')
    raw=_git(root,['ls-tree','-r','-z','-l',COMMIT])
    if len(raw)>MAX_TREE_BYTES:raise RetiredReferenceHold('Retired Git tree exceeds its budget')
    rows={}
    for row in raw.split(b'\0'):
        if not row:continue
        meta,name=row.split(b'\t',1);mode,kind,oid,size=meta.split();name=name.decode()
        if kind==b'blob' and mode in (b'100644',b'100755'):
            try:count=int(size)
            except ValueError as exc:raise RetiredReferenceHold('Retired Git blob missing or damaged: '+name) from exc
            rows[name]=dict(git_blob=oid.decode(),size_bytes=count)
    return rows


def _blob(root,tree,name):
    if name not in tree:raise RetiredReferenceHold('Retired source is absent from pinned Git tree: '+name)
    if tree[name]['size_bytes']>MAX_FILE_BYTES:raise RetiredReferenceHold('Retired source exceeds its file budget')
    raw=_git(root,['cat-file','blob',tree[name]['git_blob']])
    if len(raw)!=tree[name]['size_bytes']:raise RetiredReferenceHold('Retired Git blob size differs')
    return raw


def _sealed(v,key):
    if v.get(key)!=identity({k:x for k,x in v.items() if k!=key}):
        raise RetiredReferenceHold('Retired '+key+' differs')


def _held(v):
    for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release'):
        if v.get(k) is not False:raise RetiredReferenceHold('Retired evidence cannot grant '+k)
    for k in ('configuration_adopted','selected_reference_changed'):
        if k in v and v[k] is not False:raise RetiredReferenceHold('Retired comparison cannot select a new design')


def _snapshot(root):
    tree=_tree(root);bindings={};packets={};actual_files={}
    def bind(name,wanted):
        _path(root,name)
        if name in bindings and bindings[name]!=wanted:raise RetiredReferenceHold('Conflicting retired source bindings')
        if not isinstance(wanted,str) or len(wanted)!=64:raise RetiredReferenceHold('Exact retired SHA-256 required')
        if name not in tree:raise RetiredReferenceHold('Pinned retired blob missing: '+name)
        bindings[name]=wanted
    for name,(sk,fk,ik,disp) in PACKETS.items():
        prefix='docs/design-engine/'+name+'/';mp=prefix+'manifest.json';raw=_blob(root,tree,mp);m=json.loads(raw);_sealed(m,ik)
        d=m if disp is None else json.loads(_blob(root,tree,prefix+disp[0]))
        if disp is not None:_sealed(d,disp[1])
        _held(d)
        for flag in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release'):
            if flag in m and m[flag] is not False:raise RetiredReferenceHold('Retired manifest grants release')
        payload={prefix+n:h for n,h in m[fk].items()};payload[mp]=sha256(raw).hexdigest()
        inventory={p for p in tree if p.startswith(prefix)}
        if not set(payload)<=inventory:raise RetiredReferenceHold('Retired declared packet file is missing: '+name)
        extra_files={p:sha256(_blob(root,tree,p)).hexdigest() for p in sorted(inventory-set(payload))}
        payload.update(extra_files)
        for p,h in {**m[sk],**payload}.items():bind(p,h)
        actual_files.update(payload);packets[name]=dict(manifest_id=m[ik],manifest_path=mp,manifest_sha256=sha256(raw).hexdigest(),unmanifested_git_files_sha256=extra_files,files_sha256=payload)
    mp='docs/design-engine/current/manifest.json';raw=_blob(root,tree,mp);m=json.loads(raw);_sealed(m,'manifest_id');_held(m)
    bind(mp,sha256(raw).hexdigest())
    dossier={ 'docs/design-engine/current/'+n:h for n,h in m['files_sha256'].items() }
    if {p for p in tree if p.startswith('docs/design-engine/current/')}!=set(dossier)|{mp}:
        raise RetiredReferenceHold('Retired current dossier inventory differs')
    for p,h in {**m['source_sha256'],**dossier,**m['linked_artifacts_sha256']}.items():bind(p,h)
    for n,h in m['workbench_files_sha256'].items():bind('docs/workbench/current/'+n,h)
    selector='engineering/development-baseline.toml';selector_raw=_blob(root,tree,selector);bind(selector,sha256(selector_raw).hexdigest())
    cfg=tomllib.loads(selector_raw.decode())
    if identity(cfg)!=m['selection_id']:raise RetiredReferenceHold('Retired selector identity differs')
    records={p:dict(tree[p],sha256=h) for p,h in sorted(bindings.items())}
    if len(records)>MAX_FILES or sum(v['size_bytes'] for v in records.values())>MAX_TOTAL_BYTES:
        raise RetiredReferenceHold('Retired source closure exceeds its budget')
    v=dict(schema='osr-retired-station-reference/1',reference_commit=COMMIT,
        reference_selection_id=m['selection_id'],reference_evaluation_id=m['evaluation_id'],
        reference_candidate_ids={k:m[k] for k in ('candidate_id','body_candidate_id','support_component_id','propulsion_component_id')},
        retired_current_manifest_id=m['manifest_id'],retired_current_manifest_sha256=sha256(raw).hexdigest(),
        retired_selector_sha256=sha256(selector_raw).hexdigest(),packets=packets,git_files=records,
        current_path_files_sha256=dict(sorted(actual_files.items())),
        retention_basis='Exact pinned Git blobs; retired comparison packets also checked in place; no bulk data copied',
        scope='Retired fixed-service LIM comparison only; neither900m nor100m is an active propulsion selection',
        native_archive_contents_preserved=True,nested_native_source_epochs_independently_validated=False,
        source_files_checked_against_current_paths=False,**FLAGS)
    v['retention_id']=identity(v);return v


def _storage_stamp(root,records):
    common=Path(_git(root,['rev-parse','--git-common-dir']).decode().strip())
    if not common.is_absolute():common=Path(root)/common
    objects=common.resolve()/'objects';alternates=objects/'info/alternates'
    if alternates.is_file() and alternates.read_bytes().strip():raise RetiredReferenceHold('External Git object alternates require independent reconstruction')
    paths=list((objects/'pack').glob('*'))
    paths.extend(objects/v['git_blob'][:2]/v['git_blob'][2:] for v in records.values())
    values=[]
    for p in sorted(set(paths)):
        if p.is_symlink():raise RetiredReferenceHold('Linked Git object storage is not allowed')
        if p.exists():
            s=p.stat();values.append((str(p),s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns))
    return str(common.resolve()),tuple(values)


def _verify_blobs(root,records):
    before=_storage_stamp(root,records);key=(COMMIT,identity(records),before)
    if key in _cache:_cache.move_to_end(key);return
    process=subprocess.Popen([*_command(),'cat-file','--batch'],cwd=root,env=_env(),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        done={}
        for name,v in records.items():
            oid=v['git_blob']
            if oid in done:
                if done[oid]!=v['sha256']:raise RetiredReferenceHold('Conflicting retired blob SHA-256')
                continue
            process.stdin.write((oid+'\n').encode());process.stdin.flush();header=process.stdout.readline().split()
            if len(header)!=3 or header[0].decode()!=oid or header[1]!=b'blob' or int(header[2])!=v['size_bytes']:
                raise RetiredReferenceHold('Retired Git blob missing or size differs: '+name)
            h=sha256();remaining=v['size_bytes']
            while remaining:
                b=process.stdout.read(min(1024**2,remaining))
                if not b:raise RetiredReferenceHold('Retired Git blob is truncated: '+name)
                remaining-=len(b);h.update(b)
            if process.stdout.read(1)!=b'\n' or h.hexdigest()!=v['sha256']:
                raise RetiredReferenceHold('Retired Git source bytes differ: '+name)
            done[oid]=h.hexdigest()
        process.stdin.close();process.wait(timeout=10)
        if process.returncode:raise RetiredReferenceHold('Retired Git blob reader failed')
    finally:
        if process.poll() is None:process.kill();process.wait(timeout=5)
        for f in (process.stdin,process.stdout,process.stderr):f.close()
    if _storage_stamp(root,records)!=before:raise RetiredReferenceHold('Git source storage changed during verification')
    _cache[key]=True
    while len(_cache)>2:_cache.popitem(last=False)


def _verify_current_coupled_packet(root):
    """Verify the changed packet in its exact current or retained source epoch."""
    folder=_path(root,'docs/design-engine/coupled-railway')
    paths=list(folder.rglob('*'))
    if any(p.is_symlink() for p in paths):
        raise RetiredReferenceHold('Linked active coupled-railway evidence is not allowed')
    manifest=json.loads(_path(root,'docs/design-engine/coupled-railway/manifest.json').read_bytes())
    from engineering.design_search import railway_publication
    source_epoch='current'
    if manifest.get('manifest_id')==COUPLED_PACKET_MANIFEST_ID:
        support_dir=_path(root,COUPLED_SOURCE_EPOCH)
        support_path=support_dir/'manifest.json'
        support=json.loads(_path(root,COUPLED_SOURCE_EPOCH+'/manifest.json').read_bytes())
        _sealed(support,'archive_id')
        if (support.get('schema')!='osr-coupled-railway-source-epoch/1'
                or support.get('archive_id')!=COUPLED_SOURCE_EPOCH_ID
                or support.get('coupled_manifest_id')!=COUPLED_PACKET_MANIFEST_ID
                or support.get('source_commit')!=COUPLED_SOURCE_COMMIT
                or support.get('source_git_blob')!=COUPLED_SOURCE_BLOB
                or support.get('scope')!='Exact historical source bytes for the unchanged coupled-railway packet; no calculation replay or current-evaluator admission'
                or any(support.get(k) is not False for k in FLAGS)):
            raise RetiredReferenceHold('Coupled source-epoch support does not match its explicit historical scope')
        if support.get('source_sha256')!={'engineering/station_rail/braking.py':'905af0b5762a1acf987a831d588f5b8b26f0b400f3bf33be2dac2f940ce38510'}:
            raise RetiredReferenceHold('Coupled historical source binding differs')
        expected_file='source/engineering/station_rail/braking.py'
        if support.get('files_sha256')!={expected_file:'905af0b5762a1acf987a831d588f5b8b26f0b400f3bf33be2dac2f940ce38510'}:
            raise RetiredReferenceHold('Coupled historical source archive inventory differs')
        if support.get('source_artifacts')!={'engineering/station_rail/braking.py':expected_file}:
            raise RetiredReferenceHold('Coupled historical source artifact path differs')
        source_path=_path(root,COUPLED_SOURCE_EPOCH+'/'+expected_file)
        if source_path.stat().st_size>1024*1024 or _hash(source_path)!=support['source_sha256']['engineering/station_rail/braking.py']:
            raise RetiredReferenceHold('Coupled historical braking source bytes differ')
        archive_paths=list(support_dir.rglob('*'))
        if any(p.is_symlink() for p in archive_paths):
            raise RetiredReferenceHold('Linked coupled source-epoch evidence is not allowed')
        archive_files={p.relative_to(support_dir).as_posix():_hash(p)
            for p in archive_paths if p.is_file() and p!=support_path}
        if archive_files!=support['files_sha256']:
            raise RetiredReferenceHold('Coupled historical source archive inventory differs')
        if manifest.get('source_sha256',{}).get('engineering/station_rail/braking.py')!=support['source_sha256']['engineering/station_rail/braking.py']:
            raise RetiredReferenceHold('Coupled packet does not bind its retained braking source')
        current_source=root/'engineering/station_rail/braking.py'
        archived_hash=support['source_sha256']['engineering/station_rail/braking.py']
        original_digest=railway_publication.digest
        def epoch_digest(path):
            if Path(path)==current_source:return archived_hash
            return original_digest(path)
        with _COUPLED_VERIFY_LOCK:
            railway_publication.digest=epoch_digest
            try:
                result=railway_publication.verify(root,output=folder)
            finally:
                railway_publication.digest=original_digest
        paths.extend([support_path,source_path]);source_epoch='historical'
    else:
        result=railway_publication.verify(root,output=folder)
    if result.get('verified') is not True:
        raise RetiredReferenceHold('Current coupled-railway publication did not verify')
    return dict(result,source_epoch=source_epoch),paths


def verify_coupled_packet(root=ROOT):
    """Verify only the coupled packet used by Journey C, without unrelated archives."""
    root=Path(root).resolve()
    result,_=_verify_current_coupled_packet(root)
    expected=COUPLED_PACKET_MANIFEST_ID
    if result.get('manifest_id')!=expected:
        raise RetiredReferenceHold('Coupled Journey C manifest identity differs')
    if result.get('source_epoch')!='historical':
        raise RetiredReferenceHold('Coupled Journey C must remain explicitly historical')
    return dict(schema='osr-coupled-railway-journey-c-integrity/1',verified=True,
        manifest_id=result['manifest_id'],source_epoch=result['source_epoch'],
        analytical_replay=False,native_solver_jobs=0,
        **FLAGS)


def verify(root=ROOT):
    root=Path(root).resolve()
    if _hash(_path(root,PRODUCER))!=_LOADED_SHA:raise RetiredReferenceHold('Loaded retired-reference verifier source differs')
    path=_path(root,OUTPUT+'/manifest.json');raw=path.read_bytes();m=json.loads(raw)
    if m.get('retention_id')!=EXPECTED_RECEIPT_ID or identity({k:v for k,v in m.items() if k!='retention_id'})!=EXPECTED_RECEIPT_ID:
        raise RetiredReferenceHold('Retired reference receipt differs from its fixed pin')
    if m!=_snapshot(root):raise RetiredReferenceHold('Retired reference Git bindings differ')
    _verify_blobs(root,m['git_files'])
    deps={PRODUCER:_hash(_path(root,PRODUCER)),OUTPUT+'/manifest.json':sha256(raw).hexdigest()}
    stamps={path:_stamp(path),_path(root,PRODUCER):_stamp(_path(root,PRODUCER))}
    active_packets={};active_packet_source_epochs={};evolved_packets=set()
    for name,packet in m['packets'].items():
        folder=_path(root,'docs/design-engine/'+name);paths=list(folder.rglob('*'))
        if any(p.is_symlink() for p in paths):raise RetiredReferenceHold('Linked retired evidence is not allowed')
        if name=='coupled-railway':
            manifest_path=folder/'manifest.json'
            if not manifest_path.is_file():raise RetiredReferenceHold('Current coupled-railway manifest is missing')
            current_manifest_sha=sha256(manifest_path.read_bytes()).hexdigest()
            if current_manifest_sha!=packet['manifest_sha256']:
                result,paths=_verify_current_coupled_packet(root)
                evolved_packets.add(name)
                active_packets[name]=result['manifest_id']
                active_packet_source_epochs[name]=result.get('source_epoch','current')
                # README bytes remain covered by the publication verifier and
                # mutation stamps, but do not enter the calculation dependency
                # identity for an evolved packet.
                deps.update({p.relative_to(root).as_posix():_hash(p) for p in paths
                    if p.is_file() and p.name!='README.md'})
                stamps.update({p:_stamp(p) for p in paths if p.is_file()})
                continue
        if {p.relative_to(root).as_posix() for p in paths if p.is_file()}!=set(packet['files_sha256']):
            raise RetiredReferenceHold('Retired comparison file inventory changed: '+name)
    for name,wanted in m['current_path_files_sha256'].items():
        if any(name.startswith('docs/design-engine/'+packet+'/') for packet in evolved_packets):
            continue
        p=_path(root,name)
        if not p.is_file() or _hash(p)!=wanted:raise RetiredReferenceHold('Retired comparison payload changed: '+name)
        deps[name]=wanted;stamps[p]=_stamp(p)
    if _hash(_path(root,PRODUCER))!=_LOADED_SHA or path.read_bytes()!=raw or any(_stamp(p)!=s for p,s in stamps.items()):
        raise RetiredReferenceHold('Retired reference inputs changed during verification')
    return dict(verified=True,reference_commit=COMMIT,retention_id=EXPECTED_RECEIPT_ID,
        reference_selection_id=m['reference_selection_id'],reference_evaluation_id=m['reference_evaluation_id'],
        reference_candidate_ids=m['reference_candidate_ids'],retired_manifest_ids={k:v['manifest_id'] for k,v in m['packets'].items()},
        packet_count=len(m['packets']),git_file_count=len(m['git_files']),
        dependency_sha256=dict(sorted(deps.items())),active_packet_manifest_ids=active_packets,
        active_packet_source_epochs=active_packet_source_epochs,
        historical_payloads_verified_from_pinned_git=True,scope=m['scope'],**FLAGS)


def reference_bytes(relative,root=ROOT):
    """Read one explicitly pinned old file, without current-evaluator admission."""
    verified=verify(root);root=Path(root).resolve()
    m=json.loads(_path(root,OUTPUT+'/manifest.json').read_bytes())
    if relative not in m['git_files']:raise RetiredReferenceHold('Known pinned retired source or artifact required')
    record=m['git_files'][relative];raw=_blob(root,{relative:record},relative)
    if sha256(raw).hexdigest()!=record['sha256']:raise RetiredReferenceHold('Retired Git artifact bytes differ')
    meta=dict(reference_commit=COMMIT,retention_id=EXPECTED_RECEIPT_ID,path=relative,
        sha256=record['sha256'],git_blob=record['git_blob'],
        reference_selection_id=verified['reference_selection_id'],
        reference_evaluation_id=verified['reference_evaluation_id'],
        reference_candidate_ids=verified['reference_candidate_ids'],
        scope='Opaque retired-reference artifact only; not admitted under the current source or selection',**FLAGS)
    return raw,meta


def reference_current(root=ROOT):
    """Return the OLD summary and manifest with their original identities."""
    raw,_=reference_bytes('docs/design-engine/current/summary.json',root)
    manifest,_=reference_bytes('docs/design-engine/current/manifest.json',root)
    return json.loads(raw),json.loads(manifest)


def reference_archive(name,root=ROOT):
    if name not in ('vehicle','drive','controls'):
        raise RetiredReferenceHold('Named retired vehicle, drive or controls archive required')
    return reference_bytes('docs/design-engine/current/native-'+name+'.tar.gz',root)


def publish(root=ROOT,output=None):
    """Reproduce the one authorized pinned snapshot; never adopt newer sources."""
    v=_snapshot(root)
    if v['retention_id']!=EXPECTED_RECEIPT_ID:raise RetiredReferenceHold('Pinned capture recipe differs')
    out=Path(root)/OUTPUT if output is None else Path(output)
    if out.exists():raise FileExistsError('Fresh retired reference output required')
    out.mkdir(parents=True);(out/'manifest.json').write_bytes(encoded(v));return v


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('verify','publish'));p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--output',type=Path)
    a=p.parse_args();result=verify(a.root) if a.action=='verify' else publish(a.root,a.output)
    print(json.dumps({k:v for k,v in result.items() if k not in ('dependency_sha256','git_files','current_path_files_sha256','packets')},sort_keys=True))
