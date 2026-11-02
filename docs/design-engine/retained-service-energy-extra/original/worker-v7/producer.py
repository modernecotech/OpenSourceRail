"""Retain the additional service-energy source epoch as historical evidence.

The original packet trees are external and must remain available at verify
time. No solver is replayed and no current evaluator or physical admission is
granted. The physical-followup wrapper's older producer epoch stays separate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile

from . import retained_source_epoch as retained

GIT_COMMIT = '5cd6b8ff9b2fdf3c705f0d68073543c58e6dec76'
REFERENCE = '756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3'
SELECTION = '8e5905bc7c81d6177bbaafde81ab3a5f8cc54947c4923eb4493949566ac85cdc'
PREFIX = 'docs/design-engine/'
STORAGE = PREFIX + 'sourced-case/storage.json'
COMPANION = PREFIX + 'v06-physical-closure/manifest.json'
# Exact manifest path -> schema, identity key, source key, payload form.
CATALOG = {
 'conditional-journey-study/manifest.json': ('osr-conditional-journey-publication/2','manifest_id','source_sha256','files'),
 'periodic-thermal-research/manifest.json': ('osr-periodic-thermal-publication/1','manifest_id','source_sha256','files'),
 'mass-reconciliation/current/manifest.json': ('osr-v06-mass-reconciliation-publication/1','manifest_id','source_sha256','files'),
 'mass-reserve-sensitivity/current/manifest.json': ('osr-current-mass-reserve-sensitivity-manifest/2','manifest_id','source_sha256','files'),
 'installed-mass-support/manifest.json': ('osr-installed-mass-support-publication/1','manifest_id','source_sha256','files'),
 'digital-twin/manifest.json': ('osr-end-to-end-twin-publication/1','publication_id','source_sha256','files'),
 'reference-cell/manifest.json': ('osr-reference-cell-publication/1','publication_id','source_sha256','files'),
 'continuing-cell/manifest.json': ('osr-continuing-cell-publication/1','publication_id','source_sha256','files'),
 'sourced-case/manifest.json': ('osr-sourced-cell-publication/1','publication_id','source_sha256','files'),
 'current-mesh-preflight/manifest.json': ('osr-current-mesh-preflight-manifest/1','manifest_id','source_sha256','files'),
 'engineering-closure/manifest.json': ('osr-current-engineering-closure-publication/1','publication_id','source_sha256','archive'),
 'engineering-closure/motor-manifest.json': ('osr-current-motor-experiment-publication/1','publication_id','source_sha256','archive'),
 'engineering-closure/variant-design-manifest.json': ('osr-coupled-wayside-variant-publication/1','publication_id','source_sha256','files'),
 'retained-physical-followup-source-epoch/manifest.json': ('osr-retained-physical-followup-source-epoch/1','retention_id','current_context_source_sha256','followup'),
}
FLAGS=('physical_accepted','engineering_accepted','manufacturing_release','operating_release')
OPTIONAL_FALSE=('configuration_adopted','selected_reference_changed','physical_journey_completed',
    'physical_acceptance','current_evaluator_admission','physical_equivalence_proven',
    'installed_mass_complete','design_complete')
MAX_FOLDER_BYTES=1024*1024*1024
MAX_ALL_BYTES=2*1024*1024*1024
MAX_ENTRIES=50000
MAX_JSON=16*1024*1024
PIN_KEYS=frozenset(('schema','git_commit','manifest_ids','manifest_sha256',
    'storage_id','storage_sha256','companion_manifest_id','companion_manifest_sha256','pins_id'))
META_KEYS=frozenset(('schema','git_commit','reference_candidate_id','selection_id','pins_id',
    'capture_producer_sha256','capture_helper_sha256','records','folders','original_source_sha256',
    'source_epoch_id','source_archive_sha256','sourced_transport','physical_followup',
    'scope','numerical_reexecuted','current_evaluator_admission','physical_equivalence_proven',
    'configuration_adopted','selected_reference_changed',*FLAGS,'archive_id'))


def _pins(pins, expected_pins_id):
    retained._hex(expected_pins_id)
    if (not isinstance(pins,dict) or set(pins)!=PIN_KEYS
            or pins.get('schema')!='osr-service-energy-extra-external-pins/1'
            or pins.get('git_commit')!=GIT_COMMIT or pins.get('pins_id')!=expected_pins_id
            or retained._id({k:v for k,v in pins.items() if k!='pins_id'})!=expected_pins_id
            or not isinstance(pins.get('manifest_ids'),dict)
            or not isinstance(pins.get('manifest_sha256'),dict)
            or set(pins.get('manifest_ids',{}))!=set(CATALOG)
            or set(pins.get('manifest_sha256',{}))!=set(CATALOG)):
        raise ValueError('Externally pinned complete original Git manifest set required')
    for values in (pins['manifest_ids'],pins['manifest_sha256']):
        for value in values.values():retained._hex(value)
    for key in ('storage_id','storage_sha256','companion_manifest_id','companion_manifest_sha256'):
        retained._hex(pins[key])
    return pins


def _held(record):
    if any(record.get(k) is not False for k in FLAGS):
        raise ValueError('Historical evidence cannot grant physical or engineering release')
    if any(k in record and record[k] is not False for k in OPTIONAL_FALSE):
        raise ValueError('Historical evidence cannot promote a candidate or journey')


def _file_data(path,*args,**kwargs):
    path=retained._ordinary(path)
    if path.lstat().st_nlink!=1:raise ValueError('Hard-linked files are not permitted')
    return retained._file_data(path,*args,**kwargs)


def _inventory(folder):
    folder=retained._ordinary(folder,directory=True);files={};directories=[];entries=0;total=0
    for p in folder.rglob('*'):
        entries+=1
        if entries>MAX_ENTRIES:raise ValueError('Packet inventory entry budget exceeded')
        name=p.relative_to(folder).as_posix();retained._path(name);info=p.lstat()
        if stat.S_ISDIR(info.st_mode):directories.append(name)
        elif stat.S_ISREG(info.st_mode):
            if info.st_nlink!=1:raise ValueError('Hard-linked packet files are not permitted')
            total+=info.st_size
            if total>MAX_FOLDER_BYTES:raise ValueError('Packet inventory byte budget exceeded')
            files[name]=_file_data(p)[0]
        else:raise ValueError('Only ordinary packet files and directories are permitted')
    return dict(files_sha256=dict(sorted(files.items())),directories=sorted(directories),
        file_count=len(files),entry_count=entries,bytes=total)


def _read_json(path,limit=MAX_JSON):
    sha,raw,_=_file_data(path,limit,materialize=True)
    return retained._json(raw),sha,raw


def _storage(folder, manifest, expected):
    storage,sha,_=_read_json(folder/'storage.json')
    if (sha!=expected['storage_sha256'] or storage.get('storage_id')!=expected['storage_id']
            or retained._id({k:v for k,v in storage.items() if k!='storage_id'})!=expected['storage_id']
            or storage.get('schema')!='osr-sourced-cell-chunk-storage/1'
            or storage.get('publication_id')!=manifest['publication_id']
            or storage.get('publication_manifest_sha256')!=expected['manifest_sha256']['sourced-case/manifest.json']
            or storage.get('archive_path')!='sourced-cell.tar.gz'
            or storage.get('archive_sha256')!=manifest['files_sha256']['sourced-cell.tar.gz']):
        raise ValueError('Pinned sourced-cell chunk storage differs')
    _held(storage)
    chunks=storage.get('chunks');unit=storage.get('chunk_bytes');total=0;combined=hashlib.sha256();seen=set()
    if (not isinstance(chunks,list) or not 0<len(chunks)<=8 or type(unit) is not int
            or not 0<unit<=24*1024**2):
        raise ValueError('Bounded sourced-cell chunk inventory required')
    for i,row in enumerate(chunks):
        name=row.get('path');size=row.get('bytes');wanted=row.get('sha256')
        if (name!=f'sourced-cell.part-{i:03d}' or name in seen or type(size) is not int
                or not 0<size<=unit or (i<len(chunks)-1 and size!=unit)):
            raise ValueError('Ordered bounded sourced-cell chunks required')
        seen.add(name);retained._hex(wanted);path=retained._ordinary(folder/name);before=path.lstat()
        if before.st_nlink!=1:raise ValueError('Hard-linked sourced-cell chunks are not permitted')
        if before.st_size!=size:raise ValueError('Sourced-cell chunk size differs')
        sig=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0));h=hashlib.sha256();count=0
        with os.fdopen(fd,'rb') as stream:
            if sig(before)!=sig(os.fstat(stream.fileno())):raise ValueError('Chunk changed before reading')
            while chunk:=stream.read(1024*1024):
                count+=len(chunk);h.update(chunk);combined.update(chunk)
            if sig(before)!=sig(os.fstat(stream.fileno())) or sig(before)!=sig(path.lstat()):
                raise ValueError('Chunk changed while reading')
        if count!=size or h.hexdigest()!=wanted:raise ValueError('Sourced-cell chunk bytes differ')
        total+=size
    archive=folder/'sourced-cell.tar.gz'
    if not archive.is_file():
        raise ValueError('Missing sourced-cell.tar.gz; reassemble pinned chunks in a separate historical tree')
    archive_sha,_,archive_size=_file_data(archive)
    if (total!=storage.get('total_bytes') or total!=archive_size
            or total>192*1024**2 or combined.hexdigest()!=storage['archive_sha256']
            or archive_sha!=storage['archive_sha256']):
        raise ValueError('Sourced-cell chunk concatenation or reassembled archive differs')
    return dict(storage_id=expected['storage_id'],storage_sha256=sha,archive_sha256=archive_sha,
        total_bytes=total,chunk_count=len(chunks),archive_git_tracking='not asserted by this verifier',
        requirement='Reassembled archive bytes must be present at verify time; tracked chunks alone are not claimed to be the archive')


def _records(root,pins):
    root=retained._ordinary(root,directory=True);sources={};records={};folders={};total=0;entries=0
    for name,(schema,identity_key,source_key,kind) in sorted(CATALOG.items()):
        path=root/PREFIX/name;manifest,msha,_=_read_json(path)
        if (msha!=pins['manifest_sha256'][name] or manifest.get('schema')!=schema
                or manifest.get(identity_key)!=pins['manifest_ids'][name]
                or retained._id({k:v for k,v in manifest.items() if k!=identity_key})!=pins['manifest_ids'][name]):
            raise ValueError('Externally pinned original manifest differs: '+name)
        _held(manifest)
        for k in ('candidate_id','reference_candidate_id'):
            if k in manifest and manifest[k]!=REFERENCE:raise ValueError('Selected candidate differs: '+name)
        for k in ('selection_id','current_selection_id'):
            if k in manifest and manifest[k]!=SELECTION:raise ValueError('Selected reference identity differs: '+name)
        source=retained._checked_map(manifest.get(source_key))
        for key,value in source.items():
            if key in sources and sources[key]!=value:raise ValueError('Conflicting current source epoch: '+key)
            sources[key]=value
        folder=path.parent;relative=folder.relative_to(root).as_posix()
        if relative not in folders:
            inv=_inventory(folder);total+=inv['bytes'];entries+=inv['entry_count']
            if total>MAX_ALL_BYTES or entries>MAX_ENTRIES:raise ValueError('Total packet inventory resource budget exceeded')
            folders[relative]=inv
        inventory=folders[relative]['files_sha256']
        if kind=='files':payload=retained._checked_map(manifest.get('files_sha256'))
        elif kind=='archive':
            retained._path(manifest.get('archive'));retained._hex(manifest.get('archive_sha256'))
            payload={manifest['archive']:manifest['archive_sha256']}
        else:
            retained._hex(manifest.get('producer_archive_sha256'));payload={'producer.tar.gz':manifest['producer_archive_sha256']}
        if name=='sourced-case/manifest.json' and 'sourced-cell.tar.gz' not in inventory:
            raise ValueError('Missing sourced-cell.tar.gz; reassemble pinned chunks in a separate historical tree')
        if any(inventory.get(k)!=v for k,v in payload.items()):
            raise ValueError('Declared original packet payload differs or is missing: '+name)
        records[name]=dict(manifest_id=pins['manifest_ids'][name],manifest_sha256=msha,
            schema=schema,folder=relative,source_key=source_key,declared_payload_sha256=dict(sorted(payload.items())))
    sourced_manifest,_,_=_read_json(root/(PREFIX+'sourced-case/manifest.json'))
    transport=_storage(root/(PREFIX+'sourced-case'),sourced_manifest,pins)
    wrapper,_,_=_read_json(root/(PREFIX+'retained-physical-followup-source-epoch/manifest.json'))
    if (wrapper.get('current_reference_ids',{}).get('candidate_id')!=REFERENCE
            or any(wrapper.get(k) is not False for k in ('current_evaluator_admission','numerical_reexecuted',
                'physical_comparison_proven','omitted_native_fields_restored','installed_mass_complete'))):
        raise ValueError('Retained physical-followup context or nonpromotion disposition differs')
    old_sources=retained._checked_map(wrapper.get('original_source_sha256'))
    old_sha,old_raw,_=_file_data(root/(PREFIX+'retained-physical-followup-source-epoch/producer.tar.gz'),
        retained.MAX_ARCHIVE_BYTES,materialize=True)
    if old_sha!=wrapper['producer_archive_sha256'] or old_raw[:10]!=bytes.fromhex('1f8b08000000000002ff'):
        raise ValueError('Retained physical-followup producer archive bytes differ')
    # This historical archive uses gzip XFL=2 (maximum compression); normalize
    # only that advisory header byte in memory for the canonical bounded checker.
    # Its original unmodified bytes are already authenticated above.
    retained._check_archive(old_raw[:8]+b'\x00'+old_raw[9:],old_sources)
    companion_path=root/COMPANION;companion,csha,_=_read_json(companion_path)
    if (csha!=pins['companion_manifest_sha256'] or companion.get('manifest_id')!=pins['companion_manifest_id']
            or retained._id({k:v for k,v in companion.items() if k!='manifest_id'})!=pins['companion_manifest_id']
            or companion.get('schema')!='osr-v06-followup-publication/1'
            or companion.get('parent_candidate_id')!=REFERENCE or companion.get('installed_mass_complete') is not False
            or companion.get('source_sha256')!=old_sources
            or wrapper.get('original_manifest_id')!=pins['companion_manifest_id']
            or wrapper.get('original_manifest_sha256')!=csha
            or wrapper.get('original_payload_sha256')!=companion.get('files_sha256')
            or wrapper.get('packet')!='docs/design-engine/v06-physical-closure'):
        raise ValueError('Original physical-followup companion differs from retained wrapper')
    _held(companion);relative=companion_path.parent.relative_to(root).as_posix()
    inventory=_inventory(companion_path.parent);total+=inventory['bytes'];entries+=inventory['entry_count']
    if total>MAX_ALL_BYTES or entries>MAX_ENTRIES:raise ValueError('Total packet inventory resource budget exceeded')
    folders[relative]=inventory
    if any(inventory['files_sha256'].get(k)!=v for k,v in retained._checked_map(companion['files_sha256']).items()):
        raise ValueError('Original physical-followup payload differs')
    physical=dict(wrapper_manifest_id=pins['manifest_ids']['retained-physical-followup-source-epoch/manifest.json'],
        original_manifest_id=pins['companion_manifest_id'],original_manifest_sha256=csha,
        original_producer_archive_sha256=old_sha,original_producer_source_count=len(old_sources),
        original_source_epoch='Retained separately inside the wrapper producer archive; not merged with the current-context source map')
    if len(sources)>retained.MAX_SOURCES:raise ValueError('Original source inventory exceeds limit')
    return dict(records=records,folders=dict(sorted(folders.items())),sources=dict(sorted(sources.items())),
        sourced_transport=transport,physical_followup=physical)


def _git_bytes(root,name):
    retained._path(name)
    env=dict(os.environ,GIT_NO_REPLACE_OBJECTS='1',GIT_NO_LAZY_FETCH='1',GIT_TERMINAL_PROMPT='0',
        GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,GIT_ATTR_NOSYSTEM='1')
    for key in tuple(env):
        if key.startswith(('GIT_CONFIG_KEY_','GIT_CONFIG_VALUE_')) or key in (
                'GIT_CONFIG_COUNT','GIT_CONFIG','GIT_CONFIG_PARAMETERS','GIT_CONFIG_SYSTEM',
                'GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY',
                'GIT_ALTERNATE_OBJECT_DIRECTORIES','GIT_COMMON_DIR','GIT_SHALLOW_FILE',
                'GIT_REPLACE_REF_BASE','GIT_NAMESPACE'):
            env.pop(key,None)
    cmd=['git','--no-replace-objects','-c','core.packedGitWindowSize=16m','-c','core.packedGitLimit=64m']
    obj=GIT_COMMIT+':'+name
    size=subprocess.run([*cmd,'cat-file','-s',obj],cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60)
    if size.returncode or not size.stdout.strip().isdigit() or int(size.stdout)>MAX_JSON:
        raise ValueError('Pinned Git object absent or exceeds manifest bound: '+name)
    blob=subprocess.run([*cmd,'show',obj],cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60)
    if blob.returncode or len(blob.stdout)!=int(size.stdout):raise ValueError('Pinned Git blob unavailable: '+name)
    return blob.stdout


def _git_anchor(root,pins):
    for name in CATALOG:
        raw=_git_bytes(root,PREFIX+name)
        if hashlib.sha256(raw).hexdigest()!=pins['manifest_sha256'][name]:
            raise ValueError('Pinned Git manifest bytes differ: '+name)
    if hashlib.sha256(_git_bytes(root,STORAGE)).hexdigest()!=pins['storage_sha256']:
        raise ValueError('Pinned Git sourced transport bytes differ')
    if hashlib.sha256(_git_bytes(root,COMPANION)).hexdigest()!=pins['companion_manifest_sha256']:
        raise ValueError('Pinned Git physical companion bytes differ')


def capture(root,output,*,pins,expected_pins_id):
    root=retained._ordinary(root,directory=True);pins=_pins(pins,expected_pins_id)
    output=Path(os.path.abspath(output));retained._ordinary(output.parent,directory=True)
    if any(p.is_symlink() for p in (output,*output.parents)) or output.exists():
        raise ValueError('Fresh ordinary archive destination required')
    if output==root or output.is_relative_to(root) or root.is_relative_to(output):
        raise ValueError('Private output must be disjoint from source tree')
    producer=_file_data(__file__,MAX_JSON)[0];helper=_file_data(retained.__file__,MAX_JSON)[0]
    _git_anchor(root,pins);data=_records(root,pins)
    for name in data['sources']:_file_data(root/name)
    source_archive=retained._make_archive(root,data['sources']);retained._check_archive(source_archive,data['sources'])
    if _records(root,pins)!=data:raise ValueError('Original packets changed during capture')
    meta=dict(schema='osr-retained-service-energy-extra-epoch/1',git_commit=GIT_COMMIT,
        reference_candidate_id=REFERENCE,selection_id=SELECTION,pins_id=expected_pins_id,
        capture_producer_sha256=producer,capture_helper_sha256=helper,
        records=data['records'],folders=data['folders'],original_source_sha256=data['sources'],
        source_epoch_id=retained._id(data['sources']),source_archive_sha256=hashlib.sha256(source_archive).hexdigest(),
        sourced_transport=data['sourced_transport'],physical_followup=data['physical_followup'],
        scope='Historical source bytes and pinned packet inventories only; original packet trees remain external; original physical producer epoch remains separate; no solver replay or current evaluator admission',
        numerical_reexecuted=False,current_evaluator_admission=False,physical_equivalence_proven=False,
        configuration_adopted=False,selected_reference_changed=False,**{k:False for k in FLAGS})
    meta['archive_id']=retained._id(meta)
    stage=Path(tempfile.mkdtemp(prefix='.service-energy-extra-',dir=output.parent))
    with (stage/'sources.tar.gz').open('xb') as f:f.write(source_archive)
    with (stage/'manifest.json').open('xb') as f:f.write(retained._encoded(meta))
    if (_records(root,pins)!=data or _file_data(__file__,MAX_JSON)[0]!=producer
            or _file_data(retained.__file__,MAX_JSON)[0]!=helper):
        raise ValueError('Inputs or capture producer changed; private stage retained: '+str(stage))
    retained._rename_noreplace(stage,output)
    return meta


def verify(root,archive,*,pins,expected_pins_id,expected_archive_id):
    root=retained._ordinary(root,directory=True);archive=retained._ordinary(archive,directory=True)
    pins=_pins(pins,expected_pins_id);retained._hex(expected_archive_id)
    before=_file_data(__file__,MAX_JSON)[0];helper=_file_data(retained.__file__,MAX_JSON)[0]
    if {p.name for p in archive.iterdir()}!={'manifest.json','sources.tar.gz'}:
        raise ValueError('Exact archive file inventory required')
    meta,msha,_=_read_json(archive/'manifest.json')
    if (set(meta)!=META_KEYS or meta.get('schema')!='osr-retained-service-energy-extra-epoch/1'
            or meta.get('archive_id')!=expected_archive_id
            or retained._id({k:v for k,v in meta.items() if k!='archive_id'})!=expected_archive_id
            or meta.get('git_commit')!=GIT_COMMIT or meta.get('pins_id')!=expected_pins_id
            or meta.get('reference_candidate_id')!=REFERENCE or meta.get('selection_id')!=SELECTION
            or any(meta.get(k) is not False for k in (*FLAGS,*OPTIONAL_FALSE[:2],
                'numerical_reexecuted','current_evaluator_admission','physical_equivalence_proven'))):
        raise ValueError('Externally pinned historical archive identity or disposition differs')
    retained._hex(meta.get('capture_producer_sha256'));retained._hex(meta.get('capture_helper_sha256'))
    data=_records(root,pins)
    if (meta.get('records')!=data['records'] or meta.get('folders')!=data['folders']
            or meta.get('original_source_sha256')!=data['sources']
            or meta.get('source_epoch_id')!=retained._id(data['sources'])
            or meta.get('sourced_transport')!=data['sourced_transport']
            or meta.get('physical_followup')!=data['physical_followup']):
        raise ValueError('Historical packet inventories or source relationships differ')
    sha,raw,_=_file_data(archive/'sources.tar.gz',retained.MAX_ARCHIVE_BYTES,materialize=True)
    if sha!=meta.get('source_archive_sha256'):raise ValueError('Historical source archive bytes differ')
    retained._check_archive(raw,data['sources'])
    if (_records(root,pins)!=data or _file_data(archive/'manifest.json',MAX_JSON)[0]!=msha
            or _file_data(archive/'sources.tar.gz',retained.MAX_ARCHIVE_BYTES)[0]!=sha
            or _file_data(__file__,MAX_JSON)[0]!=before or _file_data(retained.__file__,MAX_JSON)[0]!=helper):
        raise ValueError('Historical evidence changed during verification')
    return dict(verified=True,archive_id=expected_archive_id,pins_id=expected_pins_id,
        packet_manifest_count=len(CATALOG),source_count=len(data['sources']),
        capture_producer_sha256=meta['capture_producer_sha256'],verifier_producer_sha256=before,
        capture_helper_sha256=meta['capture_helper_sha256'],verifier_helper_sha256=helper,
        sourced_archive_requires_reassembly=True,numerical_reexecuted=False,current_evaluator_admission=False,
        physical_equivalence_proven=False,configuration_adopted=False,selected_reference_changed=False,
        **{k:False for k in FLAGS})


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('capture','verify'))
    p.add_argument('--root',type=Path,required=True);p.add_argument('--archive-directory',type=Path,required=True)
    p.add_argument('--pins',type=Path,required=True);p.add_argument('--expected-pins-id',required=True)
    p.add_argument('--expected-archive-id');args=p.parse_args()
    pins=retained._json(_file_data(args.pins,1024*1024,materialize=True)[1])
    if args.action=='capture':result=capture(args.root,args.archive_directory,pins=pins,expected_pins_id=args.expected_pins_id)
    else:
        if not args.expected_archive_id:p.error('verify requires --expected-archive-id')
        result=verify(args.root,args.archive_directory,pins=pins,expected_pins_id=args.expected_pins_id,expected_archive_id=args.expected_archive_id)
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':main()
