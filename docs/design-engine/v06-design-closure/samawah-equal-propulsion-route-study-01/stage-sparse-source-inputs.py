#!/usr/bin/env python3
"""Stage only Git-pinned city files required by the all-city source manifest.

This is for a sparse source worktree. It never overwrites existing files and
records every staged path and SHA-256 in an external receipt.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess


def collect(root, commit):
    base = Path('docs/design-engine/current/planning')
    index = json.loads((root/base/'index.json').read_bytes())
    catalogue = json.loads((root/'docs/design-engine/current/cities.json').read_bytes())
    cities = {row['slug']: row for row in catalogue['cities']}
    names = {str(base/'index.json'), str(base/'manifest.json'),
             'docs/design-engine/current/cities.json'}
    for row in index['cities']:
        slug = row['city']
        plan_name = str(base/row['plan'])
        names.add(plan_name)
        names.add(cities[slug]['geography_path'])
        names.add(cities[slug]['route_geography_path'])
        plan_path = root/plan_name
        plan = json.loads(gzip.decompress(plan_path.read_bytes()))
        names.update(plan.get('source_sha256', {}))
    return names


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--commit', default='HEAD')
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    commit = subprocess.check_output(['git','-C',str(root),'rev-parse',args.commit],text=True).strip()
    names = sorted(name for name in collect(root, commit) if name.startswith('cities/'))
    listing = subprocess.check_output(['git','-C',str(root),'ls-tree','-r','-l','-z',commit,'--','cities/catalogue'])
    blobs = {}
    for item in listing.split(b'\0'):
        if not item:
            continue
        metadata, raw_name = item.split(b'\t',1)
        mode, kind, oid, size = metadata.decode().split()
        if kind == 'blob':
            blobs[raw_name.decode()] = (mode, oid, int(size))
    absent = []
    for name in names:
        path = root/name
        if path.exists():
            if path.is_symlink() or not path.is_file():
                raise ValueError('Expected ordinary source file: '+name)
            blob = blobs.get(name)
            if blob is None:
                raise ValueError('Tracked Git source missing from tree: '+name)
            data = subprocess.check_output(['git','-C',str(root),'show',f'{commit}:{name}'])
            if hashlib.sha256(path.read_bytes()).digest() != hashlib.sha256(data).digest():
                raise ValueError('Existing source differs from pinned Git bytes: '+name)
        else:
            if name not in blobs:
                raise ValueError('Required source path is not a Git blob: '+name)
            absent.append(name)
    receipt = args.receipt.resolve()
    if receipt.exists():
        raise ValueError('Fresh source receipt required; preserve prior attempts')
    receipt.parent.mkdir(parents=True, exist_ok=True)
    records = []
    for name in absent:
        mode, oid, size = blobs[name]
        target = root/name
        if target.exists() or target.is_symlink():
            raise ValueError('Refusing to overwrite existing path: '+name)
        parent = target.parent
        parent.mkdir(parents=True, exist_ok=True)
        if parent.resolve().is_relative_to(root) is False:
            raise ValueError('Source path escaped worktree: '+name)
        proc = subprocess.Popen(['git','-C',str(root),'cat-file','blob',oid],stdout=subprocess.PIPE)
        sha = hashlib.sha256()
        byte_count = 0
        with target.open('xb') as output:
            while True:
                chunk = proc.stdout.read(1024*1024)
                if not chunk:
                    break
                output.write(chunk)
                sha.update(chunk)
                byte_count += len(chunk)
        if proc.wait() != 0 or byte_count != size:
            raise ValueError('Git blob extraction failed or size differs: '+name)
        records.append(dict(path=name, git_blob=oid, size_bytes=size,
            sha256=sha.hexdigest(), staged_by_this_run=True))
    result = dict(schema='osr-sparse-city-source-staging/1', source_commit=commit,
        root=str(root), source_file_count=len(names), already_present_count=len(names)-len(absent),
        staged_file_count=len(records), staged_bytes=sum(row['size_bytes'] for row in records),
        files=records, os_sandbox_enforced=False)
    result['receipt_id'] = hashlib.sha256((json.dumps(result,sort_keys=True,separators=(',',':'))+'\n').encode()).hexdigest()
    receipt.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('source_commit','source_file_count','already_present_count','staged_file_count','staged_bytes','receipt_id')},sort_keys=True))


if __name__ == '__main__':
    main()
