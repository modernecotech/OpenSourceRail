#!/usr/bin/env python3
"""Publish a new run-bound wrapper around unchanged, reopened IFC evidence.

No IFC export or structural solver is invoked. Original IFC files, raw receipts
and their compressed archive are preserved byte for byte. The existing geometry
verifier can independently reopen the resulting publication afterward.
"""
import argparse
import gzip
import hashlib
import importlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PRODUCER = 'tools/automation/sourced-ifc-reuse.py'
ARCHIVE = 'revised-vehicles-ifc.tar.gz'
RECORD = 'revised-vehicles-ifc.json'
VEHICLES = tuple('V'+str(i) for i in range(1,6))
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    manufacturing_release=False, operating_release=False, selected_reference_changed=False)
CONTROL_FLAGS = {*FLAGS, 'configuration_adopted', 'physical_journey_completed',
    'complete_installed_geometry'}
MAX_JSON = 128*1024**2
MAX_ARCHIVE = 128*1024**2
MAX_RAW = 512*1024**2
BUFFER = 1024**2


def encoded(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def identity(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def _signature(value):
    return (value.st_dev,value.st_ino,value.st_size,value.st_mtime_ns,value.st_ctime_ns)


def _parents(path):
    path=Path(os.path.abspath(path))
    for item in reversed((path,*path.parents)):
        if item.is_symlink():raise ValueError('Unlinked ordinary paths required')
    return path


def _directory(path):
    path=_parents(path)
    if not path.is_dir():raise ValueError('Existing ordinary input directory required')
    return path


def _open(path, maximum):
    path=_parents(path)
    before=path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_size>maximum:
        raise ValueError('Bounded ordinary input required: '+str(path))
    fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
    stream=os.fdopen(fd,'rb')
    if _signature(os.fstat(stream.fileno()))!=_signature(before):
        stream.close();raise ValueError('Input changed while opening')
    return stream,before


def _unchanged(path, stream, before):
    if (_signature(os.fstat(stream.fileno()))!=_signature(before)
            or _signature(Path(path).lstat())!=_signature(before)):
        raise ValueError('Input changed during reading: '+str(path))


def digest(path, maximum=MAX_RAW):
    stream,before=_open(path,maximum);h=hashlib.sha256()
    with stream:
        for block in iter(lambda:stream.read(BUFFER),b''):h.update(block)
        _unchanged(path,stream,before)
    return h.hexdigest()


def read(path, maximum=MAX_JSON):
    stream,before=_open(path,maximum)
    with stream:
        if Path(path).suffix=='.gz':
            with gzip.GzipFile(fileobj=stream) as compressed:raw=compressed.read(maximum+1)
        else:raw=stream.read(maximum+1)
        if len(raw)>maximum:raise ValueError('JSON expansion budget exceeded')
        _unchanged(path,stream,before)
    return json.loads(raw)


def _unreleased(value):
    if isinstance(value,dict):
        for key,item in value.items():
            if key in CONTROL_FLAGS and item is not False:raise ValueError('Unsupported acceptance or release')
            _unreleased(item)
    elif isinstance(value,list):
        for item in value:_unreleased(item)


def _sealed(value,key):
    if not isinstance(value,dict) or value.get(key)!=identity({k:v for k,v in value.items() if k!=key}):
        raise ValueError('Invalid source record seal: '+key)
    if any(value.get(flag) is not False for flag in FLAGS):
        raise ValueError('Explicit unaccepted source disposition required')
    _unreleased(value)


def _hash(value):
    return isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value)


def _name(value):
    return (isinstance(value,str) and value and '\\' not in value
        and PurePosixPath(value).as_posix()==value and not PurePosixPath(value).is_absolute()
        and '..' not in PurePosixPath(value).parts)


def _sources(value, root=None):
    if (not isinstance(value,dict) or not value or len(value)>4096
            or any(not _name(k) or not _hash(v) for k,v in value.items())):
        raise ValueError('Canonical bounded source map required')
    if root is not None:
        for name,sha in value.items():
            if digest(Path(root)/name)!=sha:raise ValueError('Stale narrow source: '+name)


def _modules(root):
    if str(root) not in sys.path:sys.path.insert(0,str(root))
    names=('engineering.sourced_case.coordinator','engineering.sourced_case.geometry',
        'engineering.reference_cell.geometry')
    modules=tuple(importlib.import_module(name) for name in names)
    for name,module in zip(names,modules):
        if Path(module.__file__).resolve()!=root/(name.replace('.','/')+'.py'):
            raise ValueError('Executed geometry/coordinator source root differs')
    if digest(root/PRODUCER)!=digest(__file__):raise ValueError('Executed reuse producer source differs')
    return modules


def _consume_archive(path, expected, *, maximum_members, target=None):
    """Read ordinary short-name tar headers before allocating member contents.

    Reject PAX/GNU/sparse extensions and oversized sizes before tarfile can
    allocate an extension payload. Current source/IFC archives use plain ustar.
    """
    stream,before=_open(path,MAX_ARCHIVE);seen=set();total=0
    with stream,gzip.GzipFile(fileobj=stream) as raw:
        while True:
            header=raw.read(512)
            if len(header)!=512:raise ValueError('Truncated ordinary tar header')
            if header==bytes(512):
                trailer=raw.read(10240+1)
                if len(trailer)>10240 or any(trailer) or len(trailer)<512:
                    raise ValueError('Nonordinary or unbounded tar trailer')
                break
            member=tarfile.TarInfo.frombuf(header,'utf-8','strict')
            total+=member.size
            if (len(seen)>=maximum_members or member.type not in (tarfile.REGTYPE,tarfile.AREGTYPE)
                    or member.name not in expected or member.name in seen or not _name(member.name)
                    or member.size<0 or member.size>MAX_RAW or total>MAX_RAW):
                raise ValueError('Closed ordinary bounded archive required')
            destination=None if target is None else (target/member.name).open('xb')
            try:
                h=hashlib.sha256();remaining=member.size
                while remaining:
                    block=raw.read(min(remaining,BUFFER))
                    if not block:raise ValueError('Truncated archive member')
                    remaining-=len(block);h.update(block)
                    if destination is not None:destination.write(block)
                if h.hexdigest()!=expected[member.name]:raise ValueError('Original archive member bytes differ')
            finally:
                if destination is not None:destination.close()
            padding=raw.read((-member.size)%512)
            if len(padding)!=(-member.size)%512 or any(padding):raise ValueError('Nonordinary tar padding')
            seen.add(member.name)
        if seen!=set(expected):raise ValueError('Incomplete original archive')
        _unchanged(path,stream,before)


def _snapshot(path, epoch):
    """Authenticate original source bytes without executing archived producers."""
    _consume_archive(path,epoch,maximum_members=4096)


def _run(folder, plan):
    value=read(folder/'latest.json');_sealed(value,'run_id');_sources(value.get('source_sha256'))
    cases=value.get('cases');pending=value.get('pending')
    if (value.get('schema')!='osr-sourced-cell-run/1' or not isinstance(cases,list) or len(cases)!=30 or pending!=[]
            or sorted(identity(r.get('request')) for r in cases)!=sorted(map(identity,plan))):
        raise ValueError('Exact complete five-family thirty-case index required')
    for row in cases:
        req=row['request'];expected='cases/'+identity(dict(request=req,source=value['source_sha256']))+'.json.gz'
        if row.get('path')!=expected or not _hash(row.get('candidate_id')) or not _hash(row.get('evaluation_id')):
            raise ValueError('Mixed or noncanonical case index')
    _snapshot(folder/'input-sources.tar.gz',value['source_sha256'])
    return value


def _archive(path, record, target):
    expected={}
    for row in record['vehicles']:
        vid=row['vehicle_id'];files=row.get('files_sha256')
        if (not isinstance(files,dict) or set(files)!={vid+'.ifc',vid+'.ifc.receipt.json'}
                or any(not _hash(v) for v in files.values())):raise ValueError('Exact IFC/receipt pair required')
        expected.update(files)
    _consume_archive(path,expected,maximum_members=10,target=target)


def reuse(old_state,new_state,original_geometry,output,*,root=ROOT):
    """Reopen preserved evidence once per vehicle and emit a NEW outer record."""
    root=_directory(root);old_state=_directory(old_state);new_state=_directory(new_state)
    original_geometry=_directory(original_geometry);output=_parents(output)
    inputs=(old_state,new_state,original_geometry)
    if old_state==new_state or any(output==p or p in output.parents or output in p.parents for p in inputs):
        raise ValueError('Fresh disjoint output and distinct old/new states required')
    if output.exists() and not output.is_dir():raise ValueError('Ordinary output directory required')
    if any(os.path.lexists(output/name) for name in (ARCHIVE,RECORD)):
        raise ValueError('Geometry destinations already exist; preserve and choose a fresh output')
    coordinator,geometry,native=_modules(root)
    epoch=coordinator.sources(root);_sources(epoch)
    plan=coordinator.plan()
    if (len(plan)!=30 or len(set(map(identity,plan)))!=30
            or any(sum(r['vehicle_id']==vid for r in plan)!=6 for vid in VEHICLES)):
        raise ValueError('Exact declared thirty-case plan required')
    helper_sha=digest(__file__)
    record_path=original_geometry/RECORD;archive_path=original_geometry/ARCHIVE
    pinned={str(p):digest(p,MAX_ARCHIVE if p.suffix=='.gz' else MAX_JSON) for p in (
        record_path,archive_path,old_state/'latest.json',new_state/'latest.json',
        old_state/'input-sources.tar.gz',new_state/'input-sources.tar.gz')}
    old_run=_run(old_state,plan);new_run=_run(new_state,plan)
    if new_run['source_sha256']!=epoch:raise ValueError('New state source epoch is stale')
    if old_run['run_id']==new_run['run_id']:raise ValueError('Distinct new run identity required')
    old_candidates={identity(r['request']):r['candidate_id'] for r in old_run['cases']}
    if old_candidates!={identity(r['request']):r['candidate_id'] for r in new_run['cases']}:
        raise ValueError('Physical cell candidate identities changed')
    record_path=original_geometry/RECORD;archive_path=original_geometry/ARCHIVE
    original=read(record_path,4*1024**2);_sealed(original,'publication_id')
    if (original.get('schema')!='osr-sourced-vehicle-geometry/1'
            or original.get('run_id')!=old_run['run_id'] or original.get('source_sha256')!=old_run['source_sha256']
            or not isinstance(original.get('vehicles'),list) or len(original['vehicles'])!=5
            or sorted(r.get('vehicle_id') for r in original['vehicles'])!=list(VEHICLES)):
        raise ValueError('Original geometry/run provenance or coverage differs')
    archive_sha=digest(archive_path,MAX_ARCHIVE)
    if original.get('files_sha256')!={ARCHIVE:archive_sha}:raise ValueError('Original geometry archive digest differs')
    rows=[];ancestry=[]
    with tempfile.TemporaryDirectory(prefix='osr-preserved-ifc-reopen-') as scratch:
        scratch=Path(scratch);_archive(archive_path,original,scratch)
        for previous in sorted(original['vehicles'],key=lambda r:r['vehicle_id']):
            vid=previous['vehicle_id'];old_path=old_state/'vehicles'/(vid+'.json.gz');new_path=new_state/'vehicles'/(vid+'.json.gz')
            pinned[str(old_path)]=digest(old_path);pinned[str(new_path)]=digest(new_path)
            old_equipment=read(old_path);new_equipment=read(new_path)
            _sealed(old_equipment,'evaluation_id');_sealed(new_equipment,'evaluation_id')
            old=old_equipment['vehicle'];new=new_equipment['vehicle'];_sealed(old,'evaluation_id');_sealed(new,'evaluation_id')
            for value in (old,new):
                if (value.get('vehicle_id')!=vid or value.get('candidate_id')!=value.get('registry',{}).get('candidate_id')
                        or not _hash(value['registry'].get('registry_id'))):raise ValueError('Mixed vehicle/registry identity')
            _sources(new.get('source_sha256'),root)
            if (old['candidate_id']!=new['candidate_id'] or old['registry']['registry_id']!=new['registry']['registry_id']
                    or old['source_sha256']!=new['source_sha256'] or encoded(old)!=encoded(new)):
                raise ValueError('Old/new exact vehicle, registry or narrow source contract differs')
            if any(e.get('candidate_id')!=new['candidate_id'] for e in (old_equipment,new_equipment)):
                raise ValueError('Equipment and IFC vehicle candidates differ')
            if previous.get('candidate_id')!=new['candidate_id'] or previous.get('registry_id')!=new['registry']['registry_id']:
                raise ValueError('Original wrapper uses another vehicle/registry')
            raw_receipt=read(scratch/(vid+'.ifc.receipt.json'),4*1024**2);_sealed(raw_receipt,'receipt_id')
            if (raw_receipt.get('schema')!='osr-reference-cell-ifc/1' or raw_receipt.get('candidate_id')!=new['candidate_id'] or raw_receipt.get('registry_id')!=new['registry']['registry_id']
                    or raw_receipt.get('source_sha256')!=native._source(new) or raw_receipt.get('file')!=vid+'.ifc'
                    or raw_receipt.get('file_sha256')!=previous['files_sha256'][vid+'.ifc']
                    or raw_receipt.get('reopened')!=previous.get('reopened')):
                raise ValueError('Original raw IFC receipt contract differs')
            _sources(raw_receipt['source_sha256'],root)
            validation=native.verify_ifc(new,scratch/(vid+'.ifc'))
            _unreleased(validation)
            if (any(validation.get(flag) is not False for flag in FLAGS)
                    or validation.get('verified') is not True or validation.get('actual_reopened') is not True
                    or validation.get('candidate_id')!=new['candidate_id'] or validation.get('receipt_id')!=raw_receipt['receipt_id']
                    or validation.get('native_reuse_eligible') is not False):raise ValueError('Actual unreleased IFC reopening required')
            if any(digest(scratch/name)!=sha for name,sha in previous['files_sha256'].items()):
                raise ValueError('IFC reopening modified original extracted evidence')
            rows.append(dict(vehicle_id=vid,candidate_id=new['candidate_id'],registry_id=new['registry']['registry_id'],
                reopened=raw_receipt['reopened'],validation=validation,files_sha256=previous['files_sha256']))
            ancestry.append(dict(vehicle_id=vid,vehicle_evaluation_id=new['evaluation_id'],
                narrow_source_identity=identity(new['source_sha256']),raw_receipt_id=raw_receipt['receipt_id'],
                original_ifcopenshell_version=raw_receipt.get('ifcopenshell_version'),
                current_verifier_ifcopenshell_version=validation.get('current_verifier_ifcopenshell_version'),
                original_validation_identity=identity(previous['validation']),current_validation_identity=identity(validation),
                source_geometry_publication_id=original['publication_id']))
            del old_equipment,new_equipment,old,new
    if (coordinator.sources(root)!=epoch or digest(__file__)!=helper_sha
            or any(digest(Path(name))!=sha for name,sha in pinned.items())):
        raise ValueError('Input/source epoch changed during IFC reuse')
    value=dict(schema='osr-sourced-vehicle-geometry/1',run_id=new_run['run_id'],vehicles=rows,
        source_sha256=epoch,files_sha256={ARCHIVE:archive_sha},scope=original['scope'],
        reuse=dict(schema='osr-preserved-sourced-ifc-provenance/1',producer=PRODUCER,producer_sha256=helper_sha,
            original_publication_id=original['publication_id'],original_run_id=old_run['run_id'],
            original_geometry_record_sha256=pinned[str(record_path)],original_archive_sha256=archive_sha,
            original_source_identity=identity(old_run['source_sha256']),new_source_identity=identity(epoch),
            input_files_sha256=pinned,vehicles=ancestry,actual_IFC_reopen_count=5,
            IFC_export_executed=False,native_structural_solver_executed=False,
            original_archive_preserved_byte_for_byte=True,raw_receipts_modified=False,
            independent_geometry_verification_executed_by_this_call=False),complete_installed_geometry=False,**FLAGS)
    value['publication_id']=identity(value)
    output.mkdir(parents=True,exist_ok=True)
    with archive_path.open('rb') as source,(output/ARCHIVE).open('xb') as destination:
        shutil.copyfileobj(source,destination,BUFFER)
    if digest(output/ARCHIVE,MAX_ARCHIVE)!=archive_sha or digest(archive_path,MAX_ARCHIVE)!=archive_sha:
        raise ValueError('Preserved compressed archive copy differs')
    with (output/RECORD).open('xb') as destination:destination.write(encoded(value))
    return value


def verify(state,output,*,root=ROOT):
    """Separate independent reopening through the unchanged canonical verifier."""
    root=_directory(root);state=_directory(state);output=_directory(output)
    _,geometry,_=_modules(root)
    return geometry.verify(state,output,root=root)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
    command=sub.add_parser('reuse')
    for name in ('old_state','new_state','original_geometry','output'):command.add_argument(name,type=Path)
    command.add_argument('--root',type=Path,default=ROOT)
    command=sub.add_parser('verify');command.add_argument('state',type=Path);command.add_argument('output',type=Path)
    command.add_argument('--root',type=Path,default=ROOT)
    args=parser.parse_args(argv)
    try:
        result=(reuse(args.old_state,args.new_state,args.original_geometry,args.output,root=args.root)
            if args.action=='reuse' else verify(args.state,args.output,root=args.root))
    except (ValueError,OSError,EOFError,KeyError,TypeError,tarfile.TarError) as error:
        parser.exit(2,str(error)+'\n')
    print(json.dumps(result,sort_keys=True,indent=2));return 0


if __name__=='__main__':raise SystemExit(main())
