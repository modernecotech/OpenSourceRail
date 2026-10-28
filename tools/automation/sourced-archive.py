#!/usr/bin/env python3
"""Portable bounded transport for an unchanged source-bound publication archive.

Hashes authenticate bytes against the original publication manifest. This is not
an engineering acceptance or a substitute for the original semantic verifier.
"""
import argparse
from contextlib import contextmanager
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import stat
import tempfile

ARCHIVE='sourced-cell.tar.gz'
MANIFEST='manifest.json'
STORAGE='storage.json'
PREFIX='sourced-cell.part-'
SCHEMA='osr-sourced-cell-chunk-storage/1'
CHUNK_BYTES=24*1024**2
MAX_CHUNKS=8
MAX_TOTAL=192*1024**2
MAX_JSON=4*1024**2
BUFFER=1024**2
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
           operating_release=False,selected_reference_changed=False)


def encoded(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def identity(value):return sha256(encoded(value)).hexdigest()


def _hash(value):return isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None


def _integer(value,low,high):return type(value) is int and low<=value<=high


def _folder(folder):
    p=Path(os.path.abspath(os.fspath(folder)))
    for parent in reversed((p,*p.parents)):
        if parent.is_symlink():raise ValueError('Symlink publication directory/ancestor refused')
        if not parent.is_dir():raise ValueError('Existing ordinary publication directory required')
    return p


def _signature(s):return (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)


@contextmanager
def _open(path,max_size):
    try:before=path.lstat()
    except FileNotFoundError:raise ValueError('Missing publication file: '+path.name) from None
    if not stat.S_ISREG(before.st_mode) or before.st_size>max_size:raise ValueError('Bounded ordinary file required: '+path.name)
    fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
    with os.fdopen(fd,'rb') as stream:
        actual=os.fstat(stream.fileno())
        if not stat.S_ISREG(actual.st_mode) or _signature(before)!=_signature(actual):raise ValueError('Publication file changed during opening')
        yield stream,actual.st_size
        if _signature(actual)!=_signature(os.fstat(stream.fileno())) or _signature(actual)!=_signature(path.lstat()):
            raise ValueError('Publication file changed during reading')


def _pairs(pairs):
    value={}
    for key,item in pairs:
        if key in value:raise ValueError('Duplicate JSON key')
        value[key]=item
    return value


def _json(path):
    with _open(path,MAX_JSON) as (stream,size):raw=stream.read(MAX_JSON+1)
    try:value=json.loads(raw,object_pairs_hook=_pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('Nonfinite JSON value')))
    except (json.JSONDecodeError,UnicodeDecodeError) as exc:raise ValueError('Malformed publication JSON') from exc
    if not isinstance(value,dict):raise ValueError('JSON object required')
    return value,sha256(raw).hexdigest()


def _unaccepted(value):
    if isinstance(value,dict):
        for key,item in value.items():
            if key in FLAGS or key in ('physical_journey_completed','configuration_adopted','physical_release','design_complete'):
                if item is not False:raise ValueError('Transport cannot grant acceptance')
            _unaccepted(item)
    elif isinstance(value,list):
        for item in value:_unaccepted(item)


def _manifest(folder):
    value,raw_sha=_json(folder/MANIFEST);_unaccepted(value)
    if value.get('schema')!='osr-sourced-cell-publication/1' or not _hash(value.get('publication_id')):
        raise ValueError('Original sourced publication manifest required')
    if value['publication_id']!=identity({k:v for k,v in value.items() if k!='publication_id'}):raise ValueError('Original publication identity differs')
    hashes=value.get('files_sha256')
    if not isinstance(hashes,dict) or not _hash(hashes.get(ARCHIVE)):raise ValueError('Original manifest must bind full archive SHA256')
    return value,raw_sha,hashes[ARCHIVE]


def _reserved(folder):
    return {p.name for p in folder.iterdir() if p.name.startswith(PREFIX)}


def _descriptor(folder):
    d,_=_json(folder/STORAGE)
    expected={'schema','archive_path','archive_sha256','total_bytes','chunk_bytes','chunks',
       'publication_manifest_sha256','publication_id','storage_id',*FLAGS}
    if set(d)!=expected or d.get('schema')!=SCHEMA or d.get('archive_path')!=ARCHIVE:raise ValueError('Exact storage schema required')
    if not _hash(d['storage_id']) or d['storage_id']!=identity({k:v for k,v in d.items() if k!='storage_id'}):raise ValueError('Storage identity differs')
    if any(d[k] is not False for k in FLAGS):raise ValueError('Storage release flags must remain false')
    if not _integer(d['total_bytes'],1,MAX_TOTAL) or not _integer(d['chunk_bytes'],1,CHUNK_BYTES):raise ValueError('Storage size budget exceeded')
    if not _hash(d['archive_sha256']) or not _hash(d['publication_manifest_sha256']) or not _hash(d['publication_id']):raise ValueError('Canonical storage hashes required')
    chunks=d['chunks']
    if not isinstance(chunks,list) or not 1<=len(chunks)<=MAX_CHUNKS:raise ValueError('One to eight bounded chunks required')
    if len(chunks)!=(d['total_bytes']+d['chunk_bytes']-1)//d['chunk_bytes']:raise ValueError('Chunk count/total size differ')
    names=[]
    for n,c in enumerate(chunks):
        if not isinstance(c,dict) or set(c)!={'path','bytes','sha256'} or c['path']!=f'{PREFIX}{n:03d}':raise ValueError('Canonical ordered chunk paths required')
        expected_size=min(d['chunk_bytes'],d['total_bytes']-n*d['chunk_bytes'])
        if not _integer(c['bytes'],1,CHUNK_BYTES) or c['bytes']!=expected_size or not _hash(c['sha256']):raise ValueError('Chunk size/hash contract differs')
        names.append(c['path'])
    if _reserved(folder)!=set(names):raise ValueError('Exact closed chunk inventory differs')
    manifest,raw_sha,archive_sha=_manifest(folder)
    if d['publication_manifest_sha256']!=raw_sha or d['publication_id']!=manifest['publication_id'] or d['archive_sha256']!=archive_sha:
        raise ValueError('Storage rebound from original publication manifest')
    return d


def _chunks(folder,d,output=None):
    combined=sha256();total=0
    for c in d['chunks']:
        h=sha256();count=0
        with _open(folder/c['path'],CHUNK_BYTES) as (stream,size):
            if size!=c['bytes']:raise ValueError('Chunk length differs')
            while block:=stream.read(BUFFER):
                count+=len(block);total+=len(block);h.update(block);combined.update(block)
                if output is not None:output.write(block)
        if count!=c['bytes'] or h.hexdigest()!=c['sha256']:raise ValueError('Chunk hash differs')
    if total!=d['total_bytes'] or combined.hexdigest()!=d['archive_sha256']:raise ValueError('Combined archive hash/size differs')


def _digest(path,max_size):
    h=sha256()
    with _open(path,max_size) as (stream,size):
        while block:=stream.read(BUFFER):h.update(block)
    return h.hexdigest(),size


def _atomic(folder,name,writer):
    fd,temp=tempfile.mkstemp(prefix='.sourced-archive-',suffix='.tmp',dir=folder)
    try:
        with os.fdopen(fd,'wb') as stream:
            writer(stream);stream.flush();os.fsync(stream.fileno())
        os.chmod(temp,0o644)
        destination=folder/name
        if destination.is_symlink() or destination.exists() and not destination.is_file():raise ValueError('Ordinary destination required')
        os.replace(temp,destination)
    finally:
        if os.path.lexists(temp):os.unlink(temp)


def split(folder,*,chunk_bytes=CHUNK_BYTES):
    """Write bounded transport chunks; retain the original full local archive."""
    folder=_folder(folder)
    if not _integer(chunk_bytes,1,CHUNK_BYTES):raise ValueError('Chunk budget must be1..24MiB')
    manifest,raw_sha,expected=_manifest(folder)
    archive_sha,size=_digest(folder/ARCHIVE,MAX_TOTAL)
    if size<1 or archive_sha!=expected:raise ValueError('Full archive differs from original manifest')
    count=(size+chunk_bytes-1)//chunk_bytes
    if not 1<=count<=MAX_CHUNKS:raise ValueError('Archive requires more than eight bounded chunks')
    names={f'{PREFIX}{n:03d}' for n in range(count)}
    if _reserved(folder)-names:raise ValueError('Stale/extra chunks must be reviewed before splitting')
    # Reject malformed destinations before any output mutation.
    for name in names|{STORAGE}:
        p=folder/name
        if p.is_symlink() or p.exists() and not p.is_file():raise ValueError('Ordinary chunk/descriptor destination required')
    chunks=[];full=sha256()
    with _open(folder/ARCHIVE,MAX_TOTAL) as (stream,total):
        for n in range(count):
            block=stream.read(chunk_bytes)
            if not block:raise ValueError('Archive changed during splitting')
            full.update(block);name=f'{PREFIX}{n:03d}'
            _atomic(folder,name,lambda out,data=block:out.write(data))
            chunks.append(dict(path=name,bytes=len(block),sha256=sha256(block).hexdigest()))
        if stream.read(1):raise ValueError('Archive grew during splitting')
    if full.hexdigest()!=expected:raise ValueError('Archive changed during splitting')
    d=dict(schema=SCHEMA,archive_path=ARCHIVE,archive_sha256=expected,total_bytes=size,
       chunk_bytes=chunk_bytes,chunks=chunks,publication_manifest_sha256=raw_sha,publication_id=manifest['publication_id'],**FLAGS)
    d['storage_id']=identity(d);_atomic(folder,STORAGE,lambda out:out.write(encoded(d)))
    _chunks(folder,_descriptor(folder))
    return dict(action='split',storage_id=d['storage_id'],archive_sha256=expected,total_bytes=size,chunks=len(chunks),original_archive_retained=True,**FLAGS)


def ensure(folder):
    """Strictly verify chunks and atomically restore the original full bytes."""
    folder=_folder(folder);storage=folder/STORAGE
    if not os.path.lexists(storage):return dict(action='no-storage',reconstructed=False,**FLAGS)
    d=_descriptor(folder);_chunks(folder,d) # Verify even when the local cache is good.
    archive=folder/ARCHIVE;matches=False
    if os.path.lexists(archive):
        if archive.is_symlink() or not archive.is_file():raise ValueError('Ordinary archive cache required')
        if archive.stat().st_size<=MAX_TOTAL:
            h,size=_digest(archive,MAX_TOTAL);matches=h==d['archive_sha256'] and size==d['total_bytes']
    if not matches:
        # Reverify while writing; a failure preserves any previous cache.
        _atomic(folder,ARCHIVE,lambda out:_chunks(folder,d,out))
        h,size=_digest(archive,MAX_TOTAL)
        if h!=d['archive_sha256'] or size!=d['total_bytes']:raise ValueError('Reconstructed archive differs')
    return dict(action='ensure',storage_id=d['storage_id'],archive_sha256=d['archive_sha256'],
       total_bytes=d['total_bytes'],chunks=len(d['chunks']),reconstructed=not matches,**FLAGS)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=('split','ensure'));parser.add_argument('folder',type=Path)
    args=parser.parse_args(argv)
    try:result=split(args.folder) if args.command=='split' else ensure(args.folder)
    except (ValueError,OSError) as exc:parser.exit(2,'sourced archive: '+str(exc)+'\n')
    print(encoded(result).decode(),end='');return 0


if __name__=='__main__':raise SystemExit(main())
