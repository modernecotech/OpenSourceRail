#!/usr/bin/env python3
"""Verify source receipts are portable through Git, without native tool execution."""
from hashlib import sha1
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[3]
manifest=json.loads((ROOT/'docs/design-engine/ferrite-maglev/reference/manifest.json').read_text())
paths=set(manifest['source_sha256'])
for directory in ('native','beam-only','system-development','baghdad-reference','coupled','reference'):
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'docs/design-engine/ferrite-maglev'/directory).rglob('*') if p.is_file())
raw=subprocess.check_output(['git','ls-files','--stage','-z'],cwd=ROOT)
index={}
for record in raw.split(b'\0'):
    if record:
        metadata,name=record.split(b'\t',1)
        mode,digest,stage=metadata.split()
        if stage!=b'0':raise ValueError('unmerged input: '+name.decode())
        index[name.decode()]=digest.decode()
errors=[]
for name in sorted(paths):
    data=(ROOT/name).read_bytes()
    digest=sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    if index.get(name)!=digest:errors.append(name)
if errors:raise ValueError('receipt inputs missing or changed in Git: '+str(errors))
print(json.dumps(dict(checked_files=len(paths),git_source_and_packet_identity=True,physical_release=False)))
