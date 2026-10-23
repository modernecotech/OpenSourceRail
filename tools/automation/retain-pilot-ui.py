#!/usr/bin/env python3
"""Retain exact-source browser executions after the two actual browser suites."""
from datetime import datetime,timezone
import argparse,subprocess
from hashlib import sha256
from pathlib import Path
import json,shutil,sys
root=Path(__file__).resolve().parents[2]
output=root/'engineering/assurance/v052-pilot-ui'
prepared=root/'build/pilot-ui-inputs.json'
def digest(p):return sha256(p.read_bytes()).hexdigest()
def sources():
    packet=root/'docs/design-engine/ferrite-maglev/pilot-delivery'
    v=json.loads((packet/'study.json').read_bytes())
    paths=[packet/'manifest.json',root/'docs/design-engine/ferrite-maglev/reference/manifest.json',
        *(root/r['packet']/'manifest.json' for r in v['components']),
        *(root/n for n in ['docs/workbench/maglev/index.html','docs/workbench/maglev/app.js','docs/workbench/maglev/pilot.js','docs/workbench/maglev/app.css','tools/automation/maglev-workbench.py','tools/automation/tests/verify-maglev-workbench.mjs','tools/automation/tests/verify-maglev-v05.mjs','package.json','package-lock.json','tools/automation/retain-pilot-ui.py','tools/automation/osr-python'])]
    return {p.relative_to(root).as_posix():digest(p) for p in paths}
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('action',choices=('prepare','retain','verify'))
args=parser.parse_args()
if args.action=='verify':
    receipt=json.loads((output/'manifest.json').read_bytes())
    assert receipt['passed'] is True and receipt['source_unchanged'] is True and receipt['source_sha256']==sources(),'stale browser execution inputs'
    assert all(receipt.get(k) is False for k in ('engineering_accepted','physical_release','manufacturing_release','design_complete'))
    assert {p.name for p in output.iterdir()}==set(receipt['files_sha256'])|{'manifest.json'},'unexpected browser record inventory'
    for name,d in receipt['files_sha256'].items():
        path=output/name
        assert path.parent==output and not path.is_symlink() and path.stat().st_size<=32*1024*1024 and digest(path)==d,'altered browser record'
    print('Exact-source browser execution record verified')
elif args.action=='prepare':
    prepared.write_text(json.dumps(dict(started_utc=datetime.now(timezone.utc).isoformat(),source_sha256=sources()),indent=2)+'\n')
    print('Prepared exact UI and publication source receipt')
else:
    before=json.loads(prepared.read_bytes());assert before['source_sha256']==sources(),'UI inputs changed during browser campaigns'
    wb=root/'build/maglev-workbench-browser';ref=root/'build/maglev-browser'
    w=json.loads((wb/'checks.json').read_bytes());r=json.loads((ref/'browser-check.json').read_bytes())
    assert w['primary_ui'] and w['pilot_packets']==9 and w['pilot_visual_tampering_held'] and w['missing_video_digest_held'] and w['pilot_error_recovery'] and w['current_candidate_media_verified']
    assert not w['errors'] and not w['external'] and not r['javascript_errors'] and not r['external_requests'] and not r['failed_requests']
    output.mkdir(parents=True,exist_ok=True)
    copies=[(wb/'candidate-mobile.png','candidate-mobile.png'),(wb/'coupled-actuators.png','coupled-actuators.png'),(wb/'desktop.png','workbench-desktop.png'),(wb/'mobile.png','workbench-mobile.png'),(wb/'checks.json','workbench-checks.json'),(ref/'primary-study-desktop.png','reference-desktop.png'),(ref/'primary-study-mobile.png','reference-mobile.png'),(ref/'browser-check.json','reference-checks.json'),(root/'build/pilot-final-browser-workbench.log','workbench-run.txt'),(root/'build/pilot-final-browser-reference.log','reference-run.txt')]
    assert not any(p.is_symlink() for p in output.iterdir())
    for source,name in copies:shutil.copyfile(source,output/name)
    receipt=dict(schema='osr-pilot-browser-execution/1',passed=True,started_utc=before['started_utc'],finished_utc=datetime.now(timezone.utc).isoformat(),source_sha256=before['source_sha256'],source_unchanged=True,node_version=subprocess.check_output(['node','--version'],text=True).strip(),retainer_source='tools/automation/retain-pilot-ui.py',commands=[['node','tools/automation/tests/verify-maglev-workbench.mjs','build/maglev-workbench-browser'],['node','tools/automation/tests/verify-maglev-v05.mjs','build/maglev-browser']],files_sha256={name:digest(output/name) for _,name in copies},engineering_accepted=False,physical_release=False,manufacturing_release=False,design_complete=False,scope='Actual read-only browsers, geometry receipts, UI/mobile and adverse delivered-byte tests; no engineering or physical acceptance')
    (output/'manifest.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(retained=str(output.relative_to(root)),files=len(copies),passed=True)))
