"""Portable archive validation; optional exact numerical replay in a temp tree."""
from hashlib import sha256
from pathlib import Path,PurePosixPath
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

BASE=Path(__file__).resolve().parent

def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def path(name):
    p=PurePosixPath(name)
    if not name or p.is_absolute() or '..' in p.parts or p.as_posix()!=name:raise ValueError('safe archive relative path required')
    return BASE/name

def verify(check_current_sources=False,replay=False):
    receipt=json.loads((BASE/'archive-receipt.json').read_bytes())
    flags=('design_complete','physical_validation','manufacturing_release','physical_release','physical_output_authorised','engineering_accepted')
    if receipt['schema']!='osr-magnetic-redesign-archive/1' or any(receipt.get(k)is not False for k in (*flags,'configuration_adopted')):raise ValueError('unreleased isolated research scope required')
    expected=receipt['files_sha256']
    actual={p.relative_to(BASE).as_posix() for p in BASE.rglob('*') if p.is_file()}
    if actual!=set(expected)|{'archive-receipt.json'}:raise ValueError('archive inventory differs')
    total=0
    for name,h in expected.items():
        p=path(name);total+=p.stat().st_size
        if p.is_symlink() or not p.is_file() or p.stat().st_size>64*1024*1024 or total>128*1024*1024 or digest(p)!=h:raise ValueError('bounded archive bytes differ')
    manifest=json.loads((BASE/'source-manifest.json').read_bytes());result=json.loads((BASE/'results.json').read_bytes())
    if manifest['source_sha256']!=result['source_sha256'] or not manifest['source_unchanged_after_execution'] or not result['source_unchanged']:raise ValueError('executed source closure differs')
    if any(result.get(k)is not False for k in (*flags,'configuration_adopted','production_sources_edited','canonical_outputs_edited')):raise ValueError('research must not promote a design')
    if receipt['original_execution_path']!='build/magnetic-redesign-bounds/run.py' or receipt['command']!=manifest['command']:raise ValueError('actual original execution mapping differs')
    if set(receipt['source_archive_mapping'])!=set(manifest['source_sha256']) or set(receipt['executed_file_mapping'])!=set(manifest['files_sha256']):raise ValueError('complete original file/source mapping required')
    for name,h in manifest['files_sha256'].items():
        mapped=receipt['executed_file_mapping'][name]
        if digest(path(mapped))!=h:raise ValueError('executed output bytes differ')
    for name,h in manifest['source_sha256'].items():
        original=PurePosixPath(name)
        if original.is_absolute() or '..' in original.parts or original.as_posix()!=name:raise ValueError('safe original source path required')
        p=path(receipt['source_archive_mapping'][name])
        if digest(p)!=h:raise ValueError('archived original source differs')
        if check_current_sources and name!=receipt['original_execution_path']:
            current=BASE.parents[2]/name
            if not current.is_file() or digest(current)!=h:raise ValueError('current repository input differs from archived source')
    answer=dict(archive_inventory_verified=True,source_files=len(manifest['source_sha256']),file_count=len(expected),
        executed_driver_byte_identical=True,cases=len(result['cases']),current_sources_checked=check_current_sources,
        complete_system_feasible=False,configuration_adopted=False)
    if replay:
        with tempfile.TemporaryDirectory(prefix='osr-magnetic-bounds-replay-') as temporary:
            root=Path(temporary)
            for name,mapped in receipt['source_archive_mapping'].items():
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path(mapped),target)
            driver=root/receipt['original_execution_path'];env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
            with (driver.parent/'execution.log').open('wb') as log:
                subprocess.run([sys.executable,str(driver)],cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
            fresh=json.loads((driver.parent/'results.json').read_bytes())
            old=dict(result);new=dict(fresh)
            old.pop('elapsed_s');new.pop('elapsed_s')
            if old!=new:raise ValueError('portable numerical replay differs')
            answer.update(portable_numerical_replay_verified=True,comparison_ignored_fields=['elapsed_s'],
                replayed_cases=len(fresh['cases']),same_source_sha256=True)
    return answer

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-current-sources',action='store_true')
    parser.add_argument('--replay',action='store_true')
    args=parser.parse_args()
    print(json.dumps(verify(args.check_current_sources,args.replay),sort_keys=True))
