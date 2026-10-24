#!/usr/bin/env python3
"""Verify source receipts are portable through Git, without native tool execution."""
from hashlib import sha1
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[3]
manifest=json.loads((ROOT/'docs/design-engine/ferrite-maglev/reference/manifest.json').read_text())
paths=set(manifest['source_sha256'])
for directory in ('native','beam-only','system-development','baghdad-reference','coupled','iterative','station-powered','station-structure','station-protocol','station-native','moving-train','system-campaign','manufactured-dossier','manufactured-native','corridor','booster-kit','booster-native','interchange-hubs','line-capacity','hub-access','qualification','assembled-body','shared-hub-layout','body-stiffness','stopped-recovery','drive-construction','pilot-product','pilot-actuators','launch-optimisation','delivery-schedule','pilot-corridor','pilot-variants','pilot-lifecycle','assurance-profiles','capability-migration','pilot-delivery','candidate-native','candidate-magnetics','candidate-structures','full-dynamics','candidate-manufacturing','candidate-lifecycle','bim-field','operations-crosscheck','planning-platform','planning-ui','system-detailed','reference'):
    packet=ROOT/'docs/design-engine/ferrite-maglev'/directory
    paths.update(p.relative_to(ROOT).as_posix() for p in packet.rglob('*') if p.is_file())
    for receipt in [*packet.rglob('manifest.json'),*packet.rglob('receipt.json')]:
        value=json.loads(receipt.read_text())
        for key in ('source_sha256','sources_sha256'):
            paths.update(value.get(key,{}))
for name in ('engineering/assurance/v052-pilot-profiles','engineering/assurance/v052-pilot-lifecycle-native','engineering/assurance/v053-candidate-lifecycle-native','engineering/assurance/v052-pilot-ui','engineering/assurance/v052-pilot-body-axial','engineering/assurance/v053-detailed-body-axial','engineering/assurance/v053-magnetic-redesign-bounds','engineering/assurance/v053-propulsion-redesign-screen','engineering/assurance/v052-pilot-actuator-crosscheck','docs/design-engine/ferrite-maglev/pilot-variant-failures','docs/design-engine/ferrite-maglev/pilot-actuators-rejected-120turn','docs/design-engine/ferrite-maglev/pilot-actuators-python-observer-baseline'):
    packet=ROOT/name
    paths.update(p.relative_to(ROOT).as_posix() for p in packet.rglob('*') if p.is_file())
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
