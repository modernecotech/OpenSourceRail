"""Prototype preservation of original railway research producer epochs.

The archive stores the *source bytes* named by pinned original publications.
Original packets stay in place and all their regular-file bytes are checked on
capture and verification. No solver is rerun, no current evaluator is admitted,
and matching physical IDs do not establish physical equivalence.
"""
from __future__ import annotations

import argparse
import ctypes
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import stat
import tarfile
import tempfile
import zlib

REFERENCE_CANDIDATE = '756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3'
REFERENCE_SCOPE = 'Declared project context only; archived packets retain their own candidates and identities'
# schema, source-map key, payload-map key, manifest identity key, optional
# disposition record (filename, schema, identity key). These are fixed
# structural contracts; the actual trusted manifest identities are caller pins.
CATALOG = {
 'v06-architecture': ('osr-architecture-publication/1','source_sha256','files_sha256','manifest_id',None),
 'civil-shape-mechanics': ('osr-civil-mechanics-publication/1','source_sha256','files_sha256','manifest_id',None),
 'civil-topology': ('osr-civil-topology-publication/1','source_sha256','files_sha256','manifest_id',('result.json','osr-civil-topology-portfolio/1','portfolio_id')),
 'civil-topology-revisions': ('osr-topology-revision-publication/1','source_sha256','files_sha256','manifest_id',('result.json','osr-topology-revision-portfolio/1','portfolio_id')),
 'flanged-span-study': ('osr-flanged-span-stage1-manifest/1','source_sha256','files_sha256','manifest_id',('result.json','osr-flanged-span-stage1-publication/1','publication_id')),
 'flanged-system-cost-study': ('osr-flanged-system-cost-publication/1','source_sha256','files_sha256','manifest_id',('result.json','osr-flanged-system-cost-publication-result/1','publication_id')),
 'matched-renewal-research': ('osr-matched-renewal-publication/1','source_sha256','files_sha256','manifest_id',('result.json','osr-matched-renewal-publication-result/1','publication_id')),
 'v06-adaptive-design': ('osr-adaptive-publication/1','source_sha256','files_sha256','manifest_id',None),
 'generative-structure': ('osr-generative-structure-publication/1','source_sha256','files_sha256','manifest_id',None),
 'coupled-railway': ('osr-coupled-railway-publication/1','source_sha256','files_sha256','manifest_id',None),
 'railway-closure': ('osr-end-to-end-railway-closure-publication/1','sources','files','publication_id',None),
 'practical-launch': ('osr-practical-launch-publication/1','source_sha256','files_sha256','manifest_id',None),
 'propulsion-layout': ('osr-propulsion-layout-publication/1','source_sha256','files_sha256','manifest_id',None),
 'station-accelerators': ('osr-station-accelerator-publication/1','sources_sha256','files_sha256','manifest_id',None),
 'breadth-first-shape-portfolio': ('osr-breadth-first-shape-portfolio-publication/1','source_sha256','files_sha256','manifest_id',('result.json','osr-breadth-first-shape-portfolio/1','portfolio_id')),
}
FLAGS = ('physical_accepted','engineering_accepted','manufacturing_release','operating_release')
METADATA_KEYS = frozenset(('schema','reference_candidate_id','reference_candidate_scope',
    'capture_producer_sha256','pinned_original_manifest_ids','packets','original_source_sha256',
    'source_archive_sha256','scope','numerical_reexecuted','current_evaluator_admission',
    'physical_equivalence_proven','configuration_adopted','selected_reference_changed',
    *FLAGS,'archive_id'))
MAX_SOURCES = 4096
MAX_PACKET_ENTRIES = 10000
MAX_PACKET_BYTES = 512 * 1024 * 1024
MAX_TOTAL_PACKET_FILES = 100000
MAX_TOTAL_PACKET_BYTES = 1024 * 1024 * 1024
MAX_SOURCE_BYTES = 128 * 1024 * 1024
MAX_PACKET_FILE_BYTES = 512 * 1024 * 1024
MAX_ARCHIVE_BYTES = 160 * 1024 * 1024
# Bound tar headers/PAX metadata and 10 KiB record padding separately from
# payload bytes. This is an explicit resource bound, not a filesystem sandbox.
MAX_TAR_BYTES = MAX_SOURCE_BYTES + MAX_SOURCES * 8192 + 10240


def _encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def _id(value):
    return hashlib.sha256(_encoded(value)).hexdigest()


def _path(name):
    if not isinstance(name,str) or not name or '\\' in name:
        raise ValueError('Ordinary relative POSIX path required')
    p=PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or str(p)!=name:
        raise ValueError('Ordinary relative POSIX path required: '+name)
    return p


def _ordinary(path, *, directory=False):
    path=Path(os.path.abspath(path))
    if any(p.is_symlink() for p in (path,*path.parents)):
        raise ValueError('Symlink path or ancestor rejected')
    mode=path.lstat().st_mode
    if not (stat.S_ISDIR(mode) if directory else stat.S_ISREG(mode)):
        raise ValueError('Ordinary directory or regular file required')
    return path


def _file_data(path, limit=MAX_PACKET_FILE_BYTES, *, materialize=False):
    path=_ordinary(path); before=path.lstat()
    if before.st_size>limit:raise ValueError('File exceeds declared resource limit')
    signature=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    fd=os.open(path, os.O_RDONLY|getattr(os,'O_NOFOLLOW',0));h=hashlib.sha256();chunks=[];total=0
    with os.fdopen(fd,'rb') as stream:
        if signature(before)!=signature(os.fstat(stream.fileno())):raise ValueError('Input changed before read')
        while True:
            chunk=stream.read(1024*1024)
            if not chunk:break
            total+=len(chunk)
            if total>limit:raise ValueError('Input exceeds declared resource limit')
            h.update(chunk)
            if materialize:chunks.append(chunk)
        if signature(before)!=signature(os.fstat(stream.fileno())) or signature(before)!=signature(path.lstat()):
            raise ValueError('Input changed during read')
    return h.hexdigest(),b''.join(chunks) if materialize else None,total


def _json(data):
    def pairs(items):
        out={}
        for k,v in items:
            if k in out:raise ValueError('Duplicate JSON key')
            out[k]=v
        return out
    try: value=json.loads(data,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))
    except (UnicodeDecodeError,json.JSONDecodeError) as exc:raise ValueError('Invalid JSON') from exc
    if not isinstance(value,dict):raise ValueError('JSON object required')
    return value


def _hex(value):
    if not isinstance(value,str) or len(value)!=64 or any(c not in '0123456789abcdef' for c in value):
        raise ValueError('External SHA-256 pin required')
    return value


def _pins(pins):
    if not isinstance(pins,dict) or set(pins)!=set(CATALOG):
        raise ValueError('Explicit external pins for the entire packet catalog required')
    return {k:_hex(v) for k,v in sorted(pins.items())}


def _checked_map(mapping):
    if not isinstance(mapping,dict) or not mapping or len(mapping)>10000:
        raise ValueError('Bounded nonempty source/payload map required')
    for name,wanted in mapping.items():_path(name);_hex(wanted)
    return mapping


def _inventory(folder):
    folder=_ordinary(folder,directory=True);out={};entries=0;total_bytes=0
    for p in folder.rglob('*'):
        entries+=1
        if entries>MAX_PACKET_ENTRIES:raise ValueError('Packet entry count exceeds limit')
        name=p.relative_to(folder).as_posix();_path(name)
        info=p.lstat();mode=info.st_mode
        if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
            raise ValueError('Only ordinary packet files and directories allowed')
        if stat.S_ISREG(mode) and name!='manifest.json':
            total_bytes+=info.st_size
            if total_bytes>MAX_PACKET_BYTES:raise ValueError('Packet file bytes exceed limit')
            out[name]=_file_data(p)[0]
    return dict(sorted(out.items())),entries,total_bytes


def _records(root, pins):
    root=_ordinary(root,directory=True);pins=_pins(pins); records={};sources={};entry_total=0;byte_total=0
    for name,contract in sorted(CATALOG.items()):
        _path(name);schema,sk,pk,ik,disposition=contract;folder=root/'docs/design-engine'/name
        _ordinary(folder,directory=True);path=folder/'manifest.json';mh,raw,_=_file_data(path,16*1024*1024,materialize=True);m=_json(raw)
        if m.get('schema')!=schema or m.get(ik)!=pins[name] or _id({k:v for k,v in m.items() if k!=ik})!=pins[name]:
            raise ValueError('Externally pinned packet identity differs: '+name)
        src=_checked_map(m.get(sk));declared=_checked_map(m.get(pk));actual,entries,packet_bytes=_inventory(folder)
        entry_total+=entries;byte_total+=packet_bytes
        if entry_total>MAX_TOTAL_PACKET_FILES or byte_total>MAX_TOTAL_PACKET_BYTES:
            raise ValueError('Total packet inventory exceeds limit')
        if any(actual.get(k)!=v for k,v in declared.items()):raise ValueError('Declared packet payload differs: '+name)
        disp=m
        if disposition:
            filename,expected_schema,key=disposition
            if filename not in declared:raise ValueError('Disposition is not in declared payload')
            _,blob,_=_file_data(folder/filename,16*1024*1024,materialize=True);disp=_json(blob)
            if disp.get('schema')!=expected_schema or disp.get(key)!=_id({k:v for k,v in disp.items() if k!=key}):
                raise ValueError('Disposition identity differs: '+name)
        if any(disp.get(k) is not False or (k in m and m[k] is not False) for k in FLAGS):
            raise ValueError('Historical packet cannot grant physical or engineering release')
        if any(k in r and r[k] is not False for r in (m,disp) for k in ('configuration_adopted','selected_reference_changed')):
            raise ValueError('Historical packet cannot promote a candidate')
        for key,value in src.items():
            if key in sources and sources[key]!=value:raise ValueError('Conflicting original source epochs: '+key)
            sources[key]=value
        records[name]=dict(manifest_id=pins[name],manifest_sha256=mh,declared_payload_sha256=dict(sorted(declared.items())),
            all_payload_sha256=actual,undeclared_files=sorted(set(actual)-set(declared)))
    if len(sources)>MAX_SOURCES:raise ValueError('Original source inventory exceeds limit')
    return records,dict(sorted(sources.items()))


def _tar_entry(name, size):
    entry=tarfile.TarInfo(name);entry.size=size;entry.mode=0o644;entry.mtime=0
    entry.uid=0;entry.gid=0;entry.uname='';entry.gname=''
    return entry


def _make_archive(root, sources):
    buffer=io.BytesIO();total=0
    with gzip.GzipFile(fileobj=buffer,mode='wb',filename='',mtime=0,compresslevel=6) as gz:
        with tarfile.open(fileobj=gz,mode='w|',format=tarfile.PAX_FORMAT) as tar:
            for name,wanted in sorted(sources.items()):
                _path(name);h,raw,n=_file_data(Path(root)/name,MAX_SOURCE_BYTES,materialize=True);total+=n
                if h!=wanted:raise ValueError('Original source bytes differ: '+name)
                if total>MAX_SOURCE_BYTES:raise ValueError('Source archive exceeds expanded bound')
                tar.addfile(_tar_entry(name,n),io.BytesIO(raw))
    result=buffer.getvalue()
    if len(result)>MAX_ARCHIVE_BYTES:raise ValueError('Compressed source archive exceeds bound')
    return result


def _check_archive(raw,sources):
    if len(raw)>MAX_ARCHIVE_BYTES:raise ValueError('Compressed source archive exceeds bound')
    # gzip.decompress() permits concatenated members; tarfile iteration stops at
    # the first tar end marker. Check the gzip boundary explicitly, then check
    # every decompressed tar byte against the one canonical representation.
    if raw[:10] != b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\xff':
        raise ValueError('Canonical gzip header required')
    try:
        decompressor=zlib.decompressobj(wbits=31)
        expanded=decompressor.decompress(raw,MAX_TAR_BYTES+1)
        if (len(expanded)>MAX_TAR_BYTES or not decompressor.eof
                or decompressor.unconsumed_tail or decompressor.unused_data):
            raise ValueError('One bounded gzip member with no trailing data required')
        found={};total=0;canonical=io.BytesIO()
        with tarfile.open(fileobj=io.BytesIO(expanded),mode='r:') as tar:
            with tarfile.open(fileobj=canonical,mode='w|',format=tarfile.PAX_FORMAT) as rebuilt:
                for item in tar:
                    _path(item.name)
                    if not item.isfile() or item.name in found or item.size<0:raise ValueError('Unique regular archive members required')
                    total+=item.size
                    if len(found)>=MAX_SOURCES or total>MAX_SOURCE_BYTES:raise ValueError('Expanded source archive exceeds bound')
                    content=tar.extractfile(item).read(item.size+1)
                    if len(content)!=item.size:raise ValueError('Truncated tar member')
                    found[item.name]=hashlib.sha256(content).hexdigest()
                    rebuilt.addfile(_tar_entry(item.name,item.size),io.BytesIO(content))
        if found!=sources:raise ValueError('Archive membership or source bytes differ')
        if list(found)!=sorted(sources) or canonical.getvalue()!=expanded:
            raise ValueError('Canonical tar member order and complete end padding required')
    except (tarfile.TarError,EOFError,OSError,zlib.error) as exc:raise ValueError('Invalid compressed source archive') from exc


def _rename_noreplace(source,destination):
    """Atomically hand off a directory on Linux without replacing any path."""
    libc=ctypes.CDLL(None,use_errno=True)
    try:rename=libc.renameat2
    except AttributeError as exc:raise OSError('Atomic no-replace rename unavailable') from exc
    rename.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint]
    rename.restype=ctypes.c_int
    if rename(-100,os.fsencode(source),-100,os.fsencode(destination),1)!=0:
        error=ctypes.get_errno();raise OSError(error,os.strerror(error),str(destination))


def capture(root, output, *, expected_manifests):
    """Write fresh private source archive; caller supplies all trusted packet IDs."""
    root=_ordinary(root,directory=True);out=Path(os.path.abspath(output));_ordinary(out.parent,directory=True)
    if any(p.is_symlink() for p in (out,*out.parents)):raise ValueError('Symlink output rejected')
    if out==root or out.is_relative_to(root):
        raise ValueError('Private archive output must be outside the source tree')
    if out.exists():raise FileExistsError('Private archive output already exists: '+str(out))
    producer_before=_file_data(__file__,16*1024*1024)[0]
    pins=_pins(expected_manifests);records,sources=_records(root,pins);archive=_make_archive(root,sources);_check_archive(archive,sources)
    if _records(root,pins)!=(records,sources):raise ValueError('Original packet inputs changed during capture')
    meta=dict(schema='osr-retained-multi-packet-source-epoch/1',reference_candidate_id=REFERENCE_CANDIDATE,
        reference_candidate_scope=REFERENCE_SCOPE,
        capture_producer_sha256=producer_before,
        pinned_original_manifest_ids=pins,packets=records,original_source_sha256=sources,
        source_archive_sha256=hashlib.sha256(archive).hexdigest(),
        scope='Historical original source bytes and packet file integrity only; packet files remain in their original locations; no solver replay or current-evaluator admission',
        numerical_reexecuted=False,current_evaluator_admission=False,physical_equivalence_proven=False,
        configuration_adopted=False,selected_reference_changed=False,
        physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False)
    meta['archive_id']=_id(meta)
    stage=Path(tempfile.mkdtemp(prefix='.retained-source-stage-',dir=out.parent))
    # A failed stage is intentionally left in place for inspection; no cleanup
    # deletes potentially concurrent user data, and it is never a final packet.
    with (stage/'sources.tar.gz').open('xb') as f:f.write(archive)
    with (stage/'manifest.json').open('xb') as f:f.write(_encoded(meta))
    if _records(root,pins)!=(records,sources) or _file_data(__file__,16*1024*1024)[0]!=producer_before:
        raise ValueError('Original inputs or capture producer changed during write; private stage retained: '+str(stage))
    _rename_noreplace(stage,out)
    return meta


def verify(root, archive_directory, *, expected_manifests, expected_archive_id):
    """Verify old packet/source bytes without comparing old sources to current files."""
    root=_ordinary(root,directory=True);folder=_ordinary(archive_directory,directory=True);pins=_pins(expected_manifests);_hex(expected_archive_id)
    verifier_before=_file_data(__file__,16*1024*1024)[0]
    if {p.name for p in folder.iterdir()}!={'manifest.json','sources.tar.gz'}:
        raise ValueError('Exact retained archive file inventory required')
    _,raw,_=_file_data(folder/'manifest.json',16*1024*1024,materialize=True);m=_json(raw)
    if (set(m)!=METADATA_KEYS or m.get('schema')!='osr-retained-multi-packet-source-epoch/1' or m.get('archive_id')!=expected_archive_id
            or _id({k:v for k,v in m.items() if k!='archive_id'})!=expected_archive_id
            or m.get('pinned_original_manifest_ids')!=pins or m.get('reference_candidate_id')!=REFERENCE_CANDIDATE
            or m.get('reference_candidate_scope')!=REFERENCE_SCOPE
            or any(m.get(k) is not False for k in (*FLAGS,'numerical_reexecuted','current_evaluator_admission','physical_equivalence_proven','configuration_adopted','selected_reference_changed'))):
        raise ValueError('Pinned archive identity or historical disposition differs')
    _hex(m.get('capture_producer_sha256'))
    records,sources=_records(root,pins)
    if records!=m.get('packets') or sources!=m.get('original_source_sha256'):
        raise ValueError('Original packet files or source relationships differ')
    ah,archive,_=_file_data(folder/'sources.tar.gz',MAX_ARCHIVE_BYTES,materialize=True)
    if ah!=m.get('source_archive_sha256'):raise ValueError('Source archive digest differs')
    _check_archive(archive,sources)
    if (_records(root,pins)!=(records,sources) or _file_data(folder/'manifest.json',16*1024*1024)[0]!=hashlib.sha256(raw).hexdigest()
            or _file_data(folder/'sources.tar.gz',MAX_ARCHIVE_BYTES)[0]!=ah or _file_data(__file__,16*1024*1024)[0]!=verifier_before):
        raise ValueError('Retained evidence changed during verification')
    return dict(verified=True,archive_id=expected_archive_id,packet_count=len(records),source_count=len(sources),
        capture_producer_sha256=m['capture_producer_sha256'],verifier_producer_sha256=verifier_before,
        numerical_reexecuted=False,current_evaluator_admission=False,physical_equivalence_proven=False,
        configuration_adopted=False,selected_reference_changed=False,
        physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('capture','verify'))
    parser.add_argument('--root',required=True,type=Path);parser.add_argument('--archive-directory',required=True,type=Path)
    parser.add_argument('--pins',required=True,type=Path);parser.add_argument('--expected-archive-id')
    args=parser.parse_args();pins=_json(_file_data(args.pins,1024*1024,materialize=True)[1])
    if args.action=='capture':value=capture(args.root,args.archive_directory,expected_manifests=pins)
    else:
        if not args.expected_archive_id:parser.error('verify requires --expected-archive-id')
        value=verify(args.root,args.archive_directory,expected_manifests=pins,expected_archive_id=args.expected_archive_id)
    print(json.dumps(value,indent=2,sort_keys=True))


if __name__=='__main__':main()
