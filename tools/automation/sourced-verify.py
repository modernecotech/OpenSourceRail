#!/usr/bin/env python3
"""Full parallel semantic verification of the unchanged sourced publication.

The frozen executor rebuilds all five registries with original coordinator.verify
and actually recomputes and byte-compares all30 cases. This wrapper adds original
publication/summary/archive checks; it never substitutes integrity-only checking.
"""
import argparse
from collections import Counter
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path,PurePosixPath
import platform
import shutil
import stat
import sys
import tarfile

ROOT=Path(__file__).resolve().parents[2]
HELPER='tools/automation/sourced-execute.py'
HELPER_SHA256='a563d40b1c3219fe6b70c6cfa880f803605841797b9823a9fa7a886740444133'
MAX_ARCHIVE=192*1024**2
MAX_EXPANDED=1024**3
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
           operating_release=False,selected_reference_changed=False)


def _ordinary(path,max_bytes):
    p=Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size>max_bytes:raise ValueError('Bounded ordinary publication input required: '+p.name)
    return p


def _sha(path):
    h=sha256()
    with Path(path).open('rb') as stream:
        while block:=stream.read(1024**2):h.update(block)
    return h.hexdigest()


def _directory(path,*,exists=True):
    p=Path(os.path.abspath(path))
    for q in reversed((p,*p.parents)):
        if q.is_symlink():raise ValueError('Linked publication/audit directory refused')
        if q.exists() and not q.is_dir():raise ValueError('Ordinary publication/audit directory required')
    if exists and not p.is_dir():raise ValueError('Publication directory required')
    return p


def _pairs(pairs):
    value={}
    for key,item in pairs:
        if key in value:raise ValueError('Duplicate JSON key')
        value[key]=item
    return value


def _json(path,limit=4*1024**2):
    p=_ordinary(path,limit)
    try:return json.loads(p.read_bytes(),object_pairs_hook=_pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('Nonfinite JSON value')))
    except (UnicodeDecodeError,json.JSONDecodeError) as error:raise ValueError('Malformed publication JSON') from error


def _executor(root):
    p=_ordinary(Path(root)/HELPER,1024**2)
    if _sha(p)!=HELPER_SHA256:raise ValueError('Frozen semantic executor source differs')
    spec=importlib.util.spec_from_file_location('osr_frozen_sourced_executor',p)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


def _extract(archive,state):
    with tarfile.open(archive,'r:gz') as source:
        members=source.getmembers();names=[];total=0
        if len(members)>40:raise ValueError('Archive member count budget exceeded')
        for m in members:
            n=PurePosixPath(m.name);total+=m.size
            if not m.isfile() or not m.name or not n.parts or n.parts[0].endswith(':') or n.as_posix()!=m.name or n.is_absolute() or '..' in n.parts or '\\' in m.name or m.size<0 or total>MAX_EXPANDED:
                raise ValueError('Bounded canonical regular publication archive required')
            names.append(m.name)
        if len(names)!=len(set(names)):raise ValueError('Duplicate archive member')
        if not names:raise ValueError('Nonempty publication archive required')
        for member in members:
            target=state/member.name;target.parent.mkdir(parents=True,exist_ok=True)
            with source.extractfile(member) as stream,target.open('xb') as output:shutil.copyfileobj(stream,output,1024**2)
            if target.stat().st_size!=member.size:raise ValueError('Extracted archive member size differs')
    return dict(member_count=len(members),expanded_bytes=total)


def verify(publication,*,audit,workers=3,root=ROOT,timeout_s=1800.):
    verifier_sha=_sha(__file__)
    if type(workers) is not int or not 1<=workers<=3:raise ValueError('One to three bounded workers required')
    pub=_directory(publication);private=_directory(audit,exists=False);root=_directory(root)
    if private==pub or pub in private.parents or private in pub.parents:raise ValueError('Private audit must be disjoint from publication')
    executor=_executor(root);c=executor.modules(root)
    manifest_path=_ordinary(pub/'manifest.json',4*1024**2);manifest=_json(manifest_path)
    executor.unreleased(manifest)
    if not isinstance(manifest,dict) or manifest.get('schema')!='osr-sourced-cell-publication/1' or any(manifest.get(k) is not False for k in FLAGS):raise ValueError('Original unreleased sourced publication required')
    if manifest.get('publication_id')!=c.identity({k:v for k,v in manifest.items() if k!='publication_id'}):raise ValueError('Original publication seal differs')
    epoch=c.sources(root)
    if manifest.get('source_sha256')!=epoch:raise ValueError('Original publication source epoch differs')
    hashes=manifest.get('files_sha256')
    if not isinstance(hashes,dict) or set(hashes)!={'sourced-cell.tar.gz','summary.json'}:raise ValueError('Exact original two-file publication hash inventory required')
    for name,expected in hashes.items():
        if not isinstance(expected,str) or len(expected)!=64 or any(x not in '0123456789abcdef' for x in expected):raise ValueError('Canonical publication digest required')
        p=_ordinary(pub/name,MAX_ARCHIVE if name.endswith('.gz') else 4*1024**2)
        if _sha(p)!=expected:raise ValueError('Original publication file SHA differs')
    original_manifest_sha=_sha(manifest_path);source_summary=_json(pub/'summary.json')
    plan=c.plan();bodies=Counter(r['vehicle_id'] for r in plan)
    if len(plan)!=30 or bodies!=Counter({f'V{i}':6 for i in range(1,6)}):raise ValueError('This full verifier requires exactfive-body30-case plan')
    private.mkdir(parents=True,exist_ok=True);attempt=executor.fresh(private,'publication-verify');os.chmod(attempt,0o700)
    state=attempt/'extracted-state';state.mkdir(mode=0o700)
    extracted=_extract(pub/'sourced-cell.tar.gz',state)
    index=c.read(state/'latest.json')
    expected_summary=dict(schema='osr-sourced-cell-summary/1',run_id=index['run_id'],cases=index['cases'],pending=index['pending'],**FLAGS)
    if c.encoded(expected_summary)!=c.encoded(source_summary):raise ValueError('Exact original publication summary differs')
    replay,where=executor.execute('replay',state,audit=attempt/'semantic-replay',workers=workers,root=root,timeout_s=timeout_s)
    executor.unreleased(replay)
    if replay.get('orchestration_id')!=executor.ident({k:v for k,v in replay.items() if k!='orchestration_id'}):raise ValueError('Actual replay orchestration seal differs')
    if replay.get('operation')!='replay' or replay.get('failures')!=[] or replay.get('semantic_replay_executed') is not True or replay.get('source_sha256')!=epoch or replay.get('executor_sha256')!=HELPER_SHA256:
        raise ValueError('Full actual semantic replay failed; private audit retained at '+str(attempt))
    reports=replay.get('workers')
    if not isinstance(reports,list) or len(reports)!=5 or {r.get('folder') for r in reports}!=set(bodies):raise ValueError('Five distinct actual replay workers required')
    for row in reports:
        execution=row.get('execution',{})
        if row.get('validated_cases')!=bodies[row['folder']] or execution.get('returncode')!=0 or execution.get('interrupted') is not False or not isinstance(row.get('worker_receipt_id'),str) or len(row['worker_receipt_id'])!=64:
            raise ValueError('Every original case must be actually replayed successfully')
    # Reuse only the ORIGINAL first verification, pinned to unchanged canonical
    # inputs by the frozen executor. It already rebuilt all five registries.
    check=executor.bind_verified_snapshot(c,state,replay,root)
    if check.get('verified') is not True or check.get('pending')!=0 or check.get('cases')!=30 or check.get('semantic_replay_executed') is not False:raise ValueError('Complete original first integrity verification required')
    for vid in sorted(bodies):
        worker=Path(where)/vid;request=executor.load(worker/'input.json')
        executor.bind_replayed_canonical(c,state,worker,request,epoch)
    check['semantic_replay_executed']=True
    if check!=manifest.get('validation'):raise ValueError('Original publication validation differs from actual full replay')
    index=c.read(state/'latest.json')
    summary=dict(schema='osr-sourced-cell-summary/1',run_id=index['run_id'],cases=index['cases'],pending=index['pending'],**FLAGS)
    if c.encoded(summary)!=c.encoded(source_summary):raise ValueError('Exact original publication summary differs')
    _directory(pub);_ordinary(root/HELPER,1024**2);_ordinary(manifest_path,4*1024**2)
    for name in hashes:_ordinary(pub/name,MAX_ARCHIVE if name.endswith('.gz') else 4*1024**2)
    if c.sources(root)!=epoch or _sha(__file__)!=verifier_sha or _sha(root/HELPER)!=HELPER_SHA256 or _sha(manifest_path)!=original_manifest_sha or any(_sha(pub/name)!=h for name,h in hashes.items()):raise ValueError('Publication/source/helper changed during full verification')
    result=dict(schema='osr-full-parallel-publication-verification/1',verified=True,semantic_replay_executed=True,
       publication_id=manifest['publication_id'],original_manifest_sha256=original_manifest_sha,original_files_sha256=hashes,
       original_validation=check,source_sha256=epoch,source_epoch_id=c.identity(epoch),
       executor_sha256=HELPER_SHA256,verifier_source_sha256=verifier_sha,
       source_archive_sha256=replay['source_archive_sha256'],orchestration_id=replay['orchestration_id'],
       actual_replayed_cases=sum(r['validated_cases'] for r in reports),actual_body_workers=len(reports),
       worker_receipt_ids={r['folder']:r['worker_receipt_id'] for r in reports},archive_inventory=extracted,
       actor=dict(executable=sys.executable,python_version=sys.version,platform=platform.platform(),
          isolation='Ordinary subprocesses with frozen-helper address-space/wall-clock limits; filesystem/network access is not OS sandboxed'),
       private_audit=str(attempt),full_original_semantic_contract_preserved=True,**FLAGS)
    result['verification_id']=c.identity(result);executor.write(attempt/'verification.json',result)
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('publication',type=Path);p.add_argument('--audit',type=Path,required=True)
    p.add_argument('--workers',type=int,default=3);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--timeout-s',type=float,default=1800.)
    a=p.parse_args(argv)
    try:result=verify(a.publication,audit=a.audit,workers=a.workers,root=a.root,timeout_s=a.timeout_s)
    except (ValueError,OSError,EOFError,tarfile.TarError) as error:p.exit(2,'sourced full verification: '+str(error)+'\n')
    print(json.dumps(result,sort_keys=True));return 0


if __name__=='__main__':raise SystemExit(main())
