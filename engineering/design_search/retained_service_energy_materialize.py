"""Reconstruct or stream-audit the fixed additional service-energy epoch.

Audit mode writes no packet tree. Materialize mode creates one private tree,
reassembles its sole untracked sourced-cell archive and verifies it twice.
Neither mode replays a solver or grants current-evaluator/physical acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile

from . import retained_packet_materialize as prior
from . import retained_service_energy_epoch as extra
from . import retained_source_epoch as retained

COMMIT='5cd6b8ff9b2fdf3c705f0d68073543c58e6dec76'
PINS_ID='91d8be8f7893aea692e90683c214bbda0d35c4dbe1a652c7cb8908e3d3a4f050'
ARCHIVE_ID='d2f4511f180592083945bb993658353218b9efcf91d0dd3f21d02e58399967b9'
SOURCE_EPOCH_ID='8d01378a06607b2bb671c4d3f318c177661066a5434af8df257042794e9268bc'
SOURCE_ARCHIVE_SHA='5e1488edf2c771138e2c332099c6b4e5969774d1730ccbd857af1a3277b32b30'
SOURCED_TAR='docs/design-engine/sourced-case/sourced-cell.tar.gz'
STORAGE='docs/design-engine/sourced-case/storage.json'
SOURCED_MANIFEST='docs/design-engine/sourced-case/manifest.json'
OLD_PRODUCER='docs/design-engine/retained-physical-followup-source-epoch/producer.tar.gz'
OLD_WRAPPER='docs/design-engine/retained-physical-followup-source-epoch/manifest.json'
TAR_BYTES=101182028
TAR_SHA='f27adb241ce58fcb5ea42a6456a1c91b911e46d1ccf4a78588f0e53a1483993b'
GIT_FILES=365
GIT_BYTES=971850897
FINAL_FILES=366
FINAL_BYTES=1073032925
MAX_BYTES=1280*1024*1024
MAX_ENTRIES=20000
MAX_TAR_BYTES=MAX_BYTES+MAX_ENTRIES*1024+1024*1024
MAX_STDOUT=16*1024*1024
CHUNK=1024*1024
LIMIT_S=540
PRODUCER='engineering/design_search/retained_service_energy_materialize.py'
HELPERS=('engineering/design_search/retained_packet_materialize.py',
         'engineering/design_search/retained_service_energy_epoch.py',
         'engineering/design_search/retained_source_epoch.py')
FOLDERS=tuple(sorted({str(PurePosixPath(extra.PREFIX+name).parent) for name in extra.CATALOG}
                    | {str(PurePosixPath(extra.COMPANION).parent)}))
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
    operating_release=False,configuration_adopted=False,selected_reference_changed=False,
    physical_journey_completed=False,numerical_reexecuted=False,current_evaluator_admission=False,
    physical_equivalence_proven=False)


def _allowed_file(name):
    prior._relative(name)
    if not any(name.startswith(folder+'/') for folder in FOLDERS):
        raise ValueError('Git path outside fixed additional-packet allowlist')
    return name


def _ordinary(path,*,directory=True):
    return prior._ordinary(path,directory=directory)


def _file(path,limit=extra.MAX_JSON,*,materialize=False):
    return extra._file_data(path,limit,materialize=materialize)


def _env():
    value=prior._environment()
    for name in ('GIT_CONFIG_PARAMETERS','GIT_CONFIG_SYSTEM','GIT_NAMESPACE'):
        value.pop(name,None)
    return value


def _fixed(expected_commit,expected_pins_id,expected_archive_id):
    if (expected_commit!=COMMIT or expected_pins_id!=PINS_ID or expected_archive_id!=ARCHIVE_ID):
        raise ValueError('The exact externally pinned commit, pins and archive identities are required')


def _preflight(archive,pins,expected_pins_id,expected_archive_id):
    archive=_ordinary(archive);pins=extra._pins(pins,expected_pins_id)
    if {p.name for p in archive.iterdir()}!={'manifest.json','sources.tar.gz'}:
        raise ValueError('Exact retained archive inventory required')
    msha,raw,_=_file(archive/'manifest.json',materialize=True);meta=retained._json(raw)
    if (set(meta)!=extra.META_KEYS or meta.get('schema')!='osr-retained-service-energy-extra-epoch/1'
            or meta.get('archive_id')!=expected_archive_id
            or retained._id({k:v for k,v in meta.items() if k!='archive_id'})!=expected_archive_id
            or meta.get('git_commit')!=COMMIT or meta.get('pins_id')!=expected_pins_id
            or meta.get('reference_candidate_id')!=extra.REFERENCE or meta.get('selection_id')!=extra.SELECTION
            or any(meta.get(k) is not False for k in (*extra.FLAGS,'configuration_adopted','selected_reference_changed',
                'numerical_reexecuted','current_evaluator_admission','physical_equivalence_proven'))):
        raise ValueError('Pinned historical archive metadata or disposition differs')
    sources=retained._checked_map(meta.get('original_source_sha256'))
    if len(sources)!=442 or retained._id(sources)!=SOURCE_EPOCH_ID or meta.get('source_epoch_id')!=SOURCE_EPOCH_ID:
        raise ValueError('The exact 442-source original epoch is required')
    if set(meta.get('records',{}))!=set(extra.CATALOG) or set(meta.get('folders',{}))!=set(FOLDERS):
        raise ValueError('Exact 14 records and 13 unique folders required')
    for name,record in meta['records'].items():
        if (record.get('manifest_id')!=pins['manifest_ids'][name]
                or record.get('manifest_sha256')!=pins['manifest_sha256'][name]):
            raise ValueError('Pinned original manifest record differs')
    physical=meta.get('physical_followup',{})
    if (physical.get('original_manifest_id')!=pins['companion_manifest_id']
            or physical.get('original_manifest_sha256')!=pins['companion_manifest_sha256']
            or physical.get('original_producer_source_count')!=26):
        raise ValueError('Separate original 26-source physical producer epoch required')
    transport=meta.get('sourced_transport',{})
    if (transport.get('storage_id')!=pins['storage_id'] or transport.get('storage_sha256')!=pins['storage_sha256']
            or transport.get('archive_sha256')!=TAR_SHA or transport.get('total_bytes')!=TAR_BYTES
            or transport.get('chunk_count')!=5):
        raise ValueError('Pinned five-chunk sourced transport required')
    expected={};dirs=set();total=0
    for folder,inv in sorted(meta['folders'].items()):
        if (set(inv)!={'files_sha256','directories','file_count','entry_count','bytes'}
                or not isinstance(inv['files_sha256'],dict) or not isinstance(inv['directories'],list)):
            raise ValueError('Exact historical folder inventory required')
        local=set()
        for name,sha in inv['files_sha256'].items():
            retained._path(name);retained._hex(sha);full=folder+'/'+name;_allowed_file(full)
            if full in expected:raise ValueError('Duplicate historical packet path')
            expected[full]=sha
            for parent in PurePosixPath(name).parents:
                if str(parent)!='.':local.add(str(parent))
        if (set(inv['directories'])!=local or len(inv['directories'])!=len(local)
                or inv['file_count']!=len(inv['files_sha256'])
                or inv['entry_count']!=len(local)+len(inv['files_sha256'])
                or type(inv['bytes']) is not int or inv['bytes']<0):
            raise ValueError('Original folder counts or directory inventory differs')
        total+=inv['bytes']
    for name in expected:
        for parent in PurePosixPath(name).parents:
            if str(parent)!='.':dirs.add(str(parent))
    if len(expected)!=FINAL_FILES or total!=FINAL_BYTES or expected.get(SOURCED_TAR)!=TAR_SHA:
        raise ValueError('The exact 366-file historical inventory is required')
    asha,raw_tar,_=_file(archive/'sources.tar.gz',retained.MAX_ARCHIVE_BYTES,materialize=True)
    if asha!=SOURCE_ARCHIVE_SHA or meta.get('source_archive_sha256')!=asha:
        raise ValueError('Pinned source archive differs')
    retained._check_archive(raw_tar,sources)
    if _file(archive/'manifest.json')[0]!=msha or _file(archive/'sources.tar.gz')[0]!=asha:
        raise ValueError('Historical archive changed during preflight')
    return meta,expected,dirs,(msha,asha)


def _bounded_git(repo,args,log,max_bytes=MAX_STDOUT):
    timeout=shutil.which('timeout')
    if not timeout:raise ValueError('Local timeout executable required')
    with log.open('ab') as errors:
        child=subprocess.Popen([timeout,str(LIMIT_S),*prior._git(),*args],cwd=repo,env=_env(),
            stdout=subprocess.PIPE,stderr=errors,bufsize=0,preexec_fn=prior._limit_git_log)
        out=bytearray()
        try:
            while True:
                block=child.stdout.read(min(CHUNK,max_bytes+1-len(out)))
                if not block:break
                out.extend(block)
                if len(out)>max_bytes:raise ValueError('Git output exceeds declared bound')
            code=child.wait(timeout=10)
            if code!=0:raise ValueError('Local Git command failed: '+str(code))
        finally:
            if child.poll() is None:child.kill();child.wait()
            child.stdout.close()
    return bytes(out)


def _tree(repo,expected,log):
    if _bounded_git(repo,['cat-file','-t',COMMIT],log,max_bytes=64)!=b'commit\n':
        raise ValueError('Pinned Git commit absent or not a commit; no fetch attempted')
    raw=_bounded_git(repo,['ls-tree','-r','-z','-l',COMMIT,'--',*FOLDERS],log)
    if raw and not raw.endswith(b'\0'):raise ValueError('Incomplete Git tree listing')
    tree={};total=0
    for row in raw.split(b'\0'):
        if not row:continue
        try:
            metadata,raw_name=row.split(b'\t',1);mode,kind,oid,size=metadata.split();name=raw_name.decode('utf-8','strict');n=int(size)
        except (ValueError,UnicodeDecodeError) as exc:raise ValueError('Malformed Git tree entry') from exc
        _allowed_file(name)
        if (mode not in (b'100644',b'100755') or kind!=b'blob' or n<0 or n>retained.MAX_PACKET_FILE_BYTES
                or len(oid)!=40 or any(c not in b'0123456789abcdef' for c in oid) or name in tree):
            raise ValueError('Unique normal SHA-1 Git blobs required')
        total+=n
        if len(tree)>=GIT_FILES or total>MAX_BYTES:raise ValueError('Bounded original Git tree required')
        tree[name]=dict(oid=oid.decode(),size=n)
    if (len(tree)!=GIT_FILES or total!=GIT_BYTES or set(expected)-set(tree)!={SOURCED_TAR}
            or set(tree)-set(expected) or SOURCED_TAR in tree):
        raise ValueError('Git tree must match historical inventory except the one sourced archive')
    return dict(sorted(tree.items()))


def _git_blob(repo,entry,log):
    if entry['size']>extra.MAX_JSON:raise ValueError('Bounded Git metadata blob required')
    raw=_bounded_git(repo,['cat-file','blob',entry['oid']],log,max_bytes=extra.MAX_JSON)
    if len(raw)!=entry['size'] or hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest()!=entry['oid']:
        raise ValueError('Pinned Git metadata blob differs')
    return raw


def _git_metadata(repo,tree,pins,meta,log):
    for name,contract in sorted(extra.CATALOG.items()):
        path=extra.PREFIX+name;raw=_git_blob(repo,tree[path],log);value=retained._json(raw);key=contract[1]
        if (hashlib.sha256(raw).hexdigest()!=pins['manifest_sha256'][name] or value.get('schema')!=contract[0]
                or value.get(key)!=pins['manifest_ids'][name]
                or retained._id({k:v for k,v in value.items() if k!=key})!=pins['manifest_ids'][name]):
            raise ValueError('Pinned original Git manifest differs: '+name)
    companion=_git_blob(repo,tree[extra.COMPANION],log)
    if hashlib.sha256(companion).hexdigest()!=pins['companion_manifest_sha256']:
        raise ValueError('Pinned physical-followup companion differs')
    raw=_git_blob(repo,tree[STORAGE],log);storage=retained._json(raw)
    if (hashlib.sha256(raw).hexdigest()!=pins['storage_sha256'] or storage.get('storage_id')!=pins['storage_id']
            or retained._id({k:v for k,v in storage.items() if k!='storage_id'})!=pins['storage_id']
            or storage.get('schema')!='osr-sourced-cell-chunk-storage/1'
            or storage.get('publication_id')!=pins['manifest_ids']['sourced-case/manifest.json']
            or storage.get('publication_manifest_sha256')!=pins['manifest_sha256']['sourced-case/manifest.json']
            or storage.get('archive_path')!='sourced-cell.tar.gz' or storage.get('archive_sha256')!=TAR_SHA
            or storage.get('total_bytes')!=TAR_BYTES or storage.get('chunk_bytes')!=24*1024**2
            or any(storage.get(k) is not False for k in (*extra.FLAGS,'selected_reference_changed'))):
        raise ValueError('Pinned sourced storage metadata differs')
    chunks=storage.get('chunks')
    if not isinstance(chunks,list) or len(chunks)!=5:raise ValueError('Exactly five sourced chunks required')
    for i,row in enumerate(chunks):
        if not isinstance(row,dict):raise ValueError('Pinned sourced chunk object required')
        name='docs/design-engine/sourced-case/sourced-cell.part-'+f'{i:03d}'
        size=min(storage['chunk_bytes'],TAR_BYTES-i*storage['chunk_bytes'])
        if (set(row)!={'path','bytes','sha256'} or row['path']!=PurePosixPath(name).name or row['bytes']!=size
                or name not in tree or tree[name]['size']!=size or meta['folders'][str(PurePosixPath(name).parent)]['files_sha256'].get(row['path'])!=row['sha256']):
            raise ValueError('Pinned sourced chunk declaration differs')
    return storage


def _exact(stream,n):
    return prior._exact(stream,n)


def _stream_tar(stream,tree,expected,storage,*,destination=None):
    """Verify every Git blob; optionally write each only into a private root."""
    if destination is not None:destination=_ordinary(destination)
    dirs=set()
    for name in tree:
        for parent in PurePosixPath(name).parents:
            if str(parent)!='.':dirs.add(str(parent))
    files_seen=set();dirs_seen=set();global_seen=False;entries=0;raw_total=0;blob_total=0
    chunks=['docs/design-engine/sourced-case/'+row['path'] for row in storage['chunks']]
    chunk_index=0;chunk_hash=hashlib.sha256();chunk_bytes=0;old_archive=None
    while True:
        header=_exact(stream,512);raw_total+=512
        if raw_total>MAX_TAR_BYTES:raise ValueError('Git archive byte budget exceeded')
        if header==b'\0'*512:
            if _exact(stream,512)!=b'\0'*512:raise ValueError('Incomplete tar end marker')
            padding=0
            while True:
                tail=stream.read(min(CHUNK,65537-padding))
                if not tail:break
                padding+=len(tail)
                if padding>65536 or any(tail):raise ValueError('Unexpected trailing Git archive data')
            break
        try:entry=tarfile.TarInfo.frombuf(header,'utf-8','strict')
        except (tarfile.HeaderError,ValueError,UnicodeDecodeError) as exc:raise ValueError('Invalid Git tar header') from exc
        entries+=1
        if entries>MAX_ENTRIES or entry.size<0:raise ValueError('Git tar entry budget exceeded')
        if entry.type==tarfile.XGLTYPE:
            wanted=('52 comment='+COMMIT+'\n').encode()
            if global_seen or entries!=1 or entry.name!='pax_global_header' or entry.size!=len(wanted):
                raise ValueError('One bounded Git commit header required')
            if _exact(stream,entry.size)!=wanted:raise ValueError('Git archive commit comment differs')
            pad=(-entry.size)%512
            if any(_exact(stream,pad)):raise ValueError('Nonzero Git metadata padding')
            raw_total+=entry.size+pad;global_seen=True;continue
        if not global_seen:raise ValueError('Git archive commit header missing')
        if entry.type not in (tarfile.REGTYPE,tarfile.AREGTYPE,tarfile.DIRTYPE):
            raise ValueError('Git tar links, special files and extensions are rejected')
        name=entry.name;prior._relative(name)
        if entry.isdir():
            if entry.size!=0 or name not in dirs or name in dirs_seen or name in files_seen:
                raise ValueError('Unlisted or duplicate Git directory')
            if destination is not None:
                _ordinary((destination/name).parent);os.mkdir(destination/name,0o700)
            dirs_seen.add(name);continue
        _allowed_file(name)
        if name not in tree or name in files_seen or name in dirs_seen:
            raise ValueError('Unlisted or duplicate Git file')
        want=tree[name]
        if entry.size!=want['size'] or entry.size>retained.MAX_PACKET_FILE_BYTES:
            raise ValueError('Git file size differs from pinned tree')
        raw_total+=entry.size+(-entry.size)%512;blob_total+=entry.size
        if raw_total>MAX_TAR_BYTES or blob_total>MAX_BYTES:raise ValueError('Git archive exceeds resource budget')
        h1=hashlib.sha1();h1.update(('blob '+str(entry.size)+'\0').encode());h2=hashlib.sha256();left=entry.size
        if name==OLD_PRODUCER and entry.size>retained.MAX_ARCHIVE_BYTES:
            raise ValueError('Original producer archive exceeds compressed byte limit')
        output=None;old_data=bytearray() if name==OLD_PRODUCER else None
        is_chunk=name in chunks
        if is_chunk:
            if chunk_index>=len(chunks) or name!=chunks[chunk_index]:raise ValueError('Sourced chunks not in original order')
            chunk_index+=1
        if destination is not None:
            path=destination/name;_ordinary(path.parent)
            fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0),0o600);output=os.fdopen(fd,'wb')
        try:
            while left:
                data=_exact(stream,min(left,CHUNK));left-=len(data);h1.update(data);h2.update(data)
                if is_chunk:chunk_hash.update(data);chunk_bytes+=len(data)
                if old_data is not None:old_data.extend(data)
                if output is not None:output.write(data)
        finally:
            if output is not None:output.close()
        if h1.hexdigest()!=want['oid'] or h2.hexdigest()!=expected[name]:
            raise ValueError('Git blob or historical packet SHA differs: '+name)
        if old_data is not None:old_archive=bytes(old_data)
        if any(_exact(stream,(-entry.size)%512)):raise ValueError('Nonzero Git file padding')
        files_seen.add(name)
    if not global_seen or files_seen!=set(tree) or dirs_seen!=dirs or blob_total!=sum(v['size'] for v in tree.values()):
        raise ValueError('Git stream does not reproduce the pinned tree')
    if chunk_index!=5 or chunk_bytes!=TAR_BYTES or chunk_hash.hexdigest()!=TAR_SHA:
        raise ValueError('Combined sourced chunks do not reproduce the pinned full archive')
    if old_archive is None:raise ValueError('Original physical producer archive missing')
    return dict(file_count=len(files_seen),directory_count=len(dirs_seen),blob_bytes=blob_total,
        sourced_chunks=len(chunks),sourced_combined_bytes=chunk_bytes,sourced_combined_sha256=chunk_hash.hexdigest()),old_archive


def _old_archive(raw,wrapper):
    old=retained._checked_map(wrapper.get('original_source_sha256'))
    if (len(old)!=26 or hashlib.sha256(raw).hexdigest()!=wrapper.get('producer_archive_sha256')
            or raw[:10]!=bytes.fromhex('1f8b08000000000002ff')):
        raise ValueError('Pinned separate physical producer epoch differs')
    retained._check_archive(raw[:8]+b'\x00'+raw[9:],old)


def _assemble(root,storage):
    """Create the sole missing original payload without replacing any path."""
    target=root/SOURCED_TAR;_ordinary(target.parent)
    fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0),0o600)
    combined=hashlib.sha256();total=0
    with os.fdopen(fd,'wb') as out:
        for row in storage['chunks']:
            name='docs/design-engine/sourced-case/'+row['path'];path=extra.retained._ordinary(root/name)
            before=path.lstat();sig=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
            if before.st_nlink!=1 or before.st_size!=row['bytes']:raise ValueError('Unsafe sourced chunk file')
            part=hashlib.sha256();count=0;read_fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
            with os.fdopen(read_fd,'rb') as source:
                if sig(before)!=sig(os.fstat(source.fileno())):raise ValueError('Sourced chunk changed before reading')
                while data:=source.read(CHUNK):
                    count+=len(data);total+=len(data);part.update(data);combined.update(data);out.write(data)
                if sig(before)!=sig(os.fstat(source.fileno())) or sig(before)!=sig(path.lstat()):
                    raise ValueError('Sourced chunk changed during reading')
            if count!=row['bytes'] or part.hexdigest()!=row['sha256']:
                raise ValueError('Sourced chunk bytes differ during reconstruction')
        out.flush();os.fsync(out.fileno())
    if total!=TAR_BYTES or combined.hexdigest()!=TAR_SHA or _file(target,retained.MAX_PACKET_FILE_BYTES)[0]!=TAR_SHA:
        raise ValueError('Reassembled sourced archive differs')


def _check_root(root,expected,dirs):
    root=_ordinary(root);actual={};actual_dirs=set();total=0;entries=0
    for path in root.rglob('*'):
        entries+=1
        if entries>MAX_ENTRIES:raise ValueError('Materialized entry budget exceeded')
        name=path.relative_to(root).as_posix();prior._relative(name);info=path.lstat()
        if stat.S_ISDIR(info.st_mode):actual_dirs.add(name)
        elif stat.S_ISREG(info.st_mode):
            if info.st_nlink!=1 or name not in expected:raise ValueError('Unlisted or linked materialized file')
            total+=info.st_size
            if total>MAX_BYTES:raise ValueError('Materialized byte budget exceeded')
            actual[name]=_file(path,retained.MAX_PACKET_FILE_BYTES)[0]
        else:raise ValueError('Materialized tree contains a link or special file')
    if actual!=expected or actual_dirs!=dirs or total!=FINAL_BYTES:
        raise ValueError('Materialized root differs from pinned packet inventory')


def run(repo,output,archive,*,pins,mode,expected_commit,expected_pins_id,expected_archive_id):
    _fixed(expected_commit,expected_pins_id,expected_archive_id)
    if mode not in ('audit','materialize'):raise ValueError('Audit or materialize mode required')
    repo=_ordinary(repo);archive=_ordinary(archive);out=Path(os.path.abspath(output));_ordinary(out.parent)
    if any(p.is_symlink() for p in (out,*out.parents)) or out.exists():
        raise ValueError('Fresh ordinary destination required')
    if (out==repo or out.is_relative_to(repo) or repo.is_relative_to(out)
            or out==archive or out.is_relative_to(archive) or archive.is_relative_to(out)):
        raise ValueError('Private destination must be disjoint from inputs')
    pins=extra._pins(pins,expected_pins_id)
    helper_paths=(Path(__file__),Path(prior.__file__),Path(extra.__file__),Path(retained.__file__))
    helper_hashes=[_file(path)[0] for path in helper_paths]
    meta,expected,dirs,archive_hashes=_preflight(archive,pins,expected_pins_id,expected_archive_id)
    if mode=='materialize' and shutil.disk_usage(out.parent).free<FINAL_BYTES+200*1024*1024:
        raise ValueError('Insufficient free disk for one bounded reconstruction plus reserve')
    stage=Path(tempfile.mkdtemp(prefix='.service-energy-materialize-',dir=out.parent))
    print('Private stage retained on failure: '+str(stage),file=sys.stderr,flush=True)
    preflight_log=stage/'git-preflight.stderr.log';archive_log=stage/'git-archive.stderr.log'
    tree=_tree(repo,expected,preflight_log);storage=_git_metadata(repo,tree,pins,meta,preflight_log)
    wrapper=retained._json(_git_blob(repo,tree[OLD_WRAPPER],preflight_log))
    timeout=shutil.which('timeout')
    if not timeout:raise ValueError('Local timeout unavailable; private stage retained: '+str(stage))
    root=None
    if mode=='materialize':root=stage/'root';root.mkdir(mode=0o700)
    with archive_log.open('xb') as errors:
        child=subprocess.Popen([timeout,str(LIMIT_S),*prior._git(),'archive','--format=tar',COMMIT,'--',*FOLDERS],
            cwd=repo,env=_env(),stdout=subprocess.PIPE,stderr=errors,bufsize=0,preexec_fn=prior._limit_git_log)
        try:
            details,old_raw=_stream_tar(child.stdout,tree,expected,storage,destination=root)
            code=child.wait(timeout=10)
            if code!=0:raise ValueError('Local Git archive failed with exit '+str(code))
        finally:
            if child.poll() is None:child.kill();child.wait()
            child.stdout.close()
    _old_archive(old_raw,wrapper)
    if _tree(repo,expected,preflight_log)!=tree:raise ValueError('Pinned Git tree changed during streaming')
    verification=None
    if mode=='materialize':
        _assemble(root,storage);_check_root(root,expected,dirs)
        verification=extra.verify(root,archive,pins=pins,expected_pins_id=expected_pins_id,expected_archive_id=expected_archive_id)
        _check_root(root,expected,dirs)
        if extra.verify(root,archive,pins=pins,expected_pins_id=expected_pins_id,expected_archive_id=expected_archive_id)!=verification:
            raise ValueError('Historical packet verification changed during replay')
        _check_root(root,expected,dirs)
    if (_preflight(archive,pins,expected_pins_id,expected_archive_id)[3]!=archive_hashes
            or [_file(path)[0] for path in helper_paths]!=helper_hashes):
        raise ValueError('Archive or executing source changed; private stage retained: '+str(stage))
    value=dict(schema='osr-service-energy-packet-materialization/1',mode=mode,git_commit=COMMIT,
        pins_id=expected_pins_id,archive_id=expected_archive_id,source_epoch_id=SOURCE_EPOCH_ID,
        reference_candidate_id=extra.REFERENCE,selection_id=extra.SELECTION,
        git_tree_id=retained._id(tree),git_tree_files=details['file_count'],git_blob_bytes=details['blob_bytes'],
        expected_final_files=FINAL_FILES,expected_final_bytes=FINAL_BYTES,
        sourced_combined_sha256=details['sourced_combined_sha256'],sourced_combined_bytes=details['sourced_combined_bytes'],
        original_physical_producer_sha256=hashlib.sha256(old_raw).hexdigest(),original_physical_source_count=26,
        source_sha256=dict(zip((PRODUCER,*HELPERS),helper_hashes)),
        git_preflight_stderr_sha256=_file(preflight_log)[0],git_archive_stderr_sha256=_file(archive_log)[0],
        archive_verification=verification,full_packet_verifier_executed=mode=='materialize',
        root_written=mode=='materialize',scope='Historical Git-byte and source-epoch integrity only; no numerical replay or current evaluator admission',
        isolation='No filesystem or network sandbox; Git lazy fetch disabled; time/resource limits are process boundaries only',**FLAGS)
    value['result_id']=retained._id(value)
    (stage/'result.json').write_bytes(retained._encoded(value))
    if mode=='materialize':_check_root(root,expected,dirs)
    retained._rename_noreplace(stage,out)
    return value


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=('audit','materialize'))
    p.add_argument('--git-repo',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    p.add_argument('--archive-directory',required=True,type=Path);p.add_argument('--pins',required=True,type=Path)
    p.add_argument('--expected-commit',required=True);p.add_argument('--expected-pins-id',required=True);p.add_argument('--expected-archive-id',required=True)
    args=p.parse_args();pins=retained._json(_file(args.pins,1024*1024,materialize=True)[1])
    result=run(args.git_repo,args.output,args.archive_directory,pins=pins,mode=args.mode,
        expected_commit=args.expected_commit,expected_pins_id=args.expected_pins_id,expected_archive_id=args.expected_archive_id)
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':main()
