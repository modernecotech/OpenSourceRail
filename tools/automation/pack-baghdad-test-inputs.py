#!/usr/bin/env python3
"""Freeze current ignored CI inputs independently of the historical proposal."""
import hashlib
import json
from pathlib import Path
import sys
from proposal_archives import write_parts

ROOT=Path(__file__).resolve().parents[2]
CITY=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
OUT=ROOT/'engineering/assurance/baghdad-test-inputs'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def receipt(path):return dict(bytes=path.stat().st_size,sha256=sha(path))

def main():
    ops=json.loads((CITY/'operations/baghdad-operations-manifest.json').read_text())
    payload=CITY/'operations'/ops['file']
    if receipt(payload)!=dict(bytes=ops['compressed_bytes'],sha256=ops['compressed_sha256']):
        raise ValueError('Current operations input differs from its own receipt')
    historical=json.loads((CITY/'manifest.json').read_text());prefix=CITY.relative_to(ROOT).as_posix()+'/engineering/'
    corridor=(CITY/'corridors.json').relative_to(ROOT).as_posix()
    members={name:ROOT/name for name in historical['inputs'] if name==corridor or name.startswith(prefix) and name[len(prefix):].startswith(('energy/','gis/','sumo/'))}
    members[payload.relative_to(ROOT).as_posix()]=payload
    if any(not p.is_file() for p in members.values()):raise ValueError('A current solver/GIS input is missing')
    OUT.mkdir(parents=True,exist_ok=True)
    parts=write_parts(OUT,members,'2026-10-10',50*1024*1024)
    renamed={}
    for name,names in parts.items():
        new=name.replace('Baghdad-Proposal-Supporting-Data','Baghdad-Current-Test-Inputs')
        (OUT/name).replace(OUT/new);renamed[new]=names
    sources=[Path(__file__).resolve(),ROOT/'tools/automation/bootstrap_baghdad_tests.py',ROOT/'tools/automation/proposal_archives.py',
             CITY/'design.toml',CITY/'baghdad.toml',CITY/'operations/baghdad-operations-manifest.json']
    manifest=dict(schema='osr-current-baghdad-test-inputs/1',scope='Current exact operations and solver/GIS test inputs; historical publication remains a separate snapshot',
                  supporting_archives=renamed,archive_members=sorted(members),members={n:receipt(p) for n,p in sorted(members.items())},
                  outputs={(OUT/n).relative_to(ROOT).as_posix():receipt(OUT/n) for n in renamed},
                  source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sources},physical_release=False,operating_release=False)
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print('Current Baghdad test inputs:',len(members),'members in',len(parts),'verified-size parts')

if __name__=='__main__':main()
