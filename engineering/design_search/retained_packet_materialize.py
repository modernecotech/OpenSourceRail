"""Reconstruct exact retained packet trees from a pinned local Git object.

Only the fixed historical packet paths are read, and extraction never invokes
TarFile.extract.  The original source-epoch verifier checks the reconstructed
packet bytes before private atomic handoff.  This is archival integrity only:
no physics is replayed and no current-evaluator or physical admission follows.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import resource
import shutil
import stat
import subprocess
import tarfile
import tempfile

from . import retained_source_epoch as retained

ORIGINAL_COMMIT='dad8c4bedb2361d3e621e9def312273167279027'
PRODUCER='engineering/design_search/retained_packet_materialize.py'
ALLOWED_PREFIXES=tuple('docs/design-engine/'+name for name in sorted(retained.CATALOG))
MAX_FILES=10000
MAX_ENTRIES=20000
MAX_TOTAL_BYTES=1024*1024*1024
MAX_RAW_TAR_BYTES=MAX_TOTAL_BYTES+MAX_ENTRIES*1024+1024*1024
MAX_TREE_OUTPUT=16*1024*1024
MAX_LOG_BYTES=16*1024*1024
GIT_COMMAND_LIMIT_S=540
CHUNK=1024*1024


def _limit_git_log():
    # The child writes only a pipe and its private stderr file. Limit the latter
    # even on a corrupt repository; this is a resource limit, not a sandbox.
    resource.setrlimit(resource.RLIMIT_FSIZE,(MAX_LOG_BYTES,MAX_LOG_BYTES))


def _ordinary(path, *, directory=True):
    path=Path(os.path.abspath(path))
    if any(p.is_symlink() for p in (path,*path.parents)):
        raise ValueError('Symlink path or ancestor rejected')
    mode=path.lstat().st_mode
    if not (stat.S_ISDIR(mode) if directory else stat.S_ISREG(mode)):
        raise ValueError('Ordinary directory or regular file required')
    return path


def _relative(name):
    if not isinstance(name,str) or not name or '\\' in name:
        raise ValueError('Ordinary relative POSIX path required')
    path=PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or str(path)!=name:
        raise ValueError('Ordinary relative POSIX path required')
    return path


def _allowed_file(name):
    _relative(name)
    if not any(name.startswith(prefix+'/') for prefix in ALLOWED_PREFIXES):
        raise ValueError('Git tree file is outside the fixed packet allowlist: '+name)
    return name


def _pin_commit(commit):
    if commit!=ORIGINAL_COMMIT:
        raise ValueError('Exact externally pinned original commit required')
    return commit


def _environment():
    env=dict(os.environ)
    env.update(GIT_NO_REPLACE_OBJECTS='1',GIT_NO_LAZY_FETCH='1',GIT_TERMINAL_PROMPT='0',
        GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,GIT_ATTR_NOSYSTEM='1',GIT_OPTIONAL_LOCKS='0')
    # Remove caller-supplied repository/config overrides.  This is not a network
    # sandbox; Git itself is instructed not to lazily fetch missing objects.
    for k in tuple(env):
        if (k.startswith('GIT_CONFIG_KEY_') or k.startswith('GIT_CONFIG_VALUE_')
                or k in ('GIT_CONFIG_COUNT','GIT_CONFIG','GIT_DIR','GIT_WORK_TREE',
                    'GIT_INDEX_FILE','GIT_ALTERNATE_OBJECT_DIRECTORIES','GIT_OBJECT_DIRECTORY',
                    'GIT_REPLACE_REF_BASE','GIT_SHALLOW_FILE','GIT_COMMON_DIR')):
            env.pop(k,None)
    return env


def _git():
    executable=shutil.which('git')
    if not executable:raise ValueError('Local Git executable required')
    return [executable,'--no-replace-objects','-c','core.packedGitWindowSize=16m',
        '-c','core.packedGitLimit=64m','-c','core.deltaBaseCacheLimit=32m']


def _git_tree(repo, expected_commit):
    commit=_pin_commit(expected_commit);repo=_ordinary(repo)
    check=subprocess.run([*_git(),'cat-file','-t',commit],cwd=repo,env=_environment(),
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60)
    if check.returncode!=0 or check.stdout!=b'commit\n':
        raise ValueError('Pinned Git commit is absent or not a commit; no fetch attempted')
    result=subprocess.run([*_git(),'ls-tree','-r','-z','-l',commit,'--',*ALLOWED_PREFIXES],
        cwd=repo,env=_environment(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60)
    if result.returncode!=0 or len(result.stdout)>MAX_TREE_OUTPUT:
        raise ValueError('Bounded pinned Git tree listing failed')
    if result.stdout and not result.stdout.endswith(b'\0'):
        raise ValueError('Incomplete Git tree listing')
    tree={};total=0
    for row in result.stdout.split(b'\0'):
        if not row:continue
        try:
            metadata,raw_name=row.split(b'\t',1);mode,kind,oid,size=metadata.split()
            name=raw_name.decode('utf-8','strict');n=int(size)
        except (ValueError,UnicodeDecodeError) as exc:raise ValueError('Malformed Git tree entry') from exc
        _allowed_file(name)
        if (mode not in (b'100644',b'100755') or kind!=b'blob' or n<0
                or len(oid)!=40 or any(c not in b'0123456789abcdef' for c in oid)):
            raise ValueError('Only normal SHA-1 Git blob files are allowed')
        if name in tree:raise ValueError('Duplicate Git tree path')
        total+=n
        if len(tree)>=MAX_FILES or n>retained.MAX_PACKET_FILE_BYTES or total>MAX_TOTAL_BYTES:
            raise ValueError('Bounded original Git tree required')
        tree[name]=dict(oid=oid.decode(),size=n)
    if not tree or any(not any(k.startswith(prefix+'/') for k in tree) for prefix in ALLOWED_PREFIXES):
        raise ValueError('Every allowlisted packet must exist in the pinned Git tree')
    return dict(sorted(tree.items()))


def _check_manifest_pins(repo,commit,pins,tree):
    """Reject wrong caller pins before extracting hundreds of MiB."""
    for name,contract in sorted(retained.CATALOG.items()):
        path='docs/design-engine/'+name+'/manifest.json';entry=tree.get(path)
        if entry is None or entry['size']>16*1024*1024:
            raise ValueError('Bounded original Git packet manifest required: '+name)
        result=subprocess.run([*_git(),'cat-file','blob',entry['oid']],cwd=repo,env=_environment(),
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60)
        raw=result.stdout
        if result.returncode!=0 or len(raw)!=entry['size']:
            raise ValueError('Original Git packet manifest blob unavailable: '+name)
        git_hash=hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest()
        if git_hash!=entry['oid']:raise ValueError('Original Git packet manifest blob differs: '+name)
        value=retained._json(raw);key=contract[3]
        if (value.get('schema')!=contract[0] or value.get(key)!=pins[name]
                or retained._id({k:v for k,v in value.items() if k!=key})!=pins[name]):
            raise ValueError('Externally pinned original Git packet manifest differs: '+name)


def _preflight_archive(folder,pins,expected_archive_id):
    """Check the retained source archive before allocating the packet tree."""
    folder=_ordinary(folder);mh,raw,_=retained._file_data(folder/'manifest.json',16*1024*1024,materialize=True)
    value=retained._json(raw)
    if (set(value)!=retained.METADATA_KEYS or value.get('schema')!='osr-retained-multi-packet-source-epoch/1'
            or value.get('archive_id')!=expected_archive_id
            or retained._id({k:v for k,v in value.items() if k!='archive_id'})!=expected_archive_id
            or value.get('pinned_original_manifest_ids')!=pins
            or value.get('reference_candidate_id')!=retained.REFERENCE_CANDIDATE
            or value.get('reference_candidate_scope')!=retained.REFERENCE_SCOPE
            or any(value.get(k) is not False for k in (*retained.FLAGS,'numerical_reexecuted',
                'current_evaluator_admission','physical_equivalence_proven','configuration_adopted','selected_reference_changed'))):
        raise ValueError('Pinned retained source archive identity or disposition differs')
    ah,blob,_=retained._file_data(folder/'sources.tar.gz',retained.MAX_ARCHIVE_BYTES,materialize=True)
    if ah!=value.get('source_archive_sha256'):raise ValueError('Retained source archive bytes differ')
    retained._check_archive(blob,value['original_source_sha256'])
    if retained._file_data(folder/'manifest.json',16*1024*1024)[0]!=mh or retained._file_data(folder/'sources.tar.gz',retained.MAX_ARCHIVE_BYTES)[0]!=ah:
        raise ValueError('Retained source archive changed during preflight')
    return mh,ah


def _exact(stream,n):
    if n<0:raise ValueError('Negative archive read')
    out=[];left=n
    while left:
        b=stream.read(min(left,CHUNK))
        if not b:raise ValueError('Truncated Git archive')
        out.append(b);left-=len(b)
    return b''.join(out)


def _write_file(stream,root,name,size,oid):
    path=root/name;_allowed_file(name)
    # Parent directories must have appeared as ordinary allowlisted tar entries.
    parent=_ordinary(path.parent);base=_ordinary(root)
    if not parent.is_relative_to(base):raise ValueError('Archive parent escaped private root')
    h=hashlib.sha1();h.update(('blob '+str(size)+'\0').encode());left=size
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0),0o600)
    with os.fdopen(fd,'wb') as out:
        while left:
            data=_exact(stream,min(left,CHUNK));out.write(data);h.update(data);left-=len(data)
    if h.hexdigest()!=oid:raise ValueError('Extracted file differs from pinned Git blob: '+name)


def _extract_tar(stream, destination, tree, commit):
    """Parse bounded Git tar records, rejecting links/extensions/duplicates.

    Git emits one 52-byte global PAX commit comment, regular ustar files and
    directories for this exact pinned tree. Other PAX/GNU extensions are not
    needed and are rejected before any variable-sized metadata allocation.
    """
    _pin_commit(commit);root=_ordinary(destination);expected_dirs=set()
    for name in tree:
        _allowed_file(name)
        for parent in PurePosixPath(name).parents:
            if str(parent)!='.':expected_dirs.add(str(parent))
    seen_files=set();seen_dirs=set();global_seen=False;entry_count=0;total=0
    while True:
        header=_exact(stream,512);total+=512
        if total>MAX_RAW_TAR_BYTES:raise ValueError('Raw Git archive exceeds bound')
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
        entry_count+=1
        if entry_count>MAX_ENTRIES or entry.size<0:raise ValueError('Git tar entry budget exceeded')
        if entry.type==tarfile.XGLTYPE:
            wanted=('52 comment='+commit+'\n').encode()
            if global_seen or entry_count!=1 or entry.name!='pax_global_header' or entry.size!=len(wanted):
                raise ValueError('One bounded Git global commit header required')
            if _exact(stream,entry.size)!=wanted:raise ValueError('Git archive commit comment differs')
            pad=(-entry.size)%512
            if any(_exact(stream,pad)):raise ValueError('Nonzero Git tar metadata padding')
            total+=entry.size+pad;global_seen=True;continue
        if not global_seen:raise ValueError('Git archive commit header is missing')
        if entry.type not in (tarfile.REGTYPE,tarfile.AREGTYPE,tarfile.DIRTYPE):
            raise ValueError('Git tar links, special files and extensions are rejected')
        name=entry.name;_relative(name)
        if entry.isdir():
            if entry.size!=0 or name not in expected_dirs or name in seen_dirs or name in seen_files:
                raise ValueError('Unlisted or duplicate Git tar directory')
            path=root/name;_ordinary(path.parent)
            os.mkdir(path,0o700);seen_dirs.add(name);continue
        if name not in tree or name in seen_files or name in seen_dirs:
            raise ValueError('Unlisted or duplicate Git tar file')
        want=tree[name]
        if entry.size!=want['size'] or entry.size>retained.MAX_PACKET_FILE_BYTES:
            raise ValueError('Git tar file size differs from pinned tree')
        total+=entry.size+(-entry.size)%512
        if total>MAX_RAW_TAR_BYTES:raise ValueError('Raw Git archive exceeds bound')
        _write_file(stream,root,name,entry.size,want['oid'])
        if any(_exact(stream,(-entry.size)%512)):raise ValueError('Nonzero Git tar file padding')
        seen_files.add(name)
    if not global_seen or seen_files!=set(tree) or seen_dirs!=expected_dirs:
        raise ValueError('Git tar inventory does not reproduce all pinned tree paths')
    return dict(file_count=len(seen_files),directory_count=len(seen_dirs),
        blob_bytes=sum(row['size'] for row in tree.values()))


def _check_materialized(root,tree):
    """Check the entire private tree, including paths outside packet folders."""
    root=_ordinary(root);files=set();directories=set();expected_dirs=set();count=0;total=0
    for name in tree:
        for parent in PurePosixPath(name).parents:
            if str(parent)!='.':expected_dirs.add(str(parent))
    for path in root.rglob('*'):
        count+=1
        if count>MAX_ENTRIES:raise ValueError('Materialized tree entry budget exceeded')
        name=path.relative_to(root).as_posix();_relative(name);info=path.lstat()
        if stat.S_ISDIR(info.st_mode):directories.add(name)
        elif stat.S_ISREG(info.st_mode):
            files.add(name);total+=info.st_size
            if name not in tree or info.st_size!=tree[name]['size'] or total>MAX_TOTAL_BYTES:
                raise ValueError('Materialized tree has an unlisted or resized file')
        else:raise ValueError('Materialized tree contains a link or special file')
    if files!=set(tree) or directories!=expected_dirs:
        raise ValueError('Materialized tree inventory differs from pinned Git tree')


def materialize(repo,output,archive_directory,*,expected_commit,expected_manifests,expected_archive_id):
    """Build one fresh private historical tree and verify against external pins."""
    commit=_pin_commit(expected_commit);pins=retained._pins(expected_manifests);retained._hex(expected_archive_id)
    repo=_ordinary(repo);archive=_ordinary(archive_directory);out=Path(os.path.abspath(output));_ordinary(out.parent)
    if any(p.is_symlink() for p in (out,*out.parents)):raise ValueError('Symlink destination rejected')
    if (out==repo or out.is_relative_to(repo) or repo.is_relative_to(out)
            or out==archive or out.is_relative_to(archive) or archive.is_relative_to(out)):
        raise ValueError('Destination must be private and separate from all inputs')
    if out.exists():raise FileExistsError('Destination already exists: '+str(out))
    producer=hashlib.sha256(_ordinary(__file__,directory=False).read_bytes()).hexdigest()
    verifier=hashlib.sha256(_ordinary(retained.__file__,directory=False).read_bytes()).hexdigest()
    tree=_git_tree(repo,commit);_check_manifest_pins(repo,commit,pins,tree)
    archive_hashes=_preflight_archive(archive,pins,expected_archive_id)
    stage=Path(tempfile.mkdtemp(prefix='.retained-packets-stage-',dir=out.parent))
    root=stage/'root';root.mkdir(mode=0o700)
    # GNU timeout is a hard coordinator deadline; it is not filesystem or network isolation.
    timeout=shutil.which('timeout')
    if not timeout:raise ValueError('Local timeout executable required; private stage retained: '+str(stage))
    stderr_path=stage/'git-archive.stderr.log'
    with stderr_path.open('xb') as errors:
        child=subprocess.Popen([timeout,str(GIT_COMMAND_LIMIT_S),*_git(),'archive','--format=tar',commit,'--',*ALLOWED_PREFIXES],
            cwd=repo,env=_environment(),stdout=subprocess.PIPE,stderr=errors,bufsize=0,preexec_fn=_limit_git_log)
        try:
            details=_extract_tar(child.stdout,root,tree,commit)
            code=child.wait(timeout=10)
            if code!=0:raise ValueError('Local Git archive failed with exit '+str(code))
        finally:
            if child.poll() is None:child.kill();child.wait()
            child.stdout.close()
    if _git_tree(repo,commit)!=tree:raise ValueError('Pinned Git inventory changed; private stage retained: '+str(stage))
    _check_materialized(root,tree)
    verification=retained.verify(root,archive,expected_manifests=pins,expected_archive_id=expected_archive_id)
    if (_preflight_archive(archive,pins,expected_archive_id)!=archive_hashes):
        raise ValueError('Retained source archive changed; private stage retained: '+str(stage))
    if (hashlib.sha256(_ordinary(__file__,directory=False).read_bytes()).hexdigest()!=producer
            or hashlib.sha256(_ordinary(retained.__file__,directory=False).read_bytes()).hexdigest()!=verifier):
        raise ValueError('Materializer or archival verifier changed; private stage retained: '+str(stage))
    handoff=dict(schema='osr-retained-packet-materialization/1',original_commit=commit,
        expected_original_manifest_ids=pins,expected_archive_id=expected_archive_id,
        git_tree_sha256=retained._id(tree),git_tree_file_count=details['file_count'],
        git_tree_directory_count=details['directory_count'],git_blob_bytes=details['blob_bytes'],
        source_sha256={PRODUCER:producer,'engineering/design_search/retained_source_epoch.py':verifier},
        git_archive_stderr_sha256=retained._file_data(stderr_path,MAX_LOG_BYTES)[0],
        archive_verification=verification,scope='Original packet files reconstructed from pinned local Git blobs and checked against retained source archive; no current evaluator or physical acceptance',
        numerical_reexecuted=False,current_evaluator_admission=False,physical_equivalence_proven=False,
        configuration_adopted=False,selected_reference_changed=False,physical_accepted=False,
        engineering_accepted=False,manufacturing_release=False,operating_release=False,
        isolation='No filesystem or network sandbox; Git lazy fetch explicitly disabled')
    handoff['handoff_id']=retained._id(handoff)
    (stage/'handoff.json').write_bytes(retained._encoded(handoff))
    _check_materialized(root,tree)
    if (retained.verify(root,archive,expected_manifests=pins,expected_archive_id=expected_archive_id)!=verification
            or retained._file_data(stderr_path,MAX_LOG_BYTES)[0]!=handoff['git_archive_stderr_sha256']
            or hashlib.sha256(_ordinary(__file__,directory=False).read_bytes()).hexdigest()!=producer
            or hashlib.sha256(_ordinary(retained.__file__,directory=False).read_bytes()).hexdigest()!=verifier):
        raise ValueError('Evidence changed before handoff; private stage retained: '+str(stage))
    _check_materialized(root,tree)
    retained._rename_noreplace(stage,out)
    return handoff


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--git-repo',required=True,type=Path);parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--archive-directory',required=True,type=Path);parser.add_argument('--pins',required=True,type=Path)
    parser.add_argument('--expected-commit',required=True);parser.add_argument('--expected-archive-id',required=True)
    args=parser.parse_args();pins=retained._json(retained._file_data(args.pins,1024*1024,materialize=True)[1])
    result=materialize(args.git_repo,args.output,args.archive_directory,expected_commit=args.expected_commit,
        expected_manifests=pins,expected_archive_id=args.expected_archive_id)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=='__main__':main()
